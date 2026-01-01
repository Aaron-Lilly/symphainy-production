#!/usr/bin/env python3
"""
Frontend Gateway Builder - SDK Builder for Frontend Gateway

Creates Frontend Gateway instances for realms using the Experience SDK.
"""

from typing import Dict, Any, Optional

# Import FrontendGatewayService from Experience Foundation
from foundations.experience_foundation.services.frontend_gateway_service.frontend_gateway_service import FrontendGatewayService


class FrontendGatewayBuilder:
    """
    Frontend Gateway Builder - SDK Builder for Frontend Gateway
    
    Creates Frontend Gateway instances for realms.
    Wraps the existing FrontendGatewayService with realm-specific configuration.
    """
    
    def __init__(
        self,
        realm_name: str,
        config: Dict[str, Any],
        di_container: Any,
        platform_gateway: Any,
        public_works_foundation: Optional[Any] = None,
        curator_foundation: Optional[Any] = None
    ):
        """
        Initialize Frontend Gateway Builder.
        
        Args:
            realm_name: Name of realm creating the gateway
            config: Gateway configuration
                - composes: List of orchestrators/services to compose (e.g., ["content_analysis", "insights"])
                - api_prefix: API prefix (e.g., "/api/mvp")
                - transforms: Response transformation config
                - journey_type: Optional journey type (e.g., "mvp")
            di_container: DI Container
            platform_gateway: Platform Infrastructure Gateway
            public_works_foundation: Public Works Foundation (optional)
            curator_foundation: Curator Foundation (optional)
        """
        self.realm_name = realm_name
        self.config = config
        self.di_container = di_container
        self.platform_gateway = platform_gateway
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        if not di_container:
            raise ValueError("DI Container is required for FrontendGatewayBuilder initialization")
        self.logger = di_container.get_logger(f"FrontendGatewayBuilder.{realm_name}")
        
        # Gateway instance (will be created in initialize)
        self.gateway: Optional[FrontendGatewayService] = None
    
    def _get_telemetry(self):
        """Get telemetry utility from DI container."""
        try:
            if hasattr(self.di_container, 'get_telemetry'):
                return self.di_container.get_telemetry()
            return None
        except Exception:
            return None
    
    def _get_error_handler(self):
        """Get error handler utility from DI container."""
        try:
            if hasattr(self.di_container, 'get_error_handler'):
                return self.di_container.get_error_handler()
            return None
        except Exception:
            return None
    
    def _get_security(self):
        """Get security utility from DI container."""
        try:
            if hasattr(self.di_container, 'get_security'):
                return self.di_container.get_security()
            return None
        except Exception:
            return None
    
    def _get_tenant(self):
        """Get tenant utility from DI container."""
        try:
            if hasattr(self.di_container, 'get_utility'):
                return self.di_container.get_utility("tenant")
            return None
        except Exception:
            return None
    
    async def _log_operation_with_telemetry(self, operation: str, success: bool = True):
        """Log operation with telemetry."""
        try:
            telemetry = self._get_telemetry()
            if telemetry:
                await telemetry.record_operation_event(f"operation_{operation}", {"success": success})
        except Exception:
            pass  # Telemetry is optional
    
    async def _record_health_metric(self, metric_name: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record health metric."""
        try:
            telemetry = self._get_telemetry()
            if telemetry:
                tags = {k: str(v) for k, v in (metadata or {}).items() if isinstance(v, (str, int, float, bool))}
                await telemetry.record_metric(metric_name, value, tags)
        except Exception:
            pass  # Telemetry is optional
    
    async def _handle_error_with_audit(self, error: Exception, operation: str):
        """Handle error with audit."""
        try:
            error_handler = self._get_error_handler()
            if error_handler:
                await error_handler.handle_error(error, {"operation": operation, "builder": "FrontendGatewayBuilder"})
        except Exception:
            pass  # Error handler is optional
    
    async def initialize(self) -> bool:
        """
        Initialize Frontend Gateway instance.
        
        Returns:
            bool: True if initialized successfully
        """
        try:
            # Start telemetry tracking
            await self._log_operation_with_telemetry("frontend_gateway_builder_initialize_start", success=True)
            
            self.logger.info(f"🔧 Initializing Frontend Gateway for realm: {self.realm_name}")
            
            # Create FrontendGatewayService instance
            service_name = f"{self.realm_name}_frontend_gateway"
            self.gateway = FrontendGatewayService(
                service_name=service_name,
                realm_name=self.realm_name,
                platform_gateway=self.platform_gateway,
                di_container=self.di_container
            )
            
            # Initialize the gateway
            success = await self.gateway.initialize()
            
            if success:
                self.logger.info(f"✅ Frontend Gateway initialized for realm: {self.realm_name}")
                # Record success metric
                await self._record_health_metric("frontend_gateway_builder_initialize_success", 1.0, {"realm_name": self.realm_name})
            else:
                self.logger.error(f"❌ Frontend Gateway initialization failed for realm: {self.realm_name}")
                await self._log_operation_with_telemetry("frontend_gateway_builder_initialize_complete", success=False)
            
            # End telemetry tracking
            await self._log_operation_with_telemetry("frontend_gateway_builder_initialize_complete", success=success)
            
            return success
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._handle_error_with_audit(e, "frontend_gateway_builder_initialize")
            self.logger.error(f"❌ Frontend Gateway Builder initialization failed: {e}", exc_info=True)
            await self._log_operation_with_telemetry("frontend_gateway_builder_initialize_complete", success=False)
            return False
    
    async def route_request(self, request: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route frontend request through the gateway.
        
        Args:
            request: Frontend request data
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Frontend-ready response
        """
        try:
            # Start telemetry tracking
            await self._log_operation_with_telemetry("route_request_start", success=True)
            
            if not self.gateway:
                raise RuntimeError("Frontend Gateway not initialized")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self._get_security()
                if security:
                    request_id = request.get("request_id", "unknown")
                    if not await security.check_permissions(user_context, request_id, "read"):
                        await self._record_health_metric("route_request_access_denied", 1.0, {"request_id": request_id})
                        await self._log_operation_with_telemetry("route_request_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            result = await self.gateway.route_frontend_request(request)
            
            # Record success metric
            await self._record_health_metric("route_request_success", 1.0, {})
            
            # End telemetry tracking
            await self._log_operation_with_telemetry("route_request_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._handle_error_with_audit(e, "route_request")
            self.logger.error(f"❌ Failed to route request: {e}", exc_info=True)
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def expose_api(
        self,
        api_name: str,
        endpoint: str,
        handler: Any,
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Expose a frontend API endpoint.
        
        Args:
            api_name: Name of the API
            endpoint: API endpoint path
            handler: Handler function for the API
            user_context: Optional user context for security and tenant validation
        
        Returns:
            bool: True if API exposed successfully
        """
        try:
            # Start telemetry tracking
            await self._log_operation_with_telemetry("expose_api_start", success=True)
            
            if not self.gateway:
                raise RuntimeError("Frontend Gateway not initialized")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self._get_security()
                if security:
                    if not await security.check_permissions(user_context, api_name, "write"):
                        await self._record_health_metric("expose_api_access_denied", 1.0, {"api_name": api_name})
                        await self._log_operation_with_telemetry("expose_api_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self._get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self._record_health_metric("expose_api_tenant_denied", 1.0, {"api_name": api_name, "tenant_id": tenant_id})
                            await self._log_operation_with_telemetry("expose_api_complete", success=False)
                            return False
            
            result = await self.gateway.expose_frontend_api(api_name, endpoint, handler)
            
            # Record success metric
            await self._record_health_metric("expose_api_success", 1.0, {"api_name": api_name})
            
            # End telemetry tracking
            await self._log_operation_with_telemetry("expose_api_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._handle_error_with_audit(e, "expose_api")
            self.logger.error(f"❌ Failed to expose API: {e}", exc_info=True)
            return False
    
    def get_gateway(self, user_context: Optional[Dict[str, Any]] = None) -> FrontendGatewayService:
        """
        Get the gateway instance.
        
        Args:
            user_context: Optional user context for security validation
        
        Returns:
            FrontendGatewayService instance
        """
        try:
            # Note: Security validation could be added here if needed
            # For now, this is a simple getter that returns the instance
            if not self.gateway:
                raise RuntimeError("Frontend Gateway not initialized")
            
            return self.gateway
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get gateway: {e}", exc_info=True)
            raise

