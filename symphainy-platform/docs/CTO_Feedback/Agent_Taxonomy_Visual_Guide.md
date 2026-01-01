# 🤖 Agent Taxonomy Visual Guide

**Quick Reference:** Agent Levels, Capabilities, and Evolution Path

---

## 🎯 4-LEVEL AGENT HIERARCHY

```
┌────────────────────────────────────────────────────────────────┐
│ LEVEL 4: USER-FACING AGENTS                                   │
│ (Orchestration + User Interactivity)                          │
│                                                                │
│  DimensionLiaisonAgent          GlobalGuideAgent             │
│  "Content Pillar Guide"         "Solution Architect"          │
│  └─ Guides users WITHIN         └─ Guides users ACROSS        │
│     a dimension                     ALL dimensions            │
│                                                                │
│  Capabilities: LLM + Tools + State + Orchestration + Chat     │
└────────────────────────────────────────────────────────────────┘
                           ▲
                           │ adds User Interactivity
                           │
┌────────────────────────────────────────────────────────────────┐
│ LEVEL 3: ORCHESTRATION AGENTS                                 │
│ (LLM + Tools + State + Coordination)                          │
│                                                                │
│  DimensionSpecialistAgent       GlobalOrchestratorAgent      │
│  "Content Orchestrator"         "Platform Orchestrator"       │
│  └─ Orchestrates WITHIN         └─ Orchestrates ACROSS        │
│     a dimension                     ALL dimensions            │
│                                                                │
│  Capabilities: LLM + Tools + State Management + Coordination  │
└────────────────────────────────────────────────────────────────┘
                           ▲
                           │ adds Orchestration + State
                           │
┌────────────────────────────────────────────────────────────────┐
│ LEVEL 2: TOOL-ENABLED AGENTS                                  │
│ (LLM + Tools)                                                  │
│                                                                │
│  ToolAgent                                                     │
│  "File Processor" "Data Transformer"                          │
│  └─ Uses tools to accomplish tasks                            │
│                                                                │
│  Capabilities: LLM + MCP Tools                                │
└────────────────────────────────────────────────────────────────┘
                           ▲
                           │ adds Tool Usage
                           │
┌────────────────────────────────────────────────────────────────┐
│ LEVEL 1: SIMPLE AGENTS                                        │
│ (LLM-Only)                                                     │
│                                                                │
│  LightweightLLMAgent          TaskLLMAgent                    │
│  "Content Analyzer"           "Data Extractor"                │
│  └─ General LLM ops           └─ Task-specific LLM ops        │
│                                                                │
│  Capabilities: LLM-only (no tools, no orchestration)          │
└────────────────────────────────────────────────────────────────┘
```

---

## 📊 CAPABILITY MATRIX

| Capability | Level 1 (Simple) | Level 2 (Tool) | Level 3 (Orchestration) | Level 4 (User-Facing) |
|------------|------------------|----------------|-------------------------|------------------------|
| **LLM Operations** | ✅ | ✅ | ✅ | ✅ |
| **MCP Tools** | ❌ | ✅ | ✅ | ✅ |
| **State Management** | ❌ | Basic | ✅ Advanced | ✅ Advanced |
| **Orchestration** | ❌ | ❌ | ✅ | ✅ |
| **Tool Chaining** | ❌ | ❌ | ✅ | ✅ |
| **User Interactivity** | ❌ | ❌ | ❌ | ✅ |
| **Conversational** | ❌ | ❌ | ❌ | ✅ |
| **Cross-Dimensional** | ❌ | ❌ | Global only | Global only |

---

## 🎯 YOUR ORIGINAL TAXONOMY MAPPING

| Your Category | Maps To | Level | Example |
|---------------|---------|-------|---------|
| **"Simple ones (just call an LLM)"** | `LightweightLLMAgent` + `TaskLLMAgent` | Level 1 | Content Analyzer |
| **"Use Tools (wizard agents)"** | `ToolAgent` (NEW name) | Level 2 | File Processor |
| **"Orchestrate (Pillar Agents)"** | `DimensionSpecialistAgent` + `GlobalOrchestratorAgent` | Level 3 | Content Orchestrator |
| **"Talk to Users (Guide & Liaison)"** | `DimensionLiaisonAgent` + `GlobalGuideAgent` | Level 4 | Solution Architect |

**Assessment:** ✅ **Your intuition was PERFECT!** Current implementation matches your vision exactly.

---

## 🚀 EVOLUTION PATH

### **How Agents Evolve Through Levels**

```
Start Simple → Add Capabilities → Add Orchestration → Add User Interface

Level 1                Level 2              Level 3                   Level 4
(Simple)              (Tool-Enabled)       (Orchestration)           (User-Facing)

LightweightLLM  →  ToolAgent  →  DimensionSpecialist  →  DimensionLiaison
     │                  │                    │                        │
     │                  │                    │                        │
     └─ LLM only        └─ + Tools          └─ + Orchestration       └─ + User Chat


                         OR (for global agents)

LightweightLLM  →  ToolAgent  →  GlobalOrchestrator  →  GlobalGuide
     │                  │                    │                    │
     │                  │                    │                    │
     └─ LLM only        └─ + Tools          └─ + Cross-Dim       └─ + User Chat
```

---

## 🏗️ CONCRETE EXAMPLES

### **Level 1: Simple Agent**

```python
# Content Analyzer - analyzes text, no tools
analyzer = LightweightLLMAgent(
    agent_name="ContentAnalyzer",
    capabilities=["analyze", "summarize", "classify"],
    required_roles=["librarian"],
    agui_schema=analysis_schema
)

# Usage
result = await analyzer.call_llm(
    prompt="Analyze this content for themes and topics",
    context={"content": document_text}
)
```

**Use Cases:**
- Text analysis
- Summarization
- Classification
- Entity extraction

---

### **Level 2: Tool Agent**

```python
# File Processor - uses tools to process files
processor = ToolAgent(
    agent_name="FileProcessor",
    capabilities=["upload", "parse", "extract_metadata"],
    required_roles=["librarian", "data_steward"],
    agui_schema=file_processing_schema
)

# Usage
result = await processor.use_tool(
    tool_name="upload_file",
    params={"file": file_data}
)
parsed = await processor.use_tool(
    tool_name="parse_document",
    params={"doc_id": result["doc_id"]}
)
```

**Use Cases:**
- File upload and processing
- Data transformation
- Multi-step tool workflows
- "Wizard" style operations

---

### **Level 3: Orchestration Agent (Dimension)**

```python
# Content Orchestrator - orchestrates content workflows
orchestrator = DimensionSpecialistAgent(
    agent_name="ContentOrchestrator",
    dimension="content_management",
    capabilities=[
        "orchestrate_content_workflow",
        "coordinate_content_tools",
        "manage_content_pipeline"
    ],
    required_roles=["librarian", "data_steward", "content_steward"],
    agui_schema=content_orchestration_schema
)

# Usage
result = await orchestrator.orchestrate_workflow({
    "workflow_type": "content_ingestion",
    "steps": [
        {"tool": "upload_file", "params": {...}},
        {"tool": "parse_document", "params": {...}},
        {"tool": "extract_metadata", "params": {...}},
        {"tool": "index_content", "params": {...}}
    ]
})
```

**Use Cases:**
- Pillar-level workflows (Content, Insights, Operations, Business Outcomes)
- Service coordination within dimension
- Complex multi-tool pipelines

---

### **Level 3: Orchestration Agent (Global)**

```python
# Platform Orchestrator - orchestrates across dimensions
orchestrator = GlobalOrchestratorAgent(
    agent_name="PlatformOrchestrator",
    capabilities=[
        "orchestrate_cross_pillar",
        "coordinate_dimensions",
        "manage_global_workflow"
    ],
    required_roles=["city_manager", "conductor", "all_pillars"],
    agui_schema=global_orchestration_schema
)

# Usage
result = await orchestrator.orchestrate_workflow({
    "workflow_type": "mvp_journey",
    "pillars": ["content", "insights", "operations", "business_outcomes"],
    "coordination": "sequential"
})
```

**Use Cases:**
- Cross-pillar workflows
- Journey orchestration
- Platform-level coordination

---

### **Level 4: User-Facing Agent (Dimension)**

```python
# Content Guide - guides users through content workflows
guide = DimensionLiaisonAgent(
    agent_name="ContentGuide",
    dimension="content_management",
    capabilities=[
        "guide_user_workflow",
        "translate_user_request",
        "provide_content_guidance"
    ],
    required_roles=["librarian", "data_steward", "content_steward"],
    agui_schema=content_liaison_schema
)

# Usage (chat interface)
response = await guide.converse_with_user(
    message="I want to upload a document and extract insights",
    context={"session_id": session_id, "user": user_context}
)
# Guide orchestrates the workflow AND explains it to the user
```

**Use Cases:**
- Pillar-specific user guidance
- Dimension-focused conversations
- User assistance within a realm

---

### **Level 4: User-Facing Agent (Global)**

```python
# Solution Architect - guides users across entire platform
architect = GlobalGuideAgent(
    agent_name="SolutionArchitect",
    capabilities=[
        "guide_mvp_journey",
        "coordinate_user_across_pillars",
        "provide_solution_guidance"
    ],
    required_roles=["city_manager", "conductor", "all_pillars"],
    agui_schema=solution_architect_schema
)

# Usage (chat interface)
response = await architect.converse_with_user(
    message="I want to build a coexistence roadmap for my business",
    context={"session_id": session_id, "user": user_context}
)
# Architect coordinates ALL 4 pillars AND guides the user through the journey
```

**Use Cases:**
- Solution Architect (MVP journey)
- Business outcomes guidance (cross-pillar)
- Platform-wide user assistance

---

## 🌟 FUTURE AGENTS (Agentic IDP Vision)

### **City Manager Agent** (Platform Orchestrator - NOT user-facing)

```
┌─────────────────────────────────────────────────────────────┐
│ CityManagerAgent (extends GlobalOrchestratorAgent)         │
│                                                             │
│  Orchestrates: Smart City realm (entire platform)          │
│  Manages: All Smart City services                          │
│  Coordinates: With other realm managers                     │
│  User-Facing: NO (works behind the scenes)                 │
│                                                             │
│  Enables: Agentic IDP (self-managing platform)             │
└─────────────────────────────────────────────────────────────┘
```

**Example:**
```python
city_manager = CityManagerAgent(
    agent_name="CityManager",
    capabilities=[
        "orchestrate_platform",
        "manage_services",
        "coordinate_realms",
        "optimize_resources"
    ],
    required_roles=["all_smart_city_roles"],
    agui_schema=city_manager_schema
)

# Usage (platform orchestration)
await city_manager.orchestrate_platform({
    "action": "scale_services",
    "target": "content_pillar",
    "reason": "high_load"
})
```

---

### **Solution Manager Agent** (Business User Empowerment - VERY user-facing)

```
┌─────────────────────────────────────────────────────────────┐
│ SolutionManagerAgent (extends GlobalGuideAgent)            │
│                                                             │
│  Guides: Business users to compose custom journeys         │
│  Understands: Business outcomes, platform capabilities     │
│  Recommends: Which capabilities to use                      │
│  User-Facing: YES (highly interactive)                     │
│                                                             │
│  Enables: Non-technical users to build their own solutions │
└─────────────────────────────────────────────────────────────┘
```

**Example:**
```python
solution_manager = SolutionManagerAgent(
    agent_name="SolutionManager",
    capabilities=[
        "analyze_business_outcome",
        "compose_custom_journey",
        "recommend_capabilities",
        "guide_journey_creation"
    ],
    required_roles=["city_manager", "all_pillars", "conductor"],
    agui_schema=solution_manager_schema
)

# Usage (business user chat)
response = await solution_manager.converse_with_user(
    message="I want to improve customer retention using data insights",
    context={"session_id": session_id, "user": business_user}
)
# Solution Manager analyzes the outcome, recommends capabilities,
# and guides the user to compose a custom journey
```

---

## 📋 MIXIN ARCHITECTURE (Clean Agent Bases)

### **Agent Base is TOO BIG** (1047 lines) ⚠️

Just like your service bases, use **mixin pattern**:

```
foundations/agentic_foundation/agent_sdk/mixins/
├── llm_operations_mixin.py (100 lines)
│   └─ LLM calls, governance, rate limiting
│
├── tool_usage_mixin.py (120 lines)
│   └─ MCP tool integration, tool discovery
│
├── state_management_mixin.py (90 lines)
│   └─ Agent state, context, session management
│
├── orchestration_mixin.py (130 lines)
│   └─ Tool chaining, workflow coordination
│
├── user_interactivity_mixin.py (110 lines)
│   └─ Conversation, guidance, user context
│
├── multi_tenancy_mixin.py (80 lines)
│   └─ Tenant isolation, security
│
└── agui_formatting_mixin.py (90 lines)
    └─ Structured output, AGUI schemas
```

### **Each Agent Type Composes What It Needs**

```python
# Level 1: Simple Agent (minimal mixins)
class LightweightLLMAgent(
    AgentBase,
    LLMOperationsMixin,       # ✅ LLM only
    MultiTenancyMixin,        # ✅ Security
    AGUIFormattingMixin       # ✅ Output
):
    # Total: 3 mixins (~270 lines of capabilities)
    pass

# Level 2: Tool Agent (adds tool usage)
class ToolAgent(
    AgentBase,
    LLMOperationsMixin,       # ✅ LLM
    ToolUsageMixin,           # ✅ Tools
    MultiTenancyMixin,        # ✅ Security
    AGUIFormattingMixin       # ✅ Output
):
    # Total: 4 mixins (~390 lines of capabilities)
    pass

# Level 3: Orchestration Agent (adds orchestration + state)
class OrchestrationAgent(
    AgentBase,
    LLMOperationsMixin,       # ✅ LLM
    ToolUsageMixin,           # ✅ Tools
    StateManagementMixin,     # ✅ State
    OrchestrationMixin,       # ✅ Orchestration
    MultiTenancyMixin,        # ✅ Security
    AGUIFormattingMixin       # ✅ Output
):
    # Total: 6 mixins (~610 lines of capabilities)
    pass

# Level 4: User-Facing Agent (adds user interactivity)
class UserFacingAgent(
    AgentBase,
    LLMOperationsMixin,       # ✅ LLM
    ToolUsageMixin,           # ✅ Tools
    StateManagementMixin,     # ✅ State
    OrchestrationMixin,       # ✅ Orchestration
    UserInteractivityMixin,   # ✅ User Chat
    MultiTenancyMixin,        # ✅ Security
    AGUIFormattingMixin       # ✅ Output
):
    # Total: 7 mixins (ALL capabilities, ~720 lines)
    pass
```

**Benefits:**
- ✅ Each mixin under 350 lines
- ✅ Composable (agents pick what they need)
- ✅ Testable independently
- ✅ Clear capability boundaries

---

## ✅ KEY TAKEAWAYS

### **1. Your Taxonomy is Already Excellent ✅**

Your 4-level mental model maps PERFECTLY to your current implementation:
- Level 1: Simple (LLM-only) ✅
- Level 2: Tool-enabled (wizard agents) ✅
- Level 3: Orchestration (pillar agents) ✅
- Level 4: User-facing (guide & liaison agents) ✅

### **2. Just Needs Formalization**

- Document the 4-level hierarchy clearly
- Create agent protocols (type safety)
- Consider "ToolAgent" name for Level 2 (clarifies intent)

### **3. Refactor Agent Base (Like Service Bases)**

- Extract mixins (7 mixins, ~720 lines)
- Create aggregator base (100 lines)
- Reduce AgentBase from 1047 → 100 lines

### **4. Future-Proof for Agentic IDP**

- City Manager Agent (extends GlobalOrchestratorAgent) ✅ Ready
- Solution Manager Agent (extends GlobalGuideAgent) ✅ Ready
- Scales to "a LOT more agents" ✅ Ready

---

## 🎯 RECOMMENDATION

**You're in GREAT shape!** Just needs:
1. Formalize taxonomy (document the 4 levels)
2. Refactor AgentBase using mixins
3. Create agent protocols
4. You're ready for Agentic IDP vision!



