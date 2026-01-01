# Operations Pillar API Contract

**Date**: November 11, 2025  
**Status**: Draft for Migration  
**Pattern**: Follows Content & Insights universal gateway pattern

---

## 🎯 Overview

The Operations Pillar provides SOP (Standard Operating Procedure) and Workflow management capabilities:
- **Process Blueprint**: Convert between SOPs and Workflows
- **Coexistence Analysis**: Optimize SOP/Workflow alignment  
- **Wizard Mode**: Interactive SOP building
- **Session Management**: Track user workflow state

---

## 📋 API Endpoints

### Base URL
```
/api/operations/*
```

All endpoints follow RESTful patterns and return consistent response formats.

---

## 1. Session Management

### Get Session Elements
**Endpoint**: `GET /api/operations/session/elements`  
**Description**: Retrieve current session state (SOP and Workflow elements)

**Query Parameters**:
- `session_token` (required): User session identifier

**Response**:
```typescript
{
  valid: boolean
  action: string
  missing?: string
  session_state: {
    has_sop: boolean
    has_workflow: boolean
    section2_complete: boolean
  }
  elements?: {
    sop: any
    workflow: any
  }
}
```

### Clear Session Elements
**Endpoint**: `DELETE /api/operations/session/elements`  
**Description**: Clear session state (reset workflow)

**Query Parameters**:
- `session_token` (required): User session identifier

**Response**:
```typescript
{
  success: boolean
  message: string
}
```

---

## 2. Process Blueprint (SOP ↔ Workflow Conversion)

### Generate Workflow from SOP
**Endpoint**: `POST /api/operations/generate-workflow-from-sop`  
**Description**: Convert SOP document to structured workflow

**Request Body**:
```typescript
{
  session_token: string
  sop_file_uuid: string
}
```

**Response**:
```typescript
{
  success: boolean
  sop_text: string
  workflow: {
    name: string
    description: string
    steps: Array<{
      id: string
      name: string
      description: string
      order: number
    }>
  }
  session_state: {
    has_sop: boolean
    has_workflow: boolean
    section2_complete: boolean
  }
}
```

### Generate SOP from Workflow
**Endpoint**: `POST /api/operations/generate-sop-from-workflow`  
**Description**: Convert structured workflow to SOP document

**Request Body**:
```typescript
{
  session_token: string
  workflow_file_uuid: string
}
```

**Response**:
```typescript
{
  success: boolean
  workflow_text: string
  sop: {
    title: string
    purpose: string
    scope: string
    procedures: Array<{
      step: number
      description: string
      substeps?: string[]
    }>
  }
  session_state: {
    has_sop: boolean
    has_workflow: boolean
    section2_complete: boolean
  }
}
```

### Analyze File (Legacy)
**Endpoint**: `GET /api/operations/files/analyze`  
**Description**: Analyze file and convert to desired output type

**Query Parameters**:
- `session_token` (required): User session identifier
- `input_file_uuid` (required): File to analyze
- `output_type` (required): "workflow" | "sop"

**Response**:
```typescript
{
  success: boolean
  sop_text?: string
  workflow?: object
  workflow_text?: string
  sop?: object
}
```

---

## 3. Coexistence Analysis

### Analyze Coexistence (File-based)
**Endpoint**: `GET /api/operations/files/coexistence`  
**Description**: Analyze how SOP and Workflow coexist and provide optimization recommendations

**Query Parameters**:
- `session_token` (required): User session identifier (contains SOP and Workflow from session)

**Response**:
```typescript
{
  success: boolean
  coexistence_analysis: {
    alignment_score: number // 0-100
    gaps: Array<{
      type: "missing_in_sop" | "missing_in_workflow" | "mismatch"
      description: string
      severity: "low" | "medium" | "high"
    }>
    recommendations: Array<{
      action: string
      rationale: string
      priority: "low" | "medium" | "high"
    }>
  }
}
```

### Analyze Coexistence (Content-based)
**Endpoint**: `POST /api/operations/coexistence/analyze`  
**Description**: Analyze coexistence using direct content (not file UUIDs)

**Request Body**:
```typescript
{
  session_token: string
  sop_content: string
  workflow_content: object
}
```

**Response**: Same as file-based coexistence

---

## 4. Wizard Mode

### Start Wizard
**Endpoint**: `POST /api/operations/wizard/start`  
**Description**: Initialize interactive SOP building wizard

**Request Body**:
```typescript
{
  // No parameters needed
}
```

**Response**:
```typescript
{
  success: boolean
  session_token: string
  wizard_state: {
    step: number
    total_steps: number
    current_question: string
  }
}
```

### Wizard Chat
**Endpoint**: `POST /api/operations/wizard/chat`  
**Description**: Send user message to wizard and get next step

**Request Body**:
```typescript
{
  session_token: string
  user_message: string
}
```

**Response**:
```typescript
{
  success: boolean
  wizard_response: string
  wizard_state: {
    step: number
    total_steps: number
    current_question: string
    is_complete: boolean
  }
  sop_draft?: object
}
```

### Wizard Publish
**Endpoint**: `POST /api/operations/wizard/publish`  
**Description**: Finalize and publish wizard-generated SOP

**Request Body**:
```typescript
{
  session_token: string
}
```

**Response**:
```typescript
{
  success: boolean
  sop: object
  sop_uuid: string
  message: string
}
```

---

## 5. Blueprint Management

### Save Blueprint
**Endpoint**: `POST /api/operations/blueprint/save`  
**Description**: Save process blueprint for later use

**Request Body**:
```typescript
{
  blueprint: object
  user_id: string
}
```

**Response**:
```typescript
{
  success: boolean
  blueprint_id: string
}
```

---

## 6. Liaison Agent (Conversational)

### Process Query
**Endpoint**: `POST /api/operations/query`  
**Description**: Process natural language query about operations

**Request Body**:
```typescript
{
  session_id: string
  query: string
  file_url?: string
  context?: object
}
```

**Response**:
```typescript
{
  success: boolean
  response: string
  suggested_actions?: string[]
}
```

### Process Conversation
**Endpoint**: `POST /api/operations/conversation`  
**Description**: Continue conversational interaction

**Request Body**:
```typescript
{
  session_id: string
  message: string
  context?: object
}
```

**Response**:
```typescript
{
  success: boolean
  response: string
  context: object
}
```

### Get Conversation Context
**Endpoint**: `GET /api/operations/session/{session_id}/context`  
**Description**: Retrieve conversation context for session

**Response**:
```typescript
{
  success: boolean
  context: object
  history: Array<{
    role: "user" | "assistant"
    message: string
    timestamp: string
  }>
}
```

### Analyze Intent
**Endpoint**: `POST /api/operations/intent/analyze`  
**Description**: Analyze user intent from query

**Request Body**:
```typescript
{
  query: string
}
```

**Response**:
```typescript
{
  success: boolean
  intent: {
    type: "create_sop" | "create_workflow" | "convert" | "analyze"
    confidence: number
    entities: object
  }
}
```

---

## 7. Health Check

### Health Check
**Endpoint**: `GET /api/operations/health`  
**Description**: Check Operations Pillar health status

**Response**:
```typescript
{
  status: "healthy" | "unhealthy"
  pillar: "operations"
  orchestrator_status: object
  timestamp: string
}
```

---

## 📊 Summary

**Total Endpoints**: 14

**By Category**:
- Session Management: 2 endpoints
- Process Blueprint: 3 endpoints
- Coexistence Analysis: 2 endpoints
- Wizard Mode: 3 endpoints
- Blueprint Management: 1 endpoint
- Liaison Agent: 4 endpoints
- Health: 1 endpoint

**HTTP Methods**:
- GET: 4 endpoints
- POST: 9 endpoints
- DELETE: 1 endpoint

---

## 🔄 Migration Notes

### Current State
- Frontend calls: `/api/operations/*` (via fastapi_bridge)
- Semantic router: `/api/operations-pillar/*` (not used by frontend)
- MVP router: `/api/mvp/operations/*` (legacy)

### Target State
- Universal router: `/api/operations/*`
- FrontendGatewayService: 14 handler methods
- Old routers: Archived

### Migration Steps
1. Add 14 handler methods to FrontendGatewayService
2. Update universal router with Operations routing
3. Archive old operations_pillar_router.py
4. Remove fastapi_bridge Operations routes
5. Test all 14 endpoints

---

**Status**: Ready for implementation  
**Pattern**: Follows Content & Insights migration  
**Estimated Time**: 2-3 hours



