#!/usr/bin/env python3
"""
Phase 2 Client Config Foundation Test Script

Tests Client Config Foundation SDK builders and functionality.

WHAT: Validates Phase 2 Client Config Foundation implementation
HOW: Tests ConfigLoader, ConfigStorage, ConfigValidator, ConfigVersioner
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Client Config Foundation
try:
    from symphainy_platform.foundations.client_config_foundation.client_config_foundation_service import ClientConfigFoundationService
    from symphainy_platform.foundations.di_container.di_container_service import DIContainerService
    from symphainy_platform.foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
except ImportError:
    # Try alternative import paths
    try:
        sys.path.insert(0, str(project_root / "symphainy-platform"))
        from foundations.client_config_foundation.client_config_foundation_service import ClientConfigFoundationService
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the project root")
        sys.exit(1)


class Phase2ClientConfigTester:
    """Test Phase 2 Client Config Foundation."""
    
    def __init__(self):
        self.test_results = []
        self.di_container = None
        self.client_config_foundation = None
        self.public_works_foundation = None
        self.test_tenant_id = "test_tenant_001"
    
    async def setup_test_environment(self) -> bool:
        """Set up test environment."""
        try:
            print("\n🔧 Setting up test environment...")
            
            # Create DI Container
            self.di_container = DIContainerService("test_realm")
            
            # Initialize Public Works Foundation (required for storage)
            try:
                self.public_works_foundation = PublicWorksFoundationService(self.di_container)
                await self.public_works_foundation.initialize()
                print("   ✅ Public Works Foundation initialized")
            except Exception as e:
                print(f"   ⚠️  Public Works Foundation initialization failed: {e}")
                print("   Continuing with limited functionality...")
            
            # Initialize Client Config Foundation
            self.client_config_foundation = ClientConfigFoundationService(
                di_container=self.di_container,
                public_works_foundation=self.public_works_foundation
            )
            await self.client_config_foundation.initialize()
            print("   ✅ Client Config Foundation initialized")
            
            print("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup test environment: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_config_loader_creation(self) -> Dict[str, Any]:
        """Test ConfigLoader creation."""
        print("\n🧪 Test 1: ConfigLoader Creation")
        
        try:
            # Create config loader
            loader = await self.client_config_foundation.create_config_loader(
                tenant_id=self.test_tenant_id,
                storage_type="db"
            )
            
            if loader:
                print(f"   ✅ ConfigLoader created successfully")
                result = {
                    "test": "config_loader_creation",
                    "success": True,
                    "loader_available": loader is not None
                }
            else:
                print(f"   ❌ ConfigLoader creation returned None")
                result = {
                    "test": "config_loader_creation",
                    "success": False,
                    "error": "Loader is None"
                }
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test": "config_loader_creation",
                "success": False,
                "error": str(e)
            }
    
    async def test_config_loader_functionality(self) -> Dict[str, Any]:
        """Test ConfigLoader functionality."""
        print("\n🧪 Test 2: ConfigLoader Functionality")
        
        try:
            # Create config loader
            loader_builder = await self.client_config_foundation.create_config_loader(
                tenant_id=self.test_tenant_id,
                storage_type="db"
            )
            
            if not loader_builder:
                return {
                    "test": "config_loader_functionality",
                    "success": False,
                    "error": "Loader builder not created"
                }
            
            loader = loader_builder.get_loader()
            if not loader:
                return {
                    "test": "config_loader_functionality",
                    "success": False,
                    "error": "Loader instance not available"
                }
            
            # Test loading configs (will return empty if no configs exist, which is OK)
            configs = await loader.load_tenant_config()
            
            print(f"   ✅ ConfigLoader loaded configs (found {len(configs)} config types)")
            result = {
                "test": "config_loader_functionality",
                "success": True,
                "configs_loaded": len(configs),
                "config_types": list(configs.keys()) if isinstance(configs, dict) else []
            }
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test": "config_loader_functionality",
                "success": False,
                "error": str(e)
            }
    
    async def test_config_storage_creation(self) -> Dict[str, Any]:
        """Test ConfigStorage creation."""
        print("\n🧪 Test 3: ConfigStorage Creation")
        
        try:
            # Create config storage
            storage = await self.client_config_foundation.create_config_storage(
                tenant_id=self.test_tenant_id,
                storage_type="db"
            )
            
            if storage:
                print(f"   ✅ ConfigStorage created successfully")
                result = {
                    "test": "config_storage_creation",
                    "success": True,
                    "storage_available": storage is not None
                }
            else:
                print(f"   ❌ ConfigStorage creation returned None")
                result = {
                    "test": "config_storage_creation",
                    "success": False,
                    "error": "Storage is None"
                }
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test": "config_storage_creation",
                "success": False,
                "error": str(e)
            }
    
    async def test_config_storage_functionality(self) -> Dict[str, Any]:
        """Test ConfigStorage functionality."""
        print("\n🧪 Test 4: ConfigStorage Functionality")
        
        try:
            # Create config storage
            storage_builder = await self.client_config_foundation.create_config_storage(
                tenant_id=self.test_tenant_id,
                storage_type="db"
            )
            
            if not storage_builder:
                return {
                    "test": "config_storage_functionality",
                    "success": False,
                    "error": "Storage builder not created"
                }
            
            storage = storage_builder.get_storage()
            if not storage:
                return {
                    "test": "config_storage_functionality",
                    "success": False,
                    "error": "Storage instance not available"
                }
            
            # Test storing a config
            test_config = {
                "name": "test_domain_model",
                "fields": [
                    {"name": "id", "type": "string"},
                    {"name": "name", "type": "string"}
                ]
            }
            
            user_context = {
                "user_id": "test_user",
                "tenant_id": self.test_tenant_id
            }
            
            config_id = await storage.store_config(
                config_type="domain_models",
                config=test_config,
                user_context=user_context
            )
            
            print(f"   ✅ ConfigStorage stored config (ID: {config_id})")
            result = {
                "test": "config_storage_functionality",
                "success": True,
                "config_id": config_id
            }
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test": "config_storage_functionality",
                "success": False,
                "error": str(e)
            }
    
    async def test_config_validator_creation(self) -> Dict[str, Any]:
        """Test ConfigValidator creation."""
        print("\n🧪 Test 5: ConfigValidator Creation")
        
        try:
            # Create config validator
            validator = await self.client_config_foundation.create_config_validator(
                tenant_id=self.test_tenant_id
            )
            
            if validator:
                print(f"   ✅ ConfigValidator created successfully")
                result = {
                    "test": "config_validator_creation",
                    "success": True,
                    "validator_available": validator is not None
                }
            else:
                print(f"   ❌ ConfigValidator creation returned None")
                result = {
                    "test": "config_validator_creation",
                    "success": False,
                    "error": "Validator is None"
                }
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test": "config_validator_creation",
                "success": False,
                "error": str(e)
            }
    
    async def test_config_validator_functionality(self) -> Dict[str, Any]:
        """Test ConfigValidator functionality."""
        print("\n🧪 Test 6: ConfigValidator Functionality")
        
        try:
            # Create config validator
            validator_builder = await self.client_config_foundation.create_config_validator(
                tenant_id=self.test_tenant_id
            )
            
            if not validator_builder:
                return {
                    "test": "config_validator_functionality",
                    "success": False,
                    "error": "Validator builder not created"
                }
            
            validator = validator_builder.get_validator()
            if not validator:
                return {
                    "test": "config_validator_functionality",
                    "success": False,
                    "error": "Validator instance not available"
                }
            
            # Test validating a valid config
            valid_config = {
                "name": "test_workflow",
                "steps": [
                    {"type": "action", "name": "step1"}
                ]
            }
            
            user_context = {
                "user_id": "test_user",
                "tenant_id": self.test_tenant_id
            }
            
            validation_result = await validator.validate_config(
                config_type="workflows",
                config=valid_config,
                user_context=user_context
            )
            
            is_valid = validation_result.get("is_valid", False)
            issues = validation_result.get("issues", [])
            
            if is_valid:
                print(f"   ✅ ConfigValidator validated config (valid)")
            else:
                print(f"   ⚠️  ConfigValidator found {len(issues)} issues")
                for issue in issues:
                    print(f"      - {issue}")
            
            result = {
                "test": "config_validator_functionality",
                "success": True,
                "is_valid": is_valid,
                "issues_count": len(issues)
            }
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test": "config_validator_functionality",
                "success": False,
                "error": str(e)
            }
    
    async def test_config_versioner_creation(self) -> Dict[str, Any]:
        """Test ConfigVersioner creation."""
        print("\n🧪 Test 7: ConfigVersioner Creation")
        
        try:
            # Create config versioner
            versioner = await self.client_config_foundation.create_config_versioner(
                tenant_id=self.test_tenant_id,
                storage_type="db"
            )
            
            if versioner:
                print(f"   ✅ ConfigVersioner created successfully")
                result = {
                    "test": "config_versioner_creation",
                    "success": True,
                    "versioner_available": versioner is not None
                }
            else:
                print(f"   ❌ ConfigVersioner creation returned None")
                result = {
                    "test": "config_versioner_creation",
                    "success": False,
                    "error": "Versioner is None"
                }
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test": "config_versioner_creation",
                "success": False,
                "error": str(e)
            }
    
    async def test_config_versioner_functionality(self) -> Dict[str, Any]:
        """Test ConfigVersioner functionality."""
        print("\n🧪 Test 8: ConfigVersioner Functionality")
        
        try:
            # Create config versioner
            versioner_builder = await self.client_config_foundation.create_config_versioner(
                tenant_id=self.test_tenant_id,
                storage_type="db"
            )
            
            if not versioner_builder:
                return {
                    "test": "config_versioner_functionality",
                    "success": False,
                    "error": "Versioner builder not created"
                }
            
            versioner = versioner_builder.get_versioner()
            if not versioner:
                return {
                    "test": "config_versioner_functionality",
                    "success": False,
                    "error": "Versioner instance not available"
                }
            
            # Test getting versions (will return empty if no versions exist, which is OK)
            versions = await versioner.get_versions("domain_models", limit=10)
            
            print(f"   ✅ ConfigVersioner retrieved versions (found {len(versions)} versions)")
            result = {
                "test": "config_versioner_functionality",
                "success": True,
                "versions_found": len(versions)
            }
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "test": "config_versioner_functionality",
                "success": False,
                "error": str(e)
            }
    
    async def run_all_tests(self):
        """Run all Phase 2 Client Config Foundation tests."""
        print("=" * 70)
        print("Phase 2: Client Config Foundation - Test Suite")
        print("=" * 70)
        
        # Setup
        setup_success = await self.setup_test_environment()
        if not setup_success:
            print("\n❌ Test environment setup failed")
            return {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "results": []
            }
        
        # Run tests
        self.test_results.append(await self.test_config_loader_creation())
        self.test_results.append(await self.test_config_loader_functionality())
        self.test_results.append(await self.test_config_storage_creation())
        self.test_results.append(await self.test_config_storage_functionality())
        self.test_results.append(await self.test_config_validator_creation())
        self.test_results.append(await self.test_config_validator_functionality())
        self.test_results.append(await self.test_config_versioner_creation())
        self.test_results.append(await self.test_config_versioner_functionality())
        
        # Print summary
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        
        passed = sum(1 for r in self.test_results if r.get("success", False))
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅ PASS" if result.get("success", False) else "❌ FAIL"
            print(f"{status}: {result.get('test', 'unknown')}")
            if not result.get("success", False) and "error" in result:
                print(f"      Error: {result['error']}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "results": self.test_results
        }


async def main():
    """Main test execution."""
    tester = Phase2ClientConfigTester()
    results = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())










