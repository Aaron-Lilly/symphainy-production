#!/usr/bin/env python3
"""
User Experience Builder - SDK Builder for User Experience

Creates User Experience instances for realms using the Experience SDK.
"""

from typing import Dict, Any, Optional

# Import UserExperienceService from Experience Foundation
from foundations.experience_foundation.services.user_experience_service.user_experience_service import UserExperienceService


class UserExperienceBuilder:
    """
    User Experience Builder - SDK Builder for User Experience
    
    Creates User Experience instances for realms.
    Wraps the existing UserExperienceService with realm-specific configuration.
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
        Initialize User Experience Builder.
        
        Args:
            realm_name: Name of realm creating the user experience service
            config: User experience configuration
                - personalization_enabled: Enable personalization (default: True)
                - analytics_enabled: Enable UX analytics (default: True)
                - preference_storage: Backend for preferences ("librarian", "data_steward")
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
            raise ValueError("DI Container is required for UserExperienceBuilder initialization")
        self.logger = di_container.get_logger(f"UserExperienceBuilder.{realm_name}")
        
        # User experience instance (will be created in initialize)
        self.user_experience: Optional[UserExperienceService] = None
    
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
                await error_handler.handle_error(error, {"operation": operation, "builder": "UserExperienceBuilder"})
        except Exception:
            pass  # Error handler is optional
    
    async def initialize(self) -> bool:
        """
        Initialize User Experience instance.
        
        Returns:
            bool: True if initialized successfully
        """
        try:
            # Start telemetry tracking
            await self._log_operation_with_telemetry("user_experience_builder_initialize_start", success=True)
            
            self.logger.info(f"🔧 Initializing User Experience for realm: {self.realm_name}")
            
            # Create UserExperienceService instance
            service_name = f"{self.realm_name}_user_experience"
            self.user_experience = UserExperienceService(
                service_name=service_name,
                realm_name=self.realm_name,
                platform_gateway=self.platform_gateway,
                di_container=self.di_container
            )
            
            # Initialize the user experience
            success = await self.user_experience.initialize()
            
            if success:
                self.logger.info(f"✅ User Experience initialized for realm: {self.realm_name}")
                # Record success metric
                await self._record_health_metric("user_experience_builder_initialize_success", 1.0, {"realm_name": self.realm_name})
            else:
                self.logger.error(f"❌ User Experience initialization failed for realm: {self.realm_name}")
                await self._log_operation_with_telemetry("user_experience_builder_initialize_complete", success=False)
            
            # End telemetry tracking
            await self._log_operation_with_telemetry("user_experience_builder_initialize_complete", success=success)
            
            return success
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._handle_error_with_audit(e, "user_experience_builder_initialize")
            self.logger.error(f"❌ User Experience Builder initialization failed: {e}", exc_info=True)
            await self._log_operation_with_telemetry("user_experience_builder_initialize_complete", success=False)
            return False
    
    async def personalize_experience(
        self,
        user_id: str,
        context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Personalize user experience based on preferences and context.
        
        Args:
            user_id: User ID
            context: Context data (data_id, page, action, etc.)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Personalized experience configuration
        """
        try:
            # Start telemetry tracking
            await self._log_operation_with_telemetry("personalize_experience_start", success=True)
            
            if not self.user_experience:
                raise RuntimeError("User Experience not initialized")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self._get_security()
                if security:
                    if not await security.check_permissions(user_context, user_id, "read"):
                        await self._record_health_metric("personalize_experience_access_denied", 1.0, {"user_id": user_id})
                        await self._log_operation_with_telemetry("personalize_experience_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self._get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self._record_health_metric("personalize_experience_tenant_denied", 1.0, {"user_id": user_id, "tenant_id": tenant_id})
                            await self._log_operation_with_telemetry("personalize_experience_complete", success=False)
                            return {"success": False, "error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
            
            result = await self.user_experience.personalize_experience(user_id, context)
            
            # Record success metric
            await self._record_health_metric("personalize_experience_success", 1.0, {"user_id": user_id})
            
            # End telemetry tracking
            await self._log_operation_with_telemetry("personalize_experience_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._handle_error_with_audit(e, "personalize_experience")
            self.logger.error(f"❌ Failed to personalize experience: {e}", exc_info=True)
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    async def get_user_preferences(self, user_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Args:
            user_id: User ID
            user_context: Optional user context for security and tenant validation
        
        Returns:
            User preferences
        """
        try:
            # Start telemetry tracking
            await self._log_operation_with_telemetry("get_user_preferences_start", success=True)
            
            if not self.user_experience:
                raise RuntimeError("User Experience not initialized")
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self._get_security()
                if security:
                    if not await security.check_permissions(user_context, user_id, "read"):
                        await self._record_health_metric("get_user_preferences_access_denied", 1.0, {"user_id": user_id})
                        await self._log_operation_with_telemetry("get_user_preferences_complete", success=False)
                        return {"success": False, "error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            result = await self.user_experience.get_user_preferences(user_id)
            
            # Record success metric
            await self._record_health_metric("get_user_preferences_success", 1.0, {"user_id": user_id})
            
            # End telemetry tracking
            await self._log_operation_with_telemetry("get_user_preferences_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self._handle_error_with_audit(e, "get_user_preferences")
            self.logger.error(f"❌ Failed to get user preferences: {e}", exc_info=True)
            return {"success": False, "error": str(e), "error_code": type(e).__name__}
    
    def get_user_experience(self, user_context: Optional[Dict[str, Any]] = None) -> UserExperienceService:
        """
        Get the user experience instance.
        
        Args:
            user_context: Optional user context for security validation
        
        Returns:
            UserExperienceService instance
        """
        try:
            # Note: Security validation could be added here if needed
            # For now, this is a simple getter that returns the instance
            if not self.user_experience:
                raise RuntimeError("User Experience not initialized")
            
            return self.user_experience
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user experience: {e}", exc_info=True)
            raise

