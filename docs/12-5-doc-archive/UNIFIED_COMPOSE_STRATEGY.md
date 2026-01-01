# Unified Docker Compose Strategy

**Date:** December 2024  
**Status:** 🎯 **STRATEGIC ALIGNMENT WITH OPTION C**

---

## 🧭 The Problem

**Current State:**
- `docker-compose.prod.yml` (backend, frontend) - project: `symphainy_source`
- `docker-compose.infrastructure.yml` (Traefik, ArangoDB, Redis, etc.) - project: `symphainy-platform`
- **Result:** Traefik can't discover backend services (different compose projects)
- **Operational Friction:** Always guessing how to start the platform

**Root Cause:**
- Docker Compose creates separate projects by default
- Traefik's Docker provider only watches containers in its own project
- No single source of truth for "how to start everything"

---

## ✅ The Solution: Unified Compose Project

### **Strategy: One Compose File for Development/Staging**

**For Development/Staging (MVP → Alpha):**
- **Single unified `docker-compose.yml`** that includes:
  - Infrastructure services (Traefik, ArangoDB, Redis, Consul, Meilisearch, etc.)
  - Application services (Backend, Frontend)
  - All on the same network, same project
  - Traefik automatically discovers all services

**For Production (Option C - Fully Hosted):**
- **Replace infrastructure services with managed equivalents:**
  - Redis → GCP MemoryStore or Upstash
  - ArangoDB → ArangoDB Oasis
  - Meilisearch → Meilisearch Cloud
  - Supabase → Supabase Cloud (already using)
  - Telemetry → Grafana Cloud
- **Keep application containers** (Backend, Frontend) - deploy to Cloud Run or GKE
- **Traefik** → Replace with Cloud Load Balancer or Cloud Run's built-in routing

---

## 🎯 Alignment with Hybrid Cloud Strategy

### **Option C: Fully Hosted "Everything as a Service"**

| Stage | Infrastructure | Application | Orchestration |
|-------|---------------|-------------|---------------|
| **Development/Staging** | Unified `docker-compose.yml` (all services) | Containers in compose | Docker Compose |
| **Production (Option C)** | Managed services (MemoryStore, ArangoDB Oasis, etc.) | Containers on Cloud Run/GKE | Cloud Run / GKE |

**Key Insight:**
- **Development/Staging:** One unified compose project = stability, predictability, easy testing
- **Production:** Option C = managed infrastructure + containerized applications
- **No conflict:** Unified compose is the **development foundation** that makes Option C production deployment **easier**

---

## 📋 Implementation Plan

### **Phase 1: Create Unified Compose File**

**File:** `docker-compose.yml` (root of `symphainy_source/`)

**Structure:**
```yaml
services:
  # Infrastructure Services (from docker-compose.infrastructure.yml)
  traefik:
    # ... Traefik config ...
  
  arangodb:
    # ... ArangoDB config ...
  
  redis:
    # ... Redis config ...
  
  consul:
    # ... Consul config ...
  
  meilisearch:
    # ... Meilisearch config ...
  
  # ... other infrastructure services ...
  
  # Application Services (from docker-compose.prod.yml)
  backend:
    depends_on:
      - traefik
      - arangodb
      - redis
      - consul
    # ... Backend config ...
  
  frontend:
    depends_on:
      - backend
    # ... Frontend config ...
```

**Benefits:**
- ✅ Single command to start everything: `docker-compose up`
- ✅ Traefik automatically discovers all services
- ✅ Proper dependency ordering
- ✅ Single network, single project
- ✅ No more guessing

---

### **Phase 2: Update Scripts and Documentation**

**Startup Script:**
```bash
#!/bin/bash
# scripts/start-platform.sh

cd "$(dirname "$0")/.."
docker-compose up -d

echo "✅ Platform starting..."
echo "   - Frontend: http://localhost"
echo "   - Backend API: http://localhost/api"
echo "   - Traefik Dashboard: http://localhost:8080"
```

**Stop Script:**
```bash
#!/bin/bash
# scripts/stop-platform.sh

cd "$(dirname "$0")/.."
docker-compose down
```

---

### **Phase 3: Production Deployment (Option C)**

**When ready for production:**

1. **Create `docker-compose.production.yml`** (overrides for managed services):
   ```yaml
   services:
     backend:
       environment:
         - REDIS_URL=${GCP_MEMORYSTORE_URL}  # Managed Redis
         - ARANGO_URL=${ARANGODB_OASIS_URL}   # Managed ArangoDB
         - MEILISEARCH_URL=${MEILISEARCH_CLOUD_URL}  # Managed Meilisearch
     # No infrastructure services - all managed
   ```

2. **Deploy to Cloud Run:**
   ```bash
   # Build and push containers
   docker build -t gcr.io/PROJECT/backend:latest ./symphainy-platform
   docker push gcr.io/PROJECT/backend:latest
   
   # Deploy to Cloud Run
   gcloud run deploy symphainy-backend \
     --image gcr.io/PROJECT/backend:latest \
     --platform managed \
     --region us-central1
   ```

3. **Use Cloud Load Balancer** instead of Traefik (or Cloud Run's built-in routing)

---

## 🚀 Migration Path

### **Step 1: Create Unified Compose (Now)**
- Merge `docker-compose.infrastructure.yml` + `docker-compose.prod.yml`
- Test locally
- Update documentation

### **Step 2: Stabilize Development (Next)**
- Use unified compose for all development/staging
- Create startup/stop scripts
- Document the "one command" startup

### **Step 3: Production Deployment (Future - Option C)**
- Replace infrastructure services with managed equivalents
- Deploy application containers to Cloud Run/GKE
- Use Cloud Load Balancer for routing

---

## ✅ Benefits

1. **Operational Clarity:**
   - One command to start: `docker-compose up`
   - No more guessing which compose file to use
   - Traefik automatically discovers everything

2. **Development Velocity:**
   - Faster iteration (everything starts together)
   - Easier debugging (all services visible)
   - Consistent environment

3. **Production Ready:**
   - Unified compose = stable foundation
   - Option C migration = swap infrastructure services for managed
   - Application containers remain unchanged

4. **Team Alignment:**
   - Single source of truth
   - Clear documentation
   - Predictable startup sequence

---

## 🎯 Recommendation

**✅ YES - Create unified compose project now**

**Why:**
- Solves immediate operational friction (Traefik discovery, startup confusion)
- Aligns perfectly with Option C (dev/staging unified, production managed)
- No downside - can still use separate files for specific scenarios
- Makes production migration easier (stable foundation)

**Next Steps:**
1. Create unified `docker-compose.yml`
2. Test locally
3. Update startup scripts
4. Document the new approach

---

## 📝 Notes

- **Keep existing files** as reference/backup initially
- **Gradually migrate** scripts and documentation
- **Option C production** doesn't require changing the unified compose - it's for dev/staging
- **Production** will use managed services + Cloud Run/GKE, not compose files

