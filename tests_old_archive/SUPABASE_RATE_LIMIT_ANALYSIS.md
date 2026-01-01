# Supabase Rate Limit Analysis & Results

**Date:** 2025-12-04  
**Project:** symphainy-test  
**Project Ref:** eocztpcvzcdqgygxlnqg

---

## ✅ **Credentials Added**

Successfully added Supabase Management API credentials to `.env.secrets`:
- `SUPABASE_PROJECT_REF=eocztpcvzcdqgygxlnqg`
- `SUPABASE_ACCESS_TOKEN=sbp_ae7cf60064ac405b2800dd15b536ceb5945ff9ea`

---

## 📊 **Current Rate Limits (Retrieved)**

### **Project Information:**
- **Project Name:** symphainy-test
- **Region:** us-west-2
- **Plan/Tier:** Free Tier (based on limits)

### **Rate Limit Settings:**

| Limit Type | Current Value | Notes |
|------------|---------------|-------|
| **Anonymous Users** | 30 req/min | ⚠️ Very low - causing 429 errors |
| **Email Sent** | 2/hour | ⚠️ Extremely low - only 2 emails per hour |
| **OTP** | 30 req/min | Low |
| **SMS Sent** | 30 req/min | Low |
| **Token Refresh** | 150 req/min | ✅ Highest limit |
| **Verify** | 30 req/min | Low |
| **Web3** | 30 req/min | Low |

---

## 🔍 **Analysis**

### **Root Cause:**
- **Free Tier** has very restrictive rate limits
- **30 requests/minute** for anonymous users is the main bottleneck
- Tests are hitting this limit quickly, causing 429 errors

### **Why Tests Are Failing:**
1. Each test makes multiple API calls (auth, upload, parse, analyze, etc.)
2. With 30 req/min limit, tests can only make ~0.5 requests/second
3. Our test suite makes requests much faster than this
4. Result: Rate limit exceeded (429 errors)

---

## 💡 **Solutions & Workarounds**

### **Option 1: Upgrade to Pro Tier** ⭐ **RECOMMENDED**

**Cost:** $25/month  
**Benefits:**
- Higher rate limits (typically 10x or more)
- Better suited for testing
- Can downgrade later if needed

**Steps:**
1. Go to: https://supabase.com/dashboard/project/eocztpcvzcdqgygxlnqg/settings/billing
2. Click "Upgrade to Pro"
3. Enter payment info
4. Limits increase automatically

### **Option 2: Optimize Test Strategy** ✅ **ALREADY IMPLEMENTED**

**Current Workarounds:**
- ✅ Graceful 429 handling (tests skip when rate limited)
- ✅ Rate limit monitoring and throttling
- ✅ Request delays between tests (0.2s in test mode)
- ✅ Separate test Supabase project (isolated from production)

**Additional Optimizations:**
- 💡 Increase delays between test batches
- 💡 Run tests in smaller groups
- 💡 Cache test data more aggressively
- 💡 Reduce number of requests per test

### **Option 3: Use Multiple Test Projects**

**Strategy:**
- Create 2-3 test projects
- Rotate between them
- Distribute load across projects

**Pros:**
- Each project has separate quota
- Can run more tests in parallel

**Cons:**
- More complex setup
- Need to manage multiple projects

### **Option 4: Wait for Rate Limit Reset**

**Current Behavior:**
- Rate limits reset after time window (typically 1 hour)
- Tests will work again after reset

**Limitation:**
- Can only run tests once per hour
- Not suitable for continuous testing

---

## 🔧 **Attempting to Update Limits**

We'll try to update limits via Management API, but **this likely won't work on Free tier** as limits are typically hard-coded.

**Expected Result:**
- API may accept the request
- But Free tier will still enforce lower limits
- May need to upgrade to Pro tier for adjustable limits

---

## 📝 **Scripts Created**

### **1. Check Rate Limits**
```bash
python3 tests/scripts/check_supabase_rate_limits.py
```
- Fetches current rate limit settings
- Displays project information
- Provides recommendations

### **2. Update Rate Limits**
```bash
python3 tests/scripts/update_supabase_rate_limits.py
```
- Attempts to increase rate limits via Management API
- May not work on Free tier (limits are hard-coded)

### **3. Add Credentials**
```bash
./tests/scripts/add_supabase_management_credentials.sh
```
- Adds Management API credentials to `.env.secrets`
- Safe to run multiple times (checks for existing entries)

---

## 🎯 **Recommended Next Steps**

1. **Immediate:** Continue with current workarounds (graceful 429 handling)
2. **Short-term:** Consider upgrading to Pro tier for better testing experience
3. **Long-term:** Optimize test strategy to use fewer requests

---

## ✅ **Current Status**

**What's Working:**
- ✅ Credentials added to `.env.secrets`
- ✅ Scripts created to check/update limits
- ✅ Rate limits retrieved successfully
- ✅ Tests handle 429 errors gracefully

**What's Needed:**
- ⏳ Decision on whether to upgrade to Pro tier
- ⏳ OR continue with optimized test strategy
- ⏳ OR wait for rate limit resets

---

**Next:** Run `update_supabase_rate_limits.py` to attempt increasing limits (may not work on Free tier)



