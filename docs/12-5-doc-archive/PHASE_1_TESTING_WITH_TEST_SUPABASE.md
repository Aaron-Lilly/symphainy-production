# Phase 1 Testing with Test Supabase Project

**Date:** December 2024  
**Status:** 📋 **TEST SUPABASE INTEGRATION COMPLETE**

---

## 🎯 Overview

Phase 1 Security Integration tests now support using a **test Supabase project** to avoid rate limiting and ensure isolated testing.

---

## 🔧 Configuration

### **Option 1: Environment Variables (Recommended)**

Set these environment variables before running tests:

```bash
# Test Supabase Project Configuration
export TEST_SUPABASE_URL="https://your-test-project.supabase.co"
export TEST_SUPABASE_ANON_KEY="your-test-anon-key"
export TEST_SUPABASE_EMAIL="test@symphainy.com"
export TEST_SUPABASE_PASSWORD="test_password_123"
```

### **Option 2: Use Existing Token**

If you already have a JWT token:

```bash
export SYMPHAINY_API_TOKEN="your_existing_jwt_token"
```

### **Option 3: Fallback to Production**

If neither test Supabase nor token is provided, tests will skip token-based tests.

---

## 🧪 Test Behavior

### **Automatic Token Retrieval**

The Phase 1 test script will:

1. **Check for existing token:**
   - If `SYMPHAINY_API_TOKEN` is set, use it

2. **Try to get test token from Supabase:**
   - If `TEST_SUPABASE_URL` and `TEST_SUPABASE_ANON_KEY` are set
   - Attempts to sign in with `TEST_SUPABASE_EMAIL` and `TEST_SUPABASE_PASSWORD`
   - If user doesn't exist, attempts to sign up first
   - Returns JWT token if successful

3. **Skip token tests if no token available:**
   - Invalid token and missing token tests still run
   - Valid token and tenant-aware routing tests are skipped

---

## 🚀 Running Tests

### **With Test Supabase Project:**

```bash
cd /home/founders/demoversion/symphainy_source

# Set test Supabase credentials
export TEST_SUPABASE_URL="https://your-test-project.supabase.co"
export TEST_SUPABASE_ANON_KEY="your-test-anon-key"
export TEST_SUPABASE_EMAIL="test@symphainy.com"
export TEST_SUPABASE_PASSWORD="test_password_123"

# Run Phase 1 tests
python3 scripts/test_phase1_security_integration.py
```

### **With Existing Token:**

```bash
cd /home/founders/demoversion/symphainy_source

# Set existing token
export SYMPHAINY_API_TOKEN="your_jwt_token"

# Run Phase 1 tests
python3 scripts/test_phase1_security_integration.py
```

### **Combined Tests (Phase 1 + Phase 2):**

```bash
cd /home/founders/demoversion/symphainy_source

# Set test Supabase credentials
export TEST_SUPABASE_URL="https://your-test-project.supabase.co"
export TEST_SUPABASE_ANON_KEY="your-test-anon-key"
export TEST_SUPABASE_EMAIL="test@symphainy.com"
export TEST_SUPABASE_PASSWORD="test_password_123"

# Run both phases
python3 scripts/test_phases_1_and_2.py
```

---

## 📋 Test Supabase Project Setup

### **1. Create Test Project in Supabase**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Name: `symphainy-test` (or similar)
4. Region: Same as production (for consistency)
5. Database password: Generate and save
6. Wait for project to provision (~2 minutes)

### **2. Get Test Credentials**

1. Navigate to: **Settings** → **API**
2. Copy:
   - **Project URL** → `TEST_SUPABASE_URL`
   - **anon/public key** → `TEST_SUPABASE_ANON_KEY`
   - **service_role key** → `TEST_SUPABASE_SERVICE_KEY` (optional, for admin operations)

### **3. Create Test User (Optional)**

The test script will automatically create a test user if it doesn't exist, but you can also create one manually:

1. Go to **Authentication** → **Users**
2. Click "Add User"
3. Email: `test@symphainy.com` (or your preferred test email)
4. Password: `test_password_123` (or your preferred password)
5. Auto Confirm User: ✅ (for testing)

---

## 🔍 Test Output

### **Successful Test Token Retrieval:**

```
🔍 No token provided, attempting to get test token from Supabase...
   🔐 Getting test token from Supabase: https://your-test-project.supabase.co
   ✅ Test token obtained successfully
   ✅ Using test token from Supabase
```

### **Test User Creation:**

```
🔍 No token provided, attempting to get test token from Supabase...
   🔐 Getting test token from Supabase: https://your-test-project.supabase.co
   ⚠️  Sign in failed (user may not exist), attempting sign up...
   ✅ Test user created and token obtained
   ✅ Using test token from Supabase
```

### **Missing Configuration:**

```
🔍 No token provided, attempting to get test token from Supabase...
   ⚠️  Test Supabase credentials not configured
   Set TEST_SUPABASE_URL and TEST_SUPABASE_ANON_KEY environment variables
   ⚠️  Skipping valid token test (no token available)
```

---

## ✅ Benefits of Test Supabase Project

1. **No Rate Limiting:**
   - Isolated test environment
   - No impact on production rate limits

2. **Clean Test Data:**
   - Separate database
   - Can reset without affecting production

3. **Safe Testing:**
   - No risk of affecting production users
   - Can test edge cases safely

4. **Automated Token Retrieval:**
   - Test script automatically gets tokens
   - No manual token management needed

---

## 🛠️ Troubleshooting

### **Token Retrieval Fails:**

1. **Check Supabase URL:**
   ```bash
   echo $TEST_SUPABASE_URL
   # Should be: https://your-project-ref.supabase.co
   ```

2. **Check Anon Key:**
   ```bash
   echo $TEST_SUPABASE_ANON_KEY
   # Should be a JWT token starting with eyJ...
   ```

3. **Check Email/Password:**
   ```bash
   echo $TEST_SUPABASE_EMAIL
   echo $TEST_SUPABASE_PASSWORD
   ```

4. **Verify User Exists:**
   - Go to Supabase Dashboard → Authentication → Users
   - Check if test user exists
   - If not, the script will try to create it

### **Sign Up Fails:**

- Check if email confirmation is required
- Set "Auto Confirm User" in Supabase settings
- Check Supabase project settings for email restrictions

### **Token Validation Fails:**

- Verify backend is using the same Supabase project
- Check if backend has correct Supabase credentials
- Verify ForwardAuth endpoint is working

---

## 📝 Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `TEST_SUPABASE_URL` | Test Supabase project URL | Yes (for auto token) | `https://abc123.supabase.co` |
| `TEST_SUPABASE_ANON_KEY` | Test Supabase anon key | Yes (for auto token) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `TEST_SUPABASE_EMAIL` | Test user email | Yes (for auto token) | `test@symphainy.com` |
| `TEST_SUPABASE_PASSWORD` | Test user password | Yes (for auto token) | `test_password_123` |
| `SYMPHAINY_API_TOKEN` | Existing JWT token | Alternative to auto token | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |
| `SYMPHAINY_API_URL` | Backend API URL | No | `http://localhost/api` |

---

**Last Updated:** December 2024  
**Status:** Ready for Testing with Test Supabase Project




