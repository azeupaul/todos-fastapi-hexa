from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.memory_store import task_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_task_store():
    """Reset le store avant chaque test."""
    task_store._tasks = {}
    task_store._next_id = 1


def test_create_task_minimal():
    """Test de création d'une tâche avec les champs minimaux."""
    task_data = {"title": "Test Task"}

    response = client.post("/api/v1/tasks/", json=task_data)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Task"
    assert data["description"] is None
    assert data["completed"] is False
    assert data["due_date"] is None
    assert data["priority"] == "Normal"
    assert data["created_at"] is not None
    assert data["completed_at"] is None


def test_create_task_complete():
    """Test de création d'une tâche avec tous les champs."""
    due_date = (datetime.now() + timedelta(days=7)).isoformat()
    task_data = {
        "title": "Complete Task",
        "description": "A complete task description",
        "completed": True,
        "due_date": due_date,
        "priority": "High",
    }

    response = client.post("/api/v1/tasks/", json=task_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Complete Task"
    assert data["description"] == "A complete task description"
    assert data["completed"] is True
    assert data["due_date"] == due_date
    assert data["priority"] == "High"
    assert data["completed_at"] is not None


def test_create_task_invalid_priority():
    """Test de création d'une tâche avec priorité invalide."""
    task_data = {"title": "Test Task", "priority": "InvalidPriority"}

    response = client.post("/api/v1/tasks/", json=task_data)

    assert response.status_code == 422


def test_create_task_missing_title():
    """Test de création d'une tâche sans titre."""
    task_data = {"description": "Task without title"}

    response = client.post("/api/v1/tasks/", json=task_data)

    assert response.status_code == 422


def test_get_all_tasks_empty():
    """Test de récupération de toutes les tâches quand vide."""
    response = client.get("/api/v1/tasks/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_all_tasks_multiple():
    """Test de récupération de plusieurs tâches."""
    # Créer plusieurs tâches
    task1 = {"title": "Task 1", "priority": "High"}
    task2 = {"title": "Task 2", "priority": "Low"}

    client.post("/api/v1/tasks/", json=task1)
    client.post("/api/v1/tasks/", json=task2)

    response = client.get("/api/v1/tasks/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"


def test_get_task_exists():
    """Test de récupération d'une tâche existante."""
    # Créer une tâche
    task_data = {"title": "Test Task", "description": "Test description"}
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Récupérer la tâche
    response = client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"
    assert data["description"] == "Test description"


def test_get_task_not_found():
    """Test de récupération d'une tâche inexistante."""
    response = client.get("/api/v1/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Tâche non trouvée"


def test_update_task_partial():
    """Test de mise à jour partielle d'une tâche."""
    # Créer une tâche
    task_data = {"title": "Original Task", "priority": "Normal"}
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Mettre à jour partiellement
    update_data = {"title": "Updated Task"}
    response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["priority"] == "Normal"  # Pas changé


def test_update_task_complete():
    """Test de mise à jour complète d'une tâche."""
    # Créer une tâche
    task_data = {"title": "Original Task"}
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Mettre à jour complètement
    due_date = (datetime.now() + timedelta(days=3)).isoformat()
    update_data = {
        "title": "Completely Updated Task",
        "description": "Updated description",
        "completed": True,
        "due_date": due_date,
        "priority": "Top",
    }
    response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Completely Updated Task"
    assert data["description"] == "Updated description"
    assert data["completed"] is True
    assert data["due_date"] == due_date
    assert data["priority"] == "Top"
    assert data["completed_at"] is not None


def test_update_task_mark_completed():
    """Test de marquage d'une tâche comme complétée."""
    # Créer une tâche non complétée
    task_data = {"title": "Task to complete", "completed": False}
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Marquer comme complétée
    update_data = {"completed": True}
    response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True
    assert data["completed_at"] is not None


def test_update_task_mark_uncompleted():
    """Test de marquage d'une tâche comme non complétée."""
    # Créer une tâche complétée
    task_data = {"title": "Completed Task", "completed": True}
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Marquer comme non complétée
    update_data = {"completed": False}
    response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is False
    assert data["completed_at"] is None


def test_update_task_not_found():
    """Test de mise à jour d'une tâche inexistante."""
    update_data = {"title": "Updated Task"}
    response = client.put("/api/v1/tasks/999", json=update_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Tâche non trouvée"


def test_delete_task_exists():
    """Test de suppression d'une tâche existante."""
    # Créer une tâche
    task_data = {"title": "Task to delete"}
    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Supprimer la tâche
    response = client.delete(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 204

    # Vérifier que la tâche n'existe plus
    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found():
    """Test de suppression d'une tâche inexistante."""
    response = client.delete("/api/v1/tasks/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Tâche non trouvée"


def test_task_priorities_all_valid():
    """Test que toutes les priorités sont valides."""
    priorities = ["Low", "Normal", "Medium", "High", "Top"]

    for priority in priorities:
        task_data = {"title": f"Task {priority}", "priority": priority}
        response = client.post("/api/v1/tasks/", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["priority"] == priority


def test_task_workflow():
    """Test d'un workflow complet de tâche."""
    # 1. Créer une tâche
    due_date = (datetime.now() + timedelta(days=5)).isoformat()
    task_data = {
        "title": "Workflow Task",
        "description": "Task for workflow testing",
        "priority": "Medium",
        "due_date": due_date,
    }
    create_response = client.post("/api/v1/tasks/", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # 2. Récupérer la tâche
    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 200

    # 3. Mettre à jour la priorité
    update_response = client.put(f"/api/v1/tasks/{task_id}", json={"priority": "High"})
    assert update_response.status_code == 200
    assert update_response.json()["priority"] == "High"

    # 4. Marquer comme complétée
    complete_response = client.put(f"/api/v1/tasks/{task_id}", json={"completed": True})
    assert complete_response.status_code == 200
    assert complete_response.json()["completed"] is True

    # 5. Vérifier dans la liste
    list_response = client.get("/api/v1/tasks/")
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id
    assert tasks[0]["completed"] is True

    # 6. Supprimer la tâche
    delete_response = client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_response.status_code == 204

    # 7. Vérifier qu'elle n'existe plus
    final_list_response = client.get("/api/v1/tasks/")
    assert final_list_response.status_code == 200
    assert final_list_response.json() == []
