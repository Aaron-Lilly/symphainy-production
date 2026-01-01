# DIL Foundation v2: Execution Plan
## Cross-Cutting Data Governance for Semantic-First Integration

**Date:** January 2025  
**Status:** 🎯 **READY FOR IMPLEMENTATION**  
**Approach:** Break and fix - bring vision to life

---

## Executive Summary

This plan implements DIL Foundation as the **cross-cutting data governance, lineage, classification, contracts, and metadata unification layer** that enables semantic-first data integration across the platform.

**Strategic Principle:** "If everything is data and everything needs to be correlated, then Data Governance is foundational."

**Mindset:** Break and fix - implement the vision correctly, fix what breaks.

---

## Vision: What DIL Foundation Enables

### 1. Semantic-First Data Integration
- Embeddings set semantic model/schema for each data source
- Semantic schemas exposed as "semantic data contracts"
- Platform operates via semantic contracts (not raw data)
- Client updates data source → update contract → everything keeps working

### 2. Cross-Cutting Data Governance
- **Lineage:** Track data flow across all realms
- **Classification:** Platform vs client data distinction
- **Contracts:** Semantic schemas as first-class contracts
- **Metadata Unification:** Single source of truth for all data metadata

### 3. Realm Freedom
- Realms orchestrate via DIL SDK
- DIL handles all data complexity (governance, lineage, classification)
- Realms don't need to worry about data infrastructure

### 4. Agents as First-Class Citizens
- Agentic SDK + DIL SDK = lightweight agent constructs with heavyweight maturity
- Agent execution tracked via DIL SDK
- Agents use DIL SDK for all data operations

### 5. Platform-Wide Correlation
- All platform data flows through DIL
- WAL/Saga for reliable multi-step operations
- Observability for platform health
- Cross-tenant learning without data leakage

---

## DIL Foundation Architecture

### Core Structure

```
foundations/data_intelligence_foundation/
├── data_intelligence_foundation_service.py  # Foundation service
├── protocols/
│   ├── dil_foundation_protocol.py
│   └── dil_sdk_protocol.py
├── sdk/
│   ├── dil_sdk.py  # Main SDK entry point
│   ├── data_operations.py  # Upload, parse, embed, query
│   ├── governance.py  # Lineage, classification, contracts
│   ├── orchestration.py  # WAL, Saga
│   ├── agents.py  # Agent execution tracking
│   └── observability.py  # Platform data, telemetry, tracing
└── capability_domains/
    ├── orchestration/  # WAL/Saga implementation
    ├── data_runtime/  # Data Mash, semantic-first integration
    ├── semantic_layer/  # Contracts, schemas, mappings, ontologies
    ├── agent_fabric/  # Agent execution tracking, tool registry
    ├── pii_governance/  # PII patterns, governance
    └── observability/  # Platform data, telemetry, correlation
```

### DIL SDK API (Complete)

```python
from dil import data, governance, orchestration, agents, observability

# ============================================================================
# DATA OPERATIONS (Upload, Parse, Embed, Query)
# ============================================================================

# Upload
file_metadata = await dil.data.upload_file(file_data, filename, user_context)

# Parse
parse_result = await dil.data.parse_file(file_id, parse_options, user_context)

# Embed
embeddings = await dil.data.embed_content(parsed_data, embedding_type, user_context)

# Store semantic
await dil.data.store_semantic(content_id, embeddings, semantic_graph, user_context)

# Query semantic
results = await dil.data.query_semantic(query, filters, user_context)
results = await dil.data.query_by_semantic_id(semantic_id, user_context)
results = await dil.data.vector_search(query_vector, top_k, user_context)

# ============================================================================
# GOVERNANCE (Lineage, Classification, Contracts)
# ============================================================================

# Lineage
lineage = await dil.governance.get_lineage(data_source_id, user_context)
await dil.governance.record_lineage(source_id, target_id, transformation, user_context)

# Classification
await dil.governance.classify_data(data_id, classification, tenant_id, user_context)
platform_data = await dil.governance.query_platform_data(filters, user_context)
client_data = await dil.governance.query_client_data(tenant_id, filters, user_context)

# Contracts (Semantic Schemas)
contract = await dil.governance.create_contract(data_source_id, semantic_schema, user_context)
await dil.governance.update_contract(contract_id, updates, user_context)
semantic_schema = await dil.governance.get_semantic_schema(data_source_id, user_context)
contracts = await dil.governance.list_contracts(tenant_id, filters, user_context)

# ============================================================================
# ORCHESTRATION (WAL, Saga)
# ============================================================================

# WAL (Write-Ahead Logging)
wal_transaction = await dil.orchestration.wal.begin(operation_id, user_context)
await dil.orchestration.wal.append(wal_transaction, step_name, payload, compensate_ref)
await dil.orchestration.wal.commit(wal_transaction)
await dil.orchestration.wal.rollback(wal_transaction)

# Saga (Compensating Transactions)
saga = await dil.orchestration.saga.begin(operations, compensations, user_context)
await dil.orchestration.saga.step(saga, step_name, payload)
await dil.orchestration.saga.compensate(saga, step_name)
await dil.orchestration.saga.complete(saga)

# ============================================================================
# AGENTS (Execution Tracking, Tool Registry)
# ============================================================================

# Execution Tracking
await dil.agents.track_execution(agent_id, prompt_hash, response, trace_id, user_context)
execution_log = await dil.agents.get_execution_log(agent_id, trace_id, user_context)
agent_events = await dil.agents.query_agent_events(filters, user_context)

# Tool Registry
tools = await dil.agents.list_tools(capability, user_context)
tool_metadata = await dil.agents.get_tool_metadata(tool_id, user_context)

# ============================================================================
# OBSERVABILITY (Platform Data, Telemetry, Tracing)
# ============================================================================

# Platform Data Recording
await dil.observability.record_platform_event(event_type, metadata, trace_id, user_context)
await dil.observability.record_agent_log(agent_id, log_data, trace_id, user_context)
await dil.observability.record_semantic_metric(metric_name, value, tags, user_context)

# Platform Data Queries
platform_data = await dil.observability.query_platform_data(filters, user_context)
trace_data = await dil.observability.get_trace(trace_id, user_context)
metrics = await dil.observability.get_metrics(metric_names, time_range, user_context)
```

---

## Layer-by-Layer Implementation

### Layer 1: Infrastructure Dependencies

**Status:** ✅ **NO CHANGES NEEDED**

All required dependencies exist in `pyproject.toml`:
- `python-arango` - ArangoDB client
- `transformers` - HuggingFace embeddings
- `pyarrow` - Parquet support
- `opentelemetry-*` - Observability
- `pandas`, `numpy` - Data processing

**Action:** None required

---

### Layer 2: DI Container Updates

**File:** `foundations/di_container/di_container_service.py`

**Changes:**
1. Add `data_intelligence_foundation` property
2. Add `get_data_intelligence_foundation()` method

**Implementation:**
```python
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

---

### Layer 3: Utilities Updates

**Status:** ✅ **NO CHANGES NEEDED**

Existing utilities work with DIL Foundation.

**Action:** None required

---

### Layer 4: Public Works Foundation Updates

#### 4.1: Enhance Content Metadata Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/content_metadata_abstraction.py`

**Changes:**
1. Add `data_classification` parameter to all methods
2. Add tenant filtering to all queries
3. Add `query_by_semantic_id()` method
4. Add vector similarity search
5. Add semantic contract storage methods

**Key Updates:**
```python
async def get_semantic_embeddings(
    self,
    content_id: str,
    tenant_id: Optional[str] = None,
    data_classification: Optional[str] = None
) -> List[Dict[str, Any]]:
    filter_conditions = {"content_id": content_id}
    if tenant_id:
        filter_conditions["tenant_id"] = tenant_id
    if data_classification:
        filter_conditions["data_classification"] = data_classification
    # ... implementation

async def query_by_semantic_id(
    self,
    semantic_id: str,
    tenant_id: Optional[str] = None,
    data_classification: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query by semantic ID (semantic contract lookup)."""
    # ... implementation

async def vector_search(
    self,
    query_vector: List[float],
    top_k: int = 10,
    tenant_id: Optional[str] = None,
    data_classification: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Vector similarity search."""
    # ... implementation
```

**Acceptance Criteria:**
- [ ] All semantic queries filter by tenant_id and data_classification
- [ ] Vector search working
- [ ] Semantic contract queries working

#### 4.2: Enhance File Management Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/file_management_abstraction.py`

**Changes:**
1. Add `data_classification` validation in `create_file()`
2. Add `list_platform_files()` method
3. Add `list_client_files()` method
4. Add lineage tracking methods

**Key Updates:**
```python
async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
    # Validate data_classification
    data_classification = file_data.get("data_classification", "client")
    tenant_id = file_data.get("tenant_id")
    
    if data_classification == "platform" and tenant_id is not None:
        # Platform data can have tenant_id for attribution
        pass
    elif data_classification == "client" and tenant_id is None:
        raise ValueError("Client data must have tenant_id")
    
    # ... implementation

async def list_platform_files(self, user_id: str) -> List[Dict[str, Any]]:
    """List platform files (data_classification = 'platform')."""
    return await self.list_files(user_id, tenant_id=None, filters={"data_classification": "platform"})

async def list_client_files(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
    """List client files (data_classification = 'client', tenant_id = provided)."""
    return await self.list_files(user_id, tenant_id=tenant_id, filters={"data_classification": "client"})
```

**Acceptance Criteria:**
- [ ] data_classification validation working
- [ ] Platform/client file listing working
- [ ] Lineage tracking working

#### 4.3: Create ArangoDB Initialization Script

**File:** `scripts/initialize_arangodb_collections.py`

**Purpose:** Create all ArangoDB collections and indexes for DIL Foundation

**Collections to Create:**
- `structured_embeddings` (document) - Semantic embeddings
- `semantic_graph_nodes` (document) - Semantic graph nodes
- `semantic_graph_edges` (edge) - Semantic graph edges
- `content_metadata` (document) - Content metadata
- `semantic_contracts` (document) - Semantic contracts (NEW)
- `semantic_mappings` (document) - Semantic mappings (NEW)
- `tenant_wal` (document) - WAL entries (NEW)
- `saga_state` (document) - Saga state (NEW)
- `agent_execution_logs` (document) - Agent execution logs (NEW)
- `prompt_events` (document) - Prompt events (NEW)
- `platform_telemetry` (document) - Platform telemetry (NEW)
- `data_lineage` (edge) - Data lineage (NEW)

**Indexes to Create:**
- All collections: Index on `data_classification`, `tenant_id`, composite `(data_classification, tenant_id)`
- `structured_embeddings`: Index on `content_id`, `file_id`, `semantic_id`
- `semantic_contracts`: Index on `data_source_id`, `tenant_id`, `version`
- `tenant_wal`: Index on `saga_id`, `operation_id`, `status`
- `saga_state`: Index on `saga_id`, `status`
- `agent_execution_logs`: Index on `agent_id`, `trace_id`, `timestamp`
- `prompt_events`: Index on `agent_id`, `trace_id`, `prompt_hash`
- `data_lineage`: Index on `source_id`, `target_id`, `transformation_type`

**Acceptance Criteria:**
- [ ] All collections created
- [ ] All indexes created
- [ ] Script runs as part of deployment

---

### Layer 5: DIL Foundation (NEW)

#### 5.1: Create DIL Foundation Service

**File:** `foundations/data_intelligence_foundation/data_intelligence_foundation_service.py`

**Pattern:** Like `AgenticFoundationService` and `ExperienceFoundationService`

**Dependencies:**
- Public Works Foundation (for infrastructure abstractions)
- Curator Foundation (for service registration)
- Agentic Foundation (for agent integration)

**Initialization Order:** After Curator, before Agentic (or after Agentic if it needs Agentic)

**Implementation:**
```python
class DataIntelligenceFoundationService(FoundationServiceBase):
    """DIL Foundation Service - Cross-cutting data governance layer."""
    
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
        
        # Capability domains
        self.orchestration_service = None
        self.data_runtime_service = None
        self.semantic_layer_service = None
        self.agent_fabric_service = None
        self.pii_governance_service = None
        self.observability_service = None
    
    async def initialize(self) -> bool:
        """Initialize DIL Foundation and all capability domains."""
        # Initialize DIL SDK
        from .sdk.dil_sdk import DILSDK
        self.dil_sdk = DILSDK(
            di_container=self.di_container,
            public_works_foundation=self.public_works_foundation,
            agentic_foundation=self.agentic_foundation
        )
        await self.dil_sdk.initialize()
        
        # Initialize capability domains
        await self._initialize_capability_domains()
        
        # Register with Curator
        if self.curator_foundation:
            await self._register_with_curator()
        
        return True
    
    async def _initialize_capability_domains(self):
        """Initialize all DIL capability domains."""
        from .capability_domains.orchestration.dil_orchestration_service import DILOrchestrationService
        from .capability_domains.data_runtime.dil_data_runtime_service import DILDataRuntimeService
        from .capability_domains.semantic_layer.dil_semantic_layer_service import DILSemanticLayerService
        from .capability_domains.agent_fabric.dil_agent_fabric_service import DILAgentFabricService
        from .capability_domains.pii_governance.dil_pii_service import DILPIIGovernanceService
        from .capability_domains.observability.dil_observability_service import DILObservabilityService
        
        # Initialize all domains
        self.orchestration_service = DILOrchestrationService(...)
        await self.orchestration_service.initialize()
        
        self.data_runtime_service = DILDataRuntimeService(...)
        await self.data_runtime_service.initialize()
        
        self.semantic_layer_service = DILSemanticLayerService(...)
        await self.semantic_layer_service.initialize()
        
        self.agent_fabric_service = DILAgentFabricService(...)
        await self.agent_fabric_service.initialize()
        
        self.pii_governance_service = DILPIIGovernanceService(...)
        await self.pii_governance_service.initialize()
        
        self.observability_service = DILObservabilityService(...)
        await self.observability_service.initialize()
    
    def get_sdk(self):
        """Get DIL SDK instance."""
        return self.dil_sdk
```

**Acceptance Criteria:**
- [ ] DIL Foundation initializes successfully
- [ ] All 6 capability domains initialized
- [ ] DIL SDK accessible via `get_sdk()`
- [ ] Registered with Curator

#### 5.2: Create DIL SDK

**File:** `foundations/data_intelligence_foundation/sdk/dil_sdk.py`

**Purpose:** Main SDK entry point - exposes all DIL capabilities

**Structure:**
```python
class DILSDK:
    """Data Intelligence Layer SDK - Cross-cutting data governance."""
    
    def __init__(self, di_container, public_works_foundation, agentic_foundation=None):
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.agentic_foundation = agentic_foundation
        
        # SDK modules
        self.data = DataOperationsModule(...)
        self.governance = GovernanceModule(...)
        self.orchestration = OrchestrationModule(...)
        self.agents = AgentsModule(...)
        self.observability = ObservabilityModule(...)
    
    async def initialize(self):
        """Initialize DIL SDK and all modules."""
        await self.data.initialize()
        await self.governance.initialize()
        await self.orchestration.initialize()
        await self.agents.initialize()
        await self.observability.initialize()
```

**SDK Modules:**
- `data_operations.py` - Upload, parse, embed, query
- `governance.py` - Lineage, classification, contracts
- `orchestration.py` - WAL, Saga
- `agents.py` - Agent execution tracking
- `observability.py` - Platform data, telemetry, tracing

**Acceptance Criteria:**
- [ ] DIL SDK initializes successfully
- [ ] All SDK modules accessible
- [ ] All API methods implemented

#### 5.3: Implement Capability Domains

**All 6 domains must be fully implemented (not just structure):**

1. **DIL-Orchestration** - WAL/Saga implementation
2. **DIL-Data Runtime** - Data Mash, semantic-first integration
3. **DIL-Semantic Layer** - Contracts, schemas, mappings, ontologies
4. **DIL-Agent Fabric** - Agent execution tracking, tool registry
5. **DIL-PII Governance** - PII patterns, governance
6. **DIL-Observability** - Platform data, telemetry, correlation

**Acceptance Criteria:**
- [ ] All capability domains fully implemented
- [ ] All domains integrated with DIL SDK
- [ ] All domains tested

---

### Layer 6: Curator Foundation Updates

**File:** `foundations/data_intelligence_foundation/data_intelligence_foundation_service.py`

**Changes:**
- Register DIL Foundation with Curator during initialization
- Register all DIL SDK capabilities
- Register all capability domains

**Acceptance Criteria:**
- [ ] DIL Foundation registered with Curator
- [ ] All capabilities discoverable

---

### Layer 7: Agentic Foundation Updates

**File:** `foundations/agentic_foundation/agentic_foundation_service.py`

**Changes:**
1. Integrate DIL SDK for agent execution tracking
2. Agents automatically track execution via DIL SDK
3. Agent tool registry uses DIL SDK

**Implementation:**
```python
# In AgentBase or agent initialization
async def execute_agent(self, prompt, tools, user_context):
    """Execute agent with DIL SDK tracking."""
    # Get DIL SDK
    dil_foundation = self.di_container.get_foundation_service("DataIntelligenceFoundationService")
    if dil_foundation:
        dil_sdk = dil_foundation.get_sdk()
        
        # Track execution
        trace_id = user_context.get("trace_id") or str(uuid.uuid4())
        await dil_sdk.agents.track_execution(
            agent_id=self.agent_name,
            prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
            response=None,  # Will be updated after execution
            trace_id=trace_id,
            user_context=user_context
        )
    
    # Execute agent
    response = await self._execute(prompt, tools, user_context)
    
    # Update execution log
    if dil_sdk:
        await dil_sdk.agents.track_execution(
            agent_id=self.agent_name,
            prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
            response=response,
            trace_id=trace_id,
            user_context=user_context
        )
    
    return response
```

**Acceptance Criteria:**
- [ ] Agents automatically track execution via DIL SDK
- [ ] Agent execution logs stored in DIL
- [ ] No breaking changes to agent API

---

### Layer 8: Experience Foundation Updates

**Status:** ✅ **NO CHANGES NEEDED**

Experience Foundation provides frontend gateway. DIL SDK used by backend services.

**Action:** None required

---

### Layer 9: Smart City Updates

#### 9.1: Consolidate Data Steward and Content Steward

**File:** `backend/smart_city/services/data_steward/data_steward_service.py`

**Changes:**
1. Move Content Steward file lifecycle into Data Steward
2. Update Data Steward to use DIL SDK for all data operations
3. Deprecate Content Steward (remove, not keep for backward compatibility)

**Implementation:**
```python
class DataStewardService(SmartCityRoleBase):
    """Data Steward - Consolidated from Data Steward + Content Steward."""
    
    def __init__(self, ...):
        # Get DIL SDK
        self.dil_sdk = None
    
    async def initialize(self):
        """Initialize Data Steward with DIL SDK."""
        dil_foundation = self.di_container.get_foundation_service("DataIntelligenceFoundationService")
        if dil_foundation:
            self.dil_sdk = dil_foundation.get_sdk()
        
        # Initialize modules
        await self.file_lifecycle.initialize()
        await self.data_governance.initialize()
        await self.data_query.initialize()
    
    async def process_upload(self, file_data, metadata, user_context):
        """Process file upload using DIL SDK."""
        # Use DIL SDK for upload
        file_metadata = await self.dil_sdk.data.upload_file(
            file_data, metadata.get("filename"), user_context
        )
        
        # Record lineage
        await self.dil_sdk.governance.record_lineage(
            source_id=None,
            target_id=file_metadata["file_id"],
            transformation="upload",
            user_context=user_context
        )
        
        return file_metadata
```

**Acceptance Criteria:**
- [ ] Data Steward uses DIL SDK for all data operations
- [ ] Content Steward removed (not deprecated)
- [ ] All references updated

#### 9.2: Update City Manager

**File:** `backend/smart_city/services/city_manager/modules/realm_orchestration.py`

**Changes:**
- Update service discovery to use Data Steward (not Content Steward)
- Remove Content Steward references

**Acceptance Criteria:**
- [ ] City Manager uses Data Steward
- [ ] Content Steward references removed

---

### Layer 10: Business Enablement Updates

#### 10.1: Update ContentAnalysisOrchestrator to Use DIL SDK

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/content_analysis_orchestrator.py`

**Changes:**
1. Replace all direct infrastructure calls with DIL SDK
2. Use DIL SDK for all data operations
3. Use DIL WAL/Saga for multi-step operations
4. Use DIL agent tracking for agent calls
5. Generate 3rd embedding (samples_embedding)

**Implementation:**
```python
class ContentAnalysisOrchestrator(OrchestratorBase):
    """Content Analysis Orchestrator - Uses DIL SDK."""
    
    async def initialize(self):
        """Initialize with DIL SDK."""
        dil_foundation = self.di_container.get_foundation_service("DataIntelligenceFoundationService")
        if dil_foundation:
            self.dil_sdk = dil_foundation.get_sdk()
    
    async def parse_file(self, file_id, parse_options, user_context):
        """Parse file using DIL SDK."""
        # Use DIL SDK
        parse_result = await self.dil_sdk.data.parse_file(
            file_id, parse_options, user_context
        )
        return parse_result
    
    async def _process_structured_semantic(self, parse_result, user_context):
        """Process structured data semantically using DIL SDK."""
        # Generate embeddings using DIL SDK
        embeddings = []
        for column_name in columns:
            # Metadata embedding
            metadata_emb = await self.dil_sdk.data.embed_content(
                column_name, "metadata", user_context
            )
            
            # Meaning embedding
            meaning_emb = await self.dil_sdk.data.embed_content(
                column_name, "meaning", user_context
            )
            
            # Samples embedding (3rd embedding - from sample values)
            samples = [str(record.get(column_name, ""))[:100] for record in records[:10]]
            samples_text = " ".join(samples)
            samples_emb = await self.dil_sdk.data.embed_content(
                samples_text, "samples", user_context
            )
            
            embeddings.append({
                "column_name": column_name,
                "metadata_embedding": metadata_emb,
                "meaning_embedding": meaning_emb,
                "samples_embedding": samples_emb  # 3rd embedding
            })
        
        return {"success": True, "embeddings": embeddings}
    
    async def _store_semantic_via_content_metadata(self, file_id, parse_result, semantic_result, data_type, user_context):
        """Store semantic data using DIL SDK."""
        # Use DIL SDK for semantic storage
        await self.dil_sdk.data.store_semantic(
            content_id=content_id,
            embeddings=semantic_result.get("embeddings"),
            semantic_graph=semantic_result.get("semantic_graph"),
            user_context=user_context
        )
        
        # Record lineage
        await self.dil_sdk.governance.record_lineage(
            source_id=file_id,
            target_id=content_id,
            transformation="semantic_processing",
            user_context=user_context
        )
```

**Acceptance Criteria:**
- [ ] ContentAnalysisOrchestrator uses DIL SDK for all data operations
- [ ] 3rd embedding (samples_embedding) generated
- [ ] WAL/Saga used for multi-step operations
- [ ] Agent execution tracked via DIL SDK

---

### Layer 11: Journey Updates

#### 11.1: Create Data Mash Journey Orchestrator

**Location:** `backend/journey/services/data_mash_journey_orchestrator_service/`

**Pattern:** Like `StructuredJourneyOrchestratorService`

**Journey Steps:**
1. **Ingest Data** → DIL SDK.data.upload_file()
2. **Parse Data** → DIL SDK.data.parse_file()
3. **Embed/AI Enable** → DIL SDK.data.embed_content()
4. **Use AI Data** → DIL SDK.data.query_semantic() → Insights, integration, POC

**Implementation:**
```python
class DataMashJourneyOrchestratorService(RealmServiceBase):
    """Data Mash Journey Orchestrator - Uses DIL SDK throughout."""
    
    async def execute_journey(self, journey_id, user_context):
        """Execute Data Mash Journey using DIL SDK."""
        # Get DIL SDK
        dil_foundation = self.di_container.get_foundation_service("DataIntelligenceFoundationService")
        dil_sdk = dil_foundation.get_sdk()
        
        # Step 1: Ingest Data
        file_metadata = await dil_sdk.data.upload_file(...)
        
        # Step 2: Parse Data
        parse_result = await dil_sdk.data.parse_file(...)
        
        # Step 3: Embed/AI Enable
        embeddings = await dil_sdk.data.embed_content(...)
        await dil_sdk.data.store_semantic(...)
        
        # Step 4: Use AI Data
        results = await dil_sdk.data.query_semantic(...)
        
        return results
```

**Acceptance Criteria:**
- [ ] Data Mash Journey uses DIL SDK throughout
- [ ] All 4 steps implemented
- [ ] Registered with Curator

#### 11.2: Refactor MVP Journey to Use Data Mash

**File:** `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

**Changes:**
- Compose Data Mash Journey instead of direct ContentAnalysisOrchestrator
- Showcase DIL capabilities

**Acceptance Criteria:**
- [ ] MVP Journey uses Data Mash Journey
- [ ] DIL capabilities showcased

---

### Layer 12: Solution Updates

#### 12.1: Create Data Mash Solution

**Location:** `backend/solution/services/data_mash_solution_service/`

**Pattern:** Like `SolutionComposerService`

**Implementation:**
```python
class DataMashSolutionService(RealmServiceBase):
    """Data Mash Solution - Composes Data Mash Journeys."""
    
    async def execute_solution(self, solution_id, user_context):
        """Execute Data Mash Solution using DIL SDK."""
        # Get DIL SDK
        dil_foundation = self.di_container.get_foundation_service("DataIntelligenceFoundationService")
        dil_sdk = dil_foundation.get_sdk()
        
        # Compose Data Mash Journeys
        # Use DIL SDK for orchestration
        # ...
```

**Acceptance Criteria:**
- [ ] Data Mash Solution created
- [ ] Composes Data Mash Journeys
- [ ] Uses DIL SDK for orchestration

---

### Layer 13: Frontend Updates

#### 13.1: Update Content Pillar

**Location:** `symphainy-frontend/` (separate repo)

**Changes:**
1. Show semantic contracts (not just content metadata)
2. Show embedded data graphs
3. Use DIL SDK semantic queries

**API Changes:**
- Use DIL SDK semantic queries
- Display semantic contracts
- Show data classification

**Acceptance Criteria:**
- [ ] Content pillar shows semantic contracts
- [ ] Embedded data graphs displayed
- [ ] Semantic queries working

#### 13.2: Update Insights Pillar

**Location:** `symphainy-frontend/` (separate repo)

**Changes:**
1. Query semantic data layer (not client data files)
2. Use semantic contracts for insights
3. Show cross-file semantic relationships

**Acceptance Criteria:**
- [ ] Insights uses semantic data layer
- [ ] Semantic contracts used for insights
- [ ] Cross-file relationships shown

---

## Implementation Phases

### Phase 0.1: Foundation Setup (Week 1-2)
- Layer 1: Infrastructure (no changes)
- Layer 2: DI Container (add DIL Foundation)
- Layer 3: Utilities (no changes)
- Layer 4: Public Works (enhance abstractions, ArangoDB init)
- Layer 5: DIL Foundation (create structure + SDK + ALL capability domains)
- Layer 6: Curator (register DIL Foundation)

### Phase 0.2: Foundation Integration (Week 2-3)
- Layer 7: Agentic (integrate DIL SDK)
- Layer 8: Experience (no changes)

### Phase 0.3: Smart City Consolidation (Week 3)
- Layer 9: Smart City (consolidate Data/Content Steward, use DIL SDK)

### Phase 0.4: Business Enablement (Week 3-4)
- Layer 10: Business Enablement (update ContentAnalysisOrchestrator to use DIL SDK)

### Phase 0.5: Journey & Solution (Week 4-5)
- Layer 11: Journey (create Data Mash Journey, refactor MVP Journey)
- Layer 12: Solution (create Data Mash Solution)

### Phase 0.6: Frontend Integration (Week 5-6)
- Layer 13: Frontend (update Content/Insights pillars)

---

## Success Criteria

### Phase 0 Complete When:
1. ✅ DIL Foundation operational with ALL 6 capability domains
2. ✅ DIL SDK working (all API methods implemented)
3. ✅ WAL/Saga patterns working for realms
4. ✅ Semantic contracts working (semantic schemas exposed as contracts)
5. ✅ Agent execution tracking working (agents feed DIL)
6. ✅ Platform data observability working
7. ✅ Data Steward consolidated (uses DIL SDK)
8. ✅ ContentAnalysisOrchestrator uses DIL SDK for all data operations
9. ✅ Data Mash Journey operational (uses DIL SDK throughout)
10. ✅ MVP Journey showcases Data Mash and DIL capabilities
11. ✅ Frontend shows semantic contracts and embedded data graphs
12. ✅ Insights uses semantic data layer
13. ✅ Realms can orchestrate freely via DIL SDK
14. ✅ Agents are first-class citizens (Agentic SDK + DIL SDK)
15. ✅ All tests passing

---

## Breaking Changes Strategy

**Mindset:** Break and fix - implement the vision correctly, fix what breaks.

**Approach:**
1. Implement DIL Foundation correctly
2. Update all services to use DIL SDK
3. Remove deprecated services (Content Steward)
4. Fix what breaks during implementation
5. Test thoroughly after each layer

**No Backward Compatibility:**
- Content Steward removed (not deprecated)
- Direct infrastructure calls replaced with DIL SDK
- Old patterns replaced with new patterns

---

## Next Steps

1. **Review and approve this plan**
2. **Start Phase 0.1: Foundation Setup**
3. **Execute layer by layer**
4. **Test after each layer**
5. **Fix what breaks**
6. **Document as you go**

---

## Conclusion

This plan brings the DIL Foundation vision to life:
- Cross-cutting data governance
- Semantic-first data integration
- Realm freedom via DIL SDK
- Agents as first-class citizens
- Platform-wide correlation
- Break and fix mindset

**Everything data-related goes through DIL SDK**, enabling the platform vision.

