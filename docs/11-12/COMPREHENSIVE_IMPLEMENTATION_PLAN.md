# Comprehensive Implementation Plan: Platform Production Readiness

**Date**: December 2024  
**Status**: 🎯 Ready for Execution  
**Goal**: Ensure symphainy-platform + symphainy-frontend works end-to-end, aligned with README.md vision

---

## Executive Summary

This plan addresses all critical issues preventing production deployment:
1. **Platform Startup Failure** - Missing router module blocks startup
2. **Frontend-Backend Disconnection** - Routes not registered, frontend can't connect
3. **Curator Refactoring** - Critical path for standardization and routing metadata
4. **Utility Compliance Gaps** - Journey/Solution realms missing utilities
5. **Routing Architecture** - Incomplete, needs universal router with versioning

**Success Criteria**: Platform starts successfully, frontend connects, CTO demo scenarios work, all utilities compliant, Curator standardized.

---

## Architecture Principles

### From README.md Vision
- **Headless Architecture**: Platform core decoupled from frontend
- **Semantic APIs**: User-focused, domain-aligned REST APIs
- **API Versioning**: `/api/v1/...` pattern for extensibility
- **Service Mesh Ready**: Routing metadata tracked for Consul Connect evolution
- **Smart City First-Class Citizen**: Platform governance built-in

### Implementation Standards
- **No Parallel Implementations**: Archive old, rename new (no `_updated`/`_new` suffixes)
- **Single Registration Path**: Curator as central hub
- **Protocol-Agnostic Gateway**: FrontendGatewayService supports REST/WebSocket/GraphQL
- **Utility Compliance**: All services use logging, error handling, telemetry, security, multi-tenancy

---

## Phase 1: Critical Unblock (Universal Router + Frontend Migration)

**Goal**: Fix platform startup and frontend connection  
**Time**: 3-4 hours  
**Priority**: 🔴 CRITICAL - Blocks everything else

### 1.1: Implement Universal Pillar Router

**File**: `symphainy-platform/backend/api/universal_pillar_router.py`

**Requirements**:
- Handle `/api/v1/{pillar}/{path:path}` pattern
- Support pillars: `content-pillar`, `insights-pillar`, `operations-pillar`, `business-outcomes-pillar`
- Support HTTP methods: GET, POST, PUT, DELETE, PATCH
- Call `FrontendGatewayService.route_frontend_request()`
- Extract request data (body, headers, query params, user_id, session_token)

**Implementation**:
```python
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Universal Pillar API"])

_frontend_gateway = None

def set_frontend_gateway(gateway):
    """Inject FrontendGatewayService (dependency injection)."""
    global _frontend_gateway
    _frontend_gateway = gateway
    logger.info("✅ Universal router connected to Frontend Gateway Service")

def get_frontend_gateway():
    """Get FrontendGatewayService."""
    if not _frontend_gateway:
        raise HTTPException(
            status_code=503,
            detail="Frontend Gateway Service not initialized"
        )
    return _frontend_gateway

@router.api_route(
    "/api/v1/{pillar}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def universal_pillar_handler(request: Request, pillar: str, path: str):
    """
    Universal handler for ALL pillar requests with versioning.
    
    Routes:
    - /api/v1/content-pillar/*           → ContentAnalysisOrchestrator
    - /api/v1/insights-pillar/*          → InsightsOrchestrator  
    - /api/v1/operations-pillar/*         → OperationsOrchestrator
    - /api/v1/business-outcomes-pillar/* → BusinessOutcomesOrchestrator
    
    All business logic is in FrontendGatewayService!
    """
    gateway = get_frontend_gateway()
    
    # Extract request data
    body = {}
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except:
            body = {}
    
    # Route to gateway (all validation, transformation, orchestration happens there!)
    return await gateway.route_frontend_request({
        "endpoint": f"/api/v1/{pillar}/{path}",
        "method": request.method,
        "params": body,
        "headers": dict(request.headers),
        "user_id": request.headers.get("X-User-ID"),
        "session_token": request.headers.get("X-Session-Token"),
        "query_params": dict(request.query_params)
    })
```

**Success Criteria**:
- [ ] File created at `backend/api/universal_pillar_router.py`
- [ ] Handles `/api/v1/{pillar}/{path:path}` pattern
- [ ] Extracts request data correctly
- [ ] Calls `FrontendGatewayService.route_frontend_request()`

---

### 1.2: Implement register_api_routers()

**File**: `symphainy-platform/backend/api/__init__.py`

**Requirements**:
- Export `register_api_routers()` function
- Get `FrontendGatewayService` from platform orchestrator
- Create universal pillar router
- Register router with FastAPI app
- Set frontend gateway in router

**Implementation**:
```python
"""
API Layer for SymphAIny Platform

This module provides FastAPI routers that connect the frontend to the backend services.
All routes go through the appropriate managers and orchestrators.
"""

from fastapi import FastAPI
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Import universal router
from .universal_pillar_router import router as universal_pillar_router, set_frontend_gateway

async def register_api_routers(app: FastAPI, platform_orchestrator) -> None:
    """
    Register API routers with FastAPI app.
    
    This function:
    1. Gets FrontendGatewayService from platform orchestrator
    2. Creates universal pillar router
    3. Registers router with FastAPI app
    4. Connects router to FrontendGatewayService
    
    Args:
        app: FastAPI application instance
        platform_orchestrator: PlatformOrchestrator instance
    """
    try:
        logger.info("🔌 Registering API routers...")
        
        # Get FrontendGatewayService from platform orchestrator
        experience_foundation = platform_orchestrator.foundation_services.get("ExperienceFoundationService")
        if not experience_foundation:
            raise RuntimeError("ExperienceFoundationService not found in platform orchestrator")
        
        # Get FrontendGatewayService
        frontend_gateway = experience_foundation.get_frontend_gateway_service()
        if not frontend_gateway:
            raise RuntimeError("FrontendGatewayService not found in ExperienceFoundationService")
        
        # Set frontend gateway in universal router
        set_frontend_gateway(frontend_gateway)
        logger.info("✅ FrontendGatewayService connected to universal router")
        
        # Register universal router with FastAPI app
        app.include_router(universal_pillar_router)
        logger.info("✅ Universal pillar router registered with FastAPI app")
        
        logger.info("🎉 API routers registered successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to register API routers: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise RuntimeError(f"API router registration failed: {e}") from e
```

**Success Criteria**:
- [ ] File updated at `backend/api/__init__.py`
- [ ] `register_api_routers()` function implemented
- [ ] Gets FrontendGatewayService from platform orchestrator
- [ ] Registers universal router with FastAPI app
- [ ] Handles errors gracefully

---

### 1.3: Update FrontendGatewayService to Handle Pillar Names

**File**: `symphainy-platform/foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py`

**Requirements**:
- Update routing logic to handle `content-pillar`, `insights-pillar`, `operations-pillar`, `business-outcomes-pillar`
- Support `/api/v1/{pillar}/{path}` pattern
- Parse version from endpoint (currently `v1`, future `v2`, `v3`)

**Changes Needed**:
1. Update endpoint parsing (line ~271) to handle `/api/v1/{pillar}/{path}`:
   ```python
   # Parse endpoint: /api/v1/{pillar}/{path}
   parts = endpoint.strip("/").split("/")
   if len(parts) < 4 or parts[0] != "api" or parts[1] != "v1":
       return {
           "success": False,
           "error": "Invalid Endpoint",
           "message": f"Endpoint must be /api/v1/{{pillar}}/{{path}}, got: {endpoint}"
       }
   
   version = parts[1]  # v1, v2, v3, etc.
   pillar = parts[2]  # content-pillar, insights-pillar, operations-pillar, business-outcomes-pillar
   path_parts = parts[3:]  # remaining path
   path = "/".join(path_parts)
   ```

2. Update pillar routing logic (line ~331) to handle full pillar names:
   ```python
   # CONTENT PILLAR ROUTING
   if pillar == "content-pillar":
       # ... existing content routing logic
   
   # INSIGHTS PILLAR ROUTING
   elif pillar == "insights-pillar":
       # ... existing insights routing logic
   
   # OPERATIONS PILLAR ROUTING
   elif pillar == "operations-pillar":
       # ... existing operations routing logic
   
   # BUSINESS OUTCOMES PILLAR ROUTING
   elif pillar == "business-outcomes-pillar":
       # ... existing business outcomes routing logic
   ```

**Success Criteria**:
- [ ] Endpoint parsing handles `/api/v1/{pillar}/{path}` pattern
- [ ] Pillar routing logic handles `content-pillar`, `insights-pillar`, `operations-pillar`, `business-outcomes-pillar`
- [ ] Version extracted from endpoint (for future extensibility)
- [ ] All existing routing logic preserved

---

### 1.4: Update Frontend API Managers to Use Semantic APIs

**Files to Update**:
1. `symphainy-frontend/shared/managers/ContentAPIManager.ts`
2. `symphainy-frontend/shared/services/insights/core.ts`
3. `symphainy-frontend/shared/services/operations/*.ts` (all operations service files)
4. `symphainy-frontend/shared/managers/BusinessOutcomesAPIManager.ts`

**ContentAPIManager.ts Changes**:
- Update base URL: `/api/mvp/content` → `/api/v1/content-pillar`
- Update endpoints:
  - `/api/mvp/content/files` → `/api/v1/content-pillar/list-uploaded-files`
  - `/api/mvp/content/upload` → `/api/v1/content-pillar/upload-file`
  - `/api/mvp/content/parse/{file_id}` → `/api/v1/content-pillar/process-file/{file_id}`

**InsightsService (core.ts) Changes**:
- Update base URL: `/api/insights` → `/api/v1/insights-pillar`
- Update endpoints:
  - `/api/insights/session/start` → `/api/v1/insights-pillar/analyze-content-for-insights`
  - `/api/insights/analysis/eda` → `/api/v1/insights-pillar/analyze-content-for-insights`
  - Map to semantic API endpoints per documentation

**Operations Services Changes**:
- Update base URL: `/api/operations` → `/api/v1/operations-pillar`
- Update endpoints:
  - `/api/operations/sop-to-workflow` → `/api/v1/operations-pillar/convert-sop-to-workflow`
  - `/api/operations/workflow-to-sop` → `/api/v1/operations-pillar/convert-workflow-to-sop`
  - Map all operations endpoints to semantic API endpoints

**BusinessOutcomesAPIManager.ts Changes**:
- Update base URL: `/api/v1/business_enablement/outcomes` → `/api/v1/business-outcomes-pillar`
- Update endpoints:
  - `/api/v1/business_enablement/outcomes/generate-strategic-roadmap` → `/api/v1/business-outcomes-pillar/generate-strategic-roadmap`
  - `/api/v1/business_enablement/outcomes/generate-proof-of-concept-proposal` → `/api/v1/business-outcomes-pillar/generate-proof-of-concept-proposal`

**Success Criteria**:
- [ ] All frontend API managers updated to use `/api/v1/{pillar-pillar}/...` pattern
- [ ] All endpoints mapped to semantic API endpoints
- [ ] No references to old routes (`/api/mvp/content`, `/api/insights`, `/api/operations`, `/api/v1/business_enablement/outcomes`)
- [ ] Frontend can connect to backend

---

### 1.5: Test Platform Startup and Frontend Connection

**Test Steps**:
1. Start platform: `python3 main.py`
2. Verify startup logs show:
   - ✅ Foundation infrastructure initialized
   - ✅ Smart City Gateway initialized
   - ✅ API routers registered successfully
3. Test health endpoint: `curl http://localhost:8000/health`
4. Test route registration: `curl http://localhost:8000/api/v1/content-pillar/list-uploaded-files`
5. Start frontend: `npm run dev` (or production build)
6. Verify frontend can connect to backend
7. Test CTO demo scenario 1 (quick smoke test)

**Success Criteria**:
- [ ] Platform starts without errors
- [ ] Routes are registered (no 404 errors)
- [ ] Frontend can connect to backend
- [ ] CTO demo scenario 1 works (at least file upload)

---

## Phase 2: Curator Refactoring (Critical Path)

**Goal**: Standardize registration using Protocols, align with existing CapabilityDefinition, implement route tracking and service mesh policy reporting  
**Time**: 1-2 days  
**Priority**: 🔴 CRITICAL - Required for routing integration and long-term health

### Design Principles (Aligned with Revised Approach)

1. **Use Protocols (not interfaces)**: Align with existing Python `typing.Protocol` pattern (`ServiceProtocol`, `RealmServiceProtocol`)
2. **Route Tracking Strategy**: Domains define routes (when registering capabilities/SOA APIs), Curator tracks routes centrally (endpoint registry for discovery and service mesh evolution)
3. **Service Mesh Policies**: Domains own service mesh policies (load balancing, timeouts, circuit breakers), Curator reports/aggregates
4. **Agent Access Pattern**: Agents → MCP Tools → Services (one way), Services → Agents (direct)
5. **Extend Existing Framework**: Use existing `CapabilityDefinition` model, extend with semantic mapping (don't replace)

**Key Insight from CURATOR_CENTRAL_HUB_DESIGN.md**:
- "API Routing: Service mesh handles routing (Curator provides endpoint registry)"
- Curator PROVIDES endpoint registry (tracks routes centrally for discovery)
- Service mesh HANDLES routing (executes routes)
- Domains DEFINE routes (when registering capabilities/SOA APIs)

### 2.1: Implement Service Protocol Registry

**File**: `symphainy-platform/foundations/curator_foundation/services/service_protocol_registry_service.py` (NEW)

**Requirements**:
- Register service protocols (Python `typing.Protocol`)
- Store protocol definitions with method contracts
- Align with existing Protocol pattern in codebase

**Implementation**:
```python
async def register_service_protocol(
    self,
    service_name: str,
    protocol_name: str,  # e.g., "IFileParser" (Protocol name, not interface)
    protocol: Dict[str, Any],  # Protocol definition
    user_context: Dict[str, Any] = None
) -> bool:
    """
    Register a service protocol (Python typing.Protocol).
    
    Protocol definition format:
    {
        "methods": {
            "parse_file": {
                "input_schema": {...},
                "output_schema": {...},
                "semantic_mapping": {
                    "domain_capability": "content.upload_file",
                    "user_journey": "upload_document_for_analysis"
                }
            }
        }
    }
    """
```

**Success Criteria**:
- [ ] Service Protocol Registry service created
- [ ] Protocols registered (Python `typing.Protocol` pattern)
- [ ] Protocol definitions stored with method contracts
- [ ] Aligns with existing Protocol architecture

---

### 2.2: Extend CapabilityDefinition with Semantic Mapping

**File**: `symphainy-platform/foundations/curator_foundation/models/capability_definition.py`

**Requirements**:
- Extend existing `CapabilityDefinition` model (don't replace)
- Add `semantic_mapping` field
- Add `contracts` field for multiple invocation methods
- Maintain backward compatibility

**Changes Needed**:
```python
@dataclass
class CapabilityDefinition:
    """Definition of a service capability (extended with semantic mapping)."""
    # Existing fields
    service_name: str
    interface_name: str  # Protocol name (e.g., "IFileParser")
    endpoints: List[str]
    tools: List[str]
    description: str
    realm: str
    version: str = "1.0.0"
    registered_at: str = None
    
    # New fields (extend, don't replace)
    semantic_mapping: Optional[Dict[str, Any]] = None  # New: semantic API mapping
    contracts: Optional[Dict[str, Any]] = None  # New: multiple invocation methods
    
    def __post_init__(self):
        if self.registered_at is None:
            self.registered_at = datetime.utcnow().isoformat()
```

**Success Criteria**:
- [ ] `CapabilityDefinition` extended with `semantic_mapping` and `contracts`
- [ ] Backward compatibility maintained
- [ ] Existing code continues to work

---

### 2.3: Implement Domain Capability Registration

**File**: `symphainy-platform/foundations/curator_foundation/curator_foundation_service.py`

**Requirements**:
- Register capabilities using extended `CapabilityDefinition`
- Support semantic mapping and contract mappings
- Align with existing capability registry framework

**Implementation**:
```python
async def register_domain_capability(
    self,
    capability: CapabilityDefinition,
    user_context: Dict[str, Any] = None
) -> bool:
    """
    Register a domain capability using CapabilityDefinition.
    
    Example:
    capability = CapabilityDefinition(
        service_name="FileParserService",
        interface_name="IFileParser",  # Protocol name
        capability_name="file_parsing",
        capability_type="soa_api",
        description="Parse files into structured formats",
        # New: semantic mapping
        semantic_mapping={
            "domain_capability": "content.upload_file",
            "semantic_api": "/api/v1/content-pillar/upload-file",
            "user_journey": "upload_document_for_analysis"
        },
        # New: contract mappings (multiple ways to invoke)
        contracts={
            "soa_api": {
                "protocol": "IFileParser",
                "method": "parse_file"
            },
            "rest_api": {
                "endpoint": "/api/v1/content-pillar/upload-file",
                "method": "POST"
            },
            "mcp_tool": {
                "tool_name": "upload_file_tool",
                "mcp_server": "content_pillar_mcp_server"
            }
        },
        # Existing fields
        endpoints=[...],
        tools=[...],
        realm="business_enablement",
        version="1.0.0"
    )
    """
```

**Success Criteria**:
- [ ] `register_domain_capability()` implemented
- [ ] Uses extended `CapabilityDefinition` model
- [ ] Semantic mapping and contracts supported
- [ ] Aligns with existing capability registry

---

### 2.4: Implement Route Registry (Endpoint Registry for Service Mesh)

**File**: `symphainy-platform/foundations/curator_foundation/services/route_registry_service.py` (NEW)

**Requirements**:
- Track routes centrally (Curator owns endpoint registry)
- Routes defined by domains (when registering capabilities/SOA APIs)
- Support route discovery and service mesh evolution (Consul Connect)

**Implementation**:
```python
async def register_route(
    self,
    route_metadata: Dict[str, Any],
    user_context: Dict[str, Any] = None
) -> bool:
    """
    Register a route in Curator's endpoint registry.
    
    Routes are DEFINED by domains (when registering capabilities/SOA APIs),
    but TRACKED centrally by Curator (endpoint registry for discovery).
    
    Route metadata format:
    {
        "route_id": "...",
        "path": "/api/v1/content-pillar/upload-file",
        "method": "POST",
        "pillar": "content-pillar",
        "realm": "business_enablement",
        "service_name": "FileParserService",
        "capability_name": "file_parsing",
        "handler": "parse_file",
        "description": "...",
        "version": "v1",
        "defined_by": "business_enablement_realm"  # Domain that defined this route
    }
    """
    # Store route in endpoint registry
    # Curator owns the registry (for discovery and service mesh evolution)
    # Domain defined the route (when registering capability/SOA API)

async def discover_routes(
    self,
    pillar: str = None,
    realm: str = None,
    service_name: str = None
) -> List[Dict[str, Any]]:
    """
    Discover routes from endpoint registry.
    
    Returns routes tracked in Curator's endpoint registry.
    Used for route discovery and service mesh evolution.
    """
```

**Success Criteria**:
- [ ] Route Registry service created
- [ ] Routes tracked centrally in Curator (endpoint registry)
- [ ] Routes discoverable by pillar, realm, service
- [ ] Domain attribution clear (which domain defined the route)

---

### 2.5: Implement Service Mesh Policy Reporter

**File**: `symphainy-platform/foundations/curator_foundation/services/service_mesh_metadata_reporter_service.py` (NEW)

**Requirements**:
- Report service mesh policies (domains own, Curator reports/aggregates)
- Policies include: load balancing, timeouts, circuit breakers, traffic splitting
- Support service mesh evolution (Consul Connect)

**Implementation**:
```python
async def report_service_mesh_policies(
    self,
    service_name: str,
    policies: Dict[str, Any],
    user_context: Dict[str, Any] = None
) -> bool:
    """
    Report service mesh policies (domain owns, Curator reports).
    
    Policies format (domain-provided):
    {
        "source": "business_enablement_realm",  # Domain that owns this
        "reported_at": "...",
        "policies": {
            "load_balancing": "round_robin",  # Owned by domain
            "timeout": "30s",  # Owned by domain
            "circuit_breakers": {...},  # Owned by domain
            "traffic_splitting": [...],  # Owned by domain
            "intentions": [...]  # Owned by domain
        }
    }
    """
    # Store policies with source attribution
    # Curator reports/aggregates, doesn't manage

async def get_service_mesh_policy_report(
    self,
    service_name: str
) -> Dict[str, Any]:
    """
    Aggregate service mesh policies from domains and report.
    
    Returns:
    {
        "service": service_name,
        "policies": {
            "source": "domain_reported",
            "aggregated_at": "...",
            "load_balancing": "...",
            "timeout": "...",
            "circuit_breakers": [...],
            "traffic_splitting": [...]
        }
    }
    """
```

**Success Criteria**:
- [ ] Service Mesh Policy Reporter service created
- [ ] Policies reported (domain-owned)
- [ ] Policies aggregated and reported
- [ ] Clear ownership: domain = source of truth for policies, Curator = reporter

---

### 2.6: Implement Agent Registry with MCP Tool Access Pattern

**File**: `symphainy-platform/foundations/curator_foundation/services/agent_registry_service.py` (NEW or UPDATE)

**Requirements**:
- Register agents with MCP tool mappings
- Support agent-to-service access pattern: Agents → MCP Tools → Services
- Support service-to-agent access pattern: Services → Agents (direct)

**Implementation**:
```python
async def register_agent(
    self,
    agent_id: str,
    agent_name: str,
    characteristics: Dict[str, Any],
    contracts: Dict[str, Any],
    user_context: Dict[str, Any] = None
) -> bool:
    """
    Register an agent with MCP tool access pattern.
    
    Example:
    await curator.register_agent(
        agent_id="content_analysis_specialist",
        agent_name="Content Analysis Specialist",
        characteristics={
            "specialization": "content_analysis",
            "pillar": "content",
            "capabilities": ["analyze_content", "extract_insights"],
            "required_roles": ["librarian", "content_steward"],
            "agui_schema": {...}
        },
        contracts={
            "mcp_tools": [  # Agents use MCP tools (not direct service access)
                {
                    "tool_name": "upload_file_tool",
                    "mcp_server": "content_pillar_mcp_server",
                    "wraps_service": "FileParserService",  # Tool wraps service
                    "wraps_method": "parse_file"  # Tool wraps method
                }
            ],
            "agent_api": {  # How services invoke this agent (direct access)
                "endpoint": "/api/agents/content_analysis_specialist",
                "method": "POST"
            }
        }
    )

async def discover_agents_for_capability(
    self,
    capability: str
) -> List[Dict[str, Any]]:
    """
    Services discover agents that can help with a capability.
    
    Returns:
    [
        {
            "agent_id": "...",
            "agent_name": "...",
            "agent_api": {...},  # How service calls agent directly
            "capabilities": [...]
        }
    ]
    """
```

**Success Criteria**:
- [ ] Agent Registry supports MCP tool access pattern
- [ ] Agents registered with MCP tool mappings
- [ ] Service-to-agent discovery works
- [ ] Clear access patterns: Agent → MCP Tool → Service, Service → Agent

---

### 2.7: Update Unified Registration Flow

**File**: `symphainy-platform/bases/realm_service_base.py`

**Requirements**:
- Update `register_with_curator()` to use new registration pattern
- Register capabilities, protocols, routing metadata, agents separately
- Align with revised design

**Implementation**:
```python
async def register_with_curator(
    self,
    capabilities: list,
    soa_apis: list,
    mcp_tools: list,
    protocols: Optional[List[Dict[str, Any]]] = None,
    routing_metadata: Optional[Dict[str, Any]] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Register service with Curator (unified registration flow).
    
    Aligned with revised design:
    1. Register capabilities (using CapabilityDefinition) - routes automatically tracked
    2. Register service protocols (Python typing.Protocol)
    3. Register routes in endpoint registry (domains define, Curator tracks)
    4. Report service mesh policies (domain owns, Curator reports)
    5. Register with service discovery (via Public Works)
    """
    try:
        curator = self.get_curator()
        if not curator:
            self.logger.warning("⚠️ Curator Foundation not available")
            return False
        
        # 1. Register capabilities (using CapabilityDefinition)
        for capability in capabilities:
            capability_def = CapabilityDefinition(
                service_name=self.service_name,
                interface_name=capability.get("protocol", f"I{self.service_name}"),
                capability_name=capability["name"],
                # ... existing CapabilityDefinition fields ...
                # New: semantic mapping
                semantic_mapping=capability.get("semantic_mapping", {}),
                # New: contracts
                contracts=capability.get("contracts", {})
            )
            await curator.register_domain_capability(capability_def)
        
        # 2. Register service protocols (Python typing.Protocol)
        if protocols:
            for protocol in protocols:
                await curator.register_service_protocol(
                    service_name=self.service_name,
                    protocol_name=protocol["name"],
                    protocol=protocol["definition"]
                )
        
        # 3. Register routes in Curator's endpoint registry (domains define, Curator tracks)
        # Routes are automatically registered when capabilities/SOA APIs are registered
        # (Routes are part of capability/SOA API metadata)
        
        # 4. Report service mesh policies (domain owns, Curator reports)
        if routing_metadata and routing_metadata.get("policies"):
            await curator.report_service_mesh_policies(
                service_name=self.service_name,
                policies=routing_metadata["policies"]  # Domain-provided policies
            )
        
        # 5. Register with service discovery (via Public Works)
        # (Existing registration continues)
        
        return True
    except Exception as e:
        self.logger.error(f"❌ Failed to register with Curator: {e}")
        return False
```

**Success Criteria**:
- [ ] `register_with_curator()` uses new registration pattern
- [ ] Capabilities, protocols, routes, policies registered separately
- [ ] Routes tracked in Curator's endpoint registry
- [ ] Aligns with revised design
- [ ] All services can register via this method

---

### 2.8: Update All Services to Use New Registration Pattern

**Files to Update** (one realm at a time):
1. **Business Enablement Realm**:
   - All enabling services
   - All orchestrators
   - Delivery Manager

2. **Journey Realm**:
   - Journey Analytics Service
   - Journey Milestone Tracker Service
   - Structured Journey Orchestrator Service
   - MVP Journey Orchestrator Service

3. **Solution Realm**:
   - Solution Analytics Service
   - Solution Composer Service
   - Solution Deployment Manager Service

4. **Smart City Realm**:
   - All Smart City roles (if not already updated)

**Process**:
1. Update one service at a time
2. Test registration after each service
3. Verify in Curator registry
4. Move to next service

**Success Criteria**:
- [ ] All services use new `register_with_curator()` pattern
- [ ] All services register successfully
- [ ] Curator registry shows all services

---

### 2.9: Archive Old Registration Methods

**Files to Archive**:
- Old `register_soa_api()` method (if separate implementation exists)
- Old `register_mcp_tool()` method (if separate implementation exists)
- Old `register_capability()` direct calls (if any)

**Process**:
1. Create archive directory: `foundations/curator_foundation/services/archive/`
2. Move old methods to archive (with `_old` suffix)
3. Remove temporary compatibility code
4. Update all references

**Success Criteria**:
- [ ] Old methods archived
- [ ] No parallel implementations
- [ ] All references updated

---

### 2.10: Update Validation to Match Current Architecture

**File**: `symphainy-platform/foundations/curator_foundation/services/capability_registry_service.py`

**Requirements**:
- Update validation to match current architecture (per CURATOR_CENTRAL_HUB_DESIGN.md)
- Remove strict `service_type` restriction
- Make `capabilities` flexible (list or dict)
- Validate `realm` format
- Only require `service_name` as mandatory

**Changes Needed**:
1. Update `_validate_capability_structure()` to be more flexible:
   - Accept dict or list for capabilities
   - Only require identifying fields (description, name, service_name, realm, interface, endpoints, tools)
   - Remove strict structure requirements

2. Update `_validate_service_metadata()`:
   - Remove `service_type` restriction
   - Make `capabilities` flexible
   - Validate `realm` format (must be valid realm name)
   - Only require `service_name` as mandatory

3. Update validation error messages to be more helpful

**Success Criteria**:
- [ ] Validation matches current architecture
- [ ] Capabilities can be list or dict
- [ ] No strict `service_type` restriction
- [ ] Validation errors are helpful

---

## Phase 3: Experience Foundation & API Gateway Integration

**Goal**: Position Experience Foundation as extensible platform capability, implement REST API Gateway (REST APIs as one experience type), integrate with APIRoutingUtility and Curator  
**Time**: 1-2 days  
**Priority**: 🟡 HIGH - Required for headless architecture and service mesh evolution

**📄 See detailed implementation plan**: [PHASE3_EXPERIENCE_FOUNDATION_API_GATEWAY_INTEGRATION.md](./PHASE3_EXPERIENCE_FOUNDATION_API_GATEWAY_INTEGRATION.md)

### Strategic Vision

- **Experience Foundation** = Extensible SDK for any "head" type (REST, WebSocket, ERP, CLI, etc.)
- **REST APIs** = One experience type (not the only one)
- **API Gateway Foundation** = REST API implementation
- **symphainy-frontend** = One client consuming REST APIs (MVP)

### 3.1: Establish Experience Foundation Strategy

**File**: `docs/11-12/EXPERIENCE_FOUNDATION_STRATEGY.md` (NEW)

**Purpose**: Document Experience Foundation as extensible platform capability

**Success Criteria**:
- [ ] Strategy document created
- [ ] Experience Foundation positioned as extensible platform capability
- [ ] REST APIs positioned as one experience type
- [ ] API Gateway Foundation positioned as REST API implementation
- [ ] symphainy-frontend positioned as one client (MVP)
- [ ] Future extensibility documented

---

### 3.2: Update FrontendGatewayService as REST API Gateway

**File**: `symphainy-platform/foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py`

**Requirements**:
- Position as REST API Gateway (not frontend-specific)
- Integrate APIRoutingUtility as routing engine
- Register routes in Curator when orchestrators discovered

**Success Criteria**:
- [ ] Class docstring updated to clarify REST API Gateway role
- [ ] APIRoutingUtility integrated
- [ ] Routes registered via APIRoutingUtility when orchestrators discovered
- [ ] Route metadata flows to Curator's Route Registry
- [ ] Client-agnostic (any client can consume REST APIs)
- [ ] symphainy-frontend continues to work (no loss of functionality)

---

### 3.3: Update APIRoutingUtility to Register Routes in Curator

**File**: `symphainy-platform/utilities/api_routing/api_routing_utility.py`

**Requirements**:
- Register routes in Curator's endpoint registry when routes are registered
- Route metadata includes path, method, pillar, realm, handler

**Success Criteria**:
- [ ] `register_route()` registers routes in Curator's endpoint registry
- [ ] Route metadata flows to Curator's Route Registry
- [ ] Routes tracked centrally (for discovery and service mesh evolution)
- [ ] Routes discoverable via Curator's discovery methods

---

### 3.4: End-to-End REST API Experience Test (Client-Agnostic)

**Test Steps**:
1. Start platform
2. Verify routes registered in Curator's endpoint registry
3. Test route discovery: `await curator.discover_routes(pillar="content-pillar")`
4. Test REST API consumption by any client (curl, Postman)
5. Test symphainy-frontend as one client (MVP implementation)
6. Verify routes tracked in Curator (centralized endpoint registry)

**Success Criteria**:
- [ ] Routes registered in Curator's endpoint registry
- [ ] Routes discoverable via Curator's discovery methods
- [ ] REST APIs work with any client (curl, Postman, etc.)
- [ ] symphainy-frontend works as one client (MVP)
- [ ] Route metadata accurate
- [ ] Domain attribution clear (which domain defined each route)
- [ ] API Gateway is client-agnostic
- [ ] No loss of functionality (all existing features work)

---

## Phase 4: Utility Compliance

**Goal**: Add utilities to all realm services  
**Time**: 2-3 days  
**Priority**: 🟡 HIGH - Required for production readiness

### 4.1: Journey Realm Utility Compliance

**Files to Update**:
1. `backend/journey/services/journey_analytics_service/journey_analytics_service.py`
2. `backend/journey/services/journey_milestone_tracker_service/journey_milestone_tracker_service.py`
3. `backend/journey/services/structured_journey_orchestrator_service/structured_journey_orchestrator_service.py`
4. `backend/journey/services/mvp_journey_orchestrator_service/mvp_journey_orchestrator_service.py`

**Required Utilities**:
- `log_operation_with_telemetry()` - For all operations
- `handle_error_with_audit()` - For error handling
- `check_permissions()` - For security
- `validate_tenant_access()` - For multi-tenancy
- `record_health_metric()` - For health monitoring

**Process**:
1. Update one service at a time
2. Add utilities to all public methods
3. Test after each service
4. Verify utilities are called

**Success Criteria**:
- [ ] All Journey services have utility compliance
- [ ] All operations logged with telemetry
- [ ] All errors handled with audit
- [ ] Security and multi-tenancy validated

---

### 4.2: Solution Realm Utility Compliance

**Files to Update**:
1. `backend/solution/services/solution_analytics_service/solution_analytics_service.py`
2. `backend/solution/services/solution_composer_service/solution_composer_service.py`
3. `backend/solution/services/solution_deployment_manager_service/solution_deployment_manager_service.py`

**Required Utilities**: Same as Journey realm

**Process**: Same as Journey realm

**Success Criteria**: Same as Journey realm

---

### 4.3: Business Enablement Realm Utility Compliance

**Files to Update**: All Business Enablement services (30+ services)

**Process**:
1. Audit all services for utility compliance
2. Update services missing utilities
3. Test after each service
4. Verify comprehensive coverage

**Success Criteria**:
- [ ] All Business Enablement services have utility compliance
- [ ] Comprehensive audit completed
- [ ] All services tested

---

## Phase 5: Testing & Validation

**Goal**: Ensure everything works end-to-end  
**Time**: 1 day  
**Priority**: 🔴 CRITICAL - Required before production

### 5.1: Platform Startup Test

**Test Steps**:
1. Start platform: `python3 main.py`
2. Verify all phases complete:
   - ✅ Foundation infrastructure initialized
   - ✅ Smart City Gateway initialized
   - ✅ API routers registered
   - ✅ Routes registered in Curator
3. Test health endpoint
4. Test route endpoints

**Success Criteria**:
- [ ] Platform starts without errors
- [ ] All routes registered
- [ ] Health endpoint works

---

### 5.2: Frontend-Backend Integration Test

**Test Steps**:
1. Start backend
2. Start frontend
3. Test all 4 pillars:
   - Content: Upload file, list files, parse file
   - Insights: Analyze content, get results
   - Operations: Generate SOP, create workflow
   - Business Outcomes: Generate roadmap, create POC
4. Verify no 404 errors
5. Verify responses are correct

**Success Criteria**:
- [ ] Frontend connects to backend
- [ ] All pillars work
- [ ] No 404 errors
- [ ] Responses correct

---

### 5.3: CTO Demo Scenario Tests

**Test Scenarios**:
1. **Scenario 1: Autonomous Vehicle Testing**
   - Upload mission plan CSV
   - Parse COBOL binary with copybook
   - Generate insights
   - Generate SOP
   - Generate roadmap

2. **Scenario 2: Life Insurance Underwriting**
   - Upload claims CSV
   - Upload reinsurance Excel
   - Parse policy master binary
   - Generate insights
   - Generate roadmap

3. **Scenario 3: Data Coexistence/Migration**
   - Upload legacy policies
   - Upload target schema
   - Analyze schema mapping
   - Generate SOP
   - Generate migration blueprint

**Success Criteria**:
- [ ] All 3 scenarios work end-to-end
- [ ] No errors or failures
- [ ] Outputs are correct
- [ ] Ready for CTO demo

---

## Execution Checklist

### Pre-Execution
- [ ] Review this plan
- [ ] Ensure all dependencies are available
- [ ] Backup current codebase
- [ ] Create feature branch

### Phase 1: Critical Unblock
- [ ] 1.1: Implement universal pillar router
- [ ] 1.2: Implement register_api_routers()
- [ ] 1.3: Update FrontendGatewayService
- [ ] 1.4: Update frontend API managers
- [ ] 1.5: Test platform startup and frontend connection

### Phase 2: Curator Refactoring
- [ ] 2.1: Update CuratorFoundationService.register_service()
- [ ] 2.2: Update RealmServiceBase.register_with_curator()
- [ ] 2.3: Update all services
- [ ] 2.4: Archive old registration methods
- [ ] 2.5: Add routing metadata integration

### Phase 3: Routing Integration
- [ ] 3.1: Integrate APIRoutingUtility with Curator
- [ ] 3.2: Update FrontendGatewayService
- [ ] 3.3: End-to-end routing test

### Phase 4: Utility Compliance
- [ ] 4.1: Journey realm utility compliance
- [ ] 4.2: Solution realm utility compliance
- [ ] 4.3: Business Enablement realm utility compliance

### Phase 5: Testing & Validation
- [ ] 5.1: Platform startup test
- [ ] 5.2: Frontend-backend integration test
- [ ] 5.3: CTO demo scenario tests

### Post-Execution
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Ready for production deployment

---

## Success Metrics

### Platform Health
- ✅ Platform starts successfully (100% success rate)
- ✅ All routes registered (0 404 errors)
- ✅ Frontend connects to backend (100% success rate)

### Curator Health
- ✅ All services registered via single path (100% compliance)
- ✅ Validation matches current architecture (100% alignment)
- ✅ Routing metadata tracked (100% coverage)

### Utility Compliance
- ✅ Journey realm: 100% compliance
- ✅ Solution realm: 100% compliance
- ✅ Business Enablement realm: 100% compliance

### CTO Demo Readiness
- ✅ All 3 scenarios work end-to-end
- ✅ No errors or failures
- ✅ Ready for production demo

---

## Notes for Executing Agent

1. **Execute phases sequentially** - Each phase builds on the previous one
2. **Test after each step** - Don't proceed if tests fail
3. **Archive old code** - Never use `_updated` or `_new` suffixes
4. **Update documentation** - Keep docs in sync with code
5. **Ask for help** - If stuck, ask user for clarification

---

## References

- **Curator Design**: `docs/11-12/CURATOR_CENTRAL_HUB_DESIGN.md`
- **Semantic API Documentation**: `docs/11-11/SEMANTIC_API_IMPLEMENTATION_COMPLETE.md`
- **Platform README**: `symphainy-platform/README.md`
- **CTO Demo Scenarios**: `tests/CTO_DEMO_TESTING_STRATEGY.md`

---

**End of Implementation Plan**

