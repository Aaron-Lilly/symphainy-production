# WebSocket Gateway Tests

Comprehensive tests for the WebSocket Gateway Service using **real production infrastructure** to ensure it actually works before trying in the browser.

## Overview

These tests validate all three phases of the WebSocket Gateway implementation:

- **Phase 1**: Basic connection handling, channel routing, session validation
- **Phase 2**: Redis-backed connection registry, SOA APIs, MCP tools, Consul registration
- **Phase 3**: Fan-out message distribution, backpressure handling, session eviction, OpenTelemetry observability

## Test Files

### `test_websocket_gateway_integration.py`
Integration tests that verify WebSocket Gateway functionality with real infrastructure:
- Connection acceptance and welcome messages
- Channel routing (guide, pillar:content, pillar:insights, etc.)
- Redis-backed connection registry
- Post Office SOA APIs
- Connection statistics
- Fan-out message distribution
- Backpressure handling
- Session eviction and heartbeat
- OpenTelemetry metrics and tracing

### `test_websocket_gateway_e2e.py`
End-to-end tests that simulate real browser usage:
- Complete connection flow (connect → welcome → message → response)
- Channel switching (guide ↔ pillar channels)
- Concurrent connections (multiple browser tabs)
- Connection recovery after network issues
- Error handling (invalid JSON, missing fields, etc.)
- Heartbeat/keepalive handling

## Prerequisites

### Required Infrastructure (Running)
- ✅ **Backend** (`symphainy-backend-prod`) - Port 8000
- ✅ **Redis** (`symphainy-redis`) - Port 6379
- ✅ **Traffic Cop Service** - For session validation
- ✅ **Post Office Service** - With WebSocket Gateway initialized

### Environment Variables
```bash
export TEST_USE_REAL_INFRASTRUCTURE=true
export TEST_BACKEND_URL="http://localhost:8000"
export TEST_REDIS_URL="redis://localhost:6379"
```

## Running Tests

### Run All WebSocket Tests
```bash
cd /home/founders/demoversion/symphainy_source/tests
pytest integration/smart_city/test_websocket_gateway_*.py -v
```

### Run Integration Tests Only
```bash
pytest integration/smart_city/test_websocket_gateway_integration.py -v -m integration
```

### Run E2E Tests Only
```bash
pytest integration/smart_city/test_websocket_gateway_e2e.py -v -m e2e
```

### Run Specific Test
```bash
pytest integration/smart_city/test_websocket_gateway_integration.py::TestWebSocketGatewayIntegration::test_websocket_connection_accepts -v
```

### Run with Real Infrastructure Check
```bash
# Tests will automatically validate infrastructure is available
pytest integration/smart_city/test_websocket_gateway_*.py -v --tb=short
```

## Test Coverage

### Phase 1: Basic Functionality ✅
- [x] WebSocket connection acceptance
- [x] Welcome message delivery
- [x] Channel routing (guide, pillar channels)
- [x] Invalid message format handling
- [x] Session validation

### Phase 2: Redis & SOA APIs ✅
- [x] Redis-backed connection registry
- [x] Channel subscription tracking
- [x] Post Office SOA API: `get_websocket_endpoint`
- [x] Post Office SOA API: `publish_to_agent_channel`
- [x] Connection count statistics

### Phase 3: Production Hardening ✅
- [x] Fan-out message distribution
- [x] Backpressure handling (circuit breakers)
- [x] Session eviction (heartbeat monitoring)
- [x] OpenTelemetry metrics collection
- [x] OpenTelemetry distributed tracing

### E2E: Real Browser Simulation ✅
- [x] Complete connection flow
- [x] Channel switching
- [x] Concurrent connections
- [x] Connection recovery
- [x] Error handling
- [x] Heartbeat/keepalive

## What These Tests Verify

### ✅ Real Infrastructure Works
Tests use **actual Redis, Traffic Cop, and Post Office services** - no mocks. This ensures:
- Real session validation works
- Real Redis Pub/Sub works
- Real connection registry works
- Real message routing works

### ✅ Browser Compatibility
E2E tests simulate **exact browser behavior**:
- WebSocket connection establishment
- Message format (channel-based routing)
- Error handling
- Connection lifecycle

### ✅ Production Readiness
Tests verify **production features**:
- Horizontal scaling (fan-out across instances)
- Backpressure handling (circuit breakers)
- Resource management (session eviction)
- Observability (metrics, tracing)

## Troubleshooting

### Connection Refused
```
Error: Connection refused
```
**Solution**: Ensure backend is running on port 8000
```bash
docker ps | grep backend
```

### Redis Connection Failed
```
Error: Redis connection failed
```
**Solution**: Ensure Redis is running
```bash
docker ps | grep redis
redis-cli ping  # Should return PONG
```

### Session Validation Failed
```
Error: Session validation failed
```
**Solution**: Ensure Traffic Cop service is initialized and accessible via DI Container

### No Welcome Message
```
Timeout waiting for welcome message
```
**Solution**: 
1. Check backend logs for WebSocket Gateway initialization
2. Verify `/ws` endpoint is registered in FastAPI
3. Check Traefik routing for `/ws` path

## Test Output

### Successful Test Run
```
integration/smart_city/test_websocket_gateway_integration.py::TestWebSocketGatewayIntegration::test_websocket_connection_accepts PASSED
integration/smart_city/test_websocket_gateway_integration.py::TestWebSocketGatewayIntegration::test_websocket_channel_routing_guide PASSED
...
```

### Failed Test
```
FAILED integration/smart_city/test_websocket_gateway_integration.py::TestWebSocketGatewayIntegration::test_websocket_connection_accepts
AssertionError: WebSocket connection not open
```

## Next Steps

After these tests pass:
1. ✅ WebSocket Gateway is production-ready
2. ✅ Real infrastructure integration works
3. ✅ Browser compatibility verified
4. ✅ Ready to test in actual browser

## Notes

- Tests use **real infrastructure** by default (no mocks)
- Tests are **asynchronous** (use `pytest-asyncio`)
- Tests use **websockets library** for WebSocket client
- Tests validate **all three phases** of implementation
- Tests simulate **real browser behavior** in E2E tests

