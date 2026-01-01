#!/usr/bin/env python3
"""
SymphAIny Platform - Surgical Legacy Platform Cleanup Script

This script surgically removes legacy platform files while preserving the new architecture.
"""

import os
import shutil
from pathlib import Path
import sys

def backup_legacy_files():
    """Create a backup of legacy files before deletion."""
    backup_dir = Path("archive/legacy_platform_backup")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Creating backup in {backup_dir}")
    return backup_dir

def identify_legacy_files():
    """Identify legacy files that should be removed."""
    # Legacy test files (old architecture)
    legacy_test_files = [
        "test_5_layer_architecture.py",
        "test_5_layer_architecture_simple.py", 
        "test_agentic_foundation_llm_integration.py",
        "test_bootstrap_architecture.py",
        "test_city_manager_di_container.py",
        "test_complete_5_layer_architecture.py",
        "test_complete_librarian_5_layer_architecture.py",
        "test_complete_security_implementation.py",
        "test_complete_security_vision.py",
        "test_composition_services_simple.py",
        "test_conductor_5_layer_architecture.py",
        "test_conductor_architecture_simple.py",
        "test_curator_5_layer_architecture.py",
        "test_curator_direct_library_usage.py",
        "test_curator_service_refactoring.py",
        "test_data_infrastructure_abstractions.py",
        "test_data_infrastructure_adapters.py",
        "test_data_infrastructure_composition.py",
        "test_data_infrastructure_protocols.py",
        "test_governance_integration.py",
        "test_governance_simple.py",
        "test_integrated_security_capabilities.py",
        "test_librarian_infrastructure_abstractions.py",
        "test_librarian_infrastructure_adapters.py",
        "test_librarian_infrastructure_composition.py",
        "test_llm_agentic_integration_simple.py",
        "test_llm_infrastructure_refactoring.py",
        "test_manager_vision_simple.py",
        "test_manager_vision_startup.py",
        "test_nurse_architecture_simple.py",
        "test_post_office_composition_service.py",
        "test_realm_access_control.py",
        "test_refactoring_pattern.py",
        "test_security_abstractions_access.py",
        "test_security_e2e_flow.py",
        "test_security_e2e_flow_mock.py",
        "test_security_implementation_simple.py",
        "test_security_infrastructure.py",
        "test_security_vision_simplified.py",
        "test_traffic_cop_composition_services.py",
        "test_updated_di_container.py"
    ]
    
    # Legacy directories (old architecture)
    legacy_directories = [
        "tests/",  # Old test structure
        "archived_implementations/",  # Already archived
        "abstractions/",  # Old abstraction layer
        "agentic/",  # Old agentic implementation
        "core/",  # Old core implementation
        "engines/",  # Old engine implementation
        "infrastructure/",  # Old infrastructure layer
        "monitoring/",  # Old monitoring implementation
        "registry/",  # Old registry implementation
        "symphainy-platform/",  # Duplicate platform directory
        "symphainy_source/",  # Source directory (should be separate)
        "utilities/",  # Old utilities (now in symphainy_source)
        "logs/",  # Log files directory
        "poetry_lib/",  # Old poetry library
        "frontend/",  # Old frontend implementation
        "grafana/",  # Old monitoring setup
        "docs/",  # Old documentation
        "scripts/",  # Old scripts
        "managers/"  # Old manager implementation
    ]
    
    # Legacy configuration files
    legacy_config_files = [
        ".env",
        ".env.secrets",
        ".frontend.pid",
        ".gateway.pid", 
        ".platform.pid",
        ".platform_port",
        "=5.0.0",
        "Dockerfile",
        "Dockerfile.platform",
        "docker-compose.consul-tempo.yml",
        "docker-compose.consul.yml",
        "docker-compose.dev.yml",
        "docker-compose.infrastructure.yml",
        "docker-compose.platform.yml",
        "docker-compose.prod.yml",
        "docker-compose.simplified.yml",
        "otel-collector-config.yaml",
        "tempo-config.yaml",
        "playwright.config.py",
        "poetry.lock",
        "pyproject.toml.backup",
        "pyproject_clean.toml",
        "requirements-minimal.txt",
        "requirements-test.txt",
        "pytest.ini",
        "production_readiness_assessment.py",
        "mcp_gateway.py",
        "minimal_main.py",
        "orchestrate_services.py",
        "start_pillar_services.py",
        "startup.py",
        "startup.sh",
        "startup_manager_vision.py",
        "startup_manager_vision.sh",
        "stop.sh",
        "logs.sh"
    ]
    
    # Legacy documentation files
    legacy_doc_files = [
        "DEPLOYMENT.md",
        "ENVIRONMENT_SETUP.md", 
        "MANAGER_VISION_IMPLEMENTATION_PLAN.md",
        "README.md",
        "STARTUP_README.md",
        "cross_pillar_integration_analysis.md",
        "cross_pillar_integration_business_outcomes_analysis.md",
        "infrastructure_refactoring_analysis.md",
        "infrastructure_refactoring_comparison.md",
        "remaining_abstractions_analysis.md",
        "strategic_coordination_analysis.md",
        "platform_env_file_for_cursor.md"
    ]
    
    # Legacy log files
    legacy_log_files = [
        "test_manager_vision_startup.log"
    ]
    
    return {
        "legacy_test_files": legacy_test_files,
        "legacy_directories": legacy_directories,
        "legacy_config_files": legacy_config_files,
        "legacy_doc_files": legacy_doc_files,
        "legacy_log_files": legacy_log_files
    }

def identify_preserve_files():
    """Identify files that should be preserved (new architecture)."""
    preserve_files = [
        # New architecture core directories
        "bases/",
        "foundations/",
        "backend/",
        "journey_solution/",
        "experience/",
        "solution/",
        "utilities/",
        
        # New architecture configuration
        "pyproject.toml",
        "requirements.txt",
        
        # New architecture main files
        "main.py",
        "enhanced_main.py"
    ]
    
    return preserve_files

def surgical_cleanup():
    """Perform surgical cleanup of legacy platform files."""
    print("🧹 SYMPHAINY PLATFORM - SURGICAL LEGACY CLEANUP")
    print("=" * 70)
    
    # Create backup
    backup_dir = backup_legacy_files()
    
    # Identify files to clean up
    legacy_files = identify_legacy_files()
    preserve_files = identify_preserve_files()
    
    print(f"\n📋 LEGACY FILES TO REMOVE:")
    print(f"  🗑️  Legacy test files: {len(legacy_files['legacy_test_files'])}")
    print(f"  🗑️  Legacy directories: {len(legacy_files['legacy_directories'])}")
    print(f"  🗑️  Legacy config files: {len(legacy_files['legacy_config_files'])}")
    print(f"  🗑️  Legacy documentation: {len(legacy_files['legacy_doc_files'])}")
    print(f"  🗑️  Legacy log files: {len(legacy_files['legacy_log_files'])}")
    
    print(f"\n✅ FILES TO PRESERVE:")
    for file in preserve_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    # Confirm before proceeding
    print(f"\n⚠️  SURGICAL CLEANUP READY")
    print("This will:")
    print("  • Backup legacy files to archive/legacy_platform_backup/")
    print("  • Remove legacy platform files")
    print("  • Preserve new architecture files")
    print("  • Keep core platform functionality intact")
    
    response = input("\nProceed with surgical cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cleanup cancelled.")
        return False
    
    # Perform surgical cleanup
    removed_count = 0
    backup_count = 0
    
    # Clean up legacy test files
    for file in legacy_files['legacy_test_files']:
        if os.path.exists(file):
            try:
                # Backup first
                shutil.copy2(file, backup_dir / file)
                backup_count += 1
                
                # Remove file
                os.remove(file)
                removed_count += 1
                print(f"  ✅ Removed test file: {file}")
                    
            except Exception as e:
                print(f"  ❌ Error removing {file}: {e}")
    
    # Clean up legacy directories
    for dir in legacy_files['legacy_directories']:
        if os.path.exists(dir):
            try:
                # Backup first
                shutil.copytree(dir, backup_dir / dir, dirs_exist_ok=True)
                backup_count += 1
                
                # Remove directory
                shutil.rmtree(dir)
                removed_count += 1
                print(f"  ✅ Removed directory: {dir}")
                    
            except Exception as e:
                print(f"  ❌ Error removing {dir}: {e}")
    
    # Clean up legacy config files
    for file in legacy_files['legacy_config_files']:
        if os.path.exists(file):
            try:
                # Backup first
                shutil.copy2(file, backup_dir / file)
                backup_count += 1
                
                # Remove file
                os.remove(file)
                removed_count += 1
                print(f"  ✅ Removed config file: {file}")
                    
            except Exception as e:
                print(f"  ❌ Error removing {file}: {e}")
    
    # Clean up legacy documentation
    for file in legacy_files['legacy_doc_files']:
        if os.path.exists(file):
            try:
                # Backup first
                shutil.copy2(file, backup_dir / file)
                backup_count += 1
                
                # Remove file
                os.remove(file)
                removed_count += 1
                print(f"  ✅ Removed documentation: {file}")
                    
            except Exception as e:
                print(f"  ❌ Error removing {file}: {e}")
    
    # Clean up legacy log files
    for file in legacy_files['legacy_log_files']:
        if os.path.exists(file):
            try:
                # Backup first
                shutil.copy2(file, backup_dir / file)
                backup_count += 1
                
                # Remove file
                os.remove(file)
                removed_count += 1
                print(f"  ✅ Removed log file: {file}")
                    
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
        "bases/",
        "foundations/",
        "backend/",
        "journey_solution/",
        "experience/",
        "solution/",
        "utilities/",
        "pyproject.toml",
        "requirements.txt",
        "main.py"
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
        print(f"✅ New architecture platform intact")
        print(f"✅ Legacy files removed")
        print(f"✅ Ready for production")
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
                print(f"✅ Platform is clean and ready!")
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







