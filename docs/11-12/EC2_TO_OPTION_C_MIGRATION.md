# EC2 to Option C Migration Guide

**Date**: November 13, 2025  
**Purpose**: Guide for migrating from current EC2 setup to Option C (Everything as a Service) deployment

---

## Current Setup (EC2)

The platform is currently configured to run on EC2 with all services running in Docker containers via `docker-compose.infrastructure.yml`.

**Services Running Locally**:
- ArangoDB (localhost:8529)
- Redis (localhost:6379)
- Meilisearch (localhost:7700)
- Consul (localhost:8500)
- Tempo (localhost:3200)
- OpenTelemetry Collector (localhost:4317)
- Celery (local workers)
- Grafana (localhost:3000)
- **OPA** (localhost:8181) - **NEW**

**Configuration**: `symphainy-platform/config/production.env`

---

## Option C Setup (Managed Services)

Option C uses managed SaaS services instead of self-hosted Docker containers.

**Services to Replace**:
- ArangoDB → ArangoDB Oasis (managed)
- Redis → MemoryStore (managed) or Redis Cloud
- Meilisearch → Managed Meilisearch or Algolia
- Consul → Managed Consul or HashiCorp Cloud Platform
- Tempo → Grafana Cloud Tempo
- OpenTelemetry Collector → Grafana Cloud Collector
- Celery → Managed task queue (e.g., Cloud Tasks, SQS)
- Grafana → Grafana Cloud
- **OPA** → Managed OPA service or self-hosted on cloud

**Configuration**: Same file (`production.env`), different URLs

---

## Migration Steps

### Step 1: Update `production.env`

Replace localhost URLs with managed service URLs:

```bash
# Database Configuration
# BEFORE (EC2):
DATABASE_HOST=localhost

# AFTER (Option C):
DATABASE_HOST=your-managed-db-host.cloud-provider.com

# Redis Configuration
# BEFORE (EC2):
REDIS_HOST=localhost

# AFTER (Option C):
REDIS_HOST=your-redis-instance.memorystore.cloud-provider.com

# ArangoDB Configuration
# BEFORE (EC2):
ARANGO_HOSTS=localhost:8529

# AFTER (Option C):
ARANGO_HOSTS=your-cluster.arangodb-cloud.com:8529

# OPA Configuration
# BEFORE (EC2):
OPA_URL=http://localhost:8181

# AFTER (Option C):
OPA_URL=https://your-opa-service.cloud-provider.com
```

### Step 2: Update Docker Compose (Optional)

For Option C, you may not need `docker-compose.infrastructure.yml` at all, or you may only need it for:
- Local development
- Services that can't be managed (e.g., custom services)

**Option**: Comment out or remove services that are now managed:
```yaml
# services:
#   arangodb:  # Now using ArangoDB Oasis
#   redis:     # Now using MemoryStore
#   opa:       # Now using managed OPA
```

### Step 3: Update Environment Variables

If using environment variables (Docker/Kubernetes), update:
```bash
# EC2 (current)
export REDIS_HOST=localhost
export ARANGO_HOSTS=localhost:8529
export OPA_URL=http://localhost:8181

# Option C (future)
export REDIS_HOST=your-redis-instance.memorystore.cloud-provider.com
export ARANGO_HOSTS=your-cluster.arangodb-cloud.com:8529
export OPA_URL=https://your-opa-service.cloud-provider.com
```

### Step 4: Update Secrets

Move secrets from `.env.secrets` to:
- Cloud provider secret manager (AWS Secrets Manager, GCP Secret Manager, etc.)
- Or keep in `.env.secrets` but ensure it's not committed to git

---

## Configuration File Structure

### Current (EC2) - `production.env`
```bash
# CURRENT (EC2): Using localhost for services running in docker-compose
DATABASE_HOST=localhost
REDIS_HOST=localhost
ARANGO_HOSTS=localhost:8529
OPA_URL=http://localhost:8181
```

### Future (Option C) - `production.env`
```bash
# OPTION C: Using managed services
DATABASE_HOST=your-managed-db-host.cloud-provider.com
REDIS_HOST=your-redis-instance.memorystore.cloud-provider.com
ARANGO_HOSTS=your-cluster.arangodb-cloud.com:8529
OPA_URL=https://your-opa-service.cloud-provider.com
```

**Note**: The file structure stays the same - only URLs change!

---

## Testing Migration

### Before Migration (EC2)
1. ✅ All services running in Docker
2. ✅ Platform connects to localhost services
3. ✅ Demo working on EC2

### After Migration (Option C)
1. ✅ All services running as managed services
2. ✅ Platform connects to managed service URLs
3. ✅ Demo working with managed services

### Rollback Plan
If Option C migration fails:
1. Revert `production.env` to localhost URLs
2. Restart Docker containers
3. Platform should work with EC2 setup again

---

## Service-Specific Migration

### ArangoDB
- **EC2**: `localhost:8529` (Docker container)
- **Option C**: ArangoDB Oasis cluster URL
- **Migration**: Update `ARANGO_HOSTS` in `production.env`

### Redis
- **EC2**: `localhost:6379` (Docker container)
- **Option C**: MemoryStore or Redis Cloud URL
- **Migration**: Update `REDIS_HOST` in `production.env`

### OPA
- **EC2**: `http://localhost:8181` (Docker container)
- **Option C**: Managed OPA service URL
- **Migration**: Update `OPA_URL` in `production.env`
- **Note**: OPA service added to `docker-compose.infrastructure.yml` for EC2

### Meilisearch
- **EC2**: `localhost:7700` (Docker container)
- **Option C**: Managed Meilisearch or Algolia
- **Migration**: Update Meilisearch config (if configured separately)

### Other Services
- **Tempo**: Grafana Cloud Tempo
- **OpenTelemetry**: Grafana Cloud Collector
- **Grafana**: Grafana Cloud
- **Consul**: HashiCorp Cloud Platform or managed Consul

---

## Checklist

### Pre-Migration (EC2 - Current)
- [x] OPA added to `docker-compose.infrastructure.yml`
- [x] `production.env` configured for localhost services
- [x] All services running in Docker
- [x] Platform working on EC2

### Migration (Option C - Future)
- [ ] Provision managed services (ArangoDB Oasis, MemoryStore, etc.)
- [ ] Update `production.env` with managed service URLs
- [ ] Update secrets in cloud secret manager
- [ ] Test connectivity to managed services
- [ ] Deploy platform with Option C configuration
- [ ] Verify all services working
- [ ] Update `docker-compose.infrastructure.yml` (remove or comment managed services)

### Post-Migration
- [ ] Monitor service health
- [ ] Verify performance matches EC2 setup
- [ ] Update documentation
- [ ] Train team on managed services

---

## Benefits of Option C

1. **Reduced Operational Overhead**: No Docker container management
2. **Scalability**: Managed services auto-scale
3. **Reliability**: Managed services have SLAs
4. **Security**: Cloud provider security features
5. **Cost Optimization**: Pay for what you use

---

## Notes

- **Current setup (EC2) is production-ready** for demo purposes
- **Option C migration is straightforward** - just URL changes
- **No code changes required** - only configuration updates
- **Easy rollback** - revert URLs if needed

---

**Status**: ✅ **EC2 setup ready for demo** | ⏳ **Option C migration ready when approved**





