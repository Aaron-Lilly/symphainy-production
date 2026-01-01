# Standardized Abstraction & Adapter Pattern

**Date**: November 13, 2025  
**Purpose**: Define a standardized pattern for infrastructure adapters and abstractions that supports dependency injection, testability, and extensibility while maintaining flexibility.

---

## Executive Summary

This document proposes a **standardized pattern** for the 5-level infrastructure architecture that:
- ✅ Supports dependency injection (no internal adapter creation)
- ✅ Makes testing easier (mockable, no nested clients)
- ✅ Maintains flexibility (no forced base classes)
- ✅ Works with Platform Gateway (abstractions exposed to realms)
- ✅ Supports future extensibility (BYOI, custom adapters)

**Key Principle**: **Registries create, Abstractions consume, Adapters expose**

---

## Current Architecture Context

### 5-Level Architecture (Public Works Foundation)

```
Layer 0: Infrastructure Adapters (Raw Technology)
    ↓
Layer 1: Infrastructure Abstractions (Business Logic)
    ↓
Layer 2: Composition Services (Orchestration)
    ↓
Layer 3: Infrastructure Registries (Initialization & Discovery)
    ↓
Layer 4: Foundation Service (Public Works Foundation Service)
```

### Platform Gateway Integration

```
Public Works Foundation
    ↓ (exposes abstractions)
Platform Gateway (validates realm access)
    ↓ (grants access)
Realms (Smart City, Business Enablement, etc.)
```

### Current Issues

1. **Abstractions create adapters internally** → Hard to test, tight coupling
2. **Adapter.client pattern** → Nested mocking complexity
3. **No standardization** → Inconsistent patterns across codebase
4. **Parameter naming** → `business_context` vs `context_data` inconsistency

---

## Proposed Standardized Pattern

### Core Principle: **Dependency Injection via Registries**

**Registries are the single source of truth for initialization.** They:
- Create adapters (Layer 0)
- Create abstractions with adapters (Layer 1)
- Register with DI Container
- Expose via Platform Gateway

**Abstractions should NEVER create adapters internally.**

---

## Pattern 1: Adapter Standardization

### Adapter Interface Pattern (No Base Class Required)

**Principle**: Adapters implement protocols, not base classes. This maintains flexibility while providing structure.

#### Standard Adapter Structure

```python
#!/usr/bin/env python3
"""
[Adapter Name] Adapter - Raw Technology Wrapper

WHAT (Infrastructure Role): I provide [capability] using [technology]
HOW (Infrastructure Implementation): I wrap [technology] client with business logic
"""

import logging
from typing import Dict, Any, Optional
from ..abstraction_contracts.[protocol_name] import [ProtocolName]

logger = logging.getLogger(__name__)

class [AdapterName]Adapter([ProtocolName]):
    """
    [Technology] adapter for [capability].
    
    Provides raw technology access with minimal business logic.
    This is Layer 0 of the 5-layer infrastructure architecture.
    """
    
    def __init__(self, 
                 # Technology-specific config
                 host: str = "localhost",
                 port: int = 6379,
                 # Optional: nested client (if needed)
                 client: Optional[Any] = None,
                 **kwargs):
        """
        Initialize adapter.
        
        Args:
            host: Technology host
            port: Technology port
            client: Optional pre-configured client (for testing)
            **kwargs: Additional technology-specific config
        """
        self.host = host
        self.port = port
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Initialize client (use provided or create new)
        self.client = client or self._create_client(host, port, **kwargs)
        
        self.logger.info(f"✅ {self.__class__.__name__} initialized: {host}:{port}")
    
    def _create_client(self, host: str, port: int, **kwargs) -> Any:
        """Create technology client. Override in subclasses."""
        # Technology-specific client creation
        raise NotImplementedError("Subclasses must implement _create_client")
    
    # ============================================================================
    # PROTOCOL IMPLEMENTATION (Required by Protocol)
    # ============================================================================
    
    async def [protocol_method](self, ...) -> ...:
        """Implement protocol method."""
        # Use self.client or direct technology calls
        pass
    
    # ============================================================================
    # WRAPPER METHODS (For Testability)
    # ============================================================================
    
    # If adapter uses nested client, provide wrapper methods
    # This makes testing easier (no need to mock nested client)
    
    async def _client_operation(self, ...) -> ...:
        """
        Wrapper for client operation.
        
        This method wraps the nested client call, making it easier to mock.
        """
        return await self.client.operation(...)
    
    # ============================================================================
    # HEALTH & CONNECTION
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for adapter."""
        try:
            # Test connection
            is_healthy = await self._test_connection()
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "adapter": self.__class__.__name__,
                "host": self.host,
                "port": self.port
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _test_connection(self) -> bool:
        """Test connection to technology. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _test_connection")
```

### Key Adapter Patterns

#### Pattern 1A: Simple Adapter (No Nested Client)

```python
class GCSFileAdapter(FileManagementProtocol):
    """GCS file adapter - no nested client needed."""
    
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client.from_service_account_json(credentials_path)
        self.bucket = self.storage_client.bucket(bucket_name)
    
    async def upload_file(self, blob_name: str, file_data: bytes, ...) -> bool:
        """Upload file directly - no nested client."""
        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(file_data)
        return True
```

#### Pattern 1B: Adapter with Nested Client (Redis, ArangoDB, etc.)

```python
class RedisAdapter:
    """Redis adapter with wrapper methods only (no .client access)."""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6379,
                 client: Optional[redis.Redis] = None):  # Allow injection for testing
        self.host = host
        self.port = port
        # Use provided client or create new (internal only)
        self._client = client or redis.Redis(host=host, port=port)
    
    # WRAPPER METHODS (Required - no .client access)
    async def get(self, key: str) -> Optional[str]:
        """Get value - wrapper method."""
        return self._client.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value - wrapper method."""
        return self._client.set(key, value, ex=ttl)
    
    async def hset(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set hash fields - wrapper method."""
        return self._client.hset(key, mapping=mapping)
    
    async def hgetall(self, key: str) -> Dict[str, Any]:
        """Get all hash fields - wrapper method."""
        return self._client.hgetall(key)
    
    # NO .client property - all access via wrapper methods
```

**Why Wrapper Methods Only?**
- ✅ Easier to mock (mock `get()` not `client.get()`)
- ✅ Better abstraction (hide internal client structure)
- ✅ Consistent pattern (all adapters use same pattern)
- ✅ Future-proof (can change client implementation without breaking abstractions)
- ✅ No confusion (one pattern, not two)

---

## Pattern 2: Abstraction Standardization

### Abstraction Dependency Injection Pattern

**Principle**: Abstractions accept adapters via constructor, never create them internally.

#### Standard Abstraction Structure

```python
#!/usr/bin/env python3
"""
[Abstraction Name] Abstraction - Business Logic Implementation

WHAT (Infrastructure Role): I provide [capability] with business logic
HOW (Infrastructure Implementation): I coordinate adapters and apply business rules
"""

import logging
from typing import Dict, Any, Optional
from ..abstraction_contracts.[protocol_name] import [ProtocolName]

logger = logging.getLogger(__name__)

class [AbstractionName]Abstraction([ProtocolName]):
    """
    [Capability] abstraction with business logic.
    
    Implements [ProtocolName] using injected adapters.
    This is Layer 1 of the 5-layer infrastructure architecture.
    """
    
    def __init__(self,
                 # REQUIRED: Adapters via dependency injection
                 primary_adapter: [AdapterType],
                 secondary_adapter: Optional[AdapterType] = None,
                 config_adapter: Optional[ConfigAdapter] = None,
                 # Optional: Factory for creating additional adapters (advanced)
                 adapter_factory: Optional[Any] = None):
        """
        Initialize abstraction with dependency injection.
        
        Args:
            primary_adapter: Primary adapter (required)
            secondary_adapter: Optional secondary adapter
            config_adapter: Optional configuration adapter
            adapter_factory: Optional factory for creating adapters dynamically
        """
        # Store injected adapters
        self.primary_adapter = primary_adapter
        self.secondary_adapter = secondary_adapter
        self.config_adapter = config_adapter
        self.adapter_factory = adapter_factory
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Validate adapters
        if not primary_adapter:
            raise ValueError(f"{self.__class__.__name__} requires primary_adapter")
        
        self.logger.info(f"✅ {self.__class__.__name__} initialized")
    
    # ============================================================================
    # PROTOCOL IMPLEMENTATION
    # ============================================================================
    
    async def [protocol_method](self, ...) -> ...:
        """Implement protocol method with business logic."""
        # Use injected adapters
        result = await self.primary_adapter.method(...)
        # Apply business logic
        return self._apply_business_rules(result)
    
    # ============================================================================
    # BUSINESS LOGIC HELPERS
    # ============================================================================
    
    def _apply_business_rules(self, data: Any) -> Any:
        """Apply business logic rules. Override in subclasses."""
        return data
```

### Abstraction Patterns by Type

#### Pattern 2A: Single Adapter Abstraction

```python
class FileManagementAbstraction(FileManagementProtocol):
    """File management with GCS + Supabase."""
    
    def __init__(self,
                 gcs_adapter: GCSFileAdapter,  # Required
                 supabase_adapter: SupabaseFileManagementAdapter,  # Required
                 config_adapter: Optional[ConfigAdapter] = None):
        self.gcs_adapter = gcs_adapter
        self.supabase_adapter = supabase_adapter
        self.config_adapter = config_adapter
        # NO adapter creation here!
```

#### Pattern 2B: Multi-Adapter Abstraction (Provider Switching) - Future-Ready Design

```python
class LLMAbstraction(LLMProtocol):
    """LLM abstraction with provider switching - supports factory pattern for future."""
    
    def __init__(self,
                 # Option 1: Direct adapter injection (for testing and simple cases)
                 openai_adapter: Optional[OpenAIAdapter] = None,
                 anthropic_adapter: Optional[AnthropicAdapter] = None,
                 ollama_adapter: Optional[OllamaAdapter] = None,
                 # Option 2: Factory injection (for future dynamic creation)
                 adapter_factory: Optional[LLMAdapterFactory] = None,
                 # Configuration
                 provider: str = "openai",
                 **kwargs):
        """
        Initialize with dependency injection.
        
        Supports two patterns:
        1. Direct injection (current): Provide adapters directly
        2. Factory injection (future): Provide factory for dynamic creation
        
        At least one option must be provided.
        """
        self.provider = provider
        self.logger = logging.getLogger("LLMAbstraction")
        
        # Initialize adapters using factory OR direct injection
        if adapter_factory:
            # FUTURE: Use factory for dynamic creation
            self.adapters = adapter_factory.create_adapters(**kwargs)
            self.logger.info("✅ LLM abstraction initialized with factory")
        elif openai_adapter or anthropic_adapter:
            # CURRENT: Use direct injection
            self.adapters = {
                "openai": openai_adapter,
                "anthropic": anthropic_adapter,
                "ollama": ollama_adapter
            }
            self.logger.info("✅ LLM abstraction initialized with direct injection")
        else:
            raise ValueError(
                "Must provide either adapters (openai_adapter, anthropic_adapter) "
                "or adapter_factory"
            )
        
        # Set primary adapter
        self.primary_adapter = self.adapters.get(provider)
        if not self.primary_adapter:
            raise ValueError(f"Provider {provider} not available")
```

**Key Points**:
- ✅ **Future-ready**: Interface supports factory from day one
- ✅ **Testable now**: Can inject mocks directly (no factory needed)
- ✅ **No breaking changes**: Can add factory support later without changing signature
- ✅ **Clear pattern**: Factory takes precedence if provided, otherwise use direct injection

#### Pattern 2C: Abstraction with Adapter Selection

```python
class SessionAbstraction(SessionProtocol):
    """Session abstraction with adapter selection."""
    
    def __init__(self,
                 redis_adapter: Optional[RedisAdapter] = None,
                 jwt_adapter: Optional[JWTAdapter] = None,
                 adapter_type: str = "redis",
                 config_adapter: Optional[ConfigAdapter] = None):
        """
        Initialize with adapter selection.
        
        Adapters are injected, but abstraction selects which to use.
        """
        self.redis_adapter = redis_adapter
        self.jwt_adapter = jwt_adapter
        self.config_adapter = config_adapter
        
        # Select adapter based on type (but don't create it!)
        if adapter_type == "redis" and redis_adapter:
            # Create session adapter using injected Redis adapter
            from ..infrastructure_adapters.redis_session_adapter import RedisSessionAdapter
            self.adapter = RedisSessionAdapter(
                redis_adapter=redis_adapter,  # Pass injected adapter
                jwt_adapter=jwt_adapter
            )
        else:
            raise ValueError(f"Adapter type {adapter_type} requires {adapter_type}_adapter")
```

**Key Point**: Abstraction can create specialized adapters, but uses injected base adapters.

---

## Pattern 3: Registry Initialization Pattern

### Registry as Dependency Injection Coordinator

**Principle**: Registries are responsible for creating and wiring adapters and abstractions.

#### Standard Registry Structure

```python
#!/usr/bin/env python3
"""
[Capability] Registry - Infrastructure Initialization

WHAT (Registry Role): I initialize and coordinate [capability] infrastructure
HOW (Registry Implementation): I create adapters, then abstractions, then register with DI
"""

import logging
from typing import Dict, Any, Optional
from ..infrastructure_adapters.[adapter] import [Adapter]
from ..infrastructure_abstractions.[abstraction] import [Abstraction]

logger = logging.getLogger(__name__)

class [Capability]Registry:
    """
    Registry for [capability] infrastructure.
    
    Manages initialization of adapters and abstractions using dependency injection.
    This is Layer 3 of the 5-layer infrastructure architecture.
    """
    
    def __init__(self, config_adapter: ConfigAdapter):
        """Initialize registry with configuration."""
        self.config_adapter = config_adapter
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Infrastructure components (initialized in initialize())
        self.[adapter_name]_adapter = None
        self.[abstraction_name]_abstraction = None
        
        self.logger.info(f"✅ {self.__class__.__name__} initialized")
    
    async def initialize(self):
        """Initialize all infrastructure components."""
        try:
            # Layer 0: Initialize adapters
            await self._initialize_adapters()
            
            # Layer 1: Initialize abstractions (with injected adapters)
            await self._initialize_abstractions()
            
            # Layer 2: Initialize composition services (optional)
            await self._initialize_composition_services()
            
            # Verify health
            await self._verify_health()
            
            self.logger.info(f"✅ {self.__class__.__name__} fully initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.__class__.__name__}: {e}")
            raise
    
    async def _initialize_adapters(self):
        """Initialize infrastructure adapters (Layer 0)."""
        try:
            # Get configuration
            config = self.config_adapter.get_[capability]_config()
            
            # Create adapter with configuration
            self.[adapter_name]_adapter = [Adapter](
                host=config["host"],
                port=config["port"],
                **config.get("options", {})
            )
            
            # Test connection
            health = await self.[adapter_name]_adapter.health_check()
            if health.get("status") != "healthy":
                raise ConnectionError(f"Adapter health check failed: {health}")
            
            self.logger.info(f"✅ {[Adapter].__name__} initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize adapter: {e}")
            raise
    
    async def _initialize_abstractions(self):
        """Initialize infrastructure abstractions (Layer 1) with dependency injection."""
        try:
            # Create abstraction with injected adapters
            self.[abstraction_name]_abstraction = [Abstraction](
                primary_adapter=self.[adapter_name]_adapter,  # Inject adapter
                config_adapter=self.config_adapter
            )
            
            # Test abstraction
            health = await self.[abstraction_name]_abstraction.health_check()
            if health.get("status") != "healthy":
                raise ConnectionError(f"Abstraction health check failed: {health}")
            
            self.logger.info(f"✅ {[Abstraction].__name__} initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize abstraction: {e}")
            raise
```

### Registry Pattern Examples

#### Example: Security Registry (Multi-Adapter)

```python
class SecurityRegistry:
    """Security infrastructure registry."""
    
    async def _initialize_adapters(self):
        """Initialize security adapters."""
        # Create adapters
        self.supabase_adapter = SupabaseAdapter(...)
        self.redis_adapter = RedisAdapter(...)
        self.jwt_adapter = JWTAdapter(...)
    
    async def _initialize_abstractions(self):
        """Initialize abstractions with injected adapters."""
        # Inject adapters into abstractions
        self.auth_abstraction = AuthAbstraction(
            supabase_adapter=self.supabase_adapter,  # Injected
            jwt_adapter=self.jwt_adapter  # Injected
        )
        
        self.session_abstraction = SessionAbstraction(
            redis_adapter=self.redis_adapter,  # Injected
            jwt_adapter=self.jwt_adapter,  # Injected
            adapter_type="redis"
        )
```

#### Example: File Management Registry (Multi-Adapter)

```python
class FileManagementRegistry:
    """File management infrastructure registry."""
    
    async def _initialize_adapters(self):
        """Initialize file management adapters."""
        self.gcs_adapter = GCSFileAdapter(bucket_name=...)
        self.supabase_adapter = SupabaseFileManagementAdapter(...)
    
    async def _initialize_abstractions(self):
        """Initialize abstraction with injected adapters."""
        self.file_management_abstraction = FileManagementAbstraction(
            gcs_adapter=self.gcs_adapter,  # Injected
            supabase_adapter=self.supabase_adapter,  # Injected
            config_adapter=self.config_adapter
        )
```

---

## Pattern 4: Testing Support

### Adapter Testing Pattern

```python
# tests/unit/infrastructure_adapters/test_redis_adapter.py

@pytest.fixture
def mock_redis_client(self):
    """Mock Redis client."""
    client = AsyncMock()
    client.get = AsyncMock(return_value=b"value")
    client.set = AsyncMock(return_value=True)
    client.hset = AsyncMock(return_value=True)
    return client

@pytest.fixture
def redis_adapter(self, mock_redis_client):
    """Create Redis adapter with mocked client."""
    return RedisAdapter(
        host="localhost",
        port=6379,
        client=mock_redis_client  # Inject mocked client
    )

@pytest.mark.asyncio
async def test_get(self, redis_adapter, mock_redis_client):
    """Test get operation."""
    result = await redis_adapter.get("key")
    assert result == b"value"
    mock_redis_client.get.assert_called_once_with("key")
```

### Abstraction Testing Pattern

```python
# tests/unit/infrastructure_abstractions/test_file_management_abstraction.py

@pytest.fixture
def mock_gcs_adapter(self):
    """Mock GCS adapter."""
    adapter = AsyncMock()
    adapter.upload_file = AsyncMock(return_value=True)
    adapter.download_file = AsyncMock(return_value=b"content")
    return adapter

@pytest.fixture
def mock_supabase_adapter(self):
    """Mock Supabase adapter."""
    adapter = AsyncMock()
    adapter.create_file = AsyncMock(return_value={"uuid": "file_123"})
    adapter.get_file = AsyncMock(return_value={"uuid": "file_123"})
    return adapter

@pytest.fixture
def abstraction(self, mock_gcs_adapter, mock_supabase_adapter):
    """Create abstraction with injected mocks."""
    return FileManagementAbstraction(
        gcs_adapter=mock_gcs_adapter,  # Injected mock
        supabase_adapter=mock_supabase_adapter,  # Injected mock
        config_adapter=MagicMock()
    )

@pytest.mark.asyncio
async def test_create_file(self, abstraction, mock_gcs_adapter, mock_supabase_adapter):
    """Test create file."""
    result = await abstraction.create_file({...})
    assert result is not None
    mock_gcs_adapter.upload_file.assert_called_once()
    mock_supabase_adapter.create_file.assert_called_once()
```

---

## Pattern 5: Platform Gateway Integration

### Abstraction Registration Pattern

```python
# In Public Works Foundation Service

async def initialize_foundation(self):
    """Initialize foundation and register abstractions."""
    # Initialize registries
    await self.security_registry.initialize()
    await self.file_management_registry.initialize()
    
    # Get abstractions from registries
    self.auth_abstraction = self.security_registry.get_abstraction("auth")
    self.session_abstraction = self.security_registry.get_abstraction("session")
    self.file_management_abstraction = self.file_management_registry.file_management_abstraction
    
    # Register with DI Container
    self.di_container.register_service("auth_abstraction", self.auth_abstraction)
    self.di_container.register_service("session_abstraction", self.session_abstraction)
    self.di_container.register_service("file_management_abstraction", self.file_management_abstraction)
    
    # Platform Gateway automatically exposes these via get_abstraction()
```

### Platform Gateway Access Pattern

```python
# In Realm Services (via InfrastructureAccessMixin)

def get_infrastructure_abstraction(self, name: str) -> Any:
    """Get abstraction via Platform Gateway."""
    # Platform Gateway validates realm access
    return self.platform_gateway.get_abstraction(
        realm_name=self.realm_name,
        abstraction_name=name
    )
```

---

## Migration Strategy

### Phase 1: Fix Critical Abstractions (Breaking) - Future-Ready Design

**Goal**: Fix LLMAbstraction and SessionAbstraction immediately, with factory support in interface.

**Steps**:
1. Update LLMAbstraction to accept adapters OR factory via constructor
2. Update SessionAbstraction to accept adapter via constructor
3. Remove all internal adapter creation
4. Update registries to create and inject adapters (use direct injection for now)
5. Update all call sites
6. Update tests

**Example**:
```python
# BEFORE (Anti-pattern)
class LLMAbstraction(LLMProtocol):
    def __init__(self, provider: str = "openai", **kwargs):
        self._initialize_adapters(**kwargs)  # ❌ Creates internally

# AFTER (Fixed - Future-Ready)
class LLMAbstraction(LLMProtocol):
    def __init__(self,
                 # Option 1: Direct injection (for testing and simple cases)
                 openai_adapter: Optional[OpenAIAdapter] = None,
                 anthropic_adapter: Optional[AnthropicAdapter] = None,
                 ollama_adapter: Optional[OllamaAdapter] = None,
                 # Option 2: Factory injection (for future dynamic creation)
                 adapter_factory: Optional[LLMAdapterFactory] = None,
                 provider: str = "openai",
                 **kwargs):
        # Use factory OR direct injection (factory takes precedence)
        if adapter_factory:
            self.adapters = adapter_factory.create_adapters(**kwargs)
        elif openai_adapter or anthropic_adapter:
            self.adapters = {
                "openai": openai_adapter,
                "anthropic": anthropic_adapter,
                "ollama": ollama_adapter
            }
        else:
            raise ValueError("Must provide adapters or factory")
        # NO internal creation!
```

**Key Point**: Interface supports factory from day one, but we use direct injection initially. Factory can be added later without breaking changes.

### Phase 2: Fix Remaining Abstractions (Breaking)

**Goal**: Fix all remaining abstractions creating adapters internally.

**Steps**:
1. Fix HealthAbstraction, TelemetryAbstraction, AlertManagementAbstraction
2. Fix TracingAbstraction, PolicyAbstraction
3. Fix VisualizationAbstraction, BusinessMetricsAbstraction
4. Update all registries
5. Update all call sites
6. Update tests

### Phase 3: Remove .client Access (Breaking)

**Goal**: Add wrapper methods and remove `.client` access.

**Steps**:
1. Add wrapper methods to all adapters with nested clients
2. Change `self.client` to `self._client` (private)
3. Update all abstractions to use wrapper methods
4. Remove all `.client` access from abstractions
5. Update tests to use wrapper methods

**Example**:
```python
# BEFORE
class RedisAdapter:
    def __init__(self, host, port):
        self.client = redis.Redis(host=host, port=port)

# Abstraction uses:
await self.redis_adapter.client.hset(key, mapping=data)  # ❌

# AFTER
class RedisAdapter:
    def __init__(self, host, port, client=None):
        self._client = client or redis.Redis(host=host, port=port)  # Private
    
    async def hset(self, key: str, mapping: Dict) -> bool:
        return self._client.hset(key, mapping=mapping)

# Abstraction uses:
await self.redis_adapter.hset(key, mapping=data)  # ✅
```

### Phase 4: Update All Tests (Non-Breaking)

**Goal**: Update all tests to use new patterns.

**Steps**:
1. Update adapter tests to use wrapper methods
2. Update abstraction tests to inject mocks
3. Update registry tests to verify DI pattern
4. Verify all tests pass

---

## Standardization Checklist

### For New Adapters

- [ ] Implements protocol (not base class)
- [ ] Accepts `client` parameter for testing (if nested client)
- [ ] Provides wrapper methods for common operations
- [ ] Exposes `.client` for advanced use cases
- [ ] Implements `health_check()` method
- [ ] Has proper logging
- [ ] Follows naming convention: `[Technology][Capability]Adapter`

### For New Abstractions

- [ ] Implements protocol (not base class)
- [ ] Accepts adapters via constructor (dependency injection)
- [ ] Never creates adapters internally
- [ ] Can accept adapter factory for dynamic creation (optional)
- [ ] Implements `health_check()` method
- [ ] Has proper logging
- [ ] Follows naming convention: `[Capability]Abstraction`

### For New Registries

- [ ] Creates adapters first (Layer 0)
- [ ] Creates abstractions with injected adapters (Layer 1)
- [ ] Creates composition services (Layer 2, optional)
- [ ] Registers with DI Container
- [ ] Verifies health of all components
- [ ] Follows naming convention: `[Capability]Registry`

---

## Benefits

### 1. Testability
- ✅ Easy to mock adapters (inject mocks)
- ✅ No nested client mocking needed (wrapper methods)
- ✅ Abstractions testable in isolation

### 2. Flexibility
- ✅ No forced base classes (protocols only)
- ✅ Supports multiple adapter types
- ✅ Supports adapter factories for dynamic creation
- ✅ Maintains `.client` access for advanced use

### 3. Consistency
- ✅ Standardized initialization pattern
- ✅ Standardized testing pattern
- ✅ Standardized naming conventions

### 4. Extensibility
- ✅ Easy to add new adapters
- ✅ Easy to add new abstractions
- ✅ Supports BYOI (Bring Your Own Infrastructure)
- ✅ Supports custom adapter factories

### 5. Maintainability
- ✅ Clear separation of concerns
- ✅ Registries handle initialization
- ✅ Abstractions handle business logic
- ✅ Adapters handle technology

---

## Example: Complete Pattern Implementation

### Adapter

```python
class RedisAdapter:
    """Redis adapter with wrapper methods."""
    
    def __init__(self, host: str = "localhost", port: int = 6379, 
                 client: Optional[redis.Redis] = None):
        self.host = host
        self.port = port
        self.client = client or redis.Redis(host=host, port=port)
    
    # Wrapper methods (for testing)
    async def get(self, key: str) -> Optional[str]:
        return self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        return self.client.set(key, value, ex=ttl)
    
    async def health_check(self) -> Dict[str, Any]:
        try:
            self.client.ping()
            return {"status": "healthy"}
        except:
            return {"status": "unhealthy"}
```

### Abstraction

```python
class CacheAbstraction(CacheProtocol):
    """Cache abstraction with dependency injection."""
    
    def __init__(self,
                 cache_adapter: RedisAdapter,  # Required - injected
                 config_adapter: Optional[ConfigAdapter] = None):
        self.cache_adapter = cache_adapter  # Use injected adapter
        self.config_adapter = config_adapter
        # NO adapter creation here!
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Use injected adapter's wrapper method
        return await self.cache_adapter.get(key)
```

### Registry

```python
class CacheRegistry:
    """Cache infrastructure registry."""
    
    async def _initialize_adapters(self):
        """Create Redis adapter."""
        config = self.config_adapter.get_redis_config()
        self.redis_adapter = RedisAdapter(
            host=config["host"],
            port=config["port"]
        )
    
    async def _initialize_abstractions(self):
        """Create abstraction with injected adapter."""
        self.cache_abstraction = CacheAbstraction(
            cache_adapter=self.redis_adapter  # Inject adapter
        )
```

### Test

```python
@pytest.fixture
def mock_redis_adapter(self):
    """Mock Redis adapter."""
    adapter = AsyncMock()
    adapter.get = AsyncMock(return_value="value")
    return adapter

@pytest.fixture
def cache_abstraction(self, mock_redis_adapter):
    """Create abstraction with mock."""
    return CacheAbstraction(cache_adapter=mock_redis_adapter)

@pytest.mark.asyncio
async def test_get(self, cache_abstraction, mock_redis_adapter):
    """Test get operation."""
    result = await cache_abstraction.get("key")
    assert result == "value"
    mock_redis_adapter.get.assert_called_once_with("key")
```

---

## Migration Priority

### High Priority (Do First)
1. **LLM Abstraction** - Currently creates adapters internally
2. **Session Abstraction** - Uses nested client pattern
3. **Add wrapper methods** to Redis adapters

### Medium Priority
4. **Standardize parameter naming** (`business_context` vs `context_data`)
5. **Add wrapper methods** to all adapters with nested clients
6. **Update all registries** to use DI pattern

### Low Priority
7. **Add default factories** to dataclasses
8. **Standardize method names** (legacy cleanup)

---

## Decisions Made

1. **Adapter Factory Pattern**: **ARCHITECT FOR IT NOW, IMPLEMENT LATER** - Design abstraction interface to support factory from day one, but use direct injection initially. This prevents breaking changes when we add factory support later for dynamic multi-provider scenarios.

2. **Base Classes**: **Protocols only** - No base classes, maintain flexibility through protocols.

3. **Nested Client Access**: **REMOVE `.client` access** - Standardize on wrapper methods only. This provides consistent testing, better abstraction, and easier maintenance.

4. **Migration Timeline**: **Aggressive breaking changes** - Fix all issues now, don't maintain backward compatibility.

---

**Last Updated**: November 13, 2025

