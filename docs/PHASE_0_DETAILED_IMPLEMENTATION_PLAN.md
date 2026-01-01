# Phase 0: Detailed Implementation Plan
## Data Steward Consolidation & Data Mash Flow

**Date:** January 2025  
**Status:** 🎯 **READY FOR IMPLEMENTATION**  
**Based on:** DATA_MASH_VISION_GAP_ANALYSIS.md

---

## Executive Summary

This document provides a detailed, step-by-step implementation plan for Phase 0, which establishes the foundation for the data mash vision:
1. **Data Steward Consolidation** - Merge Content Steward and Data Steward into a single service
2. **Data Mash Flow** - Implement explicit, traceable data flow from infrastructure → semantic layer
3. **Data Classification** - Implement platform vs client data distinction using `data_classification` field
4. **Parsed Data Storage** - Store parsed data in GCS (Parquet files) + Supabase (metadata)

---

## Approved Decisions

### Decision 1: Platform vs Client Data Classification ✅

**Approach:** Use `data_classification` field (not just `tenant_id`).

- **Platform Data:** `data_classification = "platform"` (tenant_id optional for attribution)
- **Client Data:** `data_classification = "client"` AND `tenant_id != NULL` (required)

**Rationale:** Enables tenant attribution for platform data (e.g., to see which tenant is experiencing errors) while maintaining clear distinction.

### Decision 2: Parsed Data Storage ✅

**Decision:** Store parsed data using Supabase/GCS pattern (NOT ArangoDB).

- **Parsed Data Files (Parquet):** Store in GCS (binary storage)
- **Parsed Data Metadata:** Store in Supabase (metadata table)
- **Semantic Connections:** Store in ArangoDB (links to semantic data)

**Rationale:** 
- ArangoDB is not suitable for large Parquet files or DataFrames (pandas DataFrames or Parquet files)
- Follows existing file storage pattern for consistency (GCS for binaries, Supabase for metadata)
- Enables real-world simplicity: easier to document known transformations on parsed data

### Decision 3: ArangoDB Collection Initialization ✅

**Decision:** Explicit initialization script.

- Create initialization script to create collections and indexes
- Run as part of deployment process
- Enables index creation and schema validation

---

## Phase 0.1: Data Steward Consolidation (Week 1-2)

### Goal
Consolidate Content Steward and Data Steward into a single `Data Steward` service with clear module separation and data classification support.

---

### Step 1.1: Infrastructure Setup

#### 1.1.1: Create ArangoDB Collection Initialization Script

**File:** `scripts/initialize_arangodb_collections.py`

**Purpose:** Create all ArangoDB collections and indexes needed for semantic data layer.

**Collections to Create:**
- `content_metadata` (document collection)
- `structured_embeddings` (document collection)
- `semantic_graph_nodes` (document collection)
- `semantic_graph_edges` (edge collection)

**Note:** Parsed data is NOT stored in ArangoDB. It is stored in GCS (Parquet files) + Supabase (metadata), following the existing file storage pattern.

**Indexes to Create:**
- All collections: Index on `data_classification`
- All collections: Index on `tenant_id`
- All collections: Composite index on `(data_classification, tenant_id)`
- `content_metadata`: Index on `file_id`
- `structured_embeddings`: Index on `content_id`, `file_id`, `semantic_id`
- `semantic_graph_nodes`: Index on `content_id`, `file_id`, `entity_id`
- `semantic_graph_edges`: Index on `content_id`, `file_id`, `source_entity_id`, `target_entity_id`

**Implementation:**
```python
#!/usr/bin/env python3
"""
ArangoDB Collection Initialization Script

Creates all collections and indexes needed for semantic data layer.
Run this script as part of deployment process.
"""

import asyncio
from typing import Dict, Any, List
from foundations.public_works_foundation.infrastructure_adapters.arango_adapter import ArangoAdapter

async def initialize_collections(arango_adapter: ArangoAdapter) -> Dict[str, Any]:
    """Initialize all ArangoDB collections and indexes."""
    results = {}
    
    # Collections to create
    collections = [
        {
            "name": "content_metadata",
            "type": "document"
        },
        {
            "name": "structured_embeddings",
            "type": "document"
        },
        {
            "name": "semantic_graph_nodes",
            "type": "document"
        },
        {
            "name": "semantic_graph_edges",
            "type": "edge"
        }
    ]
    
    # Create collections
    for collection in collections:
        try:
            await arango_adapter.create_collection(collection["name"], collection["type"])
            results[collection["name"]] = "created"
        except Exception as e:
            results[collection["name"]] = f"error: {str(e)}"
    
    # Create indexes for each collection
    index_definitions = [
        # Common indexes for all collections
        {
            "collection": "content_metadata",
            "indexes": [
                {"type": "persistent", "fields": ["data_classification"]},
                {"type": "persistent", "fields": ["tenant_id"]},
                {"type": "persistent", "fields": ["data_classification", "tenant_id"]},
                {"type": "persistent", "fields": ["file_id"]}
            ]
        },
        {
            "collection": "structured_embeddings",
            "indexes": [
                {"type": "persistent", "fields": ["data_classification"]},
                {"type": "persistent", "fields": ["tenant_id"]},
                {"type": "persistent", "fields": ["data_classification", "tenant_id"]},
                {"type": "persistent", "fields": ["content_id"]},
                {"type": "persistent", "fields": ["file_id"]},
                {"type": "persistent", "fields": ["semantic_id"]}
            ]
        },
        {
            "collection": "semantic_graph_nodes",
            "indexes": [
                {"type": "persistent", "fields": ["data_classification"]},
                {"type": "persistent", "fields": ["tenant_id"]},
                {"type": "persistent", "fields": ["data_classification", "tenant_id"]},
                {"type": "persistent", "fields": ["content_id"]},
                {"type": "persistent", "fields": ["file_id"]},
                {"type": "persistent", "fields": ["entity_id"]}
            ]
        },
        {
            "collection": "semantic_graph_edges",
            "indexes": [
                {"type": "persistent", "fields": ["data_classification"]},
                {"type": "persistent", "fields": ["tenant_id"]},
                {"type": "persistent", "fields": ["data_classification", "tenant_id"]},
                {"type": "persistent", "fields": ["content_id"]},
                {"type": "persistent", "fields": ["file_id"]},
                {"type": "persistent", "fields": ["source_entity_id"]},
                {"type": "persistent", "fields": ["target_entity_id"]}
            ]
        }
    ]
    
    # Create indexes
    for collection_def in index_definitions:
        collection_name = collection_def["collection"]
        for index_def in collection_def["indexes"]:
            try:
                await arango_adapter.create_index(
                    collection_name,
                    index_def["type"],
                    index_def["fields"]
                )
                results[f"{collection_name}_{index_def['fields']}"] = "created"
            except Exception as e:
                results[f"{collection_name}_{index_def['fields']}"] = f"error: {str(e)}"
    
    return results
```

**Testing:**
- Run script and verify all collections created
- Verify all indexes created
- Test query performance with indexes

---

#### 1.1.2: Create Supabase Schema for Parsed Data

**File:** `foundations/public_works_foundation/sql/create_parsed_data_schema.sql`

**Purpose:** Create Supabase table for parsed data metadata.

**Schema:**
```sql
-- =============================================================================
-- PARSED DATA METADATA TABLE
-- =============================================================================
-- Stores metadata for parsed data files (Parquet files stored in GCS)
-- =============================================================================

CREATE TABLE IF NOT EXISTS parsed_data_files (
  -- Core Identifiers
  uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_id UUID NOT NULL,                    -- Original file UUID (from project_files)
  parsed_file_id TEXT NOT NULL,             -- GCS path or identifier for parsed file
  
  -- Data Classification
  data_classification TEXT NOT NULL CHECK (data_classification IN ('platform', 'client')),
  tenant_id TEXT,                           -- Required if data_classification = 'client'
  
  -- Parsed Data Information
  format_type TEXT NOT NULL,                -- 'parquet', 'json_structured', 'json_chunks'
  content_type TEXT CHECK (content_type IN ('structured', 'unstructured', 'hybrid')),
  
  -- File Information
  file_size BIGINT,                         -- Parsed file size in bytes
  row_count INTEGER,                         -- Number of rows (for structured data)
  column_count INTEGER,                      -- Number of columns (for structured data)
  column_names JSONB,                       -- Array of column names
  data_types JSONB,                         -- Column data types
  
  -- Processing Information
  parsed_at TIMESTAMPTZ DEFAULT now(),
  parsed_by TEXT,                           -- Service/user that performed parsing
  parse_options JSONB,                      -- Options used for parsing
  
  -- Status & Processing
  status TEXT NOT NULL DEFAULT 'parsed',    -- parsed, processing, completed, failed
  processing_status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
  processing_errors JSONB,                  -- Error details if processing failed
  
  -- Metadata
  metadata JSONB,                           -- Additional metadata
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_file_id ON parsed_data_files(file_id);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_data_classification ON parsed_data_files(data_classification);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_tenant_id ON parsed_data_files(tenant_id);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_classification_tenant ON parsed_data_files(data_classification, tenant_id);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_status ON parsed_data_files(status);
```

**Testing:**
- Run migration script
- Verify table created
- Verify indexes created
- Test insert/query operations

---

### Step 1.2: Update FileManagementAbstraction

#### 1.2.1: Add `data_classification` Field Support

**File:** `foundations/public_works_foundation/infrastructure_abstractions/file_management_abstraction.py`

**Changes:**
1. Add `data_classification` field to file metadata
2. Add validation for platform vs client data
3. Add platform/client query methods

**New Methods:**
```python
async def list_platform_files(
    self,
    tenant_id: Optional[str] = None,  # Optional: filter by tenant for attribution
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    List platform files (data_classification = "platform").
    
    tenant_id can be provided to filter platform data by tenant attribution
    (e.g., to see which tenant is experiencing errors).
    """
    filter_conditions = {"data_classification": "platform"}
    if tenant_id is not None:
        filter_conditions["tenant_id"] = tenant_id
    # Query Supabase with filters
    ...

async def list_client_files(
    self,
    tenant_id: str,  # Required for client data
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    List client files (data_classification = "client" AND tenant_id = provided tenant_id).
    """
    filter_conditions = {
        "data_classification": "client",
        "tenant_id": tenant_id
    }
    # Query Supabase with filters
    ...

async def create_file(
    self,
    file_id: str,
    file_data: bytes,
    metadata: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create file with data classification validation.
    """
    # Validate data_classification
    data_classification = metadata.get("data_classification")
    tenant_id = metadata.get("tenant_id")
    
    if data_classification == "client" and not tenant_id:
        raise ValueError("Client data must have tenant_id")
    
    if data_classification not in ["platform", "client"]:
        raise ValueError("data_classification must be 'platform' or 'client'")
    
    # Store file in GCS
    # Store metadata in Supabase with data_classification
    ...
```

**Testing:**
- Test platform file creation (with and without tenant_id)
- Test client file creation (with tenant_id)
- Test validation errors (client without tenant_id)
- Test platform/client query methods

---

### Step 1.3: Update ContentMetadataAbstraction

#### 1.3.1: Add `data_classification` Field and Tenant Filtering

**File:** `foundations/public_works_foundation/infrastructure_abstractions/content_metadata_abstraction.py`

**Changes:**
1. Add `data_classification` field to all semantic data storage
2. Add tenant filtering to all query methods
3. Add platform/client query methods

**Updated Methods:**
```python
async def store_semantic_embeddings(
    self,
    content_id: str,
    file_id: str,
    embeddings: List[Dict[str, Any]],
    data_classification: str,  # NEW: "platform" or "client"
    tenant_id: Optional[str] = None,  # NEW: Required if data_classification = "client"
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store semantic embeddings with data classification.
    """
    # Validate data_classification
    if data_classification == "client" and not tenant_id:
        raise ValueError("Client data must have tenant_id")
    
    for emb in embeddings:
        embedding_doc = {
            "_key": f"emb_{file_id}_{emb.get('column_name', 'unknown')}",
            "content_id": content_id,
            "file_id": file_id,
            "data_classification": data_classification,  # NEW
            "tenant_id": tenant_id,  # NEW
            "column_name": emb.get("column_name"),
            "metadata_embedding": emb.get("metadata_embedding"),
            "meaning_embedding": emb.get("meaning_embedding"),
            "samples_embedding": emb.get("samples_embedding"),
            "semantic_id": emb.get("semantic_id"),
            "created_at": datetime.utcnow().isoformat()
        }
        await self.arango_adapter.create_document(
            self.structured_embeddings_collection,
            embedding_doc
        )
    ...

async def get_semantic_embeddings(
    self,
    content_id: str,
    data_classification: Optional[str] = None,  # NEW: "platform" or "client"
    tenant_id: Optional[str] = None  # NEW: Required if data_classification = "client"
) -> List[Dict[str, Any]]:
    """
    Get semantic embeddings with data classification and tenant filtering.
    """
    filter_conditions = {"content_id": content_id}
    if data_classification:
        filter_conditions["data_classification"] = data_classification
    if tenant_id is not None:
        filter_conditions["tenant_id"] = tenant_id
    # If data_classification = "client", tenant_id is required
    if data_classification == "client" and not tenant_id:
        raise ValueError("Client data queries require tenant_id")
    ...

async def query_platform_semantic_embeddings(
    self,
    tenant_id: Optional[str] = None,  # Optional: filter by tenant for attribution
    filters: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Query platform semantic embeddings (data_classification = "platform").
    """
    filter_conditions = {"data_classification": "platform"}
    if tenant_id is not None:
        filter_conditions["tenant_id"] = tenant_id
    if filters:
        filter_conditions.update(filters)
    ...

async def query_client_semantic_embeddings(
    self,
    tenant_id: str,  # Required for client data
    filters: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Query client semantic embeddings (data_classification = "client" AND tenant_id = provided tenant_id).
    """
    filter_conditions = {
        "data_classification": "client",
        "tenant_id": tenant_id
    }
    if filters:
        filter_conditions.update(filters)
    ...
```

**Testing:**
- Test semantic embedding storage with data_classification
- Test validation (client without tenant_id)
- Test platform/client query methods
- Test tenant filtering

---

### Step 1.4: Create Parsed Data Storage Abstraction

#### 1.4.1: Create ParsedDataAbstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/parsed_data_abstraction.py`

**Purpose:** Abstraction for storing and retrieving parsed data (Parquet files in GCS + metadata in Supabase).

**Implementation:**
```python
#!/usr/bin/env python3
"""
Parsed Data Abstraction

Stores parsed data files (Parquet) in GCS and metadata in Supabase.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

class ParsedDataAbstraction:
    """Abstraction for parsed data storage (GCS + Supabase)."""
    
    def __init__(self, gcs_adapter: Any, supabase_adapter: Any):
        self.gcs_adapter = gcs_adapter
        self.supabase_adapter = supabase_adapter
        self.logger = None  # Set via DI container
    
    async def store_parsed_data(
        self,
        file_id: str,
        parsed_data: bytes,  # Parquet file bytes
        format_type: str,  # 'parquet', 'json_structured', 'json_chunks'
        metadata: Dict[str, Any],
        data_classification: str,  # 'platform' or 'client'
        tenant_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store parsed data file in GCS and metadata in Supabase.
        """
        # Validate data_classification
        if data_classification == "client" and not tenant_id:
            raise ValueError("Client data must have tenant_id")
        
        # Generate parsed file ID
        parsed_file_id = f"parsed_{uuid.uuid4()}"
        
        # Store file in GCS
        gcs_path = f"parsed_data/{parsed_file_id}.{format_type}"
        await self.gcs_adapter.upload_file(gcs_path, parsed_data)
        
        # Store metadata in Supabase
        metadata_doc = {
            "file_id": file_id,
            "parsed_file_id": parsed_file_id,
            "data_classification": data_classification,
            "tenant_id": tenant_id,
            "format_type": format_type,
            "content_type": metadata.get("content_type"),
            "file_size": len(parsed_data),
            "row_count": metadata.get("row_count"),
            "column_count": metadata.get("column_count"),
            "column_names": metadata.get("column_names"),
            "data_types": metadata.get("data_types"),
            "parsed_at": datetime.utcnow().isoformat(),
            "status": "parsed"
        }
        
        result = await self.supabase_adapter.insert(
            "parsed_data_files",
            metadata_doc
        )
        
        return {
            "success": True,
            "parsed_file_id": parsed_file_id,
            "gcs_path": gcs_path,
            "metadata_id": result.get("uuid")
        }
    
    async def get_parsed_data(
        self,
        parsed_file_id: str,
        data_classification: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get parsed data file from GCS and metadata from Supabase.
        """
        # Get metadata from Supabase
        metadata = await self.supabase_adapter.select(
            "parsed_data_files",
            {"parsed_file_id": parsed_file_id}
        )
        
        if not metadata:
            return {"success": False, "error": "Parsed data not found"}
        
        # Validate data_classification and tenant_id
        if data_classification and metadata["data_classification"] != data_classification:
            return {"success": False, "error": "Data classification mismatch"}
        
        if tenant_id and metadata["tenant_id"] != tenant_id:
            return {"success": False, "error": "Tenant ID mismatch"}
        
        # Get file from GCS
        gcs_path = f"parsed_data/{parsed_file_id}.{metadata['format_type']}"
        file_data = await self.gcs_adapter.download_file(gcs_path)
        
        return {
            "success": True,
            "file_data": file_data,
            "metadata": metadata
        }
    
    async def query_platform_parsed_data(
        self,
        tenant_id: Optional[str] = None,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Query platform parsed data (data_classification = "platform").
        """
        filter_conditions = {"data_classification": "platform"}
        if tenant_id is not None:
            filter_conditions["tenant_id"] = tenant_id
        if filters:
            filter_conditions.update(filters)
        
        return await self.supabase_adapter.select(
            "parsed_data_files",
            filter_conditions
        )
    
    async def query_client_parsed_data(
        self,
        tenant_id: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Query client parsed data (data_classification = "client" AND tenant_id = provided tenant_id).
        """
        filter_conditions = {
            "data_classification": "client",
            "tenant_id": tenant_id
        }
        if filters:
            filter_conditions.update(filters)
        
        return await self.supabase_adapter.select(
            "parsed_data_files",
            filter_conditions
        )
```

**Testing:**
- Test parsed data storage (GCS + Supabase)
- Test validation (client without tenant_id)
- Test platform/client query methods
- Test file retrieval from GCS

---

### Step 1.5: Complete Data Steward Consolidation

#### 1.5.1: Update Data Steward Service

**File:** `backend/smart_city/services/data_steward/data_steward_service.py`

**Changes:**
1. Ensure file_lifecycle module is integrated
2. Add data_governance module (with data_classification support)
3. Add data_query module (with platform/client queries)

#### 1.5.2: Implement Data Query Module

**File:** `backend/smart_city/services/data_steward/modules/data_query.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""
Data Steward Service - Data Query Module

Micro-module for querying all data types:
- Platform data queries (files, parsed data, semantic data)
- Client data queries (files, parsed data, semantic data)
"""

import logging
from typing import Any, Dict, Optional, List

class DataQuery:
    """Data query module for all data types."""

    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")

    async def query_platform_files(
        self,
        tenant_id: Optional[str] = None,
        filters: Dict[str, Any] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query platform files (data_classification = "platform")."""
        file_management = self.service.file_management_abstraction
        if not file_management:
            return {"success": False, "error": "File Management Abstraction not available"}
        
        files = await file_management.list_platform_files(
            tenant_id=tenant_id,
            filters=filters
        )
        return {"success": True, "files": files}

    async def query_platform_parsed_data(
        self,
        tenant_id: Optional[str] = None,
        filters: Dict[str, Any] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query platform parsed data (data_classification = "platform")."""
        parsed_data_abstraction = self.service.get_abstraction("parsed_data")
        if not parsed_data_abstraction:
            return {"success": False, "error": "Parsed Data Abstraction not available"}
        
        parsed_data = await parsed_data_abstraction.query_platform_parsed_data(
            tenant_id=tenant_id,
            filters=filters
        )
        return {"success": True, "parsed_data": parsed_data}

    async def query_platform_semantic_embeddings(
        self,
        tenant_id: Optional[str] = None,
        filters: Dict[str, Any] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query platform semantic embeddings (data_classification = "platform")."""
        content_metadata = self.service.content_metadata_abstraction
        if not content_metadata:
            return {"success": False, "error": "Content Metadata Abstraction not available"}
        
        embeddings = await content_metadata.query_platform_semantic_embeddings(
            tenant_id=tenant_id,
            filters=filters
        )
        return {"success": True, "embeddings": embeddings}

    async def query_client_files(
        self,
        tenant_id: str,
        filters: Dict[str, Any] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query client files (data_classification = "client" AND tenant_id = provided tenant_id)."""
        file_management = self.service.file_management_abstraction
        if not file_management:
            return {"success": False, "error": "File Management Abstraction not available"}
        
        files = await file_management.list_client_files(
            tenant_id=tenant_id,
            filters=filters
        )
        return {"success": True, "files": files}

    async def query_client_parsed_data(
        self,
        tenant_id: str,
        filters: Dict[str, Any] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query client parsed data (data_classification = "client" AND tenant_id = provided tenant_id)."""
        parsed_data_abstraction = self.service.get_abstraction("parsed_data")
        if not parsed_data_abstraction:
            return {"success": False, "error": "Parsed Data Abstraction not available"}
        
        parsed_data = await parsed_data_abstraction.query_client_parsed_data(
            tenant_id=tenant_id,
            filters=filters
        )
        return {"success": True, "parsed_data": parsed_data}

    async def query_client_semantic_embeddings(
        self,
        tenant_id: str,
        filters: Dict[str, Any] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query client semantic embeddings (data_classification = "client" AND tenant_id = provided tenant_id)."""
        content_metadata = self.service.content_metadata_abstraction
        if not content_metadata:
            return {"success": False, "error": "Content Metadata Abstraction not available"}
        
        embeddings = await content_metadata.query_client_semantic_embeddings(
            tenant_id=tenant_id,
            filters=filters
        )
        return {"success": True, "embeddings": embeddings}
```

#### 1.5.3: Implement Data Governance Module

**File:** `backend/smart_city/services/data_steward/modules/data_governance.py`

**Implementation:**
```python
#!/usr/bin/env python3
"""
Data Steward Service - Data Governance Module

Micro-module for data governance operations across all data types.
"""

import logging
from typing import Any, Dict, Optional, List

class DataGovernance:
    """Data governance module for Data Steward service."""

    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")

    async def govern_platform_file_metadata(
        self,
        file_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Govern platform file metadata (data_classification = "platform")."""
        # Apply platform data governance policies
        # Validate data_classification = "platform"
        # Apply retention policies
        # Apply access controls
        ...

    async def govern_client_file_metadata(
        self,
        file_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Govern client file metadata (data_classification = "client" AND tenant_id)."""
        # Apply client data governance policies
        # Validate data_classification = "client" AND tenant_id
        # Apply tenant isolation
        # Apply retention policies
        ...

    async def govern_platform_parsed_data(
        self,
        parsed_file_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Govern platform parsed data (data_classification = "platform")."""
        # Apply platform data governance policies
        ...

    async def govern_client_parsed_data(
        self,
        parsed_file_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Govern client parsed data (data_classification = "client" AND tenant_id)."""
        # Apply client data governance policies
        # Validate tenant isolation
        ...

    async def govern_semantic_data(
        self,
        content_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Govern semantic data (embeddings/graphs)."""
        # Apply semantic data governance policies
        # Validate data_classification
        # Apply tenant isolation for client data
        ...

    async def apply_quality_policy(
        self,
        data_id: str,
        data_type: str,  # 'file', 'parsed_data', 'semantic'
        policy_id: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Apply quality policy to data."""
        # Apply quality policy based on data_type
        ...

    async def track_lineage(
        self,
        lineage_data: Dict[str, Any],
        user_context: Optional[Dict] = None
    ) -> str:
        """Track data lineage."""
        # Track lineage: file → parsed_data → semantic_data
        ...
```

---

## Phase 0.2: Data Mash Flow Implementation (Week 3-4)

### Goal
Implement explicit, traceable data mash flow with semantic layer storage.

---

### Step 2.1: Create DataMashSolutionOrchestrator

**File:** `backend/business_enablement/delivery_manager/solution_orchestrators/data_mash_solution_orchestrator/data_mash_solution_orchestrator.py`

**Purpose:** Orchestrates end-to-end data mash flow with explicit handoffs and trace IDs.

**Implementation:**
```python
#!/usr/bin/env python3
"""
Data Mash Solution Orchestrator

Orchestrates end-to-end data mash flow:
1. File upload → Data Steward (file lifecycle)
2. File parsing → FileParserService
3. Parsed data storage → ParsedDataAbstraction (GCS + Supabase)
4. Semantic processing → StatelessHFInferenceAgent
5. Semantic storage → ContentMetadataAbstraction (ArangoDB)
6. Insights/Operations → Semantic layer queries
"""

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from bases.orchestrator_base import OrchestratorBase

class DataMashSolutionOrchestrator(OrchestratorBase):
    """Data Mash Solution Orchestrator."""
    
    async def orchestrate_data_mash(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate complete data mash flow.
        
        Returns:
            Dict with all handoff results and trace_id for end-to-end tracking
        """
        # Generate trace_id for end-to-end tracking
        trace_id = str(uuid.uuid4())
        
        results = {}
        
        try:
            # Step 1: File validation (Data Steward)
            file_result = await self._validate_file(file_id, trace_id, user_context)
            results["file_result"] = file_result
            
            if not file_result.get("success"):
                return {
                    "success": False,
                    "trace_id": trace_id,
                    "error": "File validation failed",
                    "results": results
                }
            
            # Step 2: File parsing (FileParserService)
            parse_result = await self._parse_file(file_id, trace_id, user_context)
            results["parse_result"] = parse_result
            
            if not parse_result.get("success"):
                return {
                    "success": False,
                    "trace_id": trace_id,
                    "error": "File parsing failed",
                    "results": results
                }
            
            # Step 3: Store parsed data (ParsedDataAbstraction)
            parsed_storage_result = await self._store_parsed_data(
                file_id, parse_result, trace_id, user_context
            )
            results["parsed_storage_result"] = parsed_storage_result
            
            # Step 4: Semantic processing (StatelessHFInferenceAgent)
            semantic_result = await self._process_semantic(
                file_id, parse_result, trace_id, user_context
            )
            results["semantic_result"] = semantic_result
            
            # Step 5: Semantic storage (ContentMetadataAbstraction)
            if semantic_result and semantic_result.get("success"):
                storage_result = await self._store_semantic(
                    file_id, parse_result, semantic_result, trace_id, user_context
                )
                results["storage_result"] = storage_result
            else:
                results["storage_result"] = {"success": False, "error": "Semantic processing failed"}
            
            # Step 6: Return complete result with trace_id
            return {
                "success": True,
                "trace_id": trace_id,
                "results": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "trace_id": trace_id,
                "error": str(e),
                "results": results
            }
    
    async def _validate_file(
        self, file_id: str, trace_id: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Validate file via Data Steward."""
        # Get Data Steward service
        # Validate file
        # Return result with trace_id
        ...
    
    async def _parse_file(
        self, file_id: str, trace_id: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Parse file via FileParserService."""
        # Get FileParserService
        # Parse file
        # Return result with trace_id
        ...
    
    async def _store_parsed_data(
        self, file_id: str, parse_result: Dict[str, Any], trace_id: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Store parsed data via ParsedDataAbstraction."""
        # Get ParsedDataAbstraction
        # Convert parse_result to Parquet if needed
        # Store in GCS + Supabase
        # Return result with trace_id
        ...
    
    async def _process_semantic(
        self, file_id: str, parse_result: Dict[str, Any], trace_id: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process semantically via StatelessHFInferenceAgent."""
        # Get StatelessHFInferenceAgent
        # Process structured/unstructured
        # Return result with trace_id
        ...
    
    async def _store_semantic(
        self, file_id: str, parse_result: Dict[str, Any], semantic_result: Dict[str, Any], trace_id: str, user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Store semantic data via ContentMetadataAbstraction."""
        # Get ContentMetadataAbstraction
        # Store embeddings/graphs with data_classification
        # Return result with trace_id
        ...
```

---

### Step 2.2: Create DataMashJourneyOrchestrator

**File:** `backend/journey/journey_orchestrators/data_mash_journey_orchestrator/data_mash_journey_orchestrator.py`

**Purpose:** Tracks user journey through data mash flow with milestones.

**Implementation:**
```python
#!/usr/bin/env python3
"""
Data Mash Journey Orchestrator

Tracks user journey through data mash flow with milestones.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from bases.journey_orchestrator_base import JourneyOrchestratorBase

class DataMashJourneyOrchestrator(JourneyOrchestratorBase):
    """Data Mash Journey Orchestrator."""
    
    async def track_milestone(
        self,
        trace_id: str,
        milestone: str,  # 'file_uploaded', 'file_parsed', 'parsed_data_stored', 'semantic_processed', 'semantic_stored'
        metadata: Dict[str, Any] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track milestone in data mash journey."""
        milestone_data = {
            "trace_id": trace_id,
            "milestone": milestone,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Store milestone (in ArangoDB or Supabase)
        # Link to journey
        ...
        
        return {"success": True, "milestone_id": milestone_data.get("id")}
    
    async def get_journey(
        self,
        trace_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get complete journey for trace_id."""
        # Retrieve all milestones for trace_id
        # Return journey timeline
        ...
```

---

### Step 2.3: Update ContentAnalysisOrchestrator

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/content_analysis_orchestrator.py`

**Changes:**
1. Use DataMashSolutionOrchestrator for E2E flow
2. Track journey milestones
3. Propagate trace_id

**Updated `parse_file` method:**
```python
async def parse_file(
    self,
    file_id: str,
    parse_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse file using Data Mash Solution Orchestrator.
    """
    # Get DataMashSolutionOrchestrator
    data_mash_orchestrator = await self.get_orchestrator("DataMashSolutionOrchestrator")
    
    # Orchestrate complete flow
    result = await data_mash_orchestrator.orchestrate_data_mash(
        file_id, user_context
    )
    
    # Track journey milestones
    journey_orchestrator = await self.get_orchestrator("DataMashJourneyOrchestrator")
    if result.get("success"):
        await journey_orchestrator.track_milestone(
            result["trace_id"],
            "data_mash_complete",
            {"file_id": file_id}
        )
    
    return result
```

---

## Phase 0.3: Testing & Validation (Week 4-5)

### Test Plan

#### 3.1: Infrastructure Tests
- Test ArangoDB collection initialization
- Test Supabase schema creation
- Test GCS storage for parsed data
- Test indexes and query performance

#### 3.2: Data Classification Tests
- Test platform file creation (with and without tenant_id)
- Test client file creation (with tenant_id)
- Test validation errors (client without tenant_id)
- Test platform/client queries

#### 3.3: Parsed Data Storage Tests
- Test parsed data storage (GCS + Supabase)
- Test parsed data retrieval
- Test platform/client parsed data queries

#### 3.4: Semantic Data Storage Tests
- Test semantic embedding storage with data_classification
- Test semantic graph storage with data_classification
- Test platform/client semantic queries

#### 3.5: End-to-End Tests
- Test complete data mash flow
- Test trace_id propagation
- Test journey milestone tracking
- Test error handling and rollback

---

## Implementation Checklist

### Phase 0.1: Data Steward Consolidation
- [ ] Create ArangoDB collection initialization script
- [ ] Create Supabase schema for parsed data
- [ ] Update FileManagementAbstraction (data_classification, platform/client queries)
- [ ] Update ContentMetadataAbstraction (data_classification, tenant filtering)
- [ ] Create ParsedDataAbstraction (GCS + Supabase)
- [ ] Implement Data Query module (platform/client queries)
- [ ] Implement Data Governance module (platform/client governance)
- [ ] Update Data Steward service (integrate modules)

### Phase 0.2: Data Mash Flow
- [ ] Create DataMashSolutionOrchestrator
- [ ] Create DataMashJourneyOrchestrator
- [ ] Update ContentAnalysisOrchestrator (use DataMashSolutionOrchestrator)
- [ ] Add trace_id propagation to all handoffs
- [ ] Add journey milestone tracking

### Phase 0.3: Testing & Validation
- [ ] Infrastructure tests
- [ ] Data classification tests
- [ ] Parsed data storage tests
- [ ] Semantic data storage tests
- [ ] End-to-end tests

---

## Next Steps

1. **Review this implementation plan**
2. **Start with Phase 0.1.1** (ArangoDB collection initialization)
3. **Proceed step-by-step** through each phase
4. **Test as you go** (don't wait until the end)

---

## Appendix: Data Classification Schema

### Platform Data (data_classification = "platform")
- `data_classification`: "platform"
- `tenant_id`: Optional (can be set for attribution)

### Client Data (data_classification = "client")
- `data_classification`: "client"
- `tenant_id`: Required (must be set)

### Validation Rules
- If `data_classification = "client"`, `tenant_id` must be set
- If `data_classification = "platform"`, `tenant_id` is optional
- All queries must filter by `data_classification`
- Client queries must also filter by `tenant_id`

---

## Conclusion

This implementation plan provides a detailed, step-by-step approach to implementing Phase 0. The plan is based on approved decisions and follows the existing architecture patterns. Each step includes specific files, methods, and testing requirements.

**Key Principles:**
- Follow existing patterns (GCS + Supabase for files/parsed data)
- Use `data_classification` field for platform vs client distinction
- Enable tenant attribution for platform data
- Implement explicit flow orchestration with trace IDs
- Test as you go

