# DIL Foundation v3: Complete Execution Plan
## MVP-Focused, Use-Case-Driven, Pattern-First Implementation

**Date:** January 2025  
**Status:** 🎯 **READY FOR IMPLEMENTATION**  
**Approach:** Secure by design, open by policy - patterns now, enforcement later

---

## Executive Summary

This v3 plan consolidates all refinements, enabling services guidance, and observability updates into a single, cohesive implementation plan. It brings the DIL Foundation vision to life with a focus on MVP use cases (Content + Insights pillars), following "secure by design, open by policy" principles.

**Strategic Principle:** "If everything is data and everything needs to be correlated, then Data Governance is foundational."

**Mindset:** Break and fix - implement the vision correctly, fix what breaks.

---

## Vision: What DIL Foundation Enables

### 1. Semantic-First Data Integration
- Embeddings set semantic model/schema for each data source
- Semantic IDs/relationships exposed (evolvable to contracts)
- Platform operates via semantic data (not raw data)
- Client updates data source → update semantic → everything keeps working

### 2. Cross-Cutting Data Governance
- **Lineage:** Track data flow across all realms
- **Classification:** Platform vs client data distinction
- **Semantic IDs/Relationships:** Evolvable to contracts without rewrites
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
- Observability data stored in DIL (platform data)
- Trace correlation across logs, traces, metrics
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
│   ├── data_operations.py  # Upload, parse, embed, query, correlation map
│   ├── governance.py  # Lineage, classification, semantic IDs/relationships
│   ├── orchestration.py  # WAL, Saga (interfaces only for MVP)
│   ├── agents.py  # Agent execution tracking
│   └── observability.py  # Platform data, telemetry, tracing
└── capability_domains/
    ├── orchestration/  # WAL/Saga interfaces (no enforcement)
    ├── data_runtime/  # Data Mash, semantic-first integration
    ├── semantic_layer/  # Semantic IDs/relationships (evolvable to contracts)
    ├── agent_fabric/  # Agent execution tracking, tool registry
    ├── pii_governance/  # PII detection (flagging only, no masking)
    └── observability/  # Platform data, telemetry, correlation
```

### DIL SDK API (Complete for MVP)

```python
from dil import data, governance, agents, observability

# ============================================================================
# DATA OPERATIONS (Upload, Parse, Embed, Query, Correlation Map)
# ============================================================================

# Upload
file_metadata = await dil.data.upload_file(file_data, filename, metadata, user_context)

# Parse
parse_result = await dil.data.parse_file(file_id, parse_options, user_context)

# Embed
embeddings = await dil.data.embed_content(content, embedding_type, user_context)

# Store semantic
await dil.data.store_semantic(content_id, embeddings, semantic_graph, correlation_map, user_context)

# Query semantic
results = await dil.data.query_semantic(query, filters, user_context)
results = await dil.data.query_by_semantic_id(semantic_id, user_context)
results = await dil.data.vector_search(query_vector, top_k, filters, user_context)
graph = await dil.data.get_semantic_graph(content_id, user_context)

# Query correlation map (NEW - for hybrid)
correlation_map = await dil.data.query_correlation_map(file_id, filters, user_context)

# ============================================================================
# GOVERNANCE (Lineage, Classification, Semantic IDs/Relationships)
# ============================================================================

# Lineage
lineage = await dil.governance.get_lineage(data_source_id, user_context)
await dil.governance.record_lineage(source_id, target_id, transformation, user_context)

# Classification
await dil.governance.classify_data(data_id, classification, tenant_id, user_context)
platform_data = await dil.governance.query_platform_data(filters, user_context)
client_data = await dil.governance.query_client_data(tenant_id, filters, user_context)

# Semantic IDs/Relationships (evolvable to contracts)
semantic_id = await dil.governance.create_semantic_id(name, meaning, semantic_type, data_type, user_context)
relationships = await dil.governance.create_semantic_relationship(source_id, target_id, relationship_type, user_context)

# ============================================================================
# AGENTS (Execution Tracking, Tool Registry)
# ============================================================================

# Execution Tracking
await dil.agents.track_execution(agent_id, prompt_hash, response, trace_id, execution_metadata, user_context)
execution_log = await dil.agents.get_execution_log(agent_id, trace_id, user_context)
agent_events = await dil.agents.query_agent_events(filters, user_context)

# Tool Registry
tools = await dil.agents.list_tools(capability, user_context)
tool_metadata = await dil.agents.get_tool_metadata(tool_id, user_context)

# ============================================================================
# OBSERVABILITY (Platform Data, Telemetry, Tracing)
# ============================================================================

# Platform Event Recording
await dil.observability.record_platform_event(event_type, event_data, trace_id, user_context)
await dil.observability.record_agent_execution(agent_id, prompt_hash, response, trace_id, execution_metadata, user_context)
await dil.observability.record_semantic_metric(metric_name, value, tags, trace_id, user_context)

# Platform Data Queries
platform_data = await dil.observability.query_platform_data(filters, time_range, user_context)
trace_data = await dil.observability.get_trace(trace_id, include_logs, include_metrics, user_context)
metrics = await dil.observability.get_metrics(metric_names, time_range, filters, user_context)
```

---

## Data Steward: Hybrid B/C Pattern

### Pattern: Like Security Guard and Nurse

**Data Steward SOA APIs:**
```python
class DataStewardService:
    # Governance APIs (like Security Guard/Nurse)
    async def curate_semantic_definition(
        self, semantic_id: str, definition: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Review/approve semantic ID that realm created via DIL SDK."""
        pass
    
    async def manage_semantic_relationships(
        self, source_id: str, target_id: str, relationship: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage relationships between semantic entities."""
        pass
    
    async def configure_data_policies(
        self, policy_type: str, policy_config: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure DIL SDK policies (PII, retention, etc.)."""
        pass
    
    async def review_corrections(
        self, correction_id: str, action: str, user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Review/approve corrections from realms."""
        pass
    
    async def get_semantic_governance_dashboard(
        self, filters: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get governance dashboard data."""
        pass
```

**Realm Usage Pattern:**
- Realms use DIL SDK directly for data operations
- Data Steward curates/manages what realms create
- Data Steward doesn't create contracts (bridge too far)
- Semantic IDs/relationships evolvable to contracts later

---

## Semantic Evolution: IDs/Relationships → Contracts

### Current State: Semantic IDs/Relationships

```python
semantic_id = {
    "id": "revenue_metric_v1",
    "name": "revenue",
    "meaning": "Total revenue for the period",
    "type": "metric",  # metric, dimension, entity
    "data_type": "numeric",
    "unit": "USD",
    "relationships": [...],
    "created_by": "realm:insights",
    "curated_by": "data_steward",
    "version": "v1"
}
```

### Future State: Semantic Contracts (Evolvable)

```python
semantic_contract = {
    "contract_id": "revenue_metric_v1",
    "semantic_id": "revenue_metric_v1",  # Links to semantic ID
    "schema": {...},
    "relationships": [...],  # Same structure
    "retrieval_rules": {...},
    "version": "v1"
}
```

**Evolution Strategy:**
1. Phase 0: Semantic IDs/relationships only
2. Phase 1: Add contract metadata to semantic IDs (optional fields)
3. Phase 2: Activate contract enforcement when use case demands it
4. No Rewrites: Contract structure extends semantic ID structure

---

## Layer-by-Layer Implementation

### Layer 1: Infrastructure Dependencies

**Status:** ✅ **NO CHANGES NEEDED**

All required dependencies exist in `pyproject.toml`.

**Action:** None required

---

### Layer 2: DI Container Updates

**File:** `foundations/di_container/di_container_service.py`

**Changes:**
1. Add `data_intelligence_foundation` property
2. Add `get_data_intelligence_foundation()` method

**Acceptance Criteria:**
- [ ] DIL Foundation accessible via DI Container
- [ ] No breaking changes to existing code

---

### Layer 3: Utilities Updates

**Status:** ✅ **NO CHANGES NEEDED**

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
5. Add correlation map storage methods

**Key Updates:**
```python
async def store_correlation_map(
    self,
    file_id: str,
    correlation_map: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Store correlation map for hybrid parsing."""
    # Store in correlation_maps collection
    pass

async def query_correlation_map(
    self,
    file_id: str,
    filters: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Query correlation map for hybrid parsing."""
    # Query correlation_maps collection
    pass
```

**Acceptance Criteria:**
- [ ] All semantic queries filter by tenant_id and data_classification
- [ ] Vector search working
- [ ] Semantic contract queries working
- [ ] Correlation map storage working

#### 4.2: Enhance File Management Abstraction

**File:** `foundations/public_works_foundation/infrastructure_abstractions/file_management_abstraction.py`

**Changes:**
1. Add `data_classification` validation in `create_file()`
2. Add `list_platform_files()` method
3. Add `list_client_files()` method
4. Add lineage tracking methods

**Acceptance Criteria:**
- [ ] data_classification validation working
- [ ] Platform/client file listing working
- [ ] Lineage tracking working

#### 4.3: Create ArangoDB Initialization Script

**File:** `scripts/initialize_arangodb_collections.py`

**Collections to Create:**
- `structured_embeddings` (document)
- `semantic_graph_nodes` (document)
- `semantic_graph_edges` (edge)
- `content_metadata` (document)
- `semantic_ids` (document) - NEW
- `semantic_relationships` (edge) - NEW
- `correlation_maps` (document) - NEW
- `platform_events` (document) - NEW
- `agent_execution_logs` (document) - NEW
- `semantic_metrics` (document) - NEW
- `observability_traces` (document) - NEW
- `data_lineage` (edge)

**Acceptance Criteria:**
- [ ] All collections created
- [ ] All indexes created
- [ ] Script runs as part of deployment

---

### Layer 5: DIL Foundation (NEW)

#### 5.1: Create DIL Foundation Service

**File:** `foundations/data_intelligence_foundation/data_intelligence_foundation_service.py`

**Pattern:** Like `AgenticFoundationService` and `ExperienceFoundationService`

**Initialization Order:** After Curator, before Agentic (or after Agentic if it needs Agentic)

**Acceptance Criteria:**
- [ ] DIL Foundation initializes successfully
- [ ] All 6 capability domains initialized
- [ ] DIL SDK accessible via `get_sdk()`
- [ ] Registered with Curator

#### 5.2: Create DIL SDK

**File:** `foundations/data_intelligence_foundation/sdk/dil_sdk.py`

**SDK Modules:**
- `data_operations.py` - Upload, parse, embed, query, correlation map
- `governance.py` - Lineage, classification, semantic IDs/relationships
- `orchestration.py` - WAL, Saga (interfaces only)
- `agents.py` - Agent execution tracking
- `observability.py` - Platform data, telemetry, tracing

**Acceptance Criteria:**
- [ ] DIL SDK initializes successfully
- [ ] All SDK modules accessible
- [ ] All API methods implemented

#### 5.3: Implement Capability Domains

**All 6 domains must be fully implemented (not just structure):**

1. **DIL-Orchestration** - WAL/Saga interfaces (no enforcement for MVP)
2. **DIL-Data Runtime** - Data Mash, semantic-first integration
3. **DIL-Semantic Layer** - Semantic IDs/relationships (evolvable to contracts)
4. **DIL-Agent Fabric** - Agent execution tracking, tool registry
5. **DIL-PII Governance** - PII detection (flagging only, no masking)
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
            response=None,
            trace_id=trace_id,
            execution_metadata={"tools": [tool.name for tool in tools]},
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
            execution_metadata={"tools": [tool.name for tool in tools], "success": True},
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

**Action:** None required

---

### Layer 9: Smart City Updates

#### 9.1: Consolidate Data Steward and Content Steward

**File:** `backend/smart_city/services/data_steward/data_steward_service.py`

**Changes:**
1. Move Content Steward file lifecycle into Data Steward
2. Update Data Steward to use DIL SDK for all data operations
3. Implement SOA APIs (curate, manage, configure, review)
4. Deprecate Content Steward (remove, not keep for backward compatibility)

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
    
    # SOA APIs for governance
    async def curate_semantic_definition(self, semantic_id, definition, user_context):
        """Review/approve semantic ID that realm created via DIL SDK."""
        # Review semantic ID
        # Approve/reject/modify
        # Store in DIL as canonical definition
        pass
    
    async def manage_semantic_relationships(self, source_id, target_id, relationship, user_context):
        """Manage relationships between semantic entities."""
        pass
    
    async def configure_data_policies(self, policy_type, policy_config, user_context):
        """Configure DIL SDK policies."""
        pass
    
    async def review_corrections(self, correction_id, action, user_context):
        """Review/approve corrections from realms."""
        pass
```

**Acceptance Criteria:**
- [ ] Data Steward uses DIL SDK for all data operations
- [ ] Content Steward removed (not deprecated)
- [ ] All references updated
- [ ] SOA APIs implemented

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
3. Generate correlation map for hybrid parsing (NEW)
4. Generate 3rd embedding (samples_embedding)
5. Use DIL SDK for semantic storage

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
        parse_result = await self.dil_sdk.data.parse_file(
            file_id, parse_options, user_context
        )
        return parse_result
    
    async def _process_hybrid_semantic(self, parse_result, user_context):
        """Process hybrid data semantically using DIL SDK."""
        # Process structured via DIL SDK
        structured_embeddings = []
        for column in columns:
            metadata_emb = await self.dil_sdk.data.embed_content(
                column, "metadata", user_context
            )
            meaning_emb = await self.dil_sdk.data.embed_content(
                column, "meaning", user_context
            )
            samples_emb = await self.dil_sdk.data.embed_content(
                samples_text, "samples", user_context
            )
            structured_embeddings.append({
                "column_name": column,
                "metadata_embedding": metadata_emb,
                "meaning_embedding": meaning_emb,
                "samples_embedding": samples_emb  # 3rd embedding
            })
        
        # Process unstructured via DIL SDK
        unstructured_graph = await self.dil_sdk.data.embed_content(
            parse_result["text_content"], "entity", user_context
        )
        
        # ✅ NEW: Generate correlation map
        correlation_map = await self._generate_correlation_map(
            structured_embeddings=structured_embeddings,
            unstructured_graph=unstructured_graph,
            parse_result=parse_result,
            user_context=user_context
        )
        
        # Store via DIL SDK
        await self.dil_sdk.data.store_semantic(
            content_id=content_id,
            embeddings=structured_embeddings,
            semantic_graph=unstructured_graph,
            correlation_map=correlation_map,  # ✅ NEW
            user_context=user_context
        )
        
        return {
            "structured_result": structured_embeddings,
            "unstructured_result": unstructured_graph,
            "correlation_map": correlation_map  # ✅ NEW
        }
```

**Acceptance Criteria:**
- [ ] ContentAnalysisOrchestrator uses DIL SDK for all data operations
- [ ] 3rd embedding (samples_embedding) generated
- [ ] Correlation map generated for hybrid parsing
- [ ] Correlation map stored via DIL SDK

#### 10.2: Refactor Insights Enabling Services (Enabling Services Team)

**Services to Refactor:**
- `DataAnalyzerService` - Use `dil.data.query_semantic()` instead of direct file access
- `MetricsCalculatorService` - Use `dil.data.query_by_semantic_id()` for metrics
- `VisualizationEngineService` - Use semantic data, semantic graph, correlation map
- `InsightsGeneratorService` - Use semantic data and vector search
- `DataInsightsQueryService` - Query semantic data layer

**Guidance:** See `DIL_ENABLING_SERVICES_INTEGRATION_GUIDE.md`

**Acceptance Criteria:**
- [ ] All Insights services use DIL SDK
- [ ] Services query semantic data, not raw files
- [ ] Services use semantic IDs, relationships, correlation maps

---

### Layer 11: Journey Updates

#### 11.1: Create Data Mash Journey Orchestrator

**Location:** `backend/journey/services/data_mash_journey_orchestrator_service/`

**Journey Steps:**
1. **Ingest Data** → DIL SDK.data.upload_file()
2. **Parse Data** → DIL SDK.data.parse_file()
3. **Embed/AI Enable** → DIL SDK.data.embed_content()
4. **Use AI Data** → DIL SDK.data.query_semantic() → Insights, integration, POC

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

**Acceptance Criteria:**
- [ ] Data Mash Solution created
- [ ] Composes Data Mash Journeys
- [ ] Uses DIL SDK for orchestration

---

### Layer 13: Frontend Updates

#### 13.1: Update Content Pillar

**Location:** `symphainy-frontend/` (separate repo)

**Changes:**
1. Show semantic graphs (unstructured)
2. Show column metadata + semantic IDs (structured)
3. Show correlation map (hybrid) - NEW
4. Use DIL SDK semantic queries

**Acceptance Criteria:**
- [ ] Content pillar shows semantic graphs
- [ ] Column metadata + semantic IDs displayed
- [ ] Correlation map displayed (hybrid)

#### 13.2: Update Insights Pillar

**Location:** `symphainy-frontend/` (separate repo)

**Changes:**
1. Query semantic data layer (not client data files)
2. Use semantic IDs/relationships for insights
3. Show cross-file semantic relationships

**Acceptance Criteria:**
- [ ] Insights uses semantic data layer
- [ ] Semantic IDs/relationships used for insights
- [ ] Cross-file relationships shown

---

## Implementation Phases

### Phase 0: Foundation + Assessment (Week 1-2)

**Goal:** Establish DIL Foundation, assess current capabilities

**Deliverables:**
1. **DIL Foundation Structure**
   - DIL SDK with data operations, governance, agents, observability
   - All 6 capability domains (fully implemented)
   - ArangoDB initialization script

2. **Capability Assessment**
   - Review hybrid parsing (correlation map added)
   - Review semantic processing
   - Review data storage
   - Review business logic
   - Document findings

3. **Data Steward Consolidation**
   - Merge Content Steward into Data Steward
   - Implement SOA APIs (curate, manage, configure, review)
   - Data Steward uses DIL SDK internally

4. **Observability Foundation**
   - DIL SDK observability module
   - Platform data storage (ArangoDB)
   - Correlation framework (trace ID, request ID)

**Acceptance Criteria:**
- [ ] DIL Foundation operational
- [ ] DIL SDK data operations working
- [ ] Capability assessment complete
- [ ] Data Steward consolidated
- [ ] Observability foundation working

### Phase 1: Content + Insights Integration (Week 3-4)

**Goal:** Content and Insights pillars use semantic data layer

**Deliverables:**
1. **Content Pillar Updates**
   - Parse → Embed → Store semantic data
   - Display semantic graphs (unstructured)
   - Display column metadata + semantic IDs (structured)
   - Display correlation map (hybrid) - NEW
   - Use DIL SDK for all data operations

2. **Insights Pillar Updates**
   - Refactor Insights enabling services to use DIL SDK
   - Query semantic data instead of direct client files
   - Use semantic data for analysis/visualization
   - Provide refactoring requirements to enabling services team

3. **Hybrid Parsing Correlation Map**
   - Generate correlation map in ContentAnalysisOrchestrator
   - Store correlation map via DIL SDK
   - Display correlation map in Content Pillar

4. **Semantic Data Queries**
   - Query by file_id
   - Query by semantic_id
   - Vector search
   - Semantic graph queries
   - Correlation map queries

**Acceptance Criteria:**
- [ ] Content Pillar shows semantic data
- [ ] Insights Pillar uses semantic data
- [ ] All Insights services use DIL SDK
- [ ] Semantic queries working
- [ ] Hybrid parsing correlation map working

### Phase 2: Agentic Enhancement (Week 5-6)

**Goal:** Enhance agentic capabilities for demo

**Deliverables:**
1. **Declarative Agent Pattern**
   - Base class for declarative agents
   - YAML configuration support
   - LLM reasoning for intent understanding
   - Tool selection via LLM

2. **Liaison Agent Conversion**
   - Convert Content Liaison to declarative
   - Convert Insights Liaison to declarative
   - Convert Operations Liaison to declarative
   - Convert Business Outcomes Liaison to declarative

3. **Agent Execution Tracking**
   - DIL SDK agent tracking
   - Agent execution logs
   - Agent tool registry
   - MCP tool integration

**Acceptance Criteria:**
- [ ] Declarative agents working
- [ ] All liaison agents converted
- [ ] Agent execution tracking working
- [ ] MCP tools integrated
- [ ] Demo-ready agentic capabilities

### Phase 3: Observability Streamlining (Week 7-8)

**Goal:** Streamline observability capabilities

**Deliverables:**
1. **DIL SDK Observability Module**
   - Platform event recording
   - Agent log recording
   - Semantic metric recording
   - Trace correlation

2. **Observability Integration**
   - Nurse uses DIL SDK for observability
   - All services use DIL SDK for observability
   - Unified observability interface

3. **Observability Assessment**
   - Review existing observability code
   - Consolidate duplicate code
   - Fix broken capabilities
   - Align to best practices

**Acceptance Criteria:**
- [ ] DIL SDK observability module working
- [ ] Observability integrated with Nurse
- [ ] Observability streamlined
- [ ] Platform data stored in DIL
- [ ] All capabilities assessed and working

---

## Success Criteria

### Phase 0 Complete When:
1. ✅ DIL Foundation operational with ALL 6 capability domains
2. ✅ DIL SDK working (all API methods implemented)
3. ✅ Semantic IDs/relationships working (evolvable to contracts)
4. ✅ Agent execution tracking working (agents feed DIL)
5. ✅ Platform data observability working
6. ✅ Data Steward consolidated (uses DIL SDK, SOA APIs implemented)
7. ✅ Capability assessment complete

### Phase 1 Complete When:
1. ✅ Content Pillar shows semantic data
2. ✅ Insights Pillar uses semantic data
3. ✅ All Insights services use DIL SDK
4. ✅ Semantic queries working
5. ✅ Hybrid parsing correlation map working
6. ✅ Realms can orchestrate freely via DIL SDK

### Phase 2 Complete When:
1. ✅ Declarative agents working
2. ✅ All liaison agents converted
3. ✅ Agent execution tracking working
4. ✅ MCP tools integrated
5. ✅ Demo-ready agentic capabilities

### Phase 3 Complete When:
1. ✅ DIL SDK observability module working
2. ✅ Observability integrated with Nurse
3. ✅ Observability streamlined
4. ✅ Platform data stored in DIL
5. ✅ All capabilities assessed and working
6. ✅ Can observe platform health
7. ✅ Can correlate logs, traces, metrics
8. ✅ Can track agent execution

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

## Deferred Capabilities (Open by Policy)

**These are built but not enforced until use case demands:**

1. **Semantic Contracts**
   - Contract registry structure exists
   - Contract enforcement deferred
   - Semantic IDs/relationships evolvable to contracts

2. **WAL/Saga Enforcement**
   - WAL/Saga interfaces exist
   - Enforcement deferred
   - Available when use case demands

3. **PII Masking**
   - PII detection (flagging) exists
   - Masking enforcement deferred
   - Available when client requires it

4. **Multi-Tenant Strict Isolation**
   - Tenant scoping exists
   - Strict enforcement deferred
   - Available when client requires it

5. **Advanced Observability**
   - Base capability exists
   - Advanced analytics deferred
   - Automated remediation deferred

---

## Next Steps

1. **Review and approve this v3 plan**
2. **Start Phase 0: Foundation + Assessment**
3. **Execute layer by layer**
4. **Test after each layer**
5. **Fix what breaks**
6. **Document as you go**

---

## Conclusion

This v3 plan brings the DIL Foundation vision to life:
- Cross-cutting data governance
- Semantic-first data integration
- Realm freedom via DIL SDK
- Agents as first-class citizens
- Platform-wide correlation
- Secure by design, open by policy
- Break and fix mindset

**Everything data-related goes through DIL SDK**, enabling the platform vision while staying focused on MVP use cases.

