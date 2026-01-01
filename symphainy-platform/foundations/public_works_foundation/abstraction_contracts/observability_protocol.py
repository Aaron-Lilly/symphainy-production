#!/usr/bin/env python3
"""
Observability Protocol - Abstraction Contract

Defines the contract for platform observability operations (logs, metrics, traces, agent execution).
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define the contract for platform observability operations
HOW (Infrastructure Implementation): I provide abstract methods for observability data storage
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime

class ObservabilityProtocol(Protocol):
    """Protocol for platform observability operations."""
    
    # ============================================================================
    # PLATFORM LOG OPERATIONS
    # ============================================================================
    
    async def record_platform_log(
        self,
        log_level: str,
        message: str,
        service_name: str,
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record platform log entry.
        
        Args:
            log_level: Log level (debug, info, warning, error, critical)
            message: Log message
            service_name: Name of the service generating the log
            trace_id: Optional trace ID for correlation
            user_context: Optional user context for tenant_id
            metadata: Optional additional metadata
        
        Returns:
            Storage result with log entry ID
        """
        ...
    
    async def get_platform_logs(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get platform logs with filtering.
        
        Args:
            filters: Optional filters (service_name, log_level, trace_id, etc.)
            limit: Maximum number of results
            user_context: Optional user context for tenant_id
        
        Returns:
            List of log entries
        """
        ...
    
    # ============================================================================
    # PLATFORM METRIC OPERATIONS
    # ============================================================================
    
    async def record_platform_metric(
        self,
        metric_name: str,
        metric_value: float,
        service_name: str,
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record platform metric.
        
        Args:
            metric_name: Name of the metric
            metric_value: Metric value
            service_name: Name of the service generating the metric
            trace_id: Optional trace ID for correlation
            user_context: Optional user context for tenant_id
            metadata: Optional additional metadata
        
        Returns:
            Storage result with metric entry ID
        """
        ...
    
    async def get_platform_metrics(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get platform metrics with filtering.
        
        Args:
            filters: Optional filters (metric_name, service_name, trace_id, etc.)
            limit: Maximum number of results
            user_context: Optional user context for tenant_id
        
        Returns:
            List of metric entries
        """
        ...
    
    # ============================================================================
    # PLATFORM TRACE OPERATIONS
    # ============================================================================
    
    async def record_platform_trace(
        self,
        trace_id: str,
        span_name: str,
        service_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        duration_ms: Optional[float] = None,
        status: str = "ok",
        user_context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record platform trace span.
        
        Args:
            trace_id: Trace ID
            span_name: Name of the span
            service_name: Name of the service generating the trace
            start_time: Span start time
            end_time: Optional span end time
            duration_ms: Optional duration in milliseconds
            status: Span status (ok, error, etc.)
            user_context: Optional user context for tenant_id
            metadata: Optional additional metadata
        
        Returns:
            Storage result with trace entry ID
        """
        ...
    
    async def get_platform_traces(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get platform traces with filtering.
        
        Args:
            filters: Optional filters (trace_id, service_name, status, etc.)
            limit: Maximum number of results
            user_context: Optional user context for tenant_id
        
        Returns:
            List of trace entries
        """
        ...
    
    # ============================================================================
    # AGENT EXECUTION OPERATIONS
    # ============================================================================
    
    async def record_agent_execution(
        self,
        agent_id: str,
        agent_name: str,
        prompt_hash: str,
        response: str,
        trace_id: Optional[str] = None,
        execution_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record agent execution for observability.
        
        Args:
            agent_id: Agent ID
            agent_name: Agent name
            prompt_hash: Hash of the prompt used
            response: Agent response
            trace_id: Optional trace ID for correlation
            execution_metadata: Optional execution metadata (tokens, latency, etc.)
            user_context: Optional user context for tenant_id
        
        Returns:
            Storage result with agent execution entry ID
        """
        ...
    
    async def get_agent_executions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get agent executions with filtering.
        
        Args:
            filters: Optional filters (agent_id, agent_name, trace_id, etc.)
            limit: Maximum number of results
            user_context: Optional user context for tenant_id
        
        Returns:
            List of agent execution entries
        """
        ...
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of the observability system.
        
        Returns:
            Dict containing health status information
        """
        ...



