#!/usr/bin/env python3
"""
Observability Abstraction - Business Logic Implementation

Implements platform observability operations (logs, metrics, traces, agent execution) with business logic.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I manage platform observability data storage with business logic
HOW (Infrastructure Implementation): I implement business rules for observability data storage and retrieval
"""

import logging
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..abstraction_contracts.observability_protocol import ObservabilityProtocol

logger = logging.getLogger(__name__)


def _sanitize_for_storage(data: Any, max_depth: int = 10, visited: Optional[set] = None) -> Any:
    """
    Sanitize data for storage by converting complex objects to simple types.
    
    Handles circular references and non-serializable objects by converting them to strings.
    
    Args:
        data: Data to sanitize
        max_depth: Maximum recursion depth
        visited: Set of visited object IDs to detect circular references
    
    Returns:
        Sanitized data (only simple types: str, int, float, bool, None, dict, list)
    """
    if visited is None:
        visited = set()
    
    # Base case: prevent infinite recursion
    if max_depth <= 0:
        return "<max_depth_exceeded>"
    
    # Handle None
    if data is None:
        return None
    
    # Handle simple types
    if isinstance(data, (str, int, float, bool)):
        return data
    
    # Handle datetime
    if isinstance(data, datetime):
        return data.isoformat()
    
    # Handle circular references
    obj_id = id(data)
    if obj_id in visited:
        return "<circular_reference>"
    visited.add(obj_id)
    
    try:
        # Handle dict
        if isinstance(data, dict):
            return {str(k): _sanitize_for_storage(v, max_depth - 1, visited) for k, v in data.items()}
        
        # Handle list/tuple
        if isinstance(data, (list, tuple)):
            return [_sanitize_for_storage(item, max_depth - 1, visited) for item in data]
        
        # Handle objects with __dict__
        if hasattr(data, '__dict__'):
            return _sanitize_for_storage(data.__dict__, max_depth - 1, visited)
        
        # Try to convert to string for other types
        try:
            return str(data)
        except Exception:
            return "<non_serializable>"
    
    finally:
        visited.discard(obj_id)

class ObservabilityAbstraction(ObservabilityProtocol):
    """
    Observability abstraction with business logic.
    
    Implements platform observability operations (logs, metrics, traces, agent execution)
    with business rules, validation, and enhanced functionality for the platform.
    """
    
    def __init__(self, arango_adapter, config_adapter, di_container=None):
        """Initialize observability abstraction."""
        self.arango_adapter = arango_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "observability_abstraction"
        
        # Observability collections for ArangoDB
        self.platform_logs_collection = "platform_logs"
        self.platform_metrics_collection = "platform_metrics"
        self.platform_traces_collection = "platform_traces"
        self.agent_execution_collection = "agent_executions"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Observability Abstraction initialized")
    
    # ============================================================================
    # PLATFORM LOG OPERATIONS WITH BUSINESS LOGIC
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
        Record platform log entry with business logic validation.
        
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
        try:
            # Validate required fields
            if not message or not service_name:
                raise ValueError("message and service_name are required")
            
            # Validate log level
            valid_levels = ["debug", "info", "warning", "error", "critical"]
            if log_level not in valid_levels:
                raise ValueError(f"log_level must be one of {valid_levels}")
            
            # Sanitize metadata and user_context to prevent circular reference errors
            sanitized_metadata = _sanitize_for_storage(metadata) if metadata else {}
            sanitized_user_context = _sanitize_for_storage(user_context) if user_context else {}
            
            log_doc = {
                "_key": f"log_{uuid.uuid4().hex}",
                "log_level": log_level,
                "message": str(message),  # Ensure message is a string
                "service_name": str(service_name),  # Ensure service_name is a string
                "trace_id": str(trace_id) if trace_id else None,
                "data_classification": "platform",  # Always platform data
                "tenant_id": sanitized_user_context.get("tenant_id") if isinstance(sanitized_user_context, dict) else None,
                "metadata": sanitized_metadata if isinstance(sanitized_metadata, dict) else {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = await self.arango_adapter.create_document(
                self.platform_logs_collection,
                log_doc
            )
            
            self.logger.debug(f"✅ Recorded platform log: {service_name} - {log_level}")
            
            return {
                "success": True,
                "log_id": result.get("_key"),
                "service_name": service_name,
                "log_level": log_level
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record platform log: {e}")
            raise
    
    async def get_platform_logs(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get platform logs with filtering and business logic validation.
        
        Args:
            filters: Optional filters (service_name, log_level, trace_id, etc.)
            limit: Maximum number of results
            user_context: Optional user context for tenant_id
        
        Returns:
            List of log entries
        """
        try:
            filter_conditions = filters or {}
            
            # Add tenant filtering if provided (for correlation, not isolation)
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            result = await self.arango_adapter.find_documents(
                self.platform_logs_collection,
                filter_conditions=filter_conditions,
                limit=limit
            )
            
            # Sort by timestamp descending (most recent first)
            result.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            self.logger.debug(f"✅ Retrieved {len(result)} platform logs")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get platform logs: {e}")
            raise
    
    # ============================================================================
    # PLATFORM METRIC OPERATIONS WITH BUSINESS LOGIC
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
        Record platform metric with business logic validation.
        
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
        try:
            # Validate required fields
            if not metric_name or not service_name:
                raise ValueError("metric_name and service_name are required")
            
            # Sanitize metadata and user_context to prevent circular reference errors
            sanitized_metadata = _sanitize_for_storage(metadata) if metadata else {}
            sanitized_user_context = _sanitize_for_storage(user_context) if user_context else {}
            
            metric_doc = {
                "_key": f"metric_{uuid.uuid4().hex}",
                "metric_name": str(metric_name),  # Ensure metric_name is a string
                "metric_value": float(metric_value),  # Ensure metric_value is a float
                "service_name": str(service_name),  # Ensure service_name is a string
                "trace_id": str(trace_id) if trace_id else None,
                "data_classification": "platform",  # Always platform data
                "tenant_id": sanitized_user_context.get("tenant_id") if isinstance(sanitized_user_context, dict) else None,
                "metadata": sanitized_metadata if isinstance(sanitized_metadata, dict) else {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = await self.arango_adapter.create_document(
                self.platform_metrics_collection,
                metric_doc
            )
            
            self.logger.debug(f"✅ Recorded platform metric: {service_name} - {metric_name} = {metric_value}")
            
            return {
                "success": True,
                "metric_id": result.get("_key"),
                "service_name": service_name,
                "metric_name": metric_name
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record platform metric: {e}")
            raise
    
    async def get_platform_metrics(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get platform metrics with filtering and business logic validation.
        
        Args:
            filters: Optional filters (metric_name, service_name, trace_id, etc.)
            limit: Maximum number of results
            user_context: Optional user context for tenant_id
        
        Returns:
            List of metric entries
        """
        try:
            filter_conditions = filters or {}
            
            # Add tenant filtering if provided (for correlation, not isolation)
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            result = await self.arango_adapter.find_documents(
                self.platform_metrics_collection,
                filter_conditions=filter_conditions,
                limit=limit
            )
            
            # Sort by timestamp descending (most recent first)
            result.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            self.logger.debug(f"✅ Retrieved {len(result)} platform metrics")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get platform metrics: {e}")
            raise
    
    # ============================================================================
    # PLATFORM TRACE OPERATIONS WITH BUSINESS LOGIC
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
        Record platform trace span with business logic validation.
        
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
        try:
            # Validate required fields
            if not trace_id or not span_name or not service_name:
                raise ValueError("trace_id, span_name, and service_name are required")
            
            # Calculate duration if not provided
            if duration_ms is None and end_time:
                duration_ms = (end_time - start_time).total_seconds() * 1000
            
            # Sanitize metadata and user_context to prevent circular reference errors
            sanitized_metadata = _sanitize_for_storage(metadata) if metadata else {}
            sanitized_user_context = _sanitize_for_storage(user_context) if user_context else {}
            
            trace_doc = {
                "_key": f"trace_{uuid.uuid4().hex}",
                "trace_id": str(trace_id),  # Ensure trace_id is a string
                "span_name": str(span_name),  # Ensure span_name is a string
                "service_name": str(service_name),  # Ensure service_name is a string
                "start_time": start_time.isoformat() if isinstance(start_time, datetime) else str(start_time),
                "end_time": end_time.isoformat() if end_time and isinstance(end_time, datetime) else (str(end_time) if end_time else None),
                "duration_ms": float(duration_ms) if duration_ms is not None else None,
                "status": str(status),  # Ensure status is a string
                "data_classification": "platform",  # Always platform data
                "tenant_id": sanitized_user_context.get("tenant_id") if isinstance(sanitized_user_context, dict) else None,
                "metadata": sanitized_metadata if isinstance(sanitized_metadata, dict) else {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = await self.arango_adapter.create_document(
                self.platform_traces_collection,
                trace_doc
            )
            
            self.logger.debug(f"✅ Recorded platform trace: {service_name} - {span_name}")
            
            return {
                "success": True,
                "trace_entry_id": result.get("_key"),
                "trace_id": trace_id,
                "service_name": service_name
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record platform trace: {e}")
            raise
    
    async def get_platform_traces(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get platform traces with filtering and business logic validation.
        
        Args:
            filters: Optional filters (trace_id, service_name, status, etc.)
            limit: Maximum number of results
            user_context: Optional user context for tenant_id
        
        Returns:
            List of trace entries
        """
        try:
            filter_conditions = filters or {}
            
            # Add tenant filtering if provided (for correlation, not isolation)
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            result = await self.arango_adapter.find_documents(
                self.platform_traces_collection,
                filter_conditions=filter_conditions,
                limit=limit
            )
            
            # Sort by timestamp descending (most recent first)
            result.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            self.logger.debug(f"✅ Retrieved {len(result)} platform traces")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get platform traces: {e}")
            raise
    
    # ============================================================================
    # AGENT EXECUTION OPERATIONS WITH BUSINESS LOGIC
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
        Record agent execution for observability with business logic validation.
        
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
        try:
            # Validate required fields
            if not agent_id or not agent_name or not prompt_hash:
                raise ValueError("agent_id, agent_name, and prompt_hash are required")
            
            # Sanitize execution_metadata and user_context to prevent circular reference errors
            sanitized_execution_metadata = _sanitize_for_storage(execution_metadata) if execution_metadata else {}
            sanitized_user_context = _sanitize_for_storage(user_context) if user_context else {}
            
            execution_doc = {
                "_key": f"agent_{uuid.uuid4().hex}",
                "agent_id": str(agent_id),  # Ensure agent_id is a string
                "agent_name": str(agent_name),  # Ensure agent_name is a string
                "prompt_hash": str(prompt_hash),  # Ensure prompt_hash is a string
                "response": str(response) if response else "",  # Ensure response is a string
                "trace_id": str(trace_id) if trace_id else None,
                "data_classification": "platform",  # Always platform data
                "execution_metadata": sanitized_execution_metadata if isinstance(sanitized_execution_metadata, dict) else {},
                "tenant_id": sanitized_user_context.get("tenant_id") if isinstance(sanitized_user_context, dict) else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = await self.arango_adapter.create_document(
                self.agent_execution_collection,
                execution_doc
            )
            
            self.logger.debug(f"✅ Recorded agent execution: {agent_name} ({agent_id})")
            
            return {
                "success": True,
                "execution_id": result.get("_key"),
                "agent_id": agent_id,
                "agent_name": agent_name
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record agent execution: {e}")
            raise
    
    async def get_agent_executions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get agent executions with filtering and business logic validation.
        
        Args:
            filters: Optional filters (agent_id, agent_name, trace_id, etc.)
            limit: Maximum number of results
            user_context: Optional user context for tenant_id
        
        Returns:
            List of agent execution entries
        """
        try:
            filter_conditions = filters or {}
            
            # Add tenant filtering if provided (for correlation, not isolation)
            if user_context and user_context.get("tenant_id"):
                filter_conditions["tenant_id"] = user_context.get("tenant_id")
            
            result = await self.arango_adapter.find_documents(
                self.agent_execution_collection,
                filter_conditions=filter_conditions,
                limit=limit
            )
            
            # Sort by timestamp descending (most recent first)
            result.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            self.logger.debug(f"✅ Retrieved {len(result)} agent executions")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get agent executions: {e}")
            raise
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health with business logic validation."""
        try:
            result = await self.arango_adapter.health_check()
            
            # Add business logic health checks
            if result.get("status") == "healthy":
                # Test observability operations
                test_logs = await self.arango_adapter.find_documents(
                    self.platform_logs_collection,
                    filter_conditions={},
                    limit=1
                )
                result["business_logic"] = "operational"
                result["test_results"] = {
                    "logs_test": len(test_logs),
                    "collections": [
                        self.platform_logs_collection,
                        self.platform_metrics_collection,
                        self.platform_traces_collection,
                        self.agent_execution_collection
                    ]
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            raise



