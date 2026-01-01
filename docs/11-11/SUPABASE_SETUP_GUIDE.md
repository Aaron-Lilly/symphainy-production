# 🚀 Supabase Project Setup Guide

**Date:** November 9, 2025  
**Purpose:** Set up a new Supabase project after previous project was paused/unrecoverable

---

## 📋 Step-by-Step Instructions

### **Step 1: Create New Supabase Project**

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard
   - Sign in with your account

2. **Create New Project**
   - Click **"New Project"** button (top right)
   - Fill in project details:
     - **Name:** `symphainy-platform` (or your preferred name)
     - **Database Password:** Create a strong password (save this!)
     - **Region:** Choose closest to your deployment (e.g., `US East (N. Virginia)`)
     - **Pricing Plan:** Free tier is fine for development/testing
   
3. **Wait for Project Creation**
   - This takes 1-2 minutes
   - You'll see a progress indicator
   - Don't close the browser tab!

---

### **Step 2: Get Your Credentials**

Once your project is ready:

1. **Go to Project Settings**
   - Click the **⚙️ Settings** icon (gear) in the left sidebar
   - Select **"API"** from the settings menu

2. **Copy Your Credentials**
   You'll need these three values:

   **a) Project URL**
   ```
   Format: https://[project-ref].supabase.co
   Example: https://abcdefghijklmnop.supabase.co
   ```
   - Found in **"Project URL"** section
   - Copy the full URL (including `https://`)

   **b) Publishable Key** (New naming - preferred!)
   ```
   Format: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   - Found in **"Project API keys"** section
   - Labeled as **"Publishable"** key (new) or **"anon"** key (legacy)
   - This is safe to expose in frontend code
   - **Note:** Supabase is transitioning from "Anon Key" to "Publishable Key" - they're the same thing!

   **c) Secret Key** ⚠️ **KEEP SECRET!** (New naming - preferred!)
   ```
   Format: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
   - Found in **"Project API keys"** section
   - Labeled as **"Secret"** key (new) or **"service_role"** key (legacy)
   - **⚠️ NEVER expose this in frontend code!**
   - This bypasses Row Level Security (RLS)
   - **Note:** Supabase is transitioning from "Service Role Key" to "Secret Key" - they're the same thing!

---

### **Step 3: Create Storage Bucket**

Your platform needs a storage bucket for file uploads:

1. **Go to Storage**
   - Click **"Storage"** in the left sidebar
   - Click **"New bucket"** button

2. **Create Bucket**
   - **Name:** `project_files` (must match exactly)
   - **Public bucket:** ✅ **Checked** (for file access)
   - Click **"Create bucket"**

3. **Set Bucket Policies (Optional but Recommended)**
   - Click on the `project_files` bucket
   - Go to **"Policies"** tab
   - For development, you can use:
     - **Allow public read access** (for testing)
     - **Restrict write access** to authenticated users (for production)

---

### **Step 4: Set Up Database Schema**

Your platform needs the file management tables. We have a complete schema file ready:

1. **Open the schema file:**
   ```bash
   cat /home/founders/demoversion/symphainy_source/symphainy-platform/foundations/public_works_foundation/sql/create_file_management_schema.sql
   ```

2. **Go to Supabase Dashboard:**
   - Click **"SQL Editor"** in the left sidebar
   - Click **"New query"** button

3. **Copy and run the schema:**
   - Open the schema file: `foundations/public_works_foundation/sql/create_file_management_schema.sql`
   - Copy **ALL** contents (it's ~245 lines)
   - Paste into Supabase SQL Editor
   - Click **"Run"** (or press `Ctrl+Enter`)

4. **Verify tables were created:**
   - Go to **"Table Editor"** in left sidebar
   - You should see:
     - ✅ `project_files` table
     - ✅ `file_links` table

**Note:** The schema includes:
- File management tables with lineage support
- Indexes for performance
- Row Level Security (RLS) policies
- Helper functions for lineage queries

---

### **Step 5: (Alternative) Simplified Schema (If Full Schema Fails)**

If the full schema has issues, you can start with this minimal version:

```sql
-- Minimal schema for testing (use full schema from Step 4 for production)
CREATE TABLE IF NOT EXISTS project_files (
  uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  ui_name TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_size BIGINT,
  status TEXT NOT NULL DEFAULT 'uploaded',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_project_files_user_id ON project_files(user_id);
ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;

-- Allow all operations for development (restrict for production!)
CREATE POLICY "Allow all operations" ON project_files FOR ALL USING (true);
```

**⚠️ Important:** This minimal schema is for testing only. Use the full schema from Step 4 for production!

---

### **Step 6: Update Platform Configuration**

Now update your platform's configuration file:

1. **Locate the secrets file:**
   ```bash
   cd /home/founders/demoversion/symphainy_source/symphainy-platform
   ls -la .env.secrets
   ```

2. **Edit the file** (or create if it doesn't exist):
   ```bash
   nano .env.secrets
   # or
   vim .env.secrets
   ```

3. **Update Supabase configuration:**
   
   **Option A: New Naming (Recommended - Future-proof!)**
   ```bash
   # =============================================================================
   # SUPABASE CONFIGURATION (New Project - New Naming)
   # =============================================================================
   SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
   SUPABASE_PUBLISHABLE_KEY=YOUR-PUBLISHABLE-KEY-HERE
   SUPABASE_SECRET_KEY=YOUR-SECRET-KEY-HERE
   ```
   
   **Option B: Legacy Naming (Still works, but deprecated)**
   ```bash
   # =============================================================================
   # SUPABASE CONFIGURATION (New Project - Legacy Naming)
   # =============================================================================
   SUPABASE_URL=https://YOUR-PROJECT-REF.supabase.co
   SUPABASE_ANON_KEY=YOUR-ANON-KEY-HERE
   SUPABASE_SERVICE_KEY=YOUR-SERVICE-ROLE-KEY-HERE
   ```

   **Replace:**
   - `YOUR-PROJECT-REF` with your actual project reference (from Step 2a)
   - `YOUR-PUBLISHABLE-KEY-HERE` with your Publishable key (from Step 2b) - **OR** use `SUPABASE_ANON_KEY` with legacy naming
   - `YOUR-SECRET-KEY-HERE` with your Secret key (from Step 2c) - **OR** use `SUPABASE_SERVICE_KEY` with legacy naming
   
   **💡 Recommendation:** Use the new naming (`SUPABASE_PUBLISHABLE_KEY` and `SUPABASE_SECRET_KEY`) since we're setting up fresh. The code supports both, but new naming is future-proof!

4. **Save the file**

---

### **Step 7: Verify Configuration**

Test that your configuration is correct:

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Check if environment variables are loaded
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.secrets')
print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))
# Check both new and legacy naming
secret_key = os.getenv('SUPABASE_SECRET_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
print('SUPABASE_SECRET_KEY (or SERVICE_KEY):', secret_key[:20] + '...' if secret_key else 'NOT SET')
publishable_key = os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
print('SUPABASE_PUBLISHABLE_KEY (or ANON_KEY):', publishable_key[:20] + '...' if publishable_key else 'NOT SET')
"
```

**Expected output:**
```
SUPABASE_URL: https://abcdefghijklmnop.supabase.co
SUPABASE_SECRET_KEY (or SERVICE_KEY): eyJhbGciOiJIUzI1NiIs...
SUPABASE_PUBLISHABLE_KEY (or ANON_KEY): eyJhbGciOiJIUzI1NiIs...
```

---

### **Step 8: Test Connection**

Start your platform and verify Supabase connection:

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
python3 main.py
```

**Look for these log messages:**
```
✅ Supabase File Management adapter initialized with URL: https://...
✅ Supabase File Management adapter connected
✅ Supabase File Management Adapter initialized and connected
```

**If you see errors:**
- Check that your credentials are correct
- Verify the project URL includes `https://` and ends with `.supabase.co`
- Make sure the service role key is the full JWT token (starts with `eyJ...`)

---

## ✅ Success Checklist

- [ ] Supabase project created
- [ ] Credentials copied (URL, Anon Key, Service Role Key)
- [ ] Storage bucket `project_files` created
- [ ] Database schema created (project_files table)
- [ ] `.env.secrets` file updated with credentials
- [ ] Platform starts without Supabase connection errors
- [ ] File upload test succeeds (no more in-memory fallback)

---

## 🐛 Troubleshooting

### **Error: "Supabase configuration is required"**
- **Fix:** Make sure `.env.secrets` file exists and has:
  - `SUPABASE_URL` (required)
  - Either `SUPABASE_SECRET_KEY` (new) or `SUPABASE_SERVICE_KEY` (legacy)
  - Either `SUPABASE_PUBLISHABLE_KEY` (new) or `SUPABASE_ANON_KEY` (legacy) - optional for file management

### **Error: "Failed to connect to Supabase"**
- **Fix:** Check that:
  - Project URL is correct (includes `https://`)
  - Service role key is the full JWT token
  - Project is not paused (check Supabase dashboard)

### **Error: "File not found" after upload**
- **Fix:** 
  - Verify storage bucket `project_files` exists
  - Check bucket is set to public (for development)
  - Verify database table `project_files` was created

### **Error: "Permission denied" or RLS policy errors**
- **Fix:** 
  - Check RLS policies in Supabase dashboard
  - For development, you can temporarily disable RLS:
    ```sql
    ALTER TABLE project_files DISABLE ROW LEVEL SECURITY;
    ```
  - (Re-enable for production!)

---

## 📚 Next Steps

Once Supabase is configured:

1. **Test file upload:**
   ```bash
   curl -X POST http://localhost:8000/api/mvp/content/upload \
     -F "file=@test_document.txt" \
     -F "user_id=test_user"
   ```

2. **Verify file is in Supabase:**
   - Check Supabase Dashboard → Storage → `project_files` bucket
   - Check Supabase Dashboard → Table Editor → `project_files` table

3. **Test file parsing:**
   ```bash
   curl -X POST "http://localhost:8000/api/mvp/content/parse/{file_id}" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test_user"}'
   ```

4. **Remove in-memory fallback** (once everything works):
   - Edit `content_analysis_orchestrator.py`
   - Remove the in-memory fallback code (lines 332-356)

---

## 🔒 Security Notes

- **Never commit `.env.secrets` to git** (it should be in `.gitignore`)
- **Service Role Key** bypasses all security - keep it secret!
- **For production:** Set up proper RLS policies instead of public access
- **Rotate keys** if they're ever exposed

---

**Status:** Ready to configure! 🚀

