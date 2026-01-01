#!/usr/bin/env python3
"""
Operations Management Interface

Interface for operations management capabilities provided by the Operations Pillar role.
Defines the contract for SOP building, workflow conversion, coexistence analysis, and process optimization.

WHAT (Business Enablement Role): I manage workflows, SOPs, and process optimization
HOW (Interface): I define the contract for operations management operations
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


class SOPStatus(Enum):
    """SOP (Standard Operating Procedure) status."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class WorkflowStatus(Enum):
    """Workflow status."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class CoexistenceType(Enum):
    """Types of AI-human coexistence."""
    COLLABORATIVE = "collaborative"
    COMPLEMENTARY = "complementary"
    AUTOMATED = "automated"
    SUPERVISED = "supervised"
    INDEPENDENT = "independent"


@dataclass
class SOPRequest:
    """Request to create or update an SOP."""
    title: str
    description: str
    content: Dict[str, Any]
    user_context: UserContext
    session_id: str
    category: Optional[str] = None
    tags: List[str] = None
    version: str = "1.0"
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.options is None:
            self.options = {}


@dataclass
class SOPResponse:
    """Response from SOP operations."""
    success: bool
    sop_id: str
    title: str
    status: SOPStatus
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowRequest:
    """Request to create or update a workflow."""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    user_context: UserContext
    session_id: str
    category: Optional[str] = None
    tags: List[str] = None
    version: str = "1.0"
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.options is None:
            self.options = {}


@dataclass
class WorkflowResponse:
    """Response from workflow operations."""
    success: bool
    workflow_id: str
    name: str
    status: WorkflowStatus
    steps: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class ConversionRequest:
    """Request to convert between SOP and workflow."""
    source_id: str
    source_type: str  # "sop" or "workflow"
    target_type: str  # "workflow" or "sop"
    user_context: UserContext
    session_id: str
    conversion_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conversion_options is None:
            self.conversion_options = {}


@dataclass
class ConversionResponse:
    """Response from conversion operations."""
    success: bool
    source_id: str
    target_id: str
    source_type: str
    target_type: str
    converted_content: Dict[str, Any]
    conversion_metadata: Dict[str, Any]
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class CoexistenceAnalysisRequest:
    """Request for coexistence analysis."""
    process_description: str
    current_ai_usage: Dict[str, Any]
    human_roles: List[str]
    user_context: UserContext
    session_id: str
    analysis_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.analysis_options is None:
            self.analysis_options = {}


@dataclass
class CoexistenceAnalysisResponse:
    """Response from coexistence analysis."""
    success: bool
    analysis_id: str
    coexistence_type: CoexistenceType
    recommendations: List[str]
    ai_capabilities: List[str]
    human_value_propositions: List[str]
    collaboration_patterns: Dict[str, Any]
    implementation_plan: Dict[str, Any]
    confidence_score: float
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class ProcessOptimizationRequest:
    """Request for process optimization."""
    process_id: str
    current_process: Dict[str, Any]
    optimization_goals: List[str]
    constraints: List[str]
    user_context: UserContext
    session_id: str
    optimization_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.optimization_options is None:
            self.optimization_options = {}


@dataclass
class ProcessOptimizationResponse:
    """Response from process optimization."""
    success: bool
    optimization_id: str
    optimized_process: Dict[str, Any]
    improvements: List[str]
    efficiency_gains: Dict[str, float]
    implementation_steps: List[Dict[str, Any]]
    estimated_impact: Dict[str, Any]
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class WizardStepRequest:
    """Request for wizard step operations."""
    wizard_id: str
    step_number: int
    user_input: Dict[str, Any]
    user_context: UserContext
    session_id: str
    step_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.step_options is None:
            self.step_options = {}


@dataclass
class WizardStepResponse:
    """Response from wizard step operations."""
    success: bool
    wizard_id: str
    current_step: int
    total_steps: int
    next_question: str
    progress_percentage: float
    collected_data: Dict[str, Any]
    is_complete: bool
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class CoexistenceBlueprintRequest:
    """Request to create a coexistence blueprint directly."""
    requirements: Dict[str, Any]
    constraints: Dict[str, Any]
    user_context: UserContext
    session_id: str
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class CoexistenceBlueprintResponse:
    """Response from coexistence blueprint creation."""
    success: bool
    blueprint_id: str
    coexistence_blueprint: Dict[str, Any]
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None


class IOperationsManagement(ABC):
    """
    Operations Management Interface
    
    Defines the contract for operations management operations provided by the Operations Pillar role.
    Handles SOP building, workflow conversion, coexistence analysis, and process optimization.
    
    WHAT (Business Enablement Role): I manage workflows, SOPs, and process optimization
    HOW (Interface): I define the contract for operations management operations
    """
    
    @abstractmethod
    async def create_sop(self, request: SOPRequest) -> SOPResponse:
        """
        Create a new Standard Operating Procedure.
        
        Args:
            request: SOP creation request with content and metadata
            
        Returns:
            SOPResponse with created SOP details
        """
        pass
    
    @abstractmethod
    async def update_sop(self, sop_id: str, request: SOPRequest) -> SOPResponse:
        """
        Update an existing SOP.
        
        Args:
            sop_id: The SOP ID to update
            request: SOP update request with new content
            
        Returns:
            SOPResponse with updated SOP details
        """
        pass
    
    @abstractmethod
    async def get_sop(self, sop_id: str, user_context: UserContext) -> Optional[SOPResponse]:
        """
        Get an SOP by ID.
        
        Args:
            sop_id: The SOP ID to retrieve
            user_context: User context for authorization
            
        Returns:
            SOPResponse or None if not found
        """
        pass
    
    @abstractmethod
    async def list_sops(self, user_context: UserContext, status: Optional[SOPStatus] = None,
                       limit: int = 100, offset: int = 0) -> List[SOPResponse]:
        """
        List SOPs for a user.
        
        Args:
            user_context: User context for authorization
            status: Optional status filter
            limit: Maximum number of SOPs to return
            offset: Number of SOPs to skip
            
        Returns:
            List of SOP responses
        """
        pass
    
    @abstractmethod
    async def create_workflow(self, request: WorkflowRequest) -> WorkflowResponse:
        """
        Create a new workflow.
        
        Args:
            request: Workflow creation request with steps and metadata
            
        Returns:
            WorkflowResponse with created workflow details
        """
        pass
    
    @abstractmethod
    async def update_workflow(self, workflow_id: str, request: WorkflowRequest) -> WorkflowResponse:
        """
        Update an existing workflow.
        
        Args:
            workflow_id: The workflow ID to update
            request: Workflow update request with new steps
            
        Returns:
            WorkflowResponse with updated workflow details
        """
        pass
    
    @abstractmethod
    async def get_workflow(self, workflow_id: str, user_context: UserContext) -> Optional[WorkflowResponse]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: The workflow ID to retrieve
            user_context: User context for authorization
            
        Returns:
            WorkflowResponse or None if not found
        """
        pass
    
    @abstractmethod
    async def list_workflows(self, user_context: UserContext, status: Optional[WorkflowStatus] = None,
                            limit: int = 100, offset: int = 0) -> List[WorkflowResponse]:
        """
        List workflows for a user.
        
        Args:
            user_context: User context for authorization
            status: Optional status filter
            limit: Maximum number of workflows to return
            offset: Number of workflows to skip
            
        Returns:
            List of workflow responses
        """
        pass
    
    @abstractmethod
    async def convert_sop_to_workflow(self, request: ConversionRequest) -> ConversionResponse:
        """
        Convert an SOP to a workflow.
        
        Args:
            request: Conversion request with SOP ID and options
            
        Returns:
            ConversionResponse with converted workflow
        """
        pass
    
    @abstractmethod
    async def convert_workflow_to_sop(self, request: ConversionRequest) -> ConversionResponse:
        """
        Convert a workflow to an SOP.
        
        Args:
            request: Conversion request with workflow ID and options
            
        Returns:
            ConversionResponse with converted SOP
        """
        pass
    
    @abstractmethod
    async def analyze_coexistence(self, request: CoexistenceAnalysisRequest) -> CoexistenceAnalysisResponse:
        """
        Analyze AI-human coexistence opportunities.
        
        Args:
            request: Coexistence analysis request with process description
            
        Returns:
            CoexistenceAnalysisResponse with analysis results
        """
        pass
    
    @abstractmethod
    async def optimize_process(self, request: ProcessOptimizationRequest) -> ProcessOptimizationResponse:
        """
        Optimize a business process.
        
        Args:
            request: Process optimization request with current process
            
        Returns:
            ProcessOptimizationResponse with optimized process
        """
        pass
    
    @abstractmethod
    async def start_sop_wizard(self, user_context: UserContext, session_id: str) -> WizardStepResponse:
        """
        Start an SOP creation wizard.
        
        Args:
            user_context: User context for authorization
            session_id: Session ID for wizard tracking
            
        Returns:
            WizardStepResponse with first wizard step
        """
        pass
    
    @abstractmethod
    async def process_wizard_step(self, request: WizardStepRequest) -> WizardStepResponse:
        """
        Process a wizard step.
        
        Args:
            request: Wizard step request with user input
            
        Returns:
            WizardStepResponse with next step or completion
        """
        pass
    
    @abstractmethod
    async def start_workflow_wizard(self, user_context: UserContext, session_id: str) -> WizardStepResponse:
        """
        Start a workflow creation wizard.
        
        Args:
            user_context: User context for authorization
            session_id: Session ID for wizard tracking
            
        Returns:
            WizardStepResponse with first wizard step
        """
        pass
    
    @abstractmethod
    async def delete_sop(self, sop_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Delete an SOP.
        
        Args:
            sop_id: The SOP ID to delete
            user_context: User context for authorization
            
        Returns:
            Dict with deletion status
        """
        pass
    
    @abstractmethod
    async def delete_workflow(self, workflow_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Delete a workflow.
        
        Args:
            workflow_id: The workflow ID to delete
            user_context: User context for authorization
            
        Returns:
            Dict with deletion status
        """
        pass
    
    @abstractmethod
    async def search_sops(self, query: str, user_context: UserContext,
                         category: Optional[str] = None, limit: int = 100) -> List[SOPResponse]:
        """
        Search SOPs by content or metadata.
        
        Args:
            query: Search query string
            user_context: User context for authorization
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of matching SOP responses
        """
        pass
    
    @abstractmethod
    async def search_workflows(self, query: str, user_context: UserContext,
                              category: Optional[str] = None, limit: int = 100) -> List[WorkflowResponse]:
        """
        Search workflows by content or metadata.
        
        Args:
            query: Search query string
            user_context: User context for authorization
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of matching workflow responses
        """
        pass
    
    @abstractmethod
    async def get_operations_analytics(self, user_context: UserContext,
                                      time_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Get operations management analytics and statistics.
        
        Args:
            user_context: User context for analytics
            time_range: Optional time range for analytics
            
        Returns:
            Dict with analytics data
        """
        pass
    
    @abstractmethod
    async def create_coexistence_blueprint(self, request: CoexistenceBlueprintRequest) -> CoexistenceBlueprintResponse:
        """
        Create a coexistence blueprint directly without analysis.
        
        Args:
            request: Blueprint creation request with requirements and constraints
            
        Returns:
            CoexistenceBlueprintResponse with created blueprint details
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Get health status of the operations management service.
        
        Returns:
            Dict with health status information
        """
        pass
