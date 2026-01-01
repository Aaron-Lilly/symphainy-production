#!/usr/bin/env python3
"""
Utilities Module - Traffic Cop Service

Provides utility methods and infrastructure validation.
"""

from typing import Dict, Any
from datetime import datetime


class Utilities:
    """Utilities module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that Traffic Cop is using correct infrastructure abstractions."""
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
                "analytics_abstraction": self.service.analytics_abstraction is not None
            }
            
            # Check direct library injection
            validation_results["libraries"] = {
                "fastapi": self.service.fastapi is not None,
                "websocket": self.service.websocket is not None,
                "pandas": self.service.pandas is not None,
                "httpx": self.service.httpx is not None,
                "asyncio": self.service.asyncio is not None
            }
            
            # Overall validation
            all_abstractions_connected = all(validation_results["abstractions"].values())
            all_libraries_available = all(validation_results["libraries"].values())
            
            validation_results["overall_success"] = all_abstractions_connected and all_libraries_available
            
            if validation_results["overall_success"]:
                self.service._log("info", "✅ Traffic Cop infrastructure mapping validation successful")
            else:
                self.service._log("warning", "⚠️ Traffic Cop infrastructure mapping validation failed")
            
            return validation_results
            
        except Exception as e:
            self.service._log("error", f"Infrastructure validation failed: {e}")
            return {
                "service_name": self.service.service_name,
                "overall_success": False,
                "error": str(e),
                "validation_timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Traffic Cop service capabilities."""
        return {
            "service_name": self.service.service_name,
            "role": "traffic_cop",
            "capabilities": {
                "load_balancing": True,
                "rate_limiting": True,
                "session_management": True,
                "state_synchronization": True,
                "api_gateway": True,
                "traffic_analytics": True,
                "websocket_support": True
            },
            "infrastructure_abstractions": [
                "session_abstraction",
                "state_management_abstraction", 
                "messaging_abstraction",
                "file_management_abstraction",
                "analytics_abstraction"
            ],
            "direct_libraries": [
                "fastapi",
                "websocket", 
                "pandas",
                "httpx",
                "asyncio"
            ],
            "soa_apis": list(self.service.soa_apis.keys()),
            "mcp_tools": list(self.service.mcp_tools.keys()),
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }







