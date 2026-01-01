#!/usr/bin/env python3
"""
Direct API Test - Test API endpoints directly with proper service initialization
"""

import asyncio
import json
import base64
from fastapi.testclient import TestClient
from main import app

async def test_api_endpoints():
    """Test API endpoints with proper service initialization."""
    print("🧪 Testing API Endpoints Directly...")
    
    # Initialize services manually
    from main import startup_event
    await startup_event()
    
    # Create test client
    client = TestClient(app)
    
    # Test enhanced file upload
    print("\n📁 Testing Enhanced File Upload...")
    csv_data = "name,age,city\nJohn,30,New York\nJane,25,Los Angeles"
    csv_base64 = base64.b64encode(csv_data.encode()).decode()
    
    response = client.post(
        "/api/content/enhanced/process",
        data={
            "file_data": csv_base64,
            "filename": "test_data.csv",
            "file_type": "csv",
            "user_id": "test_user_123",
            "options": json.dumps({
                "extract_metadata": True,
                "auto_track_lineage": True
            })
        }
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Enhanced file upload successful: {result.get('success', False)}")
        print(f"File ID: {result.get('file_id', 'N/A')}")
    else:
        print(f"❌ Enhanced file upload failed: {response.text}")
    
    # Test health check
    print("\n🏥 Testing Health Check...")
    response = client.get("/health")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        health = response.json()
        print(f"✅ Health check successful: {health.get('status', 'unknown')}")
    else:
        print(f"❌ Health check failed: {response.text}")
    
    # Test insights pillar
    print("\n📊 Testing Insights Pillar...")
    response = client.post(
        "/api/insights/analyze",
        json={
            "data": {"test": "data"},
            "user_context": {"user_id": "test_user"}
        }
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Insights analysis successful: {result.get('success', False)}")
    else:
        print(f"❌ Insights analysis failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())

