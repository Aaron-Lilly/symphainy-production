# Configuration Pattern - Secrets vs Environment Config

**Date:** December 2024  
**Purpose:** Document the pattern for what goes in `.env.secrets` vs `config/production.env`

---

## 🎯 **Pattern: Project-Specific = Secrets**

### **Principle:**
If it's **project-specific** and **unique to your deployment**, it goes in `.env.secrets`, even if it's not a cryptographic secret.

### **Rationale:**
- Project-specific values shouldn't be committed to version control
- They're unique to your project/deployment
- They shouldn't be shared publicly
- Consistent pattern makes it clear where to find project-specific config

---

## 📋 **What Goes in `.env.secrets`**

### **Supabase (Example Pattern):**
- `SUPABASE_URL` - Project-specific, unique to your Supabase project
- `SUPABASE_PUBLISHABLE_KEY` - Project-specific, unique to your project
- `SUPABASE_SECRET_KEY` - Cryptographic secret

### **GCS (Following Same Pattern):**
- `GCS_PROJECT_ID` - Project-specific, unique to your GCP project
- `GCS_BUCKET_NAME` - Project-specific, unique to your deployment
- `GCS_CREDENTIALS_JSON` - Cryptographic secret (service account credentials)

### **Other Examples:**
- Database connection strings (project-specific)
- API keys (project-specific)
- Service URLs (project-specific)
- Any unique identifiers for your deployment

---

## 📋 **What Goes in `config/production.env`**

### **Non-Project-Specific Configuration:**
- Default values that can be overridden
- Configuration that's the same across deployments
- Business logic settings
- Feature flags
- Timeouts, retry counts, pool sizes
- Logging levels
- Rate limiting settings

### **Examples:**
```env
# These are NOT project-specific
API_PORT=8000
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=100
DATABASE_POOL_SIZE=20
HEALTH_CHECK_INTERVAL=60
```

---

## 🔄 **Configuration Precedence**

The `UnifiedConfigurationManager` loads configuration in this order (later overrides earlier):

1. **Secrets Layer** (`.env.secrets`) - Highest precedence
2. **Environment Layer** (`config/production.env`)
3. **Business Logic Layer** (`config/business-logic.yaml`)
4. **Defaults Layer** (built-in defaults)

**Result:** Secrets always win, which is correct for project-specific values.

---

## ✅ **Benefits of This Pattern**

1. **Consistency:** Same pattern for all project-specific values
2. **Security:** Project-specific values not in version control
3. **Clarity:** Clear separation between project-specific and generic config
4. **Flexibility:** Easy to override with environment variables if needed
5. **Maintainability:** One place to look for project-specific values

---

## 📝 **Example `.env.secrets` Structure**

```env
# Supabase (Project-Specific)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=your-publishable-key
SUPABASE_SECRET_KEY=your-secret-key

# GCS (Project-Specific)
GCS_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-gcs-bucket-name
GCS_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"..."}

# Database (Project-Specific)
DATABASE_HOST=your-db-host
DATABASE_PASSWORD=your-db-password

# Other Project-Specific Secrets
API_KEY=your-api-key
SERVICE_URL=https://your-service.com
```

---

## 🚫 **Anti-Patterns to Avoid**

### **❌ Don't Put Project-Specific Values in `config/production.env`:**
```env
# BAD - This is project-specific, should be in .env.secrets
GCS_PROJECT_ID=symphainymvp-devbox
GCS_BUCKET_NAME=symphainy-bucket-2025
SUPABASE_URL=https://rmymvrifwvqpeffmxkwi.supabase.co
```

### **✅ Do Put Generic Configuration in `config/production.env`:**
```env
# GOOD - These are generic, not project-specific
API_PORT=8000
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=100
```

---

## 🔍 **How to Identify Project-Specific Values**

Ask yourself:
1. **Is this unique to my project/deployment?** → Secrets
2. **Would this be different for another team's deployment?** → Secrets
3. **Is this a generic setting that applies to all deployments?** → Config file
4. **Is this a cryptographic secret?** → Always secrets

---

**Last Updated:** December 2024

