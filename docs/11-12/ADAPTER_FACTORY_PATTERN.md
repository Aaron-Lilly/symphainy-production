# Adapter Factory Pattern - Future Architecture

**Date**: November 13, 2025  
**Purpose**: Define the factory pattern for future dynamic adapter creation, even though we're not implementing it initially.

---

## Executive Summary

**Decision**: Design abstractions to support factory pattern from day one, even though we won't implement factories initially.

**Why**: This prevents breaking changes when we add factory support later for dynamic multi-provider scenarios (e.g., user-configurable LLM providers).

---

## Factory Pattern Design

### Factory Protocol

```python
from typing import Protocol, Dict, Any, Optional

class LLMAdapterFactory(Protocol):
    """Protocol for LLM adapter factories."""
    
    def create_adapters(self, **kwargs) -> Dict[str, Any]:
        """
        Create all LLM adapters.
        
        Returns:
            Dictionary mapping provider names to adapter instances
        """
        ...
```

### Simple Factory Implementation (Initial)

```python
#!/usr/bin/env python3
"""
Simple LLM Adapter Factory

Initial implementation - creates adapters from configuration.
Future: Can be extended for dynamic creation based on user preferences, etc.
"""

import logging
from typing import Dict, Any, Optional
from ..infrastructure_adapters.openai_adapter import OpenAIAdapter
from ..infrastructure_adapters.anthropic_adapter import AnthropicAdapter
from ..infrastructure_adapters.ollama_adapter import OllamaAdapter

logger = logging.getLogger(__name__)

class SimpleLLMAdapterFactory:
    """
    Simple factory for creating LLM adapters from configuration.
    
    This is the initial implementation. Future versions can support:
    - User-configurable providers
    - Dynamic provider discovery
    - Provider-specific configuration
    """
    
    def __init__(self, config_adapter: Optional[ConfigAdapter] = None):
        """
        Initialize factory.
        
        Args:
            config_adapter: Optional configuration adapter for reading config
        """
        self.config_adapter = config_adapter
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def create_adapters(self, **kwargs) -> Dict[str, Any]:
        """
        Create all LLM adapters from configuration.
        
        Args:
            **kwargs: Adapter configuration (api keys, endpoints, etc.)
        
        Returns:
            Dictionary mapping provider names to adapter instances
        """
        adapters = {}
        
        try:
            # Get configuration (from kwargs or config_adapter)
            config = self._get_config(**kwargs)
            
            # Create OpenAI adapter
            if config.get("openai_enabled", True):
                adapters["openai"] = OpenAIAdapter(
                    api_key=config.get("openai_api_key"),
                    base_url=config.get("openai_base_url"),
                    **kwargs
                )
            
            # Create Anthropic adapter
            if config.get("anthropic_enabled", True):
                adapters["anthropic"] = AnthropicAdapter(
                    api_key=config.get("anthropic_api_key"),
                    **kwargs
                )
            
            # Create Ollama adapter (optional)
            if config.get("ollama_enabled", False):
                adapters["ollama"] = OllamaAdapter(
                    base_url=config.get("ollama_base_url", "http://localhost:11434"),
                    **kwargs
                )
            
            self.logger.info(f"✅ Created {len(adapters)} LLM adapters via factory")
            return adapters
            
        except Exception as e:
            self.logger.error(f"Failed to create LLM adapters: {e}")
            raise
    
    def _get_config(self, **kwargs) -> Dict[str, Any]:
        """Get configuration from kwargs or config_adapter."""
        if self.config_adapter:
            # Read from config adapter
            return self.config_adapter.get_llm_config()
        else:
            # Use kwargs directly
            return kwargs
```

### Future Factory Implementation (Dynamic)

```python
#!/usr/bin/env python3
"""
Dynamic LLM Adapter Factory

Future implementation - supports user-configurable providers, dynamic discovery, etc.
"""

import logging
from typing import Dict, Any, Optional, List
from ..infrastructure_adapters.openai_adapter import OpenAIAdapter
from ..infrastructure_adapters.anthropic_adapter import AnthropicAdapter
from ..infrastructure_adapters.ollama_adapter import OllamaAdapter

logger = logging.getLogger(__name__)

class DynamicLLMAdapterFactory:
    """
    Dynamic factory for creating LLM adapters based on user preferences.
    
    Future features:
    - User-configurable provider selection
    - Dynamic provider discovery
    - Provider-specific configuration per user
    - Provider health checking and failover
    """
    
    def __init__(self, 
                 config_adapter: Optional[ConfigAdapter] = None,
                 user_preferences: Optional[Dict[str, Any]] = None):
        """
        Initialize dynamic factory.
        
        Args:
            config_adapter: Configuration adapter
            user_preferences: User-specific provider preferences
        """
        self.config_adapter = config_adapter
        self.user_preferences = user_preferences or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    def create_adapters(self, 
                       enabled_providers: Optional[List[str]] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Create LLM adapters based on user preferences and configuration.
        
        Args:
            enabled_providers: List of provider names to enable (if None, use user preferences)
            **kwargs: Adapter configuration
        
        Returns:
            Dictionary mapping provider names to adapter instances
        """
        adapters = {}
        
        # Determine which providers to create
        providers_to_create = enabled_providers or self._get_user_preferred_providers()
        
        # Create each provider adapter
        for provider in providers_to_create:
            try:
                adapter = self._create_provider_adapter(provider, **kwargs)
                if adapter:
                    adapters[provider] = adapter
            except Exception as e:
                self.logger.warning(f"Failed to create {provider} adapter: {e}")
                # Continue with other providers
        
        self.logger.info(f"✅ Created {len(adapters)} LLM adapters dynamically")
        return adapters
    
    def _get_user_preferred_providers(self) -> List[str]:
        """Get user's preferred providers from preferences."""
        # Future: Read from user preferences
        return self.user_preferences.get("preferred_providers", ["openai", "anthropic"])
    
    def _create_provider_adapter(self, provider: str, **kwargs) -> Optional[Any]:
        """Create adapter for specific provider."""
        if provider == "openai":
            return OpenAIAdapter(**kwargs)
        elif provider == "anthropic":
            return AnthropicAdapter(**kwargs)
        elif provider == "ollama":
            return OllamaAdapter(**kwargs)
        else:
            self.logger.warning(f"Unknown provider: {provider}")
            return None
```

---

## Abstraction Pattern (Future-Ready)

### LLM Abstraction with Factory Support

```python
class LLMAbstraction(LLMProtocol):
    """LLM abstraction - supports both direct injection and factory pattern."""
    
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

---

## Usage Patterns

### Current Usage (Direct Injection)

```python
# In Registry
async def _initialize_adapters(self):
    """Create adapters directly."""
    self.openai_adapter = OpenAIAdapter(api_key=...)
    self.anthropic_adapter = AnthropicAdapter(api_key=...)

async def _initialize_abstractions(self):
    """Create abstraction with direct injection."""
    self.llm_abstraction = LLMAbstraction(
        openai_adapter=self.openai_adapter,
        anthropic_adapter=self.anthropic_adapter,
        provider="openai"
    )
```

### Future Usage (Factory Pattern)

```python
# In Registry
async def _initialize_abstractions(self):
    """Create abstraction with factory."""
    factory = SimpleLLMAdapterFactory(config_adapter=self.config_adapter)
    self.llm_abstraction = LLMAbstraction(
        adapter_factory=factory,  # Use factory instead of direct injection
        provider="openai"
    )
```

### Testing (Direct Injection - Always Works)

```python
# In Tests
@pytest.fixture
def mock_openai_adapter(self):
    return AsyncMock()

@pytest.fixture
def mock_anthropic_adapter(self):
    return AsyncMock()

@pytest.fixture
def llm_abstraction(self, mock_openai_adapter, mock_anthropic_adapter):
    """Test with direct injection - no factory needed."""
    return LLMAbstraction(
        openai_adapter=mock_openai_adapter,
        anthropic_adapter=mock_anthropic_adapter,
        provider="openai"
    )
```

---

## Benefits of Future-Ready Design

### 1. No Breaking Changes
- ✅ Abstraction signature supports factory from day one
- ✅ Can add factory support later without changing interface
- ✅ Existing code (direct injection) continues to work

### 2. Testability
- ✅ Can always use direct injection for testing
- ✅ Can mock factory if needed
- ✅ No dependency on factory for tests

### 3. Flexibility
- ✅ Simple cases: Use direct injection
- ✅ Complex cases: Use factory
- ✅ Future: Can add dynamic factory without breaking changes

### 4. Clear Migration Path
- ✅ Start with direct injection everywhere
- ✅ Add factory when needed (user config, dynamic providers, etc.)
- ✅ Migrate incrementally (no big bang)

---

## When to Use Factory Pattern

### Use Direct Injection When:
- ✅ Simple, static configuration
- ✅ Testing (always use direct injection)
- ✅ Single provider scenario
- ✅ Fixed provider set

### Use Factory Pattern When:
- ✅ User-configurable providers
- ✅ Dynamic provider discovery
- ✅ Provider-specific configuration per user/tenant
- ✅ Multi-tenant scenarios with different provider sets
- ✅ Provider health checking and failover

---

## Implementation Timeline

### Phase 1: Now (Initial Platform)
- ✅ Design abstraction interface to support factory
- ✅ Use direct injection everywhere
- ✅ Factory interface exists but not implemented

### Phase 2: Future (When Needed)
- ⏳ Implement `SimpleLLMAdapterFactory` if needed
- ⏳ Use factory in registries for dynamic scenarios
- ⏳ Keep direct injection for simple cases

### Phase 3: Advanced (Future)
- ⏳ Implement `DynamicLLMAdapterFactory` for user config
- ⏳ Add provider health checking
- ⏳ Add provider failover logic

---

## Other Abstractions That Could Use Factories

### Session Abstraction
- Future: User-configurable session storage (Redis, Memcached, etc.)

### File Management Abstraction
- Future: User-configurable storage backends (GCS, S3, Azure Blob, etc.)

### Cache Abstraction
- Future: User-configurable cache backends (Redis, Memcached, etc.)

### Telemetry Abstraction
- Future: User-configurable telemetry backends (OpenTelemetry, Datadog, etc.)

---

## Summary

**Design Decision**: Support factory pattern in abstraction interface from day one, even though we won't implement factories initially.

**Benefits**:
- ✅ No breaking changes when adding factory support
- ✅ Testable now (direct injection)
- ✅ Flexible for future (factory support ready)
- ✅ Clear migration path

**Implementation**:
- ✅ Now: Use direct injection everywhere
- ⏳ Future: Add factory when needed for dynamic scenarios

---

**Last Updated**: November 13, 2025





