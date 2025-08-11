from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth import get_current_active_user
from src.models.memory_store import task_store
from src.schemas.task import Task, TaskCreate, TaskUpdate
from src.schemas.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate, current_user: Annotated[User, Depends(get_current_active_user)]
) -> Task:
    """Créer une nouvelle tâche."""
    return task_store.create_task(task, current_user.id)


@router.get("/", response_model=List[Task])
async def get_tasks(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> List[Task]:
    """Récupérer toutes les tâches."""
    return task_store.get_all_tasks(current_user.id)


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int, current_user: Annotated[User, Depends(get_current_active_user)]
) -> Task:
    """Récupérer une tâche par son ID."""
    task = task_store.get_task(task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tâche non trouvée"
        )
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Task:
    """Mettre à jour une tâche."""
    task = task_store.update_task(task_id, task_update, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tâche non trouvée"
        )
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Supprimer une tâche."""
    if not task_store.delete_task(task_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tâche non trouvée"
        )
