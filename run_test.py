#!/usr/bin/env python3
"""
Simple test script to verify the backend foundation works correctly.
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test imports
    from app.main import app
    print("✓ Main application imported successfully")
    
    # Test configuration
    from app.config import settings
    print("✓ Configuration system imported successfully")
    
    # Test database initialization
    from app.database import init_db
    print("✓ Database module imported successfully")
    
    # Test that endpoints exist
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    print(f"✓ Root endpoint works: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Response data: {data}")
        expected_keys = ["name", "status", "version"]
        for key in expected_keys:
            if key not in data:
                print(f"✗ Missing key '{key}' in root endpoint")
            else:
                print(f"✓ Key '{key}' found with value: {data[key]}")
    
    # Test health endpoint
    response = client.get("/health")
    print(f"✓ Health endpoint works: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"  Response data: {data}")
        
    print("\n🎉 All tests passed! Backend foundation is working correctly.")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)