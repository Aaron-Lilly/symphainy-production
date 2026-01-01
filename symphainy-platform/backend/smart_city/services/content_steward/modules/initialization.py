#!/usr/bin/env python3
"""
Content Steward Service - Initialization Module

Micro-module for Content Steward service initialization.
"""

from typing import Any


class Initialization:
    """Initialization module for Content Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_infrastructure_connections(self):
        """Initialize infrastructure connections using mixin methods."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "initialize_infrastructure_connections_start",
            success=True
        )
        
        try:
            # Get File Management Abstraction (GCS + Supabase)
            # This handles file storage in GCS and file metadata in Supabase
            self.service.file_management_abstraction = self.service.get_infrastructure_abstraction("file_management")
            if not self.service.file_management_abstraction:
                raise Exception("File Management Abstraction not available")
            
            # Get Content Metadata Abstraction (ArangoDB) - OPTIONAL for MVP
            # This handles content metadata storage and management
            # For MVP: File metadata stored in Supabase (via file_management_abstraction)
            self.service.content_metadata_abstraction = self.service.get_infrastructure_abstraction("content_metadata")
            if not self.service.content_metadata_abstraction:
                # Don't raise - content metadata is optional for MVP (file metadata in Supabase is sufficient)
                pass
            
            # Get Cache Abstraction for content/data caching (OPTIONAL)
            # Cache abstraction is for performance optimization, NOT platform messaging (Post Office's domain)
            # Swappable backends: Redis (production), Memory (development), File (testing)
            self.service.cache_abstraction = self.service.get_infrastructure_abstraction("cache")
            if not self.service.cache_abstraction:
                # Don't raise - caching is optional for MVP
                pass
            
            self.service.is_infrastructure_connected = True
            
            # Record health metric
            await self.service.record_health_metric(
                "infrastructure_connected",
                1.0,
                {
                    "file_management": "connected",
                    "content_metadata": "connected" if self.service.content_metadata_abstraction else "optional",
                    "cache": "connected" if self.service.cache_abstraction else "optional"
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_connections_complete",
                success=True,
                details={
                    "file_management": "connected",
                    "content_metadata": "connected" if self.service.content_metadata_abstraction else "optional",
                    "cache": "connected" if self.service.cache_abstraction else "optional"
                }
            )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "initialize_infrastructure_connections")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_connections_complete",
                success=False,
                details={"error": str(e)}
            )
            raise






