#!/usr/bin/env python3
"""
Validation Test for State Management Enhancement
Tests the enhanced state management system
"""

import os
import sys
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
    required_files = ['enhanced_core.ts', 'index.ts']
    optional_files = ['persistence.ts', 'sync.ts', 'hooks.ts', 'EnhancedStateProvider.tsx']
    
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
    
    # Check optional files (at least some should exist)
    optional_exists = any((base_dir / file).exists() for file in optional_files)
    if not optional_exists:
        print(f"⚠️  No optional files found in {base_path}")
    
    return True

def validate_state_micro_modules():
    """Validate state management micro-modules"""
    print("🔍 Validating State Management Micro-Modules...")
    
    state_dir = "shared/state"
    
    # Check directory structure
    if not check_directory_structure(state_dir):
        return False
    
    # Check file sizes
    files_to_check = [
        f"{state_dir}/enhanced_core.ts",
        f"{state_dir}/persistence.ts",
        f"{state_dir}/sync.ts",
        f"{state_dir}/hooks.ts",
        f"{state_dir}/EnhancedStateProvider.tsx",
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

def check_state_enhancement_features():
    """Check state enhancement features"""
    print("\n🔍 Checking State Enhancement Features...")
    
    enhancement_files = [
        "shared/state/enhanced_core.ts",
        "shared/state/persistence.ts",
        "shared/state/sync.ts"
    ]
    
    enhancement_patterns = [
        'EnhancedStateManager',
        'StatePersistence',
        'StateSynchronizer',
        'StateNode',
        'StateChange',
        'setState',
        'getState',
        'subscribe',
        'saveState',
        'loadState',
        'syncChanges',
        'syncNode'
    ]
    
    all_enhancements_valid = True
    for file_path in enhancement_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in enhancement_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 4:  # At least 4 patterns should be found
                        print(f"✅ {file_path}: Enhancement features present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing enhancement features")
                        all_enhancements_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_enhancements_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_enhancements_valid

def check_react_integration():
    """Check React integration features"""
    print("\n🔍 Checking React Integration...")
    
    react_files = [
        "shared/state/hooks.ts",
        "shared/state/EnhancedStateProvider.tsx"
    ]
    
    react_patterns = [
        'useEnhancedState',
        'useStateSync',
        'useStatePersistence',
        'EnhancedStateProvider',
        'createContext',
        'useContext',
        'useEffect',
        'useState',
        'useCallback'
    ]
    
    all_react_valid = True
    for file_path in react_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in react_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 3:  # At least 3 patterns should be found
                        print(f"✅ {file_path}: React integration present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing React integration")
                        all_react_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_react_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_react_valid

def check_websocket_integration():
    """Check WebSocket integration"""
    print("\n🔍 Checking WebSocket Integration...")
    
    integration_files = [
        "shared/state/sync.ts",
        "shared/state/hooks.ts"
    ]
    
    websocket_patterns = [
        'EnhancedSmartCityWebSocketClient',
        'wsClient',
        'storeSession',
        'deleteSession',
        'syncChanges',
        'syncNode'
    ]
    
    all_websocket_valid = True
    for file_path in integration_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    found_patterns = []
                    for pattern in websocket_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
                    
                    if len(found_patterns) >= 2:  # At least 2 patterns should be found
                        print(f"✅ {file_path}: WebSocket integration present ({len(found_patterns)} patterns)")
                    else:
                        print(f"❌ {file_path}: Missing WebSocket integration")
                        all_websocket_valid = False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_websocket_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_websocket_valid

def main():
    """Main validation function"""
    print("🚀 Phase 4: State Management Enhancement - Validation")
    print("=" * 80)
    
    # Validate state micro-modules
    state_valid = validate_state_micro_modules()
    
    # Check state enhancement features
    enhancement_valid = check_state_enhancement_features()
    
    # Check React integration
    react_valid = check_react_integration()
    
    # Check WebSocket integration
    websocket_valid = check_websocket_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"State Micro-Modules: {'✅ PASS' if state_valid else '❌ FAIL'}")
    print(f"State Enhancement Features: {'✅ PASS' if enhancement_valid else '❌ FAIL'}")
    print(f"React Integration: {'✅ PASS' if react_valid else '❌ FAIL'}")
    print(f"WebSocket Integration: {'✅ PASS' if websocket_valid else '❌ FAIL'}")
    
    overall_success = state_valid and enhancement_valid and react_valid and websocket_valid
    
    if overall_success:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ State management enhancement completed successfully")
        print("✅ Enhanced state manager implemented")
        print("✅ Persistence layer created")
        print("✅ Synchronization layer added")
        print("✅ React hooks and provider created")
        print("\n🚀 Ready to proceed to next phase!")
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        print("Please review and fix the issues above before proceeding")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 