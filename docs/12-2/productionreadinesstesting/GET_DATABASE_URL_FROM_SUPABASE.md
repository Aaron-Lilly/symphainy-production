# How to Get DATABASE_URL from Supabase

**Date:** December 1, 2025  
**Purpose:** Get the PostgreSQL connection string (DATABASE_URL) from Supabase Dashboard

---

## The Difference

### SUPABASE_URL (What You Have)
- **Format:** `https://rmymvrifwvqpeffmxkwi.supabase.co`
- **Purpose:** API gateway URL for Supabase services (auth, storage, REST API)
- **Used For:** Client libraries, REST API calls, authentication

### DATABASE_URL (What You Need)
- **Format:** `postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres`
- **Purpose:** Direct PostgreSQL database connection
- **Used For:** Running migrations, direct SQL queries, database tools

---

## How to Get DATABASE_URL

### Method 1: Supabase Dashboard (Easiest)

1. **Go to Supabase Dashboard**
   - https://supabase.com/dashboard
   - Select your project: `rmymvrifwvqpeffmxkwi`

2. **Navigate to Database Settings**
   - Click **Settings** (gear icon in left sidebar)
   - Click **Database** in the settings menu

3. **Get Connection String**
   - Scroll down to **Connection string** section
   - You'll see several tabs:
     - **URI** ← **Use this one**
     - **JDBC**
     - **Golang**
     - **psql**
     - **Connection pooling**

4. **Copy URI Connection String**
   - Click the **URI** tab
   - You'll see something like:
     ```
     postgresql://postgres.rmymvrifwvqpeffmxkwi:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
     ```
   - **Important:** Replace `[YOUR-PASSWORD]` with your actual database password
   - The password is shown if you click "Reveal" or it's in the connection string

5. **Get Database Password**
   - If password is hidden, look for:
     - **Database password** field (may be shown or hidden)
     - Or click **Reset database password** to set a new one
     - Or check if it's stored elsewhere in your project

6. **Copy Complete Connection String**
   - Replace `[YOUR-PASSWORD]` with actual password
   - Copy the complete string
   - It should look like:
     ```
     postgresql://postgres.rmymvrifwvqpeffmxkwi:your_actual_password@aws-0-us-west-1.pooler.supabase.com:6543/postgres
     ```

---

## Method 2: Extract from Project Settings

If you can't find the password in the dashboard:

1. **Check Project Settings**
   - Settings → General
   - Look for database credentials

2. **Reset Database Password** (if needed)
   - Settings → Database
   - Click **Reset database password**
   - Set a new password
   - Use this password in the connection string

---

## Method 3: Use Connection Pooling (Recommended)

Supabase provides a **pooled connection** which is better for migrations:

1. **Go to:** Settings → Database → Connection string
2. **Select:** **Connection pooling** tab
3. **Copy:** The pooled connection string
4. **Format:** Usually uses port `6543` (pooled) instead of `5432` (direct)

**Pooled Connection Example:**
```
postgresql://postgres.rmymvrifwvqpeffmxkwi:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

---

## Add to .env.secrets

Once you have the DATABASE_URL:

```bash
# Add to .env.secrets file
DATABASE_URL=postgresql://postgres.rmymvrifwvqpeffmxkwi:your_password@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

**Security Note:** 
- The `.env.secrets` file should NOT be committed to git
- The password in DATABASE_URL is sensitive - keep it secure

---

## Quick Reference

**Your Project:**
- Project Reference: `rmymvrifwvqpeffmxkwi`
- SUPABASE_URL: `https://rmymvrifwvqpeffmxkwi.supabase.co`

**DATABASE_URL Format:**
```
postgresql://postgres.rmymvrifwvqpeffmxkwi:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

**What You Need:**
- ✅ Project reference: `rmymvrifwvqpeffmxkwi` (from SUPABASE_URL)
- ❌ Database password: Need to get from Supabase Dashboard

---

## Alternative: Use Supabase CLI

If you have Supabase CLI installed:

```bash
# Login
supabase login

# Link project
supabase link --project-ref rmymvrifwvqpeffmxkwi

# The CLI will handle the connection automatically
```

---

## Next Steps

1. Get DATABASE_URL from Supabase Dashboard (see Method 1 above)
2. Add to `.env.secrets` file
3. Run migrations:
   ```bash
   python3 scripts/run_supabase_migrations.py
   ```

---

**Need Help?** If you can't find the database password, you can:
- Reset it in Supabase Dashboard
- Or use Supabase CLI (handles connection automatically)

