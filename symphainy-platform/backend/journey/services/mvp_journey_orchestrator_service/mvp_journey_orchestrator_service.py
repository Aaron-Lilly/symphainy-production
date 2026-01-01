#!/usr/bin/env python3
"""
MVP Journey Orchestrator Service

WHAT: MVP-specific journey orchestration for 4-pillar navigation (Content, Insights, Operations, Business Outcome)
HOW: Composes SessionJourneyOrchestratorService with MVP-specific pillar configurations

This service provides MVP-SPECIFIC journey orchestration by composing the
SessionJourneyOrchestratorService with the 4-pillar structure from the MVP.

MVP Structure:
- Content Pillar: File upload, parsing, preview
- Insights Pillar: Analysis, visualization, insights summary
- Operations Pillar: Workflow/SOP generation, coexistence blueprint
- Business Outcome Pillar: Roadmap and POC proposal

Composes: SessionJourneyOrchestratorService for free-form navigation
"""

import os
import sys
import inspect
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class MVPJourneyOrchestratorService(OrchestratorBase):
    """
    MVP Journey Orchestrator Service for Journey realm.
    
    MVP-SPECIFIC implementation for 4-pillar navigation (Content, Insights, 
    Operations, Business Outcome) by composing SessionJourneyOrchestratorService.
    
    Provides MVP-specific pillar configurations, completion criteria, and
    recommended navigation flow while preserving user's freedom to navigate.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any, delivery_manager: Any = None, business_orchestrator: Any = None):
        """
        Initialize MVP Journey Orchestrator Service.
        
        Args:
            service_name: Name of the orchestrator service
            realm_name: Realm name (e.g., "journey")
            platform_gateway: Platform Gateway for infrastructure access
            di_container: DI Container for service discovery
            delivery_manager: Delivery Manager reference (optional)
            business_orchestrator: Business Orchestrator reference (optional, legacy)
        """
        super().__init__(
            service_name=service_name,
            realm_name=realm_name,
            platform_gateway=platform_gateway,
            di_container=di_container,
            delivery_manager=delivery_manager,
            business_orchestrator=business_orchestrator
        )
        
        # Will be initialized in initialize()
        self.session_orchestrator = None  # SessionJourneyOrchestratorService
        
        # Experience services (for direct pillar interactions)
        self.frontend_gateway = None
        self.user_experience = None
        
        # Guide Agent (declarative, LLM-powered)
        self.guide_agent = None
        
        # MVP Pillar Configuration
        self.mvp_pillars = self._define_mvp_pillars()
    
    async def initialize(self) -> bool:
        """
        Initialize MVP Journey Orchestrator Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking (via realm service delegation)
        await self._realm_service.log_operation_with_telemetry(
            "mvp_journey_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (initializes composed realm service)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            # 1. Discover Session Journey Orchestrator via Curator
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                try:
                    self.session_orchestrator = await curator.discover_service_by_name("SessionJourneyOrchestratorService")
                    self.logger.info("✅ Discovered SessionJourneyOrchestratorService")
                except Exception:
                    self.logger.warning("⚠️ SessionJourneyOrchestratorService not yet available")
            
            # 2. Initialize Guide Agent (declarative, LLM-powered)
            from backend.journey.agents.guide_cross_domain_agent import GuideCrossDomainAgent
            
            self.guide_agent = await self.initialize_agent(
                GuideCrossDomainAgent,
                "MVPGuideAgent",
                agent_type="guide",
                capabilities=["cross_domain_navigation", "intent_analysis", "journey_guidance"]
            )
            
            if self.guide_agent:
                self.logger.info("✅ Guide Cross-Domain Agent initialized (declarative, LLM-powered)")
            
            # 3. Compose experience "head" using Experience Foundation SDK
            await self._compose_experience_head()
            
            # 4. Register with Curator (Phase 2 pattern) (via realm service delegation)
            await self._realm_service.register_with_curator(
                capabilities=[
                    {
                        "name": "mvp_orchestration",
                        "protocol": "MVPJourneyOrchestratorProtocol",
                        "description": "Start and manage MVP-specific 4-pillar journeys",
                        "contracts": {
                            "soa_api": {
                                "api_name": "start_mvp_journey",
                                "endpoint": "/api/v1/journey/mvp/start",
                                "method": "POST",
                                "handler": self.start_mvp_journey,
                                "metadata": {
                                    "description": "Start MVP journey with 4 pillars",
                                    "parameters": ["user_id", "initial_pillar", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.start_mvp",
                            "semantic_api": "/api/v1/journey/mvp/start",
                            "user_journey": "start_mvp_journey"
                        }
                    },
                    {
                        "name": "pillar_navigation",
                        "protocol": "MVPJourneyOrchestratorProtocol",
                        "description": "Navigate between MVP pillars (free navigation)",
                        "contracts": {
                            "soa_api": {
                                "api_name": "navigate_to_pillar",
                                "endpoint": "/api/v1/journey/mvp/navigate",
                                "method": "POST",
                                "handler": self.navigate_to_pillar,
                                "metadata": {
                                    "description": "Navigate to specific MVP pillar",
                                    "parameters": ["session_id", "pillar_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.navigate_to_pillar",
                            "semantic_api": "/api/v1/journey/mvp/navigate",
                            "user_journey": "navigate_to_pillar"
                        }
                    },
                    {
                        "name": "mvp_completion_tracking",
                        "protocol": "MVPJourneyOrchestratorProtocol",
                        "description": "Track MVP journey completion across all pillars",
                        "contracts": {
                            "soa_api": {
                                "api_name": "check_mvp_completion",
                                "endpoint": "/api/v1/journey/mvp/check-completion",
                                "method": "POST",
                                "handler": self.check_mvp_completion,
                                "metadata": {
                                    "description": "Check if MVP journey is complete",
                                    "parameters": ["session_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.check_mvp_completion",
                            "semantic_api": "/api/v1/journey/mvp/check-completion",
                            "user_journey": "check_mvp_completion"
                        }
                    }
                ],
                soa_apis=[
                    "start_mvp_journey", "navigate_to_pillar", "get_pillar_state",
                    "update_pillar_progress", "get_mvp_progress", "end_mvp_journey",
                    "get_recommended_next_pillar", "check_mvp_completion"
                ],
                mcp_tools=[]  # Journey services provide SOA APIs, not MCP tools
            )
            
            # Record health metric (via realm service delegation)
            await self._realm_service.record_health_metric(
                "mvp_journey_orchestrator_initialized",
                1.0,
                {"service": self.service_name, "pillars_count": len(self.mvp_pillars)}
            )
            
            # End telemetry tracking (via realm service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "mvp_journey_orchestrator_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ MVP Journey Orchestrator Service initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit (via realm service delegation)
            await self._realm_service.handle_error_with_audit(e, "mvp_journey_orchestrator_initialize")
            
            # End telemetry tracking with failure (via realm service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "mvp_journey_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ MVP Journey Orchestrator Service initialization failed: {e}")
            return False
    
    async def _compose_experience_head(self):
        """Compose experience 'head' using Experience Foundation SDK."""
        try:
            # Get Experience Foundation from DI container
            experience_foundation = self.di_container.service_registry.get("ExperienceFoundationService")
            if not experience_foundation:
                # Try alternative access method
                experience_foundation = self.di_container.get_foundation_service("ExperienceFoundationService")
            
            if not experience_foundation:
                self.logger.warning("⚠️ Experience Foundation not available - experience head will not be composed")
                return
            
            self.logger.info("🔧 Composing experience 'head' using Experience Foundation SDK...")
            
            # Create Frontend Gateway using SDK
            gateway_config = {
                "composes": ["content_analysis", "insights", "operations", "business_outcomes"],
                "api_prefix": "/api/mvp",
                "journey_type": "mvp"
            }
            
            self.frontend_gateway = await experience_foundation.create_frontend_gateway(
                realm_name=self.realm_name,
                config=gateway_config
            )
            self.logger.info("✅ Frontend Gateway composed using Experience SDK")
            
            # Create User Experience using SDK
            ux_config = {
                "personalization_enabled": True,
                "analytics_enabled": True,
                "preference_storage": "librarian"
            }
            
            self.user_experience = await experience_foundation.create_user_experience(
                realm_name=self.realm_name,
                config=ux_config
            )
            self.logger.info("✅ User Experience composed using Experience SDK")
            
            self.logger.info("✅ Experience 'head' composed successfully for MVP Journey")
            
            # Verify that Frontend Gateway can discover orchestrators from Delivery Manager
            await self._verify_delivery_manager_readiness()
            
        except Exception as e:
            self.logger.error(f"❌ Experience head composition failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    async def _verify_delivery_manager_readiness(self):
        """Verify that Delivery Manager has initialized MVP orchestrators."""
        try:
            delivery_manager = self.di_container.service_registry.get("DeliveryManagerService")
            if delivery_manager and hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
                orchestrator_count = sum(1 for v in delivery_manager.mvp_pillar_orchestrators.values() if v is not None)
                if orchestrator_count > 0:
                    self.logger.info(f"✅ Delivery Manager has {orchestrator_count} MVP pillar orchestrators initialized")
                else:
                    self.logger.warning("⚠️ Delivery Manager has no MVP pillar orchestrators initialized yet")
            else:
                self.logger.warning("⚠️ Delivery Manager not available or missing mvp_pillar_orchestrators")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not verify Delivery Manager readiness: {e}")
    
    def _define_mvp_pillars(self) -> Dict[str, Dict[str, Any]]:
        """Define MVP pillar configurations."""
        return {
            "content": {
                "area_id": "content",
                "area_name": "Content Pillar",
                "description": "File upload, parsing, and preview",
                "recommended_order": 1,
                "completion_criteria": {
                    "files_uploaded": True,
                    "files_parsed": True
                },
                "available_actions": [
                    "upload_file",
                    "parse_file",
                    "preview_data",
                    "chat_with_content_liaison"
                ]
            },
            "insights": {
                "area_id": "insights",
                "area_name": "Insights Pillar",
                "description": "Data analysis, visualization, and insights summary",
                "recommended_order": 2,
                "completion_criteria": {
                    "file_selected": True,
                    "analysis_complete": True,
                    "insights_summary_generated": True
                },
                "available_actions": [
                    "select_file",
                    "analyze_data",
                    "create_visualization",
                    "generate_insights_summary",
                    "chat_with_insights_liaison"
                ]
            },
            "operations": {
                "area_id": "operations",
                "area_name": "Operations Pillar",
                "description": "Workflow/SOP generation and coexistence blueprint",
                "recommended_order": 3,
                "completion_criteria": {
                    "workflow_generated": True,
                    "sop_generated": True,
                    "coexistence_blueprint_created": True
                },
                "available_actions": [
                    "select_files",
                    "generate_workflow",
                    "generate_sop",
                    "create_coexistence_blueprint",
                    "chat_with_operations_liaison"
                ]
            },
            "business_outcome": {
                "area_id": "business_outcome",
                "area_name": "Business Outcome Pillar",
                "description": "Roadmap and POC proposal generation",
                "recommended_order": 4,
                "completion_criteria": {
                    "summaries_reviewed": True,
                    "roadmap_generated": True,
                    "poc_proposal_generated": True
                },
                "available_actions": [
                    "review_summaries",
                    "add_context",
                    "generate_roadmap",
                    "generate_poc_proposal",
                    "chat_with_experience_liaison"
                ]
            }
        }
    
    # ========================================================================
    # SOA APIs (MVP Journey Management)
    # ========================================================================
    
    async def start_mvp_journey(
        self,
        user_id: str,
        initial_pillar: str = "content",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start MVP journey for user (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            user_id: User ID
            initial_pillar: Initial pillar to start with (default: content)
            user_context: User context for security and tenant validation
        
        Returns:
            MVP journey session
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "start_mvp_journey_start",
            success=True,
            details={"user_id": user_id, "initial_pillar": initial_pillar}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "start_mvp_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "start_mvp_journey",
                    details={"user_id": user_id}
                )
                await self.record_health_metric("start_mvp_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("start_mvp_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "start_mvp_journey",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("start_mvp_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("start_mvp_journey_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if not self.session_orchestrator:
                return {
                    "success": False,
                    "error": "Session orchestrator not available"
                }
            
            # Create session config with MVP pillars
            session_config = {
                "areas": list(self.mvp_pillars.values()),
                "initial_area": initial_pillar,
                "session_type": "mvp",
                "recommended_flow": ["content", "insights", "operations", "business_outcome"]
            }
            
            # Extract solution_context from user_context if present (from landing page)
            solution_context = user_context.get("solution_context") if user_context else None
            if solution_context:
                self.logger.info("📋 Storing solution context in session")
                # Store solution context in session metadata
                if "metadata" not in session_config:
                    session_config["metadata"] = {}
                session_config["metadata"]["solution_context"] = solution_context
            
            # Start session via SessionJourneyOrchestrator
            session_result = await self.session_orchestrator.start_session(
                user_id,
                session_config,
                user_context=user_context
            )
            
            # Also store solution_context in session after creation (for easy retrieval)
            if solution_context and session_result.get("success"):
                session_id = session_result.get("session", {}).get("session_id")
                if session_id:
                    await self._store_solution_context_in_session(session_id, solution_context)
            
            if session_result.get("success"):
                session_id = session_result.get("session", {}).get("session_id")
                
                # Record health metric (success)
                await self.record_health_metric("start_mvp_journey_success", 1.0, {"user_id": user_id, "session_id": session_id, "initial_pillar": initial_pillar})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("start_mvp_journey_complete", success=True, details={"user_id": user_id, "session_id": session_id})
                
                self.logger.info(f"✅ MVP journey started for user: {user_id}")
            
            return session_result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "start_mvp_journey", details={"user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("start_mvp_journey_failed", 1.0, {"user_id": user_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("start_mvp_journey_complete", success=False, details={"user_id": user_id, "error": str(e)})
            
            self.logger.error(f"❌ Start MVP journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def navigate_to_pillar(
        self,
        session_id: str,
        pillar_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Navigate to specific pillar (SOA API - FREE NAVIGATION!).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            pillar_id: Pillar ID (content, insights, operations, business_outcome)
            user_context: User context for security and tenant validation
        
        Returns:
            Navigation result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "navigate_to_pillar_start",
            success=True,
            details={"session_id": session_id, "pillar_id": pillar_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "navigate_to_pillar", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "navigate_to_pillar",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id, "pillar_id": pillar_id}
                )
                await self.record_health_metric("navigate_to_pillar_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("navigate_to_pillar_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "navigate_to_pillar",
                                details={"tenant_id": tenant_id, "session_id": session_id, "pillar_id": pillar_id}
                            )
                            await self.record_health_metric("navigate_to_pillar_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("navigate_to_pillar_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if not self.session_orchestrator:
                return {
                    "success": False,
                    "error": "Session orchestrator not available"
                }
            
            # Validate pillar
            if pillar_id not in self.mvp_pillars:
                return {
                    "success": False,
                    "error": f"Invalid pillar: {pillar_id}"
                }
            
            # Navigate via SessionJourneyOrchestrator
            nav_result = await self.session_orchestrator.navigate_to_area(
                session_id,
                pillar_id,
                user_context=user_context
            )
            
            if nav_result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("navigate_to_pillar_success", 1.0, {"session_id": session_id, "pillar_id": pillar_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("navigate_to_pillar_complete", success=True, details={"session_id": session_id, "pillar_id": pillar_id})
                
                self.logger.info(f"✅ Navigated to pillar: {pillar_id}")
            
            return nav_result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "navigate_to_pillar", details={"session_id": session_id, "pillar_id": pillar_id})
            
            # Record health metric (failure)
            await self.record_health_metric("navigate_to_pillar_failed", 1.0, {"session_id": session_id, "pillar_id": pillar_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("navigate_to_pillar_complete", success=False, details={"session_id": session_id, "pillar_id": pillar_id, "error": str(e)})
            
            self.logger.error(f"❌ Navigate to pillar failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_pillar_state(
        self,
        session_id: str,
        pillar_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get state of specific pillar (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            pillar_id: Pillar ID
            user_context: User context for security and tenant validation
        
        Returns:
            Pillar state
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_pillar_state_start",
            success=True,
            details={"session_id": session_id, "pillar_id": pillar_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_pillar_state", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_pillar_state",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id, "pillar_id": pillar_id}
                )
                await self.record_health_metric("get_pillar_state_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_pillar_state_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_pillar_state",
                                details={"tenant_id": tenant_id, "session_id": session_id, "pillar_id": pillar_id}
                            )
                            await self.record_health_metric("get_pillar_state_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_pillar_state_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if not self.session_orchestrator:
                await self.log_operation_with_telemetry("get_pillar_state_complete", success=False, details={"session_id": session_id, "pillar_id": pillar_id, "error": "Session orchestrator not available"})
                return {
                    "success": False,
                    "error": "Session orchestrator not available"
                }
            
            result = await self.session_orchestrator.get_area_state(
                session_id,
                pillar_id,
                user_context=user_context
            )
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("get_pillar_state_success", 1.0, {"session_id": session_id, "pillar_id": pillar_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_pillar_state_complete", success=True, details={"session_id": session_id, "pillar_id": pillar_id})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_pillar_state", details={"session_id": session_id, "pillar_id": pillar_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_pillar_state_failed", 1.0, {"session_id": session_id, "pillar_id": pillar_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_pillar_state_complete", success=False, details={"session_id": session_id, "pillar_id": pillar_id, "error": str(e)})
            
            self.logger.error(f"❌ Get pillar state failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_pillar_progress(
        self,
        session_id: str,
        pillar_id: str,
        progress_updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update pillar progress (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            pillar_id: Pillar ID
            progress_updates: Progress updates (e.g., {"files_uploaded": True})
            user_context: User context for security and tenant validation
        
        Returns:
            Updated pillar state
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "update_pillar_progress_start",
            success=True,
            details={"session_id": session_id, "pillar_id": pillar_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "update_pillar_progress", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "update_pillar_progress",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id, "pillar_id": pillar_id}
                )
                await self.record_health_metric("update_pillar_progress_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("update_pillar_progress_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "update_pillar_progress",
                                details={"tenant_id": tenant_id, "session_id": session_id, "pillar_id": pillar_id}
                            )
                            await self.record_health_metric("update_pillar_progress_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("update_pillar_progress_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if not self.session_orchestrator:
                return {
                    "success": False,
                    "error": "Session orchestrator not available"
                }
            
            # Update area state
            update_result = await self.session_orchestrator.update_area_state(
                session_id,
                pillar_id,
                progress_updates,
                user_context=user_context
            )
            
            # Check completion
            if update_result.get("success"):
                completion_result = await self.session_orchestrator.check_area_completion(
                    session_id,
                    pillar_id,
                    user_context=user_context
                )
                update_result["completion"] = completion_result
                
                # Record health metric (success)
                await self.record_health_metric("update_pillar_progress_success", 1.0, {"session_id": session_id, "pillar_id": pillar_id, "completed": completion_result.get("completed", False)})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("update_pillar_progress_complete", success=True, details={"session_id": session_id, "pillar_id": pillar_id})
            
            return update_result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "update_pillar_progress", details={"session_id": session_id, "pillar_id": pillar_id})
            
            # Record health metric (failure)
            await self.record_health_metric("update_pillar_progress_failed", 1.0, {"session_id": session_id, "pillar_id": pillar_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("update_pillar_progress_complete", success=False, details={"session_id": session_id, "pillar_id": pillar_id, "error": str(e)})
            
            self.logger.error(f"❌ Update pillar progress failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_mvp_progress(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get overall MVP progress (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            user_context: User context for security and tenant validation
        
        Returns:
            MVP progress
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_mvp_progress_start",
            success=True,
            details={"session_id": session_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_mvp_progress", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_mvp_progress",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id}
                )
                await self.record_health_metric("get_mvp_progress_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_mvp_progress_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_mvp_progress",
                                details={"tenant_id": tenant_id, "session_id": session_id}
                            )
                            await self.record_health_metric("get_mvp_progress_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_mvp_progress_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if not self.session_orchestrator:
                await self.log_operation_with_telemetry("get_mvp_progress_complete", success=False, details={"session_id": session_id, "error": "Session orchestrator not available"})
                return {
                    "success": False,
                    "error": "Session orchestrator not available"
                }
            
            result = await self.session_orchestrator.get_session_progress(session_id, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("get_mvp_progress_success", 1.0, {"session_id": session_id, "completion_percent": result.get("progress", {}).get("completion_percent", 0)})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_mvp_progress_complete", success=True, details={"session_id": session_id})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_mvp_progress", details={"session_id": session_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_mvp_progress_failed", 1.0, {"session_id": session_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_mvp_progress_complete", success=False, details={"session_id": session_id, "error": str(e)})
            
            self.logger.error(f"❌ Get MVP progress failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def end_mvp_journey(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        End MVP journey (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            user_context: User context for security and tenant validation
        
        Returns:
            End journey result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "end_mvp_journey_start",
            success=True,
            details={"session_id": session_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "end_mvp_journey", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "end_mvp_journey",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id}
                )
                await self.record_health_metric("end_mvp_journey_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("end_mvp_journey_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "end_mvp_journey",
                                details={"tenant_id": tenant_id, "session_id": session_id}
                            )
                            await self.record_health_metric("end_mvp_journey_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("end_mvp_journey_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if not self.session_orchestrator:
                await self.log_operation_with_telemetry("end_mvp_journey_complete", success=False, details={"session_id": session_id, "error": "Session orchestrator not available"})
                return {
                    "success": False,
                    "error": "Session orchestrator not available"
                }
            
            result = await self.session_orchestrator.end_session(session_id, user_context=user_context)
            
            if result.get("success"):
                # Record health metric (success)
                await self.record_health_metric("end_mvp_journey_success", 1.0, {"session_id": session_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("end_mvp_journey_complete", success=True, details={"session_id": session_id})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "end_mvp_journey", details={"session_id": session_id})
            
            # Record health metric (failure)
            await self.record_health_metric("end_mvp_journey_failed", 1.0, {"session_id": session_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("end_mvp_journey_complete", success=False, details={"session_id": session_id, "error": str(e)})
            
            self.logger.error(f"❌ End MVP journey failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_recommended_next_pillar(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get recommended next pillar based on completion (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            user_context: User context for security and tenant validation
        
        Returns:
            Recommended next pillar
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_recommended_next_pillar_start",
            success=True,
            details={"session_id": session_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_recommended_next_pillar", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_recommended_next_pillar",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id}
                )
                await self.record_health_metric("get_recommended_next_pillar_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_recommended_next_pillar_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_recommended_next_pillar",
                                details={"tenant_id": tenant_id, "session_id": session_id}
                            )
                            await self.record_health_metric("get_recommended_next_pillar_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_recommended_next_pillar_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if not self.session_orchestrator:
                await self.log_operation_with_telemetry("get_recommended_next_pillar_complete", success=False, details={"session_id": session_id, "error": "Session orchestrator not available"})
                return {
                    "success": False,
                    "error": "Session orchestrator not available"
                }
            
            # Get session state
            session_result = await self.session_orchestrator.get_session_state(session_id, user_context=user_context)
            if not session_result.get("success"):
                await self.log_operation_with_telemetry("get_recommended_next_pillar_complete", success=False, details={"session_id": session_id})
                return session_result
            
            session = session_result["session"]
            
            # Find next incomplete pillar in recommended order
            recommended_flow = ["content", "insights", "operations", "business_outcome"]
            
            for pillar_id in recommended_flow:
                area = session["areas"].get(pillar_id)
                if area and area.get("status") != "completed":
                    # Record health metric (success)
                    await self.record_health_metric("get_recommended_next_pillar_success", 1.0, {"session_id": session_id, "recommended_pillar": pillar_id})
                    
                    # End telemetry tracking
                    await self.log_operation_with_telemetry("get_recommended_next_pillar_complete", success=True, details={"session_id": session_id, "recommended_pillar": pillar_id})
                    
                    return {
                        "success": True,
                        "recommended_pillar": pillar_id,
                        "pillar_info": self.mvp_pillars[pillar_id]
                    }
            
            # All complete!
            # Record health metric (success - all complete)
            await self.record_health_metric("get_recommended_next_pillar_success", 1.0, {"session_id": session_id, "recommended_pillar": None, "all_complete": True})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_recommended_next_pillar_complete", success=True, details={"session_id": session_id, "all_complete": True})
            
            return {
                "success": True,
                "recommended_pillar": None,
                "message": "All pillars complete!"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_recommended_next_pillar", details={"session_id": session_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_recommended_next_pillar_failed", 1.0, {"session_id": session_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_recommended_next_pillar_complete", success=False, details={"session_id": session_id, "error": str(e)})
            
            self.logger.error(f"❌ Get recommended next pillar failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_mvp_completion(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if MVP journey is complete (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            user_context: User context for security and tenant validation
        
        Returns:
            Completion status
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "check_mvp_completion_start",
            success=True,
            details={"session_id": session_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "check_mvp_completion", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "check_mvp_completion",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id}
                )
                await self.record_health_metric("check_mvp_completion_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("check_mvp_completion_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "check_mvp_completion",
                                details={"tenant_id": tenant_id, "session_id": session_id}
                            )
                            await self.record_health_metric("check_mvp_completion_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("check_mvp_completion_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            if not self.session_orchestrator:
                await self.log_operation_with_telemetry("check_mvp_completion_complete", success=False, details={"session_id": session_id, "error": "Session orchestrator not available"})
                return {
                    "success": False,
                    "error": "Session orchestrator not available"
                }
            
            # Get session state
            session_result = await self.session_orchestrator.get_session_state(session_id, user_context=user_context)
            if not session_result.get("success"):
                await self.log_operation_with_telemetry("check_mvp_completion_complete", success=False, details={"session_id": session_id})
                return session_result
            
            session = session_result["session"]
            
            # Check all pillars
            all_complete = True
            pillar_status = {}
            
            for pillar_id in ["content", "insights", "operations", "business_outcome"]:
                area = session["areas"].get(pillar_id)
                completed = area.get("status") == "completed" if area else False
                pillar_status[pillar_id] = {
                    "completed": completed,
                    "status": area.get("status") if area else "not_started"
                }
                if not completed:
                    all_complete = False
            
            # Record health metric (success)
            await self.record_health_metric("check_mvp_completion_success", 1.0, {"session_id": session_id, "mvp_complete": all_complete, "completed_pillars": sum(1 for p in pillar_status.values() if p.get("completed"))})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("check_mvp_completion_complete", success=True, details={"session_id": session_id, "mvp_complete": all_complete})
            
            return {
                "success": True,
                "mvp_complete": all_complete,
                "pillar_status": pillar_status
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "check_mvp_completion", details={"session_id": session_id})
            
            # Record health metric (failure)
            await self.record_health_metric("check_mvp_completion_failed", 1.0, {"session_id": session_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("check_mvp_completion_complete", success=False, details={"session_id": session_id, "error": str(e)})
            
            self.logger.error(f"❌ Check MVP completion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOLUTION CONTEXT MANAGEMENT
    # ========================================================================
    
    async def _store_solution_context_in_session(
        self,
        session_id: str,
        solution_context: Dict[str, Any]
    ):
        """
        Store solution context in session for later retrieval.
        
        Args:
            session_id: Session identifier
            solution_context: Solution context from landing page
        """
        try:
            # Store in session via Session Orchestrator (which has access to session storage)
            if self.session_orchestrator and hasattr(self.session_orchestrator, 'update_session'):
                await self.session_orchestrator.update_session(
                    session_id=session_id,
                    updates={
                        "solution_context": solution_context
                    }
                )
                self.logger.info(f"✅ Stored solution context in session {session_id}")
            else:
                # Fallback: Store in local cache if session orchestrator not available
                if hasattr(self, 'active_sessions'):
                    if session_id in self.active_sessions:
                        self.active_sessions[session_id]["solution_context"] = solution_context
                        self.logger.info(f"✅ Stored solution context in local cache for session {session_id}")
                else:
                    self.logger.warning("⚠️ Session storage not available, cannot store solution context")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to store solution context in session: {e}")
    
    async def get_solution_context(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get solution context from session.
        
        This context includes:
        - solution_structure: Agent-created pillar configuration
        - reasoning: Agent's analysis and recommendations
        - user_goals: User's stated goals
        - strategic_focus: Agent-determined focus area
        
        Args:
            session_id: Session identifier
        
        Returns:
            Solution context dict or None if not found
        """
        try:
            # Try to get from session orchestrator
            if self.session_orchestrator and hasattr(self.session_orchestrator, 'get_session'):
                session_data = await self.session_orchestrator.get_session(session_id)
                if session_data:
                    # Try to get from session data
                    solution_context = session_data.get("solution_context")
                    if solution_context:
                        self.logger.debug(f"✅ Retrieved solution context from session {session_id}")
                        return solution_context
                    
                    # Try to get from session metadata (if stored there)
                    session_metadata = session_data.get("metadata", {})
                    solution_context = session_metadata.get("solution_context")
                    if solution_context:
                        self.logger.debug(f"✅ Retrieved solution context from session metadata {session_id}")
                        return solution_context
            
            # Fallback: Try local cache
            if hasattr(self, 'active_sessions') and session_id in self.active_sessions:
                solution_context = self.active_sessions[session_id].get("solution_context")
                if solution_context:
                    self.logger.debug(f"✅ Retrieved solution context from local cache for session {session_id}")
                    return solution_context
            
            self.logger.debug(f"ℹ️ No solution context found for session {session_id}")
            return None
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to retrieve solution context: {e}")
            return None
    
    async def get_specialization_context(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get specialization context for liaison agents.
        
        This is a formatted version of solution context optimized for agent prompting.
        Includes user goals, strategic focus, and recommended data types.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Specialization context dict for liaison agents
        """
        try:
            solution_context = await self.get_solution_context(session_id)
            if not solution_context:
                return {}
            
            solution_structure = solution_context.get("solution_structure", {})
            reasoning = solution_context.get("reasoning", {})
            
            # Format for liaison agent consumption
            specialization_context = {
                "user_goals": solution_context.get("user_goals", ""),
                "strategic_focus": solution_structure.get("strategic_focus", "general"),
                "recommended_data_types": solution_structure.get("recommended_data_types", []),
                "pillar_priorities": {
                    pillar["name"]: {
                        "priority": pillar.get("priority"),
                        "enabled": pillar.get("enabled"),
                        "focus_areas": pillar.get("customizations", {}).get("focus_areas", [])
                    }
                    for pillar in solution_structure.get("pillars", [])
                },
                "key_insights": reasoning.get("key_insights", []),
                "recommendations": reasoning.get("recommendations", []),
                "confidence": reasoning.get("confidence", 0.0)
            }
            
            return specialization_context
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get specialization context: {e}")
            return {}
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "session_orchestrator_available": self.session_orchestrator is not None,
            "pillars": list(self.mvp_pillars.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "journey_service",
            "realm": "journey",
            "layer": "mvp_orchestration",
            "mvp_specific": True,
            "capabilities": ["mvp_orchestration", "pillar_navigation", "mvp_completion_tracking"],
            "soa_apis": [
                "start_mvp_journey", "navigate_to_pillar", "get_pillar_state",
                "update_pillar_progress", "get_mvp_progress", "end_mvp_journey",
                "get_recommended_next_pillar", "check_mvp_completion"
            ],
            "mcp_tools": [],
            "composes": "session_journey_orchestrator",
            "pillars": list(self.mvp_pillars.keys())
        }








