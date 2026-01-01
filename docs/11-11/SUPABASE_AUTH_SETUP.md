# Supabase Authentication Setup Guide

**Date:** November 9, 2025  
**Purpose:** Set up authentication and authorization in the new Supabase project

---

## Current Status

✅ **File Management:** Working with new Supabase project  
❌ **Authentication:** Not yet configured in new Supabase project

---

## Step 1: Verify Supabase Project Configuration

### Check Current Configuration

From `env_secrets_for_cursor.md`, we have:

**Hosted Supabase (New Project):**
- URL: `https://rmymvrifwvqpeffmxkwi.supabase.co`
- Publishable Key: `sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W`
- Secret Key: `sb_secret_9q0019y231s_eVt9Qgu5iQ_U7v8UcfW`

**⚠️ Important:** These keys look like they might be from the old project. We need to verify they're correct for the new project.

### Verify in Supabase Dashboard

1. Go to: https://supabase.com/dashboard/project/rmymvrifwvqpeffmxkwi
2. Navigate to: **Settings** → **API**
3. Verify:
   - **Project URL** matches: `https://rmymvrifwvqpeffmxkwi.supabase.co`
   - **Publishable Key** matches the one in env file
   - **Secret Key** matches the one in env file

**If keys don't match:**
- Copy the correct keys from Supabase Dashboard
- Update `env_secrets_for_cursor.md` and `.env.secrets` file

---

## Step 2: Configure Authentication Providers

### Enable Email/Password Authentication

1. **Go to Supabase Dashboard**
   - Navigate to: **Authentication** → **Providers**
   
2. **Enable Email Provider**
   - Find **"Email"** in the providers list
   - Toggle it **ON** (should be enabled by default)
   - Configure settings:
     - ✅ **Enable email confirmations:** OFF (for development) or ON (for production)
     - ✅ **Secure email change:** ON
     - ✅ **Double confirm email changes:** ON (recommended)

3. **Configure Email Templates (Optional)**
   - Go to: **Authentication** → **Email Templates**
   - Customize templates if needed (or use defaults)

### Enable OAuth Providers (Optional)

If you want Google OAuth:

1. **Go to:** **Authentication** → **Providers**
2. **Enable Google Provider**
   - Toggle **Google** ON
   - Add your Google OAuth credentials:
     - Client ID
     - Client Secret
   - Set redirect URL: `https://rmymvrifwvqpeffmxkwi.supabase.co/auth/v1/callback`

---

## Step 3: Set Up Database Schema for Authentication

Supabase Auth uses the `auth.users` table automatically, but we may need custom tables for user profiles.

### Check if User Profiles Table Exists

1. **Go to Supabase Dashboard**
   - Navigate to: **Table Editor**
   - Look for `user_profiles` or `users` table

2. **If table doesn't exist, create it:**

```sql
-- User profiles table (extends auth.users)
CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own profile
CREATE POLICY "Users can read own profile"
  ON public.user_profiles
  FOR SELECT
  USING (auth.uid() = id);

-- Policy: Users can update their own profile
CREATE POLICY "Users can update own profile"
  ON public.user_profiles
  FOR UPDATE
  USING (auth.uid() = id);

-- Policy: Users can insert their own profile
CREATE POLICY "Users can insert own profile"
  ON public.user_profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- Create function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile when user signs up
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();
```

3. **Run the SQL:**
   - Go to: **SQL Editor** in Supabase Dashboard
   - Paste the SQL above
   - Click **Run**

---

## Step 4: Configure Row Level Security (RLS) Policies

### For File Management Tables

If you haven't already, set up RLS policies for file management:

```sql
-- Ensure RLS is enabled on project_files
ALTER TABLE public.project_files ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own files
CREATE POLICY "Users can read own files"
  ON public.project_files
  FOR SELECT
  USING (auth.uid()::text = user_id);

-- Policy: Users can insert their own files
CREATE POLICY "Users can insert own files"
  ON public.project_files
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- Policy: Users can update their own files
CREATE POLICY "Users can update own files"
  ON public.project_files
  FOR UPDATE
  USING (auth.uid()::text = user_id);

-- Policy: Users can delete their own files
CREATE POLICY "Users can delete own files"
  ON public.project_files
  FOR DELETE
  USING (auth.uid()::text = user_id);
```

---

## Step 5: Update Backend Configuration

### Verify Environment Variables

Check that the backend is using the correct Supabase credentials:

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Check if .env.secrets exists
ls -la .env.secrets

# Verify Supabase configuration is loaded
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.secrets')
print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))
print('SUPABASE_KEY (first 20 chars):', os.getenv('SUPABASE_KEY', os.getenv('SUPABASE_PUBLISHABLE_KEY', 'NOT SET'))[:20])
print('SUPABASE_SERVICE_KEY (first 20 chars):', os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_SECRET_KEY', 'NOT SET'))[:20])
"
```

### Update .env.secrets File

Make sure `.env.secrets` has the correct values:

```bash
# =============================================================================
# SUPABASE CONFIGURATION (New Project)
# =============================================================================
SUPABASE_URL=https://rmymvrifwvqpeffmxkwi.supabase.co
SUPABASE_KEY=sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W
SUPABASE_PUBLISHABLE_KEY=sb_publishable_t9T4pMnQjXytsC1_8yigrg_VEWrTs3W
SUPABASE_SERVICE_KEY=sb_secret_9q0019y231s_eVt9Qgu5iQ_U7v8UcfW
SUPABASE_SECRET_KEY=sb_secret_9q0019y231s_eVt9Qgu5iQ_U7v8UcfW
```

**Note:** The code supports both legacy (`SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`) and new naming (`SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`).

---

## Step 6: Test Authentication Endpoints

### Test User Registration

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "user": {
    "user_id": "...",
    "email": "test@example.com",
    "full_name": "Test User"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Test User Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "user": {
    "user_id": "...",
    "email": "test@example.com",
    "full_name": "Test User"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Step 7: Verify Frontend Authentication

### Check Frontend Configuration

The frontend should be calling:
- `POST /api/auth/login`
- `POST /api/auth/register`

These endpoints should be using the Supabase adapter in the backend.

### Test in Browser

1. **Start frontend:**
   ```bash
   cd symphainy-frontend
   npm run dev
   ```

2. **Navigate to:** http://localhost:3000

3. **Try to log in:**
   - Look for login/register UI
   - Create a test account
   - Verify login works

---

## Step 8: Configure Session Management

### Check Session Token Handling

The backend should:
1. Use Supabase to authenticate users
2. Return Supabase access token to frontend
3. Frontend stores token in localStorage
4. Frontend sends token in API requests

### Verify Token Validation

The backend should validate tokens on protected endpoints:

```python
# Example token validation
from supabase import create_client

def validate_token(access_token: str):
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        user = supabase.auth.get_user(access_token)
        return user
    except Exception as e:
        return None
```

---

## Troubleshooting

### Error: "Invalid API key"

**Fix:**
- Verify keys in Supabase Dashboard match keys in `.env.secrets`
- Make sure you're using the correct project's keys
- Check for typos or extra spaces

### Error: "Email not confirmed"

**Fix:**
- Go to Supabase Dashboard → Authentication → Providers → Email
- Disable "Enable email confirmations" for development
- Or check email inbox for confirmation link

### Error: "User already exists"

**Fix:**
- Check Supabase Dashboard → Authentication → Users
- Delete test user if needed
- Or use a different email

### Error: "RLS policy violation"

**Fix:**
- Check RLS policies are set up correctly
- Verify `auth.uid()` matches `user_id` in tables
- For development, you can temporarily disable RLS:
  ```sql
  ALTER TABLE project_files DISABLE ROW LEVEL SECURITY;
  ```

---

## Success Checklist

- [ ] Supabase project URL verified
- [ ] Supabase keys verified and updated in `.env.secrets`
- [ ] Email authentication enabled in Supabase Dashboard
- [ ] User profiles table created (if needed)
- [ ] RLS policies configured for file management
- [ ] Backend authentication endpoints working
- [ ] Frontend can register new users
- [ ] Frontend can log in existing users
- [ ] Session tokens are stored and sent correctly
- [ ] Protected endpoints validate tokens

---

## Next Steps

Once authentication is working:

1. **Test Playwright tests** - They should now be able to authenticate
2. **Set up OAuth** (optional) - Google, GitHub, etc.
3. **Configure email templates** - Customize welcome emails
4. **Set up password reset** - Enable password reset flow
5. **Add role-based access** - If needed for your use case

---

**Status:** Ready to configure! 🚀





