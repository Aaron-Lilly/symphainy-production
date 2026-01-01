"""
Data Analysis Protocol - Contract for data analysis infrastructure

Defines the contract for data analysis infrastructure capabilities
including data processing, analysis, and quality management.

WHAT (Infrastructure Role): I provide data analysis infrastructure capabilities
HOW (Infrastructure Contract): I define protocols for data analysis operations
"""

from typing import Dict, Any, List, Optional, Protocol
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class AnalysisType(Enum):
    """Data analysis types."""
    DESCRIPTIVE = "descriptive"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"
    DIAGNOSTIC = "diagnostic"
    CORRELATION = "correlation"
    ANOMALY_DETECTION = "anomaly_detection"
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    TIME_SERIES = "time_series"


class DataQualityLevel(Enum):
    """Data quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass(frozen=True)
class DataAnalysisRequest:
    """Data analysis request."""
    data: Dict[str, Any]
    analysis_type: AnalysisType
    parameters: Dict[str, Any]
    user_context: Dict[str, Any]
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class DataAnalysisResponse:
    """Data analysis response."""
    success: bool
    analysis_id: str
    results: Dict[str, Any]
    confidence_score: float
    processing_time: float
    data_quality: DataQualityLevel
    recommendations: List[str]
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow())


@dataclass(frozen=True)
class DataQualityReport:
    """Data quality report."""
    completeness: float
    accuracy: float
    consistency: float
    timeliness: float
    validity: float
    overall_score: float
    issues: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class DataProcessingRequest:
    """Data processing request."""
    data: Dict[str, Any]
    processing_type: str
    parameters: Dict[str, Any]
    user_context: Dict[str, Any]
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})


@dataclass(frozen=True)
class DataProcessingResponse:
    """Data processing response."""
    success: bool
    processing_id: str
    processed_data: Dict[str, Any]
    processing_time: float
    transformations_applied: List[str]
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, 'metadata', {})
        if self.timestamp is None:
            object.__setattr__(self, 'timestamp', datetime.utcnow())


class DataAnalysisProtocol(Protocol):
    """Protocol for data analysis infrastructure."""
    
    async def analyze_data(self, request: DataAnalysisRequest) -> DataAnalysisResponse:
        """Analyze data using specified analysis type."""
        ...
    
    async def get_analysis_types(self, user_context: Dict[str, Any]) -> List[AnalysisType]:
        """Get available analysis types."""
        ...
    
    async def validate_data_quality(self, data: Dict[str, Any], user_context: Dict[str, Any]) -> DataQualityReport:
        """Validate data quality."""
        ...
    
    async def process_data(self, request: DataProcessingRequest) -> DataProcessingResponse:
        """Process data with specified transformations."""
        ...
    
    async def get_analysis_capabilities(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get data analysis capabilities."""
        ...
    
    async def get_analysis_history(self, user_context: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Get analysis history."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check data analysis service health."""
        ...
