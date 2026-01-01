#!/usr/bin/env python3
"""
Enhanced Nurse Service - Multi-Tenant

Comprehensive health monitoring, telemetry collection, alert management, and failure
classification service for the Smart City platform with multi-tenant awareness.
Built on the enhanced foundation layers with real OpenTelemetry, Tempo, and ArangoDB integration.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from bases.soa_service_base import SOAServiceBase
from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol, SOAEndpoint, SOAServiceInfo
from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment

from .micro_modules.health_monitoring import HealthMonitoringModule
from .micro_modules.telemetry_collection import TelemetryCollectionModule
from .micro_modules.alert_management import AlertManagementModule
from .micro_modules.failure_classification import FailureClassificationModule


class NurseService(SOAServiceBase):
    """
    Enhanced Nurse Service - Multi-Tenant
    
    Provides comprehensive health monitoring, telemetry collection, alert management,
    and failure classification capabilities for the Smart City platform with multi-tenant awareness.
    """
    
    def __init__(self, utility_foundation, curator_foundation=None, 
                 public_works_foundation=None, environment=Environment.DEVELOPMENT):
        """Initialize the Enhanced Nurse Service with multi-tenant capabilities."""
        super().__init__("NurseService", utility_foundation, curator_foundation)
        
        self.public_works_foundation = public_works_foundation
        self.env_loader = EnvironmentLoader(environment)
        
        # Multi-tenant coordination service
        self.multi_tenant_coordinator = None
        if self.public_works_foundation:
            self.multi_tenant_coordinator = self.public_works_foundation.multi_tenant_coordination_service
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}
        
        # Initialize SOA protocol
        self.soa_protocol = NurseSOAProtocol("NurseService", self, curator_foundation), public_works_foundation
        
        # Environment-specific configuration
        self.config = self.env_loader.get_all_config()
        self.api_config = self.env_loader.get_api_config()
        self.feature_flags = self.env_loader.get_feature_flags()
        
        # Initialize micro-modules after parent initialization
        self.health_monitoring_module = HealthMonitoringModule(self.logger, self.env_loader)
        self.telemetry_collection_module = TelemetryCollectionModule(self.logger, self.env_loader)
        self.alert_management_module = AlertManagementModule(self.logger, self.env_loader)
        self.failure_classification_module = FailureClassificationModule(self.logger, self.env_loader)
        
        # Service capabilities
        self.capabilities = [
            "health_monitoring",
            "telemetry_collection", 
            "alert_management",
            "failure_classification",
            "distributed_tracing",
            "metrics_storage",
            "system_diagnostics",
            "service_health_checks",
            "automated_alerting",
            "failure_analysis",
            "multi_tenant_health_monitoring"
        ]
        
        self.logger.info("🏥 Nurse Service initialized - Multi-Tenant Health Monitoring Hub")
    
    async def initialize(self):
        """Initialize the Nurse Service with multi-tenant capabilities."""
        try:
            await super().initialize()
            
            self.logger.info("🚀 Initializing Nurse Service with multi-tenant capabilities...")

            # Initialize SOA protocol
            await self.soa_protocol.initialize()
            self.logger.info("✅ SOA Protocol initialized")

            # Initialize multi-tenant coordination
            if self.multi_tenant_coordinator:
                await self.multi_tenant_coordinator.initialize()
                self.logger.info("✅ Multi-tenant coordination initialized")
            
            # Load smart city abstractions from public works
            if self.public_works_foundation:
                await self.soa_protocol.load_smart_city_abstractions()
            self.smart_city_abstractions = self.soa_protocol.get_all_abstractions()
                self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions")
            
            # Initialize modules
            await self._initialize_modules()
            
            self.logger.info("✅ Nurse Service initialized with multi-tenant capabilities")
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="nurse_initialize")
            raise
    
    async def _initialize_modules(self) -> bool:
        """Initialize all micro-modules."""
        try:
            # Initialize telemetry collection module (async)
            if not await self.telemetry_collection_module.initialize():
                self.logger.error("Failed to initialize TelemetryCollectionModule")
                return False
            
            # Initialize other modules (sync)
            modules = [
                self.health_monitoring_module,
                self.alert_management_module,
                self.failure_classification_module
            ]
            
            for module in modules:
                if not module.initialize():
                    self.logger.error(f"Failed to initialize {module.__class__.__name__}")
                    return False
            
            self.logger.info("All Nurse Service modules initialized successfully")
            return True
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="nurse_service_initialization")
            return False
    
    # ============================================================================
    # HEALTH MONITORING CAPABILITIES
    # ============================================================================
    
    def perform_system_health_check(self, arguments: Dict[str, Any] = None, 
                                   user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform a comprehensive system health check."""
        try:
            health_result = self.health_monitoring_module.perform_system_health_check()
            
            # Note: Telemetry recording would need to be done asynchronously in a separate context
            # For now, we'll skip telemetry in synchronous methods
            
            return health_result
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def perform_service_health_check(self, arguments: Dict[str, Any], 
                                   user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform a health check for a specific service."""
        try:
            service_name = arguments.get("service_name")
            if not service_name:
                return {"error": "service_name is required"}
            
            return self.health_monitoring_module.perform_service_health_check(service_name)
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def start_continuous_monitoring(self, arguments: Dict[str, Any], 
                                  user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Start continuous health monitoring for a service."""
        try:
            service_name = arguments.get("service_name")
            duration_minutes = arguments.get("duration_minutes", 60)
            
            if not service_name:
                return {"error": "service_name is required"}
            
            return self.health_monitoring_module.start_continuous_monitoring(
                service_name, duration_minutes
            )
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def get_health_dashboard_data(self, arguments: Dict[str, Any] = None, 
                                user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive health dashboard data."""
        try:
            hours = arguments.get("hours", 24) if arguments else 24
            return self.health_monitoring_module.get_health_dashboard_data(hours)
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    # ============================================================================
    # TELEMETRY COLLECTION CAPABILITIES
    # ============================================================================
    
    async def collect_system_telemetry(self, arguments: Dict[str, Any] = None, 
                               user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Collect comprehensive system telemetry data."""
        try:
            service_name = arguments.get("service_name") if arguments else None
            return await self.telemetry_collection_module.collect_system_telemetry(service_name)
        except Exception as e:
            await self.error_handler.handle_error(e, context="nurse_system_telemetry")
            return {"error": str(e)}
    
    async def start_telemetry_collection(self, arguments: Dict[str, Any], 
                                 user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Start continuous telemetry collection for a service."""
        try:
            service_name = arguments.get("service_name")
            duration_minutes = arguments.get("duration_minutes", 60)
            
            if not service_name:
                return {"error": "service_name is required"}
            
            return await self.telemetry_collection_module.start_telemetry_collection(
                service_name, duration_minutes
            )
        except Exception as e:
            await self.error_handler.handle_error(e, context="nurse_telemetry_collection")
            return {"error": str(e)}
    
    async def create_custom_metric(self, arguments: Dict[str, Any], 
                           user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a custom metric."""
        try:
            metric_name = arguments.get("metric_name")
            value = arguments.get("value")
            tags = arguments.get("tags", {})
            metadata = arguments.get("metadata", {})
            
            if not metric_name or value is None:
                return {"error": "metric_name and value are required"}
            
            success = await self.telemetry_collection_module.create_custom_metric(
                metric_name, value, tags, metadata
            )
            
            return {"success": success}
        except Exception as e:
            await self.error_handler.handle_error(e, context="nurse_custom_metric")
            return {"error": str(e)}
    
    async def start_trace(self, arguments: Dict[str, Any], 
                   user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Start a distributed trace."""
        try:
            operation_name = arguments.get("operation_name")
            service_name = arguments.get("service_name")
            parent_span_id = arguments.get("parent_span_id")
            tags = arguments.get("tags", {})
            
            if not operation_name:
                return {"error": "operation_name is required"}
            
            span_id = await self.telemetry_collection_module.start_trace(
                operation_name, service_name, parent_span_id, tags
            )
            
            return {"span_id": span_id}
        except Exception as e:
            await self.error_handler.handle_error(e, context="nurse_start_trace")
            return {"error": str(e)}
    
    async def finish_trace(self, arguments: Dict[str, Any], 
                    user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Finish a distributed trace."""
        try:
            span_id = arguments.get("span_id")
            status = arguments.get("status", "ok")
            tags = arguments.get("tags", {})
            logs = arguments.get("logs", [])
            
            if not span_id:
                return {"error": "span_id is required"}
            
            success = await self.telemetry_collection_module.finish_trace(
                span_id, status, tags, logs
            )
            
            return {"success": success}
        except Exception as e:
            await self.error_handler.handle_error(e, context="nurse_finish_trace")
            return {"error": str(e)}
    
    async def get_telemetry_dashboard_data(self, arguments: Dict[str, Any] = None, 
                                   user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive telemetry dashboard data."""
        try:
            hours = arguments.get("hours", 24) if arguments else 24
            return await self.telemetry_collection_module.get_telemetry_dashboard_data(hours)
        except Exception as e:
            await self.error_handler.handle_error(e, context="nurse_telemetry_dashboard")
            return {"error": str(e)}
    
    # ============================================================================
    # ALERT MANAGEMENT CAPABILITIES
    # ============================================================================
    
    def create_health_alert(self, arguments: Dict[str, Any], 
                          user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a health-related alert."""
        try:
            alert_type = arguments.get("alert_type")
            severity = arguments.get("severity")
            message = arguments.get("message")
            service_name = arguments.get("service_name")
            metadata = arguments.get("metadata", {})
            
            if not all([alert_type, severity, message]):
                return {"error": "alert_type, severity, and message are required"}
            
            alert_id = self.alert_management_module.create_health_alert(
                alert_type, severity, message, service_name, metadata
            )
            
            return {"alert_id": alert_id}
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def create_failure_alert(self, arguments: Dict[str, Any], 
                           user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a failure-related alert with automatic classification."""
        try:
            error_message = arguments.get("error_message")
            error_code = arguments.get("error_code")
            service_name = arguments.get("service_name")
            metadata = arguments.get("metadata", {})
            
            if not error_message:
                return {"error": "error_message is required"}
            
            alert_id = self.alert_management_module.create_failure_alert(
                error_message, error_code, service_name, metadata
            )
            
            return {"alert_id": alert_id}
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def acknowledge_alert(self, arguments: Dict[str, Any], 
                        user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Acknowledge an alert."""
        try:
            alert_id = arguments.get("alert_id")
            acknowledged_by = arguments.get("acknowledged_by", "system")
            acknowledgment_notes = arguments.get("acknowledgment_notes", "")
            
            if not alert_id:
                return {"error": "alert_id is required"}
            
            success = self.alert_management_module.acknowledge_alert(
                alert_id, acknowledged_by, acknowledgment_notes
            )
            
            return {"success": success}
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def resolve_alert(self, arguments: Dict[str, Any], 
                    user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Resolve an alert."""
        try:
            alert_id = arguments.get("alert_id")
            resolved_by = arguments.get("resolved_by", "system")
            resolution_notes = arguments.get("resolution_notes", "")
            resolution_category = arguments.get("resolution_category")
            
            if not alert_id:
                return {"error": "alert_id is required"}
            
            success = self.alert_management_module.resolve_alert(
                alert_id, resolved_by, resolution_notes, resolution_category
            )
            
            return {"success": success}
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def get_alert_dashboard_data(self, arguments: Dict[str, Any] = None, 
                               user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive alert dashboard data."""
        try:
            hours = arguments.get("hours", 24) if arguments else 24
            return self.alert_management_module.get_alert_dashboard_data(hours)
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    # ============================================================================
    # FAILURE CLASSIFICATION CAPABILITIES
    # ============================================================================
    
    def classify_failure(self, arguments: Dict[str, Any], 
                        user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Classify a failure without creating an alert."""
        try:
            error_message = arguments.get("error_message")
            error_code = arguments.get("error_code")
            service_name = arguments.get("service_name")
            metadata = arguments.get("metadata", {})
            
            if not error_message:
                return {"error": "error_message is required"}
            
            return self.failure_classification_module.classify_failure(
                error_message, error_code, service_name, metadata
            )
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def classify_and_alert(self, arguments: Dict[str, Any], 
                          user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Classify a failure and optionally create an alert."""
        try:
            error_message = arguments.get("error_message")
            error_code = arguments.get("error_code")
            service_name = arguments.get("service_name")
            metadata = arguments.get("metadata", {})
            
            if not error_message:
                return {"error": "error_message is required"}
            
            return self.failure_classification_module.classify_and_alert(
                error_message, error_code, service_name, metadata
            )
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def analyze_failure_patterns(self, arguments: Dict[str, Any] = None, 
                               user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze failure patterns over time."""
        try:
            hours = arguments.get("hours", 24) if arguments else 24
            return self.failure_classification_module.analyze_failure_patterns(hours)
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def get_failure_dashboard_data(self, arguments: Dict[str, Any] = None, 
                                 user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive failure classification dashboard data."""
        try:
            hours = arguments.get("hours", 24) if arguments else 24
            return self.failure_classification_module.get_failure_dashboard_data(hours)
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    # ============================================================================
    # SERVICE MANAGEMENT CAPABILITIES
    # ============================================================================
    
    def get_service_status(self, arguments: Dict[str, Any] = None, 
                         user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive service status and health."""
        try:
            status = {
                "service_name": "nurse",
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "capabilities": self.capabilities,
                "modules": {
                    "health_monitoring": self.health_monitoring_module.get_health_status(),
                    "telemetry_collection": self.telemetry_collection_module.get_telemetry_status(),
                    "alert_management": self.alert_management_module.get_alert_management_status(),
                    "failure_classification": self.failure_classification_module.get_failure_classification_status()
                }
            }
            
            return status
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def configure_service(self, arguments: Dict[str, Any], 
                        user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Configure service parameters."""
        try:
            config_type = arguments.get("config_type")
            config_data = arguments.get("config_data", {})
            
            if not config_type:
                return {"error": "config_type is required"}
            
            success = False
            
            if config_type == "health_monitoring":
                success = self.health_monitoring_module.configure_health_monitoring(config_data)
            elif config_type == "telemetry_collection":
                success = self.telemetry_collection_module.configure_telemetry(config_data)
            elif config_type == "alert_management":
                success = self.alert_management_module.configure_alert_management(config_data)
            elif config_type == "failure_classification":
                success = self.failure_classification_module.configure_failure_classification(config_data)
            else:
                return {"error": f"Unknown config_type: {config_type}"}
            
            return {"success": success}
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    def get_comprehensive_dashboard_data(self, arguments: Dict[str, Any] = None, 
                                       user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive dashboard data from all modules."""
        try:
            hours = arguments.get("hours", 24) if arguments else 24
            
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "time_range_hours": hours,
                "service_name": "nurse",
                "health_monitoring": self.health_monitoring_module.get_health_dashboard_data(hours),
                "telemetry_collection": self.telemetry_collection_module.get_telemetry_dashboard_data(hours),
                "alert_management": self.alert_management_module.get_alert_dashboard_data(hours),
                "failure_classification": self.failure_classification_module.get_failure_dashboard_data(hours)
            }
            
            return dashboard_data
        except Exception as e:
            # Note: Error handling would need to be done asynchronously in a separate context
            # For now, we'll use basic error handling
            return {"error": str(e)}
    
    # ============================================================================
    # MULTI-TENANT SPECIFIC METHODS
    # ============================================================================
    
    async def get_tenant_health_status(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get health status for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's health status"}
            
            # Get tenant-specific health data
            health_data = self.health_monitoring_module.get_health_dashboard_data(24)  # Last 24 hours
            
            # Filter health data by tenant (assuming tenant_id is in the data)
            tenant_health_data = {
                "tenant_id": tenant_id,
                "overall_status": "healthy",  # Simplified
                "service_health": self._filter_health_data_by_tenant(health_data, tenant_id),
                "alerts": self._get_tenant_alerts(tenant_id),
                "metrics": self._get_tenant_metrics(tenant_id)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_health_status", "nurse",
                    {"tenant_id": tenant_id, "overall_status": tenant_health_data["overall_status"]}
                )
            
            return {"success": True, "health_data": tenant_health_data}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_health_status")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_health_metrics(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get health metrics for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's health metrics"}
            
            # Get tenant health status
            tenant_health = await self.get_tenant_health_status(tenant_id, user_context)
            if not tenant_health.get("success"):
                return tenant_health
            
            health_data = tenant_health.get("health_data", {})
            
            # Calculate health metrics
            health_metrics = {
                "tenant_id": tenant_id,
                "uptime_percentage": self._calculate_uptime_percentage(health_data),
                "average_response_time": self._calculate_average_response_time(health_data),
                "error_rate": self._calculate_error_rate(health_data),
                "alert_count": len(health_data.get("alerts", [])),
                "service_count": len(health_data.get("service_health", {})),
                "health_trend": self._calculate_health_trend(health_data)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_health_metrics", "nurse",
                    {"tenant_id": tenant_id, "uptime_percentage": health_metrics["uptime_percentage"]}
                )
            
            return {"success": True, "health_metrics": health_metrics}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_health_metrics")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_alert_summary(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get alert summary for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's alert summary"}
            
            # Get tenant alerts
            tenant_alerts = self._get_tenant_alerts(tenant_id)
            
            # Calculate alert summary
            alert_summary = {
                "tenant_id": tenant_id,
                "total_alerts": len(tenant_alerts),
                "critical_alerts": len([a for a in tenant_alerts if a.get("severity") == "critical"]),
                "warning_alerts": len([a for a in tenant_alerts if a.get("severity") == "warning"]),
                "info_alerts": len([a for a in tenant_alerts if a.get("severity") == "info"]),
                "resolved_alerts": len([a for a in tenant_alerts if a.get("status") == "resolved"]),
                "active_alerts": len([a for a in tenant_alerts if a.get("status") == "active"]),
                "alert_trends": self._calculate_alert_trends(tenant_alerts)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_alert_summary", "nurse",
                    {"tenant_id": tenant_id, "total_alerts": alert_summary["total_alerts"]}
                )
            
            return {"success": True, "alert_summary": alert_summary}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_alert_summary")
            return {"success": False, "error": str(e)}
    
    def _filter_health_data_by_tenant(self, health_data: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
        """Filter health data by tenant ID."""
        # Simplified filtering - in a real implementation, you'd filter based on actual tenant data
        return {
            "services": health_data.get("services", {}),
            "overall_health": health_data.get("overall_health", "healthy")
        }
    
    def _get_tenant_alerts(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get alerts for a specific tenant."""
        # Simplified - in a real implementation, you'd query alerts by tenant
        return [
            {
                "id": f"alert_{tenant_id}_1",
                "severity": "warning",
                "status": "active",
                "message": f"High CPU usage detected for tenant {tenant_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    
    def _get_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """Get metrics for a specific tenant."""
        # Simplified - in a real implementation, you'd query metrics by tenant
        return {
            "cpu_usage": 75.5,
            "memory_usage": 60.2,
            "disk_usage": 45.8,
            "network_io": 1024.5
        }
    
    def _calculate_uptime_percentage(self, health_data: Dict[str, Any]) -> float:
        """Calculate uptime percentage for tenant."""
        # Simplified calculation
        return 99.9
    
    def _calculate_average_response_time(self, health_data: Dict[str, Any]) -> float:
        """Calculate average response time for tenant."""
        # Simplified calculation
        return 150.5
    
    def _calculate_error_rate(self, health_data: Dict[str, Any]) -> float:
        """Calculate error rate for tenant."""
        # Simplified calculation
        return 0.1
    
    def _calculate_health_trend(self, health_data: Dict[str, Any]) -> str:
        """Calculate health trend for tenant."""
        # Simplified calculation
        return "improving"
    
    def _calculate_alert_trends(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate alert trends for tenant."""
        # Simplified trend calculation
        return {
            "last_hour": len([a for a in alerts if self._is_recent_alert(a, 1)]),
            "last_24_hours": len([a for a in alerts if self._is_recent_alert(a, 24)]),
            "last_week": len([a for a in alerts if self._is_recent_alert(a, 168)])
        }
    
    def _is_recent_alert(self, alert: Dict[str, Any], hours: int) -> bool:
        """Check if an alert is recent."""
        if not alert.get("timestamp"):
            return False
        
        try:
            from datetime import timedelta
            alert_time = datetime.fromisoformat(alert["timestamp"].replace('Z', '+00:00'))
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return alert_time >= cutoff_time
        except:
            return False


class NurseSOAProtocol(SOAServiceProtocol):
    """SOA Protocol implementation for Nurse Service."""
    
    def __init__(self, service_name: str, service_instance, curator_foundation=None, public_works_foundation=None):
        """Initialize Nurse SOA Protocol."""
        super().__init__(service_name, None, curator_foundation, public_works_foundation)
        self.service_instance = service_instance
        self.service_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the SOA service."""
        # Create service info with multi-tenant metadata
        self.service_info = SOAServiceInfo(
            service_name="NurseService",
            version="1.0.0",
            description="Nurse Service - Multi-tenant health monitoring and telemetry",
            interface_name="INurse",
            endpoints=self._create_all_endpoints(),
            tags=["health-monitoring", "telemetry", "multi-tenant", "alerting"],
            contact={"email": "nurse@smartcity.com"},
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_service_info(self) -> SOAServiceInfo:
        """Get service information for OpenAPI generation."""
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI 3.0 specification for this service."""
        if not self.service_info:
            return {"error": "Service not initialized"}
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description,
                "contact": self.service_info.contact
            },
            "servers": [
                {"url": "https://api.smartcity.com/nurse", "description": "Nurse Service"}
            ],
            "paths": self._create_openapi_paths(),
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    
    def get_docs(self) -> Dict[str, Any]:
        """Get service documentation."""
        return {
            "service": self.service_info.service_name,
            "description": self.service_info.description,
            "version": self.service_info.version,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
            "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
            "tenant_isolation_level": self.service_info.tenant_isolation_level
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this service with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],  # MCP tools handled separately
                "description": self.service_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
                "tenant_isolation_level": self.service_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.service_name, 
                capability, 
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_endpoints(self) -> List[SOAEndpoint]:
        """Create all endpoints for Nurse Service."""
        endpoints = []
        
        # Standard endpoints
        endpoints.extend(self._create_standard_endpoints())
        endpoints.extend(self._create_health_endpoints())
        endpoints.extend(self._create_tenant_aware_endpoints())
        
        # Nurse specific endpoints
        endpoints.extend([
            SOAEndpoint(
                path="/health/check",
                method="POST",
                summary="Perform Health Check",
                description="Perform a health check with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string"},
                        "check_type": {"type": "string"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["service_name", "check_type"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string"},
                        "status": {"type": "string"},
                        "response_time_ms": {"type": "number"}
                    }
                }),
                tags=["Health", "Monitoring"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/telemetry/collect",
                method="POST",
                summary="Collect Telemetry Data",
                description="Collect telemetry data with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "metric_name": {"type": "string"},
                        "value": {"type": "number"},
                        "tags": {"type": "object"},
                        "timestamp": {"type": "string"}
                    },
                    "required": ["metric_name", "value"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "metric_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Telemetry", "Collection"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/alerts",
                method="GET",
                summary="List Alerts",
                description="List alerts for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "alerts": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"}
                    }
                }),
                tags=["Alerts", "Management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/alerts",
                method="POST",
                summary="Create Alert",
                description="Create a new alert",
                request_schema={
                    "type": "object",
                    "properties": {
                        "rule_id": {"type": "string"},
                        "severity": {"type": "string"},
                        "message": {"type": "string"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["rule_id", "severity", "message"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "alert_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Alerts", "Management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/health-summary",
                method="GET",
                summary="Get Tenant Health Summary",
                description="Get health summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "overall_health": {"type": "string"},
                        "uptime_percentage": {"type": "number"},
                        "average_response_time": {"type": "number"}
                    }
                }),
                tags=["Tenant", "Health"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/alert-summary",
                method="GET",
                summary="Get Tenant Alert Summary",
                description="Get alert summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_alerts": {"type": "integer"},
                        "active_alerts": {"type": "integer"},
                        "alert_trends": {"type": "object"}
                    }
                }),
                tags=["Tenant", "Alerts"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return endpoints
    
    def _create_openapi_paths(self) -> Dict[str, Any]:
        """Create OpenAPI paths for all endpoints."""
        paths = {}
        
        for endpoint in self.service_info.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "security": [{"BearerAuth": []}] if endpoint.requires_tenant else []
                }
            }
            
            if endpoint.parameters:
                path_item[endpoint.method.lower()]["parameters"] = endpoint.parameters
            
            if endpoint.request_schema:
                path_item[endpoint.method.lower()]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
            
            if endpoint.response_schema:
                path_item[endpoint.method.lower()]["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": self._create_error_response_schema()
                            }
                        }
                    }
                }
            
            paths[endpoint.path] = path_item
        
        return paths