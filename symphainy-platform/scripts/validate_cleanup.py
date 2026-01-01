#!/usr/bin/env python3
"""
Safe Validation Script for Technical Debt Cleanup

This script ONLY validates - it doesn't make any changes.
Use this to test before and after each cleanup step.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_critical_imports():
    """Test that critical services still import successfully."""
    print("🔍 Testing Critical Service Imports...")
    print("=" * 50)
    
    critical_services = [
        'backend.business_enablement.pillars.content_pillar.content_pillar_service',
        'backend.business_enablement.pillars.delivery_manager.delivery_manager_service',
        'foundations.public_works_foundation.public_works_foundation_service',
        'experience.roles.journey_manager.journey_manager_service',
        'experience.roles.frontend_integration.frontend_integration_service',
        'backend.smart_city.services.data_steward.mcp_server.data_steward_mcp_server',
        'backend.smart_city.services.city_manager.mcp_server.city_manager_mcp_server'
    ]
    
    all_working = True
    working_count = 0
    
    for service in critical_services:
        try:
            __import__(service)
            print(f'✅ {service}: Import successful')
            working_count += 1
        except Exception as e:
            print(f'❌ {service}: Import failed - {e}')
            all_working = False
    
    print(f"\n📊 Results: {working_count}/{len(critical_services)} services working")
    
    if all_working:
        print('🎉 All critical services working!')
        return True
    else:
        print('❌ Some services broken - investigation needed!')
        return False

def check_parallel_implementations():
    """Check for remaining parallel implementations."""
    print("\n🔍 Checking for Parallel Implementations...")
    print("=" * 50)
    
    # Check for _new files
    new_files = list(project_root.rglob("*_new.py"))
    if new_files:
        print(f"⚠️  Found {len(new_files)} *_new.py files:")
        for file in new_files:
            print(f"   {file.relative_to(project_root)}")
    else:
        print("✅ No *_new.py files found")
    
    # Check for _refactored files
    refactored_files = list(project_root.rglob("*_refactored.py"))
    if refactored_files:
        print(f"⚠️  Found {len(refactored_files)} *_refactored.py files:")
        for file in refactored_files:
            print(f"   {file.relative_to(project_root)}")
    else:
        print("✅ No *_refactored.py files found")
    
    # Check for _old files (excluding archived)
    old_files = [f for f in project_root.rglob("*_old.py") 
                 if "archived" not in str(f) and "_archived" not in str(f)]
    if old_files:
        print(f"⚠️  Found {len(old_files)} *_old.py files (excluding archived):")
        for file in old_files:
            print(f"   {file.relative_to(project_root)}")
    else:
        print("✅ No *_old.py files found (excluding archived)")

def check_import_consistency():
    """Check that __init__.py files are importing from standard names."""
    print("\n🔍 Checking Import Consistency...")
    print("=" * 50)
    
    init_files = [
        "backend/business_enablement/pillars/content_pillar/__init__.py",
        "backend/business_enablement/pillars/delivery_manager/__init__.py",
        "foundations/public_works_foundation/__init__.py"
    ]
    
    for init_file in init_files:
        init_path = project_root / init_file
        if init_path.exists():
            with open(init_path, 'r') as f:
                content = f.read()
                if '_new' in content or '_refactored' in content or '_old' in content:
                    print(f"⚠️  {init_file} contains non-standard imports:")
                    for line_num, line in enumerate(content.split('\n'), 1):
                        if '_new' in line or '_refactored' in line or '_old' in line:
                            print(f"   Line {line_num}: {line.strip()}")
                else:
                    print(f"✅ {init_file}: Clean imports")

def main():
    """Main validation function."""
    print("🔧 Technical Debt Cleanup Validation")
    print("=" * 60)
    
    # Test critical imports
    imports_ok = test_critical_imports()
    
    # Check for parallel implementations
    check_parallel_implementations()
    
    # Check import consistency
    check_import_consistency()
    
    print("\n🎯 Overall Status:")
    if imports_ok:
        print("✅ Foundation is stable - safe to proceed with cleanup")
    else:
        print("❌ Foundation has issues - fix before proceeding")
    
    return imports_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

















