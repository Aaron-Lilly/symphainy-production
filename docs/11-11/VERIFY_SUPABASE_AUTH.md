# Verify Supabase Authentication Setup

## Quick Verification Steps

### 1. Check Supabase Dashboard

Go to: https://supabase.com/dashboard/project/rmymvrifwvqpeffmxkwi

**Verify:**
- [ ] Project is active (not paused)
- [ ] Authentication → Providers → Email is enabled
- [ ] Authentication → Users shows any existing users (or is empty)

### 2. Test Authentication Directly

```bash
# Test registration
curl -X POST https://rmymvrifwvqpeffmxkwi.supabase.co/auth/v1/signup \
  -H "apikey: sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# Test login
curl -X POST https://rmymvrifwvqpeffmxkwi.supabase.co/auth/v1/token?grant_type=password \
  -H "apikey: sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Expected:** Should return access token and user data

### 3. Check Backend Configuration

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Check if Supabase is configured
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.secrets')
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_PUBLISHABLE_KEY')
print(f'URL: {url}')
print(f'Key (first 30 chars): {key[:30] if key else \"NOT SET\"}...')
"
```

### 4. Test Backend Auth Endpoints

```bash
# Test registration via backend
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test2@example.com",
    "password": "testpassword123"
  }'

# Test login via backend
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "testpassword123"
  }'
```

**Expected:** Should return success with user data and token

---

## If Authentication is Not Working

### Issue: "Mock authentication" in logs

**Fix:** Security Guard is not using Supabase. Check:
1. Security Guard is initialized with Supabase adapter
2. Supabase credentials are correct
3. Security Guard's `authenticate_user` method uses Supabase

### Issue: "Invalid API key"

**Fix:**
1. Verify keys in Supabase Dashboard
2. Update `.env.secrets` with correct keys
3. Restart backend server

### Issue: "Email not confirmed"

**Fix:**
1. Go to Supabase Dashboard → Authentication → Providers → Email
2. Disable "Enable email confirmations" for development
3. Or check email for confirmation link

---

## Next Steps

Once verified:
1. Update Security Guard to use Supabase (if not already)
2. Test full authentication flow
3. Update Playwright tests to use real authentication
4. Configure RLS policies for user data





