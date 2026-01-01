# Agentic Foundation Pattern Analysis

**Date:** November 19, 2025  
**Purpose:** Determine the appropriate utility pattern for Agentic Foundation

---

## 🏗️ Agentic Foundation Architecture

### Components:

1. **Main Foundation Service**
   - `AgenticFoundationService` (FoundationServiceBase)
   - Provides SDK access to realms
   - Coordinates agent lifecycle

2. **Manager Service**
   - `AgenticManagerService` (ManagerServiceBase)
   - Orchestrates agents across realms

3. **SDK Components** (`agent_sdk/`)
   - `AgentBase` - Base class for agents (ABC, TenantProtocol)
   - `MCPClientManager` - MCP client management
   - `PolicyIntegration` - Policy integration
   - `ToolComposition` - Tool composition
   - `BusinessAbstractionHelper` - Business abstraction helper
   - Agent types (DimensionLiaisonAgent, etc.)

4. **Infrastructure Enablement Services** (`infrastructure_enablement/`)
   - `ToolRegistryService` - Business service (NOT FoundationServiceBase)
   - `ToolDiscoveryService` - Business service
   - `SessionService` - Business service
   - `PolicyService` - Business service
   - `HealthService` - Business service
   - `AGUIOutputFormatter` - Business service

5. **Tool Factory** (`tool_factory/`)
   - `ToolFactoryService` - Tool creation service

6. **Other Services**
   - `AgentDashboardService` - Dashboard service
   - `SpecializationRegistry` - Registry service
   - `AGUISchemaRegistry` - Schema registry

---

## 🔍 Key Observations

### Similarities to Curator:
- ✅ Has a main foundation service (FoundationServiceBase)
- ✅ Has multiple sub-services/components
- ✅ Provides capabilities to realms

### Differences from Curator:
- ❌ SDK components are **base classes**, not micro-services
- ❌ Infrastructure enablement services are **business services** (not FoundationServiceBase)
- ❌ More SDK-focused (provides base classes for agents)
- ❌ Has a Manager service (ManagerServiceBase)

### Similarities to Public Works:
- ✅ Has infrastructure enablement services (similar to abstractions)
- ✅ Services are business services (not foundation services)

---

## 🎯 Pattern Recommendation

### **"Utilities at Service Layer" Pattern** (Similar to Public Works)

**Rationale:**
1. **SDK Components (Base Classes)**: Should NOT have utilities directly
   - `AgentBase` and other base classes get utilities from mixins (already implemented)
   - These are base classes, not services

2. **Infrastructure Enablement Services**: Should handle utilities at service layer
   - Similar to Public Works abstractions
   - These are business services that orchestrate infrastructure
   - Utilities should be handled at the service layer (before delegating to abstractions)

3. **Main Foundation Service**: Should handle utilities
   - Coordinates SDK access
   - Wraps calls to infrastructure enablement services
   - Similar to Public Works main service

4. **Manager Service**: Should handle utilities
   - It's a ManagerServiceBase
   - Orchestrates agents
   - Should use utilities for coordination

---

## 📋 Pattern Details

### Main Foundation Service (`AgenticFoundationService`)
- ✅ Wraps infrastructure enablement service calls with utilities
- ✅ Handles realm-facing APIs with full utilities
- ✅ Uses `handle_error_with_audit`, `log_operation_with_telemetry`, `record_health_metric`
- ✅ Validates security and tenant when `user_context` is provided

### Infrastructure Enablement Services
- ✅ Handle utilities at service layer
- ✅ Similar to Public Works abstractions pattern
- ✅ Services wrap abstraction calls with utilities
- ✅ Abstractions are utility-free (if any)

### SDK Components (Base Classes)
- ✅ No utilities needed (get from mixins)
- ✅ These are base classes, not services
- ✅ Utilities come from `FoundationServiceBase` mixins

### Manager Service (`AgenticManagerService`)
- ✅ Handles utilities at service layer
- ✅ Uses utilities for coordination and orchestration

---

## 🔧 Implementation Approach

1. **Main Service**: Add utilities to all methods (similar to Public Works)
2. **Infrastructure Enablement Services**: Add utilities to all methods (similar to Public Works abstractions)
3. **SDK Components**: No changes needed (base classes)
4. **Manager Service**: Add utilities to all methods

---

## ✅ Expected Pattern

**"Utilities at Service Layer"** - Same pattern as Public Works and Communication Foundations

- Main service wraps calls with utilities
- Infrastructure enablement services handle utilities at their service layer
- SDK components (base classes) get utilities from mixins
- Manager service handles utilities at service layer







