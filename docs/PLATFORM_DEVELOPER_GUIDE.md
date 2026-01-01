# Platform Developer Guide & Toolkit
## Comprehensive Guide for Building Compliant Platform Features

**Date:** December 20, 2025  
**Status:** 📚 **Living Document**  
**Purpose:** Ensure all new features are built in a compliant, architecturally sound fashion

> **📝 Amendment Notice:** See `PLATFORM_DEVELOPER_GUIDE_AMENDMENT_2025.md` for recent updates including:
> - Agentic Correlation Pattern
> - Platform Data Sidecar Pattern
> - MVP as Realm Capability Demonstrations
> - Three Client Data Journeys
> - Bidirectional Bridge Pattern
> - DataAnalyzerService & VisualizationEngineService Patterns

---

## 📚 **Table of Contents**

1. [Platform Foundation & Architecture](#part-1-platform-foundation--architecture)
2. [Base Classes & Patterns](#part-2-base-classes--patterns)
3. [Security & Multi-Tenancy](#part-3-security--multi-tenancy)
4. [Service Discovery & Registration](#part-4-service-discovery--registration)
5. [Data Solution Architecture](#part-5-data-solution-architecture)
6. [Agentic Foundation & Agents](#part-6-agentic-foundation--agents)
7. [Utilities & Infrastructure](#part-7-utilities--infrastructure)
8. [MCP Tools & Agents](#part-8-mcp-tools--agents)
9. [Testing & Validation](#part-9-testing--validation)
10. [Common Patterns & Anti-Patterns](#part-10-common-patterns--anti-patterns)
11. [Development Workflow](#part-11-development-workflow)
12. [Reference & Quick Lookup](#part-12-reference--quick-lookup)

---

## Part 1: Platform Foundation & Architecture

### 1.1 Platform Overview

**Architecture Layers:**
```
Foundation Layer (EAGER - Always Start)
  ├── DI Container (Infrastructure Kernel)
  ├── Public Works Foundation
  ├── Platform Gateway Foundation
  ├── Curator Foundation
  ├── Agentic Foundation
  └── Experience Foundation

Realm Layer (LAZY - Load on Demand)
  ├── Smart City Realm
  ├── Business Enablement Realm
  ├── Experience Realm
  ├── Journey Realm
  └── Solution Realm

Service Layer (LAZY - Load on Demand)
  ├── Realm Services
  ├── Orchestrators
  ├── Managers
  └── Enabling Services

Agent Layer (LAZY - Load on Demand)
  ├── Liaison Agents
  ├── Specialist Agents
  └── Guide Agents
```

**Key Principles:**
- **Role = What:** Defines what a service does (semantic meaning)
- **Service = How:** Defines how a service does it (implementation)
- **Agent = Agency:** Agents have agency to make decisions
- **Micro-Modules:** Services stay under 350 lines (use micro-modules if needed)
- **Lazy Hydration:** Services load on-demand, not at startup
- **Zero-Trust Security:** Every operation validates security context
- **Semantic Data Boundary:** Platform only uses semantic data (embeddings), not raw parsed data

---

### 1.2 Startup Sequence & Bootstrap

#### Container & Poetry Setup

**Docker Container Initialization:**
- Platform runs in Docker container
- Poetry manages dependencies (`pyproject.toml`)
- Environment variables loaded from `.env.secrets`
- Test mode configuration via `TEST_MODE` environment variable
- GCP credentials protected (never in `.env.secrets`)

**Poetry Dependencies:**
```bash
# Install dependencies
poetry install

# Add new dependency
poetry add package-name

# Add dev dependency
poetry add --group dev package-name
```

#### Platform Bootstrap Flow

**Complete Startup Sequence:**

```python
# main.py - PlatformOrchestrator.orchestrate_platform_startup()

Phase 0.5: Generate workflow_id for correlation
  └── platform_startup_workflow_id = str(uuid.uuid4())

Phase 1: Bootstrap Foundation (EAGER)
  ├── DI Container initialization
  │   └── DIContainerService("platform_orchestrated")
  ├── FastAPI Router Manager (utility)
  │   └── FastAPIRouterManager()
  ├── Public Works Foundation
  │   └── PublicWorksFoundationService(di_container)
  ├── Platform Gateway Foundation
  │   └── PlatformGatewayFoundationService(di_container, public_works_foundation)
  ├── Curator Foundation
  │   └── CuratorFoundationService(di_container, public_works_foundation)
  ├── Agentic Foundation
  │   └── AgenticFoundationService(di_container, public_works_foundation, curator_foundation)
  └── Experience Foundation
      └── ExperienceFoundationService(di_container, public_works_foundation, curator_foundation)

Phase 2: Register Smart City Gateway (EAGER)
  └── Smart City Gateway registration

Phase 2.5: Initialize MVP Solution (EAGER - required for MVP)
  └── City Manager bootstrap (top-down)
      ├── Solution Manager
      │   └── SolutionManagerService(di_container, platform_gateway)
      ├── Journey Manager
      │   └── JourneyManagerService(di_container, platform_gateway, solution_manager)
      └── Delivery Manager
          └── DeliveryManagerService(di_container, platform_gateway, journey_manager)

Phase 3: Lazy Realm Hydration (deferred)
  └── Services load on-demand when first accessed

Phase 4: Background Health Watchers
  └── Async health monitoring tasks

Phase 5: Curator Auto-Discovery
  └── Continuous service discovery

Phase 6: Critical Services Health Validation
  └── Validate critical services are healthy
```

**Key Points:**
- **EAGER Services:** Foundations and critical infrastructure (always start)
- **LAZY Services:** Realms, services, orchestrators (load on-demand)
- **Top-Down Bootstrap:** City Manager → Solution → Journey → Delivery
- **Correlation Tracking:** `workflow_id` generated at startup for end-to-end tracking

---

### 1.3 DI Container Deep Dive

#### What It Is

**DIContainerService** is the **infrastructure kernel** (not a foundation service). It provides all utilities and service management for the entire platform.

**Key Responsibilities:**
- Service registration and discovery
- Utility provision (logging, config, health, telemetry, etc.)
- Foundation service management
- Security provider and authorization guard integration

#### Initialization

```python
# DI Container is initialized FIRST
di_container = DIContainerService("platform_orchestrated")

# Security components (optional, injected at initialization)
security_provider = SecurityProvider(...)
authorization_guard = AuthorizationGuard(...)
di_container = DIContainerService(
    "platform_orchestrated",
    security_provider=security_provider,
    authorization_guard=authorization_guard
)
```

#### Utilities Provided

All utilities are accessed via `di_container.get_utility(name)`:

| Utility | Access Pattern | Description |
|---------|---------------|-------------|
| `config` | `di_container.get_utility("config")` | Configuration management |
| `logger` | `di_container.get_logger("service_name")` | Logging service |
| `health` | `di_container.get_utility("health")` | Health monitoring |
| `telemetry` | `di_container.get_utility("telemetry")` | Telemetry tracking |
| `security` | `di_container.get_utility("security")` | Security utilities |
| `error_handler` | `di_container.get_utility("error_handler")` | Error handling |
| `tenant` | `di_container.get_utility("tenant")` | Tenant management |
| `validation` | `di_container.get_utility("validation")` | Data validation |
| `serialization` | `di_container.get_utility("serialization")` | Data serialization |

#### Service Registry

**Unified Service Registry:**
```python
# Register service
di_container.service_registry["MyService"] = my_service_instance

# Get service
service = di_container.service_registry.get("MyService")

# Get foundation service
foundation = di_container.get_foundation_service("CuratorFoundationService")
```

**Service Types:**
- `ServiceType.FOUNDATION` - Foundation services
- `ServiceType.INFRASTRUCTURE` - Infrastructure services
- `ServiceType.REALM` - Realm services
- `ServiceType.UTILITY` - Utility services

#### Security Integration

**SecurityProvider:**
- Token validation (JWKS local verification)
- Context extraction from tokens
- User/tenant information extraction

**AuthorizationGuard:**
- Policy enforcement
- Permission checking
- Resource access validation

Both are injected into DI Container at initialization and available to all services via SecurityMixin.

---

### 1.4 Foundation Layers

#### Foundation Services (EAGER - Always Start)

**1. DI Container** (Infrastructure Kernel)
- Not a foundation service - it IS the infrastructure
- Provides all utilities
- Manages service registry

**2. Public Works Foundation**
- Infrastructure abstractions (databases, messaging, caching)
- Infrastructure adapters (Supabase, ArangoDB, Redis, etc.)
- Provides infrastructure to all other foundations

**3. Platform Gateway Foundation**
- Gateway to abstractions for realms
- Validates access to infrastructure
- Provides realm-specific filtering

**4. Curator Foundation**
- Service discovery
- Capability registry
- Pattern validation
- Anti-pattern detection

**5. Agentic Foundation**
- Agent SDK and capabilities
- Agent factory
- MCP client management
- Policy integration

**6. Experience Foundation**
- Experience SDK and capabilities
- Frontend gateway builder
- Session manager builder
- User experience builder

#### Foundation Initialization Order

```python
# CRITICAL: Order matters - dependencies must be initialized first

1. DI Container (first - provides utilities)
   └── No dependencies

2. Public Works Foundation (infrastructure provider)
   └── Depends on: DI Container

3. Platform Gateway Foundation (gateway to abstractions)
   └── Depends on: DI Container, Public Works Foundation

4. Curator Foundation (service discovery)
   └── Depends on: DI Container, Public Works Foundation

5. Agentic Foundation (agent capabilities)
   └── Depends on: DI Container, Public Works Foundation, Curator Foundation

6. Experience Foundation (experience capabilities)
   └── Depends on: DI Container, Public Works Foundation, Curator Foundation
```

#### Foundation Access Pattern

```python
# ✅ CORRECT: Get foundation from DI Container
curator = di_container.get_foundation_service("CuratorFoundationService")
public_works = di_container.get_foundation_service("PublicWorksFoundationService")
agentic = di_container.get_foundation_service("AgenticFoundationService")

# ❌ WRONG: Direct import and initialization
from foundations.curator_foundation import CuratorFoundationService
curator = CuratorFoundationService(...)  # Don't do this!
```

---

### 1.5 Realms Architecture

#### Available Realms

**Smart City Realm:**
- Platform governance, security, data management
- Services: City Manager, Security Guard, Traffic Cop, Librarian, Content Steward, Data Steward, Conductor, Post Office, Nurse
- Base class: `SmartCityRoleBase`
- Access: Direct foundation access (not via Platform Gateway)

**Business Enablement Realm:**
- Content, insights, operations, business outcomes
- Services: Content Orchestrator, Insights Orchestrator, Operations Orchestrator, Business Outcomes Orchestrator, Enabling Services
- Base class: `RealmServiceBase` or `OrchestratorBase`
- Access: Via Platform Gateway

**Experience Realm:**
- Frontend integration, user experience
- Services: Frontend Gateway, Session Manager, User Experience
- Base class: `RealmServiceBase`
- Access: Via Platform Gateway

**Journey Realm:**
- Journey orchestration
- Services: Client Data Journey Orchestrator, Session Journey Orchestrator
- Base class: `OrchestratorBase`
- Access: Via Platform Gateway

**Solution Realm:**
- Solution orchestration
- Services: Data Solution Orchestrator, Solution Manager
- Base class: `OrchestratorBase` or `ManagerServiceBase`
- Access: Via Platform Gateway

#### Realm Service Pattern

```python
# All realm services extend RealmServiceBase
class MyRealmService(RealmServiceBase):
    def __init__(self, service_name, realm_name, platform_gateway, di_container):
        super().__init__(service_name, realm_name, platform_gateway, di_container)
    
    async def initialize(self):
        await super().initialize()
        
        # Get Smart City services via helper methods
        self.librarian = await self.get_librarian_api()
        
        # Get infrastructure via Platform Gateway
        self.file_mgmt = self.get_abstraction("file_management")
        
        # Register with Curator
        await self.register_with_curator(...)
```

---

## Part 2: Base Classes & Patterns

### 2.1 Base Class Hierarchy

#### FoundationServiceBase

**For:** Foundation services only

**Mixins:**
- `UtilityAccessMixin` - Utility access
- `InfrastructureAccessMixin` - Infrastructure access
- `PerformanceMonitoringMixin` - Performance monitoring

**Startup Policy:** `EAGER` (always start)

**Example:**
```python
class MyFoundationService(FoundationServiceBase):
    def __init__(self, service_name, di_container):
        super().__init__(
            service_name=service_name,
            di_container=di_container,
            security_provider=None,  # Set by DI container
            authorization_guard=None  # Set by DI container
        )
    
    async def initialize(self):
        await super().initialize()
        # Foundation-specific initialization
```

---

#### RealmServiceBase

**For:** All realm services

**Mixins:**
- `UtilityAccessMixin` - Utility access
- `InfrastructureAccessMixin` - Infrastructure access (via Platform Gateway)
- `SecurityMixin` - Security context management
- `PerformanceMonitoringMixin` - Performance monitoring
- `PlatformCapabilitiesMixin` - Curator, Smart City service access
- `CommunicationMixin` - Post Office, Traffic Cop access
- `MicroModuleSupportMixin` - Micro-module loading

**Startup Policy:** `LAZY` (load on-demand)

**Example:**
```python
class MyRealmService(RealmServiceBase):
    def __init__(self, service_name, realm_name, platform_gateway, di_container):
        super().__init__(service_name, realm_name, platform_gateway, di_container)
    
    async def initialize(self):
        await super().initialize()
        
        # Get Smart City services
        self.librarian = await self.get_librarian_api()
        
        # Get infrastructure
        self.file_mgmt = self.get_abstraction("file_management")
        
        # Register with Curator
        await self.register_with_curator(
            capabilities=[...],
            soa_apis=["method1", "method2"],
            mcp_tools=["tool1", "tool2"]
        )
```

---

#### SmartCityRoleBase

**For:** Smart City services only

**Mixins:** Same as RealmServiceBase + direct foundation access

**Key Difference:** Direct foundation access (not via Platform Gateway)

**Startup Policy:** `EAGER` (for critical services)

**Example:**
```python
class MySmartCityService(SmartCityRoleBase):
    def __init__(self, di_container):
        super().__init__(
            role_name="MySmartCityService",
            di_container=di_container
        )
    
    async def initialize(self):
        await super().initialize()
        
        # Direct foundation access (not via Platform Gateway)
        self.curator = self.di_container.get_foundation_service("CuratorFoundationService")
        self.public_works = self.di_container.get_foundation_service("PublicWorksFoundationService")
```

---

#### OrchestratorBase

**For:** Orchestrators (use case coordinators)

**Key Difference:** Composes RealmServiceBase (delegation, not inheritance)

**Startup Policy:** `LAZY` (load on-demand)

**Example:**
```python
class MyOrchestrator(OrchestratorBase):
    def __init__(self, service_name, realm_name, platform_gateway, di_container, delivery_manager):
        super().__init__(
            service_name=service_name,
            realm_name=realm_name,
            platform_gateway=platform_gateway,
            di_container=di_container,
            delivery_manager=delivery_manager
        )
    
    async def initialize(self):
        await super().initialize()
        
        # Get enabling services
        self.enabling_service = await self.get_enabling_service("MyEnablingService")
        
        # Get Smart City services (via delegation)
        self.librarian = await self.get_librarian_api()
        
        # Initialize agents
        self.agent = await self.initialize_agent(
            MyAgent,
            "MyAgent",
            agent_type="liaison"
        )
```

---

#### ManagerServiceBase

**For:** Manager services

**Key Difference:** Extends RealmServiceBase, adds manager-specific orchestration

**Startup Policy:** `LAZY` (load on-demand)

**Example:**
```python
class MyManagerService(ManagerServiceBase):
    def __init__(self, service_name, realm_name, platform_gateway, di_container):
        super().__init__(service_name, realm_name, platform_gateway, di_container)
    
    async def initialize(self):
        await super().initialize()
        # Manager-specific initialization
```

---

### 2.2 Mixins Deep Dive

#### UtilityAccessMixin

**Provides:**
- `get_utility(name)` - Get utility by name
- `get_config()` - Get configuration utility
- `get_health()` - Get health monitoring utility
- `get_telemetry()` - Get telemetry utility
- `get_error_handler()` - Get error handling utility

**Access Pattern:**
```python
# ✅ CORRECT: Use mixin methods
config = self.get_config()
health = self.get_health()
telemetry = self.get_telemetry()

# ❌ WRONG: Direct DI Container access
config = self.di_container.get_utility("config")  # Don't do this!
```

---

#### InfrastructureAccessMixin

**Provides:**
- `get_abstraction(name)` - Get infrastructure abstraction via Platform Gateway

**Access Pattern:**
```python
# ✅ CORRECT: Use Platform Gateway
file_mgmt = self.get_abstraction("file_management")
content_metadata = self.get_abstraction("content_metadata")
semantic_data = self.get_abstraction("semantic_data")

# ❌ WRONG: Direct Public Works access
file_mgmt = self.di_container.get_abstraction("file_management")  # Don't do this!
```

---

#### SecurityMixin

**Provides:**
- `get_security_context()` - Get current security context
- `set_security_context(context)` - Set security context
- `validate_access(resource, action)` - Validate access
- `get_tenant_id()` - Get current tenant ID
- `get_user_id()` - Get current user ID

**Access Pattern:**
```python
# ✅ CORRECT: Use mixin methods
tenant_id = self.get_tenant_id()
user_id = self.get_user_id()
context = self.get_security_context()

if not self.validate_access("file", "read"):
    raise PermissionError("Access denied")
```

---

#### PerformanceMonitoringMixin

**Provides:**
- `log_operation_with_telemetry(operation_name, success, details)` - Track operations

**Access Pattern:**
```python
# ✅ CORRECT: Track operations
await self.log_operation_with_telemetry(
    "my_operation_start",
    success=True
)

try:
    result = await self._do_work()
    await self.log_operation_with_telemetry(
        "my_operation_complete",
        success=True,
        details={"result_count": len(result)}
    )
except Exception as e:
    await self.log_operation_with_telemetry(
        "my_operation_complete",
        success=False,
        details={"error": str(e)}
    )
    raise
```

---

#### PlatformCapabilitiesMixin

**Provides:**
- `get_curator()` - Get Curator Foundation
- `register_with_curator(...)` - Register service with Curator
- `get_librarian_api()` - Get Librarian Smart City service
- `get_content_steward_api()` - Get Content Steward Smart City service
- `get_data_steward_api()` - Get Data Steward Smart City service
- `get_security_guard_api()` - Get Security Guard Smart City service
- `get_traffic_cop_api()` - Get Traffic Cop Smart City service
- `get_conductor_api()` - Get Conductor Smart City service
- `get_post_office_api()` - Get Post Office Smart City service
- `get_nurse_api()` - Get Nurse Smart City service
- `get_city_manager_api()` - Get City Manager Smart City service

**Access Pattern:**
```python
# ✅ CORRECT: Use helper methods
librarian = await self.get_librarian_api()
curator = self.get_curator()
await self.register_with_curator(...)

# ❌ WRONG: Direct foundation access (for realm services)
curator = self.di_container.get_foundation_service("CuratorFoundationService")  # Don't do this!
```

---

#### CommunicationMixin

**Provides:**
- Post Office access (messaging, events)
- Traffic Cop access (session management)

**Access Pattern:**
```python
# ✅ CORRECT: Use helper methods
post_office = await self.get_post_office_api()
traffic_cop = await self.get_traffic_cop_api()

# Publish event
await post_office.publish_event({
    "event_type": "file_uploaded",
    "file_id": file_id,
    "tenant_id": tenant_id
})
```

---

#### MicroModuleSupportMixin

**Provides:**
- Micro-module loading
- 350-line enforcement

**Access Pattern:**
```python
# Micro-modules are loaded automatically
# Services stay under 350 lines by using micro-modules
```

---

### 2.3 Service Creation Checklist

**Before Creating a Service:**
- [ ] Choose correct base class (FoundationServiceBase, RealmServiceBase, SmartCityRoleBase, OrchestratorBase, ManagerServiceBase)
- [ ] Understand startup policy (EAGER vs LAZY)
- [ ] Identify required mixins
- [ ] Plan service capabilities
- [ ] Plan SOA APIs
- [ ] Plan MCP tools (if needed)

**During Service Creation:**
- [ ] Initialize with DI Container (required)
- [ ] Initialize with Platform Gateway (for realm services)
- [ ] Implement `initialize()` method
- [ ] Get Smart City services via helper methods
- [ ] Get infrastructure abstractions via Platform Gateway
- [ ] Register with Curator
- [ ] Implement health check
- [ ] Add telemetry tracking
- [ ] Implement error handling
- [ ] Add security context validation
- [ ] Follow 350-line limit (use micro-modules if needed)

**After Service Creation:**
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test Curator registration
- [ ] Test Smart City service discovery
- [ ] Test infrastructure access
- [ ] Test security context validation
- [ ] Test multi-tenancy isolation
- [ ] Test telemetry tracking
- [ ] Test error handling

---

## Part 3: Security & Multi-Tenancy

### 3.1 Security Architecture

#### SecurityProvider

**Role:** Token validation, context extraction

**Responsibilities:**
- Validate JWT tokens (JWKS local verification)
- Extract user/tenant information from tokens
- Create SecurityContext objects

**Access Pattern:**
```python
# SecurityProvider is injected into DI Container
# Services access via SecurityMixin
security_context = self.get_security_context()
```

---

#### AuthorizationGuard

**Role:** Policy enforcement, permission checking

**Responsibilities:**
- Enforce authorization policies
- Check permissions
- Validate resource access

**Access Pattern:**
```python
# AuthorizationGuard is injected into DI Container
# Services access via SecurityMixin
if not self.validate_access("file", "read"):
    raise PermissionError("Access denied")
```

---

#### SecurityContextProvider

**Role:** Central security context management

**Responsibilities:**
- Extract context from tokens
- Manage security state
- Cache security contexts

**Implementation:**
- Uses JWKS local token validation
- Caches contexts (5-minute TTL)
- Falls back to network validation if needed

---

### 3.2 JWKS Local Token Validation

#### How It Works

**Flow:**
```
1. JWT token received
2. Extract kid (key ID) from JWT header
3. Fetch JWKS (cached, 10-minute TTL)
4. Find matching public key by kid
5. Verify JWT signature using RS256
6. Extract claims (user_id, email, tenant_id)
7. Query database for tenant info (if needed)
8. Return SecurityContext
```

**Benefits:**
- ✅ Fast (no network calls)
- ✅ Reliable (no dependency on Supabase API)
- ✅ Best practice (Supabase's recommended approach)
- ✅ Secure (RS256 asymmetric keys)

**Performance:**
- **Before:** 150-700ms (network call + database query)
- **After:** 51-210ms (local verification + database query)
- **Improvement:** ~3-5x faster

#### Implementation

```python
# AuthAbstraction uses local validation
security_context = await auth_abstraction.validate_token(token)

# Returns SecurityContext with:
# - user_id
# - tenant_id
# - roles
# - permissions
# - origin
```

---

### 3.3 Security Context Pattern

#### New Security Element

**Key Innovation:** Security context extracted once at gateway, passed through user_context

**Benefits:**
- No need to extract user_context repeatedly
- Consistent security context across all services
- Better performance (extract once, use many times)

**Pattern:**
```python
# Gateway extracts context once
security_context = await auth_abstraction.validate_token(token)
user_context = {
    "user_id": security_context.user_id,
    "tenant_id": security_context.tenant_id,
    "security_context": security_context
}

# Services use SecurityMixin
tenant_id = self.get_tenant_id()  # From SecurityMixin
user_id = self.get_user_id()  # From SecurityMixin
context = self.get_security_context()  # From SecurityMixin
```

---

### 3.4 Multi-Tenancy Patterns

#### Tenant Isolation

**Principle:** All queries filter by tenant_id

**Data Classification:**
- **Client Data:** `data_classification="client"`, `tenant_id != NULL`
- **Platform Data:** `data_classification="platform"`, `tenant_id` optional

**Access Pattern:**
```python
# ✅ CORRECT: Always filter by tenant_id
tenant_id = self.get_tenant_id()
query = {
    "tenant_id": tenant_id,
    "data_classification": "client"
}
results = await self.semantic_data.query(query)

# ❌ WRONG: No tenant filtering
results = await self.semantic_data.query({})  # Don't do this!
```

#### Access Validation

```python
# ✅ CORRECT: Validate access before operations
if not self.validate_access("file", "read"):
    raise PermissionError("Access denied")

# Then proceed with operation
result = await self._read_file(file_id)
```

---

## Part 4: Service Discovery & Registration

### 4.1 Curator Foundation

#### What It Provides

**Capabilities:**
- Service registry (cache-based, fast)
- Capability registry (capability-based discovery)
- Service discovery (via Public Works, optional)
- Pattern validation
- Anti-pattern detection

**Access Pattern:**
```python
# Get Curator
curator = self.get_curator()

# Register service
await curator.register_service(service_instance, service_metadata)

# Discover service
service = await curator.get_service("ServiceName")
```

---

### 4.2 Service Registration Pattern

#### Standard Registration

```python
await self.register_with_curator(
    capabilities=[
        {
            "name": "capability_name",
            "protocol": "IProtocolName",
            "description": "Description",
            "semantic_mapping": {
                "domain_capability": "domain.capability",
                "semantic_api": "/api/v1/endpoint"
            },
            "contracts": {
                "soa_api": {
                    "api_name": "method_name",
                    "endpoint": "/api/v1/endpoint",
                    "method": "POST"
                },
                "mcp_tool": {
                    "tool_name": "tool_name",
                    "tool_definition": {...}
                }
            }
        }
    ],
    soa_apis=["method1", "method2"],
    mcp_tools=["tool1", "tool2"]
)
```

#### Registration Checklist

- [ ] Define capabilities (what the service can do)
- [ ] Define SOA APIs (how to call the service)
- [ ] Define MCP tools (if applicable)
- [ ] Define semantic mappings (domain capabilities)
- [ ] Define contracts (REST API, MCP tool definitions)
- [ ] Register with Curator
- [ ] Verify registration (check Curator registry)

---

### 4.3 Service Discovery Pattern

#### Four-Tier Access Pattern

**Tier 1:** Enabling Service (via Curator)
```python
service = await self.get_enabling_service("ServiceName")
```

**Tier 2:** Direct import and initialization (fallback)
```python
if not service:
    from backend.path import ServiceName
    service = ServiceName(...)
    await service.initialize()
```

**Tier 3:** SOA API or Platform Gateway equivalent (if available)
```python
if not service:
    # Use SOA API or Platform Gateway equivalent
    result = await self.call_soa_api("ServiceName", "method", params)
```

**Tier 4:** Return None (calling code handles None gracefully)
```python
if not service:
    self.logger.warning("Service not available")
    return None
```

#### Discovery Pattern

```python
# ✅ CORRECT: Four-tier pattern
async def _get_enabling_service(self, service_name):
    # Tier 1: Try Curator discovery
    service = await self.get_enabling_service(service_name)
    if service:
        return service
    
    # Tier 2: Direct import
    try:
        from backend.path import ServiceName
        service = ServiceName(...)
        await service.initialize()
        return service
    except Exception as e:
        self.logger.warning(f"Failed to import {service_name}: {e}")
    
    # Tier 3: SOA API (if available)
    # ... (not always applicable)
    
    # Tier 4: Return None
    return None
```

---

## Part 5: Data Solution Architecture

### 5.1 Data Solution Orchestrator

#### Role

**Lightweight shell with platform correlation**

**Responsibilities:**
1. **Client Data Operations** → delegates to ClientDataJourneyOrchestratorService
2. **Platform Correlation** → orchestrates all platform services

#### Platform Correlation Orchestration

**Services Orchestrated:**
- **Security Guard:** Validate auth & tenant
- **Traffic Cop:** Manage session/state
- **Conductor:** Track workflow
- **Post Office:** Publish events & messaging
- **Nurse:** Record telemetry & observability

**Pattern:**
```python
# Data Solution Orchestrator orchestrates platform correlation
async def orchestrate_data_ingest(self, file_data, user_context):
    workflow_id = user_context.get("workflow_id") or str(uuid.uuid4())
    
    # Platform correlation
    await self.security_guard.validate_auth(user_context)
    await self.traffic_cop.manage_session(user_context)
    await self.conductor.track_workflow(workflow_id)
    
    # Client data operation
    result = await self.client_data_journey.orchestrate_data_ingest(
        file_data=file_data,
        user_context=user_context,
        workflow_id=workflow_id
    )
    
    # Platform correlation (events, telemetry)
    await self.post_office.publish_event({
        "event_type": "data_ingested",
        "file_id": result["file_id"],
        "workflow_id": workflow_id
    })
    await self.nurse.record_telemetry("data_ingest", success=True)
    
    return result
```

---

### 5.2 Client Data Journey Orchestrator

#### Role

**Orchestrates client data journey (Ingest → Parse → Embed → Expose)**

**Flow:**
```
ClientDataJourneyOrchestratorService
  ↓ composes
FrontendGatewayService (Experience Realm)
  ↓ routes to
ContentOrchestrator (Business Enablement Realm)
  ↓ composes
Smart City Services
```

**Methods:**
- `orchestrate_data_ingest()` - File upload
- `orchestrate_data_parse()` - File parsing
- `orchestrate_data_embed()` - Semantic embedding creation
- `orchestrate_data_expose()` - Semantic layer exposure

---

### 5.3 Semantic Data Layer Security

#### Security Boundary

**Principle:** Platform only uses semantic data (embeddings), not raw parsed data

**Why:**
- Client data security (platform doesn't see raw data)
- Compliance (platform uses semantic layer only)
- Scalability (semantic layer is optimized for queries)

#### Semantic Enrichment Gateway

**When embeddings insufficient, request enrichment (not raw data)**

**Pattern:**
```python
# Platform requests enrichment (not raw data)
enrichment_request = {
    "content_id": content_id,
    "enrichment_type": "missing_fields",
    "fields_needed": ["field1", "field2"]
}

# Enrichment service (secure boundary) creates new embeddings
new_embeddings = await semantic_enrichment_gateway.enrich_semantic_layer(
    content_id=content_id,
    enrichment_request=enrichment_request,
    user_context=user_context
)

# Platform queries enriched semantic layer
results = await self.semantic_data.query({
    "content_id": content_id,
    "tenant_id": tenant_id
})
```

**Security:**
- Enrichment service is in secure boundary
- Platform never sees raw parsed data
- Only semantic embeddings are created and stored
- Platform queries semantic layer only

---

## Part 6: Agentic Foundation & Agents

### 6.1 Agentic Foundation SDK

#### What It Provides

**Components:**
- **AgentBase** - Base class for all agents
- **MCPClientManager** - MCP client management
- **PolicyIntegration** - Policy enforcement
- **ToolComposition** - Tool chaining
- **BusinessAbstractionHelper** - Business logic helpers
- **AGUI schema registry** - AGUI schema management

**Access Pattern:**
```python
# Get Agentic Foundation
agentic = di_container.get_foundation_service("AgenticFoundationService")

# Get agent factory
agent_factory = agentic.get_agent_factory()

# Create agent
agent = await agent_factory.create_agent(
    agent_class=MyAgent,
    agent_name="MyAgent",
    agent_type="liaison"
)
```

---

### 6.2 Agent Creation Pattern

#### Using Agentic Foundation Factory

```python
# ✅ CORRECT: Use Agentic Foundation factory
agent = await self.initialize_agent(
    agent_class=MyAgent,
    agent_name="MyAgent",
    agent_type="liaison",  # or "specialist", "guide"
    capabilities=["capability1", "capability2"],
    required_roles=["role1", "role2"]
)
```

#### Agent Base Class

**AgentBase provides:**
- Multi-tenant awareness
- Agentic business abstraction integration
- Smart City role integration via MCP tools
- Policy-aware tool execution
- Security and governance integration
- Structured AGUI output generation
- Unified observability and monitoring

**Example:**
```python
class MyAgent(AgentBase):
    def __init__(self, ...):
        super().__init__(
            agent_name="MyAgent",
            capabilities=["capability1"],
            required_roles=["role1"],
            agui_schema=self._create_agui_schema(),
            foundation_services=di_container,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter
        )
    
    async def process(self, request, user_context):
        # Get LLM client
        llm_client = self.get_llm_client()
        
        # Get MCP tools
        mcp_tools = self.get_mcp_tools()
        
        # Call tools
        result = await self.call_mcp_tool(
            "tool_name",
            {"param1": "value1"},
            user_context=user_context
        )
        
        # Generate AGUI response
        agui_response = self.generate_agui_response(result)
        return agui_response
```

---

## Part 7: Utilities & Infrastructure

### 7.1 Routing Architecture

#### HTTP REST API Routing

All HTTP REST API requests flow through the centralized routing system:

**Flow:**
```
Client Request
  ↓
Traefik (Gateway)
  ↓
FastAPI App (main.py)
  ↓
Universal Pillar Router (/api/v1/{pillar}-pillar/{path:path})
  ↓
FrontendGatewayService.route_frontend_request()
  ↓
Pillar Orchestrator (Content/Insights/Operations/BusinessOutcomes)
  ↓
Business Logic Services
```

**Key Components:**
- **Universal Pillar Router** (`backend/api/universal_pillar_router.py`)
  - Single router handles ALL pillars
  - Pattern: `/api/v1/{pillar}-pillar/{path:path}`
  - Routes to `FrontendGatewayService`
  
- **FrontendGatewayService** (`foundations/experience_foundation/services/frontend_gateway_service/`)
  - Centralized routing logic
  - Discovers orchestrators via Curator
  - Handles request transformation and validation

**Registration:**
- `register_api_routers()` in `backend/api/__init__.py`
- Order: Auth Router → Universal Router → WebSocket Router

#### WebSocket Routing (Special Protocol)

WebSocket connections use a separate router due to protocol differences:

**Flow:**
```
Client WebSocket Request
  ↓
Traefik (Gateway) - Bypasses ForwardAuth for /api/ws
  ↓
FastAPI App (main.py)
  ↓
FastAPICORSMiddleware (bypasses CORS for /api/ws)
  ↓
WebSocket Router (/api/ws/agent)
  ↓
UnifiedAgentWebSocketSDK
  ↓
Agent (Guide/Liaison)
```

**Key Components:**
- **WebSocket Router** (`backend/api/websocket_router.py`)
  - Separate router, not part of universal router
  - Endpoints: `/api/ws/agent`, `/api/ws/guide`, `/api/ws/liaison/{pillar}`
  - Direct agent communication (no FrontendGatewayService)

- **UnifiedAgentWebSocketSDK** (`foundations/experience_foundation/sdk/unified_agent_websocket_sdk.py`)
  - Routes messages to appropriate agents
  - Handles session management via Traffic Cop

**Why Separate?**
- Websockets use upgrade protocol (not HTTP)
- Direct agent communication is simpler
- Authentication via `session_token` query parameter
- CORS handling is different (bypass for websockets)

#### CORS Configuration

CORS is handled centrally through routing utilities:

**Location:** `utilities/api_routing/websocket_routing_helper.py`

**Configuration:**
- Environment-aware (dev vs production)
- Loads from environment variables: `CORS_ORIGINS`, `API_CORS_ORIGINS`
- WebSocket paths automatically bypass CORS (auth via session_token)

**WebSocket Security Features:**
1. **Origin Validation** - Validates origin even if CORS bypassed (security in depth)
2. **Connection Limits** - Per-user and global connection limits
3. **Rate Limiting** - Per-session message rate limits
4. **Security Logging** - Logs failed authentication attempts

**Configuration Variables:**
```bash
# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://symphainy.com
API_CORS_ORIGINS=http://localhost:3000,https://symphainy.com

# WebSocket Configuration
WEBSOCKET_PATHS=/api/ws
WEBSOCKET_MAX_CONNECTIONS_PER_USER=5
WEBSOCKET_MAX_GLOBAL_CONNECTIONS=1000
WEBSOCKET_MAX_MESSAGES_PER_SECOND=10
WEBSOCKET_MAX_MESSAGES_PER_MINUTE=100
```

**Adding New Endpoints:**
1. **HTTP REST:** Add to Universal Router pattern (`/api/v1/{pillar}-pillar/{path}`)
2. **WebSocket:** Add to WebSocket Router (`/api/ws/{endpoint}`)
3. **CORS:** Automatically handled by middleware

### 7.2 Utilities (via DI Container)

**All utilities accessed via `di_container.get_utility(name)`:**

| Utility | Access Pattern | Description |
|---------|---------------|-------------|
| `config` | `self.get_utility("config")` | Configuration management |
| `logger` | `self.logger` (from mixin) | Logging service |
| `health` | `self.get_health()` | Health monitoring |
| `telemetry` | `self.get_telemetry()` | Telemetry tracking |
| `security` | `self.get_utility("security")` | Security utilities |
| `error_handler` | `self.get_error_handler()` | Error handling |
| `tenant` | `self.get_utility("tenant")` | Tenant management |
| `validation` | `self.get_utility("validation")` | Data validation |
| `serialization` | `self.get_utility("serialization")` | Data serialization |

---

### 7.2 Infrastructure Abstractions (via Platform Gateway)

**All abstractions accessed via `self.get_abstraction(name)`:**

| Abstraction | Access Pattern | Description |
|------------|---------------|-------------|
| `file_management` | `self.get_abstraction("file_management")` | File storage and retrieval |
| `content_metadata` | `self.get_abstraction("content_metadata")` | Content metadata management |
| `semantic_data` | `self.get_abstraction("semantic_data")` | Semantic data queries |
| `authentication` | `self.get_abstraction("authentication")` | Authentication |
| `authorization` | `self.get_abstraction("authorization")` | Authorization |
| `messaging` | `self.get_abstraction("messaging")` | Messaging |
| `caching` | `self.get_abstraction("caching")` | Caching |

---

### 7.3 Smart City Services (via Helper Methods)

**All Smart City services accessed via helper methods:**

| Service | Access Pattern | Description |
|---------|---------------|-------------|
| Librarian | `await self.get_librarian_api()` | Document storage and retrieval |
| Content Steward | `await self.get_content_steward_api()` | Content management |
| Data Steward | `await self.get_data_steward_api()` | Data management |
| Security Guard | `await self.get_security_guard_api()` | Security and authentication |
| Traffic Cop | `await self.get_traffic_cop_api()` | Session and state management |
| Conductor | `await self.get_conductor_api()` | Workflow orchestration |
| Post Office | `await self.get_post_office_api()` | Events and messaging |
| Nurse | `await self.get_nurse_api()` | Telemetry and observability |
| City Manager | `await self.get_city_manager_api()` | City management |

---

## Part 8: MCP Tools & Agents

### 8.1 MCP Server Pattern

#### MCPServerBase

**Extends:** `MCPServerBase`

**Pattern:**
```python
class MyServiceMCPServer(MCPServerBase):
    def __init__(self, service, di_container):
        super().__init__(
            server_name="my_service_mcp",
            di_container=di_container,
            server_type="single_service"  # 1:1 for realm services
        )
        self.service = service
        self._register_tools()
    
    def _register_tools(self):
        # Register tools
        self.register_tool(
            name="tool_name",
            description="Tool description",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                }
            },
            handler=self._handle_tool
        )
    
    async def execute_tool(self, tool_name: str, parameters: dict):
        # Route to service SOA API
        if tool_name == "tool_name":
            return await self.service.method_name(**parameters)
        raise ValueError(f"Unknown tool: {tool_name}")
```

---

### 8.2 Agent Tool Usage

#### Agents Call Tools via MCP

```python
# Agent calls MCP tool
result = await self.call_mcp_tool(
    "tool_name",
    {"param1": "value1"},
    user_context=user_context
)
```

---

## Part 9: Testing & Validation

### 9.1 Testing Patterns

#### Unit Tests

**Test individual methods in isolation:**
```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_my_service_method():
    # Setup
    di_container = Mock()
    platform_gateway = Mock()
    service = MyService("MyService", "realm", platform_gateway, di_container)
    
    # Test
    result = await service.my_method()
    
    # Assert
    assert result["success"] == True
```

#### Integration Tests

**Test service interactions:**
```python
@pytest.mark.asyncio
async def test_service_integration():
    # Setup real services
    di_container = DIContainerService("test")
    await di_container.initialize()
    
    # Test
    service = MyService("MyService", "realm", platform_gateway, di_container)
    await service.initialize()
    
    # Assert
    assert service.is_initialized == True
```

#### E2E Tests

**Test complete workflows:**
```python
@pytest.mark.asyncio
async def test_e2e_workflow():
    # Setup complete platform
    # ... (full platform initialization)
    
    # Test complete workflow
    result = await orchestrator.handle_request(request)
    
    # Assert
    assert result["success"] == True
```

---

### 9.2 Validation Checklist

**Service Validation:**
- [ ] Service initializes correctly
- [ ] Curator registration works
- [ ] Smart City service discovery works
- [ ] Infrastructure abstractions accessible
- [ ] Security context validation works
- [ ] Multi-tenancy isolation verified
- [ ] Telemetry tracking works
- [ ] Error handling works
- [ ] Health checks pass
- [ ] MCP tools registered (if applicable)
- [ ] Agents initialize (if applicable)

---

## Part 10: Common Patterns & Anti-Patterns

### 10.1 ✅ DO's

- ✅ Use correct base class for service type
- ✅ Initialize with DI Container
- ✅ Register with Curator
- ✅ Use helper methods for Smart City services
- ✅ Use Platform Gateway for infrastructure
- ✅ Validate security context
- ✅ Track telemetry for operations
- ✅ Handle errors with audit
- ✅ Follow 350-line limit
- ✅ Use micro-modules for complex services
- ✅ Propagate workflow_id for correlation
- ✅ Use semantic data layer (not raw parsed data)
- ✅ Use Agentic Foundation SDK (not CrewAI)
- ✅ Use JWKS local token validation
- ✅ Extract security context once at gateway

---

### 10.2 ❌ DON'Ts

- ❌ Direct Public Works access (use Platform Gateway)
- ❌ Direct Communication Foundation access (use helper methods)
- ❌ Custom storage implementations (use Smart City services)
- ❌ Custom validation logic (use Smart City services)
- ❌ Hard-coded values (use configuration)
- ❌ LLM in services (LLM only in agents)
- ❌ CrewAI patterns (use Agentic Foundation SDK)
- ❌ Direct database access (use abstractions)
- ❌ Bypass security validation
- ❌ Skip Curator registration
- ❌ Ignore multi-tenancy
- ❌ Access parsed data directly (use semantic layer)
- ❌ Network token validation (use JWKS local)
- ❌ Extract user_context repeatedly (extract once at gateway)

---

## Part 11: Development Workflow

### 11.1 Creating a New Service

**Step 1: Choose Base Class**
```python
# Foundation service → FoundationServiceBase
# Realm service → RealmServiceBase
# Smart City service → SmartCityRoleBase
# Orchestrator → OrchestratorBase
# Manager → ManagerServiceBase
```

**Step 2: Create Service File**
```python
class MyService(RealmServiceBase):
    def __init__(self, service_name, realm_name, platform_gateway, di_container):
        super().__init__(service_name, realm_name, platform_gateway, di_container)
    
    async def initialize(self):
        await super().initialize()
        
        # Get Smart City services
        self.librarian = await self.get_librarian_api()
        
        # Get infrastructure
        self.file_mgmt = self.get_abstraction("file_management")
        
        # Register with Curator
        await self.register_with_curator(
            capabilities=[...],
            soa_apis=["method1", "method2"],
            mcp_tools=["tool1", "tool2"]
        )
```

**Step 3: Implement SOA APIs**
```python
async def my_soa_api(self, param1, param2, user_context=None):
    """Clear, atomic SOA API method."""
    # Validate security context
    tenant_id = self.get_tenant_id()
    
    # Track telemetry
    await self.log_operation_with_telemetry("my_soa_api_start", success=True)
    
    try:
        # Use Smart City services
        result = await self.librarian.store_document(...)
        
        # Track success
        await self.log_operation_with_telemetry("my_soa_api_complete", success=True)
        return {"success": True, "result": result}
    except Exception as e:
        # Track failure
        await self.log_operation_with_telemetry("my_soa_api_complete", success=False)
        await self.handle_error_with_audit(e, "my_soa_api")
        raise
```

**Step 4: Create MCP Server (if needed)**
```python
class MyServiceMCPServer(MCPServerBase):
    def __init__(self, service, di_container):
        super().__init__("my_service_mcp", di_container, "single_service")
        self.service = service
        self._register_tools()
    
    async def execute_tool(self, tool_name: str, parameters: dict):
        return await self.service.my_soa_api(**parameters)
```

**Step 5: Test**
```python
# Unit tests
# Integration tests
# E2E tests
```

---

### 11.2 Creating a New Agent

**Step 1: Extend AgentBase**
```python
class MyAgent(AgentBase):
    def __init__(self, ...):
        super().__init__(
            agent_name="MyAgent",
            capabilities=["capability1"],
            required_roles=["role1"],
            agui_schema=self._create_agui_schema(),
            ...
        )
```

**Step 2: Use Agentic Foundation SDK**
```python
async def process(self, request, user_context):
    # Get LLM client
    llm_client = self.get_llm_client()
    
    # Get MCP tools
    mcp_tools = self.get_mcp_tools()
    
    # Call tools
    result = await self.call_mcp_tool(
        "tool_name",
        {"param1": "value1"},
        user_context=user_context
    )
    
    # Generate AGUI response
    return self.generate_agui_response(result)
```

**Step 3: Initialize via Factory**
```python
agent = await orchestrator.initialize_agent(
    MyAgent,
    "MyAgent",
    agent_type="liaison"
)
```

---

### 11.3 Creating a New Orchestrator

**Step 1: Extend OrchestratorBase**
```python
class MyOrchestrator(OrchestratorBase):
    def __init__(self, delivery_manager):
        super().__init__(
            service_name="MyOrchestratorService",
            realm_name=delivery_manager.realm_name,
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            delivery_manager=delivery_manager
        )
```

**Step 2: Compose Services**
```python
async def initialize(self):
    await super().initialize()
    
    # Get enabling services
    self.enabling_service = await self.get_enabling_service("MyEnablingService")
    
    # Get Smart City services
    self.librarian = await self.get_librarian_api()
    
    # Initialize agents
    self.agent = await self.initialize_agent(
        MyAgent,
        "MyAgent",
        agent_type="liaison"
    )
```

**Step 3: Register with Curator**
```python
await self.register_with_curator(
    capabilities=[...],
    soa_apis=["method1", "method2"]
)
```

---

## Part 12: Reference & Quick Lookup

### 12.1 Quick Reference: Base Classes

| Service Type | Base Class | Startup Policy | Key Mixins |
|-------------|------------|----------------|------------|
| Foundation | FoundationServiceBase | EAGER | UtilityAccess, InfrastructureAccess, PerformanceMonitoring |
| Realm Service | RealmServiceBase | LAZY | All 7 mixins |
| Smart City | SmartCityRoleBase | EAGER | All 7 mixins + direct foundation access |
| Orchestrator | OrchestratorBase | LAZY | Composes RealmServiceBase |
| Manager | ManagerServiceBase | LAZY | Extends RealmServiceBase |

---

### 12.2 Quick Reference: Access Patterns

| What You Need | How to Get It | Example |
|--------------|---------------|---------|
| Utility | `self.get_utility("name")` | `self.get_utility("config")` |
| Infrastructure | `self.get_abstraction("name")` | `self.get_abstraction("file_management")` |
| Smart City Service | `await self.get_librarian_api()` | `await self.get_librarian_api()` |
| Foundation Service | `di_container.get_foundation_service("Name")` | `di_container.get_foundation_service("CuratorFoundationService")` |
| Enabling Service | `await self.get_enabling_service("Name")` | `await self.get_enabling_service("DataAnalyzerService")` |
| Agent | `await self.initialize_agent(...)` | `await self.initialize_agent(MyAgent, "MyAgent")` |

---

### 12.3 Quick Reference: Security

| Operation | Pattern | Example |
|-----------|---------|---------|
| Get tenant ID | `self.get_tenant_id()` | `tenant_id = self.get_tenant_id()` |
| Get user ID | `self.get_user_id()` | `user_id = self.get_user_id()` |
| Validate access | `self.validate_access(resource, action)` | `if not self.validate_access("file", "read"): raise PermissionError()` |
| Get security context | `self.get_security_context()` | `context = self.get_security_context()` |

---

### 12.4 Quick Reference: Curator Registration

```python
await self.register_with_curator(
    capabilities=[{
        "name": "capability_name",
        "protocol": "IProtocol",
        "description": "Description",
        "semantic_mapping": {...},
        "contracts": {
            "soa_api": {...},
            "mcp_tool": {...}
        }
    }],
    soa_apis=["method1", "method2"],
    mcp_tools=["tool1", "tool2"]
)
```

---

## 📋 **Validation Checklists**

### Service Creation Checklist

- [ ] Correct base class chosen
- [ ] Initialized with DI Container
- [ ] Initialized with Platform Gateway (if realm service)
- [ ] `initialize()` method implemented
- [ ] Smart City services accessed via helper methods
- [ ] Infrastructure accessed via Platform Gateway
- [ ] Registered with Curator
- [ ] Health check implemented
- [ ] Telemetry tracking added
- [ ] Error handling implemented
- [ ] Security context validation added
- [ ] Multi-tenancy isolation verified
- [ ] 350-line limit followed (micro-modules if needed)
- [ ] Unit tests written
- [ ] Integration tests written

### Agent Creation Checklist

- [ ] Extends AgentBase
- [ ] Uses Agentic Foundation SDK
- [ ] Initialized via factory
- [ ] MCP tools accessible
- [ ] LLM client accessible
- [ ] AGUI schema defined
- [ ] Security context validated
- [ ] Multi-tenancy aware
- [ ] Unit tests written
- [ ] Integration tests written

### Orchestrator Creation Checklist

- [ ] Extends OrchestratorBase
- [ ] Composes RealmServiceBase
- [ ] Enabling services discovered
- [ ] Smart City services accessed
- [ ] Agents initialized
- [ ] Registered with Curator
- [ ] Workflow correlation tracked
- [ ] Telemetry tracking added
- [ ] Error handling implemented
- [ ] Unit tests written
- [ ] Integration tests written

---

## 🎯 **Next Steps**

1. **Review this guide** - Understand all patterns
2. **Use for Insights Pillar** - Ensure compliant implementation
3. **Update as needed** - Living document, evolves with platform
4. **Share with team** - Ensure all developers use it

---

**Last Updated:** December 20, 2025  
**Status:** 📚 **Living Document**  
**Maintainer:** Platform Architecture Team


