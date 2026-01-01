#!/usr/bin/env python3
"""
Data Steward Service - Initialization Module

Micro-module for Data Steward service initialization.
"""

from typing import Any


class Initialization:
    """Initialization module for Data Steward service."""
    
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
            # Get Public Works Foundation from DI Container
            public_works_foundation = self.service.di_container.get_public_works_foundation()
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Get File Management Abstraction (GCS + Supabase) - from Content Steward consolidation
            self.service.file_management_abstraction = self.service.get_file_management_abstraction()
            if not self.service.file_management_abstraction:
                raise Exception("File Management Abstraction not available")
            
            # Get Content Metadata Abstraction (ArangoDB) - for semantic layer access
            self.service.content_metadata_abstraction = self.service.get_content_metadata_abstraction()
            if not self.service.content_metadata_abstraction:
                self.service.logger.warning("⚠️ Content Metadata Abstraction not available - semantic layer queries will be limited")
            
            # Get Knowledge Governance Abstraction (ArangoDB + Metadata)
            # This handles policies, compliance, quality metrics, and metadata
            self.service.knowledge_governance_abstraction = self.service.get_knowledge_governance_abstraction()
            if not self.service.knowledge_governance_abstraction:
                raise Exception("Knowledge Governance Abstraction not available")
            
            # Get State Management Abstraction (ArangoDB) for lineage tracking
            # State management is exposed via mixin method
            self.service.state_management_abstraction = self.service.get_state_management_abstraction()
            if not self.service.state_management_abstraction:
                raise Exception("State Management Abstraction not available")
            
            # Get Messaging Abstraction (Redis) for caching
            self.service.messaging_abstraction = self.service.get_messaging_abstraction()
            if not self.service.messaging_abstraction:
                raise Exception("Messaging Abstraction not available")
            
            self.service.is_infrastructure_connected = True
            
            # Record health metric
            await self.service.record_health_metric(
                "infrastructure_connected",
                1.0,
                {
                    "file_management": "connected",
                    "content_metadata": "connected" if self.service.content_metadata_abstraction else "unavailable",
                    "knowledge_governance": "connected",
                    "state_management": "connected",
                    "messaging": "connected"
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_connections_complete",
                success=True,
                details={
                    "file_management": "connected",
                    "content_metadata": "connected" if self.service.content_metadata_abstraction else "unavailable",
                    "knowledge_governance": "connected",
                    "state_management": "connected",
                    "messaging": "connected"
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

