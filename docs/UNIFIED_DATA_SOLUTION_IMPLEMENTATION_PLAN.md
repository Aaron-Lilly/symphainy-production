# Unified Data Solution Implementation Plan
## Foundation → Content Pillar → Insights → Pause & Reassess

**Date:** December 11, 2025  
**Status:** 🚀 Ready to Start  
**Strategy:** Break Then Fix - No Stubs, Acknowledge Dependencies

---

## 🎯 **Executive Summary**

This plan unifies three refactoring efforts into a cohesive implementation:
1. **Data Solution Orchestrator** - Foundation layer (ingest → parse → embed → expose)
2. **Content Pillar Vertical Slice** - First use case on top of foundation
3. **Insights Pillar** - Second use case, depends on foundation
4. **Pause & Reassess** - Strategic approach for remaining pillars

**Key Principle:** Build foundation first, then use cases. Break then fix - no stubs, acknowledge dependencies.

---

## 🏗️ **Architecture Layers**

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Use Case Orchestrators (Business Enablement)      │
│ - ContentAnalysisOrchestrator (uses Data Solution)         │
│ - InsightsOrchestrator (uses Data Solution)                │
│ - OperationsOrchestrator (future)                          │
│ - BusinessOutcomesOrchestrator (future)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓ Uses
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Data Solution Orchestrator (Solution Realm)      │
│ Location: backend/solution/services/data_solution_         │
│           orchestrator_service/                            │
│ - orchestrate_data_ingest()                                │
│ - orchestrate_data_parse()                                 │
│ - orchestrate_data_embed()                                 │
│ - orchestrate_data_expose()                                │
└─────────────────────────────────────────────────────────────┘
                            ↓ Uses
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Smart City Services (SOA APIs)                    │
│ - Content Steward (direct SOA API calls)                   │
│ - Librarian (direct SOA API calls)                         │
│ - Data Steward (direct SOA API calls)                      │
│ - Nurse (direct SOA API calls)                             │
└─────────────────────────────────────────────────────────────┘
                            ↓ Uses
┌─────────────────────────────────────────────────────────────┐
│ Layer 0: Infrastructure Abstractions                       │
│ - File Management, Semantic Data, Observability, etc.      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 **Phase 0: Data Solution Foundation** (Week 1)
## Create Data Solution Orchestrator

### **0.0 Phase 0.5: Correlation ID Infrastructure** (Week 1, Days 1-2)
## Setup Correlation ID Propagation Throughout Platform

**Goal:** Ensure workflow_id and correlation IDs are generated and propagated from frontend → gateway → orchestrator → services

#### **0.0.1 Update FrontendGatewayService**

**Location:** `foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py`

**Changes:**
```python
async def route_frontend_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    # Extract headers
    headers = request.get("headers", {})
    
    # Extract user context
    tenant_id = headers.get("X-Tenant-Id")
    user_id = headers.get("X-User-Id")
    session_token = headers.get("X-Session-Token")
    
    # ✅ NEW: Generate workflow_id at gateway entry point (if not provided)
    workflow_id = (
        request.get("workflow_id") or 
        headers.get("X-Workflow-Id") or 
        str(uuid.uuid4())
    )
    
    # Build user_context with workflow_id
    user_context = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "session_id": session_token,
        "workflow_id": workflow_id  # ✅ ADD THIS
    }
    
    # Add to request for propagation
    request["user_context"] = user_context
    request["params"]["workflow_id"] = workflow_id
    
    # Continue with routing...
```

**Deliverables:**
- [ ] FrontendGatewayService updated to generate workflow_id
- [ ] User context includes workflow_id
- [ ] workflow_id propagated to all orchestrator calls

---

#### **0.0.2 Update Startup Sequence**

**Location:** `symphainy-platform/main.py` - `PlatformOrchestrator.orchestrate_platform_startup()`

**Changes:**
```python
async def orchestrate_platform_startup(self) -> Dict[str, Any]:
    # ✅ NEW: Generate platform startup workflow_id
    platform_startup_workflow_id = str(uuid.uuid4())
    
    # Store in app_state for correlation
    app_state["platform_startup_workflow_id"] = platform_startup_workflow_id
    
    # Propagate to all startup operations
    await self._initialize_foundation_infrastructure(
        workflow_id=platform_startup_workflow_id
    )
```

**Deliverables:**
- [ ] Platform startup workflow_id generated
- [ ] workflow_id propagated to all startup operations
- [ ] Correlation tracking initialized

---

#### **0.0.3 Add Correlation ID Headers to Inter-Container Communication**

**Location:** `foundations/curator_foundation/services/soa_client_service.py`

**Changes:**
```python
async def call_service(self, service_name: str, endpoint: str, request_data: Dict[str, Any],
                      realm: Optional[str] = None, correlation_id: Optional[str] = None,
                      tenant_id: Optional[str] = None, workflow_id: Optional[str] = None) -> Dict[str, Any]:
    # Build headers
    headers = {}
    if correlation_id:
        headers["X-Correlation-ID"] = correlation_id
    if workflow_id:  # ✅ ADD THIS
        headers["X-Workflow-ID"] = workflow_id
    if tenant_id:
        headers["X-Tenant-ID"] = tenant_id
```

**Deliverables:**
- [ ] workflow_id header added to inter-container communication
- [ ] Correlation IDs propagated in all SOA calls

---

#### **0.0.4 Document Correlation ID Pattern**

**Deliverables:**
- [ ] Correlation ID pattern documented
- [ ] workflow_id generation points identified
- [ ] Correlation ID propagation flow documented

---

### **0.1 Goal**
Create the foundation orchestrator that handles the complete data solution flow: Ingest → Parse → Embed → Expose

### **0.2 Architecture**

**Location:** `backend/business_enablement/delivery_manager/data_solution_orchestrator/`

**Structure:**
```
data_solution_orchestrator/
├── data_solution_orchestrator.py (main orchestrator)
├── __init__.py
└── README.md
```

### **0.3 Implementation**

**Class:** `DataSolutionOrchestrator(OrchestratorBase)`

**Key Methods:**
1. `orchestrate_data_ingest()` - File upload → Content Steward
2. `orchestrate_data_parse()` - File parsing → Parsed file storage
3. `orchestrate_data_embed()` - Representative sampling → Semantic embeddings
4. `orchestrate_data_expose()` - Semantic layer exposure for other solutions

**Important:** These methods will call enabling services that don't exist yet (FileParserService, EmbeddingService). This is intentional - we acknowledge the dependency and will fix it in Phase 1.

### **0.4 Key Implementation Details**

#### **0.4.1 orchestrate_data_ingest()**

```python
async def orchestrate_data_ingest(
    self,
    file_data: bytes,
    file_name: str,
    file_type: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orchestrate data ingestion.
    
    Flow:
    1. Upload file → Content Steward (direct SOA API)
    2. Track lineage → Data Steward (direct SOA API)
    3. Record observability → Nurse (direct SOA API)
    4. Return file_id and workflow_id
    """
    # Generate workflow_id for end-to-end tracking
    workflow_id = str(uuid.uuid4())
    
    # Upload via Content Steward (direct SOA API call - no SDK)
    content_steward = await self.get_content_steward_api()
    upload_result = await content_steward.process_upload(
        file_data=file_data,
        content_type=file_type,
        metadata={"ui_name": file_name},
        user_context=user_context,
        workflow_id=workflow_id
    )
    
    # Track lineage (direct SOA API call)
    data_steward = await self.get_data_steward_api()
    await data_steward.track_lineage(
        lineage_data={
            "source_id": user_context.get("user_id") if user_context else "system",
            "target_id": upload_result["file_id"],
            "operation": "file_upload",
            "operation_type": "file_storage",
            "correlation_ids": {
                "workflow_id": workflow_id,
                "user_id": user_context.get("user_id") if user_context else None,
                "session_id": user_context.get("session_id") if user_context else None,
                "file_id": upload_result["file_id"]  # ✅ Correlation: file_id included
            }
        },
        workflow_id=workflow_id,
        user_context=user_context
    )
    
    # Record observability (direct SOA API call)
    nurse = await self.get_nurse_api()
    await nurse.record_platform_event(
        event_type="log",
        event_data={
            "level": "info",
            "message": f"File uploaded: {file_name}",
            "service_name": self.__class__.__name__,
            "file_id": upload_result["file_id"]
        },
        trace_id=workflow_id,
        user_context=user_context
    )
    
    return {
        "success": True,
        "file_id": upload_result["file_id"],
        "workflow_id": workflow_id
    }
```

#### **0.4.2 orchestrate_data_parse()**

```python
async def orchestrate_data_parse(
    self,
    file_id: str,
    parse_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None,
    workflow_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Orchestrate data parsing.
    
    Flow:
    1. Parse file → FileParserService (enabling service - will be created in Phase 1)
    2. Store parsed file → Content Steward (direct SOA API)
    3. Extract metadata → ContentMetadataExtractionService (will be created in Phase 1)
    4. Store metadata → Librarian (direct SOA API)
    5. Track lineage → Data Steward (direct SOA API)
    6. Return parse_result and metadata
    
    NOTE: FileParserService and ContentMetadataExtractionService don't exist yet.
    This will break until Phase 1. That's intentional - break then fix.
    """
    if not workflow_id:
        workflow_id = str(uuid.uuid4())
    
    # Get FileParserService (enabling service - will be created in Phase 1)
    # NOTE: This will fail until Phase 1 - that's intentional
    file_parser = await self.get_enabling_service("FileParserService")
    if not file_parser:
        raise ValueError("FileParserService not available - will be created in Phase 1")
    
    # Parse file
    parse_result = await file_parser.parse_file(
        file_id=file_id,
        parse_options=parse_options,
        user_context=user_context
    )
    
    if not parse_result.get("success"):
        return parse_result
    
    # Store parsed file via Content Steward (direct SOA API)
    content_steward = await self.get_content_steward_api()
    
    # Convert parsed data to bytes
    import json
    parsed_data_bytes = json.dumps(parse_result["data"]).encode('utf-8')
    
    # Determine format_type and content_type
    format_type = "json_structured" if parse_result.get("parsing_type") == "structured" else "json_chunks"
    content_type = parse_result.get("parsing_type", "structured")
    
    store_result = await content_steward.store_parsed_file(
        file_id=file_id,
        parsed_file_data=parsed_data_bytes,
        format_type=format_type,
        content_type=content_type,
        parse_result=parse_result,
        workflow_id=workflow_id,
        user_context=user_context
    )
    
    # Extract content metadata (ContentMetadataExtractionService - will be created in Phase 1)
    # NOTE: This will fail until Phase 1 - that's intentional
    metadata_extractor = await self.get_enabling_service("ContentMetadataExtractionService")
    if not metadata_extractor:
        raise ValueError("ContentMetadataExtractionService not available - will be created in Phase 1")
    
    content_metadata = await metadata_extractor.extract_and_store_metadata(
        file_id=file_id,
        parsed_file_id=store_result["parsed_file_id"],
        parse_result=parse_result,
        workflow_id=workflow_id,
        user_context=user_context
    )
    
    # Track lineage
    data_steward = await self.get_data_steward_api()
    await data_steward.track_lineage(
        lineage_data={
            "source_id": file_id,
            "target_id": store_result["parsed_file_id"],
            "operation": "file_parsing",
            "operation_type": "data_transformation",
            "correlation_ids": {
                "workflow_id": workflow_id,
                "user_id": user_context.get("user_id") if user_context else None,
                "session_id": user_context.get("session_id") if user_context else None,
                "file_id": file_id,  # ✅ Correlation: file_id included
                "parsed_file_id": store_result["parsed_file_id"]  # ✅ Correlation: parsed_file_id included
            }
        },
        workflow_id=workflow_id,
        user_context=user_context
    )
    
    return {
        "success": True,
        "parse_result": parse_result,
        "parsed_file_id": store_result["parsed_file_id"],
        "content_metadata": content_metadata,
        "workflow_id": workflow_id
    }
```

#### **0.4.3 orchestrate_data_embed()**

```python
async def orchestrate_data_embed(
    self,
    file_id: str,
    parsed_file_id: str,
    content_metadata: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None,
    workflow_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Orchestrate semantic embedding creation.
    
    Flow:
    1. Create representative embeddings → EmbeddingService (will be created in Phase 1)
    2. Store embeddings → Librarian (direct SOA API)
    3. Track lineage → Data Steward (direct SOA API)
    4. Return embeddings_result
    
    NOTE: EmbeddingService doesn't exist yet.
    This will break until Phase 1. That's intentional - break then fix.
    """
    if not workflow_id:
        workflow_id = str(uuid.uuid4())
    
    # Get EmbeddingService (enabling service - will be created in Phase 1)
    # NOTE: This will fail until Phase 1 - that's intentional
    embedding_service = await self.get_enabling_service("EmbeddingService")
    if not embedding_service:
        raise ValueError("EmbeddingService not available - will be created in Phase 1")
    
    # Create embeddings using representative sampling (every 10th row)
    embeddings_result = await embedding_service.create_representative_embeddings(
        parsed_file_id=parsed_file_id,
        content_metadata=content_metadata,
        sampling_strategy="every_nth",
        n=10,  # Every 10th row
        user_context=user_context
    )
    
    if not embeddings_result.get("embeddings"):
        return {
            "success": False,
            "message": "No embeddings created",
            "workflow_id": workflow_id
        }
    
    # Store via Librarian (direct SOA API)
    librarian = await self.get_librarian_api()
    content_id = content_metadata.get("content_id")
    if not content_id:
        return {
            "success": False,
            "message": "content_id not found in content_metadata",
            "workflow_id": workflow_id
        }
    
    await librarian.store_semantic_embeddings(
        content_id=content_id,
        file_id=file_id,
        embeddings=embeddings_result["embeddings"],
        workflow_id=workflow_id,
        user_context=user_context
    )
    
    # Track lineage
    data_steward = await self.get_data_steward_api()
    await data_steward.track_lineage(
        lineage_data={
            "source_id": parsed_file_id,
            "target_id": content_id,
            "operation": "embedding_creation",
            "operation_type": "semantic_processing",
            "correlation_ids": {
                "workflow_id": workflow_id,
                "user_id": user_context.get("user_id") if user_context else None,
                "session_id": user_context.get("session_id") if user_context else None,
                "file_id": file_id,  # ✅ Correlation: file_id included
                "parsed_file_id": parsed_file_id,  # ✅ Correlation: parsed_file_id included
                "content_id": content_id  # ✅ Correlation: content_id included
            }
        },
        workflow_id=workflow_id,
        user_context=user_context
    )
    
    return {
        "success": True,
        "embeddings_count": len(embeddings_result["embeddings"]),
        "content_id": content_id,
        "workflow_id": workflow_id
    }
```

#### **0.4.4 orchestrate_data_expose()**

```python
async def orchestrate_data_expose(
    self,
    file_id: str,
    parsed_file_id: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orchestrate data exposure for other solutions.
    
    Flow:
    1. Get parsed file → Content Steward (direct SOA API)
    2. Get content metadata → Librarian (direct SOA API)
    3. Get semantic embeddings → Librarian (direct SOA API)
    4. Return exposed data (semantic view)
    
    This enables Operations/Business Outcomes to access parsed files
    without touching raw client data.
    """
    # Get parsed file
    content_steward = await self.get_content_steward_api()
    
    # If parsed_file_id not provided, get it from file_id
    if not parsed_file_id:
        # Get parsed files for this file_id
        parsed_files = await content_steward.list_parsed_files(
            file_id=file_id,
            user_context=user_context
        )
        if parsed_files:
            parsed_file_id = parsed_files[0].get("parsed_file_id")
    
    if not parsed_file_id:
        return {
            "success": False,
            "message": f"No parsed file found for file_id: {file_id}"
        }
    
    parsed_file = await content_steward.get_parsed_file(
        parsed_file_id=parsed_file_id,
        user_context=user_context
    )
    
    # Get content metadata
    librarian = await self.get_librarian_api()
    content_metadata = await librarian.get_content_metadata(
        file_id=file_id,
        user_context=user_context
    )
    
    # Get semantic embeddings (optional - may not exist yet)
    embeddings = []
    if content_metadata and content_metadata.get("content_id"):
        try:
            embeddings = await librarian.get_semantic_embeddings(
                content_id=content_metadata["content_id"],
                user_context=user_context
            )
        except Exception as e:
            # Embeddings may not exist yet - that's OK
            self.logger.debug(f"Embeddings not available: {e}")
    
    # Return exposed data (semantic view)
    return {
        "success": True,
        "parsed_data": parsed_file.get("data") if parsed_file else None,
        "content_metadata": content_metadata,
        "embeddings_available": len(embeddings) > 0,
        "embeddings_count": len(embeddings),
        "exposed_via": "semantic_layer",
        "raw_client_data": False  # Not touching raw client data
    }
```

### **0.5 Deliverables**

- [ ] DataSolutionOrchestrator class created
- [ ] All 4 orchestration methods implemented
- [ ] Direct SOA API calls to Smart City services (no SDK)
- [ ] Workflow_id propagation throughout
- [ ] **Correlation IDs include file_id, parsed_file_id, content_id** ✅
- [ ] Lineage tracking integrated
- [ ] Observability recording integrated
- [ ] Error handling for missing enabling services (acknowledge dependencies)
- [ ] Unit tests for each method
- [ ] Integration tests (will fail until Phase 1 - that's OK)

### **0.6 Known Dependencies**

**These will break until Phase 1:**
- `FileParserService` - Will be created in Phase 1.1
- `ContentMetadataExtractionService` - Will be created in Phase 1.2
- `EmbeddingService` - Will be created in Phase 1.3

**This is intentional - break then fix approach.**

---

### **0.7 Correlation ID Pattern**

**Primary Correlation ID: `workflow_id`**
- Generated at gateway entry point (FrontendGatewayService)
- Propagated to all orchestrators and services
- Stored with all data types (client, security, session, agentic, telemetry)

**Secondary Correlation IDs (in `correlation_ids` dict):**
- `user_id` - User identifier
- `session_id` - Session identifier
- `file_id` - File identifier (✅ ADDED)
- `parsed_file_id` - Parsed file identifier (✅ ADDED)
- `content_id` - Content identifier (✅ ADDED)

**Correlation Flow:**
```
Frontend (generates workflow_id for multi-step operations)
  ↓ (X-Workflow-Id header)
FrontendGatewayService (generates workflow_id if missing)
  ↓ (user_context.workflow_id)
Orchestrators (receives workflow_id in user_context)
  ↓ (workflow_id + correlation_ids)
Data Solution Orchestrator (uses workflow_id, adds file_id to correlation_ids)
  ↓ (workflow_id + correlation_ids)
Smart City Services (all operations use workflow_id for correlation)
```

**Benefits:**
- Single `workflow_id` correlates all data types
- Can trace complete user journey
- Can debug cross-service issues
- Can audit data operations
- Can correlate platform/semantic/client data throughout platform

---

## 📋 **Phase 1: Content Pillar Vertical Slice** (Weeks 2-3)
## Complete Rebuild Using Data Solution Orchestrator

### **1.1 Goal**
Rebuild ContentAnalysisOrchestrator to use Data Solution Orchestrator, and create/fix all enabling services it needs.

### **1.2 Architecture**

**ContentAnalysisOrchestrator uses Data Solution Orchestrator:**
```python
class ContentAnalysisOrchestrator(OrchestratorBase):
    async def initialize(self):
        # Get Data Solution Orchestrator
        self.data_solution = await self.get_data_solution_orchestrator()
    
    async def handle_content_upload(self, ...):
        # Use Data Solution Orchestrator
        ingest_result = await self.data_solution.orchestrate_data_ingest(...)
        parse_result = await self.data_solution.orchestrate_data_parse(...)
        embed_result = await self.data_solution.orchestrate_data_embed(...)
```

### **1.3 Components to Build/Fix**

#### **1.3.0 Ensure Correlation ID Propagation** (Week 2, Day 1)

**Goal:** Ensure all Content Pillar components propagate workflow_id and correlation IDs

**Key Changes:**
- FileParserService receives workflow_id in user_context
- ContentMetadataExtractionService receives workflow_id in user_context
- EmbeddingService receives workflow_id in user_context
- ContentAnalysisOrchestrator propagates workflow_id to all operations

**Deliverables:**
- [ ] All services receive workflow_id in user_context
- [ ] workflow_id propagated to all Smart City service calls
- [ ] Correlation IDs included in all lineage tracking

---

#### **1.3.1 FileParserService Rebuild** (Week 2, Days 2-3)

**Goal:** Rebuild with parsing type determination, preserve binary + copybook support

**Key Changes:**
- Add parsing type determination (structured/unstructured/hybrid/workflow/sop)
- Add parsing orchestrator module
- Preserve all existing functionality (binary + copybook)
- Integrate with Data Solution Orchestrator (store parsed files)

**See:** `FILE_PARSER_SERVICE_REBUILDING_PLAN.md` for detailed breakdown

**Deliverables:**
- [ ] Parsing type determination implemented
- [ ] Parsing orchestrator module created
- [ ] All file types supported (including binary + copybook)
- [ ] Parsed file storage integrated
- [ ] Workflow_id propagation
- [ ] Unit tests
- [ ] Integration tests

#### **1.3.2 ContentMetadataExtractionService** (Week 2, Days 4-5)

**Note:** Must receive and propagate workflow_id from user_context

**Goal:** Create new service to extract and store content metadata

**Key Features:**
- Extract metadata from parsed files (schema, columns, data types, row count)
- Store metadata via Librarian (direct SOA API)
- Integrate with Data Solution Orchestrator

**Deliverables:**
- [ ] Service created
- [ ] Metadata extraction logic
- [ ] Librarian integration (direct SOA API)
- [ ] Workflow_id propagation
- [ ] Unit tests
- [ ] Integration tests

#### **1.3.3 EmbeddingService** (Week 3, Days 1-3)

**Note:** Must receive and propagate workflow_id from user_context

**Goal:** Create new service for representative sampling embeddings

**Key Features:**
- Representative sampling (every 10th row, not first 10 rows)
- Uses StatelessHFInferenceAgent for embeddings
- Creates 3 embeddings per column (metadata, meaning, samples)
- Integrates with Data Solution Orchestrator

**Agentic Forward Pattern:**
```python
class EmbeddingService:
    async def create_representative_embeddings(self, ...):
        # Get StatelessHFInferenceAgent
        hf_agent = await self.get_stateless_hf_inference_agent()
        
        # Representative sampling (every 10th row)
        for row in rows[::10]:
            embedding = await hf_agent.generate_embedding(row, ...)
```

**Deliverables:**
- [ ] Service created
- [ ] Representative sampling implemented (every 10th row)
- [ ] StatelessHFInferenceAgent integration
- [ ] 3 embeddings per column (metadata, meaning, samples)
- [ ] Query parsed data when needed (fallback)
- [ ] Unit tests
- [ ] Integration tests

#### **1.3.4 ContentAnalysisOrchestrator Rebuild** (Week 3, Days 4-5)

**Goal:** Rebuild to use Data Solution Orchestrator

**Key Changes:**
- Use Data Solution Orchestrator for all data operations
- Remove direct Smart City service calls
- Lightweight agentic features (commentary only)
- Preserve UI integration

**Deliverables:**
- [ ] Orchestrator rebuilt
- [ ] Data Solution Orchestrator integration
- [ ] Lightweight agentic features
- [ ] UI integration preserved
- [ ] Unit tests
- [ ] Integration tests

#### **1.3.5 Agents Rebuild** (Week 3, Days 4-5)

**Goal:** Rebuild agents with agentic forward pattern, lightweight MVP

**Agents:**
- ContentLiaisonAgent - Lightweight commentary
- ContentProcessingAgent - Lightweight commentary

**Key Features:**
- Lightweight MVP (commentary only, no editing)
- Agentic forward (enhance enabling services)
- MCP tool integration

**Deliverables:**
- [ ] Agents rebuilt
- [ ] Lightweight MVP pattern
- [ ] Agentic forward integration
- [ ] MCP tool integration
- [ ] Unit tests

#### **1.3.6 MCP Server Rebuild** (Week 3, Days 4-5)

**Goal:** Rebuild MCP Server for agentic forward pattern

**Key Features:**
- Tool definitions (read-only results + commentary)
- Agent integration (lightweight)
- Use case-level capabilities

**Deliverables:**
- [ ] MCP Server rebuilt
- [ ] Tool definitions
- [ ] Agent integration
- [ ] Unit tests

### **1.4 Fix Enabling Services As Needed**

**Only fix services that block Content Pillar:**
- FileParserService - Rebuilding anyway
- ContentMetadataExtractionService - Creating new
- EmbeddingService - Creating new
- Any other services that block Content Pillar workflow

**Defer other services until their orchestrator phase.**

### **1.5 Deliverables**

- [ ] FileParserService rebuilt
- [ ] ContentMetadataExtractionService created
- [ ] EmbeddingService created
- [ ] ContentAnalysisOrchestrator rebuilt
- [ ] Agents rebuilt
- [ ] MCP Server rebuilt
- [ ] End-to-end workflow working
- [ ] All tests passing

---

## 📋 **Phase 2: Insights Pillar** (Weeks 4-5)
## Refactor to Use Data Solution Orchestrator + Semantic Data Model

### **2.1 Goal**
Refactor InsightsOrchestrator to use Data Solution Orchestrator and semantic data model (not raw client data).

### **2.2 Architecture**

**InsightsOrchestrator uses Data Solution Orchestrator:**
```python
class InsightsOrchestrator(OrchestratorBase):
    async def initialize(self):
        # Get Data Solution Orchestrator
        self.data_solution = await self.get_data_solution_orchestrator()
    
    async def analyze_content_for_insights(self, content_id, ...):
        # Query semantic embeddings via Data Solution
        embeddings = await self.data_solution.get_semantic_embeddings(...)
        
        # Use embeddings for analysis (not raw client data)
        insights = await self._analyze_with_semantic_data(embeddings, ...)
        
        # If needed, query parsed data (representative sampling fallback)
        if need_detailed_data:
            parsed_data = await self.data_solution.query_parsed_data_when_needed(...)
```

### **2.3 Components to Fix**

#### **2.3.1 InsightsOrchestrator Refactor** (Week 4, Days 1-3)

**Key Changes:**
- Use Data Solution Orchestrator for data access
- Query semantic embeddings (not raw client data)
- Vector search for similarity matching
- Semantic reasoning
- Fallback to parsed data queries when needed

**Deliverables:**
- [ ] Orchestrator refactored
- [ ] Data Solution Orchestrator integration
- [ ] Semantic data model usage
- [ ] Vector search integration
- [ ] Unit tests
- [ ] Integration tests

#### **2.3.2 Fix Enabling Services** (Week 4, Days 4-5, Week 5, Days 1-3)

**Fix services that block Insights:**
- MetricsCalculatorService - Fix hard-coded metric definitions
- InsightsGeneratorService - Fix hard-coded historical context
- DataAnalyzerService - Fix entity extraction
- VisualizationEngineService - Fix visualization generation
- APGProcessingService - Fix pattern generation

**Agentic Forward Pattern:**
- Use agents to enhance enabling services
- Agents handle complex business logic
- Agents provide fallback when services have limitations

**Deliverables:**
- [ ] MetricsCalculatorService fixed
- [ ] InsightsGeneratorService fixed
- [ ] DataAnalyzerService fixed
- [ ] VisualizationEngineService fixed
- [ ] APGProcessingService fixed
- [ ] Agentic forward integration
- [ ] Unit tests
- [ ] Integration tests

#### **2.3.3 Agents Rebuild** (Week 5, Days 4-5)

**Agents:**
- InsightsLiaisonAgent - Rebuild with agentic forward
- InsightsSpecialistAgent - Rebuild with agentic forward

**Deliverables:**
- [ ] Agents rebuilt
- [ ] Agentic forward integration
- [ ] MCP tool integration
- [ ] Unit tests

#### **2.3.4 MCP Server Rebuild** (Week 5, Days 4-5)

**Deliverables:**
- [ ] MCP Server rebuilt
- [ ] Tool definitions
- [ ] Agent integration
- [ ] Unit tests

### **2.4 Deliverables**

- [ ] InsightsOrchestrator refactored
- [ ] All blocking enabling services fixed
- [ ] Agents rebuilt
- [ ] MCP Server rebuilt
- [ ] Semantic data model usage validated
- [ ] All tests passing

---

## 📋 **Phase 3: Pause & Reassess** (Week 6)
## Strategic Approach for Remaining Pillars

### **3.1 Goal**
Pause and holistically assess where we are, then create strategic approach for Operations and Business Outcomes pillars.

### **3.2 Assessment Areas**

1. **What's Working:**
   - Data Solution Orchestrator foundation
   - Content Pillar vertical slice
   - Insights Pillar semantic data usage
   - Enabling services fixed so far

2. **What's Remaining:**
   - Operations Orchestrator
   - Business Outcomes Orchestrator
   - Remaining enabling services (not yet fixed)
   - Workflow/SOP parsing (if not done)

3. **Lessons Learned:**
   - What worked well?
   - What didn't work?
   - What patterns emerged?
   - What should we change?

4. **Strategic Decisions:**
   - How to approach Operations/Business Outcomes?
   - Which enabling services to fix next?
   - What's the priority order?
   - Any architecture changes needed?

### **3.3 Deliverables**

- [ ] Assessment document
- [ ] Lessons learned document
- [ ] Strategic plan for remaining pillars
- [ ] Updated roadmap

---

## 🔄 **Dependencies & Integration Points**

### **Phase 0 → Phase 1**

**Data Solution Orchestrator calls:**
- `FileParserService` - Will be created in Phase 1.1
- `ContentMetadataExtractionService` - Will be created in Phase 1.2
- `EmbeddingService` - Will be created in Phase 1.3

**Status:** Will break until Phase 1 - that's intentional (break then fix)

### **Phase 1 → Phase 2**

**Content Pillar provides:**
- Working Data Solution Orchestrator
- Working FileParserService
- Working ContentMetadataExtractionService
- Working EmbeddingService
- Working ContentAnalysisOrchestrator

**Insights Pillar uses:**
- Data Solution Orchestrator (foundation)
- Semantic data model (embeddings)
- Fixes enabling services it needs

### **Phase 2 → Phase 3**

**Insights Pillar provides:**
- Validated semantic data model usage
- Fixed enabling services
- Agentic forward patterns

**Pause & Reassess:**
- Use learnings to plan remaining pillars

---

## ✅ **Success Criteria**

### **Phase 0.5 Success:**
- [ ] FrontendGatewayService generates workflow_id
- [ ] Startup sequence initializes correlation tracking
- [ ] Correlation ID headers added to inter-container communication
- [ ] Correlation ID pattern documented

### **Phase 0 Success:**
- [ ] Data Solution Orchestrator created
- [ ] All 4 orchestration methods implemented
- [ ] Direct SOA API calls working
- [ ] Workflow_id propagation working
- [ ] **Correlation IDs include file_id, parsed_file_id, content_id** ✅
- [ ] Lineage tracking working
- [ ] Observability recording working
- [ ] Acknowledges dependencies (will break until Phase 1)

### **Phase 1 Success:**
- [ ] FileParserService rebuilt and working
- [ ] ContentMetadataExtractionService created and working
- [ ] EmbeddingService created and working
- [ ] ContentAnalysisOrchestrator rebuilt and working
- [ ] **All services propagate workflow_id and correlation IDs** ✅
- [ ] Agents rebuilt and working
- [ ] MCP Server rebuilt and working
- [ ] End-to-end workflow working
- [ ] Data Solution Orchestrator calls now work
- [ ] Correlation IDs propagated throughout Content Pillar

### **Phase 2 Success:**
- [ ] InsightsOrchestrator refactored and working
- [ ] Semantic data model usage validated
- [ ] All blocking enabling services fixed
- [ ] Agents rebuilt and working
- [ ] MCP Server rebuilt and working
- [ ] End-to-end workflow working

### **Phase 3 Success:**
- [ ] Assessment complete
- [ ] Lessons learned documented
- [ ] Strategic plan created
- [ ] Ready for remaining pillars

---

## 📊 **Timeline Summary**

| Phase | Duration | Focus |
|-------|----------|-------|
| **Phase 0.5** | Week 1, Days 1-2 | Correlation ID Infrastructure |
| **Phase 0** | Week 1, Days 3-5 | Data Solution Foundation |
| **Phase 1** | Weeks 2-3 | Content Pillar Vertical Slice |
| **Phase 2** | Weeks 4-5 | Insights Pillar |
| **Phase 3** | Week 6 | Pause & Reassess |

**Total:** 6 weeks to complete foundation + 2 use cases + assessment

---

## 🎯 **Key Principles**

1. **Foundation First** - Data Solution Orchestrator is the foundation
2. **Break Then Fix** - No stubs, acknowledge dependencies
3. **Fix As Needed** - Only fix services that block current work
4. **Agentic Forward** - Agents enhance enabling services
5. **Direct SOA APIs** - No SDK, call Smart City services directly
6. **Workflow ID Propagation** - End-to-end tracking from gateway → orchestrator → services
7. **Correlation IDs** - file_id, parsed_file_id, content_id included in correlation_ids dict
8. **Representative Sampling** - Every 10th row, not first 10 rows

---

**Last Updated:** December 11, 2025  
**Status:** 🚀 Ready to Start  
**Next Action:** Begin Phase 0.5 - Correlation ID Infrastructure

---

## 📋 **Appendix: Correlation ID Implementation Details**

### **Correlation ID Pattern**

**Primary ID: `workflow_id`**
- Generated at: FrontendGatewayService (or frontend for multi-step operations)
- Propagated via: `user_context["workflow_id"]`
- Stored with: All data operations, lineage, observability

**Secondary IDs: `correlation_ids` dict**
- `user_id` - From user_context
- `session_id` - From user_context
- `file_id` - From operation context
- `parsed_file_id` - From parsing operation
- `content_id` - From content metadata

**Storage:**
- Lineage tracking: `correlation_ids` dict in lineage_data
- Observability: `trace_id` = workflow_id
- All Smart City operations: workflow_id in user_context

**Benefits:**
- Correlate platform/semantic/client data throughout platform
- Trace complete user journey
- Debug cross-service issues
- Audit data operations

