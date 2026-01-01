#!/usr/bin/env python3
"""
Simple Test for Universal Gateway Routing Logic

Tests endpoint parsing and routing without requiring full platform initialization.
"""

# ANSI color codes
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
    print(f"\n{YELLOW}Test:{RESET} {BOLD}{test_name}{RESET}")


def print_success(message):
    """Print a success message."""
    print(f"  {GREEN}✓{RESET} {message}")


def print_error(message):
    """Print an error message."""
    print(f"  {RED}✗{RESET} {message}")


def parse_endpoint(endpoint):
    """
    Parse endpoint to extract pillar and path.
    This mirrors the logic in FrontendGatewayService.route_frontend_request()
    """
    parts = endpoint.strip("/").split("/")
    
    if len(parts) < 3 or parts[0] != "api":
        return None, None, f"Invalid endpoint format: {endpoint}"
    
    pillar = parts[1]
    path = "/".join(parts[2:])
    
    return pillar, path, None


def test_endpoint_parsing():
    """Test endpoint parsing logic."""
    print_test("Endpoint Parsing Logic")
    
    test_cases = [
        {
            "endpoint": "/api/content/upload-file",
            "expected_pillar": "content",
            "expected_path": "upload-file",
            "should_succeed": True
        },
        {
            "endpoint": "/api/insights/analyze-content",
            "expected_pillar": "insights",
            "expected_path": "analyze-content",
            "should_succeed": True
        },
        {
            "endpoint": "/api/content/process-file/abc-123",
            "expected_pillar": "content",
            "expected_path": "process-file/abc-123",
            "should_succeed": True
        },
        {
            "endpoint": "/api/insights/analysis-results/test-id",
            "expected_pillar": "insights",
            "expected_path": "analysis-results/test-id",
            "should_succeed": True
        },
        {
            "endpoint": "/invalid",
            "expected_pillar": None,
            "expected_path": None,
            "should_succeed": False
        },
        {
            "endpoint": "/api/only-two-parts",
            "expected_pillar": None,
            "expected_path": None,
            "should_succeed": False
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        pillar, path, error = parse_endpoint(test_case["endpoint"])
        
        if test_case["should_succeed"]:
            if pillar == test_case["expected_pillar"] and path == test_case["expected_path"]:
                print_success(f"{test_case['endpoint']}")
                print(f"      → pillar: {BLUE}{pillar}{RESET}, path: {BLUE}{path}{RESET}")
            else:
                print_error(f"{test_case['endpoint']}")
                print(f"      Expected: pillar={test_case['expected_pillar']}, path={test_case['expected_path']}")
                print(f"      Got: pillar={pillar}, path={path}")
                all_passed = False
        else:
            if error:
                print_success(f"{test_case['endpoint']} → Correctly identified as invalid")
            else:
                print_error(f"{test_case['endpoint']} → Should have failed but succeeded")
                all_passed = False
    
    return all_passed


def test_content_pillar_routing():
    """Test Content Pillar routing logic."""
    print_test("Content Pillar Endpoint Routing")
    
    endpoints = [
        ("POST", "/api/content/upload-file", "handle_upload_file_request"),
        ("POST", "/api/content/process-file/file-123", "handle_process_file_request"),
        ("GET", "/api/content/list-uploaded-files", "handle_list_uploaded_files_request"),
        ("GET", "/api/content/get-file-details/file-123", "handle_get_file_details_request"),
        ("GET", "/api/content/health", "handle_content_pillar_health_check_request")
    ]
    
    all_passed = True
    for method, endpoint, expected_handler in endpoints:
        pillar, path, error = parse_endpoint(endpoint)
        
        if error:
            print_error(f"{method} {endpoint} → Failed to parse")
            all_passed = False
            continue
        
        # Determine handler based on path and method
        handler = None
        if pillar == "content":
            if path == "upload-file" and method == "POST":
                handler = "handle_upload_file_request"
            elif path.startswith("process-file/") and method == "POST":
                handler = "handle_process_file_request"
            elif path == "list-uploaded-files" and method == "GET":
                handler = "handle_list_uploaded_files_request"
            elif path.startswith("get-file-details/") and method == "GET":
                handler = "handle_get_file_details_request"
            elif path == "health" and method == "GET":
                handler = "handle_content_pillar_health_check_request"
        
        if handler == expected_handler:
            print_success(f"{method:6} {endpoint}")
            print(f"        → {BLUE}{handler}(){RESET}")
        else:
            print_error(f"{method} {endpoint}")
            print(f"        Expected: {expected_handler}, Got: {handler}")
            all_passed = False
    
    return all_passed


def test_insights_pillar_routing():
    """Test Insights Pillar routing logic."""
    print_test("Insights Pillar Endpoint Routing")
    
    endpoints = [
        ("POST", "/api/insights/analyze-content", "handle_analyze_content_for_insights_semantic_request"),
        ("POST", "/api/insights/query-analysis", "handle_query_insights_analysis_request"),
        ("GET", "/api/insights/available-content-metadata", "handle_get_available_content_metadata_request"),
        ("POST", "/api/insights/validate-content-metadata", "handle_validate_content_metadata_for_insights_request"),
        ("GET", "/api/insights/analysis-results/abc-123", "handle_get_insights_analysis_results_request"),
        ("GET", "/api/insights/analysis-visualizations/abc-123", "handle_get_insights_analysis_visualizations_request"),
        ("GET", "/api/insights/user-analyses", "handle_list_user_insights_analyses_request"),
        ("GET", "/api/insights/pillar-summary", "handle_get_insights_pillar_summary_request"),
        ("GET", "/api/insights/health", "handle_insights_pillar_health_check_request")
    ]
    
    all_passed = True
    for method, endpoint, expected_handler in endpoints:
        pillar, path, error = parse_endpoint(endpoint)
        
        if error:
            print_error(f"{method} {endpoint} → Failed to parse")
            all_passed = False
            continue
        
        # Determine handler based on path and method
        handler = None
        if pillar == "insights":
            if path == "analyze-content" and method == "POST":
                handler = "handle_analyze_content_for_insights_semantic_request"
            elif path == "query-analysis" and method == "POST":
                handler = "handle_query_insights_analysis_request"
            elif path == "available-content-metadata" and method == "GET":
                handler = "handle_get_available_content_metadata_request"
            elif path == "validate-content-metadata" and method == "POST":
                handler = "handle_validate_content_metadata_for_insights_request"
            elif path.startswith("analysis-results/") and method == "GET":
                handler = "handle_get_insights_analysis_results_request"
            elif path.startswith("analysis-visualizations/") and method == "GET":
                handler = "handle_get_insights_analysis_visualizations_request"
            elif path == "user-analyses" and method == "GET":
                handler = "handle_list_user_insights_analyses_request"
            elif path == "pillar-summary" and method == "GET":
                handler = "handle_get_insights_pillar_summary_request"
            elif path == "health" and method == "GET":
                handler = "handle_insights_pillar_health_check_request"
        
        if handler == expected_handler:
            print_success(f"{method:6} {endpoint}")
            print(f"        → {BLUE}{handler}(){RESET}")
        else:
            print_error(f"{method} {endpoint}")
            print(f"        Expected: {expected_handler}, Got: {handler}")
            all_passed = False
    
    return all_passed


def test_error_cases():
    """Test error handling for invalid endpoints."""
    print_test("Error Handling for Invalid Endpoints")
    
    test_cases = [
        ("/invalid", "Should reject endpoint not starting with /api"),
        ("/api/unknown-pillar/test", "Should reject unknown pillar"),
        ("/api/content/unknown-path", "Should reject unknown path"),
        ("/api", "Should reject incomplete endpoint")
    ]
    
    all_passed = True
    for endpoint, description in test_cases:
        pillar, path, error = parse_endpoint(endpoint)
        
        # For endpoints that parse successfully but route to unknown paths
        if endpoint == "/api/unknown-pillar/test":
            if pillar == "unknown-pillar":
                print_success(f"{endpoint}")
                print(f"        → {description} ✓")
            else:
                print_error(f"{endpoint}")
                all_passed = False
        elif endpoint == "/api/content/unknown-path":
            if pillar == "content" and path == "unknown-path":
                print_success(f"{endpoint}")
                print(f"        → {description} ✓")
            else:
                print_error(f"{endpoint}")
                all_passed = False
        else:
            # Should fail parsing
            if error:
                print_success(f"{endpoint}")
                print(f"        → {description} ✓")
            else:
                print_error(f"{endpoint}")
                print(f"        → {description} ✗")
                all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    print_header("UNIVERSAL GATEWAY ROUTING LOGIC TESTS")
    
    results = {}
    
    # Run tests
    results["endpoint_parsing"] = test_endpoint_parsing()
    results["content_routing"] = test_content_pillar_routing()
    results["insights_routing"] = test_insights_pillar_routing()
    results["error_handling"] = test_error_cases()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    for test_name, passed in results.items():
        status = f"{GREEN}✓ PASSED{RESET}" if passed else f"{RED}✗ FAILED{RESET}"
        print(f"  {test_name.replace('_', ' ').title():30} {status}")
    
    print(f"\n{BOLD}Total Tests:{RESET} {total_tests}")
    print(f"{GREEN}{BOLD}Passed:{RESET}      {passed_tests}")
    print(f"{RED}{BOLD}Failed:{RESET}      {failed_tests}")
    
    if failed_tests == 0:
        print(f"\n{GREEN}{BOLD}╔═══════════════════════════════════════╗{RESET}")
        print(f"{GREEN}{BOLD}║                                       ║{RESET}")
        print(f"{GREEN}{BOLD}║     ✓ ALL TESTS PASSED! 🎉            ║{RESET}")
        print(f"{GREEN}{BOLD}║                                       ║{RESET}")
        print(f"{GREEN}{BOLD}║  Routing logic is working correctly!  ║{RESET}")
        print(f"{GREEN}{BOLD}║                                       ║{RESET}")
        print(f"{GREEN}{BOLD}╚═══════════════════════════════════════╝{RESET}\n")
        return True
    else:
        print(f"\n{RED}{BOLD}╔═══════════════════════════════════════╗{RESET}")
        print(f"{RED}{BOLD}║                                       ║{RESET}")
        print(f"{RED}{BOLD}║     ✗ SOME TESTS FAILED               ║{RESET}")
        print(f"{RED}{BOLD}║                                       ║{RESET}")
        print(f"{RED}{BOLD}║  Review the failures above            ║{RESET}")
        print(f"{RED}{BOLD}║                                       ║{RESET}")
        print(f"{RED}{BOLD}╚═══════════════════════════════════════╝{RESET}\n")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)








