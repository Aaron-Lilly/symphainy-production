# Supabase Migration Runner - Complete Guide

**Date:** December 1, 2025  
**Purpose:** Run Supabase migrations automatically from command line

---

## Overview

The migration runner script (`scripts/run_supabase_migrations.py`) provides an automated, safe way to run SQL migrations against your Supabase database without using the web interface.

---

## Prerequisites

### Required

1. **Database Connection String**
   - Get from: Supabase Dashboard → Settings → Database → Connection string → URI
   - Format: `postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres`

2. **Python Dependencies**
   - `psycopg2-binary` (already installed ✅)
   - Or `psql` command-line tool
   - Or Supabase CLI

### Optional

- Supabase CLI (alternative method)
- psql (alternative method)

---

## Quick Start

### 1. Set Database Connection

```bash
export DATABASE_URL="postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
```

Or add to `.env.secrets`:
```
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

### 2. Run Migrations

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Test first (dry run)
python3 scripts/run_supabase_migrations.py --dry-run

# Run for real
python3 scripts/run_supabase_migrations.py
```

---

## How It Works

### Method Priority

The script tries methods in this order:

1. **psycopg2** (Python PostgreSQL adapter) - ✅ **Recommended**
   - Most reliable
   - Already installed
   - Direct database connection

2. **psql** (PostgreSQL command-line tool)
   - Reliable
   - Requires installation
   - Direct database connection

3. **Supabase CLI**
   - Requires setup (login, link project)
   - Uses Supabase API

4. **Manual Instructions**
   - If all automated methods fail
   - Provides copy-paste instructions

---

## Usage Examples

### Dry Run (See What Would Happen)

```bash
python3 scripts/run_supabase_migrations.py --dry-run
```

**Output:**
- Shows which migrations would run
- Shows SQL preview
- Doesn't modify database

### Run All Migrations

```bash
python3 scripts/run_supabase_migrations.py
```

**Process:**
1. Lists all migration files
2. Asks for confirmation
3. Runs each migration in order
4. Shows progress and results
5. Stops on error (with option to continue)

### Run Specific Migration

```bash
python3 scripts/run_supabase_migrations.py --migration 001
```

**Use Case:** Re-run a specific migration if it failed

### Skip Confirmation (For Automation)

```bash
python3 scripts/run_supabase_migrations.py --skip-confirm
```

**Use Case:** CI/CD pipelines, automated scripts

---

## Migration Files

The script runs these migrations in order:

1. **001_create_tenant_management_tables.sql**
   - Creates `tenants` table
   - Creates `user_tenants` junction table
   - Adds indexes and helper functions
   - **Safe to run multiple times** (uses `IF NOT EXISTS`)

2. **002_add_tenant_id_to_existing_tables.sql**
   - Adds `tenant_id` column to `files` table
   - Adds `tenant_id` column to `audit_logs` table
   - Adds `tenant_id` column to `sessions` table
   - **Safe to run multiple times** (checks if column exists)

3. **003_backfill_tenant_data.sql**
   - Creates tenants for existing users
   - Links users to tenants
   - Backfills `tenant_id` in existing data
   - **Safe to run multiple times** (uses `ON CONFLICT DO NOTHING`)

4. **004_enable_rls_policies.sql**
   - Enables RLS on all tenant-scoped tables
   - Creates security policies
   - **Safe to run multiple times** (uses `DROP POLICY IF EXISTS`)

---

## Safety Features

### ✅ Idempotent Migrations

All migrations can be run multiple times safely:
- Use `IF NOT EXISTS` for tables
- Check for existing columns before adding
- Use `ON CONFLICT DO NOTHING` for inserts
- Use `DROP POLICY IF EXISTS` for policies

### ✅ Confirmation Prompts

- Asks before running migrations
- Shows project information
- Can skip with `--skip-confirm`

### ✅ Error Handling

- Stops on error
- Shows clear error messages
- Option to continue with next migration
- Provides rollback instructions

### ✅ Dry Run Mode

- Test before executing
- See what would happen
- No database changes

---

## Troubleshooting

### Issue: "DATABASE_URL not found"

**Solution:**
1. Get connection string from Supabase Dashboard
2. Set environment variable:
   ```bash
   export DATABASE_URL="postgresql://..."
   ```
3. Or add to `.env.secrets` file

### Issue: "psycopg2 not installed"

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue: "Connection refused" or "Authentication failed"

**Solutions:**
1. Verify connection string is correct
2. Check password is correct
3. Ensure IP is allowed:
   - Supabase Dashboard → Settings → Database
   - Check connection pooling settings

### Issue: "Migration failed"

**Solutions:**
1. Check error message for specific issue
2. Verify SQL is valid (check migration file)
3. Check if tables already exist
4. Review Supabase Dashboard → Logs

### Issue: "Table already exists"

**Status:** ✅ This is OK!
- Migrations use `IF NOT EXISTS`
- Safe to run multiple times
- Script will continue

---

## Verification

After running migrations, verify:

### Check Tables Exist

```sql
-- In Supabase Dashboard → SQL Editor
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('tenants', 'user_tenants');
```

### Check RLS Enabled

```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('tenants', 'user_tenants', 'files');
```

### Check Tenants Created

```sql
SELECT COUNT(*) as tenant_count FROM public.tenants;
SELECT COUNT(*) as user_tenant_links FROM public.user_tenants;
```

---

## What Happens During Migration

### Migration 001: Create Tables

```
✅ Creates tenants table
✅ Creates user_tenants table
✅ Creates indexes
✅ Creates helper functions
✅ Creates triggers
```

### Migration 002: Add Columns

```
✅ Adds tenant_id to files table (if exists)
✅ Adds tenant_id to audit_logs table (if exists)
✅ Adds tenant_id to sessions table (if exists)
✅ Creates indexes on tenant_id columns
```

### Migration 003: Backfill Data

```
✅ Creates tenants for existing users
✅ Links users to tenants
✅ Backfills tenant_id in files (if exists)
✅ Backfills tenant_id in audit_logs (if exists)
✅ Backfills tenant_id in sessions (if exists)
```

### Migration 004: Enable RLS

```
✅ Enables RLS on tenants table
✅ Enables RLS on user_tenants table
✅ Enables RLS on files table (if exists)
✅ Creates security policies
✅ Tests policies
```

---

## Rollback

If something goes wrong:

### Option 1: Disable RLS (Temporary)

```sql
ALTER TABLE public.tenants DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_tenants DISABLE ROW LEVEL SECURITY;
-- ... repeat for other tables
```

### Option 2: Drop Policies

```sql
DROP POLICY IF EXISTS "Users can view their tenants" ON public.tenants;
-- ... repeat for other policies
```

### Option 3: Keep Schema, Revert Code

- Keep tenant tables (they don't break existing functionality)
- Keep tenant_id columns (they're nullable)
- Revert code changes if needed

---

## Best Practices

### Before Running

1. ✅ **Backup Database** (if possible)
2. ✅ **Test in Development** first
3. ✅ **Run Dry Run** to see what will happen
4. ✅ **Review Migration Files** to understand changes

### During Running

1. ✅ **Watch for Errors** - stop if critical errors occur
2. ✅ **Check Progress** - verify each migration completes
3. ✅ **Review Output** - check for warnings

### After Running

1. ✅ **Verify Tables** - check tables were created
2. ✅ **Verify RLS** - check RLS is enabled
3. ✅ **Test Registration** - verify tenant creation works
4. ✅ **Test Login** - verify tenant context loads
5. ✅ **Test Isolation** - verify users can't see other tenants' data

---

## Next Steps

After migrations complete:

1. ✅ Test new user registration (should create tenant)
2. ✅ Test existing user login (should load tenant)
3. ✅ Test file upload (should set tenant_id)
4. ✅ Test tenant isolation (users can't see other tenants' data)

---

## Support

**Script Location:** `scripts/run_supabase_migrations.py`

**Migration Files:** `foundations/public_works_foundation/sql/migrations/`

**Documentation:**
- `QUICK_MIGRATION_START.md` - Quick start guide
- `MIGRATION_SETUP_GUIDE.md` - Detailed setup instructions
- This file - Complete reference

**Questions?**
- Check error messages for specific issues
- Review migration files for SQL details
- Check Supabase Dashboard → Logs for database errors

---

**Status:** ✅ Ready to use  
**Last Updated:** December 1, 2025


