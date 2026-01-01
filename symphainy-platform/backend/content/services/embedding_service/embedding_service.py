#!/usr/bin/env python3
"""
Embedding Service - Phase 2: Enhanced Embedding Storage

WHAT: Creates semantic embeddings from parsed content with enhanced metadata
HOW: Uses StatelessHFInferenceAgent for embeddings, stores via SemanticDataAbstraction

Key Features:
- Representative sampling (every 10th row, not first 10 rows)
- Creates 3 embeddings per column (metadata, meaning, samples)
- Extracts and stores enhanced metadata (data_type, semantic_meaning, sample_values, etc.)
- Stores via SemanticDataAbstraction (ArangoDB)
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase

# Import micro-modules (will create these)
from .modules.initialization import Initialization
from .modules.embedding_creation import EmbeddingCreation
from .modules.utilities import Utilities


class EmbeddingService(RealmServiceBase):
    """
    Embedding enabling service for Business Enablement.
    
    Creates semantic embeddings from parsed content with enhanced metadata storage.
    Supports preview reconstruction from embeddings (Phase 2).
    
    Key Capabilities:
    - Representative sampling (every 10th row)
    - 3 embeddings per column (metadata, meaning, samples)
    - Enhanced metadata extraction (data_type, semantic_meaning, sample_values, etc.)
    - Stores via SemanticDataAbstraction (ArangoDB)
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Embedding Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Smart City service APIs (will be initialized in initialize())
        self.librarian = None
        self.content_steward = None  # For retrieving parsed files
        self.semantic_data = None  # SemanticDataAbstraction for storing embeddings
        self.nurse = None  # For observability
        
        # Embedding generation (HuggingFaceAdapter - PRIMARY PATHWAY ONLY)
        self.hf_adapter = None  # HuggingFace Inference Endpoint adapter (required)
        
        # LLM abstraction for semantic meaning inference
        self.llm_abstraction = None
        
        # Initialize micro-modules
        self.utilities_module = Utilities(self)
        self.initialization_module = Initialization(self)
        self.embedding_creation_module = EmbeddingCreation(self)
    
    async def initialize(self) -> bool:
        """Initialize Embedding Service."""
        await super().initialize()
        return await self.initialization_module.initialize()
    
    # SOA API Methods
    async def create_representative_embeddings(
        self,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        sampling_strategy: str = "every_nth",
        n: int = 10,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create representative embeddings from parsed content.
        
        Uses representative sampling (every 10th row) to create embeddings
        that capture the semantic meaning of columns without processing all data.
        
        Creates 3 embeddings per column:
        1. metadata_embedding: Column name + data type + structure
        2. meaning_embedding: Semantic meaning of the column
        3. samples_embedding: Representative sample values
        
        Also extracts and stores enhanced metadata for preview reconstruction:
        - data_type: Column data type (string, int, float, etc.)
        - semantic_meaning: Meaning as text (not just embedding)
        - sample_values: Sample values as text array (not just embedding)
        - row_count: Total row count
        - column_position: Column order
        - semantic_model_recommendation: Recommendation object
        
        Args:
            parsed_file_id: Parsed file identifier (parquet in GCS)
            content_metadata: Content metadata from parsing (includes schema, columns, etc.)
            sampling_strategy: Sampling strategy ("every_nth" for now)
            n: Sample every nth row (default: 10)
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Dict with success status, embeddings list, and counts
        """
        try:
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            self.logger.info(f"🧬 Creating representative embeddings: parsed_file_id={parsed_file_id} (workflow_id: {workflow_id})")
            
            # Delegate to embedding creation module
            result = await self.embedding_creation_module.create_representative_embeddings(
                parsed_file_id=parsed_file_id,
                content_metadata=content_metadata,
                sampling_strategy=sampling_strategy,
                n=n,
                user_context=user_context
            )
            
            if result.get("success"):
                self.logger.info(f"✅ Created {result.get('embeddings_count', 0)} embeddings (workflow_id: {workflow_id})")
                # Debug: Log content_id to verify it's in the result
                self.logger.info(f"🔍 [EmbeddingService] result keys: {list(result.keys()) if isinstance(result, dict) else 'NOT_A_DICT'}")
                self.logger.info(f"🔍 [EmbeddingService] result.get('content_id'): {result.get('content_id')}")
            else:
                self.logger.error(f"❌ Failed to create embeddings: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Embedding creation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self.handle_error_with_audit(e, "create_representative_embeddings")
            return {
                "success": False,
                "error": str(e),
                "embeddings": [],
                "embeddings_count": 0
            }
    
    async def list_embeddings(
        self,
        file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all embeddings for a file (or all for user).
        
        Args:
            file_id: Optional file ID to filter embeddings for a specific file
            user_context: Optional user context for security and tenant validation
        
        Returns:
            List of embeddings grouped by content_id with metadata
        """
        try:
            self.logger.info(f"📋 Listing embeddings" + (f" for file_id: {file_id}" if file_id else " for all files"))
            
            if not self.semantic_data:
                return {
                    "success": False,
                    "embeddings": [],
                    "count": 0,
                    "error": "SemanticDataAbstraction not available"
                }
            
            # Build filter conditions
            filters = {}
            if file_id:
                filters["file_id"] = file_id
            
            # Query embeddings
            # Note: get_semantic_embeddings() accepts content_id=None to query all
            print(f"[EMBEDDING_SERVICE] 🔍 Querying embeddings with filters: {filters}, content_id=None (all)")
            self.logger.info(f"🔍 Querying embeddings with filters: {filters}, content_id=None (all)")
            embeddings = await self.semantic_data.get_semantic_embeddings(
                content_id=None,  # Query all (filtered by file_id if provided)
                filters=filters,
                user_context=user_context
            )
            
            print(f"[EMBEDDING_SERVICE] 🔍 get_semantic_embeddings returned {len(embeddings) if embeddings else 0} embeddings")
            self.logger.info(f"🔍 get_semantic_embeddings returned {len(embeddings) if embeddings else 0} embeddings")
            if embeddings and len(embeddings) > 0:
                # Log first embedding structure
                self.logger.info(f"🔍 Sample embedding keys: {list(embeddings[0].keys())}")
                self.logger.info(f"🔍 Sample embedding: file_id={embeddings[0].get('file_id')}, parsed_file_id={embeddings[0].get('parsed_file_id')}, content_id={embeddings[0].get('content_id')}")
            
            if not embeddings:
                self.logger.warning(f"⚠️ No embeddings found in ArangoDB (filters: {filters})")
                return {
                    "success": True,
                    "embeddings": [],
                    "count": 0
                }
            
            # Group by content_id and file_id
            grouped = {}
            for emb in embeddings:
                content_id = emb.get("content_id")
                file_id_from_emb = emb.get("file_id")
                parsed_file_id = emb.get("parsed_file_id")  # ✅ NEW: Get parsed_file_id for matching
                key = f"{file_id_from_emb}_{content_id}"
                
                if key not in grouped:
                    grouped[key] = {
                        "file_id": file_id_from_emb,
                        "parsed_file_id": parsed_file_id,  # ✅ NEW: Include parsed_file_id in grouped result
                        "content_id": content_id,
                        "embeddings_count": 0,
                        "columns": [],
                        "created_at": emb.get("created_at")
                    }
                
                grouped[key]["embeddings_count"] += 1
                grouped[key]["columns"].append({
                    "column_name": emb.get("column_name"),
                    "data_type": emb.get("data_type"),
                    "semantic_meaning": emb.get("semantic_meaning"),
                    "semantic_id": emb.get("semantic_id")
                })
            
            # Convert to list
            embeddings_list = list(grouped.values())
            
            self.logger.info(f"✅ Found {len(embeddings_list)} embedding groups" + (f" for file_id: {file_id}" if file_id else ""))
            
            return {
                "success": True,
                "embeddings": embeddings_list,
                "count": len(embeddings_list)
            }
            
        except Exception as e:
            self.logger.error(f"❌ List embeddings failed: {e}", exc_info=True)
            return {
                "success": False,
                "embeddings": [],
                "count": 0,
                "error": str(e)
            }
    
    async def preview_embeddings(
        self,
        content_id: str,
        max_columns: int = 20,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Preview semantic layer (embeddings + metadata).
        
        Reconstructs preview from embeddings + metadata (not raw parsed data).
        
        Args:
            content_id: Content ID (semantic layer ID)
            max_columns: Maximum columns to return (default: 20)
            user_context: Optional user context for security and tenant validation
        
        Returns:
            Preview structure with columns, semantic meanings, sample values
        """
        try:
            self.logger.info(f"👁️ Previewing embeddings: content_id={content_id} (max_columns={max_columns})")
            
            if not self.semantic_data:
                return {
                    "success": False,
                    "error": "SemanticDataAbstraction not available"
                }
            
            # Get embeddings for this content_id
            embeddings = await self.semantic_data.get_semantic_embeddings(
                content_id=content_id,
                filters={},
                user_context=user_context
            )
            
            if not embeddings:
                return {
                    "success": False,
                    "error": f"No embeddings found for content_id: {content_id}"
                }
            
            # Sort embeddings by column_position for consistent preview
            embeddings.sort(key=lambda x: x.get("column_position", 0))
            
            # Build preview from embeddings + metadata
            columns = []
            for emb in embeddings[:max_columns]:
                columns.append({
                    "column_name": emb.get("column_name"),
                    "data_type": emb.get("data_type", "unknown"),
                    "semantic_meaning": emb.get("semantic_meaning", ""),
                    "semantic_id": emb.get("semantic_id"),
                    "sample_values": emb.get("sample_values", [])[:10],  # First 10 samples
                    "column_position": emb.get("column_position", 0),
                    "row_count": emb.get("row_count", 0),
                    "semantic_model_recommendation": emb.get("semantic_model_recommendation")
                })
            
            # Sort by column_position
            columns.sort(key=lambda x: x.get("column_position", 0))
            
            row_count = columns[0].get("row_count", 0) if columns else 0
            if not row_count and embeddings and embeddings[0].get("content_metadata"):
                row_count = embeddings[0].get("content_metadata", {}).get("record_count", 0)
            
            return {
                "success": True,
                "content_id": content_id,
                "file_id": embeddings[0].get("file_id") if embeddings else None,
                "columns": columns,
                "structure": {
                    "column_count": len(embeddings),
                    "row_count": row_count,
                    "semantic_insights_summary": [
                        f"Semantic meaning for {col['column_name']}: {col['semantic_meaning']}"
                        for col in columns
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Preview embeddings failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

