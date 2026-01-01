#!/usr/bin/env python3
"""
Business Outcome Analyzer Interface

Defines the contract for the Business Outcome Analyzer Service, responsible for
analyzing business outcomes and determining required capabilities.

WHAT (Journey Solution Role): I analyze business outcomes and determine required capabilities
HOW (Interface): I define the contract for business outcome analysis, capability determination, and pattern matching
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from utilities import UserContext


class BusinessOutcomeType(Enum):
    """Defines types of business outcomes."""
    DATA_ANALYSIS = "data_analysis"
    PROCESS_OPTIMIZATION = "process_optimization"
    AUTOMATION = "automation"
    INTEGRATION = "integration"
    REPORTING = "reporting"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"
    
    def __str__(self):
        return self.value


class CapabilityType(Enum):
    """Defines types of platform capabilities."""
    CONTENT_MANAGEMENT = "content_management"
    DATA_ANALYTICS = "data_analytics"
    WORKFLOW_AUTOMATION = "workflow_automation"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    INTEGRATION = "integration"
    REPORTING = "reporting"
    
    def __str__(self):
        return self.value


class IBusinessOutcomeAnalyzer(ABC):
    """
    Business Outcome Analyzer Interface
    
    Defines the contract for the Business Outcome Analyzer Service.
    """
    
    @abstractmethod
    async def analyze_business_outcome(self, business_outcome: str, use_case: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Analyze a business outcome and determine required capabilities.
        
        Args:
            business_outcome: The business outcome to analyze
            use_case: The use case for the outcome
            user_context: User context data
            
        Returns:
            Dict containing analysis result and required capabilities
        """
        pass

    @abstractmethod
    async def determine_required_capabilities(self, business_outcome: str, use_case: str) -> List[CapabilityType]:
        """
        Determine required platform capabilities for a business outcome.
        
        Args:
            business_outcome: The business outcome
            use_case: The use case
            
        Returns:
            List of required capabilities
        """
        pass

    @abstractmethod
    async def analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input to determine intent and requirements.
        
        Args:
            user_input: User input text
            
        Returns:
            Dict containing intent analysis result
        """
        pass

    @abstractmethod
    async def match_outcome_patterns(self, business_outcome: str) -> Dict[str, Any]:
        """
        Match business outcome against known patterns.
        
        Args:
            business_outcome: The business outcome to match
            
        Returns:
            Dict containing pattern matching result
        """
        pass

    @abstractmethod
    async def get_capability_requirements(self, business_outcome: str, use_case: str) -> Dict[str, Any]:
        """
        Get detailed capability requirements for a business outcome.
        
        Args:
            business_outcome: The business outcome
            use_case: The use case
            
        Returns:
            Dict containing detailed capability requirements
        """
        pass

    @abstractmethod
    async def suggest_alternative_outcomes(self, business_outcome: str, use_case: str) -> List[str]:
        """
        Suggest alternative business outcomes.
        
        Args:
            business_outcome: The original business outcome
            use_case: The use case
            
        Returns:
            List of alternative outcomes
        """
        pass

    @abstractmethod
    async def validate_business_outcome(self, business_outcome: str, use_case: str) -> Dict[str, Any]:
        """
        Validate a business outcome for feasibility.
        
        Args:
            business_outcome: The business outcome to validate
            use_case: The use case
            
        Returns:
            Dict containing validation result
        """
        pass

    @abstractmethod
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """
        Get service capabilities.
        
        Returns:
            Dict containing service capabilities
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict containing health status
        """
        pass





