from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_estado():
    response = client.get("/api/estado")
    assert response.status_code == 200
    assert response.json()["estado"] == "activo"