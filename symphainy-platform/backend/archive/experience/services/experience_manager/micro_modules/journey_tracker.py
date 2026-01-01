#!/usr/bin/env python3
"""
Journey Tracker Micro-Module

Tracks user journeys, progress, and lifecycle management.

WHAT (Micro-Module): I track user journeys and progress
HOW (Implementation): I store journey data, track milestones, and manage journey lifecycle
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from experience.interfaces.journey_manager_interface import JourneyStage, JourneyStatus, FlowType


class JourneyTrackerModule:
    """
    Journey Tracker Micro-Module
    
    Provides functionality to track user journeys, progress, and lifecycle.
    """
    
    def __init__(self, environment: EnvironmentLoader, logger: Optional[logging.Logger] = None):
        """Initialize Journey Tracker Module."""
        self.environment = environment
        self.logger = logger or logging.getLogger(__name__)
        self.is_initialized = False
        
        # In-memory journey store (for MVP)
        # In a real system, this would be a persistent store (e.g., database)
        self.journeys: Dict[str, Dict[str, Any]] = {}
        
        # Journey configuration
        self.journey_timeout = timedelta(days=30)  # 30 day journey timeout
        self.max_journeys_per_user = 10  # Maximum concurrent journeys per user
        
        self.logger.info("🗺️ Journey Tracker Module initialized")
    
    async def initialize(self):
        """Initialize the Journey Tracker Module."""
        self.logger.info("🚀 Initializing Journey Tracker Module...")
        # Load any configurations or connect to persistent storage here
        self.is_initialized = True
        self.logger.info("✅ Journey Tracker Module initialized successfully")
    
    async def shutdown(self):
        """Shutdown the Journey Tracker Module."""
        self.logger.info("🛑 Shutting down Journey Tracker Module...")
        # Clean up resources or close connections here
        self.is_initialized = False
        self.logger.info("✅ Journey Tracker Module shutdown successfully")
    
    async def create_journey(self, user_context: UserContext, journey_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user journey.
        
        Args:
            user_context: Context of the user.
            journey_config: Configuration for the journey.
            
        Returns:
            A dictionary containing the journey ID and initial state.
        """
        self.logger.debug(f"Creating journey for user: {user_context.user_id}")
        
        try:
            # Check if user has reached maximum journey limit
            user_journeys = [j for j in self.journeys.values() if j.get("user_id") == user_context.user_id]
            if len(user_journeys) >= self.max_journeys_per_user:
                return {
                    "success": False,
                    "error": "Maximum journey limit reached",
                    "message": f"User can have maximum {self.max_journeys_per_user} concurrent journeys"
                }
            
            # Generate unique journey ID
            journey_id = str(uuid.uuid4())
            
            # Create journey data
            journey_info = {
                "journey_id": journey_id,
                "user_id": user_context.user_id,
                "user_context": user_context,
                "journey_config": journey_config,
                "status": JourneyStatus.ACTIVE.value,
                "stage": JourneyStage.ONBOARDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + self.journey_timeout).isoformat(),
                "progress": {
                    "current_milestone": 0,
                    "total_milestones": journey_config.get("total_milestones", 5),
                    "milestones_completed": [],
                    "milestones_remaining": list(range(1, journey_config.get("total_milestones", 5) + 1)),
                    "completion_percentage": 0.0
                },
                "flow": {
                    "flow_type": journey_config.get("flow_type", FlowType.LINEAR.value),
                    "current_step": 1,
                    "total_steps": journey_config.get("total_steps", 10),
                    "steps_completed": [],
                    "steps_remaining": list(range(1, journey_config.get("total_steps", 10) + 1))
                },
                "analytics": {
                    "time_spent": 0,
                    "interactions_count": 0,
                    "errors_count": 0,
                    "satisfaction_score": None
                }
            }
            
            # Store journey
            self.journeys[journey_id] = journey_info
            
            self.logger.info(f"✅ Journey created: {journey_id} for user: {user_context.user_id}")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "journey_info": journey_info,
                "message": "Journey created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create journey: {e}")
            return {"success": False, "error": str(e), "message": "Failed to create journey"}
    
    async def track_progress(self, journey_id: str, progress_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Track progress in a user journey.
        
        Args:
            journey_id: The ID of the journey.
            progress_data: Data about the progress made.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the tracking success and updated progress.
        """
        self.logger.debug(f"Tracking progress for journey: {journey_id}")
        
        try:
            if journey_id not in self.journeys:
                return {"success": False, "error": "Journey not found"}
            
            journey = self.journeys[journey_id]
            
            # Check if journey belongs to user
            if journey.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to journey"}
            
            # Check if journey is active
            if journey.get("status") != JourneyStatus.ACTIVE.value:
                return {"success": False, "error": "Journey is not active"}
            
            # Update progress
            current_progress = journey.get("progress", {})
            
            # Update milestone progress
            if "milestone_completed" in progress_data:
                milestone = progress_data["milestone_completed"]
                if milestone not in current_progress.get("milestones_completed", []):
                    current_progress["milestones_completed"].append(milestone)
                    if milestone in current_progress.get("milestones_remaining", []):
                        current_progress["milestones_remaining"].remove(milestone)
                    current_progress["current_milestone"] = max(current_progress.get("milestones_completed", []))
            
            # Update step progress
            if "step_completed" in progress_data:
                step = progress_data["step_completed"]
                if step not in current_progress.get("steps_completed", []):
                    current_progress["steps_completed"].append(step)
                    if step in current_progress.get("steps_remaining", []):
                        current_progress["steps_remaining"].remove(step)
                    current_progress["current_step"] = max(current_progress.get("steps_completed", []))
            
            # Calculate completion percentage
            total_milestones = current_progress.get("total_milestones", 1)
            completed_milestones = len(current_progress.get("milestones_completed", []))
            current_progress["completion_percentage"] = (completed_milestones / total_milestones) * 100
            
            # Update analytics
            analytics = journey.get("analytics", {})
            analytics["interactions_count"] = analytics.get("interactions_count", 0) + 1
            if progress_data.get("error"):
                analytics["errors_count"] = analytics.get("errors_count", 0) + 1
            if "satisfaction_score" in progress_data:
                analytics["satisfaction_score"] = progress_data["satisfaction_score"]
            
            # Update journey
            journey["progress"] = current_progress
            journey["analytics"] = analytics
            journey["last_updated"] = datetime.utcnow().isoformat()
            
            # Check if journey is complete
            if completed_milestones >= total_milestones:
                journey["status"] = JourneyStatus.COMPLETED.value
                journey["completed_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Progress tracked for journey: {journey_id}")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "progress_updated": True,
                "completion_percentage": current_progress["completion_percentage"],
                "message": "Progress tracked successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to track progress: {e}")
            return {"success": False, "error": str(e), "message": "Failed to track progress"}
    
    async def get_journey_state(self, journey_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Get the current state of a user journey.
        
        Args:
            journey_id: The ID of the journey.
            user_context: Context of the user.
            
        Returns:
            A dictionary containing the journey state.
        """
        self.logger.debug(f"Getting journey state for: {journey_id}")
        
        try:
            if journey_id not in self.journeys:
                return {"success": False, "error": "Journey not found"}
            
            journey = self.journeys[journey_id]
            
            # Check if journey belongs to user
            if journey.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to journey"}
            
            # Check if journey is expired
            expires_at = datetime.fromisoformat(journey.get("expires_at", ""))
            if datetime.utcnow() > expires_at and journey.get("status") == JourneyStatus.ACTIVE.value:
                # Mark journey as expired
                journey["status"] = JourneyStatus.ABANDONED.value
                return {"success": False, "error": "Journey expired"}
            
            return {
                "success": True,
                "journey_id": journey_id,
                "journey_state": {
                    "status": journey.get("status"),
                    "stage": journey.get("stage"),
                    "progress": journey.get("progress"),
                    "flow": journey.get("flow"),
                    "analytics": journey.get("analytics"),
                    "created_at": journey.get("created_at"),
                    "last_updated": journey.get("last_updated")
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get journey state: {e}")
            return {"success": False, "error": str(e), "message": "Failed to get journey state"}
    
    async def pause_journey(self, journey_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Pause a user journey."""
        self.logger.debug(f"Pausing journey: {journey_id}")
        
        try:
            if journey_id not in self.journeys:
                return {"success": False, "error": "Journey not found"}
            
            journey = self.journeys[journey_id]
            
            # Check if journey belongs to user
            if journey.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to journey"}
            
            # Check if journey can be paused
            if journey.get("status") != JourneyStatus.ACTIVE.value:
                return {"success": False, "error": "Journey cannot be paused"}
            
            # Pause journey
            journey["status"] = JourneyStatus.PAUSED.value
            journey["paused_at"] = datetime.utcnow().isoformat()
            journey["last_updated"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Journey paused: {journey_id}")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "paused": True,
                "message": "Journey paused successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to pause journey: {e}")
            return {"success": False, "error": str(e), "message": "Failed to pause journey"}
    
    async def resume_journey(self, journey_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Resume a paused user journey."""
        self.logger.debug(f"Resuming journey: {journey_id}")
        
        try:
            if journey_id not in self.journeys:
                return {"success": False, "error": "Journey not found"}
            
            journey = self.journeys[journey_id]
            
            # Check if journey belongs to user
            if journey.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to journey"}
            
            # Check if journey can be resumed
            if journey.get("status") != JourneyStatus.PAUSED.value:
                return {"success": False, "error": "Journey cannot be resumed"}
            
            # Resume journey
            journey["status"] = JourneyStatus.ACTIVE.value
            journey["resumed_at"] = datetime.utcnow().isoformat()
            journey["last_updated"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Journey resumed: {journey_id}")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "resumed": True,
                "message": "Journey resumed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to resume journey: {e}")
            return {"success": False, "error": str(e), "message": "Failed to resume journey"}
    
    async def complete_journey(self, journey_id: str, completion_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Complete a user journey."""
        self.logger.debug(f"Completing journey: {journey_id}")
        
        try:
            if journey_id not in self.journeys:
                return {"success": False, "error": "Journey not found"}
            
            journey = self.journeys[journey_id]
            
            # Check if journey belongs to user
            if journey.get("user_id") != user_context.user_id:
                return {"success": False, "error": "Unauthorized access to journey"}
            
            # Complete journey
            journey["status"] = JourneyStatus.COMPLETED.value
            journey["completed_at"] = datetime.utcnow().isoformat()
            journey["last_updated"] = datetime.utcnow().isoformat()
            journey["completion_data"] = completion_data
            
            # Calculate final analytics
            analytics = journey.get("analytics", {})
            if "time_spent" in completion_data:
                analytics["time_spent"] = completion_data["time_spent"]
            if "final_satisfaction_score" in completion_data:
                analytics["satisfaction_score"] = completion_data["final_satisfaction_score"]
            
            self.logger.info(f"✅ Journey completed: {journey_id}")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "completed": True,
                "completion_summary": {
                    "completion_percentage": journey.get("progress", {}).get("completion_percentage", 0),
                    "time_spent": analytics.get("time_spent", 0),
                    "interactions_count": analytics.get("interactions_count", 0),
                    "satisfaction_score": analytics.get("satisfaction_score")
                },
                "message": "Journey completed successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to complete journey: {e}")
            return {"success": False, "error": str(e), "message": "Failed to complete journey"}
    
    async def get_user_journey_history(self, user_context: UserContext) -> Dict[str, Any]:
        """Get the journey history for a user."""
        self.logger.debug(f"Getting journey history for user: {user_context.user_id}")
        
        try:
            user_journeys = [
                {
                    "journey_id": journey_id,
                    "status": journey.get("status"),
                    "stage": journey.get("stage"),
                    "completion_percentage": journey.get("progress", {}).get("completion_percentage", 0),
                    "created_at": journey.get("created_at"),
                    "last_updated": journey.get("last_updated"),
                    "completed_at": journey.get("completed_at")
                }
                for journey_id, journey in self.journeys.items()
                if journey.get("user_id") == user_context.user_id
            ]
            
            return {
                "success": True,
                "user_id": user_context.user_id,
                "journeys": user_journeys,
                "journey_count": len(user_journeys)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get user journey history: {e}")
            return {"success": False, "error": str(e), "message": "Failed to get user journey history"}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the Journey Tracker Module."""
        return {
            "module_name": "JourneyTrackerModule",
            "status": "healthy" if self.is_initialized else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "active_journeys": len([j for j in self.journeys.values() if j.get("status") == JourneyStatus.ACTIVE.value]),
            "total_journeys": len(self.journeys),
            "message": "Journey Tracker Module is operational."
        }
