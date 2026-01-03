#!/usr/bin/env python3
"""
Business Specialist Agent Protocol

Defines the standard protocol for Business Enablement specialist agents.
All Business Enablement specialist agents must follow this protocol.

WHAT (Business Enablement Role): I provide specialized business analysis and processing
HOW (Specialist Agent Protocol): I follow the standard agent structure and patterns
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from utilities import UserContext
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase


class SpecialistCapability(Enum):
    """Types of specialist capabilities."""
    DATA_ANALYSIS = "data_analysis"
    PROCESS_OPTIMIZATION = "process_optimization"
    STRATEGIC_PLANNING = "strategic_planning"
    CONTENT_PROCESSING = "content_processing"
    WORKFLOW_DESIGN = "workflow_design"
    COEXISTENCE_ANALYSIS = "coexistence_analysis"
    ROI_CALCULATION = "roi_calculation"
    QUALITY_ASSURANCE = "quality_assurance"
    INTEGRATION_ANALYSIS = "integration_analysis"
    PERFORMANCE_MONITORING = "performance_monitoring"


class AnalysisComplexity(Enum):
    """Complexity levels for specialist analysis."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class SpecialistAnalysisRequest:
    """Request for specialist analysis."""
    analysis_type: SpecialistCapability
    input_data: Dict[str, Any]
    analysis_parameters: Dict[str, Any]
    user_context: UserContext
    session_id: str
    complexity_level: AnalysisComplexity = AnalysisComplexity.MODERATE
    priority: str = "normal"
    deadline: Optional[datetime] = None
    
    def __post_init__(self):
        if self.analysis_parameters is None:
            self.analysis_parameters = {}


@dataclass
class SpecialistAnalysisResponse:
    """Response from specialist analysis."""
    success: bool
    analysis_id: str
    analysis_type: SpecialistCapability
    results: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    complexity_level: AnalysisComplexity
    processing_time: float
    quality_metrics: Dict[str, Any] = None
    error_details: Optional[Dict[str, Any]] = None
    message: str = ""
    
    def __post_init__(self):
        if self.quality_metrics is None:
            self.quality_metrics = {}


@dataclass
class BatchAnalysisRequest:
    """Request for batch specialist analysis."""
    analyses: List[SpecialistAnalysisRequest]
    user_context: UserContext
    session_id: str
    parallel_processing: bool = True
    max_concurrent: int = 5
    
    def __post_init__(self):
        if self.analyses is None:
            self.analyses = []


@dataclass
class BatchAnalysisResponse:
    """Response from batch specialist analysis."""
    success: bool
    batch_id: str
    individual_results: List[SpecialistAnalysisResponse]
    overall_quality: Dict[str, Any]
    processing_time: float
    completed_count: int
    failed_count: int
    error_details: Optional[Dict[str, Any]] = None
    message: str = ""
    
    def __post_init__(self):
        if self.individual_results is None:
            self.individual_results = []
        if self.overall_quality is None:
            self.overall_quality = {}


@dataclass
class CapabilityAssessmentRequest:
    """Request for capability assessment."""
    capability_type: SpecialistCapability
    current_state: Dict[str, Any]
    target_state: Dict[str, Any]
    user_context: UserContext
    session_id: str
    assessment_criteria: List[str] = None
    
    def __post_init__(self):
        if self.assessment_criteria is None:
            self.assessment_criteria = []


@dataclass
class CapabilityAssessmentResponse:
    """Response from capability assessment."""
    success: bool
    assessment_id: str
    capability_type: SpecialistCapability
    current_capability_score: float
    target_capability_score: float
    gap_analysis: Dict[str, Any]
    improvement_plan: List[str]
    resource_requirements: List[str]
    timeline_estimate: str
    confidence_score: float
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.gap_analysis is None:
            self.gap_analysis = {}
        if self.improvement_plan is None:
            self.improvement_plan = []
        if self.resource_requirements is None:
            self.resource_requirements = []


class BusinessSpecialistAgentProtocol(ABC):
    """
    Business Specialist Agent Protocol
    
    Abstract base class that defines the standard protocol for Business Enablement specialist agents.
    All Business Enablement specialist agents must inherit from this class.
    
    WHAT (Business Enablement Role): I provide specialized business analysis and processing
    HOW (Specialist Agent Protocol): I follow the standard agent structure and patterns
    """
    
    def __init__(self, agent_name: str, business_domain: str, specialist_capability: SpecialistCapability,
                 utility_foundation=None):
        """Initialize Business specialist agent protocol."""
        self.agent_name = agent_name
        self.business_domain = business_domain
        self.specialist_capability = specialist_capability
        self.utility_foundation = utility_foundation
        self.analysis_history = []
        self.performance_metrics = {}
        
    @abstractmethod
    async def initialize(self, user_context: UserContext = None):
        """Initialize the Business specialist agent."""
        pass
    
    @abstractmethod
    async def perform_analysis(self, request: SpecialistAnalysisRequest) -> SpecialistAnalysisResponse:
        """
        Perform specialist analysis.
        
        Args:
            request: Specialist analysis request with data and parameters
            
        Returns:
            SpecialistAnalysisResponse with analysis results and insights
        """
        pass
    
    @abstractmethod
    async def perform_batch_analysis(self, request: BatchAnalysisRequest) -> BatchAnalysisResponse:
        """
        Perform batch specialist analysis.
        
        Args:
            request: Batch analysis request with multiple analyses
            
        Returns:
            BatchAnalysisResponse with batch analysis results
        """
        pass
    
    @abstractmethod
    async def assess_capability(self, request: CapabilityAssessmentRequest) -> CapabilityAssessmentResponse:
        """
        Assess business capability.
        
        Args:
            request: Capability assessment request with current and target states
            
        Returns:
            CapabilityAssessmentResponse with assessment results
        """
        pass
    
    @abstractmethod
    async def get_analysis_history(self, user_context: UserContext, 
                                  analysis_type: Optional[SpecialistCapability] = None,
                                  limit: int = 100, offset: int = 0) -> List[SpecialistAnalysisResponse]:
        """Get analysis history for a user."""
        pass
    
    @abstractmethod
    async def get_analysis_by_id(self, analysis_id: str, user_context: UserContext) -> Optional[SpecialistAnalysisResponse]:
        """Get specific analysis by ID."""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this specialist agent."""
        pass
    
    @abstractmethod
    async def get_capability_info(self) -> Dict[str, Any]:
        """Get information about this agent's capabilities."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of this specialist agent."""
        pass


class BusinessSpecialistAgentBase(AgentBase):
    """
    Business Specialist Agent Base Class (Refactored with Pure DI)
    
    Base class for Business Enablement specialist agents that provides common functionality.
    Refactored to inherit from the new AgentBase with pure dependency injection.
    
    WHAT (Business Enablement Role): I need to implement specialist agents with standard patterns
    HOW (Specialist Agent Base): I provide common agent functionality and business integration using pure DI
    """
    
    def __init__(self, agent_name: str, business_domain: str, specialist_capability: SpecialistCapability,
                 capabilities: List[str], required_roles: List[str], agui_schema: 'AGUISchema', 
                 foundation_services: 'DIContainerService',
                 public_works_foundation: 'PublicWorksFoundationService',
                 mcp_client_manager: 'MCPClientManager',
                 policy_integration: 'PolicyIntegration',
                 tool_composition: 'ToolComposition',
                 agui_formatter: 'AGUIOutputFormatter',
                 curator_foundation=None, metadata_foundation=None, agentic_foundation=None, **kwargs):
        """Initialize Business specialist agent base with pure dependency injection."""
        # Import here to avoid circular imports
        from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase
        
        # Initialize the base AgentBase with all required dependencies
        super().__init__(
            agent_name=agent_name,
            capabilities=capabilities,
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            **kwargs
        )
        
        # Business-specific properties
        self.business_domain = business_domain
        self.specialist_capability = specialist_capability
        self.agent_protocol = None
        self.analysis_sessions = {}
        
    async def initialize(self):
        """Initialize the Business specialist agent."""
        if self.agent_protocol:
            await self.agent_protocol.initialize()
        self.is_initialized = True
    
    async def shutdown(self):
        """Shutdown the Business specialist agent."""
        if self.agent_protocol:
            await self.agent_protocol.shutdown()
        self.is_initialized = False
    
    async def perform_analysis(self, request: SpecialistAnalysisRequest) -> SpecialistAnalysisResponse:
        """Perform specialist analysis."""
        if self.agent_protocol:
            return await self.agent_protocol.perform_analysis(request)
        else:
            return SpecialistAnalysisResponse(
                success=False,
                analysis_id="",
                analysis_type=request.analysis_type,
                results={},
                insights=[],
                recommendations=[],
                confidence_score=0.0,
                complexity_level=request.complexity_level,
                processing_time=0.0,
                message="Agent protocol not initialized",
                error_details={"error": "Agent protocol not initialized"}
            )
    
    async def perform_batch_analysis(self, request: BatchAnalysisRequest) -> BatchAnalysisResponse:
        """Perform batch specialist analysis."""
        if self.agent_protocol:
            return await self.agent_protocol.perform_batch_analysis(request)
        else:
            return BatchAnalysisResponse(
                success=False,
                batch_id="",
                individual_results=[],
                overall_quality={},
                processing_time=0.0,
                completed_count=0,
                failed_count=len(request.analyses),
                message="Agent protocol not initialized",
                error_details={"error": "Agent protocol not initialized"}
            )
    
    async def assess_capability(self, request: CapabilityAssessmentRequest) -> CapabilityAssessmentResponse:
        """Assess business capability."""
        if self.agent_protocol:
            return await self.agent_protocol.assess_capability(request)
        else:
            return CapabilityAssessmentResponse(
                success=False,
                assessment_id="",
                capability_type=request.capability_type,
                current_capability_score=0.0,
                target_capability_score=0.0,
                gap_analysis={},
                improvement_plan=[],
                resource_requirements=[],
                timeline_estimate="Unknown",
                confidence_score=0.0,
                processing_time=0.0,
                message="Agent protocol not initialized",
                error_details={"error": "Agent protocol not initialized"}
            )
    
    async def get_analysis_history(self, user_context: UserContext, 
                                  analysis_type: Optional[SpecialistCapability] = None,
                                  limit: int = 100, offset: int = 0) -> List[SpecialistAnalysisResponse]:
        """Get analysis history."""
        if self.agent_protocol:
            return await self.agent_protocol.get_analysis_history(user_context, analysis_type, limit, offset)
        else:
            return []
    
    async def get_analysis_by_id(self, analysis_id: str, user_context: UserContext) -> Optional[SpecialistAnalysisResponse]:
        """Get analysis by ID."""
        if self.agent_protocol:
            return await self.agent_protocol.get_analysis_by_id(analysis_id, user_context)
        else:
            return None
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if self.agent_protocol:
            return await self.agent_protocol.get_performance_metrics()
        else:
            return {"error": "Agent protocol not initialized"}
    
    async def get_capability_info(self) -> Dict[str, Any]:
        """Get capability info."""
        if self.agent_protocol:
            return await self.agent_protocol.get_capability_info()
        else:
            return {"error": "Agent protocol not initialized"}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status."""
        return {
            "agent_name": self.agent_name,
            "business_domain": self.business_domain,
            "specialist_capability": self.specialist_capability.value,
            "status": "healthy" if self.is_initialized else "unhealthy",
            "initialized": self.is_initialized,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # UNIFIED MCP TOOL ACCESS (Phase 3.2.5)
    # ============================================================================
    
    async def execute_mcp_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute MCP tool via orchestrator's MCP server.
        
        This is the PRIMARY method for agents to interact with services.
        Agents should NEVER access services directly.
        
        Architecture (Phase 3.2.5):
        - Agents use MCP Tools exclusively (never direct service access)
        - MCP Tools are exposed by MCP Servers (one per realm)
        - MCP Servers wrap SOA APIs as MCP Tools
        - Orchestrators initialize MCP Servers and set themselves on agents
        
        Args:
            tool_name: Name of MCP tool to execute (e.g., "content_upload_file")
            parameters: Tool parameters (dict)
            user_context: Optional user context dict with user_id, tenant_id, permissions, etc.
        
        Returns:
            Tool execution result (dict)
        
        Raises:
            ValueError: If orchestrator or MCP server not available
        
        Example:
            ```python
            result = await self.execute_mcp_tool(
                "content_upload_file",
                {
                    "file_data": file_data,
                    "filename": filename,
                    "file_type": file_type
                },
                user_context=user_context
            )
            ```
        """
        # Get orchestrator (set by orchestrator during initialization)
        orchestrator = getattr(self, 'orchestrator', None)
        if not orchestrator:
            raise ValueError(
                f"Orchestrator not set for {self.agent_name}. "
                f"Cannot execute MCP tool '{tool_name}'. "
                f"Ensure orchestrator calls set_orchestrator(agent) during initialization."
            )
        
        # Get MCP server from orchestrator
        if not hasattr(orchestrator, 'mcp_server') or orchestrator.mcp_server is None:
            raise ValueError(
                f"Orchestrator {orchestrator.__class__.__name__} does not have MCP server. "
                f"Cannot execute MCP tool '{tool_name}'. "
                f"Ensure orchestrator initializes MCP server in _initialize_mcp_server()."
            )
        
        # Use provided user_context or default from agent
        final_user_context = user_context or getattr(self, 'user_context', None)
        
        # Execute tool via MCP server
        return await orchestrator.mcp_server.execute_tool(
            tool_name,
            parameters,
            user_context=final_user_context
        )
    
    def set_orchestrator(self, orchestrator: Any):
        """
        Set orchestrator reference (called by orchestrator during initialization).
        
        This allows agents to access the orchestrator's MCP server for tool execution.
        
        Args:
            orchestrator: Orchestrator instance that owns this agent
        """
        self.orchestrator = orchestrator