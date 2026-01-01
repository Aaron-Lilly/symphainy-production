# Solution Context Usage Guide

**Date:** December 2024  
**Status:** ✅ **IMPLEMENTED**

---

## 🎯 **OVERVIEW**

The solution context from the landing page (agent-created solution structure) is now automatically propagated throughout the MVP journey. This guide explains how to use it in different parts of the system.

---

## 📋 **WHAT IS SOLUTION CONTEXT?**

Solution context includes:
- **solution_structure**: Agent-created pillar configuration (priorities, navigation order, customizations)
- **reasoning**: Agent's analysis, insights, recommendations, and confidence score
- **user_goals**: User's stated goals from landing page
- **strategic_focus**: Agent-determined focus area

---

## 🔄 **HOW IT WORKS**

### **1. Storage Flow**

```
Landing Page → MVPSolutionOrchestratorService.create_session()
    ↓
Extract solution_context from user_context
    ↓
Store in session via MVPJourneyOrchestratorService
    ↓
Available throughout journey
```

### **2. Retrieval Methods**

**Get Full Solution Context:**
```python
# In MVPJourneyOrchestratorService
solution_context = await mvp_journey_orchestrator.get_solution_context(session_id)
```

**Get Specialization Context (for Liaison Agents):**
```python
# In MVPJourneyOrchestratorService
specialization_context = await mvp_journey_orchestrator.get_specialization_context(session_id)
```

---

## 💡 **USAGE PATTERNS**

### **1. Liaison Agent Enhancement**

**Pattern:** Pass `specialization_context` in request dict to liaison agents

**Example:**
```python
# In orchestrator or frontend, when calling liaison agent
async def call_liaison_agent_with_solution_context(
    self,
    liaison_agent: DeclarativeAgentBase,
    user_message: str,
    session_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Call liaison agent with solution context."""
    
    # Get specialization context from MVPJourneyOrchestratorService
    mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
    specialization_context = await mvp_orchestrator.get_specialization_context(session_id)
    
    # Build request with solution context
    request = {
        "message": user_message,
        "session_id": session_id,
        "user_context": user_context,
        "specialization_context": specialization_context  # ✅ Solution context here
        # conversation_history: Base class manages if stateful: true
    }
    
    # Agent receives context in request, base class automatically injects into prompt
    return await liaison_agent.handle_user_query(request)
```

**What Gets Injected into Prompt:**
- User's goals
- Strategic focus area
- Recommended data types
- Pillar priorities and focus areas
- Key insights and recommendations
- Confidence score

---

### **2. Semantic Embedding Enhancement**

**Pattern:** Include solution context in `user_context` for embedding creation

**Example:**
```python
# In ContentJourneyOrchestrator.embed_content()
async def embed_content(
    self,
    file_id: str,
    parsed_file_id: str,
    content_metadata: Dict[str, Any],
    user_id: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create embeddings with solution context."""
    
    # Get solution context from session
    session_id = user_context.get("session_id") if user_context else None
    if session_id:
        mvp_orchestrator = await self._get_mvp_journey_orchestrator()
        if mvp_orchestrator:
            solution_context = await mvp_orchestrator.get_solution_context(session_id)
            if solution_context:
                # Enhance user_context with solution context
                enhanced_user_context = user_context.copy() if user_context else {}
                enhanced_user_context["solution_context"] = solution_context
                user_context = enhanced_user_context
    
    # Pass to embedding service
    return await embedding_service.create_representative_embeddings(
        parsed_file_id=parsed_file_id,
        content_metadata=content_metadata,
        user_context=user_context  # ✅ Solution context included
    )
```

**How Embedding Service Uses It:**
- Prioritizes recommended data types
- Enhances semantic meaning understanding based on user goals
- Focuses on strategic areas when inferring column meanings
- Improves context-aware embedding quality

---

### **3. Deliverable Enhancement**

**Pattern:** Include solution context in `user_context` for all operations

**Example:**
```python
# In InsightsJourneyOrchestrator.execute_analysis_workflow()
async def execute_analysis_workflow(
    self,
    file_id: str,
    analysis_type: str,
    analysis_options: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute analysis with solution context."""
    
    # Get solution context from session
    session_id = user_context.get("session_id") if user_context else None
    if session_id:
        mvp_orchestrator = await self._get_mvp_journey_orchestrator()
        if mvp_orchestrator:
            solution_context = await mvp_orchestrator.get_solution_context(session_id)
            if solution_context:
                # Enhance user_context
                enhanced_user_context = user_context.copy() if user_context else {}
                enhanced_user_context["solution_context"] = solution_context
                user_context = enhanced_user_context
    
    # Pass to analysis service
    return await analysis_service.analyze(
        file_id=file_id,
        analysis_type=analysis_type,
        analysis_options=analysis_options,
        user_context=user_context  # ✅ Solution context included
    )
```

**How Services Use It:**
- Prioritize workflows aligned with strategic focus
- Focus on relevant data types
- Align outputs with user goals
- Provide context-aware recommendations

---

## 🔧 **IMPLEMENTATION CHECKLIST**

### **For Liaison Agents:**
- [x] MVPJourneyOrchestratorService.get_specialization_context() implemented
- [ ] Update liaison agent callers to include specialization_context
- [ ] Verify base class injects context into prompts
- [ ] Test agent responses with solution context

### **For Embedding Creation:**
- [ ] Update ContentJourneyOrchestrator.embed_content() to get solution context
- [ ] Pass solution context to EmbeddingService
- [ ] Update EmbeddingService to use context for enhanced meaning
- [ ] Test embedding quality with solution context

### **For Deliverables:**
- [ ] Update InsightsJourneyOrchestrator to get solution context
- [ ] Update OperationsOrchestrator to get solution context
- [ ] Update BusinessOutcomesOrchestrator to get solution context
- [ ] Pass solution context in user_context for all operations
- [ ] Test deliverable relevance with solution context

---

## 📊 **SOLUTION CONTEXT STRUCTURE**

```python
{
    "solution_structure": {
        "pillars": [
            {
                "name": "content" | "insights" | "operations" | "business-outcomes",
                "enabled": bool,
                "priority": int,  # 1-4, lower is higher priority
                "navigation_order": int,
                "customizations": {
                    "focus_areas": [...],
                    "workflows": [...],
                    "data_types": [...]
                }
            }
        ],
        "recommended_data_types": ["csv", "json", "pdf"],
        "strategic_focus": "operations" | "insights" | "content" | "business-outcomes" | "general",
        "customization_options": {
            "workflow_creation": bool,
            "interactive_guidance": bool,
            "automated_analysis": bool
        }
    },
    "reasoning": {
        "analysis": "Agent's detailed analysis...",
        "key_insights": ["Insight 1", "Insight 2"],
        "recommendations": ["Recommendation 1", "Recommendation 2"],
        "confidence": 0.85  # 0.0-1.0
    },
    "user_goals": "I want to automate my data processing workflow...",
    "created_at": "2024-12-XX..."
}
```

---

## 🚀 **NEXT STEPS**

1. **Update Liaison Agent Callers**: Modify orchestrators to pass specialization_context
2. **Update Embedding Creation**: Enhance ContentJourneyOrchestrator to use solution context
3. **Update Deliverables**: Enhance all journey orchestrators to use solution context
4. **Test End-to-End**: Verify context propagation and usage
5. **Measure Impact**: Compare deliverable quality with and without solution context

---

## 📚 **REFERENCES**

- **Solution Context Propagation Plan**: `docs/SOLUTION_CONTEXT_PROPAGATION_PLAN.md`
- **Agent Context Sharing Architecture**: `docs/AGENT_CONTEXT_SHARING_ARCHITECTURE.md`
- **Agentic-Forward Landing Page**: `docs/AGENTIC_FORWARD_LANDING_PAGE_IMPLEMENTATION.md`









