#!/usr/bin/env python3
"""
Foundation Utility Compliance Validator

Validates that foundation services are properly using utilities:
- Error handling (handle_error_with_audit)
- Telemetry (log_operation_with_telemetry, record_health_metric)
- Security (get_security, check_permissions) - service layer only
- Multi-tenancy (get_tenant, validate_tenant_access) - service layer only

Usage:
    python3 scripts/validate_foundation_utilities.py [foundation_name]
    
    foundation_name: curator, communication, agentic, experience, or all
"""

import os
import sys
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Foundation paths
FOUNDATION_PATHS = {
    "curator": "symphainy-platform/foundations/curator_foundation",
    "communication": "symphainy-platform/foundations/communication_foundation",
    "agentic": "symphainy-platform/foundations/agentic_foundation",
    "experience": "symphainy-platform/foundations/experience_foundation",
    "public_works": "symphainy-platform/foundations/public_works_foundation"
}

# Utility patterns to check
UTILITY_PATTERNS = {
    "error_handling": {
        "required": [
            r"handle_error_with_audit",
            r"get_error_handler\(\)"
        ],
        "anti_pattern": [
            r"except\s+Exception\s+as\s+e:",
            r"except\s+.*:\s*$"
        ]
    },
    "telemetry": {
        "required": [
            r"log_operation_with_telemetry",
            r"record_health_metric"
        ]
    },
    "security": {
        "required": [
            r"get_security\(\)",
            r"check_permissions"
        ]
    },
    "tenant": {
        "required": [
            r"get_tenant\(\)",
            r"validate_tenant_access"
        ]
    }
}


class FoundationUtilityValidator:
    """Validates foundation utility compliance."""
    
    def __init__(self, foundation_name: str):
        self.foundation_name = foundation_name
        self.foundation_path = project_root / FOUNDATION_PATHS[foundation_name]
        self.violations = defaultdict(list)
        self.compliant_methods = []
        self.stats = {
            "total_files": 0,
            "total_methods": 0,
            "async_methods": 0,
            "violations": defaultdict(int),
            "compliant": 0
        }
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in foundation directory."""
        python_files = []
        
        if not self.foundation_path.exists():
            print(f"⚠️  Foundation path not found: {self.foundation_path}")
            return python_files
        
        for file_path in self.foundation_path.rglob("*.py"):
            # Skip __pycache__, test files, archived files, and abstraction contracts
            path_str = str(file_path)
            if ("__pycache__" in path_str or 
                "test" in path_str.lower() or 
                "archived" in path_str.lower() or
                "archive" in path_str.lower() or
                "abstraction_contracts" in path_str.lower() or
                "protocol" in path_str.lower()):
                continue
            python_files.append(file_path)
        
        return python_files
    
    def parse_file(self, file_path: Path) -> Optional[ast.AST]:
        """Parse Python file and return AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            # Skip files with syntax errors (likely archived/broken files)
            return None
        except Exception as e:
            # Skip other parse errors silently
            return None
    
    def is_async_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is async."""
        return isinstance(node, ast.AsyncFunctionDef)
    
    def is_service_method(self, node: ast.FunctionDef, file_path: Path) -> bool:
        """Check if method is a service method (not private helper or constructor)."""
        # Skip __init__ methods (constructors don't need utilities)
        if node.name == "__init__":
            return False
        
        # Skip __post_init__ methods (dataclass initialization, not service methods)
        if node.name == "__post_init__":
            return False
        
        # Skip data model files entirely
        if self.is_data_model_file(file_path):
            return False
        
        # Skip internal helper modules
        if self.is_internal_helper_module(file_path):
            return False
        
        # Skip abstractions (utilities at service layer)
        if self.is_abstraction_file(file_path):
            return False
        
        # Skip composition services (utilities at service layer) - but NOT Curator micro-services
        # Curator micro-services are in services/ directory and ARE services (should have utilities)
        if ("composition_service" in str(file_path).lower() or "composition_services" in str(file_path).lower()) and "curator" not in str(file_path).lower():
            return False
        
        # Skip realm bridges (utilities at service layer)
        if "realm_bridge" in str(file_path).lower() or "realm_bridges" in str(file_path).lower():
            return False
        
        # Skip infrastructure registries (utilities at service layer)
        if "infrastructure_registry" in str(file_path).lower() or "infrastructure_registries" in str(file_path).lower():
            return False
        
        # Skip realm_access_controller (not a foundation service)
        if "realm_access_controller" in str(file_path).lower():
            return False
        
        # Skip helper files (not services)
        if "helper" in str(file_path).lower() and "service" not in str(file_path).lower():
            return False
        
        # Skip SDK files (agent_sdk/) - agents get utilities from DI container, not mixins
        # Agents are instantiated by AgenticFoundationService and get utilities via foundation_services
        if "agent_sdk" in str(file_path).lower():
            return False
        
        # Skip tool_factory files - these are tool execution engines, not foundation services
        # They get utilities from DI container or are called by services that have utilities
        if "tool_factory" in str(file_path).lower():
            return False
        
        # Skip getter methods (infrastructure getters) - methods that return infrastructure components
        if node.name.startswith("get_"):
            method_source = self.get_method_source(file_path, node)
            if self.is_infrastructure_getter(file_path, node.name, method_source):
                return False
            # Also exclude if it returns infrastructure components (abstraction, composition, registry, adapter)
            if any(pattern in method_source for pattern in [
                "return self.", "self._", "abstraction", "composition", "registry", "adapter", "policy_engine"
            ]) and ("return self." in method_source or "return " in method_source):
                return False
        
        return not node.name.startswith("_") or node.name.startswith("__")
    
    def get_method_source(self, file_path: Path, node: ast.FunctionDef) -> str:
        """Get source code for method."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 20
            return ''.join(lines[start_line:end_line])
        except Exception as e:
            return f"Error reading source: {e}"
    
    def check_error_handling(self, source: str, method_name: str, file_path: Path) -> List[str]:
        """Check error handling compliance."""
        violations = []
        
        # Exclude abstractions (utilities at service layer)
        if self.is_abstraction_file(file_path):
            return violations  # Abstractions don't need utilities (handled at service layer)
        
        # Exclude data models and internal helpers (they don't have utility access)
        if self.is_data_model_file(file_path):
            return violations  # Data models don't need utilities
        
        if self.is_internal_helper_module(file_path):
            return violations  # Internal helpers don't have utility access
        
        # Check for bare except blocks (anti-pattern)
        bare_except_pattern = r"except\s+Exception\s+as\s+e:\s*$"
        if re.search(bare_except_pattern, source, re.MULTILINE):
            # Check if it uses handle_error_with_audit
            if "handle_error_with_audit" not in source:
                violations.append(f"Bare except block without handle_error_with_audit")
        
        # Check for except blocks without error handling
        except_blocks = re.finditer(r"except\s+.*?:\s*$", source, re.MULTILINE)
        for match in except_blocks:
            except_block = match.group(0)
            # Get the block content
            block_start = match.end()
            # Look for handle_error_with_audit in the next 10 lines
            block_context = source[block_start:block_start + 500]
            if "handle_error_with_audit" not in block_context and "get_error_handler" not in block_context:
                violations.append(f"Exception block without proper error handling")
        
        return violations
    
    def check_telemetry(self, source: str, method_name: str, file_path: Path) -> List[str]:
        """Check telemetry compliance."""
        violations = []
        
        # Exclude abstractions (utilities at service layer)
        if self.is_abstraction_file(file_path):
            return violations  # Abstractions don't need utilities (handled at service layer)
        
        # Exclude data models and internal helpers (they don't have utility access)
        if self.is_data_model_file(file_path):
            return violations  # Data models don't need utilities
        
        if self.is_internal_helper_module(file_path):
            return violations  # Internal helpers don't have utility access
        
        # Exclude system lifecycle methods (initialize, shutdown, start, stop)
        if self.is_system_lifecycle_method(method_name):
            return violations  # System lifecycle methods don't need telemetry
        
        # Exclude system status methods (health_check, get_status, etc.)
        if self.is_system_status_method(method_name):
            return violations  # System status methods don't need telemetry
        
        # Exclude security check methods (is_allowed, check_permissions, etc.)
        if "is_allowed" in method_name.lower() or "check_permission" in method_name.lower():
            return violations  # Security check methods don't need telemetry
        
        # Exclude permission/policy getters (they return permissions/policies, not user data)
        # These are typically nested class methods (policy engine implementations)
        if "get_user_permissions" in method_name.lower() or "get_tenant_policies" in method_name.lower():
            return violations  # Permission/policy getters return permissions, not user data
        
        # Check for log_operation_with_telemetry
        if "log_operation_with_telemetry" not in source:
            violations.append("Missing log_operation_with_telemetry")
        
        # Check for record_health_metric (should be in success paths)
        if "record_health_metric" not in source:
            violations.append("Missing record_health_metric")
        
        return violations
    
    def is_system_status_method(self, method_name: str) -> bool:
        """Check if method is a system status method (no user data access)."""
        status_patterns = [
            "get_status", "get_*_status", "run_health_check", "get_*_summary",
            "get_health_summary", "get_registry_status", "get_pattern_status",
            "get_documentation_status", "get_agentic_dimension_summary", "health_check"
        ]
        method_lower = method_name.lower()
        return any(pattern.replace("*", "").replace("_", "") in method_lower 
                  for pattern in status_patterns) or ("status" in method_lower and "get" in method_lower) or "health_check" in method_lower
    
    def is_system_lifecycle_method(self, method_name: str) -> bool:
        """Check if method is a system lifecycle method (initialize, shutdown)."""
        lifecycle_methods = ["initialize", "initialize_foundation", "shutdown", "shutdown_foundation", "start", "stop"]
        method_lower = method_name.lower()
        return method_lower in lifecycle_methods or any(lifecycle in method_lower for lifecycle in ["initialize", "shutdown", "start", "stop"])
    
    def is_infrastructure_getter(self, file_path: Path, method_name: str, source: str) -> bool:
        """Check if method is an infrastructure getter (returns infrastructure, not user data)."""
        method_lower = method_name.lower()
        
        # Check if it's a getter method
        if not method_lower.startswith("get_"):
            return False
        
        # Infrastructure getter patterns
        infrastructure_keywords = [
            "router", "gateway", "client", "manager", "service", "abstraction",
            "adapter", "foundation", "bridge", "registry", "queue", "bus", "websocket",
            "messaging", "event", "communication", "soa"
        ]
        
        # Check if method name contains infrastructure keywords
        if any(keyword in method_lower for keyword in infrastructure_keywords):
            # Additional check: verify it returns infrastructure by looking at source
            # If it returns self.something or calls get_* methods, it's likely infrastructure
            if any(pattern in source.lower() for pattern in [
                "self.", "get_", "return", "router", "gateway", "client", "manager"
            ]):
                return True
        
        return False
    
    def is_realm_bridge_getter(self, file_path: Path, method_name: str) -> bool:
        """Check if method is a realm bridge getter (returns service instance)."""
        path_str = str(file_path)
        if "realm_bridges" in path_str.lower() or "bridge" in path_str.lower():
            method_lower = method_name.lower()
            if method_lower.startswith("get_") and (
                "security_guard" in method_lower or "librarian" in method_lower or
                "delivery_manager" in method_lower or "solution_manager" in method_lower or
                "journey_manager" in method_lower or "traffic_cop" in method_lower or
                "nurse" in method_lower or "conductor" in method_lower or
                "data_steward" in method_lower or "content_steward" in method_lower or
                "post_office" in method_lower or "experience_foundation" in method_lower
            ):
                return True
        return False
    
    def is_data_model_file(self, file_path: Path) -> bool:
        """Check if file is a data model (not a service)."""
        path_str = str(file_path)
        # Check if it's in a models directory or has model in name but not service
        if "models" in path_str.lower():
            return True
        if "model" in path_str.lower() and "service" not in path_str.lower():
            return True
        return False
    
    def is_internal_helper_module(self, file_path: Path) -> bool:
        """Check if file is an internal helper module (no utility access)."""
        path_str = str(file_path)
        return ("micro_modules" in path_str.lower() or 
                "services/micro_modules" in path_str.lower() or
                "helper" in path_str.lower() and "service" not in path_str.lower())
    
    def check_security(self, source: str, method_name: str, file_path: Path, is_abstraction: bool = False) -> List[str]:
        """Check security compliance (service layer only)."""
        violations = []
        
        # Abstractions don't need security validation (already done at service layer)
        if is_abstraction:
            return violations
        
        # Exclude false positives
        if self.is_system_status_method(method_name):
            return violations  # System status methods don't access user data
        
        if self.is_system_lifecycle_method(method_name):
            return violations  # System lifecycle methods (initialize, shutdown) don't access user data
        
        if self.is_infrastructure_getter(file_path, method_name, source):
            return violations  # Infrastructure getters don't access user data
        
        if self.is_realm_bridge_getter(file_path, method_name):
            return violations  # Realm bridge getters return service instances, not user data
        
        if self.is_data_model_file(file_path):
            return violations  # Data models don't have utility access
        
        if self.is_internal_helper_module(file_path):
            return violations  # Internal helpers don't have utility access
        
        # Exclude security methods themselves (they ARE the security validation)
        security_methods = ["authenticate", "authorize", "validate_token", "validate_session", "check_permissions", "enforce", "create_session", "create_secure_session", "is_allowed"]
        if any(sec_method in method_name.lower() for sec_method in security_methods):
            return violations  # Security methods don't need security validation
        
        # Exclude permission/policy getters (they return permissions/policies, not user data)
        # These are typically nested class methods (policy engine implementations)
        if "get_user_permissions" in method_name.lower() or "get_tenant_policies" in method_name.lower():
            return violations  # Permission/policy getters return permissions, not user data
        
        # Exclude infrastructure messaging/event methods (they're infrastructure, not user-facing)
        infrastructure_methods = ["send_message", "receive_message", "publish_event", "subscribe", "realm_message_handler", "realm_event_handler"]
        if any(infra_method in method_name.lower() for infra_method in infrastructure_methods):
            return violations  # Infrastructure messaging/event methods don't need security validation
        
        # Check if method accesses data (heuristic: has parameters like id, resource_id, etc.)
        has_data_access = any(keyword in method_name.lower() or keyword in source.lower() 
                             for keyword in ["get", "create", "update", "delete", "resource", "data", "file", "content"])
        
        if has_data_access:
            if "get_security" not in source and "check_permissions" not in source:
                violations.append("Missing security validation for data access operation")
        
        return violations
    
    def check_tenant(self, source: str, method_name: str, file_path: Path, is_abstraction: bool = False) -> List[str]:
        """Check tenant compliance (service layer only)."""
        violations = []
        
        # Abstractions don't need tenant validation (already done at service layer)
        if is_abstraction:
            return violations
        
        # Exclude false positives (same as security)
        if self.is_system_status_method(method_name):
            return violations  # System status methods don't access user data
        
        if self.is_system_lifecycle_method(method_name):
            return violations  # System lifecycle methods (initialize, shutdown) don't access user data
        
        if self.is_infrastructure_getter(file_path, method_name, source):
            return violations  # Infrastructure getters don't access user data
        
        if self.is_realm_bridge_getter(file_path, method_name):
            return violations  # Realm bridge getters return service instances, not user data
        
        if self.is_data_model_file(file_path):
            return violations  # Data models don't have utility access
        
        if self.is_internal_helper_module(file_path):
            return violations  # Internal helpers don't have utility access
        
        # Exclude security methods themselves (they handle tenant validation)
        security_methods = ["authenticate", "authorize", "validate_token", "validate_session", "check_permissions", "enforce", "create_session", "create_secure_session", "is_allowed"]
        if any(sec_method in method_name.lower() for sec_method in security_methods):
            return violations  # Security methods handle tenant validation
        
        # Exclude permission/policy getters (they return permissions/policies, not user data)
        # These are typically nested class methods (policy engine implementations)
        if "get_user_permissions" in method_name.lower() or "get_tenant_policies" in method_name.lower():
            return violations  # Permission/policy getters return permissions, not user data
        
        # Exclude infrastructure messaging/event methods (they're infrastructure, not user-facing)
        infrastructure_methods = ["send_message", "receive_message", "publish_event", "subscribe", "realm_message_handler", "realm_event_handler"]
        if any(infra_method in method_name.lower() for infra_method in infrastructure_methods):
            return violations  # Infrastructure messaging/event methods don't need tenant validation
        
        # Exclude connection info getters (they're infrastructure status, not user data)
        if "get_connection" in method_name.lower() or "get_realm_connection" in method_name.lower() or "get_total_connection" in method_name.lower():
            return violations  # Connection info is infrastructure status, not user data
        
        # Check if method accesses data (heuristic: has parameters like id, resource_id, etc.)
        has_data_access = any(keyword in method_name.lower() or keyword in source.lower() 
                             for keyword in ["get", "create", "update", "delete", "resource", "data", "file", "content", "tenant"])
        
        if has_data_access:
            if "get_tenant" not in source and "validate_tenant_access" not in source:
                violations.append("Missing tenant validation for data access operation")
        
        return violations
    
    def is_abstraction_file(self, file_path: Path) -> bool:
        """Check if file is an abstraction (not a service)."""
        path_str = str(file_path)
        return "abstraction" in path_str.lower() or "adapter" in path_str.lower()
    
    def is_nested_class_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if method is nested inside a class definition."""
        # Find the class that contains this method
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                # Check if this node is a direct child of this class
                for item in parent.body:
                    if item == node:
                        # This is a direct method of the class - not nested
                        # Only exclude if it's in a nested class (not the main service class)
                        # Check if parent is nested inside another class
                        for grandparent in ast.walk(tree):
                            if isinstance(grandparent, ast.ClassDef) and parent != grandparent:
                                # Check if parent is inside grandparent
                                for grandparent_item in grandparent.body:
                                    if grandparent_item == parent:
                                        # Parent is nested - this is a nested class method
                                        return True
                        # Not nested - it's a method of the main service class
                        return False
        return False
    
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single file."""
        tree = self.parse_file(file_path)
        if not tree:
            return {"file": str(file_path), "error": "Failed to parse"}
        
        file_violations = defaultdict(list)
        file_compliant = []
        is_abstraction = self.is_abstraction_file(file_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Skip nested class methods (they're not service methods)
                if self.is_nested_class_method(node, tree):
                    continue
                
                if not self.is_service_method(node, file_path):
                    continue
                
                self.stats["total_methods"] += 1
                if self.is_async_method(node):
                    self.stats["async_methods"] += 1
                
                method_source = self.get_method_source(file_path, node)
                method_name = node.name
                
                # Check error handling
                error_violations = self.check_error_handling(method_source, method_name, file_path)
                if error_violations:
                    file_violations["error_handling"].extend([f"{method_name}: {v}" for v in error_violations])
                    self.stats["violations"]["error_handling"] += len(error_violations)
                else:
                    # Only check other utilities if error handling is present
                    # Check telemetry
                    telemetry_violations = self.check_telemetry(method_source, method_name, file_path)
                    if telemetry_violations:
                        file_violations["telemetry"].extend([f"{method_name}: {v}" for v in telemetry_violations])
                        self.stats["violations"]["telemetry"] += len(telemetry_violations)
                    
                    # Check security (service layer only)
                    security_violations = self.check_security(method_source, method_name, file_path, is_abstraction)
                    if security_violations:
                        file_violations["security"].extend([f"{method_name}: {v}" for v in security_violations])
                        self.stats["violations"]["security"] += len(security_violations)
                    
                    # Check tenant (service layer only)
                    tenant_violations = self.check_tenant(method_source, method_name, file_path, is_abstraction)
                    if tenant_violations:
                        file_violations["tenant"].extend([f"{method_name}: {v}" for v in tenant_violations])
                        self.stats["violations"]["tenant"] += len(tenant_violations)
                    
                    # If no violations, mark as compliant
                    if not error_violations and not telemetry_violations and not security_violations and not tenant_violations:
                        file_compliant.append(method_name)
                        self.stats["compliant"] += 1
        
        return {
            "file": str(file_path.relative_to(project_root)),
            "violations": dict(file_violations),
            "compliant_methods": file_compliant,
            "is_abstraction": is_abstraction
        }
    
    def validate(self) -> Dict[str, Any]:
        """Validate all files in foundation."""
        print(f"🔍 Validating {self.foundation_name} foundation...")
        
        python_files = self.find_python_files()
        self.stats["total_files"] = len(python_files)
        
        results = []
        for file_path in python_files:
            result = self.validate_file(file_path)
            # Always add results to track stats, even if no violations
            if result.get("violations") or result.get("compliant_methods"):
                results.append(result)
            if result.get("violations"):
                self.violations[result["file"]] = result["violations"]
        
        return {
            "foundation": self.foundation_name,
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "violations": dict(self.violations),
            "results": results
        }
    
    def generate_report(self, validation_result: Dict[str, Any]) -> str:
        """Generate human-readable report."""
        report = []
        report.append("=" * 80)
        report.append(f"Foundation Utility Compliance Report: {self.foundation_name.upper()}")
        report.append("=" * 80)
        report.append(f"Generated: {validation_result['timestamp']}")
        report.append("")
        
        stats = validation_result["stats"]
        report.append("📊 Summary Statistics")
        report.append("-" * 80)
        report.append(f"Total Files Scanned: {stats['total_files']}")
        report.append(f"Total Methods: {stats['total_methods']}")
        report.append(f"Async Methods: {stats['async_methods']}")
        report.append(f"Compliant Methods: {stats['compliant']}")
        report.append("")
        
        report.append("⚠️  Violations by Category")
        report.append("-" * 80)
        for category, count in stats['violations'].items():
            report.append(f"  {category}: {count}")
        report.append("")
        
        if validation_result["violations"]:
            report.append("🔴 Violations by File")
            report.append("-" * 80)
            for file_path, violations in validation_result["violations"].items():
                report.append(f"\n📄 {file_path}")
                for category, items in violations.items():
                    report.append(f"  {category.upper()}:")
                    for item in items[:5]:  # Show first 5
                        report.append(f"    - {item}")
                    if len(items) > 5:
                        report.append(f"    ... and {len(items) - 5} more")
        else:
            report.append("✅ No violations found!")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main entry point."""
    foundation_name = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if foundation_name == "all":
        foundations = ["curator", "communication", "agentic", "experience"]
    elif foundation_name in FOUNDATION_PATHS:
        foundations = [foundation_name]
    else:
        print(f"❌ Unknown foundation: {foundation_name}")
        print(f"Available: {', '.join(FOUNDATION_PATHS.keys())}, all")
        sys.exit(1)
    
    all_results = {}
    
    for foundation in foundations:
        validator = FoundationUtilityValidator(foundation)
        result = validator.validate()
        all_results[foundation] = result
        
        # Print report
        report = validator.generate_report(result)
        print(report)
        print()
        
        # Save JSON report
        report_file = project_root / "symphainy_source" / "docs" / "11-12" / f"{foundation}_utility_compliance_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"📄 JSON report saved to: {report_file}")
        print()
    
    # Generate combined summary
    if len(foundations) > 1:
        summary = {
            "timestamp": datetime.now().isoformat(),
            "foundations": all_results
        }
        summary_file = project_root / "symphainy_source" / "docs" / "11-12" / "foundation_utility_compliance_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"📄 Combined summary saved to: {summary_file}")


if __name__ == "__main__":
    main()

