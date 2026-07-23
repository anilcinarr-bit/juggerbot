"""
Test script to verify that the health endpoint returns the correct response.
"""
import asyncio
import httpx
from fastapi.testclient import TestClient

from app.main import app

async def test_health_endpoint():
    """Test that the root endpoint returns expected response."""
    client = TestClient(app)
    
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "Project Atlas"
    assert data["status"] == "running"
    assert data["version"] == "0.1.0"
    
    print("✅ Health endpoint test passed!")
    print(f"Response: {data}")

if __name__ == "__main__":
    asyncio.run(test_health_endpoint())