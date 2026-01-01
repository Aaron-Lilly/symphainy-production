#!/usr/bin/env python3
"""
Validation Test for Configuration Standardization
Tests the unified configuration system and integration
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
    optional_files = ['validation.ts', 'hooks.ts', 'global.ts']
    
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

def validate_config_micro_modules():
    """Validate configuration management micro-modules"""
    print("🔍 Validating Configuration Management Micro-Modules...")
    
    config_dir = "shared/config"
    
    # Check directory structure
    if not check_directory_structure(config_dir):
        return False
    
    # Check file sizes
    files_to_check = [
        f"{config_dir}/core.ts",
        f"{config_dir}/validation.ts",
        f"{config_dir}/hooks.ts",
        f"{config_dir}/global.ts",
        f"{config_dir}/index.ts"
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

def validate_environment_configs():
    """Validate environment-specific configurations"""
    print("\n🔍 Validating Environment Configurations...")
    
    env_dir = "shared/config/environments"
    
    if not Path(env_dir).exists():
        print(f"❌ Environment directory {env_dir} does not exist")
        return False
    
    # Check environment files
    env_files = [
        f"{env_dir}/development.ts",
        f"{env_dir}/production.ts",
        f"{env_dir}/test.ts",
        f"{env_dir}/staging.ts",
        f"{env_dir}/index.ts"
    ]
    
    all_files_valid = True
    for file_path in env_files:
        if os.path.exists(file_path):
            is_valid = check_file_size(file_path, 100)
            status = "✅" if is_valid else "❌"
            print(f"{status} {file_path}: {'Under 100 lines' if is_valid else 'Over 100 lines'}")
            if not is_valid:
                all_files_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_files_valid

def check_unified_config_integration():
    """Check unified configuration integration patterns"""
    print("\n🔍 Checking Unified Configuration Integration...")
    
    integration_files = [
        "shared/services/APIService.ts",
        "shared/services/SmartCityWebSocketClient.ts"
    ]
    
    config_patterns = ['getGlobalConfig', 'UnifiedConfig', 'config.getSection']
    
    all_integrations_valid = True
    for file_path in integration_files:
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
                        all_integrations_valid = False
                    else:
                        print(f"✅ {file_path}: Unified config integration present")
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_integrations_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_integrations_valid

def check_environment_variables():
    """Check environment variable usage"""
    print("\n🔍 Checking Environment Variable Usage...")
    
    config_files = [
        "shared/config/core.ts",
        "shared/config/environments/development.ts",
        "shared/config/environments/production.ts"
    ]
    
    env_vars = [
        'NEXT_PUBLIC_API_BASE_URL',
        'NEXT_PUBLIC_WEBSOCKET_URL',
        'NEXT_PUBLIC_SMART_CITY_ENABLED',
        'NODE_ENV'
    ]
    
    all_env_vars_valid = True
    for file_path in config_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    missing_vars = []
                    for var in env_vars:
                        if var not in content:
                            missing_vars.append(var)
                    
                    if missing_vars:
                        print(f"⚠️  {file_path}: Missing env vars: {missing_vars}")
                    else:
                        print(f"✅ {file_path}: Environment variables properly used")
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                all_env_vars_valid = False
        else:
            print(f"⚠️  {file_path}: File not found")
    
    return all_env_vars_valid

def main():
    """Main validation function"""
    print("🚀 Phase 2: Configuration Standardization - Validation")
    print("=" * 80)
    
    # Validate config micro-modules
    config_valid = validate_config_micro_modules()
    
    # Validate environment configs
    env_valid = validate_environment_configs()
    
    # Check unified config integration
    integration_valid = check_unified_config_integration()
    
    # Check environment variables
    env_vars_valid = check_environment_variables()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"Configuration Micro-Modules: {'✅ PASS' if config_valid else '❌ FAIL'}")
    print(f"Environment Configurations: {'✅ PASS' if env_valid else '❌ FAIL'}")
    print(f"Unified Config Integration: {'✅ PASS' if integration_valid else '❌ FAIL'}")
    print(f"Environment Variables: {'✅ PASS' if env_vars_valid else '❌ FAIL'}")
    
    overall_success = config_valid and env_valid and integration_valid and env_vars_valid
    
    if overall_success:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Configuration standardization completed successfully")
        print("✅ Unified configuration system implemented")
        print("✅ Environment-specific configs created")
        print("✅ Services integrated with unified config")
        print("\n🚀 Ready to proceed to next phase!")
    else:
        print("\n❌ SOME VALIDATIONS FAILED")
        print("Please review and fix the issues above before proceeding")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 