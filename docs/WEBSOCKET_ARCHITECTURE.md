# WebSocket Architecture - Holistic Review & Fixes

## Overview

This document outlines the WebSocket architecture for multi-agent chat interactions (Guide Agent + Liaison Agents) and documents the fixes applied to ensure frontend and backend alignment.

## Architecture

### Backend WebSocket Endpoints

The backend provides a **unified WebSocket endpoint** that handles all agent communications:

- **Endpoint**: `/api/ws/agent`
- **Protocol**: WebSocket (ws:// or wss://)
- **Authentication**: Session token via query parameter (`?session_token=<token>`)
- **Message Routing**: Based on `agent_type` and `pillar` fields in messages

#### Backend Endpoint Structure

```python
@router.websocket("/api/ws/agent")
async def unified_agent_websocket(websocket: WebSocket, session_token: str = Query(None)):
    """
    Unified Agent WebSocket endpoint.
    
    Handles all agent communications (Guide + Liaison) via message routing.
    Single connection per user, routes messages to appropriate agent.
    """
```

#### Message Format (Frontend → Backend)

```typescript
{
    "agent_type": "guide" | "liaison",
    "pillar": "content" | "insights" | "operations" | "business_outcomes" (required if liaison),
    "message": "user message",
    "conversation_id": "optional conversation ID"
}
```

#### Response Format (Backend → Frontend)

```typescript
{
    "type": "response" | "error",
    "message": "agent response",
    "agent_type": "guide" | "liaison",
    "pillar": "pillar name" (if liaison),
    "conversation_id": "conversation ID",
    "data": {...},  // Optional data (AGUI components, etc.)
    "visualization": {...}  // Optional visualization component
}
```

### Frontend WebSocket Architecture

The frontend uses a **unified WebSocket connection** approach:

1. **Single Connection**: One WebSocket connection per user session
2. **Message Routing**: Messages are routed to the appropriate agent based on `agent_type` and `pillar`
3. **Agent Switching**: Users can switch between Guide and Liaison agents without reconnecting

#### Frontend Components

1. **`useUnifiedAgentChat` Hook**: Main hook for unified agent chat
   - Location: `shared/hooks/useUnifiedAgentChat.ts`
   - Handles: Connection management, message sending/receiving, agent switching

2. **`SimpleWebSocketService`**: Service layer for WebSocket connections
   - Location: `shared/services/SimpleServiceLayer.ts`
   - Used by: `GuideAgentProvider` for Guide Agent connections

3. **`WebSocketManager`**: Alternative WebSocket manager
   - Location: `shared/managers/WebSocketManager.ts`
   - Provides: Connection pooling, reconnection logic

4. **`WebSocketService`**: Full-featured WebSocket service
   - Location: `shared/services/WebSocketService.ts`
   - Features: Connection pooling, message queuing, heartbeat

## Fixes Applied

### Issue: Hardcoded WebSocket URLs

**Problem**: Multiple WebSocket initialization points were using hardcoded `ws://127.0.0.1:8000` instead of the configured API URL (Traefik route on port 80).

**Solution**: Updated all WebSocket URL construction to use environment variables with proper defaults:

```typescript
// Pattern used across all WebSocket initialization points:
const apiBaseURL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://35.215.64.103";
const API_URL = apiBaseURL.replace(':8000', '').replace(/\/$/, ''); // Remove port 8000 and trailing slash
const wsBaseURL = API_URL.replace(/^http/, 'ws');
```

### Files Fixed

1. **`shared/services/SimpleServiceLayer.ts`**
   - Fixed `SimpleWebSocketService.connect()` method
   - Now constructs WebSocket URL from environment variables

2. **`shared/hooks/useUnifiedAgentChat.ts`**
   - Fixed `getWebSocketURL()` callback
   - Ensures all unified agent connections use correct URL

3. **`shared/managers/WebSocketManager.ts`**
   - Fixed constructor to use configured API URL
   - Removed hardcoded `ws://127.0.0.1:8000`

4. **`shared/services/WebSocketService.ts`**
   - Fixed constructor to use configured API URL
   - Supports `NEXT_PUBLIC_WS_BASE_URL` override

5. **`shared/config/core.ts`**
   - Updated default WebSocket URL configuration
   - Uses environment variables with production defaults

6. **`shared/managers/ContentAPIManager.ts`**
   - Fixed base URL construction (already fixed in previous session)

### URL Construction Pattern

All WebSocket connections now follow this pattern:

```typescript
// 1. Get base API URL from environment
const apiBaseURL = process.env.NEXT_PUBLIC_API_URL || 
                   process.env.NEXT_PUBLIC_BACKEND_URL || 
                   "http://35.215.64.103";

// 2. Remove port 8000 (Traefik uses port 80, which is default)
const API_URL = apiBaseURL.replace(':8000', '').replace(/\/$/, '');

// 3. Convert HTTP to WebSocket protocol
const wsBaseURL = API_URL.replace(/^http/, 'ws');

// 4. Construct full WebSocket URL with endpoint and token
const endpoint = '/api/ws/agent';
const tokenParam = sessionToken ? `?session_token=${encodeURIComponent(sessionToken)}` : '';
const wsUrl = `${wsBaseURL}${endpoint}${tokenParam}`;
```

## Best Practices

### 1. Single WebSocket Connection

✅ **DO**: Use one WebSocket connection per user session
- Reduces server load
- Simplifies connection management
- Better resource efficiency

❌ **DON'T**: Create multiple WebSocket connections for different agents
- Wastes resources
- Complicates state management
- Increases server load

### 2. Message Routing

✅ **DO**: Route messages based on `agent_type` and `pillar` fields
- Single connection handles all agents
- Easy agent switching
- Consistent message format

❌ **DON'T**: Use separate endpoints for each agent type
- Creates connection overhead
- Harder to manage
- Inconsistent architecture

### 3. URL Configuration

✅ **DO**: Use environment variables for API/WebSocket URLs
- Works across environments (dev, staging, production)
- Easy to configure
- No hardcoded values

❌ **DON'T**: Hardcode URLs like `ws://127.0.0.1:8000`
- Breaks in production
- Doesn't work with Traefik routing
- Environment-specific issues

### 4. Session Token Handling

✅ **DO**: Pass session token as query parameter
- Standard WebSocket authentication pattern
- Works with backend validation
- Easy to implement

❌ **DON'T**: Try to use Authorization header (WebSocket doesn't support custom headers easily)
- Limited browser support
- More complex implementation

## Frontend-Backend Alignment

### Connection Flow

1. **Frontend**: User authenticates → Gets session token
2. **Frontend**: Creates WebSocket connection to `/api/ws/agent?session_token=<token>`
3. **Backend**: Validates session token via Traffic Cop SOA API
4. **Backend**: Accepts WebSocket connection
5. **Backend**: Routes messages to appropriate agent based on `agent_type` and `pillar`
6. **Backend**: Sends responses back through same connection

### Message Flow

```
User Message
    ↓
Frontend: useUnifiedAgentChat hook
    ↓
Frontend: WebSocket.send({
    agent_type: "guide" | "liaison",
    pillar: "content" | ... (if liaison),
    message: "user message"
})
    ↓
Backend: /api/ws/agent endpoint
    ↓
Backend: UnifiedAgentWebSocketSDK
    ↓
Backend: Routes to Guide Agent or Liaison Agent (based on pillar)
    ↓
Backend: Agent processes message
    ↓
Backend: Sends response {
    type: "response",
    agent_type: "guide" | "liaison",
    message: "agent response",
    ...
}
    ↓
Frontend: WebSocket.onmessage handler
    ↓
Frontend: Updates UI with response
```

## Testing

### Verify WebSocket Connection

1. Open browser DevTools → Network tab → WS filter
2. Look for WebSocket connection to `ws://35.215.64.103/api/ws/agent` (not `ws://127.0.0.1:8000`)
3. Check that connection is established (status: 101 Switching Protocols)
4. Verify session token is included in query string

### Verify Message Routing

1. Send a message to Guide Agent
2. Verify response includes `agent_type: "guide"`
3. Switch to Liaison Agent (e.g., Content pillar)
4. Send a message
5. Verify response includes `agent_type: "liaison"` and `pillar: "content"`

## Environment Variables

### Required (Production)

- `NEXT_PUBLIC_API_URL`: Base API URL (defaults to `http://35.215.64.103`)
- `NEXT_PUBLIC_BACKEND_URL`: Alternative backend URL (fallback)

### Optional

- `NEXT_PUBLIC_WS_BASE_URL`: Override WebSocket base URL (if different from API URL)

## Troubleshooting

### WebSocket Connection Refused

**Symptoms**: `WebSocket connection to 'ws://127.0.0.1:8000/api/ws/agent' failed`

**Causes**:
1. Hardcoded URL still in use (check all WebSocket initialization points)
2. Browser cache (clear cache or use incognito mode)
3. Environment variable not set

**Solution**: 
- Verify all WebSocket URLs use environment variables
- Clear browser cache
- Check that `NEXT_PUBLIC_API_URL` is set correctly

### 401 Unauthorized

**Symptoms**: WebSocket connection accepted but messages return 401

**Causes**:
1. Session token expired
2. Session token not passed correctly
3. Backend session validation failing

**Solution**:
- Refresh session (log out and log back in)
- Verify session token is included in WebSocket URL query string
- Check backend logs for authentication errors

## Summary

The WebSocket architecture is now aligned between frontend and backend:

✅ **Unified Endpoint**: Single `/api/ws/agent` endpoint for all agents
✅ **Message Routing**: Messages routed based on `agent_type` and `pillar`
✅ **URL Configuration**: All WebSocket URLs use environment variables
✅ **Session Authentication**: Session tokens passed via query parameter
✅ **Best Practices**: Single connection, proper routing, environment-based configuration

All WebSocket initialization points have been updated to use the configured API URL instead of hardcoded localhost addresses.






