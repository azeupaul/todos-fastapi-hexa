"""Schémas Pydantic pour les tâches."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Priority(str, Enum):
    """Niveaux de priorité pour les tâches."""

    LOW = "Low"
    NORMAL = "Normal"
    MEDIUM = "Medium"
    HIGH = "High"
    TOP = "Top"


class TaskBase(BaseModel):
    """Schéma de base pour une tâche."""

    title: str
    description: str | None = None
    completed: bool = False
    due_date: datetime | None = None
    priority: Priority = Priority.NORMAL


class TaskCreate(TaskBase):
    """Schéma pour la création d'une tâche."""

    pass


class TaskUpdate(BaseModel):
    """Schéma pour la mise à jour d'une tâche."""

    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    due_date: datetime | None = None
    priority: Priority | None = None


class Task(TaskBase):
    """Schéma complet d'une tâche."""

    id: int
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
