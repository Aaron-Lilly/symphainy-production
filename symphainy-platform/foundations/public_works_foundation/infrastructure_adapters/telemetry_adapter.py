#!/usr/bin/env python3
"""
Telemetry Infrastructure Adapter

Raw OpenTelemetry bindings for telemetry collection and metrics.
Thin wrapper around OpenTelemetry SDK with no business logic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    from opentelemetry.metrics import Counter, Histogram, Gauge
except ImportError:
    trace = None
    metrics = None
    OTLPSpanExporter = None
    OTLPMetricExporter = None
    TracerProvider = None
    BatchSpanProcessor = None
    MeterProvider = None
    PeriodicExportingMetricReader = None
    Resource = None
    Status = None
    StatusCode = None
    Counter = None
    Histogram = None
    Gauge = None


class TelemetryAdapter:
    """Raw telemetry adapter for OpenTelemetry integration."""
    
    def __init__(self, service_name: str, service_version: str = "1.0.0", 
                 endpoint: str = None, **kwargs):
        """
        Initialize telemetry adapter.
        
        Args:
            service_name: Name of the service
            service_version: Version of the service
            endpoint: OTLP endpoint URL
        """
        self.service_name = service_name
        self.service_version = service_version
        self.endpoint = endpoint
        self.logger = logging.getLogger("TelemetryAdapter")
        
        # OpenTelemetry components
        self.tracer = None
        self.meter = None
        self.tracer_provider = None
        self.meter_provider = None
        
        # Metrics
        self.counters = {}
        self.histograms = {}
        self.gauges = {}
        
        # Initialize OpenTelemetry
        self._initialize_telemetry()
    
    def _initialize_telemetry(self):
        """Initialize OpenTelemetry components."""
        if not all([trace, metrics, TracerProvider, MeterProvider]):
            self.logger.warning("OpenTelemetry not installed, telemetry will be disabled")
            return
        
        try:
            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": self.service_version
            })
            
            # Initialize tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)
            
            # Initialize meter provider
            self.meter_provider = MeterProvider(resource=resource)
            metrics.set_meter_provider(self.meter_provider)
            
            # Get tracer and meter
            self.tracer = trace.get_tracer(self.service_name, self.service_version)
            self.meter = metrics.get_meter(self.service_name, self.service_version)
            
            # Add exporters if endpoint provided
            if self.endpoint:
                self._add_exporters()
            
            self.logger.info("✅ Telemetry adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize telemetry: {e}")
    
    def _add_exporters(self):
        """Add OTLP exporters."""
        try:
            if self.endpoint and OTLPSpanExporter and OTLPMetricExporter:
                # Add span exporter
                span_exporter = OTLPSpanExporter(endpoint=self.endpoint)
                span_processor = BatchSpanProcessor(span_exporter)
                self.tracer_provider.add_span_processor(span_processor)
                
                # Add metric exporter
                metric_exporter = OTLPMetricExporter(endpoint=self.endpoint)
                metric_reader = PeriodicExportingMetricReader(metric_exporter)
                self.meter_provider.add_metric_reader(metric_reader)
                
                self.logger.info("✅ OTLP exporters added")
                
        except Exception as e:
            self.logger.error(f"Failed to add exporters: {e}")
    
    def create_span(self, name: str, attributes: Dict[str, Any] = None) -> Any:
        """
        Create a new span.
        
        Args:
            name: Span name
            attributes: Span attributes
            
        Returns:
            Span object
        """
        if not self.tracer:
            return None
        
        try:
            span = self.tracer.start_span(name)
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            return span
            
        except Exception as e:
            self.logger.error(f"Failed to create span {name}: {e}")
            return None
    
    def end_span(self, span: Any, status: str = "OK", attributes: Dict[str, Any] = None):
        """
        End a span.
        
        Args:
            span: Span object
            status: Span status
            attributes: Additional attributes
        """
        if not span:
            return
        
        try:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            if status == "OK":
                span.set_status(StatusCode.OK)
            else:
                span.set_status(StatusCode.ERROR, status)
            
            span.end()
            
        except Exception as e:
            self.logger.error(f"Failed to end span: {e}")
    
    def create_counter(self, name: str, description: str = None) -> Any:
        """
        Create a counter metric.
        
        Args:
            name: Counter name
            description: Counter description
            
        Returns:
            Counter object
        """
        if not self.meter:
            return None
        
        try:
            counter = self.meter.create_counter(
                name=name,
                description=description
            )
            self.counters[name] = counter
            return counter
            
        except Exception as e:
            self.logger.error(f"Failed to create counter {name}: {e}")
            return None
    
    def create_histogram(self, name: str, description: str = None) -> Any:
        """
        Create a histogram metric.
        
        Args:
            name: Histogram name
            description: Histogram description
            
        Returns:
            Histogram object
        """
        if not self.meter:
            return None
        
        try:
            histogram = self.meter.create_histogram(
                name=name,
                description=description
            )
            self.histograms[name] = histogram
            return histogram
            
        except Exception as e:
            self.logger.error(f"Failed to create histogram {name}: {e}")
            return None
    
    def create_gauge(self, name: str, description: str = None) -> Any:
        """
        Create a gauge metric.
        
        Args:
            name: Gauge name
            description: Gauge description
            
        Returns:
            Gauge object
        """
        if not self.meter:
            return None
        
        try:
            gauge = self.meter.create_gauge(
                name=name,
                description=description
            )
            self.gauges[name] = gauge
            return gauge
            
        except Exception as e:
            self.logger.error(f"Failed to create gauge {name}: {e}")
            return None
    
    def record_counter(self, name: str, value: float, attributes: Dict[str, Any] = None):
        """
        Record a counter value.
        
        Args:
            name: Counter name
            value: Value to record
            attributes: Metric attributes
        """
        try:
            counter = self.counters.get(name)
            if counter:
                counter.add(value, attributes or {})
            else:
                self.logger.warning(f"Counter {name} not found")
                
        except Exception as e:
            self.logger.error(f"Failed to record counter {name}: {e}")
    
    def record_histogram(self, name: str, value: float, attributes: Dict[str, Any] = None):
        """
        Record a histogram value.
        
        Args:
            name: Histogram name
            value: Value to record
            attributes: Metric attributes
        """
        try:
            histogram = self.histograms.get(name)
            if histogram:
                histogram.record(value, attributes or {})
            else:
                self.logger.warning(f"Histogram {name} not found")
                
        except Exception as e:
            self.logger.error(f"Failed to record histogram {name}: {e}")
    
    def record_gauge(self, name: str, value: float, attributes: Dict[str, Any] = None):
        """
        Record a gauge value.
        
        Args:
            name: Gauge name
            value: Value to record
            attributes: Metric attributes
        """
        try:
            gauge = self.gauges.get(name)
            if gauge:
                gauge.set(value, attributes or {})
            else:
                self.logger.warning(f"Gauge {name} not found")
                
        except Exception as e:
            self.logger.error(f"Failed to record gauge {name}: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Dict: Current metrics
        """
        try:
            return {
                "counters": list(self.counters.keys()),
                "histograms": list(self.histograms.keys()),
                "gauges": list(self.gauges.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}
    
    def shutdown(self):
        """Shutdown telemetry components."""
        try:
            if self.tracer_provider:
                self.tracer_provider.shutdown()
            if self.meter_provider:
                self.meter_provider.shutdown()
            
            self.logger.info("✅ Telemetry adapter shutdown")
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown telemetry: {e}")



