# Supabase Authentication - Simple Setup (Based on Legacy MVP)

**Key Insight:** Supabase Auth works out of the box! You don't need to configure anything in Supabase Dashboard. Just provide the credentials and it works.

---

## What the Legacy MVP Did (And It Just Worked!)

The legacy MVP used a simple `AuthService` that:
1. ✅ Directly calls Supabase `sign_up()` and `sign_in_with_password()`
2. ✅ Uses `SUPABASE_ANON_KEY` for user operations (signup/login)
3. ✅ Uses `SUPABASE_SERVICE_KEY` for admin operations (token validation)
4. ✅ **No database setup needed** - Supabase's `auth.users` table handles everything
5. ✅ **No RLS policies needed** - Supabase Auth handles security automatically

---

## Step 1: Verify Your Supabase Credentials

From `env_secrets_for_cursor.md`, you have:

```bash
# Hosted Supabase (New Project)
SUPABASE_URL=https://rmymvrifwvqpeffmxkwi.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W
SUPABASE_SECRET_KEY=sb_secret_9q0019y231s_eVt9Qgu5iQ_U7v8UcfW
```

**⚠️ Important:** Verify these keys are correct:
1. Go to: https://supabase.com/dashboard/project/rmymvrifwvqpeffmxkwi
2. Navigate to: **Settings** → **API**
3. Verify:
   - **Project URL** matches
   - **Publishable Key** matches (this is your `SUPABASE_ANON_KEY`)
   - **Secret Key** matches (this is your `SUPABASE_SERVICE_KEY`)

---

## Step 2: Update Backend Configuration

### Update `.env.secrets` File

Make sure your backend `.env.secrets` has:

```bash
# =============================================================================
# SUPABASE CONFIGURATION (New Project)
# =============================================================================
SUPABASE_URL=https://rmymvrifwvqpeffmxkwi.supabase.co

# For user operations (signup/login) - use Publishable Key
SUPABASE_ANON_KEY=sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W
SUPABASE_PUBLISHABLE_KEY=sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W

# For admin operations (token validation) - use Secret Key
SUPABASE_SERVICE_KEY=sb_secret_9q0019y231s_eVt9Qgu5iQ_U7v8UcfW
SUPABASE_SECRET_KEY=sb_secret_9q0019y231s_eVt9Qgu5iQ_U7v8UcfW
```

**Note:** The code supports both legacy (`SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`) and new naming (`SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`).

---

## Step 3: Verify SupabaseAdapter is Using Correct Keys

Check that `SupabaseAdapter` in the current platform is initialized correctly:

**File:** `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/supabase_adapter.py`

It should:
- Use `SUPABASE_URL` for the URL
- Use `SUPABASE_ANON_KEY` (or `SUPABASE_PUBLISHABLE_KEY`) for user operations
- Use `SUPABASE_SERVICE_KEY` (or `SUPABASE_SECRET_KEY`) for admin operations

---

## Step 4: Test Authentication Directly

### Test Supabase Auth Directly (No Backend)

```bash
# Test signup
curl -X POST https://rmymvrifwvqpeffmxkwi.supabase.co/auth/v1/signup \
  -H "apikey: sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Test login
curl -X POST "https://rmymvrifwvqpeffmxkwi.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Expected:** Should return access token and user data

---

## Step 5: Test Backend Auth Endpoints

Once backend is configured:

```bash
# Test registration
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test2@example.com",
    "password": "testpassword123"
  }'

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "testpassword123"
  }'
```

**Expected:** Should return success with user data and token

---

## What You DON'T Need to Do

❌ **Don't need to:**
- Create `user_profiles` table (unless you want custom fields)
- Set up RLS policies for `auth.users` (Supabase handles it)
- Configure email templates (defaults work)
- Enable email provider (enabled by default)
- Set up OAuth (unless you want it)

✅ **Supabase Auth just works with:**
- Correct URL
- Correct Publishable Key (anon key)
- Correct Secret Key (service key)

---

## Optional: Disable Email Confirmation (For Development)

If you want to skip email confirmation during development:

1. Go to Supabase Dashboard
2. Navigate to: **Authentication** → **Providers** → **Email**
3. Toggle **"Enable email confirmations"** OFF

**Note:** For production, keep this ON and configure email templates.

---

## How It Works (Legacy MVP Pattern)

```python
# Simple initialization
supabase_anon = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
supabase_service = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Signup (uses anon key)
response = supabase_anon.auth.sign_up({
    "email": email,
    "password": password
})

# Login (uses anon key)
response = supabase_anon.auth.sign_in_with_password({
    "email": email,
    "password": password
})

# Validate token (uses service key)
user = supabase_service.auth.get_user(token)
```

That's it! No complex setup needed.

---

## Troubleshooting

### Error: "Invalid API key"

**Fix:**
- Verify keys in Supabase Dashboard match keys in `.env.secrets`
- Make sure you're using Publishable Key for user operations
- Make sure you're using Secret Key for admin operations

### Error: "Email not confirmed"

**Fix:**
- Disable email confirmations in Supabase Dashboard (for development)
- Or check email inbox for confirmation link

### Error: "User already exists"

**Fix:**
- Check Supabase Dashboard → Authentication → Users
- Delete test user if needed
- Or use a different email

---

## Success Checklist

- [ ] Supabase URL verified in Dashboard
- [ ] Publishable Key verified (this is your `SUPABASE_ANON_KEY`)
- [ ] Secret Key verified (this is your `SUPABASE_SERVICE_KEY`)
- [ ] `.env.secrets` updated with correct keys
- [ ] Direct Supabase auth test works (signup/login)
- [ ] Backend auth endpoints work
- [ ] Frontend can register/login users

---

## Next Steps

Once authentication is working:

1. **Test Playwright tests** - They should now be able to authenticate
2. **Verify Security Guard** - Make sure it's using Supabase (not mock auth)
3. **Test protected endpoints** - Verify token validation works
4. **Optional:** Set up email templates for production

---

**Status:** Ready to test! 🚀

The beauty of Supabase Auth: **It just works** once you have the right credentials!





