# Traefik Configuration Audit - Architectural Alignment

**Date:** 2026-01-03  
**Purpose:** Holistic audit of Traefik implementation to ensure alignment with Platform Architecture and identify WebSocket routing issues

---

## Executive Summary

### ✅ What's Working
1. **Router Registration**: All routers are properly configured and Traefik is discovering them
2. **Priority System**: Route priorities are correctly set (auth=100, websocket-gateway=96, websocket=95, upload=90, process=89, main=1)
3. **Middleware Chains**: Proper middleware chains exist for different route types
4. **WebSocket Middleware**: Dedicated `websocket-chain` with CORS, rate limiting, and security headers
5. **Architectural Alignment**: Routes respect Smart City role ownership (Post Office owns WebSocket Gateway)

### ⚠️ Issues Identified
1. **Router Discovery Delay**: New router labels require container recreation (not just restart)
2. **WebSocket Handshake**: 400 Bad Request indicates routing works but handshake incomplete
3. **Service Definition**: All routers correctly point to `backend` service on port 8000

---

## 1. Route Priority Analysis

### Current Priority Hierarchy
```
Priority 100: backend-auth (auth endpoints, health, session creation)
Priority 96:  backend-websocket-gateway (/ws - NEW Post Office Gateway)
Priority 95:  backend-websocket (/api/ws - legacy, may be removed)
Priority 90:  backend-upload (file uploads)
Priority 89:  backend-process-file (file processing)
Priority 1:   backend (main API routes with auth)
Priority 1:   frontend (catch-all for non-API routes)
```

### ✅ Architectural Alignment
- **High Priority Routes**: Auth and transport services (WebSocket) have highest priority
- **Transport Layer**: WebSocket Gateway (owned by Post Office) correctly prioritized
- **Smart City Authority**: Routes respect City Manager lifecycle (PostOfficeService activation)

---

## 2. WebSocket Configuration Analysis

### Current Configuration
```yaml
# docker-compose.yml
- "traefik.http.routers.backend-websocket-gateway.rule=Path(`/ws`)"
- "traefik.http.routers.backend-websocket-gateway.entrypoints=web"
- "traefik.http.routers.backend-websocket-gateway.service=backend"
- "traefik.http.routers.backend-websocket-gateway.middlewares=websocket-chain@file"
- "traefik.http.routers.backend-websocket-gateway.priority=96"
```

### Middleware Chain
```yaml
# traefik-config/middlewares.yml
websocket-chain:
  chain:
    middlewares:
      - websocket-cors      # CORS for WebSocket upgrade
      - websocket-rate-limit  # Lower rate limit (10 req/s)
      - security-headers    # Security headers
```

### ✅ Architectural Compliance
- **Bypasses ForwardAuth**: Correct - WebSocket handles auth via `session_token` query param
- **Handler-Level Auth**: Aligns with architecture (Post Office validates sessions via Traffic Cop)
- **Transport Layer**: WebSocket Gateway is transport service, owned by Smart City role (Post Office)

---

## 3. Route Rule Analysis

### Main Backend Router Exclusion
```yaml
- "traefik.http.routers.backend.rule=(Host(`api.localhost`) || PathPrefix(`/api`)) && !PathPrefix(`/api/v1/content-pillar/upload-file`) && !PathPrefix(`/api/v1/content-pillar/process-file`) && !PathPrefix(`/api/ws`) && !Path(`/ws`) && !Path(`/api/v1/session/create-user-session`)"
```

### ✅ Correct Exclusions
- `/ws` is excluded from main backend router (handled by websocket-gateway router)
- `/api/ws` is excluded (handled by legacy websocket router)
- File upload/process routes excluded (handler-level auth)
- Session creation excluded (auth router)

---

## 4. Traefik EntryPoint Configuration

### Current Settings
```yaml
entryPoints:
  web:
    address: ":80"
    transport:
      respondingTimeouts:
        readTimeout: 600s
        writeTimeout: 600s
        idleTimeout: 300s
```

### ⚠️ Potential Issue
- **No WebSocket-Specific Timeout**: WebSocket connections may need longer timeouts
- **Idle Timeout**: 300s (5 minutes) may be too short for long-lived WebSocket connections

### Recommendation
Consider adding WebSocket-specific timeout configuration or increasing idle timeout for WebSocket routes.

---

## 5. Service Discovery

### Current Setup
- **Docker Provider**: Traefik watches Docker socket for label changes
- **Network**: All services on `smart_city_net`
- **Service Definition**: All routers point to `backend` service on port 8000

### ✅ Correct Configuration
- Services are discoverable
- Network isolation maintained
- Service port correctly configured

---

## 6. WebSocket Routing Issue Diagnosis

### Symptoms
1. Router `backend-websocket-gateway@docker` now registered ✅
2. HTTP GET to `/ws` returns 400 Bad Request (progress - routing works)
3. WebSocket client connection fails with 404 (before router registration) or 400 (after)

### Root Cause Analysis
1. **Router Registration**: Fixed by container recreation
2. **400 Bad Request**: Indicates Traefik is routing correctly, but:
   - WebSocket upgrade headers may be incomplete
   - FastAPI WebSocket handler may not be receiving the request
   - Middleware may be interfering with WebSocket upgrade

### Next Steps
1. Test with proper WebSocket client (websockets library)
2. Check backend logs for WebSocket connection attempts
3. Verify FastAPI WebSocket handler is receiving requests
4. Check if middleware is interfering with WebSocket upgrade

---

## 7. Architectural Alignment Assessment

### ✅ Aligned with Platform Architecture

1. **Transport Layer (Section 7)**
   - WebSocket Gateway is transport service ✅
   - Owned by Smart City role (Post Office) ✅
   - Lifecycle managed by City Manager ✅

2. **Smart City Role Ownership (Section 7.1)**
   - Post Office owns WebSocket Gateway Service ✅
   - City Manager controls activation ✅
   - No bypassing of Smart City authority ✅

3. **ConfigAdapter Pattern (Section 9)**
   - ConfigAdapter set at startup ✅
   - WebSocketRoutingHelper uses ConfigAdapter (no fallbacks) ✅
   - Fails fast if ConfigAdapter not available ✅

4. **City Manager Authority**
   - PostOfficeService activated via City Manager ✅
   - No direct service discovery bypass ✅
   - Proper lifecycle management ✅

### ⚠️ Areas for Improvement

1. **WebSocket Timeout Configuration**
   - Consider WebSocket-specific timeouts in Traefik entryPoint
   - Long-lived connections may need extended idle timeout

2. **Legacy Route Cleanup**
   - `/api/ws` route marked as legacy - consider removal after migration
   - Document deprecation timeline

3. **Health Check Endpoint**
   - WebSocket Gateway health endpoint exists but not exposed via Traefik
   - Consider adding dedicated health route

---

## 8. Recommendations

### Immediate Actions
1. ✅ **DONE**: Recreate backend container to pick up new router labels
2. **IN PROGRESS**: Test WebSocket connection with proper client
3. **TODO**: Verify FastAPI WebSocket handler receives requests
4. **TODO**: Check middleware interference with WebSocket upgrade

### Short-Term Improvements
1. Add WebSocket-specific timeout configuration
2. Document WebSocket routing architecture
3. Add health check route for WebSocket Gateway
4. Consider removing legacy `/api/ws` route after migration

### Long-Term Enhancements
1. Add WebSocket connection metrics to observability
2. Implement WebSocket connection pooling
3. Add WebSocket-specific rate limiting per user
4. Consider WebSocket sticky sessions for horizontal scaling

---

## 9. Conclusion

The Traefik configuration is **architecturally aligned** with the Platform Architecture document. The WebSocket routing issue was caused by:

1. **Router labels not applied**: Required container recreation (not restart)
2. **WebSocket handshake**: Needs proper WebSocket client testing

The configuration correctly:
- Respects Smart City role ownership
- Prioritizes transport services correctly
- Bypasses ForwardAuth for WebSocket (handler-level auth)
- Excludes WebSocket routes from main backend router

**Status**: Configuration is correct, testing WebSocket connection with proper client to verify end-to-end functionality.

