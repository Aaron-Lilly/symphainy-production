#!/usr/bin/env python3
"""
Run Complete New Test Suite

Runs ALL newly created tests from tonight (bottom-up test strategy).
Includes: Infrastructure Adapters, Abstractions, Platform Gateway,
Enabling Services, Orchestrators, MCP Servers, and Agents.

Designed to show issues without requiring troubleshooting.
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Test categories and their paths - ALL NEW TESTS FROM TONIGHT
TEST_CATEGORIES = {
    "Layer 0: Infrastructure Adapters": [
        "tests/unit/infrastructure_adapters/test_gcs_file_adapter.py",
        "tests/unit/infrastructure_adapters/test_supabase_adapter.py",
        "tests/unit/infrastructure_adapters/test_supabase_metadata_adapter.py",
        "tests/unit/infrastructure_adapters/test_supabase_file_management_adapter.py",
        "tests/unit/infrastructure_adapters/test_redis_adapter.py",
        "tests/unit/infrastructure_adapters/test_redis_session_adapter.py",
        "tests/unit/infrastructure_adapters/test_redis_state_adapter.py",
        "tests/unit/infrastructure_adapters/test_redis_event_bus_adapter.py",
        "tests/unit/infrastructure_adapters/test_redis_graph_adapter.py",
        "tests/unit/infrastructure_adapters/test_arangodb_adapter.py",
        "tests/unit/infrastructure_adapters/test_meilisearch_knowledge_adapter.py",
        "tests/unit/infrastructure_adapters/test_opentelemetry_adapter.py",
        "tests/unit/infrastructure_adapters/test_tempo_adapter.py",
        "tests/unit/infrastructure_adapters/test_celery_adapter.py",
    ],
    "Infrastructure Abstractions": [
        "tests/unit/infrastructure_abstractions/test_file_management_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_auth_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_session_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_messaging_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_event_management_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_telemetry_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_cache_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_task_management_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_knowledge_discovery_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_llm_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_content_schema_abstraction.py",
        "tests/unit/infrastructure_abstractions/test_content_insights_abstraction.py",
    ],
    "Platform Gateway": [
        "tests/unit/foundations/platform_gateway_foundation/test_platform_gateway_foundation_service.py",
        "tests/unit/platform_infrastructure/test_platform_gateway.py",
    ],
    "Layer 3: Enabling Services": [
        "tests/unit/enabling_services/test_file_parser_service.py",
        "tests/unit/enabling_services/test_format_composer_service.py",
        "tests/unit/enabling_services/test_data_analyzer_service.py",
        "tests/unit/enabling_services/test_roadmap_generation_service.py",
        "tests/unit/enabling_services/test_poc_generation_service.py",
    ],
    "Layer 4: Orchestrators": [
        "tests/unit/orchestrators/test_content_analysis_orchestrator.py",
        "tests/unit/orchestrators/test_business_outcomes_orchestrator.py",
        "tests/unit/orchestrators/test_insights_orchestrator.py",
        "tests/unit/orchestrators/test_operations_orchestrator.py",
    ],
    "Layer 5: MCP Servers": [
        "tests/unit/mcp_servers/test_business_outcomes_mcp_server.py",
        "tests/unit/mcp_servers/test_content_analysis_mcp_server.py",
        "tests/unit/mcp_servers/test_insights_mcp_server.py",
        "tests/unit/mcp_servers/test_operations_mcp_server.py",
    ],
    "Layer 6: Agents": [
        "tests/unit/agents/test_business_outcomes_specialist_agent.py",
        "tests/unit/agents/test_insights_specialist_agent.py",
        "tests/unit/agents/test_content_processing_agent.py",
        "tests/unit/agents/test_operations_specialist_agent.py",
    ],
}


def run_pytest(test_path: str) -> Tuple[bool, str, Dict]:
    """
    Run pytest on a single test file.
    
    Returns:
        (success, output, summary)
    """
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", test_path, "-v", "--tb=short", "--json-report", "--json-report-file=/tmp/pytest_report.json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Try to read JSON report if it exists
        summary = {}
        try:
            with open("/tmp/pytest_report.json", "r") as f:
                report = json.load(f)
                summary = {
                    "passed": report.get("summary", {}).get("passed", 0),
                    "failed": report.get("summary", {}).get("failed", 0),
                    "skipped": report.get("summary", {}).get("skipped", 0),
                    "total": report.get("summary", {}).get("total", 0),
                }
        except:
            # Fallback: parse stdout
            output_lines = result.stdout.split("\n")
            for line in output_lines:
                if "passed" in line.lower() and "failed" in line.lower():
                    # Try to extract numbers
                    import re
                    nums = re.findall(r'\d+', line)
                    if len(nums) >= 3:
                        summary = {
                            "passed": int(nums[0]),
                            "failed": int(nums[1]),
                            "skipped": int(nums[2]) if len(nums) > 2 else 0,
                            "total": sum([int(n) for n in nums[:3]]),
                        }
        
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        return success, output, summary
        
    except subprocess.TimeoutExpired:
        return False, "Test timed out after 60 seconds", {}
    except Exception as e:
        return False, f"Error running test: {str(e)}", {}


def print_summary(results: Dict[str, List[Tuple[str, bool, str, Dict]]]):
    """Print a formatted summary of test results."""
    print("\n" + "=" * 80)
    print("COMPLETE NEW TEST SUITE SUMMARY (Bottom-Up Strategy)")
    print("=" * 80)
    print(f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total_passed = 0
    total_failed = 0
    total_skipped = 0
    total_tests = 0
    
    for category, test_results in results.items():
        print(f"\n📁 {category}")
        print("-" * 80)
        
        category_passed = 0
        category_failed = 0
        category_skipped = 0
        category_total = 0
        
        for test_path, success, output, summary in test_results:
            test_name = Path(test_path).stem.replace("test_", "").replace("_", " ").title()
            status = "✅ PASS" if success else "❌ FAIL"
            
            # Extract summary if available
            if summary:
                passed = summary.get("passed", 0)
                failed = summary.get("failed", 0)
                skipped = summary.get("skipped", 0)
                total = summary.get("total", 0)
                
                category_passed += passed
                category_failed += failed
                category_skipped += skipped
                category_total += total
                
                print(f"  {status} {test_name}")
                print(f"      Tests: {passed} passed, {failed} failed, {skipped} skipped ({total} total)")
            else:
                print(f"  {status} {test_name}")
                if not success:
                    # Show first few lines of error
                    error_lines = output.split("\n")[:3]
                    for line in error_lines:
                        if line.strip():
                            print(f"      {line[:70]}")
        
        total_passed += category_passed
        total_failed += category_failed
        total_skipped += category_skipped
        total_tests += category_total
        
        if category_total > 0:
            print(f"\n  Category Total: {category_passed} passed, {category_failed} failed, {category_skipped} skipped ({category_total} total)")
    
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"  ✅ Passed: {total_passed}")
    print(f"  ❌ Failed: {total_failed}")
    print(f"  ⏭️  Skipped: {total_skipped}")
    
    if total_tests > 0:
        success_rate = (total_passed / total_tests) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    # Show failed tests
    if total_failed > 0:
        print("\n" + "=" * 80)
        print("FAILED TESTS (for tomorrow)")
        print("=" * 80)
        for category, test_results in results.items():
            failed_tests = [(tp, output) for tp, success, output, _ in test_results if not success]
            if failed_tests:
                print(f"\n📁 {category}:")
                for test_path, output in failed_tests:
                    test_name = Path(test_path).stem
                    print(f"  ❌ {test_name}")
                    # Show key error lines
                    error_lines = [l for l in output.split("\n") if "error" in l.lower() or "fail" in l.lower() or "import" in l.lower()][:5]
                    for line in error_lines:
                        if line.strip():
                            print(f"      {line[:70]}")
    
    print("\n" + "=" * 80)
    print("Done! Review failed tests above for tomorrow's troubleshooting.")
    print("=" * 80 + "\n")


def main():
    """Main test runner."""
    print("Running complete new test suite (bottom-up strategy)...")
    print("This includes all tests created tonight:")
    print("  - Infrastructure Adapters (Layer 0)")
    print("  - Infrastructure Abstractions")
    print("  - Platform Gateway")
    print("  - Enabling Services (Layer 3)")
    print("  - Orchestrators (Layer 4)")
    print("  - MCP Servers (Layer 5)")
    print("  - Agents (Layer 6)")
    print("\nThis may take a few minutes...\n")
    
    results = {}
    
    for category, test_paths in TEST_CATEGORIES.items():
        print(f"Running {category} tests...")
        category_results = []
        
        for test_path in test_paths:
            # Check if file exists
            if not Path(test_path).exists():
                print(f"  ⚠️  Skipping {test_path} (file not found)")
                category_results.append((test_path, False, "File not found", {}))
                continue
            
            print(f"  Running {Path(test_path).name}...", end=" ", flush=True)
            success, output, summary = run_pytest(test_path)
            category_results.append((test_path, success, output, summary))
            
            if success:
                print("✅")
            else:
                print("❌")
        
        results[category] = category_results
    
    print_summary(results)
    
    # Exit with error code if any tests failed
    total_failed = sum(
        sum(1 for _, success, _, _ in test_results if not success)
        for test_results in results.values()
    )
    
    sys.exit(1 if total_failed > 0 else 0)


if __name__ == "__main__":
    main()

