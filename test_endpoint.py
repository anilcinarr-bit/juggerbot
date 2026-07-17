from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project Atlas"
    assert data["status"] == "running"
    assert data["version"] == "0.1.0"
    print("Root endpoint test passed!")

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print("Health endpoint test passed!")

if __name__ == "__main__":
    test_root_endpoint()
    test_health_endpoint()
    print("All tests passed!")