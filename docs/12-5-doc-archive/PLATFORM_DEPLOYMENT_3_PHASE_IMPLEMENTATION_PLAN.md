# Platform Deployment: 3-Phase Implementation Plan

**Date:** December 2024  
**Status:** 📋 **PLAN CREATED** - Ready for Implementation  
**Purpose:** Implement enterprise-grade multi-tenant platform architecture with security, config plane, and CLI integration

---

## 🎯 Executive Summary

This plan implements the enterprise platform architecture outlined in `platformdeploymentpatterns.md`, focusing on three critical areas:

1. **Phase 1: Security (Supabase) Integration with Traefik** - Tenant-aware authentication and authorization at the gateway layer
2. **Phase 2: Client Config Foundation** - Customer-specific configuration management (config plane)
3. **Phase 3: CLI Integration** - Tenant-aware CLI tools with config plane integration

**Goal:** Enable multi-tenant SaaS architecture with single gateway, tenant isolation, and customer-specific configurations that don't fork the platform.

---

## 📊 Architecture Vision

### Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Traefik Gateway (Single Entry Point)          │
│  - Tenant-aware routing (Host rules, PathPrefix)            │
│  - Supabase ForwardAuth middleware                          │
│  - Tenant-aware middleware                                  │
│  - Multi-entrypoint support (customer-specific domains)     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Platform Core (Multi-tenant)                   │
│  - Strong tenant context propagation                        │
│  - DDD boundaries                                            │
│  - Shared compute where safe                                │
│  - Namespace-isolated storage                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Client Config Foundation (Config Plane)              │
│  - Domain models (schemas, mapping rules)                    │
│  - Workflows (per-client workflows)                         │
│  - Dashboards & views (personalized)                        │
│  - Ingestion endpoints (per-client)                          │
│  - User management (RBAC hierarchy)                         │
│  - AI/agent personas (action patterns)                      │
└─────────────────────────────────────────────────────────────┘
```

### Foundation Integration

```
Client Config Foundation
    ↓ (uses storage abstractions)
Public Works Foundation
    ↓ (provides storage mechanisms)
Git-backed or DB-backed storage

Client Config Foundation
    ↓ (exposes configs to clients)
Experience Foundation
    ↓ (renders configs for different "heads")
Frontend / CLI / API clients
```

---

## 🚀 Phase 1: Security (Supabase) Integration with Traefik

**Duration:** Week 1  
**Priority:** HIGH - Enables everything else  
**Goal:** Implement tenant-aware authentication and authorization at the gateway layer

### Objectives

1. Add Supabase ForwardAuth middleware to Traefik
2. Update Security Guard to expose ForwardAuth endpoint
3. Add tenant-aware routing rules in Traefik
4. Implement tenant context extraction and propagation
5. Test tenant isolation at gateway layer

### Tasks

#### 1.1: Add Supabase ForwardAuth Middleware to Traefik

**File:** `symphainy-platform/traefik-config/middlewares.yml`

**Changes:**
- Add `supabase-auth` middleware with ForwardAuth configuration
- Configure auth response headers (X-User-Id, X-Tenant-Id, X-User-Email, X-User-Roles)
- Add `tenant-context` middleware for tenant header propagation

**Implementation:**
```yaml
http:
  middlewares:
    # Supabase JWT Validation Middleware
    supabase-auth:
      forwardAuth:
        address: "http://security-guard:8000/api/v1/auth/validate-token"
        authResponseHeaders:
          - "X-User-Id"
          - "X-Tenant-Id"
          - "X-User-Email"
          - "X-User-Roles"
          - "X-User-Permissions"
        trustForwardHeader: true
        authResponseHeadersRegex: "^X-.*"
    
    # Tenant-aware routing middleware
    tenant-context:
      headers:
        customRequestHeaders:
          X-Tenant-Id: "{tenant_id_from_jwt}"
          X-User-Id: "{user_id_from_jwt}"
    
    # Combined middleware chain with auth
    backend-chain-with-auth:
      chain:
        middlewares:
          - supabase-auth
          - tenant-context
          - rate-limit
          - cors-headers
          - compression
          - security-headers
```

#### 1.2: Update Security Guard to Expose ForwardAuth Endpoint

**File:** `backend/smart_city/services/security_guard/security_guard_service.py`

**Changes:**
- Add `/api/v1/auth/validate-token` endpoint for Traefik ForwardAuth
- Validate Supabase JWT token
- Extract tenant_id, user_id, roles, permissions from token
- Return appropriate HTTP status codes (200 for valid, 401 for invalid)
- Set response headers for Traefik to forward

**Implementation:**
```python
async def validate_token_forwardauth(self, request: Request) -> Response:
    """
    ForwardAuth endpoint for Traefik.
    
    Validates Supabase JWT token and returns user context in headers.
    Traefik will forward these headers to backend services.
    """
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return Response(status_code=401)
    
    token = auth_header.replace("Bearer ", "")
    
    # Validate token via Supabase
    security_context = await self.authentication_module.validate_token(token)
    
    if not security_context or not security_context.get("valid"):
        return Response(status_code=401)
    
    # Return 200 with user context in headers
    headers = {
        "X-User-Id": security_context.get("user_id", ""),
        "X-Tenant-Id": security_context.get("tenant_id", ""),
        "X-User-Email": security_context.get("email", ""),
        "X-User-Roles": ",".join(security_context.get("roles", [])),
        "X-User-Permissions": ",".join(security_context.get("permissions", []))
    }
    
    return Response(status_code=200, headers=headers)
```

#### 1.3: Add Tenant-Aware Routing Rules in Traefik

**File:** `symphainy-platform/docker-compose.infrastructure.yml` (Traefik labels)

**Changes:**
- Add tenant-aware routing labels to services
- Support both Host-based routing (client1.symphainy.com) and PathPrefix routing (/api/v1/tenants/{tenant_id}/...)
- Add tenant labels to Consul service registry

**Implementation:**
```yaml
# Example: Frontend Gateway Service
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.frontend-gateway.rule=PathPrefix(`/api/v1`)"
  - "traefik.http.routers.frontend-gateway.entrypoints=web"
  - "traefik.http.routers.frontend-gateway.middlewares=backend-chain-with-auth"
  - "traefik.http.services.frontend-gateway.loadbalancer.server.port=8000"
  - "traefik.http.routers.frontend-gateway.service=frontend-gateway"
  # Tenant-aware routing
  - "traefik.http.routers.frontend-gateway.rule=PathPrefix(`/api/v1`) || Host(`client1.symphainy.com`)"
```

#### 1.4: Implement Tenant Context Extraction and Propagation

**File:** `symphainy-platform/foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py`

**Changes:**
- Extract tenant_id from request headers (X-Tenant-Id from Traefik)
- Propagate tenant context to all downstream services
- Validate tenant access before processing requests

**Implementation:**
```python
async def route_frontend_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Route frontend request with tenant context."""
    # Extract tenant context from Traefik headers
    tenant_id = request.get("headers", {}).get("X-Tenant-Id")
    user_id = request.get("headers", {}).get("X-User-Id")
    
    # Build user context
    user_context = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "email": request.get("headers", {}).get("X-User-Email"),
        "roles": request.get("headers", {}).get("X-User-Roles", "").split(","),
        "permissions": request.get("headers", {}).get("X-User-Permissions", "").split(",")
    }
    
    # Validate tenant access
    if tenant_id:
        tenant = self.get_tenant()
        if tenant and not await tenant.validate_tenant_access(tenant_id):
            return {"success": False, "error": "Tenant access denied"}
    
    # Add tenant context to request
    request["user_context"] = user_context
    request["params"]["tenant_id"] = tenant_id
    
    # Continue with routing...
```

#### 1.5: Update Traefik Configuration for Consul Provider

**File:** `symphainy-platform/traefik-config/traefik.yml`

**Changes:**
- Add Consul provider for dynamic routing
- Configure Consul service discovery
- Enable tenant-aware service tags

**Implementation:**
```yaml
providers:
  consul:
    endpoint: "consul:8500"
    watch: true
    prefix: "traefik"
    exposedByDefault: false
    defaultRule: "Host(`{{ .Name }}.localhost`)"
```

### Testing

1. **Test ForwardAuth Endpoint**
   - Valid token → 200 with headers
   - Invalid token → 401
   - Missing token → 401

2. **Test Tenant-Aware Routing**
   - Request with tenant_id → routed correctly
   - Request without tenant_id → rejected or default tenant
   - Request with invalid tenant_id → rejected

3. **Test Tenant Isolation**
   - Tenant A cannot access Tenant B data
   - Tenant context propagated to all services
   - Tenant-aware filtering works correctly

### Deliverables

- ✅ Supabase ForwardAuth middleware in Traefik
- ✅ Security Guard ForwardAuth endpoint
- ✅ Tenant-aware routing rules
- ✅ Tenant context extraction and propagation
- ✅ Test suite for security integration

---

## 🏗️ Phase 2: Client Config Foundation (Config Plane)

**Duration:** Week 2-3  
**Priority:** HIGH - Core to GTM model  
**Goal:** Create Client Config Foundation for customer-specific configuration management

### Objectives

1. Create Client Config Foundation Service
2. Implement SDK builders (ConfigLoader, ConfigStorage, ConfigValidator, ConfigVersioner)
3. Integrate with Public Works Foundation (storage abstractions)
4. Integrate with Experience Foundation (config exposure)
5. Implement Git-backed and DB-backed storage
6. Create config types (domain models, workflows, dashboards, etc.)

### Tasks

#### 2.1: Create Client Config Foundation Service

**File:** `foundations/client_config_foundation/client_config_foundation_service.py`

**Structure:**
```python
class ClientConfigFoundationService(FoundationServiceBase):
    """
    Client Config Foundation Service - Customer Configuration Management
    
    WHAT: Manages customer-specific configurations that don't fork the platform
    HOW: SDK builders + Storage abstractions (Git-backed or DB-backed)
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        super().__init__(...)
        
        # SDK builders
        self.config_loader_builder = ConfigLoaderBuilder
        self.config_storage_builder = ConfigStorageBuilder
        self.config_validator_builder = ConfigValidatorBuilder
        self.config_versioner_builder = ConfigVersionerBuilder
        
        # Foundation dependencies
        self.public_works_foundation = public_works_foundation
```

#### 2.2: Implement SDK Builders

**Files:**
- `foundations/client_config_foundation/sdk/config_loader_builder.py`
- `foundations/client_config_foundation/sdk/config_storage_builder.py`
- `foundations/client_config_foundation/sdk/config_validator_builder.py`
- `foundations/client_config_foundation/sdk/config_versioner_builder.py`

**ConfigLoaderBuilder:**
- Load tenant configs from Git or DB
- Support config types (domain_models, workflows, dashboards, etc.)
- Cache configs for performance
- Support config inheritance (base configs + tenant overrides)

**ConfigStorageBuilder:**
- Store tenant configs in Git or DB
- Support version control (Git commits, DB snapshots)
- Validate configs before storage
- Support config updates and rollback

**ConfigValidatorBuilder:**
- Schema validation for configs
- Tenant isolation validation
- Dependency validation (configs that reference other configs)
- Business rule validation

**ConfigVersionerBuilder:**
- Git versioning (commits, branches, tags)
- DB versioning (timestamps, snapshots)
- Rollback capabilities
- Version comparison and diff

#### 2.3: Integrate with Public Works Foundation

**Implementation:**
```python
class ConfigStorageBuilder:
    def __init__(self, public_works_foundation):
        # Use Public Works abstractions
        self.file_management = public_works_foundation.get_abstraction("FileManagementAbstraction")
        self.knowledge_discovery = public_works_foundation.get_abstraction("KnowledgeDiscoveryAbstraction")
        
    async def store_config(self, tenant_id: str, config_type: str, config: Dict, storage_type: str = "db"):
        if storage_type == "git":
            # Git-backed (via FileManagementAbstraction)
            await self._store_in_git(tenant_id, config_type, config)
        elif storage_type == "db":
            # DB-backed (via KnowledgeDiscoveryAbstraction)
            await self._store_in_db(tenant_id, config_type, config)
        else:
            # Hybrid (Git for versioned, DB for dynamic)
            await self._store_hybrid(tenant_id, config_type, config)
```

#### 2.4: Integrate with Experience Foundation

**File:** `foundations/experience_foundation/sdk/frontend_gateway_builder.py`

**Changes:**
- Use Client Config Foundation to load tenant-specific configs
- Apply tenant configs to gateway routes, dashboards, workflows

**Implementation:**
```python
class FrontendGatewayBuilder:
    def __init__(self, client_config_foundation):
        self.config_loader = client_config_foundation.create_config_loader(...)
        
    async def build_gateway(self, tenant_id: str):
        # Load tenant-specific configs
        tenant_config = await self.config_loader.load_tenant_config(tenant_id)
        
        # Apply tenant-specific routes, dashboards, workflows
        gateway = FrontendGateway(tenant_config)
        return gateway
```

#### 2.5: Implement Config Types

**Config Types to Support:**

1. **Domain Models** (`domain_models`)
   - Custom schemas (Insurance Use Case mapping rules)
   - Canonical model extensions
   - Field mappings

2. **Workflows** (`workflows`)
   - Per-client workflow definitions
   - Business process automation
   - Approval chains

3. **Dashboards & Views** (`dashboards`)
   - Personalized dashboard layouts
   - Custom visualizations
   - Report templates

4. **Ingestion Endpoints** (`ingestion_endpoints`)
   - Per-client API endpoints
   - Data source configurations
   - Integration settings

5. **User Management** (`user_management`)
   - RBAC hierarchies
   - Permission sets
   - Role definitions

6. **AI/Agent Personas** (`ai_agent_personas`)
   - Agent action patterns
   - Insights modules
   - AI model preferences

#### 2.6: Storage Implementation

**Git-Backed Storage:**
- Store configs in Git repository (one repo per tenant or branch per tenant)
- Use FileManagementAbstraction for Git operations
- Support commits, branches, tags for versioning
- Enable rollback and audit trail

**DB-Backed Storage:**
- Store configs in ArangoDB with tenant isolation
- Use KnowledgeDiscoveryAbstraction for DB operations
- Support fast retrieval and dynamic updates
- Enable versioning via timestamps and snapshots

**Hybrid Storage:**
- Git for versioned configs (domain_models, workflows)
- DB for dynamic configs (dashboards, user_preferences)
- Automatic sync between Git and DB

### Testing

1. **Test Config Loading**
   - Load tenant configs from Git
   - Load tenant configs from DB
   - Load hybrid configs

2. **Test Config Storage**
   - Store configs in Git
   - Store configs in DB
   - Validate configs before storage

3. **Test Config Versioning**
   - Git versioning (commits, branches)
   - DB versioning (snapshots)
   - Rollback capabilities

4. **Test Tenant Isolation**
   - Tenant A cannot access Tenant B configs
   - Configs are properly namespaced

### Deliverables

- ✅ Client Config Foundation Service
- ✅ SDK builders (ConfigLoader, ConfigStorage, ConfigValidator, ConfigVersioner)
- ✅ Public Works Foundation integration
- ✅ Experience Foundation integration
- ✅ Git-backed and DB-backed storage
- ✅ Config types implementation
- ✅ Test suite for config plane

---

## 🛠️ Phase 3: CLI Integration

**Duration:** Week 4  
**Priority:** MEDIUM - Polish and integration  
**Goal:** Make CLI tenant-aware and integrate with config plane

### Objectives

1. Add tenant context to CLI
2. Add Supabase JWT auth to CLI
3. Integrate CLI with config plane
4. Enable tenant-specific CLI commands
5. Test CLI with tenant isolation

### Tasks

#### 3.1: Add Tenant Context to CLI

**File:** `scripts/insurance_use_case/data_mash_cli.py`

**Changes:**
- Add tenant_id and api_token to CLI initialization
- Extract tenant context from environment or config
- Include tenant context in all API requests

**Implementation:**
```python
class DataMashCLI:
    def __init__(self):
        self.tenant_id = os.getenv("SYMPHAINY_TENANT_ID")
        self.api_token = os.getenv("SYMPHAINY_API_TOKEN")  # Supabase JWT
        self.api_base_url = os.getenv("SYMPHAINY_API_URL", "http://localhost/api")
    
    async def _make_request(self, endpoint: str, method: str, data: Dict):
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "X-Tenant-Id": self.tenant_id,
            "Content-Type": "application/json"
        }
        # Use Traefik route: http://localhost/api/v1/insurance-migration/...
        url = f"{self.api_base_url}/v1/{endpoint}"
        # Make request with headers...
```

#### 3.2: Add Supabase JWT Auth to CLI

**Changes:**
- Validate JWT token before making requests
- Refresh token if expired
- Handle authentication errors gracefully

**Implementation:**
```python
async def _validate_token(self):
    """Validate Supabase JWT token."""
    if not self.api_token:
        raise ValueError("API token not provided. Set SYMPHAINY_API_TOKEN environment variable.")
    
    # Validate token format (basic check)
    if not self.api_token.startswith("eyJ"):
        raise ValueError("Invalid token format")
    
    # Token will be validated by Traefik ForwardAuth middleware
    return True
```

#### 3.3: Integrate CLI with Config Plane

**File:** `scripts/insurance_use_case/data_mash_cli.py`

**Changes:**
- Use Client Config Foundation to load tenant-specific CLI commands
- Support tenant-specific workflows and configurations
- Enable tenant-specific command variations

**Implementation:**
```python
async def _load_tenant_config(self):
    """Load tenant-specific CLI configuration."""
    # Use Client Config Foundation (via API or direct access)
    config_endpoint = f"{self.api_base_url}/v1/config/tenant/{self.tenant_id}/cli"
    response = await self._make_request(config_endpoint, "GET", {})
    
    if response.get("success"):
        return response.get("config", {})
    return {}
```

#### 3.4: Enable Tenant-Specific CLI Commands

**Changes:**
- Load tenant-specific command definitions from config plane
- Support tenant-specific workflows
- Enable tenant-specific command aliases

**Implementation:**
```python
async def _get_tenant_commands(self):
    """Get tenant-specific CLI commands from config plane."""
    tenant_config = await self._load_tenant_config()
    return tenant_config.get("commands", {})

async def ingest(self, file_path: str, format: str = "auto"):
    """Ingest file with tenant-specific configuration."""
    # Load tenant-specific ingestion config
    tenant_config = await self._load_tenant_config()
    ingestion_config = tenant_config.get("ingestion", {})
    
    # Apply tenant-specific settings
    # ...
```

#### 3.5: Update CLI Documentation

**File:** `scripts/insurance_use_case/README.md`

**Changes:**
- Document tenant context setup
- Document authentication setup
- Document tenant-specific commands
- Document config plane integration

### Testing

1. **Test CLI Authentication**
   - Valid token → requests succeed
   - Invalid token → requests fail
   - Missing token → error message

2. **Test Tenant Context**
   - CLI with tenant_id → requests include tenant context
   - CLI without tenant_id → error or default tenant
   - CLI with invalid tenant_id → access denied

3. **Test Config Plane Integration**
   - CLI loads tenant-specific commands
   - CLI applies tenant-specific configurations
   - CLI respects tenant isolation

### Deliverables

- ✅ Tenant-aware CLI
- ✅ Supabase JWT auth in CLI
- ✅ Config plane integration
- ✅ Tenant-specific CLI commands
- ✅ Updated CLI documentation
- ✅ Test suite for CLI integration

---

## 📋 Implementation Checklist

### Phase 1: Security Integration
- [ ] Add Supabase ForwardAuth middleware to Traefik
- [ ] Update Security Guard to expose ForwardAuth endpoint
- [ ] Add tenant-aware routing rules in Traefik
- [ ] Implement tenant context extraction and propagation
- [ ] Update Traefik configuration for Consul provider
- [ ] Test ForwardAuth endpoint
- [ ] Test tenant-aware routing
- [ ] Test tenant isolation

### Phase 2: Client Config Foundation
- [ ] Create Client Config Foundation Service
- [ ] Implement ConfigLoaderBuilder
- [ ] Implement ConfigStorageBuilder
- [ ] Implement ConfigValidatorBuilder
- [ ] Implement ConfigVersionerBuilder
- [ ] Integrate with Public Works Foundation
- [ ] Integrate with Experience Foundation
- [ ] Implement Git-backed storage
- [ ] Implement DB-backed storage
- [ ] Implement hybrid storage
- [ ] Implement domain_models config type
- [ ] Implement workflows config type
- [ ] Implement dashboards config type
- [ ] Implement ingestion_endpoints config type
- [ ] Implement user_management config type
- [ ] Implement ai_agent_personas config type
- [ ] Test config loading
- [ ] Test config storage
- [ ] Test config versioning
- [ ] Test tenant isolation

### Phase 3: CLI Integration
- [ ] Add tenant context to CLI
- [ ] Add Supabase JWT auth to CLI
- [ ] Integrate CLI with config plane
- [ ] Enable tenant-specific CLI commands
- [ ] Update CLI documentation
- [ ] Test CLI authentication
- [ ] Test tenant context
- [ ] Test config plane integration

---

## 🎯 Success Criteria

### Phase 1 Success Criteria
- ✅ All API requests authenticated via Traefik ForwardAuth
- ✅ Tenant context extracted and propagated to all services
- ✅ Tenant isolation enforced at gateway layer
- ✅ No direct service access bypassing Traefik

### Phase 2 Success Criteria
- ✅ Client Config Foundation operational
- ✅ Configs stored in Git or DB (configurable)
- ✅ Configs loaded and applied to services
- ✅ Tenant-specific configs isolated by tenant_id
- ✅ Experience Foundation uses configs for tenant-specific experiences

### Phase 3 Success Criteria
- ✅ CLI authenticated via Supabase JWT
- ✅ CLI includes tenant context in all requests
- ✅ CLI loads tenant-specific commands from config plane
- ✅ CLI respects tenant isolation

---

## 📚 Documentation

### Phase 1 Documentation
- Traefik ForwardAuth configuration guide
- Security Guard ForwardAuth endpoint documentation
- Tenant-aware routing guide
- Tenant context propagation guide

### Phase 2 Documentation
- Client Config Foundation architecture
- SDK builder usage guide
- Config storage guide (Git vs DB)
- Config types reference
- Config versioning guide

### Phase 3 Documentation
- CLI setup guide (authentication, tenant context)
- CLI usage guide
- Tenant-specific CLI commands guide
- Config plane integration guide

---

## 🚀 Next Steps

1. **Review and approve this plan**
2. **Start Phase 1: Security Integration**
3. **Complete Phase 1 testing**
4. **Start Phase 2: Client Config Foundation**
5. **Complete Phase 2 testing**
6. **Start Phase 3: CLI Integration**
7. **Complete Phase 3 testing**
8. **Integration testing across all phases**
9. **Production deployment**

---

**Last Updated:** December 2024  
**Status:** Ready for Implementation




