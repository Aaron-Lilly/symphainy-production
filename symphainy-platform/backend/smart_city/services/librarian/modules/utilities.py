#!/usr/bin/env python3
"""
Librarian Service - Utilities Module

Micro-module for utility methods.
"""

from typing import Any, Dict


class Utilities:
    """Utilities module for Librarian service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure mapping."""
        validation_results = {
            "knowledge_discovery": self.service.knowledge_discovery_abstraction is not None,
            "knowledge_governance": self.service.knowledge_governance_abstraction is not None,
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
        """Get Librarian service capabilities."""
        capabilities = {
            "service_name": "LibrarianService",
            "role_name": "librarian",
            "capabilities": {
                "knowledge_management": {
                    "store_knowledge": True,
                    "get_knowledge_item": True,
                    "update_knowledge_item": True,
                    "delete_knowledge_item": True
                },
                "search": {
                    "search_knowledge": True,
                    "semantic_search": True,
                    "get_semantic_relationships": True
                },
                "content_organization": {
                    "catalog_content": True,
                    "manage_content_schema": True,
                    "get_content_categories": True
                },
                "infrastructure": {
                    "knowledge_discovery_abstraction": self.service.knowledge_discovery_abstraction is not None,
                    "knowledge_governance_abstraction": self.service.knowledge_governance_abstraction is not None,
                    "messaging_abstraction": self.service.messaging_abstraction is not None
                }
            },
            "soa_apis": len(self.service.soa_apis),
            "mcp_tools": len(self.service.mcp_tools)
        }
        
        return capabilities







