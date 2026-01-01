#!/usr/bin/env python3
"""
Nurse Service - Observability Module

Micro-module for observability operations using ObservabilityAbstraction.

WHAT: I manage platform observability data (logs, metrics, traces, agent execution)
HOW: I use ObservabilityAbstraction to store platform data in ArangoDB
"""

from typing import Any, Dict, Optional, List
from datetime import datetime


class Observability:
    """Observability module for Nurse service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.observability_abstraction = None
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def _get_observability_abstraction(self):
        """Get observability abstraction (lazy initialization)."""
        if not self.observability_abstraction:
            # Smart City services access Public Works directly
            self.observability_abstraction = self.service.get_infrastructure_abstraction("observability")
            if not self.observability_abstraction:
                self.logger.warning("⚠️ ObservabilityAbstraction not available")
        return self.observability_abstraction
    
    async def record_platform_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record platform event (log, metric, or trace).
        
        Args:
            event_type: Type of event ("log", "metric", "trace")
            event_data: Event data dictionary
            trace_id: Optional trace ID for correlation
            user_context: Optional user context
        
        Returns:
            Dict with result (success, event_id, etc.)
        """
        try:
            abstraction = await self._get_observability_abstraction()
            if not abstraction:
                return {"success": False, "error": "ObservabilityAbstraction not available"}
            
            if event_type == "log":
                return await abstraction.record_platform_log(
                    log_level=event_data.get("level", "info"),
                    message=event_data.get("message", ""),
                    service_name=event_data.get("service_name", "unknown"),
                    trace_id=trace_id,
                    user_context=user_context,
                    metadata=event_data.get("metadata")
                )
            elif event_type == "metric":
                return await abstraction.record_platform_metric(
                    metric_name=event_data.get("metric_name", ""),
                    metric_value=event_data.get("value", 0.0),
                    service_name=event_data.get("service_name", "unknown"),
                    trace_id=trace_id,
                    user_context=user_context,
                    metadata=event_data.get("metadata")
                )
            elif event_type == "trace":
                # Extract trace data from event_data
                start_time = event_data.get("start_time")
                end_time = event_data.get("end_time")
                duration_ms = event_data.get("duration_ms", 0.0)
                
                # Calculate duration if not provided
                if not duration_ms and start_time and end_time:
                    if isinstance(start_time, str):
                        from datetime import datetime
                        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        duration_ms = (end_dt - start_dt).total_seconds() * 1000
                
                return await abstraction.record_platform_trace(
                    trace_id=trace_id or event_data.get("trace_id", ""),
                    span_name=event_data.get("span_name", event_data.get("operation_name", "")),
                    service_name=event_data.get("service_name", "unknown"),
                    start_time=start_time or datetime.utcnow(),
                    end_time=end_time or datetime.utcnow(),
                    duration_ms=duration_ms,
                    status=event_data.get("status", "ok"),
                    user_context=user_context,
                    metadata=event_data.get("metadata")
                )
            else:
                return {"success": False, "error": f"Unknown event type: {event_type}"}
        
        except Exception as e:
            self.logger.error(f"❌ Failed to record platform event: {e}")
            import traceback
            self.logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}
    
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
            agent_id: Agent identifier
            agent_name: Agent name
            prompt_hash: Hash of prompt configuration
            response: Agent response
            trace_id: Optional trace ID for correlation
            execution_metadata: Optional execution metadata (model_name, tokens, latency, etc.)
            user_context: Optional user context
        
        Returns:
            Dict with result (success, execution_id, etc.)
        """
        try:
            abstraction = await self._get_observability_abstraction()
            if not abstraction:
                return {"success": False, "error": "ObservabilityAbstraction not available"}
            
            return await abstraction.record_agent_execution(
                agent_id=agent_id,
                agent_name=agent_name,
                prompt_hash=prompt_hash,
                response=response,
                trace_id=trace_id,
                execution_metadata=execution_metadata,
                user_context=user_context
            )
        
        except Exception as e:
            self.logger.error(f"❌ Failed to record agent execution: {e}")
            import traceback
            self.logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}
    
    async def get_observability_data(
        self,
        data_type: str,  # "logs", "metrics", "traces", "agent_executions"
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query observability data.
        
        Args:
            data_type: Type of data to query ("logs", "metrics", "traces", "agent_executions")
            filters: Optional filters (service_name, trace_id, agent_id, etc.)
            limit: Maximum number of results
            user_context: Optional user context
        
        Returns:
            List of observability data records
        """
        try:
            abstraction = await self._get_observability_abstraction()
            if not abstraction:
                self.logger.warning("⚠️ ObservabilityAbstraction not available")
                return []
            
            if data_type == "logs":
                return await abstraction.get_platform_logs(
                    filters=filters,
                    limit=limit,
                    user_context=user_context
                ) or []
            elif data_type == "metrics":
                return await abstraction.get_platform_metrics(
                    filters=filters,
                    limit=limit,
                    user_context=user_context
                ) or []
            elif data_type == "traces":
                return await abstraction.get_platform_traces(
                    filters=filters,
                    limit=limit,
                    user_context=user_context
                ) or []
            elif data_type == "agent_executions":
                return await abstraction.get_agent_executions(
                    filters=filters,
                    limit=limit,
                    user_context=user_context
                ) or []
            else:
                self.logger.warning(f"⚠️ Unknown data type: {data_type}")
                return []
        
        except Exception as e:
            self.logger.error(f"❌ Failed to get observability data: {e}")
            import traceback
            self.logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return []

