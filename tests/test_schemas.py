"""Tests pour les schémas Pydantic."""
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.schemas.task import Priority, Task, TaskCreate, TaskUpdate


def test_priority_enum():
    """Test de l'énumération Priority."""
    assert Priority.LOW == "Low"
    assert Priority.NORMAL == "Normal"
    assert Priority.MEDIUM == "Medium"
    assert Priority.HIGH == "High"
    assert Priority.TOP == "Top"


def test_task_create_minimal():
    """Test de création d'une tâche avec les champs minimaux."""
    task_data = TaskCreate(title="Test Task")

    assert task_data.title == "Test Task"
    assert task_data.description is None
    assert task_data.completed is False
    assert task_data.due_date is None
    assert task_data.priority == Priority.NORMAL


def test_task_create_complete():
    """Test de création d'une tâche avec tous les champs."""
    due_date = datetime.now() + timedelta(days=7)
    task_data = TaskCreate(
        title="Complete Task",
        description="A complete task description",
        completed=True,
        due_date=due_date,
        priority=Priority.HIGH,
    )

    assert task_data.title == "Complete Task"
    assert task_data.description == "A complete task description"
    assert task_data.completed is True
    assert task_data.due_date == due_date
    assert task_data.priority == Priority.HIGH


def test_task_create_invalid_priority():
    """Test de création d'une tâche avec une priorité invalide."""
    with pytest.raises(ValidationError):
        TaskCreate(title="Test", priority="Invalid")


def test_task_update_partial():
    """Test de mise à jour partielle d'une tâche."""
    update_data = TaskUpdate(title="Updated Title")

    assert update_data.title == "Updated Title"
    assert update_data.description is None
    assert update_data.completed is None
    assert update_data.due_date is None
    assert update_data.priority is None


def test_task_update_all_fields():
    """Test de mise à jour de tous les champs."""
    due_date = datetime.now() + timedelta(days=3)
    update_data = TaskUpdate(
        title="Updated Task",
        description="Updated description",
        completed=True,
        due_date=due_date,
        priority=Priority.TOP,
    )

    assert update_data.title == "Updated Task"
    assert update_data.description == "Updated description"
    assert update_data.completed is True
    assert update_data.due_date == due_date
    assert update_data.priority == Priority.TOP


def test_task_complete_schema():
    """Test du schéma complet Task."""
    now = datetime.now()
    completed_at = now + timedelta(hours=1)

    task = Task(
        id=1,
        title="Complete Task Schema",
        description="Test description",
        completed=True,
        due_date=now + timedelta(days=5),
        priority=Priority.MEDIUM,
        created_at=now,
        completed_at=completed_at,
    )

    assert task.id == 1
    assert task.title == "Complete Task Schema"
    assert task.description == "Test description"
    assert task.completed is True
    assert task.due_date == now + timedelta(days=5)
    assert task.priority == Priority.MEDIUM
    assert task.created_at == now
    assert task.completed_at == completed_at
