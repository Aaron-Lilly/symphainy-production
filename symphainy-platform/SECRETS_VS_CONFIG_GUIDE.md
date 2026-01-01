# Secrets vs Config Guide

## 🎯 What Goes Where?

### **`.env.secrets`** (Secrets Only)
Contains **sensitive values** that should never be committed:
- ✅ **Passwords**: `ARANGO_PASS`, `REDIS_PASSWORD`, `DATABASE_PASSWORD`
- ✅ **API Keys**: `LLM_OPENAI_API_KEY`, `GOOGLE_API_KEY`, `STRIPE_SECRET_KEY`
- ✅ **Service Keys**: `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`, `SUPABASE_ANON_KEY`
- ✅ **Credentials**: `GCS_CREDENTIALS_JSON` (service account JSON)
- ✅ **Secret Keys**: `SECRET_KEY`, `JWT_SECRET`
- ✅ **Tokens**: `STRIPE_WEBHOOK_SECRET`, `CONSUL_TOKEN`

### **`config/development.env`** (Non-Sensitive Config)
Contains **non-sensitive configuration** that can be committed:
- ✅ **URLs**: `ARANGO_URL`, `REDIS_URL` (if not sensitive)
- ✅ **Hosts/Ports**: `REDIS_HOST`, `REDIS_PORT`, `ARANGO_HOSTS`
- ✅ **Database Names**: `ARANGO_DB`, `ARANGO_DATABASE`
- ✅ **Usernames**: `ARANGO_USER` (if not sensitive)
- ✅ **Settings**: `API_PORT`, `LOG_LEVEL`, `DEBUG_MODE`, etc.

### **`config/infrastructure.yaml`** (Infrastructure Config)
Contains **infrastructure settings**:
- ✅ **Project IDs**: `GCS_PROJECT_ID`
- ✅ **Bucket Names**: `GCS_BUCKET_NAME`
- ✅ **Service Endpoints**: Base URLs, ports
- ✅ **Infrastructure Settings**: Timeouts, retries, etc.

---

## 📋 Current Status

### **What's Currently in `.env.secrets` (Should Move to Config)**

These should be moved to `config/development.env`:
- `ARANGO_URL=http://localhost:8529` → Move to `config/development.env`
- `ARANGO_DB=symphainy_metadata` → Move to `config/development.env`
- `ARANGO_USER=root` → Move to `config/development.env` (if not sensitive)
- `REDIS_HOST=localhost` → Move to `config/development.env`
- `REDIS_PORT=6379` → Move to `config/development.env`
- `REDIS_DB=0` → Move to `config/development.env`
- `REDIS_URL=redis://localhost:6379` → Move to `config/development.env`
- `GCS_PROJECT_ID=symphainymvp-devbox` → Move to `config/infrastructure.yaml`
- `GCS_BUCKET_NAME=symphainy-bucket-2025` → Move to `config/infrastructure.yaml`

### **What Should Stay in `.env.secrets`**

- `ARANGO_PASS=` (password)
- `REDIS_PASSWORD=` (password)
- `SUPABASE_URL=` (contains project-specific info, could stay or move)
- `SUPABASE_KEY=`, `SUPABASE_SERVICE_KEY=` (service keys)
- `SECRET_KEY=`, `JWT_SECRET=` (secret keys)
- `LLM_OPENAI_API_KEY=` (API key)
- `GOOGLE_API_KEY=` (API key)
- `GCS_CREDENTIALS_JSON=` (credentials)
- `STRIPE_SECRET_KEY=`, `STRIPE_PUBLIC_KEY=` (API keys)

---

## ⚠️ Migration Considerations

**Before Moving Values**:
1. Check if code reads these from `.env.secrets` directly
2. Verify `UnifiedConfigurationManager` loads from both sources
3. Test that values are still accessible after moving

**If Code Depends on `.env.secrets`**:
- The `UnifiedConfigurationManager` loads `.env.secrets` first (Layer 1)
- Then loads `config/development.env` (Layer 2)
- Values in `.env.secrets` override values in config files
- So moving values should work, but test first!

---

## ✅ Recommended Action

**Option 1: Keep Current Structure** (Safest)
- Keep URLs/hosts/ports in `.env.secrets` for now
- Document that they should be moved eventually
- Focus on fixing the GCS credentials issue first

**Option 2: Move Non-Sensitive Values** (Cleaner)
- Move URLs/hosts/ports to `config/development.env`
- Move project/bucket names to `config/infrastructure.yaml`
- Keep only secrets in `.env.secrets`
- Test thoroughly after moving

**Recommendation**: Start with **Option 1** (keep current structure), then migrate to **Option 2** in a separate task after verifying everything works.






