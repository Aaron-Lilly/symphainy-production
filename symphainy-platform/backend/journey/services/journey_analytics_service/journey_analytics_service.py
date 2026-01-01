#!/usr/bin/env python3
"""
Journey Analytics Service

WHAT: Measures journey success, analyzes user behavior, and optimizes journey performance
HOW: Composes Experience analytics and Smart City services to calculate journey metrics

This service provides journey analytics by analyzing user behavior patterns,
completion rates, and performance metrics across journeys.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class JourneyAnalyticsService(RealmServiceBase):
    """
    Journey Analytics Service for Journey realm.
    
    Measures journey success and analyzes user behavior by composing
    Experience service analytics and Smart City data processing.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Journey Analytics Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.data_steward = None
        self.librarian = None
        self.nurse = None
        
        # Experience services (discovered via Curator)
        self.user_experience = None
        self.session_manager = None
    
    async def initialize(self) -> bool:
        """
        Initialize Journey Analytics Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "journey_analytics_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.data_steward = await self.get_data_steward_api()
            self.librarian = await self.get_librarian_api()
            self.nurse = await self.get_nurse_api()
            
            # 2. Discover Experience services via Curator
            await self._discover_experience_services()
            
            # 3. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "journey_analytics",
                        "protocol": "JourneyAnalyticsProtocol",
                        "description": "Calculate comprehensive journey metrics",
                        "contracts": {
                            "soa_api": {
                                "api_name": "calculate_journey_metrics",
                                "endpoint": "/api/v1/journey/analytics/metrics",
                                "method": "POST",
                                "handler": self.calculate_journey_metrics,
                                "metadata": {
                                    "description": "Calculate comprehensive journey metrics",
                                    "parameters": ["journey_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.calculate_metrics",
                            "semantic_api": "/api/v1/journey/analytics/metrics",
                            "user_journey": "calculate_journey_metrics"
                        }
                    },
                    {
                        "name": "journey_metrics",
                        "protocol": "JourneyAnalyticsProtocol",
                        "description": "Get journey completion rate and duration metrics",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_completion_rate",
                                "endpoint": "/api/v1/journey/analytics/completion-rate",
                                "method": "POST",
                                "handler": self.get_completion_rate,
                                "metadata": {
                                    "description": "Get journey completion rate",
                                    "parameters": ["journey_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.get_completion_rate",
                            "semantic_api": "/api/v1/journey/analytics/completion-rate",
                            "user_journey": "get_completion_rate"
                        }
                    },
                    {
                        "name": "journey_duration_metrics",
                        "protocol": "JourneyAnalyticsProtocol",
                        "description": "Get average journey duration",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_average_duration",
                                "endpoint": "/api/v1/journey/analytics/average-duration",
                                "method": "POST",
                                "handler": self.get_average_duration,
                                "metadata": {
                                    "description": "Get average journey duration",
                                    "parameters": ["journey_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.get_average_duration",
                            "semantic_api": "/api/v1/journey/analytics/average-duration",
                            "user_journey": "get_average_duration"
                        }
                    },
                    {
                        "name": "journey_drop_off_analysis",
                        "protocol": "JourneyAnalyticsProtocol",
                        "description": "Identify where users drop off in journey",
                        "contracts": {
                            "soa_api": {
                                "api_name": "identify_drop_off_points",
                                "endpoint": "/api/v1/journey/analytics/drop-off-points",
                                "method": "POST",
                                "handler": self.identify_drop_off_points,
                                "metadata": {
                                    "description": "Identify where users drop off in journey",
                                    "parameters": ["journey_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.identify_drop_off_points",
                            "semantic_api": "/api/v1/journey/analytics/drop-off-points",
                            "user_journey": "identify_drop_off_points"
                        }
                    },
                    {
                        "name": "journey_optimization",
                        "protocol": "JourneyAnalyticsProtocol",
                        "description": "Analyze journey performance and get optimization recommendations",
                        "contracts": {
                            "soa_api": {
                                "api_name": "analyze_journey_performance",
                                "endpoint": "/api/v1/journey/analytics/performance",
                                "method": "POST",
                                "handler": self.analyze_journey_performance,
                                "metadata": {
                                    "description": "Analyze overall journey performance",
                                    "parameters": ["journey_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.analyze_performance",
                            "semantic_api": "/api/v1/journey/analytics/performance",
                            "user_journey": "analyze_journey_performance"
                        }
                    },
                    {
                        "name": "journey_optimization_recommendations",
                        "protocol": "JourneyAnalyticsProtocol",
                        "description": "Get journey optimization recommendations",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_optimization_recommendations",
                                "endpoint": "/api/v1/journey/analytics/optimization-recommendations",
                                "method": "POST",
                                "handler": self.get_optimization_recommendations,
                                "metadata": {
                                    "description": "Get journey optimization recommendations",
                                    "parameters": ["journey_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.get_optimization_recommendations",
                            "semantic_api": "/api/v1/journey/analytics/optimization-recommendations",
                            "user_journey": "get_optimization_recommendations"
                        }
                    },
                    {
                        "name": "journey_comparison",
                        "protocol": "JourneyAnalyticsProtocol",
                        "description": "Compare multiple journeys and get benchmarks",
                        "contracts": {
                            "soa_api": {
                                "api_name": "compare_journeys",
                                "endpoint": "/api/v1/journey/analytics/compare",
                                "method": "POST",
                                "handler": self.compare_journeys,
                                "metadata": {
                                    "description": "Compare multiple journeys",
                                    "parameters": ["journey_ids", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.compare",
                            "semantic_api": "/api/v1/journey/analytics/compare",
                            "user_journey": "compare_journeys"
                        }
                    },
                    {
                        "name": "journey_benchmarks",
                        "protocol": "JourneyAnalyticsProtocol",
                        "description": "Get journey benchmarks",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_journey_benchmarks",
                                "endpoint": "/api/v1/journey/analytics/benchmarks",
                                "method": "GET",
                                "handler": self.get_journey_benchmarks,
                                "metadata": {
                                    "description": "Get journey benchmarks",
                                    "parameters": ["user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.get_benchmarks",
                            "semantic_api": "/api/v1/journey/analytics/benchmarks",
                            "user_journey": "get_journey_benchmarks"
                        }
                    }
                ],
                soa_apis=[
                    "calculate_journey_metrics", "get_completion_rate", "get_average_duration",
                    "identify_drop_off_points", "analyze_journey_performance",
                    "get_optimization_recommendations", "compare_journeys", "get_journey_benchmarks"
                ],
                mcp_tools=[]  # Journey services provide SOA APIs, not MCP tools
            )
            
            # Record health metric
            await self.record_health_metric(
                "journey_analytics_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "journey_analytics_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Journey Analytics Service initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "journey_analytics_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "journey_analytics_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Journey Analytics Service initialization failed: {e}")
            return False
    
    async def _discover_experience_services(self):
        """Discover Experience services via Curator."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            
            if curator:
                try:
                    self.user_experience = await curator.discover_service_by_name("UserExperienceService")
                    self.logger.info("✅ Discovered UserExperienceService")
                except Exception:
                    self.logger.warning("⚠️ UserExperienceService not yet available")
                
                try:
                    self.session_manager = await curator.discover_service_by_name("SessionManagerService")
                    self.logger.info("✅ Discovered SessionManagerService")
                except Exception:
                    self.logger.warning("⚠️ SessionManagerService not yet available")
            
        except Exception as e:
            self.logger.error(f"❌ Experience service discovery failed: {e}")
    
    # ========================================================================
    # SOA APIs (Journey Metrics)
    # ========================================================================
    
    async def calculate_journey_metrics(
        self,
        journey_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive journey metrics (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_context: User context for security and tenant validation
        
        Returns:
            Journey metrics
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "calculate_journey_metrics_start",
            success=True,
            details={"journey_id": journey_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "calculate_journey_metrics", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "calculate_journey_metrics",
                    details={"user_id": user_context.get("user_id"), "journey_id": journey_id}
                )
                await self.record_health_metric("calculate_journey_metrics_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("calculate_journey_metrics_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "calculate_journey_metrics",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("calculate_journey_metrics_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("calculate_journey_metrics_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get all journey executions
            executions = await self.search_documents(
                "journey_execution",
                {"type": "journey_execution", "journey_id": journey_id}
            )
            
            if not executions or len(executions) == 0:
                await self.record_health_metric("calculate_journey_metrics_no_executions", 1.0, {"journey_id": journey_id})
                await self.log_operation_with_telemetry("calculate_journey_metrics_complete", success=False, details={"journey_id": journey_id})
                return {
                    "success": False,
                    "error": "No executions found for journey"
                }
            
            execution_data = [r.get("document") if isinstance(r, dict) else r for r in executions]
            
            # Calculate metrics
            total_executions = len(execution_data)
            completed = len([e for e in execution_data if e.get("status") == "completed"])
            in_progress = len([e for e in execution_data if e.get("status") == "in_progress"])
            cancelled = len([e for e in execution_data if e.get("status") == "cancelled"])
            
            # Calculate durations for completed journeys
            durations = []
            for execution in execution_data:
                if execution.get("status") == "completed" and "started_at" in execution and "completed_at" in execution:
                    start = datetime.fromisoformat(execution["started_at"])
                    end = datetime.fromisoformat(execution["completed_at"])
                    duration = (end - start).total_seconds()
                    durations.append(duration)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            metrics = {
                "journey_id": journey_id,
                "total_executions": total_executions,
                "completed": completed,
                "in_progress": in_progress,
                "cancelled": cancelled,
                "completion_rate": completed / total_executions if total_executions > 0 else 0,
                "average_duration_seconds": avg_duration,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("calculate_journey_metrics_success", 1.0, {"journey_id": journey_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("calculate_journey_metrics_complete", success=True, details={"journey_id": journey_id})
            
            self.logger.info(f"✅ Journey metrics calculated: {journey_id}")
            
            return {
                "success": True,
                "metrics": metrics
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "calculate_journey_metrics", details={"journey_id": journey_id})
            
            # Record health metric (failure)
            await self.record_health_metric("calculate_journey_metrics_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("calculate_journey_metrics_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Calculate journey metrics failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_completion_rate(
        self,
        journey_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get journey completion rate (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_context: User context for security and tenant validation
        
        Returns:
            Completion rate
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_completion_rate_start",
            success=True,
            details={"journey_id": journey_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_completion_rate", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_completion_rate",
                    details={"user_id": user_context.get("user_id"), "journey_id": journey_id}
                )
                await self.record_health_metric("get_completion_rate_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_completion_rate_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_completion_rate",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_completion_rate_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_completion_rate_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            metrics_result = await self.calculate_journey_metrics(journey_id, user_context=user_context)
            
            if metrics_result.get("success"):
                metrics = metrics_result["metrics"]
                
                # Record health metric (success)
                await self.record_health_metric("get_completion_rate_success", 1.0, {"journey_id": journey_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_completion_rate_complete", success=True, details={"journey_id": journey_id})
                
                return {
                    "success": True,
                    "journey_id": journey_id,
                    "completion_rate": metrics["completion_rate"],
                    "completed": metrics["completed"],
                    "total_executions": metrics["total_executions"]
                }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_completion_rate_complete", success=False, details={"journey_id": journey_id})
            return metrics_result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_completion_rate", details={"journey_id": journey_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_completion_rate_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_completion_rate_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Get completion rate failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_average_duration(
        self,
        journey_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get average journey duration (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_context: User context for security and tenant validation
        
        Returns:
            Average duration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_average_duration_start",
            success=True,
            details={"journey_id": journey_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_average_duration", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_average_duration",
                    details={"user_id": user_context.get("user_id"), "journey_id": journey_id}
                )
                await self.record_health_metric("get_average_duration_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_average_duration_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_average_duration",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_average_duration_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_average_duration_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            metrics_result = await self.calculate_journey_metrics(journey_id, user_context=user_context)
            
            if metrics_result.get("success"):
                metrics = metrics_result["metrics"]
                
                # Record health metric (success)
                await self.record_health_metric("get_average_duration_success", 1.0, {"journey_id": journey_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_average_duration_complete", success=True, details={"journey_id": journey_id})
                
                return {
                    "success": True,
                    "journey_id": journey_id,
                    "average_duration_seconds": metrics["average_duration_seconds"],
                    "average_duration_minutes": metrics["average_duration_seconds"] / 60
                }
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_average_duration_complete", success=False, details={"journey_id": journey_id})
            return metrics_result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_average_duration", details={"journey_id": journey_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_average_duration_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_average_duration_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Get average duration failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def identify_drop_off_points(
        self,
        journey_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Identify where users drop off in journey (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_context: User context for security and tenant validation
        
        Returns:
            Drop-off analysis
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "identify_drop_off_points_start",
            success=True,
            details={"journey_id": journey_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "identify_drop_off_points", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "identify_drop_off_points",
                    details={"user_id": user_context.get("user_id"), "journey_id": journey_id}
                )
                await self.record_health_metric("identify_drop_off_points_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("identify_drop_off_points_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "identify_drop_off_points",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("identify_drop_off_points_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("identify_drop_off_points_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get all journey executions
            executions = await self.search_documents(
                "journey_execution",
                {"type": "journey_execution", "journey_id": journey_id}
            )
            
            if not executions or len(executions) == 0:
                await self.record_health_metric("identify_drop_off_points_no_executions", 1.0, {"journey_id": journey_id})
                await self.log_operation_with_telemetry("identify_drop_off_points_complete", success=False, details={"journey_id": journey_id})
                return {
                    "success": False,
                    "error": "No executions found for journey"
                }
            
            execution_data = [r.get("document") if isinstance(r, dict) else r for r in executions]
            
            # Analyze drop-off points
            milestone_drop_offs: Dict[str, int] = {}
            
            for execution in execution_data:
                if execution.get("status") in ["cancelled", "paused"]:
                    current_milestone = execution.get("current_milestone")
                    if current_milestone:
                        milestone_drop_offs[current_milestone] = milestone_drop_offs.get(current_milestone, 0) + 1
            
            # Sort by drop-off count
            sorted_drop_offs = sorted(
                milestone_drop_offs.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            drop_offs = [
                {
                    "milestone_id": milestone_id,
                    "drop_off_count": count,
                    "drop_off_rate": count / len(execution_data)
                }
                for milestone_id, count in sorted_drop_offs
            ]
            
            # Record health metric (success)
            await self.record_health_metric("identify_drop_off_points_success", 1.0, {"journey_id": journey_id, "drop_off_count": len(drop_offs)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("identify_drop_off_points_complete", success=True, details={"journey_id": journey_id})
            
            self.logger.info(f"✅ Drop-off points identified: {journey_id}")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "drop_off_points": drop_offs,
                "total_drop_offs": sum(milestone_drop_offs.values())
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "identify_drop_off_points", details={"journey_id": journey_id})
            
            # Record health metric (failure)
            await self.record_health_metric("identify_drop_off_points_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("identify_drop_off_points_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Identify drop-off points failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Journey Optimization)
    # ========================================================================
    
    async def analyze_journey_performance(
        self,
        journey_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze overall journey performance (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_context: User context for security and tenant validation
        
        Returns:
            Performance analysis
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "analyze_journey_performance_start",
            success=True,
            details={"journey_id": journey_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "analyze_journey_performance", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "analyze_journey_performance",
                    details={"user_id": user_context.get("user_id"), "journey_id": journey_id}
                )
                await self.record_health_metric("analyze_journey_performance_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("analyze_journey_performance_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "analyze_journey_performance",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("analyze_journey_performance_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("analyze_journey_performance_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get metrics
            metrics_result = await self.calculate_journey_metrics(journey_id, user_context=user_context)
            if not metrics_result.get("success"):
                await self.log_operation_with_telemetry("analyze_journey_performance_complete", success=False, details={"journey_id": journey_id})
                return metrics_result
            
            metrics = metrics_result["metrics"]
            
            # Get drop-off points
            drop_offs_result = await self.identify_drop_off_points(journey_id, user_context=user_context)
            drop_offs = drop_offs_result.get("drop_off_points", []) if drop_offs_result.get("success") else []
            
            # Analyze performance
            performance_score = 0
            issues = []
            
            # Completion rate analysis
            if metrics["completion_rate"] >= 0.8:
                performance_score += 40
            elif metrics["completion_rate"] >= 0.6:
                performance_score += 20
                issues.append("Completion rate below 80%")
            else:
                issues.append("Low completion rate (< 60%)")
            
            # Duration analysis
            if metrics["average_duration_seconds"] < 600:  # < 10 minutes
                performance_score += 30
            elif metrics["average_duration_seconds"] < 1800:  # < 30 minutes
                performance_score += 15
                issues.append("Journey duration above 10 minutes")
            else:
                issues.append("Long journey duration (> 30 minutes)")
            
            # Drop-off analysis
            if len(drop_offs) == 0:
                performance_score += 30
            elif len(drop_offs) <= 2:
                performance_score += 15
                issues.append(f"{len(drop_offs)} drop-off points identified")
            else:
                issues.append(f"Multiple drop-off points ({len(drop_offs)})")
            
            analysis = {
                "journey_id": journey_id,
                "performance_score": performance_score,
                "performance_grade": self._get_performance_grade(performance_score),
                "metrics": metrics,
                "drop_off_points": drop_offs[:3],  # Top 3
                "issues": issues,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("analyze_journey_performance_success", 1.0, {"journey_id": journey_id, "performance_score": performance_score})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("analyze_journey_performance_complete", success=True, details={"journey_id": journey_id, "performance_score": performance_score})
            
            self.logger.info(f"✅ Journey performance analyzed: {journey_id} (score: {performance_score})")
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "analyze_journey_performance", details={"journey_id": journey_id})
            
            # Record health metric (failure)
            await self.record_health_metric("analyze_journey_performance_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("analyze_journey_performance_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Analyze journey performance failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_performance_grade(self, score: int) -> str:
        """Get performance grade from score."""
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
    
    async def get_optimization_recommendations(
        self,
        journey_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get journey optimization recommendations (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_id: Journey ID
            user_context: User context for security and tenant validation
        
        Returns:
            Optimization recommendations
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_optimization_recommendations_start",
            success=True,
            details={"journey_id": journey_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_optimization_recommendations", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_optimization_recommendations",
                    details={"user_id": user_context.get("user_id"), "journey_id": journey_id}
                )
                await self.record_health_metric("get_optimization_recommendations_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_optimization_recommendations_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_optimization_recommendations",
                    details={"tenant_id": tenant_id, "journey_id": journey_id}
                )
                await self.record_health_metric("get_optimization_recommendations_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_optimization_recommendations_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get performance analysis
            analysis_result = await self.analyze_journey_performance(journey_id, user_context=user_context)
            if not analysis_result.get("success"):
                await self.log_operation_with_telemetry("get_optimization_recommendations_complete", success=False, details={"journey_id": journey_id})
                return analysis_result
            
            analysis = analysis_result["analysis"]
            
            # Generate recommendations
            recommendations = []
            
            # Completion rate recommendations
            if analysis["metrics"]["completion_rate"] < 0.8:
                recommendations.append({
                    "priority": "high",
                    "category": "completion",
                    "recommendation": "Simplify journey steps or add guidance",
                    "rationale": f"Completion rate is {analysis['metrics']['completion_rate']:.1%}"
                })
            
            # Duration recommendations
            if analysis["metrics"]["average_duration_seconds"] > 1800:
                recommendations.append({
                    "priority": "medium",
                    "category": "performance",
                    "recommendation": "Optimize slow milestones or enable parallel processing",
                    "rationale": f"Average duration is {analysis['metrics']['average_duration_seconds'] / 60:.1f} minutes"
                })
            
            # Drop-off recommendations
            if analysis["drop_off_points"]:
                top_drop_off = analysis["drop_off_points"][0]
                recommendations.append({
                    "priority": "high",
                    "category": "engagement",
                    "recommendation": f"Improve milestone: {top_drop_off['milestone_id']}",
                    "rationale": f"{top_drop_off['drop_off_rate']:.1%} of users drop off at this step"
                })
            
            # Record health metric (success)
            await self.record_health_metric("get_optimization_recommendations_success", 1.0, {"journey_id": journey_id, "recommendation_count": len(recommendations)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_optimization_recommendations_complete", success=True, details={"journey_id": journey_id, "recommendation_count": len(recommendations)})
            
            self.logger.info(f"✅ Optimization recommendations generated: {journey_id}")
            
            return {
                "success": True,
                "journey_id": journey_id,
                "recommendations": recommendations,
                "performance_score": analysis["performance_score"]
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_optimization_recommendations", details={"journey_id": journey_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_optimization_recommendations_failed", 1.0, {"journey_id": journey_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_optimization_recommendations_complete", success=False, details={"journey_id": journey_id, "error": str(e)})
            
            self.logger.error(f"❌ Get optimization recommendations failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # SOA APIs (Journey Comparison)
    # ========================================================================
    
    async def compare_journeys(
        self,
        journey_ids: List[str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple journeys (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            journey_ids: List of journey IDs to compare
            user_context: User context for security and tenant validation
        
        Returns:
            Comparison results
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "compare_journeys_start",
            success=True,
            details={"journey_count": len(journey_ids)}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "compare_journeys", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "compare_journeys",
                    details={"user_id": user_context.get("user_id"), "journey_count": len(journey_ids)}
                )
                await self.record_health_metric("compare_journeys_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("compare_journeys_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "compare_journeys",
                    details={"tenant_id": tenant_id, "journey_count": len(journey_ids)}
                )
                await self.record_health_metric("compare_journeys_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("compare_journeys_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            comparisons = []
            
            for journey_id in journey_ids:
                metrics_result = await self.calculate_journey_metrics(journey_id, user_context=user_context)
                if metrics_result.get("success"):
                    comparisons.append({
                        "journey_id": journey_id,
                        "metrics": metrics_result["metrics"]
                    })
            
            # Find best/worst
            if comparisons:
                best = max(comparisons, key=lambda x: x["metrics"]["completion_rate"])
                worst = min(comparisons, key=lambda x: x["metrics"]["completion_rate"])
            else:
                best = worst = None
            
            # Record health metric (success)
            await self.record_health_metric("compare_journeys_success", 1.0, {"journey_count": len(journey_ids), "comparison_count": len(comparisons)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("compare_journeys_complete", success=True, details={"journey_count": len(journey_ids), "comparison_count": len(comparisons)})
            
            self.logger.info(f"✅ Journeys compared: {len(journey_ids)}")
            
            return {
                "success": True,
                "comparisons": comparisons,
                "best_performing": best,
                "worst_performing": worst
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "compare_journeys", details={"journey_ids": journey_ids})
            
            # Record health metric (failure)
            await self.record_health_metric("compare_journeys_failed", 1.0, {"journey_count": len(journey_ids), "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("compare_journeys_complete", success=False, details={"journey_count": len(journey_ids), "error": str(e)})
            
            self.logger.error(f"❌ Compare journeys failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_journey_benchmarks(
        self,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get journey benchmarks (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        
        Args:
            user_context: User context for security and tenant validation
        
        Returns:
            Journey benchmarks
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_journey_benchmarks_start",
            success=True
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.security.check_permissions(user_context, "get_journey_benchmarks", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_journey_benchmarks",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_journey_benchmarks_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_journey_benchmarks_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.tenant.validate_tenant_access(tenant_id, self.service_name):
                await self.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "get_journey_benchmarks",
                    details={"tenant_id": tenant_id}
                )
                await self.record_health_metric("get_journey_benchmarks_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.log_operation_with_telemetry("get_journey_benchmarks_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied"
                }
        
        try:
            # Get all journey executions
            executions = await self.search_documents(
                "journey_execution",
                {"type": "journey_execution"}
            )
            
            if not executions or len(executions) == 0:
                await self.record_health_metric("get_journey_benchmarks_no_executions", 1.0, {})
                await self.log_operation_with_telemetry("get_journey_benchmarks_complete", success=True, details={"total_journeys": 0})
                return {
                    "success": True,
                    "benchmarks": {
                        "average_completion_rate": 0,
                        "average_duration_seconds": 0,
                        "total_journeys": 0
                    }
                }
            
            execution_data = [r.get("document") if isinstance(r, dict) else r for r in executions]
            
            # Calculate benchmarks
            completed = len([e for e in execution_data if e.get("status") == "completed"])
            total = len(execution_data)
            
            durations = []
            for execution in execution_data:
                if execution.get("status") == "completed" and "started_at" in execution and "completed_at" in execution:
                    start = datetime.fromisoformat(execution["started_at"])
                    end = datetime.fromisoformat(execution["completed_at"])
                    duration = (end - start).total_seconds()
                    durations.append(duration)
            
            benchmarks = {
                "average_completion_rate": completed / total if total > 0 else 0,
                "average_duration_seconds": sum(durations) / len(durations) if durations else 0,
                "total_journeys": total,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("get_journey_benchmarks_success", 1.0, {"total_journeys": total})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_journey_benchmarks_complete", success=True, details={"total_journeys": total})
            
            self.logger.info("✅ Journey benchmarks calculated")
            
            return {
                "success": True,
                "benchmarks": benchmarks
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_journey_benchmarks")
            
            # Record health metric (failure)
            await self.record_health_metric("get_journey_benchmarks_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_journey_benchmarks_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get journey benchmarks failed: {e}")
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
            "experience_services_available": {
                "user_experience": self.user_experience is not None,
                "session_manager": self.session_manager is not None
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "journey_service",
            "realm": "journey",
            "layer": "journey_analytics",
            "capabilities": ["journey_analytics", "journey_metrics", "journey_optimization", "journey_comparison"],
            "soa_apis": [
                "calculate_journey_metrics", "get_completion_rate", "get_average_duration",
                "identify_drop_off_points", "analyze_journey_performance",
                "get_optimization_recommendations", "compare_journeys", "get_journey_benchmarks"
            ],
            "mcp_tools": [],
            "composes": "experience_analytics"
        }








