# Phase 2 Updated Approach - Three-Tier Access Pattern

**Date**: November 15, 2025  
**Status**: ✅ **Approach Updated Based on Architecture Review**

---

## Architecture Review Summary

After reviewing the current architecture, we've identified the correct pattern for accessing capabilities:

### Three-Tier Access Pattern

1. **SOA APIs (First Priority)** - Smart City and other realm services
2. **Platform Gateway (Second Priority)** - Infrastructure abstractions
3. **Fail Gracefully (Third Priority)** - Clear error messages

See `ABSTRACTION_ACCESS_PATTERN.md` for complete documentation.

---

## Updated Phase 2 Strategy

### Key Changes from Original Plan

**Original Plan**:
- Option 1: Try Platform Gateway
- Option 2: Fail gracefully

**Updated Plan**:
- **Tier 1**: Try SOA APIs first (Smart City services)
- **Tier 2**: Try Platform Gateway (infrastructure abstractions)
- **Tier 3**: Fail gracefully with clear error

---

## Implementation Pattern

### Standard Three-Tier Pattern

```python
async def get_capability(self, capability_name: str, **kwargs) -> Dict[str, Any]:
    """
    Get capability using three-tier access pattern.
    """
    # Tier 1: Try SOA API first (if applicable)
    soa_service = await self._get_soa_service_for_capability(capability_name)
    if soa_service:
        try:
            result = await soa_service.get_capability(**kwargs)
            if result:
                return {"success": True, "data": result}
        except Exception as e:
            self.logger.warning(f"SOA API failed: {e}, trying Platform Gateway")
    
    # Tier 2: Try Platform Gateway
    try:
        abstraction = self.get_abstraction(capability_name)
        if abstraction:
            result = await abstraction.get_capability(**kwargs)
            if result:
                return {"success": True, "data": result}
    except Exception as e:
        self.logger.warning(f"Platform Gateway access failed: {e}")
    
    # Tier 3: Fail gracefully
    return {
        "success": False,
        "error": f"{capability_name} capability not available",
        "error_code": "CAPABILITY_UNAVAILABLE",
        "message": (
            f"Could not access {capability_name}. "
            f"Tried SOA APIs and Platform Gateway - both unavailable."
        )
    }
```

---

## Service-Specific Patterns

### File Operations

```python
# Tier 1: Content Steward SOA API
content_steward = await self.get_content_steward_api()
if content_steward:
    file_record = await content_steward.get_file(file_id)
    if file_record:
        return {"success": True, "data": file_record}

# Tier 2: Platform Gateway
file_management = self.get_abstraction("file_management")
if file_management:
    file_record = await file_management.get_file(file_id)
    if file_record:
        return {"success": True, "data": file_record}

# Tier 3: Fail gracefully
return {"success": False, "error": "File retrieval failed", ...}
```

### Metadata Operations

```python
# Tier 1: Librarian SOA API
librarian = await self.get_librarian_api()
if librarian:
    metadata = await librarian.get_knowledge_item(item_id)
    if metadata:
        return {"success": True, "data": metadata}

# Tier 2: Platform Gateway
content_metadata = self.get_abstraction("content_metadata")
if content_metadata:
    metadata = await content_metadata.get_content_metadata(item_id)
    if metadata:
        return {"success": True, "data": metadata}

# Tier 3: Fail gracefully
return {"success": False, "error": "Metadata retrieval failed", ...}
```

### LLM Operations

```python
# Tier 1: No SOA API for LLM (use Platform Gateway directly)
# Tier 2: Platform Gateway
llm = self.get_abstraction("llm")
if llm:
    result = await llm.generate_text(prompt)
    if result:
        return {"success": True, "data": result}

# Tier 3: Fail gracefully
return {"success": False, "error": "LLM capability not available", ...}
```

---

## Benefits of Updated Approach

1. **Encapsulation**: SOA APIs hide infrastructure complexity
2. **Flexibility**: Can use SOA APIs or abstractions depending on needs
3. **Resilience**: Graceful degradation when services unavailable
4. **Observability**: Clear error messages help debugging
5. **Consistency**: Same pattern across all services

---

## Migration Checklist

For each method returning `None`:

- [ ] Identify capability needed (file, metadata, LLM, etc.)
- [ ] Check if SOA API exists (Smart City service)
- [ ] Implement Tier 1: SOA API access
- [ ] Implement Tier 2: Platform Gateway access
- [ ] Implement Tier 3: Fail gracefully
- [ ] Update return type to structured response
- [ ] Add logging for each tier attempt
- [ ] Test with service available
- [ ] Test with service unavailable

---

## Next Steps

1. Review Phase 2 issues with updated pattern
2. Implement fixes using three-tier pattern
3. Test all fixes
4. Document any exceptions to the pattern

---

**Status**: ✅ Approach updated and ready for implementation
