#!/usr/bin/env python3
"""
Utilities Module - Security Guard Service

Provides utility methods and capabilities registration.
"""

from typing import Dict, Any
from datetime import datetime


class Utilities:
    """Utilities module for Security Guard Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Security Guard service capabilities."""
        return {
            "service_name": "SecurityGuardService",
            "service_type": "security_communication_gateway",
            "capabilities": {
                "core_security": {
                    "authentication": True,
                    "authorization": True,
                    "session_management": True
                },
                "orchestration": {
                    "security_communication": True,
                    "zero_trust_policy": True,
                    "tenant_isolation": True
                },
                "integration": {
                    "soa_api": True,
                    "mcp_server": self.service.mcp_server_enabled
                }
            },
            "soa_apis": list(self.service.soa_apis.keys()),
            "mcp_tools": list(self.service.mcp_tools.keys()),
            "status": "active",
            "timestamp": datetime.utcnow().isoformat()
        }







