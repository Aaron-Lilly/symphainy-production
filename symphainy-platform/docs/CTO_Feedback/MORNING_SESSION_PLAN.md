# Morning Session: Guide & Liaison Agents
## SDK-First, Domain-Configurable Approach

**Date:** November 6, 2025  
**Goal:** Build extensible Guide and Liaison agents using SDK patterns

---

## 📋 **LAST NIGHT'S PROGRESS**

### **✅ What We Completed:**
1. ✅ Eliminated interface pattern (protocols + bases)
2. ✅ Fixed Guide Agent abstract method implementation
3. ✅ Created Chat Service for frontend integration
4. ✅ Completed 4 Liaison Agents integration with orchestrators
5. ✅ Updated 4 Specialist Agents
6. ✅ Created Phase 1 unit tests
7. ✅ Comprehensive production readiness review
8. ✅ Discovered architectural crisis (all 7 agents broken)
9. ✅ Planned SDK-first refactoring approach

### **🚨 What We Discovered:**
- **ALL 7 agents have signature mismatch** with AgentBase
- **Service Locator anti-pattern** (old `di_container` pattern)
- **Need SDK-first rebuild** (faster than fixing broken code)

---

## 🎯 **THIS MORNING'S STRATEGY**

### **The Strategic Pattern: Domain-Configurable Agents**

**Key Principles:**
1. **Guide Agent = Cross-Domain Navigator** (one per solution)
2. **Liaison Agent = Domain-Specific Conversational Interface** (one per domain)
3. **Both use SDK base classes** (GlobalGuideAgent, DimensionLiaisonAgent)
4. **Configuration-driven** (works for MVP, Data Mash, APG, etc.)

### **Why This Approach Wins:**

| Aspect | Old (Pillar-Aligned) | New (Domain-Configurable) |
|--------|---------------------|---------------------------|
| **Reusability** | MVP only | MVP + Data Mash + APG |
| **Extensibility** | Hardcoded pillars | Infinite domains |
| **Maintainability** | Duplicate code | Single agent type |
| **Time to Build** | 3+ hours | 2 hours |
| **Technical Debt** | High | Zero |

---

## 🏗️ **IMPLEMENTATION PLAN**

### **Phase 1: Build Platform-Level Agent Capabilities** (90 min)

#### **1. GuideCrossDomainAgent** (45 min)
**What:** Cross-domain navigation agent
**Extends:** SDK's `GlobalGuideAgent`
**Capabilities:**
- Cross-domain intent analysis
- Dynamic liaison agent discovery
- User journey tracking
- Holistic guidance

**Pattern:**
```python
class GuideCrossDomainAgent(GlobalGuideAgent):
    """
    Platform-level Guide Agent for cross-domain navigation.
    
    CONFIGURABLE for any solution (MVP, Data Mash, APG).
    NOT solution-specific!
    """
    
    def __init__(self, solution_config, foundation_services, ...):
        super().__init__(
            agent_name="GuideCrossDomainAgent",
            capabilities=["intent_analysis", "routing", "guidance"],
            required_roles=[],  # Discovers liaison agents dynamically
            foundation_services=foundation_services,
            ...
        )
        self.solution_config = solution_config
        self.liaison_agents = {}
    
    async def configure_for_solution(self, solution_type: str):
        """Discover and configure liaison agents for solution."""
        if solution_type == "mvp":
            domains = ["content_management", "insights_analysis", 
                      "operations_management", "business_outcomes"]
        elif solution_type == "data_mash":
            domains = ["metadata_extraction", "schema_alignment", 
                      "virtual_composition"]
        # ... etc
        
        await self._discover_liaison_agents(domains)
```

#### **2. LiaisonDomainAgent** (45 min)
**What:** Domain-specific conversational interface
**Extends:** SDK's `DimensionLiaisonAgent`
**Capabilities:**
- Domain-specific dialogue
- Intent understanding
- Orchestrator coordination
- MCP tool usage

**Pattern:**
```python
class LiaisonDomainAgent(DimensionLiaisonAgent):
    """
    Platform-level Liaison Agent for domain-specific conversation.
    
    CONFIGURABLE for any domain.
    NOT pillar-specific!
    """
    
    def __init__(self, domain_name, domain_config, foundation_services, ...):
        super().__init__(
            agent_name=f"{domain_name}LiaisonAgent",
            capabilities=domain_config['capabilities'],
            required_roles=[domain_config['orchestrator']],
            dimension=domain_name,
            foundation_services=foundation_services,
            ...
        )
        self.domain_name = domain_name
        self.domain_config = domain_config
        self.orchestrator = None
    
    async def handle_user_request(self, request):
        """Handle domain-specific user request with AI reasoning."""
        # 1. Analyze intent (SDK provides!)
        intent = await self.analyze_intent(request)
        
        # 2. Direct handling or orchestrator delegation?
        if self._can_handle_directly(intent):
            return await self.execute_with_mcp_tools(intent)
        else:
            return await self.orchestrator.handle_request(intent)
```

---

### **Phase 2: Configure for MVP** (30 min)

#### **3. MVP Guide Configuration** (10 min)
```python
# backend/business_enablement/agents/mvp_guide_agent.py

from .guide_cross_domain_agent import GuideCrossDomainAgent

class MVPGuideAgent:
    """Factory for MVP Guide Agent."""
    
    @classmethod
    async def create(cls, foundation_services, agentic_foundation, ...):
        """Create Guide Agent configured for MVP."""
        guide = GuideCrossDomainAgent(
            solution_config="mvp",
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            ...
        )
        
        await guide.configure_for_solution("mvp")
        return guide
```

#### **4. MVP Liaison Configurations** (20 min)
```python
# backend/business_enablement/agents/mvp_liaison_agents.py

from .liaison_domain_agent import LiaisonDomainAgent

# MVP Domain Configs
MVP_DOMAINS = {
    "content_management": {
        'capabilities': ["file_upload", "parsing", "validation"],
        'orchestrator': "ContentAnalysisOrchestrator"
    },
    "insights_analysis": {
        'capabilities': ["data_analysis", "visualization", "reporting"],
        'orchestrator': "InsightsOrchestrator"
    },
    "operations_management": {
        'capabilities': ["workflow_management", "sop_generation", "compliance"],
        'orchestrator': "OperationsOrchestrator"
    },
    "business_outcomes": {
        'capabilities': ["metrics", "forecasting", "recommendations"],
        'orchestrator': "BusinessOutcomesOrchestrator"
    }
}

class MVPLiaisonAgents:
    """Factory for MVP Liaison Agents."""
    
    @classmethod
    async def create_all(cls, foundation_services, agentic_foundation, ...):
        """Create all 4 MVP liaison agents."""
        agents = {}
        
        for domain_name, config in MVP_DOMAINS.items():
            agent = LiaisonDomainAgent(
                domain_name=domain_name,
                domain_config=config,
                foundation_services=foundation_services,
                agentic_foundation=agentic_foundation,
                ...
            )
            await agent.initialize()
            agents[domain_name] = agent
        
        return agents
```

---

## 📂 **FILE STRUCTURE**

### **New Agent Directory:**
```
backend/business_enablement/agents/
├── __init__.py                        # Exports
├── archive/                           # Old agents
│   ├── guide_agent_old/              # 987 lines of broken code
│   └── liaison_agents_old/           # 1600 lines of broken code
├── guide_cross_domain_agent.py       # NEW! (250 lines)
├── liaison_domain_agent.py           # NEW! (200 lines)
├── mvp_guide_agent.py                # NEW! (50 lines - MVP config)
└── mvp_liaison_agents.py             # NEW! (80 lines - MVP configs)
```

**Total New Code:** ~580 lines (vs. 2587 lines of broken old code!)

---

## 🎯 **SUCCESS CRITERIA**

### **For Guide Agent:**
- ✅ Extends `GlobalGuideAgent` from SDK
- ✅ Configurable for multiple solutions (MVP, Data Mash, APG)
- ✅ Dynamic liaison agent discovery
- ✅ Cross-domain intent routing
- ✅ User journey tracking
- ✅ Holistic guidance capabilities

### **For Liaison Agent:**
- ✅ Extends `DimensionLiaisonAgent` from SDK
- ✅ Configurable for multiple domains (any domain!)
- ✅ Domain-specific dialogue
- ✅ Orchestrator coordination
- ✅ MCP tool usage for autonomous reasoning
- ✅ Intent analysis and handling

### **For MVP Configuration:**
- ✅ 1 Guide Agent configured for MVP user journey
- ✅ 4 Liaison Agents configured for MVP domains
- ✅ Works exactly like pillar-specific agents
- ✅ But architecture supports extension!

---

## 🔄 **USER FLOW EXAMPLES**

### **Example 1: MVP Content Upload**
```
User: "I want to upload a document"
    ↓
MVPGuideAgent (analyzes intent)
    → "This is content_management domain"
    → Routes to ContentLiaisonAgent
        ↓
ContentLiaisonAgent
    → Understands file upload request
    → Uses MCP tools OR delegates to ContentAnalysisOrchestrator
    → Returns: "I'll help you upload your document..."
```

### **Example 2: Data Mash Schema Alignment (Future!)**
```
User: "I need to align schemas from two data sources"
    ↓
DataMashGuideAgent (SAME TYPE, different config!)
    → "This is schema_alignment domain"
    → Routes to SchemaAlignmentLiaisonAgent (SAME TYPE, different domain!)
        ↓
SchemaAlignmentLiaisonAgent
    → Understands schema harmonization
    → Uses MCP tools OR delegates to SchemaAlignmentOrchestrator
    → Returns: "I'll analyze your schemas..."
```

**SAME PATTERN, DIFFERENT DOMAINS!**

---

## 💡 **KEY ARCHITECTURAL INSIGHTS**

### **1. Separation of Concerns**
- **Platform Layer:** Define agent capabilities (`GuideCrossDomainAgent`, `LiaisonDomainAgent`)
- **Solution Layer:** Configure for use cases (MVP, Data Mash, APG)

### **2. Configuration Over Coding**
```python
# NOT this (hardcoded):
class ContentLiaisonAgent(DimensionLiaisonAgent):
    # Hardcoded to content pillar
    
# BUT this (configurable):
content_liaison = LiaisonDomainAgent(
    domain_name="content_management",
    domain_config=MVP_CONTENT_CONFIG
)
```

### **3. Infinite Extensibility**
- **MVP:** content, insights, operations, business_outcomes
- **Data Mash:** metadata, schema, composition
- **APG:** test_orchestration, vehicle_coordination, results_analysis
- **Future:** ANY domain you can imagine!

---

## 📊 **ESTIMATED TIME**

| Task | Time | Notes |
|------|------|-------|
| **Build GuideCrossDomainAgent** | 45 min | Extends GlobalGuideAgent |
| **Build LiaisonDomainAgent** | 45 min | Extends DimensionLiaisonAgent |
| **MVP Guide Configuration** | 10 min | Factory + config |
| **MVP Liaison Configurations** | 20 min | 4 domain configs |
| **Archive Old Agents** | 5 min | Move broken code |
| **Update Imports** | 10 min | Fix imports across codebase |
| **Unit Tests** | 15 min | Test new agents |
| **Integration with Chat Service** | 10 min | Wire up for MVP |
| **TOTAL** | **2.5 hours** | **Clean, extensible agents!** |

---

## 🚀 **NEXT STEPS AFTER COMPLETION**

1. **Specialist Agents** (1.5 hours)
   - Build `SpecialistCapabilityAgent` base
   - Map to enabling services (1:1)
   - Configure for MVP

2. **Testing** (1 hour)
   - Agent unit tests
   - Integration tests
   - E2E smoke tests

3. **Production** (30 min)
   - Final validation
   - E2E testing with Team B
   - Platform launch! 🎉

---

## 💬 **THE BEAUTY OF THIS APPROACH**

### **Tonight's MVP:**
- 1 Guide Agent for MVP
- 4 Liaison Agents for MVP
- Works perfectly for MVP requirements
- **But...**

### **Tomorrow's Data Mash:**
- **SAME Guide Agent type!** (just different config)
- **SAME Liaison Agent type!** (just different domains)
- **NO refactoring needed!**
- **Build in 30 minutes!**

### **Next Week's APG:**
- **SAME Guide Agent type!** (just different config)
- **SAME Liaison Agent type!** (just different domains)
- **NO refactoring needed!**
- **Build in 30 minutes!**

---

**THIS IS THE POWER OF STRATEGIC ARCHITECTURE!** 🎯

Platform built once, configured infinitely! 🚀

---

**STATUS:** 🟢 **READY TO BUILD**

**NEXT:** Build `GuideCrossDomainAgent` (45 min)







