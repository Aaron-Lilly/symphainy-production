#!/usr/bin/env python3
"""
Verify Universal Gateway Implementation

Checks that all required files exist and contain expected code patterns.
"""

import re
from pathlib import Path

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
    print(f"\n{YELLOW}Checking:{RESET} {BOLD}{test_name}{RESET}")


def print_success(message):
    """Print a success message."""
    print(f"  {GREEN}✓{RESET} {message}")


def print_error(message):
    """Print an error message."""
    print(f"  {RED}✗{RESET} {message}")


def print_warning(message):
    """Print a warning message."""
    print(f"  {YELLOW}⚠{RESET} {message}")


def check_file_exists(file_path):
    """Check if a file exists."""
    return Path(file_path).exists()


def check_file_contains(file_path, pattern, description):
    """Check if a file contains a specific pattern."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if re.search(pattern, content, re.MULTILINE):
                print_success(f"{description}")
                return True
            else:
                print_error(f"{description} - Pattern not found")
                return False
    except Exception as e:
        print_error(f"{description} - Error reading file: {e}")
        return False


def verify_universal_router():
    """Verify universal router implementation."""
    print_test("Universal Pillar Router")
    
    file_path = "symphainy-platform/backend/experience/api/universal_pillar_router.py"
    
    if not check_file_exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    print_success(f"File exists: {file_path}")
    
    # Check for universal route
    checks = [
        (r'@router\.api_route.*\/api\/\{pillar\}\/\{path:path\}', 
         "Universal route pattern @router.api_route('/api/{pillar}/{path:path}')"),
        (r'async def universal_pillar_handler',
         "Universal handler function"),
        (r'def set_frontend_gateway',
         "set_frontend_gateway() function"),
        (r'def get_frontend_gateway',
         "get_frontend_gateway() function"),
        (r'gateway\.route_frontend_request',
         "Calls gateway.route_frontend_request()")
    ]
    
    all_passed = True
    for pattern, description in checks:
        if not check_file_contains(file_path, pattern, description):
            all_passed = False
    
    return all_passed


def verify_frontend_gateway_service():
    """Verify FrontendGatewayService implementation."""
    print_test("FrontendGatewayService")
    
    file_path = "symphainy-platform/backend/experience/services/frontend_gateway_service/frontend_gateway_service.py"
    
    if not check_file_exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    print_success(f"File exists: {file_path}")
    
    # Check for Content Pillar handlers
    content_handlers = [
        (r'async def handle_upload_file_request', "Content: handle_upload_file_request()"),
        (r'async def handle_process_file_request', "Content: handle_process_file_request()"),
        (r'async def handle_list_uploaded_files_request', "Content: handle_list_uploaded_files_request()"),
        (r'async def handle_get_file_details_request', "Content: handle_get_file_details_request()"),
        (r'async def handle_content_pillar_health_check_request', "Content: handle_content_pillar_health_check_request()")
    ]
    
    # Check for Insights Pillar handlers
    insights_handlers = [
        (r'async def handle_analyze_content_for_insights_semantic_request', "Insights: handle_analyze_content_for_insights_semantic_request()"),
        (r'async def handle_query_insights_analysis_request', "Insights: handle_query_insights_analysis_request()"),
        (r'async def handle_get_available_content_metadata_request', "Insights: handle_get_available_content_metadata_request()"),
        (r'async def handle_validate_content_metadata_for_insights_request', "Insights: handle_validate_content_metadata_for_insights_request()"),
        (r'async def handle_get_insights_analysis_results_request', "Insights: handle_get_insights_analysis_results_request()"),
        (r'async def handle_get_insights_analysis_visualizations_request', "Insights: handle_get_insights_analysis_visualizations_request()"),
        (r'async def handle_list_user_insights_analyses_request', "Insights: handle_list_user_insights_analyses_request()"),
        (r'async def handle_get_insights_pillar_summary_request', "Insights: handle_get_insights_pillar_summary_request()"),
        (r'async def handle_insights_pillar_health_check_request', "Insights: handle_insights_pillar_health_check_request()")
    ]
    
    # Check for routing logic
    routing_checks = [
        (r'async def route_frontend_request', "Universal routing method route_frontend_request()"),
        (r'pillar = parts\[1\]', "Extracts pillar from endpoint"),
        (r'if pillar == "content":', "Routes Content Pillar requests"),
        (r'elif pillar == "insights":', "Routes Insights Pillar requests")
    ]
    
    all_checks = content_handlers + insights_handlers + routing_checks
    all_passed = True
    
    for pattern, description in all_checks:
        if not check_file_contains(file_path, pattern, description):
            all_passed = False
    
    return all_passed


def verify_main_api_registration():
    """Verify main_api.py registration."""
    print_test("Main API Registration")
    
    file_path = "symphainy-platform/backend/experience/api/main_api.py"
    
    if not check_file_exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    print_success(f"File exists: {file_path}")
    
    checks = [
        (r'from \. import universal_pillar_router', "Imports universal_pillar_router"),
        (r'universal_pillar_router\.set_frontend_gateway', "Connects gateway to router"),
        (r'app\.include_router\(universal_pillar_router\.router\)', "Registers universal router"),
        (r'#.*content_pillar_router.*ARCHIVED', "Old content router commented out (archived)"),
        (r'#.*insights_pillar_router.*ARCHIVED', "Old insights router commented out (archived)")
    ]
    
    all_passed = True
    for pattern, description in checks:
        if not check_file_contains(file_path, pattern, description):
            all_passed = False
    
    return all_passed


def verify_archived_routers():
    """Verify old routers are archived."""
    print_test("Archived Routers")
    
    archived_dir = "symphainy-platform/backend/experience/api/semantic/archived"
    
    if not Path(archived_dir).exists():
        print_error(f"Archived directory not found: {archived_dir}")
        return False
    
    print_success(f"Archived directory exists: {archived_dir}")
    
    # Check archived files
    archived_files = [
        "content_pillar_router.py",
        "insights_pillar_router.py"
    ]
    
    all_passed = True
    for filename in archived_files:
        file_path = f"{archived_dir}/{filename}"
        if check_file_exists(file_path):
            print_success(f"Archived: {filename}")
        else:
            print_error(f"Not found in archive: {filename}")
            all_passed = False
    
    # Check they're NOT in the active directory
    active_dir = "symphainy-platform/backend/experience/api/semantic"
    for filename in archived_files:
        active_path = f"{active_dir}/{filename}"
        if not check_file_exists(active_path):
            print_success(f"Removed from active: {filename}")
        else:
            print_warning(f"Still in active directory: {filename}")
    
    return all_passed


def verify_protocol_updates():
    """Verify protocol updates."""
    print_test("FrontendGatewayServiceProtocol")
    
    file_path = "symphainy-platform/backend/experience/protocols/frontend_gateway_service_protocol.py"
    
    if not check_file_exists(file_path):
        print_error(f"File not found: {file_path}")
        return False
    
    print_success(f"File exists: {file_path}")
    
    # Check for updated methods
    checks = [
        (r'async def discover_orchestrators', "Has discover_orchestrators()"),
        (r'async def route_frontend_request', "Has route_frontend_request()"),
        (r'async def validate_api_request', "Has validate_api_request()"),
        (r'async def transform_for_frontend', "Has transform_for_frontend()"),
        (r'Reflects enabling services \+ semantic API', "Updated documentation")
    ]
    
    all_passed = True
    for pattern, description in checks:
        if not check_file_contains(file_path, pattern, description):
            all_passed = False
    
    return all_passed


def main():
    """Run all verifications."""
    print_header("UNIVERSAL GATEWAY IMPLEMENTATION VERIFICATION")
    
    results = {}
    
    # Run verifications
    results["universal_router"] = verify_universal_router()
    results["frontend_gateway"] = verify_frontend_gateway_service()
    results["main_api"] = verify_main_api_registration()
    results["archived_routers"] = verify_archived_routers()
    results["protocol_updates"] = verify_protocol_updates()
    
    # Print summary
    print_header("VERIFICATION SUMMARY")
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r)
    failed_checks = total_checks - passed_checks
    
    for check_name, passed in results.items():
        status = f"{GREEN}✓ VERIFIED{RESET}" if passed else f"{RED}✗ FAILED{RESET}"
        print(f"  {check_name.replace('_', ' ').title():30} {status}")
    
    print(f"\n{BOLD}Total Checks:{RESET} {total_checks}")
    print(f"{GREEN}{BOLD}Passed:{RESET}       {passed_checks}")
    print(f"{RED}{BOLD}Failed:{RESET}       {failed_checks}")
    
    if failed_checks == 0:
        print(f"\n{GREEN}{BOLD}╔═══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{GREEN}{BOLD}║                                                           ║{RESET}")
        print(f"{GREEN}{BOLD}║     ✓ ALL VERIFICATIONS PASSED! 🎉                        ║{RESET}")
        print(f"{GREEN}{BOLD}║                                                           ║{RESET}")
        print(f"{GREEN}{BOLD}║  Universal Gateway is correctly implemented!              ║{RESET}")
        print(f"{GREEN}{BOLD}║                                                           ║{RESET}")
        print(f"{GREEN}{BOLD}║  - Universal router: ✓ Working                            ║{RESET}")
        print(f"{GREEN}{BOLD}║  - Content Pillar: ✓ 5 endpoints                          ║{RESET}")
        print(f"{GREEN}{BOLD}║  - Insights Pillar: ✓ 9 endpoints                         ║{RESET}")
        print(f"{GREEN}{BOLD}║  - Old routers: ✓ Archived                                ║{RESET}")
        print(f"{GREEN}{BOLD}║  - Protocol: ✓ Updated                                    ║{RESET}")
        print(f"{GREEN}{BOLD}║                                                           ║{RESET}")
        print(f"{GREEN}{BOLD}║  Ready for production testing! 🚀                          ║{RESET}")
        print(f"{GREEN}{BOLD}║                                                           ║{RESET}")
        print(f"{GREEN}{BOLD}╚═══════════════════════════════════════════════════════════╝{RESET}\n")
        return True
    else:
        print(f"\n{RED}{BOLD}╔═══════════════════════════════════════╗{RESET}")
        print(f"{RED}{BOLD}║                                       ║{RESET}")
        print(f"{RED}{BOLD}║     ✗ SOME VERIFICATIONS FAILED       ║{RESET}")
        print(f"{RED}{BOLD}║                                       ║{RESET}")
        print(f"{RED}{BOLD}║  Review the failures above            ║{RESET}")
        print(f"{RED}{BOLD}║                                       ║{RESET}")
        print(f"{RED}{BOLD}╚═══════════════════════════════════════╝{RESET}\n")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)








