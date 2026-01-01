# Supabase Test User Best Practices

**Date:** December 1, 2025  
**Purpose:** Prevent email bounces and Supabase email suspension

---

## ⚠️ Problem

Supabase temporarily suspended email privileges due to high bounce rates from test users with fake email addresses (e.g., `test_user_123@gmail.com`).

**Why this happens:**
- Test users with fake email addresses cause email bounces
- High bounce rates trigger Supabase's email suspension
- This affects all email sending from the project

---

## ✅ Solution

### 1. Clean Up Test Users

**After running tests, always clean up test users:**

```bash
cd symphainy-platform
python3 scripts/cleanup_test_users.py
```

This script:
- Finds all test users with patterns like `test_*@gmail.com`
- Deletes them from Supabase Auth
- Cleans up associated tenant data

### 2. Use Valid Test Email Addresses

**Option A: Use Real Email Addresses (Recommended)**
- Use your own email address or a test email you control
- Example: `yourname+test1@gmail.com` (Gmail supports `+` aliases)

**Option B: Disable Email Confirmation (Development Only)**
- In Supabase Dashboard: Settings → Authentication → Email Templates
- Disable "Confirm email" for development
- **Warning:** Only for local development, not production

**Option C: Use Supabase's Test Mode**
- Supabase has a test mode that doesn't send emails
- Check Supabase documentation for test mode setup

### 3. Update Test Scripts

**Current test script creates users with fake emails:**
- `test_tenant_*@gmail.com`
- `test_token_*@gmail.com`
- `test_isolate*@gmail.com`

**Best Practice:**
- Use real email addresses you control
- Or use email addresses that won't bounce (like `+test` aliases)
- Always clean up after tests

---

## 📋 Cleanup Checklist

After running multi-tenant tests:

1. ✅ Run cleanup script: `python3 scripts/cleanup_test_users.py`
2. ✅ Verify users are deleted in Supabase Dashboard
3. ✅ Check email bounce rate in Supabase Dashboard (Settings → Email)

---

## 🔧 Updated Test Script

The test script (`test_multi_tenant_implementation.py`) now includes:
- Warning about fake email addresses
- Instructions to run cleanup script after tests

**Before running tests:**
- Consider using real email addresses
- Or be prepared to clean up immediately after

---

## 🚨 If Email is Already Suspended

1. **Clean up test users immediately:**
   ```bash
   python3 scripts/cleanup_test_users.py
   ```

2. **Contact Supabase Support:**
   - Explain that test users with fake emails were created
   - Confirm that cleanup has been completed
   - Request email privileges to be restored

3. **Prevent future issues:**
   - Always clean up test users after tests
   - Use real email addresses for testing
   - Monitor bounce rates in Supabase Dashboard

---

## 📝 Best Practices Summary

1. ✅ **Always clean up test users** after running tests
2. ✅ **Use real email addresses** for testing (or disable email confirmation in dev)
3. ✅ **Monitor bounce rates** in Supabase Dashboard
4. ✅ **Run cleanup script** as part of test cleanup process
5. ✅ **Document test user patterns** so they can be easily identified and cleaned

---

## 🔗 Related Scripts

- `scripts/test_multi_tenant_implementation.py` - Creates test users
- `scripts/cleanup_test_users.py` - Removes test users
- `scripts/setup_test_users.py` - Sets up pre-confirmed test users (uses real emails)

---

**Remember:** Test users with fake emails = email bounces = Supabase email suspension!


