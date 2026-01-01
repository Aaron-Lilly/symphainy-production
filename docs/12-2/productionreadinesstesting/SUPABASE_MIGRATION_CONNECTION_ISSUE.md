# Supabase Migration Connection Issue

**Date:** December 1, 2025  
**Issue:** Unable to connect to Supabase database for migrations

---

## Problem Summary

The migration script is having trouble connecting to Supabase using the DATABASE_URL. We've tried:

1. **Pooled Connection (port 6543)**: Error "Tenant or user not found"
2. **Direct Connection (port 5432)**: Error "Network is unreachable"

---

## Recommended Solution: Use Supabase Dashboard SQL Editor

Since automated connection is having issues, the **most reliable method** is to run migrations via the Supabase Dashboard SQL Editor:

### Steps:

1. **Go to Supabase Dashboard**
   - https://supabase.com/dashboard/project/rmymvrifwvqpeffmxkwi

2. **Open SQL Editor**
   - Click **SQL Editor** in the left sidebar
   - Click **New query**

3. **Run Each Migration File**

   Copy and paste the SQL from each migration file in order:

   **Migration 1:** `001_create_tenant_management_tables.sql`
   - Copy the entire SQL content
   - Paste into SQL Editor
   - Click **Run** (or press Ctrl+Enter)
   - Verify success

   **Migration 2:** `002_add_tenant_id_to_existing_tables.sql`
   - Repeat above steps

   **Migration 3:** `003_backfill_tenant_data.sql`
   - Repeat above steps

   **Migration 4:** `004_enable_rls_policies.sql`
   - Repeat above steps

---

## Alternative: Fix Connection String

If you want to use the automated script, we need to verify the exact connection string format from Supabase Dashboard:

1. **Go to:** Settings → Database → Connection string
2. **Copy the exact URI** (don't modify it)
3. **Verify:**
   - Username format (should be `postgres.[ref]` for pooled)
   - Password is URL-encoded if it contains special characters
   - Hostname and port are correct

---

## Migration Files Location

All migration files are located at:
```
symphainy-platform/foundations/public_works_foundation/sql/migrations/
```

Files:
- `001_create_tenant_management_tables.sql`
- `002_add_tenant_id_to_existing_tables.sql`
- `003_backfill_tenant_data.sql`
- `004_enable_rls_policies.sql`

---

## Next Steps

**Option 1 (Recommended):** Use Supabase Dashboard SQL Editor
- Most reliable
- No connection issues
- Visual feedback

**Option 2:** Fix DATABASE_URL connection string
- Get exact connection string from Supabase Dashboard
- Verify password encoding
- Test connection manually first

---

**Note:** The connection issues might be due to:
- Network restrictions (firewall, VPN)
- Incorrect connection string format
- Password encoding issues
- Supabase project settings (IP allowlisting)


