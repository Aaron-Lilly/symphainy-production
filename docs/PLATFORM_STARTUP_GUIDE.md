# SymphAIny Platform Startup Guide

## Overview

This guide provides clear, step-by-step instructions for starting the SymphAIny Platform. The platform uses Docker Compose to orchestrate all services, making startup a single command.

## Quick Start

### Start Everything (Recommended)

From the project root directory (`/home/founders/demoversion/symphainy_source`):

```bash
docker-compose up -d
```

This single command starts:
- **Infrastructure Services**: Consul, Redis, ArangoDB, Traefik, Tempo, OpenTelemetry Collector, Grafana, Loki, OPA, Meilisearch
- **Application Services**: Backend API, Frontend, Celery Worker, Celery Beat

### Verify Platform is Running

```bash
# Check container status
docker-compose ps

# Check backend health
curl http://localhost/api/health

# Or access via browser
# Frontend: http://localhost
# API Docs: http://localhost/api/docs
# Traefik Dashboard: http://localhost:8080
```

## Detailed Startup Process

### 1. Prerequisites

- **Docker** and **Docker Compose** installed and running
- **Environment Variables**: `.env.secrets` file in `symphainy-platform/` directory with required credentials
- **Ports Available**: Ensure ports 80, 443, 8080, 8500, 6379, 8529, 3100, 3200, 4317-4318, 7700, 8181 are available

### 2. Startup Sequence

The `docker-compose.yml` file defines the complete platform with proper dependency ordering:

1. **Infrastructure Layer** (starts first):
   - Consul (Service Discovery)
   - Redis (Cache & Message Broker)
   - ArangoDB (Metadata Storage)
   - Traefik (Reverse Proxy)
   - Tempo (Distributed Tracing)
   - OpenTelemetry Collector
   - Loki (Log Aggregation)
   - Grafana (Visualization)
   - OPA (Policy Engine)
   - Meilisearch (Search Engine)

2. **Application Layer** (starts after infrastructure is healthy):
   - Backend API (FastAPI)
   - Frontend (Next.js)
   - Celery Worker (Background Tasks)
   - Celery Beat (Task Scheduler)

### 3. Health Checks

All services include health checks. The platform waits for dependencies to be healthy before starting dependent services:

- **Consul**: `http://localhost:8500/v1/status/leader`
- **Redis**: `redis-cli ping`
- **ArangoDB**: `http://localhost:8529/_api/version`
- **Backend**: `http://localhost:8000/health`
- **Frontend**: `http://localhost:3000`

### 4. Access Points

Once started, access the platform via:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | `http://localhost` | Main UI (routed through Traefik) |
| **Backend API** | `http://localhost/api` | API endpoints (routed through Traefik) |
| **API Docs** | `http://localhost/api/docs` | Swagger/OpenAPI documentation |
| **Traefik Dashboard** | `http://localhost:8080` | Reverse proxy dashboard |
| **Consul UI** | `http://localhost:8500` | Service discovery UI |
| **Grafana** | `http://localhost:3100` | Monitoring and visualization |
| **ArangoDB** | `http://localhost:8529` | Database UI |
| **Meilisearch** | `http://localhost:7700` | Search engine UI |

## Cloud-Ready Mode

The platform supports two startup modes:

### Legacy Mode (Default)

Uses `PlatformOrchestrator` with manual service registration. This is the current production mode.

### Cloud-Ready Mode

Uses `CloudReadyPlatformOrchestrator` with auto-discovery and unified service registry. To enable:

```bash
# Set environment variable before starting
export CLOUD_READY_MODE=enabled

# Or add to docker-compose.yml backend service environment:
environment:
  - CLOUD_READY_MODE=enabled

# Then restart
docker-compose up -d backend
```

**Cloud-Ready Features:**
- Auto-discovery of services
- Unified service registry
- Simplified startup sequence
- Better dependency resolution

See `docs/CLOUD_READY_FEATURE_FLAG_EXPLANATION.md` for details.

## Common Operations

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Start with logs visible
docker-compose up
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Check Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Service health
curl http://localhost/api/health
```

## Troubleshooting

### Containers Won't Start

1. **Check Docker is running**:
   ```bash
   docker info
   ```

2. **Check port conflicts**:
   ```bash
   # Check if ports are in use
   lsof -i :80
   lsof -i :8500
   lsof -i :6379
   ```

3. **Check logs**:
   ```bash
   docker-compose logs [service-name]
   ```

### Backend Health Check Fails

1. **Check backend logs**:
   ```bash
   docker logs symphainy-backend-prod
   ```

2. **Verify dependencies are healthy**:
   ```bash
   # Check Consul
   curl http://localhost:8500/v1/status/leader
   
   # Check Redis
   docker exec symphainy-redis redis-cli ping
   
   # Check ArangoDB
   curl http://localhost:8529/_api/version
   ```

3. **Check environment variables**:
   ```bash
   # Verify .env.secrets exists
   ls -la symphainy-platform/.env.secrets
   ```

### Services Show as "Unhealthy"

Some services (Loki, Tempo, Traefik) may show as "unhealthy" but still function. This is often due to:
- Health check timing (services need time to fully initialize)
- Health check endpoint configuration
- Network connectivity within Docker network

If services are responding to requests, they're likely working correctly despite the health check status.

### Frontend Not Accessible

1. **Check Traefik is running**:
   ```bash
   docker logs symphainy-traefik
   ```

2. **Check Traefik dashboard**:
   ```bash
   # Visit http://localhost:8080
   # Verify frontend and backend routes are registered
   ```

3. **Check frontend logs**:
   ```bash
   docker logs symphainy-frontend-prod
   ```

## Architecture Notes

### Service Communication

- **Internal**: Services communicate via Docker network using container names (e.g., `http://backend:8000`)
- **External**: All external access routes through Traefik on port 80
- **Service Discovery**: Consul manages service registration and discovery

### Data Persistence

Data is persisted in Docker volumes:
- `arangodb_data`: ArangoDB database
- `redis_data`: Redis cache and queues
- `meilisearch_data`: Search indices
- `consul_data`: Consul KV store
- `grafana_data`: Grafana dashboards
- `loki_data`: Log storage
- `tempo_data`: Trace storage

### Network

All services run on the `smart_city_net` Docker network, enabling:
- Service-to-service communication via container names
- Isolation from host network
- Traefik automatic service discovery

## Environment Variables

### Required in `.env.secrets`

The backend requires these variables (loaded from `symphainy-platform/.env.secrets`):

- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_KEY`: Supabase service role key
- `SECRET_KEY`: Application secret key
- `JWT_SECRET`: JWT signing secret

### Optional Environment Variables

- `CLOUD_READY_MODE`: Enable cloud-ready orchestrator (`enabled`, `disabled`, `hybrid`)
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `ENVIRONMENT`: Environment name (`development`, `production`)

## Next Steps

- **Development**: See `docs/DEVELOPMENT_GUIDE.md` for development workflows
- **Cloud Deployment**: See `docs/CLOUD_READY_ARCHITECTURE_MIGRATION_PLAN.md` for cloud deployment patterns
- **Architecture**: See `docs/PLATFORM_ARCHITECTURAL_REFACTORING_PLAN.md` for architectural details

## Summary

**Start the platform:**
```bash
cd /home/founders/demoversion/symphainy_source
docker-compose up -d
```

**Verify it's working:**
```bash
curl http://localhost/api/health
```

**Access the platform:**
- Frontend: http://localhost
- API Docs: http://localhost/api/docs

That's it! The platform is now running. 🚀








