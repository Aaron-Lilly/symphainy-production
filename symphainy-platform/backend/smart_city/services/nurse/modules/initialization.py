#!/usr/bin/env python3
"""
Nurse Service - Initialization Module

Micro-module for Nurse service initialization with proper infrastructure connections.
"""

from typing import Any


class Initialization:
    """Initialization module for Nurse service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_infrastructure_connections(self):
        """
        Initialize infrastructure connections using mixin methods.
        
        NORMAL PATTERN: This method doesn't provide telemetry, so we can use utilities normally.
        """
        # Start telemetry tracking (Nurse can use telemetry utilities for non-telemetry operations)
        await self.service.log_operation_with_telemetry(
            "nurse_initialize_infrastructure_start",
            success=True
        )
        
        try:
            if self.service.logger:
                self.service.logger.info("🔌 Connecting to proper infrastructure abstractions...")
            
            # Get Telemetry Abstraction (OpenTelemetry + Tempo)
            self.service.telemetry_abstraction = self.service.get_telemetry_abstraction()
            if not self.service.telemetry_abstraction:
                raise Exception("Telemetry Abstraction not available")
            
            # Get Observability Abstraction (Platform data storage - ArangoDB)
            self.service.observability_abstraction = self.service.get_infrastructure_abstraction("observability")
            if not self.service.observability_abstraction:
                # Don't raise - observability is optional for MVP (can work without it)
                self.service.logger.warning("⚠️ Observability Abstraction not available (optional)")
            
            # Get Alert Management Abstraction (Redis-based alert management)
            self.service.alert_management_abstraction = self.service.get_alert_management_abstraction()
            if not self.service.alert_management_abstraction:
                raise Exception("Alert Management Abstraction not available")
            
            # Get Health Abstraction (OpenTelemetry + Simple Health for health monitoring)
            self.service.health_abstraction = self.service.get_health_abstraction()
            if not self.service.health_abstraction:
                raise Exception("Health Abstraction not available")
            
            # Get Session Management Abstraction (Redis for health state)
            self.service.session_management_abstraction = self.service.get_session_abstraction()
            if not self.service.session_management_abstraction:
                raise Exception("Session Management Abstraction not available")
            
            # Get State Management Abstraction (Redis for alert state)
            self.service.state_management_abstraction = self.service.get_state_management_abstraction()
            if not self.service.state_management_abstraction:
                raise Exception("State Management Abstraction not available")
            
            self.service.is_infrastructure_connected = True
            
            # Record health metric
            await self.service.record_health_metric(
                "nurse_infrastructure_connected",
                1.0,
                {"service": "NurseService"}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "nurse_initialize_infrastructure_complete",
                success=True
            )
            
            if self.service.logger:
                self.service.logger.info("✅ Proper infrastructure connections established:")
                self.service.logger.info("  - Telemetry Abstraction (OpenTelemetry + Tempo): ✅")
                self.service.logger.info(f"  - Observability Abstraction (Platform Data): {'✅' if self.service.observability_abstraction else '⚠️ Optional'}")
                self.service.logger.info("  - Alert Management Abstraction (Redis): ✅")
                self.service.logger.info("  - Health Abstraction (OpenTelemetry + Simple Health): ✅")
                self.service.logger.info("  - Session Management (Redis): ✅")
                self.service.logger.info("  - State Management (Redis): ✅")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "nurse_initialize_infrastructure")
            
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "nurse_initialize_infrastructure_complete",
                success=False,
                details={"error": str(e)}
            )
            
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to connect to proper infrastructure: {str(e)}")
            raise e






