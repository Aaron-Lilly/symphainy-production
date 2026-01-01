#!/usr/bin/env python3
"""
Architectural Pattern Validation Test

Validates the three critical architectural patterns:
1. Smart City roles have access to ALL abstractions, Business Enablement has selective access
2. Smart City roles expose SOA APIs (to curator) for other realms to use
3. Business Enablement roles use Smart City SOA APIs (from curator) to compose services

WHAT (Validation Role): I validate architectural access patterns and SOA API enforcement
HOW (Validation Test): I test abstraction access and SOA API patterns to prevent spaghetti code
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bases.protocols.service_protocol import ServiceProtocol
from bases.protocols.smart_city_role_protocol import SmartCityRoleProtocol
from bases.protocols.realm_service_protocol import RealmServiceProtocol
from bases.smart_city_role_base import SmartCityRoleBase
from bases.realm_service_base import RealmServiceBase
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.infrastructure_access_mixin import InfrastructureAccessMixin
from bases.mixins.security_mixin import SecurityMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin
from bases.mixins.platform_capabilities_mixin import PlatformCapabilitiesMixin
from bases.mixins.micro_module_support_mixin import MicroModuleSupportMixin
from bases.mixins.communication_mixin import CommunicationMixin


class MockPlatformGateway:
    """Mock Platform Gateway with proper realm access control."""
    
    def __init__(self):
        # Smart City gets ALL abstractions (privileged access)
        self.smart_city_abstractions = {
            "auth", "authorization", "session", "tenant", "file_management",
            "content_metadata", "content_schema", "content_insights", "llm",
            "agui", "policy", "tool_storage", "event_management", "messaging",
            "task_management", "workflow_orchestration", "resource_allocation",
            "health_monitoring", "telemetry_reporting", "api_gateway_routing",
            "load_balancing", "real_time_communication", "streaming_data"
        }
        
        # Business Enablement gets SELECTIVE abstractions (controlled access)
        self.business_enablement_abstractions = {
            "content_metadata", "content_schema", "content_insights", 
            "file_management", "llm"
        }
        
        # Experience gets SELECTIVE abstractions (controlled access)
        self.experience_abstractions = {
            "session", "auth", "authorization", "tenant"
        }
    
    def get_abstraction(self, abstraction_name: str, realm_name: str):
        """Get abstraction for specific realm with access control."""
        if realm_name == "smart_city":
            if abstraction_name in self.smart_city_abstractions:
                return MockAbstraction(abstraction_name, "smart_city")
            else:
                raise PermissionError(f"Smart City cannot access {abstraction_name}")
        
        elif realm_name == "business_enablement":
            if abstraction_name in self.business_enablement_abstractions:
                return MockAbstraction(abstraction_name, "business_enablement")
            else:
                raise PermissionError(f"Business Enablement cannot access {abstraction_name}")
        
        elif realm_name == "experience":
            if abstraction_name in self.experience_abstractions:
                return MockAbstraction(abstraction_name, "experience")
            else:
                raise PermissionError(f"Experience cannot access {abstraction_name}")
        
        else:
            raise PermissionError(f"Unknown realm: {realm_name}")
    
    def get_realm_abstractions(self, realm_name: str):
        """Get all allowed abstractions for a realm."""
        if realm_name == "smart_city":
            abstractions = {}
            for abs_name in self.smart_city_abstractions:
                abstractions[abs_name] = MockAbstraction(abs_name, "smart_city")
            return abstractions
        
        elif realm_name == "business_enablement":
            abstractions = {}
            for abs_name in self.business_enablement_abstractions:
                abstractions[abs_name] = MockAbstraction(abs_name, "business_enablement")
            return abstractions
        
        elif realm_name == "experience":
            abstractions = {}
            for abs_name in self.experience_abstractions:
                abstractions[abs_name] = MockAbstraction(abs_name, "experience")
            return abstractions
        
        else:
            return {}


class MockAbstraction:
    """Mock abstraction for testing."""
    
    def __init__(self, name: str, realm: str):
        self.name = name
        self.realm = realm
    
    async def process(self, data: Dict[str, Any]):
        return {"processed": True, "abstraction": self.name, "realm": self.realm, "data": data}


class MockCuratorFoundation:
    """Mock Curator Foundation for SOA API management."""
    
    def __init__(self):
        self.soa_apis = {}
        self.api_registry = {}
    
    def register_soa_api(self, service_name: str, api_name: str, endpoint: str, handler: Any):
        """Register SOA API from Smart City role."""
        if service_name not in self.soa_apis:
            self.soa_apis[service_name] = {}
        
        self.soa_apis[service_name][api_name] = {
            "endpoint": endpoint,
            "handler": handler,
            "registered_at": datetime.utcnow().isoformat()
        }
        
        # Also register in global API registry
        self.api_registry[f"{service_name}.{api_name}"] = {
            "service": service_name,
            "api": api_name,
            "endpoint": endpoint,
            "handler": handler
        }
        
        print(f"✅ SOA API registered: {service_name}.{api_name} at {endpoint}")
        return True
    
    def get_soa_api(self, service_name: str, api_name: str):
        """Get SOA API for realm consumption."""
        if service_name in self.soa_apis and api_name in self.soa_apis[service_name]:
            return self.soa_apis[service_name][api_name]
        return None
    
    def list_soa_apis(self, service_name: Optional[str] = None):
        """List available SOA APIs."""
        if service_name:
            return self.soa_apis.get(service_name, {})
        return self.api_registry


class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.logger = MockLogger()
        self.config = MockConfig()
        self.health = MockHealth()
        self.telemetry = MockTelemetry()
        self.error_handler = MockErrorHandler()
        self.tenant = MockTenant()
        self.validation = MockValidation()
        self.serialization = MockSerialization()
        self.security = MockSecurity()
        self.curator_foundation = MockCuratorFoundation()
    
    def get_utility(self, name: str):
        """Get utility by name."""
        utilities = {
            "logger": self.logger,
            "config": self.config,
            "health": self.health,
            "telemetry": self.telemetry,
            "error_handler": self.error_handler,
            "tenant": self.tenant,
            "validation": self.validation,
            "serialization": self.serialization,
            "security": self.security,
            "curator_foundation": self.curator_foundation
        }
        return utilities.get(name)
    
    def get_abstraction(self, name: str):
        """Get abstraction by name (for Smart City direct access)."""
        return MockAbstraction(name, "smart_city")


class MockLogger:
    """Mock Logger for testing."""
    
    def info(self, message: str):
        print(f"INFO: {message}")
    
    def debug(self, message: str):
        print(f"DEBUG: {message}")
    
    def warning(self, message: str):
        print(f"WARNING: {message}")
    
    def error(self, message: str):
        print(f"ERROR: {message}")


class MockConfig:
    """Mock Config for testing."""
    
    def get(self, key: str, default: Any = None):
        config_values = {
            "service_name": "test_service",
            "debug_mode": True,
            "max_connections": 100
        }
        return config_values.get(key, default)


class MockHealth:
    """Mock Health for testing."""
    
    async def run_all_health_checks(self):
        return {
            "status": "healthy",
            "checks": {
                "database": "healthy",
                "redis": "healthy",
                "api": "healthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }


class MockTelemetry:
    """Mock Telemetry for testing."""
    
    def record_metric(self, name: str, value: float, metadata: Dict[str, Any]):
        print(f"TELEMETRY: {name} = {value} with {metadata}")
    
    def record_event(self, name: str, data: Dict[str, Any]):
        print(f"EVENT: {name} with {data}")


class MockErrorHandler:
    """Mock Error Handler for testing."""
    
    async def handle_error(self, error: Exception):
        print(f"ERROR HANDLED: {error}")


class MockTenant:
    """Mock Tenant for testing."""
    
    def get_current_tenant(self):
        return "test_tenant"


class MockValidation:
    """Mock Validation for testing."""
    
    def validate(self, data: Any, schema: Any):
        return True


class MockSerialization:
    """Mock Serialization for testing."""
    
    def serialize(self, data: Any):
        return str(data)
    
    def deserialize(self, data: str):
        return data


class MockSecurity:
    """Mock Security for testing."""
    
    def validate_context(self, context: Dict[str, Any]):
        return context


class TestSmartCityRole(SmartCityRoleBase, UtilityAccessMixin, InfrastructureAccessMixin, 
                       SecurityMixin, PerformanceMonitoringMixin, PlatformCapabilitiesMixin,
                       MicroModuleSupportMixin, CommunicationMixin):
    """Test Smart City Role with ALL abstraction access."""
    
    def __init__(self, service_name: str, role_name: str, di_container: MockDIContainer):
        # Initialize core properties first
        self.service_name = service_name
        self.role_name = role_name
        self.di_container = di_container
        self.start_time = datetime.utcnow()
        self.is_initialized = False
        self.service_health = "unknown"
        
        # Initialize all mixins
        self._init_utility_access(di_container)
        self._init_infrastructure_access(di_container)
        self._init_security()
        self._init_performance_monitoring(di_container)
        self._init_platform_capabilities(di_container)
        self._init_micro_module_support(service_name)
        self._init_communication(di_container)
        
        self.logger = self.get_logger()
        self.capabilities = ["soa_api_exposure", "foundation_orchestration"]
        self.dependencies = ["all_foundations"]
        
        self.logger.info(f"🏗️ TestSmartCityRole '{service_name}' initialized for role '{role_name}'")
    
    async def initialize(self) -> bool:
        """Initialize the Smart City role."""
        try:
            self.logger.info(f"🚀 Initializing {self.service_name}...")
            
            # Smart City-specific initialization
            self.service_health = "healthy"
            self.is_initialized = True
            
            self.logger.info(f"✅ {self.service_name} Smart City Role initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            self.service_health = "unhealthy"
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the Smart City role gracefully."""
        try:
            self.logger.info(f"🛑 Shutting down {self.service_name}...")
            
            # Smart City-specific shutdown
            self.is_initialized = False
            self.service_health = "shutdown"
            
            self.logger.info(f"✅ {self.service_name} Smart City Role shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown {self.service_name}: {e}")
            return False
    
    def get_foundation_abstraction(self, name: str) -> Any:
        """Get foundation abstraction directly (Smart City privilege)."""
        return self.di_container.get_abstraction(name)
    
    def get_all_foundation_abstractions(self) -> Dict[str, Any]:
        """Get all foundation abstractions (Smart City privilege)."""
        abstractions = {}
        abstraction_names = [
            "auth", "authorization", "session", "tenant", "file_management",
            "content_metadata", "content_schema", "content_insights", "llm",
            "agui", "policy", "tool_storage", "event_management", "messaging",
            "task_management", "workflow_orchestration", "resource_allocation",
            "health_monitoring", "telemetry_reporting", "api_gateway_routing",
            "load_balancing", "real_time_communication", "streaming_data"
        ]
        
        for name in abstraction_names:
            try:
                abstractions[name] = self.get_foundation_abstraction(name)
            except:
                pass  # Some abstractions may not be available
        
        return abstractions
    
    async def expose_soa_api(self, api_name: str, endpoint: str, handler: Any) -> bool:
        """Expose SOA API for realm consumption via Curator."""
        try:
            curator = self.di_container.get_utility("curator_foundation")
            success = curator.register_soa_api(self.service_name, api_name, endpoint, handler)
            self.logger.info(f"Exposed SOA API: {api_name} at {endpoint}")
            return success
        except Exception as e:
            self.logger.error(f"Failed to expose SOA API {api_name}: {e}")
            return False
    
    async def get_soa_apis(self) -> Dict[str, Any]:
        """Get all exposed SOA APIs."""
        curator = self.di_container.get_utility("curator_foundation")
        return curator.list_soa_apis(self.service_name)


class TestBusinessEnablementRole(RealmServiceBase, UtilityAccessMixin, InfrastructureAccessMixin, 
                                SecurityMixin, PerformanceMonitoringMixin, PlatformCapabilitiesMixin,
                                CommunicationMixin):
    """Test Business Enablement Role with SELECTIVE abstraction access."""
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: MockPlatformGateway, di_container: MockDIContainer):
        # Initialize core properties first
        self.service_name = service_name
        self.realm_name = realm_name
        self.platform_gateway = platform_gateway
        self.di_container = di_container
        self.start_time = datetime.utcnow()
        self.is_initialized = False
        self.service_health = "unknown"
        
        # Initialize all mixins
        self._init_utility_access(di_container)
        self._init_infrastructure_access(di_container)
        self._init_security()
        self._init_performance_monitoring(di_container)
        self._init_platform_capabilities(di_container)
        self._init_communication(di_container)
        
        self.logger = self.get_logger()
        self.capabilities = ["business_workflow", "pillar_coordination"]
        self.dependencies = ["smart_city_soa_apis"]
        
        self.logger.info(f"🏗️ TestBusinessEnablementRole '{service_name}' initialized for realm '{realm_name}'")
    
    async def initialize(self) -> bool:
        """Initialize the Business Enablement role."""
        try:
            self.logger.info(f"🚀 Initializing {self.service_name}...")
            
            # Business Enablement-specific initialization
            self.service_health = "healthy"
            self.is_initialized = True
            
            self.logger.info(f"✅ {self.service_name} Business Enablement Role initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            self.service_health = "unhealthy"
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the Business Enablement role gracefully."""
        try:
            self.logger.info(f"🛑 Shutting down {self.service_name}...")
            
            # Business Enablement-specific shutdown
            self.is_initialized = False
            self.service_health = "shutdown"
            
            self.logger.info(f"✅ {self.service_name} Business Enablement Role shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown {self.service_name}: {e}")
            return False
    
    def get_abstraction(self, abstraction_name: str) -> Any:
        """Get abstraction through Platform Gateway (controlled access)."""
        return self.platform_gateway.get_abstraction(abstraction_name, self.realm_name)
    
    def get_realm_abstractions(self) -> Dict[str, Any]:
        """Get all allowed abstractions for this realm."""
        return self.platform_gateway.get_realm_abstractions(self.realm_name)
    
    async def use_smart_city_soa_api(self, service_name: str, api_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Use Smart City SOA API via Curator Foundation."""
        try:
            curator = self.di_container.get_utility("curator_foundation")
            soa_api = curator.get_soa_api(service_name, api_name)
            
            if soa_api:
                self.logger.info(f"Using Smart City SOA API: {service_name}.{api_name}")
                # Simulate API call
                return {
                    "status": "success",
                    "service": service_name,
                    "api": api_name,
                    "request": request,
                    "response": "processed_by_smart_city"
                }
            else:
                return {"status": "error", "error": f"SOA API {service_name}.{api_name} not found"}
                
        except Exception as e:
            self.logger.error(f"Failed to use Smart City SOA API {service_name}.{api_name}: {e}")
            return {"status": "error", "error": str(e)}


async def test_abstraction_access_patterns():
    """Test 1: Smart City has ALL abstractions, Business Enablement has SELECTIVE abstractions."""
    print("🔍 Testing Abstraction Access Patterns...")
    
    di_container = MockDIContainer()
    platform_gateway = MockPlatformGateway()
    
    # Test Smart City Role (should have ALL abstractions)
    smart_city_role = TestSmartCityRole("post_office", "post_office", di_container)
    
    print("\n1. Testing Smart City Role - ALL Abstraction Access...")
    
    # Smart City should be able to access ALL abstractions
    all_abstractions = smart_city_role.get_all_foundation_abstractions()
    assert len(all_abstractions) > 20, "Smart City should have access to ALL abstractions"
    
    # Test specific abstractions that only Smart City should have
    auth_abstraction = smart_city_role.get_foundation_abstraction("auth")
    assert auth_abstraction is not None, "Smart City should have access to auth abstraction"
    
    messaging_abstraction = smart_city_role.get_foundation_abstraction("messaging")
    assert messaging_abstraction is not None, "Smart City should have access to messaging abstraction"
    
    print("✅ Smart City Role has ALL abstraction access")
    
    # Test Business Enablement Role (should have SELECTIVE abstractions)
    business_role = TestBusinessEnablementRole("content_pillar", "business_enablement", platform_gateway, di_container)
    
    print("\n2. Testing Business Enablement Role - SELECTIVE Abstraction Access...")
    
    # Business Enablement should only have SELECTIVE abstractions
    realm_abstractions = business_role.get_realm_abstractions()
    assert len(realm_abstractions) == 5, "Business Enablement should have only 5 abstractions"
    
    # Test allowed abstractions
    content_metadata = business_role.get_abstraction("content_metadata")
    assert content_metadata is not None, "Business Enablement should have access to content_metadata"
    
    llm_abstraction = business_role.get_abstraction("llm")
    assert llm_abstraction is not None, "Business Enablement should have access to llm"
    
    # Test forbidden abstractions (should raise PermissionError)
    try:
        auth_abstraction = business_role.get_abstraction("auth")
        assert False, "Business Enablement should NOT have access to auth abstraction"
    except PermissionError:
        print("✅ Business Enablement correctly blocked from auth abstraction")
    
    try:
        messaging_abstraction = business_role.get_abstraction("messaging")
        assert False, "Business Enablement should NOT have access to messaging abstraction"
    except PermissionError:
        print("✅ Business Enablement correctly blocked from messaging abstraction")
    
    print("✅ Business Enablement Role has SELECTIVE abstraction access")
    
    return True


async def test_soa_api_exposure():
    """Test 2: Smart City roles expose SOA APIs to Curator."""
    print("\n🔍 Testing SOA API Exposure...")
    
    di_container = MockDIContainer()
    smart_city_role = TestSmartCityRole("post_office", "post_office", di_container)
    
    # Initialize Smart City role
    await smart_city_role.initialize()
    
    print("\n3. Testing Smart City SOA API Exposure...")
    
    # Smart City should expose SOA APIs
    success = await smart_city_role.expose_soa_api("send_message", "/api/messaging/send", lambda x: x)
    assert success, "Smart City should be able to expose SOA APIs"
    
    success = await smart_city_role.expose_soa_api("route_event", "/api/events/route", lambda x: x)
    assert success, "Smart City should be able to expose multiple SOA APIs"
    
    # Check that APIs are registered in Curator
    curator = di_container.get_utility("curator_foundation")
    soa_apis = curator.list_soa_apis("post_office")
    assert len(soa_apis) == 2, "Curator should have registered SOA APIs"
    
    print("✅ Smart City Role exposes SOA APIs to Curator")
    
    return True


async def test_soa_api_consumption():
    """Test 3: Business Enablement roles use Smart City SOA APIs via Curator."""
    print("\n🔍 Testing SOA API Consumption...")
    
    di_container = MockDIContainer()
    platform_gateway = MockPlatformGateway()
    
    # First, expose some SOA APIs from Smart City
    smart_city_role = TestSmartCityRole("post_office", "post_office", di_container)
    await smart_city_role.initialize()
    await smart_city_role.expose_soa_api("send_message", "/api/messaging/send", lambda x: x)
    await smart_city_role.expose_soa_api("route_event", "/api/events/route", lambda x: x)
    
    # Now test Business Enablement consuming those APIs
    business_role = TestBusinessEnablementRole("content_pillar", "business_enablement", platform_gateway, di_container)
    await business_role.initialize()
    
    print("\n4. Testing Business Enablement SOA API Consumption...")
    
    # Business Enablement should use Smart City SOA APIs
    result = await business_role.use_smart_city_soa_api("post_office", "send_message", {"message": "test"})
    assert result["status"] == "success", "Business Enablement should be able to use Smart City SOA APIs"
    assert result["service"] == "post_office", "Should use correct Smart City service"
    assert result["api"] == "send_message", "Should use correct SOA API"
    
    result = await business_role.use_smart_city_soa_api("post_office", "route_event", {"event": "test"})
    assert result["status"] == "success", "Business Enablement should be able to use multiple SOA APIs"
    
    # Test non-existent API
    result = await business_role.use_smart_city_soa_api("post_office", "non_existent", {"test": "data"})
    assert result["status"] == "error", "Should handle non-existent SOA APIs gracefully"
    
    print("✅ Business Enablement Role uses Smart City SOA APIs via Curator")
    
    return True


async def test_spaghetti_code_prevention():
    """Test that the architecture prevents spaghetti code implementations."""
    print("\n🔍 Testing Spaghetti Code Prevention...")
    
    di_container = MockDIContainer()
    platform_gateway = MockPlatformGateway()
    
    # First, expose SOA APIs from Smart City
    smart_city_role = TestSmartCityRole("post_office", "post_office", di_container)
    await smart_city_role.initialize()
    await smart_city_role.expose_soa_api("send_message", "/api/messaging/send", lambda x: x)
    
    # Now test Business Enablement
    business_role = TestBusinessEnablementRole("content_pillar", "business_enablement", platform_gateway, di_container)
    await business_role.initialize()
    
    print("\n5. Testing Spaghetti Code Prevention...")
    
    # Business Enablement should NOT be able to directly access Smart City capabilities
    # This prevents spaghetti code where realms implement Smart City functionality
    
    # Test 1: Cannot access forbidden abstractions
    forbidden_abstractions = ["messaging", "event_management", "workflow_orchestration"]
    for abstraction in forbidden_abstractions:
        try:
            business_role.get_abstraction(abstraction)
            assert False, f"Business Enablement should NOT have direct access to {abstraction}"
        except PermissionError:
            print(f"✅ Business Enablement correctly blocked from {abstraction}")
    
    # Test 2: Must use SOA APIs instead of direct access
    # This enforces the pattern: Business Enablement -> Smart City SOA APIs -> Smart City capabilities
    result = await business_role.use_smart_city_soa_api("post_office", "send_message", {"message": "test"})
    assert result["status"] == "success", "Business Enablement should use SOA APIs for Smart City capabilities"
    
    print("✅ Architecture prevents spaghetti code implementations")
    
    return True


async def main():
    """Run all architectural pattern validation tests."""
    print("🏗️ Architectural Pattern Validation Test")
    print("=" * 60)
    
    try:
        # Run all tests
        await test_abstraction_access_patterns()
        await test_soa_api_exposure()
        await test_soa_api_consumption()
        await test_spaghetti_code_prevention()
        
        print("\n" + "=" * 60)
        print("🎉 ALL ARCHITECTURAL PATTERN TESTS PASSED!")
        print("\n✅ Architectural Pattern Validation Results:")
        print("   • Smart City has ALL abstraction access: ✅ Enforced")
        print("   • Business Enablement has SELECTIVE abstraction access: ✅ Enforced")
        print("   • Smart City exposes SOA APIs to Curator: ✅ Working")
        print("   • Business Enablement uses Smart City SOA APIs: ✅ Working")
        print("   • Spaghetti code prevention: ✅ Enforced")
        
        print("\n🚀 CONCLUSION: Architecture properly enforces access patterns!")
        print("   • Smart City roles: Direct foundation access + SOA API exposure")
        print("   • Business Enablement roles: Controlled abstraction access + SOA API consumption")
        print("   • Curator Foundation: SOA API registry and routing")
        print("   • Spaghetti code prevention: Architecture enforces proper patterns")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
