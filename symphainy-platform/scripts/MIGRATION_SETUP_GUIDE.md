# Supabase Migration Setup Guide

**Purpose:** Set up your environment to run migrations automatically

---

## Quick Start

### Option 1: Using psql (Recommended - Most Reliable)

**Step 1: Install PostgreSQL Client**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql-client

# macOS
brew install postgresql

# Verify installation
psql --version
```

**Step 2: Get Database Connection String**

1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Go to: **Settings** → **Database**
4. Scroll to **Connection string**
5. Select **URI** tab
6. Copy the connection string (looks like: `postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres`)

**Step 3: Set Environment Variable**

```bash
# Add to your .env.secrets file or export:
export DATABASE_URL="postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
```

**Step 4: Run Migrations**

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
python3 scripts/run_supabase_migrations.py
```

---

### Option 2: Using Supabase CLI

**Step 1: Install Supabase CLI**

```bash
# macOS
brew install supabase/tap/supabase

# Linux
# Download from: https://github.com/supabase/cli/releases

# Verify installation
supabase --version
```

**Step 2: Login to Supabase**

```bash
supabase login
```

**Step 3: Link Your Project**

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
supabase link --project-ref YOUR_PROJECT_REF
```

(Get project ref from your Supabase URL: `https://YOUR_PROJECT_REF.supabase.co`)

**Step 4: Run Migrations**

```bash
python3 scripts/run_supabase_migrations.py
```

---

### Option 3: Manual (Fallback)

If automated methods don't work:

1. Open each migration file in order (001, 002, 003, 004)
2. Copy SQL content
3. Go to Supabase Dashboard → SQL Editor
4. Paste SQL
5. Click "Run"

---

## Migration Script Usage

### Dry Run (See What Would Happen)

```bash
python3 scripts/run_supabase_migrations.py --dry-run
```

### Run All Migrations

```bash
python3 scripts/run_supabase_migrations.py
```

### Run Specific Migration

```bash
python3 scripts/run_supabase_migrations.py --migration 001
```

### Skip Confirmation (For Automation)

```bash
python3 scripts/run_supabase_migrations.py --skip-confirm
```

---

## Troubleshooting

### Issue: "psql not found"

**Solution:**
```bash
# Install PostgreSQL client (see Option 1 above)
sudo apt-get install postgresql-client  # Ubuntu/Debian
brew install postgresql                  # macOS
```

### Issue: "DATABASE_URL not found"

**Solution:**
1. Get connection string from Supabase Dashboard
2. Set environment variable:
   ```bash
   export DATABASE_URL="postgresql://..."
   ```
   Or add to `.env.secrets`:
   ```
   DATABASE_URL=postgresql://...
   ```

### Issue: "Connection refused" or "Authentication failed"

**Solution:**
1. Verify connection string is correct
2. Check password is correct
3. Ensure IP is allowed in Supabase Dashboard:
   - Settings → Database → Connection Pooling
   - Add your IP if needed

### Issue: "Migration failed"

**Solution:**
1. Check error message for specific issue
2. Verify migration SQL is valid
3. Check if tables already exist (migrations use `IF NOT EXISTS`)
4. Review Supabase Dashboard → Logs for detailed errors

---

## Migration Files

The script will run these migrations in order:

1. **001_create_tenant_management_tables.sql**
   - Creates `tenants` and `user_tenants` tables
   - Safe to run multiple times (uses `IF NOT EXISTS`)

2. **002_add_tenant_id_to_existing_tables.sql**
   - Adds `tenant_id` columns to existing tables
   - Safe to run multiple times (checks if column exists)

3. **003_backfill_tenant_data.sql**
   - Creates tenants for existing users
   - Links users to tenants
   - Backfills tenant_id in existing data
   - Safe to run multiple times (uses `ON CONFLICT DO NOTHING`)

4. **004_enable_rls_policies.sql**
   - Enables RLS on all tenant-scoped tables
   - Creates security policies
   - Safe to run multiple times (uses `DROP POLICY IF EXISTS`)

---

## Safety Features

✅ **Idempotent Migrations:** All migrations can be run multiple times safely  
✅ **Dry Run Mode:** Test before executing  
✅ **Confirmation Prompts:** Prevents accidental execution  
✅ **Error Handling:** Stops on error, shows clear messages  
✅ **Rollback Info:** Instructions provided if migration fails  

---

## Verification

After running migrations, verify:

```sql
-- Check tenants table exists
SELECT COUNT(*) FROM public.tenants;

-- Check user_tenants table exists
SELECT COUNT(*) FROM public.user_tenants;

-- Check RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('tenants', 'user_tenants', 'files');
```

---

## Next Steps

After migrations complete:

1. ✅ Test registration (should create tenant automatically)
2. ✅ Test login (should load tenant context)
3. ✅ Test file upload (should set tenant_id)
4. ✅ Test tenant isolation (users can't see other tenants' data)

---

**Questions?** Check the main implementation guide or review migration files for details.






