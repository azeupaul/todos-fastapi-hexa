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


def test_create_task(task_store, sample_task_data):
    """Test de création d'une tâche."""
    task = task_store.create_task(sample_task_data)

    assert task.id == 1
    assert task.title == sample_task_data.title
    assert task.description == sample_task_data.description
    assert task.priority == sample_task_data.priority
    assert task.due_date == sample_task_data.due_date
    assert task.completed is False
    assert task.completed_at is None
    assert task.created_at is not None


def test_create_completed_task(task_store):
    """Test de création d'une tâche déjà complétée."""
    task_data = TaskCreate(title="Completed Task", completed=True)
    task = task_store.create_task(task_data)

    assert task.completed is True
    assert task.completed_at is not None


def test_get_task_exists(task_store, sample_task_data):
    """Test de récupération d'une tâche existante."""
    created_task = task_store.create_task(sample_task_data)
    retrieved_task = task_store.get_task(created_task.id)

    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.title == created_task.title


def test_get_task_not_exists(task_store):
    """Test de récupération d'une tâche inexistante."""
    task = task_store.get_task(999)
    assert task is None


def test_get_all_tasks_empty(task_store):
    """Test de récupération de toutes les tâches quand vide."""
    tasks = task_store.get_all_tasks()
    assert tasks == []


def test_get_all_tasks_multiple(task_store):
    """Test de récupération de plusieurs tâches."""
    task1_data = TaskCreate(title="Task 1", priority=Priority.HIGH)
    task2_data = TaskCreate(title="Task 2", priority=Priority.LOW)

    task1 = task_store.create_task(task1_data)
    task2 = task_store.create_task(task2_data)

    all_tasks = task_store.get_all_tasks()
    assert len(all_tasks) == 2
    assert task1 in all_tasks
    assert task2 in all_tasks


def test_update_task_exists(task_store, sample_task_data):
    """Test de mise à jour d'une tâche existante."""
    created_task = task_store.create_task(sample_task_data)

    update_data = TaskUpdate(
        title="Updated Title", priority=Priority.TOP, completed=True
    )

    updated_task = task_store.update_task(created_task.id, update_data)

    assert updated_task is not None
    assert updated_task.title == "Updated Title"
    assert updated_task.priority == Priority.TOP
    assert updated_task.completed is True
    assert updated_task.completed_at is not None


def test_update_task_not_exists(task_store):
    """Test de mise à jour d'une tâche inexistante."""
    update_data = TaskUpdate(title="Non-existent Task")
    result = task_store.update_task(999, update_data)
    assert result is None


def test_update_task_mark_completed(task_store, sample_task_data):
    """Test de marquage d'une tâche comme complétée."""
    created_task = task_store.create_task(sample_task_data)
    assert created_task.completed_at is None

    update_data = TaskUpdate(completed=True)
    updated_task = task_store.update_task(created_task.id, update_data)

    assert updated_task.completed is True
    assert updated_task.completed_at is not None


def test_update_task_mark_uncompleted(task_store):
    """Test de marquage d'une tâche comme non complétée."""
    task_data = TaskCreate(title="Completed Task", completed=True)
    created_task = task_store.create_task(task_data)
    assert created_task.completed_at is not None

    update_data = TaskUpdate(completed=False)
    updated_task = task_store.update_task(created_task.id, update_data)

    assert updated_task.completed is False
    assert updated_task.completed_at is None


def test_delete_task_exists(task_store, sample_task_data):
    """Test de suppression d'une tâche existante."""
    created_task = task_store.create_task(sample_task_data)

    result = task_store.delete_task(created_task.id)
    assert result is True

    # Vérifier que la tâche n'existe plus
    retrieved_task = task_store.get_task(created_task.id)
    assert retrieved_task is None


def test_delete_task_not_exists(task_store):
    """Test de suppression d'une tâche inexistante."""
    result = task_store.delete_task(999)
    assert result is False


def test_task_id_increment(task_store):
    """Test que les IDs s'incrémentent correctement."""
    task1_data = TaskCreate(title="Task 1")
    task2_data = TaskCreate(title="Task 2")
    task3_data = TaskCreate(title="Task 3")

    task1 = task_store.create_task(task1_data)
    task2 = task_store.create_task(task2_data)
    task3 = task_store.create_task(task3_data)

    assert task1.id == 1
    assert task2.id == 2
    assert task3.id == 3
