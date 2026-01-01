"""
Experience Manager Service
Cross-dimensional orchestration for Experience services
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from bases.manager_service_base import ManagerServiceBase, ManagerServiceType, OrchestrationScope, GovernanceLevel
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from bases.interfaces.i_manager_service import IManagerService
from bases.protocols.manager_service_protocol import ManagerServiceProtocol


class ExperienceManagerService(ManagerServiceBase, IManagerService, ManagerServiceProtocol):
    """
    Experience Manager Service - Cross-dimensional orchestration for Experience services.
    
    EVOLUTIONARY VISION:
    - Current: POC frontend website for MVP demonstration
    - Future: Gateway to entire platform with expansive capabilities
    - External system integration: HubSpot, Voiceflow, Twilio, ERP, insurance platforms, GIS
    - AI-coexistence vision enabler across all client touchpoints
    
    Responsibilities:
    - Orchestrate experience services within the Experience domain
    - Coordinate with other domain managers for cross-dimensional experience orchestration
    - Manage experience service health and performance
    - Provide experience orchestration capabilities to other managers
    - Enable platform gateway capabilities for future expansion
    """
    
    def __init__(self, public_works_foundation: PublicWorksFoundationService):
        super().__init__(
            realm_name="experience",
            manager_type=ManagerServiceType.EXPERIENCE_MANAGER,
            public_works_foundation=public_works_foundation,
            orchestration_scope=OrchestrationScope.CROSS_DIMENSIONAL,
            governance_level=GovernanceLevel.MODERATE
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized Experience Manager Service for {self.realm_name} realm")
        
        # Experience-specific services (Current MVP)
        self.experience_services = {
            "frontend_integration": None,
            "session_manager": None,
            "ui_state_manager": None,
            "real_time_coordinator": None
        }
        
        # Experience-specific agents
        self.experience_agents = {
            "experience_coordinator": None,
            "ui_state_tracker": None
        }
        
        # Future Gateway Capabilities (Evolutionary Vision)
        self.gateway_services = {
            "platform_gateway": None,           # Central entry point for all client interactions
            "external_connectors": {},          # HubSpot, Voiceflow, Twilio, ERP, insurance, GIS
            "multi_channel_orchestrator": None, # Web, voice, chat, API, mobile experiences
            "ai_coexistence_enabler": None      # Seamless integration across all client touchpoints
        }
        
        # External System Integration Capabilities (Future)
        self.external_system_capabilities = {
            "hubspot_integration": {
                "enabled": False,
                "capabilities": ["crm_integration", "marketing_automation", "lead_management"],
                "future_vision": "Seamless CRM and marketing automation integration"
            },
            "voiceflow_integration": {
                "enabled": False,
                "capabilities": ["voice_ai", "conversational_ai", "voice_workflows"],
                "future_vision": "Voice and conversational AI integration"
            },
            "twilio_integration": {
                "enabled": False,
                "capabilities": ["communications", "messaging", "voice_calls", "sms"],
                "future_vision": "Multi-channel communications integration"
            },
            "erp_integration": {
                "enabled": False,
                "capabilities": ["enterprise_planning", "resource_management", "business_processes"],
                "future_vision": "Enterprise resource planning integration"
            },
            "insurance_platform_integration": {
                "enabled": False,
                "capabilities": ["insurance_workflows", "policy_management", "claims_processing"],
                "future_vision": "Insurance-specific workflow integration"
            },
            "gis_integration": {
                "enabled": False,
                "capabilities": ["geographic_data", "location_services", "spatial_analysis"],
                "future_vision": "Geographic information system integration"
            }
        }
    
    # ============================================================================
    # REALM STARTUP ORCHESTRATION
    # ============================================================================
    
    async def _get_realm_services(self) -> List[str]:
        """Get list of services managed by this realm."""
        return list(self.experience_services.keys())
    
    async def _start_service(self, service_name: str) -> Dict[str, Any]:
        """Start a specific service."""
        try:
            if service_name == "frontend_integration":
                return await self._start_frontend_integration()
            elif service_name == "session_manager":
                return await self._start_session_manager()
            elif service_name == "ui_state_manager":
                return await self._start_ui_state_manager()
            elif service_name == "real_time_coordinator":
                return await self._start_real_time_coordinator()
            else:
                return {"error": f"Unknown service: {service_name}", "status": "failed"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status of a specific service."""
        try:
            if service_name == "frontend_integration":
                return await self._get_frontend_integration_health()
            elif service_name == "session_manager":
                return await self._get_session_manager_health()
            elif service_name == "ui_state_manager":
                return await self._get_ui_state_manager_health()
            elif service_name == "real_time_coordinator":
                return await self._get_real_time_coordinator_health()
            else:
                return {"error": f"Unknown service: {service_name}", "status": "unhealthy"}
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    async def _shutdown_service(self, service_name: str) -> Dict[str, Any]:
        """Shutdown a specific service."""
        try:
            if service_name == "frontend_integration":
                return await self._shutdown_frontend_integration()
            elif service_name == "session_manager":
                return await self._shutdown_session_manager()
            elif service_name == "ui_state_manager":
                return await self._shutdown_ui_state_manager()
            elif service_name == "real_time_coordinator":
                return await self._shutdown_real_time_coordinator()
            else:
                return {"error": f"Unknown service: {service_name}", "status": "failed"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    # ============================================================================
    # DEPENDENCY MANAGEMENT
    # ============================================================================
    
    async def get_startup_dependencies(self) -> List[str]:
        """Experience Manager depends on Delivery Manager."""
        return ["delivery_manager"]
    
    async def _wait_for_manager_health(self, manager_name: str) -> bool:
        """Wait for a specific manager to be healthy."""
        if manager_name == "delivery_manager":
            return await self._wait_for_delivery_manager_health()
        return True
    
    async def _get_other_managers(self) -> List[str]:
        """Get list of other managers to coordinate with."""
        return ["delivery_manager", "city_manager", "journey_manager"]
    
    async def _coordinate_with_manager(self, manager_name: str, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with a specific manager."""
        if manager_name == "delivery_manager":
            return await self._coordinate_with_delivery_manager(startup_context)
        elif manager_name == "city_manager":
            return await self._coordinate_with_city_manager(startup_context)
        elif manager_name == "journey_manager":
            return await self._coordinate_with_journey_manager(startup_context)
        else:
            return {"error": f"Unknown manager: {manager_name}", "status": "failed"}
    
    # ============================================================================
    # EXPERIENCE SERVICE IMPLEMENTATIONS
    # ============================================================================
    
    async def _start_frontend_integration(self) -> Dict[str, Any]:
        """Start frontend integration service."""
        try:
            self.experience_services["frontend_integration"] = {
                "status": "started",
                "started_at": datetime.utcnow().isoformat()
            }
            
            return {
                "service_name": "frontend_integration",
                "status": "started",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _start_session_manager(self) -> Dict[str, Any]:
        """Start session manager service."""
        try:
            self.experience_services["session_manager"] = {
                "status": "started",
                "started_at": datetime.utcnow().isoformat()
            }
            
            return {
                "service_name": "session_manager",
                "status": "started",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _start_ui_state_manager(self) -> Dict[str, Any]:
        """Start UI state manager service."""
        try:
            self.experience_services["ui_state_manager"] = {
                "status": "started",
                "started_at": datetime.utcnow().isoformat()
            }
            
            return {
                "service_name": "ui_state_manager",
                "status": "started",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _start_real_time_coordinator(self) -> Dict[str, Any]:
        """Start real-time coordinator service."""
        try:
            self.experience_services["real_time_coordinator"] = {
                "status": "started",
                "started_at": datetime.utcnow().isoformat()
            }
            
            return {
                "service_name": "real_time_coordinator",
                "status": "started",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _get_frontend_integration_health(self) -> Dict[str, Any]:
        """Get frontend integration health."""
        try:
            service = self.experience_services.get("frontend_integration")
            if service and service.get("status") == "started":
                return {
                    "service_name": "frontend_integration",
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "service_name": "frontend_integration",
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    async def _get_session_manager_health(self) -> Dict[str, Any]:
        """Get session manager health."""
        try:
            service = self.experience_services.get("session_manager")
            if service and service.get("status") == "started":
                return {
                    "service_name": "session_manager",
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "service_name": "session_manager",
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    async def _get_ui_state_manager_health(self) -> Dict[str, Any]:
        """Get UI state manager health."""
        try:
            service = self.experience_services.get("ui_state_manager")
            if service and service.get("status") == "started":
                return {
                    "service_name": "ui_state_manager",
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "service_name": "ui_state_manager",
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    async def _get_real_time_coordinator_health(self) -> Dict[str, Any]:
        """Get real-time coordinator health."""
        try:
            service = self.experience_services.get("real_time_coordinator")
            if service and service.get("status") == "started":
                return {
                    "service_name": "real_time_coordinator",
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "service_name": "real_time_coordinator",
                    "status": "unhealthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    async def _shutdown_frontend_integration(self) -> Dict[str, Any]:
        """Shutdown frontend integration service."""
        try:
            self.experience_services["frontend_integration"] = {
                "status": "shutdown",
                "shutdown_at": datetime.utcnow().isoformat()
            }
            
            return {
                "service_name": "frontend_integration",
                "status": "shutdown",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _shutdown_session_manager(self) -> Dict[str, Any]:
        """Shutdown session manager service."""
        try:
            self.experience_services["session_manager"] = {
                "status": "shutdown",
                "shutdown_at": datetime.utcnow().isoformat()
            }
            
            return {
                "service_name": "session_manager",
                "status": "shutdown",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _shutdown_ui_state_manager(self) -> Dict[str, Any]:
        """Shutdown UI state manager service."""
        try:
            self.experience_services["ui_state_manager"] = {
                "status": "shutdown",
                "shutdown_at": datetime.utcnow().isoformat()
            }
            
            return {
                "service_name": "ui_state_manager",
                "status": "shutdown",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _shutdown_real_time_coordinator(self) -> Dict[str, Any]:
        """Shutdown real-time coordinator service."""
        try:
            self.experience_services["real_time_coordinator"] = {
                "status": "shutdown",
                "shutdown_at": datetime.utcnow().isoformat()
            }
            
            return {
                "service_name": "real_time_coordinator",
                "status": "shutdown",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    # ============================================================================
    # COORDINATION WITH OTHER MANAGERS
    # ============================================================================
    
    async def _wait_for_delivery_manager_health(self) -> bool:
        """Wait for Delivery Manager to be healthy."""
        try:
            # In a real implementation, this would check the actual Delivery Manager health
            # For now, we'll simulate a successful health check
            await asyncio.sleep(0.1)  # Simulate health check delay
            return True
        except Exception as e:
            self.logger.error(f"Failed to wait for Delivery Manager health: {e}")
            return False
    
    async def _coordinate_with_delivery_manager(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with Delivery Manager."""
        try:
            return {
                "manager_name": "delivery_manager",
                "coordination_type": "experience_to_delivery",
                "startup_context": startup_context,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _coordinate_with_city_manager(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with City Manager."""
        try:
            return {
                "manager_name": "city_manager",
                "coordination_type": "experience_to_city",
                "startup_context": startup_context,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    async def _coordinate_with_journey_manager(self, startup_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Coordinate with Journey Manager."""
        try:
            return {
                "manager_name": "journey_manager",
                "coordination_type": "experience_to_journey",
                "startup_context": startup_context,
                "status": "coordinated",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}


    # ============================================================================
    # MVP EXPERIENCE ORCHESTRATION
    # ============================================================================
    
    async def orchestrate_mvp_experience(self, solution_context: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate MVP experience with solution context and client-specific adaptations."""
        try:
            self.logger.info("🎭 Orchestrating MVP experience with solution context")
            
            # Extract solution context
            business_outcome = solution_context.get("business_outcome", "")
            solution_type = solution_context.get("solution_type", "custom")
            pillar_focus = solution_context.get("pillar_focus", {})
            agentic_personas = solution_context.get("agentic_personas", {})
            ui_adaptations = solution_context.get("ui_adaptations", {})
            
            # Determine client context for experience customization
            client_context = self._determine_client_context(solution_context)
            
            # Create MVP experience orchestration
            mvp_experience = await self._create_mvp_experience_orchestration(
                solution_context, user_context, client_context
            )
            
            # Orchestrate experience across all 4 pillars
            pillar_experience = await self._orchestrate_mvp_pillar_experience(
                solution_context, user_context, client_context
            )
            
            # Coordinate frontend integration with context
            frontend_coordination = await self._coordinate_frontend_integration(
                solution_context, user_context, client_context
            )
            
            return {
                "success": True,
                "mvp_experience": mvp_experience,
                "pillar_experience": pillar_experience,
                "frontend_coordination": frontend_coordination,
                "client_context": client_context,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate MVP experience: {e}")
            return {
                "success": False,
                "error": str(e),
                "mvp_experience": None
            }
    
    def _determine_client_context(self, solution_context: Dict[str, Any]) -> str:
        """Determine client context for experience customization."""
        business_outcome = solution_context.get("business_outcome", "").lower()
        solution_type = solution_context.get("solution_type", "custom")
        
        if "insurance" in business_outcome or "insurance" in solution_type:
            return "insurance_client"
        elif "autonomous" in business_outcome or "vehicle" in business_outcome or "testing" in business_outcome:
            return "autonomous_vehicle_testing"
        elif "carbon" in business_outcome or "credit" in business_outcome or "trading" in business_outcome:
            return "carbon_credits_trader"
        elif "legacy" in business_outcome or "integration" in business_outcome or "modernization" in business_outcome:
            return "data_integration_platform"
        else:
            return "custom_client"
    
    async def _create_mvp_experience_orchestration(self, solution_context: Dict[str, Any], 
                                                 user_context: Dict[str, Any], client_context: str) -> Dict[str, Any]:
        """Create MVP experience orchestration structure."""
        return {
            "experience_id": f"mvp_experience_{int(datetime.utcnow().timestamp())}",
            "business_outcome": solution_context.get("business_outcome", ""),
            "solution_context": solution_context,
            "user_context": user_context,
            "client_context": client_context,
            "pillar_sequence": [
                "content_pillar_experience",
                "insights_pillar_experience", 
                "operations_pillar_experience",
                "business_outcomes_pillar_experience"
            ],
            "current_pillar": "content_pillar_experience",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
    
    async def _orchestrate_mvp_pillar_experience(self, solution_context: Dict[str, Any], 
                                               user_context: Dict[str, Any], client_context: str) -> Dict[str, Any]:
        """Orchestrate MVP experience across all 4 pillars with client-specific adaptations."""
        pillar_results = {}
        
        # Content Pillar Experience
        content_experience = await self._orchestrate_content_pillar_experience(
            solution_context, user_context, client_context
        )
        pillar_results["content_pillar_experience"] = content_experience
        
        # Insights Pillar Experience  
        insights_experience = await self._orchestrate_insights_pillar_experience(
            solution_context, user_context, client_context
        )
        pillar_results["insights_pillar_experience"] = insights_experience
        
        # Operations Pillar Experience
        operations_experience = await self._orchestrate_operations_pillar_experience(
            solution_context, user_context, client_context
        )
        pillar_results["operations_pillar_experience"] = operations_experience
        
        # Business Outcomes Pillar Experience
        business_outcomes_experience = await self._orchestrate_business_outcomes_pillar_experience(
            solution_context, user_context, client_context
        )
        pillar_results["business_outcomes_pillar_experience"] = business_outcomes_experience
        
        return {
            "success": True,
            "pillar_experience": pillar_results,
            "client_context": client_context,
            "orchestration_complete": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _orchestrate_content_pillar_experience(self, solution_context: Dict[str, Any], 
                                                   user_context: Dict[str, Any], client_context: str) -> Dict[str, Any]:
        """Orchestrate Content Pillar experience with client-specific adaptations."""
        return {
            "pillar": "content",
            "experience_focus": "file_upload_and_parsing",
            "frontend_components": [
                "file_uploader",
                "data_preview",
                "parsing_status",
                "content_liaison_chat"
            ],
            "client_adaptations": self._get_content_pillar_experience_adaptations(client_context),
            "ui_adaptations": self._get_content_pillar_ui_adaptations(client_context),
            "agent_integration": self._get_content_pillar_agent_integration(client_context),
            "status": "ready"
        }
    
    async def _orchestrate_insights_pillar_experience(self, solution_context: Dict[str, Any], 
                                                    user_context: Dict[str, Any], client_context: str) -> Dict[str, Any]:
        """Orchestrate Insights Pillar experience with client-specific adaptations."""
        return {
            "pillar": "insights",
            "experience_focus": "data_analysis_and_visualization",
            "frontend_components": [
                "file_selection",
                "analysis_display",
                "visualization_components",
                "insights_liaison_chat"
            ],
            "client_adaptations": self._get_insights_pillar_experience_adaptations(client_context),
            "ui_adaptations": self._get_insights_pillar_ui_adaptations(client_context),
            "agent_integration": self._get_insights_pillar_agent_integration(client_context),
            "status": "ready"
        }
    
    async def _orchestrate_operations_pillar_experience(self, solution_context: Dict[str, Any], 
                                                      user_context: Dict[str, Any], client_context: str) -> Dict[str, Any]:
        """Orchestrate Operations Pillar experience with client-specific adaptations."""
        return {
            "pillar": "operations",
            "experience_focus": "workflow_and_sop_generation",
            "frontend_components": [
                "file_selection_or_upload",
                "workflow_visualization",
                "sop_display",
                "coexistence_blueprint",
                "operations_liaison_chat"
            ],
            "client_adaptations": self._get_operations_pillar_experience_adaptations(client_context),
            "ui_adaptations": self._get_operations_pillar_ui_adaptations(client_context),
            "agent_integration": self._get_operations_pillar_agent_integration(client_context),
            "status": "ready"
        }
    
    async def _orchestrate_business_outcomes_pillar_experience(self, solution_context: Dict[str, Any], 
                                                             user_context: Dict[str, Any], client_context: str) -> Dict[str, Any]:
        """Orchestrate Business Outcomes Pillar experience with client-specific adaptations."""
        return {
            "pillar": "business_outcomes",
            "experience_focus": "summary_and_proposal_generation",
            "frontend_components": [
                "summary_display",
                "poc_proposal",
                "roadmap_visualization",
                "business_outcomes_liaison_chat"
            ],
            "client_adaptations": self._get_business_outcomes_pillar_experience_adaptations(client_context),
            "ui_adaptations": self._get_business_outcomes_pillar_ui_adaptations(client_context),
            "agent_integration": self._get_business_outcomes_pillar_agent_integration(client_context),
            "status": "ready"
        }
    
    async def _coordinate_frontend_integration(self, solution_context: Dict[str, Any], 
                                             user_context: Dict[str, Any], client_context: str) -> Dict[str, Any]:
        """Coordinate frontend integration with solution context."""
        return {
            "frontend_coordination": {
                "client_context": client_context,
                "ui_theme": self._get_client_ui_theme(client_context),
                "color_scheme": self._get_client_color_scheme(client_context),
                "component_adaptations": self._get_client_component_adaptations(client_context),
                "agent_personas": solution_context.get("agentic_personas", {}),
                "status": "coordinated"
            }
        }
    
    # ============================================================================
    # CLIENT-SPECIFIC ADAPTATION METHODS
    # ============================================================================
    
    def _get_content_pillar_experience_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get Content Pillar experience adaptations based on client context."""
        adaptations = {
            "insurance_client": {
                "file_types": ["policy_documents", "claims_data", "underwriting_reports"],
                "parsing_focus": "insurance_data_parsing",
                "preview_capabilities": ["policy_analysis", "claims_insights", "risk_assessment"]
            },
            "autonomous_vehicle_testing": {
                "file_types": ["sensor_data", "test_results", "safety_reports"],
                "parsing_focus": "av_test_data_parsing",
                "preview_capabilities": ["sensor_analysis", "test_insights", "safety_assessment"]
            },
            "carbon_credits_trader": {
                "file_types": ["trading_data", "market_data", "carbon_metrics"],
                "parsing_focus": "carbon_trading_data_parsing",
                "preview_capabilities": ["trading_analysis", "market_insights", "carbon_assessment"]
            },
            "data_integration_platform": {
                "file_types": ["legacy_data", "integration_configs", "migration_data"],
                "parsing_focus": "legacy_data_parsing",
                "preview_capabilities": ["legacy_analysis", "integration_insights", "migration_assessment"]
            }
        }
        return adaptations.get(client_context, adaptations["insurance_client"])
    
    def _get_insights_pillar_experience_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get Insights Pillar experience adaptations based on client context."""
        adaptations = {
            "insurance_client": {
                "analysis_types": ["risk_analysis", "fraud_detection", "claims_analytics"],
                "visualization_types": ["risk_dashboards", "fraud_metrics", "claims_charts"],
                "recommendation_focus": "insurance_optimization"
            },
            "autonomous_vehicle_testing": {
                "analysis_types": ["safety_analysis", "performance_metrics", "test_analytics"],
                "visualization_types": ["safety_dashboards", "performance_metrics", "test_charts"],
                "recommendation_focus": "av_optimization"
            },
            "carbon_credits_trader": {
                "analysis_types": ["market_analysis", "trading_metrics", "carbon_analytics"],
                "visualization_types": ["market_dashboards", "trading_metrics", "carbon_charts"],
                "recommendation_focus": "trading_optimization"
            },
            "data_integration_platform": {
                "analysis_types": ["legacy_analysis", "integration_metrics", "migration_analytics"],
                "visualization_types": ["legacy_dashboards", "integration_metrics", "migration_charts"],
                "recommendation_focus": "integration_optimization"
            }
        }
        return adaptations.get(client_context, adaptations["insurance_client"])
    
    def _get_operations_pillar_experience_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get Operations Pillar experience adaptations based on client context."""
        adaptations = {
            "insurance_client": {
                "workflow_types": ["claims_processing", "underwriting_workflows", "policy_management"],
                "sop_types": ["claims_procedures", "underwriting_standards", "policy_guidelines"],
                "coexistence_focus": "insurance_integration"
            },
            "autonomous_vehicle_testing": {
                "workflow_types": ["testing_protocols", "safety_workflows", "validation_processes"],
                "sop_types": ["testing_procedures", "safety_standards", "validation_guidelines"],
                "coexistence_focus": "av_testing_integration"
            },
            "carbon_credits_trader": {
                "workflow_types": ["trading_protocols", "market_workflows", "compliance_processes"],
                "sop_types": ["trading_procedures", "market_standards", "compliance_guidelines"],
                "coexistence_focus": "carbon_trading_integration"
            },
            "data_integration_platform": {
                "workflow_types": ["migration_protocols", "integration_workflows", "modernization_processes"],
                "sop_types": ["migration_procedures", "integration_standards", "modernization_guidelines"],
                "coexistence_focus": "legacy_integration"
            }
        }
        return adaptations.get(client_context, adaptations["insurance_client"])
    
    def _get_business_outcomes_pillar_experience_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get Business Outcomes Pillar experience adaptations based on client context."""
        adaptations = {
            "insurance_client": {
                "summary_types": ["insurance_capability_summary", "risk_management_overview"],
                "poc_focus": "insurance_poc_validation",
                "roadmap_focus": "insurance_implementation_roadmap"
            },
            "autonomous_vehicle_testing": {
                "summary_types": ["av_testing_capability_summary", "safety_validation_overview"],
                "poc_focus": "av_testing_poc_validation",
                "roadmap_focus": "av_testing_implementation_roadmap"
            },
            "carbon_credits_trader": {
                "summary_types": ["carbon_trading_capability_summary", "market_strategy_overview"],
                "poc_focus": "carbon_trading_poc_validation",
                "roadmap_focus": "carbon_trading_implementation_roadmap"
            },
            "data_integration_platform": {
                "summary_types": ["legacy_modernization_capability_summary", "integration_strategy_overview"],
                "poc_focus": "legacy_modernization_poc_validation",
                "roadmap_focus": "legacy_modernization_implementation_roadmap"
            }
        }
        return adaptations.get(client_context, adaptations["insurance_client"])
    
    # ============================================================================
    # UI ADAPTATION METHODS
    # ============================================================================
    
    def _get_content_pillar_ui_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get Content Pillar UI adaptations based on client context."""
        return {
            "theme": f"{client_context}_content_focused",
            "color_scheme": self._get_client_color_scheme(client_context),
            "icons": f"{client_context}_content_icons",
            "layout": "content_pillar_layout"
        }
    
    def _get_insights_pillar_ui_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get Insights Pillar UI adaptations based on client context."""
        return {
            "theme": f"{client_context}_insights_focused",
            "color_scheme": self._get_client_color_scheme(client_context),
            "icons": f"{client_context}_insights_icons",
            "layout": "insights_pillar_layout"
        }
    
    def _get_operations_pillar_ui_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get Operations Pillar UI adaptations based on client context."""
        return {
            "theme": f"{client_context}_operations_focused",
            "color_scheme": self._get_client_color_scheme(client_context),
            "icons": f"{client_context}_operations_icons",
            "layout": "operations_pillar_layout"
        }
    
    def _get_business_outcomes_pillar_ui_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get Business Outcomes Pillar UI adaptations based on client context."""
        return {
            "theme": f"{client_context}_business_outcomes_focused",
            "color_scheme": self._get_client_color_scheme(client_context),
            "icons": f"{client_context}_business_outcomes_icons",
            "layout": "business_outcomes_pillar_layout"
        }
    
    def _get_client_ui_theme(self, client_context: str) -> str:
        """Get client-specific UI theme."""
        themes = {
            "insurance_client": "insurance_focused",
            "autonomous_vehicle_testing": "av_testing_focused",
            "carbon_credits_trader": "carbon_trading_focused",
            "data_integration_platform": "legacy_modernization_focused"
        }
        return themes.get(client_context, "default")
    
    def _get_client_color_scheme(self, client_context: str) -> str:
        """Get client-specific color scheme."""
        color_schemes = {
            "insurance_client": "blue_white",
            "autonomous_vehicle_testing": "green_blue",
            "carbon_credits_trader": "green_purple",
            "data_integration_platform": "orange_red"
        }
        return color_schemes.get(client_context, "default")
    
    def _get_client_component_adaptations(self, client_context: str) -> Dict[str, Any]:
        """Get client-specific component adaptations."""
        return {
            "client_context": client_context,
            "component_theme": self._get_client_ui_theme(client_context),
            "color_scheme": self._get_client_color_scheme(client_context),
            "custom_components": f"{client_context}_specific_components"
        }
    
    # ============================================================================
    # AGENT INTEGRATION METHODS
    # ============================================================================
    
    def _get_content_pillar_agent_integration(self, client_context: str) -> Dict[str, str]:
        """Get Content Pillar agent integration based on client context."""
        return {
            "content_liaison": f"{client_context}_content_specialist",
            "data_specialist": f"{client_context}_data_specialist",
            "file_processing_expert": f"{client_context}_file_processing_expert"
        }
    
    def _get_insights_pillar_agent_integration(self, client_context: str) -> Dict[str, str]:
        """Get Insights Pillar agent integration based on client context."""
        return {
            "insights_liaison": f"{client_context}_analytics_specialist",
            "data_analyst": f"{client_context}_data_analyst",
            "visualization_expert": f"{client_context}_visualization_expert"
        }
    
    def _get_operations_pillar_agent_integration(self, client_context: str) -> Dict[str, str]:
        """Get Operations Pillar agent integration based on client context."""
        return {
            "operations_liaison": f"{client_context}_workflow_specialist",
            "process_expert": f"{client_context}_process_expert",
            "coexistence_specialist": f"{client_context}_coexistence_specialist"
        }
    
    def _get_business_outcomes_pillar_agent_integration(self, client_context: str) -> Dict[str, str]:
        """Get Business Outcomes Pillar agent integration based on client context."""
        return {
            "business_outcomes_liaison": f"{client_context}_outcome_specialist",
            "roadmap_expert": f"{client_context}_roadmap_expert",
            "poc_specialist": f"{client_context}_poc_specialist"
        }
    
    # ============================================================================
    # EVOLUTIONARY GATEWAY CAPABILITIES
    # ============================================================================
    
    async def get_evolutionary_vision(self) -> Dict[str, Any]:
        """Get the evolutionary vision for Experience realm as platform gateway."""
        return {
            "current_state": {
                "description": "POC frontend website for MVP demonstration",
                "capabilities": [
                    "Basic frontend website",
                    "Business Enablement output exposure",
                    "MVP journey support",
                    "Context-aware UI"
                ],
                "limitations": [
                    "Limited to web interface",
                    "Basic integration capabilities",
                    "Single channel experience"
                ]
            },
            "future_vision": {
                "description": "Gateway to entire platform with expansive capabilities",
                "capabilities": [
                    "Platform gateway for all client interactions",
                    "External system integration (HubSpot, Voiceflow, Twilio, ERP, insurance, GIS)",
                    "Multi-channel experience orchestration",
                    "AI-coexistence vision enabler",
                    "Seamless integration across all client touchpoints"
                ],
                "external_systems": self.external_system_capabilities,
                "integration_vision": "Enable clients to connect to any system they need for their AI-coexistence vision"
            },
            "evolutionary_path": {
                "phase_1": "Enhanced frontend website with context-aware UI (Current MVP)",
                "phase_2": "Platform gateway with basic external integrations",
                "phase_3": "Multi-channel orchestration with advanced integrations",
                "phase_4": "Full AI-coexistence vision enabler across all touchpoints"
            }
        }
    
    async def get_external_system_capabilities(self) -> Dict[str, Any]:
        """Get external system integration capabilities for future expansion."""
        return {
            "current_capabilities": {
                "enabled": [cap for cap, config in self.external_system_capabilities.items() if config["enabled"]],
                "disabled": [cap for cap, config in self.external_system_capabilities.items() if not config["enabled"]]
            },
            "future_integrations": self.external_system_capabilities,
            "integration_roadmap": {
                "short_term": ["hubspot_integration", "twilio_integration"],
                "medium_term": ["voiceflow_integration", "erp_integration"],
                "long_term": ["insurance_platform_integration", "gis_integration"]
            }
        }
    
    async def enable_external_system_integration(self, system_name: str) -> Dict[str, Any]:
        """Enable external system integration (future capability)."""
        if system_name in self.external_system_capabilities:
            self.external_system_capabilities[system_name]["enabled"] = True
            return {
                "success": True,
                "message": f"External system integration enabled: {system_name}",
                "capabilities": self.external_system_capabilities[system_name]["capabilities"],
                "future_vision": self.external_system_capabilities[system_name]["future_vision"]
            }
        else:
            return {
                "success": False,
                "error": f"Unknown external system: {system_name}",
                "available_systems": list(self.external_system_capabilities.keys())
            }
    
    async def get_platform_gateway_capabilities(self) -> Dict[str, Any]:
        """Get platform gateway capabilities for future expansion."""
        return {
            "gateway_services": self.gateway_services,
            "current_status": "MVP frontend website",
            "future_capabilities": [
                "Central entry point for all client interactions",
                "External system connectors (HubSpot, Voiceflow, Twilio, ERP, insurance, GIS)",
                "Multi-channel orchestration (Web, voice, chat, API, mobile)",
                "AI-coexistence vision enabler across all client touchpoints"
            ],
            "integration_vision": "Enable clients to connect to any system they need for their AI-coexistence vision"
        }


# Create service instance
experience_manager_service = None  # Will be set by foundation services during initialization