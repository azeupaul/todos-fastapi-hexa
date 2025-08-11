"""Point d'entrée principal de l'application FastAPI."""
from fastapi import FastAPI

from src.api.auth import router as auth_router
from src.api.tasks import router as tasks_router

app = FastAPI(
    title="Todos FastAPI", description="Une API de gestion de tâches", version="0.1.0"
)

# Inclure les routes des tâches
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Point d'entrée racine."""
    return {"message": "Bienvenue sur l'API Todos FastAPI!"}


@app.get("/health")
async def health_check():
    """Vérification de santé de l'API."""
    return {"status": "healthy"}
