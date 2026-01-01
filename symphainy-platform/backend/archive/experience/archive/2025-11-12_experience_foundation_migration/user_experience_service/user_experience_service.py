#!/usr/bin/env python3
"""
User Experience Service

WHAT: Manages user experience personalization, preferences, and UX optimization
HOW: Tracks user behavior, personalizes content, optimizes UX via Smart City and orchestrators

This service provides UX personalization by composing Business Enablement orchestrators
with user preferences and behavior analytics.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class UserExperienceService(RealmServiceBase):
    """
    User Experience Service for Experience realm.
    
    Manages user experience personalization, preferences, and UX optimization
    by composing Business Enablement orchestrators with user-specific context.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize User Experience Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.data_steward = None
        self.nurse = None
        
        # User preferences cache
        self.preferences_cache: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> bool:
        """Initialize User Experience Service."""
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.librarian = await self.get_librarian_api()
            self.data_steward = await self.get_data_steward_api()
            self.nurse = await self.get_nurse_api()
            
            # 2. Register with Curator
            await self.register_with_curator(
                capabilities=["ux_personalization", "user_preferences", "ux_optimization", "ux_analytics"],
                soa_apis=[
                    "personalize_experience", "get_user_preferences", "update_user_preferences",
                    "optimize_user_flow", "track_user_interaction", "get_ux_recommendations",
                    "get_user_analytics", "analyze_ux_metrics"
                ],
                mcp_tools=[],  # Experience services provide SOA APIs, not MCP tools
                additional_metadata={
                    "layer": "experience",
                    "personalization": True,
                    "composes": "business_enablement_orchestrators"
                }
            )
            
            self.logger.info("✅ User Experience Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ User Experience Service initialization failed: {e}")
            return False
    
    # ========================================================================
    # SOA APIs (Personalization)
    # ========================================================================
    
    async def personalize_experience(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Personalize user experience based on preferences and context (SOA API).
        
        Args:
            user_id: User ID
            context: Context data (data_id, page, action, etc.)
        
        Returns:
            Personalized experience configuration
        """
        try:
            # Get user preferences
            prefs = await self.get_user_preferences(user_id)
            
            # Get UX recommendations
            recommendations = await self.get_ux_recommendations(user_id)
            
            # Personalize based on context
            personalization = {
                "user_id": user_id,
                "preferences": prefs,
                "recommendations": recommendations,
                "theme": prefs.get("theme", "light"),
                "layout": prefs.get("layout", "default"),
                "visualization_type": prefs.get("preferred_viz", "chart"),
                "favorite_metrics": prefs.get("favorite_metrics", []),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Experience personalized for user: {user_id}")
            
            return {
                "success": True,
                "personalization": personalization
            }
            
        except Exception as e:
            self.logger.error(f"❌ Personalize experience failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_preferences(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get user preferences (SOA API).
        
        Args:
            user_id: User ID
        
        Returns:
            User preferences
        """
        try:
            # Check cache first
            if user_id in self.preferences_cache:
                return self.preferences_cache[user_id]
            
            # Retrieve from Librarian
            prefs_doc = await self.retrieve_document(
                f"user_preferences_{user_id}"
            )
            
            if prefs_doc and "document" in prefs_doc:
                prefs = prefs_doc["document"]
                self.preferences_cache[user_id] = prefs
                return prefs
            
            # Return defaults if not found
            default_prefs = {
                "theme": "light",
                "layout": "default",
                "preferred_viz": "chart",
                "favorite_metrics": [],
                "notifications": True
            }
            
            return default_prefs
            
        except Exception as e:
            self.logger.error(f"❌ Get user preferences failed: {e}")
            return {}
    
    async def update_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user preferences (SOA API).
        
        Args:
            user_id: User ID
            preferences: Updated preferences
        
        Returns:
            Update result
        """
        try:
            # Store via Librarian
            result = await self.store_document(
                document_data=preferences,
                metadata={
                    "type": "user_preferences",
                    "user_id": user_id,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            # Update cache
            self.preferences_cache[user_id] = preferences
            
            self.logger.info(f"✅ User preferences updated: {user_id}")
            
            return {
                "success": True,
                "preferences": preferences,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Update user preferences failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (UX Optimization)
    # ========================================================================
    
    async def optimize_user_flow(
        self,
        user_id: str,
        flow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize user flow based on behavior data (SOA API).
        
        Args:
            user_id: User ID
            flow_data: Flow data (steps, timing, completion, etc.)
        
        Returns:
            Optimization recommendations
        """
        try:
            # Analyze flow via Data Steward
            analysis = await self.validate_data_quality(flow_data)
            
            # Generate optimization recommendations
            optimizations = []
            
            # Check for slow steps
            if "steps" in flow_data:
                for step in flow_data["steps"]:
                    if step.get("duration", 0) > 5000:  # > 5 seconds
                        optimizations.append({
                            "type": "performance",
                            "step": step["name"],
                            "recommendation": "Consider caching or pre-loading data"
                        })
            
            # Check for abandoned steps
            if flow_data.get("completed", False) is False:
                last_step = flow_data.get("last_step")
                if last_step:
                    optimizations.append({
                        "type": "completion",
                        "step": last_step,
                        "recommendation": "Add guidance or simplify step"
                    })
            
            self.logger.info(f"✅ User flow optimized: {user_id}")
            
            return {
                "success": True,
                "optimizations": optimizations,
                "flow_score": len(optimizations) == 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Optimize user flow failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def track_user_interaction(
        self,
        user_id: str,
        interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track user interaction for analytics (SOA API).
        
        Args:
            user_id: User ID
            interaction: Interaction data (action, element, timestamp, etc.)
        
        Returns:
            Tracking result
        """
        try:
            # Store interaction via Librarian
            result = await self.store_document(
                document_data=interaction,
                metadata={
                    "type": "user_interaction",
                    "user_id": user_id,
                    "tracked_at": datetime.utcnow().isoformat()
                }
            )
            
            # Record health metric via Nurse
            await self.record_health_metric(
                service_name="user_experience",
                metric_type="interaction",
                metric_value=1
            )
            
            self.logger.info(f"✅ User interaction tracked: {user_id}")
            
            return {
                "success": True,
                "interaction_id": result.get("document_id"),
                "tracked_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Track user interaction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_ux_recommendations(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get UX recommendations for user (SOA API).
        
        Args:
            user_id: User ID
        
        Returns:
            List of UX recommendations
        """
        try:
            # Get user preferences
            prefs = await self.get_user_preferences(user_id)
            
            recommendations = []
            
            # Theme recommendation
            if prefs.get("theme") == "light":
                recommendations.append({
                    "type": "theme",
                    "recommendation": "Try dark mode for reduced eye strain",
                    "action": "switch_theme"
                })
            
            # Visualization recommendation
            if not prefs.get("preferred_viz"):
                recommendations.append({
                    "type": "visualization",
                    "recommendation": "Set preferred visualization type in settings",
                    "action": "set_preference"
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Get UX recommendations failed: {e}")
            return []
    
    # ========================================================================
    # SOA APIs (Analytics)
    # ========================================================================
    
    async def get_user_analytics(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Get user analytics (SOA API).
        
        Args:
            user_id: User ID
        
        Returns:
            User analytics data
        """
        try:
            # Search for user interactions via Librarian
            interactions = await self.search_documents({
                "type": "user_interaction",
                "user_id": user_id
            })
            
            # Calculate analytics
            total_interactions = len(interactions.get("results", []))
            
            analytics = {
                "user_id": user_id,
                "total_interactions": total_interactions,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ User analytics generated: {user_id}")
            
            return {
                "success": True,
                "analytics": analytics
            }
            
        except Exception as e:
            self.logger.error(f"❌ Get user analytics failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_ux_metrics(
        self,
        metrics_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze UX metrics (SOA API).
        
        Args:
            metrics_data: UX metrics data
        
        Returns:
            Analysis results
        """
        try:
            # Analyze via Data Steward
            analysis = await self.validate_data_quality(metrics_data)
            
            # Generate UX insights
            insights = {
                "metrics_analyzed": len(metrics_data.keys()),
                "quality_score": analysis.get("quality_score", 0),
                "recommendations": [],
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info("✅ UX metrics analyzed")
            
            return {
                "success": True,
                "insights": insights
            }
            
        except Exception as e:
            self.logger.error(f"❌ Analyze UX metrics failed: {e}")
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
            "cached_preferences": len(self.preferences_cache),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "experience_service",
            "realm": "experience",
            "layer": "ux_management",
            "capabilities": ["ux_personalization", "user_preferences", "ux_optimization", "ux_analytics"],
            "soa_apis": [
                "personalize_experience", "get_user_preferences", "update_user_preferences",
                "optimize_user_flow", "track_user_interaction", "get_ux_recommendations",
                "get_user_analytics", "analyze_ux_metrics"
            ],
            "mcp_tools": [],
            "composes": "business_enablement_orchestrators"
        }









