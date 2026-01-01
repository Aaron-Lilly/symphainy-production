#!/usr/bin/env python3
"""
Nurse Service - Utilities Module

Micro-module for utility methods.
"""

from typing import Any, Dict
from datetime import datetime


class Utilities:
    """Utilities module for Nurse service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure mapping."""
        validation_results = {
            "telemetry": self.service.telemetry_abstraction is not None,
            "alert_management": self.service.alert_management_abstraction is not None,
            "health": self.service.health_abstraction is not None,
            "session": self.service.session_management_abstraction is not None,
            "state": self.service.state_management_abstraction is not None,
            "infrastructure_connected": self.service.is_infrastructure_connected
        }
        
        all_valid = all(validation_results.values())
        
        if self.service.logger:
            if all_valid:
                self.service.logger.info("✅ Infrastructure mapping validated")
            else:
                self.service.logger.warning(f"⚠️ Infrastructure mapping validation failed: {validation_results}")
        
        return {
            "valid": all_valid,
            "results": validation_results,
            "status": "success" if all_valid else "error"
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Nurse Service capabilities."""
        capabilities = {
            "service_name": "NurseService",
            "service_type": "health_monitor",
            "realm": "smart_city",
            "capabilities": [
                "health_monitoring",
                "telemetry_collection",
                "distributed_tracing",
                "alert_management",
                "system_diagnostics",
                "infrastructure_integration"
            ],
            "infrastructure_connections": {
                "telemetry_abstraction": self.service.telemetry_abstraction is not None,
                "alert_management_abstraction": self.service.alert_management_abstraction is not None,
                "health_abstraction": self.service.health_abstraction is not None,
                "session_management_abstraction": self.service.session_management_abstraction is not None,
                "state_management_abstraction": self.service.state_management_abstraction is not None
            },
            "soa_apis": len(self.service.soa_apis),
            "mcp_tools": len(self.service.mcp_tools)
        }
        
        return capabilities






