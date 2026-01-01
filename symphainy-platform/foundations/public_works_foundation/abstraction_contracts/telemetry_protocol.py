#!/usr/bin/env python3
"""
Telemetry Protocol

Abstraction contract for telemetry collection and metrics storage.
Defines interfaces for telemetry operations.
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class TelemetryType(Enum):
    """Telemetry type enumeration."""
    METRIC = "metric"
    TRACE = "trace"
    LOG = "log"
    EVENT = "event"


class MetricType(Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class TelemetryData:
    """Telemetry data point."""
    name: str
    value: float
    type: TelemetryType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceSpan:
    """Trace span data."""
    name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)


class TelemetryProtocol(Protocol):
    """Protocol for telemetry operations."""
    
    async def record_metric(self, name: str, value: float, 
                           metric_type: MetricType, labels: Dict[str, str] = None) -> bool:
        """
        Record a metric.
        
        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            labels: Metric labels
            
        Returns:
            bool: Success status
        """
        ...
    
    async def create_span(self, name: str, attributes: Dict[str, Any] = None) -> str:
        """
        Create a new trace span.
        
        Args:
            name: Span name
            attributes: Span attributes
            
        Returns:
            str: Span ID
        """
        ...
    
    async def end_span(self, span_id: str, attributes: Dict[str, Any] = None) -> bool:
        """
        End a trace span.
        
        Args:
            span_id: Span ID
            attributes: Final span attributes
            
        Returns:
            bool: Success status
        """
        ...
    
    async def add_span_event(self, span_id: str, name: str, 
                           attributes: Dict[str, Any] = None) -> bool:
        """
        Add event to span.
        
        Args:
            span_id: Span ID
            name: Event name
            attributes: Event attributes
            
        Returns:
            bool: Success status
        """
        ...
    
    async def log_event(self, message: str, level: str = "INFO", 
                       attributes: Dict[str, Any] = None) -> bool:
        """
        Log an event.
        
        Args:
            message: Log message
            level: Log level
            attributes: Log attributes
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_metrics(self, name: str, start_time: datetime = None, 
                         end_time: datetime = None) -> List[TelemetryData]:
        """
        Get metrics by name.
        
        Args:
            name: Metric name
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            List[TelemetryData]: Telemetry data
        """
        ...
    
    async def get_traces(self, trace_id: str = None, 
                        start_time: datetime = None, 
                        end_time: datetime = None) -> List[TraceSpan]:
        """
        Get trace data.
        
        Args:
            trace_id: Specific trace ID
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            List[TraceSpan]: Trace spans
        """
        ...



