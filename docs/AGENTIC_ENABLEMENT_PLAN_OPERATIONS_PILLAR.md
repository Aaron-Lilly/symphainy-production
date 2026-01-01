# Agentic Enablement Plan: Operations Pillar

## Executive Summary

This plan transforms the Operations Pillar to enable conversational process design, SOP creation guidance, workflow optimization, and coexistence analysis through declarative agents. Users can describe processes in natural language, get guided SOP creation, and receive intelligent recommendations for AI-human coexistence patterns.

## Current State Analysis

### Current Architecture

**Orchestrator Pattern:**
- `OperationsOrchestrator` - Service orchestrator for operations management
- `OperationsLiaisonAgent` - Extends `BusinessLiaisonAgentBase` with keyword-based intent analysis
- `OperationsSpecialistAgent` - Specialist agent for process optimization
- Enabling Services: `WorkflowConversionService`, `CoexistenceAnalysisService`, `SOPBuilderService`
- MCP Server: `OperationsMCPServer` exposes orchestrator methods

**Current Liaison Agent Limitations:**
1. **Simple Intent Analysis**: Uses `_analyze_intent()` with keyword matching
2. **No LLM Reasoning**: Static responses, no dynamic process understanding
3. **Limited Context**: Can't maintain complex multi-turn conversations for SOP creation
4. **No Tool Integration**: Doesn't use MCP tools for orchestrator capabilities
5. **Static Guidance**: Pre-written help text, not context-aware

**Current Strengths:**
- Good service delegation pattern
- Specialist agent for complex operations
- MCP tools already exposed
- Wizard pattern for SOP creation

## Target State Vision

### Declarative Agent + Conversational Process Design

**Operations Liaison Agent (Declarative):**
- LLM reasoning for understanding process descriptions
- Conversational SOP creation with guided wizard
- Natural language workflow design
- Intelligent coexistence analysis recommendations

**Conversational Capabilities:**
- "I want to create an SOP for customer onboarding" → Guided SOP creation
- "Convert this SOP to a workflow" → Workflow generation with recommendations
- "Help me design an AI-human coexistence process" → Coexistence blueprint generation
- "Optimize this workflow" → Process optimization with suggestions
- "What's the best way to automate this step?" → Automation recommendations

## Implementation Plan

### Phase 1: Convert Operations Liaison Agent to Declarative Pattern

**1.1 Create Declarative Agent Configuration**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/agents/configs/operations_liaison_agent.yaml`

```yaml
agent_name: OperationsLiaisonAgent
role: Operations Process Assistant
goal: Help users design, document, and optimize business processes through conversational interaction
backstory: |
  You are an expert Operations Process Assistant. You help users create Standard Operating Procedures (SOPs),
  convert processes to workflows, analyze AI-human coexistence patterns, and optimize business processes.
  You guide users through process design using natural language, ask clarifying questions, and provide
  intelligent recommendations. You maintain conversation context to support multi-turn process design
  conversations and remember user preferences for process patterns.

instructions:
  - Understand user intent for operations tasks (sop_creation, workflow_conversion, coexistence_analysis, process_optimization, visualization)
  - Guide users through SOP creation with clarifying questions
  - Convert process descriptions to structured SOPs and workflows
  - Analyze and recommend AI-human coexistence patterns
  - Provide process optimization suggestions
  - Maintain conversation context for multi-turn process design
  - Explain technical concepts (workflows, SOPs, coexistence) in plain language
  - Suggest best practices for process design

allowed_mcp_servers:
  - OperationsMCPServer

allowed_tools:
  - start_sop_wizard_tool
  - wizard_chat_tool
  - wizard_publish_tool
  - generate_workflow_from_sop_tool
  - generate_sop_from_workflow_tool
  - analyze_coexistence_content_tool
  - optimize_process_tool
  - visualize_workflow_tool
  - get_process_recommendations_tool

capabilities:
  - conversational_sop_creation
  - workflow_design_guidance
  - coexistence_analysis
  - process_optimization
  - workflow_visualization
  - process_recommendations

llm_config:
  model: gpt-4o-mini
  temperature: 0.3
  max_tokens: 2000
  timeout: 120
  retry:
    enabled: true
    max_attempts: 3
    base_delay: 2.0

stateful: true
max_conversation_history: 30  # More history for process design conversations

iterative_execution: true  # Enable for multi-step process design
max_iterations: 5

cost_tracking: true
tool_selection_strategy: autonomous
max_tool_calls_per_request: 10
```

**1.2 Refactor OperationsLiaisonAgent Class** (UPDATED - Correct Pattern)

**Changes:**
- Extend `DeclarativeAgentBase` instead of `BusinessLiaisonAgentBase`
- Remove keyword-based intent analysis (`_analyze_intent`)
- Use `handle_user_query()` → `process_request()` delegation pattern
- Accept `**kwargs` to ignore orchestrator parameters
- **CRITICAL**: Don't manually retrieve context - base class handles it if `stateful: true`

**✅ CORRECT Implementation:**
```python
class OperationsLiaisonAgent(DeclarativeAgentBase):
    def __init__(self, agent_config_path: str = None, **kwargs):
        """Initialize Operations Liaison Agent with declarative configuration."""
        if agent_config_path is None:
            config_path = Path(__file__).parent / "configs" / "operations_liaison_agent.yaml"
        else:
            config_path = Path(agent_config_path)
        
        super().__init__(
            agent_config_path=str(config_path),
            foundation_services=foundation_services,
            # ... other dependencies
            **kwargs  # Accept and ignore orchestrator params
        )
    
    async def handle_user_query(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle operations query using declarative agent's LLM reasoning.
        
        Base class handles conversation history automatically if stateful: true.
        Context should be passed in request dict, not retrieved manually.
        
        Args:
            request: User request containing:
                - message: User query
                - session_id: Optional session ID
                - user_context: User context
                - conversation_history: Optional (base class manages if stateful)
                - session_context: Optional (files, current SOP/workflow state)
        
        Returns:
            Response with process guidance, SOP/workflow results, and recommendations.
        """
        # Base class handles conversation history if stateful: true
        result = await self.process_request(request)
        
        # Format response
        response = {
            "type": "operations_response",
            "agent_type": self.agent_name,
            "message": result.get("response", ""),
            "sop_results": result.get("sop_results", []),
            "workflow_results": result.get("workflow_results", [])
        }
        
        return response
```

**1.3 Update Orchestrator Integration** (UPDATED - Correct Pattern)

**✅ CORRECT Pattern:**
```python
# In OperationsOrchestrator.initialize()
self.liaison_agent = await self.initialize_agent(
    OperationsLiaisonAgent,
    "OperationsLiaisonAgent",
    agent_type="liaison",
    capabilities=["sop_creation", "workflow_design", "coexistence_analysis"],
    required_roles=[]
)
```

### Phase 2: Enhance MCP Tools for Conversational Operations

**2.1 Add Conversational Process Design Tools**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/mcp_server/operations_mcp_server.py`

**New Tools:**

```python
@mcp_tool
async def create_sop_from_description_tool(
    description: str,  # User's process description
    sop_type: str,  # "technical", "administrative", "standard"
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create SOP from natural language description.
    
    Agent uses this when user describes a process.
    """
    # Call SOP Builder Service
    pass

@mcp_tool
async def get_process_recommendations_tool(
    process_description: str,
    recommendation_type: str,  # "optimization", "automation", "coexistence"
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get recommendations for process design.
    
    Returns best practices, optimization suggestions, automation opportunities.
    """
    pass

@mcp_tool
async def analyze_process_for_coexistence_tool(
    process_description: str,
    current_state: Optional[Dict[str, Any]],  # Current process if exists
    target_state: Optional[Dict[str, Any]],  # Desired state
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze process for AI-human coexistence opportunities.
    
    Returns coexistence patterns, recommendations, blueprint suggestions.
    """
    pass

@mcp_tool
async def suggest_workflow_pattern_tool(
    sop_content: str,
    process_type: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Suggest best workflow pattern for SOP.
    
    Returns: sequential, parallel, conditional, iterative, or hybrid
    """
    pass
```

**2.2 Enhance Existing Tools**

- `start_sop_wizard_tool` - Add context from conversation
- `generate_workflow_from_sop_tool` - Add pattern recommendations
- `analyze_coexistence_content_tool` - Add intelligent recommendations

### Phase 3: Create Process Design Service (Pure Service)

**3.1 New Enabling Service: ProcessDesignService**

**File:** `backend/business_enablement/enabling_services/process_design_service/`

**Purpose:** Pure service for process design recommendations (NO LLM)

**Key Methods:**
```python
async def get_process_recommendations(
    self,
    process_description: str,
    recommendation_type: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get process design recommendations (rule-based patterns).
    
    Returns best practices, common patterns, optimization suggestions.
    """
    pass

async def suggest_workflow_pattern(
    self,
    process_steps: List[Dict[str, Any]],
    process_type: str
) -> Dict[str, Any]:
    """
    Suggest workflow pattern based on process structure.
    
    Rule-based analysis of process steps.
    """
    pass

async def identify_automation_opportunities(
    self,
    process_steps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Identify steps that could be automated.
    
    Rule-based pattern matching for automation candidates.
    """
    pass

async def get_coexistence_patterns(
    self,
    process_type: str,
    complexity: str
) -> Dict[str, Any]:
    """
    Get recommended coexistence patterns for process type.
    
    Returns pattern library (rule-based).
    """
    pass
```

### Phase 4: Enhance SOP Builder for Conversational Creation

**4.1 Conversational SOP Creation Flow**

**Current:** Wizard with structured steps
**Enhanced:** Natural language conversation with LLM-guided questions

**Flow:**
```
User: "I want to create an SOP for customer onboarding"
Agent (LLM reasoning):
  - Intent: sop_creation
  - Action: Start conversational SOP creation
  - Tool: create_sop_from_description_tool(description, ...)
  
Agent: "Great! Let me help you create an SOP for customer onboarding. 
        To get started, can you describe the main steps in your current onboarding process?"

User: "First we collect customer information, then we verify their identity, 
       then we set up their account, and finally we send a welcome email"

Agent (LLM reasoning):
  - Extracts: 4 steps identified
  - Action: Ask for more details on each step
  - Tool: (internal processing, no tool call yet)
  
Agent: "Perfect! I've identified 4 main steps. Let me ask a few questions to make this SOP comprehensive:
        1. For identity verification, what documents do you require?
        2. For account setup, what systems need to be configured?
        3. Are there any approval steps or quality checks?"

User: [Answers questions]

Agent: [Uses answers to create structured SOP]
        [Calls wizard_publish_tool when ready]
        
Response: "I've created your customer onboarding SOP with 4 detailed steps. 
           Would you like me to convert it to a workflow, or make any adjustments?"
```

**4.2 Multi-Turn Process Design**

- Agent asks clarifying questions
- Maintains context across turns
- Builds SOP incrementally
- Validates completeness before publishing

## Concrete Improvements

### Improvement 1: Natural Language Process Description

**Current:** User must use structured wizard
**Enhanced:** User describes process in natural language

**Example:**
```
User: "I want to document our order fulfillment process. We receive orders, 
       check inventory, pick items, pack them, and ship them out."

Agent (LLM reasoning):
  - Intent: sop_creation
  - Extracts: 5 steps (receive, check, pick, pack, ship)
  - Action: Create SOP structure, ask for details
  - Tool: create_sop_from_description_tool(description, "standard")
  
Agent: "I've identified 5 steps in your order fulfillment process. 
        Let me create a draft SOP. For each step, I'd like to know:
        - Who is responsible?
        - What systems are used?
        - Are there any quality checks?"
```

### Improvement 2: Intelligent Workflow Pattern Suggestions

**Current:** User must know workflow patterns
**Enhanced:** Agent suggests best pattern based on process

**Example:**
```
User: "Convert this SOP to a workflow"
Agent (LLM reasoning):
  - Analyzes SOP structure
  - Identifies: Some steps can run in parallel, some need sequential order
  - Tool: suggest_workflow_pattern_tool(sop_content, ...)
  - Recommendation: "Hybrid pattern - steps 1-2 sequential, steps 3-4 parallel"
  
Agent: "Based on your SOP structure, I recommend a hybrid workflow pattern:
        - Steps 1-2 (receive order, check inventory) must be sequential
        - Steps 3-4 (pick items, pack items) can run in parallel
        - Step 5 (ship) waits for both 3 and 4 to complete
        
        Would you like me to generate this workflow?"
```

### Improvement 3: Conversational Coexistence Analysis

**Current:** User uploads files, gets analysis
**Enhanced:** Agent guides through coexistence design conversationally

**Example:**
```
User: "Help me design an AI-human coexistence process for customer support"

Agent (LLM reasoning):
  - Intent: coexistence_design
  - Action: Start conversational coexistence design
  - Tool: analyze_process_for_coexistence_tool(description, ...)
  
Agent: "Great! Let's design an optimal AI-human coexistence pattern for customer support.
        First, let me understand your current process:
        1. How do you currently handle customer inquiries?
        2. What tasks do humans do today?
        3. What tasks could AI assist with?"

User: [Describes current process]

Agent: [Analyzes, suggests coexistence patterns]
        "Based on your process, I recommend a 'Collaborative' coexistence pattern:
         - AI handles initial inquiry classification and routing
         - AI provides suggested responses for common questions
         - Humans review and personalize responses
         - AI handles follow-up and satisfaction surveys
         
         This pattern would reduce human workload by 40% while maintaining quality.
         Would you like me to create a detailed coexistence blueprint?"
```

### Improvement 4: Context-Aware Process Optimization

**Current:** Generic optimization suggestions
**Enhanced:** Agent analyzes specific process and provides targeted recommendations

**Example:**
```
User: "How can I optimize my order fulfillment process?"

Agent (LLM reasoning):
  - Intent: process_optimization
  - Context: User has order fulfillment SOP
  - Action: Analyze process, identify optimization opportunities
  - Tool: get_process_recommendations_tool(process_description, "optimization")
  
Agent: "I've analyzed your order fulfillment process. Here are my recommendations:
        1. **Automation Opportunity**: Inventory checking can be automated (saves 15 min/order)
        2. **Parallelization**: Picking and packing prep can run in parallel (saves 10 min/order)
        3. **Bottleneck**: Shipping label generation is sequential - can be parallelized
        4. **Quality Check**: Add automated validation before shipping (prevents errors)
        
        Implementing these would reduce process time by 35% and error rate by 20%.
        Would you like me to create an optimized version of your workflow?"
```

## MCP Tools Required

### New Tools

1. **`create_sop_from_description_tool`**
   - Purpose: Create SOP from natural language description
   - Input: description, sop_type
   - Output: SOP structure

2. **`get_process_recommendations_tool`**
   - Purpose: Get process design recommendations
   - Input: process_description, recommendation_type
   - Output: Recommendations

3. **`analyze_process_for_coexistence_tool`**
   - Purpose: Analyze process for coexistence opportunities
   - Input: process_description, current_state, target_state
   - Output: Coexistence analysis

4. **`suggest_workflow_pattern_tool`**
   - Purpose: Suggest workflow pattern for SOP
   - Input: sop_content, process_type
   - Output: Pattern recommendation

5. **`identify_automation_opportunities_tool`**
   - Purpose: Identify automation candidates
   - Input: process_steps
   - Output: Automation opportunities

### Enhanced Existing Tools

- `start_sop_wizard_tool` - Add conversational context
- `generate_workflow_from_sop_tool` - Add pattern recommendations
- `analyze_coexistence_content_tool` - Add intelligent analysis
- `optimize_process_tool` - Add targeted recommendations

## Service Enhancements

### New Service: ProcessDesignService

**Location:** `backend/business_enablement/enabling_services/process_design_service/`

**Purpose:** Pure service for process design recommendations (NO LLM)

**Key Methods:**
- `get_process_recommendations()` - Rule-based recommendations
- `suggest_workflow_pattern()` - Pattern suggestions
- `identify_automation_opportunities()` - Automation analysis
- `get_coexistence_patterns()` - Coexistence pattern library

### Enhanced Service: SOPBuilderService

**Changes:**
- Support conversational SOP creation
- Accept natural language descriptions
- Generate structured SOPs from descriptions
- Maintain conversation state for multi-turn creation

## Testing Scenarios

### Scenario 1: Conversational SOP Creation

```
User: "I want to create an SOP for our customer refund process"

Agent: "I'd be happy to help! Can you describe the main steps in your refund process?"

User: "First we receive the refund request, then we verify the purchase, 
       check if it's within the return window, process the refund, and notify the customer"

Agent: [LLM extracts 5 steps, asks for details]
       "I've identified 5 steps. For each step, I need:
        - Who handles it?
        - What systems are used?
        - Any approval requirements?"

User: [Provides details]

Agent: [Creates structured SOP]
       "I've created your refund process SOP. It includes:
        - 5 detailed steps with responsibilities
        - System integration points
        - Approval workflows
        - Quality checkpoints
        
        Would you like to review it, convert it to a workflow, or make changes?"
```

### Scenario 2: Intelligent Workflow Conversion

```
User: "Convert my order fulfillment SOP to a workflow"

Agent: [Analyzes SOP structure]
       "I've analyzed your SOP. I recommend a hybrid workflow pattern:
        - Sequential: Receive order → Check inventory (must be in order)
        - Parallel: Pick items || Pack items (can run simultaneously)
        - Sequential: Ship (waits for both pick and pack)
        
        This pattern will reduce processing time by 25%.
        Should I generate this workflow?"

User: "Yes, that sounds good"

Agent: [Calls generate_workflow_from_sop_tool with pattern recommendation]
       "Workflow generated! It includes:
        - 3 sequential steps
        - 2 parallel branches
        - Automatic dependency management
        
        Would you like to visualize it or make adjustments?"
```

### Scenario 3: Conversational Coexistence Design

```
User: "Help me design AI-human coexistence for our customer support"

Agent: "Let's design an optimal coexistence pattern. First, tell me about your current process:
        - How do you handle customer inquiries today?
        - What tasks take the most time?
        - What are your quality requirements?"

User: "We get about 100 inquiries per day. Agents handle everything - 
       initial response, research, solution, follow-up. Takes about 15 minutes per inquiry.
       We need 95% customer satisfaction."

Agent: [Analyzes, suggests pattern]
       "Based on your requirements, I recommend a 'Delegated' coexistence pattern:
        - AI handles: Initial inquiry classification (100% accuracy)
        - AI handles: Common question responses (80% of inquiries)
        - Humans handle: Complex issues, escalations, quality review
        - AI handles: Follow-up and satisfaction surveys
        
        This would:
        - Reduce human workload by 60%
        - Maintain 95%+ satisfaction (AI responses reviewed by humans)
        - Reduce average response time from 15 min to 5 min
        
        Would you like me to create a detailed coexistence blueprint?"
```

## Success Metrics

1. **Conversational Quality:**
   - Users can describe processes in natural language
   - Agent asks relevant clarifying questions
   - Multi-turn conversations flow naturally

2. **Process Design Quality:**
   - SOPs created from descriptions are comprehensive
   - Workflow patterns are appropriate
   - Coexistence recommendations are actionable

3. **Context Management:**
   - Conversation context maintained across turns
   - Process state tracked during creation
   - User preferences remembered

## Implementation Timeline

**Week 1-2:** Phase 1 - Convert to Declarative Agent
- Create YAML config
- Refactor agent class
- Test LLM reasoning for process understanding

**Week 3:** Phase 2 - Enhance MCP Tools
- Add conversational process design tools
- Enhance existing tools
- Test tool integration

**Week 4:** Phase 3 - Create ProcessDesignService
- Implement new service
- Add rule-based recommendations
- Integrate with orchestrator

**Week 5:** Phase 4 - Enhance SOP Builder
- Add conversational creation support
- Test multi-turn flows
- Refine prompts

**Week 6:** Testing & Refinement
- Test all scenarios
- Refine process design guidance
- Performance optimization

## Dependencies

- DeclarativeAgentBase (already exists)
- OperationsOrchestrator MCP Server (already exists)
- SOPBuilderService (already exists, needs enhancement)
- New: ProcessDesignService (to be created)

## Risks & Mitigations

**Risk 1:** LLM may not extract process steps correctly
- **Mitigation:** Iterative execution, ask clarifying questions, validate structure

**Risk 2:** Multi-turn conversations may become complex
- **Mitigation:** Clear conversation state management, progress indicators, ability to restart

**Risk 3:** Process recommendations may not be relevant
- **Mitigation:** Rule-based pattern library, user feedback loop, refinement based on context


