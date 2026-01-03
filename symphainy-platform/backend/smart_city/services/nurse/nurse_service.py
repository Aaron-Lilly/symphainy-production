#!/usr/bin/env python3
"""
Nurse Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for telemetry (OpenTelemetry + Tempo) and health (OpenTelemetry + Simple Health).

WHAT (Smart City Role): I orchestrate health monitoring, telemetry collection, and system diagnostics
HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure abstractions
"""

from typing import Dict, Any, List, Optional

# Import base and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.nurse_service_protocol import NurseServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.telemetry_health import TelemetryHealth
from .modules.alert_management import AlertManagement
from .modules.diagnostics import Diagnostics
from .modules.tracing import Tracing
from .modules.orchestration import Orchestration
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities
from .modules.observability import Observability


class NurseService(SmartCityRoleBase, NurseServiceProtocol):
    """
    Nurse Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for telemetry (OpenTelemetry + Tempo) and health (OpenTelemetry + Simple Health).
    
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
        self.observability_abstraction = None  # NEW: ObservabilityAbstraction for platform data
        self.alert_management_abstraction = None  # Redis-based alert management
        self.health_abstraction = None  # OpenTelemetry + Simple Health for health monitoring
        self.session_management_abstraction = None  # Redis for health state
        self.state_management_abstraction = None  # Redis for alert state
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Service-specific state (backward compatibility)
        self.health_metrics: Dict[str, Dict[str, Any]] = {}
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        self.active_traces: Dict[str, Dict[str, Any]] = {}
        self.system_diagnostics: Dict[str, Any] = {}
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.telemetry_health_module = TelemetryHealth(self)
        self.alert_management_module = AlertManagement(self)
        self.diagnostics_module = Diagnostics(self)
        self.tracing_module = Tracing(self)
        self.orchestration_module = Orchestration(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        self.observability_module = Observability(self)  # NEW: Observability module
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Nurse Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize Nurse Service with proper infrastructure connections.
        
        NORMAL PATTERN: This method doesn't provide telemetry, so we can use utilities normally.
        """
        # Start telemetry tracking (Nurse can use telemetry utilities for non-telemetry operations)
        await self.log_operation_with_telemetry(
            "nurse_initialize_start",
            success=True
        )
        
        try:
            if self.logger:
                self.logger.info("🚀 Initializing Nurse Service with proper infrastructure connections...")
            
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register capabilities with curator (Phase 2 pattern - simplified for Smart City)
            await self.soa_mcp_module.register_capabilities()
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Record health metric
            await self.record_health_metric(
                "nurse_initialized",
                1.0,
                {"service": "NurseService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "nurse_initialize_complete",
                success=True
            )
            
            if self.logger:
                self.logger.info("✅ Nurse Service (Proper Infrastructure) initialized successfully")
            
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e,
                "nurse_initialize",
                {
                    "service": "NurseService",
                    "error_type": type(e).__name__
                }
            )
            
            self.service_health = "unhealthy"
            
            # Log failure
            await self.log_operation_with_telemetry(
                "nurse_initialize_complete",
                success=False,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            
            # Record health metric
            await self.record_health_metric(
                "nurse_initialized",
                0.0,
                metadata={"error_type": type(e).__name__}
            )
            
            if self.logger:
                self.logger.error(f"❌ Failed to initialize Nurse Service: {str(e)}")
            
            return False
    
    # ============================================================================
    # HEALTH MONITORING METHODS
    # ============================================================================
    
    async def collect_telemetry(self, service_name: str, metric_name: str, metric_value: float, tags: Optional[Dict[str, Any]] = None) -> str:
        """Collect telemetry data using OpenTelemetry infrastructure."""
        return await self.telemetry_health_module.collect_telemetry(service_name, metric_name, metric_value, tags)
    
    async def get_health_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get health metrics using Health Abstraction (OpenTelemetry + Simple Health)."""
        return await self.telemetry_health_module.get_health_metrics(service_name)
    
    async def set_alert_threshold(self, service_name: str, metric_name: str, threshold: float) -> bool:
        """Set alert threshold using Alert Management Abstraction (Redis)."""
        return await self.alert_management_module.set_alert_threshold(service_name, metric_name, threshold)
    
    async def run_diagnostics(self, service_name: str) -> Dict[str, Any]:
        """Run system diagnostics using Health Abstraction."""
        return await self.diagnostics_module.run_diagnostics(service_name)
    
    # ============================================================================
    # DISTRIBUTED TRACING METHODS
    # ============================================================================
    
    async def start_trace(self, trace_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Start a distributed trace using Tempo infrastructure."""
        return await self.tracing_module.start_trace(trace_name, context)
    
    async def add_span(self, trace_id: str, span_name: str, attributes: Optional[Dict[str, Any]] = None) -> str:
        """Add a span to an existing trace using Tempo infrastructure."""
        return await self.tracing_module.add_span(trace_id, span_name, attributes)
    
    async def end_trace(self, trace_id: str, status: str = "success") -> bool:
        """End a distributed trace using Tempo infrastructure."""
        return await self.tracing_module.end_trace(trace_id, status)
    
    async def get_trace(self, trace_id: str) -> Dict[str, Any]:
        """Retrieve trace data from Tempo infrastructure."""
        return await self.tracing_module.get_trace(trace_id)
    
    # ============================================================================
    # OBSERVABILITY METHODS (Phase 2.2)
    # ============================================================================
    
    async def record_platform_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        trace_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record platform event (log, metric, or trace) via ObservabilityAbstraction.
        
        SOA API: Exposes observability capabilities to realm services.
        
        Args:
            event_type: Type of event ("log", "metric", "trace")
            event_data: Event data dictionary
            trace_id: Optional trace ID for correlation
            user_context: Optional user context
        
        Returns:
            Dict with result (success, event_id, etc.)
        """
        return await self.observability_module.record_platform_event(
            event_type, event_data, trace_id, user_context
        )
    
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
        Record agent execution for observability via ObservabilityAbstraction.
        
        SOA API: Exposes agent tracking capabilities to Agentic Foundation.
        
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
        return await self.observability_module.record_agent_execution(
            agent_id, agent_name, prompt_hash, response, trace_id, execution_metadata, user_context
        )
    
    async def get_observability_data(
        self,
        data_type: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query observability data via ObservabilityAbstraction.
        
        SOA API: Exposes observability query capabilities to realm services.
        
        Args:
            data_type: Type of data to query ("logs", "metrics", "traces", "agent_executions")
            filters: Optional filters (service_name, trace_id, agent_id, etc.)
            limit: Maximum number of results
            user_context: Optional user context
        
        Returns:
            List of observability data records
        """
        return await self.observability_module.get_observability_data(
            data_type, filters, limit, user_context
        )
    
    # ============================================================================
    # HEALTH ORCHESTRATION METHODS
    # ============================================================================
    
    async def orchestrate_health_monitoring(self, services_or_request) -> Dict[str, Any]:
        """Orchestrate health monitoring across multiple services."""
        # Handle both protocol (request dict) and direct (services list) calls
        if isinstance(services_or_request, dict):
            services = services_or_request.get("services", [])
        else:
            # If called directly with List[str], use it directly
            services = services_or_request if isinstance(services_or_request, list) else []
        return await self.orchestration_module.orchestrate_health_monitoring(services)
    
    async def orchestrate_system_wellness(self, wellness_plan_or_request) -> Dict[str, Any]:
        """Orchestrate system wellness management."""
        # Handle both protocol (request dict) and direct (wellness_plan dict) calls
        if isinstance(wellness_plan_or_request, dict) and "wellness_plan" in wellness_plan_or_request:
            wellness_plan = wellness_plan_or_request.get("wellness_plan", {})
        else:
            # If called directly with wellness_plan dict, use it directly
            wellness_plan = wellness_plan_or_request if isinstance(wellness_plan_or_request, dict) else {}
        return await self.orchestration_module.orchestrate_system_wellness(wellness_plan)
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure mapping."""
        return await self.utilities_module.validate_infrastructure_mapping()
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and configuration."""
        return await self.utilities_module.get_service_capabilities()
    
    # ============================================================================
    # PROTOCOL COMPLIANCE METHODS (from NurseServiceProtocol)
    # ============================================================================
    
    async def monitor_service_health(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor health of specific service."""
        service_name = request.get("service_name")
        return await self.get_health_metrics(service_name)
    
    async def perform_system_diagnostics(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive system diagnostics."""
        service_name = request.get("service_name")
        return await self.run_diagnostics(service_name)
    
    async def generate_health_report(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate health monitoring report."""
        services = request.get("services", [])
        return await self.orchestrate_health_monitoring(services)
    
    # ============================================================================
    # LOG AGGREGATION METHODS
    # ============================================================================
    
    async def monitor_log_aggregation(self, **kwargs) -> Dict[str, Any]:
        """Monitor log aggregation health and metrics."""
        return await self.telemetry_health_module.monitor_log_aggregation()
    
    async def query_logs(self, query: str, limit: int = 100, start: str = None, end: str = None, **kwargs) -> Dict[str, Any]:
        """Query logs from aggregation backend using LogQL."""
        from datetime import datetime
        from foundations.public_works_foundation.abstraction_contracts.log_aggregation_protocol import LogQuery
        
        # Get log aggregation abstraction
        platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
        if not platform_gateway:
            return {"status": "error", "error": "Platform Gateway not available"}
        
        log_abstraction = platform_gateway.get_abstraction("log_aggregation")
        if not log_abstraction:
            return {"status": "error", "error": "Log aggregation abstraction not available"}
        
        # Parse timestamps
        start_dt = None
        end_dt = None
        if start:
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            except:
                pass
        if end:
            try:
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            except:
                pass
        
        # Create query
        log_query = LogQuery(
            query=query,
            limit=limit,
            start=start_dt,
            end=end_dt
        )
        
        # Execute query
        log_entries = await log_abstraction.query_logs(log_query)
        
        return {
            "status": "success",
            "query": query,
            "count": len(log_entries),
            "logs": [
                {
                    "line": entry.line,
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "service_name": entry.service_name,
                    "labels": entry.labels
                }
                for entry in log_entries
            ]
        }
    
    async def search_logs(self, filters: Dict[str, Any] = None, time_range: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Search logs with filters."""
        # Get log aggregation abstraction
        platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
        if not platform_gateway:
            return {"status": "error", "error": "Platform Gateway not available"}
        
        log_abstraction = platform_gateway.get_abstraction("log_aggregation")
        if not log_abstraction:
            return {"status": "error", "error": "Log aggregation abstraction not available"}
        
        # Execute search
        search_params = {
            "filters": filters or {},
            "time_range": time_range or {}
        }
        
        result = await log_abstraction.search_logs(search_params)
        return result
    
    async def get_log_metrics(self, time_range: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Get log volume and aggregation metrics."""
        # Get log aggregation abstraction
        platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
        if not platform_gateway:
            return {"status": "error", "error": "Platform Gateway not available"}
        
        log_abstraction = platform_gateway.get_abstraction("log_aggregation")
        if not log_abstraction:
            return {"status": "error", "error": "Log aggregation abstraction not available"}
        
        # Execute metrics query
        metrics = await log_abstraction.get_log_metrics(time_range or {})
        return metrics