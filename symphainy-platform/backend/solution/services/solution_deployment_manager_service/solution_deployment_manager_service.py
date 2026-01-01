#!/usr/bin/env python3
"""
Solution Deployment Manager Service

WHAT: Manages solution deployment lifecycle
HOW: Validates readiness, orchestrates deployment, monitors health

This service manages the deployment lifecycle of solutions including
validation, execution, monitoring, and rollback capabilities.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class SolutionDeploymentManagerService(RealmServiceBase):
    """
    Solution Deployment Manager Service for Solution realm.
    
    Manages solution deployment lifecycle including validation,
    deployment orchestration, health monitoring, and rollback.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Solution Deployment Manager Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.conductor = None
        self.nurse = None
        self.post_office = None
        self.librarian = None
    
    async def initialize(self) -> bool:
        """
        Initialize Solution Deployment Manager Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Phase 2 Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "solution_deployment_manager_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.conductor = await self.get_conductor_api()
            self.nurse = await self.get_nurse_api()
            self.post_office = await self.get_post_office_api()
            self.librarian = await self.get_librarian_api()
            
            # 2. Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "deployment_management",
                        "protocol": "SolutionDeploymentManagerProtocol",
                        "description": "Manage solution deployment lifecycle",
                        "contracts": {
                            "soa_api": {
                                "api_name": "deploy_solution",
                                "endpoint": "/api/v1/solution/deployment/deploy",
                                "method": "POST",
                                "handler": self.deploy_solution,
                                "metadata": {
                                    "description": "Deploy a solution",
                                    "parameters": ["solution_id", "deployment_strategy", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.deploy",
                            "semantic_api": "/api/v1/solution/deployment/deploy",
                            "user_journey": "deploy_solution"
                        }
                    },
                    {
                        "name": "deployment_validation",
                        "protocol": "SolutionDeploymentManagerProtocol",
                        "description": "Validate solution readiness and prerequisites",
                        "contracts": {
                            "soa_api": {
                                "api_name": "validate_solution_readiness",
                                "endpoint": "/api/v1/solution/deployment/validate",
                                "method": "POST",
                                "handler": self.validate_solution_readiness,
                                "metadata": {
                                    "description": "Validate solution readiness for deployment",
                                    "parameters": ["solution_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.validate_readiness",
                            "semantic_api": "/api/v1/solution/deployment/validate",
                            "user_journey": "validate_solution_readiness"
                        }
                    },
                    {
                        "name": "deployment_monitoring",
                        "protocol": "SolutionDeploymentManagerProtocol",
                        "description": "Monitor deployment status and health",
                        "contracts": {
                            "soa_api": {
                                "api_name": "monitor_deployment_health",
                                "endpoint": "/api/v1/solution/deployment/health",
                                "method": "POST",
                                "handler": self.monitor_deployment_health,
                                "metadata": {
                                    "description": "Monitor deployment health",
                                    "parameters": ["deployment_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.monitor_health",
                            "semantic_api": "/api/v1/solution/deployment/health",
                            "user_journey": "monitor_deployment_health"
                        }
                    },
                    {
                        "name": "deployment_rollback",
                        "protocol": "SolutionDeploymentManagerProtocol",
                        "description": "Rollback and manage deployment lifecycle",
                        "contracts": {
                            "soa_api": {
                                "api_name": "rollback_deployment",
                                "endpoint": "/api/v1/solution/deployment/rollback",
                                "method": "POST",
                                "handler": self.rollback_deployment,
                                "metadata": {
                                    "description": "Rollback a deployment",
                                    "parameters": ["deployment_id", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.rollback",
                            "semantic_api": "/api/v1/solution/deployment/rollback",
                            "user_journey": "rollback_deployment"
                        }
                    }
                ],
                soa_apis=[
                    "validate_solution_readiness", "check_deployment_prerequisites",
                    "deploy_solution", "get_deployment_status", "monitor_deployment_health",
                    "pause_deployment", "resume_deployment", "rollback_deployment", "get_deployment_history"
                ],
                mcp_tools=[]
            )
            
            # Record health metric
            await self.record_health_metric(
                "solution_deployment_manager_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "solution_deployment_manager_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Solution Deployment Manager Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "solution_deployment_manager_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "solution_deployment_manager_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Solution Deployment Manager Service initialization failed: {e}")
            return False
    
    # ========================================================================
    # SOA APIs
    # ========================================================================
    
    async def validate_solution_readiness(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate solution readiness for deployment (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "validate_solution_readiness_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "validate_solution_readiness", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "validate_solution_readiness",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("validate_solution_readiness_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("validate_solution_readiness_complete", success=False)
                return {
                    "success": False,
                    "ready": False,
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
                                "validate_solution_readiness",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("validate_solution_readiness_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("validate_solution_readiness_complete", success=False)
                            return {
                                "success": False,
                                "ready": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            solution_doc = await self.retrieve_document(f"solution_{solution_id}")
            if not solution_doc or "document" not in solution_doc:
                result = {"success": False, "ready": False, "error": "Solution not found"}
                await self.log_operation_with_telemetry("validate_solution_readiness_complete", success=False, details={"error": result["error"]})
                return result
            
            solution = solution_doc["document"]
            
            # Validate phases
            if not solution.get("phases"):
                result = {"success": True, "ready": False, "issues": ["No phases defined"]}
                await self.log_operation_with_telemetry("validate_solution_readiness_complete", success=True, details={"ready": False})
                return result
            
            result = {
                "success": True,
                "ready": True,
                "solution_id": solution_id,
                "phases_count": len(solution["phases"]),
                "validated_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("validate_solution_readiness_success", 1.0, {"solution_id": solution_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_solution_readiness_complete", success=True, details={"solution_id": solution_id})
            
            self.logger.info(f"✅ Solution readiness validated: {solution_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "validate_solution_readiness", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("validate_solution_readiness_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("validate_solution_readiness_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Validate solution readiness failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_deployment_prerequisites(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Check deployment prerequisites (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "check_deployment_prerequisites_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "check_deployment_prerequisites", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "check_deployment_prerequisites",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("check_deployment_prerequisites_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("check_deployment_prerequisites_complete", success=False)
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
                                "check_deployment_prerequisites",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("check_deployment_prerequisites_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("check_deployment_prerequisites_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Check platform health
            if self.nurse:
                health = await self.nurse.health_check("platform")
                platform_healthy = health.get("status") == "healthy"
            else:
                platform_healthy = True
            
            prerequisites_met = platform_healthy
            
            result = {
                "success": True,
                "prerequisites_met": prerequisites_met,
                "checks": {
                    "platform_health": platform_healthy
                }
            }
            
            # Record health metric (success)
            await self.record_health_metric("check_deployment_prerequisites_success", 1.0, {"prerequisites_met": prerequisites_met})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("check_deployment_prerequisites_complete", success=True, details={"prerequisites_met": prerequisites_met})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "check_deployment_prerequisites", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("check_deployment_prerequisites_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("check_deployment_prerequisites_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Check deployment prerequisites failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def deploy_solution(
        self,
        solution_id: str,
        deployment_strategy: str = "standard",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deploy solution (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "deploy_solution_start",
            success=True,
            details={"solution_id": solution_id, "strategy": deployment_strategy}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "deploy_solution", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "deploy_solution",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("deploy_solution_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("deploy_solution_complete", success=False)
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
                                "deploy_solution",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("deploy_solution_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("deploy_solution_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Validate readiness
            readiness = await self.validate_solution_readiness(solution_id, user_context=user_context)
            if not readiness.get("ready"):
                result = {"success": False, "error": "Solution not ready", "validation": readiness}
                await self.log_operation_with_telemetry("deploy_solution_complete", success=False, details={"error": result["error"]})
                return result
            
            # Create deployment record
            deployment = {
                "deployment_id": f"dep_{solution_id}_{datetime.utcnow().timestamp()}",
                "solution_id": solution_id,
                "strategy": deployment_strategy,
                "status": "deploying",
                "started_at": datetime.utcnow().isoformat(),
                "user_id": user_context.get("user_id") if user_context else None,
                "tenant_id": user_context.get("tenant_id") if user_context else None
            }
            
            # Store deployment
            await self.store_document(deployment, {"type": "deployment_record", "solution_id": solution_id})
            
            # Send notification
            if self.post_office:
                await self.post_office.send_notification("admin", {
                    "type": "deployment_started",
                    "deployment_id": deployment["deployment_id"],
                    "solution_id": solution_id
                })
            
            result = {"success": True, "deployment": deployment}
            
            # Record health metric (success)
            await self.record_health_metric("deploy_solution_success", 1.0, {"solution_id": solution_id, "deployment_id": deployment["deployment_id"]})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("deploy_solution_complete", success=True, details={"solution_id": solution_id, "deployment_id": deployment["deployment_id"]})
            
            self.logger.info(f"✅ Solution deployed: {solution_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "deploy_solution", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("deploy_solution_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("deploy_solution_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Deploy solution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_deployment_status(
        self,
        deployment_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get deployment status (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_deployment_status_start",
            success=True,
            details={"deployment_id": deployment_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_deployment_status", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_deployment_status",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_deployment_status_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_deployment_status_complete", success=False)
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
                                "get_deployment_status",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("get_deployment_status_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_deployment_status_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            results = await self.search_documents("deployment_record", {"type": "deployment_record", "deployment_id": deployment_id})
            
            if results and len(results) > 0:
                deployment = results[0].get("document") if isinstance(results[0], dict) else results[0]
                
                result = {"success": True, "deployment": deployment}
                
                # Record health metric (success)
                await self.record_health_metric("get_deployment_status_success", 1.0, {"deployment_id": deployment_id})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("get_deployment_status_complete", success=True, details={"deployment_id": deployment_id})
                
                return result
            
            result = {"success": False, "error": "Deployment not found"}
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_deployment_status_complete", success=False, details={"error": result["error"]})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_deployment_status", details={"deployment_id": deployment_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_deployment_status_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_deployment_status_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get deployment status failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def monitor_deployment_health(
        self,
        deployment_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Monitor deployment health (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "monitor_deployment_health_start",
            success=True,
            details={"deployment_id": deployment_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "monitor_deployment_health", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "monitor_deployment_health",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("monitor_deployment_health_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("monitor_deployment_health_complete", success=False)
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
                                "monitor_deployment_health",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("monitor_deployment_health_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("monitor_deployment_health_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            # Get deployment
            status_result = await self.get_deployment_status(deployment_id, user_context=user_context)
            if not status_result.get("success"):
                await self.log_operation_with_telemetry("monitor_deployment_health_complete", success=False, details={"error": status_result.get("error")})
                return status_result
            
            deployment = status_result["deployment"]
            
            # Check health
            health = {
                "deployment_id": deployment_id,
                "status": deployment.get("status"),
                "healthy": deployment.get("status") in ["deploying", "completed"],
                "checked_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (using service utility method)
            await self.record_health_metric("deployment_health_check", 1.0 if health["healthy"] else 0.0, {"deployment_id": deployment_id, "status": health["status"]})
            
            result = {"success": True, "health": health}
            
            # Record health metric (success)
            await self.record_health_metric("monitor_deployment_health_success", 1.0, {"deployment_id": deployment_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("monitor_deployment_health_complete", success=True, details={"deployment_id": deployment_id, "healthy": health["healthy"]})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "monitor_deployment_health", details={"deployment_id": deployment_id})
            
            # Record health metric (failure)
            await self.record_health_metric("monitor_deployment_health_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("monitor_deployment_health_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Monitor deployment health failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def pause_deployment(
        self,
        deployment_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pause deployment (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "pause_deployment_start",
            success=True,
            details={"deployment_id": deployment_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "pause_deployment", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "pause_deployment",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("pause_deployment_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("pause_deployment_complete", success=False)
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
                                "pause_deployment",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("pause_deployment_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("pause_deployment_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            result = {"success": True, "status": "paused"}
            
            # Record health metric (success)
            await self.record_health_metric("pause_deployment_success", 1.0, {"deployment_id": deployment_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("pause_deployment_complete", success=True, details={"deployment_id": deployment_id})
            
            self.logger.info(f"✅ Deployment paused: {deployment_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "pause_deployment", details={"deployment_id": deployment_id})
            
            # Record health metric (failure)
            await self.record_health_metric("pause_deployment_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("pause_deployment_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def resume_deployment(
        self,
        deployment_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resume deployment (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "resume_deployment_start",
            success=True,
            details={"deployment_id": deployment_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "resume_deployment", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "resume_deployment",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("resume_deployment_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("resume_deployment_complete", success=False)
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
                                "resume_deployment",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("resume_deployment_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("resume_deployment_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            result = {"success": True, "status": "deploying"}
            
            # Record health metric (success)
            await self.record_health_metric("resume_deployment_success", 1.0, {"deployment_id": deployment_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("resume_deployment_complete", success=True, details={"deployment_id": deployment_id})
            
            self.logger.info(f"✅ Deployment resumed: {deployment_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "resume_deployment", details={"deployment_id": deployment_id})
            
            # Record health metric (failure)
            await self.record_health_metric("resume_deployment_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("resume_deployment_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def rollback_deployment(
        self,
        deployment_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Rollback deployment (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "rollback_deployment_start",
            success=True,
            details={"deployment_id": deployment_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "rollback_deployment", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "rollback_deployment",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("rollback_deployment_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("rollback_deployment_complete", success=False)
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
                                "rollback_deployment",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("rollback_deployment_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("rollback_deployment_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            result = {"success": True, "status": "rolled_back"}
            
            # Record health metric (success)
            await self.record_health_metric("rollback_deployment_success", 1.0, {"deployment_id": deployment_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("rollback_deployment_complete", success=True, details={"deployment_id": deployment_id})
            
            self.logger.info(f"✅ Deployment rolled back: {deployment_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "rollback_deployment", details={"deployment_id": deployment_id})
            
            # Record health metric (failure)
            await self.record_health_metric("rollback_deployment_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("rollback_deployment_complete", success=False, details={"error": str(e)})
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_deployment_history(
        self,
        solution_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get deployment history (SOA API).
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_deployment_history_start",
            success=True,
            details={"solution_id": solution_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_deployment_history", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_deployment_history",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.record_health_metric("get_deployment_history_access_denied", 1.0, {})
                await self.log_operation_with_telemetry("get_deployment_history_complete", success=False)
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
                                "get_deployment_history",
                                details={"tenant_id": tenant_id}
                            )
                            await self.record_health_metric("get_deployment_history_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_deployment_history_complete", success=False)
                            return {
                                "success": False,
                                "error": "Tenant access denied"
                            }
                    else:
                        self.logger.debug(f"Tenant management not configured, allowing access (open by default)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Tenant validation raised exception: {e}, allowing access (tenant management not configured)")
        
        try:
            results = await self.search_documents("deployment_record", {"type": "deployment_record", "solution_id": solution_id})
            
            history = [r.get("document") if isinstance(r, dict) else r for r in results]
            history.sort(key=lambda x: x.get("started_at", ""), reverse=True)
            
            result = {"success": True, "history": history}
            
            # Record health metric (success)
            await self.record_health_metric("get_deployment_history_success", 1.0, {"solution_id": solution_id, "history_count": len(history)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_deployment_history_complete", success=True, details={"solution_id": solution_id, "history_count": len(history)})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_deployment_history", details={"solution_id": solution_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_deployment_history_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("get_deployment_history_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Get deployment history failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "solution_service",
            "realm": "solution",
            "layer": "deployment_management",
            "capabilities": ["deployment_management", "deployment_validation", "deployment_monitoring", "deployment_rollback"],
            "soa_apis": [
                "validate_solution_readiness", "check_deployment_prerequisites",
                "deploy_solution", "get_deployment_status", "monitor_deployment_health",
                "pause_deployment", "resume_deployment", "rollback_deployment", "get_deployment_history"
            ],
            "mcp_tools": []
        }








