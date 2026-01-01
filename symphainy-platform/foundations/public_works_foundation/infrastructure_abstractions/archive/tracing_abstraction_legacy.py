#!/usr/bin/env python3
"""
Tracing Abstraction - Infrastructure abstraction for distributed tracing

Coordinates tracing adapters and handles infrastructure-level concerns like
error handling, retries, logging, and adapter selection for Tempo integration.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from foundations.public_works_foundation.abstraction_contracts.tracing_protocol import (
    TracingProtocol, TraceContext, SpanContext, TraceData, SpanData,
    TraceStatus, SpanStatus
)
from foundations.public_works_foundation.infrastructure_adapters.tempo_adapter import TempoAdapter
from foundations.public_works_foundation.infrastructure_adapters.opentelemetry_tracing_adapter import OpenTelemetryTracingAdapter


class TracingAbstraction(TracingProtocol):
    """
    Tracing Abstraction - Infrastructure abstraction for distributed tracing
    
    Coordinates different tracing adapters and handles infrastructure-level concerns.
    This layer provides swappable tracing engines and infrastructure coordination.
    """
    
    def __init__(self, 
                 adapter_type: str = "tempo",
                 config_adapter=None,
                 service_name: str = "tracing_abstraction"):
        """Initialize Tracing Abstraction."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"{service_name}")
        self.config_adapter = config_adapter
        
        # Initialize the selected adapter
        self.adapter = self._initialize_adapter(adapter_type)
        self.adapter_type = adapter_type
        
        # Infrastructure-level configuration
        self.max_retries = 3
        self.retry_delay = 0.1
        self.timeout = 30
        
        self.logger.info(f"Initialized Tracing Abstraction with {adapter_type} adapter")
    
    async def start_trace(self, 
                         trace_name: str,
                         context: TraceContext) -> str:
        """Start a distributed trace with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Starting trace '{trace_name}' with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_trace_context(context)
            
            # Start trace with retry logic
            trace_id = await self._execute_with_retry(
                self.adapter.start_trace,
                trace_name,
                enhanced_context
            )
            
            self.logger.info(f"✅ Trace started: {trace_name} ({trace_id})")
            return trace_id
            
        except Exception as e:
            self.logger.error(f"Failed to start trace '{trace_name}': {e}")
            raise e
    
    async def add_span(self, 
                      trace_id: str,
                      span_name: str,
                      context: SpanContext) -> str:
        """Add a span to an existing trace with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Adding span '{span_name}' to trace {trace_id} with {self.adapter_type}")
            
            # Add infrastructure-level context
            enhanced_context = self._enhance_span_context(context)
            
            # Add span with retry logic
            span_id = await self._execute_with_retry(
                self.adapter.add_span,
                trace_id,
                span_name,
                enhanced_context
            )
            
            self.logger.debug(f"✅ Span added: {span_name} ({span_id}) to trace {trace_id}")
            return span_id
            
        except Exception as e:
            self.logger.error(f"Failed to add span '{span_name}' to trace {trace_id}: {e}")
            raise e
    
    async def end_span(self, 
                      span_id: str,
                      status: SpanStatus = SpanStatus.SUCCESS) -> bool:
        """End a span with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Ending span {span_id} with status {status.value} using {self.adapter_type}")
            
            # End span with retry logic
            success = await self._execute_with_retry(
                self.adapter.end_span,
                span_id,
                status
            )
            
            if success:
                self.logger.debug(f"✅ Span ended: {span_id}")
            else:
                self.logger.warning(f"⚠️ Failed to end span: {span_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to end span {span_id}: {e}")
            return False
    
    async def end_trace(self, 
                       trace_id: str,
                       status: TraceStatus = TraceStatus.SUCCESS) -> bool:
        """End a distributed trace with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Ending trace {trace_id} with status {status.value} using {self.adapter_type}")
            
            # End trace with retry logic
            success = await self._execute_with_retry(
                self.adapter.end_trace,
                trace_id,
                status
            )
            
            if success:
                self.logger.info(f"✅ Trace ended: {trace_id}")
            else:
                self.logger.warning(f"⚠️ Failed to end trace: {trace_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to end trace {trace_id}: {e}")
            return False
    
    async def get_trace(self, trace_id: str) -> Optional[TraceData]:
        """Retrieve trace data with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Retrieving trace {trace_id} using {self.adapter_type}")
            
            # Get trace with retry logic
            trace_data = await self._execute_with_retry(
                self.adapter.get_trace,
                trace_id
            )
            
            if trace_data:
                self.logger.debug(f"✅ Trace retrieved: {trace_id}")
            else:
                self.logger.warning(f"⚠️ Trace not found: {trace_id}")
            
            return trace_data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve trace {trace_id}: {e}")
            return None
    
    async def search_traces(self, 
                           query: Dict[str, Any],
                           limit: int = 100) -> List[TraceData]:
        """Search traces with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Searching traces with query using {self.adapter_type}")
            
            # Search traces with retry logic
            traces = await self._execute_with_retry(
                self.adapter.search_traces,
                query,
                limit
            )
            
            self.logger.debug(f"✅ Found {len(traces)} traces")
            return traces
            
        except Exception as e:
            self.logger.error(f"Failed to search traces: {e}")
            return []
    
    async def get_trace_metrics(self, 
                               trace_id: str) -> Dict[str, Any]:
        """Get trace metrics with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting metrics for trace {trace_id} using {self.adapter_type}")
            
            # Get metrics with retry logic
            metrics = await self._execute_with_retry(
                self.adapter.get_trace_metrics,
                trace_id
            )
            
            self.logger.debug(f"✅ Trace metrics retrieved: {trace_id}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get trace metrics for {trace_id}: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check tracing infrastructure health."""
        try:
            self.logger.debug("Checking tracing infrastructure health")
            
            # Check adapter health
            adapter_health = await self.adapter.health_check()
            
            # Add abstraction-level health info
            return {
                "status": "healthy" if adapter_health.get("status") == "healthy" else "unhealthy",
                "abstraction_layer": "tracing_abstraction",
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
            self.logger.error(f"Tracing infrastructure health check failed: {e}")
            return {
                "status": "unhealthy",
                "abstraction_layer": "tracing_abstraction",
                "adapter_type": self.adapter_type,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def switch_adapter(self, new_adapter_type: str) -> bool:
        """Switch to a different tracing adapter."""
        try:
            self.logger.info(f"Switching from {self.adapter_type} to {new_adapter_type}")
            
            # Initialize new adapter
            new_adapter = self._initialize_adapter(new_adapter_type)
            
            # Test new adapter
            health = await new_adapter.health_check()
            if health.get("status") != "healthy":
                self.logger.error(f"New adapter {new_adapter_type} is not healthy")
                return False
            
            # Switch adapters
            old_adapter = self.adapter
            self.adapter = new_adapter
            self.adapter_type = new_adapter_type
            
            self.logger.info(f"Successfully switched to {new_adapter_type} adapter")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to switch to {new_adapter_type} adapter: {e}")
            return False
    
    def _initialize_adapter(self, adapter_type: str):
        """Initialize the specified tracing adapter."""
        if adapter_type == "tempo":
            return TempoAdapter()
        elif adapter_type == "opentelemetry":
            return OpenTelemetryTracingAdapter()
        else:
            self.logger.warning(f"Unknown adapter type {adapter_type}, falling back to tempo")
            return TempoAdapter()
    
    def _enhance_trace_context(self, context: TraceContext) -> TraceContext:
        """Add infrastructure-level context enhancements."""
        # Add infrastructure metadata
        enhanced_metadata = context.metadata or {}
        enhanced_metadata.update({
            "abstraction_layer": "tracing_abstraction",
            "adapter_type": self.adapter_type,
            "trace_timestamp": datetime.utcnow().isoformat()
        })
        
        # Create enhanced context
        return TraceContext(
            trace_id=context.trace_id or str(uuid.uuid4()),
            parent_trace_id=context.parent_trace_id,
            service_name=context.service_name,
            operation_name=context.operation_name,
            tags=context.tags or {},
            metadata=enhanced_metadata
        )
    
    def _enhance_span_context(self, context: SpanContext) -> SpanContext:
        """Add infrastructure-level context enhancements."""
        # Add infrastructure metadata
        enhanced_metadata = context.metadata or {}
        enhanced_metadata.update({
            "abstraction_layer": "tracing_abstraction",
            "adapter_type": self.adapter_type,
            "span_timestamp": datetime.utcnow().isoformat()
        })
        
        # Create enhanced context
        return SpanContext(
            span_id=context.span_id or str(uuid.uuid4()),
            parent_span_id=context.parent_span_id,
            operation_name=context.operation_name,
            tags=context.tags or {},
            metadata=enhanced_metadata
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
                else:
                    self.logger.error(f"All {self.max_retries + 1} attempts failed")
        
        raise last_exception
