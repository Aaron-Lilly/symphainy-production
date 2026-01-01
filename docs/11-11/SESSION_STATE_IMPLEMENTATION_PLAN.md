# 🚀 Session & State Management Implementation Plan

**Date:** November 9, 2025  
**Status:** Ready for Implementation  
**Approach:** Breaking Changes - No Backward Compatibility

---

## 📋 Overview

This plan implements the architectural vision for session and state management, including **critical agentic foundation integration** for seamless demo experiences. All changes are **breaking** - we're fully aligning with the new platform architecture.

---

## 🎯 Core Architecture Changes

### New Session Structure
```python
session = {
    "session_id": str,                    # Primary identifier
    "user_id": str,                       # User identifier
    "session_token": str,                 # Frontend-facing token
    
    # Orchestrator Context (NEW)
    "orchestrator_context": {
        "active_orchestrators": [         # List of active orchestrators
            {
                "orchestrator_name": "ContentAnalysisOrchestrator",
                "workflow_id": "workflow_123",
                "status": "processing",
                "started_at": "2025-11-09T10:00:00Z",
                "enabling_services": ["FileParser", "DataAnalyzer"]
            }
        ],
        "enabling_services": {            # Service usage tracking
            "FileParser": {
                "invocations": 5,
                "last_used": "2025-11-09T10:05:00Z"
            }
        },
        "workflow_delegation_chain": []   # Service composition chain
    },
    
    # Agent Conversations (NEW - CRITICAL FOR DEMO)
    "conversations": {
        "guide_agent": {
            "conversation_id": "conv_guide_123",
            "messages": [
                {
                    "role": "user",
                    "content": "Help me upload a file",
                    "timestamp": "2025-11-09T10:00:00Z"
                },
                {
                    "role": "assistant",
                    "content": "I'll help you upload a file...",
                    "timestamp": "2025-11-09T10:00:01Z",
                    "orchestrator_context": {
                        "orchestrator": "ContentAnalysisOrchestrator",
                        "workflow_id": "workflow_123"
                    }
                }
            ],
            "orchestrator_context": {
                "active_workflows": ["workflow_123"],
                "last_workflow_update": "2025-11-09T10:05:00Z"
            }
        },
        "content_liaison": {
            "conversation_id": "conv_content_456",
            "messages": [...],
            "orchestrator_context": {
                "orchestrator": "ContentAnalysisOrchestrator",
                "workflow_id": "workflow_123",
                "status": "processing"
            }
        },
        "insights_liaison": {...},
        "operations_liaison": {...},
        "business_outcomes_liaison": {...}
    },
    
    # Legacy fields (for transition)
    "state": {},                          # General state
    "workflow_states": {},                # Legacy workflow tracking
    
    # Metadata
    "created_at": str,
    "updated_at": str,
    "expires_at": str,
    "last_activity": str
}
```

### New State Structure
```python
state = {
    "state_id": str,
    "session_id": str,                    # Link to session
    "state_data": Dict[str, Any],
    
    # Orchestrator Metadata (NEW)
    "orchestrator_metadata": {
        "created_by_orchestrator": "ContentAnalysisOrchestrator",
        "workflow_id": "workflow_123",
        "enabling_service_contributions": [
            {
                "service": "FileParser",
                "contribution": "parsed_file_data",
                "timestamp": "2025-11-09T10:05:00Z"
            }
        ],
        "delegation_chain": [
            "ContentAnalysisOrchestrator",
            "FileParser",
            "DataAnalyzer"
        ]
    },
    
    # Metadata
    "metadata": Dict[str, Any],
    "ttl": int,
    "stored_at": str
}
```

---

## 🔨 Implementation Tasks

### Phase 1: Agentic Foundation Integration (CRITICAL - Demo Blockers)

#### Task 1.1: Update SessionManagerService for Conversations
**File:** `backend/experience/services/session_manager_service/session_manager_service.py`

**Changes:**
1. Add `conversations` dict to session structure
2. Add methods for conversation management:
   - `add_conversation_message(session_id, agent_type, message)`
   - `get_conversation_history(session_id, agent_type)`
   - `update_conversation_orchestrator_context(session_id, agent_type, context)`
3. Persist conversations to Redis/ArangoDB via TrafficCop
4. Map `conversation_id` to `session_id`

**Code Changes:**
```python
# In create_session method
session = {
    "session_id": session_id,
    "user_id": user_id,
    "conversations": {},  # NEW
    "orchestrator_context": {},  # NEW
    # ... rest of session
}

# New methods
async def add_conversation_message(
    self,
    session_id: str,
    agent_type: str,  # "guide_agent", "content_liaison", etc.
    role: str,  # "user" or "assistant"
    content: str,
    orchestrator_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Add message to conversation history."""
    
async def get_conversation_history(
    self,
    session_id: str,
    agent_type: str
) -> List[Dict[str, Any]]:
    """Get conversation history for agent."""
    
async def update_conversation_orchestrator_context(
    self,
    session_id: str,
    agent_type: str,
    orchestrator_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Update orchestrator context in conversation."""
```

#### Task 1.2: Refactor Guide Agent for Session Integration
**Files:**
- `backend/business_enablement/agents/guide_cross_domain_agent.py`
- `backend/experience/api/guide_agent_router.py`

**Changes:**
1. Remove any local conversation storage
2. Accept `session_id` instead of `session_token` (or map token to ID)
3. Use SessionManagerService for all conversation operations
4. Track orchestrator workflows in conversation context
5. Update guide_agent_router to:
   - Get session_id from session_token
   - Pass session_id to guide agent
   - Use SessionManagerService for conversation persistence

**Code Changes:**
```python
# In guide_cross_domain_agent.py
async def provide_guidance(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
    session_id = user_request.get('session_id')  # NEW - require session_id
    message = user_request.get('message')
    
    # Get session manager
    session_manager = await self._get_session_manager()
    
    # Add user message to conversation
    await session_manager.add_conversation_message(
        session_id=session_id,
        agent_type="guide_agent",
        role="user",
        content=message
    )
    
    # Process message (existing logic)
    response = await self._process_guidance_request(user_request)
    
    # Track orchestrator context if response includes workflow
    orchestrator_context = {}
    if response.get('workflow_id'):
        orchestrator_context = {
            "orchestrator": response.get('orchestrator'),
            "workflow_id": response.get('workflow_id'),
            "status": response.get('status')
        }
    
    # Add assistant response to conversation
    await session_manager.add_conversation_message(
        session_id=session_id,
        agent_type="guide_agent",
        role="assistant",
        content=response.get('guidance', ''),
        orchestrator_context=orchestrator_context
    )
    
    return response
```

#### Task 1.3: Refactor Liaison Agents for Session Integration
**Files:**
- `backend/business_enablement/business_orchestrator/use_cases/mvp/*/agents/*_liaison_agent.py`
- `backend/experience/api/liaison_agent_router.py`

**Changes:**
1. Remove `conversation_contexts` dict from all liaison agents
2. Accept `session_id` instead of `conversation_id` (or map conversation_id to session_id)
3. Use SessionManagerService for all conversation operations
4. Track orchestrator workflows in conversation context
5. Update liaison_agent_router to:
   - Get session_id from conversation_id or create mapping
   - Pass session_id to liaison agent
   - Use SessionManagerService for conversation persistence

**Code Changes:**
```python
# In content_liaison_agent.py (and all liaison agents)
async def process_user_query(
    self,
    query: str,
    session_id: str,  # CHANGED from conversation_id
    user_context: UserContext
) -> Dict[str, Any]:
    # Get session manager
    session_manager = await self._get_session_manager()
    
    # Add user message
    await session_manager.add_conversation_message(
        session_id=session_id,
        agent_type="content_liaison",
        role="user",
        content=query
    )
    
    # Process query (existing logic)
    response = await self._process_query(query, user_context)
    
    # Get orchestrator context if available
    orchestrator_context = {}
    if self.content_orchestrator:
        orchestrator_context = {
            "orchestrator": "ContentAnalysisOrchestrator",
            "workflow_id": response.get('workflow_id'),
            "status": response.get('status')
        }
    
    # Add assistant response
    await session_manager.add_conversation_message(
        session_id=session_id,
        agent_type="content_liaison",
        role="assistant",
        content=response.get('message', ''),
        orchestrator_context=orchestrator_context
    )
    
    return response
```

#### Task 1.4: Refactor Chat Service for Session Integration
**File:** `backend/experience/services/chat_service/chat_service.py`

**Changes:**
1. Remove local `conversations` dict
2. Use SessionManagerService for all conversation storage
3. Map conversation_id to session_id
4. Track orchestrator workflows in conversation context

**Code Changes:**
```python
# In send_message_to_guide
async def send_message_to_guide(
    self,
    message: str,
    session_id: str,  # CHANGED from conversation_id
    user_id: str
) -> Dict[str, Any]:
    # Get session manager
    session_manager = await self.get_session_manager_api()
    
    # Add user message
    await session_manager.add_conversation_message(
        session_id=session_id,
        agent_type="guide_agent",
        role="user",
        content=message
    )
    
    # Send to Guide Agent
    response = await self.guide_agent.provide_guidance({
        "message": message,
        "session_id": session_id,  # Pass session_id
        "user_id": user_id
    })
    
    # Response already added to conversation by guide agent
    return response
```

---

### Phase 2: Orchestrator Pattern Integration

#### Task 2.1: Update SessionManagerService for Orchestrator Context
**File:** `backend/experience/services/session_manager_service/session_manager_service.py`

**Changes:**
1. Add `orchestrator_context` to session structure
2. Add methods:
   - `track_orchestrator_workflow(session_id, orchestrator_name, workflow_data)`
   - `get_orchestrator_state(session_id, orchestrator_name)`
   - `update_enabling_service_status(session_id, service_name, status)`

#### Task 2.2: Update Session Router
**File:** `backend/experience/api/session_router.py`

**Changes:**
1. Replace `pillar_states` with `orchestrator_states`
2. Return `orchestrator_context` in session response
3. Remove `get_initial_pillar_states()` function
4. Add `get_initial_orchestrator_states()` function

#### Task 2.3: Integrate Business Orchestrator
**File:** `backend/business_enablement/business_orchestrator/business_orchestrator_service.py`

**Changes:**
1. Accept `session_id` in orchestrator operations
2. Track orchestrator workflows in session
3. Update session state when workflows complete

---

### Phase 3: Frontend Updates

#### Task 3.1: Update GlobalSessionProvider
**File:** `symphainy-frontend/shared/session/GlobalSessionProvider.tsx`

**Changes:**
1. Replace `pillarStates` with `orchestratorStates`
2. Add conversation state management
3. Integrate with new session API

#### Task 3.2: Update useSession Hook
**File:** `symphainy-frontend/shared/hooks/useSession.ts`

**Changes:**
1. Add orchestrator state management
2. Add conversation state management
3. Implement backend state sync

---

## 📊 Implementation Order

1. **Phase 1.1** - SessionManagerService conversations (Foundation)
2. **Phase 1.2** - Guide Agent integration (Demo critical)
3. **Phase 1.3** - Liaison Agents integration (Demo critical)
4. **Phase 1.4** - Chat Service integration
5. **Phase 2** - Orchestrator pattern integration
6. **Phase 3** - Frontend updates

---

## ✅ Success Criteria

### Demo Readiness:
- ✅ Guide Agent conversations persist across page refreshes
- ✅ Liaison agent conversations persist and show orchestrator progress
- ✅ Conversation history available in session state
- ✅ Orchestrator workflows visible in agent conversations
- ✅ State synchronization between frontend and backend

### Architecture Alignment:
- ✅ No pillar-based state tracking
- ✅ All conversations in session/state management
- ✅ Orchestrator context tracked in all interactions
- ✅ Enabling service usage tracked
- ✅ Frontend uses orchestrator states

---

**Ready to begin implementation!**






