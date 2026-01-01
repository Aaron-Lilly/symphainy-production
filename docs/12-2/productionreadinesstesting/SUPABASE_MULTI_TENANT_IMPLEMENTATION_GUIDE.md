# Supabase Multi-Tenant Implementation Guide

**Date:** December 1, 2025  
**Purpose:** Step-by-step guide for implementing multi-tenant architecture  
**Status:** Phase 1-4 Complete

---

## Overview

This guide documents the implementation of a secure, scalable multi-tenant architecture using Supabase. The implementation follows a phased approach:

- **Phase 1:** MVP Security Fixes (Server-side tenant creation)
- **Phase 2:** Database-Level Isolation (RLS policies)
- **Phase 3:** Enterprise Features (Multi-tenant users, admin features)
- **Phase 4:** User Documentation (What users should expect)

---

## Phase 1: MVP Security Fixes

### What Changed

1. **Tenant Management Tables Created**
   - `tenants` table for tenant/organization information
   - `user_tenants` junction table for user-tenant relationships

2. **Server-Side Tenant Creation**
   - Tenants are now created automatically during user registration
   - Tenant ID is assigned server-side (not client-side)
   - Users are automatically linked to their tenant

3. **Enhanced Token Validation**
   - Token validation now fetches tenant information from database
   - Tenant context is always validated and up-to-date

4. **Frontend Updates**
   - Removed client-side tenant ID generation
   - Tenant ID now comes from backend response

### Database Migrations

Run these migrations in order:

1. **001_create_tenant_management_tables.sql**
   - Creates `tenants` and `user_tenants` tables
   - Adds indexes and helper functions

2. **002_add_tenant_id_to_existing_tables.sql**
   - Adds `tenant_id` column to existing tables (files, audit_logs, sessions)

3. **003_backfill_tenant_data.sql**
   - Creates tenants for existing users
   - Links existing users to their tenants
   - Backfills tenant_id in existing data

### How to Run Migrations

**Option 1: Supabase Dashboard**
1. Go to Supabase Dashboard → SQL Editor
2. Copy and paste each migration file
3. Run each migration in order

**Option 2: Supabase CLI**
```bash
supabase db push
```

**Option 3: psql**
```bash
psql -h <host> -U <user> -d <database> -f 001_create_tenant_management_tables.sql
psql -h <host> -U <user> -d <database> -f 002_add_tenant_id_to_existing_tables.sql
psql -h <host> -U <user> -d <database> -f 003_backfill_tenant_data.sql
```

### Verification

After running migrations, verify:

```sql
-- Check tenants were created
SELECT COUNT(*) FROM public.tenants;

-- Check users are linked to tenants
SELECT COUNT(*) FROM public.user_tenants;

-- Check existing data has tenant_id
SELECT COUNT(*) FROM public.files WHERE tenant_id IS NOT NULL;
```

---

## Phase 2: Database-Level Isolation

### What Changed

1. **RLS Policies Enabled**
   - Row Level Security enabled on all tenant-scoped tables
   - Policies enforce tenant isolation at database level

2. **Security Policies**
   - Users can only see data from their tenants
   - Database automatically filters queries by tenant
   - Defense in depth: Application checks + RLS

### Database Migration

Run this migration:

**004_enable_rls_policies.sql**
- Enables RLS on all tenant-scoped tables
- Creates policies for tenant isolation

### Testing RLS

```sql
-- Test as different users
SET ROLE authenticated;
SET request.jwt.claim.sub = '<user_id>';

-- Try to query data
SELECT * FROM public.files;
-- Should only return files from user's tenant

-- Try to query other tenant's data
SELECT * FROM public.files WHERE tenant_id = '<other_tenant_id>';
-- Should return empty (RLS blocks it)
```

---

## Phase 3: Enterprise Features

### Multi-Tenant User Support

Users can now belong to multiple tenants:

```python
# Add user to additional tenant
await supabase_adapter.link_user_to_tenant(
    user_id=user_id,
    tenant_id=tenant_id,
    role="member",
    is_primary=False
)
```

### Tenant Switching

Users can switch between their tenants:

```python
# Get user's tenants
response = supabase.table("user_tenants").select(
    "tenant_id, role, tenants(name, type)"
).eq("user_id", user_id).execute()

# Switch primary tenant
await supabase_adapter.link_user_to_tenant(
    user_id=user_id,
    tenant_id=new_tenant_id,
    role=existing_role,
    is_primary=True
)
```

---

## Phase 4: User-Facing Changes

### What Users Should Expect

#### Registration Flow

**Before:**
- User registers → Account created
- Tenant ID generated client-side (insecure)

**After:**
- User registers → Account created
- Tenant automatically created server-side
- User automatically linked to tenant
- Tenant ID assigned securely

**User Experience:**
- ✅ No change to registration form
- ✅ Same email/password flow
- ✅ Automatic tenant creation (transparent to user)
- ✅ Faster registration (no additional steps)

#### Login Flow

**Before:**
- User logs in → Token validated
- Tenant ID from metadata (may be missing)

**After:**
- User logs in → Token validated
- Tenant ID fetched from database (always available)
- Tenant context validated

**User Experience:**
- ✅ No change to login form
- ✅ Same email/password flow
- ✅ More reliable tenant context
- ✅ Better security

#### Data Access

**Before:**
- Users could potentially access other users' data
- Relied on application-level checks only

**After:**
- Users can only see data from their tenant
- Database-level security (RLS) enforces isolation
- Defense in depth: Application + Database checks

**User Experience:**
- ✅ Better data security
- ✅ No change to user interface
- ✅ Transparent security improvements

### Migration for Existing Users

**Automatic:**
- Existing users automatically get tenants created
- Existing data automatically linked to tenants
- No action required from users

**Timeline:**
- Migration runs automatically during deployment
- Users may see brief delay on first login (tenant creation)
- Subsequent logins are normal speed

### What Users Don't Need to Do

- ❌ No need to re-register
- ❌ No need to update profile
- ❌ No need to change password
- ❌ No need to take any action

### What Users Will Notice

- ✅ More reliable login (better token validation)
- ✅ Better data security (transparent)
- ✅ No changes to user interface
- ✅ Same features, better security

---

## Developer Guide

### Creating a Tenant Manually

```python
# Create tenant
tenant_result = await supabase_adapter.create_tenant({
    "name": "My Organization",
    "slug": "my-org",
    "type": "organization",
    "owner_id": user_id,
    "status": "active"
})

# Link user to tenant
await supabase_adapter.link_user_to_tenant(
    user_id=user_id,
    tenant_id=tenant_result["tenant_id"],
    role="owner",
    is_primary=True
)
```

### Querying Tenant-Scoped Data

```python
# Always filter by tenant_id from SecurityContext
context = await auth_abstraction.validate_token(token)

# Query files for user's tenant
response = supabase.table("files").select("*").eq(
    "tenant_id", context.tenant_id
).execute()
```

### Adding Tenant Isolation to New Tables

1. **Add tenant_id column:**
```sql
ALTER TABLE public.new_table 
ADD COLUMN tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE;

CREATE INDEX idx_new_table_tenant_id ON public.new_table(tenant_id);
```

2. **Enable RLS:**
```sql
ALTER TABLE public.new_table ENABLE ROW LEVEL SECURITY;
```

3. **Create RLS policy:**
```sql
CREATE POLICY "Users can access new_table from their tenants"
    ON public.new_table
    FOR ALL
    USING (
        tenant_id IN (
            SELECT tenant_id 
            FROM public.user_tenants
            WHERE user_id = auth.uid()
        )
    );
```

---

## Troubleshooting

### Issue: User has no tenant_id

**Symptom:** `tenant_id` is None in SecurityContext

**Solution:**
1. Check if user exists in `user_tenants` table
2. If not, create tenant and link user:
```python
await auth_abstraction._create_tenant_for_user(user_id, "individual", "Default Tenant", email)
```

### Issue: RLS blocking legitimate access

**Symptom:** Users can't see their own data

**Solution:**
1. Verify user is in `user_tenants` table
2. Check RLS policies are correct
3. Verify `auth.uid()` matches user_id

### Issue: Migration fails

**Symptom:** SQL errors during migration

**Solution:**
1. Check if tables already exist
2. Run migrations in order
3. Check Supabase service key has proper permissions

---

## Security Best Practices

### ✅ DO

- Always extract tenant_id from validated token
- Always filter queries by tenant_id
- Use RLS as defense in depth
- Validate tenant_id exists before operations

### ❌ DON'T

- Never trust client-provided tenant_id
- Never skip tenant_id validation
- Never disable RLS for "performance"
- Never expose service key to frontend

---

## Next Steps

1. **Run Migrations:** Execute SQL migrations in order
2. **Test Registration:** Create new user, verify tenant created
3. **Test Login:** Login existing user, verify tenant context
4. **Test RLS:** Verify users can't access other tenants' data
5. **Monitor:** Watch for any tenant-related errors

---

## Support

For issues or questions:
1. Check this guide first
2. Review migration logs
3. Check Supabase dashboard for errors
4. Review application logs for tenant-related errors

---

**Status:** ✅ Implementation Complete  
**Last Updated:** December 1, 2025

