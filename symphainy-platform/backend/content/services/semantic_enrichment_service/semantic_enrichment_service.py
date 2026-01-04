#!/usr/bin/env python3
"""
Semantic Enrichment Service - Phase 4: Secure Boundary Service

WHAT: Processes parsed data to create new semantic embeddings
HOW: Runs in secure boundary, can access parsed data, creates embeddings, returns them (not raw data)

Key Features:
- ONLY service that can access parsed data
- Creates new embeddings from parsed data
- Returns embeddings (not raw data)
- Maintains security boundary
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase

# Import micro-modules
from .modules.initialization import Initialization
from .modules.utilities import Utilities
from .modules.embedding_creation import EmbeddingCreation


class SemanticEnrichmentService(RealmServiceBase):
    """
    Semantic Enrichment Service - Runs in secure boundary.
    
    This service CAN access parsed data to create new embeddings.
    It's the only service that crosses the security boundary.
    
    Key Capabilities:
    - Accesses parsed data (ONLY place this happens)
    - Creates new embeddings from parsed data
    - Returns embeddings (not raw data)
    - Maintains security boundary
    
    Security Pattern:
    - This service is the ONLY place where parsed data is accessed
    - New embeddings are created and returned (not raw data)
    - Platform never sees raw parsed data
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Semantic Enrichment Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Smart City service APIs (will be initialized in initialize())
        self.librarian = None
        self.data_steward = None  # For retrieving parsed files (SECURE BOUNDARY)
        self.nurse = None  # For observability
        
        # Initialize micro-modules
        self.utilities_module = Utilities(self)
        self.initialization_module = Initialization(self)
        self.embedding_creation_module = EmbeddingCreation(self)
    
    async def initialize(self) -> bool:
        """Initialize Semantic Enrichment Service."""
        await super().initialize()
        return await self.initialization_module.initialize()
    
    # SOA API Methods
    
    async def create_enrichment_embeddings(
        self,
        content_id: str,
        enrichment_type: str,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create new embeddings from parsed data.
        
        This is the ONLY place where parsed data is accessed.
        New embeddings are created and returned (not raw data).
        
        Args:
            content_id: Content metadata ID
            enrichment_type: Type of enrichment ("column_values", "statistics", etc.)
            filters: Optional filters (which columns/rows needed)
            user_context: Optional user context
            
        Returns:
            List of new embeddings (not raw data):
            [
                {
                    "_key": str,
                    "content_id": str,
                    "embedding_type": str,
                    "metadata": Dict[str, Any],
                    ...
                },
                ...
            ]
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "create_enrichment_embeddings_start",
                success=True,
                details={
                    "content_id": content_id,
                    "enrichment_type": enrichment_type
                }
            )
            
            # Step 1: Get parsed data (ONLY place this happens)
            parsed_file = await self.embedding_creation_module.get_parsed_file(
                content_id=content_id,
                user_context=user_context
            )
            
            if not parsed_file:
                self.logger.warning(f"⚠️ Parsed file not found for content_id: {content_id}")
                return []
            
            # Step 2: Process parsed data based on enrichment type
            if enrichment_type == "column_values":
                new_embeddings = await self.embedding_creation_module.create_column_value_embeddings(
                    parsed_file=parsed_file,
                    content_id=content_id,
                    filters=filters,
                    user_context=user_context
                )
            elif enrichment_type == "statistics":
                new_embeddings = await self.embedding_creation_module.create_statistics_embeddings(
                    parsed_file=parsed_file,
                    content_id=content_id,
                    filters=filters,
                    user_context=user_context
                )
            elif enrichment_type == "correlations":
                new_embeddings = await self.embedding_creation_module.create_correlation_embeddings(
                    parsed_file=parsed_file,
                    content_id=content_id,
                    filters=filters,
                    user_context=user_context
                )
            elif enrichment_type == "distributions":
                new_embeddings = await self.embedding_creation_module.create_distribution_embeddings(
                    parsed_file=parsed_file,
                    content_id=content_id,
                    filters=filters,
                    user_context=user_context
                )
            elif enrichment_type == "missing_values":
                new_embeddings = await self.embedding_creation_module.create_missing_value_embeddings(
                    parsed_file=parsed_file,
                    content_id=content_id,
                    filters=filters,
                    user_context=user_context
                )
            else:
                self.logger.warning(f"⚠️ Unknown enrichment type: {enrichment_type}")
                return []
            
            # Step 3: Return new embeddings (not raw data)
            if not new_embeddings:
                self.logger.warning(f"⚠️ No embeddings created for enrichment_type: {enrichment_type}")
                return []
            
            # Record completion
            await self.log_operation_with_telemetry(
                "create_enrichment_embeddings_complete",
                success=True,
                details={
                    "content_id": content_id,
                    "enrichment_type": enrichment_type,
                    "count": len(new_embeddings)
                }
            )
            
            self.logger.info(f"✅ Created {len(new_embeddings)} enrichment embeddings for type: {enrichment_type}")
            
            return new_embeddings
            
        except Exception as e:
            self.logger.error(f"❌ Enrichment embedding creation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Record failure
            await self.log_operation_with_telemetry(
                "create_enrichment_embeddings_failed",
                success=False,
                details={"error": str(e), "content_id": content_id}
            )
            
            return []

