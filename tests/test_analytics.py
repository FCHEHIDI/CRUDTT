"""Tests endpoints Analytics (GET /api/v1/analytics/*)."""

from decimal import Decimal

import pytest

from app.models.category import Category as CategoryModel
from app.models.tool import Tool as ToolModel

BASE = "/api/v1/analytics"


# ──────────────────────────── Fixtures ────────────────────────────────────────


@pytest.fixture()
def category(db):
    """Crée une catégorie de test dans la base SQLite.

    Args:
        db: Session de base de données de test.

    Returns:
        Instance CategoryModel persistée.
    """
    cat = CategoryModel(name="Dev Tools", description="Outils de développement")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@pytest.fixture()
def category2(db):
    """Crée une seconde catégorie de test.

    Args:
        db: Session de base de données de test.

    Returns:
        Instance CategoryModel persistée.
    """
    cat = CategoryModel(name="Marketing Tools", description="Outils marketing")
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def _add_tool(
    db,
    category_id: int,
    *,
    name: str = "TestTool",
    vendor: str = "Acme",
    monthly_cost: str = "100.00",
    active_users_count: int = 10,
    owner_department: str = "Engineering",
    status: str = "active",
) -> ToolModel:
    """Insère un Tool directement en base sans passer par l'API.

    Args:
        db: Session de base de données de test.
        category_id: ID de la catégorie associée.
        name: Nom de l'outil.
        vendor: Nom du fournisseur.
        monthly_cost: Coût mensuel (string converti en Decimal).
        active_users_count: Nombre d'utilisateurs actifs.
        owner_department: Département propriétaire.
        status: Statut de l'outil.

    Returns:
        Instance ToolModel persistée et rafraîchie.
    """
    tool = ToolModel(
        name=name,
        vendor=vendor,
        category_id=category_id,
        monthly_cost=Decimal(monthly_cost),
        active_users_count=active_users_count,
        owner_department=owner_department,
        status=status,
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool


# ──────────────────────────── department-costs ────────────────────────────────


class TestDepartmentCosts:
    """Tests pour GET /api/v1/analytics/department-costs."""

    def test_empty_db_returns_empty_data(self, client):
        """Sans outils actifs, data est vide et summary cohérent."""
        response = client.get(f"{BASE}/department-costs")
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert Decimal(str(body["summary"]["total_company_cost"])) == Decimal("0.00")
        assert body["summary"]["departments_count"] == 0
        assert body["summary"]["most_expensive_department"] is None

    def test_inactive_tools_excluded(self, client, db, category):
        """Les outils non-actifs (deprecated, trial) ne sont pas comptés."""
        _add_tool(db, category.id, name="Active", status="active", monthly_cost="50.00")
        _add_tool(db, category.id, name="Old", status="deprecated", monthly_cost="200.00")
        response = client.get(f"{BASE}/department-costs")
        assert response.status_code == 200
        body = response.json()
        assert body["summary"]["departments_count"] == 1
        assert Decimal(str(body["summary"]["total_company_cost"])) == Decimal("50.00")

    def test_single_department_structure(self, client, db, category):
        """Un département retourne la structure complète avec tous les champs."""
        _add_tool(db, category.id, name="Tool A", owner_department="Engineering",
                  monthly_cost="100.00", active_users_count=10)
        response = client.get(f"{BASE}/department-costs")
        assert response.status_code == 200
        item = response.json()["data"][0]
        assert item["department"] == "Engineering"
        assert Decimal(str(item["total_cost"])) == Decimal("100.00")
        assert item["tools_count"] == 1
        assert item["total_users"] == 10
        assert Decimal(str(item["average_cost_per_tool"])) == Decimal("100.00")
        assert item["cost_percentage"] == 100.0

    def test_cost_percentage_sums_to_100(self, client, db, category, category2):
        """Les cost_percentage de tous les départements somment à 100.0."""
        _add_tool(db, category.id, name="ToolA", owner_department="Engineering",
                  monthly_cost="300.00")
        _add_tool(db, category2.id, name="ToolB", owner_department="Sales",
                  monthly_cost="700.00")
        response = client.get(f"{BASE}/department-costs")
        items = response.json()["data"]
        total_pct = sum(item["cost_percentage"] for item in items)
        assert abs(total_pct - 100.0) < 0.2

    def test_most_expensive_department(self, client, db, category, category2):
        """most_expensive_department pointe vers le département avec le plus grand coût."""
        _add_tool(db, category.id, name="Cheap", owner_department="HR",
                  monthly_cost="50.00")
        _add_tool(db, category2.id, name="Expensive", owner_department="Engineering",
                  monthly_cost="500.00")
        body = client.get(f"{BASE}/department-costs").json()
        assert body["summary"]["most_expensive_department"] == "Engineering"

    def test_sort_by_department_asc(self, client, db, category, category2):
        """sort_by=department&order=asc retourne les départements par ordre alphabétique."""
        _add_tool(db, category.id, name="T1", owner_department="Sales")
        _add_tool(db, category2.id, name="T2", owner_department="Engineering")
        response = client.get(f"{BASE}/department-costs?sort_by=department&order=asc")
        depts = [d["department"] for d in response.json()["data"]]
        assert depts == sorted(depts)

    def test_sort_by_total_cost_desc(self, client, db, category, category2):
        """sort_by=total_cost&order=desc (défaut) retourne le plus cher en premier."""
        _add_tool(db, category.id, name="T1", owner_department="HR",
                  monthly_cost="50.00")
        _add_tool(db, category2.id, name="T2", owner_department="Engineering",
                  monthly_cost="500.00")
        response = client.get(f"{BASE}/department-costs?sort_by=total_cost&order=desc")
        costs = [float(d["total_cost"]) for d in response.json()["data"]]
        assert costs == sorted(costs, reverse=True)

    def test_multiple_tools_same_department_aggregated(self, client, db, category):
        """Deux outils dans le même département sont agrégés en une seule ligne."""
        _add_tool(db, category.id, name="T1", owner_department="Engineering",
                  monthly_cost="100.00", active_users_count=5)
        _add_tool(db, category.id, name="T2", owner_department="Engineering",
                  monthly_cost="200.00", active_users_count=15)
        body = client.get(f"{BASE}/department-costs").json()
        assert len(body["data"]) == 1
        item = body["data"][0]
        assert Decimal(str(item["total_cost"])) == Decimal("300.00")
        assert item["tools_count"] == 2
        assert item["total_users"] == 20
        assert Decimal(str(item["average_cost_per_tool"])) == Decimal("150.00")


# ──────────────────────────── expensive-tools ─────────────────────────────────


class TestExpensiveTools:
    """Tests pour GET /api/v1/analytics/expensive-tools."""

    def test_empty_db_returns_empty_data(self, client):
        """Sans outils actifs, data est vide et analysis cohérente."""
        response = client.get(f"{BASE}/expensive-tools")
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["analysis"]["total_tools_analyzed"] == 0
        assert Decimal(str(body["analysis"]["potential_savings_identified"])) == Decimal("0.00")

    def test_inactive_tools_excluded(self, client, db, category):
        """Les outils deprecated ne remontent pas dans le top."""
        _add_tool(db, category.id, name="Active", monthly_cost="100.00", status="active")
        _add_tool(db, category.id, name="Dead", monthly_cost="9999.00", status="deprecated")
        body = client.get(f"{BASE}/expensive-tools").json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Active"

    def test_sorted_by_cost_desc(self, client, db, category):
        """Les outils sont triés du plus coûteux au moins coûteux."""
        _add_tool(db, category.id, name="Cheap", monthly_cost="10.00")
        _add_tool(db, category.id, name="Mid", monthly_cost="50.00")
        _add_tool(db, category.id, name="Expensive", monthly_cost="200.00")
        body = client.get(f"{BASE}/expensive-tools").json()
        costs = [float(item["monthly_cost"]) for item in body["data"]]
        assert costs == sorted(costs, reverse=True)

    def test_limit_param(self, client, db, category):
        """limit=2 retourne au maximum 2 outils."""
        for i in range(5):
            _add_tool(db, category.id, name=f"Tool{i}", monthly_cost=f"{(i+1)*10}.00")
        body = client.get(f"{BASE}/expensive-tools?limit=2").json()
        assert len(body["data"]) == 2

    def test_limit_invalid_returns_400(self, client):
        """limit=-5 retourne 400 (RequestValidationError → handler custom retourne 400)."""
        response = client.get(f"{BASE}/expensive-tools?limit=-5")
        assert response.status_code == 400

    def test_min_cost_filter(self, client, db, category):
        """min_cost filtre les outils en dessous du seuil."""
        _add_tool(db, category.id, name="Cheap", monthly_cost="10.00")
        _add_tool(db, category.id, name="Expensive", monthly_cost="500.00")
        body = client.get(f"{BASE}/expensive-tools?min_cost=100").json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Expensive"

    def test_tool_with_zero_users_has_null_cost_per_user(self, client, db, category):
        """Un outil avec 0 utilisateurs a cost_per_user=null (division par zéro évitée)."""
        _add_tool(db, category.id, name="NoUsers", active_users_count=0)
        body = client.get(f"{BASE}/expensive-tools").json()
        assert body["data"][0]["cost_per_user"] is None

    def test_tool_with_zero_users_has_efficiency_rating_low(self, client, db, category):
        """Un outil avec 0 utilisateurs a efficiency_rating='low'."""
        _add_tool(db, category.id, name="NoUsers", active_users_count=0)
        body = client.get(f"{BASE}/expensive-tools").json()
        assert body["data"][0]["efficiency_rating"] == "low"

    def test_efficiency_rating_excellent(self, client, db, category):
        """Un outil très bon marché par rapport à la moyenne a rating='excellent'."""
        # avg_cpu = 100/10 = 10€ ; outil = 1/10 = 0.1€ → ratio=0.01 < 0.5 → excellent
        _add_tool(db, category.id, name="Expensive", monthly_cost="100.00",
                  active_users_count=10)
        _add_tool(db, category.id, name="Cheap", monthly_cost="1.00",
                  active_users_count=10)
        body = client.get(f"{BASE}/expensive-tools").json()
        ratings = {item["name"]: item["efficiency_rating"] for item in body["data"]}
        assert ratings["Cheap"] == "excellent"

    def test_potential_savings_only_low_rated(self, client, db, category):
        """potential_savings_identified = somme des coûts des outils 'low' seulement."""
        # Deux outils avec 0 users → efficiency_rating='low'
        _add_tool(db, category.id, name="LowA", monthly_cost="100.00",
                  active_users_count=0)
        _add_tool(db, category.id, name="LowB", monthly_cost="200.00",
                  active_users_count=0)
        body = client.get(f"{BASE}/expensive-tools").json()
        assert Decimal(str(body["analysis"]["potential_savings_identified"])) == Decimal("300.00")

    def test_response_fields_present(self, client, db, category):
        """Chaque item contient tous les champs attendus."""
        _add_tool(db, category.id, name="T1")
        item = client.get(f"{BASE}/expensive-tools").json()["data"][0]
        for field in ("id", "name", "monthly_cost", "active_users_count",
                      "cost_per_user", "department", "vendor", "efficiency_rating"):
            assert field in item, f"Champ manquant: {field}"


# ──────────────────────────── tools-by-category ───────────────────────────────


class TestToolsByCategory:
    """Tests pour GET /api/v1/analytics/tools-by-category."""

    def test_empty_db_returns_empty_data(self, client):
        """Sans outils actifs, data est vide et insights sont null."""
        response = client.get(f"{BASE}/tools-by-category")
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["insights"]["most_expensive_category"] is None
        assert body["insights"]["most_efficient_category"] is None

    def test_inactive_tools_excluded(self, client, db, category):
        """Les outils deprecated ne sont pas comptés dans les catégories."""
        _add_tool(db, category.id, name="Active", status="active")
        _add_tool(db, category.id, name="Dead", status="deprecated", monthly_cost="9999.00")
        body = client.get(f"{BASE}/tools-by-category").json()
        assert len(body["data"]) == 1
        assert body["data"][0]["tools_count"] == 1

    def test_category_structure(self, client, db, category):
        """Une catégorie retourne la structure complète."""
        _add_tool(db, category.id, name="T1", monthly_cost="100.00",
                  active_users_count=10)
        item = client.get(f"{BASE}/tools-by-category").json()["data"][0]
        assert item["category_name"] == "Dev Tools"
        assert item["tools_count"] == 1
        assert Decimal(str(item["total_cost"])) == Decimal("100.00")
        assert item["total_users"] == 10
        assert item["percentage_of_budget"] == 100.0
        assert Decimal(str(item["average_cost_per_user"])) == Decimal("10.00")

    def test_average_cost_per_user_null_when_no_users(self, client, db, category):
        """average_cost_per_user est null si tous les outils ont 0 utilisateurs."""
        _add_tool(db, category.id, name="T1", monthly_cost="100.00",
                  active_users_count=0)
        item = client.get(f"{BASE}/tools-by-category").json()["data"][0]
        assert item["average_cost_per_user"] is None

    def test_percentage_of_budget_sums_to_100(self, client, db, category, category2):
        """La somme des percentage_of_budget de toutes les catégories ≈ 100."""
        _add_tool(db, category.id, name="T1", monthly_cost="400.00")
        _add_tool(db, category2.id, name="T2", monthly_cost="600.00")
        items = client.get(f"{BASE}/tools-by-category").json()["data"]
        total = sum(item["percentage_of_budget"] for item in items)
        assert abs(total - 100.0) < 0.2

    def test_most_expensive_category(self, client, db, category, category2):
        """most_expensive_category pointe vers la catégorie au total le plus élevé."""
        _add_tool(db, category.id, name="T1", monthly_cost="100.00")
        _add_tool(db, category2.id, name="T2", monthly_cost="900.00")
        insights = client.get(f"{BASE}/tools-by-category").json()["insights"]
        assert insights["most_expensive_category"] == "Marketing Tools"

    def test_most_efficient_category(self, client, db, category, category2):
        """most_efficient_category a le plus petit average_cost_per_user."""
        # category = 100€ / 100 users = 1€/user → plus efficace
        _add_tool(db, category.id, name="T1", monthly_cost="100.00",
                  active_users_count=100)
        # category2 = 100€ / 2 users = 50€/user
        _add_tool(db, category2.id, name="T2", monthly_cost="100.00",
                  active_users_count=2)
        insights = client.get(f"{BASE}/tools-by-category").json()["insights"]
        assert insights["most_efficient_category"] == "Dev Tools"

    def test_multiple_tools_same_category_aggregated(self, client, db, category):
        """Plusieurs outils dans la même catégorie sont agrégés."""
        _add_tool(db, category.id, name="T1", monthly_cost="100.00",
                  active_users_count=5)
        _add_tool(db, category.id, name="T2", monthly_cost="200.00",
                  active_users_count=15)
        items = client.get(f"{BASE}/tools-by-category").json()["data"]
        assert len(items) == 1
        assert Decimal(str(items[0]["total_cost"])) == Decimal("300.00")
        assert items[0]["tools_count"] == 2
        assert items[0]["total_users"] == 20


# ──────────────────────────── low-usage-tools ─────────────────────────────────


class TestLowUsageTools:
    """Tests pour GET /api/v1/analytics/low-usage-tools."""

    def test_empty_db_returns_empty_data(self, client):
        """Sans outils actifs, data est vide et savings_analysis à zéro."""
        response = client.get(f"{BASE}/low-usage-tools")
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert Decimal(str(body["savings_analysis"]["potential_monthly_savings"])) == Decimal("0.00")
        assert Decimal(str(body["savings_analysis"]["potential_annual_savings"])) == Decimal("0.00")
        assert body["savings_analysis"]["total_underutilized_tools"] == 0

    def test_only_tools_under_threshold_returned(self, client, db, category):
        """Seuls les outils avec active_users_count <= max_users sont retournés."""
        _add_tool(db, category.id, name="Low", active_users_count=3)
        _add_tool(db, category.id, name="High", active_users_count=50)
        body = client.get(f"{BASE}/low-usage-tools?max_users=5").json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Low"

    def test_inactive_tools_excluded(self, client, db, category):
        """Les outils deprecated avec peu d'utilisateurs ne remontent pas."""
        _add_tool(db, category.id, name="Active", active_users_count=2, status="active")
        _add_tool(db, category.id, name="Dead", active_users_count=1, status="deprecated")
        body = client.get(f"{BASE}/low-usage-tools").json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Active"

    def test_warning_level_high_zero_users(self, client, db, category):
        """Un outil avec 0 utilisateurs a warning_level='high'."""
        _add_tool(db, category.id, name="NoUsers", active_users_count=0,
                  monthly_cost="10.00")
        item = client.get(f"{BASE}/low-usage-tools").json()["data"][0]
        assert item["warning_level"] == "high"
        assert item["cost_per_user"] is None

    def test_warning_level_high_expensive_per_user(self, client, db, category):
        """cost/user > 50€ → warning_level='high'."""
        # 300€ / 3 users = 100€/user > 50 → high
        _add_tool(db, category.id, name="Expensive", active_users_count=3,
                  monthly_cost="300.00")
        item = client.get(f"{BASE}/low-usage-tools").json()["data"][0]
        assert item["warning_level"] == "high"

    def test_warning_level_medium(self, client, db, category):
        """20 ≤ cost/user ≤ 50 → warning_level='medium'."""
        # 100€ / 4 users = 25€/user → medium
        _add_tool(db, category.id, name="Medium", active_users_count=4,
                  monthly_cost="100.00")
        item = client.get(f"{BASE}/low-usage-tools").json()["data"][0]
        assert item["warning_level"] == "medium"

    def test_warning_level_low(self, client, db, category):
        """cost/user < 20€ → warning_level='low'."""
        # 50€ / 5 users = 10€/user < 20 → low
        _add_tool(db, category.id, name="Efficient", active_users_count=5,
                  monthly_cost="50.00")
        item = client.get(f"{BASE}/low-usage-tools").json()["data"][0]
        assert item["warning_level"] == "low"

    def test_potential_savings_high_and_medium_only(self, client, db, category):
        """potential_monthly_savings = somme des coûts high + medium uniquement."""
        # high: 0 users, 100€
        _add_tool(db, category.id, name="HighTool", active_users_count=0,
                  monthly_cost="100.00")
        # medium: 25€/user (100/4), 100€
        _add_tool(db, category.id, name="MedTool", active_users_count=4,
                  monthly_cost="100.00")
        # low: 10€/user (50/5), 50€ — ne compte pas
        _add_tool(db, category.id, name="LowTool", active_users_count=5,
                  monthly_cost="50.00")
        body = client.get(f"{BASE}/low-usage-tools").json()
        assert Decimal(str(body["savings_analysis"]["potential_monthly_savings"])) == Decimal("200.00")

    def test_potential_annual_savings_is_12x_monthly(self, client, db, category):
        """potential_annual_savings = potential_monthly_savings × 12."""
        _add_tool(db, category.id, name="H", active_users_count=0,
                  monthly_cost="100.00")
        body = client.get(f"{BASE}/low-usage-tools").json()
        monthly = Decimal(str(body["savings_analysis"]["potential_monthly_savings"]))
        annual = Decimal(str(body["savings_analysis"]["potential_annual_savings"]))
        assert annual == monthly * 12

    def test_max_users_param(self, client, db, category):
        """max_users=0 retourne uniquement les outils à 0 utilisateurs."""
        _add_tool(db, category.id, name="Zero", active_users_count=0)
        _add_tool(db, category.id, name="One", active_users_count=1)
        body = client.get(f"{BASE}/low-usage-tools?max_users=0").json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Zero"

    def test_sorted_by_cost_desc(self, client, db, category):
        """Les outils sont triés du plus coûteux au moins coûteux."""
        _add_tool(db, category.id, name="Cheap", active_users_count=1,
                  monthly_cost="10.00")
        _add_tool(db, category.id, name="Expensive", active_users_count=2,
                  monthly_cost="999.00")
        body = client.get(f"{BASE}/low-usage-tools").json()
        costs = [float(item["monthly_cost"]) for item in body["data"]]
        assert costs == sorted(costs, reverse=True)


# ──────────────────────────── vendor-summary ──────────────────────────────────


class TestVendorSummary:
    """Tests pour GET /api/v1/analytics/vendor-summary."""

    def test_empty_db_returns_empty_data(self, client):
        """Sans outils actifs, data est vide et insights sont null."""
        response = client.get(f"{BASE}/vendor-summary")
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["vendor_insights"]["most_expensive_vendor"] is None
        assert body["vendor_insights"]["most_efficient_vendor"] is None
        assert body["vendor_insights"]["single_tool_vendors"] == 0

    def test_inactive_tools_excluded(self, client, db, category):
        """Les outils deprecated ne sont pas agrégés par vendor."""
        _add_tool(db, category.id, name="Active", vendor="VendorX", status="active")
        _add_tool(db, category.id, name="Dead", vendor="VendorY", status="deprecated")
        body = client.get(f"{BASE}/vendor-summary").json()
        vendors = [item["vendor"] for item in body["data"]]
        assert "VendorX" in vendors
        assert "VendorY" not in vendors

    def test_vendor_structure(self, client, db, category):
        """Un vendor retourne la structure complète."""
        _add_tool(db, category.id, name="T1", vendor="Atlassian",
                  monthly_cost="100.00", active_users_count=10,
                  owner_department="Engineering")
        item = client.get(f"{BASE}/vendor-summary").json()["data"][0]
        assert item["vendor"] == "Atlassian"
        assert item["tools_count"] == 1
        assert Decimal(str(item["total_monthly_cost"])) == Decimal("100.00")
        assert item["total_users"] == 10
        assert Decimal(str(item["average_cost_per_user"])) == Decimal("10.00")
        assert "vendor_efficiency" in item
        assert "departments" in item

    def test_departments_alphabetically_sorted(self, client, db, category, category2):
        """Les départements d'un vendor sont triés alphabétiquement."""
        _add_tool(db, category.id, name="T1", vendor="Acme",
                  owner_department="Sales")
        _add_tool(db, category2.id, name="T2", vendor="Acme",
                  owner_department="Engineering")
        item = client.get(f"{BASE}/vendor-summary").json()["data"][0]
        depts = item["departments"].split(",")
        assert depts == sorted(depts)

    def test_departments_no_duplicates(self, client, db, category, category2):
        """Le même département n'est pas listé en doublon pour un vendor."""
        _add_tool(db, category.id, name="T1", vendor="Acme",
                  owner_department="Engineering")
        _add_tool(db, category2.id, name="T2", vendor="Acme",
                  owner_department="Engineering")
        item = client.get(f"{BASE}/vendor-summary").json()["data"][0]
        depts = item["departments"].split(",")
        assert len(depts) == len(set(depts))

    def test_single_tool_vendors_count(self, client, db, category, category2):
        """single_tool_vendors compte les vendors avec exactement 1 outil actif."""
        _add_tool(db, category.id, name="T1", vendor="Solo")
        _add_tool(db, category.id, name="T2", vendor="Multi")
        _add_tool(db, category2.id, name="T3", vendor="Multi")
        body = client.get(f"{BASE}/vendor-summary").json()
        assert body["vendor_insights"]["single_tool_vendors"] == 1

    def test_most_expensive_vendor(self, client, db, category, category2):
        """most_expensive_vendor pointe vers le vendor au coût total le plus élevé."""
        _add_tool(db, category.id, name="T1", vendor="Cheap", monthly_cost="50.00")
        _add_tool(db, category2.id, name="T2", vendor="Pricey", monthly_cost="999.00")
        insights = client.get(f"{BASE}/vendor-summary").json()["vendor_insights"]
        assert insights["most_expensive_vendor"] == "Pricey"

    def test_most_efficient_vendor(self, client, db, category, category2):
        """most_efficient_vendor a le plus petit average_cost_per_user."""
        # Efficient: 100€ / 100 users = 1€/user
        _add_tool(db, category.id, name="T1", vendor="Efficient",
                  monthly_cost="100.00", active_users_count=100)
        # Wasteful: 100€ / 2 users = 50€/user
        _add_tool(db, category2.id, name="T2", vendor="Wasteful",
                  monthly_cost="100.00", active_users_count=2)
        insights = client.get(f"{BASE}/vendor-summary").json()["vendor_insights"]
        assert insights["most_efficient_vendor"] == "Efficient"

    def test_vendor_efficiency_excellent(self, client, db, category):
        """average_cost_per_user < 5€ → vendor_efficiency='excellent'."""
        # 40€ / 10 users = 4€/user < 5 → excellent
        _add_tool(db, category.id, name="T1", vendor="GoodVendor",
                  monthly_cost="40.00", active_users_count=10)
        item = client.get(f"{BASE}/vendor-summary").json()["data"][0]
        assert item["vendor_efficiency"] == "excellent"

    def test_vendor_efficiency_poor(self, client, db, category):
        """average_cost_per_user > 25€ → vendor_efficiency='poor'."""
        # 300€ / 10 users = 30€/user > 25 → poor
        _add_tool(db, category.id, name="T1", vendor="BadVendor",
                  monthly_cost="300.00", active_users_count=10)
        item = client.get(f"{BASE}/vendor-summary").json()["data"][0]
        assert item["vendor_efficiency"] == "poor"

    def test_tools_without_vendor_excluded(self, client, db, category):
        """Les outils sans vendor (NULL) ne sont pas comptés."""
        tool = ToolModel(
            name="NoVendor",
            vendor=None,
            category_id=category.id,
            monthly_cost=Decimal("100.00"),
            active_users_count=5,
            owner_department="Engineering",
            status="active",
        )
        db.add(tool)
        db.commit()
        body = client.get(f"{BASE}/vendor-summary").json()
        assert body["data"] == []
