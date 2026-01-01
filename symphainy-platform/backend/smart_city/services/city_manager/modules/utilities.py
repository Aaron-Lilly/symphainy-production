#!/usr/bin/env python3
"""
City Manager Service - Utilities Module

Micro-module for utility methods.
"""

from typing import Any, Dict
from datetime import datetime


class Utilities:
    """Utilities module for City Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that City Manager is using correct infrastructure abstractions."""
        try:
            validation_results = {
                "service_name": self.service.service_name,
                "infrastructure_connected": self.service.is_infrastructure_connected,
                "abstractions": {},
                "libraries": {},
                "validation_timestamp": datetime.utcnow().isoformat()
            }
            
            # Check Public Works abstractions
            validation_results["abstractions"] = {
                "session_abstraction": self.service.session_abstraction is not None,
                "state_management_abstraction": self.service.state_management_abstraction is not None,
                "messaging_abstraction": self.service.messaging_abstraction is not None,
                "file_management_abstraction": self.service.file_management_abstraction is not None,
                "analytics_abstraction": self.service.analytics_abstraction is not None,
                "health_abstraction": self.service.health_abstraction is not None,
                "telemetry_abstraction": self.service.telemetry_abstraction is not None
            }
            
            # Check direct library injection
            validation_results["libraries"] = {
                "asyncio": self.service.asyncio is not None,
                "httpx": self.service.httpx is not None
            }
            
            # Overall validation
            all_abstractions_connected = all(validation_results["abstractions"].values())
            all_libraries_available = all(validation_results["libraries"].values())
            
            validation_results["overall_success"] = all_abstractions_connected and all_libraries_available
            
            if validation_results["overall_success"]:
                if self.service.logger:
                    self.service.logger.info("✅ City Manager infrastructure mapping validation successful")
            else:
                if self.service.logger:
                    self.service.logger.warning("⚠️ City Manager infrastructure mapping validation failed")
            
            return validation_results
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"Infrastructure validation failed: {str(e)}")
            return {
                "service_name": self.service.service_name,
                "overall_success": False,
                "error": str(e),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get City Manager service capabilities."""
        capabilities = {
            "service_name": self.service.service_name,
            "role": "city_manager",
            "role_name": self.service.role_name,
            "orchestration_scope": self.service.orchestration_scope,
            "governance_level": self.service.governance_level,
            "capabilities": {
                "bootstrapping": True,
                "realm_startup_orchestration": True,
                "service_management": True,
                "platform_governance": True,
                "cross_dimensional_coordination": True
            },
            "infrastructure_abstractions": [
                "session_abstraction",
                "state_management_abstraction",
                "messaging_abstraction",
                "file_management_abstraction",
                "analytics_abstraction",
                "health_abstraction",
                "telemetry_abstraction"
            ],
            "direct_libraries": [
                "asyncio",
                "httpx"
            ],
            "smart_city_services": list(self.service.smart_city_services.keys()),
            "manager_hierarchy": list(self.service.manager_hierarchy.keys()),
            "soa_apis": len(self.service.soa_apis),
            "mcp_tools": len(self.service.mcp_tools),
            "bootstrapping_complete": self.service.bootstrapping_complete,
            "realm_startup_complete": self.service.realm_startup_complete
        }
        
        return capabilities



