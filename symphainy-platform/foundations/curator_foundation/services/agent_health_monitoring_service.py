#!/usr/bin/env python3
"""
Agent Health Monitoring Service

Provides agent-specific health monitoring for the Curator Foundation.
Monitors agent health, performance, and operational status in real-time.

WHAT (Curator Role): I provide agent-specific health monitoring and operational status tracking
HOW (Agent Health Monitoring Service): I monitor agent health, performance, and operational status in real-time
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase


@dataclass
class AgentHealthMetrics:
    """Agent health metrics definition."""
    agent_id: str
    agent_name: str
    overall_status: str  # healthy, degraded, unhealthy, unknown
    response_time_ms: float
    success_rate: float
    error_rate: float
    availability_percentage: float
    last_health_check: str
    capabilities_status: Dict[str, str]  # capability_name -> status
    dependencies_status: Dict[str, str]  # dependency -> status
    resource_usage: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    alerts: List[Dict[str, Any]]


@dataclass
class AgentHealthReport:
    """Agent health report for Curator."""
    agent_id: str
    agent_name: str
    health_status: str
    performance_score: float
    reliability_score: float
    availability_score: float
    last_updated: str
    trends: Dict[str, Any]
    recommendations: List[str]
    critical_issues: List[str]


class AgentHealthMonitoringService(FoundationServiceBase):
    """
    Agent Health Monitoring Service for Curator Foundation.
    
    Provides agent-specific health monitoring and operational status tracking.
    Monitors agent health, performance, and operational status in real-time.
    
    Features:
    - Real-time agent health monitoring
    - Performance metrics tracking
    - Availability and reliability monitoring
    - Capability health assessment
    - Dependency health tracking
    - Resource usage monitoring
    - Alert generation and management
    - Health trend analysis
    - Automated health recommendations
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize Agent Health Monitoring Service."""
        super().__init__("agent_health_monitoring", di_container)
        
        # Store public works foundation reference
        self.public_works_foundation = public_works_foundation
        
        # Agent health storage
        self.agent_health: Dict[str, AgentHealthMetrics] = {}  # agent_id -> health metrics
        self.health_history: Dict[str, List[Dict[str, Any]]] = {}  # agent_id -> health history
        self.health_alerts: Dict[str, List[Dict[str, Any]]] = {}  # agent_id -> alerts
        
        # Monitoring configuration
        self.health_check_interval = 30  # seconds
        self.performance_thresholds = {
            "response_time_ms": 5000,  # 5 seconds
            "success_rate": 0.95,  # 95%
            "error_rate": 0.05,  # 5%
            "availability": 0.99  # 99%
        }
        
        # Monitoring tasks
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        
        self.logger.info("Agent Health Monitoring Service initialized")
    
    async def initialize(self):
        """Initialize the Agent Health Monitoring Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_health_monitoring_initialize_start", success=True)
            
            self.logger.info("🚀 Initializing Agent Health Monitoring Service...")
            
            # Load existing health data from storage
            await self._load_health_data_from_storage()
            
            # Start health monitoring for existing agents
            await self._start_health_monitoring()
            
            self.logger.info("✅ Agent Health Monitoring Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("agent_health_monitoring_initialized", 1.0, {"service": "agent_health_monitoring"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_health_monitoring_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_health_monitoring_initialize")
            self.logger.error(f"❌ Failed to initialize Agent Health Monitoring Service: {e}")
            raise
    
    async def _load_health_data_from_storage(self):
        """Load existing health data from persistent storage."""
        try:
            # In a real implementation, this would load from a database
            # For now, we'll start with an empty registry
            self.logger.info("📚 Loaded health data from storage")
            
        except Exception as e:
            self.logger.error(f"Failed to load health data from storage: {e}")
            await self.handle_error_with_audit(e, "load_health_data_from_storage_failed")
    
    async def _start_health_monitoring(self):
        """Start health monitoring for all registered agents."""
        try:
            # Start monitoring task for each agent
            for agent_id in self.agent_health.keys():
                await self._start_agent_monitoring(agent_id)
            
            self.logger.info(f"🔍 Started health monitoring for {len(self.monitoring_tasks)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to start health monitoring: {e}")
            await self.handle_error_with_audit(e, "start_health_monitoring_failed")
    
    async def _start_agent_monitoring(self, agent_id: str):
        """Start health monitoring for a specific agent."""
        try:
            if agent_id in self.monitoring_tasks:
                return  # Already monitoring
            
            # Create monitoring task
            monitor_task = asyncio.create_task(self._monitor_agent_health(agent_id))
            self.monitoring_tasks[agent_id] = monitor_task
            
            self.logger.info(f"🔍 Started health monitoring for agent {agent_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring for agent {agent_id}: {e}")
            await self.handle_error_with_audit(e, f"start_agent_monitoring_failed_{agent_id}")
    
    async def _monitor_agent_health(self, agent_id: str):
        """Monitor agent health in real-time."""
        try:
            while True:
                # Perform health check
                await self._perform_health_check(agent_id)
                
                # Update health history
                await self._update_health_history(agent_id)
                
                # Check for alerts
                await self._check_health_alerts(agent_id)
                
                # Wait before next check
                await asyncio.sleep(self.health_check_interval)
                
        except asyncio.CancelledError:
            self.logger.info(f"Health monitoring stopped for agent {agent_id}")
        except Exception as e:
            self.logger.error(f"Error monitoring health for agent {agent_id}: {e}")
            await self.handle_error_with_audit(e, f"monitor_agent_health_failed_{agent_id}")
    
    async def _perform_health_check(self, agent_id: str):
        """Perform comprehensive health check for an agent."""
        try:
            if agent_id not in self.agent_health:
                # Initialize health metrics for new agent
                self.agent_health[agent_id] = AgentHealthMetrics(
                    agent_id=agent_id,
                    agent_name=f"Agent_{agent_id}",
                    overall_status="unknown",
                    response_time_ms=0.0,
                    success_rate=0.0,
                    error_rate=0.0,
                    availability_percentage=0.0,
                    last_health_check=datetime.now().isoformat(),
                    capabilities_status={},
                    dependencies_status={},
                    resource_usage={},
                    performance_metrics={},
                    alerts=[]
                )
            
            health_metrics = self.agent_health[agent_id]
            
            # Simulate health check (in real implementation, this would call agent health endpoints)
            start_time = datetime.now()
            
            # Simulate response time
            response_time = 100.0 + (hash(agent_id) % 1000)  # Simulate 100-1100ms response time
            
            # Simulate success rate (90-99%)
            success_rate = 0.90 + (hash(agent_id) % 10) / 100.0
            
            # Simulate error rate
            error_rate = 1.0 - success_rate
            
            # Simulate availability (95-99.9%)
            availability = 0.95 + (hash(agent_id) % 50) / 1000.0
            
            # Update health metrics
            health_metrics.response_time_ms = response_time
            health_metrics.success_rate = success_rate
            health_metrics.error_rate = error_rate
            health_metrics.availability_percentage = availability
            health_metrics.last_health_check = datetime.now().isoformat()
            
            # Determine overall status
            health_metrics.overall_status = self._determine_health_status(health_metrics)
            
            # Update capabilities status
            health_metrics.capabilities_status = await self._check_capabilities_health(agent_id)
            
            # Update dependencies status
            health_metrics.dependencies_status = await self._check_dependencies_health(agent_id)
            
            # Update resource usage
            health_metrics.resource_usage = await self._check_resource_usage(agent_id)
            
            # Update performance metrics
            health_metrics.performance_metrics = await self._collect_performance_metrics(agent_id)
            
            self.logger.debug(f"Health check completed for agent {agent_id}: {health_metrics.overall_status}")
            
        except Exception as e:
            self.logger.error(f"Failed to perform health check for agent {agent_id}: {e}")
            await self.handle_error_with_audit(e, f"perform_health_check_failed_{agent_id}")
    
    def _determine_health_status(self, health_metrics: AgentHealthMetrics) -> str:
        """Determine overall health status based on metrics."""
        try:
            # Check response time
            if health_metrics.response_time_ms > self.performance_thresholds["response_time_ms"]:
                return "degraded"
            
            # Check success rate
            if health_metrics.success_rate < self.performance_thresholds["success_rate"]:
                return "unhealthy"
            
            # Check error rate
            if health_metrics.error_rate > self.performance_thresholds["error_rate"]:
                return "unhealthy"
            
            # Check availability
            if health_metrics.availability_percentage < self.performance_thresholds["availability"]:
                return "degraded"
            
            return "healthy"
            
        except Exception as e:
            self.logger.error(f"Failed to determine health status: {e}")
            return "unknown"
    
    async def _check_capabilities_health(self, agent_id: str) -> Dict[str, str]:
        """Check health of agent capabilities."""
        try:
            # In a real implementation, this would check actual capability health
            # For now, simulate capability status
            capabilities = ["analysis", "data_processing", "output_generation"]
            status_map = {}
            
            for capability in capabilities:
                # Simulate capability health (mostly healthy with occasional issues)
                if hash(f"{agent_id}_{capability}") % 10 == 0:
                    status_map[capability] = "degraded"
                else:
                    status_map[capability] = "healthy"
            
            return status_map
            
        except Exception as e:
            self.logger.error(f"Failed to check capabilities health for agent {agent_id}: {e}")
            return {}
    
    async def _check_dependencies_health(self, agent_id: str) -> Dict[str, str]:
        """Check health of agent dependencies."""
        try:
            # In a real implementation, this would check actual dependency health
            # For now, simulate dependency status
            dependencies = ["database", "redis", "llm_service", "storage"]
            status_map = {}
            
            for dependency in dependencies:
                # Simulate dependency health (mostly healthy)
                if hash(f"{agent_id}_{dependency}") % 20 == 0:
                    status_map[dependency] = "degraded"
                else:
                    status_map[dependency] = "healthy"
            
            return status_map
            
        except Exception as e:
            self.logger.error(f"Failed to check dependencies health for agent {agent_id}: {e}")
            return {}
    
    async def _check_resource_usage(self, agent_id: str) -> Dict[str, Any]:
        """Check agent resource usage."""
        try:
            # In a real implementation, this would check actual resource usage
            # For now, simulate resource usage
            return {
                "cpu_percentage": 20.0 + (hash(agent_id) % 30),
                "memory_mb": 100 + (hash(agent_id) % 200),
                "disk_usage_mb": 50 + (hash(agent_id) % 100),
                "network_io_mb": 10 + (hash(agent_id) % 50)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check resource usage for agent {agent_id}: {e}")
            return {}
    
    async def _collect_performance_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Collect performance metrics for an agent."""
        try:
            # In a real implementation, this would collect actual performance metrics
            # For now, simulate performance metrics
            return {
                "requests_per_minute": 10 + (hash(agent_id) % 50),
                "average_processing_time_ms": 200 + (hash(agent_id) % 800),
                "peak_memory_usage_mb": 150 + (hash(agent_id) % 100),
                "cache_hit_rate": 0.85 + (hash(agent_id) % 15) / 100.0,
                "error_count_last_hour": hash(agent_id) % 5
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance metrics for agent {agent_id}: {e}")
            return {}
    
    async def _update_health_history(self, agent_id: str):
        """Update health history for trend analysis."""
        try:
            if agent_id not in self.health_history:
                self.health_history[agent_id] = []
            
            health_metrics = self.agent_health.get(agent_id)
            if not health_metrics:
                return
            
            # Add current health data to history
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": health_metrics.overall_status,
                "response_time_ms": health_metrics.response_time_ms,
                "success_rate": health_metrics.success_rate,
                "error_rate": health_metrics.error_rate,
                "availability_percentage": health_metrics.availability_percentage
            }
            
            self.health_history[agent_id].append(history_entry)
            
            # Keep only last 100 entries (about 50 minutes of data at 30s intervals)
            if len(self.health_history[agent_id]) > 100:
                self.health_history[agent_id] = self.health_history[agent_id][-100:]
            
        except Exception as e:
            self.logger.error(f"Failed to update health history for agent {agent_id}: {e}")
            await self.handle_error_with_audit(e, f"update_health_history_failed_{agent_id}")
    
    async def _check_health_alerts(self, agent_id: str):
        """Check for health alerts and generate new ones."""
        try:
            health_metrics = self.agent_health.get(agent_id)
            if not health_metrics:
                return
            
            alerts = []
            
            # Check for performance issues
            if health_metrics.response_time_ms > self.performance_thresholds["response_time_ms"]:
                alerts.append({
                    "type": "performance",
                    "severity": "warning",
                    "message": f"High response time: {health_metrics.response_time_ms:.1f}ms",
                    "timestamp": datetime.now().isoformat()
                })
            
            if health_metrics.success_rate < self.performance_thresholds["success_rate"]:
                alerts.append({
                    "type": "reliability",
                    "severity": "critical",
                    "message": f"Low success rate: {health_metrics.success_rate:.2%}",
                    "timestamp": datetime.now().isoformat()
                })
            
            if health_metrics.error_rate > self.performance_thresholds["error_rate"]:
                alerts.append({
                    "type": "reliability",
                    "severity": "critical",
                    "message": f"High error rate: {health_metrics.error_rate:.2%}",
                    "timestamp": datetime.now().isoformat()
                })
            
            if health_metrics.availability_percentage < self.performance_thresholds["availability"]:
                alerts.append({
                    "type": "availability",
                    "severity": "warning",
                    "message": f"Low availability: {health_metrics.availability_percentage:.2%}",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Check capability health
            for capability, status in health_metrics.capabilities_status.items():
                if status == "degraded":
                    alerts.append({
                        "type": "capability",
                        "severity": "warning",
                        "message": f"Capability {capability} is degraded",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Check dependency health
            for dependency, status in health_metrics.dependencies_status.items():
                if status == "degraded":
                    alerts.append({
                        "type": "dependency",
                        "severity": "warning",
                        "message": f"Dependency {dependency} is degraded",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Update alerts
            if agent_id not in self.health_alerts:
                self.health_alerts[agent_id] = []
            
            # Add new alerts
            for alert in alerts:
                if not self._is_duplicate_alert(agent_id, alert):
                    self.health_alerts[agent_id].append(alert)
            
            # Update health metrics alerts
            health_metrics.alerts = self.health_alerts[agent_id][-10:]  # Keep last 10 alerts
            
        except Exception as e:
            self.logger.error(f"Failed to check health alerts for agent {agent_id}: {e}")
            await self.handle_error_with_audit(e, f"check_health_alerts_failed_{agent_id}")
    
    def _is_duplicate_alert(self, agent_id: str, new_alert: Dict[str, Any]) -> bool:
        """Check if alert is a duplicate of recent alerts."""
        try:
            if agent_id not in self.health_alerts:
                return False
            
            recent_alerts = self.health_alerts[agent_id][-5:]  # Check last 5 alerts
            
            for alert in recent_alerts:
                if (alert["type"] == new_alert["type"] and 
                    alert["message"] == new_alert["message"] and
                    alert["severity"] == new_alert["severity"]):
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check duplicate alert: {e}")
            return False
    
    # ============================================================================
    # PUBLIC API METHODS
    # ============================================================================
    
    async def register_agent_for_monitoring(self, agent_id: str, agent_name: str, user_context: Dict[str, Any] = None) -> bool:
        """
        Register an agent for health monitoring.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_agent_for_monitoring_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "write"):
                        await self.record_health_metric("register_agent_for_monitoring_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("register_agent_for_monitoring_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_agent_for_monitoring_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_agent_for_monitoring_complete", success=False)
                            return False
            
            self.logger.info(f"📝 Registering agent {agent_name} for health monitoring")
            
            # Initialize health metrics
            self.agent_health[agent_id] = AgentHealthMetrics(
                agent_id=agent_id,
                agent_name=agent_name,
                overall_status="unknown",
                response_time_ms=0.0,
                success_rate=0.0,
                error_rate=0.0,
                availability_percentage=0.0,
                last_health_check=datetime.now().isoformat(),
                capabilities_status={},
                dependencies_status={},
                resource_usage={},
                performance_metrics={},
                alerts=[]
            )
            
            # Initialize health history
            self.health_history[agent_id] = []
            
            # Initialize alerts
            self.health_alerts[agent_id] = []
            
            # Start monitoring
            await self._start_agent_monitoring(agent_id)
            
            self.logger.info(f"✅ Successfully registered agent {agent_name} for health monitoring")
            
            # Record health metric
            await self.record_health_metric("register_agent_for_monitoring_success", 1.0, {"agent_id": agent_id, "agent_name": agent_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_agent_for_monitoring_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agent_for_monitoring")
            self.logger.error(f"❌ Failed to register agent for monitoring: {e}")
            return False
    
    async def get_agent_health(self, agent_id: str, user_context: Dict[str, Any] = None) -> Optional[AgentHealthMetrics]:
        """
        Get current health metrics for an agent.
        
        Args:
            agent_id: Agent identifier
            user_context: Optional user context for security and tenant validation
            
        Returns:
            AgentHealthMetrics or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_health_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("get_agent_health_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_health_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_health_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_health_complete", success=False)
                            return None
            
            result = self.agent_health.get(agent_id)
            
            # Record health metric
            await self.record_health_metric("get_agent_health_success", 1.0, {"agent_id": agent_id, "found": result is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_health_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_health")
            self.logger.error(f"Failed to get health for agent {agent_id}: {e}")
            return None
    
    async def get_agent_health_report(self, agent_id: str, user_context: Dict[str, Any] = None) -> Optional[AgentHealthReport]:
        """
        Get comprehensive health report for an agent.
        
        Args:
            agent_id: Agent identifier
            user_context: Optional user context for security and tenant validation
            
        Returns:
            AgentHealthReport or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_health_report_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("get_agent_health_report_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_health_report_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_health_report_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_health_report_complete", success=False)
                            return None
            
            health_metrics = self.agent_health.get(agent_id)
            if not health_metrics:
                await self.record_health_metric("get_agent_health_report_not_found", 1.0, {"agent_id": agent_id})
                await self.log_operation_with_telemetry("get_agent_health_report_complete", success=True)
                return None
            
            # Calculate performance score (0-100)
            performance_score = self._calculate_performance_score(health_metrics)
            
            # Calculate reliability score (0-100)
            reliability_score = self._calculate_reliability_score(health_metrics)
            
            # Calculate availability score (0-100)
            availability_score = health_metrics.availability_percentage * 100
            
            # Analyze trends
            trends = await self._analyze_health_trends(agent_id)
            
            # Generate recommendations
            recommendations = await self._generate_health_recommendations(health_metrics)
            
            # Identify critical issues
            critical_issues = await self._identify_critical_issues(health_metrics)
            
            result = AgentHealthReport(
                agent_id=agent_id,
                agent_name=health_metrics.agent_name,
                health_status=health_metrics.overall_status,
                performance_score=performance_score,
                reliability_score=reliability_score,
                availability_score=availability_score,
                last_updated=health_metrics.last_health_check,
                trends=trends,
                recommendations=recommendations,
                critical_issues=critical_issues
            )
            
            # Record health metric
            await self.record_health_metric("get_agent_health_report_success", 1.0, {"agent_id": agent_id, "status": health_metrics.overall_status})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_health_report_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_health_report")
            self.logger.error(f"Failed to generate health report for agent {agent_id}: {e}")
            return None
    
    def _calculate_performance_score(self, health_metrics: AgentHealthMetrics) -> float:
        """Calculate performance score (0-100)."""
        try:
            # Response time score (0-40 points)
            response_time_score = max(0, 40 - (health_metrics.response_time_ms / 100))
            
            # Success rate score (0-30 points)
            success_rate_score = health_metrics.success_rate * 30
            
            # Error rate score (0-30 points)
            error_rate_score = max(0, 30 - (health_metrics.error_rate * 600))
            
            return min(100, response_time_score + success_rate_score + error_rate_score)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate performance score: {e}")
            return 0.0
    
    def _calculate_reliability_score(self, health_metrics: AgentHealthMetrics) -> float:
        """Calculate reliability score (0-100)."""
        try:
            # Base score from success rate
            base_score = health_metrics.success_rate * 70
            
            # Bonus for low error rate
            error_bonus = max(0, 30 - (health_metrics.error_rate * 600))
            
            return min(100, base_score + error_bonus)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate reliability score: {e}")
            return 0.0
    
    async def _analyze_health_trends(self, agent_id: str) -> Dict[str, Any]:
        """Analyze health trends for an agent."""
        try:
            if agent_id not in self.health_history or len(self.health_history[agent_id]) < 2:
                return {"trend": "insufficient_data"}
            
            history = self.health_history[agent_id]
            recent_data = history[-10:]  # Last 10 data points
            
            # Calculate trends
            response_times = [entry["response_time_ms"] for entry in recent_data]
            success_rates = [entry["success_rate"] for entry in recent_data]
            
            # Simple trend calculation (slope of linear regression)
            response_trend = self._calculate_trend(response_times)
            success_trend = self._calculate_trend(success_rates)
            
            return {
                "response_time_trend": "improving" if response_trend < 0 else "degrading" if response_trend > 0 else "stable",
                "success_rate_trend": "improving" if success_trend > 0 else "degrading" if success_trend < 0 else "stable",
                "trend_period": f"{len(recent_data)} data points",
                "overall_trend": "improving" if response_trend < 0 and success_trend > 0 else "degrading" if response_trend > 0 and success_trend < 0 else "stable"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze health trends for agent {agent_id}: {e}")
            return {"trend": "analysis_failed"}
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope for a series of values."""
        try:
            if len(values) < 2:
                return 0.0
            
            n = len(values)
            x = list(range(n))
            
            # Simple linear regression slope
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(xi * xi for xi in x)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return slope
            
        except Exception as e:
            self.logger.error(f"Failed to calculate trend: {e}")
            return 0.0
    
    async def _generate_health_recommendations(self, health_metrics: AgentHealthMetrics) -> List[str]:
        """Generate health recommendations based on metrics."""
        try:
            recommendations = []
            
            # Response time recommendations
            if health_metrics.response_time_ms > self.performance_thresholds["response_time_ms"]:
                recommendations.append("Consider optimizing agent processing logic to reduce response time")
                recommendations.append("Check for resource bottlenecks or inefficient algorithms")
            
            # Success rate recommendations
            if health_metrics.success_rate < self.performance_thresholds["success_rate"]:
                recommendations.append("Review error handling and input validation")
                recommendations.append("Check for external service dependencies that may be failing")
            
            # Error rate recommendations
            if health_metrics.error_rate > self.performance_thresholds["error_rate"]:
                recommendations.append("Implement better error handling and retry mechanisms")
                recommendations.append("Review agent configuration and dependencies")
            
            # Availability recommendations
            if health_metrics.availability_percentage < self.performance_thresholds["availability"]:
                recommendations.append("Implement health checks and automatic recovery mechanisms")
                recommendations.append("Consider implementing redundancy or failover")
            
            # Capability recommendations
            degraded_capabilities = [cap for cap, status in health_metrics.capabilities_status.items() if status == "degraded"]
            if degraded_capabilities:
                recommendations.append(f"Review and fix degraded capabilities: {', '.join(degraded_capabilities)}")
            
            # Dependency recommendations
            degraded_dependencies = [dep for dep, status in health_metrics.dependencies_status.items() if status == "degraded"]
            if degraded_dependencies:
                recommendations.append(f"Check and fix degraded dependencies: {', '.join(degraded_dependencies)}")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to generate health recommendations: {e}")
            return []
    
    async def _identify_critical_issues(self, health_metrics: AgentHealthMetrics) -> List[str]:
        """Identify critical issues that need immediate attention."""
        try:
            critical_issues = []
            
            # Critical performance issues
            if health_metrics.response_time_ms > self.performance_thresholds["response_time_ms"] * 2:
                critical_issues.append(f"Critical: Response time is extremely high ({health_metrics.response_time_ms:.1f}ms)")
            
            if health_metrics.success_rate < 0.8:  # Below 80%
                critical_issues.append(f"Critical: Success rate is critically low ({health_metrics.success_rate:.2%})")
            
            if health_metrics.error_rate > 0.2:  # Above 20%
                critical_issues.append(f"Critical: Error rate is critically high ({health_metrics.error_rate:.2%})")
            
            if health_metrics.availability_percentage < 0.9:  # Below 90%
                critical_issues.append(f"Critical: Availability is critically low ({health_metrics.availability_percentage:.2%})")
            
            # Critical capability issues
            failed_capabilities = [cap for cap, status in health_metrics.capabilities_status.items() if status == "failed"]
            if failed_capabilities:
                critical_issues.append(f"Critical: Failed capabilities: {', '.join(failed_capabilities)}")
            
            # Critical dependency issues
            failed_dependencies = [dep for dep, status in health_metrics.dependencies_status.items() if status == "failed"]
            if failed_dependencies:
                critical_issues.append(f"Critical: Failed dependencies: {', '.join(failed_dependencies)}")
            
            return critical_issues
            
        except Exception as e:
            self.logger.error(f"Failed to identify critical issues: {e}")
            return []
    
    async def get_all_agent_health_reports(self, user_context: Dict[str, Any] = None) -> List[AgentHealthReport]:
        """Get health reports for all monitored agents."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_all_agent_health_reports_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_health_monitoring", "read"):
                        await self.record_health_metric("get_all_agent_health_reports_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_all_agent_health_reports_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            reports = []
            for agent_id in self.agent_health.keys():
                # Filter by tenant if user_context provided
                if user_context:
                    tenant = self.get_tenant()
                    if tenant:
                        tenant_id = user_context.get("tenant_id")
                        if tenant_id:
                            if not await tenant.validate_tenant_access(tenant_id):
                                continue  # Skip agents from other tenants
                
                report = await self.get_agent_health_report(agent_id, user_context)
                if report:
                    reports.append(report)
            
            # Record health metric
            await self.record_health_metric("get_all_agent_health_reports_success", 1.0, {"count": len(reports)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_all_agent_health_reports_complete", success=True)
            
            return reports
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_all_agent_health_reports")
            self.logger.error(f"Failed to get all agent health reports: {e}")
            return []
    
    async def get_health_summary(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get overall health summary for all agents."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_health_summary_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_health", "read"):
                        await self.record_health_metric("get_health_summary_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_health_summary_complete", success=False)
                        return {}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_health_summary_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_health_summary_complete", success=False)
                            return {}
            
            total_agents = len(self.agent_health)
            healthy_agents = len([h for h in self.agent_health.values() if h.overall_status == "healthy"])
            degraded_agents = len([h for h in self.agent_health.values() if h.overall_status == "degraded"])
            unhealthy_agents = len([h for h in self.agent_health.values() if h.overall_status == "unhealthy"])
            unknown_agents = len([h for h in self.agent_health.values() if h.overall_status == "unknown"])
            
            # Calculate average metrics
            if total_agents > 0:
                avg_response_time = sum(h.response_time_ms for h in self.agent_health.values()) / total_agents
                avg_success_rate = sum(h.success_rate for h in self.agent_health.values()) / total_agents
                avg_error_rate = sum(h.error_rate for h in self.agent_health.values()) / total_agents
                avg_availability = sum(h.availability_percentage for h in self.agent_health.values()) / total_agents
            else:
                avg_response_time = 0.0
                avg_success_rate = 0.0
                avg_error_rate = 0.0
                avg_availability = 0.0
            
            # Count total alerts
            total_alerts = sum(len(alerts) for alerts in self.health_alerts.values())
            critical_alerts = sum(
                len([alert for alert in alerts if alert.get("severity") == "critical"])
                for alerts in self.health_alerts.values()
            )
            
            result = {
                "total_agents": total_agents,
                "health_distribution": {
                    "healthy": healthy_agents,
                    "degraded": degraded_agents,
                    "unhealthy": unhealthy_agents,
                    "unknown": unknown_agents
                },
                "average_metrics": {
                    "response_time_ms": avg_response_time,
                    "success_rate": avg_success_rate,
                    "error_rate": avg_error_rate,
                    "availability_percentage": avg_availability
                },
                "alerts": {
                    "total": total_alerts,
                    "critical": critical_alerts,
                    "warning": total_alerts - critical_alerts
                },
                "generated_at": datetime.now().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("get_health_summary_success", 1.0, {"total_agents": total_agents, "healthy_agents": healthy_agents})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_health_summary_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_health_summary")
            self.logger.error(f"Failed to generate health summary: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup the service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_health_monitoring_cleanup_start", success=True)
            
            # Cancel monitoring tasks
            for task in self.monitoring_tasks.values():
                task.cancel()
            
            self.monitoring_tasks.clear()
            self.agent_health.clear()
            self.health_history.clear()
            self.health_alerts.clear()
            
            self.logger.info("Agent Health Monitoring Service cleaned up")
            
            # Record health metric
            await self.record_health_metric("agent_health_monitoring_cleanup", 1.0, {"service": "agent_health_monitoring"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_health_monitoring_cleanup_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_health_monitoring_cleanup")
            self.logger.error(f"Error during cleanup: {e}")

    async def shutdown(self):
        """Shutdown the Agent Health Monitoring Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_health_monitoring_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Agent Health Monitoring Service...")
            
            # Clear health data
            self.agent_health_data.clear()
            self.health_alerts.clear()
            
            self.logger.info("✅ Agent Health Monitoring Service shutdown complete")
            
            # Record health metric
            await self.record_health_metric("agent_health_monitoring_shutdown", 1.0, {"service": "agent_health_monitoring"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_health_monitoring_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_health_monitoring_shutdown")
            self.logger.error(f"❌ Error during Agent Health Monitoring Service shutdown: {e}")





