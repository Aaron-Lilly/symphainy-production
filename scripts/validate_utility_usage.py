#!/usr/bin/env python3
"""
Utility Usage Validator

Systematically checks if services are using foundational utilities:
1. Error handling utility
2. Telemetry and health reporting
3. Authorization (user context)
4. Multi-tenancy
5. Zero trust (secure by design, open by policy)
6. Other utilities as appropriate

This validator identifies services that have access to utilities via base classes
but aren't actually using them - a critical architectural gap.
"""

import os
import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class UtilityUsageViolation:
    """Represents a utility usage violation."""
    file_path: str
    line_number: int
    violation_type: str
    violation_message: str
    context: str = ""


@dataclass
class ServiceUtilityUsage:
    """Utility usage summary for a service."""
    service_name: str
    file_path: str
    has_error_handler: bool = False
    has_telemetry: bool = False
    has_health: bool = False
    has_security: bool = False
    has_tenant: bool = False
    has_config: bool = False
    try_except_blocks: int = 0
    operations_without_tracking: int = 0
    violations: List[UtilityUsageViolation] = field(default_factory=list)


class UtilityUsageValidator:
    """Validates utility usage in services."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.violations: List[UtilityUsageViolation] = []
        self.service_usage: Dict[str, ServiceUtilityUsage] = {}
        
        # Utility method patterns
        self.error_handler_patterns = [
            r'get_error_handler\(\)',
            r'handle_error_with_audit\(',
            r'error_handler\.',
            r'self\.error_handler',
        ]
        
        self.telemetry_patterns = [
            r'get_telemetry\(\)',
            r'track_performance\(',
            r'record_telemetry_event\(',
            r'record_telemetry_metric\(',
            r'telemetry\.',
            r'self\.telemetry',
        ]
        
        self.health_patterns = [
            r'get_health\(\)',
            r'health_check\(',
            r'record_health_metric\(',
            r'health\.',
            r'self\.health',
        ]
        
        self.security_patterns = [
            r'get_security\(\)',
            r'validate_access\(',
            r'validate_tenant_access\(',
            r'set_security_context\(',
            r'get_tenant_id\(',
            r'get_user_id\(',
            r'security\.',
            r'self\.security',
        ]
        
        self.tenant_patterns = [
            r'get_tenant\(\)',
            r'get_tenant_id\(',
            r'validate_tenant_access\(',
            r'tenant\.',
            r'self\.tenant',
        ]
        
        self.config_patterns = [
            r'get_config\(\)',
            r'get_configuration\(',
            r'config\.',
            r'self\.config',
        ]
    
    def validate_directory(self, directory: str) -> Dict[str, Any]:
        """Validate all services in a directory."""
        dir_path = self.project_root / directory
        
        if not dir_path.exists():
            return {
                "directory": directory,
                "exists": False,
                "violations": [],
                "services": {}
            }
        
        services = {}
        
        # Find all Python service files
        for py_file in dir_path.rglob("*.py"):
            # Skip test files, __init__, and archive
            if any(skip in str(py_file) for skip in ["test_", "__pycache__", "archive", "tests"]):
                continue
            
            # Check if it's a service file (contains class that extends base)
            if self._is_service_file(py_file):
                service_usage = self.validate_file(str(py_file))
                if service_usage:
                    services[service_usage.service_name] = service_usage
        
        return {
            "directory": directory,
            "exists": True,
            "violations": self.violations,
            "services": services,
            "summary": self._generate_summary(services)
        }
    
    def _is_service_file(self, file_path: Path) -> bool:
        """Check if file is a service file."""
        try:
            content = file_path.read_text()
            # Check for base class inheritance
            if any(base in content for base in [
                "RealmServiceBase",
                "FoundationServiceBase",
                "SmartCityRoleBase",
                "OrchestratorBase",
                "ManagerServiceBase"
            ]):
                return True
        except Exception:
            pass
        return False
    
    def validate_file(self, file_path: str) -> Optional[ServiceUtilityUsage]:
        """Validate utility usage in a single file."""
        try:
            full_path = self.project_root / file_path if not Path(file_path).is_absolute() else Path(file_path)
            content = full_path.read_text()
            lines = content.split('\n')
            
            # Extract service name
            service_name = self._extract_service_name(content, full_path)
            if not service_name:
                return None
            
            usage = ServiceUtilityUsage(
                service_name=service_name,
                file_path=str(full_path.relative_to(self.project_root))
            )
            
            # Check for utility usage
            usage.has_error_handler = self._has_pattern(content, self.error_handler_patterns)
            usage.has_telemetry = self._has_pattern(content, self.telemetry_patterns)
            usage.has_health = self._has_pattern(content, self.health_patterns)
            usage.has_security = self._has_pattern(content, self.security_patterns)
            usage.has_tenant = self._has_pattern(content, self.tenant_patterns)
            usage.has_config = self._has_pattern(content, self.config_patterns)
            
            # Count try/except blocks
            usage.try_except_blocks = len(re.findall(r'\btry\s*:', content))
            
            # Find violations
            self._find_violations(usage, content, lines)
            
            return usage
            
        except Exception as e:
            print(f"Error validating {file_path}: {e}")
            return None
    
    def _extract_service_name(self, content: str, file_path: Path) -> Optional[str]:
        """Extract service name from file."""
        # Try to find class definition
        match = re.search(r'class\s+(\w+(?:Service|Orchestrator|Manager|Agent))', content)
        if match:
            return match.group(1)
        
        # Fallback to filename
        return file_path.stem.replace('_', ' ').title().replace(' ', '')
    
    def _has_pattern(self, content: str, patterns: List[str]) -> bool:
        """Check if content has any of the patterns."""
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False
    
    def _find_violations(self, usage: ServiceUtilityUsage, content: str, lines: List[str]):
        """Find utility usage violations."""
        # Check for try/except without error handler
        if usage.try_except_blocks > 0 and not usage.has_error_handler:
            for i, line in enumerate(lines, 1):
                if 'try:' in line:
                    # Check if error handler is used in this try block
                    # Look ahead for except block
                    try_end = self._find_except_block(lines, i-1)
                    if try_end:
                        try_block = '\n'.join(lines[i-1:try_end])
                        if not self._has_pattern(try_block, self.error_handler_patterns):
                            usage.violations.append(UtilityUsageViolation(
                                file_path=usage.file_path,
                                line_number=i,
                                violation_type="MISSING_ERROR_HANDLER",
                                violation_message="try/except block without error_handler utility usage",
                                context=line.strip()
                            ))
        
        # Check for async methods without telemetry
        async_methods = re.finditer(r'async\s+def\s+(\w+)\(', content)
        for match in async_methods:
            method_name = match.group(1)
            method_start = match.start()
            method_end = self._find_method_end(content, method_start)
            if method_end:
                method_content = content[method_start:method_end]
                # Skip if it's a private method or test
                if method_name.startswith('_') or 'test' in method_name.lower():
                    continue
                
                # Check if method has telemetry tracking
                if not self._has_pattern(method_content, self.telemetry_patterns):
                    # Check if it's a significant operation (not just getters)
                    if any(op in method_name.lower() for op in ['parse', 'analyze', 'process', 'execute', 'create', 'update', 'delete']):
                        line_num = content[:method_start].count('\n') + 1
                        usage.violations.append(UtilityUsageViolation(
                            file_path=usage.file_path,
                            line_number=line_num,
                            violation_type="MISSING_TELEMETRY",
                            violation_message=f"Operation method '{method_name}' without telemetry tracking",
                            context=f"async def {method_name}(...)"
                        ))
        
        # Check for operations without security validation
        public_methods = re.finditer(r'async\s+def\s+(\w+)\(', content)
        for match in public_methods:
            method_name = match.group(1)
            method_start = match.start()
            method_end = self._find_method_end(content, method_start)
            if method_end:
                method_content = content[method_start:method_end]
                # Skip if it's a private method
                if method_name.startswith('_'):
                    continue
                
                # Check if method validates access
                if not self._has_pattern(method_content, self.security_patterns):
                    # Check if it's a data access operation
                    if any(op in method_name.lower() for op in ['get', 'retrieve', 'store', 'save', 'delete', 'update', 'create']):
                        line_num = content[:method_start].count('\n') + 1
                        usage.violations.append(UtilityUsageViolation(
                            file_path=usage.file_path,
                            line_number=line_num,
                            violation_type="MISSING_SECURITY",
                            violation_message=f"Data access method '{method_name}' without security validation",
                            context=f"async def {method_name}(...)"
                        ))
        
        # Check for data operations without tenant validation
        data_methods = re.finditer(r'async\s+def\s+(\w+)\(', content)
        for match in data_methods:
            method_name = match.group(1)
            method_start = match.start()
            method_end = self._find_method_end(content, method_start)
            if method_end:
                method_content = content[method_start:method_end]
                # Skip if it's a private method
                if method_name.startswith('_'):
                    continue
                
                # Check if method validates tenant
                if not self._has_pattern(method_content, self.tenant_patterns):
                    # Check if it's a data operation
                    if any(op in method_name.lower() for op in ['store', 'save', 'retrieve', 'get', 'query', 'search']):
                        line_num = content[:method_start].count('\n') + 1
                        usage.violations.append(UtilityUsageViolation(
                            file_path=usage.file_path,
                            line_number=line_num,
                            violation_type="MISSING_TENANT",
                            violation_message=f"Data operation method '{method_name}' without tenant validation",
                            context=f"async def {method_name}(...)"
                        ))
    
    def _find_except_block(self, lines: List[str], start_line: int) -> Optional[int]:
        """Find the end of an except block."""
        indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        for i in range(start_line + 1, len(lines)):
            if lines[i].strip() and not lines[i].startswith(' ' * (indent_level + 1)) and not lines[i].startswith('\t'):
                if 'except' in lines[i] or 'finally' in lines[i]:
                    # Find end of except/finally block
                    except_indent = len(lines[i]) - len(lines[i].lstrip())
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith(' ' * (except_indent + 1)):
                            return j
                    return len(lines)
        return None
    
    def _find_method_end(self, content: str, start_pos: int) -> Optional[int]:
        """Find the end of a method definition."""
        lines = content[start_pos:].split('\n')
        indent_level = len(lines[0]) - len(lines[0].lstrip())
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip():
                line_indent = len(line) - len(line.lstrip())
                if line_indent <= indent_level and not line.strip().startswith('#'):
                    return start_pos + len('\n'.join(lines[:i]))
        
        return start_pos + len(content[start_pos:])
    
    def _generate_summary(self, services: Dict[str, ServiceUtilityUsage]) -> Dict[str, Any]:
        """Generate summary statistics."""
        total_services = len(services)
        
        error_handler_usage = sum(1 for s in services.values() if s.has_error_handler)
        telemetry_usage = sum(1 for s in services.values() if s.has_telemetry)
        health_usage = sum(1 for s in services.values() if s.has_health)
        security_usage = sum(1 for s in services.values() if s.has_security)
        tenant_usage = sum(1 for s in services.values() if s.has_tenant)
        config_usage = sum(1 for s in services.values() if s.has_config)
        
        total_violations = sum(len(s.violations) for s in services.values())
        violations_by_type = defaultdict(int)
        for service in services.values():
            for violation in service.violations:
                violations_by_type[violation.violation_type] += 1
        
        return {
            "total_services": total_services,
            "utility_usage": {
                "error_handler": {"used": error_handler_usage, "percentage": (error_handler_usage / total_services * 100) if total_services > 0 else 0},
                "telemetry": {"used": telemetry_usage, "percentage": (telemetry_usage / total_services * 100) if total_services > 0 else 0},
                "health": {"used": health_usage, "percentage": (health_usage / total_services * 100) if total_services > 0 else 0},
                "security": {"used": security_usage, "percentage": (security_usage / total_services * 100) if total_services > 0 else 0},
                "tenant": {"used": tenant_usage, "percentage": (tenant_usage / total_services * 100) if total_services > 0 else 0},
                "config": {"used": config_usage, "percentage": (config_usage / total_services * 100) if total_services > 0 else 0},
            },
            "total_violations": total_violations,
            "violations_by_type": dict(violations_by_type),
            "services_with_violations": sum(1 for s in services.values() if s.violations),
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate utility usage in services")
    parser.add_argument("--directory", type=str, help="Directory to validate", default="symphainy-platform/backend")
    parser.add_argument("--output", type=str, help="Output file for results", default="utility_usage_validation_results.json")
    parser.add_argument("--project-root", type=str, help="Project root directory", default=".")
    
    args = parser.parse_args()
    
    validator = UtilityUsageValidator(args.project_root)
    
    # Validate directories
    directories_to_check = [
        "symphainy-platform/backend/business_enablement",
        "symphainy-platform/backend/smart_city",
        "symphainy-platform/foundations",
    ]
    
    results = {}
    for directory in directories_to_check:
        print(f"Validating {directory}...")
        result = validator.validate_directory(directory)
        results[directory] = result
    
    # Print summary
    print("\n" + "="*80)
    print("UTILITY USAGE VALIDATION SUMMARY")
    print("="*80)
    
    for directory, result in results.items():
        if not result.get("exists"):
            continue
        
        summary = result.get("summary", {})
        print(f"\n{directory}:")
        print(f"  Total Services: {summary.get('total_services', 0)}")
        print(f"  Total Violations: {summary.get('total_violations', 0)}")
        print(f"  Services with Violations: {summary.get('services_with_violations', 0)}")
        
        utility_usage = summary.get("utility_usage", {})
        print(f"\n  Utility Usage:")
        for utility, stats in utility_usage.items():
            print(f"    {utility}: {stats['used']}/{summary.get('total_services', 0)} ({stats['percentage']:.1f}%)")
        
        violations_by_type = summary.get("violations_by_type", {})
        if violations_by_type:
            print(f"\n  Violations by Type:")
            for vtype, count in violations_by_type.items():
                print(f"    {vtype}: {count}")
    
    # Save results
    import json
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to {output_path}")
    
    return 0 if all(r.get("summary", {}).get("total_violations", 0) == 0 for r in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

