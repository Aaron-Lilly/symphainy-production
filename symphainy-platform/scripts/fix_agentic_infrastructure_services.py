#!/usr/bin/env python3
"""
Helper script to add utilities to Agentic Foundation infrastructure enablement services.

This script helps identify methods that need utilities added, but manual review
and fixing is required to ensure proper security/tenant validation.
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Any

def find_methods_needing_utilities(file_path: Path) -> List[Dict[str, Any]]:
    """Find methods that need utilities added."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    tree = ast.parse(content)
    methods = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            method_source = ast.get_source_segment(content, node)
            method_name = node.name
            
            # Skip private methods that start with __
            if method_name.startswith('__') and not method_name.startswith('__init__'):
                continue
            
            # Check if method has utilities
            has_telemetry_start = 'log_operation_with_telemetry' in method_source
            has_error_handling = 'handle_error_with_audit' in method_source
            has_health_metric = 'record_health_metric' in method_source
            
            if not (has_telemetry_start and has_error_handling):
                methods.append({
                    "name": method_name,
                    "line": node.lineno,
                    "has_telemetry": has_telemetry_start,
                    "has_error_handling": has_error_handling,
                    "has_health_metric": has_health_metric
                })
    
    return methods

def main():
    """Main function to analyze infrastructure enablement services."""
    infra_dir = Path("symphainy-platform/foundations/agentic_foundation/infrastructure_enablement")
    
    print("🔍 Analyzing infrastructure enablement services...\n")
    
    for file_path in infra_dir.glob("*.py"):
        if file_path.name == "__init__.py":
            continue
        
        print(f"\n📄 {file_path.name}")
        print("=" * 60)
        
        try:
            methods = find_methods_needing_utilities(file_path)
            if methods:
                print(f"⚠️  {len(methods)} methods need utilities:")
                for method in methods[:10]:  # Show first 10
                    status = []
                    if not method["has_telemetry"]:
                        status.append("telemetry")
                    if not method["has_error_handling"]:
                        status.append("error_handling")
                    if not method["has_health_metric"]:
                        status.append("health_metric")
                    print(f"  - {method['name']} (line {method['line']}): missing {', '.join(status)}")
                if len(methods) > 10:
                    print(f"  ... and {len(methods) - 10} more")
            else:
                print("✅ All methods have utilities")
        except Exception as e:
            print(f"❌ Error analyzing {file_path.name}: {e}")

if __name__ == "__main__":
    main()







