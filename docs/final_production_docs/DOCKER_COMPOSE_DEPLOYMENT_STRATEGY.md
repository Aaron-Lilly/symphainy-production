# Docker Compose & Containerized Deployment Strategy

**Date:** January 2025  
**Status:** 🎯 **STRATEGIC ALIGNMENT - PHASE 1.3 & PHASE 2**

---

## 🎯 Strategic Goals

1. **Phase 1.3:** Convert all docker-compose files to environment variable-based (eliminate hardcoded values)
2. **Phase 2:** Create containerized deployment scripts for GCS VM that prove Option C pattern viability
3. **Alignment:** Ensure docker-compose and deployment scripts work together seamlessly

---

## 📋 Current State Analysis

### Issues Identified

1. **Hardcoded Values:**
   - IP addresses: `35.215.64.103` (hardcoded in multiple places)
   - Port numbers: Some hardcoded, some use environment variables
   - Service URLs: Mixed hardcoded and environment-based

2. **Multiple Compose Files:**
   - `docker-compose.yml` (unified - good)
   - `docker-compose.prod.yml` (production-like testing)
   - `docker-compose.infrastructure.yml` (infrastructure only)
   - `docker-compose.test.yml` (testing)
   - `docker-compose.ci.yml` (CI/CD)

3. **Inconsistent Environment Variable Usage:**
   - Some services use `${VAR:-default}`, others hardcode
   - Frontend build args hardcoded
   - Traefik configuration partially hardcoded

---

## ✅ Solution: Unified Environment-Based Architecture

### Strategy Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Environment Variables                      │
│  (.env.secrets, .env.development, .env.staging, .env.prod)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              docker-compose.yml (Base)                       │
│  - All values from environment variables                    │
│  - No hardcoded IPs, ports, or URLs                         │
│  - Supports: development, staging, production                │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌───────────────────────┐          ┌──────────────────────────┐
│  docker-compose.yml   │          │ docker-compose.option-c.yml│
│  (Development/Staging)│          │ (Option C - Managed Services)│
│  - All infrastructure │          │ - Replace infrastructure  │
│  - All application    │          │   with managed services   │
│  - Local containers   │          │ - Keep application only   │
└───────────────────────┘          └──────────────────────────┘
        ↓                                       ↓
┌─────────────────────────────────────────────────────────────┐
│              Deployment Scripts (GCS VM)                     │
│  - deploy.sh (development/staging)                          │
│  - deploy-option-c.sh (Option C pattern)                    │
│  - Uses docker-compose files above                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

```
symphainy_source/
├── docker-compose.yml                    # Unified base (env-based)
├── docker-compose.option-c.yml          # Option C pattern (managed services)
├── .env.development                      # Development environment
├── .env.staging                          # Staging environment
├── .env.production                       # Production environment (template)
├── scripts/
│   ├── deploy/
│   │   ├── deploy.sh                    # Standard deployment
│   │   ├── deploy-option-c.sh           # Option C deployment
│   │   ├── validate-env.sh              # Environment validation
│   │   └── health-check.sh              # Post-deployment health check
│   └── docker/
│       ├── build-all.sh                 # Build all images
│       └── cleanup.sh                   # Cleanup old containers/images
└── symphainy-platform/
    └── .env.secrets                      # Secrets (gitignored)
```

---

## 🔧 Environment Variable Categories

### 1. Network & Routing

```bash
# Frontend/Backend URLs
FRONTEND_URL=http://localhost                    # Development
FRONTEND_URL=https://app.symphainy.com          # Production
API_URL=http://localhost                        # Development
API_URL=https://api.symphainy.com               # Production

# Traefik Configuration
TRAEFIK_HTTP_PORT=80
TRAEFIK_HTTPS_PORT=443
TRAEFIK_DASHBOARD_PORT=8080
TRAEFIK_DASHBOARD_ENABLED=true                  # false in production

# Network
DOCKER_NETWORK_NAME=smart_city_net
```

### 2. Infrastructure Services

```bash
# Consul
CONSUL_DATACENTER=dc1
CONSUL_HTTP_PORT=8500
CONSUL_DNS_PORT=8600

# Redis
REDIS_HOST=redis                                # Container name or external
REDIS_PORT=6379
REDIS_PASSWORD=                                  # Optional

# ArangoDB
ARANGO_HOST=arangodb                            # Container name or external
ARANGO_PORT=8529
ARANGO_DB=symphainy_metadata
ARANGO_USER=root
ARANGO_PASS=                                     # Optional

# Meilisearch
MEILI_MASTER_KEY=                               # Required
MEILI_PORT=7700

# Observability
TEMPO_PORT=3200
OTEL_COLLECTOR_GRPC_PORT=4317
OTEL_COLLECTOR_HTTP_PORT=4318
GRAFANA_PORT=3100
LOKI_PORT=3101
```

### 3. Application Configuration

```bash
# Backend
ENVIRONMENT=development                         # development|staging|production
LOG_LEVEL=INFO
PORT=8000

# Frontend
NODE_ENV=development                            # development|production
NEXT_PUBLIC_API_URL=${API_URL}                 # Inherits from API_URL
NEXT_PUBLIC_FRONTEND_URL=${FRONTEND_URL}       # Inherits from FRONTEND_URL

# CORS
CORS_ORIGINS=${FRONTEND_URL}                    # Comma-separated
API_CORS_ORIGINS=${FRONTEND_URL}                # Comma-separated
```

### 4. Option C (Managed Services)

```bash
# Option C: Use managed services instead of containers
OPTION_C_ENABLED=false                          # Enable Option C pattern

# Managed Service URLs (when OPTION_C_ENABLED=true)
REDIS_URL=redis://managed-redis.example.com:6379
ARANGO_URL=https://managed-arango.example.com
MEILISEARCH_URL=https://managed-meilisearch.example.com

# Keep application containers
BACKEND_CONTAINER_ENABLED=true
FRONTEND_CONTAINER_ENABLED=true
CELERY_WORKER_ENABLED=true
```

---

## 🚀 Deployment Scripts

### Standard Deployment (`deploy.sh`)

```bash
#!/bin/bash
# Deploys using docker-compose.yml (all services in containers)

# 1. Validate environment
# 2. Load environment variables
# 3. Build images (if needed)
# 4. Start services
# 5. Health checks
# 6. Report status
```

### Option C Deployment (`deploy-option-c.sh`)

```bash
#!/bin/bash
# Deploys using docker-compose.option-c.yml (managed services + app containers)

# 1. Validate environment (including managed service URLs)
# 2. Load environment variables
# 3. Verify managed services are accessible
# 4. Build application images only
# 5. Start application containers
# 6. Health checks
# 7. Report status
```

---

## 📝 Implementation Plan

### Phase 1.3: Environment Variable Conversion

1. **Audit all docker-compose files**
   - Identify all hardcoded values
   - Map to environment variables

2. **Create unified docker-compose.yml**
   - Replace all hardcoded values with `${VAR:-default}` pattern
   - Use environment file references
   - Support multiple environments

3. **Create docker-compose.option-c.yml**
   - Remove infrastructure services
   - Replace with managed service URLs
   - Keep application containers

4. **Create environment file templates**
   - `.env.development`
   - `.env.staging`
   - `.env.production.example`

### Phase 2: Containerized Deployment

1. **Create deployment scripts**
   - `deploy.sh` (standard)
   - `deploy-option-c.sh` (Option C)
   - `validate-env.sh` (validation)
   - `health-check.sh` (post-deployment)

2. **Create build scripts**
   - `build-all.sh` (build all images)
   - `cleanup.sh` (cleanup old resources)

3. **Documentation**
   - Deployment guide
   - Environment setup guide
   - Option C migration guide

---

## ✅ Success Criteria

1. **No Hardcoded Values:**
   - ✅ All IP addresses from environment variables
   - ✅ All ports from environment variables
   - ✅ All URLs from environment variables

2. **Environment Support:**
   - ✅ Development environment works
   - ✅ Staging environment works
   - ✅ Production environment works
   - ✅ Option C pattern works

3. **Deployment Scripts:**
   - ✅ Standard deployment works on GCS VM
   - ✅ Option C deployment works on GCS VM
   - ✅ Health checks pass
   - ✅ Services accessible

4. **Documentation:**
   - ✅ Environment variables documented
   - ✅ Deployment process documented
   - ✅ Option C pattern documented

---

## 🎯 Next Steps

1. Create unified `docker-compose.yml` with environment variables
2. Create `docker-compose.option-c.yml` for Option C pattern
3. Create environment file templates
4. Create deployment scripts
5. Test on GCS VM
6. Document everything

---

**Last Updated:** January 2025  
**Status:** 🟡 **IN PROGRESS**



