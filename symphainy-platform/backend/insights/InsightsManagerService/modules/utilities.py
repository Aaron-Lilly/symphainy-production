#!/usr/bin/env python3
"""
Insights Manager Service - Utilities Module

Micro-module for utility methods.
"""

import logging
from typing import Any, Dict


class Utilities:
    """Utilities module for Insights Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure abstractions are properly mapped."""
        mapping_status = {
            "librarian": self.service.librarian is not None,
            "data_steward": self.service.data_steward is not None,
            "content_steward": self.service.content_steward is not None,
            "is_infrastructure_connected": self.service.is_infrastructure_connected
        }
        
        return mapping_status
    
    def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Insights Manager service capabilities."""
        return {
            "service_name": self.service.service_name,
            "realm": self.service.realm_name,
            "manager_type": str(self.service.manager_type),
            "capabilities": {
                "data_analysis": True,
                "insights_generation": True,
                "visualization": True,
                "business_analysis": True
            },
            "insights_orchestrator_available": self.service.insights_orchestrator is not None,
            "infrastructure": self.validate_infrastructure_mapping(),
            "soa_apis": list(self.service.soa_apis.keys()) if hasattr(self.service, 'soa_apis') else [],
            "mcp_tools": list(self.service.mcp_tools.keys()) if hasattr(self.service, 'mcp_tools') else []
        }

