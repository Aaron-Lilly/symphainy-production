# Insurance Use Case: Agent Integration Plan

**Date:** December 2024  
**Status:** 📋 **PLAN CREATED**

---

## 🎯 Overview

Based on the MVP use case pattern, this document identifies where and how agents should be integrated into the Insurance Use Case (Data Mash architecture).

### **Key Principle from MVP:**
```
If it's DETERMINISTIC → Enabling Service (no agent)
If it needs AI REASONING → Specialist Agent
```

---

## 🔍 MVP Agent Pattern Analysis

### **Current MVP Agents:**

#### **1. Liaison Agents (Conversational Guidance)**
- **ContentLiaisonAgent**: Provides guidance, routes to services
- **Pattern**: Help desk / FAQ behavior
- **Does NOT**: Execute services, use MCP tools directly
- **Does**: Explain capabilities, route to orchestrators

#### **2. Specialist Agents (AI-Powered Execution)**
- **ContentProcessingAgent**: Enhances metadata extraction with AI reasoning
- **Pattern**: POST-PARSING enhancement (works after deterministic services)
- **Does**: 
  - Calls orchestrator methods via MCP tools
  - Adds AI reasoning on top of deterministic output
  - Enhances results with interpretation

**Key Insight:** Specialist agents enhance deterministic service output with AI reasoning, they don't replace services.

---

## 📋 Insurance Use Case: Agent Opportunities

### **Category 1: Analogous to MVP (Direct Mapping)**

#### **1. Insurance Liaison Agent** ✅
**Analogous to:** ContentLiaisonAgent

**Purpose:** Provide conversational guidance for insurance migration operations

**Capabilities:**
- Explain insurance migration capabilities
- Guide users through wave planning
- Route to appropriate orchestrators
- Answer questions about policy tracking

**Implementation:**
- Similar to ContentLiaisonAgent
- Routes to Insurance Migration Orchestrator, Wave Orchestrator, Policy Tracker
- Provides guidance on migration workflows

---

#### **2. Insurance Migration Specialist Agent** ⭐
**Analogous to:** ContentProcessingAgent

**Purpose:** Enhance migration operations with AI reasoning

**Key Enhancement Opportunities:**

**A. AI-Assisted Schema Mapping** (From InsuraceUseCase.md: "AI-assisted semantic mapping")
- **When:** After Schema Mapper Service extracts source schema
- **What:** Agent analyzes source schema and suggests mappings to canonical model
- **How:** 
  - Schema Mapper extracts deterministic schema
  - Agent uses LLM to suggest semantic mappings
  - Agent validates mapping confidence
  - Agent flags ambiguous mappings for human review

**B. AI-Assisted Mapping Rule Generation** (From InsuraceUseCase.md: "AI assists with drafting and validating mapping rules")
- **When:** When creating source → canonical → target mapping chains
- **What:** Agent generates mapping rules from examples
- **How:**
  - Agent analyzes source and target schemas
  - Agent suggests mapping rules based on semantic similarity
  - Agent validates rules against canonical model
  - Agent learns from approved mappings

**C. Data Quality Interpretation** (From InsuraceUseCase.md: "Automated quality checks")
- **When:** After Data Steward profiles data quality
- **What:** Agent interprets quality metrics and suggests remediation
- **How:**
  - Data Steward provides deterministic quality metrics
  - Agent interprets metrics in business context
  - Agent suggests data cleansing strategies
  - Agent prioritizes quality issues by business impact

---

### **Category 2: New Opportunities (Data Mash Specific)**

#### **3. Wave Planning Specialist Agent** 🆕
**Purpose:** AI-powered wave planning and candidate selection

**Opportunity:** Wave planning requires business judgment and risk assessment

**Capabilities:**
- **Analyze Policy Cohorts:** Use AI to identify similar policies for wave grouping
- **Risk Assessment:** Assess migration risk for each wave
- **Quality Gate Recommendations:** Suggest quality gate thresholds based on wave characteristics
- **Timeline Estimation:** Estimate wave duration based on complexity
- **Dependency Analysis:** Identify dependencies between waves

**When to Use:**
- During wave creation (`create_wave`)
- During candidate selection (`select_wave_candidates`)
- Before wave execution (risk assessment)

**How:**
```python
# Orchestrator calls agent for wave planning
wave_plan = await wave_planning_agent.plan_wave(
    selection_criteria=criteria,
    historical_data=previous_waves,
    business_rules=business_rules
)

# Agent uses AI to:
# 1. Analyze policy characteristics
# 2. Group similar policies
# 3. Assess migration risk
# 4. Recommend wave structure
```

---

#### **4. Routing Decision Specialist Agent** 🆕
**Purpose:** AI-powered routing decisions for complex cases

**Opportunity:** Some routing decisions require business judgment beyond simple rules

**Capabilities:**
- **Complex Routing:** Handle edge cases where routing rules are ambiguous
- **Business Context Analysis:** Consider business context in routing decisions
- **Conflict Resolution:** Resolve routing conflicts (e.g., policy partially migrated)
- **Adaptive Routing:** Learn from routing decisions and improve over time

**When to Use:**
- When routing rules are ambiguous
- When policy status is unclear
- When multiple routing targets are possible
- For adaptive routing improvements

**How:**
```python
# Routing Engine evaluates rules first (deterministic)
routing_result = await routing_engine.evaluate_routing(policy_data)

# If ambiguous, agent makes decision
if routing_result.get("confidence") < 0.8:
    agent_decision = await routing_agent.decide_routing(
        policy_data=policy_data,
        routing_options=routing_result["options"],
        business_context=business_context
    )
```

---

#### **5. Change Impact Assessment Specialist Agent** 🆕
**Purpose:** AI-powered change impact analysis (From InsuraceUseCase.md)

**Opportunity:** "Change impact assessment ('if you alter field X, here are the downstream consequences')"

**Capabilities:**
- **Mapping Rule Impact:** Analyze impact of mapping rule changes
- **Schema Evolution Impact:** Assess impact of canonical model changes
- **Downstream Dependency Analysis:** Identify affected policies, waves, systems
- **Risk Assessment:** Assess risk of proposed changes
- **Mitigation Recommendations:** Suggest mitigation strategies

**When to Use:**
- Before changing mapping rules
- Before evolving canonical model
- Before modifying routing rules
- During governance reviews

**How:**
```python
# Agent analyzes change impact
impact = await change_impact_agent.assess_change(
    change_type="mapping_rule",
    change_details=proposed_change,
    current_state=current_mappings,
    downstream_systems=["new_platform", "legacy_system"]
)

# Agent provides:
# - Affected policies count
# - Affected waves
# - Risk assessment
# - Mitigation recommendations
```

---

#### **6. Data Quality Remediation Specialist Agent** 🆕
**Purpose:** AI-powered data quality remediation strategies

**Opportunity:** "Automated quality checks (profiling, reject buckets, anomaly detection)"

**Capabilities:**
- **Anomaly Interpretation:** Interpret data quality anomalies in business context
- **Remediation Strategy:** Suggest data cleansing strategies
- **Priority Ranking:** Rank quality issues by business impact
- **Pattern Detection:** Detect patterns in data quality issues
- **Preventive Recommendations:** Suggest preventive measures

**When to Use:**
- After data profiling
- During quality gate checks
- When quality issues are detected
- For preventive quality management

**How:**
```python
# Data Steward profiles data (deterministic)
quality_metrics = await data_steward.profile_data(policy_data)

# Agent interprets and suggests remediation
remediation = await quality_agent.recommend_remediation(
    quality_metrics=quality_metrics,
    business_context=business_context,
    policy_type=policy_type
)
```

---

#### **7. Coexistence Strategy Specialist Agent** 🆕
**Purpose:** AI-powered coexistence strategy recommendations

**Opportunity:** Multi-year coexistence requires strategic planning

**Capabilities:**
- **Coexistence Pattern Analysis:** Analyze coexistence patterns and suggest optimizations
- **Sync Strategy Recommendations:** Recommend dual-write vs selective-write strategies
- **Conflict Resolution Strategies:** Suggest conflict resolution approaches
- **Retirement Planning:** Plan legacy system retirement strategy
- **Cost-Benefit Analysis:** Analyze costs/benefits of coexistence strategies

**When to Use:**
- During solution design
- When planning bi-directional flows
- During coexistence optimization
- For retirement planning

**How:**
```python
# Agent analyzes coexistence strategy
strategy = await coexistence_agent.recommend_strategy(
    current_state=current_coexistence,
    business_goals=business_goals,
    constraints=constraints
)

# Agent provides:
# - Recommended coexistence pattern
# - Sync strategy
# - Conflict resolution approach
# - Retirement timeline
```

---

## 🏗️ Agent Architecture for Insurance Use Case

### **Agent → Orchestrator → Enabling Services Pattern**

```
Specialist Agent
    ↓ (calls orchestrator methods via MCP tools)
Orchestrator (e.g., InsuranceMigrationOrchestrator)
    ↓ (calls enabling services)
Enabling Services (e.g., SchemaMapperService, CanonicalModelService)
    ↓ (calls Smart City services)
Smart City Services (e.g., Data Steward, Librarian)
```

### **Example: AI-Assisted Schema Mapping**

```python
# 1. Orchestrator calls Schema Mapper (deterministic)
schema_result = await schema_mapper.extract_schema(source_data)

# 2. Orchestrator calls Agent for AI enhancement
mapping_suggestions = await migration_agent.suggest_canonical_mappings(
    source_schema=schema_result["schema"],
    canonical_model="policy_v1"
)

# 3. Agent uses LLM to:
#    - Analyze semantic similarity
#    - Suggest field mappings
#    - Calculate confidence scores
#    - Flag ambiguous mappings

# 4. Orchestrator uses suggestions to create mapping rules
mapping_rules = await schema_mapper.create_mapping_rules(
    source_schema=schema_result["schema"],
    canonical_model="policy_v1",
    suggested_mappings=mapping_suggestions["mappings"]
)
```

---

## 📊 Agent Integration Matrix

| Agent | Type | Orchestrator | Primary Enhancement | When to Use |
|-------|------|--------------|-------------------|-------------|
| **Insurance Liaison** | Liaison | All | Conversational guidance | User queries, guidance |
| **Migration Specialist** | Specialist | Insurance Migration | Schema mapping, rule generation | During ingestion, mapping |
| **Wave Planning Specialist** | Specialist | Wave | Wave planning, risk assessment | Wave creation, selection |
| **Routing Decision Specialist** | Specialist | Routing Engine | Complex routing decisions | Ambiguous routing cases |
| **Change Impact Specialist** | Specialist | All | Change impact analysis | Before rule/model changes |
| **Quality Remediation Specialist** | Specialist | Insurance Migration | Quality remediation | After profiling, quality gates |
| **Coexistence Strategy Specialist** | Specialist | Solution Composer | Coexistence strategy | Solution design, planning |
| **Saga/WAL Management Specialist** | Specialist | Saga Journey / Data Steward | Triage, notifications, escalations | Ongoing operations, monitoring |

---

## 🎯 Implementation Priority

### **Phase 1: Core Agents (MVP Parity)**
1. ✅ **Insurance Liaison Agent** - User guidance
2. ⭐ **Insurance Migration Specialist Agent** - AI-assisted mapping

### **Phase 2: Strategic Agents (Data Mash Specific)**
3. 🆕 **Wave Planning Specialist Agent** - Wave planning intelligence
4. 🆕 **Change Impact Assessment Specialist Agent** - Governance intelligence

### **Phase 3: Advanced Agents (Optimization)**
5. 🆕 **Routing Decision Specialist Agent** - Complex routing
6. 🆕 **Quality Remediation Specialist Agent** - Quality intelligence
7. 🆕 **Coexistence Strategy Specialist Agent** - Strategic planning
8. ⭐ **Saga/WAL Management Specialist Agent** - Operational intelligence (HIGH PRIORITY)

---

## 📋 Agent Implementation Pattern

### **Template for Specialist Agents:**

```python
class InsuranceMigrationSpecialistAgent(BusinessSpecialistAgentBase):
    """
    Specialist agent for insurance migration with AI reasoning.
    
    Enhances deterministic service output with AI interpretation.
    """
    
    def __init__(self, ...):
        super().__init__(...)
        self.orchestrator = None  # Set by orchestrator
    
    async def suggest_canonical_mappings(
        self,
        source_schema: Dict[str, Any],
        canonical_model: str
    ) -> Dict[str, Any]:
        """
        AI-powered: Suggest mappings from source schema to canonical model.
        
        POST-SCHEMA-EXTRACTION: Works after Schema Mapper extracts schema.
        """
        # 1. Get deterministic schema (already extracted)
        # 2. Use LLM to analyze semantic similarity
        # 3. Suggest field mappings with confidence scores
        # 4. Flag ambiguous mappings for review
        pass
    
    async def generate_mapping_rules(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        examples: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        AI-powered: Generate mapping rules from examples.
        
        Learns from approved mappings to improve over time.
        """
        # 1. Analyze source and target schemas
        # 2. Learn from example mappings
        # 3. Generate mapping rules
        # 4. Validate against canonical model
        pass
```

---

## 🔗 Integration Points

### **1. Orchestrator Integration**
- Orchestrators call agents for AI enhancement
- Agents use orchestrator MCP tools
- Agents enhance deterministic service output

### **2. MCP Server Integration**
- MCP servers expose orchestrator methods as tools
- Agents can call orchestrator methods via MCP
- Agents can also call orchestrator methods directly

### **3. Service Integration**
- Agents enhance enabling service output
- Agents don't replace services
- Agents add AI reasoning layer

---

## 📚 Related Documentation

- [Agent Analysis Summary](../../symphainy-platform/docs/CTO_Feedback/AGENT_ANALYSIS_SUMMARY.md)
- [Agent Capability Analysis](../../symphainy-platform/docs/CTO_Feedback/AGENT_CAPABILITY_ANALYSIS.md)
- [Architecture Clarification](../../symphainy-platform/docs/11-11/ARCHITECTURE_CLARIFICATION.md)
- [Orchestrator Completion Plan](./ORCHESTRATOR_COMPLETION_PLAN.md)

---

**Last Updated:** December 2024  
**Status:** 📋 **PLAN CREATED - READY FOR IMPLEMENTATION**

