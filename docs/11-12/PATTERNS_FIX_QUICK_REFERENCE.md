# Production Patterns Fix - Quick Reference

**Last Updated**: November 13, 2025

---

## Issue Summary

| Issue | Current State | Target State | Effort | Priority |
|-------|--------------|--------------|--------|----------|
| **1. Parameter Naming** | 54 `context_data` vs 227 `business_context` | All use `business_context` | 1-1.5 days | Medium |
| **2. Required Parameters** | ~10-15 dataclasses | All have defaults | 1 day | Low |
| **3. Method Naming** | 40 legacy method names | All use protocol names | 1-1.5 days | Low |

---

## Issue 1: Parameter Naming - Quick Fix Guide

### Standard: Use `business_context` (not `context_data`)

**Files to Update** (54 occurrences):
1. `business_outcomes_orchestrator.py` - 3 methods
2. `business_outcomes_mcp_server.py` - 3 tools
3. Other files - 48 occurrences

**Quick Fix Pattern**:
```python
# OLD
async def generate_strategic_roadmap(self, context_data: Dict[str, Any], user_id: str):
    # Use context_data...

# NEW
async def generate_strategic_roadmap(self, business_context: Dict[str, Any], user_id: str):
    # Use business_context...
```

**Search & Replace**:
- `context_data` → `business_context` (in parameter names)
- `context_data` → `business_context` (in variable assignments)
- Update docstrings

---

## Issue 2: Required Parameters - Quick Fix Guide

### Standard: Use `field(default_factory=...)` for timestamps and collections

**Files to Update**:
1. `foundations/public_works_foundation/abstraction_contracts/telemetry_protocol.py` - `TelemetryData`, `TraceSpan`

**Quick Fix Pattern**:
```python
# OLD
@dataclass
class TelemetryData:
    timestamp: datetime  # Required
    labels: Dict[str, str] = None  # Bad default
    metadata: Dict[str, Any] = None  # Bad default

# NEW
from dataclasses import field

@dataclass
class TelemetryData:
    timestamp: datetime = field(default_factory=datetime.utcnow)  # Auto-generate
    labels: Dict[str, str] = field(default_factory=dict)  # Proper default
    metadata: Dict[str, Any] = field(default_factory=dict)  # Proper default
```

**Common Patterns**:
- `timestamp: datetime` → `timestamp: datetime = field(default_factory=datetime.utcnow)`
- `created_at: datetime` → `created_at: datetime = field(default_factory=datetime.utcnow)`
- `labels: Dict = None` → `labels: Dict = field(default_factory=dict)`
- `metadata: Dict = None` → `metadata: Dict = field(default_factory=dict)`
- `events: List = None` → `events: List = field(default_factory=list)`

---

## Issue 4: Method Naming - Quick Fix Guide

### Standard: Use protocol method names

**Mapping**:
- `retrieve_file()` → `get_file()` ✅ **FIX THIS**
- `create_metadata()` → **KEEP** (intentionally different - metadata-only operations)
- `update_metadata()` → **KEEP** (intentionally different - metadata-only operations)
- `delete_metadata()` → **KEEP** (intentionally different - metadata-only operations)

**Note**: Metadata methods are intentionally different from file operations. They enable metadata-only workflows for clients who don't want their data exposed.

**Files to Update** (reduced scope):
1. `content_steward_service.py` - `retrieve_file()` → `get_file()` ✅
2. Other files with `retrieve_file()` - Verify and update
3. `supabase_metadata_adapter.py` - **KEEP** `create_metadata()` etc. (intentionally different)

**Quick Fix Pattern**:
```python
# OLD
async def retrieve_file(self, file_id: str) -> Optional[Dict[str, Any]]:
    # Implementation...

# NEW (with deprecation)
async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
    """Get file via file_management infrastructure (SOA API)."""
    # Implementation...

# Deprecated method (remove after migration)
async def retrieve_file(self, file_id: str) -> Optional[Dict[str, Any]]:
    """DEPRECATED: Use get_file() instead."""
    import warnings
    warnings.warn(
        "retrieve_file() is deprecated. Use get_file() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return await self.get_file(file_id)
```

---

## Testing Checklist

After each fix:
- [ ] Run unit tests: `pytest tests/unit/`
- [ ] Run integration tests: `pytest tests/integration/`
- [ ] Check for new warnings
- [ ] Verify backward compatibility
- [ ] Update API documentation

---

## Commands for Verification

```bash
# Issue 1: Verify parameter naming
grep -rn "context_data" backend/business_enablement/ --include="*.py" | wc -l
# Should be 0 after fix

# Issue 2: Find dataclasses needing defaults
grep -rn "@dataclass" --include="*.py" -A 5 | grep -E "timestamp.*datetime[^=]|created_at.*datetime[^=]"

# Issue 4: Verify method naming
grep -rn "def retrieve_file\|def create_metadata\|def update_metadata\|def delete_metadata" --include="*.py"
# Should be 0 after fix (except deprecations)
```

---

## Decision Log

### Issue 1: Parameter Naming
- **Decision**: Standardize on `business_context`
- **Rationale**: 81% of usage already uses `business_context`, more descriptive
- **Date**: November 13, 2025

### Issue 4: Method Naming
- **Decision**: Standardize on protocol names (`get_file`, `create_file`, etc.)
- **Clarification**: `create_metadata()`/`update_metadata()`/`delete_metadata()` are intentionally different (metadata-only operations)
- **Date**: November 13, 2025

---

**See**: `PATTERNS_FIX_PLAN.md` for detailed implementation plan

