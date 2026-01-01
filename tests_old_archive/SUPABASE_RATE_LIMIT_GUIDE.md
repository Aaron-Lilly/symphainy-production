# Supabase Rate Limit Settings Guide

**Date:** 2025-12-04  
**Purpose:** How to find and adjust rate limits in Supabase dashboard

---

## 🎯 **Important: Rate Limits Are Not in Dashboard UI**

**Key Finding:** Supabase rate limits are **NOT directly configurable** in the dashboard UI. They must be adjusted via the **Supabase Management API**.

---

## 📍 **Where to Check Current Rate Limits**

### **Option 1: Dashboard → Project Settings → API**

1. Go to: https://supabase.com/dashboard
2. Select your **test project** (e.g., `symphainy-test`)
3. Navigate to: **Settings** → **API**
4. Look for:
   - **Rate Limits** section (if visible)
   - **Project URL** and **API keys** (needed for Management API)

**Note:** The dashboard may show your current plan/tier, which determines default rate limits, but won't show adjustable rate limit settings.

### **Option 2: Check Your Plan/Tier**

1. Go to: **Settings** → **Billing** (or **Project Settings** → **General**)
2. Check your **Plan/Tier**:
   - **Free Tier:** 60 requests/minute (API), 2 emails/hour
   - **Pro Tier:** Higher limits
   - **Team/Enterprise:** Custom limits

**Current Issue:** You're likely on **Free Tier** with **60 requests/minute** limit, which is why tests are hitting 429 errors.

---

## 🔧 **How to Adjust Rate Limits (Management API)**

### **Step 1: Generate Personal Access Token (PAT)**

1. Go to: https://supabase.com/dashboard/account/tokens
2. Click **"Generate New Token"**
3. **Name:** `rate-limit-management`
4. **Scopes:** Select `projects:read` and `projects:write`
5. **Copy the token** (you won't see it again!)

### **Step 2: Get Your Project Reference (Project Ref)**

1. Go to your project dashboard
2. **Project Ref** is in the URL: `https://supabase.com/dashboard/project/[PROJECT_REF]`
3. Or go to: **Settings** → **General** → **Reference ID**

### **Step 3: Check Current Rate Limits**

```bash
# Replace with your values
PROJECT_REF="your-project-ref"
SUPABASE_ACCESS_TOKEN="your-pat-token"

# Check current auth rate limits
curl -X GET "https://api.supabase.com/v1/projects/$PROJECT_REF/config/auth" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  | jq '.rate_limit_*'
```

### **Step 4: Update Rate Limits**

**⚠️ Important:** Some rate limits are tied to your plan tier and **cannot be increased** on Free tier. You may need to:

1. **Upgrade to Pro tier** ($25/month) for higher limits
2. **Use custom SMTP** for email rate limits (bypasses Supabase email limits)

**For API Rate Limits (if adjustable):**

```bash
curl -X PATCH "https://api.supabase.com/v1/projects/$PROJECT_REF/config/auth" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rate_limit_anonymous_users": 100,
    "rate_limit_email_sent": 100,
    "rate_limit_verify": 100,
    "rate_limit_token_refresh": 100
  }'
```

**Note:** These may not work on Free tier - limits are often hard-coded by plan.

---

## 📊 **Default Rate Limits by Plan**

### **Free Tier:**
- **API Requests:** 60 requests/minute
- **Email Sending:** 2 emails/hour (via Supabase SMTP)
- **Database Connections:** 60 connections
- **Database Size:** 500 MB

### **Pro Tier ($25/month):**
- **API Requests:** Higher limits (varies)
- **Email Sending:** Higher limits (or use custom SMTP)
- **Database Connections:** Higher limits
- **Database Size:** 8 GB

### **Team/Enterprise:**
- **Custom limits** based on contract

---

## 💡 **Recommended Solutions**

### **Option 1: Upgrade to Pro Tier** (Recommended for Testing)

**Cost:** $25/month  
**Benefits:**
- Higher rate limits
- More suitable for testing
- Can downgrade later if needed

**Steps:**
1. Go to: **Settings** → **Billing**
2. Click **"Upgrade to Pro"**
3. Enter payment info
4. Rate limits increase automatically

### **Option 2: Use Custom SMTP** (For Email Limits)

If email sending is the issue:

1. Go to: **Settings** → **Auth** → **SMTP Settings**
2. Configure custom SMTP (Gmail, SendGrid, etc.)
3. This bypasses Supabase's 2 emails/hour limit
4. You control email rate limits

**Note:** This only helps with **email** rate limits, not API rate limits.

### **Option 3: Optimize Test Strategy** (Current Approach)

**What we're already doing:**
- ✅ Separate test Supabase project
- ✅ Rate limit monitoring and throttling
- ✅ Graceful 429 handling (tests skip when rate limited)
- ✅ Request delays between tests

**Additional optimizations:**
- Run tests in smaller batches
- Add longer delays between test suites
- Use test fixtures that cache results

### **Option 4: Wait for Rate Limit Reset**

**Free Tier:** Rate limits reset after the time window (typically 1 hour)

**Check current status:**
- Look at error messages - they include `retry_after` (in seconds)
- Wait for that duration
- Rate limits reset automatically

---

## 🔍 **How to Check Current Rate Limit Status**

### **Via Dashboard:**

1. Go to: **Project Dashboard** → **Logs** (or **API Logs**)
2. Look for **429 errors** in recent logs
3. Check **timestamp** - rate limits reset after time window

### **Via API Response:**

When you get a 429 error, the response includes:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 3600
  }
}
```

**`retry_after`** tells you how many seconds to wait.

---

## 📝 **Quick Reference: Dashboard Locations**

| Setting | Location in Dashboard |
|---------|---------------------|
| **Project Ref** | Settings → General → Reference ID |
| **API Keys** | Settings → API |
| **Plan/Tier** | Settings → Billing |
| **SMTP Settings** | Settings → Auth → SMTP Settings |
| **Rate Limit Logs** | Logs → API Logs (look for 429 errors) |
| **Personal Access Token** | Account Settings → Access Tokens |

---

## 🎯 **Recommended Action Plan**

### **For Immediate Testing:**

1. ✅ **Current approach is good:** Tests skip gracefully when rate limited
2. ⏳ **Wait for rate limit reset:** Check `retry_after` in error messages
3. 🔄 **Run tests in smaller batches:** Don't run all tests at once

### **For Long-Term Solution:**

1. **Option A:** Upgrade test project to **Pro tier** ($25/month)
   - Higher rate limits
   - Better for continuous testing
   - Can downgrade later

2. **Option B:** Optimize test strategy further
   - Reduce number of requests per test
   - Increase delays between tests
   - Cache test data more aggressively

3. **Option C:** Use multiple test projects
   - Rotate between projects
   - Distribute load

---

## ✅ **Current Status**

**What's Working:**
- ✅ Tests handle 429 errors gracefully (skip instead of fail)
- ✅ Rate limit monitoring and throttling active
- ✅ Separate test Supabase project (isolated from production)

**What's Needed:**
- ⏳ Wait for rate limit reset OR
- 💰 Upgrade to Pro tier for higher limits OR
- 🔧 Further optimize test strategy

---

## 📚 **Additional Resources**

- **Supabase Rate Limits Docs:** https://supabase.com/docs/guides/auth/rate-limits
- **Management API Docs:** https://supabase.com/docs/reference/api
- **Supabase Pricing:** https://supabase.com/pricing

---

**Next Steps:** Choose one of the recommended solutions above based on your needs and budget.



