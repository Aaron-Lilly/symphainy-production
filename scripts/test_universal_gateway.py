#!/usr/bin/env python3
"""
Test Universal Gateway Implementation

Tests the universal pillar router and FrontendGatewayService routing.
Verifies Content and Insights Pillar endpoints work correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform" / "backend"))

from experience.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService
from experience.api.universal_pillar_router import set_frontend_gateway, get_frontend_gateway

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    """Print a header."""
    print(f"\n{BLUE}{BOLD}{'='*80}{RESET}")
    print(f"{BLUE}{BOLD}{text.center(80)}{RESET}")
    print(f"{BLUE}{BOLD}{'='*80}{RESET}\n")


def print_test(test_name):
    """Print a test name."""
    print(f"{YELLOW}Testing:{RESET} {test_name}")


def print_success(message):
    """Print a success message."""
    print(f"  {GREEN}✓{RESET} {message}")


def print_error(message):
    """Print an error message."""
    print(f"  {RED}✗{RESET} {message}")


def print_info(message):
    """Print an info message."""
    print(f"  {BLUE}ℹ{RESET} {message}")


class MockOrchestrator:
    """Mock orchestrator for testing."""
    
    def __init__(self, name):
        self.name = name
    
    async def upload_file(self, **kwargs):
        return {
            "success": True,
            "file_id": "test-file-123",
            "message": f"{self.name} processed upload"
        }
    
    async def process_file(self, **kwargs):
        return {
            "success": True,
            "file_id": kwargs.get("file_id"),
            "message": f"{self.name} processed file"
        }
    
    async def list_uploaded_files(self, **kwargs):
        return {
            "success": True,
            "files": [{"file_id": "test-1"}, {"file_id": "test-2"}],
            "count": 2
        }
    
    async def get_file_details(self, **kwargs):
        return {
            "success": True,
            "file": {"file_id": kwargs.get("file_id"), "name": "test.pdf"}
        }
    
    async def analyze_content_for_insights(self, **kwargs):
        return {
            "success": True,
            "analysis_id": "analysis-123",
            "message": f"{self.name} analyzed content"
        }
    
    async def query_analysis_results(self, **kwargs):
        return {
            "success": True,
            "query": kwargs.get("query"),
            "results": "Top 5 items..."
        }
    
    async def get_available_content_metadata(self, **kwargs):
        return {
            "success": True,
            "metadata": [{"id": "meta-1"}, {"id": "meta-2"}],
            "count": 2
        }
    
    async def validate_content_metadata_for_insights(self, **kwargs):
        return {
            "success": True,
            "valid": True,
            "metadata_id": kwargs.get("metadata_id")
        }
    
    async def get_analysis_results(self, **kwargs):
        return {
            "success": True,
            "analysis_id": kwargs.get("analysis_id"),
            "results": {"summary": "Test results"}
        }
    
    async def get_analysis_visualizations(self, **kwargs):
        return {
            "success": True,
            "visualizations": [{"type": "bar", "data": [1, 2, 3]}]
        }
    
    async def list_user_analyses(self, **kwargs):
        return {
            "success": True,
            "analyses": [{"id": "a1"}, {"id": "a2"}],
            "count": 2
        }
    
    async def get_pillar_summary(self, **kwargs):
        return {
            "success": True,
            "summary": {
                "textual": "Summary text",
                "tabular": [{"col": "val"}],
                "visualizations": []
            }
        }
    
    async def health_check(self):
        return {
            "status": "healthy",
            "orchestrator": self.name
        }


async def test_gateway_initialization():
    """Test 1: Gateway service initialization."""
    print_test("Gateway Service Initialization")
    
    try:
        # Create gateway service
        gateway = FrontendGatewayService()
        
        # Add mock orchestrators
        gateway.orchestrators = {
            "ContentAnalysisOrchestrator": MockOrchestrator("ContentAnalysis"),
            "InsightsOrchestrator": MockOrchestrator("Insights")
        }
        
        print_success("Gateway service created")
        print_success("Mock orchestrators registered")
        
        return gateway
    
    except Exception as e:
        print_error(f"Failed to initialize gateway: {e}")
        return None


async def test_universal_router_connection(gateway):
    """Test 2: Universal router connection."""
    print_test("Universal Router Connection")
    
    try:
        # Set gateway in universal router
        set_frontend_gateway(gateway)
        print_success("Gateway connected to universal router")
        
        # Get gateway back
        retrieved_gateway = get_frontend_gateway()
        if retrieved_gateway == gateway:
            print_success("Gateway retrieval works")
        else:
            print_error("Gateway retrieval failed")
            return False
        
        return True
    
    except Exception as e:
        print_error(f"Failed to connect router: {e}")
        return False


async def test_endpoint_parsing(gateway):
    """Test 3: Endpoint parsing logic."""
    print_test("Endpoint Parsing Logic")
    
    test_cases = [
        {
            "endpoint": "/api/content/upload-file",
            "expected_pillar": "content",
            "expected_path": "upload-file"
        },
        {
            "endpoint": "/api/insights/analyze-content",
            "expected_pillar": "insights",
            "expected_path": "analyze-content"
        },
        {
            "endpoint": "/api/content/process-file/abc-123",
            "expected_pillar": "content",
            "expected_path": "process-file/abc-123"
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        endpoint = test_case["endpoint"]
        parts = endpoint.strip("/").split("/")
        
        if len(parts) >= 3 and parts[0] == "api":
            pillar = parts[1]
            path = "/".join(parts[2:])
            
            if pillar == test_case["expected_pillar"] and path == test_case["expected_path"]:
                print_success(f"✓ {endpoint} → pillar={pillar}, path={path}")
            else:
                print_error(f"✗ {endpoint} parsed incorrectly")
                all_passed = False
        else:
            print_error(f"✗ {endpoint} failed to parse")
            all_passed = False
    
    return all_passed


async def test_content_pillar_endpoints(gateway):
    """Test 4: Content Pillar endpoints."""
    print_test("Content Pillar Endpoints")
    
    test_cases = [
        {
            "name": "Upload File",
            "request": {
                "endpoint": "/api/content/upload-file",
                "method": "POST",
                "params": {
                    "file_data": b"test data",
                    "filename": "test.pdf",
                    "content_type": "application/pdf",
                    "user_id": "test_user"
                }
            },
            "expected_success": True
        },
        {
            "name": "List Files",
            "request": {
                "endpoint": "/api/content/list-uploaded-files",
                "method": "GET",
                "params": {"user_id": "test_user"}
            },
            "expected_success": True
        },
        {
            "name": "Process File",
            "request": {
                "endpoint": "/api/content/process-file/test-file-123",
                "method": "POST",
                "params": {"user_id": "test_user"}
            },
            "expected_success": True
        },
        {
            "name": "Get File Details",
            "request": {
                "endpoint": "/api/content/get-file-details/test-file-123",
                "method": "GET",
                "params": {"user_id": "test_user"}
            },
            "expected_success": True
        },
        {
            "name": "Health Check",
            "request": {
                "endpoint": "/api/content/health",
                "method": "GET",
                "params": {}
            },
            "expected_success": True
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        try:
            result = await gateway.route_frontend_request(test_case["request"])
            
            if result.get("success") or result.get("status") == "healthy":
                print_success(f"{test_case['name']}: {test_case['request']['endpoint']}")
            else:
                print_error(f"{test_case['name']}: {result.get('error', 'Unknown error')}")
                all_passed = False
        
        except Exception as e:
            print_error(f"{test_case['name']}: {str(e)}")
            all_passed = False
    
    return all_passed


async def test_insights_pillar_endpoints(gateway):
    """Test 5: Insights Pillar endpoints."""
    print_test("Insights Pillar Endpoints")
    
    test_cases = [
        {
            "name": "Analyze Content",
            "request": {
                "endpoint": "/api/insights/analyze-content",
                "method": "POST",
                "params": {
                    "content_id": "test-123",
                    "user_id": "test_user"
                }
            },
            "expected_success": True
        },
        {
            "name": "Query Analysis",
            "request": {
                "endpoint": "/api/insights/query-analysis",
                "method": "POST",
                "params": {
                    "analysis_id": "analysis-123",
                    "query": "top 5",
                    "user_id": "test_user"
                }
            },
            "expected_success": True
        },
        {
            "name": "Available Metadata",
            "request": {
                "endpoint": "/api/insights/available-content-metadata",
                "method": "GET",
                "params": {"user_id": "test_user"}
            },
            "expected_success": True
        },
        {
            "name": "Validate Metadata",
            "request": {
                "endpoint": "/api/insights/validate-content-metadata",
                "method": "POST",
                "params": {
                    "metadata_id": "meta-123",
                    "user_id": "test_user"
                }
            },
            "expected_success": True
        },
        {
            "name": "Get Analysis Results",
            "request": {
                "endpoint": "/api/insights/analysis-results/analysis-123",
                "method": "GET",
                "params": {"user_id": "test_user"}
            },
            "expected_success": True
        },
        {
            "name": "Get Visualizations",
            "request": {
                "endpoint": "/api/insights/analysis-visualizations/analysis-123",
                "method": "GET",
                "params": {"user_id": "test_user"}
            },
            "expected_success": True
        },
        {
            "name": "List User Analyses",
            "request": {
                "endpoint": "/api/insights/user-analyses",
                "method": "GET",
                "params": {"user_id": "test_user"}
            },
            "expected_success": True
        },
        {
            "name": "Pillar Summary",
            "request": {
                "endpoint": "/api/insights/pillar-summary",
                "method": "GET",
                "params": {"user_id": "test_user"}
            },
            "expected_success": True
        },
        {
            "name": "Health Check",
            "request": {
                "endpoint": "/api/insights/health",
                "method": "GET",
                "params": {}
            },
            "expected_success": True
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        try:
            result = await gateway.route_frontend_request(test_case["request"])
            
            if result.get("success") or result.get("status") == "healthy":
                print_success(f"{test_case['name']}: {test_case['request']['endpoint']}")
            else:
                print_error(f"{test_case['name']}: {result.get('error', 'Unknown error')}")
                all_passed = False
        
        except Exception as e:
            print_error(f"{test_case['name']}: {str(e)}")
            all_passed = False
    
    return all_passed


async def test_error_handling(gateway):
    """Test 6: Error handling."""
    print_test("Error Handling")
    
    test_cases = [
        {
            "name": "Invalid Endpoint Format",
            "request": {
                "endpoint": "/invalid",
                "method": "GET",
                "params": {}
            },
            "should_fail": True
        },
        {
            "name": "Unknown Pillar",
            "request": {
                "endpoint": "/api/unknown-pillar/test",
                "method": "GET",
                "params": {}
            },
            "should_fail": True
        },
        {
            "name": "Unknown Path",
            "request": {
                "endpoint": "/api/content/unknown-endpoint",
                "method": "GET",
                "params": {}
            },
            "should_fail": True
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        try:
            result = await gateway.route_frontend_request(test_case["request"])
            
            if test_case["should_fail"]:
                if not result.get("success"):
                    print_success(f"{test_case['name']}: Correctly failed with error")
                else:
                    print_error(f"{test_case['name']}: Should have failed but succeeded")
                    all_passed = False
            else:
                if result.get("success"):
                    print_success(f"{test_case['name']}: Succeeded as expected")
                else:
                    print_error(f"{test_case['name']}: Failed unexpectedly")
                    all_passed = False
        
        except Exception as e:
            if test_case["should_fail"]:
                print_success(f"{test_case['name']}: Correctly raised exception")
            else:
                print_error(f"{test_case['name']}: Unexpected exception: {str(e)}")
                all_passed = False
    
    return all_passed


async def main():
    """Run all tests."""
    print_header("UNIVERSAL GATEWAY TEST SUITE")
    
    # Track results
    results = {}
    
    # Test 1: Gateway initialization
    gateway = await test_gateway_initialization()
    results["initialization"] = gateway is not None
    
    if not gateway:
        print_error("\nCannot continue tests without gateway")
        return False
    
    # Test 2: Universal router connection
    results["router_connection"] = await test_universal_router_connection(gateway)
    
    # Test 3: Endpoint parsing
    results["endpoint_parsing"] = await test_endpoint_parsing(gateway)
    
    # Test 4: Content Pillar endpoints
    results["content_endpoints"] = await test_content_pillar_endpoints(gateway)
    
    # Test 5: Insights Pillar endpoints
    results["insights_endpoints"] = await test_insights_pillar_endpoints(gateway)
    
    # Test 6: Error handling
    results["error_handling"] = await test_error_handling(gateway)
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    for test_name, passed in results.items():
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n{BOLD}Total:{RESET} {total_tests} tests")
    print(f"{GREEN}{BOLD}Passed:{RESET} {passed_tests}")
    print(f"{RED}{BOLD}Failed:{RESET} {failed_tests}")
    
    if failed_tests == 0:
        print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED!{RESET}\n")
        return True
    else:
        print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED{RESET}\n")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)








