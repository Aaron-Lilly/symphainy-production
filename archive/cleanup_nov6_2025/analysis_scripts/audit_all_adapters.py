#!/usr/bin/env python3
"""
Audit All Public Works Foundation Adapters

Systematically checks each adapter for real implementations vs. simulations.
"""

import os
import sys
import re
from pathlib import Path

def audit_file(file_path, search_for_simulation_patterns=True):
    """Audit a single file for simulation patterns."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check for simulation patterns
    if search_for_simulation_patterns:
        simulation_patterns = [
            (r'# Simulate.*\n', "Has comment indicating simulation"),
            (r'await asyncio\.sleep\(0\.001\)', "Has simulated async sleep"),
            (r'return \{\s*"test_', "Returns hard-coded test data"),
            (r'return "test_', "Returns hard-coded test string"),
            (r'MockRedis|Mock[A-Z]\w+', "Uses mock classes"),
            (r'# Mock|# Fake|# Simulate', "Has mock comment"),
        ]
        
        for pattern, description in simulation_patterns:
            matches = re.findall(pattern, content)
            if matches:
                issues.append(f"  ❌ {description}")
    
    # Check for real implementations
    real_patterns = [
        (r'import redis', "Imports real redis library"),
        (r'from redis\.', "Uses real redis package"),
        (r'import jwt|import jose', "Imports JWT library"),
        (r'from celery', "Uses Celery library"),
        (r'from supabase', "Uses Supabase library"),
        (r'await self\.client\.', "Actually calls client methods"),
    ]
    
    for pattern, description in real_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"  ✅ {description}")
    
    return issues

def main():
    """Main audit function."""
    
    adapters_dir = Path("symphainy-platform/foundations/public_works_foundation/infrastructure_adapters")
    
    if not adapters_dir.exists():
        print(f"❌ Directory not found: {adapters_dir}")
        return
    
    print("=" * 70)
    print("🔍 AUDITING ALL PUBLIC WORKS FOUNDATION ADAPTERS")
    print("=" * 70)
    
    # List all Python files in the adapters directory
    adapter_files = sorted(adapters_dir.glob("*.py"))
    
    for adapter_file in adapter_files:
        if adapter_file.name.startswith("__"):
            continue
        
        print(f"\n📄 {adapter_file.name}")
        
        issues = audit_file(adapter_file)
        
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("  ⚠️  No clear indicators found")
    
    print("\n" + "=" * 70)
    print("✅ AUDIT COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()


