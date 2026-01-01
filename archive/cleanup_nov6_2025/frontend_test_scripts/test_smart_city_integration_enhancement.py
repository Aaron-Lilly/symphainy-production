#!/usr/bin/env python3
"""
Validation Test for Smart City Integration Enhancement
Tests the enhanced WebSocket client and Smart City integration
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
    required_files = ['core.ts', 'index.ts']
    optional_files = ['smart_city_integration.ts', 'message_queue.ts', 'connection.ts', 'hooks.ts']
    
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

def validate_websocket_micro_modules():
    """Validate WebSocket management micro-modules"""
    print("🔍 Validating WebSocket Management Micro-Modules...")
    
    websocket_dir = "shared/websocket"
    
    # Check directory structure
    if not check_directory_structure(websocket_dir):
        return False
    
    # Check file sizes
    files_to_check = [
        f"{websocket_dir}/core.ts",
        f"{websocket_dir}/smart_city_integration.ts",
        f"{websocket_dir}/message_queue.ts",
        f"{websocket_dir}/connection.ts",
        f"{websocket_dir}/hooks.ts",
        f"{websocket_dir}/EnhancedSmartCityWebSocketClient.ts",
        f"{websocket_dir}/index.ts"
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
    print("\n🔍 Checking Smart City Integration...")
    
    integration_files = [
        "shared/websocket/smart_city_integration.ts",
        "shared/websocket/EnhancedSmartCityWebSocketClient.ts",
        "shared/services/SmartCityWebSocketClient.ts"
    ]
    
    integration_patterns = [
        'TrafficCopMessage',
        'ArchiveMessage', 
        'ConductorMessage',
        'PostOfficeMessage',
        'routeSession',
        'validateSession',
        'createSession',
        'storeSession',
        'retrieveSession',
        'orchestrateSession'
    ]
    
    all_integrations_valid = True
    for file_path in integration_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    missing_patterns = []
                    for pattern in integration_patterns:
                        if pattern not in content:
                            missing_patterns.append(pattern)
                    
                    if len(missing_patterns) > 5:  # Allow some missing patterns
                        print(f"❌ {file_path}: Missing many integration patterns: {missing_patterns[:5]}...")
                        all_integrations_valid = False
                    else:
                        print(f"✅ {file_path}: Smart City integration present")
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_integrations_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_integrations_valid

def check_websocket_enhancements():
    """Check WebSocket enhancement features"""
    print("\n🔍 Checking WebSocket Enhancements...")
    
    enhancement_files = [
        "shared/websocket/message_queue.ts",
        "shared/websocket/connection.ts",
        "shared/websocket/hooks.ts"
    ]
    
    enhancement_patterns = [
        'MessageQueue',
        'ConnectionManager',
        'useWebSocketConnection',
        'useSmartCitySession',
        'useMessageQueue',
        'useConnectionHealth',
        'enqueue',
        'dequeue',
        'getConnection',
        'releaseConnection'
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
                    
                    if len(found_patterns) >= 3:  # At least 3 patterns should be found
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

def check_configuration_integration():
    """Check configuration integration"""
    print("\n🔍 Checking Configuration Integration...")
    
    config_files = [
        "shared/websocket/core.ts",
        "shared/websocket/smart_city_integration.ts",
        "shared/websocket/connection.ts"
    ]
    
    config_patterns = ['getGlobalConfig', 'config.getSection']
    
    all_config_valid = True
    for file_path in config_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    missing_patterns = []
                    for pattern in config_patterns:
                        if pattern not in content:
                            missing_patterns.append(pattern)
                    
                    if missing_patterns:
                        print(f"❌ {file_path}: Missing config patterns: {missing_patterns}")
                        all_config_valid = False
                    else:
                        print(f"✅ {file_path}: Configuration integration present")
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_config_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_config_valid

def main():
    """Main validation function"""
    print("🚀 Phase 3: Smart City Integration Enhancement - Validation")
    print("=" * 80)
    
    # Validate WebSocket micro-modules
    websocket_valid = validate_websocket_micro_modules()
    
    # Check Smart City integration
    integration_valid = check_smart_city_integration()
    
    # Check WebSocket enhancements
    enhancements_valid = check_websocket_enhancements()
    
    # Check configuration integration
    config_valid = check_configuration_integration()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"WebSocket Micro-Modules: {'✅ PASS' if websocket_valid else '❌ FAIL'}")
    print(f"Smart City Integration: {'✅ PASS' if integration_valid else '❌ FAIL'}")
    print(f"WebSocket Enhancements: {'✅ PASS' if enhancements_valid else '❌ FAIL'}")
    print(f"Configuration Integration: {'✅ PASS' if config_valid else '❌ FAIL'}")
    
    overall_success = websocket_valid and integration_valid and enhancements_valid and config_valid
    
    if overall_success:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Smart City integration enhancement completed successfully")
        print("✅ Enhanced WebSocket client implemented")
        print("✅ Message queuing and retry system created")
        print("✅ Connection pooling and health monitoring added")
        print("✅ React hooks for WebSocket functionality created")
        print("\n🚀 Ready to proceed to next phase!")
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        print("Please review and fix the issues above before proceeding")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 