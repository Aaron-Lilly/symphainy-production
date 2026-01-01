# ServiceDiscoveryRegistry Refactoring Plan

**Date**: November 14, 2025  
**Status**: 🚧 In Progress

---

## Issue

`ServiceDiscoveryRegistry` creates `ConsulServiceDiscoveryAdapter` internally in `_build_consul_adapter()`, which violates the architectural pattern: **"Public Works Foundation creates everything; registries expose"**.

---

## Current State

1. **ServiceDiscoveryRegistry**:
   - Creates `ConsulServiceDiscoveryAdapter` in `_build_consul_adapter()`
   - Creates `ServiceDiscoveryAbstraction` in `build_infrastructure()`
   - Has methods: `build_infrastructure()`, `_build_consul_adapter()`, `get_service_discovery()`

2. **PublicWorksFoundationService**:
   - Calls `service_discovery_registry.build_infrastructure(consul_config)`
   - Gets abstraction via `service_discovery_registry.get_service_discovery()`
   - Comment says: "Service Discovery Registry is a special case - it still creates adapters because Consul is self-hosted (not a managed service)"

---

## Target State

1. **PublicWorksFoundationService**:
   - Creates `ConsulServiceDiscoveryAdapter` in `_create_all_adapters()`
   - Creates `ServiceDiscoveryAbstraction` in `_create_all_abstractions()` (injecting adapter)
   - Registers abstraction with `ServiceDiscoveryRegistry` in `_initialize_and_register_abstractions()`

2. **ServiceDiscoveryRegistry**:
   - **Exposure-only** (like other registries)
   - Removes `build_infrastructure()`, `_build_consul_adapter()`, `_build_istio_adapter()`, `_build_linkerd_adapter()`
   - Adds `register_abstraction()` method
   - `get_service_discovery()` returns registered abstraction

---

## Implementation Steps

1. **Move Consul adapter creation to PublicWorksFoundationService**:
   - Add `ConsulServiceDiscoveryAdapter` creation in `_create_all_adapters()`
   - Create `consul.Consul` client from config
   - Store as `self.consul_service_discovery_adapter`

2. **Create ServiceDiscoveryAbstraction in PublicWorksFoundationService**:
   - Add `ServiceDiscoveryAbstraction` creation in `_create_all_abstractions()`
   - Inject `consul_service_discovery_adapter`
   - Store as `self.service_discovery_abstraction`

3. **Refactor ServiceDiscoveryRegistry**:
   - Remove `build_infrastructure()` method
   - Remove `_build_consul_adapter()`, `_build_istio_adapter()`, `_build_linkerd_adapter()` methods
   - Add `register_abstraction()` method
   - Update `get_service_discovery()` to return registered abstraction
   - Update `__init__()` to remove adapter/abstraction initialization

4. **Update PublicWorksFoundationService**:
   - Remove old `ServiceDiscoveryRegistry.build_infrastructure()` call
   - Initialize `ServiceDiscoveryRegistry` (exposure-only)
   - Register abstraction with registry
   - Update `get_service_discovery_abstraction()` to return from instance variable

---

## Benefits

1. **Architectural Consistency** - All registries follow the same pattern
2. **Swappability** - Consul adapter can be swapped for Istio/Linkerd in `_create_all_adapters()`
3. **Testability** - Adapter can be mocked and injected
4. **Future-Ready** - Easy to migrate to Consul Cloud (Option C)

---

**Status**: Ready to implement




