# Symphainy Platform Deployment Guide

**Version:** 1.0  
**Date:** January 2025  
**Status:** Production Ready

---

## 📋 Overview

This guide provides step-by-step instructions for deploying the Symphainy Platform using Docker Compose. The platform supports two deployment patterns:

1. **Standard Deployment:** All services in containers (development/staging)
2. **Option C Deployment:** Managed services + application containers (production-ready)

---

## 🎯 Quick Start

### Standard Deployment (Development/Staging)

```bash
# 1. Set up environment file
cp scripts/deploy/env.development.template .env.development
# Edit .env.development with your values

# 2. Set up secrets
# Create symphainy-platform/.env.secrets with your secrets

# 3. Deploy
./scripts/deploy/deploy.sh development
```

### Option C Deployment (Production Pattern)

```bash
# 1. Set up environment file with managed services
cp scripts/deploy/env.production.template .env.production
# Edit .env.production:
#   - Set OPTION_C_ENABLED=true
#   - Set managed service URLs (REDIS_URL, ARANGO_URL, etc.)

# 2. Set up secrets
# Create symphainy-platform/.env.secrets with your secrets

# 3. Deploy
./scripts/deploy/deploy-option-c.sh production
```

---

## 📁 File Structure

```
symphainy_source/
├── docker-compose.yml              # Standard deployment (all services)
├── docker-compose.option-c.yml    # Option C deployment (managed services)
├── .env.development                # Development environment (create from template)
├── .env.staging                    # Staging environment (create from template)
├── .env.production                 # Production environment (create from template)
├── scripts/deploy/
│   ├── deploy.sh                   # Standard deployment script
│   ├── deploy-option-c.sh          # Option C deployment script
│   ├── validate-env.sh             # Environment validation
│   ├── health-check.sh             # Post-deployment health checks
│   ├── env.development.template    # Development environment template
│   └── env.production.template     # Production environment template
└── symphainy-platform/
    └── .env.secrets                 # Secrets file (gitignored)
```

---

## 🔧 Environment Setup

### 1. Create Environment File

Choose the appropriate template and create your environment file:

```bash
# Development
cp scripts/deploy/env.development.template .env.development

# Staging
cp scripts/deploy/env.staging.template .env.staging

# Production
cp scripts/deploy/env.production.template .env.production
```

### 2. Configure Environment Variables

Edit your environment file and set:

**Required:**
- `FRONTEND_URL` - Frontend application URL
- `API_URL` - Backend API URL
- `NEXT_PUBLIC_API_URL` - Public API URL (for frontend)
- `NEXT_PUBLIC_BACKEND_URL` - Backend URL (for frontend)

**Recommended:**
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `API_CORS_ORIGINS` - API CORS origins (comma-separated)

**For Production:**
- Set `ENVIRONMENT=production`
- Set `NODE_ENV=production`
- Set `TRAEFIK_DASHBOARD_ENABLED=false`
- Configure all security settings

### 3. Configure Secrets

Create `symphainy-platform/.env.secrets` with:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# JWT
JWT_SECRET=your-jwt-secret

# LLM API Keys
LLM_OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Other secrets...
```

**⚠️ CRITICAL:** Never commit `.env.secrets` to git!

---

## 🚀 Deployment

### Standard Deployment

Deploys all services (infrastructure + application) in containers:

```bash
./scripts/deploy/deploy.sh [environment]
```

**Example:**
```bash
./scripts/deploy/deploy.sh development
```

**What it does:**
1. Validates environment file exists
2. Loads environment variables
3. Validates required variables
4. Builds Docker images
5. Stops existing containers
6. Starts all services
7. Runs health checks
8. Displays status

### Option C Deployment

Deploys application containers only, uses managed services for infrastructure:

```bash
./scripts/deploy/deploy-option-c.sh [environment]
```

**Example:**
```bash
./scripts/deploy/deploy-option-c.sh production
```

**Prerequisites:**
- `OPTION_C_ENABLED=true` in environment file
- Managed service URLs configured (REDIS_URL, ARANGO_URL, etc.)

**What it does:**
1. Validates environment file exists
2. Validates Option C is enabled
3. Tests managed service connectivity
4. Builds application images only
5. Stops existing containers
6. Starts application services
7. Runs health checks
8. Displays status

---

## 🏥 Health Checks

After deployment, health checks verify all services are running:

```bash
# Manual health check
./scripts/deploy/health-check.sh [environment] [compose-suffix]

# Example
./scripts/deploy/health-check.sh development
./scripts/deploy/health-check.sh production option-c
```

**Checks:**
- Backend API health endpoint
- Frontend accessibility
- Traefik dashboard
- Consul service discovery
- Redis connectivity (if not Option C)
- ArangoDB connectivity (if not Option C)

---

## 🔍 Troubleshooting

### Services Not Starting

1. **Check environment variables:**
   ```bash
   source .env.development
   ./scripts/deploy/validate-env.sh development
   ```

2. **Check container logs:**
   ```bash
   docker-compose --env-file .env.development logs [service-name]
   ```

3. **Check container status:**
   ```bash
   docker-compose --env-file .env.development ps
   ```

### Health Checks Failing

1. **Wait longer for services to start:**
   ```bash
   # Services may need more time to initialize
   sleep 30
   ./scripts/deploy/health-check.sh development
   ```

2. **Check service dependencies:**
   - Ensure infrastructure services start before application services
   - Check `depends_on` conditions in docker-compose.yml

### Option C Connectivity Issues

1. **Verify managed service URLs:**
   ```bash
   # Test Redis
   redis-cli -u ${REDIS_URL} ping

   # Test ArangoDB
   curl ${ARANGO_URL}/_api/version
   ```

2. **Check network connectivity:**
   - Ensure GCS VM can reach managed services
   - Check firewall rules
   - Verify credentials

---

## 📊 Service Access

After successful deployment:

### Standard Deployment

- **Frontend:** `${FRONTEND_URL}` (default: http://localhost)
- **Backend API:** `${API_URL}/api` (default: http://localhost/api)
- **Traefik Dashboard:** http://localhost:${TRAEFIK_DASHBOARD_PORT}
- **Consul UI:** http://localhost:${CONSUL_HTTP_PORT}
- **Grafana:** http://localhost:${GRAFANA_PORT}
- **ArangoDB:** http://localhost:${ARANGO_PORT}

### Option C Deployment

- **Frontend:** `${FRONTEND_URL}`
- **Backend API:** `${API_URL}/api`
- **Traefik Dashboard:** http://localhost:${TRAEFIK_DASHBOARD_PORT}
- **Consul UI:** http://localhost:${CONSUL_HTTP_PORT}
- **Managed Services:** Access via configured URLs

---

## 🔄 Updating Deployment

### Update Environment Variables

1. Edit your environment file (`.env.development`, `.env.staging`, etc.)
2. Restart services:
   ```bash
   docker-compose --env-file .env.development down
   ./scripts/deploy/deploy.sh development
   ```

### Update Application Code

1. Rebuild images:
   ```bash
   docker-compose --env-file .env.development build
   ```

2. Restart services:
   ```bash
   docker-compose --env-file .env.development up -d
   ```

### Update Secrets

1. Update `symphainy-platform/.env.secrets`
2. Restart affected services:
   ```bash
   docker-compose --env-file .env.development restart backend celery-worker celery-beat
   ```

---

## 🛑 Stopping Deployment

```bash
# Stop all services
docker-compose --env-file .env.development down

# Stop and remove volumes (⚠️ deletes data)
docker-compose --env-file .env.development down -v
```

---

## 📝 Environment Variable Reference

See `ENVIRONMENT_VARIABLES.md` for complete reference of all environment variables.

**Key Variables:**
- `FRONTEND_URL` - Frontend application URL
- `API_URL` - Backend API URL
- `ENVIRONMENT` - Environment name (development|staging|production)
- `OPTION_C_ENABLED` - Enable Option C pattern (true|false)
- `REDIS_URL` - Redis connection URL (for Option C)
- `ARANGO_URL` - ArangoDB connection URL (for Option C)

---

## 🎯 Option C Pattern Validation

To validate Option C pattern on GCS VM:

1. **Set up managed services:**
   - Configure Redis (MemoryStore or Upstash)
   - Configure ArangoDB (ArangoDB Oasis or self-hosted)
   - Configure other managed services

2. **Configure environment:**
   ```bash
   OPTION_C_ENABLED=true
   REDIS_URL=redis://managed-redis.example.com:6379
   ARANGO_URL=https://managed-arango.example.com
   ```

3. **Deploy:**
   ```bash
   ./scripts/deploy/deploy-option-c.sh production
   ```

4. **Validate:**
   - All application containers running
   - Health checks passing
   - Services connecting to managed services
   - Platform fully functional

---

## ✅ Success Criteria

Deployment is successful when:

1. ✅ All containers are running (`docker-compose ps`)
2. ✅ Health checks pass (`./scripts/deploy/health-check.sh`)
3. ✅ Frontend accessible at `${FRONTEND_URL}`
4. ✅ Backend API accessible at `${API_URL}/api`
5. ✅ Services can communicate (check logs)
6. ✅ Option C: Managed services accessible (if Option C enabled)

---

## 🚨 Common Issues

### Port Conflicts

If ports are already in use:
- Change port mappings in environment file
- Stop conflicting services
- Use different ports

### Network Issues

If services can't communicate:
- Check Docker network exists: `docker network ls`
- Verify services are on same network
- Check container names match environment variables

### Environment Variable Not Loading

If variables aren't being used:
- Verify environment file exists and is readable
- Check variable names match exactly (case-sensitive)
- Ensure no typos in variable names

---

## 📚 Additional Resources

- **Environment Variables:** `docs/final_production_docs/ENVIRONMENT_VARIABLES.md`
- **Docker Compose Strategy:** `docs/final_production_docs/DOCKER_COMPOSE_DEPLOYMENT_STRATEGY.md`
- **Hybrid Cloud Strategy:** `docs/hybridcloudstrategy.md`

---

**Last Updated:** January 2025  
**Status:** ✅ **PRODUCTION READY**




