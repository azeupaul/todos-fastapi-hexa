from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    """Point d'entrée racine."""
    return {
        "message": "Bienvenue sur l'API Todos FastAPI!",
    }

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Vérification de santé de l'API."""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    app()
