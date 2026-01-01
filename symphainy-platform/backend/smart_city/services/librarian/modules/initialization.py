#!/usr/bin/env python3
"""
Librarian Service - Initialization Module

Micro-module for Librarian service initialization.
"""

from typing import Any, Dict


class Initialization:
    """Initialization module for Librarian service."""
    
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
            # Get Public Works Foundation via DI Container
            public_works_foundation = self.service.di_container.get_public_works_foundation()
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Get Knowledge Discovery Abstraction (Meilisearch + Redis Graph + ArangoDB)
            self.service.knowledge_discovery_abstraction = self.service.get_knowledge_discovery_abstraction()
            if not self.service.knowledge_discovery_abstraction:
                raise Exception("Knowledge Discovery Abstraction not available")
            
            # Get Knowledge Governance Abstraction (Metadata + ArangoDB)
            self.service.knowledge_governance_abstraction = self.service.get_knowledge_governance_abstraction()
            if not self.service.knowledge_governance_abstraction:
                raise Exception("Knowledge Governance Abstraction not available")
            
            # Get Messaging Abstraction (Redis) for caching
            self.service.messaging_abstraction = self.service.get_messaging_abstraction()
            if not self.service.messaging_abstraction:
                raise Exception("Messaging Abstraction not available")
            
            # Get Content Metadata Abstraction (ArangoDB) - NEW
            self.service.content_metadata_abstraction = self.service.get_infrastructure_abstraction("content_metadata")
            if not self.service.content_metadata_abstraction:
                # Don't raise - content metadata is optional for MVP
                self.logger.warning("⚠️ Content Metadata Abstraction not available - content metadata storage will not work")
            
            # Get Semantic Data Abstraction (ArangoDB) - NEW
            self.service.semantic_data_abstraction = self.service.get_infrastructure_abstraction("semantic_data")
            if not self.service.semantic_data_abstraction:
                # Don't raise - semantic data is optional for MVP
                self.logger.warning("⚠️ Semantic Data Abstraction not available - embeddings storage will not work")
            
            self.service.is_infrastructure_connected = True
            
            # Record health metric
            await self.service.record_health_metric(
                "infrastructure_connected",
                1.0,
                {
                    "knowledge_discovery": "connected",
                    "knowledge_governance": "connected",
                    "messaging": "connected",
                    "content_metadata": "connected" if self.service.content_metadata_abstraction else "optional",
                    "semantic_data": "connected" if self.service.semantic_data_abstraction else "optional"
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_connections_complete",
                success=True,
                details={
                    "knowledge_discovery": "connected",
                    "knowledge_governance": "connected",
                    "messaging": "connected",
                    "content_metadata": "connected" if self.service.content_metadata_abstraction else "optional",
                    "semantic_data": "connected" if self.service.semantic_data_abstraction else "optional"
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
