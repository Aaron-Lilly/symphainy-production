#!/usr/bin/env python3
"""
Smart City Foundation Gateway - Platform Capabilities Gateway

Stateless, public API surface exposing Public Works Foundation abstractions
and Smart City role capabilities to all realms.

WHAT (Gateway Role): I expose platform capabilities as APIs to all realms
HOW (Gateway Implementation): I provide direct proxy to Public Works abstractions and Smart City role APIs

Based on CTO's architectural guidance for Sprint 1.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import actual foundation services
from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService

# Import Smart City role base
from bases.smart_city_role_base import SmartCityRoleBase


class SmartCityFoundationGateway(SmartCityRoleBase):
    """
    Smart City Foundation Gateway - Platform Capabilities Gateway
    
    Stateless, public API surface exposing Public Works Foundation abstractions
    and Smart City role capabilities to all realms. This is the "cheat gateway"
    that directly proxies Public Works abstractions for efficient access.
    
    WHAT (Gateway Role): I expose platform capabilities as APIs to all realms
    HOW (Gateway Implementation): I provide direct proxy to Public Works abstractions and Smart City role APIs
    """
    
    def __init__(self, di_container: DIContainerService):
        """Initialize Smart City Foundation Gateway."""
        super().__init__(di_container, "SmartCityFoundationGateway")
        
        # Smart City role APIs (will be populated during initialization)
        self.role_apis = {}
        
        self.logger.info("✅ Smart City Foundation Gateway initialized")
    
    async def initialize(self) -> bool:
        """Initialize the Smart City Foundation Gateway."""
        try:
            self.logger.info("🚀 Initializing Smart City Foundation Gateway...")
            
            # Initialize role APIs
            await self._initialize_role_apis()
            
            # Register gateway capabilities with Curator
            await self._register_gateway_capabilities()
            
            self.is_initialized = True
            self.logger.info("✅ Smart City Foundation Gateway initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Smart City Foundation Gateway: {e}")
            return False
    
    async def _initialize_role_apis(self):
        """Initialize Smart City role APIs."""
        try:
            # Get Smart City role services from DI Container (using actual method)
            role_services = [
                "LibrarianService",
                "DataStewardService", 
                "SecurityGuardService",
                "TrafficCopService",
                "NurseService",
                "ConductorService",
                "CityManagerService",
                "PostOfficeService"
            ]
            
            for role_name in role_services:
                try:
                    # Use actual DI Container method
                    role_service = self.di_container.get_foundation_service(role_name)
                    if role_service:
                        # Extract role name from service name (e.g., "LibrarianService" -> "librarian")
                        api_name = role_name.lower().replace("service", "")
                        self.role_apis[api_name] = role_service
                        self.logger.info(f"✅ Registered {api_name} API")
                    else:
                        self.logger.warning(f"⚠️ {role_name} not found in DI Container")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to register {role_name}: {e}")
            
            self.logger.info(f"✅ Initialized {len(self.role_apis)} role APIs")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize role APIs: {e}")
            raise
    
    async def _register_gateway_capabilities(self):
        """Register gateway capabilities with Curator."""
        try:
            capabilities = {
                "service_name": "SmartCityFoundationGateway",
                "service_type": "platform_gateway",
                "capabilities": {
                    "infrastructure_abstractions": [
                        "auth", "authorization", "session", "tenant",
                        "file_management", "content_metadata", "llm", "mcp", "agui",
                        "policy", "tool_storage", "config"
                    ],
                    "smart_city_roles": list(self.role_apis.keys()),
                    "communication_gateway": "post_office"
                },
                "access_pattern": "api_via_smart_city_gateway",
                "version": "1.0"
            }
            
            await self.register_with_curator(capabilities)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register gateway capabilities: {e}")
            raise
    
    # ============================================================================
    # INFRASTRUCTURE ABSTRACTION METHODS (Direct Proxy to Public Works)
    # Based on ACTUAL Public Works Foundation methods
    # ============================================================================
    
    def get_abstraction(self, name: str) -> Any:
        """
        Get infrastructure abstraction from Public Works Foundation.
        This is the "cheat gateway" method that directly proxies Public Works abstractions.
        Based on ACTUAL Public Works Foundation methods.
        """
        try:
            # Map abstraction names to actual Public Works Foundation methods
            abstraction_methods = {
                "auth": "get_auth_abstraction",
                "authorization": "get_authorization_abstraction", 
                "session": "get_session_abstraction",
                "tenant": "get_tenant_abstraction",
                "file_management": "get_file_management_abstraction",
                "content_metadata": "get_content_metadata_abstraction",
                "content_schema": "get_content_schema_abstraction",
                "content_insights": "get_content_insights_abstraction",
                "llm": "get_llm_abstraction",
                "mcp": "get_mcp_abstraction",
                "agui": "get_agui_abstraction",
                "policy": "get_policy_abstraction",
                "tool_storage": "get_tool_storage_abstraction"
            }
            
            if name not in abstraction_methods:
                self.logger.error(f"❌ Abstraction '{name}' not supported. Available: {list(abstraction_methods.keys())}")
                raise ValueError(f"Abstraction '{name}' not supported")
            
            # Get the actual method name
            method_name = abstraction_methods[name]
            
            # Call the actual Public Works Foundation method
            if hasattr(self.public_works_foundation, method_name):
                abstraction = getattr(self.public_works_foundation, method_name)()
                self.logger.debug(f"✅ Retrieved {name} abstraction via gateway using {method_name}")
                return abstraction
            else:
                self.logger.error(f"❌ Method '{method_name}' not found in Public Works Foundation")
                raise ValueError(f"Method '{method_name}' not found")
        except Exception as e:
            self.logger.error(f"❌ Failed to get {name} abstraction: {e}")
            raise
    
    # ============================================================================
    # DIRECT ABSTRACTION METHODS (Based on ACTUAL Public Works Foundation)
    # ============================================================================
    
    def get_auth_abstraction(self) -> Any:
        """Get auth abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_auth_abstraction()
    
    def get_authorization_abstraction(self) -> Any:
        """Get authorization abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_authorization_abstraction()
    
    def get_session_abstraction(self) -> Any:
        """Get session abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_session_abstraction()
    
    def get_tenant_abstraction(self) -> Any:
        """Get tenant abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_tenant_abstraction()
    
    def get_file_management_abstraction(self) -> Any:
        """Get file management abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_file_management_abstraction()
    
    def get_file_management_composition(self) -> Any:
        """Get file management composition service via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_file_management_composition()
    
    def get_content_metadata_abstraction(self) -> Any:
        """Get content metadata abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_content_metadata_abstraction()
    
    def get_content_schema_abstraction(self) -> Any:
        """Get content schema abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_content_schema_abstraction()
    
    def get_content_insights_abstraction(self) -> Any:
        """Get content insights abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_content_insights_abstraction()
    
    def get_content_metadata_composition(self) -> Any:
        """Get content metadata composition service via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_content_metadata_composition()
    
    def get_content_analysis_composition(self) -> Any:
        """Get content analysis composition service via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_content_analysis_composition()
    
    def get_llm_abstraction(self) -> Any:
        """Get LLM abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_llm_abstraction()
    
    def get_llm_composition_service(self) -> Any:
        """Get LLM composition service via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_llm_composition_service()
    
    def get_mcp_abstraction(self) -> Any:
        """Get MCP abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_mcp_abstraction()
    
    def get_mcp_composition_service(self) -> Any:
        """Get MCP composition service via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_mcp_composition_service()
    
    def get_agui_abstraction(self) -> Any:
        """Get AGUI abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_agui_abstraction()
    
    def get_agui_composition_service(self) -> Any:
        """Get AGUI composition service via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_agui_composition_service()
    
    def get_policy_abstraction(self) -> Any:
        """Get policy abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_policy_abstraction()
    
    def get_policy_composition_service(self) -> Any:
        """Get policy composition service via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_policy_composition_service()
    
    def get_tool_storage_abstraction(self) -> Any:
        """Get tool storage abstraction via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_tool_storage_abstraction()
    
    def get_policy_engine(self, engine_name: str = "default") -> Any:
        """Get policy engine via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_policy_engine(engine_name)
    
    def get_config_adapter(self) -> Any:
        """Get configuration adapter via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_config_adapter()
    
    def get_agentic_abstractions(self) -> Dict[str, Any]:
        """Get all agentic abstractions via gateway (ACTUAL method)."""
        return self.public_works_foundation.get_agentic_abstractions()
    
    # ============================================================================
    # SMART CITY ROLE API METHODS
    # ============================================================================
    
    def get_role_api(self, role_name: str) -> Any:
        """Get Smart City role API."""
        try:
            if role_name in self.role_apis:
                return self.role_apis[role_name]
            else:
                self.logger.error(f"❌ Role API '{role_name}' not found")
                raise ValueError(f"Role API '{role_name}' not found")
        except Exception as e:
            self.logger.error(f"❌ Failed to get {role_name} API: {e}")
            raise
    
    def get_librarian_api(self) -> Any:
        """Get Librarian API."""
        return self.get_role_api("librarian")
    
    def get_data_steward_api(self) -> Any:
        """Get Data Steward API."""
        return self.get_role_api("data_steward")
    
    def get_security_guard_api(self) -> Any:
        """Get Security Guard API."""
        return self.get_role_api("security_guard")
    
    def get_traffic_cop_api(self) -> Any:
        """Get Traffic Cop API."""
        return self.get_role_api("traffic_cop")
    
    def get_nurse_api(self) -> Any:
        """Get Nurse API."""
        return self.get_role_api("nurse")
    
    def get_conductor_api(self) -> Any:
        """Get Conductor API."""
        return self.get_role_api("conductor")
    
    def get_city_manager_api(self) -> Any:
        """Get City Manager API."""
        return self.get_role_api("city_manager")
    
    def get_post_office_api(self) -> Any:
        """Get Post Office API."""
        return self.get_role_api("post_office")
    
    # ============================================================================
    # COMMUNICATION GATEWAY METHODS
    # ============================================================================
    
    def get_communication_gateway(self) -> Any:
        """Get Post Office as communication orchestration gateway."""
        return self.get_post_office_api()
    
    # ============================================================================
    # HEALTH CHECK AND MONITORING
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the Smart City Foundation Gateway."""
        try:
            health_status = {
                "service_name": "SmartCityFoundationGateway",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {}
            }
            
            # Check Public Works Foundation
            try:
                if self.public_works_foundation and self.public_works_foundation.is_initialized:
                    health_status["components"]["public_works_foundation"] = "healthy"
                else:
                    health_status["components"]["public_works_foundation"] = "unhealthy"
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["components"]["public_works_foundation"] = f"error: {str(e)}"
                health_status["status"] = "unhealthy"
            
            # Check Communication Foundation
            try:
                if self.communication_foundation:
                    health_status["components"]["communication_foundation"] = "healthy"
                else:
                    health_status["components"]["communication_foundation"] = "unhealthy"
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["components"]["communication_foundation"] = f"error: {str(e)}"
                health_status["status"] = "unhealthy"
            
            # Check Curator Foundation
            try:
                if self.curator_foundation:
                    health_status["components"]["curator_foundation"] = "healthy"
                else:
                    health_status["components"]["curator_foundation"] = "unhealthy"
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["components"]["curator_foundation"] = f"error: {str(e)}"
                health_status["status"] = "unhealthy"
            
            # Check DI Container
            try:
                if self.di_container:
                    health_status["components"]["di_container"] = "healthy"
                else:
                    health_status["components"]["di_container"] = "unhealthy"
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["components"]["di_container"] = f"error: {str(e)}"
                health_status["status"] = "unhealthy"
            
            # Check Role APIs
            health_status["components"]["role_apis"] = {
                "total_registered": len(self.role_apis),
                "registered_roles": list(self.role_apis.keys()),
                "status": "healthy" if len(self.role_apis) > 0 else "no_roles_registered"
            }
            
            # Check abstraction availability
            try:
                available_abstractions = [
                    "auth", "authorization", "session", "tenant",
                    "file_management", "content_metadata", "content_schema", "content_insights",
                    "llm", "mcp", "agui", "policy", "tool_storage"
                ]
                
                abstraction_status = {}
                for abstraction_name in available_abstractions:
                    try:
                        # Test if abstraction is available
                        self.get_abstraction(abstraction_name)
                        abstraction_status[abstraction_name] = "available"
                    except Exception as e:
                        abstraction_status[abstraction_name] = f"error: {str(e)}"
                
                health_status["components"]["abstractions"] = abstraction_status
                
            except Exception as e:
                health_status["components"]["abstractions"] = f"error: {str(e)}"
                health_status["status"] = "unhealthy"
            
            self.logger.info(f"✅ Health check completed: {health_status['status']}")
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return {
                "service_name": "SmartCityFoundationGateway",
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    # ============================================================================
    # SERVICE CAPABILITIES
    # ============================================================================
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities for registration with Curator."""
        return {
            "service_name": "SmartCityFoundationGateway",
            "service_type": "platform_gateway",
            "capabilities": {
                "infrastructure_abstractions": [
                    "auth", "authorization", "session", "tenant",
                    "file_management", "content_metadata", "content_schema", "content_insights",
                    "llm", "mcp", "agui", "policy", "tool_storage"
                ],
                "composition_services": [
                    "file_management_composition", "content_metadata_composition", 
                    "content_analysis_composition", "llm_composition_service",
                    "mcp_composition_service", "agui_composition_service",
                    "policy_composition_service"
                ],
                "smart_city_roles": list(self.role_apis.keys()),
                "communication_gateway": "post_office",
                "policy_engines": ["default"],
                "config_adapter": True,
                "agentic_abstractions": True
            },
            "access_pattern": "api_via_smart_city_gateway",
            "version": "1.0",
            "is_initialized": self.is_initialized,
            "health_status": await self.health_check()
        }
