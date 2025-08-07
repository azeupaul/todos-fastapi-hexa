"""Point d'entrée principal de l'application FastAPI."""
from fastapi import FastAPI

app = FastAPI(
    title="Todos FastAPI", description="Une API de gestion de tâches", version="0.1.0"
)


@app.get("/")
async def root():
    """Point d'entrée racine."""
    return {"message": "Bienvenue sur l'API Todos FastAPI!"}


@app.get("/health")
async def health_check():
    """Vérification de santé de l'API."""
    return {"status": "healthy"}
