# Solution Context Propagation Plan

**Date:** December 2024  
**Status:** 📋 **PLAN**

---

## 🎯 **OBJECTIVE**

Incorporate the solution landing page context (agent-created solution structure) throughout the MVP journey to:

1. **Enhance Liaison Agent Expertise**: Provide solution context for better prompting and personalized guidance
2. **Inform Semantic Embeddings**: Include solution context to improve data meaning understanding
3. **Improve Deliverable Relevance**: Use solution context to make outputs more aligned with user goals

---

## 🏗️ **ARCHITECTURE**

### **Context Flow:**

```
Landing Page (Agent Reasoning)
    ↓
Solution Structure Created
    ↓
MVPSolutionOrchestratorService.create_session()
    ↓ (Store in session)
Session Storage (solution_context)
    ↓
MVPJourneyOrchestratorService.get_solution_context()
    ↓ (Retrieve from session)
Pass to Liaison Agents (specialization_context)
    ↓
Pass to Embedding Creation (user_context)
    ↓
Pass to Deliverables (user_context)
```

---

## 📋 **IMPLEMENTATION STEPS**

### **Step 1: Store Solution Context in Session**

**File:** `backend/solution/services/mvp_solution_orchestrator_service/mvp_solution_orchestrator_service.py`

**Method:** `orchestrate_mvp_session()`

**Changes:**
- Extract `solution_structure` from `user_context` if present
- Store in session as `solution_context` when creating session
- Include in `user_context` passed to MVPJourneyOrchestratorService

---

### **Step 2: Retrieve Solution Context from Session**

**File:** `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

**Method:** `get_solution_context()`

**New Method:**
- Retrieve `solution_context` from session
- Return structured solution context for use by liaison agents and services

---

### **Step 3: Pass Solution Context to Liaison Agents**

**File:** `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

**Method:** `_build_liaison_agent_request()`

**Changes:**
- Get solution context from session
- Include in `specialization_context` in request dict
- Base class automatically injects into prompts

---

### **Step 4: Pass Solution Context to Embedding Creation**

**File:** `backend/journey/orchestrators/content_journey_orchestrator/content_orchestrator.py`

**Method:** `embed_content()`

**Changes:**
- Get solution context from session
- Include in `user_context` passed to embedding service
- Embedding service uses context to enhance semantic meaning

---

### **Step 5: Pass Solution Context to Deliverables**

**Files:**
- `backend/journey/orchestrators/insights_journey_orchestrator/insights_journey_orchestrator.py`
- `backend/journey/orchestrators/operations_orchestrator/operations_orchestrator.py`
- `backend/journey/orchestrators/business_outcomes_orchestrator/business_outcomes_orchestrator.py`

**Changes:**
- Get solution context from session
- Include in `user_context` for all operations
- Services use context to improve relevance

---

## 📝 **SOLUTION CONTEXT STRUCTURE**

```python
{
    "solution_structure": {
        "pillars": [...],
        "recommended_data_types": [...],
        "strategic_focus": str,
        "customization_options": {...}
    },
    "reasoning": {
        "analysis": str,
        "key_insights": [...],
        "recommendations": [...],
        "confidence": float
    },
    "user_goals": str,
    "created_at": str
}
```

---

## 🔄 **USAGE PATTERNS**

### **1. Liaison Agent Enhancement**

**Pattern:**
```python
# Solution context is automatically injected into liaison agent prompts
# via specialization_context in request dict

request = {
    "message": user_message,
    "session_id": session_id,
    "user_context": user_context,
    "specialization_context": {
        "solution_structure": {...},
        "user_goals": "...",
        "strategic_focus": "..."
    }
}

# Base class automatically injects into prompt:
# "User's goals: {user_goals}"
# "Strategic focus: {strategic_focus}"
# "Recommended data types: {recommended_data_types}"
```

### **2. Semantic Embedding Enhancement**

**Pattern:**
```python
# Solution context included in user_context for embedding creation
user_context = {
    "workflow_id": "...",
    "solution_context": {
        "strategic_focus": "operations",
        "recommended_data_types": ["csv", "json"],
        "user_goals": "..."
    }
}

# Embedding service uses context to:
# - Enhance semantic meaning understanding
# - Prioritize relevant data types
# - Improve column meaning inference
```

### **3. Deliverable Enhancement**

**Pattern:**
```python
# Solution context included in user_context for all operations
user_context = {
    "workflow_id": "...",
    "solution_context": {
        "strategic_focus": "operations",
        "pillars": [...],
        "user_goals": "..."
    }
}

# Services use context to:
# - Prioritize relevant workflows
# - Focus on strategic areas
# - Align outputs with user goals
```

---

## ✅ **BENEFITS**

1. **Personalized Guidance**: Liaison agents provide context-aware recommendations
2. **Better Data Understanding**: Embeddings understand data meaning in context of user goals
3. **Relevant Deliverables**: All outputs aligned with solution structure
4. **Consistent Experience**: Context flows through entire journey
5. **Agent Expertise**: Agents have full context for better reasoning

---

## 🚀 **NEXT STEPS**

1. Implement Step 1: Store solution context in session
2. Implement Step 2: Retrieve solution context method
3. Implement Step 3: Pass to liaison agents
4. Implement Step 4: Pass to embedding creation
5. Implement Step 5: Pass to deliverables
6. Test end-to-end flow
7. Verify context propagation










