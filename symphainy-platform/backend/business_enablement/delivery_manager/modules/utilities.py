#!/usr/bin/env python3
"""
Delivery Manager Service - Utilities Module

Micro-module for utility methods.
"""

import logging
from typing import Any, Dict


class Utilities:
    """Utilities module for Delivery Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure abstractions are properly mapped."""
        mapping_status = {
            "session_abstraction": self.service.session_abstraction is not None,
            "state_management_abstraction": self.service.state_management_abstraction is not None,
            "messaging_abstraction": self.service.messaging_abstraction is not None,
            "is_infrastructure_connected": self.service.is_infrastructure_connected
        }
        
        return mapping_status
    
    def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Delivery Manager service capabilities."""
        return {
            "service_name": self.service.service_name,
            "realm": self.service.realm_name,
            "manager_type": str(self.service.manager_type),
            "capabilities": {
                "capability_delivery": True,
                "pillar_orchestration": True,
                "outcome_tracking": True,
                "business_enablement_orchestration": True
            },
            "business_pillars": list(self.service.business_pillars.keys()) if hasattr(self.service, 'business_pillars') else [],
            "infrastructure": self.validate_infrastructure_mapping(),
            "soa_apis": list(self.service.soa_apis.keys()) if hasattr(self.service, 'soa_apis') else [],
            "mcp_tools": list(self.service.mcp_tools.keys()) if hasattr(self.service, 'mcp_tools') else []
        }






