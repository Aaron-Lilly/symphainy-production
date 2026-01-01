# Manual Cleanup of Test Users in Supabase

**Date:** December 1, 2025  
**Purpose:** Remove test users that may have caused email bounces

---

## 🔍 How to Find Test Users

### Option 1: Supabase Dashboard

1. **Go to Supabase Dashboard:**
   - https://supabase.com/dashboard/project/rmymvrifwvqpeffmxkwi

2. **Navigate to Authentication → Users**

3. **Search for test users:**
   - Look for emails containing:
     - `test_tenant_`
     - `test_token_`
     - `test_isolate`
   - These are the test users created during multi-tenant testing

4. **Delete test users:**
   - Click on each test user
   - Click "Delete user" button
   - Confirm deletion

### Option 2: SQL Query

Run this in Supabase SQL Editor to find test users:

```sql
-- Find test users by email pattern
SELECT 
    id,
    email,
    created_at,
    email_confirmed_at
FROM auth.users
WHERE email LIKE '%test_tenant_%@gmail.com'
   OR email LIKE '%test_token_%@gmail.com'
   OR email LIKE '%test_isolate%@gmail.com'
ORDER BY created_at DESC;
```

### Option 3: Check User-Tenant Relationships

```sql
-- Find test users via tenant names
SELECT 
    u.id as user_id,
    u.email,
    t.name as tenant_name,
    ut.role,
    ut.is_primary
FROM auth.users u
JOIN public.user_tenants ut ON ut.user_id = u.id
JOIN public.tenants t ON t.id = ut.tenant_id
WHERE u.email LIKE '%test_%@gmail.com'
   OR t.name LIKE 'Tenant for test_%'
ORDER BY u.created_at DESC;
```

---

## 🗑️ Delete Test Users

### Via Supabase Dashboard (Easiest)

1. Go to **Authentication → Users**
2. Search for test email addresses
3. Click on each user
4. Click **"Delete user"**
5. Confirm deletion

**Note:** Deleting a user will also:
- Delete their user_tenants relationships (CASCADE)
- Keep their tenant record (but tenant will have no owner)

### Via SQL (Bulk Delete)

**⚠️ WARNING: This permanently deletes users. Use with caution.**

```sql
-- First, see what will be deleted
SELECT id, email FROM auth.users
WHERE email LIKE '%test_tenant_%@gmail.com'
   OR email LIKE '%test_token_%@gmail.com'
   OR email LIKE '%test_isolate%@gmail.com';

-- If the list looks correct, uncomment and run:
-- DELETE FROM auth.users
-- WHERE email LIKE '%test_tenant_%@gmail.com'
--    OR email LIKE '%test_token_%@gmail.com'
--    OR email LIKE '%test_isolate%@gmail.com';
```

---

## 🧹 Clean Up Associated Data

After deleting users, you may want to clean up orphaned tenants:

```sql
-- Find tenants without owners (orphaned)
SELECT 
    t.id,
    t.name,
    t.slug,
    t.owner_id,
    COUNT(ut.user_id) as member_count
FROM public.tenants t
LEFT JOIN public.user_tenants ut ON ut.tenant_id = t.id
WHERE t.owner_id NOT IN (SELECT id FROM auth.users)
   OR t.owner_id IS NULL
GROUP BY t.id, t.name, t.slug, t.owner_id;

-- Delete orphaned tenants (if desired)
-- DELETE FROM public.tenants
-- WHERE owner_id NOT IN (SELECT id FROM auth.users)
--    OR owner_id IS NULL;
```

---

## ✅ Verify Cleanup

After cleanup, verify:

1. **Check user count:**
   ```sql
   SELECT COUNT(*) as test_user_count
   FROM auth.users
   WHERE email LIKE '%test_%@gmail.com';
   ```
   Should return 0.

2. **Check Supabase Dashboard:**
   - Go to Authentication → Users
   - Search for "test"
   - Should find no test users

3. **Check email bounce rate:**
   - Go to Settings → Email
   - Check bounce rate (should decrease after cleanup)

---

## 📧 Contact Supabase Support

After cleanup:

1. **Email Supabase Support:**
   - Explain that test users with fake emails were created
   - Confirm that cleanup has been completed
   - Request email privileges to be restored

2. **Provide details:**
   - Number of test users deleted
   - Confirmation that cleanup is complete
   - Commitment to prevent future issues

---

## 🔒 Prevent Future Issues

1. ✅ **Always clean up test users** after running tests
2. ✅ **Use real email addresses** for testing (or disable email confirmation in dev)
3. ✅ **Run cleanup script** as part of test cleanup process
4. ✅ **Monitor bounce rates** in Supabase Dashboard

---

**Remember:** Test users with fake emails = email bounces = Supabase email suspension!


