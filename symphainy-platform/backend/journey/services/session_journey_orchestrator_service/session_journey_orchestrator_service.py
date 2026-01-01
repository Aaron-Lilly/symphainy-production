#!/usr/bin/env python3
"""
Session Journey Orchestrator Service

WHAT: Enables free-form, user-driven navigation across solution areas/pillars
HOW: Tracks session state per area, enables jumping between areas, preserves context

This service provides SESSION-BASED journey orchestration for free-form, exploratory flows
where users control navigation completely (e.g., MVP website navigation, exploratory solutions)
by tracking progress per area/pillar and preserving context across navigation.

Use this for: User-driven exploration, MVP websites, flexible workflows
For structured, linear journeys, use StructuredJourneyOrchestratorService instead.
"""

import os
import sys
import inspect
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class SessionJourneyOrchestratorService(RealmServiceBase):
    """
    Session Journey Orchestrator Service for Journey realm.
    
    Enables FREE-FORM, USER-DRIVEN navigation where users control their path completely.
    Tracks progress per area/pillar, preserves context, and enables jumping between areas.
    
    Use for: MVP websites, exploratory solutions, user-driven workflows
    For structured, linear journeys, use StructuredJourneyOrchestratorService instead.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Session Journey Orchestrator Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.traffic_cop = None  # For session state management
        
        # Experience services (discovered via Curator)
        self.frontend_gateway = None
        self.user_experience = None
        self.session_manager = None
        
        # Journey Analytics and Milestone Tracker (discovered via Curator)
        self.journey_analytics = None
        self.milestone_tracker = None
        
        # Active sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> bool:
        """
        Initialize Session Journey Orchestrator Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "session_journey_orchestrator_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.librarian = await self.get_librarian_api()
            self.traffic_cop = await self.get_traffic_cop_api()
            
            # 2. Discover Experience services via Curator
            await self._discover_experience_services()
            
            # 3. Discover Journey services via Curator
            await self._discover_journey_services()
            
            # 4. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "session_orchestration",
                        "protocol": "SessionJourneyOrchestratorProtocol",
                        "description": "Start and manage free-form session journeys",
                        "contracts": {
                            "soa_api": {
                                "api_name": "start_session",
                                "endpoint": "/api/v1/journey/session/start",
                                "method": "POST",
                                "handler": self.start_session,
                                "metadata": {
                                    "description": "Start a new session journey",
                                    "parameters": ["user_id", "session_config", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.start_session",
                            "semantic_api": "/api/v1/journey/session/start",
                            "user_journey": "start_session_journey"
                        }
                    },
                    {
                        "name": "free_navigation",
                        "protocol": "SessionJourneyOrchestratorProtocol",
                        "description": "Enable free-form navigation between areas",
                        "contracts": {
                            "soa_api": {
                                "api_name": "navigate_to_area",
                                "endpoint": "/api/v1/journey/session/navigate",
                                "method": "POST",
                                "handler": self.navigate_to_area,
                                "metadata": {
                                    "description": "Navigate to a specific area (free navigation)",
                                    "parameters": ["session_id", "area_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.navigate_to_area",
                            "semantic_api": "/api/v1/journey/session/navigate",
                            "user_journey": "navigate_to_area"
                        }
                    },
                    {
                        "name": "area_tracking",
                        "protocol": "SessionJourneyOrchestratorProtocol",
                        "description": "Track area state and progress",
                        "contracts": {
                            "soa_api": {
                                "api_name": "update_area_state",
                                "endpoint": "/api/v1/journey/session/update-area",
                                "method": "POST",
                                "handler": self.update_area_state,
                                "metadata": {
                                    "description": "Update area state",
                                    "parameters": ["session_id", "area_id", "updates", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.update_area_state",
                            "semantic_api": "/api/v1/journey/session/update-area",
                            "user_journey": "update_area_state"
                        }
                    },
                    {
                        "name": "context_preservation",
                        "protocol": "SessionJourneyOrchestratorProtocol",
                        "description": "Preserve context across area navigation",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_session_state",
                                "endpoint": "/api/v1/journey/session/state",
                                "method": "GET",
                                "handler": self.get_session_state,
                                "metadata": {
                                    "description": "Get session state with preserved context",
                                    "parameters": ["session_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.get_session_state",
                            "semantic_api": "/api/v1/journey/session/state",
                            "user_journey": "get_session_state"
                        }
                    }
                ],
                soa_apis=[
                    "start_session", "navigate_to_area", "get_session_state", "end_session",
                    "get_area_state", "update_area_state", "get_available_areas",
                    "get_available_actions", "check_area_completion", "get_session_progress"
                ],
                mcp_tools=[]  # Journey services provide SOA APIs, not MCP tools
            )
            
            # Record health metric
            await self.record_health_metric(
                "session_journey_orchestrator_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "session_journey_orchestrator_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Session Journey Orchestrator Service initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "session_journey_orchestrator_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "session_journey_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Session Journey Orchestrator Service initialization failed: {e}")
            return False
    
    async def _discover_experience_services(self):
        """Discover Experience services via Curator."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            
            if curator:
                try:
                    self.frontend_gateway = await curator.discover_service_by_name("FrontendGatewayService")
                    self.logger.info("✅ Discovered FrontendGatewayService")
                except Exception:
                    self.logger.warning("⚠️ FrontendGatewayService not yet available")
                
                try:
                    self.user_experience = await curator.discover_service_by_name("UserExperienceService")
                    self.logger.info("✅ Discovered UserExperienceService")
                except Exception:
                    self.logger.warning("⚠️ UserExperienceService not yet available")
                
                try:
                    self.session_manager = await curator.discover_service_by_name("SessionManagerService")
                    self.logger.info("✅ Discovered SessionManagerService")
                except Exception:
                    self.logger.warning("⚠️ SessionManagerService not yet available")
            
        except Exception as e:
            self.logger.error(f"❌ Experience service discovery failed: {e}")
    
    async def _discover_journey_services(self):
        """Discover other Journey services via Curator."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            
            if curator:
                try:
                    self.journey_analytics = await curator.discover_service_by_name("JourneyAnalyticsService")
                    self.logger.info("✅ Discovered JourneyAnalyticsService")
                except Exception:
                    self.logger.warning("⚠️ JourneyAnalyticsService not yet available")
                
                try:
                    self.milestone_tracker = await curator.discover_service_by_name("JourneyMilestoneTrackerService")
                    self.logger.info("✅ Discovered JourneyMilestoneTrackerService")
                except Exception:
                    self.logger.warning("⚠️ JourneyMilestoneTrackerService not yet available")
            
        except Exception as e:
            self.logger.error(f"❌ Journey service discovery failed: {e}")
    
    # ========================================================================
    # SOA APIs (Session Management)
    # ========================================================================
    
    async def start_session(
        self,
        user_id: str,
        session_config: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a new session journey (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            user_id: User ID
            session_config: Session configuration (areas, initial area, etc.)
            user_context: User context for security and tenant validation
        
        Returns:
            Session data
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "start_session_start",
            success=True,
            details={"user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "start_session", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "start_session",
                    details={"user_id": user_id}
                )
                await self.record_health_metric("start_session_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("start_session_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                # For journey services, the resource tenant is the same as user tenant (user owns their journey)
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
                                "start_session",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("start_session_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("start_session_complete", success=False)
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
            session_id = str(uuid.uuid4())
            
            # Create session via SessionManager (Experience)
            if self.session_manager:
                session_result = await self.session_manager.create_session(user_id, {
                    "session_type": "free_navigation",
                    "config": session_config
                })
                experience_session_id = session_result.get("session", {}).get("session_id")
            else:
                experience_session_id = None
            
            # Initialize area states
            areas = session_config.get("areas", [])
            area_states = {}
            for area in areas:
                area_states[area["area_id"]] = {
                    "area_id": area["area_id"],
                    "area_name": area["area_name"],
                    "status": "not_started",
                    "visited_count": 0,
                    "last_visited": None,
                    "context": {},
                    "completion_criteria": area.get("completion_criteria", {})
                }
            
            # Create session
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "experience_session_id": experience_session_id,
                "areas": area_states,
                "current_area": session_config.get("initial_area"),
                "navigation_history": [],
                "started_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "config": session_config
            }
            
            # Store in cache
            self.active_sessions[session_id] = session
            
            # Persist via TrafficCop (for state synchronization)
            if self.traffic_cop:
                try:
                    # TrafficCop.update_session expects updates dict, not full session
                    await self.traffic_cop.update_session(session_id, {"session_data": session}, user_context=user_context)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to persist session state via TrafficCop: {e}")
            
            # Store via Librarian for analytics
            await self.store_document(
                document_data=session,
                metadata={
                    "type": "session_journey",
                    "session_id": session_id,
                    "user_id": user_id
                }
            )
            
            # Record health metric (success)
            await self.record_health_metric("start_session_success", 1.0, {"session_id": session_id, "user_id": user_id, "areas_count": len(area_states)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("start_session_complete", success=True, details={"session_id": session_id, "user_id": user_id})
            
            self.logger.info(f"✅ Session journey started: {session_id} for user {user_id}")
            
            return {
                "success": True,
                "session": session
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "start_session", details={"user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("start_session_failed", 1.0, {"user_id": user_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("start_session_complete", success=False, details={"user_id": user_id, "error": str(e)})
            
            self.logger.error(f"❌ Start session failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def navigate_to_area(
        self,
        session_id: str,
        area_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Navigate to a specific area (SOA API - FREE NAVIGATION!).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            area_id: Area ID to navigate to
            user_context: User context for security and tenant validation
        
        Returns:
            Navigation result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "navigate_to_area_start",
            success=True,
            details={"session_id": session_id, "area_id": area_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "navigate_to_area", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "navigate_to_area",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id, "area_id": area_id}
                )
                await self.record_health_metric("navigate_to_area_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("navigate_to_area_complete", success=False)
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
                                "navigate_to_area",
                                details={"tenant_id": tenant_id, "session_id": session_id, "area_id": area_id}
                            )
                            await self.record_health_metric("navigate_to_area_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("navigate_to_area_complete", success=False)
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
            # Get session
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
            else:
                # Try to restore from TrafficCop
                if self.traffic_cop:
                    restore_result = await self.traffic_cop.restore_session_state(session_id)
                    if restore_result.get("success"):
                        session = restore_result["session"]
                        self.active_sessions[session_id] = session
                    else:
                        return {
                            "success": False,
                            "error": "Session not found"
                        }
                else:
                    return {
                        "success": False,
                        "error": "Session not found"
                    }
            
            # Check if area exists
            if area_id not in session["areas"]:
                return {
                    "success": False,
                    "error": f"Area '{area_id}' not found in session"
                }
            
            # Update previous area (if any)
            if session.get("current_area") and session["current_area"] in session["areas"]:
                prev_area = session["areas"][session["current_area"]]
                if prev_area["status"] == "not_started":
                    prev_area["status"] = "visited"
            
            # Navigate to new area
            area = session["areas"][area_id]
            area["visited_count"] += 1
            area["last_visited"] = datetime.utcnow().isoformat()
            if area["status"] == "not_started":
                area["status"] = "in_progress"
            
            # Update session
            session["current_area"] = area_id
            session["navigation_history"].append({
                "area_id": area_id,
                "navigated_at": datetime.utcnow().isoformat()
            })
            session["last_activity"] = datetime.utcnow().isoformat()
            
            # Update cache
            self.active_sessions[session_id] = session
            
            # Persist via TrafficCop (for state synchronization)
            if self.traffic_cop:
                try:
                    # TrafficCop.update_session expects updates dict, not full session
                    await self.traffic_cop.update_session(session_id, {"session_data": session}, user_context=user_context)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to persist session state via TrafficCop: {e}")
            
            # Track interaction via UserExperience
            if self.user_experience:
                await self.user_experience.track_user_interaction(session["user_id"], {
                    "type": "area_navigation",
                    "session_id": session_id,
                    "area_id": area_id
                })
            
            # Record health metric (success)
            await self.record_health_metric("navigate_to_area_success", 1.0, {"session_id": session_id, "area_id": area_id, "visited_count": area.get("visited_count", 0)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("navigate_to_area_complete", success=True, details={"session_id": session_id, "area_id": area_id})
            
            self.logger.info(f"✅ Navigated to area: {area_id} in session {session_id}")
            
            return {
                "success": True,
                "area": area,
                "session": session
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "navigate_to_area", details={"session_id": session_id, "area_id": area_id})
            
            # Record health metric (failure)
            await self.record_health_metric("navigate_to_area_failed", 1.0, {"session_id": session_id, "area_id": area_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("navigate_to_area_complete", success=False, details={"session_id": session_id, "area_id": area_id, "error": str(e)})
            
            self.logger.error(f"❌ Navigate to area failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session_state(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get complete session state (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            user_context: User context for security and tenant validation
        
        Returns:
            Session state
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_session_state_start",
            success=True,
            details={"session_id": session_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_session_state", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_session_state",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id}
                )
                await self.record_health_metric("get_session_state_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_session_state_complete", success=False)
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
                                "get_session_state",
                                details={"tenant_id": tenant_id, "session_id": session_id}
                            )
                            await self.record_health_metric("get_session_state_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_session_state_complete", success=False)
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
            if session_id in self.active_sessions:
                # Record health metric (success)
                await self.record_health_metric("get_session_state_success", 1.0, {"session_id": session_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_session_state_complete", success=True, details={"session_id": session_id})
                
                return {
                    "success": True,
                    "session": self.active_sessions[session_id]
                }
            
            # Try to restore from TrafficCop
            if self.traffic_cop:
                restore_result = await self.traffic_cop.restore_session_state(session_id)
                if restore_result.get("success"):
                    session = restore_result["session"]
                    self.active_sessions[session_id] = session
                    
                    # Record health metric (success)
                    await self.record_health_metric("get_session_state_success", 1.0, {"session_id": session_id})
                    
                    # End telemetry tracking
                    await self.log_operation_with_telemetry("get_session_state_complete", success=True, details={"session_id": session_id})
                    
                    return {
                        "success": True,
                        "session": session
                    }
            
            # Record health metric (not found)
            await self.record_health_metric("get_session_state_not_found", 1.0, {"session_id": session_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_session_state_complete", success=False, details={"session_id": session_id, "error": "Session not found"})
            
            return {
                "success": False,
                "error": "Session not found"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_session_state", details={"session_id": session_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_session_state_failed", 1.0, {"session_id": session_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_session_state_complete", success=False, details={"session_id": session_id, "error": str(e)})
            
            self.logger.error(f"❌ Get session state failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def end_session(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        End session journey (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            user_context: User context for security and tenant validation
        
        Returns:
            End session result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "end_session_start",
            success=True,
            details={"session_id": session_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "end_session", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "end_session",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id}
                )
                await self.record_health_metric("end_session_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("end_session_complete", success=False)
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
                                "end_session",
                                details={"tenant_id": tenant_id, "session_id": session_id}
                            )
                            await self.record_health_metric("end_session_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("end_session_complete", success=False)
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
            # Get session
            session_result = await self.get_session_state(session_id, user_context=user_context)
            if not session_result.get("success"):
                await self.log_operation_with_telemetry("end_session_complete", success=False, details={"session_id": session_id})
                return session_result
            
            session = session_result["session"]
            
            # Mark as ended
            session["status"] = "ended"
            session["ended_at"] = datetime.utcnow().isoformat()
            
            # Persist final state via Librarian
            await self.store_document(
                document_data=session,
                metadata={
                    "type": "session_journey",
                    "session_id": session_id,
                    "status": "ended"
                }
            )
            
            # Remove from cache
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Record health metric (success)
            await self.record_health_metric("end_session_success", 1.0, {"session_id": session_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("end_session_complete", success=True, details={"session_id": session_id})
            
            self.logger.info(f"✅ Session ended: {session_id}")
            
            return {
                "success": True,
                "session": session
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "end_session", details={"session_id": session_id})
            
            # Record health metric (failure)
            await self.record_health_metric("end_session_failed", 1.0, {"session_id": session_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("end_session_complete", success=False, details={"session_id": session_id, "error": str(e)})
            
            self.logger.error(f"❌ End session failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Area Management)
    # ========================================================================
    
    async def get_area_state(
        self,
        session_id: str,
        area_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get state of specific area (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            area_id: Area ID
            user_context: User context for security and tenant validation
        
        Returns:
            Area state
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_area_state_start",
            success=True,
            details={"session_id": session_id, "area_id": area_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_area_state", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_area_state",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id, "area_id": area_id}
                )
                await self.record_health_metric("get_area_state_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_area_state_complete", success=False)
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
                                "get_area_state",
                                details={"tenant_id": tenant_id, "session_id": session_id, "area_id": area_id}
                            )
                            await self.record_health_metric("get_area_state_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_area_state_complete", success=False)
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
            session_result = await self.get_session_state(session_id, user_context=user_context)
            if not session_result.get("success"):
                await self.log_operation_with_telemetry("get_area_state_complete", success=False, details={"session_id": session_id, "area_id": area_id})
                return session_result
            
            session = session_result["session"]
            
            if area_id not in session["areas"]:
                # Record health metric (not found)
                await self.record_health_metric("get_area_state_not_found", 1.0, {"session_id": session_id, "area_id": area_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_area_state_complete", success=False, details={"session_id": session_id, "area_id": area_id, "error": "Area not found"})
                
                return {
                    "success": False,
                    "error": f"Area '{area_id}' not found"
                }
            
            # Record health metric (success)
            await self.record_health_metric("get_area_state_success", 1.0, {"session_id": session_id, "area_id": area_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_area_state_complete", success=True, details={"session_id": session_id, "area_id": area_id})
            
            return {
                "success": True,
                "area": session["areas"][area_id]
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_area_state", details={"session_id": session_id, "area_id": area_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_area_state_failed", 1.0, {"session_id": session_id, "area_id": area_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_area_state_complete", success=False, details={"session_id": session_id, "area_id": area_id, "error": str(e)})
            
            self.logger.error(f"❌ Get area state failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_area_state(
        self,
        session_id: str,
        area_id: str,
        updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update state of specific area (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            area_id: Area ID
            updates: State updates
            user_context: User context for security and tenant validation
        
        Returns:
            Updated area state
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "update_area_state_start",
            success=True,
            details={"session_id": session_id, "area_id": area_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "update_area_state", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "update_area_state",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id, "area_id": area_id}
                )
                await self.record_health_metric("update_area_state_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("update_area_state_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                # Handle both sync and async validate_tenant_access
                try:
                    # DEBUG: Log tenant utility state
                    self.logger.info(f"🔍 Tenant validation debug - tenant_id: {tenant_id}, tenant type: {type(tenant)}")
                    self.logger.info(f"🔍 Tenant utility has multi_tenant_enabled: {hasattr(tenant, 'multi_tenant_enabled')}")
                    if hasattr(tenant, 'multi_tenant_enabled'):
                        self.logger.info(f"🔍 Tenant utility multi_tenant_enabled value: {tenant.multi_tenant_enabled}")
                    
                    # Check if tenant management is configured (multi-tenancy enabled)
                    # If not configured, allow access by default (open by default)
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    self.logger.info(f"🔍 Tenant management configured: {is_configured}")
                    
                    if is_configured:
                        # Only validate if tenant management is actually configured
                        self.logger.info(f"🔍 Validating tenant access - user_tenant_id: {tenant_id}, resource_tenant_id: {tenant_id}")
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        self.logger.info(f"🔍 Tenant validation result: {is_valid}")
                        
                        if not is_valid:
                            self.logger.warning(f"⚠️ Tenant validation failed - user_tenant_id: {tenant_id}, resource_tenant_id: {tenant_id}")
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "update_area_state",
                                details={"tenant_id": tenant_id, "session_id": session_id, "area_id": area_id}
                            )
                            await self.record_health_metric("update_area_state_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("update_area_state_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        # Tenant management not configured - allow access by default (open by default)
                        self.logger.info(f"✅ Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    # If tenant validation fails due to configuration issues, allow access (open by default)
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
                    import traceback
                    self.logger.debug(f"🔍 Tenant validation exception traceback: {traceback.format_exc()}")
        
        try:
            session_result = await self.get_session_state(session_id, user_context=user_context)
            if not session_result.get("success"):
                await self.log_operation_with_telemetry("update_area_state_complete", success=False, details={"session_id": session_id, "area_id": area_id})
                return session_result
            
            session = session_result["session"]
            
            if area_id not in session["areas"]:
                return {
                    "success": False,
                    "error": f"Area '{area_id}' not found"
                }
            
            # Update area context
            area = session["areas"][area_id]
            area["context"].update(updates)
            area["last_updated"] = datetime.utcnow().isoformat()
            
            # Update session
            self.active_sessions[session_id] = session
            
            # Persist via TrafficCop (for state synchronization)
            if self.traffic_cop:
                try:
                    # TrafficCop.update_session expects updates dict, not full session
                    await self.traffic_cop.update_session(session_id, {"session_data": session}, user_context=user_context)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to persist session state via TrafficCop: {e}")
            
            # Record health metric (success)
            await self.record_health_metric("update_area_state_success", 1.0, {"session_id": session_id, "area_id": area_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("update_area_state_complete", success=True, details={"session_id": session_id, "area_id": area_id})
            
            self.logger.info(f"✅ Area state updated: {area_id} in session {session_id}")
            
            return {
                "success": True,
                "area": area
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "update_area_state", details={"session_id": session_id, "area_id": area_id})
            
            # Record health metric (failure)
            await self.record_health_metric("update_area_state_failed", 1.0, {"session_id": session_id, "area_id": area_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("update_area_state_complete", success=False, details={"session_id": session_id, "area_id": area_id, "error": str(e)})
            
            self.logger.error(f"❌ Update area state failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_areas(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all available areas in session (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            user_context: User context for security and tenant validation
        
        Returns:
            Available areas
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_available_areas_start",
            success=True,
            details={"session_id": session_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_available_areas", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_available_areas",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id}
                )
                await self.record_health_metric("get_available_areas_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_available_areas_complete", success=False)
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
                                "get_available_areas",
                                details={"tenant_id": tenant_id, "session_id": session_id}
                            )
                            await self.record_health_metric("get_available_areas_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_available_areas_complete", success=False)
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
            session_result = await self.get_session_state(session_id, user_context=user_context)
            if not session_result.get("success"):
                await self.log_operation_with_telemetry("get_available_areas_complete", success=False, details={"session_id": session_id})
                return session_result
            
            session = session_result["session"]
            
            # Record health metric (success)
            await self.record_health_metric("get_available_areas_success", 1.0, {"session_id": session_id, "areas_count": len(session["areas"])})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_available_areas_complete", success=True, details={"session_id": session_id, "areas_count": len(session["areas"])})
            
            return {
                "success": True,
                "areas": list(session["areas"].values())
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_available_areas", details={"session_id": session_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_available_areas_failed", 1.0, {"session_id": session_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_available_areas_complete", success=False, details={"session_id": session_id, "error": str(e)})
            
            self.logger.error(f"❌ Get available areas failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_actions(
        self,
        session_id: str,
        area_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get available actions for specific area (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            area_id: Area ID
            user_context: User context for security and tenant validation
        
        Returns:
            Available actions
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_available_actions_start",
            success=True,
            details={"session_id": session_id, "area_id": area_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_available_actions", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_available_actions",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id, "area_id": area_id}
                )
                await self.record_health_metric("get_available_actions_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_available_actions_complete", success=False)
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
                                "get_available_actions",
                                details={"tenant_id": tenant_id, "session_id": session_id, "area_id": area_id}
                            )
                            await self.record_health_metric("get_available_actions_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_available_actions_complete", success=False)
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
            area_result = await self.get_area_state(session_id, area_id, user_context=user_context)
            if not area_result.get("success"):
                await self.log_operation_with_telemetry("get_available_actions_complete", success=False, details={"session_id": session_id, "area_id": area_id})
                return area_result
            
            area = area_result["area"]
            
            # Get actions from area config
            actions = area.get("context", {}).get("available_actions", [])
            
            # Record health metric (success)
            await self.record_health_metric("get_available_actions_success", 1.0, {"session_id": session_id, "area_id": area_id, "actions_count": len(actions)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_available_actions_complete", success=True, details={"session_id": session_id, "area_id": area_id, "actions_count": len(actions)})
            
            return {
                "success": True,
                "area_id": area_id,
                "actions": actions
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_available_actions", details={"session_id": session_id, "area_id": area_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_available_actions_failed", 1.0, {"session_id": session_id, "area_id": area_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_available_actions_complete", success=False, details={"session_id": session_id, "area_id": area_id, "error": str(e)})
            
            self.logger.error(f"❌ Get available actions failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_area_completion(
        self,
        session_id: str,
        area_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check if area completion criteria are met (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            area_id: Area ID
            user_context: User context for security and tenant validation
        
        Returns:
            Completion status
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "check_area_completion_start",
            success=True,
            details={"session_id": session_id, "area_id": area_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "check_area_completion", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "check_area_completion",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id, "area_id": area_id}
                )
                await self.record_health_metric("check_area_completion_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("check_area_completion_complete", success=False)
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
                                "check_area_completion",
                                details={"tenant_id": tenant_id, "session_id": session_id, "area_id": area_id}
                            )
                            await self.record_health_metric("check_area_completion_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("check_area_completion_complete", success=False)
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
            area_result = await self.get_area_state(session_id, area_id, user_context=user_context)
            if not area_result.get("success"):
                await self.log_operation_with_telemetry("check_area_completion_complete", success=False, details={"session_id": session_id, "area_id": area_id})
                return area_result
            
            area = area_result["area"]
            criteria = area.get("completion_criteria", {})
            context = area.get("context", {})
            
            # Check each criterion
            all_met = True
            criteria_status = {}
            
            for criterion_name, criterion_value in criteria.items():
                met = context.get(criterion_name) == criterion_value
                criteria_status[criterion_name] = {
                    "required": criterion_value,
                    "current": context.get(criterion_name),
                    "met": met
                }
                if not met:
                    all_met = False
            
            # Update area status if complete
            if all_met and area["status"] != "completed":
                area["status"] = "completed"
                area["completed_at"] = datetime.utcnow().isoformat()
                
                # Update session
                session_result = await self.get_session_state(session_id, user_context=user_context)
                session = session_result["session"]
                self.active_sessions[session_id] = session
                
                # Persist via TrafficCop (for state synchronization)
                if self.traffic_cop:
                    try:
                        await self.traffic_cop.update_session(session_id, session, user_context=user_context)
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to persist session state via TrafficCop: {e}")
            
            # Record health metric (success)
            await self.record_health_metric("check_area_completion_success", 1.0, {"session_id": session_id, "area_id": area_id, "completed": all_met})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("check_area_completion_complete", success=True, details={"session_id": session_id, "area_id": area_id, "completed": all_met})
            
            return {
                "success": True,
                "area_id": area_id,
                "completed": all_met,
                "criteria_status": criteria_status
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "check_area_completion", details={"session_id": session_id, "area_id": area_id})
            
            # Record health metric (failure)
            await self.record_health_metric("check_area_completion_failed", 1.0, {"session_id": session_id, "area_id": area_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("check_area_completion_complete", success=False, details={"session_id": session_id, "area_id": area_id, "error": str(e)})
            
            self.logger.error(f"❌ Check area completion failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session_progress(
        self,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get overall session progress (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            session_id: Session ID
            user_context: User context for security and tenant validation
        
        Returns:
            Session progress
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_session_progress_start",
            success=True,
            details={"session_id": session_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_session_progress", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_session_progress",
                    details={"user_id": user_context.get("user_id"), "session_id": session_id}
                )
                await self.record_health_metric("get_session_progress_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_session_progress_complete", success=False)
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
                                "get_session_progress",
                                details={"tenant_id": tenant_id, "session_id": session_id}
                            )
                            await self.record_health_metric("get_session_progress_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_session_progress_complete", success=False)
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
            session_result = await self.get_session_state(session_id, user_context=user_context)
            if not session_result.get("success"):
                await self.log_operation_with_telemetry("get_session_progress_complete", success=False, details={"session_id": session_id})
                return session_result
            
            session = session_result["session"]
            
            # Calculate progress
            total_areas = len(session["areas"])
            completed_areas = len([a for a in session["areas"].values() if a.get("status") == "completed"])
            visited_areas = len([a for a in session["areas"].values() if a.get("visited_count", 0) > 0])
            
            progress = {
                "session_id": session_id,
                "total_areas": total_areas,
                "completed_areas": completed_areas,
                "visited_areas": visited_areas,
                "completion_percent": (completed_areas / total_areas) * 100 if total_areas > 0 else 0,
                "current_area": session.get("current_area"),
                "navigation_count": len(session.get("navigation_history", []))
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_session_progress_success", 1.0, {"session_id": session_id, "completion_percent": progress.get("completion_percent", 0)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_session_progress_complete", success=True, details={"session_id": session_id, "completion_percent": progress.get("completion_percent", 0)})
            
            return {
                "success": True,
                "progress": progress
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_session_progress", details={"session_id": session_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_session_progress_failed", 1.0, {"session_id": session_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_session_progress_complete", success=False, details={"session_id": session_id, "error": str(e)})
            
            self.logger.error(f"❌ Get session progress failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "active_sessions": len(self.active_sessions),
            "experience_services_available": {
                "frontend_gateway": self.frontend_gateway is not None,
                "user_experience": self.user_experience is not None,
                "session_manager": self.session_manager is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "journey_service",
            "realm": "journey",
            "layer": "session_orchestration",
            "navigation_type": "free_form",
            "capabilities": ["session_orchestration", "free_navigation", "area_tracking", "context_preservation"],
            "soa_apis": [
                "start_session", "navigate_to_area", "get_session_state", "end_session",
                "get_area_state", "update_area_state", "get_available_areas",
                "get_available_actions", "check_area_completion", "get_session_progress"
            ],
            "mcp_tools": [],
            "composes": "experience_services"
        }








