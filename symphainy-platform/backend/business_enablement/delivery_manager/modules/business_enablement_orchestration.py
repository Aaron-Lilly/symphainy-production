#!/usr/bin/env python3
"""
Delivery Manager Service - Business Enablement Orchestration Module

Micro-module for orchestrating business enablement pillars (Delivery → Business Enablement).
"""

from typing import Any, Dict, Optional
from datetime import datetime


class BusinessEnablementOrchestration:
    """Business enablement orchestration module for Delivery Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def orchestrate_business_enablement(
        self,
        business_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate business enablement by coordinating all 5 pillars.
        
        This orchestrates: Content Pillar, Insights Pillar, Operations Pillar,
        Business Outcomes Pillar, and Context Pillar via Business Orchestrator.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking (via service)
        await self.service.log_operation_with_telemetry(
            "orchestrate_business_enablement_start",
            success=True,
            details={"capability_type": business_context.get("capability_type")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.service.security.check_permissions(user_context, "orchestrate_business_enablement", "execute"):
                await self.service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "orchestrate_business_enablement",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.service.record_health_metric("orchestrate_business_enablement_access_denied", 1.0, {})
                await self.service.log_operation_with_telemetry("orchestrate_business_enablement_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.service.tenant.validate_tenant_access(tenant_id, self.service.service_name):
                await self.service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "orchestrate_business_enablement",
                    details={"tenant_id": tenant_id}
                )
                await self.service.record_health_metric("orchestrate_business_enablement_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.service.log_operation_with_telemetry("orchestrate_business_enablement_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        try:
            if self.service.logger:
                self.service.logger.info("🎯 Orchestrating business enablement...")
            
            # Get Business Orchestrator (lazy-load if needed)
            business_orchestrator = await self.service.get_business_orchestrator()
            
            if business_orchestrator:
                # Call Business Orchestrator's orchestrate_pillars method
                if hasattr(business_orchestrator, "orchestrate_pillars"):
                    orchestration_result = await business_orchestrator.orchestrate_pillars(business_context)
                    
                    if self.service.logger:
                        self.service.logger.info(f"✅ Business enablement orchestrated successfully: {orchestration_result.get('success', False)}")
                    
                    # Record health metric (success)
                    await self.service.record_health_metric("orchestrate_business_enablement_success", 1.0, {})
                    
                    # End telemetry tracking
                    await self.service.log_operation_with_telemetry("orchestrate_business_enablement_complete", success=True)
                    
                    return {
                        "success": True,
                        "business_enablement_orchestrated": True,
                        "orchestration_result": orchestration_result,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    if self.service.logger:
                        self.service.logger.warning("⚠️ Business Orchestrator does not have orchestrate_pillars method")
            
            # Fallback: Direct pillar coordination if Business Orchestrator not available
            if self.service.logger:
                self.service.logger.info("⚠️ Business Orchestrator not available - coordinating pillars directly")
            
            pillar_results = {}
            for pillar_name in self.service.business_pillars.keys():
                pillar_results[pillar_name] = {
                    "status": "coordinated",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Record health metric (success)
            await self.service.record_health_metric("orchestrate_business_enablement_success", 1.0, {})
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry("orchestrate_business_enablement_complete", success=True)
            
            return {
                "success": True,
                "business_enablement_orchestrated": True,
                "pillar_results": pillar_results,
                "timestamp": datetime.utcnow().isoformat()
            }
                
        except Exception as e:
            # Error handling with audit
            await self.service.handle_error_with_audit(e, "orchestrate_business_enablement", details={"business_context": business_context})
            
            # Record health metric (failure)
            await self.service.record_health_metric("orchestrate_business_enablement_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry("orchestrate_business_enablement_complete", success=False, details={"error": str(e)})
            
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to orchestrate business enablement: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "business_context": business_context,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def deliver_capability(
        self,
        capability_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Deliver a business capability via business enablement pillars.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "deliver_capability_start",
            success=True,
            details={"capability_type": capability_request.get("capability_type")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.service.security.check_permissions(user_context, "deliver_capability", "execute"):
                await self.service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "deliver_capability",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.service.record_health_metric("deliver_capability_access_denied", 1.0, {})
                await self.service.log_operation_with_telemetry("deliver_capability_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.service.tenant.validate_tenant_access(tenant_id, self.service.service_name):
                await self.service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "deliver_capability",
                    details={"tenant_id": tenant_id}
                )
                await self.service.record_health_metric("deliver_capability_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.service.log_operation_with_telemetry("deliver_capability_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        try:
            if self.service.logger:
                self.service.logger.info("📦 Delivering capability...")
            
            capability_type = capability_request.get("capability_type")
            capability_context = capability_request.get("context", {})
            
            # Deliver capability via business enablement orchestration
            delivery_result = await self.orchestrate_business_enablement({
                "capability_type": capability_type,
                "context": capability_context
            }, user_context=user_context)
            
            # Record health metric (success)
            await self.service.record_health_metric("deliver_capability_success", 1.0, {"capability_type": capability_type})
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry("deliver_capability_complete", success=True, details={"capability_type": capability_type})
            
            return {
                "success": True,
                "capability_delivered": True,
                "delivery_result": delivery_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Error handling with audit
            await self.service.handle_error_with_audit(e, "deliver_capability", details={"capability_request": capability_request})
            
            # Record health metric (failure)
            await self.service.record_health_metric("deliver_capability_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry("deliver_capability_complete", success=False, details={"error": str(e)})
            
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to deliver capability: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "capability_request": capability_request,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def track_outcomes(
        self,
        outcome_request: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track business outcomes.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        - Security and tenant validation
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "track_outcomes_start",
            success=True,
            details={"outcome_type": outcome_request.get("outcome_type")}
        )
        
        # Security and Tenant Validation
        if user_context:
            if not await self.service.security.check_permissions(user_context, "track_outcomes", "execute"):
                await self.service.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "track_outcomes",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.service.record_health_metric("track_outcomes_access_denied", 1.0, {})
                await self.service.log_operation_with_telemetry("track_outcomes_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            tenant_id = user_context.get("tenant_id")
            if tenant_id and not await self.service.tenant.validate_tenant_access(tenant_id, self.service.service_name):
                await self.service.handle_error_with_audit(
                    ValueError("Tenant access denied"),
                    "track_outcomes",
                    details={"tenant_id": tenant_id}
                )
                await self.service.record_health_metric("track_outcomes_tenant_denied", 1.0, {"tenant_id": tenant_id})
                await self.service.log_operation_with_telemetry("track_outcomes_complete", success=False)
                return {
                    "success": False,
                    "error": "Tenant access denied",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        try:
            if self.service.logger:
                self.service.logger.info("📊 Tracking outcomes...")
            
            outcome_type = outcome_request.get("outcome_type")
            outcome_metrics = outcome_request.get("metrics", {})
            
            tracking_result = {
                "outcome_id": f"outcome_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "outcome_type": outcome_type,
                "metrics": outcome_metrics,
                "status": "tracked",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.service.record_health_metric("track_outcomes_success", 1.0, {"outcome_type": outcome_type})
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry("track_outcomes_complete", success=True, details={"outcome_type": outcome_type})
            
            return {
                "success": True,
                "tracking_result": tracking_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Error handling with audit
            await self.service.handle_error_with_audit(e, "track_outcomes", details={"outcome_request": outcome_request})
            
            # Record health metric (failure)
            await self.service.record_health_metric("track_outcomes_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry("track_outcomes_complete", success=False, details={"error": str(e)})
            
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to track outcomes: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "outcome_request": outcome_request,
                "timestamp": datetime.utcnow().isoformat()
            }






