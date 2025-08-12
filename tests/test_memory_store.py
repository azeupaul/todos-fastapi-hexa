"""Tests pour le stockage en mémoire."""
from datetime import datetime, timedelta

import pytest

from src.models.memory_store import TaskStore
from src.schemas.task import Priority, TaskCreate, TaskUpdate


@pytest.fixture
def task_store():
    """Fixture pour un stockage de tâches vide."""
    return TaskStore()


@pytest.fixture
def sample_task_data():
    """Fixture pour des données de tâche exemple."""
    return TaskCreate(
        title="Sample Task",
        description="A sample task for testing",
        priority=Priority.MEDIUM,
        due_date=datetime.now() + timedelta(days=7),
    )


@pytest.fixture
def sample_user_id():
    """Fixture pour un ID utilisateur exemple."""
    return 1


def test_create_task(task_store, sample_task_data, sample_user_id):
    """Test de création d'une tâche."""
    task = task_store.create_task(sample_task_data, sample_user_id)

    assert task.id == 1
    assert task.user_id == sample_user_id
    assert task.title == sample_task_data.title
    assert task.description == sample_task_data.description
    assert task.priority == sample_task_data.priority
    assert task.due_date == sample_task_data.due_date
    assert task.completed is False
    assert task.completed_at is None
    assert task.created_at is not None


def test_create_completed_task(task_store, sample_user_id):
    """Test de création d'une tâche déjà complétée."""
    task_data = TaskCreate(title="Completed Task", completed=True)
    task = task_store.create_task(task_data, sample_user_id)

    assert task.completed is True
    assert task.completed_at is not None
    assert task.user_id == sample_user_id


def test_get_task_exists(task_store, sample_task_data, sample_user_id):
    """Test de récupération d'une tâche existante."""
    created_task = task_store.create_task(sample_task_data, sample_user_id)
    retrieved_task = task_store.get_task(created_task.id, sample_user_id)

    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.user_id == sample_user_id
    assert retrieved_task.title == created_task.title


def test_get_task_with_user_filter(task_store, sample_task_data):
    """Test de récupération d'une tâche avec filtre utilisateur."""
    user1_id = 1
    user2_id = 2

    # Créer une tâche pour l'utilisateur 1
    created_task = task_store.create_task(sample_task_data, user1_id)

    # Récupérer avec le bon utilisateur
    retrieved_task = task_store.get_task(created_task.id, user1_id)
    assert retrieved_task is not None
    assert retrieved_task.user_id == user1_id

    # Essayer de récupérer avec le mauvais utilisateur
    retrieved_task = task_store.get_task(created_task.id, user2_id)
    assert retrieved_task is None


def test_get_task_not_exists(task_store, sample_user_id):
    """Test de récupération d'une tâche inexistante."""
    task = task_store.get_task(999, sample_user_id)
    assert task is None


def test_get_all_tasks_empty(task_store, sample_user_id):
    """Test de récupération de toutes les tâches quand vide."""
    tasks = task_store.get_all_tasks(sample_user_id)
    assert tasks == []


def test_get_all_tasks_multiple_users(task_store):
    """Test de récupération de tâches pour plusieurs utilisateurs."""
    user1_id = 1
    user2_id = 2

    task1_data = TaskCreate(title="Task 1", priority=Priority.HIGH)
    task2_data = TaskCreate(title="Task 2", priority=Priority.LOW)
    task3_data = TaskCreate(title="Task 3", priority=Priority.MEDIUM)

    # Créer des tâches pour différents utilisateurs
    task1 = task_store.create_task(task1_data, user1_id)
    task2 = task_store.create_task(task2_data, user2_id)
    task3 = task_store.create_task(task3_data, user1_id)

    # Récupérer les tâches de l'utilisateur 1
    user1_tasks = task_store.get_all_tasks(user1_id)
    assert len(user1_tasks) == 2
    assert all(task.user_id == user1_id for task in user1_tasks)
    assert task1 in user1_tasks
    assert task3 in user1_tasks

    # Récupérer les tâches de l'utilisateur 2
    user2_tasks = task_store.get_all_tasks(user2_id)
    assert len(user2_tasks) == 1
    assert user2_tasks[0] == task2
    assert user2_tasks[0].user_id == user2_id


def test_update_task_exists(task_store, sample_task_data, sample_user_id):
    """Test de mise à jour d'une tâche existante."""
    created_task = task_store.create_task(sample_task_data, sample_user_id)

    update_data = TaskUpdate(
        title="Updated Title", priority=Priority.TOP, completed=True
    )

    updated_task = task_store.update_task(created_task.id, update_data, sample_user_id)

    assert updated_task is not None
    assert updated_task.title == "Updated Title"
    assert updated_task.priority == Priority.TOP
    assert updated_task.completed is True
    assert updated_task.completed_at is not None
    assert updated_task.user_id == sample_user_id


def test_update_task_with_user_filter(task_store, sample_task_data):
    """Test de mise à jour d'une tâche avec filtre utilisateur."""
    user1_id = 1
    user2_id = 2

    # Créer une tâche pour l'utilisateur 1
    created_task = task_store.create_task(sample_task_data, user1_id)

    update_data = TaskUpdate(title="Updated Title")

    # Mettre à jour avec le bon utilisateur
    updated_task = task_store.update_task(created_task.id, update_data, user1_id)
    assert updated_task is not None
    assert updated_task.title == "Updated Title"

    # Essayer de mettre à jour avec le mauvais utilisateur
    update_data2 = TaskUpdate(title="Hacked Title")
    updated_task = task_store.update_task(created_task.id, update_data2, user2_id)
    assert updated_task is None


def test_update_task_not_exists(task_store, sample_user_id):
    """Test de mise à jour d'une tâche inexistante."""
    update_data = TaskUpdate(title="Non-existent Task")
    result = task_store.update_task(999, update_data, sample_user_id)
    assert result is None


def test_update_task_completion_states(task_store, sample_task_data, sample_user_id):
    """Test des transitions d'état de completion."""
    # Créer une tâche non complétée
    created_task = task_store.create_task(sample_task_data, sample_user_id)
    assert created_task.completed_at is None

    # Marquer comme complétée
    update_data = TaskUpdate(completed=True)
    updated_task = task_store.update_task(created_task.id, update_data, sample_user_id)

    assert updated_task.completed is True
    assert updated_task.completed_at is not None

    # Marquer comme non complétée
    update_data = TaskUpdate(completed=False)
    updated_task = task_store.update_task(created_task.id, update_data, sample_user_id)

    assert updated_task.completed is False
    assert updated_task.completed_at is None


def test_delete_task_exists(task_store, sample_task_data, sample_user_id):
    """Test de suppression d'une tâche existante."""
    created_task = task_store.create_task(sample_task_data, sample_user_id)

    result = task_store.delete_task(created_task.id, sample_user_id)
    assert result is True

    # Vérifier que la tâche n'existe plus
    retrieved_task = task_store.get_task(created_task.id, sample_user_id)
    assert retrieved_task is None


def test_delete_task_with_user_filter(task_store, sample_task_data):
    """Test de suppression d'une tâche avec filtre utilisateur."""
    user1_id = 1
    user2_id = 2

    # Créer une tâche pour l'utilisateur 1
    created_task = task_store.create_task(sample_task_data, user1_id)

    # Essayer de supprimer avec le mauvais utilisateur
    result = task_store.delete_task(created_task.id, user2_id)
    assert result is False

    # Vérifier que la tâche existe toujours
    retrieved_task = task_store.get_task(created_task.id, user1_id)
    assert retrieved_task is not None

    # Supprimer avec le bon utilisateur
    result = task_store.delete_task(created_task.id, user1_id)
    assert result is True

    # Vérifier que la tâche n'existe plus
    retrieved_task = task_store.get_task(created_task.id, user1_id)
    assert retrieved_task is None


def test_delete_task_not_exists(task_store, sample_user_id):
    """Test de suppression d'une tâche inexistante."""
    result = task_store.delete_task(999, sample_user_id)
    assert result is False


def test_task_id_increment_multiple_users(task_store):
    """Test que les IDs s'incrémentent correctement pour plusieurs utilisateurs."""
    user1_id = 1
    user2_id = 2

    task1_data = TaskCreate(title="Task 1")
    task2_data = TaskCreate(title="Task 2")
    task3_data = TaskCreate(title="Task 3")

    task1 = task_store.create_task(task1_data, user1_id)
    task2 = task_store.create_task(task2_data, user2_id)
    task3 = task_store.create_task(task3_data, user1_id)

    assert task1.id == 1
    assert task1.user_id == user1_id
    assert task2.id == 2
    assert task2.user_id == user2_id
    assert task3.id == 3
    assert task3.user_id == user1_id


def test_user_isolation_complete(task_store):
    """Test complet de l'isolation entre utilisateurs."""
    user1_id = 1
    user2_id = 2

    # Créer des tâches pour chaque utilisateur
    task1_data = TaskCreate(title="User 1 Task 1")
    task2_data = TaskCreate(title="User 1 Task 2")
    task3_data = TaskCreate(title="User 2 Task 1")

    user1_task1 = task_store.create_task(task1_data, user1_id)
    user1_task2 = task_store.create_task(task2_data, user1_id)
    user2_task1 = task_store.create_task(task3_data, user2_id)

    # Vérifier l'isolation pour la récupération
    user1_tasks = task_store.get_all_tasks(user1_id)
    user2_tasks = task_store.get_all_tasks(user2_id)

    assert len(user1_tasks) == 2
    assert len(user2_tasks) == 1
    assert all(task.user_id == user1_id for task in user1_tasks)
    assert all(task.user_id == user2_id for task in user2_tasks)

    # Vérifier l'isolation pour la mise à jour
    update_data = TaskUpdate(title="Updated by wrong user")
    update_data2 = TaskUpdate(title="Updated by user 2")

    # User 2 ne peut pas modifier les tâches de User 1
    result = task_store.update_task(user1_task1.id, update_data, user2_id)
    assert result is None

    # User 2 peut modifier ses propres tâches
    result = task_store.update_task(user2_task1.id, update_data2, user2_id)
    assert result is not None
    assert result.title == "Updated by user 2"

    # User 1 peut modifier ses propres tâches
    result = task_store.update_task(user1_task1.id, update_data, user1_id)
    assert result is not None
    assert result.title == "Updated by wrong user"

    # Vérifier l'isolation pour la suppression
    # User 2 ne peut pas supprimer les tâches de User 1
    result = task_store.delete_task(user1_task2.id, user2_id)
    assert result is False

    # Vérifier que la tâche existe toujours
    task = task_store.get_task(user1_task2.id, user1_id)
    assert task is not None

    # User 1 peut supprimer ses propres tâches
    result = task_store.delete_task(user1_task2.id, user1_id)
    assert result is True

    # Vérifier que la tâche n'existe plus
    task = task_store.get_task(user1_task2.id, user1_id)
    assert task is None
