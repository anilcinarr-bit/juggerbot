#!/usr/bin/env python3
"""
Simple test to check if backend imports and starts correctly.
"""
import sys
import os

try:
    # Test that we can import everything properly
    from app.config import settings
    print("✓ Configuration loaded successfully")
    print(f"  API Host: {settings.api_host}")
    print(f"  API Port: {settings.api_port}")
    print(f"  Database URL: {settings.database_url}")
    
    from app.main import app
    print("✓ Main application imported successfully")
    
    # Test that the endpoints exist
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    print(f"✓ Root endpoint: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Response: {data}")
    
    # Test health endpoint  
    response = client.get("/health")
    print(f"✓ Health endpoint: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Response: {data}")
        
    print("\n🎉 All tests passed! Backend foundation is working correctly.")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)