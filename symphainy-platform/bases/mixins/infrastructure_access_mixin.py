#!/usr/bin/env python3
"""
Infrastructure Access Mixin

Focused mixin for infrastructure abstraction access - extracts abstraction getter
functionality from base classes into a reusable, testable component.

WHAT (Infrastructure Access Role): I provide standardized access to infrastructure abstractions
HOW (Infrastructure Access Mixin): I centralize abstraction access patterns with validation
"""

from typing import Dict, Any, Optional


class InfrastructureAccessMixin:
    """
    Mixin for standardized infrastructure abstraction access patterns.
    
    Provides consistent access to infrastructure abstractions through the DI Container
    with proper validation and error handling.
    """
    
    def _init_infrastructure_access(self, di_container: Any, platform_gateway: Any = None):
        """Initialize infrastructure access patterns."""
        if not di_container:
            raise ValueError(
                "DI Container is required for InfrastructureAccessMixin initialization. "
                "Services must be created with a valid DI Container instance."
            )
        
        self.di_container = di_container
        # Set platform_gateway if provided, otherwise try to get it from DI container
        if platform_gateway:
            self.platform_gateway = platform_gateway
        elif hasattr(di_container, 'get_foundation_service'):
            try:
                self.platform_gateway = di_container.get_foundation_service("PlatformInfrastructureGateway")
            except Exception:
                self.platform_gateway = None
        else:
            self.platform_gateway = None
        
        # Get logger from DI Container (should be available - DI Container initializes logging in __init__)
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError(
                f"DI Container does not have get_logger method. "
                f"This indicates a platform initialization failure or incorrect DI Container instance."
            )
        
        try:
            # Use DI Container's get_logger method to create logger for this mixin
            logger_service = di_container.get_logger(f"{self.__class__.__name__}.infrastructure_access")
            if not logger_service:
                raise RuntimeError(
                    f"DI Container.get_logger() returned None. "
                    f"Logging service should be available - this indicates a platform initialization failure."
                )
            # SmartCityLoggingService has .logger attribute and methods like .info(), .error(), etc.
            self.logger = logger_service
        except Exception as e:
            raise RuntimeError(
                f"Failed to get logger from DI Container: {e}. "
                f"DI Container must initialize logging utility before services can use it. "
                f"This indicates a platform initialization failure."
            ) from e
        
        # Infrastructure abstraction cache
        self._abstraction_cache = {}
        
        self.logger.debug("Infrastructure access mixin initialized")
    
    def get_infrastructure_abstraction(self, name: str) -> Any:
        """Get infrastructure abstraction by name with caching."""
        # Logger should be available (set during initialization)
        logger = self.logger if hasattr(self, 'logger') and self.logger else None
        
        if name in self._abstraction_cache:
            if logger:
                logger.debug(f"Returning cached '{name}' abstraction")
            return self._abstraction_cache[name]
        
        try:
            realm_name = getattr(self, 'realm_name', 'unknown')
            role_name = getattr(self, 'role_name', None)
            
            # Smart City services have DIRECT access to Public Works abstractions (first-class citizen privilege)
            # Other realms MUST use Platform Gateway (no direct access allowed)
            if realm_name == "smart_city":
                # Smart City: Direct Public Works access (bypass Platform Gateway)
                if hasattr(self, 'di_container') and self.di_container:
                    try:
                        public_works = self.di_container.get_public_works_foundation()
                        if public_works:
                            abstraction = public_works.get_abstraction(name)
                            if abstraction:
                                self._abstraction_cache[name] = abstraction
                                if logger:
                                    logger.debug(f"✅ Smart City service retrieved '{name}' abstraction directly from Public Works Foundation")
                                return abstraction
                    except Exception as e:
                        if logger:
                            logger.debug(f"Failed to get '{name}' from Public Works Foundation: {e}")
                
                # If direct access failed, raise error (Smart City should always have Public Works)
                raise Exception(f"Smart City service cannot access '{name}' abstraction - Public Works Foundation not available")
            
            # Other realms: MUST use Platform Gateway (no direct access - prevents backdoor)
            # Try Platform Gateway first (for all realms EXCEPT Smart City)
            if hasattr(self, 'platform_gateway') and self.platform_gateway:
                try:
                    # Platform Gateway method signature: get_abstraction(realm_name, abstraction_name)
                    abstraction = self.platform_gateway.get_abstraction(realm_name, name)
                    if abstraction:
                        self._abstraction_cache[name] = abstraction
                        if logger:
                            logger.debug(f"✅ Retrieved '{name}' abstraction via Platform Gateway for realm '{realm_name}'")
                        return abstraction
                except ValueError as e:
                    # Platform Gateway blocked access
                    if logger:
                        logger.debug(f"Platform Gateway blocked '{name}' for realm '{realm_name}': {e}")
                    
                    # Messaging and event_management are Post Office capabilities
                    # Services should use Post Office SOA APIs, not abstractions directly
                    # Only Post Office (Smart City privilege) can access these abstractions
                    if name in ["messaging", "event_management", "event_bus"]:
                        if logger:
                            logger.warning(
                                f"⚠️ '{name}' is a Post Office capability. "
                                f"Services should use Post Office SOA APIs instead of accessing abstractions directly. "
                                f"Only Post Office (Smart City privilege) can access '{name}' abstraction."
                            )
                        raise ValueError(
                            f"'{name}' is a Post Office capability. "
                            f"Use Post Office SOA APIs (e.g., post_office.publish_event(), post_office.send_message()) "
                            f"instead of accessing '{name}' abstraction directly. "
                            f"Only Post Office service can access '{name}' abstraction."
                        )
                    
                    # WebSocket is now in Experience Foundation SDK
                    elif name == "websocket":
                        if logger:
                            logger.info(f"Routing '{name}' to Experience Foundation SDK")
                        
                        if hasattr(self, 'di_container') and self.di_container:
                            try:
                                experience_foundation = self.di_container.get_foundation_service("ExperienceFoundationService")
                                if experience_foundation:
                                    # Get WebSocket SDK from Experience Foundation
                                    # Note: This is async, but we're in a sync method, so we'll need to handle this differently
                                    # For now, we'll raise an error suggesting to use the SDK directly
                                    if logger:
                                        logger.warning(
                                            f"⚠️ WebSocket is now in Experience Foundation SDK. "
                                            f"Use experience_foundation.get_websocket_sdk() instead of accessing abstraction directly."
                                        )
                                    raise ValueError(
                                        f"WebSocket is now in Experience Foundation SDK. "
                                        f"Use experience_foundation.get_websocket_sdk() instead of accessing '{name}' abstraction directly."
                                    )
                                else:
                                    if logger:
                                        logger.warning(f"⚠️ Experience Foundation not available in DI container")
                            except Exception as e2:
                                if logger:
                                    logger.error(f"❌ Error getting '{name}' from Experience Foundation SDK: {e2}")
                    
                    # Re-raise the ValueError for other abstractions
                    raise ValueError(
                        f"Realm '{realm_name}' cannot access '{name}' via Platform Gateway. Original error: {e}"
                    )
            
            # Realm services (non-Smart City): Platform Gateway is required
            # No fallback to direct Public Works access (prevents backdoor)
            raise Exception(f"Platform Gateway not available - realm '{realm_name}' cannot access '{name}' abstraction without Platform Gateway")
            
            self._abstraction_cache[name] = abstraction
            return abstraction
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"Failed to get infrastructure abstraction '{name}': {e}")
            raise
    
    def get_auth_abstraction(self) -> Any:
        """Get authentication abstraction."""
        return self.get_infrastructure_abstraction("auth")
    
    def get_authorization_abstraction(self) -> Any:
        """Get authorization abstraction."""
        return self.get_infrastructure_abstraction("authorization")
    
    def get_session_abstraction(self) -> Any:
        """Get session management abstraction."""
        return self.get_infrastructure_abstraction("session")
    
    def get_tenant_abstraction(self) -> Any:
        """Get tenant management abstraction."""
        return self.get_infrastructure_abstraction("tenant")
    
    def get_file_management_abstraction(self) -> Any:
        """Get file management abstraction."""
        return self.get_infrastructure_abstraction("file_management")
    
    def get_content_metadata_abstraction(self) -> Any:
        """Get content metadata abstraction."""
        return self.get_infrastructure_abstraction("content_metadata")
    
    def get_content_schema_abstraction(self) -> Any:
        """Get content schema abstraction."""
        return self.get_infrastructure_abstraction("content_schema")
    
    def get_content_insights_abstraction(self) -> Any:
        """Get content insights abstraction."""
        return self.get_infrastructure_abstraction("content_insights")
    
    def get_llm_abstraction(self) -> Any:
        """Get LLM abstraction."""
        return self.get_infrastructure_abstraction("llm")
    
    def get_agui_abstraction(self) -> Any:
        """Get AGUI abstraction."""
        return self.get_infrastructure_abstraction("agui")
    
    def get_policy_abstraction(self) -> Any:
        """Get policy abstraction."""
        return self.get_infrastructure_abstraction("policy")
    
    def get_tool_storage_abstraction(self) -> Any:
        """Get tool storage abstraction."""
        return self.get_infrastructure_abstraction("tool_storage")
    
    def get_event_management_abstraction(self) -> Any:
        """
        Get event management abstraction.
        
        ⚠️ WARNING: This abstraction is Post Office's domain.
        Other services should use Post Office SOA APIs (publish_event, subscribe_to_events) instead.
        Only Post Office (Smart City privilege) can access this abstraction directly.
        """
        return self.get_infrastructure_abstraction("event_management")
    
    def get_messaging_abstraction(self) -> Any:
        """
        Get messaging abstraction.
        
        ⚠️ WARNING: This abstraction is Post Office's domain.
        Other services should use Post Office SOA APIs (send_message) instead.
        Only Post Office (Smart City privilege) can access this abstraction directly.
        """
        return self.get_infrastructure_abstraction("messaging")
    
    def get_cache_abstraction(self) -> Any:
        """Get cache abstraction (for content/data caching, NOT messaging)."""
        return self.get_infrastructure_abstraction("cache")
    
    def get_state_management_abstraction(self) -> Any:
        """Get state management abstraction."""
        return self.get_infrastructure_abstraction("state_management")
    
    def get_task_management_abstraction(self) -> Any:
        """Get task management abstraction."""
        return self.get_infrastructure_abstraction("task_management")
    
    def get_workflow_orchestration_abstraction(self) -> Any:
        """Get workflow orchestration abstraction."""
        return self.get_infrastructure_abstraction("workflow_orchestration")
    
    def get_knowledge_discovery_abstraction(self) -> Any:
        """Get knowledge discovery abstraction."""
        return self.get_infrastructure_abstraction("knowledge_discovery")
    
    def get_knowledge_governance_abstraction(self) -> Any:
        """Get knowledge governance abstraction."""
        return self.get_infrastructure_abstraction("knowledge_governance")
    
    def get_resource_allocation_abstraction(self) -> Any:
        """Get resource allocation abstraction."""
        return self.get_infrastructure_abstraction("resource_allocation")
    
    def get_health_monitoring_abstraction(self) -> Any:
        """Get health monitoring abstraction."""
        return self.get_infrastructure_abstraction("health_monitoring")
    
    def get_telemetry_reporting_abstraction(self) -> Any:
        """Get telemetry reporting abstraction."""
        return self.get_infrastructure_abstraction("telemetry_reporting")
    
    def get_telemetry_abstraction(self) -> Any:
        """Get telemetry abstraction (OpenTelemetry + Tempo)."""
        return self.get_infrastructure_abstraction("telemetry")
    
    def get_health_abstraction(self) -> Any:
        """Get health abstraction (OpenTelemetry + Simple Health)."""
        return self.get_infrastructure_abstraction("health")
    
    def get_alert_management_abstraction(self) -> Any:
        """Get alert management abstraction (Redis)."""
        return self.get_infrastructure_abstraction("alert_management")
    
    def get_analytics_abstraction(self) -> Any:
        """Get analytics abstraction (Redis + ArangoDB)."""
        return self.get_infrastructure_abstraction("analytics")
    
    def get_api_gateway_routing_abstraction(self) -> Any:
        """Get API gateway routing abstraction."""
        return self.get_infrastructure_abstraction("api_gateway_routing")
    
    def get_load_balancing_abstraction(self) -> Any:
        """Get load balancing abstraction."""
        return self.get_infrastructure_abstraction("load_balancing")
    
    def get_real_time_communication_abstraction(self) -> Any:
        """Get real-time communication abstraction."""
        return self.get_infrastructure_abstraction("real_time_communication")
    
    def get_streaming_data_abstraction(self) -> Any:
        """Get streaming data abstraction."""
        return self.get_infrastructure_abstraction("streaming_data")
    
    def clear_abstraction_cache(self):
        """Clear abstraction cache (useful for testing)."""
        self._abstraction_cache.clear()
        self.logger.debug("Infrastructure abstraction cache cleared")

