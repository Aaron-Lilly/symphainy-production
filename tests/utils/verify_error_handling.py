#!/usr/bin/env python3
"""
Error Handling Verification Utility

Verifies that services follow the standard error handling pattern:
- handle_error_with_audit()
- log_operation_with_telemetry()
- record_health_metric()
- Structured error responses with error_code and error_type
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class ErrorHandlingVerifier:
    """Verify error handling compliance across services."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.backend_path = base_path / "symphainy-platform" / "backend"
        self.results = {
            "services_checked": 0,
            "services_compliant": 0,
            "services_non_compliant": [],
            "issues": defaultdict(list),
            "patterns_found": defaultdict(int)
        }
    
    def verify_service_file(self, file_path: Path) -> Dict[str, any]:
        """Verify a single service file for error handling compliance."""
        relative_path = file_path.relative_to(self.base_path)
        result = {
            "file": str(relative_path),
            "compliant": True,
            "issues": [],
            "patterns": {
                "has_handle_error_with_audit": False,
                "has_log_operation_with_telemetry": False,
                "has_record_health_metric": False,
                "has_error_code": False,
                "has_error_type": False,
                "exception_handlers": 0,
                "compliant_handlers": 0
            }
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            result["compliant"] = False
            result["issues"].append(f"Could not read file: {e}")
            return result
        
        # Count exception handlers
        exception_pattern = r'except\s+(?:Exception|Error|.*Error)\s*:'
        exception_matches = re.findall(exception_pattern, content)
        result["patterns"]["exception_handlers"] = len(exception_matches)
        
        # Check for standard error handling methods
        if "handle_error_with_audit" in content:
            result["patterns"]["has_handle_error_with_audit"] = True
            self.results["patterns_found"]["handle_error_with_audit"] += 1
        
        if "log_operation_with_telemetry" in content:
            result["patterns"]["has_log_operation_with_telemetry"] = True
            self.results["patterns_found"]["log_operation_with_telemetry"] += 1
        
        if "record_health_metric" in content:
            result["patterns"]["has_record_health_metric"] = True
            self.results["patterns_found"]["record_health_metric"] += 1
        
        # Check for error response format
        if '"error_code"' in content or "'error_code'" in content:
            result["patterns"]["has_error_code"] = True
            self.results["patterns_found"]["error_code"] += 1
        
        if '"error_type"' in content or "'error_type'" in content:
            result["patterns"]["has_error_type"] = True
            self.results["patterns_found"]["error_type"] += 1
        
        # Check exception handlers for compliance
        # Look for exception handlers that use standard methods
        exception_blocks = re.finditer(
            r'except\s+(?:Exception|Error|.*Error)\s*:.*?(?=\n\s*(?:except|else|finally|def|class|\Z))',
            content,
            re.DOTALL
        )
        
        for block_match in exception_blocks:
            block = block_match.group(0)
            
            # Check if this handler uses standard methods
            has_audit = "handle_error_with_audit" in block
            has_telemetry = "log_operation_with_telemetry" in block
            has_health = "record_health_metric" in block
            
            if has_audit and has_telemetry and has_health:
                result["patterns"]["compliant_handlers"] += 1
            else:
                # This is a non-compliant handler
                if not has_audit:
                    result["issues"].append("Exception handler missing handle_error_with_audit()")
                if not has_telemetry:
                    result["issues"].append("Exception handler missing log_operation_with_telemetry()")
                if not has_health:
                    result["issues"].append("Exception handler missing record_health_metric()")
        
        # Determine overall compliance
        # For service files, we expect at least some exception handlers to be compliant
        if result["patterns"]["exception_handlers"] > 0:
            if result["patterns"]["compliant_handlers"] == 0 and result["patterns"]["exception_handlers"] > 0:
                # Has exception handlers but none are compliant
                result["compliant"] = False
            elif result["patterns"]["compliant_handlers"] < result["patterns"]["exception_handlers"]:
                # Some handlers are compliant, some are not (partial compliance)
                result["compliant"] = "partial"
        
        return result
    
    def verify_directory(self, directory: Path, pattern: str = "*.py") -> List[Dict]:
        """Verify all Python files in a directory."""
        results = []
        
        for file_path in directory.rglob(pattern):
            # Skip test files, __pycache__, and archive directories
            if any(skip in str(file_path) for skip in ["test_", "__pycache__", "archive", "tests"]):
                continue
            
            # Only check service files (services, orchestrators, etc.)
            if "service" in str(file_path) or "orchestrator" in str(file_path):
                result = self.verify_service_file(file_path)
                results.append(result)
                self.results["services_checked"] += 1
                
                if result["compliant"] is True:
                    self.results["services_compliant"] += 1
                elif result["compliant"] is False:
                    self.results["services_non_compliant"].append(result["file"])
                    for issue in result["issues"]:
                        self.results["issues"][result["file"]].append(issue)
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate a verification report."""
        report = []
        report.append("=" * 80)
        report.append("ERROR HANDLING VERIFICATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Services Checked: {self.results['services_checked']}")
        report.append(f"Services Compliant: {self.results['services_compliant']}")
        report.append(f"Services Non-Compliant: {len(self.results['services_non_compliant'])}")
        report.append("")
        
        # Pattern Usage
        report.append("PATTERN USAGE")
        report.append("-" * 80)
        for pattern, count in self.results["patterns_found"].items():
            report.append(f"  {pattern}: {count} files")
        report.append("")
        
        # Non-Compliant Services
        if self.results["services_non_compliant"]:
            report.append("NON-COMPLIANT SERVICES")
            report.append("-" * 80)
            for file in self.results["services_non_compliant"][:20]:  # Limit to first 20
                report.append(f"  - {file}")
            if len(self.results["services_non_compliant"]) > 20:
                report.append(f"  ... and {len(self.results['services_non_compliant']) - 20} more")
            report.append("")
        
        # Issues
        if self.results["issues"]:
            report.append("ISSUES FOUND")
            report.append("-" * 80)
            for file, issues in list(self.results["issues"].items())[:10]:  # Limit to first 10 files
                report.append(f"  {file}:")
                for issue in issues[:5]:  # Limit to first 5 issues per file
                    report.append(f"    - {issue}")
            report.append("")
        
        # Detailed Results (Sample)
        report.append("SAMPLE DETAILED RESULTS")
        report.append("-" * 80)
        for result in results[:5]:  # Show first 5 results
            report.append(f"File: {result['file']}")
            report.append(f"  Compliant: {result['compliant']}")
            report.append(f"  Exception Handlers: {result['patterns']['exception_handlers']}")
            report.append(f"  Compliant Handlers: {result['patterns']['compliant_handlers']}")
            if result["issues"]:
                report.append(f"  Issues: {len(result['issues'])}")
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)


def main():
    """Main verification function."""
    base_path = Path(__file__).parent.parent.parent
    
    verifier = ErrorHandlingVerifier(base_path)
    
    # Verify key service directories
    print("Verifying error handling compliance...")
    print("")
    
    # Check solution services
    solution_path = base_path / "symphainy-platform" / "backend" / "solution" / "services"
    if solution_path.exists():
        print(f"Checking solution services...")
        verifier.verify_directory(solution_path)
    
    # Check journey orchestrators
    journey_path = base_path / "symphainy-platform" / "backend" / "journey" / "orchestrators"
    if journey_path.exists():
        print(f"Checking journey orchestrators...")
        verifier.verify_directory(journey_path)
    
    # Check Smart City services
    smart_city_path = base_path / "symphainy-platform" / "backend" / "smart_city" / "services"
    if smart_city_path.exists():
        print(f"Checking Smart City services...")
        verifier.verify_directory(smart_city_path)
    
    # Check content services
    content_path = base_path / "symphainy-platform" / "backend" / "content" / "services"
    if content_path.exists():
        print(f"Checking content services...")
        verifier.verify_directory(content_path)
    
    # Check insights services
    insights_path = base_path / "symphainy-platform" / "backend" / "insights" / "services"
    if insights_path.exists():
        print(f"Checking insights services...")
        verifier.verify_directory(insights_path)
    
    # Generate report
    print("")
    print("Generating report...")
    print("")
    
    # Get all results (we'll use a simplified approach)
    results = []
    for file in verifier.results["services_non_compliant"]:
        full_path = base_path / file
        if full_path.exists():
            results.append(verifier.verify_service_file(full_path))
    
    report = verifier.generate_report(results)
    print(report)
    
    # Save report
    report_path = base_path / "docs" / "final_production_docs" / "ERROR_HANDLING_VERIFICATION_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    print(f"\nReport saved to: {report_path}")
    
    # Return exit code
    if verifier.results["services_non_compliant"]:
        print(f"\n⚠️  Found {len(verifier.results['services_non_compliant'])} non-compliant services")
        return 1
    else:
        print("\n✅ All checked services are compliant!")
        return 0


if __name__ == "__main__":
    sys.exit(main())

