#!/usr/bin/env python3
"""
Data Steward Service - Utilities Module

Micro-module for utility methods.
"""

from typing import Any, Dict


class Utilities:
    """Utilities module for Data Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure mapping."""
        validation_results = {
            "knowledge_governance": self.service.knowledge_governance_abstraction is not None,
            "state_management": self.service.state_management_abstraction is not None,
            "messaging": self.service.messaging_abstraction is not None,
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
        """Get Data Steward service capabilities."""
        capabilities = {
            "service_name": "DataStewardService",
            "role_name": "data_steward",
            "capabilities": {
                "policy_management": {
                    "create_content_policy": True,
                    "get_policy_for_content": True
                },
                "lineage_tracking": {
                    "record_lineage": True,
                    "get_lineage": True
                },
                "quality_compliance": {
                    "validate_schema": True,
                    "get_quality_metrics": True,
                    "enforce_compliance": True
                },
                "infrastructure": {
                    "knowledge_governance_abstraction": self.service.knowledge_governance_abstraction is not None,
                    "state_management_abstraction": self.service.state_management_abstraction is not None,
                    "messaging_abstraction": self.service.messaging_abstraction is not None
                }
            },
            "soa_apis": len(self.service.soa_apis),
            "mcp_tools": len(self.service.mcp_tools)
        }
        
        return capabilities






