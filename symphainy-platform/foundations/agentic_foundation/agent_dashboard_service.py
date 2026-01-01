"""
Agent Dashboard Service
Unified dashboard for all agents across domains
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

# Import utility mixins
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin

# AgenticManagerService has been merged into AgenticFoundationService

class AgentDashboardService(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Unified dashboard service for all agents across domains.
    Integrates with domain managers to provide comprehensive agent view.
    """
    
    def __init__(self, di_container: Any = None, public_works_foundation: Any = None):
        """Initialize Agent Dashboard Service with optional dependencies."""
        if not di_container:
            raise ValueError("DI Container is required for AgentDashboardService initialization")
        
        # Initialize utility mixins
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.di_container = di_container
        self.service_name = "agent_dashboard_service"
        
        # AgenticManagerService has been merged into AgenticFoundationService
        # Get agentic foundation from DI Container
        self.agentic_foundation = None
        if di_container:
            try:
                self.agentic_foundation = di_container.get_foundation_service("AgenticFoundationService")
                if self.agentic_foundation:
                    self.logger.info("✅ Agentic Foundation Service available for agent governance")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get Agentic Foundation Service: {e}")
        
        # Domain manager references (would be injected in real implementation)
        # Note: These would be obtained via DI Container: self.di_container.get_service('city_manager')
        self.city_manager = None
        self.delivery_manager = None
        self.experience_manager = None
        self.journey_manager = None
    
    async def get_agent_overview(self) -> Dict[str, Any]:
        """Get unified agent overview across all domains"""
        try:
            if not self.agentic_foundation:
                return {"error": "Agentic Foundation Service not available"}
            
            # Get agent overview from agentic foundation
            agent_overview = await self.agentic_foundation.get_agent_overview()
            
            # Get domain-specific agent summaries
            domain_summaries = await self._get_domain_summaries()
            
            return {
                "overview": agent_overview,
                "domain_summaries": domain_summaries,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get agent overview: {e}")
            return {"error": str(e)}
    
    async def get_agent_health_dashboard(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive agent health dashboard"""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_health_dashboard_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_dashboard", "read"):
                        await self.record_health_metric("get_agent_health_dashboard_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_agent_health_dashboard_complete", success=False)
                        return {"error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_health_dashboard_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_health_dashboard_complete", success=False)
                            return {"error": "Tenant access denied"}
            
            if not self.agentic_foundation:
                await self.record_health_metric("get_agent_health_dashboard_service_unavailable", 1.0, {})
                await self.log_operation_with_telemetry("get_agent_health_dashboard_complete", success=False)
                return {"error": "Agentic Foundation Service not available"}
            
            # Get all agents
            all_agents = await self.agentic_foundation.get_all_agents()
            
            # Get health status for each agent
            health_data = []
            for agent in all_agents.get("agents", []):
                agent_id = agent.get("id")
                if agent_id:
                    health = await self.agentic_foundation.get_agent_health(agent_id)
                    health_data.append({
                        "agent_id": agent_id,
                        "domain": agent.get("domain"),
                        "type": agent.get("type"),
                        "health": health
                    })
            
            result = {
                "health_data": health_data,
                "summary": {
                    "total_agents": len(health_data),
                    "healthy_agents": len([h for h in health_data if h.get("health", {}).get("status") == "healthy"]),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_health_dashboard_success", 1.0, {"total_agents": len(health_data)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_health_dashboard_complete", success=True, 
                                                   details={"total_agents": len(health_data)})
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_health_dashboard")
            self.logger.error(f"Failed to get agent health dashboard: {e}")
            return {"error": str(e)}
    
    async def get_agent_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive agent performance dashboard"""
        try:
            if not self.agentic_foundation:
                return {"error": "Agentic Foundation Service not available"}
            
            # Get all agents
            all_agents = await self.agentic_foundation.get_all_agents()
            
            # Get performance metrics for each agent
            performance_data = []
            for agent in all_agents.get("agents", []):
                agent_id = agent.get("id")
                if agent_id:
                    performance = await self.agentic_foundation.get_agent_performance(agent_id)
                    performance_data.append({
                        "agent_id": agent_id,
                        "domain": agent.get("domain"),
                        "type": agent.get("type"),
                        "performance": performance
                    })
            
            return {
                "performance_data": performance_data,
                "summary": {
                    "total_agents": len(performance_data),
                    "avg_response_time": self._calculate_avg_response_time(performance_data),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get agent performance dashboard: {e}")
            return {"error": str(e)}
    
    async def get_agent_deployment_status(self) -> Dict[str, Any]:
        """Get agent deployment status across domains"""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_deployment_status_start", success=True)
            
            if not self.agentic_foundation:
                await self.record_health_metric("get_agent_deployment_status_service_unavailable", 1.0, {})
                await self.log_operation_with_telemetry("get_agent_deployment_status_complete", success=False)
                return {"error": "Agentic Foundation Service not available"}
            
            # Get deployment status for each domain
            domains = ["smart_city", "business_enablement", "experience", "journey"]
            deployment_status = {}
            
            for domain in domains:
                domain_agents = await self.agentic_foundation.get_domain_agents(domain)
                deployment_status[domain] = {
                    "agent_count": domain_agents.get("agent_count", 0),
                    "agents": domain_agents.get("agents", []),
                    "deployment_status": "healthy"  # Would be determined by actual deployment status
                }
            
            result = {
                "deployment_status": deployment_status,
                "overall_status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_deployment_status_success", 1.0, {"domains_count": len(domains)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_deployment_status_complete", success=True, 
                                                   details={"domains_count": len(domains)})
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_deployment_status")
            self.logger.error(f"Failed to get agent deployment status: {e}")
            return {"error": str(e)}
    
    async def get_agent_ci_cd_status(self) -> Dict[str, Any]:
        """Get agent CI/CD status across domains"""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_ci_cd_status_start", success=True)
            
            # Get CI/CD status for each domain
            domains = ["smart_city", "business_enablement", "experience", "journey"]
            cicd_status = {}
            
            for domain in domains:
                cicd_status[domain] = {
                    "pipeline_status": "success",
                    "last_deployment": datetime.utcnow().isoformat(),
                    "deployment_frequency": "daily",
                    "success_rate": "99.9%"
                }
            
            result = {
                "cicd_status": cicd_status,
                "overall_pipeline_status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_agent_ci_cd_status_success", 1.0, {"domains_count": len(domains)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_ci_cd_status_complete", success=True, 
                                                   details={"domains_count": len(domains)})
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_ci_cd_status")
            self.logger.error(f"Failed to get agent CI/CD status: {e}")
            return {"error": str(e)}
    
    async def get_agent_business_metrics(self) -> Dict[str, Any]:
        """Get agent business metrics and ROI"""
        try:
            if not self.agentic_foundation:
                return {"error": "Agentic Foundation Service not available"}
            
            # Get business metrics for each agent
            all_agents = await self.agentic_foundation.get_all_agents()
            
            business_metrics = []
            for agent in all_agents.get("agents", []):
                agent_id = agent.get("id")
                if agent_id:
                    # Mock business metrics (would be calculated from actual data)
                    business_metrics.append({
                        "agent_id": agent_id,
                        "domain": agent.get("domain"),
                        "type": agent.get("type"),
                        "usage_count": 1000,  # Mock data
                        "business_value": "high",  # Mock data
                        "roi": "positive",  # Mock data
                        "cost": 100,  # Mock data
                        "revenue_impact": 1000  # Mock data
                    })
            
            return {
                "business_metrics": business_metrics,
                "summary": {
                    "total_agents": len(business_metrics),
                    "high_value_agents": len([m for m in business_metrics if m.get("business_value") == "high"]),
                    "total_roi": "positive",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get agent business metrics: {e}")
            return {"error": str(e)}
    
    async def _get_domain_summaries(self) -> Dict[str, Any]:
        """Get domain-specific agent summaries"""
        try:
            # This would integrate with actual domain managers
            # For now, return mock data
            return {
                "smart_city": {
                    "agent_count": 3,
                    "active_agents": 3,
                    "health_status": "healthy",
                    "performance": "excellent"
                },
                "business_enablement": {
                    "agent_count": 2,
                    "active_agents": 2,
                    "health_status": "healthy",
                    "performance": "good"
                },
                "experience": {
                    "agent_count": 1,
                    "active_agents": 1,
                    "health_status": "healthy",
                    "performance": "excellent"
                },
                "journey": {
                    "agent_count": 1,
                    "active_agents": 1,
                    "health_status": "healthy",
                    "performance": "good"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get domain summaries: {e}")
            return {}
    
    def _calculate_avg_response_time(self, performance_data: List[Dict[str, Any]]) -> str:
        """Calculate average response time across all agents"""
        try:
            response_times = []
            for data in performance_data:
                performance = data.get("performance", {})
                if "response_time" in performance:
                    # Extract numeric value from response time string
                    response_time_str = performance["response_time"]
                    if "ms" in response_time_str:
                        response_time = float(response_time_str.replace("ms", ""))
                        response_times.append(response_time)
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                return f"{avg_response_time:.1f}ms"
            else:
                return "N/A"
        except Exception as e:
            self.logger.error(f"Failed to calculate average response time: {e}")
            return "N/A"
    
    async def get_comprehensive_dashboard(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive agent dashboard with all metrics"""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_comprehensive_dashboard_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_dashboard", "read"):
                        await self.record_health_metric("get_comprehensive_dashboard_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_comprehensive_dashboard_complete", success=False)
                        return {"error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_comprehensive_dashboard_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_comprehensive_dashboard_complete", success=False)
                            return {"error": "Tenant access denied"}
            
            # Get all dashboard components
            overview = await self.get_agent_overview()
            health = await self.get_agent_health_dashboard(user_context)
            performance = await self.get_agent_performance_dashboard()
            deployment = await self.get_agent_deployment_status()
            cicd = await self.get_agent_ci_cd_status()
            business = await self.get_agent_business_metrics()
            
            result = {
                "overview": overview,
                "health": health,
                "performance": performance,
                "deployment": deployment,
                "cicd": cicd,
                "business": business,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_comprehensive_dashboard_success", 1.0, {})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_comprehensive_dashboard_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_comprehensive_dashboard")
            self.logger.error(f"Failed to get comprehensive dashboard: {e}")
            return {"error": str(e)}




