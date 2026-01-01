#!/usr/bin/env python3
"""
Guide Agent Interface

Interface for guide agent capabilities provided by the Guide Agent role.
Defines the contract for guidance, assistance, and user support operations.

WHAT (Business Enablement Role): I provide guidance and assistance to users
HOW (Interface): I define the contract for guide agent operations
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from utilities import UserContext


class GuidanceType(Enum):
    """Types of guidance that can be provided."""
    TASK_GUIDANCE = "task_guidance"
    PROCESS_GUIDANCE = "process_guidance"
    TROUBLESHOOTING = "troubleshooting"
    BEST_PRACTICES = "best_practices"
    FEATURE_EXPLANATION = "feature_explanation"
    WORKFLOW_ASSISTANCE = "workflow_assistance"


class AssistanceLevel(Enum):
    """Levels of assistance that can be provided."""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class GuidanceContext(Enum):
    """Context for guidance requests."""
    ONBOARDING = "onboarding"
    DAILY_OPERATIONS = "daily_operations"
    PROBLEM_SOLVING = "problem_solving"
    FEATURE_LEARNING = "feature_learning"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"


class IntentType(Enum):
    """Types of user intents that can be detected."""
    QUESTION = "question"
    REQUEST_HELP = "request_help"
    TASK_COMPLETION = "task_completion"
    FEATURE_EXPLORATION = "feature_exploration"
    PROBLEM_REPORTING = "problem_reporting"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    LEARNING = "learning"
    NAVIGATION = "navigation"


@dataclass
class ProvideGuidanceRequest:
    """Request for providing guidance."""
    guidance_type: GuidanceType
    assistance_level: AssistanceLevel
    context: GuidanceContext
    user_query: str
    current_task: Optional[str] = None
    user_experience_level: Optional[str] = None
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class ProvideGuidanceResponse:
    """Response for providing guidance."""
    success: bool
    guidance_id: Optional[str] = None
    guidance_content: Optional[str] = None
    guidance_steps: Optional[List[Dict[str, Any]]] = None
    related_resources: Optional[List[Dict[str, Any]]] = None
    message: str = "Guidance provided successfully"
    timestamp: Optional[datetime] = None


@dataclass
class AssistUserRequest:
    """Request for user assistance."""
    assistance_type: GuidanceType
    user_goal: str
    current_state: Optional[Dict[str, Any]] = None
    constraints: Optional[List[str]] = None
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class AssistUserResponse:
    """Response for user assistance."""
    success: bool
    assistance_id: Optional[str] = None
    assistance_plan: Optional[List[Dict[str, Any]]] = None
    next_steps: Optional[List[str]] = None
    estimated_duration: Optional[str] = None
    message: str = "User assistance provided successfully"
    timestamp: Optional[datetime] = None


@dataclass
class TroubleshootIssueRequest:
    """Request for troubleshooting assistance."""
    issue_description: str
    error_messages: Optional[List[str]] = None
    system_state: Optional[Dict[str, Any]] = None
    user_actions: Optional[List[str]] = None
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class TroubleshootIssueResponse:
    """Response for troubleshooting assistance."""
    success: bool
    troubleshooting_id: Optional[str] = None
    issue_analysis: Optional[str] = None
    solution_steps: Optional[List[Dict[str, Any]]] = None
    prevention_tips: Optional[List[str]] = None
    message: str = "Troubleshooting assistance provided successfully"
    timestamp: Optional[datetime] = None


@dataclass
class ExplainFeatureRequest:
    """Request for feature explanation."""
    feature_name: str
    explanation_level: AssistanceLevel
    use_case: Optional[str] = None
    user_context: Optional[UserContext] = None
    tenant_id: Optional[str] = None


@dataclass
class ExplainFeatureResponse:
    """Response for feature explanation."""
    success: bool
    explanation_id: Optional[str] = None
    feature_description: Optional[str] = None
    usage_examples: Optional[List[Dict[str, Any]]] = None
    related_features: Optional[List[str]] = None
    message: str = "Feature explanation provided successfully"
    timestamp: Optional[datetime] = None


@dataclass
class OptimizeWorkflowRequest:
    """Request for workflow optimization."""
    current_workflow: Dict[str, Any]
    optimization_goals: List[str]
    constraints: Optional[List[str]] = None
    tenant_id: Optional[str] = None
    user_context: Optional[UserContext] = None


@dataclass
class OptimizeWorkflowResponse:
    """Response for workflow optimization."""
    success: bool
    optimization_id: Optional[str] = None
    optimized_workflow: Optional[Dict[str, Any]] = None
    improvements: Optional[List[Dict[str, Any]]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    message: str = "Workflow optimization completed successfully"
    timestamp: Optional[datetime] = None


class IGuideAgent(ABC):
    """
    Guide Agent Interface
    
    Defines the contract for guide agent capabilities, including guidance provision,
    user assistance, troubleshooting, feature explanation, and workflow optimization.
    """
    
    @abstractmethod
    async def provide_guidance(self, request: ProvideGuidanceRequest) -> ProvideGuidanceResponse:
        """
        Provide guidance to users based on their needs and context.
        
        Args:
            request: Guidance request
            
        Returns:
            ProvideGuidanceResponse: Guidance result
        """
        pass
    
    @abstractmethod
    async def assist_user(self, request: AssistUserRequest) -> AssistUserResponse:
        """
        Assist users in achieving their goals.
        
        Args:
            request: User assistance request
            
        Returns:
            AssistUserResponse: Assistance result
        """
        pass
    
    @abstractmethod
    async def troubleshoot_issue(self, request: TroubleshootIssueRequest) -> TroubleshootIssueResponse:
        """
        Troubleshoot issues and provide solutions.
        
        Args:
            request: Troubleshooting request
            
        Returns:
            TroubleshootIssueResponse: Troubleshooting result
        """
        pass
    
    @abstractmethod
    async def explain_feature(self, request: ExplainFeatureRequest) -> ExplainFeatureResponse:
        """
        Explain features and their usage.
        
        Args:
            request: Feature explanation request
            
        Returns:
            ExplainFeatureResponse: Feature explanation result
        """
        pass
    
    @abstractmethod
    async def optimize_workflow(self, request: OptimizeWorkflowRequest) -> OptimizeWorkflowResponse:
        """
        Optimize user workflows for better efficiency.
        
        Args:
            request: Workflow optimization request
            
        Returns:
            OptimizeWorkflowResponse: Optimization result
        """
        pass