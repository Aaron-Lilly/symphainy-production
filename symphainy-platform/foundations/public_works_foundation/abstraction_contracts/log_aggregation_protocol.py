#!/usr/bin/env python3
"""
Log Aggregation Protocol - Abstraction Contract

Defines the contract for log aggregation operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define the contract for log aggregation operations
HOW (Infrastructure Implementation): I provide abstract methods for log aggregation
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class LogEntry:
    """Log entry data structure."""
    line: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    level: Optional[str] = None
    service_name: Optional[str] = None
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogQuery:
    """Log query parameters."""
    query: str  # LogQL query string
    limit: int = 100
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class LogAggregationProtocol(Protocol):
    """Protocol for log aggregation operations."""
    
    async def push_logs(self, logs: List[LogEntry]) -> bool:
        """
        Push logs to aggregation backend.
        
        Args:
            logs: List of log entries to push
            
        Returns:
            True if successful, False otherwise
        """
        ...
    
    async def query_logs(self, query: LogQuery) -> List[LogEntry]:
        """
        Query logs from aggregation backend.
        
        Args:
            query: Log query parameters
            
        Returns:
            List of log entries matching the query
        """
        ...
    
    async def search_logs(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search logs with filters.
        
        Args:
            search_params: Search parameters including:
                - service_name: Filter by service name
                - level: Filter by log level
                - time_range: Time range for search
                - text: Text search in log lines
        
        Returns:
            Dict containing search results
        """
        ...
    
    async def get_log_metrics(self, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get log volume and aggregation metrics.
        
        Args:
            time_range: Time range for metrics (start, end, or hours/days)
        
        Returns:
            Dict containing metrics:
            - volume: Total log volume
            - by_service: Log volume by service
            - by_level: Log volume by level
            - status: Aggregation status
        """
        ...

