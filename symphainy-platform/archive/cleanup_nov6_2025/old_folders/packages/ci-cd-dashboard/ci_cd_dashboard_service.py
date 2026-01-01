"""
CI/CD Dashboard Service
Comprehensive admin dashboard for CI/CD monitoring and platform governance
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService


@dataclass
class DomainHealthStatus:
    """Domain health status data structure."""
    domain: str
    status: str
    health_percentage: float
    services_count: int
    healthy_services: int
    last_updated: datetime
    issues: List[str]


@dataclass
class AgentStatus:
    """Agent status data structure."""
    agent_id: str
    domain: str
    status: str
    performance_metrics: Dict[str, Any]
    last_heartbeat: datetime
    capabilities: List[str]


@dataclass
class CICDPipelineStatus:
    """CI/CD pipeline status data structure."""
    pipeline_id: str
    domain: str
    status: str
    last_run: datetime
    success_rate: float
    duration_avg: float
    deployments_count: int


class CICDDashboardService:
    """
    CI/CD Dashboard Service
    Comprehensive admin dashboard for CI/CD monitoring and platform governance.
    
    This service aggregates data from domain managers via CI/CD abstractions
    and provides a unified view of platform health, agent status, and CI/CD metrics.
    """
    
    def __init__(self, public_works_foundation: PublicWorksFoundationService):
        """
        Initialize the CI/CD Dashboard Service.
        
        Args:
            public_works_foundation: Public Works Foundation service for accessing CI/CD abstractions
        """
        self.public_works_foundation = public_works_foundation
        self.logger = logging.getLogger(__name__)
        
        # CI/CD abstractions from Public Works Foundation
        self.cicd_monitoring_abstraction = None
        self.deployment_management_abstraction = None
        self.agent_governance_abstraction = None
        
        # Domain manager references (will be injected)
        self.city_manager = None
        self.delivery_manager = None
        self.experience_manager = None
        self.journey_manager = None
        self.agentic_manager = None
        
        # Dashboard data cache
        self.dashboard_data_cache = {}
        self.cache_ttl = 30  # seconds
        
        # Initialize the service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the CI/CD Dashboard Service."""
        try:
            self.logger.info("Initializing CI/CD Dashboard Service...")
            
            # Get CI/CD abstractions from Public Works Foundation
            self._get_cicd_abstractions()
            
            # Setup dashboard data collection
            self._setup_dashboard_data_collection()
            
            self.logger.info("✅ CI/CD Dashboard Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize CI/CD Dashboard Service: {e}")
            raise
    
    def _get_cicd_abstractions(self):
        """Get CI/CD abstractions from Public Works Foundation."""
        try:
            # Get CI/CD abstractions from Public Works Foundation
            self.cicd_monitoring_abstraction = self.public_works_foundation.get_business_abstraction("cicd_monitoring")
            self.deployment_management_abstraction = self.public_works_foundation.get_business_abstraction("deployment_management")
            self.agent_governance_abstraction = self.public_works_foundation.get_business_abstraction("agent_governance")
            
            self.logger.info("✅ CI/CD abstractions retrieved from Public Works Foundation")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get CI/CD abstractions: {e}")
            raise
    
    def _setup_dashboard_data_collection(self):
        """Setup dashboard data collection."""
        self.logger.info("Setting up dashboard data collection...")
        
        # Initialize dashboard data cache
        self.dashboard_data_cache = {
            "domain_health": {},
            "agent_status": {},
            "cicd_pipelines": {},
            "performance_metrics": {},
            "last_updated": None
        }
    
    # ============================================================================
    # DASHBOARD DATA COLLECTION
    # ============================================================================
    
    async def get_overall_platform_health(self) -> Dict[str, Any]:
        """Get overall platform health across all domains."""
        try:
            self.logger.info("Collecting overall platform health...")
            
            # Get domain health from each domain manager
            domain_health_data = await self._collect_domain_health_data()
            
            # Calculate overall health metrics
            overall_health = self._calculate_overall_health(domain_health_data)
            
            # Get agent health data
            agent_health_data = await self._collect_agent_health_data()
            
            # Get CI/CD pipeline health
            cicd_health_data = await self._collect_cicd_health_data()
            
            return {
                "overall_health": overall_health,
                "domain_health": domain_health_data,
                "agent_health": agent_health_data,
                "cicd_health": cicd_health_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get overall platform health: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _collect_domain_health_data(self) -> Dict[str, Any]:
        """Collect domain health data from domain managers."""
        try:
            domain_health = {}
            
            # Get health from each domain manager
            managers = {
                "smart_city": self.city_manager,
                "business_enablement": self.delivery_manager,
                "experience": self.experience_manager,
                "journey": self.journey_manager,
                "agentic": self.agentic_manager
            }
            
            for domain, manager in managers.items():
                if manager:
                    try:
                        # Get domain health using CI/CD monitoring abstraction
                        if self.cicd_monitoring_abstraction:
                            domain_health_result = await self.cicd_monitoring_abstraction.get_domain_pipeline_health(domain)
                            domain_health[domain] = domain_health_result
                        else:
                            # Fallback to direct manager health check
                            domain_health[domain] = await self._get_manager_health_fallback(manager, domain)
                    except Exception as e:
                        self.logger.warning(f"Failed to get health for domain {domain}: {e}")
                        domain_health[domain] = {"status": "unknown", "error": str(e)}
                else:
                    domain_health[domain] = {"status": "unavailable", "message": f"{domain} manager not available"}
            
            return domain_health
            
        except Exception as e:
            self.logger.error(f"Failed to collect domain health data: {e}")
            return {}
    
    async def _get_manager_health_fallback(self, manager, domain: str) -> Dict[str, Any]:
        """Fallback method to get manager health when CI/CD abstractions are not available."""
        try:
            # Try to get health from manager directly
            if hasattr(manager, 'monitor_realm_health'):
                health_result = await manager.monitor_realm_health()
                return {
                    "domain": domain,
                    "status": health_result.get("overall_status", "unknown"),
                    "health_percentage": health_result.get("health_percentage", 0),
                    "services_count": health_result.get("total_services", 0),
                    "healthy_services": health_result.get("healthy_services", 0)
                }
            else:
                return {"domain": domain, "status": "unknown", "message": "Health monitoring not available"}
                
        except Exception as e:
            return {"domain": domain, "status": "error", "error": str(e)}
    
    def _calculate_overall_health(self, domain_health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall health metrics from domain health data."""
        try:
            total_domains = len(domain_health_data)
            healthy_domains = 0
            total_services = 0
            healthy_services = 0
            
            for domain, health_data in domain_health_data.items():
                if health_data.get("status") == "healthy":
                    healthy_domains += 1
                
                total_services += health_data.get("services_count", 0)
                healthy_services += health_data.get("healthy_services", 0)
            
            health_percentage = (healthy_domains / total_domains * 100) if total_domains > 0 else 0
            service_health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 0
            
            return {
                "overall_status": "healthy" if health_percentage >= 80 else "degraded" if health_percentage >= 50 else "unhealthy",
                "health_percentage": health_percentage,
                "service_health_percentage": service_health_percentage,
                "healthy_domains": healthy_domains,
                "total_domains": total_domains,
                "healthy_services": healthy_services,
                "total_services": total_services
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate overall health: {e}")
            return {"overall_status": "error", "error": str(e)}
    
    async def _collect_agent_health_data(self) -> Dict[str, Any]:
        """Collect agent health data."""
        try:
            if not self.agent_governance_abstraction:
                return {"status": "unavailable", "message": "Agent governance abstraction not available"}
            
            # Get overall agent health
            overall_health = await self.agent_governance_abstraction.get_overall_agent_health()
            
            return {
                "overall_agent_health": overall_health,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect agent health data: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _collect_cicd_health_data(self) -> Dict[str, Any]:
        """Collect CI/CD health data."""
        try:
            if not self.cicd_monitoring_abstraction:
                return {"status": "unavailable", "message": "CI/CD monitoring abstraction not available"}
            
            # Get platform deployment summary
            deployment_summary = await self.cicd_monitoring_abstraction.get_platform_deployment_summary()
            
            return {
                "deployment_summary": deployment_summary,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect CI/CD health data: {e}")
            return {"error": str(e), "status": "failed"}
    
    # ============================================================================
    # DOMAIN-SPECIFIC DASHBOARD DATA
    # ============================================================================
    
    async def get_domain_ci_cd_status(self, domain_name: str) -> Dict[str, Any]:
        """Get CI/CD status for a specific domain."""
        try:
            self.logger.info(f"Getting CI/CD status for domain: {domain_name}")
            
            if not self.cicd_monitoring_abstraction:
                return {
                    "domain": domain_name,
                    "status": "unavailable",
                    "message": "CI/CD monitoring abstraction not available"
                }
            
            # Get domain pipeline health
            domain_health = await self.cicd_monitoring_abstraction.get_domain_pipeline_health(domain_name)
            
            # Get domain coupling validation
            coupling_validation = await self.cicd_monitoring_abstraction.validate_domain_coupling(domain_name)
            
            return {
                "domain": domain_name,
                "pipeline_health": domain_health,
                "coupling_validation": coupling_validation,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get CI/CD status for domain {domain_name}: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_agent_performance_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Get performance metrics for a specific agent."""
        try:
            self.logger.info(f"Getting performance metrics for agent: {agent_id}")
            
            if not self.agent_governance_abstraction:
                return {
                    "agent_id": agent_id,
                    "status": "unavailable",
                    "message": "Agent governance abstraction not available"
                }
            
            # Get agent performance metrics
            performance_metrics = await self.agent_governance_abstraction.monitor_agent_performance(agent_id)
            
            return {
                "agent_id": agent_id,
                "performance_metrics": performance_metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics for agent {agent_id}: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_deployment_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get deployment history across the platform."""
        try:
            self.logger.info("Getting deployment history...")
            
            if not self.cicd_monitoring_abstraction:
                return {
                    "status": "unavailable",
                    "message": "CI/CD monitoring abstraction not available",
                    "deployments": []
                }
            
            # Get platform deployment summary
            deployment_summary = await self.cicd_monitoring_abstraction.get_platform_deployment_summary()
            
            return {
                "deployment_summary": deployment_summary,
                "limit": limit,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get deployment history: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_test_suite_summary(self) -> Dict[str, Any]:
        """Get test suite summary across all domains."""
        try:
            self.logger.info("Getting test suite summary...")
            
            # Get test results from each domain
            test_results = {}
            
            managers = {
                "smart_city": self.city_manager,
                "business_enablement": self.delivery_manager,
                "experience": self.experience_manager,
                "journey": self.journey_manager,
                "agentic": self.agentic_manager
            }
            
            for domain, manager in managers.items():
                if manager:
                    try:
                        # Get test results for domain
                        domain_test_results = await self._get_domain_test_results(manager, domain)
                        test_results[domain] = domain_test_results
                    except Exception as e:
                        self.logger.warning(f"Failed to get test results for domain {domain}: {e}")
                        test_results[domain] = {"error": str(e), "status": "failed"}
                else:
                    test_results[domain] = {"status": "unavailable", "message": f"{domain} manager not available"}
            
            # Calculate overall test summary
            overall_summary = self._calculate_test_summary(test_results)
            
            return {
                "overall_summary": overall_summary,
                "domain_results": test_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get test suite summary: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _get_domain_test_results(self, manager, domain: str) -> Dict[str, Any]:
        """Get test results for a specific domain."""
        try:
            # This would integrate with actual test results
            # For now, return mock data
            return {
                "domain": domain,
                "total_tests": 100,
                "passed_tests": 95,
                "failed_tests": 3,
                "skipped_tests": 2,
                "success_rate": 95.0,
                "last_run": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"domain": domain, "error": str(e), "status": "failed"}
    
    def _calculate_test_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall test summary from domain test results."""
        try:
            total_tests = 0
            passed_tests = 0
            failed_tests = 0
            skipped_tests = 0
            
            for domain, results in test_results.items():
                if isinstance(results, dict) and "total_tests" in results:
                    total_tests += results.get("total_tests", 0)
                    passed_tests += results.get("passed_tests", 0)
                    failed_tests += results.get("failed_tests", 0)
                    skipped_tests += results.get("skipped_tests", 0)
            
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": success_rate,
                "overall_status": "healthy" if success_rate >= 90 else "degraded" if success_rate >= 70 else "unhealthy"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate test summary: {e}")
            return {"error": str(e), "status": "failed"}
    
    # ============================================================================
    # DASHBOARD API ENDPOINTS
    # ============================================================================
    
    async def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        try:
            self.logger.info("Getting comprehensive dashboard data...")
            
            # Get all dashboard components
            platform_health = await self.get_overall_platform_health()
            
            # Get test suite summary
            test_summary = await self.get_test_suite_summary()
            
            # Get deployment history
            deployment_history = await self.get_deployment_history()
            
            return {
                "platform_health": platform_health,
                "test_summary": test_summary,
                "deployment_history": deployment_history,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive dashboard: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def get_domain_dashboard(self, domain_name: str) -> Dict[str, Any]:
        """Get domain-specific dashboard data."""
        try:
            self.logger.info(f"Getting dashboard data for domain: {domain_name}")
            
            # Get domain CI/CD status
            cicd_status = await self.get_domain_ci_cd_status(domain_name)
            
            # Get domain health
            domain_health = await self._get_domain_health(domain_name)
            
            return {
                "domain": domain_name,
                "cicd_status": cicd_status,
                "domain_health": domain_health,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get domain dashboard for {domain_name}: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _get_domain_health(self, domain_name: str) -> Dict[str, Any]:
        """Get health data for a specific domain."""
        try:
            managers = {
                "smart_city": self.city_manager,
                "business_enablement": self.delivery_manager,
                "experience": self.experience_manager,
                "journey": self.journey_manager,
                "agentic": self.agentic_manager
            }
            
            manager = managers.get(domain_name)
            if not manager:
                return {"status": "unavailable", "message": f"{domain_name} manager not available"}
            
            # Get health from manager
            if hasattr(manager, 'monitor_realm_health'):
                health_result = await manager.monitor_realm_health()
                return health_result
            else:
                return {"status": "unknown", "message": "Health monitoring not available"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    # ============================================================================
    # DASHBOARD DATA CACHING
    # ============================================================================
    
    async def refresh_dashboard_cache(self) -> Dict[str, Any]:
        """Refresh dashboard data cache."""
        try:
            self.logger.info("Refreshing dashboard data cache...")
            
            # Get fresh dashboard data
            dashboard_data = await self.get_comprehensive_dashboard()
            
            # Update cache
            self.dashboard_data_cache = dashboard_data
            self.dashboard_data_cache["last_updated"] = datetime.utcnow()
            
            self.logger.info("✅ Dashboard data cache refreshed")
            
            return {
                "status": "success",
                "message": "Dashboard data cache refreshed",
                "last_updated": self.dashboard_data_cache["last_updated"].isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to refresh dashboard cache: {e}")
            return {"error": str(e), "status": "failed"}
    
    def get_cached_dashboard_data(self) -> Dict[str, Any]:
        """Get cached dashboard data."""
        return self.dashboard_data_cache
    
    def is_cache_valid(self) -> bool:
        """Check if dashboard cache is valid."""
        if not self.dashboard_data_cache.get("last_updated"):
            return False
        
        cache_age = datetime.utcnow() - self.dashboard_data_cache["last_updated"]
        return cache_age.total_seconds() < self.cache_ttl