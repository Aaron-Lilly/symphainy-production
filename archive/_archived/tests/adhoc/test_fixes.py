#!/usr/bin/env python3
"""
Test script to verify all systematic fixes are working.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

async def test_endpoint(session: aiohttp.ClientSession, method: str, url: str, 
                       data: Dict[str, Any] = None, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint."""
    try:
        if method.upper() == "GET":
            async with session.get(url) as response:
                return {
                    "url": url,
                    "method": method,
                    "status": response.status,
                    "expected": expected_status,
                    "success": response.status == expected_status,
                    "response": await response.text() if response.status < 500 else "Server Error"
                }
        elif method.upper() == "POST":
            async with session.post(url, json=data or {}) as response:
                return {
                    "url": url,
                    "method": method,
                    "status": response.status,
                    "expected": expected_status,
                    "success": response.status == expected_status,
                    "response": await response.text() if response.status < 500 else "Server Error"
                }
    except Exception as e:
        return {
            "url": url,
            "method": method,
            "status": "ERROR",
            "expected": expected_status,
            "success": False,
            "response": str(e)
        }

async def run_comprehensive_test():
    """Run comprehensive endpoint testing."""
    print("🧪 Starting Comprehensive Endpoint Testing...")
    print("=" * 60)
    
    # Test endpoints that should work after our fixes
    test_cases = [
        # Health endpoints
        ("GET", "http://localhost:8000/health", None, 200),
        ("GET", "http://localhost:8000/api/content/health", None, 200),
        ("GET", "http://localhost:8000/api/insights/health", None, 200),
        ("GET", "http://localhost:8000/api/experience/health", None, 200),
        
        # Content pillar endpoints
        ("GET", "http://localhost:8000/api/content/", None, 200),
        ("POST", "http://localhost:8000/api/content/convert", {"file_id": "test", "target_format": "json"}, 200),
        ("POST", "http://localhost:8000/api/content/enhanced/process", {"file_data": "dGVzdA==", "filename": "test.txt", "file_type": "txt"}, 200),
        ("GET", "http://localhost:8000/api/content/enhanced/test123/metadata", None, 200),
        ("GET", "http://localhost:8000/api/content/enhanced/test123/lineage", None, 200),
        
        # Insights pillar endpoints
        ("GET", "http://localhost:8000/api/insights/", None, 200),
        ("POST", "http://localhost:8000/api/insights/analyze", {"data": {"test": "data"}, "analysis_type": "basic"}, 200),
        ("POST", "http://localhost:8000/api/insights/visualize", {"data": {"test": "data"}, "chart_type": "bar"}, 200),
        ("POST", "http://localhost:8000/api/insights/apg/process-aar", {"file_data": b"test", "filename": "test.pdf"}, 200),
        
        # Experience pillar endpoints
        ("GET", "http://localhost:8000/api/experience/", None, 200),
        ("POST", "http://localhost:8000/api/experience/chat/message", {"message": "Hello", "session_id": "test123"}, 200),
        ("GET", "http://localhost:8000/api/experience/pillars", None, 200),
    ]
    
    async with aiohttp.ClientSession() as session:
        results = []
        
        for method, url, data, expected_status in test_cases:
            print(f"Testing {method} {url}...")
            result = await test_endpoint(session, method, url, data, expected_status)
            results.append(result)
            
            status_icon = "✅" if result["success"] else "❌"
            print(f"  {status_icon} Status: {result['status']} (expected: {expected_status})")
            
            if not result["success"] and result["status"] != "ERROR":
                print(f"  Response: {result['response'][:100]}...")
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        
        print(f"✅ Successful: {successful}/{total}")
        print(f"❌ Failed: {total - successful}/{total}")
        print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
        
        print("\n🔍 FAILED TESTS:")
        for result in results:
            if not result["success"]:
                print(f"  ❌ {result['method']} {result['url']} - Status: {result['status']}")
        
        print("\n🎯 FIXES VERIFICATION:")
        print(f"  ✅ Content Health Endpoint: {'PASS' if any(r['url'].endswith('/api/content/health') and r['success'] for r in results) else 'FAIL'}")
        print(f"  ✅ Insights Routes: {'PASS' if any(r['url'].startswith('/api/insights/') and r['success'] for r in results) else 'FAIL'}")
        print(f"  ✅ Experience Routes: {'PASS' if any(r['url'].startswith('/api/experience/') and r['success'] for r in results) else 'FAIL'}")
        print(f"  ✅ Content Convert Route: {'PASS' if any(r['url'].endswith('/api/content/convert') and r['success'] for r in results) else 'FAIL'}")
        print(f"  ✅ Enhanced Routes: {'PASS' if any(r['url'].startswith('/api/content/enhanced/') and r['success'] for r in results) else 'FAIL'}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())


