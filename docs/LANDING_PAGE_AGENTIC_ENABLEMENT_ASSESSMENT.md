# Landing Page Agentic Enablement Assessment

## Executive Summary

This document assesses the current landing page implementation and provides recommendations for enabling the Guide Agent to set specialization context through conversational interaction. The assessment includes architectural recommendations and frontend change requirements.

## Current Landing Page Analysis

### Current Implementation

**File:** `symphainy-frontend/components/landing/WelcomeJourney.tsx`

**Current Flow:**
1. User sees landing page with pillar overview
2. User can optionally enter goals in textarea
3. `handleGoalAnalysis()` calls `guideAgent.getGuidance(userGoals, ...)`
4. Guide Agent returns suggested data types
5. User proceeds to Content Pillar

**Current Limitations:**
1. **No Conversational Context**: Goal analysis is a one-shot call, not a conversation
2. **No Specialization Capture**: The Guide Agent's response isn't used to configure liaison agents
3. **No Context Persistence**: Specialization context isn't stored or passed to other agents
4. **Static Flow**: User must manually enter goals, no guided conversation

**Current Guide Agent Integration:**
- Uses `useGuideAgent()` hook
- Calls `guideAgent.getGuidance()` with user goals
- Receives `suggested_data_types` in response
- But this context is not used to configure agents

## Recommended Architecture: Use Existing MVPJourneyOrchestratorService (UPDATED)

### Assessment: Existing Orchestrator vs. Creating New One

**✅ CORRECT Approach: Use Existing MVPJourneyOrchestratorService**
- ✅ Already exists and extends `OrchestratorBase`
- ✅ `GuideCrossDomainAgent` already integrated
- ✅ Follows correct orchestrator pattern
- ✅ Can add specialization context management to existing orchestrator
- ✅ No need to create duplicate infrastructure

**❌ WRONG Approach (from old plans):**
- ❌ Don't create new JourneyOrchestratorService
- ❌ Use existing `MVPJourneyOrchestratorService`

### Recommendation: Enhance Existing MVPJourneyOrchestratorService

**Rationale:**
1. **Already Exists**: `MVPJourneyOrchestratorService` is already implemented
2. **Guide Agent Integrated**: `GuideCrossDomainAgent` is already initialized via `initialize_agent()`
3. **Pattern Consistency**: Already follows `OrchestratorBase` pattern
4. **Add Features**: Add specialization context management to existing orchestrator
5. **No Duplication**: Avoid creating duplicate infrastructure

## Proposed Architecture (UPDATED - Use Existing MVPJourneyOrchestratorService)

### Existing Structure (Already Implemented)

```
backend/journey/services/mvp_journey_orchestrator_service/
├── mvp_journey_orchestrator_service.py  # Main orchestrator (extends OrchestratorBase)
└── (Guide Agent is in backend/journey/agents/guide_cross_domain_agent.py)
```

### Enhancements to Existing Orchestrator

**Add to MVPJourneyOrchestratorService:**

1. **Specialization Context Management** (NEW)
   - Store user's business domain, goals, preferences
   - Share context with liaison agents
   - Update context as user progresses

2. **Landing Page Conversation** (NEW)
   - Handle landing page conversation with Guide Agent
   - Capture specialization context from conversation
   - Store in session

3. **Guide Agent Integration** (ALREADY EXISTS)
   - ✅ Guide Agent already initialized via `initialize_agent()`
   - ✅ Guide Agent is `GuideCrossDomainAgent` (declarative)
   - Add MCP tools for specialization context storage

4. **Journey State Tracking** (ENHANCE)
   - Track user's progress through pillars
   - Maintain journey context
   - Support journey analytics

### Specialization Context Structure

```python
specialization_context = {
    "user_goals": "Improve customer satisfaction and reduce churn",
    "business_domain": "customer_service",
    "industry": "retail",
    "preferred_data_types": ["customer_feedback", "satisfaction_scores", "churn_data"],
    "focus_areas": ["customer_experience", "retention"],
    "constraints": {
        "budget": 500000,
        "timeline_days": 180
    },
    "pillar_priorities": {
        "content": "high",
        "insights": "high",
        "operations": "medium",
        "business_outcomes": "high"
    }
}
```

## Implementation Plan (UPDATED - Enhance Existing Orchestrator)

### Phase 1: Enhance Existing MVPJourneyOrchestratorService

**1.1 Add Specialization Context Management**

**File:** `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

**✅ CORRECT Approach: Enhance existing orchestrator**

```python
# Add to existing MVPJourneyOrchestratorService class
class MVPJourneyOrchestratorService(OrchestratorBase):
    # ... existing code ...
    
    def __init__(self, ...):
        # ... existing initialization ...
        self.specialization_context = {}  # Per session (NEW)
    
    async def initialize(self):
        # ... existing initialization ...
        # Guide Agent already initialized:
        # self.guide_agent = await self.initialize_agent(GuideCrossDomainAgent, ...)
        
        # Add MCP tools for specialization context (NEW)
        # Tools will be in orchestrator's MCP server
    
    async def handle_landing_page_conversation(
        self,
        message: str,
        session_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle landing page conversation with Guide Agent.
        
        NEW method to add to existing orchestrator.
        """
        # Get conversation history from session
        conversation_history = await self._get_conversation_history(session_id)
        
        # Process with Guide Agent (already exists)
        request = {
            "message": message,
            "session_id": session_id,
            "user_context": user_context,
            "conversation_history": conversation_history,
            "conversation_stage": "landing_page"
        }
        
        result = await self.guide_agent.handle_user_request(request)
        
        # Extract specialization context from Guide Agent's response
        specialization = self._extract_specialization_context(result, conversation_history)
        
        # Store specialization context in session
        if specialization:
            await self._store_specialization_context(session_id, specialization)
        
        return {
            "response": result.get("message", ""),
            "specialization_context": specialization,
            "suggested_routes": result.get("suggested_routes", [])
        }
    
    async def get_specialization_context(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get stored specialization context for session."""
        return self.specialization_context.get(session_id, {})
    
    async def _store_specialization_context(
        self,
        session_id: str,
        context: Dict[str, Any]
    ):
        """Store specialization context in session."""
        self.specialization_context[session_id] = context
        
        # Also store in session via Session Manager
        session_manager = await self._get_session_manager()
        if session_manager:
            await session_manager.update_session(
                session_id=session_id,
                updates={"specialization_context": context}
            )
```
    
    async def handle_landing_page_conversation(
        self,
        message: str,
        session_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle landing page conversation with Guide Agent.
        
        This is the entry point for the landing page interaction.
        """
        # Get conversation history from session
        conversation_history = await self._get_conversation_history(session_id)
        
        # Process with Guide Agent
        request = {
            "message": message,
            "session_id": session_id,
            "user_context": user_context,
            "conversation_history": conversation_history,
            "conversation_stage": "landing_page"  # Indicates we're on landing page
        }
        
        result = await self.guide_agent.process_request(request)
        
        # Extract specialization context from Guide Agent's response
        specialization = self._extract_specialization_context(result, conversation_history)
        
        # Store specialization context in session
        if specialization:
            await self._store_specialization_context(session_id, specialization)
        
        return {
            "response": result.get("response", ""),
            "specialization_context": specialization,
            "suggested_next_steps": result.get("suggested_next_steps", [])
        }
    
    def _extract_specialization_context(
        self,
        agent_response: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract specialization context from Guide Agent's response.
        
        The Guide Agent's LLM reasoning should identify:
        - User's business domain
        - Primary goals
        - Relevant data types
        - Pillar priorities
        """
        # Parse LLM response to extract context
        # This can use structured output or LLM reasoning
        pass
    
    async def get_specialization_context(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get stored specialization context for session."""
        return self.specialization_context.get(session_id, {})
    
    async def share_specialization_context(
        self,
        session_id: str,
        target_pillar: str
    ) -> Dict[str, Any]:
        """
        Share specialization context with a pillar's liaison agent.
        
        This allows liaison agents to be configured with user's specialization.
        """
        context = await self.get_specialization_context(session_id)
        
        # Route to appropriate pillar orchestrator
        # The liaison agent can use this context to personalize responses
        return {
            "success": True,
            "specialization_context": context,
            "target_pillar": target_pillar
        }
```

**1.2 Guide Agent (Already Exists)**

**✅ Guide Agent Already Implemented:**
- File: `backend/journey/agents/guide_cross_domain_agent.py`
- Extends: `DeclarativeAgentBase`
- Config: `backend/journey/agents/configs/mvp_guide_agent.yaml`
- Already initialized in `MVPJourneyOrchestratorService.initialize()`

**No changes needed - agent already exists and is integrated!**

**1.3 Guide Agent Configuration (Already Exists)**

**File:** `backend/journey/agents/configs/mvp_guide_agent.yaml` ✅

```yaml
agent_name: GuideAgent
role: Journey Guide and Specialization Advisor
goal: Help users define their goals and capture specialization context to personalize their journey
backstory: |
  You are a friendly, helpful guide for new users. Your role is to have a natural conversation
  with users on the landing page to understand their business goals, challenges, and what they
  hope to achieve. Through this conversation, you help identify their specialization context:
  their business domain, industry, focus areas, and what types of data and analysis would be
  most relevant. You maintain a warm, conversational tone and ask clarifying questions to
  understand the user's needs deeply.

instructions:
  - Have a natural conversation with users about their business goals
  - Ask clarifying questions to understand their domain, industry, and challenges
  - Identify what types of data would be most relevant for their goals
  - Extract specialization context: business_domain, industry, focus_areas, preferred_data_types
  - Suggest which pillars would be most relevant for their goals
  - Provide personalized recommendations based on their context
  - Maintain conversation context across multiple turns
  - When you have enough context, summarize what you've learned and suggest next steps

allowed_mcp_servers:
  - JourneyOrchestratorMCPServer

allowed_tools:
  - store_specialization_context_tool
  - get_user_preferences_tool
  - suggest_data_types_tool
  - recommend_pillar_priorities_tool

capabilities:
  - landing_page_conversation
  - specialization_context_extraction
  - goal_understanding
  - personalized_recommendations

llm_config:
  model: gpt-4o-mini
  temperature: 0.4  # Slightly higher for more natural conversation
  max_tokens: 2000
  timeout: 120

stateful: true
max_conversation_history: 15  # Landing page conversations are typically shorter

iterative_execution: false  # Single-pass for conversational responses

cost_tracking: true
tool_selection_strategy: autonomous
max_tool_calls_per_request: 5
```

**1.4 Add MCP Tools to Existing Orchestrator (NEW)**

**File:** Add to existing MCP server or create if doesn't exist

**Note:** MVPJourneyOrchestratorService may not have MCP server yet. If not, create one.

```python
# In MVPJourneyOrchestratorService's MCP server
@mcp_tool
async def store_specialization_context_tool(
    specialization_context: Dict[str, Any],  # Extracted by Guide Agent LLM
    session_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Store specialization context extracted from landing page conversation.
    
    Guide Agent's LLM extracts context and calls this tool.
    """
    # Store in orchestrator's specialization_context dict
    await self.orchestrator._store_specialization_context(session_id, specialization_context)
    
    return {
        "success": True,
        "message": "Specialization context stored",
        "specialization_context": specialization_context
    }

@mcp_tool
async def suggest_data_types_tool(
    user_goals: str,
    business_domain: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Suggest relevant data types based on user goals and domain.
    
    Returns rule-based suggestions (NO LLM in service).
    """
    # Rule-based data type suggestions
    pass

@mcp_tool
async def recommend_pillar_priorities_tool(
    user_goals: str,
    business_domain: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Recommend pillar priorities based on user goals.
    
    Returns rule-based recommendations (NO LLM in service).
    """
    pass
```

### Phase 2: Update Frontend Landing Page

**2.1 Enhance WelcomeJourney Component**

**Changes to:** `symphainy-frontend/components/landing/WelcomeJourney.tsx`

**Key Changes:**
1. Replace `handleGoalAnalysis()` with conversational flow
2. Integrate with Journey Orchestrator WebSocket
3. Display conversation with Guide Agent
4. Capture specialization context from conversation

**New Implementation:**

```typescript
export function WelcomeJourney({ handleWelcomeComplete }: Props) {
  const [conversationMode, setConversationMode] = useState(false);
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [specializationContext, setSpecializationContext] = useState<any>(null);
  const { sendMessage } = useGuideAgent(); // Enhanced to use Journey Orchestrator
  
  const handleStartConversation = () => {
    setConversationMode(true);
    // Send initial message to Guide Agent
    sendMessage("Hello! I'd like to get started. Can you help me understand what I should focus on?");
  };
  
  const handleConversationComplete = async () => {
    // Get specialization context from conversation
    const context = await getSpecializationContext();
    setSpecializationContext(context);
    
    // Store in session for use by other agents
    await storeSpecializationContext(context);
    
    // Proceed to content pillar with context
    handleWelcomeComplete();
  };
  
  // Render conversation interface when in conversation mode
  if (conversationMode) {
    return (
      <ConversationInterface
        conversationHistory={conversationHistory}
        onMessageSend={handleSendMessage}
        onComplete={handleConversationComplete}
      />
    );
  }
  
  // Render original landing page with "Start Conversation" button
  return (
    // ... existing landing page UI
    <Button onClick={handleStartConversation}>
      Start Personalized Journey
    </Button>
  );
}
```

**2.2 Create Conversation Interface Component**

**New File:** `symphainy-frontend/components/landing/LandingPageConversation.tsx`

```typescript
export function LandingPageConversation({
  onComplete,
  onMessageSend
}: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const { sendMessage } = useGuideAgent();
  
  const handleSend = async (message: string) => {
    // Add user message
    setMessages(prev => [...prev, { role: "user", content: message }]);
    
    // Send to Guide Agent via Journey Orchestrator
    const response = await sendMessage(message);
    
    // Add agent response
    setMessages(prev => [...prev, { role: "assistant", content: response.message }]);
    
    // Check if Guide Agent has extracted enough context
    if (response.specialization_context) {
      // Show summary and proceed button
    }
  };
  
  return (
    <div className="conversation-interface">
      {/* Chat messages */}
      {/* Input field */}
      {/* "I'm ready to proceed" button when context is captured */}
    </div>
  );
}
```

### Phase 3: Share Specialization Context with Liaison Agents (UPDATED - Simplified)

**3.1 Pass Context in Request Dict (Simplified)**

**✅ CORRECT Pattern:**
- Specialization context is passed in `request` dict to agents
- Agents don't retrieve it manually
- Base class injects context into prompts automatically

```python
# In orchestrator or frontend, when calling liaison agent
specialization_context = await mvp_orchestrator.get_specialization_context(session_id)

request = {
    "message": user_message,
    "session_id": session_id,
    "user_context": user_context,
    "specialization_context": specialization_context,  # Pass in request dict
    "pillar_context": pillar_context
}

# Agent receives context in request, base class injects into prompt
response = await liaison_agent.handle_user_query(request)
```

**❌ WRONG Pattern (from old plans):**
```python
# Don't retrieve context in agent initialization
specialization_context = await journey_orchestrator.get_specialization_context(...)
# Pass in request dict instead
```

**3.2 Context Injection (Automatic)**

**✅ Base class automatically injects context into prompts:**
- `DeclarativeAgentBase._build_agent_prompt()` includes specialization context
- No manual application needed
- Context modifies agent behavior via prompt injection

## Frontend Changes Required

### Required Changes

**1. Landing Page Component Enhancement**
- ✅ Add conversational interface (chat UI)
- ✅ Replace static goal input with conversation flow
- ✅ Display Guide Agent responses
- ✅ Show specialization context summary before proceeding

**2. Guide Agent Provider Enhancement**
- ✅ Update to use Journey Orchestrator endpoint
- ✅ Support landing page conversation mode
- ✅ Handle specialization context extraction
- ✅ Store context in session

**3. New Components**
- ✅ `LandingPageConversation.tsx` - Conversation interface
- ✅ `SpecializationContextSummary.tsx` - Display captured context
- ✅ `ConversationProgress.tsx` - Show conversation progress

**4. Session Management**
- ✅ Store specialization context in session
- ✅ Share context with pillar pages
- ✅ Pass context to liaison agents

### Optional Enhancements

**1. Visual Enhancements**
- Progress indicator for conversation stages
- Context extraction visualization
- Pillar recommendations based on context

**2. User Experience**
- Ability to edit specialization context
- Preview of how context affects journey
- Option to skip conversation (use defaults)

## Integration Points

### 1. Guide Agent → Journey Orchestrator

```
Frontend (Landing Page)
    ↓
WebSocket: /api/ws/journey
    ↓
Journey Orchestrator Service
    ↓
Guide Agent (Declarative)
    ↓
MCP Tools (store_specialization_context_tool)
    ↓
Specialization Context Stored
```

### 2. Journey Orchestrator → Liaison Agents

```
Liaison Agent Initialization
    ↓
Get Specialization Context from Journey Orchestrator
    ↓
Apply Context to Agent Behavior
    ↓
Personalized Responses Based on Context
```

### 3. Session Context Sharing

```
Landing Page Conversation
    ↓
Specialization Context Stored in Session
    ↓
User Navigates to Pillar
    ↓
Liaison Agent Retrieves Context from Session
    ↓
Agent Uses Context for Personalization
```

## Example Flow

### Landing Page Conversation

```
User: "I want to improve customer satisfaction"
Guide Agent: "That's a great goal! To help you achieve that, I'd like to understand more. 
              What industry are you in, and what are the main challenges you're facing 
              with customer satisfaction?"

User: "I'm in retail. Our main issue is response time - customers wait too long for support"
Guide Agent: "I understand. For retail customer service, response time is critical. 
              What types of data do you have available? For example, customer feedback, 
              support tickets, satisfaction surveys?"

User: "We have customer feedback surveys and support ticket data"
Guide Agent: "Perfect! Based on your goals and available data, I recommend focusing on:
              - Content Pillar: Upload your customer feedback and support ticket data
              - Insights Pillar: Analyze satisfaction trends and identify bottlenecks
              - Operations Pillar: Optimize your support workflows
              - Business Outcomes Pillar: Track satisfaction improvements and ROI
              
              I've captured your specialization context. Ready to start your journey?"

[User clicks "Start Journey"]

Specialization Context Stored:
{
  "user_goals": "Improve customer satisfaction",
  "business_domain": "retail",
  "industry": "retail",
  "challenges": ["response_time"],
  "preferred_data_types": ["customer_feedback", "support_tickets"],
  "pillar_priorities": {
    "content": "high",
    "insights": "high",
    "operations": "high",
    "business_outcomes": "high"
  }
}
```

### Liaison Agent Personalization

```
User navigates to Content Pillar
    ↓
ContentLiaisonAgent initializes
    ↓
Retrieves specialization context:
  - Domain: retail
  - Goals: customer satisfaction
  - Data types: customer feedback, support tickets
    ↓
Agent personalizes responses:
  "Based on your goal to improve customer satisfaction, I recommend uploading 
   your customer feedback surveys first. These will help us identify key pain 
   points in your support process."
```

## Benefits of Journey Orchestrator Approach

1. **Consistent Pattern**: Matches pillar orchestrator pattern
2. **Service Layer**: Clean separation of concerns
3. **Extensibility**: Easy to add journey analytics, milestone tracking
4. **Context Management**: Centralized specialization context storage
5. **MCP Integration**: Guide Agent can use orchestrator tools
6. **Future Features**: Journey replay, journey templates, journey analytics

## Implementation Timeline (UPDATED)

**Week 1:** Enhance Existing MVPJourneyOrchestratorService
- Add specialization context management methods
- Add `handle_landing_page_conversation()` method
- Add MCP tools for specialization context storage
- Test with existing Guide Agent

**Week 2:** Frontend Integration
- Update landing page component
- Create conversation interface
- Integrate with existing `MVPJourneyOrchestratorService`
- Use `mvp_orchestrator.guide_agent` for conversations

**Week 3:** Context Sharing (Simplified)
- Pass specialization context in `request` dict to liaison agents
- Test context injection into agent prompts
- Test end-to-end flow

**Week 4:** Testing & Refinement
- Test conversation flows
- Refine prompts
- User experience improvements

**Future Enhancements:**
- Agent-to-Agent Collaboration (Guide agent can call liaison agents)
- Agent Learning (learn user preferences from landing page)
- See `AGENTIC_PLATFORM_ENHANCEMENT_OPPORTUNITIES.md` for details

## Conclusion (UPDATED)

**✅ Use Existing MVPJourneyOrchestratorService** because:
1. Already exists and follows correct `OrchestratorBase` pattern
2. Guide Agent already integrated via `initialize_agent()`
3. Can add specialization context management to existing orchestrator
4. Avoids duplicate infrastructure
5. Maintains architectural consistency

**Enhancements Needed:**
- Add specialization context management methods
- Add `handle_landing_page_conversation()` method
- Add MCP tools for context storage
- Pass context to liaison agents via `request` dict

The landing page conversation will capture specialization context naturally through Guide Agent's LLM reasoning, and this context will be shared with all liaison agents via the `request` dict to personalize the entire user journey.


