# Business Orchestrator Old - Working Patterns Analysis

## Overview
This document analyzes the working patterns from `business_orchestrator_old` to extract the real implementation details needed for integrating our new Experience Dimension with the existing working backend.

## 🏗️ **Architecture Patterns**

### 1. **Service Structure**
```
business_orchestrator_old/
├── service/
│   ├── business_orchestrator_service_refactored.py  # Main service
│   └── service_runner.py                           # Service startup
├── guide_agent/
│   ├── guide_agent.py                              # Main guide agent
│   ├── intent_analyzer.py                          # Intent analysis
│   ├── pillar_router.py                            # Pillar routing
│   └── journey_manager.py                          # Journey management
├── mcp_server/
│   ├── business_orchestrator_mcp_server.py         # MCP server
│   └── mcp_server_runner.py                        # MCP startup
├── rest_api_endpoints.py                           # FastAPI endpoints
├── rest_api_handlers.py                            # API handlers
└── test_business_orchestrator.py                   # Test suite
```

### 2. **Key Components**

#### **Business Orchestrator Service**
- **Base Class**: `AgentBase` (from Agent SDK)
- **Capabilities**: `["orchestration", "coordination", "monitoring", "integration"]`
- **Required Roles**: `["traffic_cop", "post_office"]`
- **AGUI Schema**: Business orchestrator UI components
- **Pillar Services**: Manages 4 pillar services (content, insights, operations, business_outcomes)

#### **Guide Agent**
- **Base Class**: `AgentBase` (from Agent SDK)
- **Capabilities**: `["intent_analysis", "pillar_routing", "user_guidance", "journey_planning", "context_management", "liaison_coordination", "cross_pillar_workflows", "personalized_recommendations"]`
- **Required Roles**: `["conductor", "librarian", "traffic_cop", "post_office"]`
- **Specialization**: `"user_guidance"`
- **Components**: JourneyManager, IntentAnalyzer, PillarRouter

#### **MCP Server**
- **Base Class**: `MCPBaseServer`
- **Tools**: 6 MCP tools for orchestration
- **Resources**: 4 MCP resources for data access

## 🔌 **API Patterns**

### 1. **REST API Endpoints**
```python
# Health and capabilities
GET /health
GET /capabilities

# Analysis endpoints
POST /analyze                    # Dataset analysis
POST /visualize                  # Visualization creation
POST /insights                   # Business insights generation

# Chat endpoints
POST /chat                       # Chat message processing
GET /conversation/{session_id}   # Get conversation history
DELETE /conversation/{session_id} # Clear conversation history

# Specialized analysis
POST /analyze/anomaly            # Anomaly detection
POST /analyze/correlation        # Correlation analysis
POST /analyze/statistical        # Statistical analysis

# Visualization types
POST /visualize/histogram        # Histogram creation
POST /visualize/scatter          # Scatter plot creation
POST /visualize/heatmap          # Heatmap creation
```

### 2. **Request/Response Models**
```python
# Dataset Analysis Request
class DatasetAnalysisRequest(BaseModel):
    dataset: Dict[str, Any] = Field(..., description="Dataset to analyze")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

# Visualization Request
class VisualizationRequest(BaseModel):
    dataset: Dict[str, Any] = Field(..., description="Dataset to visualize")
    visualization_type: str = Field(default="auto", description="Type of visualization")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

# Chat Message Request
class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="User's message")
    dataset: Optional[Dict[str, Any]] = Field(default=None, description="Optional dataset")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
```

### 3. **API Handler Patterns**
```python
class InsightsPillarAPIHandlers:
    async def get_user_context(self, user_id: str, session_id: Optional[str] = None) -> UserContext:
        # Creates UserContext with permissions and metadata
    
    async def analyze_dataset_handler(self, request_data: Dict[str, Any], user_id: str = "api_user") -> JSONResponse:
        # Handles dataset analysis with error handling and user context
    
    async def create_visualization_handler(self, request_data: Dict[str, Any], user_id: str = "api_user") -> JSONResponse:
        # Handles visualization creation with error handling
```

## 🎯 **Intent Analysis Patterns**

### 1. **Intent Categories**
```python
intent_patterns = {
    "content_management": {
        "keywords": ["file", "document", "upload", "parse", "convert", "content", "text", "pdf", "excel", "csv"],
        "phrases": ["upload a file", "parse document", "convert format", "analyze content", "process file"],
        "confidence_boost": 0.2
    },
    "data_analysis": {
        "keywords": ["data", "analysis", "analyze", "insights", "chart", "graph", "statistics", "metrics", "report"],
        "phrases": ["analyze data", "create chart", "generate insights", "data visualization", "statistical analysis"],
        "confidence_boost": 0.2
    },
    "workflow_management": {
        "keywords": ["workflow", "process", "automate", "optimize", "efficiency", "streamline", "sop", "procedure"],
        "phrases": ["create workflow", "optimize process", "automate task", "improve efficiency", "streamline operations"],
        "confidence_boost": 0.2
    },
    "business_outcomes": {
        "keywords": ["roi", "kpi", "outcome", "result", "impact", "measure", "track", "success", "goal", "objective"],
        "phrases": ["measure roi", "track kpis", "business impact", "success metrics", "outcome measurement"],
        "confidence_boost": 0.2
    }
}
```

### 2. **Complexity and Urgency Analysis**
```python
complexity_indicators = {
    "high": ["complex", "advanced", "sophisticated", "enterprise", "custom", "integration", "automation", "workflow"],
    "medium": ["multiple", "several", "various", "comprehensive", "detailed", "analysis", "optimization"],
    "low": ["simple", "basic", "quick", "easy", "straightforward", "single"]
}

urgency_indicators = {
    "high": ["urgent", "asap", "immediately", "quickly", "fast", "priority", "critical", "emergency"],
    "medium": ["soon", "today", "this week", "important", "need"],
    "low": ["whenever", "eventually", "sometime", "no rush", "take your time"]
}
```

## 🛣️ **Pillar Routing Patterns**

### 1. **Pillar Capabilities**
```python
pillar_capabilities = {
    "content": {
        "primary_intents": ["content_management", "file_processing", "document_analysis"],
        "capabilities": ["file_upload", "document_parsing", "format_conversion", "content_analysis", "metadata_extraction", "preview_generation"],
        "workflow_stages": ["upload", "parse", "convert", "analyze"],
        "priority": 1
    },
    "insights": {
        "primary_intents": ["data_analysis", "insights_generation", "visualization"],
        "capabilities": ["data_analysis", "statistical_analysis", "visualization", "insights_generation", "report_creation", "trend_analysis"],
        "workflow_stages": ["analyze", "visualize", "insights", "report"],
        "priority": 2
    },
    "operations": {
        "primary_intents": ["workflow_management", "process_optimization", "automation"],
        "capabilities": ["workflow_creation", "process_optimization", "task_automation", "sop_management", "operational_monitoring", "efficiency_analysis"],
        "workflow_stages": ["assess", "optimize", "automate", "monitor"],
        "priority": 3
    },
    "business_outcomes": {
        "primary_intents": ["outcome_measurement", "roi_analysis", "kpi_tracking"],
        "capabilities": ["roi_measurement", "kpi_tracking", "impact_assessment", "goal_setting", "performance_measurement", "business_analytics"],
        "workflow_stages": ["measure", "track", "assess", "optimize"],
        "priority": 4
    }
}
```

### 2. **Cross-Pillar Workflow Patterns**
```python
workflow_patterns = {
    "content_to_insights": {
        "description": "Process content and generate insights",
        "pillars": ["content", "insights"],
        "triggers": ["content_management", "data_analysis"],
        "confidence_boost": 0.2
    },
    "insights_to_operations": {
        "description": "Use insights to optimize operations",
        "pillars": ["insights", "operations"],
        "triggers": ["data_analysis", "workflow_management"],
        "confidence_boost": 0.2
    },
    "operations_to_outcomes": {
        "description": "Measure operational improvements",
        "pillars": ["operations", "business_outcomes"],
        "triggers": ["workflow_management", "outcome_measurement"],
        "confidence_boost": 0.2
    },
    "full_cycle": {
        "description": "Complete business process cycle",
        "pillars": ["content", "insights", "operations", "business_outcomes"],
        "triggers": ["comprehensive", "end-to-end", "complete"],
        "confidence_boost": 0.3
    }
}
```

## 🔧 **MCP Tools Patterns**

### 1. **Available MCP Tools**
```python
tools = [
    Tool(
        name="handle_chat_request",
        description="Handle chat requests through agentic pathway",
        inputSchema={
            "type": "object",
            "properties": {
                "user_message": {"type": "string", "description": "User chat message"},
                "user_context": {"type": "object", "description": "User context information"}
            },
            "required": ["user_message", "user_context"]
        }
    ),
    Tool(
        name="handle_api_request",
        description="Handle API requests through direct pathway",
        inputSchema={
            "type": "object",
            "properties": {
                "endpoint": {"type": "string", "description": "API endpoint"},
                "request_data": {"type": "object", "description": "Request data"},
                "user_context": {"type": "object", "description": "User context information"}
            },
            "required": ["endpoint", "request_data", "user_context"]
        }
    ),
    Tool(
        name="coordinate_pillar_workflow",
        description="Coordinate workflows across multiple pillars",
        inputSchema={
            "type": "object",
            "properties": {
                "workflow_type": {"type": "string", "description": "Type of workflow to coordinate"},
                "pillar_data": {"type": "object", "description": "Data for each pillar"},
                "user_context": {"type": "object", "description": "User context information"}
            },
            "required": ["workflow_type", "pillar_data", "user_context"]
        }
    ),
    Tool(
        name="handoff_to_pillar",
        description="Handoff data between pillars",
        inputSchema={
            "type": "object",
            "properties": {
                "source_pillar": {"type": "string", "description": "Source pillar name"},
                "target_pillar": {"type": "string", "description": "Target pillar name"},
                "data": {"type": "object", "description": "Data to handoff"},
                "user_context": {"type": "object", "description": "User context information"}
            },
            "required": ["source_pillar", "target_pillar", "data", "user_context"]
        }
    )
]
```

## 🎭 **User Context Patterns**

### 1. **UserContext Structure**
```python
class UserContext:
    user_id: str
    email: str
    full_name: str
    session_id: Optional[str]
    permissions: List[str]
    tenant_id: Optional[str]
    request_id: Optional[str]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]]
```

### 2. **Permission Patterns**
```python
# Default permissions for API users
permissions = ["insights:read", "insights:analyze", "insights:visualize"]

# Business orchestrator permissions
permissions = ["business_orchestrator_service:chat"]
```

## 🔄 **Integration Patterns**

### 1. **Service Initialization**
```python
async def initialize_business_logic(self):
    # Initialize pillar services
    # Set up callbacks
    # Configure communication
    # Start monitoring

async def start_service(self):
    # Start FastAPI server
    # Initialize MCP server
    # Begin service monitoring
```

### 2. **Error Handling Patterns**
```python
try:
    # Service operation
    result = await service.operation()
    return JSONResponse(status_code=200, content=result)
except HTTPException:
    raise
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Operation failed: {str(e)}"
    )
```

## 📊 **Key Insights for Integration**

### 1. **What We Need to Extract**
- ✅ **Real API Endpoints**: The actual REST endpoints that work
- ✅ **Request/Response Models**: The Pydantic models for validation
- ✅ **User Context Management**: How user sessions and permissions work
- ✅ **Intent Analysis Logic**: The working intent classification system
- ✅ **Pillar Routing Logic**: How requests are routed to appropriate pillars
- ✅ **MCP Tool Definitions**: The working MCP tools and their schemas
- ✅ **Error Handling Patterns**: How errors are handled and formatted

### 2. **Integration Points**
- **Frontend Integration Service** needs to route to these real endpoints
- **Guide Agent** needs the intent analysis and pillar routing logic
- **Experience Manager** needs the user context and session management
- **Journey Manager** needs the workflow coordination patterns

### 3. **Next Steps**
1. Extract the working API endpoints and integrate them into our Frontend Integration service
2. Extract the intent analysis logic and integrate it into our Guide Agent
3. Extract the pillar routing logic and integrate it into our Experience Manager
4. Extract the MCP tools and integrate them into our MCP servers
5. Test the integration with the existing frontend

This analysis provides the foundation for integrating our new Experience Dimension with the working backend patterns.
