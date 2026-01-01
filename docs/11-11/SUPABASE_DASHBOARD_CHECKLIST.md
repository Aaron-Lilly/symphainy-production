# Supabase Dashboard Settings Checklist

## How to Access

1. Go to: https://supabase.com/dashboard
2. Sign in with your account
3. Select project: `rmymvrifwvqpeffmxkwi` (or the project with URL `https://rmymvrifwvqpeffmxkwi.supabase.co`)

---

## ✅ Checklist: What to Verify

### 1. Project Status

**Location:** Dashboard Home

- [ ] Project is **Active** (not paused)
- [ ] Project URL matches: `https://rmymvrifwvqpeffmxkwi.supabase.co`
- [ ] Database is running (green status)

---

### 2. API Credentials

**Location:** Settings → API

**Verify:**
- [ ] **Project URL** matches: `https://rmymvrifwvqpeffmxkwi.supabase.co`
- [ ] **Publishable Key** (anon key) matches: `sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W`
- [ ] **Secret Key** (service key) matches: `sb_secret_9q0019y231s_eVt9Qgu5iQ_U7v8UcfW`

**If keys don't match:**
- Copy the correct keys
- Update `.env.secrets` file
- Restart backend

---

### 3. Authentication Settings

**Location:** Authentication → Settings

**Check:**
- [ ] **Site URL** is set (can be `http://localhost:3000` for development)
- [ ] **Redirect URLs** includes your frontend URL
- [ ] **JWT expiry** is reasonable (default 3600 seconds is fine)

---

### 4. Email Provider

**Location:** Authentication → Providers → Email

**Verify:**
- [ ] **Email provider is ENABLED** (toggle should be ON)
- [ ] **Enable email confirmations:** 
  - For development: **OFF** (to skip email verification)
  - For production: **ON** (with email templates configured)
- [ ] **Secure email change:** ON (recommended)
- [ ] **Double confirm email changes:** ON (recommended)

**⚠️ Important:** If email confirmations are ON, users must click a confirmation link before they can log in.

---

### 5. Email Templates (Optional)

**Location:** Authentication → Email Templates

**Check:**
- [ ] Templates are configured (or using defaults)
- [ ] **Confirm signup** template exists
- [ ] **Reset password** template exists
- [ ] **Magic link** template exists (if using magic links)

**For development:** You can use default templates.

---

### 6. Email Validation Rules

**Location:** Authentication → Settings → Email Validation

**Check:**
- [ ] **Email validation rules** are not too restrictive
- [ ] Common email domains are allowed (gmail.com, yahoo.com, etc.)
- [ ] Test domains might be blocked (test.com, example.com)

**If test emails are blocked:**
- Use a real email domain for testing
- Or adjust validation rules (if possible)

---

### 7. Users Table

**Location:** Authentication → Users

**Check:**
- [ ] Table is accessible
- [ ] Can see existing users (if any)
- [ ] No errors when viewing users

**Note:** Supabase automatically creates the `auth.users` table - you don't need to create it.

---

### 8. Row Level Security (RLS)

**Location:** Table Editor → `auth` schema → `users` table

**Check:**
- [ ] RLS is enabled on `auth.users` (should be by default)
- [ ] Policies allow users to read their own data
- [ ] Policies allow service role to manage users

**Note:** Supabase handles RLS for `auth.users` automatically - you typically don't need to configure this.

---

## Common Issues & Fixes

### Issue: "Email address is invalid"

**Possible Causes:**
1. Email validation rules are too strict
2. Test domains are blocked
3. Email format doesn't match validation rules

**Fixes:**
1. Use a real email domain (gmail.com, outlook.com, etc.)
2. Check Authentication → Settings → Email Validation
3. Try with a different email format

### Issue: "User already exists"

**Fix:**
- Go to Authentication → Users
- Delete the test user
- Or use a different email

### Issue: "Email not confirmed"

**Fix:**
- Go to Authentication → Providers → Email
- Toggle "Enable email confirmations" OFF (for development)
- Or check email inbox for confirmation link

### Issue: "Invalid API key"

**Fix:**
- Verify keys in Settings → API match keys in `.env.secrets`
- Make sure you're using Publishable Key for user operations
- Make sure you're using Secret Key for admin operations

---

## Quick Test After Checking Settings

Once you've verified the settings, test authentication:

```bash
# Test with a real email domain
curl -X POST https://rmymvrifwvqpeffmxkwi.supabase.co/auth/v1/signup \
  -H "apikey: sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W" \
  -H "Content-Type: application/json" \
  -d '{"email":"yourname@gmail.com","password":"testpassword123"}'
```

**Expected:** Should return user data and access token

---

## Settings Summary

**Minimum Required Settings:**
- ✅ Email provider enabled
- ✅ Email confirmations OFF (for development)
- ✅ Site URL set
- ✅ API keys correct

**Everything else:** Supabase handles automatically!

---

**Status:** Ready to check! 🚀





