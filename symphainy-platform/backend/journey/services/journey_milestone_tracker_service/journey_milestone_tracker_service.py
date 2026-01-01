#!/usr/bin/env python3
"""
Journey Milestone Tracker Service

WHAT: Tracks user progress through journey milestones with detailed state management
HOW: Composes Experience services and Smart City to track milestone completion, timing, and state

This service provides milestone tracking by recording milestone events,
managing milestone dependencies, and providing progress visualization data.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class JourneyMilestoneTrackerService(RealmServiceBase):
    """
    Journey Milestone Tracker Service for Journey realm.
    
    Tracks user progress through journey milestones by composing
    Experience services (SessionManager, UserExperience) and Smart City services.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Journey Milestone Tracker Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.data_steward = None
        self.post_office = None
        
        # Experience services (discovered via Curator)
        self.session_manager = None
        self.user_experience = None
        
        # Milestone tracking cache
        self.milestone_states: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> bool:
        """
        Initialize Journey Milestone Tracker Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "journey_milestone_tracker_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.librarian = await self.get_librarian_api()
            self.data_steward = await self.get_data_steward_api()
            self.post_office = await self.get_post_office_api()
            
            # 2. Discover Experience services via Curator
            await self._discover_experience_services()
            
            # 3. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "milestone_tracking",
                        "protocol": "JourneyMilestoneTrackerProtocol",
                        "description": "Track milestone start and completion",
                        "contracts": {
                            "soa_api": {
                                "api_name": "track_milestone_start",
                                "endpoint": "/api/v1/journey/milestones/track-start",
                                "method": "POST",
                                "handler": self.track_milestone_start,
                                "metadata": {
                                    "description": "Track milestone start",
                                    "parameters": ["journey_id", "user_id", "milestone_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.track_milestone_start",
                            "semantic_api": "/api/v1/journey/milestones/track-start",
                            "user_journey": "track_milestone_start"
                        }
                    },
                    {
                        "name": "progress_monitoring",
                        "protocol": "JourneyMilestoneTrackerProtocol",
                        "description": "Monitor journey progress and milestone status",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_journey_progress",
                                "endpoint": "/api/v1/journey/milestones/progress",
                                "method": "POST",
                                "handler": self.get_journey_progress,
                                "metadata": {
                                    "description": "Get overall journey progress",
                                    "parameters": ["journey_id", "user_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.get_progress",
                            "semantic_api": "/api/v1/journey/milestones/progress",
                            "user_journey": "get_journey_progress"
                        }
                    },
                    {
                        "name": "milestone_management",
                        "protocol": "JourneyMilestoneTrackerProtocol",
                        "description": "Manage milestones (retry, rollback, skip)",
                        "contracts": {
                            "soa_api": {
                                "api_name": "retry_milestone",
                                "endpoint": "/api/v1/journey/milestones/retry",
                                "method": "POST",
                                "handler": self.retry_milestone,
                                "metadata": {
                                    "description": "Retry a failed milestone",
                                    "parameters": ["journey_id", "user_id", "milestone_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.retry_milestone",
                            "semantic_api": "/api/v1/journey/milestones/retry",
                            "user_journey": "retry_milestone"
                        }
                    },
                    {
                        "name": "milestone_analytics",
                        "protocol": "JourneyMilestoneTrackerProtocol",
                        "description": "Get milestone analytics and history",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_milestone_analytics",
                                "endpoint": "/api/v1/journey/milestones/analytics",
                                "method": "POST",
                                "handler": self.get_milestone_analytics,
                                "metadata": {
                                    "description": "Get analytics for a specific milestone",
                                    "parameters": ["milestone_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.get_milestone_analytics",
                            "semantic_api": "/api/v1/journey/milestones/analytics",
                            "user_journey": "get_milestone_analytics"
                        }
                    }
                ],
                soa_apis=[
                    "track_milestone_start", "track_milestone_complete", "get_milestone_status",
                    "get_journey_progress", "retry_milestone", "rollback_milestone",
                    "skip_milestone", "get_milestone_history", "get_milestone_analytics"
                ],
                mcp_tools=[]  # Journey services provide SOA APIs, not MCP tools
            )
            
            # Record health metric
            await self.record_health_metric(
                "journey_milestone_tracker_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "journey_milestone_tracker_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Journey Milestone Tracker Service initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "journey_milestone_tracker_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "journey_milestone_tracker_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Journey Milestone Tracker Service initialization failed: {e}")
            return False
    
    async def _discover_experience_services(self):
        """Discover Experience services via Curator."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            
            if curator:
                try:
                    self.session_manager = await curator.discover_service_by_name("SessionManagerService")
                    self.logger.info("✅ Discovered SessionManagerService")
                except Exception:
                    self.logger.warning("⚠️ SessionManagerService not yet available")
                
                try:
                    self.user_experience = await curator.discover_service_by_name("UserExperienceService")
                    self.logger.info("✅ Discovered UserExperienceService")
                except Exception:
                    self.logger.warning("⚠️ UserExperienceService not yet available")
            
        except Exception as e:
            self.logger.error(f"❌ Experience service discovery failed: {e}")
    
    # ========================================================================
    # SOA APIs (Milestone Tracking)
    # ========================================================================
    
    async def track_milestone_start(
        self,
        journey_id: str,
        user_id: str,
        milestone_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track milestone start (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            milestone_id: Milestone ID
            user_context: User context for security and tenant validation
        
        Returns:
            Tracking result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "track_milestone_start_start",
            success=True,
            details={"journey_id": journey_id, "milestone_id": milestone_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "track_milestone_start", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "track_milestone_start",
                    details={"user_id": user_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("track_milestone_start_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("track_milestone_start_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "track_milestone_start",
                    details={"tenant_id": tenant_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("track_milestone_start_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("track_milestone_start_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Create milestone tracking entry
            tracking_key = f"{journey_id}_{user_id}_{milestone_id}"
            
            milestone_state = {
                "journey_id": journey_id,
                "user_id": user_id,
                "milestone_id": milestone_id,
                "status": "in_progress",
                "started_at": datetime.utcnow().isoformat(),
                "attempts": 1
            }
            
            # Store in cache
            self.milestone_states[tracking_key] = milestone_state
            
            # Store via Librarian
            await self.store_document(
                document_data=milestone_state,
                metadata={
                    "type": "milestone_tracking",
                    "journey_id": journey_id,
                    "user_id": user_id,
                    "milestone_id": milestone_id
                }
            )
            
            # Track interaction via UserExperience
            if self.user_experience:
                await self.user_experience.track_user_interaction(user_id, {
                    "type": "milestone_start",
                    "journey_id": journey_id,
                    "milestone_id": milestone_id
                })
            
            # Record health metric (success)
            await self.record_health_metric("track_milestone_start_success", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("track_milestone_start_complete", success=True, details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            self.logger.info(f"✅ Milestone start tracked: {milestone_id} for journey {journey_id}")
            
            return {
                "success": True,
                "milestone_state": milestone_state
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "track_milestone_start", details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            # Record health metric (failure)
            await self.record_health_metric("track_milestone_start_failed", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("track_milestone_start_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id, "error": str(e)})
            
            self.logger.error(f"❌ Track milestone start failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def track_milestone_complete(
        self,
        journey_id: str,
        user_id: str,
        milestone_id: str,
        result: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track milestone completion (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            milestone_id: Milestone ID
            result: Milestone result data
            user_context: User context for security and tenant validation
        
        Returns:
            Tracking result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "track_milestone_complete_start",
            success=True,
            details={"journey_id": journey_id, "milestone_id": milestone_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "track_milestone_complete", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "track_milestone_complete",
                    details={"user_id": user_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("track_milestone_complete_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("track_milestone_complete_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "track_milestone_complete",
                    details={"tenant_id": tenant_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("track_milestone_complete_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("track_milestone_complete_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            tracking_key = f"{journey_id}_{user_id}_{milestone_id}"
            
            # Get milestone state
            if tracking_key in self.milestone_states:
                milestone_state = self.milestone_states[tracking_key]
            else:
                # Try to retrieve from storage
                results = await self.search_documents(
                    "milestone_tracking",
                    {"type": "milestone_tracking", "journey_id": journey_id, "user_id": user_id, "milestone_id": milestone_id}
                )
                
                if results and len(results) > 0:
                    milestone_state = results[0].get("document") if isinstance(results[0], dict) else results[0]
                else:
                    milestone_state = {
                        "journey_id": journey_id,
                        "user_id": user_id,
                        "milestone_id": milestone_id,
                        "started_at": datetime.utcnow().isoformat()
                    }
            
            # Update state
            milestone_state["status"] = "completed"
            milestone_state["completed_at"] = datetime.utcnow().isoformat()
            milestone_state["result"] = result
            
            # Calculate duration
            if "started_at" in milestone_state:
                start = datetime.fromisoformat(milestone_state["started_at"])
                end = datetime.fromisoformat(milestone_state["completed_at"])
                milestone_state["duration_seconds"] = (end - start).total_seconds()
            
            # Update cache
            self.milestone_states[tracking_key] = milestone_state
            
            # Store via Librarian
            await self.store_document(
                document_data=milestone_state,
                metadata={
                    "type": "milestone_tracking",
                    "journey_id": journey_id,
                    "user_id": user_id,
                    "milestone_id": milestone_id,
                    "status": "completed"
                }
            )
            
            # Send notification via PostOffice
            if self.post_office:
                await self.send_notification(
                    recipient=user_id,
                    message={
                        "type": "milestone_complete",
                        "journey_id": journey_id,
                        "milestone_id": milestone_id
                    }
                )
            
            # Track interaction via UserExperience
            if self.user_experience:
                await self.user_experience.track_user_interaction(user_id, {
                    "type": "milestone_complete",
                    "journey_id": journey_id,
                    "milestone_id": milestone_id,
                    "duration": milestone_state.get("duration_seconds", 0)
                })
            
            # Record health metric (success)
            await self.record_health_metric("track_milestone_complete_success", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("track_milestone_complete_complete", success=True, details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            self.logger.info(f"✅ Milestone complete tracked: {milestone_id} for journey {journey_id}")
            
            return {
                "success": True,
                "milestone_state": milestone_state
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "track_milestone_complete", details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            # Record health metric (failure)
            await self.record_health_metric("track_milestone_complete_failed", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("track_milestone_complete_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id, "error": str(e)})
            
            self.logger.error(f"❌ Track milestone complete failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_milestone_status(
        self,
        journey_id: str,
        user_id: str,
        milestone_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get milestone status (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            milestone_id: Milestone ID
            user_context: User context for security and tenant validation
        
        Returns:
            Milestone status
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_milestone_status_start",
            success=True,
            details={"journey_id": journey_id, "milestone_id": milestone_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_milestone_status", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_milestone_status",
                    details={"user_id": user_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("get_milestone_status_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_milestone_status_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_milestone_status",
                    details={"tenant_id": tenant_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("get_milestone_status_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_milestone_status_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            tracking_key = f"{journey_id}_{user_id}_{milestone_id}"
            
            # Check cache first
            if tracking_key in self.milestone_states:
                return {
                    "success": True,
                    "milestone_state": self.milestone_states[tracking_key]
                }
            
            # Try to retrieve from storage
            results = await self.search_documents(
                "milestone_tracking",
                {"type": "milestone_tracking", "journey_id": journey_id, "user_id": user_id, "milestone_id": milestone_id}
            )
            
            if results and len(results) > 0:
                milestone_state = results[0].get("document") if isinstance(results[0], dict) else results[0]
                # Update cache
                self.milestone_states[tracking_key] = milestone_state
                
                # Record health metric (success)
                await self.record_health_metric("get_milestone_status_success", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_milestone_status_complete", success=True, details={"journey_id": journey_id, "milestone_id": milestone_id})
                
                return {
                    "success": True,
                    "milestone_state": milestone_state
                }
            
            # Record health metric (not found)
            await self.record_health_metric("get_milestone_status_not_found", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_milestone_status_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id, "error": "Milestone not found"})
            
            return {
                "success": False,
                "error": "Milestone not found"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_milestone_status", details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_milestone_status_failed", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_milestone_status_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id, "error": str(e)})
            
            self.logger.error(f"❌ Get milestone status failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_journey_progress(
        self,
        journey_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get overall journey progress for user (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            user_context: User context for security and tenant validation
        
        Returns:
            Journey progress
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_journey_progress_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_journey_progress", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_journey_progress",
                    details={"user_id": user_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_journey_progress_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_journey_progress_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_journey_progress",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_journey_progress_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_journey_progress_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get all milestones for this journey/user
            results = await self.search_documents(
                "milestone_tracking",
                {"type": "milestone_tracking", "journey_id": journey_id, "user_id": user_id}
            )
            
            if not results or len(results) == 0:
                return {
                    "success": True,
                    "progress": {
                        "journey_id": journey_id,
                        "user_id": user_id,
                        "progress_percent": 0,
                        "milestones_completed": 0,
                        "milestones_total": 0,
                        "milestones": []
                    }
                }
            
            milestones = [r["document"] for r in results["results"]]
            
            # Calculate progress
            completed = len([m for m in milestones if m.get("status") == "completed"])
            total = len(milestones)
            in_progress = [m for m in milestones if m.get("status") == "in_progress"]
            
            progress = {
                "journey_id": journey_id,
                "user_id": user_id,
                "progress_percent": (completed / total) * 100 if total > 0 else 0,
                "milestones_completed": completed,
                "milestones_total": total,
                "current_milestone": in_progress[0]["milestone_id"] if in_progress else None,
                "milestones": milestones
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_journey_progress_success", 1.0, {"journey_id": journey_id, "progress_percent": progress.get("progress_percent", 0)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_journey_progress_complete", success=True, details={"journey_id": journey_id, "progress_percent": progress.get("progress_percent", 0)})
            
            self.logger.info(f"✅ Journey progress retrieved: {journey_id} ({progress['progress_percent']:.1f}%)")
            
            return {
                "success": True,
                "progress": progress
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_journey_progress", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_journey_progress_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_journey_progress_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Get journey progress failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Milestone Management)
    # ========================================================================
    
    async def retry_milestone(
        self,
        journey_id: str,
        user_id: str,
        milestone_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Retry a failed milestone (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            milestone_id: Milestone ID
            user_context: User context for security and tenant validation
        
        Returns:
            Retry result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "retry_milestone_start",
            success=True,
            details={"journey_id": journey_id, "milestone_id": milestone_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "retry_milestone", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "retry_milestone",
                    details={"user_id": user_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("retry_milestone_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("retry_milestone_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "retry_milestone",
                    details={"tenant_id": tenant_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("retry_milestone_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("retry_milestone_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            tracking_key = f"{journey_id}_{user_id}_{milestone_id}"
            
            # Get milestone state
            status_result = await self.get_milestone_status(journey_id, user_id, milestone_id, user_context=user_context)
            if not status_result.get("success"):
                await self.log_operation_with_telemetry("retry_milestone_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id})
                return status_result
            
            milestone_state = status_result["milestone_state"]
            
            # Update for retry
            milestone_state["status"] = "in_progress"
            milestone_state["retried_at"] = datetime.utcnow().isoformat()
            milestone_state["attempts"] = milestone_state.get("attempts", 1) + 1
            
            # Update cache
            self.milestone_states[tracking_key] = milestone_state
            
            # Store via Librarian
            await self.store_document(
                document_data=milestone_state,
                metadata={
                    "type": "milestone_tracking",
                    "journey_id": journey_id,
                    "user_id": user_id,
                    "milestone_id": milestone_id,
                    "status": "retry"
                }
            )
            
            # Record health metric (success)
            await self.record_health_metric("retry_milestone_success", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id, "attempts": milestone_state.get("attempts", 1)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("retry_milestone_complete", success=True, details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            self.logger.info(f"✅ Milestone retry initiated: {milestone_id}")
            
            return {
                "success": True,
                "milestone_state": milestone_state
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "retry_milestone", details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            # Record health metric (failure)
            await self.record_health_metric("retry_milestone_failed", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("retry_milestone_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id, "error": str(e)})
            
            self.logger.error(f"❌ Retry milestone failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def rollback_milestone(
        self,
        journey_id: str,
        user_id: str,
        milestone_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Rollback a completed milestone (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            milestone_id: Milestone ID
            user_context: User context for security and tenant validation
        
        Returns:
            Rollback result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "rollback_milestone_start",
            success=True,
            details={"journey_id": journey_id, "milestone_id": milestone_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "rollback_milestone", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "rollback_milestone",
                    details={"user_id": user_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("rollback_milestone_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("rollback_milestone_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "rollback_milestone",
                    details={"tenant_id": tenant_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("rollback_milestone_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("rollback_milestone_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            tracking_key = f"{journey_id}_{user_id}_{milestone_id}"
            
            # Get milestone state
            status_result = await self.get_milestone_status(journey_id, user_id, milestone_id, user_context=user_context)
            if not status_result.get("success"):
                await self.log_operation_with_telemetry("rollback_milestone_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id})
                return status_result
            
            milestone_state = status_result["milestone_state"]
            
            # Rollback state
            milestone_state["status"] = "rolled_back"
            milestone_state["rolled_back_at"] = datetime.utcnow().isoformat()
            
            # Remove from cache
            if tracking_key in self.milestone_states:
                del self.milestone_states[tracking_key]
            
            # Store via Librarian
            await self.store_document(
                document_data=milestone_state,
                metadata={
                    "type": "milestone_tracking",
                    "journey_id": journey_id,
                    "user_id": user_id,
                    "milestone_id": milestone_id,
                    "status": "rolled_back"
                }
            )
            
            # Record health metric (success)
            await self.record_health_metric("rollback_milestone_success", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("rollback_milestone_complete", success=True, details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            self.logger.info(f"✅ Milestone rolled back: {milestone_id}")
            
            return {
                "success": True,
                "milestone_state": milestone_state
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "rollback_milestone", details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            # Record health metric (failure)
            await self.record_health_metric("rollback_milestone_failed", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("rollback_milestone_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id, "error": str(e)})
            
            self.logger.error(f"❌ Rollback milestone failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def skip_milestone(
        self,
        journey_id: str,
        user_id: str,
        milestone_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Skip an optional milestone (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            milestone_id: Milestone ID
            user_context: User context for security and tenant validation
        
        Returns:
            Skip result
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "skip_milestone_start",
            success=True,
            details={"journey_id": journey_id, "milestone_id": milestone_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "skip_milestone", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "skip_milestone",
                    details={"user_id": user_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("skip_milestone_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("skip_milestone_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "skip_milestone",
                    details={"tenant_id": tenant_id, "journey_id": journey_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("skip_milestone_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("skip_milestone_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            tracking_key = f"{journey_id}_{user_id}_{milestone_id}"
            
            milestone_state = {
                "journey_id": journey_id,
                "user_id": user_id,
                "milestone_id": milestone_id,
                "status": "skipped",
                "skipped_at": datetime.utcnow().isoformat()
            }
            
            # Update cache
            self.milestone_states[tracking_key] = milestone_state
            
            # Store via Librarian
            await self.store_document(
                document_data=milestone_state,
                metadata={
                    "type": "milestone_tracking",
                    "journey_id": journey_id,
                    "user_id": user_id,
                    "milestone_id": milestone_id,
                    "status": "skipped"
                }
            )
            
            # Record health metric (success)
            await self.record_health_metric("skip_milestone_success", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("skip_milestone_complete", success=True, details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            self.logger.info(f"✅ Milestone skipped: {milestone_id}")
            
            return {
                "success": True,
                "milestone_state": milestone_state
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "skip_milestone", details={"journey_id": journey_id, "milestone_id": milestone_id})
            
            # Record health metric (failure)
            await self.record_health_metric("skip_milestone_failed", 1.0, {"journey_id": journey_id, "milestone_id": milestone_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("skip_milestone_complete", success=False, details={"journey_id": journey_id, "milestone_id": milestone_id, "error": str(e)})
            
            self.logger.error(f"❌ Skip milestone failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Milestone Analytics)
    # ========================================================================
    
    async def get_milestone_history(
        self,
        journey_id: str,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get milestone history for user (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_id: User ID
            user_context: User context for security and tenant validation
        
        Returns:
            Milestone history
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_milestone_history_start",
            success=True,
            details={"journey_id": journey_id, "user_id": user_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_milestone_history", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_milestone_history",
                    details={"user_id": user_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_milestone_history_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_milestone_history_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_milestone_history",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_milestone_history_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_milestone_history_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get all milestones for this journey/user
            results = await self.search_documents(
                "milestone_tracking",
                {"type": "milestone_tracking", "journey_id": journey_id, "user_id": user_id}
            )
            
            if not results or len(results) == 0:
                return {
                    "success": True,
                    "history": []
                }
            
            milestones = [r["document"] for r in results["results"]]
            
            # Sort by started_at
            milestones.sort(key=lambda m: m.get("started_at", ""), reverse=True)
            
            # Record health metric (success)
            await self.record_health_metric("get_milestone_history_success", 1.0, {"journey_id": journey_id, "history_count": len(milestones)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_milestone_history_complete", success=True, details={"journey_id": journey_id, "history_count": len(milestones)})
            
            self.logger.info(f"✅ Milestone history retrieved: {journey_id}")
            
            return {
                "success": True,
                "history": milestones
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_milestone_history", details={"journey_id": journey_id, "user_id": user_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_milestone_history_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_milestone_history_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Get milestone history failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_milestone_analytics(
        self,
        milestone_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific milestone across all journeys (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            milestone_id: Milestone ID
            user_context: User context for security and tenant validation
        
        Returns:
            Milestone analytics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_milestone_analytics_start",
            success=True,
            details={"milestone_id": milestone_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_milestone_analytics", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_milestone_analytics",
                    details={"user_id": user_context.get("user_id"), "milestone_id": milestone_id}
                )
                await self.record_health_metric("get_milestone_analytics_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_milestone_analytics_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_milestone_analytics",
                    details={"tenant_id": tenant_id, "milestone_id": milestone_id}
                )
                await self.record_health_metric("get_milestone_analytics_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_milestone_analytics_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get all instances of this milestone
            results = await self.search_documents(
                "milestone_tracking",
                {"type": "milestone_tracking", "milestone_id": milestone_id}
            )
            
            if not results or len(results) == 0:
                return {
                    "success": True,
                    "analytics": {
                        "milestone_id": milestone_id,
                        "total_attempts": 0,
                        "completion_rate": 0,
                        "average_duration_seconds": 0
                    }
                }
            
            milestones = [r["document"] for r in results["results"]]
            
            # Calculate analytics
            total = len(milestones)
            completed = len([m for m in milestones if m.get("status") == "completed"])
            
            durations = [m["duration_seconds"] for m in milestones if "duration_seconds" in m]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            analytics = {
                "milestone_id": milestone_id,
                "total_attempts": total,
                "completion_rate": completed / total if total > 0 else 0,
                "average_duration_seconds": avg_duration,
                "completed": completed,
                "in_progress": len([m for m in milestones if m.get("status") == "in_progress"]),
                "skipped": len([m for m in milestones if m.get("status") == "skipped"]),
                "rolled_back": len([m for m in milestones if m.get("status") == "rolled_back"])
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_milestone_analytics_success", 1.0, {"milestone_id": milestone_id, "total_attempts": analytics.get("total_attempts", 0)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_milestone_analytics_complete", success=True, details={"milestone_id": milestone_id})
            
            self.logger.info(f"✅ Milestone analytics calculated: {milestone_id}")
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_milestone_analytics", details={"milestone_id": milestone_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_milestone_analytics_failed", 1.0, {"milestone_id": milestone_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_milestone_analytics_complete", success=False, details={"milestone_id": milestone_id, "error": str(e)})
            
            self.logger.error(f"❌ Get milestone analytics failed: {e}")
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
            "tracked_milestones": len(self.milestone_states),
            "experience_services_available": {
                "session_manager": self.session_manager is not None,
                "user_experience": self.user_experience is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "journey_service",
            "realm": "journey",
            "layer": "milestone_tracking",
            "capabilities": ["milestone_tracking", "progress_monitoring", "milestone_management", "milestone_analytics"],
            "soa_apis": [
                "track_milestone_start", "track_milestone_complete", "get_milestone_status",
                "get_journey_progress", "retry_milestone", "rollback_milestone",
                "skip_milestone", "get_milestone_history", "get_milestone_analytics"
            ],
            "mcp_tools": [],
            "composes": "experience_session_management"
        }

