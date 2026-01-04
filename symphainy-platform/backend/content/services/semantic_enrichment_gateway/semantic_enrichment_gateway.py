#!/usr/bin/env python3
"""
Semantic Enrichment Gateway - Phase 4: Security Boundary for Semantic Enrichment

WHAT: Enables semantic enrichment without exposing parsed data
HOW: Requests enrichment, enrichment service creates new embeddings, adds to semantic layer

Key Features:
- Maintains security boundary (platform uses semantic data only)
- Requests enrichment when embeddings lack information
- Enrichment service (secure boundary) processes parsed data
- Creates new embeddings and adds to semantic layer
- Returns embedding IDs (not raw data)
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase

# Import micro-modules
from .modules.initialization import Initialization
from .modules.utilities import Utilities
from .modules.enrichment import Enrichment


class SemanticEnrichmentGateway(RealmServiceBase):
    """
    Semantic Enrichment Gateway enabling service for Business Enablement.
    
    Maintains security boundary while enabling semantic enrichment when embeddings
    don't have enough information. The platform uses semantic data only, but can
    request enrichment when needed.
    
    Key Capabilities:
    - Validates enrichment requests (what semantic info is needed)
    - Requests enrichment from secure boundary service
    - Stores new embeddings in semantic layer
    - Returns embedding IDs (not raw data)
    
    Security Pattern:
    - Platform identifies what semantic info is missing
    - Requests enrichment (describes what's needed, not raw data)
    - Enrichment service (runs in secure boundary) processes parsed data
    - Creates new embeddings with requested semantic info
    - Adds to semantic layer
    - Returns new embedding IDs (not raw data)
    
    Integrates with Smart City services for semantic data access and storage.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Semantic Enrichment Gateway."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Smart City service APIs (will be initialized in initialize())
        self.librarian = None
        self.semantic_data = None  # SemanticDataAbstraction for storing embeddings
        self.data_steward = None  # For enrichment service (secure boundary)
        self.nurse = None  # For observability
        
        # Enrichment service (runs in secure boundary - can access parsed data)
        self.enrichment_service = None  # Will be initialized if available
        
        # Initialize micro-modules
        self.utilities_module = Utilities(self)
        self.initialization_module = Initialization(self)
        self.enrichment_module = Enrichment(self)
    
    async def initialize(self) -> bool:
        """Initialize Semantic Enrichment Gateway."""
        await super().initialize()
        return await self.initialization_module.initialize()
    
    # SOA API Methods
    
    async def enrich_semantic_layer(
        self,
        content_id: str,
        enrichment_request: Dict[str, Any],  # What semantic info is needed
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Request semantic enrichment without exposing parsed data.
        
        Flow:
        1. Platform identifies what semantic info is missing
        2. Requests enrichment (describes what's needed, not raw data)
        3. Enrichment service (runs in secure boundary) processes parsed data
        4. Creates new embeddings with requested semantic info
        5. Adds to semantic layer
        6. Returns new embedding IDs (not raw data)
        
        Args:
            content_id: Content metadata ID
            enrichment_request: Dict describing what semantic info is needed:
                {
                    "type": str,  # "column_values", "statistics", "correlations", etc.
                    "filters": Dict[str, Any],  # Optional: Which columns/rows needed
                    "description": str  # Optional: Human-readable description
                }
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with enrichment results:
            {
                "success": bool,
                "content_id": str,
                "embedding_ids": List[str],  # New embedding IDs (not raw data)
                "enrichment_type": str,
                "count": int
            }
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "enrich_semantic_layer_start",
                success=True,
                details={
                    "content_id": content_id,
                    "enrichment_type": enrichment_request.get("type")
                }
            )
            
            # Step 1: Validate request (what semantic info is needed)
            validation_result = self.enrichment_module.validate_enrichment_request(enrichment_request)
            if not validation_result.get("valid"):
                return {
                    "success": False,
                    "error": validation_result.get("error", "Invalid enrichment request"),
                    "content_id": content_id
                }
            
            enrichment_type = enrichment_request.get("type")
            
            # Step 2: Request enrichment from secure service
            # This service runs in secure boundary and can access parsed data
            enrichment_service = await self.enrichment_module.get_enrichment_service()
            
            if not enrichment_service:
                self.logger.warning("⚠️ Enrichment service not available - enrichment cannot be performed")
                return {
                    "success": False,
                    "error": "Enrichment service not available",
                    "content_id": content_id
                }
            
            # Step 3: Enrichment service processes parsed data and creates embeddings
            new_embeddings = await enrichment_service.create_enrichment_embeddings(
                content_id=content_id,
                enrichment_type=enrichment_type,
                filters=enrichment_request.get("filters"),  # Which columns/rows needed
                user_context=user_context
            )
            
            if not new_embeddings:
                return {
                    "success": False,
                    "error": "Enrichment failed to create embeddings",
                    "content_id": content_id
                }
            
            # Step 4: Store new embeddings in semantic layer
            store_result = await self.enrichment_module.store_enriched_embeddings(
                content_id=content_id,
                embeddings=new_embeddings,
                user_context=user_context
            )
            
            if not store_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to store enriched embeddings",
                    "store_error": store_result.get("error"),
                    "content_id": content_id
                }
            
            # Step 5: Return embedding IDs (platform can query these)
            embedding_ids = [emb.get("_key") or emb.get("id") for emb in new_embeddings if emb.get("_key") or emb.get("id")]
            
            result = {
                "success": True,
                "content_id": content_id,
                "embedding_ids": embedding_ids,
                "enrichment_type": enrichment_type,
                "count": len(embedding_ids)
            }
            
            # Record completion
            await self.log_operation_with_telemetry(
                "enrich_semantic_layer_complete",
                success=True,
                details=result
            )
            
            self.logger.info(f"✅ Semantic enrichment completed: {enrichment_type}, {len(embedding_ids)} embeddings created")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Semantic enrichment failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Record failure
            await self.log_operation_with_telemetry(
                "enrich_semantic_layer_failed",
                success=False,
                details={"error": str(e), "content_id": content_id}
            )
            
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }

