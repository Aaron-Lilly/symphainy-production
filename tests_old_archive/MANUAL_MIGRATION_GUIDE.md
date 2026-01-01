# Manual Migration Guide for Test Supabase

**Date:** 2025-12-04  
**Status:** 📋 **MANUAL MIGRATION REQUIRED**

---

## 🎯 **Why Manual Migration?**

The automated migration script requires direct database access, which may be blocked by network/firewall settings. The **Supabase Dashboard SQL Editor** is the most reliable method.

---

## 📋 **Step-by-Step: Run Migrations via Supabase Dashboard**

### **Step 1: Open Supabase Dashboard**

1. Go to: https://supabase.com/dashboard
2. Select your **test project**: `eocztpcvzcdqgygxlnqg`
3. Navigate to: **SQL Editor** (left sidebar)

### **Step 2: Run Each Migration**

Run each migration file in order:

#### **Migration 1: Create Tenant Management Tables**

1. Click **"New query"** in SQL Editor
2. Copy the contents of: `symphainy-platform/foundations/public_works_foundation/sql/migrations/001_create_tenant_management_tables.sql`
3. Paste into SQL Editor
4. Click **"Run"** (or press `Ctrl+Enter`)
5. Verify success (should see "Success. No rows returned")

#### **Migration 2: Add Tenant ID to Existing Tables**

1. Click **"New query"**
2. Copy contents of: `002_add_tenant_id_to_existing_tables.sql`
3. Paste and run

#### **Migration 3: Backfill Tenant Data**

1. Click **"New query"**
2. Copy contents of: `003_backfill_tenant_data.sql`
3. Paste and run

#### **Migration 4: Enable RLS Policies**

1. Click **"New query"**
2. Copy contents of: `004_enable_rls_policies.sql`
3. Paste and run

---

## ✅ **Verify Migrations**

After running all migrations, verify:

1. Go to: **Table Editor** (left sidebar)
2. Check that these tables exist:
   - `tenants`
   - `tenant_users`
   - `tenant_settings`
   - (And any other tables from your schema)

3. Go to: **Authentication** → **Policies**
4. Check that RLS policies are enabled

---

## 🚀 **Alternative: Use Supabase Python Client**

If you prefer to automate, you can use the Supabase Python client:

```python
from supabase import create_client, Client

# Initialize Supabase client
url = "https://eocztpcvzcdqgygxlnqg.supabase.co"
key = "sb_secret_8LSpSDeZoXlFEJiH1wM4yg_2iTEzbgR"  # Service key
supabase: Client = create_client(url, key)

# Read and execute migration
with open("migration.sql", "r") as f:
    sql = f.read()
    result = supabase.rpc("exec_sql", {"sql": sql}).execute()
```

**Note:** This requires the `exec_sql` function to be available, which may not be enabled by default.

---

## 📝 **Migration Files Location**

All migration files are located at:
```
symphainy-platform/foundations/public_works_foundation/sql/migrations/
```

Files to run in order:
1. `001_create_tenant_management_tables.sql`
2. `002_add_tenant_id_to_existing_tables.sql`
3. `003_backfill_tenant_data.sql`
4. `004_enable_rls_policies.sql`

---

## ✅ **After Migrations Complete**

Once all migrations are run:

1. ✅ Test Supabase project is ready
2. ✅ Schema matches production
3. ✅ RLS policies enabled
4. ✅ Ready for testing

**Next:** Start backend with `TEST_MODE=true` and run tests!

---

**Status:** ⏳ **WAITING FOR MANUAL MIGRATION**



