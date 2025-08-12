"""Stockage en mémoire pour les tâches."""
from datetime import datetime
from typing import Dict, List

from src.schemas.task import Task, TaskCreate, TaskUpdate


class TaskStore:
    """Stockage simple en mémoire pour les tâches."""

    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1

    def create_task(self, task_data: TaskCreate, user_id: int) -> Task:
        """Créer une nouvelle tâche."""
        now = datetime.now()
        task = Task(
            id=self._next_id,
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            due_date=task_data.due_date,
            priority=task_data.priority,
            created_at=now,
            completed_at=now if task_data.completed else None,
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get_task(self, task_id: int, user_id: int) -> Task | None:
        """Récupérer une tâche par son ID."""
        task = self._tasks.get(task_id)
        if task and task.user_id != user_id:
            return None
        return task

    def get_all_tasks(self, user_id: int) -> List[Task]:
        """Récupérer toutes les tâches."""
        return [
            task for task in self._tasks.values() if task and task.user_id == user_id
        ]

    def update_task(
        self, task_id: int, task_update: TaskUpdate, user_id: int
    ) -> Task | None:
        """Mettre à jour une tâche."""
        if task_id not in self._tasks or not self._tasks[task_id]:
            return None

        task = self._tasks[task_id]
        if task and task.user_id != user_id:
            return None

        update_data = task_update.model_dump(exclude_unset=True)

        # Gérer le completed_at quand completed change
        if "completed" in update_data:
            if update_data["completed"] and not task.completed:
                # Marquer comme complété
                task.completed_at = datetime.now()
            elif not update_data["completed"] and task.completed:
                # Marquer comme non complété
                task.completed_at = None

        # Appliquer les autres mises à jour
        for field, value in update_data.items():
            setattr(task, field, value)

        return task

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Supprimer une tâche."""
        if (
            task_id in self._tasks
            and self._tasks[task_id]
            and self._tasks[task_id].user_id == user_id
        ):
            del self._tasks[task_id]
            return True
        return False


# Instance globale pour cette phase
task_store = TaskStore()
