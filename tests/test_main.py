"""Tests pour le point d'entrée principal."""
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test du point d'entrée racine."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Bienvenue sur l'API Todos FastAPI!"


def test_health_check():
    """Test du health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
