#!/usr/bin/env python3
"""
Experience Manager Service

Main service orchestrator for the Experience Manager, implemented as a Smart City role.
Handles user experience orchestration, frontend-backend integration, and real-time coordination.

WHAT (Smart City Role): I orchestrate user experience across the platform
HOW (Service Implementation): I use micro-modules, MCP server, and cross-dimension coordination
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add the project root to the Python path
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

from utilities import UserContext
from config.environment_loader import EnvironmentLoader

# Import experience protocols and interfaces
from experience.protocols.experience_soa_service_protocol import ExperienceServiceBase, ExperienceServiceType, ExperienceOperationType
from experience.interfaces.experience_manager_interface import IExperienceManager, ExperienceType, SessionStatus

# Import micro-modules
from experience.roles.experience_manager.micro_modules.session_manager import SessionManagerModule
from experience.roles.experience_manager.micro_modules.ui_state_manager import UIStateManagerModule
from experience.roles.experience_manager.micro_modules.real_time_coordinator import RealTimeCoordinatorModule
from experience.roles.experience_manager.micro_modules.frontend_router import FrontendRouterModule

# MCP server will be initialized separately to avoid circular imports


class ExperienceManagerService(ExperienceServiceBase, IExperienceManager):
    """
    Experience Manager Service for user experience orchestration and frontend-backend integration.
    
    Implements the IExperienceManager interface and orchestrates various micro-modules,
    and MCP server to provide comprehensive user experience capabilities.
    """
    
    def __init__(self, utility_foundation=None, curator_foundation=None, 
                 environment: Optional[EnvironmentLoader] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize Experience Manager Service."""
        super().__init__(
            service_name="experience_manager",
            service_type=ExperienceServiceType.EXPERIENCE_MANAGER,
            utility_foundation=utility_foundation,
            curator_foundation=curator_foundation
        )
        
        self.environment = environment or EnvironmentLoader()
        self.logger = logger or logging.getLogger(self.service_name)
        
        # Initialize micro-modules
        self.session_manager = SessionManagerModule(self.environment, self.logger)
        self.ui_state_manager = UIStateManagerModule(self.environment, self.logger)
        self.real_time_coordinator = RealTimeCoordinatorModule(self.environment, self.logger)
        self.frontend_router = FrontendRouterModule(self.environment, self.logger)
        
        # MCP server will be initialized separately
        
        # Initialize supported operations
        self.supported_operations = [
            ExperienceOperationType.SESSION_MANAGEMENT,
            ExperienceOperationType.UI_STATE_MANAGEMENT,
            ExperienceOperationType.REAL_TIME_COORDINATION,
            ExperienceOperationType.FRONTEND_ROUTING
        ]
        
        # Service contract
        self.service_contract = {
            "service_name": self.service_name,
            "service_type": self.service_type.value,
            "supported_operations": [op.value for op in self.supported_operations],
            "capabilities": [
                "session_management",
                "ui_state_management", 
                "real_time_coordination",
                "frontend_routing",
                "pillar_coordination",
                "websocket_management"
            ]
        }
        
        # Active sessions and connections
        self.active_sessions = {}
        self.websocket_connections = {}
        
        self.logger.info(f"🎭 {self.service_name} initialized - Experience Manager")
    
    async def _initialize_service_components(self):
        """Initialize service-specific components."""
        self.logger.info("🚀 Initializing Experience Manager components...")
        
        # Initialize micro-modules
        await self.session_manager.initialize()
        await self.ui_state_manager.initialize()
        await self.real_time_coordinator.initialize()
        await self.frontend_router.initialize()
        
        # MCP server initialization handled separately
        
        self.logger.info("✅ Experience Manager components initialized")
    
    # ============================================================================
    # TENANT ISOLATION METHODS
    # ============================================================================
    
    def _validate_tenant_access(self, user_context: UserContext) -> bool:
        """Validate tenant access for the user context."""
        if not user_context or not user_context.tenant_id:
            self.logger.warning("❌ Tenant access denied: No tenant context")
            return False
        
        # Additional tenant validation can be added here
        # For now, we ensure tenant_id exists
        return True
    
    def _generate_tenant_scoped_id(self, tenant_id: str, resource_type: str) -> str:
        """Generate a tenant-scoped ID for resources."""
        import uuid
        from datetime import datetime
        
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{tenant_id}_{resource_type}_{timestamp}_{unique_id}"
    
    async def _validate_session_tenant_access(self, session_id: str, user_context: UserContext) -> bool:
        """Validate that a session belongs to the tenant."""
        try:
            # This would typically query the database to verify session ownership
            # For now, we check if the session_id contains the tenant_id
            if user_context.tenant_id in session_id:
                return True
            
            # Additional database validation can be added here
            self.logger.warning(f"❌ Session access denied: Session {session_id} does not belong to tenant {user_context.tenant_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error validating session tenant access: {e}")
            return False
    
    # ============================================================================
    # LIAISON AGENT INTEGRATION
    # ============================================================================
    
    async def process_tenant_aware_message(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process chat message with tenant awareness and liaison agent logic."""
        try:
            # Validate tenant access
            if not self._validate_tenant_access(user_context):
                return {
                    "content": "I'm sorry, but I don't have access to your tenant's experience management. Please check your authentication.",
                    "agent_name": "ExperienceManagerLiaisonAgent",
                    "current_pillar": "experience",
                    "suggestions": ["Check authentication", "Contact support"],
                    "tenant_id": None
                }
            
            # Route to appropriate liaison agent method based on message content
            message_lower = message.lower()
            
            if any(keyword in message_lower for keyword in ["session", "start", "initialize", "begin"]):
                return await self._handle_session_guidance(message, user_context, context)
            elif any(keyword in message_lower for keyword in ["ui", "interface", "state", "update"]):
                return await self._handle_ui_guidance(message, user_context, context)
            elif any(keyword in message_lower for keyword in ["real-time", "broadcast", "notification", "update"]):
                return await self._handle_realtime_guidance(message, user_context, context)
            elif any(keyword in message_lower for keyword in ["route", "navigate", "frontend", "page"]):
                return await self._handle_routing_guidance(message, user_context, context)
            else:
                return await self._handle_general_experience_guidance(message, user_context, context)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing liaison agent message: {e}")
            return {
                "content": "I encountered an error processing your request. Please try again.",
                "agent_name": "ExperienceManagerLiaisonAgent",
                "current_pillar": "experience",
                "suggestions": ["Try again", "Contact support"],
                "tenant_id": user_context.tenant_id if user_context else None
            }
    
    async def _handle_session_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on session management."""
        try:
            # Get tenant-specific session capabilities
            tenant_config = await self._get_tenant_config(user_context.tenant_id)
            max_sessions = tenant_config.get("max_sessions_per_user", 10)
            
            return {
                "content": f"I can help you manage your experience sessions! Your tenant allows up to {max_sessions} concurrent sessions. What would you like to do with your sessions?",
                "agent_name": "ExperienceManagerLiaisonAgent",
                "current_pillar": "experience",
                "suggestions": [
                    "Start a new session",
                    "Check active sessions",
                    "Manage session state",
                    "What sessions are available?",
                    "How do I start a session?"
                ],
                "tenant_id": user_context.tenant_id
            }
        except Exception as e:
            self.logger.error(f"❌ Error in session guidance: {e}")
            return {
                "content": "I can help you manage your experience sessions. What would you like to do?",
                "agent_name": "ExperienceManagerLiaisonAgent",
                "current_pillar": "experience",
                "suggestions": ["Start a session", "Check sessions"],
                "tenant_id": user_context.tenant_id
            }
    
    async def _handle_ui_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on UI state management."""
        return {
            "content": "I can help you manage your user interface state! I can synchronize UI state across the platform, update interface elements, and maintain consistent user experience. What would you like to manage?",
            "agent_name": "ExperienceManagerLiaisonAgent",
            "current_pillar": "experience",
            "suggestions": [
                "Update UI state",
                "Synchronize interface",
                "Manage UI components",
                "What UI features are available?",
                "How do I update the interface?"
            ],
            "tenant_id": user_context.tenant_id
        }
    
    async def _handle_realtime_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on real-time coordination."""
        return {
            "content": "I can help you with real-time updates and coordination! I can broadcast updates to specific sessions, coordinate real-time events, and ensure synchronized user experiences. What would you like to coordinate?",
            "agent_name": "ExperienceManagerLiaisonAgent",
            "current_pillar": "experience",
            "suggestions": [
                "Broadcast real-time update",
                "Coordinate events",
                "Sync user experiences",
                "What real-time features are available?",
                "How do I send updates?"
            ],
            "tenant_id": user_context.tenant_id
        }
    
    async def _handle_routing_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on frontend routing."""
        return {
            "content": "I can help you with frontend routing and navigation! I can manage page transitions, handle routing logic, and ensure smooth user navigation across the platform. What would you like to route?",
            "agent_name": "ExperienceManagerLiaisonAgent",
            "current_pillar": "experience",
            "suggestions": [
                "Navigate to page",
                "Handle routing",
                "Manage transitions",
                "What routing features are available?",
                "How do I navigate?"
            ],
            "tenant_id": user_context.tenant_id
        }
    
    async def _handle_general_experience_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general experience management guidance."""
        return {
            "content": "I'm your Experience Manager liaison agent! I can help you manage sessions, coordinate UI state, handle real-time updates, and manage frontend routing. What would you like to do?",
            "agent_name": "ExperienceManagerLiaisonAgent",
            "current_pillar": "experience",
            "suggestions": [
                "Manage sessions",
                "Update UI state",
                "Coordinate real-time updates",
                "Handle routing",
                "What can I do here?"
            ],
            "tenant_id": user_context.tenant_id
        }
    
    async def _get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant-specific configuration."""
        try:
            # This would typically query the database for tenant configuration
            # For now, we'll return a default configuration
            return {
                "max_sessions_per_user": 10,
                "max_ui_states_per_session": 50,
                "max_realtime_updates_per_minute": 100,
                "supported_routing_types": ["page", "component", "modal", "tab"]
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting tenant config: {e}")
            return {
                "max_sessions_per_user": 10,
                "max_ui_states_per_session": 50,
                "max_realtime_updates_per_minute": 100,
                "supported_routing_types": ["page", "component", "modal"]
            }
    
    async def _shutdown_service_components(self):
        """Shutdown service-specific components."""
        self.logger.info("🛑 Shutting down Experience Manager components...")
        
        # Shutdown micro-modules
        await self.session_manager.shutdown()
        await self.ui_state_manager.shutdown()
        await self.real_time_coordinator.shutdown()
        await self.frontend_router.shutdown()
        
        # MCP server shutdown handled separately
        
        self.logger.info("✅ Experience Manager components shutdown")
    
    # ============================================================================
    # INTERFACE IMPLEMENTATION (IExperienceManager)
    # ============================================================================
    
    async def initialize_experience_session(self, user_context: UserContext, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a new user experience session with tenant isolation."""
        self.logger.info(f"Initializing experience session for user: {user_context.user_id}")
        try:
            # Validate tenant access
            if not self._validate_tenant_access(user_context):
                return {"success": False, "error": "Tenant access denied", "message": "Invalid tenant access"}
            
            # Generate tenant-scoped session ID
            tenant_session_id = self._generate_tenant_scoped_id(
                user_context.tenant_id, 
                "session"
            )
            
            # Add tenant context to session data
            session_data_with_tenant = {
                **session_data,
                "tenant_id": user_context.tenant_id,
                "tenant_session_id": tenant_session_id
            }
            
            # Create session using session manager with tenant context
            session_result = await self.session_manager.create_session(user_context, session_data_with_tenant)
            
            if session_result.get("success"):
                session_id = tenant_session_id  # Use tenant-scoped session ID
                self.active_sessions[session_id] = {
                    "user_context": user_context,
                    "session_data": session_data_with_tenant,
                    "status": SessionStatus.ACTIVE.value,
                    "created_at": datetime.utcnow().isoformat(),
                    "tenant_id": user_context.tenant_id  # Add tenant context
                }
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "session_status": SessionStatus.ACTIVE.value,
                    "tenant_id": user_context.tenant_id,  # Add tenant context
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Experience session initialized successfully with tenant isolation"
                }
            else:
                return {"success": False, "error": "Failed to create session"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize experience session: {e}")
            return {"success": False, "error": str(e)}
    
    async def manage_user_interface_state(self, session_id: str, ui_state: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Manage and synchronize user interface state across the platform with tenant isolation."""
        self.logger.info(f"Managing UI state for session: {session_id}")
        try:
            # Validate tenant access
            if not self._validate_tenant_access(user_context):
                return {"success": False, "error": "Tenant access denied", "message": "Invalid tenant access"}
            
            # Validate session belongs to tenant
            if not await self._validate_session_tenant_access(session_id, user_context):
                return {"success": False, "error": "Session access denied", "message": "Session does not belong to tenant"}
            
            # Add tenant context to UI state
            ui_state_with_tenant = {
                **ui_state,
                "tenant_id": user_context.tenant_id,
                "session_id": session_id
            }
            
            # Update UI state using UI state manager with tenant context
            state_result = await self.ui_state_manager.update_ui_state(session_id, ui_state_with_tenant, user_context)
            
            if state_result.get("success"):
                # Broadcast state update to real-time coordinator
                await self.real_time_coordinator.broadcast_state_update(session_id, ui_state, user_context)
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "ui_state_updated": True,
                    "tenant_id": user_context.tenant_id,  # Add tenant context
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "UI state managed successfully with tenant isolation"
                }
            else:
                return {"success": False, "error": "Failed to update UI state"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to manage UI state: {e}")
            return {"success": False, "error": str(e)}
    
    async def coordinate_frontend_backend_integration(self, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Coordinate integration between frontend and backend services."""
        self.logger.info("Coordinating frontend-backend integration")
        try:
            # Use frontend router to coordinate the request
            coordination_result = await self.frontend_router.coordinate_request(request_data, user_context)
            
            return {
                "success": True,
                "coordination_result": coordination_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate frontend-backend integration: {e}")
            return {"success": False, "error": str(e)}
    
    async def route_pillar_request(self, pillar_name: str, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Route requests to appropriate business pillars."""
        self.logger.info(f"Routing request to pillar: {pillar_name}")
        try:
            # Use frontend router to route to pillar
            routing_result = await self.frontend_router.route_to_pillar(pillar_name, request_data, user_context)
            
            return {
                "success": True,
                "pillar": pillar_name,
                "routing_result": routing_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to route pillar request: {e}")
            return {"success": False, "error": str(e)}
    
    async def manage_real_time_coordination(self, coordination_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Manage real-time coordination and updates across the platform."""
        self.logger.info("Managing real-time coordination")
        try:
            # Use real-time coordinator to manage coordination
            coordination_result = await self.real_time_coordinator.coordinate_updates(coordination_data, user_context)
            
            return {
                "success": True,
                "coordination_result": coordination_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to manage real-time coordination: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_websocket_connection(self, connection_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Handle WebSocket connections for real-time communication."""
        self.logger.info(f"Handling WebSocket connection: {connection_id}")
        try:
            # Register connection with real-time coordinator
            connection_result = await self.real_time_coordinator.register_connection(connection_id, user_context)
            
            if connection_result.get("success"):
                self.websocket_connections[connection_id] = {
                    "user_context": user_context,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                return {
                    "success": True,
                    "connection_id": connection_id,
                    "connection_status": "active",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to register connection"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to handle WebSocket connection: {e}")
            return {"success": False, "error": str(e)}
    
    async def broadcast_real_time_update(self, update_data: Dict[str, Any], target_sessions: List[str], user_context: UserContext) -> Dict[str, Any]:
        """Broadcast real-time updates to specific user sessions."""
        self.logger.info(f"Broadcasting real-time update to {len(target_sessions)} sessions")
        try:
            # Use real-time coordinator to broadcast updates
            broadcast_result = await self.real_time_coordinator.broadcast_to_sessions(update_data, target_sessions, user_context)
            
            return {
                "success": True,
                "broadcast_result": broadcast_result,
                "target_sessions": target_sessions,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to broadcast real-time update: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_session_state(self, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Retrieve the current state of a user session."""
        self.logger.info(f"Getting session state for: {session_id}")
        try:
            # Get session state from session manager
            session_state = await self.session_manager.get_session_state(session_id, user_context)
            
            return {
                "success": True,
                "session_id": session_id,
                "session_state": session_state,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get session state: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_session_state(self, session_id: str, state_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Update the state of a user session."""
        self.logger.info(f"Updating session state for: {session_id}")
        try:
            # Update session state using session manager
            update_result = await self.session_manager.update_session_state(session_id, state_data, user_context)
            
            if update_result.get("success"):
                # Update local session tracking
                if session_id in self.active_sessions:
                    self.active_sessions[session_id]["last_updated"] = datetime.utcnow().isoformat()
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "state_updated": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to update session state"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update session state: {e}")
            return {"success": False, "error": str(e)}
    
    async def terminate_experience_session(self, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Terminate a user experience session."""
        self.logger.info(f"Terminating experience session: {session_id}")
        try:
            # Terminate session using session manager
            termination_result = await self.session_manager.terminate_session(session_id, user_context)
            
            if termination_result.get("success"):
                # Remove from active sessions
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "session_terminated": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to terminate session"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to terminate experience session: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_available_pillars(self, user_context: UserContext) -> Dict[str, Any]:
        """Get list of available business pillars for the user."""
        self.logger.info("Getting available pillars")
        try:
            # Get available pillars from frontend router
            pillars_result = await self.frontend_router.get_available_pillars(user_context)
            
            return {
                "success": True,
                "available_pillars": pillars_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get available pillars: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # SOA SERVICE BASE IMPLEMENTATION
    # ============================================================================
    
    async def execute_operation(self, operation_type: ExperienceOperationType, 
                               operation_data: Dict[str, Any], 
                               user_context: UserContext) -> Dict[str, Any]:
        """Execute a specific operation."""
        self.logger.info(f"Executing operation: {operation_type.value}")
        
        try:
            if operation_type == ExperienceOperationType.SESSION_MANAGEMENT:
                return await self.initialize_experience_session(user_context, operation_data)
            elif operation_type == ExperienceOperationType.UI_STATE_MANAGEMENT:
                return await self.manage_user_interface_state(
                    operation_data.get("session_id"), 
                    operation_data.get("ui_state", {}), 
                    user_context
                )
            elif operation_type == ExperienceOperationType.REAL_TIME_COORDINATION:
                return await self.manage_real_time_coordination(operation_data, user_context)
            elif operation_type == ExperienceOperationType.FRONTEND_ROUTING:
                return await self.coordinate_frontend_backend_integration(operation_data, user_context)
            else:
                return {"success": False, "error": f"Unsupported operation: {operation_type.value}"}
                
        except Exception as e:
            self.logger.error(f"❌ Operation execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the Experience Manager."""
        base_health = await super().health_check()
        
        # Add Experience Manager specific health information
        experience_health = {
            "active_sessions": len(self.active_sessions),
            "websocket_connections": len(self.websocket_connections),
            "micro_modules_health": {
                "session_manager": await self.session_manager.health_check(),
                "ui_state_manager": await self.ui_state_manager.health_check(),
                "real_time_coordinator": await self.real_time_coordinator.health_check(),
                "frontend_router": await self.frontend_router.health_check(),
            },
            "mcp_server_health": "handled separately"
        }
        
        base_health.update(experience_health)
        return base_health


# Create service instance
experience_manager_service = ExperienceManagerService()
