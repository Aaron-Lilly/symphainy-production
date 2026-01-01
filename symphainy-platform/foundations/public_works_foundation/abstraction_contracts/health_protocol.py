"""
Health Protocol - Infrastructure abstraction contracts for health monitoring

Defines the core contracts for health monitoring, metrics collection,
alerting, and health status management at the infrastructure level.
"""

from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class HealthType(Enum):
    """Types of health monitoring"""
    SYSTEM = "system"
    SERVICE = "service"
    AGENT = "agent"
    APPLICATION = "application"
    INFRASTRUCTURE = "infrastructure"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthContext:
    """Context for health monitoring"""
    service_id: Optional[str] = None
    agent_id: Optional[str] = None
    tenant_id: Optional[str] = None
    environment: Optional[str] = None
    region: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class HealthMetric:
    """Health metric definition"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    labels: Dict[str, str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class HealthCheck:
    """Health check definition"""
    check_id: str
    check_name: str
    health_type: HealthType
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class HealthAlert:
    """Health alert definition"""
    alert_id: str
    alert_name: str
    severity: AlertSeverity
    status: HealthStatus
    message: str
    timestamp: datetime
    service_id: Optional[str] = None
    agent_id: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class HealthReport:
    """Comprehensive health report"""
    report_id: str
    service_id: Optional[str] = None
    agent_id: Optional[str] = None
    overall_status: HealthStatus = HealthStatus.UNKNOWN
    health_checks: List[HealthCheck] = None
    metrics: List[HealthMetric] = None
    alerts: List[HealthAlert] = None
    timestamp: datetime = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.health_checks is None:
            self.health_checks = []
        if self.metrics is None:
            self.metrics = []
        if self.alerts is None:
            self.alerts = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class HealthProtocol(Protocol):
    """Protocol for health monitoring infrastructure"""
    
    async def check_health(self, 
                         health_type: HealthType,
                         context: HealthContext) -> HealthCheck:
        """Perform a health check for the specified type"""
        ...
    
    async def check_multiple_health(self, 
                                  health_types: List[HealthType],
                                  context: HealthContext) -> List[HealthCheck]:
        """Perform multiple health checks"""
        ...
    
    async def collect_metrics(self, 
                            health_type: HealthType,
                            context: HealthContext) -> List[HealthMetric]:
        """Collect health metrics for the specified type"""
        ...
    
    async def get_health_report(self, 
                              service_id: str,
                              context: HealthContext) -> HealthReport:
        """Get comprehensive health report for a service"""
        ...
    
    async def create_alert(self, 
                         alert: HealthAlert) -> bool:
        """Create a health alert"""
        ...
    
    async def resolve_alert(self, 
                          alert_id: str) -> bool:
        """Resolve a health alert"""
        ...
    
    async def get_active_alerts(self, 
                              service_id: Optional[str] = None) -> List[HealthAlert]:
        """Get active health alerts"""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health monitoring system health"""
        ...


class MetricsProtocol(Protocol):
    """Protocol for metrics collection infrastructure"""
    
    async def collect_system_metrics(self, context: HealthContext) -> List[HealthMetric]:
        """Collect system-level metrics (CPU, memory, disk)"""
        ...
    
    async def collect_service_metrics(self, service_id: str, context: HealthContext) -> List[HealthMetric]:
        """Collect service-level metrics"""
        ...
    
    async def collect_agent_metrics(self, agent_id: str, context: HealthContext) -> List[HealthMetric]:
        """Collect agent-specific metrics"""
        ...
    
    async def collect_application_metrics(self, context: HealthContext) -> List[HealthMetric]:
        """Collect application-level metrics"""
        ...
    
    async def collect_infrastructure_metrics(self, context: HealthContext) -> List[HealthMetric]:
        """Collect infrastructure metrics (database, cache, etc.)"""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check metrics collection system health"""
        ...


class AlertingProtocol(Protocol):
    """Protocol for alerting infrastructure"""
    
    async def send_alert(self, alert: HealthAlert) -> bool:
        """Send a health alert"""
        ...
    
    async def send_bulk_alerts(self, alerts: List[HealthAlert]) -> Dict[str, bool]:
        """Send multiple health alerts"""
        ...
    
    async def get_alert_channels(self) -> List[Dict[str, Any]]:
        """Get available alert channels"""
        ...
    
    async def test_alert_channel(self, channel_id: str) -> bool:
        """Test an alert channel"""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check alerting system health"""
        ...

