# Tenant Relationship Review & Fix Plan

**Date:** December 14, 2025  
**Status:** 🔍 Review Complete - Implementation Plan Ready  
**Issue:** Users can exist without tenant relationships, causing empty permissions

---

## 🔍 **Current State Analysis**

### ✅ **What Works**

1. **`register_user()` in `auth_abstraction.py`** ✅
   - Creates user → Creates tenant → Links user to tenant
   - Sets role as "owner" with `is_primary=True`
   - Updates user_metadata with tenant_id
   - **Location:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py:332-428`

2. **Database Schema** ✅
   - `user_tenants` table exists with proper structure
   - Indexes for efficient lookups
   - RLS policies configured
   - **Location:** `foundations/public_works_foundation/sql/migrations/001_create_tenant_management_tables.sql`

3. **Adapter Methods** ✅
   - `SupabaseAdapter.create_tenant()` - Creates tenant
   - `SupabaseAdapter.link_user_to_tenant()` - Links user to tenant
   - **Location:** `foundations/public_works_foundation/infrastructure_adapters/supabase_adapter.py:667-739`

### ❌ **What's Missing**

1. **`authenticate_user()` (Login)** ❌
   - Does NOT create tenant if missing
   - Only reads from user_metadata (which may be empty)
   - **Location:** `auth_abstraction.py:55-95`
   - **Impact:** Users who logged in before tenant system existed have no tenant

2. **`validate_token()` (JWKS Validation)** ❌
   - Does NOT create tenant if missing
   - Only logs warning: "User has no tenant_id - creating default tenant" (but doesn't actually create it)
   - **Location:** `auth_abstraction.py:214-217`
   - **Impact:** Token validation fails to populate permissions for users without tenants

3. **`setup_test_users.py`** ❌
   - Creates users but does NOT create tenant relationships
   - **Location:** `scripts/setup_test_users.py:60-161`
   - **Impact:** Test users have no tenants → permissions are empty

4. **Backfill Migration** ⚠️
   - Migration `003_backfill_tenant_data.sql` exists but may not have been run
   - **Location:** `foundations/public_works_foundation/sql/migrations/003_backfill_tenant_data.sql`
   - **Impact:** Existing users may not have tenant relationships

---

## 🎯 **Root Cause**

**The Problem:**
- Users can exist in `auth.users` without records in `user_tenants`
- When `_get_user_tenant_info()` queries `user_tenants` and finds nothing, it returns empty dict
- Empty dict → empty permissions → permission checks fail

**Why It Happens:**
1. Users created before tenant system was implemented
2. Users created via direct Supabase admin API (bypassing `register_user()`)
3. Test users created via `setup_test_users.py` (doesn't create tenants)
4. Login/validation doesn't auto-fix missing tenant relationships

---

## 🔧 **Implementation Plan**

### **Phase 1: Auto-Create Tenant on Login/Validation** (High Priority)

**Goal:** Automatically create tenant relationship if user doesn't have one during login or token validation.

#### **1.1 Update `authenticate_user()` in `auth_abstraction.py`**

**Location:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py:55-95`

**Changes:**
```python
async def authenticate_user(self, credentials: Dict[str, Any]) -> SecurityContext:
    """Authenticate user using real Supabase adapter."""
    try:
        # ... existing authentication code ...
        
        user_id = user_data.get("id")
        tenant_id = user_data.get("user_metadata", {}).get("tenant_id")
        
        # ✅ NEW: If no tenant_id, check user_tenants table
        if not tenant_id:
            tenant_info = await self.supabase._get_user_tenant_info(user_id)
            tenant_id = tenant_info.get("tenant_id")
        
        # ✅ NEW: If still no tenant, create one automatically
        if not tenant_id:
            self.logger.warning(f"⚠️ User {user_id} has no tenant - creating default tenant")
            tenant_result = await self._create_tenant_for_user(
                user_id=user_id,
                tenant_type="individual",
                tenant_name=f"Tenant for {user_data.get('email', user_id)}",
                email=user_data.get("email", "")
            )
            
            if tenant_result.get("success"):
                tenant_id = tenant_result.get("tenant_id")
                # Link user to tenant
                await self.supabase.link_user_to_tenant(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    role="owner",
                    is_primary=True
                )
                self.logger.info(f"✅ Created and linked tenant for user {user_id}")
            else:
                self.logger.error(f"❌ Failed to create tenant for user {user_id}")
        
        # Get full tenant info (with permissions)
        tenant_info = await self.supabase._get_user_tenant_info(user_id)
        roles = tenant_info.get("roles", [])
        permissions = tenant_info.get("permissions", [])
        
        # ... rest of method ...
```

#### **1.2 Update `validate_token()` in `auth_abstraction.py`**

**Location:** `foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py:170-227`

**Changes:**
```python
async def validate_token(self, token: str) -> SecurityContext:
    """Validate token using Supabase JWKS local verification."""
    try:
        # ... existing validation code ...
        
        user_id = user_data.get("id")
        tenant_id = user_data.get("tenant_id")
        
        # ✅ NEW: If no tenant_id, check user_tenants table
        if not tenant_id:
            tenant_info = await self.supabase._get_user_tenant_info(user_id)
            tenant_id = tenant_info.get("tenant_id")
        
        # ✅ NEW: If still no tenant, create one automatically
        if not tenant_id:
            self.logger.warning(f"⚠️ User {user_id} has no tenant - creating default tenant")
            tenant_result = await self._create_tenant_for_user(
                user_id=user_id,
                tenant_type="individual",
                tenant_name=f"Tenant for {user_data.get('email', user_id)}",
                email=user_data.get("email", "")
            )
            
            if tenant_result.get("success"):
                tenant_id = tenant_result.get("tenant_id")
                # Link user to tenant
                await self.supabase.link_user_to_tenant(
                    user_id=user_id,
                    tenant_id=tenant_id,
                    role="owner",
                    is_primary=True
                )
                self.logger.info(f"✅ Created and linked tenant for user {user_id}")
        
        # Get full tenant info (with permissions)
        tenant_info = await self.supabase._get_user_tenant_info(user_id)
        roles = tenant_info.get("roles", [])
        permissions = tenant_info.get("permissions", [])
        
        # ... rest of method ...
```

**Note:** We need to make `_get_user_tenant_info()` accessible. Currently it's a private method. Options:
- Make it public: `get_user_tenant_info()`
- Or call it via adapter: `await self.supabase._get_user_tenant_info(user_id)` (if we make it public)

---

### **Phase 2: Fix Test User Setup** (High Priority)

#### **2.1 Update `setup_test_users.py`**

**Location:** `scripts/setup_test_users.py`

**Changes:**
```python
def create_and_confirm_user(
    supabase_service: Client,
    email: str,
    password: str,
    name: str
) -> Dict:
    """Create a user and confirm them immediately using admin API."""
    # ... existing user creation code ...
    
    if response.user:
        user_id = response.user.id
        
        # ✅ NEW: Create tenant for user
        print(f"   📋 Creating tenant for user...")
        try:
            # Create tenant
            tenant_data = {
                "name": f"Tenant for {name}",
                "slug": f"tenant-{user_id[:8]}-{uuid.uuid4().hex[:8]}",
                "type": "individual",
                "owner_id": user_id,
                "status": "active"
            }
            tenant_response = supabase_service.table("tenants").insert(tenant_data).execute()
            
            if tenant_response.data:
                tenant_id = tenant_response.data[0]["id"]
                print(f"   ✅ Tenant created: {tenant_id}")
                
                # Link user to tenant
                link_data = {
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "role": "owner",
                    "is_primary": True
                }
                link_response = supabase_service.table("user_tenants").insert(link_data).execute()
                
                if link_response.data:
                    print(f"   ✅ User linked to tenant")
                else:
                    print(f"   ⚠️  Failed to link user to tenant")
            else:
                print(f"   ⚠️  Failed to create tenant")
        except Exception as e:
            print(f"   ⚠️  Error creating tenant: {e}")
            # Continue anyway - user is created
        
        # ... rest of method ...
```

---

### **Phase 3: Backfill Existing Users** (Medium Priority)

#### **3.1 Create Backfill Script**

**Location:** `scripts/backfill_user_tenants.py`

**Purpose:** One-time script to create tenant relationships for all existing users who don't have one.

**Implementation:**
- Query all users in `auth.users`
- For each user without a `user_tenants` record:
  - Create tenant
  - Link user to tenant with role="owner", is_primary=True
- Log results

---

### **Phase 4: Make `_get_user_tenant_info()` Public** (Required for Phase 1)

#### **4.1 Update `SupabaseAdapter`**

**Location:** `foundations/public_works_foundation/infrastructure_adapters/supabase_adapter.py:485-545`

**Changes:**
- Rename `_get_user_tenant_info()` → `get_user_tenant_info()` (make it public)
- Or keep private but add public wrapper method

---

## 📋 **Implementation Checklist**

### **Phase 1: Auto-Create Tenant**
- [ ] Make `_get_user_tenant_info()` accessible (public method or wrapper)
- [ ] Update `authenticate_user()` to auto-create tenant if missing
- [ ] Update `validate_token()` to auto-create tenant if missing
- [ ] Add unit tests for auto-creation logic
- [ ] Test with existing user without tenant

### **Phase 2: Fix Test Setup**
- [ ] Update `setup_test_users.py` to create tenant relationships
- [ ] Test script creates users with tenants
- [ ] Verify test users have permissions

### **Phase 3: Backfill**
- [ ] Create `backfill_user_tenants.py` script
- [ ] Run backfill on existing users
- [ ] Verify all users have tenant relationships

### **Phase 4: Testing**
- [ ] Test login with user without tenant (should auto-create)
- [ ] Test token validation with user without tenant (should auto-create)
- [ ] Test registration (should still work as before)
- [ ] Test E2E file upload (should now have permissions)
- [ ] Verify permissions are populated correctly

---

## 🎯 **Success Criteria**

1. ✅ All users have tenant relationships (either from registration or auto-created)
2. ✅ Login auto-creates tenant if missing
3. ✅ Token validation auto-creates tenant if missing
4. ✅ Test users have tenant relationships
5. ✅ Permissions are populated correctly
6. ✅ E2E file upload test passes

---

## 🔄 **Migration Strategy**

1. **Immediate:** Implement Phase 1 (auto-create on login/validation)
   - Fixes the issue for all future logins/validations
   - No data migration needed

2. **Short-term:** Implement Phase 2 (fix test setup)
   - Ensures new test users have tenants
   - Re-run setup script for existing test users

3. **Medium-term:** Run Phase 3 (backfill)
   - One-time fix for all existing users
   - Can be run manually or scheduled

---

## 📝 **Notes**

- **Performance:** Auto-creation adds one database write per user (first time only)
- **Idempotency:** Auto-creation checks for existing tenant before creating (safe to call multiple times)
- **Error Handling:** If tenant creation fails, log error but don't block authentication (graceful degradation)
- **Role Assignment:** Auto-created tenants assign "owner" role (full permissions)

---

**Last Updated:** December 14, 2025  
**Next Action:** Implement Phase 1 - Auto-create tenant on login/validation



