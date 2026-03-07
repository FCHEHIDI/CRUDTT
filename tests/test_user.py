"""Tests des endpoints User."""


def test_root(client):
    """Le health-check renvoie status ok."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_create_user(client):
    """Créer un utilisateur renvoie 201."""
    response = client.post(
        "/users/",
        json={"username": "fares", "email": "fares@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "fares"
    assert data["email"] == "fares@example.com"
    assert "id" in data


def test_create_user_duplicate_email(client):
    """Un email dupliqué renvoie 409."""
    payload = {"username": "fares", "email": "fares@example.com"}
    client.post("/users/", json=payload)
    response = client.post(
        "/users/", json={"username": "fares2", "email": "fares@example.com"}
    )
    assert response.status_code == 409


def test_list_users(client):
    """Lister les utilisateurs après création."""
    client.post("/users/", json={"username": "a", "email": "a@test.com"})
    client.post("/users/", json={"username": "b", "email": "b@test.com"})
    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user(client):
    """Récupérer un utilisateur par ID."""
    create_resp = client.post(
        "/users/", json={"username": "fares", "email": "fares@test.com"}
    )
    user_id = create_resp.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "fares"


def test_get_user_not_found(client):
    """Un ID inexistant renvoie 404."""
    response = client.get("/users/9999")
    assert response.status_code == 404


def test_delete_user(client):
    """Supprimer un utilisateur renvoie 204."""
    create_resp = client.post(
        "/users/", json={"username": "fares", "email": "fares@test.com"}
    )
    user_id = create_resp.json()["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
