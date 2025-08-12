"""Tests pour les endpoints de tâches avec authentification."""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.memory_store import task_store
from src.models.user_store import user_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_stores():
    """Reset les stores avant chaque test."""
    task_store._tasks = {}
    task_store._next_id = 1
    user_store._users = {}
    user_store._users_by_username = {}
    user_store._users_by_email = {}
    user_store._next_id = 1


@pytest.fixture
def user1_data():
    """Données du premier utilisateur."""
    return {
        "username": "user1",
        "email": "user1@example.com",
        "password": "password123",
        "full_name": "User One",
    }


@pytest.fixture
def user2_data():
    """Données du deuxième utilisateur."""
    return {
        "username": "user2",
        "email": "user2@example.com",
        "password": "password456",
        "full_name": "User Two",
    }


@pytest.fixture
def auth_user1(user1_data):
    """Utilisateur 1 enregistré et connecté."""
    # S'enregistrer
    client.post("/api/v1/auth/register", json=user1_data)

    # Se connecter
    login_data = {
        "username": user1_data["username"],
        "password": user1_data["password"],
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    return {"headers": {"Authorization": f"Bearer {token}"}, "user_data": user1_data}


@pytest.fixture
def auth_user2(user2_data):
    """Utilisateur 2 enregistré et connecté."""
    # S'enregistrer
    client.post("/api/v1/auth/register", json=user2_data)

    # Se connecter
    login_data = {
        "username": user2_data["username"],
        "password": user2_data["password"],
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    return {"headers": {"Authorization": f"Bearer {token}"}, "user_data": user2_data}


def test_create_task_requires_auth():
    """Test que la création de tâche nécessite une authentification."""
    task_data = {"title": "Test Task"}
    response = client.post("/api/v1/tasks/", json=task_data)

    assert response.status_code == 401


def test_create_task_with_auth(auth_user1):
    """Test de création de tâche avec authentification."""
    task_data = {"title": "Authenticated Task", "priority": "High"}

    response = client.post(
        "/api/v1/tasks/", json=task_data, headers=auth_user1["headers"]
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Authenticated Task"
    assert data["priority"] == "High"
    assert data["user_id"] == 1  # Premier utilisateur


def test_get_tasks_requires_auth():
    """Test que la récupération des tâches nécessite une authentification."""
    response = client.get("/api/v1/tasks/")

    assert response.status_code == 401


def test_get_tasks_empty_for_new_user(auth_user1):
    """Test que les tâches sont vides pour un nouvel utilisateur."""
    response = client.get("/api/v1/tasks/", headers=auth_user1["headers"])

    assert response.status_code == 200
    assert response.json() == []


def test_get_tasks_user_isolation(auth_user1, auth_user2):
    """Test que chaque utilisateur voit seulement ses propres tâches."""
    # User 1 crée une tâche
    task1_data = {"title": "User 1 Task"}
    client.post("/api/v1/tasks/", json=task1_data, headers=auth_user1["headers"])

    # User 2 crée une tâche
    task2_data = {"title": "User 2 Task"}
    client.post("/api/v1/tasks/", json=task2_data, headers=auth_user2["headers"])

    # User 1 récupère ses tâches
    response1 = client.get("/api/v1/tasks/", headers=auth_user1["headers"])
    assert response1.status_code == 200
    tasks1 = response1.json()
    assert len(tasks1) == 1
    assert tasks1[0]["title"] == "User 1 Task"
    assert tasks1[0]["user_id"] == 1

    # User 2 récupère ses tâches
    response2 = client.get("/api/v1/tasks/", headers=auth_user2["headers"])
    assert response2.status_code == 200
    tasks2 = response2.json()
    assert len(tasks2) == 1
    assert tasks2[0]["title"] == "User 2 Task"
    assert tasks2[0]["user_id"] == 2


def test_get_task_by_id_requires_auth():
    """Test que la récupération d'une tâche par ID nécessite une authentification."""
    response = client.get("/api/v1/tasks/1")

    assert response.status_code == 401


def test_get_task_user_cannot_access_other_user_task(auth_user1, auth_user2):
    """Test qu'un utilisateur ne peut pas accéder aux tâches d'un autre."""
    # User 1 crée une tâche
    task_data = {"title": "Private Task"}
    create_response = client.post(
        "/api/v1/tasks/", json=task_data, headers=auth_user1["headers"]
    )
    task_id = create_response.json()["id"]

    # User 2 essaie d'accéder à la tâche de User 1
    response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_user2["headers"])

    assert response.status_code == 404  # La tâche "n'existe pas" pour user 2


def test_update_task_requires_auth():
    """Test que la mise à jour d'une tâche nécessite une authentification."""
    update_data = {"title": "Updated Task"}
    response = client.put("/api/v1/tasks/1", json=update_data)

    assert response.status_code == 401


def test_update_task_user_cannot_update_other_user_task(auth_user1, auth_user2):
    """Test qu'un utilisateur ne peut pas modifier les tâches d'un autre."""
    # User 1 crée une tâche
    task_data = {"title": "Original Task"}
    create_response = client.post(
        "/api/v1/tasks/", json=task_data, headers=auth_user1["headers"]
    )
    task_id = create_response.json()["id"]

    # User 2 essaie de modifier la tâche de User 1
    update_data = {"title": "Hacked Task"}
    response = client.put(
        f"/api/v1/tasks/{task_id}", json=update_data, headers=auth_user2["headers"]
    )

    assert response.status_code == 404


def test_delete_task_requires_auth():
    """Test que la suppression d'une tâche nécessite une authentification."""
    response = client.delete("/api/v1/tasks/1")

    assert response.status_code == 401


def test_delete_task_user_cannot_delete_other_user_task(auth_user1, auth_user2):
    """Test qu'un utilisateur ne peut pas supprimer les tâches d'un autre."""
    # User 1 crée une tâche
    task_data = {"title": "Task to Protect"}
    create_response = client.post(
        "/api/v1/tasks/", json=task_data, headers=auth_user1["headers"]
    )
    task_id = create_response.json()["id"]

    # User 2 essaie de supprimer la tâche de User 1
    response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_user2["headers"])

    assert response.status_code == 404


def test_complete_task_workflow_with_auth(auth_user1):
    """Test d'un workflow complet de tâche avec authentification."""
    headers = auth_user1["headers"]

    # 1. Créer une tâche
    due_date = (datetime.now() + timedelta(days=7)).isoformat()
    task_data = {
        "title": "Workflow Task",
        "description": "Task for authenticated workflow",
        "priority": "Medium",
        "due_date": due_date,
    }
    create_response = client.post("/api/v1/tasks/", json=task_data, headers=headers)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # 2. Récupérer la tâche
    get_response = client.get(f"/api/v1/tasks/{task_id}", headers=headers)
    assert get_response.status_code == 200
    task = get_response.json()
    assert task["user_id"] == 1

    # 3. Mettre à jour la tâche
    update_data = {"completed": True, "priority": "High"}
    update_response = client.put(
        f"/api/v1/tasks/{task_id}", json=update_data, headers=headers
    )
    assert update_response.status_code == 200
    updated_task = update_response.json()
    assert updated_task["completed"] is True
    assert updated_task["completed_at"] is not None
    assert updated_task["priority"] == "High"

    # 4. Vérifier dans la liste
    list_response = client.get("/api/v1/tasks/", headers=headers)
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id
    assert tasks[0]["completed"] is True

    # 5. Supprimer la tâche
    delete_response = client.delete(f"/api/v1/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204

    # 6. Vérifier qu'elle n'existe plus
    final_list_response = client.get("/api/v1/tasks/", headers=headers)
    assert final_list_response.status_code == 200
    assert final_list_response.json() == []


def test_invalid_token_access():
    """Test d'accès avec un token invalide."""
    headers = {"Authorization": "Bearer invalid_token"}

    # Toutes les opérations doivent échouer
    assert client.get("/api/v1/tasks/", headers=headers).status_code == 401
    assert (
        client.post(
            "/api/v1/tasks/", json={"title": "Test"}, headers=headers
        ).status_code
        == 401
    )
    assert client.get("/api/v1/tasks/1", headers=headers).status_code == 401
    assert (
        client.put(
            "/api/v1/tasks/1", json={"title": "Test"}, headers=headers
        ).status_code
        == 401
    )
    assert client.delete("/api/v1/tasks/1", headers=headers).status_code == 401


def test_expired_token_scenario():
    """Test conceptuel d'un token expiré (simulation)."""
    # Note: Pour un vrai test de token expiré, il faudrait manipuler le temps
    # ou créer un token avec une expiration très courte
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired"}

    response = client.get("/api/v1/tasks/", headers=headers)
    assert response.status_code == 401
