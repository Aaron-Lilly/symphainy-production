# Quick Start: Run Supabase Migrations

**The easiest way to run migrations automatically**

---

## Step 1: Get Database Connection String

1. Go to: https://supabase.com/dashboard
2. Select your project
3. Go to: **Settings** → **Database**
4. Scroll to **Connection string**
5. Click **URI** tab
6. Copy the connection string (looks like: `postgresql://postgres.[ref]:[password]@...`)

---

## Step 2: Set Environment Variable

```bash
export DATABASE_URL="postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
```

Or add to `.env.secrets`:
```
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

---

## Step 3: Install psycopg2 (Python PostgreSQL adapter)

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
pip install psycopg2-binary
```

---

## Step 4: Run Migrations

```bash
# Dry run first (see what would happen)
python3 scripts/run_supabase_migrations.py --dry-run

# Run for real
python3 scripts/run_supabase_migrations.py
```

---

## That's It!

The script will:
- ✅ Read all migration files
- ✅ Execute them in order
- ✅ Show progress and results
- ✅ Stop on errors with clear messages

---

## Alternative: If psycopg2 Doesn't Work

### Option A: Install psql

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql-client

# macOS
brew install postgresql
```

Then run the script again - it will use psql automatically.

### Option B: Use Supabase CLI

```bash
# Install Supabase CLI
brew install supabase/tap/supabase  # macOS
# Or download from: https://github.com/supabase/cli/releases

# Login
supabase login

# Link project
supabase link --project-ref YOUR_PROJECT_REF

# Run migrations
python3 scripts/run_supabase_migrations.py
```

### Option C: Manual (Last Resort)

If automated methods don't work:

1. Open each migration file in order:
   - `001_create_tenant_management_tables.sql`
   - `002_add_tenant_id_to_existing_tables.sql`
   - `003_backfill_tenant_data.sql`
   - `004_enable_rls_policies.sql`

2. Copy SQL content

3. Go to Supabase Dashboard → SQL Editor

4. Paste and run

---

## Troubleshooting

**"DATABASE_URL not found"**
- Get connection string from Supabase Dashboard (see Step 1)
- Set environment variable (see Step 2)

**"psycopg2 not installed"**
- Run: `pip install psycopg2-binary`

**"Connection refused"**
- Check connection string is correct
- Verify password is correct
- Check IP is allowed in Supabase Dashboard

**"Migration failed"**
- Check error message for details
- Verify SQL is valid
- Check Supabase Dashboard → Logs

---

**Need help?** Check `MIGRATION_SETUP_GUIDE.md` for detailed instructions.






