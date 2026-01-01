#!/usr/bin/env python3
"""
Nurse Service - Diagnostics Module

Micro-module for system diagnostics using Health Abstraction (OpenTelemetry + Simple Health).
"""

from typing import Any, Dict
from datetime import datetime


class Diagnostics:
    """Diagnostics module for Nurse service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def run_diagnostics(self, service_name: str) -> Dict[str, Any]:
        """
        Run system diagnostics using Health Abstraction.
        
        NORMAL PATTERN: This method doesn't provide telemetry, so we can use utilities normally.
        """
        # Start telemetry tracking (Nurse can use telemetry utilities for non-telemetry operations)
        await self.service.log_operation_with_telemetry(
            "run_diagnostics_start",
            success=True,
            details={"service_name": service_name}
        )
        
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Run diagnostics via health abstraction
            diagnostics_result = await self.service.health_abstraction.run_diagnostics(service_name)
            
            if diagnostics_result:
                # Store diagnostics using health abstraction
                await self.service.health_abstraction.store_diagnostics(
                    service_name=service_name,
                    diagnostics_data=diagnostics_result
                )
                
                # Update local diagnostics (backward compatibility)
                self.service.system_diagnostics[service_name] = diagnostics_result
                
                # Record health metric
                await self.service.record_health_metric(
                    "diagnostics_completed",
                    1.0,
                    {"service_name": service_name}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "run_diagnostics_complete",
                    success=True,
                    details={"service_name": service_name}
                )
                
                if self.service.logger:
                    self.service.logger.info(f"✅ Diagnostics completed: {service_name}")
                return {
                    "service_name": service_name,
                    "diagnostics": diagnostics_result,
                    "completed_at": datetime.utcnow().isoformat(),
                    "status": "success"
                }
            else:
                # Record health metric (no data)
                await self.service.record_health_metric(
                    "diagnostics_no_data",
                    1.0,
                    {"service_name": service_name}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "run_diagnostics_complete",
                    success=True,
                    details={"service_name": service_name, "status": "no_data"}
                )
                
                return {
                    "service_name": service_name,
                    "diagnostics": {},
                    "completed_at": datetime.utcnow().isoformat(),
                    "status": "no_data"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "run_diagnostics")
            
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "run_diagnostics_complete",
                success=False,
                details={"service_name": service_name, "error": str(e)}
            )
            
            if self.service.logger:
                self.service.logger.error(f"❌ Error running diagnostics: {str(e)}")
            return {
                "service_name": service_name,
                "diagnostics": {},
                "error": str(e),
                "status": "error"
            }






