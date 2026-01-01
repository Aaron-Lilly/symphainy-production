# DIL E2E Execution Plan: Layer-by-Layer Implementation

**Date:** January 2025  
**Status:** 🎯 **READY FOR EXECUTION**  
**Approach:** Systematic layer-by-layer implementation

---

## Executive Summary

This document provides a comprehensive, layer-by-layer execution plan for implementing the Data Intelligence Layer (DIL) Foundation with SDK, Data Mash Solution, and refactored MVP Journey. Each layer builds on the previous, ensuring no breaking changes and incremental value delivery.

---

## Layer 1: Infrastructure Dependencies

### 1.1: Poetry/PyProject/Requirements

**Status:** ✅ **NO CHANGES NEEDED**

**Analysis:**
- All required dependencies already in `pyproject.toml`:
  - `python-arango` (^7.8.1) - ArangoDB client
  - `transformers` (^4.35.0) - HuggingFace embeddings
  - `pyarrow` (^12.0.0) - Parquet support
  - `opentelemetry-*` - Observability
  - `pandas`, `numpy` - Data processing

**Action:** None required

---

## Layer 2: DI Container Updates

### 2.1: Add DIL Foundation to DI Container

**File:** `foundations/di_container/di_container_service.py`

**Changes:**
1. Add `data_intelligence_foundation` property (optional, like other foundations)
2. Add `get_data_intelligence_foundation()` method
3. No breaking changes (foundation is optional)

**Implementation:**
```python
# In DIContainerService class
@property
def data_intelligence_foundation(self) -> Optional[Any]:
    """Get Data Intelligence Foundation Service."""
    return self.service_registry.get("DataIntelligenceFoundationService")

async def get_data_intelligence_foundation(self) -> Optional[Any]:
    """Get Data Intelligence Foundation Service (async)."""
    return self.data_intelligence_foundation
```

**Acceptance Criteria:**
- [ ] DIL Foundation accessible via DI Container
- [ ] No breaking changes to existing code
- [ ] Foundation is optional (graceful degradation)

---

## Layer 3: Utilities Updates

### 3.1: No Changes Required

**Status:** ✅ **NO CHANGES NEEDED**

**Analysis:**
- Existing utilities (telemetry, error handling, etc.) work with DIL
- DIL SDK will use existing utilities via base classes

**Action:** None required

---

## Layer 4: Public Works Foundation Updates

### 4.1: Add Parsed Data Abstraction (Optional)

**File:** `foundations/public_works_foundation/infrastructure_abstractions/parsed_data_abstraction.py` (NEW)

**Purpose:** Abstraction for parsed data storage (GCS + Supabase pattern)

**Implementation:**
- Extends existing file storage pattern
- Stores parsed data (Parquet files) in GCS
- Stores parsed data metadata in Supabase
- Follows 5-layer pattern (Adapter → Registry → Abstraction)

**5-Layer Pattern:**
1. **Adapter:** `gcs_adapter.py` (exists), `supabase_adapter.py` (exists)
2. **Registry:** `parsed_data_registry.py` (NEW)
3. **Abstraction:** `parsed_data_abstraction.py` (NEW)
4. **Composition:** Use existing `FileManagementCompositionService`
5. **Protocol:** `parsed_data_protocol.py` (NEW)

**Methods:**
```python
async def store_parsed_data(file_id: str, parsed_data: Dict, user_context: Dict) -> Dict
async def get_parsed_data(file_id: str, user_context: Dict) -> Dict
async def list_parsed_data(tenant_id: str, filters: Dict) -> List[Dict]
```

**Acceptance Criteria:**
- [ ] Parsed data abstraction follows 5-layer pattern
- [ ] Integrates with existing GCS/Supabase adapters
- [ ] Supports data_classification filtering

### 4.2: Enhance Content Metadata Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/content_metadata_abstraction.py`

**Changes:**
1. Add `data_classification` parameter to all methods
2. Add tenant filtering to all queries
3. Add `query_by_semantic_id()` method
4. Add vector similarity search (if ArangoDB supports it)

**Key Updates:**
```python
# Add data_classification filtering
async def get_semantic_embeddings(
    self,
    content_id: str,
    tenant_id: Optional[str] = None,
    data_classification: Optional[str] = None  # NEW
) -> List[Dict[str, Any]]:
    filter_conditions = {"content_id": content_id}
    if tenant_id:
        filter_conditions["tenant_id"] = tenant_id
    if data_classification:
        filter_conditions["data_classification"] = data_classification
    # ... rest of implementation
```

**Acceptance Criteria:**
- [ ] All semantic queries filter by tenant_id and data_classification
- [ ] No breaking changes (parameters are optional)
- [ ] Vector search working (if ArangoDB supports)

### 4.3: Enhance File Management Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/file_management_abstraction.py`

**Changes:**
1. Add `data_classification` validation in `create_file()`
2. Add `list_platform_files()` method (tenant_id IS NULL)
3. Add `list_client_files()` method (tenant_id = provided)
4. Add validation methods

**Key Updates:**
```python
async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
    # Validate data_classification
    data_classification = file_data.get("data_classification", "client")
    tenant_id = file_data.get("tenant_id")
    
    if data_classification == "platform" and tenant_id is not None:
        # Platform data can have tenant_id for attribution, but it's optional
        pass
    elif data_classification == "client" and tenant_id is None:
        raise ValueError("Client data must have tenant_id")
    
    # ... rest of implementation

async def list_platform_files(self, user_id: str) -> List[Dict[str, Any]]:
    """List platform files (data_classification = 'platform', tenant_id IS NULL)."""
    return await self.list_files(user_id, tenant_id=None, filters={"data_classification": "platform"})

async def list_client_files(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
    """List client files (data_classification = 'client', tenant_id = provided)."""
    return await self.list_files(user_id, tenant_id=tenant_id, filters={"data_classification": "client"})
```

**Acceptance Criteria:**
- [ ] data_classification validation working
- [ ] Platform/client file listing working
- [ ] No breaking changes

---

## Layer 5: DIL Foundation (NEW)

### 5.1: Create DIL Foundation Structure

**Location:** `foundations/data_intelligence_foundation/`

**Structure:**
```
foundations/data_intelligence_foundation/
├── __init__.py
├── data_intelligence_foundation_service.py  # Foundation service
├── protocols/
│   ├── __init__.py
│   ├── dil_foundation_protocol.py
│   ├── dil_sdk_protocol.py
│   └── dil_capability_protocols.py
├── sdk/
│   ├── __init__.py
│   ├── dil_sdk.py  # Main SDK entry point
│   ├── parse.py  # parse_file()
│   ├── embed.py  # embed_content()
│   ├── semantic.py  # store_semantic(), query_semantic()
│   └── mash.py  # mash.combine() - extensible, empty to start
├── capability_domains/
│   ├── __init__.py
│   ├── orchestration/  # CRITICAL: WAL/Saga for realms
│   ├── data_runtime/  # CRITICAL: Data Mash, semantic-first integration
│   ├── semantic_layer/  # CRITICAL: Contracts, schemas, mappings, ontologies
│   ├── agent_fabric/  # CRITICAL: Agent execution tracking, tool registry
│   ├── pii_deidentification/  # CRITICAL: PII patterns, governance
│   └── observability/  # CRITICAL: Platform data, telemetry, lineage
└── README.md
```

### 5.2: DIL Foundation Service

**File:** `foundations/data_intelligence_foundation/data_intelligence_foundation_service.py`

**Pattern:** Like `AgenticFoundationService` and `ExperienceFoundationService`

**Dependencies:**
- Public Works Foundation (for infrastructure abstractions)
- Curator Foundation (for service registration)
- Agentic Foundation (optional, for agent integration)

**Initialization Order:** After Curator, before Agentic (or after Agentic if it needs Agentic)

**Implementation:**
```python
class DataIntelligenceFoundationService(FoundationServiceBase):
    """DIL Foundation Service - SDK pattern like Agentic/Experience."""
    
    def __init__(self, di_container, public_works_foundation=None, 
                 curator_foundation=None, agentic_foundation=None):
        super().__init__(
            service_name="DataIntelligenceFoundationService",
            di_container=di_container
        )
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        self.agentic_foundation = agentic_foundation
        
        # DIL SDK (main interface)
        self.dil_sdk = None
    
    async def initialize(self) -> bool:
        """Initialize DIL Foundation and SDK."""
        # Initialize DIL SDK
        from .sdk.dil_sdk import DILSDK
        self.dil_sdk = DILSDK(
            di_container=self.di_container,
            public_works_foundation=self.public_works_foundation
        )
        await self.dil_sdk.initialize()
        
        # Register with Curator
        if self.curator_foundation:
            await self._register_with_curator()
        
        return True
    
    def get_sdk(self):
        """Get DIL SDK instance (like Agentic/Experience pattern)."""
        return self.dil_sdk
```

**Acceptance Criteria:**
- [ ] DIL Foundation initializes successfully
- [ ] DIL SDK accessible via `get_sdk()`
- [ ] All 6 capability domains initialized (not just structure - full implementation)
- [ ] Registered with Curator
- [ ] No breaking changes

### 5.4: DIL Capability Domains (CRITICAL PATH - All in Phase 0)

**Strategic Note:** These are NOT deferred - they are the core of DIL Foundation. Everything data-related in the platform goes through DIL SDK, enabling realms to orchestrate freely while DIL handles data governance, lineage, classification, contracts, and metadata unification.

#### 5.4.1: DIL-Orchestration (WAL/Saga)

**File:** `foundations/data_intelligence_foundation/capability_domains/orchestration/dil_orchestration_service.py`

**Purpose:** WAL/Saga patterns for realms to use

**Implementation:**
- WAL (Write-Ahead Logging) - default pattern for multi-step operations
- Saga (Compensating transactions) - fallback pattern
- Event-driven orchestration hooks
- Execution trace storage

**SDK Methods:**
```python
wal_transaction = await dil.wal.begin(operation_id, user_context)
await dil.wal.append(wal_transaction, step_name, payload, compensate_ref)
await dil.wal.commit(wal_transaction)
await dil.wal.rollback(wal_transaction)

saga = await dil.saga.begin(operations, compensations, user_context)
await dil.saga.step(saga, step_name, payload)
await dil.saga.compensate(saga, step_name)
```

**Storage:** ArangoDB collections: `tenant_wal`, `saga_state`

#### 5.4.2: DIL-Data Runtime (Data Mash)

**File:** `foundations/data_intelligence_foundation/capability_domains/data_runtime/dil_data_runtime_service.py`

**Purpose:** Semantic-first data integration, Data Mash runtime

**Implementation:**
- Schema detection and inference
- Semantic normalization
- Mapping with confidence
- Metadata propagation
- Data lineage tracking
- Multi-tenant ETL/ELT

**SDK Methods:**
```python
# Data Mash - semantic-first integration
combined = await dil.mash.combine(data_sources, user_context)
transformed = await dil.mash.transform(data_source, semantic_schema, user_context)
lineage = await dil.mash.get_lineage(data_source_id, user_context)
```

**Storage:** ArangoDB (semantic data), GCS (parsed data), Supabase (metadata)

#### 5.4.3: DIL-Semantic Layer (Contracts, Schemas, Mappings)

**File:** `foundations/data_intelligence_foundation/capability_domains/semantic_layer/dil_semantic_layer_service.py`

**Purpose:** Semantic intelligence foundation - contracts, schemas, mappings, ontologies

**Implementation:**
- Semantic element definitions
- Canonical ontologies
- Graph model representing meaning
- Mapping engine (legacy → inferred → canonical)
- HITL validation layer
- Confidence scoring and versioning
- Semantic contracts (semantic schemas exposed as contracts)

**SDK Methods:**
```python
# Semantic contracts (semantic schemas)
contract = await dil.contracts.create_contract(data_source_id, semantic_schema, user_context)
await dil.contracts.update_contract(contract_id, updates, user_context)
semantic_schema = await dil.contracts.get_semantic_schema(data_source_id, user_context)

# Semantic mappings
mapping = await dil.semantic.create_mapping(column_name, semantic_id, confidence, user_context)
await dil.semantic.validate_mapping(mapping_id, user_context)
await dil.semantic.publish_mapping(mapping_id, user_context)

# Semantic queries
results = await dil.semantic.query_by_semantic_id(semantic_id, user_context)
results = await dil.semantic.vector_search(query_vector, top_k, user_context)
```

**Storage:** ArangoDB collections: `semantic_contracts`, `semantic_mappings`, `semantic_ontologies`, `structured_embeddings`, `semantic_graph_nodes`, `semantic_graph_edges`

#### 5.4.4: DIL-Agent Fabric (Agent Execution Tracking)

**File:** `foundations/data_intelligence_foundation/capability_domains/agent_fabric/dil_agent_fabric_service.py`

**Purpose:** Agent execution tracking, tool registry, prompt versioning

**Implementation:**
- Agent execution logs
- Prompt/response traces (PII-aware)
- Tool capability definitions
- Tool access policy
- Agent registry metadata
- Prompt template versioning

**SDK Methods:**
```python
# Agent execution tracking
await dil.agents.track_execution(agent_id, prompt_hash, response, trace_id, user_context)
execution_log = await dil.agents.get_execution_log(agent_id, trace_id, user_context)
agent_events = await dil.agents.query_agent_events(filters, user_context)

# Tool registry
tools = await dil.agents.list_tools(capability, user_context)
tool_metadata = await dil.agents.get_tool_metadata(tool_id, user_context)
```

**Storage:** ArangoDB collections: `agent_execution_logs`, `prompt_events`, `tool_registry`

#### 5.4.5: DIL-PII & De-identification (Governance Patterns)

**File:** `foundations/data_intelligence_foundation/capability_domains/pii_deidentification/dil_pii_service.py`

**Purpose:** PII classification, tagging, governance patterns

**Implementation:**
- PII classification taxonomy
- Data tagging rules (PII, PCI, PHI, etc.)
- Retention and minimization patterns
- De-ID transforms (linked to semantic layer)
- Tenant-aware PII policies
- Audit hooks

**SDK Methods:**
```python
# PII classification
classification = await dil.pii.classify(data, user_context)
await dil.pii.tag_data(data_id, pii_tags, user_context)
pii_policy = await dil.pii.get_pii_policy(tenant_id, user_context)
```

**Storage:** ArangoDB collections: `pii_classifications`, `pii_policies`

#### 5.4.6: DIL-Observability (Platform Data)

**File:** `foundations/data_intelligence_foundation/capability_domains/observability/dil_observability_service.py`

**Purpose:** Platform data ingestion, normalization, correlation

**Implementation:**
- Telemetry ingestion & normalization
- Realm service logs
- Agent execution logs
- Prompt + response traces (PII-aware)
- Semantic pipeline metrics
- DIL internal metrics
- Error taxonomies
- Failure recovery state (WAL/Saga)
- Distributed tracing

**SDK Methods:**
```python
# Platform data recording
await dil.observability.record_platform_event(event_type, metadata, trace_id, user_context)
await dil.observability.record_agent_log(agent_id, log_data, trace_id, user_context)
await dil.observability.record_semantic_metric(metric_name, value, tags, user_context)

# Platform data queries
platform_data = await dil.observability.query_platform_data(filters, user_context)
trace_data = await dil.observability.get_trace(trace_id, user_context)
metrics = await dil.observability.get_metrics(metric_names, time_range, user_context)
```

**Storage:** ArangoDB collections: `platform_telemetry`, `platform_logs`, `platform_metrics`, `trace_data`

### 5.3: DIL SDK Implementation

**File:** `foundations/data_intelligence_foundation/sdk/dil_sdk.py`

**Pattern:** Like `AgenticFoundationService.get_sdk()` pattern

**Strategic Purpose:**
- **Data Governance Foundation:** All data operations go through DIL SDK
- **Semantic-First Integration:** Embeddings set semantic model/schema, exposed as contracts
- **Realm Freedom:** Realms orchestrate via DIL SDK, DIL handles all data complexity
- **Agent First-Class:** Agentic SDK + DIL SDK enable lightweight agent constructs
- **BYOI Support:** Fully swappable infrastructure via DIL abstractions
- **Cross-Tenant Learning:** Semantic evolution without data leakage

**API:**
```python
from dil import parse, embed, semantic, mash, wal, saga, contracts, agents, observability

# Parse file
result = await dil.parse.parse_file(file_id, user_context)

# Embed content
embeddings = await dil.embed.embed_content(parsed_data, user_context)

# Store semantic data
await dil.semantic.store_semantic(content_id, embeddings, user_context)

# Query semantic data
results = await dil.semantic.query_semantic(query, user_context)

# Data mash (semantic-first integration)
combined = await dil.mash.combine(data_sources, user_context)

# WAL/Saga (for realms)
wal_transaction = await dil.wal.begin(operation_id, user_context)
await dil.wal.append(wal_transaction, step_name, payload)
await dil.wal.commit(wal_transaction)

saga = await dil.saga.begin(operations, compensations, user_context)
await dil.saga.step(saga, step_name, payload)
await dil.saga.compensate(saga, step_name)

# Semantic contracts (semantic schemas)
contract = await dil.contracts.create_contract(data_source_id, semantic_schema, user_context)
await dil.contracts.update_contract(contract_id, updates, user_context)
semantic_schema = await dil.contracts.get_semantic_schema(data_source_id, user_context)

# Agent execution tracking
await dil.agents.track_execution(agent_id, prompt_hash, response, trace_id, user_context)
execution_log = await dil.agents.get_execution_log(agent_id, trace_id, user_context)

# Observability (platform data)
await dil.observability.record_platform_event(event_type, metadata, trace_id, user_context)
platform_data = await dil.observability.query_platform_data(filters, user_context)
```

**Acceptance Criteria:**
- [ ] DIL SDK accessible via `from dil import ...`
- [ ] All MVP methods working (parse, embed, semantic)
- [ ] Data mash structure in place (empty implementation)

---

## Layer 6: Curator Foundation Updates

### 6.1: Register DIL Foundation Capabilities

**File:** `foundations/data_intelligence_foundation/data_intelligence_foundation_service.py`

**Changes:**
- Register DIL Foundation with Curator during initialization
- Register DIL SDK capabilities
- Register Data Mash Solution capabilities (when created)

**Implementation:**
```python
async def _register_with_curator(self):
    """Register DIL Foundation with Curator."""
    if self.curator_foundation and hasattr(self.curator_foundation, 'capability_registry'):
        await self.curator_foundation.capability_registry.register_capability(
            capability_name="data_intelligence_layer",
            capability_type="foundation",
            service_instance=self,
            metadata={
                "version": "1.0.0",
                "sdk_available": True,
                "capabilities": ["parse", "embed", "semantic", "mash"]
            }
        )
```

**Acceptance Criteria:**
- [ ] DIL Foundation registered with Curator
- [ ] Capabilities discoverable
- [ ] No breaking changes

---

## Layer 7: Agentic Foundation Updates

### 7.1: Integrate DIL SDK with Agentic Foundation

**File:** `foundations/agentic_foundation/agentic_foundation_service.py`

**Changes:**
- Optional: Add DIL SDK access for agents
- Agents can use DIL SDK for semantic operations
- No breaking changes (optional integration)

**Implementation:**
```python
# In AgentBase or agent initialization
async def get_dil_sdk(self):
    """Get DIL SDK for semantic operations."""
    dil_foundation = self.di_container.get_foundation_service("DataIntelligenceFoundationService")
    if dil_foundation:
        return dil_foundation.get_sdk()
    return None
```

**Acceptance Criteria:**
- [ ] Agents can access DIL SDK (optional)
- [ ] No breaking changes
- [ ] Graceful degradation if DIL not available

---

## Layer 8: Experience Foundation Updates

### 8.1: No Changes Required

**Status:** ✅ **NO CHANGES NEEDED**

**Analysis:**
- Experience Foundation provides frontend gateway
- DIL SDK will be used by backend services
- Frontend will consume via SOA APIs (not direct SDK access)

**Action:** None required

---

## Layer 9: Smart City Updates

### 9.1: Consolidate Data Steward and Content Steward

**File:** `backend/smart_city/services/data_steward/data_steward_service.py`

**Changes:**
1. Move Content Steward file lifecycle into Data Steward
2. Add `file_lifecycle` module (already exists)
3. Add `data_governance` module (already exists)
4. Add `data_query` module (already exists)
5. Deprecate Content Steward service (keep for backward compatibility)

**Implementation:**
```python
# Data Steward already has file_lifecycle module
# Need to:
# 1. Move Content Steward's file processing into Data Steward
# 2. Update all references from Content Steward to Data Steward
# 3. Add data_classification support
# 4. Add platform/client data governance
```

**Files to Update:**
- `backend/smart_city/services/data_steward/modules/file_lifecycle.py` - Enhance with Content Steward functionality
- `backend/smart_city/services/data_steward/modules/data_governance.py` - Add platform/client governance
- `backend/smart_city/services/data_steward/modules/data_query.py` - Add semantic queries
- `backend/smart_city/services/content_steward/content_steward_service.py` - Deprecate (keep for backward compat)

**Acceptance Criteria:**
- [ ] Data Steward handles all file lifecycle operations
- [ ] Content Steward deprecated (backward compatible)
- [ ] All references updated
- [ ] data_classification support added

### 9.2: Update City Manager

**File:** `backend/smart_city/services/city_manager/modules/realm_orchestration.py`

**Changes:**
- Update service discovery to use Data Steward (not Content Steward)
- Keep Content Steward for backward compatibility

**Acceptance Criteria:**
- [ ] City Manager uses Data Steward
- [ ] Backward compatibility maintained

---

## Layer 10: Business Enablement Updates

### 10.1: Update ContentAnalysisOrchestrator to Use DIL SDK

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/content_analysis_orchestrator.py`

**Changes:**
1. Replace direct infrastructure calls with DIL SDK
2. Use `dil.parse.parse_file()` instead of direct FileParserService
3. Use `dil.embed.embed_content()` instead of direct HF agent
4. Use `dil.semantic.store_semantic()` instead of direct ContentMetadataAbstraction
5. Generate 3rd embedding (samples_embedding)

**Key Updates:**
```python
# OLD:
parse_result = await file_parser.parse_file(file_id, parse_options, user_context)

# NEW:
dil_sdk = await self._get_dil_sdk()
parse_result = await dil_sdk.parse.parse_file(file_id, parse_options, user_context)

# OLD:
embedding_result = await self.hf_inference_agent.generate_embedding(...)

# NEW:
embeddings = await dil_sdk.embed.embed_content(parsed_data, user_context)

# OLD:
await content_metadata_abstraction.store_semantic_embeddings(...)

# NEW:
await dil_sdk.semantic.store_semantic(content_id, embeddings, user_context)
```

**3rd Embedding Fix:**
```python
# Generate samples_embedding from sample column values
samples = [str(record.get(column_name, ""))[:100] for record in records[:10]]
samples_text = " ".join(samples)
samples_embedding = await dil_sdk.embed.embed_content(samples_text, user_context)
```

**Acceptance Criteria:**
- [ ] ContentAnalysisOrchestrator uses DIL SDK
- [ ] 3rd embedding (samples_embedding) generated
- [ ] No breaking changes to API
- [ ] Backward compatibility maintained

### 10.2: Create Data Mash Enabling Services (Structure Only)

**Location:** `backend/business_enablement/enabling_services/`

**New Services (Structure Only, Empty Implementation):**
- `data_ingestion_service/` - Ingest data (wraps FileManagement)
- `semantic_embedding_service/` - Embed content (wraps DIL SDK)
- `semantic_query_service/` - Query semantic data (wraps DIL SDK)
- `data_mash_service/` - Data mash operations (extensible, empty)

**Acceptance Criteria:**
- [ ] Service structures created
- [ ] Registered with Curator
- [ ] Empty implementations (extensible)

---

## Layer 11: Journey Updates

### 11.1: Create Data Mash Journey Orchestrator

**Location:** `backend/journey/services/data_mash_journey_orchestrator_service/`

**Pattern:** Like `StructuredJourneyOrchestratorService`

**Structure:**
```
backend/journey/services/data_mash_journey_orchestrator_service/
├── data_mash_journey_orchestrator_service.py
├── modules/
│   ├── ingest_journey.py  # Step 1: Ingest data
│   ├── parse_journey.py  # Step 2: Parse data
│   ├── embed_journey.py  # Step 3: Embed/AI enable
│   └── use_journey.py  # Step 4: Use AI data
└── templates/
    ├── structured_data_journey.json
    └── unstructured_data_journey.json
```

**Journey Steps:**
1. **Ingest Data** → DIL SDK (via FileManagementAbstraction)
2. **Parse Data** → DIL SDK.parse.parse_file()
3. **Embed/AI Enable** → DIL SDK.embed.embed_content()
4. **Use AI Data** → DIL SDK.semantic.query_semantic() → Insights, integration, POC

**Acceptance Criteria:**
- [ ] Data Mash Journey orchestrator created
- [ ] All 4 steps implemented
- [ ] Registered with Curator
- [ ] Journey templates created

### 11.2: Refactor MVP Journey to Use Data Mash

**File:** `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

**Changes:**
- Compose Data Mash Journey instead of direct ContentAnalysisOrchestrator
- Showcase Data Mash components:
  - Ingest data (file upload)
  - Parse it (file parsing)
  - Embed/AI enable it (semantic processing)
  - Use AI data (insights, integration, POC proposals)

**Acceptance Criteria:**
- [ ] MVP Journey uses Data Mash Journey
- [ ] All 4 components showcased
- [ ] No breaking changes to frontend API

---

## Layer 12: Solution Updates

### 12.1: Create Data Mash Solution

**Location:** `backend/solution/services/data_mash_solution_service/`

**Pattern:** Like `SolutionComposerService`

**Structure:**
```
backend/solution/services/data_mash_solution_service/
├── data_mash_solution_service.py
├── modules/
│   ├── solution_design.py  # Design data mash solutions
│   ├── journey_composition.py  # Compose data mash journeys
│   └── solution_analytics.py  # Track solution success
└── templates/
    ├── structured_data_mash.json
    ├── unstructured_data_mash.json
    └── hybrid_data_mash.json
```

**SOA APIs:**
```python
async def design_data_mash_solution(data_type: str, requirements: Dict) -> Dict
async def execute_data_mash_solution(solution_id: str, user_context: Dict) -> Dict
async def get_data_mash_status(solution_id: str) -> Dict
```

**Acceptance Criteria:**
- [ ] Data Mash Solution created
- [ ] Composes Data Mash Journeys
- [ ] Registered with Curator
- [ ] Solution templates created

---

## Layer 13: Frontend Updates

### 13.1: Update Content Pillar to Show Embedded Data Graphs

**Location:** `symphainy-frontend/` (separate repo)

**Changes:**
1. Replace content metadata display with embedded data graphs
2. Show semantic embeddings (3 embeddings per column)
3. Show semantic graph (for unstructured data)
4. Use semantic data layer instead of raw file data

**API Changes:**
- Use DIL SDK semantic queries instead of file metadata
- Display semantic embeddings/graphs
- Show data classification (platform vs client)

**Acceptance Criteria:**
- [ ] Content pillar shows embedded data graphs
- [ ] Semantic data displayed correctly
- [ ] No breaking changes to user experience

### 13.2: Update Insights Pillar to Use Semantic Data Layer

**Location:** `symphainy-frontend/` (separate repo)

**Changes:**
1. Query semantic data layer instead of client data files
2. Use semantic embeddings for insights
3. Show cross-file semantic relationships

**API Changes:**
- Use DIL SDK semantic queries
- Query by semantic_id
- Show semantic relationships

**Acceptance Criteria:**
- [ ] Insights uses semantic data layer
- [ ] Cross-file insights working
- [ ] No breaking changes

---

## Implementation Order

### Phase 0.1: Foundation Setup (Week 1-2)
1. ✅ Layer 1: Infrastructure (no changes)
2. ✅ Layer 2: DI Container (add DIL Foundation property)
3. ✅ Layer 3: Utilities (no changes)
4. ✅ Layer 4: Public Works (enhance abstractions)
5. ✅ Layer 5: DIL Foundation (create structure + SDK + ALL capability domains)
   - DIL-Orchestration (WAL/Saga)
   - DIL-Data Runtime (Data Mash)
   - DIL-Semantic Layer (Contracts, Schemas, Mappings)
   - DIL-Agent Fabric (Agent Execution Tracking)
   - DIL-PII (Governance Patterns)
   - DIL-Observability (Platform Data)
6. ✅ Layer 6: Curator (register DIL Foundation)

### Phase 0.2: Smart City Consolidation (Week 3)
7. ✅ Layer 9: Smart City (consolidate Data/Content Steward, use DIL SDK)

### Phase 0.3: Business Enablement Integration (Week 3-4)
8. ✅ Layer 10: Business Enablement (update ContentAnalysisOrchestrator to use DIL SDK)
   - Use DIL SDK for all data operations
   - Use DIL WAL/Saga for multi-step operations
   - Use DIL semantic contracts for data sources
   - Use DIL agent tracking for agent calls

### Phase 0.4: Journey & Solution (Week 4-5)
9. ✅ Layer 11: Journey (create Data Mash Journey, refactor MVP Journey)
   - Data Mash Journey uses DIL SDK throughout
   - MVP Journey showcases DIL capabilities
10. ✅ Layer 12: Solution (create Data Mash Solution)
    - Composes Data Mash Journeys
    - Uses DIL SDK for orchestration

### Phase 0.5: Frontend Integration (Week 5-6)
11. ✅ Layer 13: Frontend (update Content/Insights pillars)
    - Content Pillar: Show semantic contracts, embedded data graphs
    - Insights Pillar: Use semantic data layer, semantic queries

### Phase 0.6: Agentic Integration (Week 6)
12. ✅ Layer 7: Agentic (integrate DIL SDK for agent execution tracking)
13. ✅ Layer 8: Experience (no changes)

---

## Critical Dependencies

### Must Have (Blocking):
- Public Works Foundation (Layer 4)
- DIL Foundation (Layer 5) - **ALL 6 capability domains required**
  - DIL-Orchestration (WAL/Saga) - **CRITICAL for realms**
  - DIL-Data Runtime (Data Mash) - **CRITICAL for semantic-first integration**
  - DIL-Semantic Layer (Contracts) - **CRITICAL for semantic schemas**
  - DIL-Agent Fabric (Tracking) - **CRITICAL for agents as first-class citizens**
  - DIL-PII (Governance) - **CRITICAL for data governance**
  - DIL-Observability (Platform Data) - **CRITICAL for platform operations**
- Data Steward Consolidation (Layer 9)
- ContentAnalysisOrchestrator Updates (Layer 10)

### Should Have (Non-Blocking):
- Data Mash Journey (Layer 11)
- Data Mash Solution (Layer 12)
- Frontend Updates (Layer 13)

### Nice to Have (Optional):
- Agentic Integration (Layer 7)
- Experience Integration (Layer 8)

---

## Testing Strategy

### Unit Tests:
- Each layer tested independently
- Mock dependencies for isolated testing

### Integration Tests:
- Test layer interactions
- Test DIL SDK end-to-end
- Test Data Mash Journey end-to-end

### E2E Tests:
- Test full flow: Upload → Parse → Embed → Display
- Test platform vs client data distinction
- Test semantic queries

---

## Rollback Strategy

### If Issues Arise:
1. DIL Foundation is optional (graceful degradation)
2. ContentAnalysisOrchestrator can fall back to direct infrastructure calls
3. Content Steward kept for backward compatibility
4. Frontend can use old APIs if new ones fail

---

## Success Criteria

### Phase 0 Complete When:
1. ✅ DIL Foundation operational with ALL 6 capability domains
2. ✅ DIL SDK working (parse, embed, semantic, mash, wal, saga, contracts, agents, observability)
3. ✅ WAL/Saga patterns working for realms
4. ✅ Semantic contracts working (semantic schemas exposed as contracts)
5. ✅ Agent execution tracking working
6. ✅ Platform data observability working
7. ✅ Data Steward consolidated (uses DIL SDK)
8. ✅ ContentAnalysisOrchestrator uses DIL SDK for all data operations
9. ✅ Data Mash Journey operational (uses DIL SDK throughout)
10. ✅ MVP Journey showcases Data Mash and DIL capabilities
11. ✅ Frontend shows semantic contracts and embedded data graphs
12. ✅ Insights uses semantic data layer
13. ✅ Realms can orchestrate freely via DIL SDK
14. ✅ Agents are first-class citizens (Agentic SDK + DIL SDK)
15. ✅ No breaking changes
16. ✅ All tests passing

---

## Next Steps

1. **Review and approve this plan**
2. **Start Phase 0.1: Foundation Setup**
3. **Execute layer by layer**
4. **Test after each layer**
5. **Document as you go**

---

## Conclusion

This E2E execution plan provides a systematic, layer-by-layer approach to implementing DIL Foundation with SDK, Data Mash Solution, and refactored MVP Journey. Each layer builds on the previous, ensuring no breaking changes and incremental value delivery.

**Key Principles:**
- Incremental implementation
- No breaking changes
- Graceful degradation
- Extensible design
- Test as you go

