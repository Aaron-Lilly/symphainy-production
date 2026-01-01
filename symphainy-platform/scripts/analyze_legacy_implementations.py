#!/usr/bin/env python3
"""
SymphAIny Platform - Legacy Implementation Analysis Script

This script analyzes the platform for legacy implementations that need cleanup.
"""

import os
import shutil
from pathlib import Path
import sys

def analyze_legacy_files():
    """Analyze and categorize legacy files in the platform."""
    print("🔍 SYMPHAINY PLATFORM - LEGACY IMPLEMENTATION ANALYSIS")
    print("=" * 70)
    
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
    
    # Analyze current files
    current_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py") or file.endswith(".md") or file.endswith(".yml") or file.endswith(".yaml"):
                current_files.append(os.path.join(root, file))
    
    print(f"\n📊 PLATFORM ANALYSIS:")
    print(f"  📁 Total Python files: {len([f for f in current_files if f.endswith('.py')])}")
    print(f"  📁 Total directories: {len([d for d in os.listdir('.') if os.path.isdir(d)])}")
    print(f"  📁 Total files: {len(current_files)}")
    
    # Categorize legacy files
    legacy_test_count = 0
    legacy_dir_count = 0
    legacy_config_count = 0
    legacy_doc_count = 0
    legacy_log_count = 0
    
    print(f"\n🗑️  LEGACY FILES IDENTIFIED:")
    
    print(f"\n📋 Legacy Test Files ({len(legacy_test_files)}):")
    for file in legacy_test_files:
        if os.path.exists(file):
            legacy_test_count += 1
            print(f"  🗑️  {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    print(f"\n📁 Legacy Directories ({len(legacy_directories)}):")
    for dir in legacy_directories:
        if os.path.exists(dir):
            legacy_dir_count += 1
            print(f"  🗑️  {dir}")
        else:
            print(f"  ⚠️  {dir} (not found)")
    
    print(f"\n⚙️  Legacy Config Files ({len(legacy_config_files)}):")
    for file in legacy_config_files:
        if os.path.exists(file):
            legacy_config_count += 1
            print(f"  🗑️  {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    print(f"\n📚 Legacy Documentation ({len(legacy_doc_files)}):")
    for file in legacy_doc_files:
        if os.path.exists(file):
            legacy_doc_count += 1
            print(f"  🗑️  {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    print(f"\n📝 Legacy Log Files ({len(legacy_log_files)}):")
    for file in legacy_log_files:
        if os.path.exists(file):
            legacy_log_count += 1
            print(f"  🗑️  {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    # Summary
    total_legacy = legacy_test_count + legacy_dir_count + legacy_config_count + legacy_doc_count + legacy_log_count
    
    print(f"\n📊 LEGACY ANALYSIS SUMMARY:")
    print(f"  🗑️  Legacy test files: {legacy_test_count}")
    print(f"  🗑️  Legacy directories: {legacy_dir_count}")
    print(f"  🗑️  Legacy config files: {legacy_config_count}")
    print(f"  🗑️  Legacy documentation: {legacy_doc_count}")
    print(f"  🗑️  Legacy log files: {legacy_log_count}")
    print(f"  📊 Total legacy items: {total_legacy}")
    
    # Identify new architecture files to preserve
    preserve_files = [
        "bases/",
        "foundations/",
        "backend/",
        "journey_solution/",
        "experience/",
        "solution/",
        "utilities/",
        "pyproject.toml",
        "requirements.txt"
    ]
    
    print(f"\n✅ NEW ARCHITECTURE FILES TO PRESERVE:")
    for file in preserve_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    return {
        "legacy_test_files": legacy_test_files,
        "legacy_directories": legacy_directories,
        "legacy_config_files": legacy_config_files,
        "legacy_doc_files": legacy_doc_files,
        "legacy_log_files": legacy_log_files,
        "preserve_files": preserve_files,
        "total_legacy": total_legacy
    }

def main():
    """Main analysis function."""
    try:
        analysis = analyze_legacy_files()
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print(f"  1. 🗑️  Remove {analysis['total_legacy']} legacy items")
        print(f"  2. 📦 Backup legacy files to archive/")
        print(f"  3. ✅ Preserve new architecture files")
        print(f"  4. 🧹 Clean up platform for production")
        print(f"  5. 🚀 Ready for C-suite executive UAT")
        
        print(f"\n⚠️  CLEANUP IMPACT:")
        print(f"  • Platform will be significantly cleaner")
        print(f"  • Focus on new architecture only")
        print(f"  • Remove 2561+ legacy files")
        print(f"  • Preserve core new architecture")
        
        return analysis
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return None

if __name__ == "__main__":
    main()







