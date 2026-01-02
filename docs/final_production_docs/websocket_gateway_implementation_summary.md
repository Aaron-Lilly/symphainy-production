# WebSocket Gateway Implementation - Quick Reference

**Full Plan:** See `websocket_gateway_implementation_plan.md`

---

## 🎯 Key Decisions

1. **Post Office owns WebSocket Gateway** (Smart City Role = WHAT, Service = HOW)
2. **Single connection boundary** via `/ws` endpoint
3. **3-phase approach** with production-first design

---

## 📋 Phase Overview

### Phase 1: Stabilize (1-2 days)
- Create `WebSocketGatewayService` under Post Office
- Single `/ws` endpoint
- Logical channel routing (guide, pillar:content, etc.)
- Traffic Cop integration
- Readiness checks

### Phase 2: Architecture Cleanup (1-2 weeks)
- Service discovery via Consul
- Redis-backed connection registry
- Post Office SOA APIs for realm consumption
- Remove old WebSocket implementations
- Platform Gateway mappings

### Phase 3: Production Hardening (2-3 weeks)
- Redis fan-out (horizontal scaling)
- Observability (OpenTelemetry, metrics)
- Backpressure handling (circuit breakers, queues)
- Session eviction (heartbeat, idle timeout)

---

## 🏗️ Architecture

```
Traefik (/ws)
  ↓
Post Office Role (WHAT)
  ↓
WebSocket Gateway Service (HOW)
  ↓ (Redis Pub/Sub)
Agent Instances
```

---

## 📁 Key Files

- `backend/smart_city/services/post_office/websocket_gateway_service.py` (NEW)
- `backend/api/websocket_gateway_router.py` (NEW)
- `backend/smart_city/services/post_office/post_office_service.py` (UPDATE - add SOA APIs)
- `platform_infrastructure/infrastructure/platform_gateway.py` (UPDATE - add mappings)

---

## ✅ Success Criteria

- Phase 1: Browser testing unblocked, single endpoint working
- Phase 2: Clear layer separation, service discovery working
- Phase 3: Production-ready (scaling, observability, resilience)

---

**Timeline:** 4-6 weeks total

