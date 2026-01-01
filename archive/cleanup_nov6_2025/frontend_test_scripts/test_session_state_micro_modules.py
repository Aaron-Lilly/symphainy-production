#!/usr/bin/env python3
"""
Validation Test for Session & State Micro-Modules
Tests the micro-modular refactoring of session and state management
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_size(file_path: str, max_lines: int = 100) -> bool:
    """Check if file is under the specified line count"""
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            return len(lines) <= max_lines
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return False

def check_directory_structure(base_path: str) -> bool:
    """Check if directory follows micro-modular structure"""
    required_files = ['core.ts', 'index.ts']
    optional_files = ['smart_city_integration.ts', 'types.ts', 'hooks.ts', 'derived_atoms.ts']
    
    base_dir = Path(base_path)
    if not base_dir.exists():
        print(f"❌ Directory {base_path} does not exist")
        return False
    
    # Check required files
    for file in required_files:
        file_path = base_dir / file
        if not file_path.exists():
            print(f"❌ Required file {file} missing in {base_path}")
            return False
    
    # Check optional files (at least one should exist)
    optional_exists = any((base_dir / file).exists() for file in optional_files)
    if not optional_exists:
        print(f"⚠️  No optional files found in {base_path}")
    
    return True

def validate_session_micro_modules():
    """Validate session management micro-modules"""
    print("🔍 Validating Session Management Micro-Modules...")
    
    session_dir = "shared/session"
    
    # Check directory structure
    if not check_directory_structure(session_dir):
        return False
    
    # Check file sizes
    files_to_check = [
        f"{session_dir}/core.ts",
        f"{session_dir}/smart_city_integration.ts", 
        f"{session_dir}/types.ts",
        f"{session_dir}/hooks.ts",
        f"{session_dir}/GlobalSessionProvider.tsx",
        f"{session_dir}/index.ts"
    ]
    
    all_files_valid = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_valid = check_file_size(file_path, 100)
            status = "✅" if is_valid else "❌"
            print(f"{status} {file_path}: {'Under 100 lines' if is_valid else 'Over 100 lines'}")
            if not is_valid:
                all_files_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_files_valid

def validate_state_micro_modules():
    """Validate state management micro-modules"""
    print("\n🔍 Validating State Management Micro-Modules...")
    
    state_dir = "shared/state"
    
    # Check directory structure
    if not check_directory_structure(state_dir):
        return False
    
    # Check file sizes
    files_to_check = [
        f"{state_dir}/core.ts",
        f"{state_dir}/smart_city_integration.ts",
        f"{state_dir}/derived_atoms.ts",
        f"{state_dir}/index.ts"
    ]
    
    all_files_valid = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_valid = check_file_size(file_path, 100)
            status = "✅" if is_valid else "❌"
            print(f"{status} {file_path}: {'Under 100 lines' if is_valid else 'Over 100 lines'}")
            if not is_valid:
                all_files_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_files_valid

def check_smart_city_integration():
    """Check Smart City integration patterns"""
    print("\n🔍 Checking Smart City Integration Patterns...")
    
    integration_files = [
        "shared/session/smart_city_integration.ts",
        "shared/state/smart_city_integration.ts"
    ]
    
    smart_city_components = ['TrafficCop', 'Archive', 'Conductor']
    
    all_integrations_valid = True
    for file_path in integration_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    missing_components = []
                    for component in smart_city_components:
                        if component not in content:
                            missing_components.append(component)
                    
                    if missing_components:
                        print(f"❌ {file_path}: Missing Smart City components: {missing_components}")
                        all_integrations_valid = False
                    else:
                        print(f"✅ {file_path}: All Smart City components present")
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_integrations_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_integrations_valid

def main():
    """Main validation function"""
    print("🚀 Phase 1: Session & State Management - Micro-Modular Refactoring Validation")
    print("=" * 80)
    
    # Validate session micro-modules
    session_valid = validate_session_micro_modules()
    
    # Validate state micro-modules  
    state_valid = validate_state_micro_modules()
    
    # Check Smart City integration
    smart_city_valid = check_smart_city_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"Session Management Micro-Modules: {'✅ PASS' if session_valid else '❌ FAIL'}")
    print(f"State Management Micro-Modules: {'✅ PASS' if state_valid else '❌ FAIL'}")
    print(f"Smart City Integration: {'✅ PASS' if smart_city_valid else '❌ FAIL'}")
    
    overall_success = session_valid and state_valid and smart_city_valid
    
    if overall_success:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Micro-modular refactoring completed successfully")
        print("✅ Smart City integration patterns implemented")
        print("✅ File size targets achieved")
        print("\n🚀 Ready to proceed to next phase!")
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        print("Please review and fix the issues above before proceeding")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 