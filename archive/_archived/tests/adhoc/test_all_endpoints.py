#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing Script

Tests all endpoints systematically to identify patterns and issues.
"""

import requests
import json
import time
from typing import Dict, List, Any

def test_endpoint(method: str, url: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
    """Test a single endpoint and return results."""
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return {
            "status_code": response.status_code,
            "success": 200 <= response.status_code < 300,
            "response_length": len(response.text),
            "content_type": response.headers.get("content-type", ""),
            "response_preview": response.text[:200] if response.text else "",
            "headers": dict(response.headers)
        }
    except requests.exceptions.ConnectionError:
        return {"error": "Connection refused - server not running"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout"}
    except Exception as e:
        return {"error": str(e)}

def main():
    """Test all endpoints systematically."""
    base_url = "http://localhost:8000"
    
    # Define all endpoints to test
    endpoints = [
        # Basic endpoints
        {"method": "GET", "path": "/", "name": "Root"},
        {"method": "GET", "path": "/health", "name": "Health Check"},
        {"method": "GET", "path": "/docs", "name": "API Docs"},
        {"method": "GET", "path": "/redoc", "name": "ReDoc"},
        
        # Content Pillar endpoints
        {"method": "GET", "path": "/api/content/health", "name": "Content Health"},
        {"method": "POST", "path": "/api/content/upload", "name": "Content Upload", "data": {}},
        {"method": "POST", "path": "/api/content/parse", "name": "Content Parse", "data": {}},
        {"method": "POST", "path": "/api/content/convert", "name": "Content Convert", "data": {}},
        
        # Enhanced Content endpoints
        {"method": "POST", "path": "/api/content/enhanced/process", "name": "Enhanced Process", "data": {}},
        {"method": "GET", "path": "/api/content/enhanced/file_123/metadata", "name": "Enhanced Metadata"},
        {"method": "GET", "path": "/api/content/enhanced/file_123/lineage", "name": "Enhanced Lineage"},
        {"method": "POST", "path": "/api/content/enhanced/relationship", "name": "Enhanced Relationship", "data": {}},
        
        # Insights Pillar endpoints
        {"method": "GET", "path": "/api/insights/health", "name": "Insights Health"},
        {"method": "POST", "path": "/api/insights/analyze", "name": "Insights Analyze", "data": {}},
        {"method": "POST", "path": "/api/insights/visualize", "name": "Insights Visualize", "data": {}},
        
        # APG Document Intelligence endpoints
        {"method": "POST", "path": "/api/insights/apg/process-aar", "name": "APG Process AAR", "data": {}},
        {"method": "POST", "path": "/api/insights/apg/process-multiple-aars", "name": "APG Process Multiple AARs", "data": {}},
        {"method": "GET", "path": "/api/insights/apg/exercise-planning", "name": "APG Exercise Planning"},
        {"method": "POST", "path": "/api/insights/apg/assess-risks", "name": "APG Assess Risks", "data": {}},
        
        # Experience endpoints
        {"method": "GET", "path": "/api/experience/health", "name": "Experience Health"},
        {"method": "POST", "path": "/api/experience/chat", "name": "Experience Chat", "data": {}},
        {"method": "POST", "path": "/api/experience/orchestrator", "name": "Experience Orchestrator", "data": {}},
        
        # WebSocket endpoints (can't test with requests, but note them)
        {"method": "WS", "path": "/ws/content/test_connection", "name": "Content WebSocket"},
    ]
    
    print("🔍 Testing all endpoints systematically...")
    print("=" * 80)
    
    results = {}
    categories = {
        "working": [],
        "client_errors": [],
        "server_errors": [],
        "connection_errors": [],
        "other_errors": []
    }
    
    for endpoint in endpoints:
        if endpoint["method"] == "WS":
            # Skip WebSocket testing for now
            continue
            
        url = f"{base_url}{endpoint['path']}"
        print(f"\n🧪 Testing {endpoint['name']}: {endpoint['method']} {endpoint['path']}")
        
        result = test_endpoint(
            method=endpoint["method"],
            url=url,
            data=endpoint.get("data"),
            headers={"Content-Type": "application/json"}
        )
        
        results[endpoint["name"]] = result
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            if "Connection refused" in result["error"]:
                categories["connection_errors"].append(endpoint["name"])
            else:
                categories["other_errors"].append(endpoint["name"])
        elif result["success"]:
            print(f"✅ Success: {result['status_code']} - {result['response_length']} bytes")
            categories["working"].append(endpoint["name"])
        elif 400 <= result["status_code"] < 500:
            print(f"⚠️  Client Error: {result['status_code']} - {result['response_preview']}")
            categories["client_errors"].append(endpoint["name"])
        elif 500 <= result["status_code"] < 600:
            print(f"🔥 Server Error: {result['status_code']} - {result['response_preview']}")
            categories["server_errors"].append(endpoint["name"])
        else:
            print(f"❓ Other: {result['status_code']} - {result['response_preview']}")
            categories["other_errors"].append(endpoint["name"])
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ENDPOINT TEST SUMMARY")
    print("=" * 80)
    
    for category, endpoints in categories.items():
        if endpoints:
            print(f"\n{category.upper().replace('_', ' ')} ({len(endpoints)} endpoints):")
            for endpoint in endpoints:
                print(f"  - {endpoint}")
    
    # Patterns analysis
    print("\n🔍 PATTERN ANALYSIS")
    print("=" * 80)
    
    if categories["connection_errors"]:
        print("❌ Server not running - fix startup issues first")
    
    if categories["server_errors"]:
        print("🔥 Server errors detected - check logs for details")
        server_error_endpoints = [ep for ep in categories["server_errors"]]
        print(f"   Affected endpoints: {', '.join(server_error_endpoints)}")
    
    if categories["client_errors"]:
        print("⚠️  Client errors (404, 422, etc.) - likely missing routes or incorrect parameters")
        client_error_endpoints = [ep for ep in categories["client_errors"]]
        print(f"   Affected endpoints: {', '.join(client_error_endpoints)}")
    
    # Save detailed results
    with open("endpoint_test_results.json", "w") as f:
        json.dump({
            "timestamp": time.time(),
            "base_url": base_url,
            "results": results,
            "categories": categories,
            "summary": {
                "total_tested": len([ep for ep in endpoints if ep["method"] != "WS"]),
                "working": len(categories["working"]),
                "client_errors": len(categories["client_errors"]),
                "server_errors": len(categories["server_errors"]),
                "connection_errors": len(categories["connection_errors"]),
                "other_errors": len(categories["other_errors"])
            }
        }, indent=2)
    
    print(f"\n💾 Detailed results saved to endpoint_test_results.json")
    
    return results, categories

if __name__ == "__main__":
    main()
