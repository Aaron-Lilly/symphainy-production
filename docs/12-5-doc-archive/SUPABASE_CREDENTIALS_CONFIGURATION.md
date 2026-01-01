# Supabase Credentials Configuration Guide

**Date:** December 2024  
**Status:** 📋 **CONFIGURATION GUIDE**

---

## 🎯 Overview

This guide explains how to configure Supabase credentials for both the platform and testing, including how to use your existing `SUPABASE_PROJECT_REF` and `SUPABASE_ACCESS_TOKEN`.

---

## 📋 Current Configuration

You currently have in `.env.secrets`:
- `SUPABASE_PROJECT_REF` - Your Supabase project reference
- `SUPABASE_ACCESS_TOKEN` - Your Supabase access token

---

## 🔧 What the Platform Needs

The platform expects these environment variables:

### **Required for Platform Operation:**
- `SUPABASE_URL` - Full Supabase project URL (e.g., `https://xxxxx.supabase.co`)
- `SUPABASE_ANON_KEY` - Supabase anon/public key (for client-side auth)
- `SUPABASE_SERVICE_KEY` - Supabase service role key (for server-side operations)

### **Optional for Testing:**
- `TEST_SUPABASE_URL` - Test project URL (if using separate test project)
- `TEST_SUPABASE_ANON_KEY` - Test project anon key
- `TEST_SUPABASE_EMAIL` - Test user email
- `TEST_SUPABASE_PASSWORD` - Test user password

---

## 🔄 Using Your Existing Credentials

### **Option 1: Construct URL from PROJECT_REF (Recommended)**

If you have `SUPABASE_PROJECT_REF`, you can construct the URL:

```bash
# In .env.secrets
SUPABASE_PROJECT_REF=your-project-ref-here
SUPABASE_URL=https://${SUPABASE_PROJECT_REF}.supabase.co
```

**Or add directly:**
```bash
SUPABASE_URL=https://your-project-ref.supabase.co
```

### **Option 2: Determine What SUPABASE_ACCESS_TOKEN Is**

`SUPABASE_ACCESS_TOKEN` could be:
- **Anon Key** (most likely) - Used for client-side authentication
- **Service Key** - Used for server-side admin operations

**To determine which:**
1. Go to Supabase Dashboard → Settings → API
2. Compare `SUPABASE_ACCESS_TOKEN` with:
   - **anon/public key** (starts with `eyJ...`, shorter)
   - **service_role key** (starts with `eyJ...`, longer, more permissions)

**If it's the anon key:**
```bash
SUPABASE_ANON_KEY=${SUPABASE_ACCESS_TOKEN}
# Or rename it:
SUPABASE_ANON_KEY=your-actual-anon-key-here
```

**If it's the service key:**
```bash
SUPABASE_SERVICE_KEY=${SUPABASE_ACCESS_TOKEN}
# You'll still need the anon key for client auth
SUPABASE_ANON_KEY=your-actual-anon-key-here
```

---

## 📝 Recommended .env.secrets Configuration

### **For Test Environment (Current Setup):**

```bash
# =============================================================================
# SUPABASE CONFIGURATION (Test Environment)
# =============================================================================

# Project Reference (used to construct URL)
SUPABASE_PROJECT_REF=your-project-ref-here

# Constructed URL (or set directly)
SUPABASE_URL=https://${SUPABASE_PROJECT_REF}.supabase.co
# OR set directly:
# SUPABASE_URL=https://your-project-ref.supabase.co

# Access Token (determine if this is anon key or service key)
SUPABASE_ACCESS_TOKEN=your-access-token-here

# If SUPABASE_ACCESS_TOKEN is the anon key:
SUPABASE_ANON_KEY=${SUPABASE_ACCESS_TOKEN}
# OR set separately:
# SUPABASE_ANON_KEY=your-anon-key-here

# Service Role Key (for server-side operations)
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Optional: Test-specific credentials (if using separate test project)
TEST_SUPABASE_URL=https://your-test-project-ref.supabase.co
TEST_SUPABASE_ANON_KEY=your-test-anon-key-here
TEST_SUPABASE_EMAIL=test@symphainy.com
TEST_SUPABASE_PASSWORD=test_password_123
```

---

## 🧪 For Phase 1 Testing

The test script now supports multiple credential formats:

1. **Explicit test credentials** (preferred for testing):
   ```bash
   TEST_SUPABASE_URL=https://your-test-project.supabase.co
   TEST_SUPABASE_ANON_KEY=your-test-anon-key
   TEST_SUPABASE_EMAIL=test@symphainy.com
   TEST_SUPABASE_PASSWORD=test_password_123
   ```

2. **Platform credentials** (fallback):
   ```bash
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   ```

3. **Project reference** (auto-constructs URL):
   ```bash
   SUPABASE_PROJECT_REF=your-project-ref
   SUPABASE_ACCESS_TOKEN=your-anon-key  # If this is the anon key
   ```

**The test script will automatically:**
- Use `TEST_SUPABASE_*` if available
- Fall back to `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Construct URL from `SUPABASE_PROJECT_REF` if needed
- Use `SUPABASE_ACCESS_TOKEN` as anon key if no explicit anon key is set

---

## 🔍 How to Get Missing Credentials

### **1. Get Supabase URL**

If you have `SUPABASE_PROJECT_REF`:
```bash
SUPABASE_URL=https://${SUPABASE_PROJECT_REF}.supabase.co
```

Or get it from Supabase Dashboard:
- Go to: **Settings** → **API**
- Copy **Project URL**

### **2. Get Anon Key**

From Supabase Dashboard:
- Go to: **Settings** → **API**
- Copy **anon/public key** (starts with `eyJ...`)

### **3. Get Service Key**

From Supabase Dashboard:
- Go to: **Settings** → **API**
- Copy **service_role key** (starts with `eyJ...`, longer than anon key)

### **4. Determine What SUPABASE_ACCESS_TOKEN Is**

Compare your `SUPABASE_ACCESS_TOKEN` with:
- **anon key** from dashboard
- **service key** from dashboard

If it matches the anon key:
```bash
SUPABASE_ANON_KEY=${SUPABASE_ACCESS_TOKEN}
```

If it matches the service key:
```bash
SUPABASE_SERVICE_KEY=${SUPABASE_ACCESS_TOKEN}
# You'll still need to add SUPABASE_ANON_KEY separately
```

---

## ✅ Recommended .env.secrets Setup

Based on your current setup, here's what I recommend:

```bash
# =============================================================================
# SUPABASE CONFIGURATION (Test Environment)
# =============================================================================

# Your existing credentials
SUPABASE_PROJECT_REF=your-project-ref-here
SUPABASE_ACCESS_TOKEN=your-access-token-here

# Construct URL from project ref (or set directly)
SUPABASE_URL=https://${SUPABASE_PROJECT_REF}.supabase.co

# Determine if ACCESS_TOKEN is anon key or service key
# If it's the anon key:
SUPABASE_ANON_KEY=${SUPABASE_ACCESS_TOKEN}

# If it's the service key, set both:
# SUPABASE_SERVICE_KEY=${SUPABASE_ACCESS_TOKEN}
# SUPABASE_ANON_KEY=your-actual-anon-key-from-dashboard

# Get service key from dashboard if ACCESS_TOKEN is anon key
SUPABASE_SERVICE_KEY=your-service-role-key-from-dashboard

# Optional: Test user credentials (for Phase 1 testing)
TEST_SUPABASE_EMAIL=test@symphainy.com
TEST_SUPABASE_PASSWORD=test_password_123
```

---

## 🧪 Testing the Configuration

After updating `.env.secrets`, test the configuration:

```bash
cd /home/founders/demoversion/symphainy_source

# Load secrets
source .env.secrets  # Or however you load them

# Test Phase 1 (will use credentials from .env.secrets)
python3 scripts/test_phase1_security_integration.py
```

---

## 📋 Summary

**What to add to `.env.secrets`:**

1. **SUPABASE_URL** (construct from PROJECT_REF or set directly)
   ```bash
   SUPABASE_URL=https://${SUPABASE_PROJECT_REF}.supabase.co
   ```

2. **SUPABASE_ANON_KEY** (determine if ACCESS_TOKEN is this, or get from dashboard)
   ```bash
   SUPABASE_ANON_KEY=${SUPABASE_ACCESS_TOKEN}  # If ACCESS_TOKEN is anon key
   # OR
   SUPABASE_ANON_KEY=your-anon-key-from-dashboard
   ```

3. **SUPABASE_SERVICE_KEY** (get from dashboard)
   ```bash
   SUPABASE_SERVICE_KEY=your-service-role-key-from-dashboard
   ```

4. **Optional: Test user credentials**
   ```bash
   TEST_SUPABASE_EMAIL=test@symphainy.com
   TEST_SUPABASE_PASSWORD=test_password_123
   ```

**The test script will automatically use these credentials!** ✅

---

**Last Updated:** December 2024  
**Status:** Ready for Configuration




