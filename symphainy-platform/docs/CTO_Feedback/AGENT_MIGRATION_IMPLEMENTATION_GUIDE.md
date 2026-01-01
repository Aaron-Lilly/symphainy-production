# 🤖 AGENT MIGRATION - COMPLETE IMPLEMENTATION GUIDE

**Date:** November 4, 2024  
**Scope:** Full agent migration + MVP integration  
**Status:** 🚀 **READY TO EXECUTE**

---

## 🎯 OBJECTIVE

**Migrate all agents AND wire them up for full MVP functionality per `MVP_Description_For_Business_and_Technical_Readiness.md`:**

1. ✅ Persistent chat panel with GuideAgent + pillar-specific liaison agents
2. ✅ Landing page with Guide Agent prompting user
3. ✅ Content pillar with ContentLiaisonAgent for file interaction
4. ✅ Insights pillar with InsightLiaisonAgent for data analysis
5. ✅ Operations pillar with OperationsLiaisonAgent for workflow generation
6. ✅ Business Outcome pillar with BusinessOutcomesLiaisonAgent for outcomes

---

## 📋 IMPLEMENTATION PHASES

### **PHASE 1: GUIDE AGENT MIGRATION** ⏱️ 2 hours

**Status:** ✅ Directory created, needs code updates

**What's Done:**
- ✅ Created `/backend/business_enablement/agents/guide_agent/`
- ✅ Copied all files from `roles/guide_agent/`

**What's Needed:**

#### **1.1 Update Guide Agent Service** (`guide_agent_service.py`)

**Line 110-117 - Update required_roles:**
```python
# OLD:
required_roles=[
    "business_orchestrator",
    "delivery_manager",
    "content_pillar",          # ❌ OLD
    "insights_pillar",          # ❌ OLD
    "operations_pillar",        # ❌ OLD
    "business_outcomes_pillar"  # ❌ OLD
]

# NEW:
required_roles=[
    "business_orchestrator",
    "delivery_manager",
    "ContentAnalysisOrchestrator",        # ✅ NEW
    "InsightsOrchestrator",                # ✅ NEW
    "OperationsOrchestrator",              # ✅ NEW
    "BusinessOutcomesOrchestrator"         # ✅ NEW
]
```

#### **1.2 Add Orchestrator Discovery Method**

Add after line 186:
```python
async def _discover_orchestrators(self):
    """Discover MVP orchestrators via Curator."""
    try:
        curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
        
        if curator:
            try:
                self.content_orchestrator = await curator.get_service("ContentAnalysisOrchestrator")
                self.logger.info("✅ Discovered ContentAnalysisOrchestrator")
            except Exception:
                self.logger.warning("⚠️ ContentAnalysisOrchestrator not available")
            
            try:
                self.insights_orchestrator = await curator.get_service("InsightsOrchestrator")
                self.logger.info("✅ Discovered InsightsOrchestrator")
            except Exception:
                self.logger.warning("⚠️ InsightsOrchestrator not available")
            
            try:
                self.operations_orchestrator = await curator.get_service("OperationsOrchestrator")
                self.logger.info("✅ Discovered OperationsOrchestrator")
            except Exception:
                self.logger.warning("⚠️ OperationsOrchestrator not available")
            
            try:
                self.business_outcomes_orchestrator = await curator.get_service("BusinessOutcomesOrchestrator")
                self.logger.info("✅ Discovered BusinessOutcomesOrchestrator")
            except Exception:
                self.logger.warning("⚠️ BusinessOutcomesOrchestrator not available")
            
            self.logger.info("✅ All orchestrators discovered")
    
    except Exception as e:
        self.logger.error(f"❌ Orchestrator discovery failed: {e}")
```

#### **1.3 Update initialize() Method**

Update line 157-186 to call discovery:
```python
async def initialize(self) -> Dict[str, Any]:
    """Initialize the Guide Agent Service."""
    try:
        self.logger.info(f"🚀 Initializing {self.agent_name}...")
        
        # Initialize base class
        base_result = await super().initialize()
        if not base_result.get("success"):
            return base_result
        
        # Discover MVP orchestrators ⬅️ ADD THIS
        await self._discover_orchestrators()
        
        # Initialize micro-modules
        await self.intent_analyzer.initialize()
        await self.conversation_manager.initialize()
        await self.user_profiler.initialize()
        await self.guidance_engine.initialize()
        await self.pillar_router.initialize()
        
        # Initialize MCP server
        await self.mcp_server.initialize()
        
        # Initialize pillar liaison agents
        await self._initialize_pillar_liaison_agents()
        
        self.logger.info(f"✅ {self.agent_name} initialized successfully")
        
        return {"success": True, "message": f"{self.agent_name} initialized successfully"}
        
    except Exception as e:
        self.logger.error(f"❌ Failed to initialize {self.agent_name}: {e}")
        return {"success": False, "error": str(e)}
```

#### **1.4 Update Pillar Router Module** (`micro_modules/pillar_router.py`)

Update pillar routing to use new orchestrator names:
```python
# Find method that routes to pillars and update:
PILLAR_MAPPING = {
    "content": "content_orchestrator",        # Maps to ContentAnalysisOrchestrator
    "insights": "insights_orchestrator",      # Maps to InsightsOrchestrator
    "operations": "operations_orchestrator",  # Maps to OperationsOrchestrator
    "business_outcomes": "business_outcomes_orchestrator"  # Maps to BusinessOutcomesOrchestrator
}
```

---

### **PHASE 2: CONTENT LIAISON AGENT** ⏱️ 1 hour

**Location:** `business_orchestrator/use_cases/mvp/content_analysis_orchestrator/agents/`

#### **2.1 Create Directory & Copy Agent**
```bash
mkdir -p backend/business_enablement/business_orchestrator/use_cases/mvp/content_analysis_orchestrator/agents
cp backend/business_enablement/pillars/content_pillar/agents/content_liaison_agent.py \
   backend/business_enablement/business_orchestrator/use_cases/mvp/content_analysis_orchestrator/agents/
cp backend/business_enablement/pillars/content_pillar/agents/content_processing_agent.py \
   backend/business_enablement/business_orchestrator/use_cases/mvp/content_analysis_orchestrator/agents/
```

#### **2.2 Update Imports in content_liaison_agent.py**
```python
# OLD:
from ....protocols.business_liaison_agent_protocol import BusinessLiaisonAgentBase

# NEW:
from backend.business_enablement.protocols.business_liaison_agent_protocol import BusinessLiaisonAgentBase

# OR use relative if protocols stay in business_enablement:
from ../../../../protocols.business_liaison_agent_protocol import BusinessLiaisonAgentBase
```

#### **2.3 Add Orchestrator Discovery**
```python
async def initialize(self):
    """Initialize Content Liaison Agent."""
    # Discover orchestrator via Curator
    curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
    if curator:
        self.content_orchestrator = await curator.get_service("ContentAnalysisOrchestrator")
    
    # Rest of initialization...
```

#### **2.4 Integrate with Content Analysis Orchestrator**

Update `content_analysis_orchestrator.py`:
```python
class ContentAnalysisOrchestrator(RealmServiceBase):
    
    def __init__(self, service_name, realm_name, platform_gateway, di_container):
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Agents
        self.liaison_agent = None
        self.processing_agent = None
    
    async def initialize(self):
        await super().initialize()
        
        # Initialize agents
        from .agents.content_liaison_agent import ContentLiaisonAgent
        from .agents.content_processing_agent import ContentProcessingAgent
        
        self.liaison_agent = ContentLiaisonAgent(di_container=self.di_container)
        await self.liaison_agent.initialize()
        
        self.processing_agent = ContentProcessingAgent(di_container=self.di_container)
        await self.processing_agent.initialize()
        
        self.logger.info("✅ Content agents initialized")
        
        # Register agent capabilities with MCP server
        await self._register_agents_with_mcp()
    
    async def _register_agents_with_mcp(self):
        """Register agent capabilities with MCP server."""
        if hasattr(self, 'mcp_server') and self.mcp_server:
            # Register liaison agent chat as MCP tool
            self.mcp_server.register_tool(
                "chat_with_content_liaison",
                self._chat_with_liaison
            )
    
    async def _chat_with_liaison(self, message: str, conversation_id: str, user_context):
        """Chat with Content Liaison Agent (MCP tool)."""
        return await self.liaison_agent.process_user_query(
            query=message,
            conversation_id=conversation_id,
            user_context=user_context
        )
    
    # Add method to use agent output in orchestrator workflow
    async def analyze_content_with_agent(self, content_data, user_context):
        """Use processing agent for content analysis."""
        agent_analysis = await self.processing_agent.analyze_content(
            content_data=content_data,
            user_context=user_context
        )
        
        # Combine agent output with orchestrator workflow
        orchestrator_result = await self.analyze_content(content_data, user_context)
        
        return {
            "orchestrator_analysis": orchestrator_result,
            "agent_insights": agent_analysis,
            "combined": self._merge_agent_orchestrator_results(orchestrator_result, agent_analysis)
        }
```

---

### **PHASE 3: INSIGHTS LIAISON AGENT** ⏱️ 1 hour

**Same pattern as Content Liaison Agent:**

```bash
mkdir -p backend/business_enablement/business_orchestrator/use_cases/mvp/insights_orchestrator/agents
cp backend/business_enablement/pillars/insights_pillar/agents/insights_liaison_agent.py \
   backend/business_enablement/business_orchestrator/use_cases/mvp/insights_orchestrator/agents/
cp backend/business_enablement/pillars/insights_pillar/agents/insights_analysis_agent.py \
   backend/business_enablement/business_orchestrator/use_cases/mvp/insights_orchestrator/agents/
```

Update `insights_orchestrator.py` with same agent integration pattern.

---

### **PHASE 4: OPERATIONS LIAISON AGENT** ⏱️ 1 hour

```bash
mkdir -p backend/business_enablement/business_orchestrator/use_cases/mvp/operations_orchestrator/agents
cp backend/business_enablement/pillars/operations_pillar/agents/operations_liaison_agent.py \
   backend/business_enablement/business_orchestrator/use_cases/mvp/operations_orchestrator/agents/
cp backend/business_enablement/pillars/operations_pillar/agents/operations_specialist_agent.py \
   backend/business_enablement/business_orchestrator/use_cases/mvp/operations_orchestrator/agents/
```

Update `operations_orchestrator.py` with same pattern.

---

### **PHASE 5: BUSINESS OUTCOMES LIAISON AGENT** ⏱️ 1 hour

```bash
mkdir -p backend/business_enablement/business_orchestrator/use_cases/mvp/business_outcomes_orchestrator/agents
cp backend/business_enablement/pillars/business_outcomes_pillar/agents/business_outcomes_liaison_agent.py \
   backend/business_enablement/business_orchestrator/use_cases/mvp/business_outcomes_orchestrator/agents/
cp backend/business_enablement/pillars/business_outcomes_pillar/agents/business_outcomes_specialist_agent.py \
   backend/business_enablement/business_orchestrator/use_cases/mvp/business_outcomes_orchestrator/agents/
```

Update `business_outcomes_orchestrator.py` with same pattern.

---

### **PHASE 6: EXPERIENCE REALM CHAT SERVICE** ⏱️ 3 hours

**CRITICAL FOR MVP: This connects the frontend chat panel to Guide Agent and Liaison Agents!**

#### **6.1 Create Chat Service**

**Location:** `backend/experience/services/chat_service/chat_service.py`

```python
#!/usr/bin/env python3
"""
Chat Service for Experience Realm

WHAT: Provides chat interface for Guide Agent and Liaison Agents
HOW: Routes chat messages to appropriate agents, maintains conversation state

This service connects the frontend chat panel to the backend agents,
enabling the conversational MVP experience.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class ChatService(RealmServiceBase):
    """
    Chat Service for Experience realm.
    
    Provides persistent chat panel functionality for Guide Agent
    and pillar-specific liaison agents.
    
    Implements MVP requirement: "Persistent UI elements include a navbar 
    across the top for each of the four pillars and a chat panel along 
    the right hand side where the GuideAgent and pillar specific liaison agents live."
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Chat Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be discovered via Curator
        self.guide_agent = None
        self.content_liaison = None
        self.insights_liaison = None
        self.operations_liaison = None
        self.business_outcomes_liaison = None
        
        # Active conversations
        self.conversations: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> bool:
        """Initialize Chat Service."""
        await super().initialize()
        
        try:
            # Discover Guide Agent
            await self._discover_guide_agent()
            
            # Discover Liaison Agents via orchestrators
            await self._discover_liaison_agents()
            
            # Register with Curator
            await self.register_with_curator(
                capabilities=["chat", "agent_routing", "conversation_management"],
                soa_apis=[
                    "send_message_to_guide", "send_message_to_liaison",
                    "get_conversation_history", "create_conversation",
                    "get_active_agent", "switch_agent"
                ],
                mcp_tools=[],
                additional_metadata={
                    "layer": "experience",
                    "provides": "chat_interface"
                }
            )
            
            self.logger.info("✅ Chat Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Chat Service initialization failed: {e}")
            return False
    
    async def _discover_guide_agent(self):
        """Discover Guide Agent."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                self.guide_agent = await curator.get_service("GuideAgent")
                self.logger.info("✅ Discovered GuideAgent")
        except Exception as e:
            self.logger.warning(f"⚠️ GuideAgent not available: {e}")
    
    async def _discover_liaison_agents(self):
        """Discover liaison agents via orchestrators."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                # Get orchestrators
                content_orch = await curator.get_service("ContentAnalysisOrchestrator")
                self.content_liaison = content_orch.liaison_agent if hasattr(content_orch, 'liaison_agent') else None
                
                insights_orch = await curator.get_service("InsightsOrchestrator")
                self.insights_liaison = insights_orch.liaison_agent if hasattr(insights_orch, 'liaison_agent') else None
                
                operations_orch = await curator.get_service("OperationsOrchestrator")
                self.operations_liaison = operations_orch.liaison_agent if hasattr(operations_orch, 'liaison_agent') else None
                
                business_orch = await curator.get_service("BusinessOutcomesOrchestrator")
                self.business_outcomes_liaison = business_orch.liaison_agent if hasattr(business_orch, 'liaison_agent') else None
                
                self.logger.info("✅ Discovered liaison agents")
        except Exception as e:
            self.logger.warning(f"⚠️ Some liaison agents not available: {e}")
    
    # ========================================================================
    # SOA APIs
    # ========================================================================
    
    async def send_message_to_guide(
        self,
        message: str,
        conversation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Send message to Guide Agent (SOA API).
        
        Implements: Landing page Guide Agent interaction
        """
        try:
            if not self.guide_agent:
                return {
                    "success": False,
                    "error": "Guide Agent not available"
                }
            
            # Track conversation
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "active_agent": "guide",
                    "created_at": datetime.utcnow().isoformat(),
                    "messages": []
                }
            
            # Send to Guide Agent
            response = await self.guide_agent.provide_guidance({
                "query": message,
                "conversation_id": conversation_id,
                "user_id": user_id
            })
            
            # Track messages
            self.conversations[conversation_id]["messages"].append({
                "from": "user",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.conversations[conversation_id]["messages"].append({
                "from": "guide_agent",
                "message": response.get("guidance", ""),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "response": response,
                "conversation_id": conversation_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Send message to guide failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_message_to_liaison(
        self,
        message: str,
        pillar: str,
        conversation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Send message to pillar-specific liaison agent (SOA API).
        
        Implements: Pillar-specific liaison chat
        """
        try:
            # Get appropriate liaison agent
            liaison_agents = {
                "content": self.content_liaison,
                "insights": self.insights_liaison,
                "operations": self.operations_liaison,
                "business_outcomes": self.business_outcomes_liaison
            }
            
            liaison = liaison_agents.get(pillar)
            if not liaison:
                return {
                    "success": False,
                    "error": f"Liaison agent for {pillar} not available"
                }
            
            # Track conversation
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "active_agent": f"{pillar}_liaison",
                    "created_at": datetime.utcnow().isoformat(),
                    "messages": []
                }
            
            # Send to liaison agent
            response = await liaison.process_user_query(
                query=message,
                conversation_id=conversation_id,
                user_context={"user_id": user_id}
            )
            
            # Track messages
            self.conversations[conversation_id]["messages"].append({
                "from": "user",
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.conversations[conversation_id]["messages"].append({
                "from": f"{pillar}_liaison",
                "message": response.get("response", ""),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "response": response,
                "conversation_id": conversation_id,
                "pillar": pillar
            }
            
        except Exception as e:
            self.logger.error(f"❌ Send message to liaison failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_conversation_history(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Get conversation history (SOA API)."""
        if conversation_id in self.conversations:
            return {
                "success": True,
                "conversation": self.conversations[conversation_id]
            }
        return {
            "success": False,
            "error": "Conversation not found"
        }
    
    async def create_conversation(
        self,
        user_id: str,
        initial_agent: str = "guide"
    ) -> Dict[str, Any]:
        """Create new conversation (SOA API)."""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "active_agent": initial_agent,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
        
        return {
            "success": True,
            "conversation_id": conversation_id
        }
    
    async def switch_agent(
        self,
        conversation_id: str,
        new_agent: str
    ) -> Dict[str, Any]:
        """Switch active agent in conversation (SOA API)."""
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["active_agent"] = new_agent
            return {
                "success": True,
                "active_agent": new_agent
            }
        return {
            "success": False,
            "error": "Conversation not found"
        }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "guide_agent_available": self.guide_agent is not None,
            "liaison_agents_available": {
                "content": self.content_liaison is not None,
                "insights": self.insights_liaison is not None,
                "operations": self.operations_liaison is not None,
                "business_outcomes": self.business_outcomes_liaison is not None
            },
            "active_conversations": len(self.conversations),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "experience_service",
            "realm": "experience",
            "layer": "chat_interface",
            "capabilities": ["chat", "agent_routing", "conversation_management"],
            "soa_apis": [
                "send_message_to_guide", "send_message_to_liaison",
                "get_conversation_history", "create_conversation",
                "get_active_agent", "switch_agent"
            ],
            "mcp_tools": []
        }
```

#### **6.2 Update Frontend Gateway to Expose Chat API**

Update `frontend_gateway_service.py` to add chat routes:
```python
# Add to FrontendGatewayService:

async def _discover_experience_services(self):
    # ... existing code ...
    
    try:
        self.chat_service = await curator.get_service("ChatService")
        self.logger.info("✅ Discovered ChatService")
    except Exception:
        self.logger.warning("⚠️ ChatService not available")

# Add chat endpoints:

async def handle_chat_message_guide(self, request_data):
    """Handle chat message to Guide Agent (REST API endpoint)."""
    return await self.chat_service.send_message_to_guide(
        message=request_data["message"],
        conversation_id=request_data["conversation_id"],
        user_id=request_data["user_id"]
    )

async def handle_chat_message_liaison(self, request_data):
    """Handle chat message to pillar liaison (REST API endpoint)."""
    return await self.chat_service.send_message_to_liaison(
        message=request_data["message"],
        pillar=request_data["pillar"],  # "content", "insights", "operations", "business_outcomes"
        conversation_id=request_data["conversation_id"],
        user_id=request_data["user_id"]
    )

# Expose REST endpoints:
# POST /api/chat/guide
# POST /api/chat/liaison
# GET /api/chat/history/{conversation_id}
# POST /api/chat/create
```

---

## 📋 MVP REQUIREMENTS CHECKLIST

### **Landing Page** ✅
- [ ] Guide Agent welcomes user
- [ ] Guide Agent prompts user about goals
- [ ] Guide Agent suggests specific data to share
- [ ] Guide Agent directs user to content pillar
- **Implementation:** `ChatService.send_message_to_guide()` + Frontend Gateway `/api/chat/guide`

### **Content Pillar** ✅
- [ ] Dashboard view of available files
- [ ] File uploader (multiple file types)
- [ ] Parsing function (parquet, JSON)
- [ ] Data preview
- [ ] ContentLiaisonAgent for file interaction
- **Implementation:** Content Analysis Orchestrator + Content Liaison Agent

### **Insights Pillar** ✅
- [ ] File selection prompt
- [ ] Business analysis text
- [ ] Visual/tabular data representation
- [ ] InsightLiaisonAgent for data navigation
- [ ] Double-click analysis
- [ ] Insights summary with recommendations
- **Implementation:** Insights Orchestrator + Insights Liaison Agent

### **Operations Pillar** ✅
- [ ] 3 cards: select file / upload / generate from scratch
- [ ] Visual elements (workflow + SOP)
- [ ] AI generation for missing element
- [ ] Coexistence blueprint
- [ ] OperationsLiaisonAgent for custom development
- **Implementation:** Operations Orchestrator + Operations Liaison Agent

### **Business Outcome Pillar** ✅
- [ ] Display summaries from other pillars
- [ ] BusinessOutcomesLiaisonAgent prompts for context
- [ ] Final analysis (roadmap + POC proposal)
- **Implementation:** Business Outcomes Orchestrator + Business Outcomes Liaison Agent

### **Persistent Chat Panel** ✅
- [ ] Guide Agent always available
- [ ] Pillar-specific liaison agents
- [ ] Conversation persistence
- [ ] Agent switching
- **Implementation:** Chat Service + Frontend Gateway chat routes

---

## ⏱️ TOTAL TIMELINE

| Phase | Task | Time |
|-------|------|------|
| 1 | Guide Agent Migration | 2 hours |
| 2 | Content Liaison Agent | 1 hour |
| 3 | Insights Liaison Agent | 1 hour |
| 4 | Operations Liaison Agent | 1 hour |
| 5 | Business Outcomes Liaison Agent | 1 hour |
| 6 | Chat Service (Experience) | 3 hours |
| 7 | Specialist Agents | 2 hours |
| 8 | Wire Up Agent Outputs | 2 hours |
| 9 | Integration Testing | 3 hours |
| **TOTAL** | | **16 hours** |

---

## 🚀 EXECUTION STEPS

**For each agent migration:**
1. Create `agents/` directory in orchestrator
2. Copy agent files from old location
3. Update imports
4. Add orchestrator discovery
5. Integrate with orchestrator's `initialize()`
6. Register agent capabilities with MCP server
7. Create method to use agent output in workflows
8. Test agent functionality

**For Chat Service:**
1. Create `ChatService` in Experience realm
2. Implement agent discovery
3. Implement SOA APIs for messaging
4. Update Frontend Gateway to expose chat routes
5. Test chat flow end-to-end

---

## 🎯 SUCCESS CRITERIA

**Agent Migration Complete When:**
- ✅ All 13+ agents in new structure
- ✅ Guide Agent discovers orchestrators via Curator
- ✅ All liaison agents integrated with orchestrators
- ✅ Chat Service connects frontend to agents
- ✅ Agent outputs wired into orchestrator workflows
- ✅ MVP requirements fully met

**Testing Checklist:**
- [ ] Guide Agent can route to all orchestrators
- [ ] Each liaison agent can process queries
- [ ] Chat Service can send messages to all agents
- [ ] Frontend Gateway exposes chat API
- [ ] Agent outputs flow into orchestrator results
- [ ] Conversation history persists
- [ ] Agent switching works

---

## 📄 FILES TO UPDATE

### **Guide Agent:**
- `agents/guide_agent/guide_agent_service.py`
- `agents/guide_agent/micro_modules/pillar_router.py`

### **Each Orchestrator:**
- `content_analysis_orchestrator.py` (integrate liaison + specialist)
- `insights_orchestrator.py` (integrate liaison + specialist)
- `operations_orchestrator.py` (integrate liaison + specialist)
- `business_outcomes_orchestrator.py` (integrate liaison + specialist)

### **Experience Realm:**
- `experience/services/chat_service/chat_service.py` (NEW)
- `experience/services/frontend_gateway_service/frontend_gateway_service.py` (UPDATE)

### **Agent Files:**
- 4 liaison agents (copy + update imports)
- 6+ specialist agents (copy + update imports)

---

## 💡 KEY PATTERNS

### **Pattern 1: Agent Discovery**
```python
# All agents discover via Curator
curator = self.di_container.curator
self.orchestrator = await curator.get_service("OrchestratorName")
```

### **Pattern 2: Orchestrator-Agent Integration**
```python
# Orchestrators own and initialize agents
async def initialize(self):
    from .agents.liaison_agent import LiaisonAgent
    self.liaison_agent = LiaisonAgent(di_container=self.di_container)
    await self.liaison_agent.initialize()
```

### **Pattern 3: Agent Output in Workflow**
```python
# Combine agent insights with orchestrator results
agent_result = await self.liaison_agent.process_query(...)
orchestrator_result = await self.orchestrate_workflow(...)
return self._merge_results(agent_result, orchestrator_result)
```

### **Pattern 4: Chat Routing**
```python
# Chat Service routes to appropriate agent
if agent_type == "guide":
    return await self.guide_agent.provide_guidance(...)
else:
    liaison = self.liaison_agents[pillar]
    return await liaison.process_user_query(...)
```

---

## 🎉 BOTTOM LINE

**This implementation guide provides:**
- ✅ Complete agent migration strategy
- ✅ Full MVP integration (chat panel, agents, orchestrators)
- ✅ Code patterns for each phase
- ✅ Detailed implementation steps
- ✅ Success criteria and testing checklist

**Ready to execute!** Follow this guide phase by phase to complete the agent migration and achieve full MVP functionality. 🚀









