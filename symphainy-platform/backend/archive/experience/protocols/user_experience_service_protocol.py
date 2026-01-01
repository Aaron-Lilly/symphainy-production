#!/usr/bin/env python3
"""
User Experience Service Protocol

Defines the contract for user experience orchestration services in the Experience realm.
Handles user experience flows, interaction coordination, and experience optimization.

WHAT (User Experience Role): I orchestrate user experience flows and optimize interactions
HOW (User Experience Service): I coordinate user journeys, manage interactions, and optimize experience
"""

from typing import Dict, Any, Optional, List, runtime_checkable
from bases.protocols.service_protocol import ServiceProtocol


@runtime_checkable
class UserExperienceServiceProtocol(ServiceProtocol):
    """
    Protocol for User Experience services in the Experience realm.
    
    User Experience services handle:
    - User experience flow orchestration
    - Interaction coordination and optimization
    - Experience analytics and insights
    - User journey management
    """
    
    # ============================================================================
    # USER EXPERIENCE FLOW ORCHESTRATION
    # ============================================================================
    
    async def orchestrate_user_flow(self, flow_name: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate a user experience flow.
        
        Args:
            flow_name: Name of the experience flow
            user_context: User context and preferences
            
        Returns:
            Dict[str, Any]: Flow orchestration result
        """
        ...
    
    async def coordinate_user_interactions(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Coordinate multiple user interactions.
        
        Args:
            interactions: List of user interactions to coordinate
            
        Returns:
            Dict[str, Any]: Interaction coordination result
        """
        ...
    
    async def optimize_user_experience(self, experience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize user experience based on data and patterns.
        
        Args:
            experience_data: Experience data to analyze and optimize
            
        Returns:
            Dict[str, Any]: Optimization recommendations
        """
        ...
    
    # ============================================================================
    # USER JOURNEY MANAGEMENT
    # ============================================================================
    
    async def create_user_journey(self, journey_type: str, user_id: str) -> Dict[str, Any]:
        """
        Create a new user journey.
        
        Args:
            journey_type: Type of journey to create
            user_id: ID of the user
            
        Returns:
            Dict[str, Any]: Created journey information
        """
        ...
    
    async def track_journey_progress(self, journey_id: str, progress_data: Dict[str, Any]) -> bool:
        """
        Track progress in a user journey.
        
        Args:
            journey_id: ID of the journey
            progress_data: Progress data to track
            
        Returns:
            bool: True if tracking successful
        """
        ...
    
    async def complete_user_journey(self, journey_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete a user journey.
        
        Args:
            journey_id: ID of the journey
            completion_data: Journey completion data
            
        Returns:
            Dict[str, Any]: Journey completion result
        """
        ...
    
    # ============================================================================
    # EXPERIENCE ANALYTICS & INSIGHTS
    # ============================================================================
    
    async def analyze_user_behavior(self, user_id: str, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user behavior patterns.
        
        Args:
            user_id: ID of the user
            time_range: Time range for analysis
            
        Returns:
            Dict[str, Any]: Behavior analysis results
        """
        ...
    
    async def generate_experience_insights(self, experience_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate insights from experience data.
        
        Args:
            experience_data: Experience data to analyze
            
        Returns:
            Dict[str, Any]: Generated insights
        """
        ...
    
    async def get_experience_metrics(self, metric_types: List[str]) -> Dict[str, Any]:
        """
        Get experience metrics and KPIs.
        
        Args:
            metric_types: Types of metrics to retrieve
            
        Returns:
            Dict[str, Any]: Experience metrics
        """
        ...
    
    # ============================================================================
    # EXPERIENCE PERSONALIZATION
    # ============================================================================
    
    async def personalize_experience(self, user_id: str, personalization_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Personalize user experience based on preferences and history.
        
        Args:
            user_id: ID of the user
            personalization_data: Personalization parameters
            
        Returns:
            Dict[str, Any]: Personalized experience configuration
        """
        ...
    
    async def adapt_experience_flow(self, flow_id: str, adaptation_rules: Dict[str, Any]) -> bool:
        """
        Adapt experience flow based on rules and conditions.
        
        Args:
            flow_id: ID of the experience flow
            adaptation_rules: Rules for adaptation
            
        Returns:
            bool: True if adaptation successful
        """
        ...
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user experience preferences.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict[str, Any]: User preferences
        """
        ...
