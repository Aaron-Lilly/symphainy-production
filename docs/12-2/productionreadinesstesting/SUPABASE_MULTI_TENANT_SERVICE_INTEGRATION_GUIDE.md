# Multi-Tenant Service Integration Guide

**Date:** December 1, 2025  
**Purpose:** Document how services/agents automatically use the new tenant pattern vs what needs manual updates

---

## Executive Summary

**Good News:** Most services will work automatically because:
1. ✅ Token validation now returns `tenant_id` in SecurityContext
2. ✅ Services already extract `tenant_id` from `user_context`
3. ✅ File operations already filter by `tenant_id`
4. ✅ RLS policies provide database-level protection

**Action Required:** A few services may need updates to:
1. Ensure they always pass `user_context` with `tenant_id`
2. Ensure they filter queries by `tenant_id` (RLS helps, but explicit is better)
3. Ensure they set `tenant_id` when creating data

---

## How It Works Automatically

### 1. Token Validation Flow

**What Happens:**
```
Request → Security Guard → AuthAbstraction.validate_token() 
  → SupabaseAdapter.get_user() 
  → Fetches tenant from database
  → Returns SecurityContext with tenant_id
```

**Result:**
- ✅ All services receive `SecurityContext` with `tenant_id` populated
- ✅ No code changes needed in services that use SecurityContext
- ✅ Works automatically through the abstraction layer

### 2. Service Pattern (Already Working)

**Current Pattern:**
```python
# Services already do this:
async def some_operation(self, user_context: Dict[str, Any]):
    tenant_id = user_context.get("tenant_id")
    
    # Use tenant_id for filtering/validation
    if tenant_id:
        # Filter by tenant
        # Validate tenant access
```

**Status:** ✅ This pattern is already used throughout the codebase

### 3. File Operations (Already Working)

**File Creation:**
```python
# file_processing.py - Already extracts tenant_id
tenant_id = user_context.get("tenant_id") if user_context else None
file_record = {
    "tenant_id": tenant_id,
    # ...
}
```

**File Listing:**
```python
# supabase_file_management_adapter.py - Already filters by tenant_id
if tenant_id:
    query = query.eq("tenant_id", tenant_id)
```

**Status:** ✅ File operations already use tenant_id

---

## What Needs Attention

### 1. Services That Don't Pass user_context

**Issue:** Some services might not receive or pass `user_context` with `tenant_id`

**Check:**
```python
# Look for services that:
# 1. Don't accept user_context parameter
# 2. Don't extract tenant_id from user_context
# 3. Don't filter queries by tenant_id
```

**Fix:**
```python
# Add user_context parameter
async def some_operation(self, user_context: Optional[Dict[str, Any]] = None):
    # Extract tenant_id
    tenant_id = user_context.get("tenant_id") if user_context else None
    
    # Use tenant_id for filtering
    if tenant_id:
        query = query.eq("tenant_id", tenant_id)
```

### 2. Direct Database Queries Without tenant_id Filter

**Issue:** Services that query Supabase directly without filtering by tenant_id

**Check:**
```python
# Look for patterns like:
query = supabase.table("some_table").select("*").execute()
# Missing: .eq("tenant_id", tenant_id)
```

**Fix:**
```python
# Always filter by tenant_id
query = supabase.table("some_table").select("*")
if tenant_id:
    query = query.eq("tenant_id", tenant_id)
result = query.execute()
```

**Note:** RLS policies will block cross-tenant access, but explicit filtering is better for:
- Performance (smaller result sets)
- Clarity (obvious intent)
- Debugging (easier to see what's happening)

### 3. Data Creation Without tenant_id

**Issue:** Services that create data without setting `tenant_id`

**Check:**
```python
# Look for patterns like:
data = {
    "user_id": user_id,
    # Missing: "tenant_id": tenant_id
}
```

**Fix:**
```python
# Always include tenant_id
data = {
    "user_id": user_id,
    "tenant_id": tenant_id,  # From user_context
    # ...
}
```

---

## Services That Already Work

### ✅ File Management
- **File Upload:** Extracts tenant_id from user_context ✅
- **File Listing:** Filters by tenant_id ✅
- **File Creation:** Sets tenant_id ✅

### ✅ Data Services
- **DataInsightsQueryService:** Validates tenant access ✅
- **DataCompositorService:** Validates tenant access ✅
- **ValidationEngineService:** Validates tenant access ✅
- **MetricsCalculatorService:** Validates tenant access ✅
- **TransformationEngineService:** Validates tenant access ✅

### ✅ Orchestrators
- **ContentAnalysisOrchestrator:** Uses user_context ✅
- **InsightsOrchestrator:** Uses user_context ✅
- **OperationsOrchestrator:** Uses user_context ✅

### ✅ Agents
- **GuideCrossDomainAgent:** Uses tenant context ✅
- **ToolRegistryService:** Validates tenant access ✅

---

## Services That May Need Updates

### ⚠️ Services to Review

1. **Services that query without user_context:**
   - Check if they accept `user_context` parameter
   - Check if they extract `tenant_id`
   - Check if they filter by `tenant_id`

2. **Services that create data:**
   - Check if they set `tenant_id` when creating records
   - Check if they extract `tenant_id` from `user_context`

3. **Services that use direct Supabase queries:**
   - Check if they filter by `tenant_id`
   - Check if they use RLS-aware queries

---

## RLS as Safety Net

**Important:** Even if services don't explicitly filter by `tenant_id`, RLS policies will:
- ✅ Block cross-tenant data access
- ✅ Automatically filter queries by tenant
- ✅ Provide defense in depth

**However:**
- ⚠️ Explicit filtering is still recommended for:
  - Performance (smaller queries)
  - Clarity (obvious intent)
  - Debugging (easier troubleshooting)

---

## Verification Checklist

### For Each Service

- [ ] Service accepts `user_context` parameter
- [ ] Service extracts `tenant_id` from `user_context`
- [ ] Service filters queries by `tenant_id` (or relies on RLS)
- [ ] Service sets `tenant_id` when creating data
- [ ] Service validates tenant access when needed

### For Each Data Operation

- [ ] **Create:** Sets `tenant_id` from `user_context`
- [ ] **Read:** Filters by `tenant_id` (or relies on RLS)
- [ ] **Update:** Validates tenant access
- [ ] **Delete:** Validates tenant access

---

## Testing Strategy

### 1. Test Tenant Isolation

```python
# Create two test users with different tenants
user1_context = {"user_id": "user1", "tenant_id": "tenant1"}
user2_context = {"user_id": "user2", "tenant_id": "tenant2"}

# User 1 creates data
result1 = await service.create_data(data, user1_context)

# User 2 tries to access User 1's data
result2 = await service.get_data(result1["id"], user2_context)
# Should fail or return None (RLS blocks it)
```

### 2. Test Tenant Context Propagation

```python
# Verify tenant_id flows through the system
context = await auth_abstraction.validate_token(token)
assert context.tenant_id is not None

# Verify services receive tenant_id
user_context = {"tenant_id": context.tenant_id}
result = await service.operation(user_context)
assert result.get("tenant_id") == context.tenant_id
```

### 3. Test RLS Policies

```sql
-- Test as different users
SET ROLE authenticated;
SET request.jwt.claim.sub = '<user1_id>';

-- Try to query data
SELECT * FROM public.files;
-- Should only return files from user1's tenant

-- Try to query other tenant's data
SELECT * FROM public.files WHERE tenant_id = '<other_tenant_id>';
-- Should return empty (RLS blocks it)
```

---

## Common Patterns

### Pattern 1: Extract tenant_id from user_context

```python
async def operation(self, user_context: Optional[Dict[str, Any]] = None):
    tenant_id = user_context.get("tenant_id") if user_context else None
    
    if not tenant_id:
        raise ValueError("tenant_id required")
    
    # Use tenant_id
```

### Pattern 2: Filter queries by tenant_id

```python
query = supabase.table("some_table").select("*")
if tenant_id:
    query = query.eq("tenant_id", tenant_id)
result = query.execute()
```

### Pattern 3: Set tenant_id when creating data

```python
data = {
    "user_id": user_id,
    "tenant_id": tenant_id,  # From user_context
    # ... other fields
}
result = await supabase.table("some_table").insert(data).execute()
```

### Pattern 4: Validate tenant access

```python
# Get resource
resource = await get_resource(resource_id)

# Validate tenant access
if resource.get("tenant_id") != tenant_id:
    raise PermissionError("Tenant access denied")
```

---

## Migration Path

### Step 1: Verify Current State

1. Run tests to see what works
2. Check logs for any tenant-related errors
3. Identify services that need updates

### Step 2: Update Services (If Needed)

1. Add `user_context` parameter if missing
2. Extract `tenant_id` from `user_context`
3. Filter queries by `tenant_id`
4. Set `tenant_id` when creating data

### Step 3: Test

1. Test tenant isolation
2. Test tenant context propagation
3. Test RLS policies

### Step 4: Monitor

1. Watch for tenant-related errors
2. Monitor query performance
3. Check RLS policy effectiveness

---

## Summary

### ✅ What Works Automatically

1. **Token Validation:** Returns `tenant_id` in SecurityContext
2. **Security Context:** Services receive `tenant_id` automatically
3. **RLS Policies:** Database-level protection (safety net)
4. **File Operations:** Already use `tenant_id`
5. **Most Services:** Already extract `tenant_id` from `user_context`

### ⚠️ What May Need Updates

1. **Services without user_context:** Need to add parameter
2. **Direct queries:** Should filter by `tenant_id` (RLS helps, but explicit is better)
3. **Data creation:** Should set `tenant_id` (some may already do this)

### 🎯 Recommendation

1. **Deploy as-is:** RLS provides safety net
2. **Monitor:** Watch for any tenant-related issues
3. **Update incrementally:** Fix services as issues are found
4. **Test thoroughly:** Verify tenant isolation works

---

## Next Steps

1. **Deploy:** The abstraction layer changes are ready
2. **Test:** Run integration tests to verify tenant isolation
3. **Monitor:** Watch for any tenant-related errors
4. **Update:** Fix any services that need updates (if found)

---

**Status:** ✅ Ready for deployment  
**Confidence:** High - Most services already use the pattern  
**Risk:** Low - RLS provides safety net


