# Agentic Enablement Plan: Insights Pillar

## Executive Summary

This plan transforms the Insights Pillar to enable full conversational analytics with drill-down capabilities. Users can ask questions about their data insights and progressively explore details (e.g., "I see I have 3 customers who are more than 90 days late. Which ones are they?"). All LLM reasoning happens in the declarative Insights Liaison Agent, while services remain pure data processing.

## Current State Analysis

### Current Architecture

**Orchestrator Pattern:**
- `InsightsOrchestrator` - Service orchestrator with workflows (structured/unstructured/hybrid)
- `InsightsLiaisonAgent` - Extends `BusinessLiaisonAgentBase` with keyword-based responses
- `InsightsSpecialistAgent` - Specialist agent for data science orchestration
- `DataInsightsQueryService` - Has LLM fallback (needs to be removed - LLM should only be in agents)
- Enabling Services: `DataAnalyzerService`, `MetricsCalculatorService`, `VisualizationEngineService`, `InsightsGeneratorService`
- MCP Server: `InsightsMCPServer` exposes orchestrator methods

**Current Limitations:**
1. **No Conversational Drill-Down**: `DataInsightsQueryService` has basic pattern matching but no true conversational analytics
2. **LLM in Service**: `DataInsightsQueryService._execute_llm_query()` violates architecture (LLM should only be in agents)
3. **No Context Awareness**: Can't handle follow-up questions like "which ones are they?"
4. **Limited Data Access**: Can only query cached analysis, not underlying data sources
5. **Static Responses**: Pre-written responses, not dynamic based on actual data

**Current Strengths:**
- Good workflow patterns (structured/unstructured/hybrid)
- Analysis caching for query support
- Specialist agent for complex analysis
- MCP tools already exposed

## Target State Vision

### Declarative Agent + Conversational Analytics + Data Drill-Down

**Insights Liaison Agent (Declarative):**
- LLM reasoning for understanding data questions
- Conversational context for follow-up questions
- Tool integration for data queries and drill-downs
- Natural language explanations of insights

**Conversational Capabilities:**
- "What are my top customers?" → Query analysis results
- "I see 3 customers 90+ days late. Which ones?" → Drill down into specific records
- "Show me a chart of revenue by month" → Generate visualization
- "What's the trend in customer satisfaction?" → Trend analysis
- "Compare Q1 vs Q2 sales" → Comparative analysis

**Data Drill-Down Flow:**
1. User sees summary insight: "3 customers 90+ days late"
2. User asks: "Which ones are they?"
3. Agent (LLM): Extracts intent → drill_down, entities → {metric: "customers", filter: "90+ days late"}
4. Agent calls: `drill_down_into_data_tool(filter_criteria, ...)`
5. Service queries Data Steward for actual customer records
6. Agent formats response with customer names, amounts, contact info

## Implementation Plan

### Phase 1: Convert Insights Liaison Agent to Declarative Pattern

**1.1 Create Declarative Agent Configuration**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/agents/configs/insights_liaison_agent.yaml`

```yaml
agent_name: InsightsLiaisonAgent
role: Data Insights Assistant
goal: Help users explore and understand their data insights through conversational queries and drill-down analysis
backstory: |
  You are an expert Data Insights Assistant. You help users understand their data analysis results,
  answer questions about insights, and drill down into specific details. You can process natural language
  queries about data, extract specific records, compare metrics, and provide detailed explanations.
  You maintain conversation context to enable follow-up questions and progressive exploration.
  You explain data insights in business terms and help users make data-driven decisions.

instructions:
  - Understand user intent for data queries (drill_down, summary, comparison, filter, trend, visualization)
  - Extract entities from queries (metrics, filters, timeframes, dimensions)
  - Use available tools to query data insights and underlying data sources
  - Maintain conversation context for follow-up questions (e.g., "which ones are they?")
  - Provide clear, structured responses with data tables, lists, or summaries
  - Format responses appropriately (tables for lists, summaries for overviews, charts for visualizations)
  - Suggest relevant follow-up questions based on available data
  - Explain insights in business terms, not just technical metrics

allowed_mcp_servers:
  - InsightsMCPServer

allowed_tools:
  - query_data_insights_tool
  - drill_down_into_data_tool
  - get_data_summary_tool
  - filter_data_records_tool
  - compare_metrics_tool
  - get_data_schema_tool
  - query_raw_data_tool
  - create_visualization_tool
  - analyze_trends_tool

capabilities:
  - conversational_analytics
  - data_insights_query
  - drill_down_analysis
  - data_filtering
  - metric_comparison
  - schema_exploration
  - visualization_guidance
  - trend_analysis

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
max_conversation_history: 30  # More history for complex data conversations

iterative_execution: true  # Enable for multi-step queries
max_iterations: 5

cost_tracking: true
tool_selection_strategy: autonomous
max_tool_calls_per_request: 10
```

**1.2 Refactor InsightsLiaisonAgent Class** (UPDATED - Correct Pattern)

**Changes:**
- Extend `DeclarativeAgentBase` instead of `BusinessLiaisonAgentBase`
- Remove keyword-based responses
- Use `handle_user_query()` → `process_request()` delegation pattern
- Accept `**kwargs` to ignore orchestrator parameters
- **CRITICAL**: Don't manually retrieve context - base class handles it if `stateful: true`

**✅ CORRECT Implementation:**
```python
class InsightsLiaisonAgent(DeclarativeAgentBase):
    def __init__(self, agent_config_path: str = None, **kwargs):
        """Initialize Insights Liaison Agent with declarative configuration."""
        if agent_config_path is None:
            config_path = Path(__file__).parent / "configs" / "insights_liaison_agent.yaml"
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
        Handle data insights query using declarative agent's LLM reasoning.
        
        Base class handles conversation history automatically if stateful: true.
        Context should be passed in request dict, not retrieved manually.
        
        Args:
            request: User request containing:
                - message: User query
                - analysis_id: Optional analysis ID
                - cached_analysis: Optional cached analysis data
                - conversation_id: Optional conversation ID
                - user_context: User context
                - conversation_history: Optional (base class manages if stateful)
                - analytics_context: Optional (from session)
        
        Returns:
            Response with insights, drill-down results, and recommendations.
        """
        # Base class handles conversation history if stateful: true
        # Context should be passed in request dict, not retrieved manually
        result = await self.process_request(request)
        
        # Format response
        response = {
            "type": "insights_response",
            "agent_type": self.agent_name,
            "message": result.get("response", ""),
            "insights": result.get("insights", []),
            "drill_down_results": result.get("drill_down_results", [])
        }
        
        # Preserve metadata
        if "cost_info" in result:
            response["cost_info"] = result["cost_info"]
        
        return response
```

**1.3 Update Orchestrator Integration** (UPDATED - Correct Pattern)

**✅ CORRECT Pattern:**
```python
# In InsightsOrchestrator.initialize()
self.liaison_agent = await self.initialize_agent(
    InsightsLiaisonAgent,
    "InsightsLiaisonAgent",
    agent_type="liaison",
    capabilities=["conversational_analytics", "data_drill_down", "insights_query"],
    required_roles=[]
)
```

### Phase 2: Remove LLM from DataInsightsQueryService (CRITICAL)

**2.1 Refactor DataInsightsQueryService to Pure Service**

**File:** `backend/business_enablement/enabling_services/data_insights_query_service/data_insights_query_service.py`

**⚠️ CRITICAL**: This service currently has `_execute_llm_query()` method which violates architecture (LLM should only be in agents).

**Changes:**
- **REMOVE** `_execute_llm_query()` method completely
- **REMOVE** LLM client initialization
- Accept structured query parameters (extracted by agent LLM)
- Pure data processing only (rule-based routing)

**✅ CORRECT Method Signature:**
```python
async def process_query(
    self,
    query_params: Dict[str, Any],  # Structured from agent LLM
    analysis_id: str,
    cached_analysis: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process query with structured parameters (extracted by agent's LLM).
    
    Args:
        query_params: {
            "intent": "drill_down",
            "entities": {
                "metric": "customers",
                "filter": {
                    "field": "days_overdue",
                    "operator": ">=",
                    "value": 90
                }
            },
            "query_type": "filter"
        }
        analysis_id: Analysis identifier
        cached_analysis: Cached analysis results
        user_context: User context for security/tenant validation
    
    Returns:
        Query results (pure data processing, NO LLM)
    """
    # Pure data processing - no LLM
    intent = query_params.get("intent")
    entities = query_params.get("entities", {})
    
    # Route to appropriate handler (rule-based, not LLM)
    if intent == "drill_down":
        return await self._execute_drill_down(entities, cached_analysis, user_context)
    elif intent == "filter":
        return await self._execute_filter(entities, cached_analysis, user_context)
    elif intent == "top_n_query":
        return await self._execute_top_n(entities, cached_analysis, user_context)
    elif intent == "compare":
        return await self._execute_compare(entities, cached_analysis, user_context)
    # ... etc
    
    return {"success": False, "error": f"Unknown intent: {intent}"}
```

**Validation:**
- ✅ No LLM imports
- ✅ No LLM client initialization
- ✅ No LLM calls anywhere in service
- ✅ Pure rule-based routing

**2.2 Enhance Pattern Matcher**

- Keep rule-based pattern matching for fast responses
- Add more pattern types for drill-down queries
- Improve entity extraction patterns

### Phase 3: Create Data Drill-Down Service

**3.1 New Enabling Service: DataDrillDownService**

**File:** `backend/business_enablement/enabling_services/data_drill_down_service/`

**Purpose:** Pure data access service for detailed record queries (NO LLM)

**Key Methods:**
```python
async def get_filtered_records(
    self,
    filter_criteria: Dict[str, Any],  # Structured from agent LLM
    data_source: str,
    max_results: int = 100,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Get filtered records from data source.
    
    Args:
        filter_criteria: {
            "field": "days_overdue",
            "operator": ">=",
            "value": 90
        }
    """
    # Query Data Steward for raw data
    # Return structured records
    pass

async def get_record_details(
    self,
    record_ids: List[str],
    data_source: str,
    fields: Optional[List[str]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get detailed information for specific records."""
    pass

async def aggregate_data(
    self,
    aggregation_type: str,  # "sum", "average", "count", "group_by"
    field: str,
    filter_criteria: Optional[Dict[str, Any]] = None,
    data_source: str = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Perform data aggregations."""
    pass
```

**3.2 Integration with Data Steward**

- Use Data Steward for raw data access
- Maintain data lineage
- Respect tenant isolation
- Support various data sources

### Phase 4: Add MCP Tools for Conversational Analytics

**4.1 New MCP Tools in InsightsMCPServer**

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/mcp_server/insights_mcp_server.py`

**New Tools:**

```python
@mcp_tool
async def query_data_insights_tool(
    query_params: Dict[str, Any],  # Structured from agent LLM
    analysis_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Query data insights with structured parameters.
    
    Agent's LLM extracts intent and entities, then calls this tool.
    """
    # Get Data Insights Query Service via orchestrator
    service = await self.orchestrator.get_enabling_service("DataInsightsQueryService")
    if not service:
        return {"success": False, "error": "DataInsightsQueryService not available"}
    
    # Get cached analysis
    cached_analysis = self.orchestrator.analysis_cache.get(analysis_id) if hasattr(self.orchestrator, 'analysis_cache') else {}
    
    # Call service with structured params (NO LLM in service)
    return await service.process_query(
        query_params=query_params,  # Already structured by agent LLM
        analysis_id=analysis_id,
        cached_analysis=cached_analysis,
        user_context=user_context
    )

@mcp_tool
async def drill_down_into_data_tool(
    filter_criteria: Dict[str, Any],  # Structured from agent LLM
    insight_summary: str,
    data_source: str,
    max_results: int = 100,
    user_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Drill down into specific data records.
    
    Example: Agent extracts "customers with 90+ days overdue" and calls this tool.
    """
    # Call Data Drill-Down Service
    service = await orchestrator.get_enabling_service("DataDrillDownService")
    return await service.get_filtered_records(
        filter_criteria, data_source, max_results, user_context
    )

@mcp_tool
async def get_data_summary_tool(
    analysis_id: str,
    summary_type: str,  # "textual", "tabular", "visualizations"
    user_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Get summary of analysis results."""
    pass

@mcp_tool
async def filter_data_records_tool(
    filter_criteria: Dict[str, Any],
    data_source: str,
    user_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Filter data records based on criteria."""
    pass

@mcp_tool
async def compare_metrics_tool(
    metric1: Dict[str, Any],
    metric2: Dict[str, Any],
    comparison_type: str,  # "difference", "ratio", "percentage_change"
    user_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Compare two metrics."""
    pass

@mcp_tool
async def query_raw_data_tool(
    query: Dict[str, Any],  # SQL-like query structure
    data_source: str,
    user_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Query raw data sources (via Data Steward)."""
    pass
```

### Phase 5: Enhance Conversation Context Management (UPDATED - Simplified)

**5.1 Context Tracking (Simplified)**

- **Context is passed in `request` dict**, not retrieved manually
- Track current analysis context in session (via Session Manager)
- Base class handles conversation history automatically if `stateful: true`
- Store user's exploration state in session

**5.2 Context Resolution**

- Agent LLM resolves references: "those customers" → previous query results
- Context passed in `request` dict includes previous query results
- Maintain analysis_id context in session
- Track data source references in session

**5.3 Agent Learning (NEW - Enhancement)**

- Store query patterns in knowledge base
- Learn user's common query types
- Retrieve learned patterns to personalize responses
- See `AGENTIC_PLATFORM_ENHANCEMENT_OPPORTUNITIES.md` for details

## Concrete Improvements

### Improvement 1: Conversational Drill-Down

**Current:** User sees summary, can't ask follow-up questions
**Enhanced:** Full conversational drill-down with context

**Example Flow:**
```
User: "Analyze my customer data"
[Analysis runs, shows summary: "3 customers 90+ days late"]

User: "Which ones are they?"
Agent (LLM reasoning):
  - Intent: drill_down
  - Context: Previous query was about "customers 90+ days late"
  - Entities: {metric: "customers", filter: {field: "days_overdue", operator: ">=", value: 90}}
  - Tool: drill_down_into_data_tool(filter_criteria, ...)
  
Service: Queries Data Steward for customer records matching filter
Response: "Here are the 3 customers who are 90+ days late:
          1. Acme Corp - $15,000 overdue, 95 days late
          2. Beta Inc - $8,500 overdue, 92 days late
          3. Gamma LLC - $12,300 overdue, 91 days late"

User: "What's the total amount owed by these 3?"
Agent (LLM reasoning):
  - Intent: aggregation
  - Context: Previous query returned 3 customers
  - Tool: aggregate_data_tool(aggregation_type="sum", field="amount_overdue", filter_criteria=previous_filter)
Response: "The total amount owed by these 3 customers is $35,800."
```

### Improvement 2: Natural Language Query Understanding

**Current:** Limited pattern matching
**Enhanced:** LLM understands complex queries

**Examples:**
- "Show me customers who haven't paid in over 3 months" → Extracts: 90+ days
- "What's the average revenue per customer this quarter?" → Extracts: aggregation, timeframe, metric
- "Compare sales this month vs last month" → Extracts: comparison, timeframes

### Improvement 3: Context-Aware Responses

**Current:** Each query is independent
**Enhanced:** Agent remembers conversation context

**Example:**
```
User: "What are my top 5 customers by revenue?"
[Agent queries, returns list]

User: "Show me their contact information"
Agent: [Resolves "their" → top 5 customers from previous query]
       [Calls get_record_details_tool with those customer IDs]
Response: [Returns contact info for those 5 customers]
```

### Improvement 4: Progressive Exploration

**Current:** User must know what to ask
**Enhanced:** Agent suggests next steps

**Example:**
```
User: "Analyze my sales data"
[Analysis completes]

Agent Response: "I've analyzed your sales data. Here are the key insights:
                 - Total revenue: $250,000
                 - Top product: Widget A ($75,000)
                 - 3 customers account for 60% of revenue
                 
                 Would you like to:
                 1. See which customers are the top 3?
                 2. Analyze trends over time?
                 3. Compare this quarter to last quarter?"
```

## MCP Tools Required

### New Tools

1. **`query_data_insights_tool`**
   - Purpose: Query analysis results with structured params
   - Input: query_params (from agent LLM), analysis_id
   - Output: Query results

2. **`drill_down_into_data_tool`**
   - Purpose: Get detailed records matching criteria
   - Input: filter_criteria, data_source, max_results
   - Output: Filtered records with details

3. **`get_data_summary_tool`**
   - Purpose: Get summary of analysis
   - Input: analysis_id, summary_type
   - Output: Summary data

4. **`filter_data_records_tool`**
   - Purpose: Filter records with criteria
   - Input: filter_criteria, data_source
   - Output: Filtered records

5. **`compare_metrics_tool`**
   - Purpose: Compare two metrics
   - Input: metric1, metric2, comparison_type
   - Output: Comparison results

6. **`query_raw_data_tool`**
   - Purpose: Query raw data sources
   - Input: query structure, data_source
   - Output: Raw data results

### Enhanced Existing Tools

- `create_visualization_tool` - Add visualization type recommendations
- `analyze_trends_tool` - Add trend analysis guidance

## Service Enhancements

### New Service: DataDrillDownService

**Location:** `backend/business_enablement/enabling_services/data_drill_down_service/`

**Purpose:** Pure data access for drill-down queries (NO LLM)

**Key Methods:**
- `get_filtered_records()` - Get records matching filter criteria
- `get_record_details()` - Get detailed info for specific records
- `aggregate_data()` - Perform aggregations
- `get_data_schema()` - Get schema information

### Enhanced Service: DataInsightsQueryService

**Changes:**
- Remove LLM fallback
- Accept structured query parameters
- Enhance drill-down handlers
- Add more query pattern types

## Testing Scenarios

### Scenario 1: Basic Drill-Down

```
User: "I see I have 3 customers who are more than 90 days late in paying their bills. Which ones are they?"

Flow:
1. Agent receives question
2. LLM extracts: intent="drill_down", entities={metric: "customers", filter: {days_overdue: ">=90"}}
3. Agent calls: drill_down_into_data_tool(filter_criteria, ...)
4. Service queries Data Steward
5. Agent formats response with customer details
6. User sees: Customer names, amounts, contact info
```

### Scenario 2: Progressive Exploration

```
User: "What are my top 5 products by revenue?"
[Agent queries, returns list]

User: "Show me sales trends for these products"
Agent: [Resolves "these products" → top 5 from previous query]
       [Calls analyze_trends_tool with product IDs]
Response: [Shows trend charts for those 5 products]

User: "Which one has the best growth rate?"
Agent: [Calls compare_metrics_tool to compare growth rates]
Response: [Identifies product with best growth]
```

### Scenario 3: Complex Query

```
User: "Compare customer satisfaction scores between Q1 and Q2, and show me which customers improved the most"

Agent (LLM reasoning):
  - Intent: comparison + drill_down
  - Entities: {metric: "satisfaction", timeframes: ["Q1", "Q2"], filter: "improved"}
  - Multi-step: 
    1. Compare Q1 vs Q2 satisfaction
    2. Filter for customers who improved
    3. Get customer details
  - Tools: compare_metrics_tool → filter_data_records_tool → get_record_details_tool

Response: [Shows comparison, list of improved customers with details]
```

## Success Metrics

1. **Conversational Quality:**
   - Users can ask follow-up questions naturally
   - Agent correctly resolves context references
   - Responses are clear and actionable

2. **Drill-Down Capability:**
   - Users can drill from summaries to details
   - Data access is fast and accurate
   - Context is maintained across queries

3. **LLM Placement:**
   - All LLM calls only in agents
   - Services are pure data processing
   - Architecture principle maintained

## Implementation Timeline (UPDATED)

**Week 1-2:** Phase 1 - Convert to Declarative Agent
- Create YAML config in `agents/configs/insights_liaison_agent.yaml`
- Refactor agent class to extend `DeclarativeAgentBase`
- Update orchestrator to use `initialize_agent()` pattern
- Replace custom methods with `handle_user_query()` → `process_request()`
- Remove manual context management (base class handles it)
- Test LLM reasoning

**Week 3:** Phase 2 - Remove LLM from Service (CRITICAL)
- **REMOVE** `_execute_llm_query()` method from DataInsightsQueryService
- **REMOVE** LLM client initialization
- Refactor to accept structured params from agent LLM
- Update to pure rule-based routing
- Test service purity (verify no LLM calls)

**Week 4:** Phase 3 - Create DataDrillDownService
- Implement new pure service (NO LLM)
- Integrate with Data Steward
- Test data access

**Week 5:** Phase 4 - Add MCP Tools
- Implement new tools in InsightsMCPServer
- Test tool integration via orchestrator's MCP server
- Verify agent → tool → service flow

**Week 6:** Phase 5 - Context Management (Simplified)
- Pass context in `request` dict (not retrieved manually)
- Store analytics context in session
- Test conversation flows

**Week 7:** Testing & Refinement
- Test all scenarios
- Performance optimization
- User experience refinement

**Future Enhancements (Weeks 8-12):**
- Agent-to-Agent Collaboration (Insights agent can call Content agent)
- Agent Learning (learn query patterns, store in knowledge base)
- Cross-Pillar Collaboration (Insights + Business Outcomes workflows)
- See `AGENTIC_PLATFORM_ENHANCEMENT_OPPORTUNITIES.md` for details

## Dependencies

### Foundation Dependencies (Already Exist)
- `DeclarativeAgentBase` - Base class for declarative agents ✅
- `OrchestratorBase` - Base class for orchestrators (provides `initialize_agent()`) ✅
- `InsightsOrchestrator` MCP Server - Tool exposure ✅
- Data Steward - Data access (already exists) ✅

### New Dependencies (To Be Created)
- `DataDrillDownService` - Pure service for detailed data access (NO LLM)

### Enhanced Dependencies (To Be Refactored)
- `DataInsightsQueryService` - **CRITICAL**: Remove LLM, accept structured params

### Enhancement Dependencies (Future)
- Knowledge base integration for agent learning
- Agent-to-Agent communication infrastructure

## Risks & Mitigations

**Risk 1:** LLM may not extract correct entities for drill-down
- **Mitigation:** Iterative execution allows agent to refine queries, clear error messages

**Risk 2:** Data access performance for large datasets
- **Mitigation:** Implement pagination, limit max_results, use efficient queries

**Risk 3:** Context management complexity
- **Mitigation:** Use session manager, keep context focused, clear context boundaries

