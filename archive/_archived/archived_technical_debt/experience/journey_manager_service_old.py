#!/usr/bin/env python3
"""
Journey Manager Service

Main service orchestrator for the Journey Manager, implemented as a Smart City role.
Handles user journey tracking, flow management, and experience optimization.

WHAT (Smart City Role): I manage user journeys and experience flows
HOW (Service Implementation): I use micro-modules, MCP server, and journey coordination
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
from experience.interfaces.journey_manager_interface import IJourneyManager, JourneyStage, JourneyStatus, FlowType

# Import micro-modules
from experience.roles.journey_manager.micro_modules.journey_tracker import JourneyTrackerModule
from experience.roles.journey_manager.micro_modules.flow_manager import FlowManagerModule
from experience.roles.journey_manager.micro_modules.journey_analytics import JourneyAnalyticsModule
from experience.roles.journey_manager.micro_modules.experience_optimizer import ExperienceOptimizerModule

# MCP server will be initialized separately to avoid circular imports


class JourneyManagerService(ExperienceServiceBase, IJourneyManager):
    """
    Journey Manager Service for user journey tracking and flow management.
    
    Implements the IJourneyManager interface and orchestrates various micro-modules,
    and MCP server to provide comprehensive journey management capabilities.
    """
    
    def __init__(self, utility_foundation=None, curator_foundation=None, 
                 environment: Optional[EnvironmentLoader] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize Journey Manager Service."""
        super().__init__(
            service_name="journey_manager",
            service_type=ExperienceServiceType.JOURNEY_MANAGER,
            utility_foundation=utility_foundation,
            curator_foundation=curator_foundation
        )
        
        self.environment = environment or EnvironmentLoader()
        self.logger = logger or logging.getLogger(self.service_name)
        
        # Initialize micro-modules
        self.journey_tracker = JourneyTrackerModule(self.environment, self.logger)
        self.flow_manager = FlowManagerModule(self.environment, self.logger)
        self.journey_analytics = JourneyAnalyticsModule(self.environment, self.logger)
        self.experience_optimizer = ExperienceOptimizerModule(self.environment, self.logger)
        
        # MCP server will be initialized separately
        
        # Initialize supported operations
        self.supported_operations = [
            ExperienceOperationType.JOURNEY_TRACKING,
            ExperienceOperationType.FLOW_MANAGEMENT
        ]
        
        # Service contract
        self.service_contract = {
            "service_name": self.service_name,
            "service_type": self.service_type.value,
            "supported_operations": [op.value for op in self.supported_operations],
            "capabilities": [
                "journey_creation",
                "journey_tracking",
                "flow_management",
                "journey_analytics",
                "experience_optimization",
                "cross_pillar_coordination"
            ]
        }
        
        # Active journeys and flows
        self.active_journeys = {}
        self.journey_flows = {}
        
        self.logger.info(f"🗺️ {self.service_name} initialized - Journey Manager")
    
    async def _initialize_service_components(self):
        """Initialize service-specific components."""
        self.logger.info("🚀 Initializing Journey Manager components...")
        
        # Initialize micro-modules
        await self.journey_tracker.initialize()
        await self.flow_manager.initialize()
        await self.journey_analytics.initialize()
        await self.experience_optimizer.initialize()
        
        # MCP server initialization handled separately
        
        self.logger.info("✅ Journey Manager components initialized")
    
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
    
    async def _validate_journey_tenant_access(self, journey_id: str, user_context: UserContext) -> bool:
        """Validate that a journey belongs to the tenant."""
        try:
            # This would typically query the database to verify journey ownership
            # For now, we check if the journey_id contains the tenant_id
            if user_context.tenant_id in journey_id:
                return True
            
            # Additional database validation can be added here
            self.logger.warning(f"❌ Journey access denied: Journey {journey_id} does not belong to tenant {user_context.tenant_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error validating journey tenant access: {e}")
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
                    "content": "I'm sorry, but I don't have access to your tenant's journey management. Please check your authentication.",
                    "agent_name": "JourneyManagerLiaisonAgent",
                    "current_pillar": "journey",
                    "suggestions": ["Check authentication", "Contact support"],
                    "tenant_id": None
                }
            
            # Route to appropriate liaison agent method based on message content
            message_lower = message.lower()
            
            if any(keyword in message_lower for keyword in ["journey", "create", "start", "begin"]):
                return await self._handle_journey_creation_guidance(message, user_context, context)
            elif any(keyword in message_lower for keyword in ["progress", "track", "update", "milestone"]):
                return await self._handle_progress_guidance(message, user_context, context)
            elif any(keyword in message_lower for keyword in ["flow", "navigate", "branch", "route"]):
                return await self._handle_flow_guidance(message, user_context, context)
            elif any(keyword in message_lower for keyword in ["analytics", "analyze", "optimize", "performance"]):
                return await self._handle_analytics_guidance(message, user_context, context)
            else:
                return await self._handle_general_journey_guidance(message, user_context, context)
                
        except Exception as e:
            self.logger.error(f"❌ Error processing liaison agent message: {e}")
            return {
                "content": "I encountered an error processing your request. Please try again.",
                "agent_name": "JourneyManagerLiaisonAgent",
                "current_pillar": "journey",
                "suggestions": ["Try again", "Contact support"],
                "tenant_id": user_context.tenant_id if user_context else None
            }
    
    async def _handle_journey_creation_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on journey creation."""
        try:
            # Get tenant-specific journey capabilities
            tenant_config = await self._get_tenant_config(user_context.tenant_id)
            max_journeys = tenant_config.get("max_journeys_per_user", 5)
            
            return {
                "content": f"I can help you create and manage user journeys! Your tenant allows up to {max_journeys} concurrent journeys. What type of journey would you like to create?",
                "agent_name": "JourneyManagerLiaisonAgent",
                "current_pillar": "journey",
                "suggestions": [
                    "Create a new journey",
                    "Check active journeys",
                    "What journey types are available?",
                    "How do I start a journey?",
                    "Show journey templates"
                ],
                "tenant_id": user_context.tenant_id
            }
        except Exception as e:
            self.logger.error(f"❌ Error in journey creation guidance: {e}")
            return {
                "content": "I can help you create and manage user journeys. What would you like to do?",
                "agent_name": "JourneyManagerLiaisonAgent",
                "current_pillar": "journey",
                "suggestions": ["Create journey", "Check journeys"],
                "tenant_id": user_context.tenant_id
            }
    
    async def _handle_progress_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on journey progress tracking."""
        return {
            "content": "I can help you track journey progress! I can monitor milestones, update progress data, and provide real-time journey status. What would you like to track?",
            "agent_name": "JourneyManagerLiaisonAgent",
            "current_pillar": "journey",
            "suggestions": [
                "Track journey progress",
                "Update milestones",
                "Check journey status",
                "What progress features are available?",
                "How do I track progress?"
            ],
            "tenant_id": user_context.tenant_id
        }
    
    async def _handle_flow_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on journey flow management."""
        return {
            "content": "I can help you manage journey flows! I can handle navigation, branching decisions, and cross-pillar coordination. What flow would you like to manage?",
            "agent_name": "JourneyManagerLiaisonAgent",
            "current_pillar": "journey",
            "suggestions": [
                "Navigate to next milestone",
                "Handle journey branching",
                "Coordinate cross-pillar flows",
                "What flow features are available?",
                "How do I manage flows?"
            ],
            "tenant_id": user_context.tenant_id
        }
    
    async def _handle_analytics_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide guidance on journey analytics and optimization."""
        return {
            "content": "I can help you analyze and optimize journeys! I can provide analytics insights, performance metrics, and optimization recommendations. What would you like to analyze?",
            "agent_name": "JourneyManagerLiaisonAgent",
            "current_pillar": "journey",
            "suggestions": [
                "Analyze journey performance",
                "Get optimization recommendations",
                "View journey analytics",
                "What analytics are available?",
                "How do I optimize journeys?"
            ],
            "tenant_id": user_context.tenant_id
        }
    
    async def _handle_general_journey_guidance(self, message: str, user_context: UserContext, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general journey management guidance."""
        return {
            "content": "I'm your Journey Manager liaison agent! I can help you create journeys, track progress, manage flows, and analyze performance. What would you like to do?",
            "agent_name": "JourneyManagerLiaisonAgent",
            "current_pillar": "journey",
            "suggestions": [
                "Create a journey",
                "Track progress",
                "Manage flows",
                "Analyze performance",
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
                "max_journeys_per_user": 5,
                "max_milestones_per_journey": 20,
                "max_flow_branches": 10,
                "supported_journey_types": ["content", "insights", "operations", "business-outcomes", "cross-pillar"]
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting tenant config: {e}")
            return {
                "max_journeys_per_user": 5,
                "max_milestones_per_journey": 20,
                "max_flow_branches": 10,
                "supported_journey_types": ["content", "insights", "operations", "business-outcomes"]
            }
    
    async def _shutdown_service_components(self):
        """Shutdown service-specific components."""
        self.logger.info("🛑 Shutting down Journey Manager components...")
        
        # Shutdown micro-modules
        await self.journey_tracker.shutdown()
        await self.flow_manager.shutdown()
        await self.journey_analytics.shutdown()
        await self.experience_optimizer.shutdown()
        
        # MCP server shutdown handled separately
        
        self.logger.info("✅ Journey Manager components shutdown")
    
    # ============================================================================
    # INTERFACE IMPLEMENTATION (IJourneyManager)
    # ============================================================================
    
    async def create_user_journey(self, user_context: UserContext, journey_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user journey with tenant isolation."""
        self.logger.info(f"Creating user journey for user: {user_context.user_id}")
        try:
            # Validate tenant access
            if not self._validate_tenant_access(user_context):
                return {"success": False, "error": "Tenant access denied", "message": "Invalid tenant access"}
            
            # Generate tenant-scoped journey ID
            tenant_journey_id = self._generate_tenant_scoped_id(
                user_context.tenant_id, 
                "journey"
            )
            
            # Add tenant context to journey config
            journey_config_with_tenant = {
                **journey_config,
                "tenant_id": user_context.tenant_id,
                "tenant_journey_id": tenant_journey_id
            }
            
            # Create journey using journey tracker with tenant context
            journey_result = await self.journey_tracker.create_journey(user_context, journey_config_with_tenant)
            
            if journey_result.get("success"):
                journey_id = tenant_journey_id  # Use tenant-scoped journey ID
                self.active_journeys[journey_id] = {
                    "user_context": user_context,
                    "journey_config": journey_config_with_tenant,
                    "status": JourneyStatus.ACTIVE.value,
                    "created_at": datetime.utcnow().isoformat(),
                    "tenant_id": user_context.tenant_id  # Add tenant context
                }
                
                return {
                    "success": True,
                    "journey_id": journey_id,
                    "journey_status": JourneyStatus.ACTIVE.value,
                    "tenant_id": user_context.tenant_id,  # Add tenant context
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "User journey created successfully with tenant isolation"
                }
            else:
                return {"success": False, "error": "Failed to create journey"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create user journey: {e}")
            return {"success": False, "error": str(e)}
    
    async def track_journey_progress(self, journey_id: str, progress_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Track progress in a user journey with tenant isolation."""
        self.logger.info(f"Tracking progress for journey: {journey_id}")
        try:
            # Validate tenant access
            if not self._validate_tenant_access(user_context):
                return {"success": False, "error": "Tenant access denied", "message": "Invalid tenant access"}
            
            # Validate journey belongs to tenant
            if not await self._validate_journey_tenant_access(journey_id, user_context):
                return {"success": False, "error": "Journey access denied", "message": "Journey does not belong to tenant"}
            
            # Add tenant context to progress data
            progress_data_with_tenant = {
                **progress_data,
                "tenant_id": user_context.tenant_id,
                "journey_id": journey_id
            }
            
            # Track progress using journey tracker with tenant context
            progress_result = await self.journey_tracker.track_progress(journey_id, progress_data_with_tenant, user_context)
            
            if progress_result.get("success"):
                # Update local journey tracking
                if journey_id in self.active_journeys:
                    self.active_journeys[journey_id]["last_updated"] = datetime.utcnow().isoformat()
                
                return {
                    "success": True,
                    "journey_id": journey_id,
                    "progress_tracked": True,
                    "tenant_id": user_context.tenant_id,  # Add tenant context
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Journey progress tracked successfully with tenant isolation"
                }
            else:
                return {"success": False, "error": "Failed to track progress"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to track journey progress: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_journey_state(self, journey_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Get the current state of a user journey."""
        self.logger.info(f"Getting journey state for: {journey_id}")
        try:
            # Get journey state using journey tracker
            journey_state = await self.journey_tracker.get_journey_state(journey_id, user_context)
            
            return {
                "success": True,
                "journey_id": journey_id,
                "journey_state": journey_state,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get journey state: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_journey_flow(self, journey_id: str, flow_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Update the flow of a user journey."""
        self.logger.info(f"Updating journey flow for: {journey_id}")
        try:
            # Update flow using flow manager
            flow_result = await self.flow_manager.update_flow(journey_id, flow_data, user_context)
            
            if flow_result.get("success"):
                # Update local flow tracking
                self.journey_flows[journey_id] = flow_data
                
                return {
                    "success": True,
                    "journey_id": journey_id,
                    "flow_updated": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to update journey flow"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update journey flow: {e}")
            return {"success": False, "error": str(e)}
    
    async def navigate_to_next_milestone(self, journey_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Navigate to the next milestone in a user journey."""
        self.logger.info(f"Navigating to next milestone for journey: {journey_id}")
        try:
            # Navigate using flow manager
            navigation_result = await self.flow_manager.navigate_to_next_milestone(journey_id, user_context)
            
            return {
                "success": True,
                "journey_id": journey_id,
                "navigation_result": navigation_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to navigate to next milestone: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_journey_branching(self, journey_id: str, branch_decision: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Handle branching decisions in a user journey."""
        self.logger.info(f"Handling journey branching for: {journey_id}")
        try:
            # Handle branching using flow manager
            branching_result = await self.flow_manager.handle_branching(journey_id, branch_decision, user_context)
            
            return {
                "success": True,
                "journey_id": journey_id,
                "branching_result": branching_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle journey branching: {e}")
            return {"success": False, "error": str(e)}
    
    async def coordinate_cross_pillar_journey(self, journey_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Coordinate journeys that span multiple business pillars."""
        self.logger.info("Coordinating cross-pillar journey")
        try:
            # Coordinate using flow manager
            coordination_result = await self.flow_manager.coordinate_cross_pillar_journey(journey_data, user_context)
            
            return {
                "success": True,
                "coordination_result": coordination_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate cross-pillar journey: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_journey_analytics(self, journey_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Analyze analytics for a user journey."""
        self.logger.info(f"Analyzing journey analytics for: {journey_id}")
        try:
            # Analyze using journey analytics
            analytics_result = await self.journey_analytics.analyze_journey(journey_id, user_context)
            
            return {
                "success": True,
                "journey_id": journey_id,
                "analytics": analytics_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze journey analytics: {e}")
            return {"success": False, "error": str(e)}
    
    async def optimize_journey_experience(self, journey_id: str, optimization_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Optimize the experience of a user journey."""
        self.logger.info(f"Optimizing journey experience for: {journey_id}")
        try:
            # Optimize using experience optimizer
            optimization_result = await self.experience_optimizer.optimize_journey(journey_id, optimization_data, user_context)
            
            return {
                "success": True,
                "journey_id": journey_id,
                "optimization_result": optimization_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to optimize journey experience: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_user_journey_history(self, user_context: UserContext) -> Dict[str, Any]:
        """Get the journey history for a user."""
        self.logger.info(f"Getting journey history for user: {user_context.user_id}")
        try:
            # Get history using journey tracker
            history_result = await self.journey_tracker.get_user_journey_history(user_context)
            
            return {
                "success": True,
                "user_id": user_context.user_id,
                "journey_history": history_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user journey history: {e}")
            return {"success": False, "error": str(e)}
    
    async def pause_journey(self, journey_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Pause a user journey."""
        self.logger.info(f"Pausing journey: {journey_id}")
        try:
            # Pause using journey tracker
            pause_result = await self.journey_tracker.pause_journey(journey_id, user_context)
            
            if pause_result.get("success"):
                # Update local journey status
                if journey_id in self.active_journeys:
                    self.active_journeys[journey_id]["status"] = JourneyStatus.PAUSED.value
                
                return {
                    "success": True,
                    "journey_id": journey_id,
                    "journey_paused": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to pause journey"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to pause journey: {e}")
            return {"success": False, "error": str(e)}
    
    async def resume_journey(self, journey_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Resume a paused user journey."""
        self.logger.info(f"Resuming journey: {journey_id}")
        try:
            # Resume using journey tracker
            resume_result = await self.journey_tracker.resume_journey(journey_id, user_context)
            
            if resume_result.get("success"):
                # Update local journey status
                if journey_id in self.active_journeys:
                    self.active_journeys[journey_id]["status"] = JourneyStatus.ACTIVE.value
                
                return {
                    "success": True,
                    "journey_id": journey_id,
                    "journey_resumed": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to resume journey"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to resume journey: {e}")
            return {"success": False, "error": str(e)}
    
    async def complete_journey(self, journey_id: str, completion_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Complete a user journey."""
        self.logger.info(f"Completing journey: {journey_id}")
        try:
            # Complete using journey tracker
            completion_result = await self.journey_tracker.complete_journey(journey_id, completion_data, user_context)
            
            if completion_result.get("success"):
                # Update local journey status
                if journey_id in self.active_journeys:
                    self.active_journeys[journey_id]["status"] = JourneyStatus.COMPLETED.value
                    self.active_journeys[journey_id]["completed_at"] = datetime.utcnow().isoformat()
                
                return {
                    "success": True,
                    "journey_id": journey_id,
                    "journey_completed": True,
                    "completion_summary": completion_result.get("completion_summary", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {"success": False, "error": "Failed to complete journey"}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to complete journey: {e}")
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
            if operation_type == ExperienceOperationType.JOURNEY_TRACKING:
                return await self.track_journey_progress(
                    operation_data.get("journey_id"), 
                    operation_data.get("progress_data", {}), 
                    user_context
                )
            elif operation_type == ExperienceOperationType.FLOW_MANAGEMENT:
                return await self.update_journey_flow(
                    operation_data.get("journey_id"), 
                    operation_data.get("flow_data", {}), 
                    user_context
                )
            else:
                return {"success": False, "error": f"Unsupported operation: {operation_type.value}"}
                
        except Exception as e:
            self.logger.error(f"❌ Operation execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the Journey Manager."""
        base_health = await super().health_check()
        
        # Add Journey Manager specific health information
        journey_health = {
            "active_journeys": len(self.active_journeys),
            "journey_flows": len(self.journey_flows),
            "micro_modules_health": {
                "journey_tracker": await self.journey_tracker.health_check(),
                "flow_manager": await self.flow_manager.health_check(),
                "journey_analytics": await self.journey_analytics.health_check(),
                "experience_optimizer": await self.experience_optimizer.health_check(),
            },
            "mcp_server_health": "handled separately"
        }
        
        base_health.update(journey_health)
        return base_health


# Create service instance
journey_manager_service = JourneyManagerService()
