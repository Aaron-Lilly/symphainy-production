#!/usr/bin/env python3
"""
OpenTelemetry Infrastructure Adapter

Raw OpenTelemetry bindings for telemetry collection.
Thin wrapper around OpenTelemetry SDK with no business logic.
"""

import logging
from typing import Dict, Any, Optional

try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
except ImportError:
    trace = None
    metrics = None
    OTLPSpanExporter = None
    OTLPMetricExporter = None
    TracerProvider = None
    MeterProvider = None
    BatchSpanProcessor = None
    PeriodicExportingMetricReader = None


class OpenTelemetryAdapter:
    """Raw OpenTelemetry adapter - thin wrapper around OpenTelemetry SDK."""
    
    def __init__(self, service_name: str, endpoint: str = None, **kwargs):
        """
        Initialize OpenTelemetry adapter.
        
        Args:
            service_name: Service name for telemetry
            endpoint: OTLP endpoint URL
        """
        self.service_name = service_name
        self.endpoint = endpoint
        self.logger = logging.getLogger("OpenTelemetryAdapter")
        
        # OpenTelemetry components
        self.tracer = None
        self.meter = None
        self.tracer_provider = None
        self.meter_provider = None
        
        self._initialize_telemetry()
    
    def _initialize_telemetry(self):
        """Initialize OpenTelemetry components."""
        if trace is None:
            self.logger.warning("OpenTelemetry not installed")
            return
        
        try:
            # Initialize tracer
            self.tracer_provider = TracerProvider()
            trace.set_tracer_provider(self.tracer_provider)
            self.tracer = trace.get_tracer(self.service_name)
            
            # Initialize meter
            self.meter_provider = MeterProvider()
            metrics.set_meter_provider(self.meter_provider)
            self.meter = metrics.get_meter(self.service_name)
            
            self.logger.info("✅ OpenTelemetry adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenTelemetry: {e}")
    
    def create_span(self, name: str, attributes: Dict[str, Any] = None) -> Any:
        """Create a new span."""
        if self.tracer is None:
            return None
        
        return self.tracer.start_span(name, attributes=attributes)
    
    def create_counter(self, name: str, description: str = None) -> Any:
        """Create a counter metric."""
        if self.meter is None:
            return None
        
        return self.meter.create_counter(name, description=description)
    
    def create_histogram(self, name: str, description: str = None) -> Any:
        """Create a histogram metric."""
        if self.meter is None:
            return None
        
        return self.meter.create_histogram(name, description=description)
    
    def create_gauge(self, name: str, description: str = None) -> Any:
        """Create a gauge metric."""
        if self.meter is None:
            return None
        
        return self.meter.create_gauge(name, description=description)
    
    def add_span_event(self, span: Any, name: str, attributes: Dict[str, Any] = None):
        """Add event to span."""
        if span is None:
            return
        
        span.add_event(name, attributes=attributes)
    
    def set_span_attribute(self, span: Any, key: str, value: Any):
        """Set attribute on span."""
        if span is None:
            return
        
        span.set_attribute(key, value)
    
    def record_metric(self, metric: Any, value: float, attributes: Dict[str, Any] = None):
        """Record a metric value."""
        if metric is None:
            return
        
        metric.add(value, attributes=attributes)
    
    def get_tracer(self) -> Any:
        """Get the tracer instance."""
        return self.tracer
    
    def get_meter(self) -> Any:
        """Get the meter instance."""
        return self.meter



