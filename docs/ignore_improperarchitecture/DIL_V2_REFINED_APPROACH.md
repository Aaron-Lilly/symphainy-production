# DIL v2: Refined Approach
## MVP-Focused, Use-Case-Driven, Pattern-First Implementation

**Date:** January 2025  
**Status:** 🎯 **READY FOR DISCUSSION**  
**Approach:** Secure by design, open by policy - patterns now, enforcement later

---

## Executive Summary

This document refines the DIL v2 approach based on:
1. **Data Steward Pattern:** Hybrid B/C - exposes APIs, manages/curates what realms create (like Security Guard/Nurse)
2. **Semantic Evolution:** Semantic IDs/relationships now, evolvable to contracts without rewrites
3. **MVP Focus:** Content + Insights pillars only, showcase semantic data layer
4. **Agentic Critical:** Demo depends on agentic integration, SDKs need enhancement
5. **Observability Critical:** Platform health depends on observability, streamline existing capabilities
6. **Capability Assessment:** Use this as opportunity to assess what's actually working vs. broken

---

## 1. Data Steward: Hybrid B/C Pattern

### Pattern: Like Security Guard and Nurse

**Security Guard Pattern:**
- Exposes SOA APIs: `authenticate_user`, `authorize_action`, `create_session`
- Realms call APIs directly
- Security Guard manages policies, rules, permissions
- Security Guard curates what realms create (permissions, sessions)

**Nurse Pattern:**
- Exposes SOA APIs: `collect_telemetry`, `get_health_metrics`, `set_alert_threshold`
- Realms call APIs directly
- Nurse manages health policies, alert thresholds, diagnostics
- Nurse curates what realms report (telemetry, health data)

**Data Steward Pattern (Hybrid B/C):**
- Exposes SOA APIs for governance operations
- Realms use DIL SDK directly for data operations
- Data Steward manages/curates semantic definitions, corrections, policies
- Data Steward doesn't create contracts, but manages what realms create

### Data Steward SOA APIs

```python
# Data Steward exposes governance APIs
class DataStewardService:
    # Governance APIs (like Security Guard/Nurse)
    async def curate_semantic_definition(
        self, semantic_id: str, definition: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Review/approve semantic ID that realm created via DIL SDK."""
        # Review semantic ID
        # Approve/reject/modify
        # Store in DIL as canonical definition
        pass
    
    async def manage_semantic_relationships(
        self, source_id: str, target_id: str, relationship: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manage relationships between semantic entities."""
        # Review relationship
        # Approve/reject/modify
        # Store in DIL
        pass
    
    async def configure_data_policies(
        self, policy_type: str, policy_config: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure DIL SDK policies (PII, retention, etc.)."""
        # Configure policies
        # Store in DIL
        # DIL SDK enforces policies
        pass
    
    async def review_corrections(
        self, correction_id: str, action: str, user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Review/approve corrections from realms."""
        # Review correction
        # Approve/reject
        # Update semantic definitions if approved
        pass
    
    async def get_semantic_governance_dashboard(
        self, filters: Dict[str, Any], user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get governance dashboard data."""
        # Return semantic coverage, correctness rates, agent drift, etc.
        pass
```

### Realm Usage Pattern

```python
# Realms use DIL SDK directly for data operations
from dil import data, governance

# Realm creates semantic data via DIL SDK
file_metadata = await dil.data.upload_file(file_data, filename, user_context)
parse_result = await dil.data.parse_file(file_id, parse_options, user_context)
embeddings = await dil.data.embed_content(parsed_data, embedding_type, user_context)
await dil.data.store_semantic(content_id, embeddings, semantic_graph, user_context)

# Realm creates semantic IDs/relationships (not contracts yet)
semantic_id = await dil.governance.create_semantic_id(
    column_name="revenue",
    semantic_meaning="Total revenue for the period",
    user_context=user_context
)

# Data Steward curates what realm created
await data_steward.curate_semantic_definition(
    semantic_id=semantic_id,
    definition={"meaning": "Total revenue for the period", "type": "metric"},
    user_context=user_context
)
```

### Key Insight

**Data Steward doesn't create contracts** - that's a bridge too far. Instead:
- Realms create semantic IDs/relationships via DIL SDK
- Data Steward curates/approves what realms create
- Semantic IDs/relationships are evolvable to contracts later (without rewrites)

---

## 2. Semantic Evolution: IDs/Relationships → Contracts

### Current State: Semantic IDs/Relationships

```python
# Semantic ID structure (evolvable to contract)
semantic_id = {
    "id": "revenue_metric_v1",
    "name": "revenue",
    "meaning": "Total revenue for the period",
    "type": "metric",  # metric, dimension, entity
    "data_type": "numeric",
    "unit": "USD",
    "relationships": [
        {"target_id": "period_dimension_v1", "type": "belongs_to"},
        {"target_id": "account_dimension_v1", "type": "aggregated_by"}
    ],
    "created_by": "realm:insights",
    "curated_by": "data_steward",
    "version": "v1",
    "created_at": "2025-01-15T10:00:00Z"
}
```

### Future State: Semantic Contracts (Evolvable)

```python
# Contract structure (evolves from semantic ID)
semantic_contract = {
    "contract_id": "revenue_metric_v1",
    "semantic_id": "revenue_metric_v1",  # Links to semantic ID
    "schema": {
        "name": "revenue",
        "type": "metric",
        "data_type": "numeric",
        "unit": "USD",
        "constraints": {
            "min": 0,
            "max": None,
            "required": True
        }
    },
    "relationships": [...],  # Same structure
    "retrieval_rules": {
        "reference_first": True,
        "fallback_to_client_data": True
    },
    "version": "v1",
    "created_at": "2025-01-15T10:00:00Z"
}
```

### Evolution Strategy

1. **Phase 0:** Semantic IDs/relationships only
2. **Phase 1:** Add contract metadata to semantic IDs (optional fields)
3. **Phase 2:** Activate contract enforcement when use case demands it
4. **No Rewrites:** Contract structure extends semantic ID structure

---

## 3. MVP Focus: Content + Insights Pillars

### Content Pillar: Showcase Semantic Data Layer

**Current:** Shows parsed files, metadata

**New:** Shows semantic graphs/embeddings
- **Structured:** Column metadata + semantic IDs + relationships
- **Unstructured:** Semantic graph (nodes = entities, edges = relationships)
- **Hybrid:** Both structured and unstructured with correlation map

**Key Question:** Does hybrid parsing store a correlation map?

**Answer Needed:** Check if `_process_hybrid_semantic()` stores correlation map explaining how structured and unstructured parsed files relate.

**If Missing:** Add correlation map to hybrid processing:
```python
correlation_map = {
    "structured_file_id": "file_123",
    "unstructured_file_id": "file_124",
    "relationships": [
        {
            "source": "column:revenue",
            "target": "entity:revenue_discussion",
            "relationship_type": "discussed_in",
            "confidence": 0.85
        }
    ],
    "created_at": "2025-01-15T10:00:00Z"
}
```

### Insights Pillar: Use Semantic Data Layer

**Current:** Uses direct client data files (parquet)

**New:** Uses semantic data (ArangoDB)
- Query semantic embeddings for structured data
- Query semantic graphs for unstructured data
- Use semantic IDs/relationships for cross-file reasoning

**Refactoring:** All Insights enabling services use DIL SDK
- `DataAnalyzerService` → uses `dil.data.query_semantic()`
- `MetricsCalculatorService` → uses semantic IDs for metric definitions
- `VisualizationEngineService` → uses semantic relationships for visualization
- `InsightsGeneratorService` → uses semantic data for insights
- `DataInsightsQueryService` → queries semantic data layer

**Note:** Different team handles enabling service refactoring - provide them with DIL SDK API spec and refactoring requirements.

---

## 4. Agentic Track: Critical for Demo

### Current State Analysis

**Liaison Agents:**
- ❌ No LLM reasoning (keyword matching only)
- ❌ No MCP tool integration
- ❌ No conversational context
- ✅ Provide guidance/routing

**Specialist Agents:**
- ✅ Execute specialized tasks
- ✅ Use LLMs for generation
- ⚠️ Need enhancement for industry best practices

**Industry Best Practices (Missing):**
- Declarative agent configuration (YAML)
- LLM reasoning for intent understanding
- Stateful conversations with context
- MCP tool integration
- Iterative execution for multi-step operations

### Agentic Track Requirements

**1. Declarative Agent Pattern**
- Convert liaison agents to declarative agents
- YAML configuration (role, goal, backstory, tools, LLM config)
- LLM reasoning for intent understanding
- Tool selection via LLM

**2. Agent SDK Enhancement**
- Agent execution tracking (via DIL SDK)
- Agent tool registry (via DIL SDK)
- Agent lifecycle management
- Agent drift monitoring

**3. DIL SDK Integration**
- `dil.agents.track_execution()` - Track agent execution
- `dil.agents.get_execution_log()` - Get execution history
- `dil.agents.query_agent_events()` - Query agent events
- `dil.agents.list_tools()` - List available tools

**4. MCP Tool Integration**
- All agent capabilities exposed as MCP tools
- Tools call DIL SDK for data operations
- Tools call enabling services for business logic

### Agentic Track Scope

**Must Build:**
- Declarative agent base class
- Liaison agent conversion (Content, Insights, Operations, Business Outcomes)
- Agent execution tracking (DIL SDK integration)
- MCP tool integration

**Can Defer:**
- Advanced agent orchestration
- Multi-agent collaboration
- Agent learning/adaptation

---

## 5. Observability Track: Streamline Existing Capabilities

### Current State Assessment Needed

**Questions to Answer:**
1. Does Nurse actually collect all telemetry?
2. Are traces properly correlated across services?
3. Are metrics properly aggregated?
4. Are logs properly structured?
5. Is observability data stored in DIL (platform data)?

### Observability Track Requirements

**1. DIL SDK Observability Module**
- `dil.observability.record_platform_event()` - Record platform events
- `dil.observability.record_agent_log()` - Record agent execution logs
- `dil.observability.record_semantic_metric()` - Record semantic metrics
- `dil.observability.get_trace()` - Get distributed trace
- `dil.observability.get_metrics()` - Get aggregated metrics

**2. Streamline Existing Capabilities**
- Assess what's actually working vs. broken
- Consolidate duplicate observability code
- Unify observability patterns
- Store observability data in DIL (platform data)

**3. Integration Points**
- Nurse uses DIL SDK for observability storage
- All services use DIL SDK for observability
- DIL SDK provides unified observability interface

### Observability Track Scope

**Must Build:**
- DIL SDK observability module
- Platform data storage for observability
- Integration with Nurse
- Trace correlation

**Can Defer:**
- Advanced analytics
- Predictive monitoring
- Automated remediation

---

## 6. Capability Assessment: What's Actually Working?

### Assessment Questions

**1. Hybrid Parsing:**
- ✅ Does it parse both structured and unstructured?
- ❓ Does it store a correlation map?
- ❓ Are relationships between components properly stored?

**2. Semantic Processing:**
- ✅ Does it generate 3 embeddings for structured data?
- ✅ Does it generate semantic graph for unstructured data?
- ❓ Are semantic IDs properly assigned?
- ❓ Are relationships properly stored?

**3. Data Storage:**
- ✅ Are files stored in GCS?
- ✅ Is metadata stored in Supabase?
- ✅ Are embeddings stored in ArangoDB?
- ❓ Is parsed data stored (or just ephemeral)?

**4. Business Logic:**
- ❓ Are there hard-coded cheats in services?
- ❓ Are services following agentic-forward patterns?
- ❓ Are there business/functional logic issues?

**5. Best Practices:**
- ❓ Are we aligned to industry best practices?
- ❓ Are services properly separated (deterministic vs. AI)?
- ❓ Are agents properly using MCP tools?

### Assessment Process

**Step 1: Code Review**
- Review hybrid parsing implementation
- Review semantic processing implementation
- Review data storage implementation
- Review business logic in services

**Step 2: Test Execution**
- Run integration tests
- Check for hard-coded cheats
- Verify data flows
- Verify semantic storage

**Step 3: Documentation**
- Document what's working
- Document what's broken
- Document what needs refactoring
- Document best practice gaps

**Step 4: Remediation Plan**
- Fix broken capabilities
- Refactor services to agentic-forward patterns
- Align to best practices
- Streamline duplicate code

---

## 7. Implementation Phases

### Phase 0: Foundation + Assessment (Week 1-2)

**Goal:** Establish DIL Foundation, assess current capabilities

**Deliverables:**
1. DIL Foundation structure (lightweight)
   - DIL SDK with data operations (upload, parse, embed, store, query)
   - Semantic layer capability domain (semantic IDs/relationships, not contracts)
   - Agentic capability domain (execution tracking)
   - Observability capability domain (platform data storage)
   - Other capability domains (interfaces only)

2. Capability Assessment
   - Review hybrid parsing (correlation map?)
   - Review semantic processing
   - Review data storage
   - Review business logic
   - Document findings

3. Data Steward Consolidation
   - Merge Content Steward into Data Steward
   - Implement SOA APIs (curate, manage, configure, review)
   - Data Steward uses DIL SDK internally

**Acceptance Criteria:**
- [ ] DIL Foundation operational
- [ ] DIL SDK data operations working
- [ ] Capability assessment complete
- [ ] Data Steward consolidated

### Phase 1: Content + Insights Integration (Week 3-4)

**Goal:** Content and Insights pillars use semantic data layer

**Deliverables:**
1. Content Pillar Updates
   - Parse → Embed → Store semantic data
   - Display semantic graphs (unstructured)
   - Display column metadata + semantic IDs (structured)
   - Fix hybrid parsing correlation map (if missing)

2. Insights Pillar Updates
   - Refactor Insights enabling services to use DIL SDK
   - Query semantic data instead of direct client files
   - Use semantic data for analysis/visualization
   - Provide refactoring requirements to enabling services team

3. Semantic Data Queries
   - Query by file_id
   - Query by semantic_id
   - Vector search
   - Semantic graph queries

**Acceptance Criteria:**
- [ ] Content Pillar shows semantic data
- [ ] Insights Pillar uses semantic data
- [ ] All Insights services use DIL SDK
- [ ] Semantic queries working

### Phase 2: Agentic Enhancement (Week 5-6)

**Goal:** Enhance agentic capabilities for demo

**Deliverables:**
1. Declarative Agent Pattern
   - Base class for declarative agents
   - YAML configuration support
   - LLM reasoning for intent understanding
   - Tool selection via LLM

2. Liaison Agent Conversion
   - Convert Content Liaison to declarative
   - Convert Insights Liaison to declarative
   - Convert Operations Liaison to declarative
   - Convert Business Outcomes Liaison to declarative

3. Agent Execution Tracking
   - DIL SDK agent tracking
   - Agent execution logs
   - Agent tool registry
   - MCP tool integration

**Acceptance Criteria:**
- [ ] Declarative agents working
- [ ] All liaison agents converted
- [ ] Agent execution tracking working
- [ ] MCP tools integrated

### Phase 3: Observability Streamlining (Week 7-8)

**Goal:** Streamline observability capabilities

**Deliverables:**
1. DIL SDK Observability Module
   - Platform event recording
   - Agent log recording
   - Semantic metric recording
   - Trace correlation

2. Observability Integration
   - Nurse uses DIL SDK for observability
   - All services use DIL SDK for observability
   - Unified observability interface

3. Observability Assessment
   - Review existing observability code
   - Consolidate duplicate code
   - Fix broken capabilities
   - Align to best practices

**Acceptance Criteria:**
- [ ] DIL SDK observability module working
- [ ] Observability integrated with Nurse
- [ ] Observability streamlined
- [ ] Platform data stored in DIL

---

## 8. Success Criteria

### Phase 0 Complete When:
1. ✅ DIL Foundation operational
2. ✅ DIL SDK data operations working
3. ✅ Capability assessment complete
4. ✅ Data Steward consolidated with SOA APIs

### Phase 1 Complete When:
1. ✅ Content Pillar shows semantic data
2. ✅ Insights Pillar uses semantic data
3. ✅ All Insights services use DIL SDK
4. ✅ Semantic queries working
5. ✅ Hybrid parsing correlation map working (if needed)

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

---

## 9. Open Questions

1. **Hybrid Parsing Correlation Map:** Does it exist? If not, should we add it?
2. **Parsed Data Storage:** Should parsed data be stored, or is ephemeral OK?
3. **Semantic Contract Evolution:** Is the evolution path clear enough?
4. **Enabling Services Refactoring:** What exactly should we tell the enabling services team?
5. **Observability Assessment:** What's the process for assessing existing capabilities?
6. **Agentic SDK Enhancement:** What specific enhancements are needed beyond declarative pattern?

---

## 10. Next Steps

1. **Review and approve this refined approach**
2. **Answer open questions**
3. **Start Phase 0: Foundation + Assessment**
4. **Execute capability assessment**
5. **Begin implementation**

---

## Conclusion

This refined approach:
- **Data Steward:** Hybrid B/C pattern (like Security Guard/Nurse)
- **Semantic Evolution:** IDs/relationships now, contracts later (evolvable)
- **MVP Focus:** Content + Insights pillars only
- **Agentic Critical:** Enhance for demo
- **Observability Critical:** Streamline existing capabilities
- **Capability Assessment:** Use this as opportunity to assess what's working

**Everything data-related goes through DIL SDK**, enabling the platform vision while staying focused on MVP use cases.


