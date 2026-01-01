# Frontend Changes for Agentic Vision

## Executive Summary

This document assesses the frontend changes required to support the new declarative agent + conversational analytics architecture. It identifies UI components, interaction patterns, and integration points that need to be updated or created.

## Current Frontend Architecture

### Current Agent Integration

**Guide Agent:**
- Uses `GuideAgentProvider` with WebSocket connection
- Sends messages via `sendMessage()`
- Receives responses via WebSocket subscription
- Stores conversation history in component state

**Liaison Agents:**
- Each pillar has a liaison agent component (e.g., `ContentLiaisonAgent.tsx`)
- Currently uses local state for conversation
- Static responses based on component state
- No backend integration for actual agent communication

**Chat Interface:**
- `ChatAssistant.tsx` - Generic chat component
- Uses WebSocket for message sending
- Displays messages in scrollable area

## Required Frontend Changes

### 1. Landing Page Conversation Interface

**Current State:**
- Static goal input form
- One-shot `getGuidance()` call
- No conversational flow

**Required Changes:**

**New Component:** `components/landing/LandingPageConversation.tsx`

```typescript
interface LandingPageConversationProps {
  onContextCaptured: (context: SpecializationContext) => void;
  onComplete: () => void;
}

export function LandingPageConversation({
  onContextCaptured,
  onComplete
}: LandingPageConversationProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [contextExtracted, setContextExtracted] = useState(false);
  const { sendMessage } = useGuideAgent();
  
  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;
    
    const userMessage = input.trim();
    setInput("");
    
    // Add user message
    setMessages(prev => [...prev, {
      role: "user",
      content: userMessage,
      timestamp: new Date()
    }]);
    
    setIsProcessing(true);
    
    try {
      // Send to Guide Agent via Journey Orchestrator
      const response = await sendMessage(userMessage);
      
      // Add agent response
      setMessages(prev => [...prev, {
        role: "assistant",
        content: response.message,
        timestamp: new Date()
      }]);
      
      // Check if specialization context was extracted
      if (response.specialization_context) {
        setContextExtracted(true);
        onContextCaptured(response.specialization_context);
      }
    } catch (error) {
      // Handle error
    } finally {
      setIsProcessing(false);
    }
  };
  
  return (
    <div className="landing-conversation">
      <ConversationMessages messages={messages} />
      {contextExtracted && (
        <SpecializationContextSummary 
          context={contextExtracted}
          onProceed={onComplete}
        />
      )}
      <ConversationInput
        value={input}
        onChange={setInput}
        onSubmit={handleSend}
        disabled={isProcessing}
      />
    </div>
  );
}
```

**Changes to:** `components/landing/WelcomeJourney.tsx`

```typescript
// Replace handleGoalAnalysis with conversational flow
const [showConversation, setShowConversation] = useState(false);
const [specializationContext, setSpecializationContext] = useState(null);

const handleStartConversation = () => {
  setShowConversation(true);
};

const handleContextCaptured = (context: SpecializationContext) => {
  setSpecializationContext(context);
  // Store in session for other agents
  storeSpecializationContext(context);
};

// Render conversation interface when active
{showConversation && (
  <LandingPageConversation
    onContextCaptured={handleContextCaptured}
    onComplete={handleWelcomeComplete}
  />
)}
```

### 2. Enhanced Chat Interface for Agents

**Current State:**
- Basic chat component
- Simple message display
- No agent-specific features

**Required Changes:**

**Enhanced Component:** `features/chat/ChatAssistant.tsx`

**New Features:**
1. **Agent Type Indicator**
   - Show which agent is responding (Guide, Content Liaison, etc.)
   - Visual distinction between agents

2. **Tool Call Indicators**
   - Show when agent is calling tools
   - Display tool execution status
   - Show tool results (if relevant)

3. **Context Awareness Display**
   - Show current conversation context
   - Display specialization context (if available)
   - Show pillar context

4. **Structured Responses**
   - Support for tables, charts, lists
   - Rich formatting for agent responses
   - Action buttons for suggested next steps

**Enhanced Implementation:**

```typescript
interface EnhancedChatMessage extends ChatMessage {
  agent_type?: "guide" | "content_liaison" | "insights_liaison" | "operations_liaison" | "business_outcomes_liaison";
  tool_calls?: ToolCall[];
  context?: ConversationContext;
  structured_content?: {
    type: "table" | "chart" | "list" | "summary";
    data: any;
  };
}

function Message({ msg }: { msg: EnhancedChatMessage }) {
  return (
    <div className="message-container">
      {/* Agent type badge */}
      {msg.agent_type && (
        <Badge variant="outline">{msg.agent_type}</Badge>
      )}
      
      {/* Tool call indicators */}
      {msg.tool_calls && (
        <ToolCallIndicator toolCalls={msg.tool_calls} />
      )}
      
      {/* Structured content */}
      {msg.structured_content && (
        <StructuredContentRenderer content={msg.structured_content} />
      )}
      
      {/* Regular message content */}
      <p>{msg.content}</p>
      
      {/* Suggested actions */}
      {msg.suggested_actions && (
        <SuggestedActions actions={msg.suggested_actions} />
      )}
    </div>
  );
}
```

### 3. Liaison Agent Component Updates

**Current State:**
- Static guidance based on component state
- Local conversation state
- No backend agent integration

**Required Changes:**

**Update:** `components/liaison-agents/ContentLiaisonAgent.tsx`

**Key Changes:**
1. **Backend Integration**
   - Connect to Content Orchestrator's liaison agent
   - Use WebSocket or REST API for agent communication
   - Remove local static responses

2. **Specialization Context**
   - Retrieve specialization context from session
   - Use context to personalize responses
   - Display context-aware guidance

3. **Tool Execution Display**
   - Show when agent calls tools (parse_file_tool, etc.)
   - Display tool execution results
   - Show progress for long-running operations

**Updated Implementation:**

```typescript
export const ContentLiaisonAgent: React.FC<Props> = ({
  selectedFile,
  parseResult,
  metadata,
  ...
}) => {
  const { user } = useAuth();
  const { sessionId } = useGlobalSession();
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [specializationContext, setSpecializationContext] = useState(null);
  const [isAgentProcessing, setIsAgentProcessing] = useState(false);
  
  // Get specialization context from session
  useEffect(() => {
    const loadContext = async () => {
      const context = await getSpecializationContext(sessionId);
      setSpecializationContext(context);
    };
    loadContext();
  }, [sessionId]);
  
  // Send message to backend Content Liaison Agent
  const handleSendMessage = async (message: string) => {
    setIsAgentProcessing(true);
    
    try {
      const response = await fetch('/api/v1/content-pillar/liaison-agent/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          session_id: sessionId,
          user_context: { user_id: user?.id },
          specialization_context: specializationContext,
          current_state: {
            selected_file: selectedFile,
            parse_result: parseResult,
            metadata: metadata
          }
        })
      });
      
      const data = await response.json();
      
      // Add to conversation history
      setConversationHistory(prev => [
        ...prev,
        { role: "user", content: message },
        { role: "assistant", content: data.response }
      ]);
      
      // Handle tool calls if any
      if (data.tool_calls) {
        // Display tool execution
        handleToolCalls(data.tool_calls);
      }
    } catch (error) {
      // Handle error
    } finally {
      setIsAgentProcessing(false);
    }
  };
  
  return (
    <div className="content-liaison-agent">
      {/* Specialization context display */}
      {specializationContext && (
        <SpecializationContextBadge context={specializationContext} />
      )}
      
      {/* Conversation interface */}
      <ConversationInterface
        messages={conversationHistory}
        onSendMessage={handleSendMessage}
        isProcessing={isAgentProcessing}
      />
      
      {/* Tool execution indicators */}
      <ToolExecutionIndicator />
    </div>
  );
};
```

### 4. Insights Pillar: Drill-Down Interface

**New Component:** `components/insights/DrillDownInterface.tsx`

**Purpose:** Display drill-down results from Insights Liaison Agent

```typescript
interface DrillDownInterfaceProps {
  insightSummary: string;  // e.g., "3 customers 90+ days late"
  drillDownQuery: string;  // e.g., "Which ones are they?"
  drillDownResults: DrillDownResult;
}

export function DrillDownInterface({
  insightSummary,
  drillDownQuery,
  drillDownResults
}: DrillDownInterfaceProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Drill-Down Results</CardTitle>
        <CardDescription>
          {insightSummary} → {drillDownQuery}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Display results based on type */}
        {drillDownResults.type === "table" && (
          <DataTable data={drillDownResults.data} />
        )}
        {drillDownResults.type === "list" && (
          <ListDisplay items={drillDownResults.data} />
        )}
        {drillDownResults.type === "summary" && (
          <SummaryDisplay summary={drillDownResults.data} />
        )}
      </CardContent>
    </Card>
  );
}
```

**Integration in Insights Page:**

```typescript
// In insights/page.tsx
const [drillDownResults, setDrillDownResults] = useState(null);

// When user asks drill-down question
const handleDrillDown = async (query: string) => {
  const response = await insightsLiaisonAgent.processQuery(query, analysisId);
  
  if (response.drill_down_results) {
    setDrillDownResults(response.drill_down_results);
  }
};

// Display drill-down interface
{drillDownResults && (
  <DrillDownInterface
    insightSummary={currentInsightSummary}
    drillDownQuery={lastQuery}
    drillDownResults={drillDownResults}
  />
)}
```

### 5. Operations Pillar: Conversational SOP Creation

**New Component:** `components/operations/ConversationalSOPCreation.tsx`

**Purpose:** Multi-turn conversation for SOP creation

```typescript
export function ConversationalSOPCreation() {
  const [conversationStage, setConversationStage] = useState<
    "description" | "clarification" | "review" | "complete"
  >("description");
  const [sopDraft, setSopDraft] = useState(null);
  
  const handleAgentResponse = (response: AgentResponse) => {
    // Update conversation stage based on agent's response
    if (response.stage) {
      setConversationStage(response.stage);
    }
    
    // Update SOP draft if agent created one
    if (response.sop_draft) {
      setSopDraft(response.sop_draft);
    }
  };
  
  return (
    <div className="conversational-sop-creation">
      <ConversationStageIndicator stage={conversationStage} />
      
      <ConversationInterface
        onAgentResponse={handleAgentResponse}
        context={{ stage: conversationStage, sop_draft: sopDraft }}
      />
      
      {sopDraft && (
        <SOPDraftPreview draft={sopDraft} />
      )}
    </div>
  );
}
```

### 6. Business Outcomes Pillar: Strategic Planning Interface

**New Component:** `components/business-outcomes/StrategicPlanningConversation.tsx`

**Purpose:** Conversational strategic planning

```typescript
export function StrategicPlanningConversation() {
  const [planningStage, setPlanningStage] = useState<
    "goals" | "context" | "constraints" | "roadmap" | "complete"
  >("goals");
  const [strategicPlan, setStrategicPlan] = useState(null);
  
  return (
    <div className="strategic-planning-conversation">
      <PlanningStageProgress stages={planningStages} current={planningStage} />
      
      <ConversationInterface
        agentType="business_outcomes_liaison"
        context={{ stage: planningStage }}
        onPlanGenerated={(plan) => setStrategicPlan(plan)}
      />
      
      {strategicPlan && (
        <StrategicPlanDisplay plan={strategicPlan} />
      )}
    </div>
  );
}
```

## New UI Components Required

### 1. SpecializationContextBadge

**File:** `components/ui/specialization-context-badge.tsx`

```typescript
export function SpecializationContextBadge({
  context
}: { context: SpecializationContext }) {
  return (
    <Badge variant="outline" className="specialization-badge">
      <span>Domain: {context.business_domain}</span>
      <span>•</span>
      <span>Focus: {context.focus_areas?.join(", ")}</span>
    </Badge>
  );
}
```

### 2. ToolCallIndicator

**File:** `components/ui/tool-call-indicator.tsx`

```typescript
export function ToolCallIndicator({
  toolCalls
}: { toolCalls: ToolCall[] }) {
  return (
    <div className="tool-call-indicator">
      {toolCalls.map((call, idx) => (
        <div key={idx} className="tool-call">
          <Loader2 className="animate-spin" />
          <span>Calling {call.tool_name}...</span>
        </div>
      ))}
    </div>
  );
}
```

### 3. StructuredContentRenderer

**File:** `components/ui/structured-content-renderer.tsx`

```typescript
export function StructuredContentRenderer({
  content
}: { content: StructuredContent }) {
  switch (content.type) {
    case "table":
      return <DataTable data={content.data} />;
    case "chart":
      return <Chart data={content.data} />;
    case "list":
      return <List items={content.data} />;
    case "summary":
      return <Summary text={content.data} />;
    default:
      return <div>{JSON.stringify(content.data)}</div>;
  }
}
```

### 4. ConversationStageIndicator

**File:** `components/ui/conversation-stage-indicator.tsx`

```typescript
export function ConversationStageIndicator({
  stages,
  current
}: { stages: string[], current: string }) {
  return (
    <div className="stage-indicator">
      {stages.map((stage, idx) => (
        <div
          key={stage}
          className={`stage ${stage === current ? "active" : ""} ${
            stages.indexOf(current) > idx ? "complete" : ""
          }`}
        >
          {stage}
        </div>
      ))}
    </div>
  );
}
```

### 5. SuggestedActions

**File:** `components/ui/suggested-actions.tsx`

```typescript
export function SuggestedActions({
  actions
}: { actions: SuggestedAction[] }) {
  return (
    <div className="suggested-actions">
      {actions.map((action, idx) => (
        <Button
          key={idx}
          variant="outline"
          onClick={() => handleAction(action)}
        >
          {action.label}
        </Button>
      ))}
    </div>
  );
}
```

## API Integration Changes

### 1. Guide Agent API (Journey Orchestrator)

**Current:** WebSocket to `/api/ws/guide`

**Updated:** WebSocket to `/api/ws/journey` (Journey Orchestrator)

**Message Format:**
```typescript
// Send
{
  type: "message",
  data: {
    message: string,
    session_id: string,
    conversation_stage?: "landing_page" | "pillar_navigation"
  }
}

// Receive
{
  type: "chat_response",
  agent_type: "guide",
  message: string,
  specialization_context?: SpecializationContext,
  suggested_next_steps?: string[]
}
```

### 2. Liaison Agent APIs

**New Endpoints:**

**Content Liaison Agent:**
- `POST /api/v1/content-pillar/liaison-agent/query`
- `GET /api/v1/content-pillar/liaison-agent/context`

**Insights Liaison Agent:**
- `POST /api/v1/insights-pillar/liaison-agent/query`
- `POST /api/v1/insights-pillar/liaison-agent/drill-down`

**Operations Liaison Agent:**
- `POST /api/v1/operations-pillar/liaison-agent/query`
- `POST /api/v1/operations-pillar/liaison-agent/sop-creation`

**Business Outcomes Liaison Agent:**
- `POST /api/v1/business-outcomes-pillar/liaison-agent/query`
- `POST /api/v1/business-outcomes-pillar/liaison-agent/strategic-planning`

**Request Format:**
```typescript
{
  message: string,
  session_id: string,
  user_context: {
    user_id: string,
    tenant_id: string
  },
  specialization_context?: SpecializationContext,
  conversation_history?: Message[],
  current_state?: {
    // Pillar-specific state (files, analysis, etc.)
  }
}
```

**Response Format:**
```typescript
{
  success: boolean,
  response: string,
  tool_calls?: ToolCall[],
  structured_content?: StructuredContent,
  suggested_actions?: SuggestedAction[],
  context_updated?: boolean
}
```

### 3. Specialization Context API

**New Endpoints:**

- `GET /api/v1/journey/specialization-context?session_id={id}`
- `POST /api/v1/journey/specialization-context` (store)
- `PUT /api/v1/journey/specialization-context` (update)

## State Management Changes

### 1. Session Context Storage

**Current:** Local component state

**Updated:** Global session state via `GlobalSessionProvider`

```typescript
// In GlobalSessionProvider
interface GlobalSessionState {
  sessionId: string;
  specializationContext: SpecializationContext | null;
  conversationHistory: {
    [agentType: string]: Message[];
  };
  pillarContext: {
    [pillar: string]: any;
  };
}
```

### 2. Agent State Management

**New:** Agent-specific state management

```typescript
// hooks/useAgentState.ts
export function useAgentState(agentType: AgentType) {
  const { sessionId } = useGlobalSession();
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [agentContext, setAgentContext] = useState<any>(null);
  
  // Load conversation history from session
  useEffect(() => {
    loadConversationHistory(agentType, sessionId);
  }, [agentType, sessionId]);
  
  return {
    conversationHistory,
    agentContext,
    addMessage: (message: Message) => {
      setConversationHistory(prev => [...prev, message]);
      // Persist to session
      persistMessage(agentType, sessionId, message);
    }
  };
}
```

## User Experience Enhancements

### 1. Loading States

**New Indicators:**
- Agent thinking indicator (when LLM is processing)
- Tool execution indicator (when tools are running)
- Context loading indicator (when retrieving context)

### 2. Error Handling

**Enhanced Error Display:**
- Agent error messages (user-friendly)
- Tool execution errors
- Context retrieval errors
- Retry mechanisms

### 3. Progress Indicators

**New Components:**
- Conversation progress (for multi-turn flows)
- Journey progress (across pillars)
- Specialization context extraction progress

### 4. Contextual Help

**New Features:**
- Show available capabilities based on context
- Suggest next steps based on conversation
- Display relevant examples

## Testing Considerations

### 1. Component Testing

**New Test Files:**
- `LandingPageConversation.test.tsx`
- `DrillDownInterface.test.tsx`
- `ConversationalSOPCreation.test.tsx`
- `StructuredContentRenderer.test.tsx`

### 2. Integration Testing

**Test Scenarios:**
- Landing page conversation flow
- Specialization context capture and sharing
- Drill-down query flow
- Multi-turn SOP creation
- Strategic planning conversation

### 3. E2E Testing

**Playwright Tests:**
- Complete landing page → pillar journey
- Conversational flows
- Context persistence across navigation
- Agent tool execution

## Implementation Priority

### Phase 1: Core Infrastructure (Week 1-2)
1. Journey Orchestrator integration
2. Enhanced chat interface
3. Specialization context management
4. Basic agent API integration

### Phase 2: Pillar-Specific UI (Week 3-4)
1. Landing page conversation
2. Insights drill-down interface
3. Operations conversational SOP
4. Business Outcomes strategic planning

### Phase 3: Polish & Enhancement (Week 5-6)
1. UI/UX improvements
2. Error handling
3. Loading states
4. Testing & refinement

## Conclusion

The frontend requires significant updates to support the new agentic vision:

1. **Conversational Interfaces**: Replace static forms with chat-based interactions
2. **Agent Integration**: Connect frontend to backend agents via APIs
3. **Context Management**: Share specialization context across components
4. **Structured Responses**: Support tables, charts, and rich content
5. **Tool Execution**: Display agent tool calls and results
6. **Progress Indicators**: Show conversation and journey progress

These changes will enable natural language interaction throughout the platform while maintaining a clean, intuitive user experience.




