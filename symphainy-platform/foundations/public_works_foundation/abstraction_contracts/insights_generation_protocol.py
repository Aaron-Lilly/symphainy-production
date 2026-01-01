"""
Insights Generation Protocol - Contract for insights generation infrastructure

Defines the contract for insights generation infrastructure capabilities
including business intelligence, analytics, and insights processing.

WHAT (Infrastructure Role): I provide insights generation infrastructure capabilities
HOW (Infrastructure Contract): I define protocols for insights generation operations
"""

from typing import Dict, Any, List, Optional, Protocol
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class InsightType(Enum):
    """Insight types."""
    TREND = "trend"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    CUSTOMER = "customer"
    OPERATIONAL = "operational"


class InsightPriority(Enum):
    """Insight priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BusinessDomain(Enum):
    """Business domains."""
    FINANCE = "finance"
    OPERATIONS = "operations"
    CUSTOMER = "customer"
    MARKETING = "marketing"
    SALES = "sales"
    HR = "hr"
    IT = "it"
    COMPLIANCE = "compliance"


@dataclass(frozen=True)
class InsightsGenerationRequest:
    """Insights generation request."""
    data: Dict[str, Any]
    insight_types: List[InsightType]
    business_domains: List[BusinessDomain]
    parameters: Dict[str, Any]
    user_context: Dict[str, Any]
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class InsightsGenerationResponse:
    """Insights generation response."""
    success: bool
    insights_id: str
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    business_impact: str
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow())


@dataclass(frozen=True)
class BusinessIntelligenceRequest:
    """Business intelligence request."""
    data: Dict[str, Any]
    analysis_type: str
    business_context: Dict[str, Any]
    parameters: Dict[str, Any]
    user_context: Dict[str, Any]
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class BusinessIntelligenceResponse:
    """Business intelligence response."""
    success: bool
    bi_id: str
    analysis_results: Dict[str, Any]
    business_insights: List[Dict[str, Any]]
    strategic_recommendations: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow())


@dataclass(frozen=True)
class AnalyticsRequest:
    """Analytics request."""
    data: Dict[str, Any]
    analytics_type: str
    metrics: List[str]
    parameters: Dict[str, Any]
    user_context: Dict[str, Any]
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class AnalyticsResponse:
    """Analytics response."""
    success: bool
    analytics_id: str
    metrics_results: Dict[str, Any]
    analytics_insights: List[Dict[str, Any]]
    performance_indicators: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow())


@dataclass(frozen=True)
class InsightTemplate:
    """Insight template."""
    template_id: str
    name: str
    insight_type: InsightType
    business_domain: BusinessDomain
    default_config: Dict[str, Any]
    parameters: List[str]
    description: str
    category: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


class InsightsGenerationProtocol(Protocol):
    """Protocol for insights generation infrastructure."""
    
    async def generate_insights(self, request: InsightsGenerationRequest) -> InsightsGenerationResponse:
        """Generate insights from data."""
        ...
    
    async def generate_business_intelligence(self, request: BusinessIntelligenceRequest) -> BusinessIntelligenceResponse:
        """Generate business intelligence analysis."""
        ...
    
    async def run_analytics(self, request: AnalyticsRequest) -> AnalyticsResponse:
        """Run analytics on data."""
        ...
    
    async def get_insight_types(self, user_context: Dict[str, Any]) -> List[InsightType]:
        """Get available insight types."""
        ...
    
    async def get_business_domains(self, user_context: Dict[str, Any]) -> List[BusinessDomain]:
        """Get available business domains."""
        ...
    
    async def get_insight_templates(self, user_context: Dict[str, Any]) -> List[InsightTemplate]:
        """Get available insight templates."""
        ...
    
    async def get_insights_capabilities(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get insights generation capabilities."""
        ...
    
    async def get_insights_history(self, user_context: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Get insights generation history."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check insights generation service health."""
        ...
