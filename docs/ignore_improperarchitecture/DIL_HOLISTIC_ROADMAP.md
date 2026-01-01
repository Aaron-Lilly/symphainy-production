# Data Intelligence Layer (DIL): Holistic Phased Roadmap

**Date:** January 2025  
**Status:** 🎯 **STRATEGIC ROADMAP**  
**Vision:** Establish DIL as the unified foundation for data intelligence, orchestration, and semantic capabilities

---

## Executive Summary

This roadmap brings the Data Intelligence Layer (DIL) vision to life through incremental, value-driven phases. DIL consolidates orchestration, data runtime, semantic layer, agent fabric, PII patterns, and observability into a single, cohesive foundation that sits between Smart City Foundation and Realm Services.

**Key Principle:** Phase in new capabilities (billing, prompting, PII enforcement, etc.) incrementally while establishing the foundation structure early.

---

## Architectural Vision

```
┌─────────────────────────────────────────────────────────────┐
│ Smart City Foundation (Security & Governance)               │
│ - Security Guard, City Manager, Data Steward (governance)   │
└─────────────────────────────────────────────────────────────┘
                          ↓ (governs)
┌─────────────────────────────────────────────────────────────┐
│ Data Intelligence Layer (DIL) Foundation                    │
│ - Orchestration (WAL/Saga)                                  │
│ - Data Runtime & Transport (Data Mash)                      │
│ - Semantic Layer (Librarian integration)                   │
│ - Agent Fabric (Agentic Foundation integration)            │
│ - PII & De-identification (lightweight patterns)           │
│ - Observability & Telemetry (unified platform data)         │
└─────────────────────────────────────────────────────────────┘
                          ↓ (enables)
┌─────────────────────────────────────────────────────────────┐
│ Public Works Foundation (Infrastructure)                    │
│ - File Management, Content Metadata, Knowledge Discovery    │
└─────────────────────────────────────────────────────────────┘
                          ↓ (used by)
┌─────────────────────────────────────────────────────────────┐
│ Realm Services (Client + Platform interactions)            │
│ - Business Enablement, Solution, Journey, Experience        │
└─────────────────────────────────────────────────────────────┘
```

---

## Phased Implementation Roadmap

### Phase 0: DIL Foundation Setup (2-3 weeks) ⭐ **START HERE**

**Goal:** Establish DIL foundation structure and integrate with existing architecture.

**Deliverables:**
- DIL foundation service structure
- DIL capability domains (6 domains, initially lightweight)
- Integration with existing foundations (Public Works, Curator, Agentic)
- DIL initialization in platform startup sequence
- DIL spec v1 (contracts and interfaces)

**Key Activities:**
1. Create DIL foundation folder structure
2. Define DIL foundation service (extends FoundationServiceBase)
3. Create 6 capability domain modules (initially stubs with contracts)
4. Integrate DIL into platform startup (after Curator, before Agentic)
5. Define DIL contracts and protocols
6. Create DIL capability registry (in Curator)

**Success Criteria:**
- DIL foundation initializes successfully
- DIL appears in foundation registry
- DIL contracts defined and documented
- No breaking changes to existing functionality

**New Capabilities:** None (foundation only)

---

### Phase 1: DIL-Orchestration + WAL/Saga (4-6 weeks)

**Goal:** Implement orchestration capabilities with WAL/Saga patterns for reliability.

**Deliverables:**
- DIL-Orchestration service
- WAL pattern implementation
- Saga pattern implementation
- Migration of ContentAnalysisOrchestrator to DIL-Orchestration
- Execution trace view (basic)

**Key Activities:**
1. Implement WAL write pattern (ArangoDB storage)
2. Implement Saga compensating transactions
3. Create DIL-Orchestration service
4. Migrate ContentAnalysisOrchestrator to use DIL-Orchestration
5. Add WAL recovery mechanism
6. Add Saga coordinator
7. Create execution trace storage (ArangoDB)

**Success Criteria:**
- WAL-enabled data operations (file upload → parse → semantic)
- Saga compensations working for failed operations
- Execution traces viewable
- No data loss on failures

**New Capabilities:**
- WAL pattern for multi-step operations
- Saga pattern for compensating transactions
- Execution trace storage and retrieval

---

### Phase 2: DIL-Data Runtime + Data Mash (6-8 weeks)

**Goal:** Implement Data Mash pipeline with schema inference and semantic normalization.

**Deliverables:**
- Data Mash pipeline (file → parse → semantic)
- Schema detection and inference
- Multi-tenant data isolation
- Metadata lineage tracking
- Semantic extraction support
- Confidence scoring baseline

**Key Activities:**
1. Implement Data Mash pipeline container
2. Add column/row/schema inference (extend FileParserService)
3. Add multi-tenant data isolation (data_classification support)
4. Add metadata lineage tracking (Supabase + ArangoDB)
5. Integrate semantic extraction (Librarian integration)
6. Add confidence scoring for schema inference
7. Create HIL validation UI baseline (future)

**Success Criteria:**
- Data Mash pipeline working end-to-end
- Schema inference for 2+ file types (CSV, PDF)
- Confidence scoring > 0.7 for known schemas
- Metadata lineage tracked across pipeline

**New Capabilities:**
- Schema inference and detection
- Confidence scoring
- Metadata lineage tracking
- Multi-tenant data isolation in Data Mash

---

### Phase 3: DIL-Semantic Layer (8 weeks)

**Goal:** Consolidate semantic capabilities into DIL-Semantic Layer.

**Deliverables:**
- Canonical graph model
- Semantic element ontology
- Semantic mapping engine
- Lock/publish contracts
- Semantic versioning
- HIL validation workflow

**Key Activities:**
1. Build canonical graph model (ArangoDB)
2. Define semantic element ontology (JSON schema)
3. Implement semantic mapping engine (legacy → inferred → canonical)
4. Implement lock/publish contracts (ArangoDB + Supabase)
5. Add semantic versioning (ArangoDB)
6. Integrate HIL validation workflow (UI + API)
7. Enhance Librarian with DIL-Semantic Layer patterns

**Success Criteria:**
- Canonical graph model operational
- Semantic mapping engine working for 2+ client models
- Lock/publish workflow functional
- Semantic versioning tracking changes

**New Capabilities:**
- Canonical graph model
- Semantic mapping engine
- Lock/publish workflow
- Semantic versioning

---

### Phase 4: DIL-Agent Fabric Expansion (4-6 weeks)

**Goal:** Expand agent capabilities with MCP tools, HuggingFace, and persona configs.

**Deliverables:**
- MCP tool registry (in DIL)
- HuggingFace stateless agent runners
- JSON persona config registry
- Agent execution logs and metadata
- Structured prompt versioning
- Multi-agent composition engine

**Key Activities:**
1. Add MCP tool registry to DIL-Agent Fabric
2. Add HuggingFace stateless agent runners (extend Agentic Foundation)
3. Create JSON persona config registry (ArangoDB)
4. Add agent execution logs (ArangoDB + Supabase)
5. Add structured prompt versioning (ArangoDB)
6. Create multi-agent composition engine
7. Integrate with existing Agentic Foundation

**Success Criteria:**
- MCP tools discoverable via DIL
- HuggingFace agents running stateless
- Persona configs versioned and retrievable
- Agent execution traces viewable
- Multi-agent compositions working

**New Capabilities:**
- MCP tool registry
- HuggingFace stateless agents
- Persona config management
- Agent execution tracing
- Multi-agent composition

---

### Phase 5: DIL-PII & De-identification Foundation (Design Only) (1-2 weeks)

**Goal:** Design PII patterns without enforcement (lightweight foundation).

**Deliverables:**
- PII classification taxonomy (JSON schema)
- PII tagging rules (metadata format)
- De-ID transform definitions (placeholders)
- Semantic-aware PII metadata model
- Integration hooks for future enforcement

**Key Activities:**
1. Define PII classification taxonomy (PII, PCI, PHI, etc.)
2. Define PII tagging rules (metadata format)
3. Define de-ID transform placeholders (no implementation)
4. Create semantic-aware PII metadata model
5. Define integration hooks for future enforcement
6. Document "open by policy, secure by design" rules

**Success Criteria:**
- PII taxonomy documented
- PII metadata format defined
- Integration hooks identified
- No enforcement code (design only)

**New Capabilities:**
- PII classification taxonomy
- PII metadata format
- Integration hooks (no enforcement yet)

---

### Phase 6: DIL-Observability Unification (4 weeks)

**Goal:** Unify telemetry, logs, and metrics across all realms.

**Deliverables:**
- Unified telemetry ingestion (OpenTelemetry)
- Realm service log aggregation
- Agent execution log aggregation
- Prompt/response trace storage (PII-aware)
- Semantic pipeline metrics
- DIL internal metrics
- Error taxonomy
- Failure recovery state (WAL/Saga integration)
- Distributed tracing (trace_id propagation)

**Key Activities:**
1. Unify telemetry ingestion (extend existing OpenTelemetry)
2. Add realm service log aggregation (Loki/Tempo)
3. Add agent execution log aggregation (ArangoDB)
4. Add prompt/response trace storage (PII-aware, ArangoDB)
5. Add semantic pipeline metrics (Prometheus)
6. Add DIL internal metrics (Prometheus)
7. Create error taxonomy (JSON schema)
8. Integrate failure recovery state (WAL/Saga)
9. Enhance distributed tracing (trace_id in all stores)

**Success Criteria:**
- All platform data flowing through DIL-Observability
- Unified telemetry dashboard (Grafana)
- Agent execution traces viewable
- Error taxonomy operational
- Failure recovery state visible

**New Capabilities:**
- Unified telemetry ingestion
- Agent execution log aggregation
- Prompt/response trace storage
- Error taxonomy
- Failure recovery state tracking

---

### Phase 7: Platform Data Expansion (Ongoing, Phased)

**Goal:** Phase in new platform data capabilities as needed.

**Deliverables (Phased):**
- **7.1: Prompting & LLM Usage Tracking** (2-3 weeks)
  - Prompt versioning and tracking
  - LLM usage metrics (tokens, costs)
  - Prompt/response quality scoring
  - Integration with DIL-Observability

- **7.2: Billing & Cost Tracking** (3-4 weeks)
  - Resource usage tracking (compute, storage, LLM)
  - Cost attribution (per tenant, per operation)
  - Billing event generation
  - Integration with DIL-Observability

- **7.3: PII Enforcement** (4-6 weeks)
  - PII scanners (implement Phase 5 hooks)
  - Encryption services
  - Tokenization services
  - PII-aware data access controls

- **7.4: Advanced Analytics** (Ongoing)
  - Cross-client intelligence (semantic patterns)
  - Usage analytics
  - Performance optimization insights

**Key Principle:** Each sub-phase adds new capabilities incrementally, building on DIL foundation.

---

## Integration Points

### DIL ↔ Smart City Foundation
- **Data Steward:** Governs all data (platform, client, semantic)
- **Security Guard:** Security policies for DIL operations
- **City Manager:** Platform policies for DIL operations
- **Librarian:** Semantic storage and discovery (integrated with DIL-Semantic Layer)

### DIL ↔ Public Works Foundation
- **File Management:** Data Mash uses for file storage
- **Content Metadata:** DIL-Semantic Layer uses for semantic storage
- **Knowledge Discovery:** DIL-Agent Fabric uses for tool discovery
- **State Management:** DIL-Orchestration uses for WAL/Saga state

### DIL ↔ Agentic Foundation
- **Agent Registry:** DIL-Agent Fabric extends with MCP tools
- **Agent Execution:** DIL-Agent Fabric adds execution tracing
- **Prompt Management:** DIL-Agent Fabric adds versioning

### DIL ↔ Realm Services
- **Business Enablement:** Uses DIL-Orchestration, DIL-Data Runtime
- **Solution Realm:** Uses DIL-Orchestration for solution journeys
- **Journey Realm:** Uses DIL-Orchestration for journey execution
- **Experience Realm:** Uses DIL-Observability for user analytics

---

## Data Classification in DIL

### Platform Data (Generated by Smart City)
- **DIL-Observability:** Telemetry, logs, metrics
- **DIL-Orchestration:** Execution traces, WAL state
- **DIL-Agent Fabric:** Agent execution logs, prompt traces
- **Storage:** Supabase (metadata) + ArangoDB (semantic) + GCS (files)

### Client Data (Generated by Realms)
- **DIL-Data Runtime:** Parsed data, schema inference
- **DIL-Semantic Layer:** Client semantic embeddings, graphs
- **Storage:** Supabase (metadata) + ArangoDB (semantic) + GCS (files)
- **Isolation:** Strict tenant_id requirement

### Semantic Data (Derived from Platform or Client)
- **DIL-Semantic Layer:** Canonical ontologies, mappings
- **Classification:** Inherits from source (platform semantic vs client semantic)
- **Storage:** ArangoDB (primary) + Supabase (metadata links)
- **Access:** Inherits from source classification

---

## Success Metrics

### Phase 0-1 (Foundation + Orchestration)
- ✅ DIL foundation operational
- ✅ WAL/Saga patterns working
- ✅ Zero data loss on failures

### Phase 2 (Data Mash)
- ✅ Data Mash pipeline operational
- ✅ Schema inference > 70% confidence
- ✅ Metadata lineage tracked

### Phase 3 (Semantic Layer)
- ✅ Canonical graph model operational
- ✅ Semantic mapping working for 2+ clients
- ✅ Lock/publish workflow functional

### Phase 4 (Agent Fabric)
- ✅ MCP tools discoverable
- ✅ HuggingFace agents running
- ✅ Multi-agent compositions working

### Phase 5-7 (PII, Observability, Platform Data)
- ✅ PII patterns designed
- ✅ Unified observability dashboard
- ✅ Platform data capabilities phased in

---

## Risk Mitigation

### Technical Risks
- **Risk:** DIL foundation complexity
  - **Mitigation:** Start with lightweight structure, add capabilities incrementally
- **Risk:** Migration of existing orchestrators
  - **Mitigation:** Migrate one orchestrator at a time, validate before next
- **Risk:** Performance impact of WAL/Saga
  - **Mitigation:** Benchmark early, optimize as needed

### Team Risks
- **Risk:** Overwhelming team with new foundation
  - **Mitigation:** Clear value proposition, incremental phases, celebrate wins
- **Risk:** Breaking existing functionality
  - **Mitigation:** Comprehensive testing, gradual migration, rollback plans

---

## Next Steps

1. **Review and approve this roadmap**
2. **Start Phase 0:** DIL Foundation Setup (see PHASE_0_DIL_FOUNDATION.md)
3. **Establish DIL foundation structure**
4. **Integrate with existing architecture**
5. **Begin Phase 1:** DIL-Orchestration + WAL/Saga

---

## Conclusion

This roadmap brings the DIL vision to life through incremental, value-driven phases. Each phase builds on the previous, adding new capabilities while preserving existing functionality. The foundation structure is established early (Phase 0), enabling all subsequent phases to build on a solid base.

**Key Success Factors:**
- Incremental value delivery
- Preserve existing work
- Clear integration points
- Phased new capabilities
- Team alignment and communication


