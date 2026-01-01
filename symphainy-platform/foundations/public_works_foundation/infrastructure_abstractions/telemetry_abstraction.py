#!/usr/bin/env python3
"""
Telemetry Abstraction - Infrastructure abstraction for telemetry collection

Coordinates telemetry adapters and handles infrastructure-level concerns like
error handling, retries, logging, and adapter selection for OpenTelemetry integration.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import (
    TelemetryProtocol, TelemetryData, TraceSpan,
    TelemetryType, MetricType
)

class TelemetryAbstraction:
    """
    Telemetry Abstraction - Infrastructure abstraction for telemetry collection
    
    Coordinates different telemetry adapters and handles infrastructure-level concerns.
    This layer provides swappable telemetry engines and infrastructure coordination.
    
    NOTE: This abstraction accepts a telemetry adapter via dependency injection.
          All adapter creation happens in Public Works Foundation Service.
    """
    
    def __init__(self,
                 telemetry_adapter: TelemetryProtocol,  # Required: Accept adapter via DI
                 config_adapter=None,
                 service_name: str = "telemetry_abstraction",
                 di_container=None):
        """
        Initialize Telemetry Abstraction.
        
        Args:
            telemetry_adapter: Telemetry adapter implementing TelemetryProtocol (required)
            config_adapter: Configuration adapter (optional)
            service_name: Service name for logging (optional)
            di_container: DI Container for logging (required)
        """
        if not telemetry_adapter:
            raise ValueError("TelemetryAbstraction requires telemetry_adapter via dependency injection")
        if not di_container:
            raise ValueError("DI Container is required for TelemetryAbstraction initialization")
        
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(service_name)
        self.config_adapter = config_adapter
        
        # Use injected adapter
        self.adapter = telemetry_adapter
        self.adapter_type = getattr(telemetry_adapter, 'adapter_type', 'unknown')
        
        # Infrastructure-level configuration
        self.max_retries = 3
        self.retry_delay = 0.1
        self.timeout = 30
        
        self.logger.info(f"Initialized Telemetry Abstraction with {self.adapter_type} adapter")
    
    async def collect_metric(self, 
                           telemetry_data: TelemetryData) -> bool:
        """
        Collect metric with infrastructure-level coordination.
        
        Expects TelemetryData with type=TelemetryType.METRIC.
        Unit can be stored in metadata['unit'] if needed.
        """
        try:
            # Validate that this is a metric telemetry
            if telemetry_data.type != TelemetryType.METRIC:
                self.logger.warning(f"⚠️ collect_metric called with type={telemetry_data.type}, expected METRIC")
                return False
            
            self.logger.debug(f"Collecting metric '{telemetry_data.name}' with {self.adapter_type}")
            
            # Collect metric with retry logic
            success = await self._execute_with_retry(
                self.adapter.collect_metric,
                telemetry_data
            )
            
            if success:
                self.logger.debug(f"✅ Metric collected: {telemetry_data.name}")
            else:
                self.logger.warning(f"⚠️ Failed to collect metric: {telemetry_data.name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to collect metric '{telemetry_data.name}': {e}")
            raise  # Re-raise for service layer to handle

        """Collect trace with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Collecting trace '{trace_data.name}' with {self.adapter_type}")
            
            # Collect trace with retry logic
            success = await self._execute_with_retry(
                self.adapter.collect_trace,
                trace_data
            )
            
            if success:
                self.logger.debug(f"✅ Trace collected: {trace_data.name}")
            else:
                self.logger.warning(f"⚠️ Failed to collect trace: {trace_data.name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to collect trace '{trace_data.name}': {e}")
            raise  # Re-raise for service layer to handle

        """
        Collect log with infrastructure-level coordination.
        
        Expects TelemetryData with type=TelemetryType.LOG.
        """
        try:
            # Validate that this is a log telemetry
            if log_data.type != TelemetryType.LOG:
                self.logger.warning(f"⚠️ collect_log called with type={log_data.type}, expected LOG")
                return False
            
            self.logger.debug(f"Collecting log '{log_data.name}' with {self.adapter_type}")
            
            # Collect log with retry logic
            success = await self._execute_with_retry(
                self.adapter.collect_log,
                log_data
            )
            
            if success:
                self.logger.debug("✅ Log collected")
            else:
                self.logger.warning("⚠️ Failed to collect log")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to collect log: {e}")
            raise  # Re-raise for service layer to handle

        """
        Collect event with infrastructure-level coordination.
        
        Expects TelemetryData with type=TelemetryType.EVENT.
        """
        try:
            # Validate that this is an event telemetry
            if event_data.type != TelemetryType.EVENT:
                self.logger.warning(f"⚠️ collect_event called with type={event_data.type}, expected EVENT")
                return False
            
            self.logger.debug(f"Collecting event '{event_data.name}' with {self.adapter_type}")
            
            # Collect event with retry logic
            success = await self._execute_with_retry(
                self.adapter.collect_event,
                event_data
            )
            
            if success:
                self.logger.debug(f"✅ Event collected: {event_data.name}")
            else:
                self.logger.warning(f"⚠️ Failed to collect event: {event_data.name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to collect event '{event_data.name}': {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_metrics(self,
                         query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get metrics with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting metrics with query using {self.adapter_type}")
            
            # Get metrics with retry logic
            metrics = await self._execute_with_retry(
                self.adapter.get_metrics,
                query,
                time_range
            )
            
            self.logger.debug(f"✅ Retrieved {len(metrics)} metrics")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_traces(self,
                        query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get traces with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting traces with query using {self.adapter_type}")
            
            # Get traces with retry logic
            traces = await self._execute_with_retry(
                self.adapter.get_traces,
                query,
                time_range
            )
            
            self.logger.debug(f"✅ Retrieved {len(traces)} traces")
            return traces
            
        except Exception as e:
            self.logger.error(f"Failed to get traces: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_logs(self,
                      query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get logs with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting logs with query using {self.adapter_type}")
            
            # Get logs with retry logic
            logs = await self._execute_with_retry(
                self.adapter.get_logs,
                query,
                time_range
            )
            
            self.logger.debug(f"✅ Retrieved {len(logs)} logs")
            return logs
            
        except Exception as e:
            self.logger.error(f"Failed to get logs: {e}")
            raise  # Re-raise for service layer to handle

        """Check telemetry infrastructure health."""
        try:
            self.logger.debug("Checking telemetry infrastructure health")
            
            # Check adapter health
            adapter_health = await self.adapter.health_check()
            
            # Add abstraction-level health info
            return {
                "status": "healthy" if adapter_health.get("status") == "healthy" else "unhealthy",
                "abstraction_layer": "telemetry_abstraction",
                "adapter_type": self.adapter_type,
                "adapter_health": adapter_health,
                "infrastructure_metrics": {
                    "max_retries": self.max_retries,
                    "retry_delay": self.retry_delay,
                    "timeout": self.timeout
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Telemetry infrastructure health check failed: {e}")
    
    # ============================================================================
    # IMPLEMENT ABSTRACT METHODS FROM TelemetryProtocol
    # ============================================================================
    
            raise  # Re-raise for service layer to handle

        """Record a metric (abstract method implementation)."""
        from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import TelemetryData, TelemetryType, MetricType
        # Build kwargs - only include labels if provided (default factory handles None)
        kwargs = {
            "name": name,
            "value": value,
            "type": TelemetryType.METRIC,
            "metadata": {"metric_type": metric_type.value if hasattr(metric_type, 'value') else str(metric_type)}
        }
        if labels is not None:
            kwargs["labels"] = labels
        telemetry_data = TelemetryData(**kwargs)
        return await self.collect_metric(telemetry_data)
    
    async def create_span(self, name: str, attributes: Dict[str, Any] = None) -> str:
        """Create a new trace span (abstract method implementation)."""
        import uuid
        span_id = str(uuid.uuid4())
        # Store span in adapter if it supports it
        if hasattr(self.adapter, 'create_span'):
            span_id = await self.adapter.create_span(name, attributes)
        return span_id
    
    async def end_span(self, span_id: str, attributes: Dict[str, Any] = None) -> bool:
        """End a trace span (abstract method implementation)."""
        if hasattr(self.adapter, 'end_span'):
            return await self.adapter.end_span(span_id, attributes)
        return True
    
    async def add_span_event(self, span_id: str, name: str, 
                           attributes: Dict[str, Any] = None) -> bool:
        """Add event to span (abstract method implementation)."""
        if hasattr(self.adapter, 'add_span_event'):
            return await self.adapter.add_span_event(span_id, name, attributes)
        return True
    
    async def log_event(self, message: str, level: str = "INFO", 
                       attributes: Dict[str, Any] = None) -> bool:
        """Log an event (abstract method implementation)."""
        from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import TelemetryData, TelemetryType
        telemetry_data = TelemetryData(
            name="log_event",
            value=1.0,
            type=TelemetryType.LOG,
            labels={"level": level}
        )
        return await self.collect_log(telemetry_data)
    
    def _initialize_adapter(self, adapter_type: str):
        """Initialize the specified telemetry adapter."""
        if adapter_type == "opentelemetry":
            return TelemetryAdapter(
                service_name=self.service_name,
                service_version="1.0.0"
            )
        else:
            self.logger.warning(f"Unknown adapter type {adapter_type}, falling back to opentelemetry")
            return TelemetryAdapter(
                service_name=self.service_name,
                service_version="1.0.0"
            )
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                self.logger.error(f"All {self.max_retries + 1} attempts failed")
        
                raise  # Re-raise for service layer to handle

