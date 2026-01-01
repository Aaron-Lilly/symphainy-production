#!/usr/bin/env python3
"""
Initialization Module - Post Office Service

Initializes infrastructure connections using mixin methods.
"""

from typing import Dict, Any


class Initialization:
    """Initialization module for Post Office Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def initialize_infrastructure(self):
        """Initialize infrastructure connections using mixin methods."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "initialize_infrastructure_start",
            success=True
        )
        
        try:
            # Use mixin methods - NOT direct foundation access!
            self.service.messaging_abstraction = self.service.get_messaging_abstraction()
            if not self.service.messaging_abstraction:
                raise Exception("Messaging Abstraction not available")
            
            self.service.event_management_abstraction = self.service.get_event_management_abstraction()
            if not self.service.event_management_abstraction:
                raise Exception("Event Management Abstraction not available")
            
            self.service.session_abstraction = self.service.get_session_abstraction()
            if not self.service.session_abstraction:
                raise Exception("Session Abstraction not available")
            
            self.service.is_infrastructure_connected = True
            
            # Record health metric
            await self.service.record_health_metric(
                "infrastructure_connected",
                1.0,
                {
                    "messaging": "connected",
                    "event_management": "connected",
                    "session": "connected"
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_complete",
                success=True,
                details={
                    "messaging": "connected",
                    "event_management": "connected",
                    "session": "connected"
                }
            )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "initialize_infrastructure")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_complete",
                success=False,
                details={"error": str(e)}
            )
            raise

