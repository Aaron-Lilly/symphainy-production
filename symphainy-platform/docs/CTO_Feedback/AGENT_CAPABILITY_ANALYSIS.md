# Agent Capability Analysis
## What Agents Actually Do vs What MVP Needs

**Date:** November 6, 2025  
**Purpose:** Determine which enabling services need agentic enhancement for MVP

---

## 🔍 **INVESTIGATION FINDINGS**

### **Current Agent Types (What They Actually Do):**

#### **1. Liaison Agents** 
**Files Analyzed:**
- `content_liaison_agent.py`
- `insights_liaison_agent.py`
- `operations_liaison_agent.py`
- `business_outcomes_liaison_agent.py`

**What They Do:**
- ✅ Provide CONVERSATIONAL GUIDANCE ("I can help you...")
- ✅ Explain capabilities and features
- ✅ Route to appropriate services/orchestrators
- ❌ Do NOT execute services directly
- ❌ Do NOT use MCP tools
- ❌ Do NOT call LLMs

**Pattern:** Help desk / FAQ bot behavior

**Example:**
```python
async def _handle_file_upload_query(...):
    response = "I can help you with file uploads! Here's what you need to know:\n\n"
    response += "**Supported File Types:**\n"
    response += "• PDF documents\n"
    response += "• Microsoft Word (.docx)\n"
    # ... more text guidance ...
    return response
```

**Conclusion:** Liaison agents are **conversational routers**, not service executors.

---

#### **2. Specialist Agents**
**Files Analyzed:**
- `operations_specialist_agent.py`
- `business_outcomes_specialist_agent.py`

**What They Do:**
- ✅ EXECUTE specialized analysis tasks
- ✅ Call business services (sop_analysis_service, coexistence_optimization_service)
- ✅ Use LLMs for generation (blueprint creation, analysis)
- ✅ Perform complex reasoning
- ✅ Generate artifacts (blueprints, analyses, recommendations)

**Pattern:** AI-powered service execution

**Example:**
```python
async def _perform_coexistence_analysis(...):
    # ACTUALLY calls business service
    coexistence_result = await self.coexistence_optimization_service.analyze_human_ai_coexistence(
        workflow_data, user_context
    )
    
    # ACTUALLY uses LLM to generate blueprint
    blueprint_prompt = self._create_blueprint_prompt(...)
    blueprint_response = await self.utility_foundation.generate_llm_response(
        prompt=blueprint_prompt,
        user_context=user_context
    )
    
    return blueprint  # ACTUAL artifact generated
```

**Conclusion:** Specialist agents are **AI-powered capability executors**.

---

#### **3. Wizard Modules**
**Files Analyzed:**
- `sop_builder_wizard.py`

**What They Do:**
- ✅ Structured, guided workflows
- ✅ Call business services
- ✅ Validate and enhance outputs
- ✅ Generate artifacts (SOPs)
- ❌ Not conversational
- ❌ Not adaptive reasoning

**Pattern:** Guided workflow execution

**Example:**
```python
async def create_sop(self, description, user_context, ...):
    # Structured workflow
    sop_structure = await self._generate_sop_structure(description, template)
    
    # Call business service
    sop_analysis_result = await self.sop_analysis_service.analyze_sop_structure(
        sop_structure, user_context
    )
    
    # Enhance with service
    enhance_result = await self.sop_analysis_service.enhance_sop_content(
        sop_structure, user_context
    )
    
    return sop_content  # ACTUAL SOP artifact
```

**Conclusion:** Wizards are **structured capability executors**.

---

## 📋 **MVP REQUIREMENTS ANALYSIS**

### **From MVP_Description_For_Business_and_Technical_Readiness.md:**

#### **Content Pillar:**
- "file uploader that supports multiple file types"
- "parsing function that maps your file to an AI friendly format"
- "allows you to preview your data"
- "ContentLiaisonAgent allows you to interact with your parsed file"

**Agent Needs:**
- ✅ Liaison: Conversational help for upload/parsing
- ❌ Specialist: File parsing is deterministic (enabling service handles it)

---

#### **Insights Pillar:**
- "formatted text element to provide business analysis"
- "visual or tabular representation of your data"
- "insight liaison serves as plain english guide"
- "double click on initial analysis"
- "insights summary with recommendations"

**Agent Needs:**
- ✅ Liaison: Conversational help for navigating insights
- ✅ Specialist: **BUSINESS ANALYSIS** (AI-powered interpretation)
- ✅ Specialist: **RECOMMENDATION GENERATION** (AI reasoning)

---

#### **Operations Pillar:**
- "translate into visual elements (workflow and SOP)"
- "use AI to create the other [workflow or SOP]"
- "generate coexistence blueprint with analysis and recommendations"
- "custom development flow with OperationsLiaison"
- "describe current process (works with workflowbuilderwizard to create SOP)"
- "design target state coexistence (works with coexistenceevaluator)"

**Agent Needs:**
- ✅ Liaison: Conversational wizard guidance
- ✅ Specialist: **SOP GENERATION** (AI-powered creation)
- ✅ Specialist: **WORKFLOW GENERATION** (AI-powered creation)
- ✅ Specialist: **COEXISTENCE BLUEPRINT** (AI-powered analysis + recommendations)
- ✅ Wizard: SOP Builder Wizard (structured workflow)

---

#### **Business Outcomes Pillar:**
- "displaying summary outputs from other pillars"
- "Experience Liaison prompts for additional context"
- "prepares final analysis: roadmap and POC proposal"

**Agent Needs:**
- ✅ Liaison: Conversational requirements gathering
- ✅ Specialist: **ROADMAP GENERATION** (AI-powered synthesis)
- ✅ Specialist: **POC PROPOSAL GENERATION** (AI-powered recommendation)

---

## 🎯 **STRATEGIC CONCLUSION**

### **Liaison Agents (4 total) - Already Built!** ✅
We just built these using the new SDK-first pattern:
- Content Liaison
- Insights Liaison
- Operations Liaison
- Business Outcomes Liaison

**What they do:** Conversational help, routing, guidance
**MCP tools:** None needed (they route to orchestrators/specialists)

---

### **Specialist Agents (Actual Need: 5-6)**

#### **Agents We NEED for MVP:**

1. **Business Analysis Specialist** ⏳
   - **For:** Insights Pillar
   - **Does:** AI-powered business analysis of data
   - **Enabling Service:** Data Analyzer Service
   - **MCP Tools:** `analyze_data()`, `detect_patterns()`
   - **Output:** Business analysis text with insights

2. **Recommendation Specialist** ⏳
   - **For:** Insights Pillar + Business Outcomes Pillar
   - **Does:** AI-powered recommendation generation
   - **Enabling Service:** Metrics Calculator Service
   - **MCP Tools:** `calculate_metrics()`, `generate_recommendations()`
   - **Output:** Actionable recommendations with metrics

3. **SOP Generation Specialist** ⏳
   - **For:** Operations Pillar
   - **Does:** AI-powered SOP creation from description
   - **Enabling Service:** Workflow Manager Service (?)
   - **MCP Tools:** `create_workflow()`, `generate_sop()`
   - **Output:** Complete SOP document
   - **Note:** May use SOP Builder Wizard as structured fallback

4. **Workflow Generation Specialist** ⏳
   - **For:** Operations Pillar
   - **Does:** AI-powered workflow creation from SOP
   - **Enabling Service:** Workflow Manager Service
   - **MCP Tools:** `create_workflow()`, `visualize_workflow()`
   - **Output:** Visual workflow diagram

5. **Coexistence Blueprint Specialist** ⏳
   - **For:** Operations Pillar
   - **Does:** AI-powered coexistence analysis + blueprint
   - **Enabling Service:** ??? (may need new service)
   - **MCP Tools:** `analyze_coexistence()`, `generate_blueprint()`
   - **Output:** Coexistence blueprint with recommendations
   - **Note:** Currently uses coexistence_optimization_service

6. **Roadmap & Proposal Specialist** ⏳
   - **For:** Business Outcomes Pillar
   - **Does:** AI-powered roadmap + POC proposal synthesis
   - **Enabling Service:** Report Generator Service
   - **MCP Tools:** `synthesize_insights()`, `generate_roadmap()`, `create_proposal()`
   - **Output:** Roadmap + POC proposal documents

---

### **Agents We DON'T NEED:**

- ❌ File Parser Specialist (deterministic, enabling service handles it)
- ❌ Validation Specialist (deterministic, enabling service handles it)
- ❌ Export Formatter Specialist (deterministic, enabling service handles it)
- ❌ Schema Mapper Specialist (deterministic, enabling service handles it)
- ❌ Transformation Specialist (deterministic, enabling service handles it)
- ❌ Data Compositor Specialist (for Data Mash, not MVP)
- ❌ Reconciliation Specialist (deterministic, enabling service handles it)
- ❌ Audit Trail Specialist (deterministic, enabling service handles it)
- ❌ Configuration Specialist (deterministic, enabling service handles it)
- ❌ Notification Specialist (deterministic, enabling service handles it)

**Pattern:** If it's deterministic (no AI reasoning needed), it's just an enabling service. No agent needed!

---

## 🎨 **REFINED ARCHITECTURE**

### **The Corrected Pattern:**

```
User Request via Chat
    ↓
Guide Agent (cross-domain routing)
    ↓ (routes to domain)
    ↓
Liaison Agent (domain-specific conversation)
    ↓ (determines need)
    ↓
    ├─→ Simple Request → Enabling Service (deterministic)
    │                    └─ File parsing, validation, export, etc.
    │
    └─→ Complex Request → Specialist Agent (AI-powered)
                         ├─ Calls enabling service(s) via MCP tools
                         ├─ Applies AI reasoning
                         ├─ Generates insights/recommendations
                         └─ Returns enhanced output
```

---

## 📊 **ENABLING SERVICES VS SPECIALIST AGENTS**

| Enabling Service | Need Agent? | Why/Why Not |
|------------------|-------------|-------------|
| **File Parser** | ❌ NO | Deterministic file parsing |
| **Data Analyzer** | ✅ YES | **Business Analysis Specialist** - AI interprets data |
| **Metrics Calculator** | ✅ YES | **Recommendation Specialist** - AI generates recommendations |
| **Workflow Manager** | ✅ YES | **SOP/Workflow Generation Specialist** - AI creates processes |
| **Report Generator** | ✅ YES | **Roadmap & Proposal Specialist** - AI synthesizes insights |
| **Validation Engine** | ❌ NO | Deterministic validation rules |
| **Transformation Engine** | ❌ NO | Deterministic data transformation |
| **Export Formatter** | ❌ NO | Deterministic format conversion |
| **Schema Mapper** | ❌ NO | Deterministic schema mapping |
| **Data Compositor** | ❌ NO (MVP) | For Data Mash, not MVP |
| **Visualization Engine** | ❌ NO | Deterministic chart generation |
| **Reconciliation Service** | ❌ NO | Deterministic reconciliation |
| **Audit Trail** | ❌ NO | Deterministic logging |
| **Configuration** | ❌ NO | Deterministic config management |
| **Notification** | ❌ NO | Deterministic notifications |

**Agent Count:** **5-6 specialist agents** (not 15!)

---

## 💡 **KEY INSIGHTS**

### **1. Not All Services Need Agents!** 🎯
- Deterministic services = NO agent needed
- AI reasoning required = YES agent needed
- Rule: Agent only when human-like judgment/creativity needed

### **2. Specialists Do REAL WORK** 💪
- NOT just guidance (that's liaison's job)
- ACTUAL service execution via MCP tools
- AI reasoning + synthesis
- Artifact generation (blueprints, analyses, recommendations)

### **3. Liaison vs Specialist Roles** 📝
**Liaison:**
- Conversational help
- Understanding user intent
- Routing to services/specialists
- Explaining capabilities

**Specialist:**
- AI-powered execution
- Complex reasoning
- Service composition
- Artifact generation

### **4. Wizard vs Agent** 🧙‍♂️
**Wizard:**
- Structured, step-by-step workflow
- Deterministic flow
- Best for known processes

**Specialist Agent:**
- Adaptive, conversational
- AI-driven flow
- Best for open-ended tasks

**MVP Needs Both!**

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Validate Current Liaison Agents** ✅ DONE
- Guide Agent (cross-domain)
- 4 Liaison Agents (domain-specific)

### **Phase 2: Build MVP Specialist Agents** ⏳ NEXT
Build **ONLY** the 5-6 agents that need AI reasoning:

1. **Business Analysis Specialist** (45 min)
   - Enabling Service: Data Analyzer
   - MCP Tools: analyze_data, detect_patterns
   - Output: Business insights

2. **Recommendation Specialist** (45 min)
   - Enabling Service: Metrics Calculator
   - MCP Tools: calculate_metrics, generate_recommendations
   - Output: Actionable recommendations

3. **SOP Generation Specialist** (60 min)
   - Enabling Service: Workflow Manager
   - MCP Tools: generate_sop, create_workflow
   - Output: SOP document
   - Special: Works with SOP Builder Wizard

4. **Workflow Generation Specialist** (45 min)
   - Enabling Service: Workflow Manager
   - MCP Tools: create_workflow, visualize_workflow
   - Output: Workflow diagram

5. **Coexistence Blueprint Specialist** (60 min)
   - Enabling Service: TBD (may need new service)
   - MCP Tools: analyze_coexistence, generate_blueprint
   - Output: Coexistence blueprint

6. **Roadmap & Proposal Specialist** (60 min)
   - Enabling Service: Report Generator
   - MCP Tools: synthesize_insights, generate_roadmap, create_proposal
   - Output: Roadmap + POC proposal

**Total Time:** ~5 hours (vs 15+ hours for 15 agents!)

---

### **Phase 3: Wire Up MCP Tools** ⏳ AFTER AGENTS
- Create MCP tools for relevant orchestrators
- Map tools to specialist capabilities
- Test agent → MCP tool → enabling service flow

### **Phase 4: E2E Testing** ⏳ FINAL
- Test user flow through each pillar
- Validate agent outputs
- Ensure MVP requirements met

---

## ✅ **RECOMMENDATION**

**Build 5-6 specialist agents that add AI value, not 15 agents that duplicate enabling services!**

**Key Principle:**
> "If it's deterministic, it's a service. If it requires AI reasoning, it's an agent."

**Time Savings:**
- Original plan: 15 agents × 1 hour = 15 hours
- Refined plan: 6 agents × 1 hour = 6 hours
- **Savings: 9 hours (60%!)**

**Quality Improvement:**
- Focus on high-value AI capabilities
- Cleaner architecture
- Easier to maintain
- Better separation of concerns

---

## 📋 **NEXT STEPS**

1. ✅ Review this analysis with CTO
2. ⏳ Confirm the 5-6 specialist agents align with MVP vision
3. ⏳ Build specialist agents using SDK-first pattern
4. ⏳ Create MCP tools for orchestrators
5. ⏳ Test E2E user flows
6. ⏳ Deploy to production!

---

**STATUS:** 🟢 **READY FOR CTO REVIEW AND APPROVAL**

**QUESTION:** Does this analysis align with your MVP vision? Should we proceed with building the 5-6 specialist agents identified?







