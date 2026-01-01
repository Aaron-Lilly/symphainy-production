#!/usr/bin/env python3
"""
SymphAIny Platform - Surgical Legacy Test Cleanup Script

This script surgically removes legacy test files while preserving the new architecture test environment.
"""

import os
import shutil
from pathlib import Path
import sys

def backup_legacy_files():
    """Create a backup of legacy files before deletion."""
    backup_dir = Path("archive/legacy_tests_backup")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Creating backup in {backup_dir}")
    return backup_dir

def identify_legacy_files():
    """Identify legacy test files that should be removed."""
    legacy_files = [
        # Phase-based legacy test files
        "phase_0_test_foundation_services.py",
        "phase_1_test_di_only.py", 
        "phase_1_test_public_works_refactored.py",
        "phase_2_test_conductor_refactored.py",
        "phase_2_test_data_steward_refactored.py",
        "phase_2_test_librarian_refactored.py",
        "phase_2_test_nurse_refactored.py",
        "phase_2_test_post_office_refactored.py",
        "phase_2_test_security_guard_refactored.py",
        "phase_2_test_smart_city_protocols.py",
        "phase_2_test_smart_city_protocols_clean.py",
        "phase_2_test_smart_city_protocols_old.py",
        "phase_2_test_traffic_cop_refactored.py",
        "phase_4_test_agentic_sdk_refactored.py",
        
        # Legacy run scripts
        "run_agentic_sdk_tests.py",
        "run_corrected_vision_tests.py",
        "run_dicontainer_tests.py",
        "run_journey_solution_tests.py",
        "run_new_architecture_tests.py",
        "run_platform_transformation_tests.py",
        
        # Legacy test directories (if they exist and are empty/outdated)
        "agentic",  # Old agentic tests
        "comprehensive",  # Old comprehensive tests
        "environments",  # Old environment tests
        "infrastructure",  # Old infrastructure tests
        "manager_vision",  # Old manager vision tests
        "mvp",  # Old MVP tests
        "observability",  # Old observability tests
        "real_implementations",  # Old real implementation tests
    ]
    
    return legacy_files

def identify_preserve_files():
    """Identify files that should be preserved (new architecture)."""
    preserve_files = [
        # New architecture test structure
        "unit/",
        "integration/", 
        "e2e/",
        "chaos/",
        "performance/",
        "security/",
        "uat/",
        "utils/",
        "fixtures/",
        "scripts/",
        
        # New architecture test files
        "conftest.py",
        "pytest.ini",
        "requirements.txt",
        
        # New architecture documentation
        "README_NEW_ARCHITECTURE.md",
        "TEST_ENVIRONMENT_STRATEGY.md",
        "IMPLEMENTATION_PLAN.md",
        "COMPREHENSIVE_TEST_STRATEGY.md",
        
        # New architecture scripts
        "scripts/rebuild_test_environment.py",
        "scripts/run_comprehensive_tests.py",
    ]
    
    return preserve_files

def surgical_cleanup():
    """Perform surgical cleanup of legacy files."""
    print("🧹 SYMPHAINY PLATFORM - SURGICAL LEGACY TEST CLEANUP")
    print("=" * 60)
    
    # Create backup
    backup_dir = backup_legacy_files()
    
    # Identify files to clean up
    legacy_files = identify_legacy_files()
    preserve_files = identify_preserve_files()
    
    print(f"\n📋 LEGACY FILES TO REMOVE: {len(legacy_files)}")
    for file in legacy_files:
        if os.path.exists(file):
            print(f"  🗑️  {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    print(f"\n✅ FILES TO PRESERVE: {len(preserve_files)}")
    for file in preserve_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    # Confirm before proceeding
    print(f"\n⚠️  SURGICAL CLEANUP READY")
    print("This will:")
    print("  • Backup legacy files to archive/legacy_tests_backup/")
    print("  • Remove legacy test files")
    print("  • Preserve new architecture test environment")
    print("  • Keep all working test files intact")
    
    response = input("\nProceed with surgical cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cleanup cancelled.")
        return False
    
    # Perform surgical cleanup
    removed_count = 0
    backup_count = 0
    
    for file in legacy_files:
        if os.path.exists(file):
            try:
                # Backup first
                if os.path.isfile(file):
                    shutil.copy2(file, backup_dir / file)
                    backup_count += 1
                elif os.path.isdir(file):
                    shutil.copytree(file, backup_dir / file, dirs_exist_ok=True)
                    backup_count += 1
                
                # Remove file/directory
                if os.path.isfile(file):
                    os.remove(file)
                    removed_count += 1
                    print(f"  ✅ Removed file: {file}")
                elif os.path.isdir(file):
                    shutil.rmtree(file)
                    removed_count += 1
                    print(f"  ✅ Removed directory: {file}")
                    
            except Exception as e:
                print(f"  ❌ Error removing {file}: {e}")
    
    print(f"\n📊 CLEANUP SUMMARY:")
    print(f"  📦 Files backed up: {backup_count}")
    print(f"  🗑️  Files removed: {removed_count}")
    print(f"  ✅ New architecture preserved")
    
    return True

def verify_cleanup():
    """Verify that the cleanup was successful and new architecture is intact."""
    print(f"\n🔍 VERIFYING CLEANUP:")
    
    # Check that new architecture files are still there
    new_architecture_files = [
        "unit/foundations/test_simple_foundation.py",
        "unit/foundations/test_public_works_foundation_comprehensive.py",
        "integration/cross_realm/test_solution_to_journey_comprehensive.py",
        "e2e/mvp_scenarios/test_complete_mvp_journey_comprehensive.py",
        "chaos/failure_injection/test_system_resilience.py",
        "uat/insurance_client/test_insurance_executive_uat.py",
        "conftest.py",
        "pytest.ini",
        "requirements.txt"
    ]
    
    all_present = True
    for file in new_architecture_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing!)")
            all_present = False
    
    if all_present:
        print(f"\n🎉 CLEANUP SUCCESSFUL!")
        print(f"✅ New architecture test environment intact")
        print(f"✅ Legacy files removed")
        print(f"✅ Ready for production testing")
    else:
        print(f"\n⚠️  CLEANUP ISSUES DETECTED!")
        print(f"Some new architecture files are missing")
    
    return all_present

def main():
    """Main cleanup function."""
    try:
        # Perform surgical cleanup
        if surgical_cleanup():
            # Verify cleanup
            if verify_cleanup():
                print(f"\n🚀 SURGICAL CLEANUP COMPLETE!")
                print(f"✅ Test environment is clean and ready!")
                return 0
            else:
                print(f"\n❌ Cleanup verification failed!")
                return 1
        else:
            print(f"\n❌ Cleanup was cancelled!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())








