# Agentic Enablement Plan: Content Pillar

## Executive Summary

This plan outlines the transformation of the Content Pillar from a service orchestrator pattern to a fully agentic, declarative agent + conversational analytics architecture. The goal is to enable natural language interaction for file management, parsing guidance, and content exploration while maintaining all LLM calls within agents.

## Current State Analysis

### Current Architecture

**Orchestrator Pattern:**
- `ContentAnalysisOrchestrator` - Service orchestrator that delegates to enabling services
- `ContentLiaisonAgent` - Extends `BusinessLiaisonAgentBase` with keyword-based intent analysis
- Enabling Services: `FileParserService`, `DataAnalyzerService`, `MetricsCalculatorService`
- MCP Server: `ContentAnalysisMCPServer` exposes orchestrator methods as tools

**Current Liaison Agent Limitations:**
1. **Simple Keyword Matching**: Uses basic keyword detection (`_analyze_query_intent`) instead of LLM reasoning
2. **No Conversational Context**: Limited conversation history management
3. **No Tool Integration**: Doesn't use MCP tools for orchestrator capabilities
4. **Static Responses**: Pre-written responses, not dynamic based on user context
5. **No Declarative Pattern**: Not using declarative agent configuration

**Current Orchestrator Strengths:**
- Clean service delegation pattern
- Proper infrastructure abstractions
- Good separation of concerns
- MCP tools already exposed

## Target State Vision

### Declarative Agent + Conversational Analytics

**Content Liaison Agent (Declarative):**
- Configuration-driven agent using YAML config
- LLM reasoning for intent understanding and tool selection
- Stateful conversations with context awareness
- MCP tool integration for orchestrator capabilities
- Natural language guidance for file operations

**Conversational Capabilities:**
- "What files do I have?" → Query file list
- "Parse my latest document" → Identify and parse most recent file
- "Show me the structure of file X" → Analyze document structure
- "What format should I use for Y?" → Format conversion guidance
- "Help me understand this metadata" → Explain metadata in plain language

## Implementation Plan

### Phase 1: Convert Content Liaison Agent to Declarative Pattern

**1.1 Create Declarative Agent Configuration**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/agents/configs/content_liaison_agent.yaml`

```yaml
agent_name: ContentLiaisonAgent
role: Content Management Assistant
goal: Help users manage, parse, and understand their content files through natural language interaction
backstory: |
  You are an expert Content Management Assistant. You help users upload files, parse documents,
  extract metadata, convert formats, and understand their content. You maintain conversation context
  to provide personalized guidance and can execute file operations through available tools.
  You explain technical concepts in plain language and suggest best practices for content management.

instructions:
  - Understand user intent for content operations (upload, parse, analyze, convert, validate, metadata)
  - Maintain conversation context to remember user's files and previous operations
  - Use available tools to execute file operations when requested
  - Provide clear, actionable guidance for content management tasks
  - Explain file formats, parsing options, and conversion capabilities
  - Suggest next steps based on user's current context
  - Remember user preferences for file handling

allowed_mcp_servers:
  - ContentAnalysisMCPServer

allowed_tools:
  - handle_content_upload_tool
  - parse_file_tool
  - analyze_document_tool
  - extract_entities_tool
  - list_uploaded_files_tool
  - get_file_details_tool
  - convert_format_tool
  - get_file_metadata_tool

capabilities:
  - file_upload_guidance
  - document_parsing_help
  - format_conversion_advice
  - content_validation_support
  - metadata_extraction_guidance
  - conversational_file_management

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
max_conversation_history: 20

iterative_execution: true
max_iterations: 5

cost_tracking: true
tool_selection_strategy: autonomous
max_tool_calls_per_request: 10
```

**1.2 Refactor ContentLiaisonAgent Class** (UPDATED - Correct Pattern)

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/agents/content_liaison_agent.py`

**Changes:**
- Extend `DeclarativeAgentBase` instead of `BusinessLiaisonAgentBase`
- Remove keyword-based intent analysis (`_analyze_query_intent`)
- Use `handle_user_query()` → `process_request()` delegation pattern
- Accept `**kwargs` to ignore orchestrator parameters
- **CRITICAL**: Don't manually retrieve context - base class handles it if `stateful: true`

**✅ CORRECT Implementation:**
```python
class ContentLiaisonAgent(DeclarativeAgentBase):
    def __init__(self, agent_config_path: str = None, **kwargs):
        """Initialize Content Liaison Agent with declarative configuration."""
        # Get configuration file path
        if agent_config_path is None:
            config_path = Path(__file__).parent / "configs" / "content_liaison_agent.yaml"
        else:
            config_path = Path(agent_config_path)
        
        # Initialize declarative agent base
        super().__init__(
            agent_config_path=str(config_path),
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            public_works_foundation=public_works_foundation,
            logger=logger or logging.getLogger("ContentLiaisonAgent"),
            **kwargs  # Accept and ignore orchestrator params
        )
    
    async def handle_user_query(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user query using declarative agent's LLM reasoning.
        
        This method acts as the public interface, delegating to process_request().
        Base class handles conversation history automatically if stateful: true.
        
        Args:
            request: User request containing:
                - message: User message
                - user_context: User context
                - session_id: Optional session ID
                - conversation_history: Optional (base class manages if stateful)
                - specialization_context: Optional (from Journey Orchestrator)
                - pillar_context: Optional (from session)
        
        Returns:
            Response with guidance, actions, and results.
        """
        # Base class handles conversation history if stateful: true
        # Context should be passed in request dict, not retrieved manually
        result = await self.process_request(request)
        
        # Format response (extract intent, suggested actions, etc.)
        response = {
            "type": "liaison_response",
            "agent_type": self.agent_name,
            "message": result.get("response", ""),
            "intent": self._extract_intent(result),
            "suggested_actions": self._extract_suggested_actions(result)
        }
        
        # Preserve metadata
        if "cost_info" in result:
            response["cost_info"] = result["cost_info"]
        if "conversation_history_length" in result:
            response["conversation_history_length"] = result["conversation_history_length"]
        
        return response
```

**1.3 Update Orchestrator Integration** (UPDATED - Correct Pattern)

**✅ CORRECT Pattern:**
```python
# In ContentAnalysisOrchestrator.initialize()
self.liaison_agent = await self.initialize_agent(
    ContentLiaisonAgent,
    "ContentLiaisonAgent",
    agent_type="liaison",
    capabilities=["file_management", "parsing_guidance", "format_conversion"],
    required_roles=[]
)
```

**❌ WRONG Pattern (from old plans):**
```python
# Don't instantiate directly
self.liaison_agent = ContentLiaisonAgent(...)
# Don't manually set orchestrator
self.liaison_agent.set_orchestrator(self)
```

**Notes:**
- Agent is automatically initialized with orchestrator reference via `initialize_agent()`
- MCP tools are automatically discovered via orchestrator's MCP server
- Test agent → orchestrator → service flow

### Phase 2: Enhance MCP Tools for Conversational Operations

**2.1 Add Conversational Query Tools**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/content_analysis_orchestrator/mcp_server/content_analysis_mcp_server.py`

**New Tools:**
```python
@mcp_tool
async def query_file_list_tool(
    query_params: Dict[str, Any],  # Structured from agent LLM
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Query file list with natural language filters.
    
    Agent LLM extracts: filters, sort_by, limit
    """
    # Get ContentQueryService via orchestrator
    service = await self.orchestrator.get_enabling_service("ContentQueryService")
    if not service:
        return {"success": False, "error": "ContentQueryService not available"}
    
    # Call service with structured params (NO LLM in service)
    return await service.query_files(
        filter_criteria=query_params.get("filters", {}),
        sort_options=query_params.get("sort", {}),
        limit=query_params.get("limit", 100),
        user_context=user_context
    )

@mcp_tool
async def get_file_guidance_tool(
    file_id: str,
    guidance_type: str,  # "parsing", "format", "metadata", "conversion"
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get guidance about file operations.
    
    Returns best practices, options, recommendations.
    """
    pass

@mcp_tool
async def explain_metadata_tool(
    file_id: str,
    metadata_fields: List[str],  # Optional: specific fields to explain
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Explain file metadata in plain language.
    
    Agent uses this to help users understand their file properties.
    """
    pass
```

**2.2 Enhance Existing Tools**

- Add structured parameter support (extracted by agent LLM)
- Improve error messages for agent context
- Add metadata and guidance information to responses

### Phase 3: Create Content Query Service (Pure Service)

**3.1 New Enabling Service: ContentQueryService**

**File:** `backend/business_enablement/enabling_services/content_query_service/`

**Purpose:** Pure data processing service for content queries (NO LLM)

**Capabilities:**
- Query file lists with filters
- Get file recommendations based on context
- Format guidance (what format to use for what purpose)
- Metadata explanation (structured explanations, not LLM-generated)

**Key Methods:**
```python
async def query_files(
    filter_criteria: Dict[str, Any],  # Structured from agent
    sort_options: Dict[str, Any],
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Query files with structured filters."""
    pass

async def get_format_guidance(
    source_format: str,
    target_purpose: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """Get format conversion guidance (rule-based)."""
    pass

async def explain_metadata_structure(
    file_type: str,
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Explain metadata structure (rule-based templates)."""
    pass
```

### Phase 4: Enhance Orchestrator for Conversational Context (UPDATED - Simplified)

**4.1 Context Management (Simplified)**

- **Context is passed in `request` dict**, not retrieved manually
- Track user's file operations in session (via Session Manager)
- Store user preferences in knowledge base (for agent learning)
- Base class handles conversation history automatically if `stateful: true`

**4.2 Conversational Helpers**

- Methods to get "latest file", "recent operations" (in orchestrator or service)
- Context-aware responses (e.g., "your latest document" resolved by agent LLM)
- Agent uses context from `request` dict to resolve references

**4.3 Agent Learning (NEW - Enhancement)**

- Store user preferences in knowledge base
- Learn format preferences, parsing patterns
- Retrieve learned patterns to personalize responses
- See `AGENTIC_PLATFORM_ENHANCEMENT_OPPORTUNITIES.md` for details

## Concrete Improvements

### Improvement 1: Natural Language File Queries

**Current:** User must know exact file names/IDs
**Enhanced:** "Show me my PDF files" → Agent uses LLM to extract intent, calls `query_file_list_tool` with filters

**Implementation:**
1. Agent LLM extracts: `{"file_type": "pdf", "sort_by": "uploaded_at", "limit": 10}`
2. Calls `query_file_list_tool` with structured params
3. Formats response: "You have 5 PDF files. Here are the most recent..."

### Improvement 2: Conversational Parsing Guidance

**Current:** Static help text
**Enhanced:** Context-aware guidance based on user's files and goals

**Example Flow:**
```
User: "I uploaded a COBOL file. What should I do next?"
Agent (LLM reasoning):
  - Intent: parsing_guidance
  - Context: COBOL file uploaded
  - Action: Explain COBOL parsing options, suggest copybook if needed
  - Tool: get_file_guidance_tool(file_id, "parsing")
Response: "For COBOL files, you'll need a copybook file to parse the data structure. 
          Would you like me to help you upload a copybook, or do you have one ready?"
```

### Improvement 3: Intelligent Format Recommendations

**Current:** User must know which format to use
**Enhanced:** Agent recommends formats based on use case

**Example:**
```
User: "I want to analyze this data in Python"
Agent:
  - Understands: Python analysis → needs structured format
  - Recommends: "For Python analysis, I recommend converting to parquet or JSON structured format. 
                Parquet is better for large datasets, JSON structured is better for smaller files. 
                Which would you prefer?"
  - Tool: get_format_guidance_tool(source_format, "python_analysis")
```

### Improvement 4: Context-Aware Operations

**Current:** User must specify file IDs
**Enhanced:** Agent remembers context ("parse my latest file")

**Implementation:**
- Agent maintains conversation context
- Tracks "latest file", "recent operations"
- LLM resolves references: "my latest file" → actual file_id from context

## MCP Tools Required

### New Tools

1. **`query_file_list_tool`**
   - Purpose: Query files with natural language filters
   - Input: Structured query params from agent LLM
   - Output: Filtered file list

2. **`get_file_guidance_tool`**
   - Purpose: Get guidance for file operations
   - Input: file_id, guidance_type
   - Output: Guidance information

3. **`explain_metadata_tool`**
   - Purpose: Explain file metadata in plain language
   - Input: file_id, optional metadata_fields
   - Output: Plain language explanation

4. **`recommend_format_tool`**
   - Purpose: Recommend file formats for use cases
   - Input: source_format, target_purpose
   - Output: Format recommendations

### Enhanced Existing Tools

- `handle_content_upload_tool` - Add guidance and validation feedback
- `parse_file_tool` - Add parsing option recommendations
- `analyze_document_tool` - Add analysis type suggestions
- `convert_format_tool` - Add format conversion guidance

## Service Enhancements

### New Service: ContentQueryService

**Location:** `backend/business_enablement/enabling_services/content_query_service/`

**Purpose:** Pure data processing for content queries (NO LLM)

**Methods:**
- `query_files()` - Structured file queries
- `get_format_guidance()` - Format recommendations (rule-based)
- `explain_metadata_structure()` - Metadata explanations (template-based)
- `get_parsing_recommendations()` - Parsing option suggestions

## Testing Scenarios

### Scenario 1: Natural Language File Management

```
User: "What files do I have?"
Agent: [LLM extracts intent → calls query_file_list_tool]
Response: "You have 3 files: invoice.pdf (uploaded today), data.csv (2 days ago), report.docx (1 week ago)"

User: "Parse the invoice"
Agent: [LLM resolves "invoice" → file_id, calls parse_file_tool]
Response: "I've started parsing invoice.pdf. This will extract the text and structure..."
```

### Scenario 2: Conversational Parsing Guidance

```
User: "I uploaded a COBOL file. Help me parse it."
Agent: [LLM understands COBOL parsing needs copybook → calls get_file_guidance_tool]
Response: "COBOL files need a copybook file to define the data structure. Do you have a copybook file ready?"

User: "Yes, I'll upload it now"
Agent: [Waits for upload, then guides through parsing]
Response: "Great! Once you upload the copybook, I can parse your COBOL file. The copybook will help me understand the data structure..."
```

### Scenario 3: Format Conversion Guidance

```
User: "I want to analyze this CSV in Python. What format should I use?"
Agent: [LLM understands Python analysis → calls recommend_format_tool]
Response: "For Python analysis, I recommend parquet format for better performance with large datasets, 
          or JSON structured format for easier integration. Which would you prefer?"

User: "Parquet sounds good"
Agent: [Calls convert_format_tool with parquet]
Response: "Converting your CSV to parquet format. This will optimize it for Python pandas analysis..."
```

## Success Metrics

1. **Conversational Quality:**
   - Users can complete file operations using natural language
   - Agent correctly resolves file references ("my latest file")
   - Guidance is context-aware and helpful

2. **Tool Integration:**
   - Agent successfully calls orchestrator tools
   - Tool results are properly formatted for users
   - Error handling provides actionable feedback

3. **Context Management:**
   - Conversation history maintained across turns
   - User preferences remembered
   - File operation context preserved

## Implementation Timeline (UPDATED)

**Week 1-2:** Phase 1 - Convert to Declarative Agent
- Create YAML config in `agents/configs/content_liaison_agent.yaml`
- Refactor agent class to extend `DeclarativeAgentBase`
- Update orchestrator to use `initialize_agent()` pattern
- Replace custom methods with `handle_user_query()` → `process_request()`
- Remove manual context management (base class handles it)
- Test basic LLM reasoning

**Week 3:** Phase 2 - Enhance MCP Tools
- Add conversational query tools
- Enhance existing tools to accept structured params
- Test tool integration via orchestrator's MCP server

**Week 4:** Phase 3 - Create ContentQueryService
- Implement pure service (NO LLM)
- Add rule-based guidance
- Integrate with orchestrator
- Test service purity

**Week 5:** Phase 4 - Context Management (Simplified)
- Pass context in `request` dict (not retrieved manually)
- Store user preferences in knowledge base
- Test end-to-end flows

**Week 6:** Testing & Refinement
- Test all scenarios
- Refine prompts and guidance
- Performance optimization

**Future Enhancements (Weeks 7-12):**
- Agent-to-Agent Collaboration (Content agent can call Insights agent)
- Agent Learning (learn user preferences, store in knowledge base)
- Cross-Pillar Collaboration (Content + Insights workflows)
- See `AGENTIC_PLATFORM_ENHANCEMENT_OPPORTUNITIES.md` for details

## Dependencies

### Foundation Dependencies (Already Exist)
- `DeclarativeAgentBase` - Base class for declarative agents ✅
- `OrchestratorBase` - Base class for orchestrators (provides `initialize_agent()`) ✅
- `ContentAnalysisOrchestrator` MCP Server - Tool exposure ✅
- Session Manager - Context persistence ✅

### New Dependencies (To Be Created)
- `ContentQueryService` - Pure service for content queries (NO LLM)

### Enhancement Dependencies (Future)
- Knowledge base integration for agent learning
- Agent-to-Agent communication infrastructure
- User preference storage

## Risks & Mitigations

**Risk 1:** LLM reasoning may be slower than keyword matching
- **Mitigation:** Use gpt-4o-mini for faster responses, cache common queries

**Risk 2:** Agent may make incorrect tool calls
- **Mitigation:** Validate tool calls, provide clear error messages, iterative execution for complex queries

**Risk 3:** Context management complexity
- **Mitigation:** Use session manager for persistence, keep agent context lightweight


