# Simple Adapters Analysis

**Date**: November 13, 2025  
**Purpose**: Investigate all "Simple" adapters in the codebase and determine if they should be removed to ensure the platform uses the intended production architecture.

---

## Executive Summary

Found **2 Simple adapters** in the codebase:
1. **SimpleHealthAdapter** - ❌ **NOT USED** (remnant)
2. **SimpleRulesAdapter** - ✅ **USED** (but should be replaced with OPA for production)

**Recommendation**: 
- **Remove SimpleHealthAdapter** (unused remnant)
- **Replace SimpleRulesAdapter with OPAPolicyAdapter** (align with Option C deployment strategy)

---

## Detailed Analysis

### 1. SimpleHealthAdapter

**Location**: `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/simple_health_adapter.py`

**Purpose**: Basic health monitoring using `psutil` (CPU, memory, disk) without external dependencies.

**Usage Analysis**:
- ✅ **Only referenced in its own file** (class definition)
- ❌ **NOT imported anywhere**
- ❌ **NOT used in Public Works Foundation Service**
- ❌ **NOT used in any abstractions**

**Current Production Adapter**: `OpenTelemetryHealthAdapter` (used in `_create_all_adapters()`)

**Verdict**: **REMOVE** - Unused remnant from earlier architecture.

---

### 2. SimpleRulesAdapter

**Location**: `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/simple_rules_adapter.py`

**Purpose**: In-memory rules engine for policy evaluation using simple if-then logic.

**Usage Analysis**:
- ✅ **Used in Public Works Foundation Service** (line 492):
  ```python
  from .infrastructure_adapters.simple_rules_adapter import SimpleRulesAdapter
  policy_adapter = SimpleRulesAdapter()
  self.policy_abstraction = PolicyAbstraction(policy_adapter=policy_adapter, ...)
  ```
- ✅ **Implements PolicyProtocol** correctly
- ❌ **NOT the intended production adapter**

**Production Alternative**: `OPAPolicyAdapter` exists at:
- `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/opa_policy_adapter.py`

**OPAPolicyAdapter Features**:
- Direct integration with Open Policy Agent (OPA)
- Supports OPA's policy language (Rego)
- Configurable OPA URL (default: `http://localhost:8181`)
- Aligns with **Option C (Everything as a Service)** deployment strategy

**Verdict**: **REPLACE with OPAPolicyAdapter** - SimpleRulesAdapter is a development/testing fallback, not production-ready.

---

## Impact Analysis

### Removing SimpleHealthAdapter

**Risk**: ✅ **LOW** - Not used anywhere, safe to remove.

**Files to Update**:
- None (not imported/used)

**Action**: Delete file.

---

### Replacing SimpleRulesAdapter with OPAPolicyAdapter

**Risk**: ⚠️ **MEDIUM** - Currently in use, but replacement exists and implements same protocol.

**Files to Update**:
1. `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py`
   - Line 488: Change import from `SimpleRulesAdapter` to `OPAPolicyAdapter`
   - Line 492: Change instantiation to `OPAPolicyAdapter(opa_url=...)`
   - Add OPA URL configuration (environment variable or config)

**Configuration Needed**:
- OPA service URL (for Option C: managed OPA service)
- Default: `http://localhost:8181` (for local development)
- Production: Managed OPA service URL (from environment/config)

**Testing Considerations**:
- Verify `OPAPolicyAdapter` implements `PolicyProtocol` correctly
- Test policy evaluation with OPA
- Ensure backward compatibility with existing policy evaluations

---

## Recommendations

### Immediate Actions

1. **Remove SimpleHealthAdapter**
   - Delete `simple_health_adapter.py`
   - No other changes needed (not used)

2. **Replace SimpleRulesAdapter with OPAPolicyAdapter**
   - Update `PublicWorksFoundationService` to use `OPAPolicyAdapter`
   - Add OPA URL configuration (environment variable)
   - Test policy evaluation works correctly
   - Consider keeping `SimpleRulesAdapter` for local development/testing if needed

### Future Considerations

1. **Configuration Management**
   - Add `OPA_URL` environment variable
   - Support both local OPA (development) and managed OPA (production)
   - Document OPA setup in deployment guide

2. **Testing Strategy**
   - Unit tests with `OPAPolicyAdapter` (mock OPA server)
   - Integration tests with real OPA instance
   - Consider keeping `SimpleRulesAdapter` as a test double if needed

3. **Documentation**
   - Update architecture docs to reflect OPA as production policy engine
   - Document OPA policy language (Rego) usage
   - Add OPA setup instructions for Option C deployment

---

## Migration Plan

### Phase 1: Remove SimpleHealthAdapter (Low Risk)
```bash
# Delete unused file
rm symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/simple_health_adapter.py
```

### Phase 2: Replace SimpleRulesAdapter (Medium Risk)

**Step 1**: Update Public Works Foundation Service
```python
# Before
from .infrastructure_adapters.simple_rules_adapter import SimpleRulesAdapter
policy_adapter = SimpleRulesAdapter()

# After
from .infrastructure_adapters.opa_policy_adapter import OPAPolicyAdapter
import os
opa_url = os.getenv("OPA_URL", "http://localhost:8181")
policy_adapter = OPAPolicyAdapter(opa_url=opa_url)
```

**Step 2**: Add OPA URL configuration
- Add `OPA_URL` to `.env.example`
- Document in deployment guide

**Step 3**: Test
- Verify policy evaluation works
- Test with local OPA instance
- Test with managed OPA service (Option C)

**Step 4**: (Optional) Keep SimpleRulesAdapter for testing
- Move to `tests/` directory if needed for test doubles
- Or remove if not needed

---

## Summary

| Adapter | Status | Action | Risk |
|---------|--------|--------|------|
| SimpleHealthAdapter | ❌ Unused | **DELETE** | Low |
| SimpleRulesAdapter | ✅ Used | **REPLACE with OPAPolicyAdapter** | Medium |

**Next Steps**:
1. Remove SimpleHealthAdapter (immediate)
2. Replace SimpleRulesAdapter with OPAPolicyAdapter (after testing)
3. Update configuration and documentation





