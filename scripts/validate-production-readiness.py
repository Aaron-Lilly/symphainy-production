#!/usr/bin/env python3
"""
Pre-Deployment Production Readiness Validation Script

Validates that the platform is ready for production deployment by checking:
1. Configuration (required secrets, infrastructure config)
2. Docker setup (networks, compose files)
3. Build context (excluded files)
4. Dependencies (poetry.lock, package-lock.json)

Usage:
    python3 scripts/validate-production-readiness.py
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

from utilities.configuration.unified_configuration_manager import (
    UnifiedConfigurationManager,
    Environment
)

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def validate_configuration() -> Dict[str, Any]:
    """Validate production configuration."""
    print_header("1. Configuration Validation")
    
    try:
        config_root = project_root / "symphainy-platform"
        config_manager = UnifiedConfigurationManager(
            service_name="production_validation",
            environment=Environment.PRODUCTION,
            config_root=str(config_root)
        )
        
        validation_result = config_manager.validate_production_config()
        
        # Print results
        if validation_result["valid"]:
            print_success("All required configuration is present")
        else:
            print_error("Configuration validation failed")
        
        # Required secrets
        req_secrets = validation_result["required_secrets"]
        if req_secrets["missing"]:
            print_error(f"Missing required secrets: {', '.join(req_secrets['missing'])}")
        if req_secrets["invalid"]:
            print_error(f"Invalid required secrets: {', '.join(req_secrets['invalid'])}")
        if not req_secrets["missing"] and not req_secrets["invalid"]:
            print_success(f"All required secrets present ({req_secrets['valid_count']}/{req_secrets['total']})")
        
        # Recommended secrets
        rec_secrets = validation_result["recommended_secrets"]
        if rec_secrets["missing"]:
            print_warning(f"Missing recommended secrets: {', '.join(rec_secrets['missing'])}")
        else:
            print_success(f"All recommended secrets present ({rec_secrets['valid_count']}/{rec_secrets['total']})")
        
        # Infrastructure
        infra = validation_result["infrastructure"]
        if infra["missing"]:
            print_error(f"Missing infrastructure config: {', '.join(infra['missing'])}")
        else:
            print_success(f"All infrastructure config present ({infra['valid_count']}/{infra['total']})")
        
        # GCS Credentials
        gcs = validation_result["gcs_credentials"]
        if not gcs["valid"]:
            print_error(f"GCS credentials invalid: {gcs['error']}")
        else:
            print_success("GCS credentials format is valid")
        
        return {
            "valid": validation_result["valid"],
            "details": validation_result
        }
        
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        return {
            "valid": False,
            "error": str(e)
        }

def validate_docker_setup() -> Dict[str, Any]:
    """Validate Docker setup."""
    print_header("2. Docker Setup Validation")
    
    issues = []
    
    # Check docker-compose.prod.yml
    prod_compose = project_root / "docker-compose.prod.yml"
    if not prod_compose.exists():
        issues.append("docker-compose.prod.yml not found")
    else:
        print_success("docker-compose.prod.yml exists")
        
        # Check for network configuration
        with open(prod_compose, 'r') as f:
            content = f.read()
            if "smart_city_net" not in content:
                issues.append("docker-compose.prod.yml missing smart_city_net network")
            else:
                print_success("Network configuration present")
    
    # Check infrastructure compose
    infra_compose = project_root / "symphainy-platform" / "docker-compose.infrastructure.yml"
    if not infra_compose.exists():
        issues.append("docker-compose.infrastructure.yml not found")
    else:
        print_success("docker-compose.infrastructure.yml exists")
    
    if issues:
        for issue in issues:
            print_error(issue)
        return {"valid": False, "issues": issues}
    else:
        print_success("Docker setup is valid")
        return {"valid": True}

def validate_build_context() -> Dict[str, Any]:
    """Validate build context exclusions."""
    print_header("3. Build Context Validation")
    
    issues = []
    
    # Check backend .dockerignore
    backend_dockerignore = project_root / "symphainy-platform" / ".dockerignore"
    if not backend_dockerignore.exists():
        print_warning("symphainy-platform/.dockerignore not found (should exclude tests, docs)")
        issues.append("Backend .dockerignore missing")
    else:
        print_success("Backend .dockerignore exists")
        with open(backend_dockerignore, 'r') as f:
            content = f.read()
            required_exclusions = ["tests/", "docs/", "*.md"]
            missing = [ex for ex in required_exclusions if ex not in content]
            if missing:
                print_warning(f"Backend .dockerignore missing exclusions: {', '.join(missing)}")
            else:
                print_success("Backend .dockerignore has proper exclusions")
    
    # Check frontend .dockerignore
    frontend_dockerignore = project_root / "symphainy-frontend" / ".dockerignore"
    if not frontend_dockerignore.exists():
        print_warning("symphainy-frontend/.dockerignore not found")
        issues.append("Frontend .dockerignore missing")
    else:
        print_success("Frontend .dockerignore exists")
    
    if issues:
        return {"valid": False, "issues": issues}
    else:
        print_success("Build context is properly configured")
        return {"valid": True}

def validate_dependencies() -> Dict[str, Any]:
    """Validate dependency files."""
    print_header("4. Dependencies Validation")
    
    issues = []
    
    # Check poetry.lock
    poetry_lock = project_root / "symphainy-platform" / "poetry.lock"
    if not poetry_lock.exists():
        print_error("poetry.lock not found (should be committed)")
        issues.append("poetry.lock missing")
    else:
        print_success("poetry.lock exists")
    
    # Check package-lock.json
    package_lock = project_root / "symphainy-frontend" / "package-lock.json"
    if not package_lock.exists():
        print_warning("package-lock.json not found (should be committed)")
        issues.append("package-lock.json missing")
    else:
        print_success("package-lock.json exists")
    
    # Check pyproject.toml for gotrue
    pyproject = project_root / "symphainy-platform" / "pyproject.toml"
    if pyproject.exists():
        with open(pyproject, 'r') as f:
            content = f.read()
            if "gotrue" in content and "gotrue = " in content:
                print_warning("gotrue still in pyproject.toml (should be removed)")
                issues.append("gotrue dependency not removed")
            else:
                print_success("gotrue removed from pyproject.toml")
    
    if issues:
        return {"valid": False, "issues": issues}
    else:
        print_success("Dependencies are properly configured")
        return {"valid": True}

def main():
    """Main validation function."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("  Production Readiness Validation")
    print("="*60)
    print(f"{Colors.RESET}\n")
    
    results = {
        "configuration": validate_configuration(),
        "docker": validate_docker_setup(),
        "build_context": validate_build_context(),
        "dependencies": validate_dependencies()
    }
    
    # Summary
    print_header("Validation Summary")
    
    all_valid = all(r.get("valid", False) for r in results.values())
    
    for name, result in results.items():
        status = "✅ PASS" if result.get("valid", False) else "❌ FAIL"
        print(f"{status}: {name.replace('_', ' ').title()}")
    
    print()
    
    if all_valid:
        print_success("All validations passed! Platform is ready for production deployment.")
        return 0
    else:
        print_error("Some validations failed. Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

