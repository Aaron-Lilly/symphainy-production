# Platform Cleanup and Refactoring Plan
## "Break Then Fix" Approach - No Backward Compatibility for Anti-Patterns

## Executive Summary

This plan addresses all identified anti-patterns, hard-coding issues, and architectural inconsistencies using a **"break then fix"** approach. We remove anti-patterns completely (no backward compatibility), find all references through breakage, and fix them properly to ensure clean, consistent patterns throughout the platform.

**Goal:** Prove EC2 deployment for CTO while maintaining clean architecture that scales to Option C.

**Philosophy:** Break anti-patterns first, then fix all references. This ensures we find everything and maintain consistency.

---

## Table of Contents

1. [Anti-Patterns to Break and Fix](#anti-patterns-to-break-and-fix)
2. [Hard-Coding Audit and Removal](#hard-coding-audit-and-removal)
3. [Configuration System Unification](#configuration-system-unification)
4. [JWT Adapter Removal](#jwt-adapter-removal)
5. [Routing Pattern Standardization](#routing-pattern-standardization)
6. [Lazy Loading Verification](#lazy-loading-verification)
7. [Startup Process Cleanup](#startup-process-cleanup)
8. [Implementation Phases](#implementation-phases)

---

## Anti-Patterns to Break and Fix

### 1. Dual Configuration Systems ❌ → ✅ Single Unified System

**Current Anti-Pattern:**
- `UnifiedConfigurationManager` loads config from files into a dict
- `ConfigAdapter` reads from `os.getenv()` (environment variables)
- Gap: File-based config isn't exposed as environment variables
- Result: ConfigAdapter can't find values loaded by UnifiedConfigurationManager

**Break It:**
- Remove `os.getenv()` calls from `ConfigAdapter.get()`
- Make `ConfigAdapter` require `UnifiedConfigurationManager` as dependency
- This will break all code that uses ConfigAdapter

**Fix It:**
- Update `PublicWorksFoundationService` to pass `UnifiedConfigurationManager` to `ConfigAdapter`
- Update all `ConfigAdapter` initialization to require `UnifiedConfigurationManager`
- Test that all config access works

**Files to Change:**
- `foundations/public_works_foundation/infrastructure_adapters/config_adapter.py`
- `foundations/public_works_foundation/public_works_foundation_service.py`
- Any other code that creates `ConfigAdapter` instances

### 2. JWT Adapter for User Auth ❌ → ✅ Supabase Only

**Current Anti-Pattern:**
- `EnvironmentLoader` requires `JWT_SECRET` in `_get_required_keys()`
- `AuthAbstraction.validate_token()` uses JWT adapter instead of Supabase
- `PublicWorksFoundationService` creates JWT adapter during initialization
- Supabase handles all user authentication tokens

**Break It:**
- Remove `JWT_SECRET` from `EnvironmentLoader._get_required_keys()`
- Remove JWT adapter creation from `PublicWorksFoundationService._create_all_adapters()`
- Update `AuthAbstraction.validate_token()` to use Supabase only (remove JWT path)
- Update `SecurityContextProvider` to remove JWT fallback
- This will break any code expecting JWT validation

**Fix It:**
- Update all token validation to use Supabase
- Remove JWT_SECRET from all config files
- Update error messages to be Supabase-specific
- Test authentication flow

**Files to Change:**
- `config/environment_loader.py`
- `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py`
- `foundations/public_works_foundation/public_works_foundation_service.py`
- `backend/smart_city/services/security_guard/modules/security_context_provider_module.py`
- `config/secrets.example` (remove JWT_SECRET)

### 3. Hard-Coded Paths and URLs ❌ → ✅ Configuration-Based

**Current Anti-Pattern:**
- Hard-coded localhost URLs in config files
- Hard-coded API prefixes (`/api/v1`)
- Hard-coded file paths in `path_utils.py`
- Hard-coded service endpoints

**Break It:**
- Remove all hard-coded URLs from code
- Remove hard-coded API prefixes from routers
- Remove hard-coded paths from `path_utils.py`
- This will break startup and routing

**Fix It:**
- Add service URLs to `config/infrastructure.yaml`
- Add API routing config to `config/business-logic.yaml`
- Update all adapters to read URLs from config
- Update routers to read API prefix from config
- Update `path_utils.py` to use environment variables only

**Files to Change:**
- `config/infrastructure.yaml` (add service_urls section)
- `config/business-logic.yaml` (add api_routing section)
- `utilities/path_utils.py` (remove hard-coded paths)
- `backend/api/universal_pillar_router.py` (read prefix from config)
- All adapter files that have hard-coded URLs

---

## Hard-Coding Audit and Removal

### Hard-Coded URLs Found

**Location:** `config/infrastructure.yaml`
```yaml
mcp_server:
  base_url: "http://localhost"  # ❌ BREAK THIS
  port: 8000                     # ❌ BREAK THIS
```

**Location:** `config/development.env`
```bash
ARANGO_HOSTS=localhost:8529     # ❌ BREAK THIS
REDIS_HOST=localhost             # ❌ BREAK THIS
```

**Location:** `utilities/path_utils.py:63`
```python
common_paths = [
    Path("/home/founders/demoversion/symphainy_source/symphainy-platform"),  # ❌ BREAK THIS
]
```

**Location:** `backend/api/universal_pillar_router.py:42`
```python
@router.api_route(
    "/api/v1/{pillar}/{path:path}",  # ❌ BREAK THIS - hard-coded prefix
)
```

### Fixes Required

#### 1. Service URLs → Configuration

**Add to `config/infrastructure.yaml`:**
```yaml
service_urls:
  arangodb: "${ARANGO_URL:-http://localhost:8529}"
  redis: "${REDIS_URL:-redis://localhost:6379}"
  consul: "${CONSUL_URL:-http://localhost:8501}"
  grafana: "${GRAFANA_URL:-http://localhost:3100}"
  tempo: "${TEMPO_URL:-http://localhost:3200}"
  otel_collector: "${OTEL_COLLECTOR_URL:-http://localhost:4318}"
  mcp_server: "${MCP_SERVER_URL:-http://localhost:8000}"
```

**Update all adapters:**
- Read URLs from `config_adapter.get("SERVICE_URL_ARANGODB")` or from infrastructure.yaml
- Remove all hard-coded `localhost` references

#### 2. API Prefixes → Configuration

**Add to `config/business-logic.yaml`:**
```yaml
api_routing:
  base_prefix: "/api"
  version: "v1"
  full_prefix: "/api/v1"
  pillar_pattern: "{pillar}-pillar"
```

**Update universal router:**
- Read prefix from config instead of hard-coding
- Construct route pattern from config

#### 3. File Paths → Environment Variables Only

**Remove from `path_utils.py`:**
- Hard-coded path: `/home/founders/demoversion/symphainy_source/symphainy-platform`
- Keep only environment variable and discovery logic

---

## Configuration System Unification

### Current State (Broken)

```
UnifiedConfigurationManager (loads from files)
    ↓ (doesn't set env vars)
ConfigAdapter (reads from os.getenv())
    ↓ (can't find values)
Foundation Services (get None/missing config)
```

### Target State (Fixed)

```
UnifiedConfigurationManager (loads from files)
    ↓ (provides unified config dict)
ConfigAdapter (reads from UnifiedConfigurationManager)
    ↓ (finds all values)
Foundation Services (get all config values)
```

### Implementation: Break Then Fix

**Step 1: Break ConfigAdapter**
```python
# In config_adapter.py
class ConfigAdapter:
    def __init__(self, unified_config_manager: UnifiedConfigurationManager):
        """BREAK: Require UnifiedConfigurationManager - no default."""
        if not unified_config_manager:
            raise ValueError("ConfigAdapter requires UnifiedConfigurationManager")
        self.config_manager = unified_config_manager
    
    def get(self, key: str, default: Any = None) -> Any:
        """BREAK: Read from UnifiedConfigurationManager only - no os.getenv()."""
        return self.config_manager.get(key, default)
```

**Step 2: Find All Breakage**
- Run platform startup
- All code using `ConfigAdapter()` without UnifiedConfigurationManager will fail
- Document all failures

**Step 3: Fix All References**
```python
# In public_works_foundation_service.py
async def initialize_foundation(self, config_file: str = ".env") -> bool:
    # Get UnifiedConfigurationManager (should already exist)
    from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
    from utilities.path_utils import get_project_root
    
    unified_config = UnifiedConfigurationManager(
        service_name="public_works_foundation",
        config_root=get_project_root()
    )
    
    # Create ConfigAdapter with UnifiedConfigurationManager
    self.config_adapter = ConfigAdapter(unified_config_manager=unified_config)
```

---

## JWT Adapter Removal

### Implementation: Break Then Fix

**Step 1: Break JWT Requirements**

**File:** `config/environment_loader.py`
```python
def _get_required_keys(self) -> list:
    """BREAK: Remove JWT_SECRET from required keys."""
    base_keys = [
        "ARANGO_URL",
        "REDIS_URL", 
        "SECRET_KEY",
        # "JWT_SECRET"  # ❌ REMOVED - will break code expecting it
    ]
```

**File:** `foundations/public_works_foundation/public_works_foundation_service.py`
```python
async def _create_all_adapters(self):
    # ... existing code ...
    
    # ❌ BREAK: Remove JWT adapter creation completely
    # jwt_config = self.config_adapter.get_jwt_config()
    # self.jwt_adapter = JWTAdapter(...)  # REMOVED
    
    # This will break AuthAbstraction initialization
```

**File:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py`
```python
def __init__(self, supabase_adapter: SupabaseAdapter, jwt_adapter: JWTAdapter, di_container=None):
    """BREAK: Make jwt_adapter optional (None for user auth)."""
    self.supabase = supabase_adapter
    self.jwt = jwt_adapter  # Can be None - user auth doesn't use it
    # ... rest of init ...
```

**File:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py`
```python
async def validate_token(self, token: str) -> SecurityContext:
    """BREAK: Remove JWT validation path completely."""
    # ❌ REMOVED: JWT validation
    # validation_result = self.jwt.validate_token(token)
    
    # ✅ ONLY Supabase validation
    result = await self.supabase.get_user(token)
    
    if not result.get("success"):
        raise AuthenticationError(f"Token validation failed: {result.get('error')}")
    
    # ... create SecurityContext from Supabase user data ...
```

**Step 2: Find All Breakage**
- Run platform startup
- All code expecting JWT validation will fail
- All code requiring JWT_SECRET will fail
- Document all failures

**Step 3: Fix All References**

**File:** `foundations/public_works_foundation/public_works_foundation_service.py`
```python
# Create AuthAbstraction without JWT adapter
self.auth_abstraction = AuthAbstraction(
    supabase_adapter=self.supabase_adapter,
    jwt_adapter=None,  # ✅ User auth doesn't use JWT
    di_container=self.di_container
)
```

**File:** `backend/smart_city/services/security_guard/modules/security_context_provider_module.py`
```python
async def _extract_context_from_token(self, token: str) -> SecurityContext:
    """FIX: Use Supabase only - no JWT fallback."""
    # ✅ ONLY Supabase validation
    if not self.supabase_adapter:
        raise ValueError("Supabase adapter required")
    
    user_data = await self.supabase_adapter.get_user(token)
    # ... create SecurityContext ...
```

---

## Routing Pattern Standardization

### Current State

**Universal Router:** `/api/v1/{pillar}/{path:path}` ✅ (Primary)
- Routes to FrontendGatewayService
- Handles all pillar requests
- Versioned API

**MVP Routers:** Already removed ✅
- No MVP routers found in current codebase
- Archive directory exists but is empty

### Target State: Configurable Universal Router

**Break It:**
- Remove hard-coded `/api/v1` prefix from `universal_pillar_router.py`
- This will break routing

**Fix It:**
- Read API prefix from `config/business-logic.yaml`
- Construct route pattern from config
- Support environment-specific prefixes

**Implementation:**

**File:** `backend/api/universal_pillar_router.py`
```python
# BREAK: Remove hard-coded prefix
# @router.api_route(
#     "/api/v1/{pillar}/{path:path}",  # ❌ REMOVED
#     methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
# )

# FIX: Read from config
from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
from utilities.path_utils import get_project_root

# Get config
config_manager = UnifiedConfigurationManager(
    service_name="universal_router",
    config_root=get_project_root()
)

# Get API prefix from config
api_prefix = config_manager.get("API_ROUTING_FULL_PREFIX", "/api/v1")

# Construct route pattern
route_pattern = f"{api_prefix}/{{pillar}}/{{path:path}}"

@router.api_route(
    route_pattern,  # ✅ From config
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def universal_pillar_handler(request: Request, pillar: str, path: str):
    # ... existing code ...
```

---

## Lazy Loading Verification

### Current Lazy Loading Chain (Preserved)

```
Router → FrontendGatewayService.route_frontend_request()
    → FrontendGatewayService.handle_*_request()
    → Orchestrator method (e.g., content_orchestrator.upload_file())
    → Orchestrator.get_smart_city_api("ContentSteward")  # ✅ LAZY LOADING
    → PlatformCapabilitiesMixin.get_smart_city_api()
    → Check Curator → NOT FOUND
    → City Manager.orchestrate_realm_startup(services=["content_steward"])
    → Content Steward initializes and registers
    → Return Content Steward instance
```

### Verification: Lazy Loading Still Works

**Why it works:**
1. **ConfigAdapter changes don't affect lazy loading**
   - ConfigAdapter only affects config access
   - Lazy loading uses `get_smart_city_api()` which is unchanged
   - City Manager lazy initialization is unchanged

2. **JWT removal doesn't affect lazy loading**
   - JWT adapter was only for token validation
   - Lazy loading is independent of authentication
   - Services still lazy-load via City Manager

3. **Routing changes don't affect lazy loading**
   - Universal router still calls FrontendGatewayService
   - FrontendGatewayService still calls orchestrators
   - Orchestrators still use lazy loading

**Test Plan:**
1. Start platform (should be fast - only foundations load)
2. Make API request (e.g., upload file)
3. Verify orchestrator lazy-loads
4. Verify Smart City service lazy-loads
5. Verify service registers with Curator
6. Verify subsequent requests use cached service

---

## Startup Process Cleanup

### Current Startup Sequence

```
1. main.py loads .env.secrets
2. UnifiedConfigurationManager loads config
3. PlatformOrchestrator created
4. Foundation infrastructure initialized (EAGER)
   - ConfigAdapter created (❌ BREAKS - needs UnifiedConfigurationManager)
   - JWT adapter created (❌ BREAKS - should not be created)
5. Smart City Gateway initialized (EAGER)
6. Lazy hydration ready (deferred)
7. Background watchers started
8. Curator auto-discovery started
9. FastAPI routes setup
10. API routers registered
```

### Target Startup Sequence (After Fixes)

```
1. main.py loads .env.secrets
2. UnifiedConfigurationManager loads all config layers
3. PlatformOrchestrator created
4. Foundation infrastructure initialized (EAGER)
   - UnifiedConfigurationManager passed to ConfigAdapter ✅
   - ConfigAdapter reads from UnifiedConfigurationManager ✅
   - No JWT adapter created ✅
   - Supabase adapter created ✅
5. Smart City Gateway initialized (EAGER)
6. Lazy hydration ready (deferred)
7. Background watchers started
8. Curator auto-discovery started
9. FastAPI routes setup
10. API routers registered (with config-based prefix) ✅
```

### Startup Validation

**Add startup validation:**
```python
async def _validate_startup(self):
    """Validate startup configuration and dependencies."""
    # Check required config (no JWT_SECRET)
    required_config = [
        "ARANGO_URL", 
        "REDIS_URL", 
        "SUPABASE_URL", 
        "SUPABASE_KEY",
        "SECRET_KEY"
    ]
    missing = []
    for key in required_config:
        if not self.config_adapter.get(key):
            missing.append(key)
    
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")
    
    # Verify Supabase adapter created
    if not self.supabase_adapter:
        raise RuntimeError("Supabase adapter not created - required for authentication")
    
    # Verify JWT adapter NOT created (for user auth)
    if hasattr(self, 'jwt_adapter') and self.jwt_adapter:
        self.logger.warning("⚠️ JWT adapter created but should not be used for user auth")
```

---

## Implementation Phases

### Phase 1: Break Anti-Patterns (Day 1)

**Goal:** Remove all anti-patterns to force finding all references

1. **Break ConfigAdapter**
   - [ ] Update `ConfigAdapter.__init__()` to require `UnifiedConfigurationManager`
   - [ ] Remove `os.getenv()` from `ConfigAdapter.get()`
   - [ ] Run platform startup → document all failures
   - [ ] List all files that need fixing

2. **Break JWT Requirements**
   - [ ] Remove `JWT_SECRET` from `EnvironmentLoader._get_required_keys()`
   - [ ] Remove JWT adapter creation from `PublicWorksFoundationService`
   - [ ] Update `AuthAbstraction.validate_token()` to use Supabase only
   - [ ] Remove JWT fallback from `SecurityContextProvider`
   - [ ] Run platform startup → document all failures
   - [ ] List all files that need fixing

3. **Break Hard-Coded Values**
   - [ ] Remove hard-coded API prefix from `universal_pillar_router.py`
   - [ ] Remove hard-coded URLs from adapters
   - [ ] Remove hard-coded path from `path_utils.py`
   - [ ] Run platform startup → document all failures
   - [ ] List all files that need fixing

**Success Criteria:**
- Platform fails to start (expected - we broke it)
- All failures documented
- Complete list of files needing fixes

### Phase 2: Fix All References (Day 2-3)

**Goal:** Fix all breakage to restore functionality with clean patterns

1. **Fix ConfigAdapter Usage**
   - [ ] Update `PublicWorksFoundationService` to pass `UnifiedConfigurationManager` to `ConfigAdapter`
   - [ ] Find all other `ConfigAdapter()` instantiations
   - [ ] Update all to pass `UnifiedConfigurationManager`
   - [ ] Test configuration loading

2. **Fix Authentication**
   - [ ] Update `AuthAbstraction` initialization to not require JWT adapter
   - [ ] Update all token validation to use Supabase only
   - [ ] Remove JWT_SECRET from config files
   - [ ] Test authentication flow

3. **Fix Hard-Coding**
   - [ ] Add service URLs to `config/infrastructure.yaml`
   - [ ] Add API routing config to `config/business-logic.yaml`
   - [ ] Update universal router to read prefix from config
   - [ ] Update all adapters to read URLs from config
   - [ ] Update `path_utils.py` to remove hard-coded paths
   - [ ] Test routing and path resolution

**Success Criteria:**
- Platform starts without errors
- All config loads correctly
- Authentication works (Supabase only)
- Routing works (config-based prefix)
- No hard-coded values remain

### Phase 3: Configuration Hardening (Day 4)

**Goal:** Make configuration system robust and Option C ready

1. **Add Configuration Sections**
   - [ ] Add `service_urls` section to `infrastructure.yaml`
   - [ ] Add `api_routing` section to `business-logic.yaml`
   - [ ] Document all configuration options
   - [ ] Add validation for required config

2. **Update All Adapters**
   - [ ] Audit all adapters for hard-coded URLs
   - [ ] Update all to read from config
   - [ ] Add fallback values where appropriate
   - [ ] Test with different URL configurations

3. **Path Resolution Audit**
   - [ ] Audit all path usage in codebase
   - [ ] Replace hard-coded paths with `path_utils` functions
   - [ ] Test path resolution in different environments
   - [ ] Verify `SYMPHAINY_PLATFORM_ROOT` environment variable works

**Success Criteria:**
- All URLs come from configuration
- API prefixes are configurable
- Path resolution works in all environments
- Configuration is Option C ready

### Phase 4: Testing and Validation (Day 5)

**Goal:** Verify everything works together

1. **Integration Testing**
   - [ ] Test full startup sequence
   - [ ] Test authentication flow (Supabase only)
   - [ ] Test routing with lazy loading
   - [ ] Test configuration loading
   - [ ] Test with different config values

2. **Lazy Loading Verification**
   - [ ] Verify orchestrators lazy-load correctly
   - [ ] Verify Smart City services lazy-load correctly
   - [ ] Verify Curator registration works
   - [ ] Test cold start vs warm start

3. **Option C Readiness Check**
   - [ ] Verify all hard-coding removed
   - [ ] Verify configuration is cloud-ready
   - [ ] Test with environment variables
   - [ ] Document Option C migration path

**Success Criteria:**
- All tests pass
- Platform starts correctly
- Authentication works
- Routing works
- Lazy loading works
- Option C ready

---

## Detailed Code Changes

### Change 1: ConfigAdapter - Break Then Fix

**File:** `foundations/public_works_foundation/infrastructure_adapters/config_adapter.py`

**BREAK:**
```python
class ConfigAdapter:
    def __init__(self, unified_config_manager: UnifiedConfigurationManager = None):
        """BREAK: Require UnifiedConfigurationManager - no default."""
        if not unified_config_manager:
            raise ValueError(
                "ConfigAdapter requires UnifiedConfigurationManager. "
                "Pass UnifiedConfigurationManager instance to constructor."
            )
        self.config_manager = unified_config_manager
        self.env_file_path = None  # No longer used
        self.config_cache = {}  # No longer used
        
        logger.info(f"✅ Config adapter initialized with UnifiedConfigurationManager")
    
    def get(self, key: str, default: Any = None) -> Any:
        """BREAK: Read from UnifiedConfigurationManager only - no os.getenv()."""
        return self.config_manager.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Read integer from UnifiedConfigurationManager."""
        value = self.config_manager.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    # ... similar for get_float, get_bool, get_list ...
```

**FIX:**
```python
# In public_works_foundation_service.py
async def initialize_foundation(self, config_file: str = ".env") -> bool:
    # Get UnifiedConfigurationManager (should already exist in DI container or create new)
    from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
    from utilities.path_utils import get_project_root
    
    # Try to get from DI container first
    unified_config = None
    if hasattr(self.di_container, 'get_unified_config_manager'):
        unified_config = self.di_container.get_unified_config_manager()
    
    if not unified_config:
        # Create new instance
        unified_config = UnifiedConfigurationManager(
            service_name="public_works_foundation",
            config_root=get_project_root()
        )
    
    # Create ConfigAdapter with UnifiedConfigurationManager
    self.config_adapter = ConfigAdapter(unified_config_manager=unified_config)
```

### Change 2: JWT Removal - Break Then Fix

**File:** `config/environment_loader.py`

**BREAK:**
```python
def _get_required_keys(self) -> list:
    """BREAK: Remove JWT_SECRET from required keys."""
    base_keys = [
        "ARANGO_URL",
        "REDIS_URL", 
        "SECRET_KEY",
        # "JWT_SECRET"  # ❌ REMOVED - Supabase handles JWT
    ]
```

**File:** `foundations/public_works_foundation/public_works_foundation_service.py`

**BREAK:**
```python
async def _create_all_adapters(self):
    # ... existing code ...
    
    # ❌ BREAK: Remove JWT adapter creation completely
    # jwt_config = self.config_adapter.get_jwt_config()
    # if not jwt_config["secret_key"]:
    #     raise ValueError("JWT secret key missing")
    # self.jwt_adapter = JWTAdapter(...)  # REMOVED
    
    # Note: JWT adapter code still exists in infrastructure_adapters/jwt_adapter.py
    # but is not used for user authentication
```

**FIX:**
```python
# In _create_all_abstractions()
# Create AuthAbstraction without JWT adapter (user auth uses Supabase only)
self.auth_abstraction = AuthAbstraction(
    supabase_adapter=self.supabase_adapter,
    jwt_adapter=None,  # ✅ User auth doesn't use JWT
    di_container=self.di_container
)
```

**File:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py`

**BREAK:**
```python
async def validate_token(self, token: str) -> SecurityContext:
    """BREAK: Remove JWT validation - use Supabase only."""
    try:
        # ❌ REMOVED: JWT validation path
        # validation_result = self.jwt.validate_token(token)
        
        # ✅ ONLY Supabase validation
        result = await self.supabase.get_user(token)
        
        if not result.get("success"):
            raise AuthenticationError(f"Token validation failed: {result.get('error')}")
        
        user_data = result.get("user", {})
        
        # Extract user information
        user_id = user_data.get("id")
        tenant_id = user_data.get("user_metadata", {}).get("tenant_id")
        roles = user_data.get("user_metadata", {}).get("roles", [])
        permissions = user_data.get("user_metadata", {}).get("permissions", [])
        
        # Create security context
        context = SecurityContext(
            user_id=user_id,
            tenant_id=tenant_id,
            roles=roles if isinstance(roles, list) else [roles] if roles else [],
            permissions=permissions if isinstance(permissions, list) else [permissions] if permissions else [],
            origin="supabase_validation"  # Changed from "jwt_validation"
        )
        
        self.logger.info(f"✅ Token validated for user: {user_id}")
        return context
        
    except Exception as e:
        self.logger.error(f"❌ Token validation error: {str(e)}")
        raise AuthenticationError(f"Token validation failed: {str(e)}")
```

### Change 3: Hard-Coded URLs - Break Then Fix

**File:** `config/infrastructure.yaml`

**ADD:**
```yaml
# Service URLs (read from environment variables with defaults)
service_urls:
  arangodb: "${ARANGO_URL:-http://localhost:8529}"
  redis: "${REDIS_URL:-redis://localhost:6379}"
  consul: "${CONSUL_URL:-http://localhost:8501}"
  grafana: "${GRAFANA_URL:-http://localhost:3100}"
  tempo: "${TEMPO_URL:-http://localhost:3200}"
  otel_collector_http: "${OTEL_COLLECTOR_HTTP_URL:-http://localhost:4318}"
  otel_collector_grpc: "${OTEL_COLLECTOR_GRPC_URL:-http://localhost:4317}"
  mcp_server: "${MCP_SERVER_URL:-http://localhost:8000}"
```

**File:** `config/business-logic.yaml`

**ADD:**
```yaml
# API Routing Configuration
api_routing:
  base_prefix: "/api"
  version: "v1"
  full_prefix: "/api/v1"
  pillar_pattern: "{pillar}-pillar"
```

**File:** `backend/api/universal_pillar_router.py`

**BREAK:**
```python
# ❌ REMOVE hard-coded route
# @router.api_route(
#     "/api/v1/{pillar}/{path:path}",
#     methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
# )
```

**FIX:**
```python
# ✅ Read from config
from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
from utilities.path_utils import get_project_root

# Get config (lazy initialization)
_config_manager = None
def _get_config_manager():
    global _config_manager
    if not _config_manager:
        _config_manager = UnifiedConfigurationManager(
            service_name="universal_router",
            config_root=get_project_root()
        )
    return _config_manager

# Get API prefix from config
def _get_api_prefix():
    config = _get_config_manager()
    return config.get("API_ROUTING_FULL_PREFIX") or config.get("api_routing.full_prefix", "/api/v1")

# Construct route pattern
route_pattern = f"{_get_api_prefix()}/{{pillar}}/{{path:path}}"

@router.api_route(
    route_pattern,  # ✅ From config
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def universal_pillar_handler(request: Request, pillar: str, path: str):
    # ... existing code ...
```

**File:** `utilities/path_utils.py`

**BREAK:**
```python
# ❌ REMOVE hard-coded path
# common_paths = [
#     Path("/home/founders/demoversion/symphainy_source/symphainy-platform"),
#     Path.home() / "symphainy-platform",
# ]
```

**FIX:**
```python
# ✅ Use environment variable only
# Strategy 4: Check environment variable (already exists)
env_root = os.getenv("SYMPHAINY_PLATFORM_ROOT")
if env_root:
    project_root = Path(env_root).resolve()
    if (project_root / "foundations").exists():
        _PROJECT_ROOT_CACHE = project_root
        return _PROJECT_ROOT_CACHE

# Remove hard-coded common_paths fallback
# If we get here, raise error (don't guess)
raise RuntimeError(
    "Could not determine project root. "
    "Please ensure you're running from the symphainy-platform directory, "
    "or set SYMPHAINY_PLATFORM_ROOT environment variable."
)
```

---

## Testing Strategy

### Phase 1 Testing: Break Everything

**Goal:** Verify all anti-patterns are broken

1. **Test ConfigAdapter Breakage**
   ```bash
   # Should fail with "ConfigAdapter requires UnifiedConfigurationManager"
   python3 main.py
   ```

2. **Test JWT Breakage**
   ```bash
   # Should fail with "JWT_SECRET missing" or "JWT adapter not found"
   python3 main.py
   ```

3. **Test Hard-Coding Breakage**
   ```bash
   # Should fail with "route_pattern not defined" or similar
   python3 main.py
   ```

**Success:** Platform fails to start (expected)

### Phase 2 Testing: Fix Everything

**Goal:** Verify all fixes work

1. **Test Configuration Loading**
   ```bash
   python3 main.py
   # Should show: "✅ Config adapter initialized with UnifiedConfigurationManager"
   # Should show: "✅ Loaded X secrets from .env.secrets"
   # Should show: "✅ Loaded X values from config/development.env"
   ```

2. **Test Authentication**
   ```bash
   # Test Supabase token validation
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test"}'
   # Should return Supabase token (not JWT)
   ```

3. **Test Routing**
   ```bash
   # Test universal router with config-based prefix
   curl http://localhost:8000/api/v1/content-pillar/health
   # Should work (prefix from config)
   ```

4. **Test Lazy Loading**
   ```bash
   # Upload file - should lazy-load Content Steward
   curl -X POST http://localhost:8000/api/v1/content-pillar/upload-file \
     -F "file=@test.txt"
   # Should see lazy-loading logs
   ```

**Success:** Platform works with clean patterns

---

## Risk Assessment

### Breaking Changes

**Risk Level:** High (intentional)

**Mitigation:**
- Document all breakage
- Fix systematically
- Test after each fix
- Keep rollback plan (git commits)

### Lazy Loading

**Risk Level:** Low

**Why:**
- Lazy loading chain unchanged
- Only config access changes
- City Manager unchanged
- PlatformCapabilitiesMixin unchanged

### Authentication

**Risk Level:** Medium

**Why:**
- Removing JWT path is breaking change
- Supabase is already primary
- Need to verify all token validation paths

**Mitigation:**
- Test authentication flow thoroughly
- Verify Supabase tokens work
- Check all security guard usage

---

## Success Metrics

### Phase 1 Success (Break)

- ✅ Platform fails to start (expected)
- ✅ All failures documented
- ✅ Complete list of files needing fixes

### Phase 2 Success (Fix)

- ✅ Platform starts without errors
- ✅ All config loads correctly
- ✅ Authentication works (Supabase only)
- ✅ Routing works (config-based prefix)
- ✅ No hard-coded values remain

### Phase 3 Success (Harden)

- ✅ All URLs from config
- ✅ API prefixes configurable
- ✅ Path resolution works
- ✅ Option C ready

### Phase 4 Success (Validate)

- ✅ All tests pass
- ✅ Lazy loading verified
- ✅ CTO demo works
- ✅ Option C migration path clear

---

## Next Steps

1. **Review this plan** - Ensure approach is correct
2. **Start Phase 1** - Break all anti-patterns
3. **Document breakage** - List all failures
4. **Fix systematically** - One anti-pattern at a time
5. **Test incrementally** - After each fix
6. **Validate end-to-end** - Full platform test

---

**Document Version:** 1.0
**Last Updated:** 2025-01-XX
**Status:** Ready for Implementation
**Approach:** Break Then Fix - No Backward Compatibility for Anti-Patterns




