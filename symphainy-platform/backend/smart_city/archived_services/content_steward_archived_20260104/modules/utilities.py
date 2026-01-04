#!/usr/bin/env python3
"""
Content Steward Service - Utilities Module

Micro-module for utility methods.
"""

from typing import Any, Dict


class Utilities:
    """Utilities module for Content Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure mapping."""
        validation_results = {
            "file_management": self.service.file_management_abstraction is not None,
            "content_metadata": self.service.content_metadata_abstraction is not None,
            "cache": self.service.cache_abstraction is not None,
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
        """Get Content Steward service capabilities matching original format."""
        capabilities = {
            "service_name": "content_steward",
            "service_type": "content_processing",
            "realm": "smart_city",
            "capabilities": [
                "content_processing",
                "policy_enforcement",
                "metadata_extraction",
                "quality_assessment",
                "lineage_reporting",
                "format_conversion",
                "data_optimization",
                "content_validation"
            ],
            "detailed_capabilities": {
                "content_processing": {
                    "process_upload": True,
                    "process_file_content": True,
                    "get_file_metadata": True,
                    "update_file_metadata": True
                },
                "format_conversion": {
                    "convert_file_format": True,
                    "batch_convert_formats": True
                },
                "data_optimization": {
                    "optimize_data": True,
                    "compress_data": True,
                    "validate_output": True
                },
                "content_validation": {
                    "validate_content": True,
                    "get_quality_metrics": True
                },
                "metadata_management": {
                    "get_asset_metadata": True,
                    "get_lineage": True,
                    "get_processing_status": True
                },
                "infrastructure": {
                    "file_management_gcs_supabase": self.service.file_management_abstraction is not None,
                    "content_metadata_arango": self.service.content_metadata_abstraction is not None,
                    "cache_memory_redis": self.service.cache_abstraction is not None
                }
            },
            "soa_api_exposure": {
                "apis": list(self.service.soa_apis.keys()),
                "endpoints": [api["endpoint"] for api in self.service.soa_apis.values()],
                "description": "SOA APIs exposed for realm consumption"
            },
            "mcp_server_integration": {
                "tools": list(self.service.mcp_tools.keys()),
                "server_enabled": True,
                "description": "MCP tools available for agent access"
            },
            "access_pattern": "api_via_smart_city_gateway",
            "version": "3.0"
        }
        
        return capabilities

