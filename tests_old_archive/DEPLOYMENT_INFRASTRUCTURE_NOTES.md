# Deployment Infrastructure Notes

**Date:** December 2024  
**Purpose:** Clarify infrastructure services and dependency management

---

## 🐳 **Infrastructure Services**

The platform requires several infrastructure services that must be running before the application:

### **Services in `docker-compose.infrastructure.yml`:**

1. **ArangoDB** (Port 8529)
   - Graph database for metadata and telemetry
   - Required for: Platform metadata, session data, journey state

2. **Redis** (Port 6379)
   - Cache and message broker
   - Required for: Caching, Celery task queue, session storage

3. **Consul** (Port 8500)
   - Service discovery and KV store
   - Required for: Service registration, configuration management

4. **Meilisearch** (Port 7700)
   - Search engine for knowledge discovery
   - Required for: Content search, file indexing

5. **Celery Worker**
   - Background task processing
   - Required for: Async tasks, file processing, LLM calls

6. **Celery Beat**
   - Task scheduler
   - Required for: Scheduled tasks, periodic jobs

7. **Tempo** (Port 3200)
   - Distributed tracing backend
   - Required for: Request tracing, performance monitoring

8. **OpenTelemetry Collector** (Ports 4317, 4318)
   - Observability data collection
   - Required for: Metrics, traces, logs aggregation

9. **Grafana** (Port 3100)
   - Visualization and monitoring
   - Required for: Dashboards, metrics visualization

10. **OPA** (Port 8181)
    - Policy engine
    - Required for: Access control, policy enforcement

---

## 📦 **Dependency Management**

### **Backend Dependencies (Python):**

**In Docker (Automatic):**
- Dependencies are installed during `docker-compose build`
- Dockerfile uses Poetry: `poetry install --no-interaction --no-ansi --no-root`
- No manual installation needed

**Outside Docker (Manual):**
- Use `startup.sh` script which handles:
  1. Poetry installation
  2. Dependency installation from `pyproject.toml`
  3. Environment setup

**Files:**
- `pyproject.toml` - Poetry dependency definitions (primary)
- `requirements.txt` - Pip fallback (if Poetry unavailable)
- `poetry.lock` - Locked dependency versions

### **Frontend Dependencies (Node.js):**

**In Docker (Automatic):**
- Dependencies installed during `docker-compose build`
- Dockerfile runs: `npm ci --only=production`
- No manual installation needed

**Outside Docker (Manual):**
```bash
cd symphainy-frontend
npm install
npm run build
```

---

## 🚀 **Startup Order**

### **Correct Startup Sequence:**

1. **Infrastructure Services** (docker-compose.infrastructure.yml)
   ```bash
   docker-compose -f docker-compose.infrastructure.yml up -d
   ```
   - Start: ArangoDB, Redis, Consul, Meilisearch, Celery, etc.
   - Wait: 20-30 seconds for services to be healthy

2. **Application Services** (docker-compose.prod.yml)
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```
   - Start: Backend, Frontend
   - Depends on: Infrastructure services being healthy

### **Using Startup Script (Alternative):**

If you prefer to use the `startup.sh` script (for non-Docker deployment):

```bash
cd symphainy-platform
./startup.sh --background
```

This script:
- ✅ Handles Poetry installation
- ✅ Installs dependencies
- ✅ Starts infrastructure (if not already running)
- ✅ Starts backend in proper order

**Note:** For Docker-based deployment (recommended), use `vm-staging-deploy.sh` which handles everything automatically.

---

## 🔧 **Deployment Script Behavior**

The updated `vm-staging-deploy.sh` now:

1. **Starts Infrastructure First**
   ```bash
   docker-compose -f docker-compose.infrastructure.yml up -d
   ```

2. **Waits for Infrastructure**
   ```bash
   sleep 20  # Wait for services to be healthy
   ```

3. **Stops Old Application Containers**
   ```bash
   docker-compose -f docker-compose.prod.yml down
   ```

4. **Builds New Application Containers**
   ```bash
   docker-compose -f docker-compose.prod.yml build --no-cache
   ```
   - This installs dependencies automatically (Poetry in Dockerfile)

5. **Starts Application Containers**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

---

## ✅ **Verification Checklist**

After deployment, verify all services:

```bash
# Infrastructure services
docker-compose -f docker-compose.infrastructure.yml ps

# Application services
docker-compose -f docker-compose.prod.yml ps

# Check specific services
curl http://localhost:8529/_api/version  # ArangoDB
redis-cli ping  # Redis
curl http://localhost:8500/v1/status/leader  # Consul
curl http://localhost:7700/health  # Meilisearch
curl http://localhost:8000/health  # Backend
curl http://localhost:3000  # Frontend
```

---

## 📝 **Environment Variables**

### **Backend (.env.secrets):**
- Already exists (you confirmed)
- Contains: Database passwords, API keys, Supabase credentials

### **Frontend (.env or .env.local or .env.production):**
- You've updated both `.env` and `.env.local`
- For production, `.env.production` or `.env.production.local` is recommended
- Next.js precedence: `.env.production.local` > `.env.production` > `.env.local` > `.env`

---

## 🎯 **Summary**

1. **Infrastructure:** Start via `docker-compose.infrastructure.yml` (handled by deployment script)
2. **Dependencies:** Installed automatically during Docker build (Poetry in Dockerfile)
3. **Startup Script:** Available for non-Docker deployment, but Docker is recommended
4. **Environment Variables:** Already configured (just verify they're on VM)

**The deployment script now handles everything in the correct order!**

---

**Last Updated:** December 2024


