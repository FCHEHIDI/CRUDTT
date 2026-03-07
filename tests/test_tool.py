"""Tests des endpoints Tool (GET/POST/PUT /api/v1/tools/)."""

from decimal import Decimal

import pytest

from app.models.category import Category as CategoryModel

BASE = "/api/v1"


# ──────────────────────────── Fixtures ────────────────────────────────────────


@pytest.fixture()
def category(db):
    """Crée une catégorie de test dans la base SQLite."""
    cat = CategoryModel(name="Dev Tools", description="Outils de développement")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def _tool_payload(category_id: int, **overrides) -> dict:
    """Retourne un payload valide pour créer un outil.

    Args:
        category_id: ID de la catégorie associée.
        **overrides: Champs à surcharger.

    Returns:
        Dictionnaire prêt à passer en JSON.
    """
    payload = {
        "name": "Slack",
        "vendor": "Salesforce",
        "category_id": category_id,
        "monthly_cost": "12.99",
        "owner_department": "Engineering",
        "website_url": "https://slack.com",
        "description": "Outil de communication",
    }
    payload.update(overrides)
    return payload


# ──────────────────────────── GET /tools/ ─────────────────────────────────────


class TestListTools:
    """Tests pour GET /api/v1/tools/."""

    def test_list_tools_empty(self, client):
        """Sans outils, data est vide et total=0."""
        response = client.get(f"{BASE}/tools/")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["total"] == 0
        assert data["filtered"] == 0
        assert data["filters_applied"] == {}

    def test_list_tools_returns_created_tool(self, client, category):
        """Un outil créé apparaît dans la liste avec la bonne structure."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id))
        response = client.get(f"{BASE}/tools/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["filtered"] == 1
        tool = data["data"][0]
        assert tool["name"] == "Slack"
        assert tool["category"] == "Dev Tools"
        assert tool["status"] == "active"
        assert tool["owner_department"] == "Engineering"

    def test_list_tools_filter_department(self, client, category):
        """Filtrer par département retourne uniquement les outils de ce département."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Slack", owner_department="Engineering"))
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="HubSpot", owner_department="Sales"))
        response = client.get(f"{BASE}/tools/?department=Engineering")
        assert response.status_code == 200
        data = response.json()
        assert data["filtered"] == 1
        assert data["data"][0]["owner_department"] == "Engineering"
        assert data["filters_applied"]["department"] == "Engineering"

    def test_list_tools_filter_status(self, client, category):
        """Filtrer par statut retourne uniquement les outils avec ce statut."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Active Tool"))
        create_resp = client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Old Tool"))
        tool_id = create_resp.json()["id"]
        client.put(f"{BASE}/tools/{tool_id}", json={"status": "deprecated"})

        response = client.get(f"{BASE}/tools/?status=active")
        assert response.status_code == 200
        data = response.json()
        assert data["filtered"] == 1
        assert data["data"][0]["name"] == "Active Tool"

    def test_list_tools_filter_category(self, client, category, db):
        """Filtrer par nom de catégorie retourne uniquement les outils de cette catégorie."""
        cat2 = CategoryModel(name="Marketing Tools")
        db.add(cat2)
        db.commit()
        db.refresh(cat2)
        cat2_id = cat2.id  # cache l'id avant que le premier POST ferme la session
        category_id = category.id

        client.post(f"{BASE}/tools/", json=_tool_payload(category_id, name="Dev Tool"))
        client.post(f"{BASE}/tools/", json=_tool_payload(cat2_id, name="Mailchimp"))

        response = client.get(f"{BASE}/tools/?category=Dev+Tools")
        assert response.status_code == 200
        data = response.json()
        assert data["filtered"] == 1
        assert data["data"][0]["name"] == "Dev Tool"

    def test_list_tools_filter_min_cost(self, client, category):
        """min_cost filtre les outils en dessous du seuil."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Cheap", monthly_cost="5.00"))
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Expensive", monthly_cost="100.00"))
        response = client.get(f"{BASE}/tools/?min_cost=50")
        assert response.status_code == 200
        data = response.json()
        assert data["filtered"] == 1
        assert data["data"][0]["name"] == "Expensive"

    def test_list_tools_filter_max_cost(self, client, category):
        """max_cost filtre les outils au-dessus du seuil."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Cheap", monthly_cost="5.00"))
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Expensive", monthly_cost="100.00"))
        response = client.get(f"{BASE}/tools/?max_cost=50")
        assert response.status_code == 200
        data = response.json()
        assert data["filtered"] == 1
        assert data["data"][0]["name"] == "Cheap"

    def test_list_tools_pagination(self, client, category):
        """limit=1 retourne un seul outil mais filtered reflète le total filtré."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Tool A"))
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Tool B"))
        response = client.get(f"{BASE}/tools/?page=1&limit=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["filtered"] == 2

    def test_list_tools_pagination_page2(self, client, category):
        """page=2 avec limit=1 retourne le second outil."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Alpha"))
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Zeta"))
        response = client.get(f"{BASE}/tools/?page=2&limit=1&sort_by=name&order=asc")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Zeta"

    def test_list_tools_sort_by_name_desc(self, client, category):
        """sort_by=name&order=desc retourne les outils dans l'ordre décroissant."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Alpha"))
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Zeta"))
        response = client.get(f"{BASE}/tools/?sort_by=name&order=desc")
        assert response.status_code == 200
        names = [t["name"] for t in response.json()["data"]]
        assert names == sorted(names, reverse=True)

    def test_list_tools_sort_by_cost_asc(self, client, category):
        """sort_by=monthly_cost&order=asc retourne les outils du moins cher au plus cher."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Expensive", monthly_cost="100.00"))
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="Cheap", monthly_cost="5.00"))
        response = client.get(f"{BASE}/tools/?sort_by=monthly_cost&order=asc")
        assert response.status_code == 200
        names = [t["name"] for t in response.json()["data"]]
        assert names[0] == "Cheap"
        assert names[1] == "Expensive"


# ──────────────────────────── GET /tools/{id} ─────────────────────────────────


class TestGetTool:
    """Tests pour GET /api/v1/tools/{tool_id}."""

    def test_get_tool_success(self, client, category):
        """Un outil existant retourne 200 avec ToolDetail complet."""
        create_resp = client.post(f"{BASE}/tools/", json=_tool_payload(category.id))
        tool_id = create_resp.json()["id"]
        response = client.get(f"{BASE}/tools/{tool_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tool_id
        assert data["name"] == "Slack"
        assert data["category"] == "Dev Tools"
        assert "usage_metrics" in data
        assert "last_30_days" in data["usage_metrics"]
        assert "total_sessions" in data["usage_metrics"]["last_30_days"]
        assert "avg_session_minutes" in data["usage_metrics"]["last_30_days"]
        assert "total_monthly_cost" in data
        assert "updated_at" in data

    def test_get_tool_total_monthly_cost(self, client, category):
        """total_monthly_cost = monthly_cost * active_users_count."""
        create_resp = client.post(f"{BASE}/tools/", json=_tool_payload(category.id, monthly_cost="10.00"))
        tool_id = create_resp.json()["id"]
        response = client.get(f"{BASE}/tools/{tool_id}")
        assert response.status_code == 200
        # active_users_count=0 à la création → total_monthly_cost=0
        assert Decimal(response.json()["total_monthly_cost"]) == Decimal("0")

    def test_get_tool_not_found(self, client):
        """Un ID inexistant retourne 404."""
        response = client.get(f"{BASE}/tools/9999")
        assert response.status_code == 404


# ──────────────────────────── POST /tools/ ────────────────────────────────────


class TestCreateTool:
    """Tests pour POST /api/v1/tools/."""

    def test_create_tool_success(self, client, category):
        """Créer un outil valide retourne 201 avec ToolDetail."""
        response = client.post(f"{BASE}/tools/", json=_tool_payload(category.id))
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Slack"
        assert data["vendor"] == "Salesforce"
        assert data["status"] == "active"
        assert data["active_users_count"] == 0
        assert data["category"] == "Dev Tools"
        assert "id" in data
        assert "usage_metrics" in data
        assert "total_monthly_cost" in data

    def test_create_tool_without_optional_fields(self, client, category):
        """Créer un outil sans les champs optionnels fonctionne."""
        payload = {
            "name": "Minimal Tool",
            "vendor": "Acme",
            "category_id": category.id,
            "monthly_cost": "9.99",
            "owner_department": "HR",
        }
        response = client.post(f"{BASE}/tools/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None
        assert data["website_url"] is None

    def test_create_tool_duplicate_name(self, client, category):
        """Un nom dupliqué retourne 409."""
        client.post(f"{BASE}/tools/", json=_tool_payload(category.id))
        response = client.post(f"{BASE}/tools/", json=_tool_payload(category.id))
        assert response.status_code == 409

    def test_create_tool_invalid_category(self, client):
        """Une catégorie inexistante retourne 400."""
        response = client.post(f"{BASE}/tools/", json=_tool_payload(category_id=9999))
        assert response.status_code == 400

    def test_create_tool_invalid_url(self, client, category):
        """Une URL sans http(s):// retourne 400 (validation Pydantic)."""
        response = client.post(
            f"{BASE}/tools/",
            json=_tool_payload(category.id, website_url="slack.com"),
        )
        assert response.status_code == 400

    def test_create_tool_missing_required_fields(self, client):
        """Un payload incomplet (vendor manquant) retourne 400."""
        response = client.post(f"{BASE}/tools/", json={"name": "Slack"})
        assert response.status_code == 400

    def test_create_tool_name_too_short(self, client, category):
        """Un nom d'un seul caractère (min_length=2) retourne 400."""
        response = client.post(f"{BASE}/tools/", json=_tool_payload(category.id, name="X"))
        assert response.status_code == 400

    def test_create_tool_cost_zero(self, client, category):
        """Un coût à 0 retourne 400 (gt=0)."""
        response = client.post(f"{BASE}/tools/", json=_tool_payload(category.id, monthly_cost="0"))
        assert response.status_code == 400

    def test_create_tool_invalid_department(self, client, category):
        """Un département inexistant retourne 400."""
        response = client.post(
            f"{BASE}/tools/",
            json=_tool_payload(category.id, owner_department="InvalidDept"),
        )
        assert response.status_code == 400


# ──────────────────────────── PUT /tools/{id} ─────────────────────────────────


class TestUpdateTool:
    """Tests pour PUT /api/v1/tools/{tool_id}."""

    def _create(self, client: object, category: CategoryModel) -> int:
        """Crée un outil et retourne son ID.

        Args:
            client: Client HTTP de test.
            category: Catégorie de test.

        Returns:
            ID de l'outil créé.
        """
        resp = client.post(f"{BASE}/tools/", json=_tool_payload(category.id))
        return resp.json()["id"]

    def test_update_tool_name(self, client, category):
        """Mettre à jour le nom retourne 200 avec le nouveau nom."""
        tool_id = self._create(client, category)
        response = client.put(f"{BASE}/tools/{tool_id}", json={"name": "Slack Pro"})
        assert response.status_code == 200
        assert response.json()["name"] == "Slack Pro"

    def test_update_tool_status(self, client, category):
        """Changer le statut en deprecated fonctionne."""
        tool_id = self._create(client, category)
        response = client.put(f"{BASE}/tools/{tool_id}", json={"status": "deprecated"})
        assert response.status_code == 200
        assert response.json()["status"] == "deprecated"

    def test_update_tool_monthly_cost(self, client, category):
        """Mettre à jour monthly_cost retourne la nouvelle valeur."""
        tool_id = self._create(client, category)
        response = client.put(f"{BASE}/tools/{tool_id}", json={"monthly_cost": "49.99"})
        assert response.status_code == 200
        assert Decimal(response.json()["monthly_cost"]) == Decimal("49.99")

    def test_update_tool_preserves_other_fields(self, client, category):
        """Une mise à jour partielle ne modifie pas les champs non fournis."""
        tool_id = self._create(client, category)
        response = client.put(f"{BASE}/tools/{tool_id}", json={"name": "Slack New"})
        data = response.json()
        assert data["vendor"] == "Salesforce"
        assert data["owner_department"] == "Engineering"
        assert data["status"] == "active"

    def test_update_tool_not_found(self, client):
        """Mettre à jour un ID inexistant retourne 404."""
        response = client.put(f"{BASE}/tools/9999", json={"name": "Ghost"})
        assert response.status_code == 404

    def test_update_tool_invalid_category(self, client, category):
        """Mettre à jour avec une catégorie inexistante retourne 400."""
        tool_id = self._create(client, category)
        response = client.put(f"{BASE}/tools/{tool_id}", json={"category_id": 9999})
        assert response.status_code == 400

    def test_update_tool_invalid_url(self, client, category):
        """Mettre à jour avec une URL invalide retourne 400."""
        tool_id = self._create(client, category)
        response = client.put(f"{BASE}/tools/{tool_id}", json={"website_url": "not-a-url"})
        assert response.status_code == 400

    def test_update_tool_returns_detail_structure(self, client, category):
        """La réponse PUT contient la structure complète ToolDetail."""
        tool_id = self._create(client, category)
        response = client.put(f"{BASE}/tools/{tool_id}", json={"name": "Updated"})
        assert response.status_code == 200
        data = response.json()
        assert "usage_metrics" in data
        assert "total_monthly_cost" in data
        assert "updated_at" in data
        assert "last_30_days" in data["usage_metrics"]
