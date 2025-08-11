"""Tests pour les endpoints d'authentification."""
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.user_store import user_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_user_store():
    """Reset le store utilisateur avant chaque test."""
    user_store._users = {}
    user_store._users_by_username = {}
    user_store._users_by_email = {}
    user_store._next_id = 1


@pytest.fixture
def sample_user_data():
    """Données d'utilisateur exemple."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
    }


def test_register_user_success(sample_user_data):
    """Test d'enregistrement d'un utilisateur avec succès."""
    response = client.post("/api/v1/auth/register", json=sample_user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == sample_user_data["username"]
    assert data["email"] == sample_user_data["email"]
    assert data["full_name"] == sample_user_data["full_name"]
    assert data["is_active"] is True
    assert data["created_at"] is not None
    assert "password" not in data  # Le mot de passe ne doit pas être retourné


def test_register_user_minimal():
    """Test d'enregistrement avec les champs minimaux."""
    user_data = {
        "username": "minimaluser",
        "email": "minimal@example.com",
        "password": "password123",
    }

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "minimaluser"
    assert data["email"] == "minimal@example.com"
    assert data["full_name"] is None


def test_register_duplicate_username(sample_user_data):
    """Test d'enregistrement avec un nom d'utilisateur déjà utilisé."""
    # Premier utilisateur
    client.post("/api/v1/auth/register", json=sample_user_data)

    # Deuxième utilisateur avec le même nom d'utilisateur
    duplicate_user = sample_user_data.copy()
    duplicate_user["email"] = "different@example.com"

    response = client.post("/api/v1/auth/register", json=duplicate_user)

    assert response.status_code == 400
    assert "nom d'utilisateur existe déjà" in response.json()["detail"]


def test_register_duplicate_email(sample_user_data):
    """Test d'enregistrement avec un email déjà utilisé."""
    # Premier utilisateur
    client.post("/api/v1/auth/register", json=sample_user_data)

    # Deuxième utilisateur avec le même email
    duplicate_user = sample_user_data.copy()
    duplicate_user["username"] = "differentuser"

    response = client.post("/api/v1/auth/register", json=duplicate_user)

    assert response.status_code == 400
    assert "email existe déjà" in response.json()["detail"]


def test_register_invalid_email():
    """Test d'enregistrement avec un email invalide."""
    user_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "password123",
    }

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 422


def test_register_missing_required_fields():
    """Test d'enregistrement avec des champs requis manquants."""
    # Manque le mot de passe
    user_data = {"username": "testuser", "email": "test@example.com"}

    response = client.post("/api/v1/auth/register", json=user_data)

    assert response.status_code == 422


def test_login_success(sample_user_data):
    """Test de connexion avec succès."""
    # D'abord s'enregistrer
    client.post("/api/v1/auth/register", json=sample_user_data)

    # Puis se connecter
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }

    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_wrong_username():
    """Test de connexion avec un nom d'utilisateur incorrect."""
    login_data = {"username": "wronguser", "password": "somepassword"}

    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_wrong_password(sample_user_data):
    """Test de connexion avec un mot de passe incorrect."""
    # D'abord s'enregistrer
    client.post("/api/v1/auth/register", json=sample_user_data)

    # Puis essayer de se connecter avec un mauvais mot de passe
    login_data = {"username": sample_user_data["username"], "password": "wrongpassword"}

    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_get_current_user_success(sample_user_data):
    """Test de récupération des informations utilisateur."""
    # S'enregistrer
    client.post("/api/v1/auth/register", json=sample_user_data)

    # Se connecter
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    # Récupérer les informations utilisateur
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == sample_user_data["username"]
    assert data["email"] == sample_user_data["email"]
    assert data["full_name"] == sample_user_data["full_name"]


def test_get_current_user_no_token():
    """Test de récupération sans token."""
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_get_current_user_invalid_token():
    """Test de récupération avec un token invalide."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 401


def test_complete_auth_flow(sample_user_data):
    """Test du workflow complet d'authentification."""
    # 1. S'enregistrer
    register_response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert register_response.status_code == 201
    user_data = register_response.json()

    # 2. Se connecter
    login_data = {
        "username": sample_user_data["username"],
        "password": sample_user_data["password"],
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Récupérer ses informations
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()

    # Vérifier la cohérence des données
    assert me_data["id"] == user_data["id"]
    assert me_data["username"] == user_data["username"]
    assert me_data["email"] == user_data["email"]
