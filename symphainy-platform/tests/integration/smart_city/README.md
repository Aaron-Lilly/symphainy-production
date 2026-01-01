# Smart City Integration Tests

Integration tests for Smart City services with real infrastructure.

## Overview

These tests verify that Smart City services **actually work** with real infrastructure capabilities:
- Real Redis connections
- Real ArangoDB connections  
- Real Meilisearch connections
- Real infrastructure operations (store, retrieve, search)

## Prerequisites

1. **Start Infrastructure Services**:
   ```bash
   cd /home/founders/demoversion/symphainy_source/symphainy-platform
   docker-compose -f docker-compose.infrastructure.yml up -d
   ```

2. **Wait for Services to be Healthy**:
   ```bash
   # Check service health
   docker ps --filter "name=symphainy-"
   
   # Services should be running:
   # - symphainy-redis (port 6379)
   # - symphainy-arangodb (port 8529)
   # - symphainy-meilisearch (port 7700)
   # - symphainy-consul (port 8500)
   ```

## Running Tests

### Run All Integration Tests
```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
python3 -m pytest tests/integration/smart_city/ -v --tb=short
```

### Run Specific Test Categories

**Real Infrastructure Tests** (requires Docker services):
```bash
python3 -m pytest tests/integration/smart_city/test_smart_city_real_infrastructure.py -v -m "real_infrastructure"
```

**Foundation Integration Tests**:
```bash
python3 -m pytest tests/integration/smart_city/test_smart_city_foundation_integration.py -v
```

**Realm Exposure Tests** (requires Docker services):
```bash
python3 -m pytest tests/integration/smart_city/test_smart_city_realm_exposure.py -v -m "real_infrastructure"
```

### Skip Infrastructure Tests
```bash
python3 -m pytest tests/integration/smart_city/ -v -m "not real_infrastructure"
```

## Test Categories

### 1. Real Infrastructure Tests (`test_smart_city_real_infrastructure.py`)
- Tests Smart City services with **real** infrastructure (Redis, ArangoDB, Meilisearch)
- Verifies actual operations work (store, retrieve, search)
- Tests error handling with real infrastructure
- Verifies infrastructure abstractions are connected

**Key Tests**:
- `test_librarian_stores_knowledge_with_real_infrastructure` - Store knowledge using real Meilisearch/ArangoDB
- `test_librarian_retrieves_knowledge_with_real_infrastructure` - Retrieve knowledge from real infrastructure
- `test_librarian_searches_knowledge_with_real_infrastructure` - Search knowledge using real Meilisearch
- `test_librarian_infrastructure_abstractions_work` - Verify abstractions are connected
- `test_librarian_soa_apis_work_with_real_infrastructure` - Test SOA APIs with real infrastructure

### 2. Foundation Integration Tests (`test_smart_city_foundation_integration.py`)
- Tests Smart City services with full foundation stack
- Verifies Public Works, Curator, and Communication foundations work together
- Tests service registration with Curator
- Verifies shared infrastructure access

**Key Tests**:
- `test_foundations_initialize_together` - All foundations initialize correctly
- `test_smart_city_service_uses_public_works` - Services use Public Works Foundation
- `test_smart_city_service_registers_with_curator` - Services register with Curator
- `test_smart_city_service_can_use_communication` - Services can use Communication Foundation
- `test_city_manager_orchestrates_foundations` - City Manager orchestrates all foundations

### 3. Realm Exposure Tests (`test_smart_city_realm_exposure.py`)
- Tests that Smart City services properly expose their capabilities for other realms
- Verifies SOA APIs are registered with Curator and discoverable
- Tests MCP Tools are registered and accessible
- Verifies services can be discovered via PlatformCapabilitiesMixin methods
- Tests that other realms can access Smart City services via SOA APIs

**Key Tests**:
- `test_librarian_registers_soa_apis_with_curator` - SOA APIs registered with Curator
- `test_librarian_registers_mcp_tools_with_curator` - MCP Tools registered with Curator
- `test_services_can_be_discovered_via_curator` - Services discoverable via Curator
- `test_soa_apis_are_callable_with_real_infrastructure` - SOA APIs work with real infrastructure
- `test_platform_capabilities_mixin_methods_work` - PlatformCapabilitiesMixin methods work
- `test_other_realms_can_discover_librarian` - Other realms can discover Smart City services
- `test_other_realms_can_use_librarian_soa_api` - Other realms can use SOA APIs
- `test_city_manager_exposes_all_smart_city_services` - City Manager exposes all services

## Expected Results

### ✅ Success Criteria
- All infrastructure abstractions connect successfully
- Services can perform actual operations (store, retrieve, search)
- SOA APIs work with real infrastructure
- Services register with Curator Foundation
- Foundation stack initializes together
- Services can communicate with each other
- **Smart City services expose SOA APIs and MCP Tools for other realms**
- **Other realms can discover and use Smart City services via Curator**
- **PlatformCapabilitiesMixin methods work for service discovery**

### ⚠️ Common Issues

1. **Infrastructure Not Available**:
   - Error: `pytest.skip("Infrastructure not available")`
   - Solution: Start Docker Compose services

2. **Connection Timeouts**:
   - Error: Connection refused or timeout
   - Solution: Wait for services to be healthy, check ports

3. **Initialization Failures**:
   - Error: Service failed to initialize
   - Solution: Check infrastructure logs, verify configuration

## Next Steps

After these integration tests pass:
1. ✅ Smart City services work with real infrastructure
2. ✅ Foundation stack works together
3. ✅ Services can perform actual operations
4. ✅ Ready to test Business Enablement realm

