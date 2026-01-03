#!/usr/bin/env python3
"""
Smart City Role Base Class

Simplified base class for Smart City roles that composes focused mixins.
Implements SmartCityRoleProtocol with clean, composable architecture.

WHAT (Smart City Role): I provide the foundation for all Smart City roles
HOW (Smart City Role): I compose 7 mixins for comprehensive platform orchestration
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC

from bases.protocols.smart_city_role_protocol import SmartCityRoleProtocol
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.infrastructure_access_mixin import InfrastructureAccessMixin
from bases.mixins.security_mixin import SecurityMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin
from bases.mixins.platform_capabilities_mixin import PlatformCapabilitiesMixin
from bases.mixins.micro_module_support_mixin import MicroModuleSupportMixin
from bases.mixins.communication_mixin import CommunicationMixin


class SmartCityRoleBase(SmartCityRoleProtocol, UtilityAccessMixin, InfrastructureAccessMixin, SecurityMixin, PerformanceMonitoringMixin, PlatformCapabilitiesMixin, MicroModuleSupportMixin, CommunicationMixin, ABC):
    """
    Smart City Role Base Class - Simplified Foundation for ALL Smart City Roles
    
    Composes 7 focused mixins to provide comprehensive platform orchestration
    with direct foundation access and micro-module support.
    """
    
    def __init__(self, service_name: str, role_name: str, di_container: Any):
        """Initialize Smart City Role Base with composed mixins."""
        # Core service properties
        self.service_name = service_name
        self.role_name = role_name
        self.realm_name = "smart_city"  # Smart City services are in smart_city realm
        self.di_container = di_container
        self.start_time = datetime.utcnow()
        self.is_initialized = False
        self.service_health = "unknown"
        
        # Get Platform Gateway from DI Container (lazy-load if not available yet)
        try:
            self.platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
        except Exception:
            self.platform_gateway = None
        
        # Initialize mixins
        self._init_utility_access(di_container)
        self._init_infrastructure_access(di_container, self.platform_gateway)
        self._init_security(di_container)
        self._init_performance_monitoring(di_container)
        self._init_platform_capabilities(di_container)
        self._init_micro_module_support(service_name, di_container)
        self._init_communication(di_container)
        
        self.logger = self.get_logger()
        if self.logger:
            self.logger.info(f"🏗️ SmartCityRoleBase '{service_name}' initialized for role '{role_name}'")
    
    # ============================================================================
    # MICRO-MODULE SUPPORT - Explicit delegation to mixin
    # ============================================================================
    # Override to ensure mixin's implementation is used (not protocol's)
    # The Protocol defines get_module with ..., but the mixin has the real implementation
    # CRITICAL: Protocol comes before Mixin in MRO, so we must explicitly call the mixin
    def get_module(self, module_name: str) -> Any:
        """Get micro-module instance - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return MicroModuleSupportMixin.get_module(self, module_name)
    
    def load_micro_module(self, module_name: str) -> bool:
        """Load micro-module dynamically - explicitly call mixin's implementation."""
        return MicroModuleSupportMixin.load_micro_module(self, module_name)
    
    # ============================================================================
    # INFRASTRUCTURE ACCESS - Explicit delegation to mixin
    # ============================================================================
    # Override to ensure mixin's implementation is used (not protocol's)
    # The Protocol defines get_infrastructure_abstraction with ..., but the mixin has the real implementation
    # CRITICAL: Protocol comes before Mixin in MRO, so we must explicitly call the mixin
    def get_infrastructure_abstraction(self, name: str) -> Any:
        """Get infrastructure abstraction - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return InfrastructureAccessMixin.get_infrastructure_abstraction(self, name)
    
    def get_auth_abstraction(self) -> Any:
        """Get authentication abstraction - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return InfrastructureAccessMixin.get_auth_abstraction(self)
    
    # ============================================================================
    # UTILITY ACCESS - Explicit delegation to mixin
    # ============================================================================
    # Override to ensure mixin's implementation is used (not protocol's)
    # The Protocol defines get_utility with ..., but the mixin has the real implementation
    # CRITICAL: Protocol comes before Mixin in MRO, so we must explicitly call the mixin
    def get_utility(self, name: str) -> Any:
        """Get utility service - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return UtilityAccessMixin.get_utility(self, name)
    
    async def initialize(self) -> bool:
        """Initialize the Smart City role."""
        try:
            if self.logger:
                self.logger.info(f"🚀 Initializing {self.service_name}...")
            
            # Smart City-specific initialization
            self.service_health = "healthy"
            self.is_initialized = True
            
            if self.logger:
                self.logger.info(f"✅ {self.service_name} Smart City Role initialized successfully")
            return True
            
        except Exception as e:
            if self.logger:
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
        return self.get_infrastructure_abstraction(name)
    
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
                abstractions[name] = self.get_infrastructure_abstraction(name)
            except:
                pass  # Some abstractions may not be available
        
        return abstractions
    
    async def expose_soa_api(self, api_name: str, endpoint: str, handler: Any) -> bool:
        """Expose SOA API for realm consumption."""
        try:
            # This would integrate with the Communication Foundation
            self.logger.info(f"Exposing SOA API: {api_name} at {endpoint}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to expose SOA API {api_name}: {e}")
            return False
    
    async def get_soa_apis(self) -> Dict[str, Any]:
        """
        Get all exposed SOA APIs.
        
        Smart City services can expose SOA APIs in two ways:
        1. **SoaMcp Module Pattern (Recommended):** The `SoaMcp` micro-module sets `self.soa_apis`
           during `initialize_soa_api_exposure()`. This method automatically returns it.
        2. **Override Pattern:** Services can override this method to return custom SOA API definitions.
        
        Returns:
            Dict containing SOA API definitions. Format:
            {
                "api_name": {
                    "endpoint": "/api/service/endpoint",
                    "method": "POST",
                    "description": "API description",
                    "parameters": ["param1", "param2"]
                },
                ...
            }
        
        Note:
            If neither pattern is used, returns a placeholder dict. Services should use one of the patterns
            to properly expose their SOA APIs for realm consumption.
        """
        # Check if SoaMcp module has set self.soa_apis
        if hasattr(self, 'soa_apis') and isinstance(self.soa_apis, dict) and len(self.soa_apis) > 0:
            return self.soa_apis
        
        # If service overrides this method, it will be called instead
        # Otherwise, log a warning and return placeholder
        if self.logger:
            self.logger.warning(
                f"⚠️ {self.service_name} has not exposed SOA APIs. "
                f"Either use SoaMcp module pattern (sets self.soa_apis) or override get_soa_apis() method."
            )
        
        return {"status": "soa_apis_placeholder", "message": "Service has not exposed SOA APIs"}
    
    async def orchestrate_foundation_capabilities(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate foundational capabilities into platform services."""
        try:
            self.logger.info(f"Orchestrating foundation capabilities: {request}")
            return {"status": "orchestration_started", "request": request}
        except Exception as e:
            self.logger.error(f"Failed to orchestrate foundation capabilities: {e}")
            return {"status": "error", "error": str(e)}
    
    async def coordinate_with_other_roles(self, role_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate with other Smart City roles."""
        try:
            self.logger.info(f"Coordinating with {role_name}: {request}")
            return {"status": "coordination_started", "role": role_name, "request": request}
        except Exception as e:
            self.logger.error(f"Failed to coordinate with {role_name}: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        config = self.get_config()
        return config.get(key, default)
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        return {
            "service_name": self.service_name,
            "role_name": self.role_name,
            "service_type": "smart_city_role",
            "is_initialized": self.is_initialized,
            "service_health": self.service_health,
            "has_micro_modules": self.has_micro_modules(),
            "loaded_modules": self.get_loaded_modules(),
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    # ============================================================================
    # CURATOR REGISTRATION HELPER (Simplified Phase 2 Pattern for Smart City)
    # ============================================================================
    
    async def register_with_curator(
        self,
        capabilities: list,
        soa_apis: list,
        mcp_tools: list,
        protocols: Optional[List[Dict[str, Any]]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register Smart City service with Curator (simplified Phase 2 pattern).
        
        Smart City services are platform enablers, so they:
        - Register capabilities with SOA API and MCP Tool contracts
        - Skip semantic mapping (not user-facing)
        - Skip routing metadata (no user-facing routes)
        - Register protocols for type safety
        - Register with service discovery (via Public Works)
        
        Args:
            capabilities: List of service capabilities (dicts with name, protocol, description, contracts)
            soa_apis: List of SOA API method names (e.g., ["store_knowledge", "search_knowledge"])
            mcp_tools: List of MCP tool names (e.g., ["librarian_upload_file"])
            protocols: Optional list of protocol definitions (Python typing.Protocol)
            additional_metadata: Optional additional metadata
        
        Returns:
            True if registration successful, False otherwise
        
        Example:
            ```python
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "knowledge_management",
                        "protocol": "LibrarianServiceProtocol",
                        "description": "Knowledge management and semantic search",
                        "contracts": {
                            "soa_api": {
                                "api_name": "store_knowledge",
                                "endpoint": "/soa/librarian/store_knowledge",
                                "method": "POST"
                            },
                            "mcp_tool": {
                                "tool_name": "librarian_upload_file",
                                "mcp_server": "smart_city_mcp_server"
                            }
                        }
                        # NO semantic_mapping - Smart City services are not user-facing
                    }
                ],
                soa_apis=["store_knowledge", "search_knowledge"],
                mcp_tools=["librarian_upload_file"],
                protocols=[{
                    "name": "LibrarianServiceProtocol",
                    "definition": {"methods": {...}}
                }]
            )
            ```
        """
        try:
            curator = self.get_curator()
            if not curator:
                self.logger.warning("⚠️ Curator Foundation not available")
                return False
            
            # Import CapabilityDefinition
            from foundations.curator_foundation.models.capability_definition import CapabilityDefinition
            
            # 1. Register capabilities (using CapabilityDefinition) - simplified for Smart City
            for capability in capabilities:
                # Handle both dict and string formats (backward compatibility)
                if isinstance(capability, str):
                    # Simple string format - convert to dict
                    capability = {
                        "name": capability,
                        "description": capability,
                        "protocol": f"I{self.service_name}"
                    }
                
                # Extract capability name (required)
                capability_name = capability.get("name", capability.get("capability_name"))
                if not capability_name:
                    self.logger.warning(f"⚠️ Capability missing 'name' or 'capability_name', using description as fallback")
                    capability_name = capability.get("description", "unknown_capability").lower().replace(" ", "_")
                
                # Extract protocol name (required)
                protocol_name = capability.get("protocol", capability.get("protocol_name"))
                if not protocol_name:
                    # Default to service protocol name
                    protocol_name = f"{self.service_name}Protocol"
                
                # Ensure contracts exist (required)
                contracts = capability.get("contracts", {})
                if not contracts:
                    self.logger.warning(f"⚠️ Capability '{capability_name}' missing contracts, creating empty contracts dict")
                    contracts = {}
                
                # Convert capability dict to CapabilityDefinition
                # Smart City services don't need semantic mapping (not user-facing)
                capability_def = CapabilityDefinition(
                    capability_name=capability_name,
                    service_name=self.service_name,
                    protocol_name=protocol_name,
                    description=capability.get("description", capability.get("name", "")),
                    realm="smart_city",  # Smart City services always in smart_city realm
                    contracts=contracts,  # REQUIRED
                    semantic_mapping=None,  # Smart City services don't have semantic mapping
                    version=capability.get("version", "1.0.0")
                )
                await curator.register_domain_capability(capability_def)
            
            # 2. Register service protocols (Python typing.Protocol)
            if protocols:
                for protocol in protocols:
                    await curator.register_service_protocol(
                        service_name=self.service_name,
                        protocol_name=protocol["name"],
                        protocol=protocol["definition"]
                    )
            
            # 3. Routes are automatically registered when capabilities are registered
            # Smart City services don't have user-facing routes, so no explicit route registration needed
            
            # 4. Service mesh policies - optional for Smart City (can add later for Consul Connect)
            # Smart City services don't have user-facing routes, so routing metadata is not needed
            
            # 5. Register with service discovery (via Public Works)
            # Use existing register_service method for backward compatibility
            registration_data = {
                "service_name": self.service_name,
                "service_type": "smart_city",
                "realm": "smart_city",
                "capabilities": [cap.get("name", cap) if isinstance(cap, dict) else cap for cap in capabilities],
                "soa_apis": soa_apis,
                "mcp_tools": mcp_tools,
                "service_instance": self,
                "health_check_endpoint": f"{self.service_name}/health",
                "start_time": self.start_time.isoformat(),
                "metadata": additional_metadata or {}
            }
            
            result = await curator.register_service(
                service_instance=self,
                service_metadata=registration_data
            )
            success = result.get("success", False)
            
            if success:
                self.logger.info(f"✅ Registered {self.service_name} with Curator (Phase 2 pattern - Smart City)")
                self.logger.debug(f"   Capabilities: {len(capabilities)}")
                self.logger.debug(f"   SOA APIs: {len(soa_apis)}")
                self.logger.debug(f"   MCP Tools: {len(mcp_tools)}")
                if protocols:
                    self.logger.debug(f"   Protocols: {len(protocols)}")
            else:
                self.logger.warning(f"⚠️ Failed to register {self.service_name} with Curator")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Curator registration failed: {e}")
            return False