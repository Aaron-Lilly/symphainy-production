#!/usr/bin/env python3
"""
Alerting Protocol

Abstraction contract for alerting and notification management.
Defines interfaces for alerting operations.
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status enumeration."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Alert data."""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Alert rule definition."""
    name: str
    condition: str
    severity: AlertSeverity
    enabled: bool
    notification_channels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AlertingProtocol(Protocol):
    """Protocol for alerting operations."""
    
    async def create_alert(self, title: str, message: str, severity: AlertSeverity,
                          source: str, metadata: Dict[str, Any] = None) -> str:
        """
        Create a new alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            source: Alert source
            metadata: Additional metadata
            
        Returns:
            str: Alert ID
        """
        ...
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """
        Get alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Optional[Alert]: Alert data
        """
        ...
    
    async def update_alert_status(self, alert_id: str, status: AlertStatus) -> bool:
        """
        Update alert status.
        
        Args:
            alert_id: Alert ID
            status: New status
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_active_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        """
        Get active alerts.
        
        Args:
            severity: Filter by severity
            
        Returns:
            List[Alert]: Active alerts
        """
        ...
    
    async def create_alert_rule(self, rule: AlertRule) -> str:
        """
        Create an alert rule.
        
        Args:
            rule: Alert rule definition
            
        Returns:
            str: Rule ID
        """
        ...
    
    async def evaluate_alert_rules(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Evaluate alert rules against metrics.
        
        Args:
            metrics: Current metrics data
            
        Returns:
            List[str]: Triggered alert IDs
        """
        ...
    
    async def send_notification(self, alert_id: str, channels: List[str]) -> bool:
        """
        Send notification for alert.
        
        Args:
            alert_id: Alert ID
            channels: Notification channels
            
        Returns:
            bool: Success status
        """
        ...



