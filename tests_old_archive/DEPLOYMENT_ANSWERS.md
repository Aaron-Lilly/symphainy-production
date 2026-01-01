# Deployment Questions - Answers

**Date:** December 2024

---

## 1. ✅ Frontend Environment Variables (`.env` and `.env.local`)

**Your Setup:**
- You have both `.env` and `.env.local` updated with:
  - `NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103:8000`
  - `NEXT_PUBLIC_SUPABASE_URL=https://rmymvrifwvqpeffmxkwi.supabase.co`
  - `NEXT_SUPABASE_PUBLISHABLE_KEY=...`
  - `NEXT_SUPABASE_SECRET_KEY=...`

**Answer:** ✅ **This is Perfect!**

**Next.js Environment Variable Precedence:**
1. `.env.production.local` (highest priority for production)
2. `.env.production` (production-specific)
3. `.env.local` (local overrides - you have this ✅)
4. `.env` (default - you have this ✅)

**For Production:**
- Your `.env.local` will be used in production (it's in the precedence chain)
- However, for best practice, consider creating `.env.production` or `.env.production.local` on the VM
- But your current setup will work fine!

**Note:** Make sure these files are on the VM at:
```
/home/founders/demoversion/symphainy_source/symphainy-frontend/.env
/home/founders/demoversion/symphainy_source/symphainy-frontend/.env.local
```

---

## 2. ✅ Infrastructure Startup Script

**Your Question:** Should we use the `startup.sh` script for infrastructure startup?

**Answer:** ✅ **The deployment script now handles this automatically!**

**What Changed:**
- Updated `vm-staging-deploy.sh` to start infrastructure services first
- Uses `docker-compose.infrastructure.yml` to start all services in proper order
- No need to manually run `startup.sh` for Docker-based deployment

**Infrastructure Services Started:**
1. ✅ ArangoDB (database)
2. ✅ Redis (cache/message broker)
3. ✅ Consul (service discovery)
4. ✅ Meilisearch (search engine)
5. ✅ Celery Worker (background tasks)
6. ✅ Celery Beat (task scheduler)
7. ✅ Tempo (distributed tracing)
8. ✅ OpenTelemetry Collector (observability)
9. ✅ Grafana (monitoring)
10. ✅ OPA (policy engine)

**When to Use `startup.sh`:**
- If you're running **outside Docker** (non-containerized deployment)
- For local development
- The script handles Poetry installation and dependency management

**For Docker Deployment (Recommended):**
- Use `vm-staging-deploy.sh` - it handles everything automatically
- Infrastructure starts first, then application

---

## 3. ✅ Celery, Meilisearch, and Other Services

**Your Question:** Do we need to account for Celery, Meilisearch, or anything else?

**Answer:** ✅ **All accounted for in the updated deployment script!**

**Services Included in `docker-compose.infrastructure.yml`:**
- ✅ **Celery Worker** - Background task processing
- ✅ **Celery Beat** - Task scheduler
- ✅ **Meilisearch** - Search engine
- ✅ **ArangoDB** - Database
- ✅ **Redis** - Cache and message broker
- ✅ **Consul** - Service discovery
- ✅ **Tempo** - Distributed tracing
- ✅ **OpenTelemetry Collector** - Observability
- ✅ **Grafana** - Monitoring dashboards
- ✅ **OPA** - Policy engine

**The deployment script now:**
1. Starts all infrastructure services first
2. Waits for them to be healthy (20 seconds)
3. Then starts application services (backend, frontend)

**Nothing is missing!** ✅

---

## 4. ✅ Dependencies (Poetry/pyproject.toml/requirements.txt)

**Your Question:** What about installing dependencies?

**Answer:** ✅ **Handled automatically in Docker!**

### **Backend Dependencies:**

**In Docker (Automatic):**
- Dependencies are installed during `docker-compose build`
- Dockerfile uses Poetry: `poetry install --no-interaction --no-ansi --no-root`
- Reads from `pyproject.toml` and `poetry.lock`
- No manual installation needed ✅

**Files Used:**
- `pyproject.toml` - Primary dependency definitions (Poetry)
- `poetry.lock` - Locked versions
- `requirements.txt` - Fallback (if Poetry unavailable)

**Outside Docker (If Needed):**
- Use `startup.sh` script which handles:
  1. Poetry installation
  2. `poetry install` from `pyproject.toml`
  3. Environment setup

### **Frontend Dependencies:**

**In Docker (Automatic):**
- Dependencies installed during `docker-compose build`
- Dockerfile runs: `npm ci --only=production`
- Reads from `package.json` and `package-lock.json`
- No manual installation needed ✅

**Outside Docker (If Needed):**
```bash
cd symphainy-frontend
npm install
npm run build
```

### **Summary:**
- ✅ **Docker deployment:** Dependencies installed automatically during build
- ✅ **No manual steps needed** for Docker-based deployment
- ✅ **Deployment script handles everything**

---

## 📋 **Updated Deployment Process**

The `vm-staging-deploy.sh` script now does:

1. **Pull latest code**
2. **Start Infrastructure Services** (NEW!)
   - ArangoDB, Redis, Consul, Meilisearch, Celery, etc.
   - Waits for services to be healthy
3. **Stop old application containers**
4. **Build new containers** (installs dependencies automatically)
5. **Start application containers**
6. **Health checks**

**Everything is automated!** ✅

---

## ✅ **What You Need to Do**

### **Before First Deployment:**

1. ✅ **Verify `.env.secrets` is on VM** (you confirmed it exists)
2. ✅ **Verify frontend `.env` and `.env.local` are on VM** (you've updated them)
3. ✅ **Run deployment script:**
   ```bash
   ssh founders@35.215.64.103
   cd /home/founders/demoversion/symphainy_source
   ./scripts/vm-staging-deploy.sh
   ```

### **That's It!**

The script handles:
- ✅ Infrastructure startup (all services)
- ✅ Dependency installation (Poetry/npm in Docker)
- ✅ Service ordering (infrastructure first, then application)
- ✅ Health checks

---

## 🎯 **Summary**

1. **Frontend env vars:** ✅ Your setup is perfect (`.env` and `.env.local` both work)
2. **Infrastructure startup:** ✅ Now handled automatically by deployment script
3. **Celery/Meilisearch/etc:** ✅ All included and started automatically
4. **Dependencies:** ✅ Installed automatically during Docker build

**No manual steps needed!** The deployment script handles everything in the correct order.

---

**Last Updated:** December 2024


