# Insurance Use Case: Phase 2 Implementation Plan

**Date:** December 2024  
**Status:** 📋 **COMPREHENSIVE PLAN CREATED**  
**Target:** Production-Grade Insurance Migration Platform with Full Agent Integration

---

## 🎯 Phase 2 Overview

Phase 2 consolidates:
1. **Remaining work from original Phase 2 plan** (Advanced Routing, Wave Migration, Bi-Directional Flows)
2. **Gap analysis items** (Complete orchestrator implementations)
3. **All agent integrations** (8 agents total, including Saga/WAL Management and Universal Mapper)

### **Phase 2 Goals:**
- ✅ Complete all orchestrator implementations with full service coordination
- ✅ Integrate all specialist agents for AI-powered enhancements
- ✅ Implement wave-based migration orchestration
- ✅ Deploy Saga/WAL management for operational intelligence
- ✅ Build Universal Mapper Agent to validate CDO hypothesis
- ✅ Production-ready testing and validation

### **Timeline:**
- **Duration:** 12-14 weeks (extended to include Advanced Routing & Bi-Directional Flows)
- **Start:** After Phase 1 MVP completion
- **Dependencies:** Phase 1 services (Canonical Model, Routing Engine, WAL)

---

## 📊 Phase 2 Components Summary

### **1. Orchestrator Completion (Gap Analysis)**
- Complete `ingest_legacy_data()` orchestration (7 steps)
- Complete `map_to_canonical()` orchestration (7 steps)
- Complete `route_policies()` orchestration (7 steps)
- Add error handling and compensation
- Add state management and resumption

### **2. Agent Integration (8 Agents)**
- Insurance Liaison Agent (conversational guidance)
- **Universal Mapper Agent** (pattern learning, AI-assisted mapping, validation - covers migration AND coexistence)
- Wave Planning Specialist Agent (wave planning intelligence)
- Routing Decision Specialist Agent (complex routing)
- Change Impact Assessment Specialist Agent (governance)
- Data Quality Remediation Specialist Agent (quality intelligence)
- Coexistence Strategy Specialist Agent (strategic planning)
- **Saga/WAL Management Specialist Agent** (operational intelligence)

### **3. Wave Orchestration (Original Phase 2)**
- Wave Orchestrator service
- Wave definition and management
- Quality gates enforcement
- Wave execution and rollback

### **4. Policy Tracking (Original Phase 2)**
- Policy Tracker Orchestrator service
- Policy location tracking
- Cross-system reconciliation
- Migration status tracking

### **5. Solution & Journey Integration (Original Phase 2)**
- Saga Journey template integration
- Solution Composer template integration
- Multi-phase orchestration
- Compensation handlers

---

## 🏗️ Week-by-Week Implementation Plan

### **Week 1-2: Orchestrator Completion & Schema Mapper Enhancement**

#### **Week 1: Complete Insurance Migration Orchestrator & Enhance Schema Mapper**

**Goal:** Complete full orchestration logic for all three methods

**Tasks:**

1. **Complete `ingest_legacy_data()` Orchestration**
   - [ ] Step 1: Upload/get file via Content Steward
   - [ ] Step 2: Parse file via File Parser Service
   - [ ] Step 3: Profile data via Data Steward
   - [ ] Step 4: Extract schema via Schema Mapper Service
   - [ ] Step 5: Store metadata via Librarian
   - [ ] Step 6: Track lineage via Data Steward
   - [ ] Step 7: WAL logging (already done)
   - [ ] Error handling across all steps
   - [ ] Compensation handlers for rollback

2. **Complete `map_to_canonical()` Orchestration**
   - [ ] Step 1: Get source schema from Librarian
   - [ ] Step 2: Validate source data via Data Steward
   - [ ] Step 3: Map source → canonical via Schema Mapper Service
   - [ ] Step 4: Validate canonical data via Canonical Model Service
   - [ ] Step 5: Store mapping rules via Librarian
   - [ ] Step 6: Track mapping lineage
   - [ ] Step 7: WAL logging (already done)
   - [ ] Error handling across all steps
   - [ ] Compensation handlers for rollback

3. **Complete `route_policies()` Orchestration**
   - [ ] Step 1: Get policy status from Policy Tracker
   - [ ] Step 2: Extract routing key via Routing Engine Service
   - [ ] Step 3: Evaluate routing rules via Routing Engine Service
   - [ ] Step 4: Update Policy Tracker with routing decision
   - [ ] Step 5: Store routing decision in Librarian
   - [ ] Step 6: Track routing lineage
   - [ ] Step 7: WAL logging (already done)
   - [ ] Error handling across all steps
   - [ ] Compensation handlers for rollback

**Deliverables:**
- ✅ Complete orchestration logic for all three methods
- ✅ Error handling and compensation
- ✅ Integration tests for each method
- ✅ Documentation updates

---

#### **Week 1 (Continued): Enhance Schema Mapper Service for Canonical Models**

**Goal:** Enhance Schema Mapper Service to support canonical models (from V2 plan)

**Tasks:**

1. **Schema Mapper Enhancements**
   - [ ] Add canonical model as intermediate mapping target
   - [ ] Support source → canonical → target mapping chains
   - [ ] Add mapping rule versioning
   - [ ] Store mapping rules in governance layer
   - [ ] Integrate with Data Steward WAL for audit trail
   - [ ] Implement `map_to_canonical()` method
   - [ ] Implement `map_from_canonical()` method

**Deliverables:**
- ✅ Schema Mapper Service enhanced for canonical models
- ✅ Mapping chains operational
- ✅ WAL integration complete

---

#### **Week 2: Complete Wave & Policy Tracker Orchestrators**

**Goal:** Complete Wave Orchestrator and Policy Tracker Orchestrator implementations

**Tasks:**

1. **Wave Orchestrator Service**
   - [ ] Create `wave_orchestrator.py` with full implementation
   - [ ] Implement `create_wave()` with quality gate definition
   - [ ] Implement `select_wave_candidates()` with selection criteria
   - [ ] Implement `execute_wave()` with quality gate enforcement
   - [ ] Implement `rollback_wave()` with compensation
   - [ ] Implement `get_wave_status()` for monitoring
   - [ ] Create MCP server for agent access
   - [ ] Integration with Insurance Migration Orchestrator
   - [ ] WAL logging for all operations

2. **Policy Tracker Orchestrator Service**
   - [ ] Create `policy_tracker_orchestrator.py` with full implementation
   - [ ] Implement `register_policy()` for policy registration
   - [ ] Implement `update_migration_status()` for status tracking
   - [ ] Implement `get_policy_location()` for location queries
   - [ ] Implement `validate_migration()` for validation
   - [ ] Implement `reconcile_systems()` for cross-system reconciliation
   - [ ] Implement `get_policies_by_location()` for queries
   - [ ] Create MCP server for agent access
   - [ ] Integration with Routing Engine Service
   - [ ] WAL logging for all operations

**Deliverables:**
- ✅ Wave Orchestrator service complete
- ✅ Policy Tracker Orchestrator service complete
- ✅ MCP servers for both orchestrators
- ✅ Integration tests
- ✅ Documentation updates

---

### **Week 3-4: Core Agent Integration**

#### **Week 3: Insurance Liaison Agent**

**Goal:** Implement liaison agent for user guidance

**Tasks:**

1. **Insurance Liaison Agent**
   - [ ] Create `insurance_liaison_agent.py`
   - [ ] Implement conversational guidance for migration operations
   - [ ] Route to appropriate orchestrators
   - [ ] Answer questions about wave planning and policy tracking
   - [ ] Answer questions about mapping and coexistence
   - [ ] Integrate with Insurance Migration Orchestrator
   - [ ] Register with orchestrator

**Deliverables:**
- ✅ Insurance Liaison Agent complete
- ✅ Integration with orchestrators
- ✅ Agent tests

---

#### **Week 4: Universal Mapper Agent (Phase 1 - Foundation)**

**Goal:** Implement Universal Mapper Agent foundation for pattern learning and AI-assisted mapping

**Tasks:**

1. **Universal Mapper Agent Foundation**
   - [ ] Create `universal_mapper_agent.py`
   - [ ] Create Universal Mapping Knowledge Base structure (Librarian)
   - [ ] Implement `learn_from_mappings()` for pattern learning
   - [ ] Implement `suggest_mappings()` for AI-assisted mapping suggestions
   - [ ] Implement `validate_mappings()` for validation
   - [ ] Implement `learn_from_correction()` with human approval
   - [ ] Implement AI-assisted schema mapping (replaces Insurance Migration Specialist)
   - [ ] Implement mapping rule generation (replaces Insurance Migration Specialist)
   - [ ] Implement data quality interpretation (replaces Insurance Migration Specialist)
   - [ ] Integrate with Schema Mapper Service
   - [ ] Integrate with Canonical Model Service
   - [ ] Create MCP tools for agent capabilities

2. **Knowledge Base Setup**
   - [ ] Design Universal Mapping Knowledge Base schema
   - [ ] Implement storage in Librarian
   - [ ] Implement pattern querying
   - [ ] Implement confidence score calculation
   - [ ] Implement ACORD standard reference integration

**Deliverables:**
- ✅ Universal Mapper Agent foundation complete (covers migration AND coexistence)
- ✅ Universal Mapping Knowledge Base structure
- ✅ Pattern learning and AI-assisted mapping capabilities
- ✅ Integration tests

---

### **Week 5-6: Strategic Agent Integration**

#### **Week 5: Wave Planning & Change Impact Agents**

**Goal:** Implement strategic agents for wave planning and governance

**Tasks:**

1. **Wave Planning Specialist Agent**
   - [ ] Create `wave_planning_specialist_agent.py`
   - [ ] Implement policy cohort analysis
   - [ ] Implement risk assessment
   - [ ] Implement quality gate recommendations
   - [ ] Implement timeline estimation
   - [ ] Implement dependency analysis
   - [ ] Integrate with Wave Orchestrator
   - [ ] Create MCP tools

2. **Change Impact Assessment Specialist Agent**
   - [ ] Create `change_impact_assessment_specialist_agent.py`
   - [ ] Implement mapping rule impact analysis
   - [ ] Implement schema evolution impact
   - [ ] Implement downstream dependency analysis
   - [ ] Implement risk assessment
   - [ ] Implement mitigation recommendations
   - [ ] Integrate with all orchestrators
   - [ ] Create MCP tools

**Deliverables:**
- ✅ Wave Planning Specialist Agent complete
- ✅ Change Impact Assessment Specialist Agent complete
- ✅ Integration with orchestrators
- ✅ Agent tests

---

#### **Week 6: Routing Decision & Quality Remediation Agents**

**Goal:** Implement agents for complex routing and quality intelligence

**Tasks:**

1. **Routing Decision Specialist Agent**
   - [ ] Create `routing_decision_specialist_agent.py`
   - [ ] Implement complex routing decisions
   - [ ] Implement business context analysis
   - [ ] Implement conflict resolution
   - [ ] Implement adaptive routing
   - [ ] Integrate with Routing Engine Service
   - [ ] Create MCP tools

2. **Data Quality Remediation Specialist Agent**
   - [ ] Create `quality_remediation_specialist_agent.py`
   - [ ] Implement anomaly interpretation
   - [ ] Implement remediation strategy suggestions
   - [ ] Implement priority ranking
   - [ ] Implement pattern detection
   - [ ] Implement preventive recommendations
   - [ ] Integrate with Data Steward
   - [ ] Integrate with Insurance Migration Orchestrator
   - [ ] Create MCP tools

**Deliverables:**
- ✅ Routing Decision Specialist Agent complete
- ✅ Data Quality Remediation Specialist Agent complete
- ✅ Integration with services
- ✅ Agent tests

---

### **Week 7-8: Advanced Agent Integration**

#### **Week 7: Coexistence Strategy & Saga/WAL Management Agents**

**Goal:** Implement strategic planning and operational intelligence agents

**Tasks:**

1. **Coexistence Strategy Specialist Agent**
   - [ ] Create `coexistence_strategy_specialist_agent.py`
   - [ ] Implement coexistence pattern analysis
   - [ ] Implement sync strategy recommendations
   - [ ] Implement conflict resolution strategies
   - [ ] Implement retirement planning
   - [ ] Implement cost-benefit analysis
   - [ ] Integrate with Solution Composer Service
   - [ ] Create MCP tools

2. **Saga/WAL Management Specialist Agent**
   - [ ] Create `saga_wal_management_agent.py`
   - [ ] Implement saga execution monitoring
   - [ ] Implement WAL entry triage
   - [ ] Implement intelligent notifications
   - [ ] Implement escalation intelligence
   - [ ] Implement recovery recommendations
   - [ ] Implement predictive monitoring
   - [ ] Integrate with Saga Journey Orchestrator
   - [ ] Integrate with Data Steward WAL
   - [ ] Integrate with Solution Analytics dashboard
   - [ ] Create MCP tools

**Deliverables:**
- ✅ Coexistence Strategy Specialist Agent complete
- ✅ Saga/WAL Management Specialist Agent complete
- ✅ Dashboard integration for Saga/WAL Management
- ✅ Agent tests

---

#### **Week 8: Solution & Journey Integration**

**Goal:** Complete Solution and Journey realm integration

**Tasks:**

1. **Saga Journey Template Integration**
   - [ ] Integrate `INSURANCE_WAVE_MIGRATION_SAGA` template
   - [ ] Integrate `POLICY_MAPPING_SAGA` template
   - [ ] Integrate `WAVE_VALIDATION_SAGA` template
   - [ ] Implement compensation handlers
   - [ ] Test saga execution and compensation
   - [ ] Integration with Wave Orchestrator

2. **Solution Composer Template Integration**
   - [ ] Integrate `INSURANCE_MIGRATION_SOLUTION` template
   - [ ] Integrate `INSURANCE_DISCOVERY_JOURNEY` template
   - [ ] Integrate `INSURANCE_VALIDATION_JOURNEY` template
   - [ ] Test multi-phase solution execution
   - [ ] Integration with all orchestrators

3. **Dashboard Integration**
   - [ ] Extend Solution Analytics with agent insights
   - [ ] Create Saga Execution Dashboard component
   - [ ] Create WAL Operations Dashboard component
   - [ ] Create Operational Intelligence Dashboard component
   - [ ] Integrate with Solution Deployment Manager

**Deliverables:**
- ✅ Saga Journey templates integrated
- ✅ Solution Composer templates integrated
- ✅ Dashboard components complete
- ✅ Integration tests

---

### **Week 9-10: Universal Mapper Validation (Client 1-2)**

#### **Week 9: Universal Mapper - Client 1 Baseline**

**Goal:** Establish baseline metrics for Universal Mapper validation

**Tasks:**

1. **Client 1 Processing**
   - [ ] Process Client 1 mappings (manual/semi-automated)
   - [ ] Store all mappings in Universal Mapping Knowledge Base
   - [ ] Track baseline metrics:
     - Initial mapping accuracy: 50-70% (expected)
     - After corrections: 85-90% (expected)
     - Manual interventions: 10-15% (expected)
   - [ ] Extract field name patterns
   - [ ] Build semantic equivalences
   - [ ] Calculate confidence scores

2. **Knowledge Base Population**
   - [ ] Store all Client 1 field patterns
   - [ ] Store mapping rules (source → canonical)
   - [ ] Store semantic equivalences
   - [ ] Store validation patterns
   - [ ] Track learning metrics

**Deliverables:**
- ✅ Client 1 mappings processed
- ✅ Baseline metrics established
- ✅ Knowledge base populated
- ✅ Pattern learning validated

---

#### **Week 10: Universal Mapper - Client 2 Learning**

**Goal:** Validate pattern learning with Client 2

**Tasks:**

1. **Client 2 Processing with Learned Patterns**
   - [ ] Use Client 1 patterns to suggest Client 2 mappings
   - [ ] Measure improvement:
     - Initial mapping accuracy: Target 60-75% (10-15% improvement)
     - After corrections: Target 88-92% (3-5% improvement)
     - Manual interventions: Target 8-12% (2-3% reduction)
   - [ ] Learn from Client 2 corrections (with human approval)
   - [ ] Update knowledge base with new patterns
   - [ ] Refine confidence scores

2. **Learning Validation**
   - [ ] Track fields auto-mapped using Client 1 patterns
   - [ ] Track new patterns discovered
   - [ ] Calculate accuracy improvement
   - [ ] Calculate reduction in manual interventions
   - [ ] Validate learning effectiveness

**Deliverables:**
- ✅ Client 2 mappings processed with learned patterns
   - ✅ Improvement metrics validated
   - ✅ Knowledge base updated
   - ✅ Learning effectiveness confirmed

---

### **Week 11-12: Testing, Validation & Production Readiness**

#### **Week 11: Comprehensive Testing**

**Goal:** End-to-end testing of all Phase 2 components

**Tasks:**

1. **Orchestrator Testing**
   - [ ] Test complete `ingest_legacy_data()` workflow
   - [ ] Test complete `map_to_canonical()` workflow
   - [ ] Test complete `route_policies()` workflow
   - [ ] Test error handling and compensation
   - [ ] Test state management and resumption

2. **Agent Testing**
   - [ ] Test all 8 agents individually
   - [ ] Test agent-orchestrator integration
   - [ ] Test agent-service integration
   - [ ] Test agent learning capabilities (Universal Mapper)
   - [ ] Test agent dashboard integration (Saga/WAL Management)

3. **Integration Testing**
   - [ ] Test Wave Orchestrator with Insurance Migration Orchestrator
   - [ ] Test Policy Tracker with Routing Engine
   - [ ] Test Saga Journey execution and compensation
   - [ ] Test Solution Composer multi-phase execution
   - [ ] Test Universal Mapper pattern learning

**Deliverables:**
- ✅ Comprehensive test suite
- ✅ Test results and coverage reports
- ✅ Bug fixes and improvements
- ✅ Performance benchmarks

---

#### **Week 14: Production Readiness & Documentation**

**Goal:** Finalize production readiness and documentation

**Tasks:**

1. **Production Readiness**
   - [ ] Performance optimization
   - [ ] Security hardening
   - [ ] Error handling improvements
   - [ ] Monitoring and alerting setup
   - [ ] Deployment documentation

2. **Documentation**
   - [ ] Update all agent documentation
   - [ ] Update orchestrator documentation
   - [ ] Create Universal Mapper validation report
   - [ ] Create Phase 2 completion report
   - [ ] Create production deployment guide

3. **Client 3 Validation (If Available)**
   - [ ] Process Client 3 with learned patterns (if available)
   - [ ] Validate hypothesis:
     - Initial mapping accuracy ≥ 70%
     - Manual interventions ≤ 10%
     - Pattern discovery rate decreases
   - [ ] Generate validation report

**Deliverables:**
- ✅ Production-ready codebase
- ✅ Complete documentation
- ✅ Universal Mapper validation report (if Client 3 available)
- ✅ Phase 2 completion report

---

## 📋 Detailed Component Specifications

### **1. Orchestrator Completion**

#### **1.1 Complete `ingest_legacy_data()` Orchestration**

**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/insurance_migration_orchestrator/insurance_migration_orchestrator.py`

**Implementation:**
```python
async def ingest_legacy_data(
    self,
    file_id: Optional[str] = None,
    file_data: Optional[bytes] = None,
    filename: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete orchestration:
    1. Upload/get file via Content Steward
    2. Parse file via File Parser Service
    3. Profile data via Data Steward
    4. Extract schema via Schema Mapper Service
    5. Store metadata via Librarian
    6. Track lineage via Data Steward
    7. WAL logging (already done)
    """
    # Step 1: Upload/get file
    content_steward = await self.get_content_steward_api()
    if file_data:
        upload_result = await content_steward.upload_file(
            file_data=file_data,
            filename=filename,
            user_context=user_context
        )
        file_id = upload_result["file_id"]
    else:
        file_metadata = await content_steward.get_file_metadata(
            file_id=file_id,
            user_context=user_context
        )
    
    # Step 2: Parse file
    file_parser = await self.get_enabling_service("FileParserService")
    parse_result = await file_parser.parse_file(
        file_id=file_id,
        user_context=user_context
    )
    
    # Step 3: Profile data quality
    data_steward = await self.get_data_steward_api()
    profile_result = await data_steward.profile_data(
        data=parse_result["parsed_data"],
        user_context=user_context
    )
    
    # Step 4: Extract schema
    schema_mapper = await self.get_enabling_service("SchemaMapperService")
    schema_result = await schema_mapper.extract_schema(
        data=parse_result["parsed_data"],
        user_context=user_context
    )
    
    # Step 5: Store metadata
    librarian = await self.get_librarian_api()
    metadata_id = await librarian.store_document(
        document_data={
            "file_id": file_id,
            "schema": schema_result["schema"],
            "quality_metrics": profile_result["metrics"],
            "parsed_data_summary": {
                "record_count": len(parse_result["parsed_data"]),
                "fields": list(parse_result["parsed_data"][0].keys()) if parse_result["parsed_data"] else []
            }
        },
        metadata={
            "type": "legacy_data_ingestion",
            "file_id": file_id,
            "timestamp": datetime.utcnow().isoformat()
        },
        user_context=user_context
    )
    
    # Step 6: Track lineage
    await data_steward.track_lineage(
        lineage_data={
            "source": file_id,
            "operation": "ingest_legacy_data",
            "target": metadata_id,
            "metadata": {
                "schema_id": schema_result.get("schema_id"),
                "quality_metrics": profile_result["metrics"]
            }
        },
        user_context=user_context
    )
    
    # Step 7: WAL logging (already done at start)
    
    return {
        "success": True,
        "file_id": file_id,
        "metadata_id": metadata_id,
        "parsed_data": parse_result["parsed_data"],
        "schema": schema_result["schema"],
        "quality_metrics": profile_result["metrics"]
    }
```

**Error Handling:**
- Try-catch around each step
- Compensation handlers for rollback
- WAL logging for all operations
- State management for resumption

---

#### **1.2 Complete `map_to_canonical()` Orchestration**

**Location:** Same as above

**Implementation:**
```python
async def map_to_canonical(
    self,
    source_data: Dict[str, Any],
    source_schema_id: Optional[str] = None,
    mapping_rules: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete orchestration:
    1. Get source schema from Librarian (if not provided)
    2. Validate source data via Data Steward
    3. Map source → canonical via Schema Mapper Service
    4. Validate canonical data via Canonical Model Service
    5. Store mapping rules via Librarian
    6. Track mapping lineage
    7. WAL logging (already done)
    """
    # Step 1: Get source schema
    librarian = await self.get_librarian_api()
    if source_schema_id:
        source_schema_doc = await librarian.get_document(
            document_id=source_schema_id,
            user_context=user_context
        )
        source_schema = source_schema_doc.get("document", {})
    else:
        # Extract schema from source_data
        schema_mapper = await self.get_enabling_service("SchemaMapperService")
        schema_result = await schema_mapper.extract_schema(
            data=source_data,
            user_context=user_context
        )
        source_schema = schema_result["schema"]
    
    # Step 2: Validate source data
    data_steward = await self.get_data_steward_api()
    validation_result = await data_steward.validate_data(
        data=source_data,
        schema=source_schema,
        user_context=user_context
    )
    
    if not validation_result.get("valid"):
        return {
            "success": False,
            "error": "Source data validation failed",
            "validation_errors": validation_result.get("errors", [])
        }
    
    # Step 3: Map source → canonical
    schema_mapper = await self.get_enabling_service("SchemaMapperService")
    mapping_result = await schema_mapper.map_schema(
        source_schema_id=source_schema_id or "extracted",
        target_schema_id="canonical_policy_v1",
        mapping_strategy="semantic_match",
        user_context=user_context
    )
    
    # Apply mapping rules if provided
    if mapping_rules:
        mapping_result["field_mappings"].update(mapping_rules)
    
    # Step 4: Validate canonical data
    canonical_service = await self._get_canonical_model_service()
    canonical_validation = await canonical_service.validate_against_canonical(
        data=source_data,  # Will be transformed by mapping
        model_name="policy",
        version="1.0.0",
        user_context=user_context
    )
    
    if not canonical_validation.get("valid"):
        return {
            "success": False,
            "error": "Canonical data validation failed",
            "validation_errors": canonical_validation.get("errors", [])
        }
    
    # Step 5: Store mapping rules
    mapping_rules_id = await librarian.store_document(
        document_data={
            "mapping_id": mapping_result.get("mapping_id"),
            "source_schema": source_schema,
            "canonical_model": "policy_v1",
            "mapping_rules": mapping_result["field_mappings"],
            "confidence_score": mapping_result.get("confidence_score", 0.0)
        },
        metadata={
            "type": "canonical_mapping_rules",
            "source_schema_id": source_schema_id,
            "timestamp": datetime.utcnow().isoformat()
        },
        user_context=user_context
    )
    
    # Step 6: Track lineage
    await data_steward.track_lineage(
        lineage_data={
            "source": source_data.get("policy_id") or "unknown",
            "operation": "map_to_canonical",
            "target": mapping_rules_id,
            "metadata": {
                "canonical_model": "policy_v1",
                "mapping_confidence": mapping_result.get("confidence_score", 0.0)
            }
        },
        user_context=user_context
    )
    
    # Step 7: WAL logging (already done at start)
    
    return {
        "success": True,
        "mapping_rules_id": mapping_rules_id,
        "canonical_data": canonical_validation.get("canonical_data"),
        "mapping_confidence": mapping_result.get("confidence_score", 0.0),
        "validation_result": canonical_validation
    }
```

---

#### **1.3 Complete `route_policies()` Orchestration**

**Location:** Same as above

**Implementation:**
```python
async def route_policies(
    self,
    policy_data: Dict[str, Any],
    namespace: str = "default",
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete orchestration:
    1. Get policy status from Policy Tracker
    2. Extract routing key via Routing Engine Service
    3. Evaluate routing rules via Routing Engine Service
    4. Update Policy Tracker with routing decision
    5. Store routing decision in Librarian
    6. Track routing lineage
    7. WAL logging (already done)
    """
    # Step 1: Get policy status
    policy_tracker = await self._get_policy_tracker_orchestrator()
    policy_status = await policy_tracker.get_policy_location(
        policy_id=policy_data.get("policy_id"),
        user_context=user_context
    )
    
    # Step 2: Extract routing key
    routing_engine = await self._get_routing_engine_service()
    routing_key = await routing_engine.extract_routing_key(
        policy_data=policy_data,
        user_context=user_context
    )
    
    # Step 3: Evaluate routing rules
    routing_result = await routing_engine.evaluate_routing(
        routing_key=routing_key,
        policy_data=policy_data,
        namespace=namespace,
        user_context=user_context
    )
    
    # Step 4: Update Policy Tracker
    await policy_tracker.update_migration_status(
        policy_id=policy_data.get("policy_id"),
        status=routing_result["target_system"],
        location=routing_result["target_system"],
        user_context=user_context
    )
    
    # Step 5: Store routing decision
    librarian = await self.get_librarian_api()
    routing_decision_id = await librarian.store_document(
        document_data={
            "policy_id": policy_data.get("policy_id"),
            "routing_key": routing_key,
            "target_system": routing_result["target_system"],
            "routing_rules": routing_result["matched_rules"],
            "confidence": routing_result.get("confidence", 0.0)
        },
        metadata={
            "type": "routing_decision",
            "policy_id": policy_data.get("policy_id"),
            "timestamp": datetime.utcnow().isoformat()
        },
        user_context=user_context
    )
    
    # Step 6: Track lineage
    data_steward = await self.get_data_steward_api()
    await data_steward.track_lineage(
        lineage_data={
            "source": policy_data.get("policy_id"),
            "operation": "route_policies",
            "target": routing_result["target_system"],
            "metadata": {
                "routing_key": routing_key,
                "routing_decision_id": routing_decision_id
            }
        },
        user_context=user_context
    )
    
    # Step 7: WAL logging (already done at start)
    
    return {
        "success": True,
        "routing_decision_id": routing_decision_id,
        "target_system": routing_result["target_system"],
        "routing_key": routing_key,
        "confidence": routing_result.get("confidence", 0.0)
    }
```

---

### **2. Agent Integration Details**

#### **2.1 Insurance Liaison Agent**

**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/insurance_migration_orchestrator/agents/insurance_liaison_agent.py`

**Capabilities:**
- Conversational guidance for migration operations
- Route to appropriate orchestrators
- Answer questions about wave planning
- Answer questions about policy tracking
- Provide migration workflow guidance

**Integration:**
- Registered with Insurance Migration Orchestrator
- Uses orchestrator MCP tools
- Provides conversational interface

---

#### **2.2 Universal Mapper Agent**

**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/universal_mapper_agent/universal_mapper_agent.py`

**Capabilities:**
- **Pattern Learning:** Learn field name patterns from approved mappings across clients
- **AI-Assisted Schema Mapping:** Suggest mappings from source schema to canonical model (replaces Insurance Migration Specialist)
- **Mapping Rule Generation:** Generate mapping rules from examples (replaces Insurance Migration Specialist)
- **Data Quality Interpretation:** Interpret quality metrics and suggest remediation (replaces Insurance Migration Specialist)
- **Mapping Validation:** Validate mappings against learned patterns
- **Human Feedback Learning:** Learn from corrections with explicit approval
- **ACORD Standard Reference:** Use ACORD as reference (adapts to variations)
- **Coexistence Support:** Works for both migration AND coexistence scenarios

**Knowledge Base:**
- Stored in Librarian
- Field patterns with confidence scores
- Semantic equivalences
- Mapping rules per client
- Learning metrics

**Validation:**
- Client 1: Baseline (50-70% accuracy)
- Client 2: Learning (60-75% accuracy target)
- Client 3+: Validation (70-85% accuracy target)

---

#### **2.4 Saga/WAL Management Specialist Agent**

**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/saga_wal_management_agent/saga_wal_management_agent.py`

**Capabilities:**
- Saga execution monitoring
- WAL entry triage
- Intelligent notifications
- Escalation intelligence
- Recovery recommendations
- Predictive monitoring

**Dashboard Integration:**
- Saga Execution Dashboard
- WAL Operations Dashboard
- Operational Intelligence Dashboard
- Integrated with Solution Analytics

---

### **3. Wave Orchestration Details**

#### **3.1 Wave Orchestrator Service**

**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/wave_orchestrator/wave_orchestrator.py`

**Key Methods:**
- `create_wave()` - Create migration wave with quality gates
- `select_wave_candidates()` - Select policies for wave
- `execute_wave()` - Execute wave with quality gate enforcement
- `rollback_wave()` - Rollback wave with compensation
- `get_wave_status()` - Monitor wave execution

**Integration:**
- Uses Insurance Migration Orchestrator for migration
- Uses Policy Tracker for status tracking
- Uses WAL for audit trail
- Uses Saga Journey for atomicity

---

### **4. Solution & Journey Integration**

#### **4.1 Saga Journey Templates**

**Templates:**
- `INSURANCE_WAVE_MIGRATION_SAGA` - Wave migration with compensation
- `POLICY_MAPPING_SAGA` - Policy mapping with rollback
- `WAVE_VALIDATION_SAGA` - Wave validation with compensation

**Integration:**
- Auto-loaded by Saga Journey Orchestrator
- Compensation handlers implemented
- WAL logging for all operations

---

#### **4.2 Solution Composer Templates**

**Templates:**
- `INSURANCE_MIGRATION_SOLUTION` - Multi-phase migration solution
- `INSURANCE_DISCOVERY_JOURNEY` - Discovery phase journey
- `INSURANCE_VALIDATION_JOURNEY` - Validation phase journey

**Integration:**
- Auto-loaded by Solution Composer Service
- Multi-phase orchestration
- Integration with all orchestrators

---

## 📊 Success Criteria

### **Orchestrator Completion:**
- ✅ All three methods fully orchestrate 7 steps
- ✅ Error handling and compensation implemented
- ✅ State management and resumption working
- ✅ Integration tests passing

### **Agent Integration:**
- ✅ All 9 agents implemented and tested
- ✅ Agent-orchestrator integration working
- ✅ Agent learning capabilities validated (Universal Mapper)
- ✅ Dashboard integration complete (Saga/WAL Management)

### **Wave Orchestration:**
- ✅ Wave Orchestrator service complete
- ✅ Quality gates enforced
- ✅ Wave execution and rollback working
- ✅ Integration with Insurance Migration Orchestrator

### **Universal Mapper Validation:**
- ✅ Client 1 baseline established (50-70% accuracy)
- ✅ Client 2 learning validated (60-75% accuracy target)
- ✅ Client 3+ validation (70-85% accuracy target, if available)
- ✅ Hypothesis validated: Initial accuracy ≥ 70%, Manual interventions ≤ 10%

---

## 🎯 Deliverables Summary

### **Code:**
- ✅ Complete orchestrator implementations (3 methods × 7 steps)
- ✅ Schema Mapper Service enhancements
- ✅ 8 agent implementations (Universal Mapper replaces Insurance Migration Specialist)
- ✅ Advanced routing capabilities
- ✅ Bi-directional data flows
- ✅ Client onboarding CLI tool
- ✅ Wave Orchestrator service
- ✅ Policy Tracker Orchestrator service
- ✅ MCP servers for all orchestrators
- ✅ Dashboard components

### **Documentation:**
- ✅ Agent integration documentation
- ✅ Universal Mapper validation report
- ✅ Orchestrator completion documentation
- ✅ Phase 2 completion report

### **Testing:**
- ✅ Comprehensive test suite
- ✅ Integration tests
- ✅ Agent tests
- ✅ Performance benchmarks

---

## 📝 Key Changes from Original Plan

### **Agent Consolidation:**
- ✅ **Removed:** Insurance Migration Specialist Agent (overlapped with Universal Mapper)
- ✅ **Enhanced:** Universal Mapper Agent now covers:
  - AI-assisted schema mapping (from Insurance Migration Specialist)
  - Mapping rule generation (from Insurance Migration Specialist)
  - Data quality interpretation (from Insurance Migration Specialist)
  - Pattern learning across clients (unique to Universal Mapper)
  - Works for both migration AND coexistence scenarios

### **Added from V2 Plan:**
- ✅ Schema Mapper Service enhancements (canonical model support, mapping chains)
- ✅ Advanced Routing Engine (multi-system routing, state management, reversals)
- ✅ Bi-Directional Data Flows (dual-write, selective-write, sync orchestration)
- ✅ Client Onboarding CLI Tool (`data_mash_cli.py`)

### **Timeline Adjustment:**
- Extended from 8-12 weeks to **12-14 weeks** to accommodate:
  - Advanced Routing (Week 11)
  - Bi-Directional Flows (Week 12)
  - Comprehensive testing (Week 13)
  - Production readiness (Week 14)

### **Complete Coverage:**
- ✅ All items from original Phase 2 plan (V2)
- ✅ All gap analysis items (orchestrator completion)
- ✅ All agent integrations (8 agents, consolidated)
- ✅ Universal Mapper validation (CDO hypothesis)

---

**Last Updated:** December 2024  
**Status:** 📋 **COMPREHENSIVE PLAN CREATED - READY FOR IMPLEMENTATION**

