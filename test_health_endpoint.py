#!/usr/bin/env python3
"""
Health endpoint test for Juggerbot backend
"""

from app.main import app
from fastapi.testclient import TestClient

def test_health_endpoint():
    """Test that the health endpoint returns expected data"""
    client = TestClient(app)
    
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project Atlas"
    assert data["status"] == "running"
    assert data["version"] == "0.1.0"
    
    print("✅ Health endpoint test passed!")

if __name__ == "__main__":
    test_health_endpoint()
