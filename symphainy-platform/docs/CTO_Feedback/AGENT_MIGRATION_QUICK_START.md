# 🚀 AGENT MIGRATION - QUICK START

**Date:** November 4, 2024  
**Time to Complete:** 16 hours  
**Team Split:** Can divide into 3 parallel tracks

---

## 📊 WHAT WE'RE DOING

**Migrate 13+ agents from old pillar structure to new orchestrator architecture AND wire them up for full MVP functionality.**

**MVP Requirements:**
- ✅ Persistent chat panel (Guide Agent + pillar liaison agents)
- ✅ Landing page with Guide Agent
- ✅ Content/Insights/Operations/Business Outcome pillars with liaison agents
- ✅ Conversational interface throughout

---

## 🎯 3 PARALLEL TRACKS (DIVIDE & CONQUER)

### **TRACK 1: GUIDE AGENT (CRITICAL PATH)** ⏱️ 2 hours
**Owner:** Team Lead (must be done first)

**Tasks:**
1. Update `agents/guide_agent/guide_agent_service.py`:
   - Line 110-117: Change pillar names to orchestrator names
   - Add `_discover_orchestrators()` method
   - Call discovery in `initialize()`
2. Update `agents/guide_agent/micro_modules/pillar_router.py`:
   - Update PILLAR_MAPPING to use orchestrator names

**Why Critical:** Guide Agent must work before liaison agents can be tested

---

### **TRACK 2: LIAISON AGENTS** ⏱️ 4 hours
**Owner:** Developer A

**Tasks (all 4 agents follow same pattern):**

**For each pillar (Content, Insights, Operations, Business Outcomes):**
1. Create agents directory:
   ```bash
   mkdir -p backend/business_enablement/business_orchestrator/use_cases/mvp/{pillar}_orchestrator/agents
   ```
2. Copy liaison agent:
   ```bash
   cp pillars/{pillar}/agents/{pillar}_liaison_agent.py → orchestrator/agents/
   ```
3. Update imports in agent file
4. Add orchestrator discovery to agent
5. Update orchestrator to initialize agent
6. Register agent with MCP server

**Deliverable:** 4 liaison agents integrated with orchestrators

---

### **TRACK 3: CHAT SERVICE** ⏱️ 3 hours
**Owner:** Developer B

**Tasks:**
1. Create `experience/services/chat_service/chat_service.py`
   - Use code from implementation guide
   - Implements Guide Agent + Liaison Agent routing
2. Update `experience/services/frontend_gateway_service/frontend_gateway_service.py`
   - Add chat routes
   - Expose `/api/chat/guide` and `/api/chat/liaison`
3. Test chat flow end-to-end

**Deliverable:** Working chat panel backend

---

## ⏱️ TIMELINE

| Hour | Track 1 (Lead) | Track 2 (Dev A) | Track 3 (Dev B) |
|------|----------------|-----------------|-----------------|
| 1-2 | ✅ Guide Agent | ⏳ Wait | Chat Service design |
| 3-4 | Testing | Content Liaison | Chat Service impl |
| 5-6 | Support teams | Insights Liaison | Chat Service test |
| 7-8 | Integration | Operations Liaison | Frontend Gateway |
| 9-10 | Testing | Business Liaison | Testing |
| 11-12 | Specialist agents | Specialist agents | Wire outputs |
| 13-14 | Wire outputs | Wire outputs | Wire outputs |
| 15-16 | **Integration Testing (ALL TOGETHER)** | | |

---

## 📋 PHASE-BY-PHASE CHECKLIST

### **PHASE 1: GUIDE AGENT** ✅
- [ ] Update required_roles to orchestrator names
- [ ] Add _discover_orchestrators() method
- [ ] Update initialize() to call discovery
- [ ] Update pillar_router.py mappings
- [ ] Test: Guide Agent can route to orchestrators

### **PHASE 2-5: LIAISON AGENTS** (Parallel)
**For EACH agent:**
- [ ] Create agents/ directory in orchestrator
- [ ] Copy agent file from old location
- [ ] Update imports
- [ ] Add orchestrator discovery
- [ ] Update orchestrator to initialize agent
- [ ] Register with MCP server
- [ ] Test: Agent can process queries

### **PHASE 6: CHAT SERVICE**
- [ ] Create ChatService class
- [ ] Implement agent discovery
- [ ] Implement send_message_to_guide()
- [ ] Implement send_message_to_liaison()
- [ ] Implement conversation management
- [ ] Update Frontend Gateway
- [ ] Test: Chat routes work end-to-end

### **PHASE 7: SPECIALIST AGENTS**
- [ ] Copy specialist agents to orchestrator agents/
- [ ] Update imports
- [ ] Integrate with orchestrators
- [ ] Test: Specialists provide insights

### **PHASE 8: WIRE OUTPUTS**
- [ ] Add method in each orchestrator to use agent output
- [ ] Merge agent results with orchestrator results
- [ ] Test: Outputs flow correctly

### **PHASE 9: INTEGRATION TESTING**
- [ ] Test Guide Agent routing
- [ ] Test each liaison agent
- [ ] Test chat panel
- [ ] Test agent switching
- [ ] Test conversation persistence
- [ ] Verify MVP requirements met

---

## 🚨 CRITICAL DEPENDENCIES

**Must Complete in Order:**
1. ✅ Guide Agent (FIRST - blocks everything)
2. ✅ Liaison Agents (SECOND - needed for Chat Service)
3. ✅ Chat Service (THIRD - wires everything together)
4. Specialist Agents (can be parallel with 3)
5. Wire Outputs (needs 2-4 complete)
6. Integration Testing (needs everything)

**Parallel Work:**
- Track 2 (Liaison Agents) and Track 3 (Chat Service) can run in parallel AFTER Guide Agent is done
- Specialist agents can be done by any available developer

---

## 📄 KEY FILES

### **Files to Update:**
```
agents/guide_agent/guide_agent_service.py
agents/guide_agent/micro_modules/pillar_router.py

business_orchestrator/use_cases/mvp/content_analysis_orchestrator/content_analysis_orchestrator.py
business_orchestrator/use_cases/mvp/insights_orchestrator/insights_orchestrator.py
business_orchestrator/use_cases/mvp/operations_orchestrator/operations_orchestrator.py
business_orchestrator/use_cases/mvp/business_outcomes_orchestrator/business_outcomes_orchestrator.py

experience/services/frontend_gateway_service/frontend_gateway_service.py
```

### **Files to Create:**
```
experience/services/chat_service/chat_service.py (NEW - 400+ lines)
experience/services/chat_service/__init__.py

business_orchestrator/use_cases/mvp/*/agents/ (4 directories)
business_orchestrator/use_cases/mvp/*/agents/*_liaison_agent.py (4 files)
business_orchestrator/use_cases/mvp/*/agents/*_specialist_agent.py (4+ files)
```

---

## 💡 CODE PATTERNS

### **Pattern 1: Orchestrator Discovery in Agent**
```python
async def initialize(self):
    curator = self.di_container.curator
    self.orchestrator = await curator.get_service("OrchestratorName")
```

### **Pattern 2: Agent Initialization in Orchestrator**
```python
async def initialize(self):
    from .agents.liaison_agent import LiaisonAgent
    self.liaison_agent = LiaisonAgent(di_container=self.di_container)
    await self.liaison_agent.initialize()
```

### **Pattern 3: MCP Tool Registration**
```python
async def _register_agents_with_mcp(self):
    if hasattr(self, 'mcp_server') and self.mcp_server:
        self.mcp_server.register_tool("chat_with_liaison", self._chat_with_liaison)

async def _chat_with_liaison(self, message, conversation_id, user_context):
    return await self.liaison_agent.process_user_query(
        query=message,
        conversation_id=conversation_id,
        user_context=user_context
    )
```

---

## 🎯 SUCCESS CRITERIA

**Agent Migration Complete When:**
- ✅ Guide Agent routes to all orchestrators
- ✅ All 4 liaison agents work in their orchestrators
- ✅ Chat Service connects frontend to agents
- ✅ Chat panel backend routes messages correctly
- ✅ Agent outputs integrated with orchestrator workflows
- ✅ MVP requirements fully met

**Test Commands:**
```python
# Test Guide Agent
guide_agent = await curator.get_service("GuideAgent")
result = await guide_agent.provide_guidance({"query": "Help me get started"})

# Test Liaison Agent
content_orch = await curator.get_service("ContentAnalysisOrchestrator")
result = await content_orch.liaison_agent.process_user_query("How do I upload files?")

# Test Chat Service
chat_service = await curator.get_service("ChatService")
result = await chat_service.send_message_to_guide("Hello", conv_id, user_id)
result = await chat_service.send_message_to_liaison("Parse my file", "content", conv_id, user_id)
```

---

## 🚀 GET STARTED

**Step 1:** Review full implementation guide: `AGENT_MIGRATION_IMPLEMENTATION_GUIDE.md`

**Step 2:** Assign tracks to team members

**Step 3:** Start with Track 1 (Guide Agent) - MUST BE DONE FIRST

**Step 4:** Once Guide Agent done, start Tracks 2 & 3 in parallel

**Step 5:** Complete specialist agents and wire outputs

**Step 6:** Integration testing (all team together)

---

## 📞 SUPPORT

**If stuck, check:**
1. Full implementation guide (AGENT_MIGRATION_IMPLEMENTATION_GUIDE.md)
2. Agent architecture plan (AGENT_ARCHITECTURE_RECOVERY_PLAN.md)
3. Original agent files (pillars/*/agents/)

**Common Issues:**
- Import errors → Update import paths
- Curator not finding service → Check service registration
- Agent not responding → Check initialization sequence

---

## 🎉 BOTTOM LINE

**16 hours to complete agent migration and achieve full MVP conversational interface.**

**Can parallelize into 3 tracks to reduce calendar time to ~10 hours.**

**Follow the patterns, use the code templates, test incrementally, and you'll have a fully functional agentic MVP!** 🚀









