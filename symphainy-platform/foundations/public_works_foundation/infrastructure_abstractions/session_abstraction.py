"""
Session Abstraction - Infrastructure abstraction for session management

Coordinates session adapters and handles infrastructure-level concerns like
error handling, retries, logging, and adapter selection.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.session_protocol import (
    SessionProtocol, SessionContext, Session, SessionToken, SessionAnalytics,
    SessionStatus, SessionType, SecurityLevel
)
from foundations.public_works_foundation.infrastructure_adapters.redis_session_adapter import RedisSessionAdapter
# InMemorySessionAdapter was archived - using RedisSessionAdapter via DI only

class SessionAbstraction:
    """
    Session Abstraction - Infrastructure abstraction for session management
    
    Coordinates different session adapters and handles infrastructure-level concerns.
    This layer provides swappable session management engines and infrastructure coordination.
    """
    
    def __init__(self, 
                 session_adapter: SessionProtocol,  # Required: Accept session adapter via DI
                 config_adapter=None,
                 service_name: str = "session_abstraction",
                 di_container=None):
        """
        Initialize Session Abstraction with dependency injection.
        
        Args:
            session_adapter: Session adapter implementing SessionProtocol (required)
            config_adapter: Optional configuration adapter
            service_name: Service name for logging
            di_container: DI Container for logging (required)
        """
        if not di_container:
            raise ValueError("DI Container is required for SessionAbstraction initialization")
        
        self.di_container = di_container
        self.service_name = service_name
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(service_name)
        self.config_adapter = config_adapter
        
        # Use injected session adapter (no internal creation)
        if not session_adapter:
            raise ValueError("SessionAbstraction requires session_adapter via dependency injection")
        
        self.adapter = session_adapter
        self.adapter_type = getattr(session_adapter, 'adapter_type', 'unknown')
        
        # Infrastructure-level configuration
        self.max_retries = 3
        self.retry_delay = 0.1
        self.timeout = 30
        
        self.logger.info(f"✅ Session Abstraction initialized with injected adapter (type: {self.adapter_type})")
    
    async def create_session(self, 
                           context: SessionContext,
                           session_data: Optional[Dict[str, Any]] = None) -> Session:
        """Create a new session with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Creating session with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Extract session_data from context metadata if not provided
            if session_data is None:
                session_data = enhanced_context.metadata.get("session_data", {})
                # If still None, extract from context metadata directly
                if not session_data:
                    session_data = {
                        "user_id": enhanced_context.metadata.get("user_id"),
                        "session_id": enhanced_context.metadata.get("session_id"),
                        "session_type": enhanced_context.metadata.get("session_type", "user"),
                        "context": enhanced_context.metadata.get("context", {}),
                        "metadata": enhanced_context.metadata
                    }
            
            # Create session with retry logic
            result = await self._execute_with_retry(
                self.adapter.create_session,
                enhanced_context,
                session_data
            )
            
            # Add infrastructure-level metadata
            enhanced_metadata = result.metadata or {}
            enhanced_metadata.update({
                "adapter_type": self.adapter_type,
                "abstraction_layer": "session_abstraction",
                "created_at": datetime.utcnow().isoformat()
            })
            
            # Create new session with enhanced metadata
            result = Session(
                session_id=result.session_id,
                user_id=result.user_id,
                agent_id=result.agent_id,
                session_type=result.session_type,
                status=result.status,
                created_at=result.created_at,
                expires_at=result.expires_at,
                last_accessed=result.last_accessed,
                security_level=result.security_level,
                metadata=enhanced_metadata,
                tags=result.tags
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Session creation failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_session(self, 
                         session_id: str,
                         context: SessionContext = None) -> Optional[Session]:
        """Get session with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Get session with retry logic
            result = await self._execute_with_retry(
                self.adapter.get_session,
                session_id,
                enhanced_context
            )
            
            # Add infrastructure-level metadata if session exists
            if result:
                enhanced_metadata = result.metadata or {}
                enhanced_metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "session_abstraction",
                    "retrieved_at": datetime.utcnow().isoformat()
                })
                
                # Create new session with enhanced metadata
                result = Session(
                    session_id=result.session_id,
                    user_id=result.user_id,
                    agent_id=result.agent_id,
                    session_type=result.session_type,
                    status=result.status,
                    created_at=result.created_at,
                    expires_at=result.expires_at,
                    last_accessed=result.last_accessed,
                    security_level=result.security_level,
                    metadata=enhanced_metadata,
                    tags=result.tags
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_session(self,
                           session_id: str,
                           updates: Dict[str, Any],
                           context: SessionContext = None) -> Optional[Session]:
        """Update session with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Updating session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Update session with retry logic
            result = await self._execute_with_retry(
                self.adapter.update_session,
                session_id,
                updates,
                enhanced_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def delete_session(self,
                           session_id: str,
                           context: SessionContext = None) -> bool:
        """Delete session with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Deleting session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Delete session with retry logic
            result = await self._execute_with_retry(
                self.adapter.delete_session,
                session_id,
                enhanced_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to delete session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def validate_session(self,
                             session_id: str,
                             context: SessionContext = None) -> bool:
        """Validate session with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Validating session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Validate session with retry logic
            result = await self._execute_with_retry(
                self.adapter.validate_session,
                session_id,
                enhanced_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def refresh_session(self,
                            session_id: str,
                            context: SessionContext = None) -> Optional[Session]:
        """Refresh session with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Refreshing session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Refresh session with retry logic
            result = await self._execute_with_retry(
                self.adapter.refresh_session,
                session_id,
                enhanced_context
            )
            
            # Add infrastructure-level metadata if session exists
            if result:
                enhanced_metadata = result.metadata or {}
                enhanced_metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "session_abstraction",
                    "refreshed_at": datetime.utcnow().isoformat()
                })
                
                # Create new session with enhanced metadata
                result = Session(
                    session_id=result.session_id,
                    user_id=result.user_id,
                    agent_id=result.agent_id,
                    session_type=result.session_type,
                    status=result.status,
                    created_at=result.created_at,
                    expires_at=result.expires_at,
                    last_accessed=result.last_accessed,
                    security_level=result.security_level,
                    metadata=enhanced_metadata,
                    tags=result.tags
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to refresh session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def revoke_session(self,
                           session_id: str,
                           context: SessionContext = None) -> bool:
        """Revoke session with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Revoking session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Revoke session with retry logic
            result = await self._execute_with_retry(
                self.adapter.revoke_session,
                session_id,
                enhanced_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to revoke session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def list_sessions(self,
                          context: SessionContext) -> List[Session]:
        """List sessions with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Listing sessions with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # List sessions with retry logic
            results = await self._execute_with_retry(
                self.adapter.list_sessions,
                enhanced_context,
                filters
            )
            
            # Add infrastructure-level metadata to all sessions
            enhanced_results = []
            for result in results:
                enhanced_metadata = result.metadata or {}
                enhanced_metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "session_abstraction",
                    "listed_at": datetime.utcnow().isoformat()
                })
                
                # Create new session with enhanced metadata
                enhanced_result = Session(
                    session_id=result.session_id,
                    user_id=result.user_id,
                    agent_id=result.agent_id,
                    session_type=result.session_type,
                    status=result.status,
                    created_at=result.created_at,
                    expires_at=result.expires_at,
                    last_accessed=result.last_accessed,
                    security_level=result.security_level,
                    metadata=enhanced_metadata,
                    tags=result.tags
                )
                enhanced_results.append(enhanced_result)
            
            return enhanced_results
            
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
            raise  # Re-raise for service layer to handle
    
    async def create_session_token(self,
                                 session_id: str,
                                 token_type: str,
                                 context: SessionContext = None) -> Optional[SessionToken]:
        """Create session token with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Creating token for session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Create token with retry logic
            result = await self._execute_with_retry(
                self.adapter.create_session_token,
                session_id,
                token_type,
                enhanced_context
            )
            
            # Add infrastructure-level metadata
            enhanced_metadata = result.metadata or {}
            enhanced_metadata.update({
                "adapter_type": self.adapter_type,
                "abstraction_layer": "session_abstraction",
                "created_at": datetime.utcnow().isoformat()
            })
            
            # Add metadata to existing token
            result.metadata = enhanced_metadata
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to create token for session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def validate_session_token(self, 
                                   token_value: str,
                                   context: SessionContext = None) -> Optional[Session]:
        """Validate session token with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Validating token with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Validate token with retry logic
            result = await self._execute_with_retry(
                self.adapter.validate_session_token,
                token_value,
                enhanced_context
            )
            
            # Add infrastructure-level metadata if session exists
            if result:
                enhanced_metadata = result.metadata or {}
                enhanced_metadata.update({
                    "adapter_type": self.adapter_type,
                    "abstraction_layer": "session_abstraction",
                    "validated_at": datetime.utcnow().isoformat()
                })
                
                # Create new session with enhanced metadata
                result = Session(
                    session_id=result.session_id,
                    user_id=result.user_id,
                    agent_id=result.agent_id,
                    session_type=result.session_type,
                    status=result.status,
                    created_at=result.created_at,
                    expires_at=result.expires_at,
                    last_accessed=result.last_accessed,
                    security_level=result.security_level,
                    metadata=enhanced_metadata,
                    tags=result.tags
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate token: {e}")
            raise  # Re-raise for service layer to handle
    
    async def revoke_session_token(self,
                                 token_id: str,
                                 context: SessionContext = None) -> bool:
        """Revoke session token with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Revoking token {token_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Revoke token with retry logic
            result = await self._execute_with_retry(
                self.adapter.revoke_session_token,
                token_id,
                enhanced_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to revoke token {token_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_session_analytics(self,
                                   session_id: str,
                                   context: SessionContext = None) -> Dict[str, Any]:
        """Get session analytics with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting analytics for session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Get analytics with retry logic
            result = await self._execute_with_retry(
                self.adapter.get_session_analytics,
                session_id,
                enhanced_context
            )
            
            # Add infrastructure-level metadata
            enhanced_metadata = result.metadata or {}
            enhanced_metadata.update({
                "adapter_type": self.adapter_type,
                "abstraction_layer": "session_abstraction",
                "retrieved_at": datetime.utcnow().isoformat()
            })
            
            # Add metadata to existing analytics
            result.metadata = enhanced_metadata
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get analytics for session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_session_analytics(self,
                                     session_id: str,
                                     analytics_data: Dict[str, Any],
                                     context: SessionContext = None) -> bool:
        """Update session analytics with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Updating analytics for session {session_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_context(context)
            
            # Update analytics with retry logic
            result = await self._execute_with_retry(
                self.adapter.update_session_analytics,
                session_id,
                analytics_data,
                enhanced_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to update analytics for session {session_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def health_check(self) -> Dict[str, Any]:
        """Check session infrastructure health."""
        try:
            self.logger.debug("Checking session infrastructure health")
            
            # Check adapter health
            adapter_health = await self.adapter.health_check()
            
            # Add abstraction-level health info
            return {
                "status": "healthy" if adapter_health.get("status") == "healthy" else "unhealthy",
                "abstraction_layer": "session_abstraction",
                "adapter_type": self.adapter_type,
                "adapter_health": adapter_health,
                "infrastructure_metrics": {
                    "max_retries": self.max_retries,
                    "retry_delay": self.retry_delay,
                    "timeout": self.timeout
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Session infrastructure health check failed: {e}")
    
            raise  # Re-raise for service layer to handle
    
    async def switch_adapter(self, new_adapter: SessionProtocol) -> bool:
        """
        Switch to a different session adapter.
        
        Args:
            new_adapter: New session adapter to use (must implement SessionProtocol)
        
        Returns:
            bool: Success status
        """
        try:
            if not new_adapter:
                raise ValueError("New adapter is required")
            
            self.logger.info(f"Switching from {self.adapter_type} to new adapter")
            
            # Test new adapter
            health = await new_adapter.health_check()
            if health.get("status") != "healthy":
                self.logger.error(f"New adapter is not healthy: {health}")
            
            # Switch adapters
            old_adapter = self.adapter
            self.adapter = new_adapter
            self.adapter_type = getattr(new_adapter, 'adapter_type', 'unknown')
            
            self.logger.info(f"✅ Successfully switched to new adapter (type: {self.adapter_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to switch adapter: {e}")
            raise  # Re-raise for service layer to handle
    
    def _enhance_context(self, context: SessionContext) -> SessionContext:
        """Add infrastructure-level context enhancements."""
        # Add infrastructure metadata
        enhanced_metadata = context.metadata or {}
        enhanced_metadata.update({
            "abstraction_layer": "session_abstraction",
            "adapter_type": self.adapter_type,
            "operation_timestamp": datetime.utcnow().isoformat()
        })
        
        # Create enhanced context
        return SessionContext(
            service_id=context.service_id,
            agent_id=context.agent_id,
            tenant_id=context.tenant_id,
            environment=context.environment,
            region=context.region,
            metadata=enhanced_metadata
        )
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                self.logger.error(f"All {self.max_retries + 1} attempts failed")
        
                raise  # Re-raise for service layer to handle
