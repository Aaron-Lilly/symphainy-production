#!/usr/bin/env python3
"""
Solution Analytics Service

WHAT: Measures solution success across multiple journeys and phases
HOW: Composes Journey Analytics to calculate solution-level metrics

This service provides solution analytics by analyzing performance across
all solution phases and journeys to provide comprehensive solution insights.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class SolutionAnalyticsService(RealmServiceBase):
    """
    Solution Analytics Service for Solution realm.
    
    Measures solution success by composing Journey Analytics Service
    to calculate solution-level metrics across multiple phases.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Solution Analytics Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.data_steward = None
        self.librarian = None
        
        # Journey services (discovered via Curator)
        self.journey_analytics = None
        
        # Solution services (for agent insights)
        self.solution_composer = None
    
    async def initialize(self) -> bool:
        """
        Initialize Solution Analytics Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Phase 2 Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "solution_analytics_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.data_steward = await self.get_data_steward_api()
            self.librarian = await self.get_librarian_api()
            
            # 2. Discover Journey services via Curator
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                try:
                    self.journey_analytics = await curator.get_service("JourneyAnalyticsService")
                    self.logger.info("✅ Discovered JourneyAnalyticsService")
                except Exception:
                    self.logger.warning("⚠️ JourneyAnalyticsService not yet available")
            
            # 3. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "solution_analytics",
                        "protocol": "SolutionAnalyticsProtocol",
                        "description": "Calculate comprehensive solution metrics",
                        "contracts": {
                            "soa_api": {
                                "api_name": "calculate_solution_metrics",
                                "endpoint": "/api/v1/solution/analytics/metrics",
                                "method": "POST",
                                "handler": self.calculate_solution_metrics,
                                "metadata": {
                                    "description": "Calculate comprehensive solution metrics",
                                    "parameters": ["solution_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.calculate_metrics",
                            "semantic_api": "/api/v1/solution/analytics/metrics",
                            "user_journey": "calculate_solution_metrics"
                        }
                    },
                    {
                        "name": "solution_metrics",
                        "protocol": "SolutionAnalyticsProtocol",
                        "description": "Get solution completion rate and duration metrics",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_solution_completion_rate",
                                "endpoint": "/api/v1/solution/analytics/completion-rate",
                                "method": "POST",
                                "handler": self.get_solution_completion_rate,
                                "metadata": {
                                    "description": "Get solution completion rate",
                                    "parameters": ["solution_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.get_completion_rate",
                            "semantic_api": "/api/v1/solution/analytics/completion-rate",
                            "user_journey": "get_solution_completion_rate"
                        }
                    },
                    {
                        "name": "solution_optimization",
                        "protocol": "SolutionAnalyticsProtocol",
                        "description": "Analyze solution performance and get optimization recommendations",
                        "contracts": {
                            "soa_api": {
                                "api_name": "analyze_solution_performance",
                                "endpoint": "/api/v1/solution/analytics/performance",
                                "method": "POST",
                                "handler": self.analyze_solution_performance,
                                "metadata": {
                                    "description": "Analyze overall solution performance",
                                    "parameters": ["solution_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.analyze_performance",
                            "semantic_api": "/api/v1/solution/analytics/performance",
                            "user_journey": "analyze_solution_performance"
                        }
                    },
                    {
                        "name": "solution_comparison",
                        "protocol": "SolutionAnalyticsProtocol",
                        "description": "Compare multiple solutions and get benchmarks",
                        "contracts": {
                            "soa_api": {
                                "api_name": "compare_solutions",
                                "endpoint": "/api/v1/solution/analytics/compare",
                                "method": "POST",
                                "handler": self.compare_solutions,
                                "metadata": {
                                    "description": "Compare multiple solutions",
                                    "parameters": ["solution_ids", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.compare",
                            "semantic_api": "/api/v1/solution/analytics/compare",
                            "user_journey": "compare_solutions"
                        }
                    }
                ],
                soa_apis=[
                    "calculate_solution_metrics", "get_solution_completion_rate",
                    "get_solution_duration", "identify_solution_bottlenecks",
                    "analyze_solution_performance", "get_solution_optimization_recommendations",
                    "compare_solutions", "get_solution_benchmarks",
                    "get_solution_analytics_with_agent_insights"  # Week 8: Dashboard Integration
                ],
                mcp_tools=[]
            )
            
            # Record health metric
            await self.record_health_metric(
                "solution_analytics_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "solution_analytics_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Solution Analytics Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "solution_analytics_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "solution_analytics_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Solution Analytics Service initialization failed: {e}")
            return False
    
    # ========================================================================
    # SOA APIs (Solution Metrics)
    # ========================================================================
    
    async def calculate_solution_metrics(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive solution metrics (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "calculate_solution_metrics_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "calculate_solution_metrics", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "calculate_solution_metrics",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("calculate_solution_metrics_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("calculate_solution_metrics_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "calculate_solution_metrics",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("calculate_solution_metrics_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("calculate_solution_metrics_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get solution deployments
            deployments = await self.search_documents(
                "solution_deployment",
                {"type": "solution_deployment", "solution_id": solution_id}
            )
            
            if not deployments or len(deployments) == 0:
                return {
                    "success": False,
                    "error": "No deployments found for solution"
                }
            
            deployment_data = [r.get("document") if isinstance(r, dict) else r for r in deployments]
            
            # Calculate metrics
            total = len(deployment_data)
            completed = len([d for d in deployment_data if d.get("status") == "completed"])
            deploying = len([d for d in deployment_data if d.get("status") == "deploying"])
            paused = len([d for d in deployment_data if d.get("status") == "paused"])
            cancelled = len([d for d in deployment_data if d.get("status") == "cancelled"])
            
            # Calculate durations
            durations = []
            for deployment in deployment_data:
                if deployment.get("status") == "completed" and "started_at" in deployment and "completed_at" in deployment:
                    start = datetime.fromisoformat(deployment["started_at"])
                    end = datetime.fromisoformat(deployment["completed_at"])
                    durations.append((end - start).total_seconds())
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            metrics = {
                "solution_id": solution_id,
                "total_deployments": total,
                "completed": completed,
                "deploying": deploying,
                "paused": paused,
                "cancelled": cancelled,
                "completion_rate": completed / total if total > 0 else 0,
                "average_duration_seconds": avg_duration,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            result = {
                "success": True,
                "metrics": metrics
            }
            
            # Record health metric (success)
            await self.record_health_metric("calculate_solution_metrics_success", 1.0, {"solution_id": solution_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("calculate_solution_metrics_complete", success=True, details={"solution_id": solution_id})
            
            self.logger.info(f"✅ Solution metrics calculated: {solution_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "calculate_solution_metrics", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("calculate_solution_metrics_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("calculate_solution_metrics_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Calculate solution metrics failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_solution_completion_rate(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get solution completion rate (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_completion_rate_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_completion_rate", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_completion_rate",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_solution_completion_rate_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_solution_completion_rate_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_solution_completion_rate",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("get_solution_completion_rate_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_solution_completion_rate_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            metrics_result = await self.calculate_solution_metrics(solution_id, user_context=user_context)
            if metrics_result.get("success"):
                metrics = metrics_result["metrics"]
                result = {
                    "success": True,
                    "solution_id": solution_id,
                    "completion_rate": metrics["completion_rate"],
                    "completed": metrics["completed"],
                    "total_deployments": metrics["total_deployments"]
                }
                
                # Record health metric (success)
                await self.record_health_metric("get_solution_completion_rate_success", 1.0, {"solution_id": solution_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_solution_completion_rate_complete", success=True, details={"solution_id": solution_id})
                
                return result
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_completion_rate_complete", success=False, details={"error": metrics_result.get("error")})
            
            return metrics_result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_completion_rate", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_completion_rate_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_completion_rate_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_solution_duration(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get average solution duration (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_duration_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_duration", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_duration",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_solution_duration_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_solution_duration_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_solution_duration",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("get_solution_duration_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_solution_duration_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            metrics_result = await self.calculate_solution_metrics(solution_id, user_context=user_context)
            if metrics_result.get("success"):
                metrics = metrics_result["metrics"]
                result = {
                    "success": True,
                    "solution_id": solution_id,
                    "average_duration_seconds": metrics["average_duration_seconds"],
                    "average_duration_hours": metrics["average_duration_seconds"] / 3600
                }
                
                # Record health metric (success)
                await self.record_health_metric("get_solution_duration_success", 1.0, {"solution_id": solution_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_solution_duration_complete", success=True, details={"solution_id": solution_id})
                
                return result
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_duration_complete", success=False, details={"error": metrics_result.get("error")})
            
            return metrics_result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_duration", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_duration_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_duration_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def identify_solution_bottlenecks(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Identify solution bottlenecks (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "identify_solution_bottlenecks_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "identify_solution_bottlenecks", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "identify_solution_bottlenecks",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("identify_solution_bottlenecks_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("identify_solution_bottlenecks_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "identify_solution_bottlenecks",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("identify_solution_bottlenecks_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("identify_solution_bottlenecks_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get deployments
            deployments = await self.search_documents(
                "solution_deployment",
                {"type": "solution_deployment", "solution_id": solution_id}
            )
            
            if not deployments or len(deployments) == 0:
                return {
                    "success": False,
                    "error": "No deployments found"
                }
            
            deployment_data = [r.get("document") if isinstance(r, dict) else r for r in deployments]
            
            # Analyze phase durations
            phase_durations: Dict[str, List[float]] = {}
            
            for deployment in deployment_data:
                for phase_id, result in deployment.get("phase_results", {}).items():
                    if "duration" in result:
                        if phase_id not in phase_durations:
                            phase_durations[phase_id] = []
                        phase_durations[phase_id].append(result["duration"])
            
            # Identify bottlenecks (phases with longest avg duration)
            bottlenecks = []
            for phase_id, durations in phase_durations.items():
                avg = sum(durations) / len(durations)
                bottlenecks.append({
                    "phase_id": phase_id,
                    "average_duration": avg,
                    "executions": len(durations)
                })
            
            # Sort by duration
            bottlenecks.sort(key=lambda x: x["average_duration"], reverse=True)
            
            result = {
                "success": True,
                "solution_id": solution_id,
                "bottlenecks": bottlenecks[:3]  # Top 3
            }
            
            # Record health metric (success)
            await self.record_health_metric("identify_solution_bottlenecks_success", 1.0, {"solution_id": solution_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("identify_solution_bottlenecks_complete", success=True, details={"solution_id": solution_id})
            
            self.logger.info(f"✅ Solution bottlenecks identified: {solution_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "identify_solution_bottlenecks", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("identify_solution_bottlenecks_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("identify_solution_bottlenecks_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Identify solution bottlenecks failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_solution_performance(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze overall solution performance (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "analyze_solution_performance_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "analyze_solution_performance", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "analyze_solution_performance",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("analyze_solution_performance_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("analyze_solution_performance_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "analyze_solution_performance",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("analyze_solution_performance_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("analyze_solution_performance_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get metrics
            metrics_result = await self.calculate_solution_metrics(solution_id, user_context=user_context)
            if not metrics_result.get("success"):
                return metrics_result
            
            metrics = metrics_result["metrics"]
            
            # Get bottlenecks
            bottlenecks_result = await self.identify_solution_bottlenecks(solution_id, user_context=user_context)
            bottlenecks = bottlenecks_result.get("bottlenecks", []) if bottlenecks_result.get("success") else []
            
            # Calculate performance score
            performance_score = 0
            issues = []
            
            # Completion rate
            if metrics["completion_rate"] >= 0.8:
                performance_score += 40
            elif metrics["completion_rate"] >= 0.6:
                performance_score += 20
                issues.append("Completion rate below 80%")
            else:
                issues.append("Low completion rate (< 60%)")
            
            # Duration
            if metrics["average_duration_seconds"] < 86400:  # < 1 day
                performance_score += 30
            elif metrics["average_duration_seconds"] < 259200:  # < 3 days
                performance_score += 15
                issues.append("Solution duration above 1 day")
            else:
                issues.append("Long solution duration (> 3 days)")
            
            # Bottlenecks
            if len(bottlenecks) == 0:
                performance_score += 30
            elif len(bottlenecks) <= 2:
                performance_score += 15
                issues.append(f"{len(bottlenecks)} bottlenecks identified")
            else:
                issues.append(f"Multiple bottlenecks ({len(bottlenecks)})")
            
            analysis = {
                "solution_id": solution_id,
                "performance_score": performance_score,
                "performance_grade": self._get_grade(performance_score),
                "metrics": metrics,
                "bottlenecks": bottlenecks,
                "issues": issues,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            result = {
                "success": True,
                "analysis": analysis
            }
            
            # Record health metric (success)
            await self.record_health_metric("analyze_solution_performance_success", 1.0, {"solution_id": solution_id, "score": performance_score})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("analyze_solution_performance_complete", success=True, details={"solution_id": solution_id, "score": performance_score})
            
            self.logger.info(f"✅ Solution performance analyzed: {solution_id} (score: {performance_score})")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "analyze_solution_performance", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("analyze_solution_performance_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("analyze_solution_performance_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Analyze solution performance failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_grade(self, score: int) -> str:
        """Get performance grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    async def get_solution_optimization_recommendations(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get solution optimization recommendations (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_optimization_recommendations_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_optimization_recommendations", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_optimization_recommendations",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_solution_optimization_recommendations_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_solution_optimization_recommendations_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_solution_optimization_recommendations",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("get_solution_optimization_recommendations_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_solution_optimization_recommendations_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get performance analysis
            analysis_result = await self.analyze_solution_performance(solution_id, user_context=user_context)
            if not analysis_result.get("success"):
                return analysis_result
            
            analysis = analysis_result["analysis"]
            
            # Generate recommendations
            recommendations = []
            
            if analysis["metrics"]["completion_rate"] < 0.8:
                recommendations.append({
                    "priority": "high",
                    "category": "completion",
                    "recommendation": "Simplify solution phases or improve documentation",
                    "rationale": f"Completion rate is {analysis['metrics']['completion_rate']:.1%}"
                })
            
            if analysis["bottlenecks"]:
                top_bottleneck = analysis["bottlenecks"][0]
                recommendations.append({
                    "priority": "high",
                    "category": "performance",
                    "recommendation": f"Optimize phase: {top_bottleneck['phase_id']}",
                    "rationale": f"Phase takes {top_bottleneck['average_duration']:.1f}s on average"
                })
            
            result = {
                "success": True,
                "solution_id": solution_id,
                "recommendations": recommendations,
                "performance_score": analysis["performance_score"]
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_solution_optimization_recommendations_success", 1.0, {"solution_id": solution_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_solution_optimization_recommendations_complete", success=True, details={"solution_id": solution_id})
            
            self.logger.info(f"✅ Solution optimization recommendations generated: {solution_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_optimization_recommendations", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_optimization_recommendations_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_optimization_recommendations_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get solution optimization recommendations failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def compare_solutions(
        self,
        solution_ids: List[str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple solutions (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "compare_solutions_start",
            success=True,
            details={"solution_count": len(solution_ids)}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "compare_solutions", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "compare_solutions",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("compare_solutions_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("compare_solutions_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "compare_solutions",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("compare_solutions_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("compare_solutions_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            comparisons = []
            
            for solution_id in solution_ids:
                metrics_result = await self.calculate_solution_metrics(solution_id, user_context=user_context)
                if metrics_result.get("success"):
                    comparisons.append({
                        "solution_id": solution_id,
                        "metrics": metrics_result["metrics"]
                    })
            
            if comparisons:
                best = max(comparisons, key=lambda x: x["metrics"]["completion_rate"])
                worst = min(comparisons, key=lambda x: x["metrics"]["completion_rate"])
            else:
                best = worst = None
            
            result = {
                "success": True,
                "comparisons": comparisons,
                "best_performing": best,
                "worst_performing": worst
            }
            
            # Record health metric (success)
            await self.record_health_metric("compare_solutions_success", 1.0, {"solution_count": len(solution_ids)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("compare_solutions_complete", success=True, details={"solution_count": len(solution_ids)})
            
            self.logger.info(f"✅ Solutions compared: {len(solution_ids)}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "compare_solutions", details={"solution_ids": solution_ids})
            
            # Record health metric (failure)
            await self.record_health_metric("compare_solutions_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("compare_solutions_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Compare solutions failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_solution_benchmarks(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get solution benchmarks (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_benchmarks_start",
            success=True
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_benchmarks", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_benchmarks",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_solution_benchmarks_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_solution_benchmarks_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            tenant = self.get_tenant()
            if tenant_id and tenant:
                try:
                    import inspect
                    is_configured = hasattr(tenant, 'multi_tenant_enabled') and tenant.multi_tenant_enabled
                    if is_configured:
                        if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                            is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                        else:
                            is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                        if not is_valid:
                            await self.handle_error_with_audit(
                                ValueError("Tenant access denied"),
                                "get_solution_benchmarks",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("get_solution_benchmarks_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_solution_benchmarks_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get all deployments
            deployments = await self.search_documents(
                "solution_deployment",
                {"type": "solution_deployment"}
            )
            
            if not deployments or len(deployments) == 0:
                return {
                    "success": True,
                    "benchmarks": {
                        "average_completion_rate": 0,
                        "average_duration_seconds": 0,
                        "total_solutions": 0
                    }
                }
            
            deployment_data = [r.get("document") if isinstance(r, dict) else r for r in deployments]
            
            completed = len([d for d in deployment_data if d.get("status") == "completed"])
            total = len(deployment_data)
            
            durations = []
            for deployment in deployment_data:
                if deployment.get("status") == "completed" and "started_at" in deployment and "completed_at" in deployment:
                    start = datetime.fromisoformat(deployment["started_at"])
                    end = datetime.fromisoformat(deployment["completed_at"])
                    durations.append((end - start).total_seconds())
            
            benchmarks = {
                "average_completion_rate": completed / total if total > 0 else 0,
                "average_duration_seconds": sum(durations) / len(durations) if durations else 0,
                "total_solutions": total,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            result = {
                "success": True,
                "benchmarks": benchmarks
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_solution_benchmarks_success", 1.0, {"total_solutions": benchmarks.get("total_solutions", 0)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_solution_benchmarks_complete", success=True, details={"total_solutions": benchmarks.get("total_solutions", 0)})
            
            self.logger.info("✅ Solution benchmarks calculated")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_benchmarks")
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_benchmarks_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_benchmarks_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get solution benchmarks failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # AGENT INSIGHTS EXTENSION (Week 8: Dashboard Integration)
    # ========================================================================
    
    async def get_solution_analytics_with_agent_insights(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get solution analytics enhanced with agent insights (SOA API).
        
        Extends standard analytics with:
        - Agent recommendations (from CoexistenceStrategySpecialist)
        - Agent performance insights
        - Agent-driven optimizations
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_solution_analytics_with_agent_insights_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_solution_analytics_with_agent_insights", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_solution_analytics_with_agent_insights",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_solution_analytics_with_agent_insights_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_solution_analytics_with_agent_insights_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get standard analytics
            metrics_result = await self.calculate_solution_metrics(solution_id, user_context=user_context)
            performance_result = await self.analyze_solution_performance(solution_id, user_context=user_context)
            recommendations_result = await self.get_solution_optimization_recommendations(solution_id, user_context=user_context)
            
            # Get agent insights from Solution Composer
            agent_insights = {
                "coexistence_strategy": None,
                "agent_recommendations": [],
                "agent_alerts": []
            }
            
            if self.solution_composer:
                try:
                    # Get solution status to check for agent insights
                    solution_status = await self.solution_composer.get_solution_status(solution_id, user_context=user_context)
                    
                    if solution_status.get("success"):
                        solution_data = solution_status.get("solution", {})
                        
                        # Check if solution has agent insights stored
                        if "agent_insights" in solution_data:
                            agent_insights["coexistence_strategy"] = solution_data["agent_insights"].get("coexistence_strategy")
                        
                        # Get agent recommendations if available
                        if hasattr(self.solution_composer, '_coexistence_strategy_agent'):
                            coexistence_agent = await self.solution_composer._get_coexistence_strategy_agent()
                            if coexistence_agent:
                                # Agent insights would be stored during solution design
                                # For now, we'll extract from solution metadata
                                if "agent_recommendations" in solution_data:
                                    agent_insights["agent_recommendations"] = solution_data["agent_recommendations"]
                                
                                if "agent_alerts" in solution_data:
                                    agent_insights["agent_alerts"] = solution_data["agent_alerts"]
                except Exception as e:
                    self.logger.debug(f"Could not retrieve agent insights: {e}")
            
            # Combine analytics with agent insights
            result = {
                "success": True,
                "solution_id": solution_id,
                "analytics": {
                    "metrics": metrics_result.get("metrics", {}) if metrics_result.get("success") else {},
                    "performance": performance_result.get("analysis", {}) if performance_result.get("success") else {},
                    "recommendations": recommendations_result.get("recommendations", []) if recommendations_result.get("success") else []
                },
                "agent_insights": agent_insights,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_solution_analytics_with_agent_insights_success", 1.0, {"solution_id": solution_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_solution_analytics_with_agent_insights_complete", success=True, details={"solution_id": solution_id})
            
            self.logger.info(f"✅ Solution analytics with agent insights retrieved: {solution_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_solution_analytics_with_agent_insights", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_solution_analytics_with_agent_insights_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_solution_analytics_with_agent_insights_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get solution analytics with agent insights failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "journey_analytics_available": self.journey_analytics is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "solution_service",
            "realm": "solution",
            "layer": "solution_analytics",
            "capabilities": ["solution_analytics", "solution_metrics", "solution_optimization", "solution_comparison"],
            "soa_apis": [
                "calculate_solution_metrics", "get_solution_completion_rate",
                "get_solution_duration", "identify_solution_bottlenecks",
                "analyze_solution_performance", "get_solution_optimization_recommendations",
                "compare_solutions", "get_solution_benchmarks",
                "get_solution_analytics_with_agent_insights"  # Week 8: Dashboard Integration
            ],
            "mcp_tools": [],
            "composes": "journey_analytics"
        }








