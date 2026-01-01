# Data Solution Orchestrator

## Overview

The Data Solution Orchestrator is the foundation layer for all data operations in the platform. It orchestrates the complete data solution flow: **Ingest → Parse → Embed → Expose**.

## Architecture

- **Extends**: `OrchestratorBase` for Smart City access
- **Uses**: Direct SOA API calls to Smart City services (no SDK)
- **Delegates**: To enabling services (FileParserService, EmbeddingService, etc.)
- **Propagates**: workflow_id and correlation IDs throughout

## Key Methods

### 1. `orchestrate_data_ingest()`
- Uploads file → Content Steward
- Tracks lineage → Data Steward
- Records observability → Nurse
- Returns: `file_id`, `workflow_id`

### 2. `orchestrate_data_parse()`
- Parses file → FileParserService (Phase 1)
- Stores parsed file → Content Steward
- Extracts metadata → ContentMetadataExtractionService (Phase 1)
- Stores metadata → Librarian
- Tracks lineage → Data Steward
- Returns: `parse_result`, `parsed_file_id`, `content_metadata`, `workflow_id`

### 3. `orchestrate_data_embed()`
- Creates embeddings → EmbeddingService (Phase 1)
- Stores embeddings → Librarian
- Tracks lineage → Data Steward
- Returns: `embeddings_count`, `content_id`, `workflow_id`

### 4. `orchestrate_data_expose()`
- Gets parsed file → Content Steward
- Gets content metadata → Librarian
- Gets semantic embeddings → Librarian
- Returns: Exposed data (semantic view, no raw client data)

## Correlation IDs

All methods include correlation IDs in lineage tracking:
- `workflow_id` - Primary correlation ID (from gateway)
- `user_id` - User identifier
- `session_id` - Session identifier
- `file_id` - File identifier
- `parsed_file_id` - Parsed file identifier
- `content_id` - Content identifier

## Dependencies

**Phase 0 (Current):**
- ✅ Smart City services (Content Steward, Librarian, Data Steward, Nurse)
- ✅ Direct SOA API calls

**Phase 1 (Will break until created):**
- ⚠️ FileParserService - Will be created in Phase 1.1
- ⚠️ ContentMetadataExtractionService - Will be created in Phase 1.2
- ⚠️ EmbeddingService - Will be created in Phase 1.3

**Note:** This is intentional - "break then fix" approach. The orchestrator acknowledges dependencies and will work once Phase 1 services are created.

## Usage

```python
# Initialize
data_solution = DataSolutionOrchestrator(delivery_manager)
await data_solution.initialize()

# Ingest
ingest_result = await data_solution.orchestrate_data_ingest(
    file_data=file_data,
    file_name="example.csv",
    file_type="text/csv",
    user_context=user_context
)

# Parse
parse_result = await data_solution.orchestrate_data_parse(
    file_id=ingest_result["file_id"],
    user_context=user_context,
    workflow_id=ingest_result["workflow_id"]
)

# Embed
embed_result = await data_solution.orchestrate_data_embed(
    file_id=ingest_result["file_id"],
    parsed_file_id=parse_result["parsed_file_id"],
    content_metadata=parse_result["content_metadata"],
    user_context=user_context,
    workflow_id=ingest_result["workflow_id"]
)

# Expose
expose_result = await data_solution.orchestrate_data_expose(
    file_id=ingest_result["file_id"],
    parsed_file_id=parse_result["parsed_file_id"],
    user_context=user_context
)
```

## Status

- **Phase 0**: ✅ Complete - Foundation created
- **Phase 1**: ⏳ Pending - Enabling services will be created



