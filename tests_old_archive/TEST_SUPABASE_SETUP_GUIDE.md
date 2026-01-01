# Test Supabase Project Setup Guide

**Date:** 2025-12-04  
**Status:** 🚀 **SETUP IN PROGRESS**

---

## 📋 **Step-by-Step Setup**

### **Step 1: Create Test Supabase Project** (5 minutes)

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Sign in with your account

2. **Create New Project**
   - Click **"New Project"** button
   - **Name:** `symphainy-test` (or `symphainy-platform-test`)
   - **Database Password:** Generate a strong password (save it!)
   - **Region:** Same as production (for consistency)
   - Click **"Create new project"**

3. **Wait for Provisioning**
   - Project will take ~2 minutes to provision
   - You'll see a progress indicator

4. **Get Project Credentials**
   - Once provisioned, go to: **Settings** → **API**
   - Copy the following:
     - **Project URL** (e.g., `https://xxxxx.supabase.co`)
     - **anon/public key** (starts with `eyJ...`)
     - **service_role key** (starts with `eyJ...`)

5. **Get Database Connection String** (Optional, for migrations)
   - Go to: **Settings** → **Database**
   - Under **Connection string**, select **"URI"**
   - Copy the connection string (format: `postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres`)

---

### **Step 2: Save Test Credentials**

Once you have the credentials, we'll add them to the test configuration file.

**Please provide:**
- `TEST_SUPABASE_URL`
- `TEST_SUPABASE_ANON_KEY`
- `TEST_SUPABASE_SERVICE_KEY`
- `TEST_SUPABASE_DB_PASSWORD` (optional, for migrations)

---

## 🔧 **Next Steps (Automated)**

After you provide the credentials, I'll:
1. ✅ Create test environment configuration
2. ✅ Update ProductionTestClient to support test mode
3. ✅ Create migration script for test project
4. ✅ Create test execution script
5. ✅ Verify setup

---

**Status:** ⏳ **WAITING FOR CREDENTIALS**



