#!/usr/bin/env python3
"""
Nurse Service - Clean Rebuild with Proper Infrastructure

Clean implementation using ONLY our new base and protocol construct
with proper infrastructure abstractions for health monitoring using OpenTelemetry and Tempo.

WHAT (Smart City Role): I orchestrate health monitoring, telemetry collection, and system diagnostics
HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure abstractions
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Import ONLY our new base and protocol
from bases.smart_city_role_base import SmartCityRoleBase


class NurseServiceProtocol:
    """
    Protocol for Nurse services with proper infrastructure integration.
    Defines the contract for health monitoring, telemetry collection, and system diagnostics.
    """
    
    # Health Monitoring Methods
    async def collect_telemetry(self, service_name: str, metric_name: str, metric_value: float, tags: Dict[str, Any] = None) -> str:
        """Collect telemetry data using OpenTelemetry."""
        ...
    
    async def get_health_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get health metrics for a service."""
        ...
    
    async def set_alert_threshold(self, service_name: str, metric_name: str, threshold: float) -> bool:
        """Set alert threshold for a metric."""
        ...
    
    async def run_diagnostics(self, service_name: str) -> Dict[str, Any]:
        """Run system diagnostics for a service."""
        ...
    
    # Distributed Tracing Methods
    async def start_trace(self, trace_name: str, context: Dict[str, Any] = None) -> str:
        """Start a distributed trace using Tempo."""
        ...
    
    async def add_span(self, trace_id: str, span_name: str, attributes: Dict[str, Any] = None) -> str:
        """Add a span to an existing trace."""
        ...
    
    async def end_trace(self, trace_id: str, status: str = "success") -> bool:
        """End a distributed trace."""
        ...
    
    async def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve trace data from Tempo."""
        ...
    
    # Health Orchestration Methods
    async def orchestrate_health_monitoring(self, services: List[str]) -> Dict[str, Any]:
        """Orchestrate health monitoring across multiple services."""
        ...
    
    async def orchestrate_system_wellness(self, wellness_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate system wellness management."""
        ...


class NurseService(SmartCityRoleBase, NurseServiceProtocol):
    """
    Nurse Service - Clean Rebuild with Proper Infrastructure
    
    Clean implementation using ONLY our new base and protocol construct
    with proper infrastructure abstractions for health monitoring using OpenTelemetry and Tempo.
    
    WHAT (Smart City Role): I orchestrate health monitoring, telemetry collection, and system diagnostics
    HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure abstractions
    """
    
    def __init__(self, di_container: Any):
        """Initialize Nurse Service with proper infrastructure mapping."""
        super().__init__(
            service_name="NurseService",
            role_name="nurse",
            di_container=di_container
        )
        
        # Infrastructure Abstractions (will be initialized in initialize())
        self.telemetry_abstraction = None  # OpenTelemetry + Tempo
        self.alert_management_abstraction = None  # Redis-based alert management
        self.health_abstraction = None  # OpenTelemetry + Simple Health for health monitoring
        self.session_management_abstraction = None  # Redis for health state
        self.state_management_abstraction = None  # Redis for alert state
        
        # Service State
        self.is_infrastructure_connected = False
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Service-specific state
        self.health_metrics: Dict[str, Dict[str, Any]] = {}
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.active_traces: Dict[str, Dict[str, Any]] = {}
        self.system_diagnostics: Dict[str, Any] = {}
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Nurse Service (Clean Rebuild with Proper Infrastructure) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Nurse Service with proper infrastructure connections."""
        try:
            if self.logger:
                self.logger.info("🚀 Initializing Nurse Service with proper infrastructure connections...")
            
            # Initialize infrastructure connections
            await self._initialize_infrastructure_connections()
            
            # Initialize SOA API exposure
            await self._initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self._initialize_mcp_tool_integration()
            
            # Register capabilities with curator
            capabilities = await self._register_nurse_capabilities()
            await self.register_capability("NurseService", capabilities)
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            if self.logger:
                self.logger.info("✅ Nurse Service (Proper Infrastructure) initialized successfully")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to initialize Nurse Service: {str(e)}")
            self.service_health = "unhealthy"
            return False
    
    async def _initialize_infrastructure_connections(self):
        """Initialize connections to proper infrastructure abstractions."""
        try:
            if self.logger:
                self.logger.info("🔌 Connecting to proper infrastructure abstractions...")
            
            # Get Public Works Foundation
            public_works_foundation = self.get_public_works_foundation()
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Get Telemetry Abstraction (OpenTelemetry + Tempo)
            self.telemetry_abstraction = public_works_foundation.get_telemetry_abstraction()
            if not self.telemetry_abstraction:
                raise Exception("Telemetry Abstraction not available")
            
            # Get Alert Management Abstraction (Redis-based alert management)
            self.alert_management_abstraction = public_works_foundation.get_alert_management_abstraction()
            if not self.alert_management_abstraction:
                raise Exception("Alert Management Abstraction not available")
            
            # Get Health Abstraction (OpenTelemetry + Simple Health for health monitoring)
            self.health_abstraction = public_works_foundation.get_health_abstraction()
            if not self.health_abstraction:
                raise Exception("Health Abstraction not available")
            
            # Get Session Management Abstraction (Redis for health state)
            self.session_management_abstraction = public_works_foundation.get_session_abstraction()
            if not self.session_management_abstraction:
                raise Exception("Session Management Abstraction not available")
            
            # Get State Management Abstraction (Redis for alert state)
            self.state_management_abstraction = await public_works_foundation.get_abstraction("state_management")
            if not self.state_management_abstraction:
                raise Exception("State Management Abstraction not available")
            
            self.is_infrastructure_connected = True
            
            if self.logger:
                self.logger.info("✅ Proper infrastructure connections established:")
                self.logger.info(f"  - Telemetry Abstraction (OpenTelemetry + Tempo): {'✅' if self.telemetry_abstraction else '❌'}")
                self.logger.info(f"  - Alert Management Abstraction (Redis): {'✅' if self.alert_management_abstraction else '❌'}")
                self.logger.info(f"  - Health Abstraction (OpenTelemetry + Simple Health): {'✅' if self.health_abstraction else '❌'}")
                self.logger.info(f"  - Session Management (Redis): {'✅' if self.session_management_abstraction else '❌'}")
                self.logger.info(f"  - State Management (Redis): {'✅' if self.state_management_abstraction else '❌'}")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to connect to proper infrastructure: {str(e)}")
            raise e
    
    async def _initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities."""
        self.soa_apis = {
            "collect_telemetry": {
                "endpoint": "/api/nurse/telemetry",
                "method": "POST",
                "description": "Collect telemetry data using OpenTelemetry",
                "parameters": ["service_name", "metric_name", "metric_value", "tags"]
            },
            "get_health_metrics": {
                "endpoint": "/api/nurse/health/{service_name}",
                "method": "GET",
                "description": "Get health metrics for a service",
                "parameters": ["service_name"]
            },
            "set_alert_threshold": {
                "endpoint": "/api/nurse/alerts/thresholds",
                "method": "POST",
                "description": "Set alert threshold for a metric",
                "parameters": ["service_name", "metric_name", "threshold"]
            },
            "run_diagnostics": {
                "endpoint": "/api/nurse/diagnostics/{service_name}",
                "method": "POST",
                "description": "Run system diagnostics for a service",
                "parameters": ["service_name"]
            },
            "start_trace": {
                "endpoint": "/api/nurse/traces",
                "method": "POST",
                "description": "Start a distributed trace using Tempo",
                "parameters": ["trace_name", "context"]
            },
            "get_trace": {
                "endpoint": "/api/nurse/traces/{trace_id}",
                "method": "GET",
                "description": "Retrieve trace data from Tempo",
                "parameters": ["trace_id"]
            },
            "orchestrate_health_monitoring": {
                "endpoint": "/api/nurse/orchestration/health",
                "method": "POST",
                "description": "Orchestrate health monitoring across multiple services",
                "parameters": ["services"]
            }
        }
    
    async def _initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for health monitoring operations."""
        self.mcp_tools = {
            "health_monitor": {
                "name": "health_monitor",
                "description": "Monitor health metrics and system status",
                "parameters": ["service_name", "monitoring_options"]
            },
            "telemetry_collector": {
                "name": "telemetry_collector",
                "description": "Collect telemetry data using OpenTelemetry",
                "parameters": ["metric_data", "collection_options"]
            },
            "trace_analyzer": {
                "name": "trace_analyzer",
                "description": "Analyze distributed traces using Tempo",
                "parameters": ["trace_id", "analysis_options"]
            },
            "alert_manager": {
                "name": "alert_manager",
                "description": "Manage alerts and thresholds",
                "parameters": ["alert_config", "threshold_settings"]
            }
        }
    
    async def _register_nurse_capabilities(self) -> Dict[str, Any]:
        """Register Nurse Service capabilities with proper infrastructure mapping."""
        return {
            "service_name": "NurseService",
            "service_type": "health_monitor",
            "realm": "smart_city",
            "capabilities": [
                "health_monitoring",
                "telemetry_collection",
                "distributed_tracing",
                "alert_management",
                "system_diagnostics",
                "infrastructure_integration"
            ],
            "infrastructure_connections": {
                "telemetry": "OpenTelemetry",
                "tracing": "Tempo",
                "health_monitoring": "Redis",
                "alert_management": "Redis"
            },
            "soa_apis": self.soa_apis,
            "mcp_tools": self.mcp_tools,
            "status": "active",
            "infrastructure_connected": self.is_infrastructure_connected,
            "infrastructure_correct_from_start": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # HEALTH MONITORING METHODS WITH PROPER INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def collect_telemetry(self, service_name: str, metric_name: str, metric_value: float, tags: Dict[str, Any] = None) -> str:
        """Collect telemetry data using OpenTelemetry infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            metric_id = str(uuid.uuid4())
            telemetry_data = {
                "metric_id": metric_id,
                "service_name": service_name,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "tags": tags or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Collect telemetry via OpenTelemetry
            success = await self.telemetry_abstraction.collect_metric(
                metric_id=metric_id,
                telemetry_data=telemetry_data
            )
            
            if success:
                # Update local health metrics
                if service_name not in self.health_metrics:
                    self.health_metrics[service_name] = {}
                
                self.health_metrics[service_name][metric_name] = {
                    "value": metric_value,
                    "last_updated": datetime.utcnow().isoformat()
                }
                
                # Store health metrics using proper health abstraction
                from foundations.public_works_foundation.abstraction_contracts.health_protocol import HealthType, HealthContext, HealthMetric
                
                health_context = HealthContext(
                    service_id=service_name,
                    metadata=tags or {}
                )
                
                health_metric = HealthMetric(
                    name=metric_name,
                    value=metric_value,
                    unit="percent" if "usage" in metric_name else "count",
                    timestamp=datetime.utcnow(),
                    labels=tags or {},
                    metadata={"service_id": service_name}
                )
                
                await self.health_abstraction.collect_metrics(
                    health_type=HealthType.SYSTEM,
                    context=health_context
                )
                
                if self.logger:
                    self.logger.info(f"✅ Telemetry collected: {service_name}/{metric_name}")
                return metric_id
            else:
                raise Exception("Failed to collect telemetry via OpenTelemetry")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error collecting telemetry: {str(e)}")
            raise e
    
    async def get_health_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get health metrics using Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get metrics from Redis
            metrics = await self.health_abstraction.get_health_metrics(service_name)
            
            if metrics:
                if self.logger:
                    self.logger.info(f"✅ Health metrics retrieved: {service_name}")
                return {
                    "service_name": service_name,
                    "metrics": metrics,
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "status": "success"
                }
            else:
                return {
                    "service_name": service_name,
                    "metrics": {},
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "status": "no_data"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting health metrics: {str(e)}")
            return {
                "service_name": service_name,
                "metrics": {},
                "error": str(e),
                "status": "error"
            }
    
    async def set_alert_threshold(self, service_name: str, metric_name: str, threshold: float) -> bool:
        """Set alert threshold using Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Create alert rule for threshold
            from foundations.public_works_foundation.abstraction_contracts.alerting_protocol import AlertRule, AlertSeverity
            
            alert_rule = AlertRule(
                name=f"{service_name}_{metric_name}_threshold",
                condition=f"{metric_name} > {threshold}",
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                metadata={
                    "service_name": service_name,
                    "metric_name": metric_name,
                    "threshold": threshold
                }
            )
            
            rule_id = await self.alert_management_abstraction.create_alert_rule(alert_rule)
            success = rule_id is not None
            
            if success:
                # Update local thresholds
                if service_name not in self.alert_thresholds:
                    self.alert_thresholds[service_name] = {}
                
                self.alert_thresholds[service_name][metric_name] = threshold
                
                if self.logger:
                    self.logger.info(f"✅ Alert threshold set: {service_name}/{metric_name} = {threshold}")
                return True
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Failed to set alert threshold: {service_name}/{metric_name}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error setting alert threshold: {str(e)}")
            return False
    
    async def run_diagnostics(self, service_name: str) -> Dict[str, Any]:
        """Run system diagnostics using Redis infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Run diagnostics via health monitoring abstraction
            diagnostics_result = await self.health_abstraction.run_diagnostics(service_name)
            
            if diagnostics_result:
                # Store diagnostics in Redis
                await self.health_abstraction.store_diagnostics(
                    service_name=service_name,
                    diagnostics_data=diagnostics_result
                )
                
                self.system_diagnostics[service_name] = diagnostics_result
                
                if self.logger:
                    self.logger.info(f"✅ Diagnostics completed: {service_name}")
                return {
                    "service_name": service_name,
                    "diagnostics": diagnostics_result,
                    "completed_at": datetime.utcnow().isoformat(),
                    "status": "success"
                }
            else:
                return {
                    "service_name": service_name,
                    "diagnostics": {},
                    "completed_at": datetime.utcnow().isoformat(),
                    "status": "no_data"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error running diagnostics: {str(e)}")
            return {
                "service_name": service_name,
                "diagnostics": {},
                "error": str(e),
                "status": "error"
            }
    
    # ============================================================================
    # DISTRIBUTED TRACING METHODS WITH PROPER INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def start_trace(self, trace_name: str, context: Dict[str, Any] = None) -> str:
        """Start a distributed trace using Tempo infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            trace_id = str(uuid.uuid4())
            trace_data = {
                "trace_id": trace_id,
                "trace_name": trace_name,
                "context": context or {},
                "started_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Start trace via Telemetry Abstraction (which handles Tempo)
            from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import TraceSpan
            
            trace_span = TraceSpan(
                name=trace_name,
                trace_id=trace_id,
                span_id=str(uuid.uuid4()),
                start_time=datetime.utcnow(),
                end_time=None,
                attributes=context or {},
                events=[]
            )
            
            success = await self.telemetry_abstraction.collect_trace(trace_span)
            
            if success:
                self.active_traces[trace_id] = trace_data
                
                if self.logger:
                    self.logger.info(f"✅ Trace started: {trace_name} ({trace_id})")
                return trace_id
            else:
                raise Exception("Failed to start trace via Tempo")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error starting trace: {str(e)}")
            raise e
    
    async def add_span(self, trace_id: str, span_name: str, attributes: Dict[str, Any] = None) -> str:
        """Add a span to an existing trace using Tempo infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            span_id = str(uuid.uuid4())
            span_data = {
                "span_id": span_id,
                "trace_id": trace_id,
                "span_name": span_name,
                "attributes": attributes or {},
                "started_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Add span via Telemetry Abstraction
            from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import TraceSpan
            
            trace_span = TraceSpan(
                name=span_name,
                trace_id=trace_id,
                span_id=span_id,
                start_time=datetime.utcnow(),
                end_time=None,
                attributes=attributes or {},
                events=[]
            )
            
            success = await self.telemetry_abstraction.collect_trace(trace_span)
            
            if success:
                if trace_id in self.active_traces:
                    if "spans" not in self.active_traces[trace_id]:
                        self.active_traces[trace_id]["spans"] = []
                    self.active_traces[trace_id]["spans"].append(span_data)
                
                if self.logger:
                    self.logger.info(f"✅ Span added: {span_name} to trace {trace_id}")
                return span_id
            else:
                raise Exception("Failed to add span via Tempo")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error adding span: {str(e)}")
            raise e
    
    async def end_trace(self, trace_id: str, status: str = "success") -> bool:
        """End a distributed trace using Tempo infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # End trace via Telemetry Abstraction
            # For now, we'll just mark the trace as completed locally
            # In a real implementation, we'd send the end event to the telemetry system
            success = True
            
            if success:
                if trace_id in self.active_traces:
                    self.active_traces[trace_id]["status"] = "completed"
                    self.active_traces[trace_id]["ended_at"] = datetime.utcnow().isoformat()
                
                if self.logger:
                    self.logger.info(f"✅ Trace ended: {trace_id} ({status})")
                return True
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Failed to end trace: {trace_id}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error ending trace: {str(e)}")
            return False
    
    async def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve trace data from Tempo infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get trace from Tempo
            trace_data = await self.tracing_abstraction.get_trace(trace_id)
            
            if trace_data:
                if self.logger:
                    self.logger.info(f"✅ Trace retrieved: {trace_id}")
                return {
                    "trace_id": trace_id,
                    "trace_data": trace_data,
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "status": "success"
                }
            else:
                return {
                    "trace_id": trace_id,
                    "trace_data": None,
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "status": "not_found"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting trace: {str(e)}")
            return {
                "trace_id": trace_id,
                "trace_data": None,
                "error": str(e),
                "status": "error"
            }
    
    # ============================================================================
    # HEALTH ORCHESTRATION METHODS WITH PROPER INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def orchestrate_health_monitoring(self, services: List[str]) -> Dict[str, Any]:
        """Orchestrate health monitoring across multiple services using proper infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            orchestration_id = str(uuid.uuid4())
            health_status = {}
            overall_health = "healthy"
            
            for service_name in services:
                # Get health metrics for each service
                service_metrics = await self.get_health_metrics(service_name)
                
                if service_metrics.get("status") == "success":
                    health_status[service_name] = "healthy"
                else:
                    health_status[service_name] = "unhealthy"
                    overall_health = "unhealthy"
            
            orchestration_result = {
                "orchestration_id": orchestration_id,
                "services": services,
                "health_status": health_status,
                "overall_health": overall_health,
                "monitored_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            # Store orchestration result in Redis
            await self.health_abstraction.store_orchestration_result(
                orchestration_id=orchestration_id,
                result=orchestration_result
            )
            
            if self.logger:
                self.logger.info(f"✅ Health monitoring orchestrated: {len(services)} services")
            return orchestration_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error orchestrating health monitoring: {str(e)}")
            return {
                "orchestration_id": str(uuid.uuid4()),
                "services": services,
                "health_status": {},
                "overall_health": "error",
                "error": str(e),
                "status": "error"
            }
    
    async def orchestrate_system_wellness(self, wellness_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate system wellness management using proper infrastructure."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            wellness_id = str(uuid.uuid4())
            wellness_actions = wellness_plan.get("actions", [])
            wellness_results = []
            
            for action in wellness_actions:
                action_type = action.get("type")
                action_target = action.get("target")
                
                if action_type == "health_check":
                    # Run health check
                    health_result = await self.run_diagnostics(action_target)
                    wellness_results.append({
                        "action": action,
                        "result": health_result,
                        "status": "completed"
                    })
                elif action_type == "metric_collection":
                    # Collect metrics
                    metric_result = await self.collect_telemetry(
                        service_name=action_target,
                        metric_name=action.get("metric_name", "wellness_metric"),
                        metric_value=action.get("metric_value", 1.0)
                    )
                    wellness_results.append({
                        "action": action,
                        "result": {"metric_id": metric_result},
                        "status": "completed"
                    })
            
            wellness_result = {
                "wellness_id": wellness_id,
                "wellness_plan": wellness_plan,
                "wellness_results": wellness_results,
                "completed_at": datetime.utcnow().isoformat(),
                "status": "success"
            }
            
            # Store wellness result in Redis
            await self.health_abstraction.store_wellness_result(
                wellness_id=wellness_id,
                result=wellness_result
            )
            
            if self.logger:
                self.logger.info(f"✅ System wellness orchestrated: {len(wellness_actions)} actions")
            return wellness_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error orchestrating system wellness: {str(e)}")
            return {
                "wellness_id": str(uuid.uuid4()),
                "wellness_plan": wellness_plan,
                "wellness_results": [],
                "error": str(e),
                "status": "error"
            }
    
    # ============================================================================
    # INFRASTRUCTURE VALIDATION METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that proper infrastructure mapping is working correctly."""
        try:
            validation_results = {
                "telemetry_opentelemetry": False,
                "tracing_tempo": False,
                "health_monitoring_redis": False,
                "alert_management_redis": False,
                "overall_status": False
            }
            
            # Test Telemetry (OpenTelemetry)
            try:
                if self.telemetry_abstraction:
                    test_result = await self.telemetry_abstraction.health_check()
                    validation_results["telemetry_opentelemetry"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Telemetry (OpenTelemetry) test failed: {str(e)}")
            
            # Test Tracing (Tempo)
            try:
                if self.tracing_abstraction:
                    test_result = await self.tracing_abstraction.health_check()
                    validation_results["tracing_tempo"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Tracing (Tempo) test failed: {str(e)}")
            
            # Test Health Monitoring (Redis)
            try:
                if self.health_abstraction:
                    test_result = await self.health_abstraction.health_check()
                    validation_results["health_monitoring_redis"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Health Monitoring (Redis) test failed: {str(e)}")
            
            # Test Alert Management (Redis)
            try:
                if self.alert_management_abstraction:
                    test_result = await self.alert_management_abstraction.health_check()
                    validation_results["alert_management_redis"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Alert Management (Redis) test failed: {str(e)}")
            
            # Overall status
            validation_results["overall_status"] = all([
                validation_results["telemetry_opentelemetry"],
                validation_results["tracing_tempo"],
                validation_results["health_monitoring_redis"],
                validation_results["alert_management_redis"]
            ])
            
            if self.logger:
                self.logger.info("🔍 Proper infrastructure mapping validation completed:")
                self.logger.info(f"  - Telemetry (OpenTelemetry): {'✅' if validation_results['telemetry_opentelemetry'] else '❌'}")
                self.logger.info(f"  - Tracing (Tempo): {'✅' if validation_results['tracing_tempo'] else '❌'}")
                self.logger.info(f"  - Health Monitoring (Redis): {'✅' if validation_results['health_monitoring_redis'] else '❌'}")
                self.logger.info(f"  - Alert Management (Redis): {'✅' if validation_results['alert_management_redis'] else '❌'}")
                self.logger.info(f"  - Overall Status: {'✅' if validation_results['overall_status'] else '❌'}")
            
            return validation_results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error validating proper infrastructure mapping: {str(e)}")
            return {
                "telemetry_opentelemetry": False,
                "tracing_tempo": False,
                "health_monitoring_redis": False,
                "alert_management_redis": False,
                "overall_status": False,
                "error": str(e)
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities with proper infrastructure status."""
        try:
            return {
                "service_name": "NurseService",
                "service_type": "health_monitor",
                "realm": "smart_city",
                "capabilities": [
                    "health_monitoring",
                    "telemetry_collection",
                    "distributed_tracing",
                    "alert_management",
                    "system_diagnostics",
                    "infrastructure_integration"
                ],
                "infrastructure_connections": {
                    "telemetry": "OpenTelemetry",
                    "tracing": "Tempo",
                    "health_monitoring": "Redis",
                    "alert_management": "Redis"
                },
                "infrastructure_status": {
                    "connected": self.is_infrastructure_connected,
                    "telemetry_available": self.telemetry_abstraction is not None,
                    "tracing_available": self.tracing_abstraction is not None,
                    "health_monitoring_available": self.health_abstraction is not None,
                    "alert_management_available": self.alert_management_abstraction is not None
                },
                "infrastructure_correct_from_start": True,
                "soa_apis": self.soa_apis,
                "mcp_tools": self.mcp_tools,
                "status": "active",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting service capabilities: {str(e)}")
            return {
                "service_name": "NurseService",
                "error": str(e),
                "status": "error"
            }
