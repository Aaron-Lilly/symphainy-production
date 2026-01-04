# Environment Variables Reference

**Version:** 1.0  
**Date:** January 2025  
**Status:** Production Ready

---

## 📋 Overview

This document provides a comprehensive reference for all environment variables used in the Symphainy platform. All hardcoded values have been removed, and the platform now requires proper environment variable configuration for deployment.

**⚠️ CRITICAL:** Production deployments **MUST** configure all required environment variables. The platform will fail fast if required variables are missing in production.

---

## 🎯 Quick Reference

### Required for Production
- `NEXT_PUBLIC_API_URL` or `NEXT_PUBLIC_BACKEND_URL` (Frontend)
- `DATABASE_HOST`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD` (Backend)
- `REDIS_URL` or `REDIS_HOST` (Backend)
- `JWT_SECRET` (Backend - Security)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` (Backend - Authentication)

### Optional (with defaults)
- All other variables have sensible defaults for development
- See sections below for details

---

## 🌐 Frontend Environment Variables

### API Configuration

#### `NEXT_PUBLIC_API_URL` ⭐ **REQUIRED (Production)**
- **Description:** Primary API base URL for frontend API calls
- **Priority:** 1 (highest)
- **Format:** `http://example.com` or `https://api.example.com`
- **Example:** `https://api.symphainy.com`
- **Fallback:** `NEXT_PUBLIC_BACKEND_URL` → `NEXT_PUBLIC_API_BASE_URL` → **FAILS in production**
- **Used by:** All frontend API calls, service layer, managers
- **Note:** Remove port `:8000` if present (Traefik uses port 80)

#### `NEXT_PUBLIC_BACKEND_URL` ⭐ **REQUIRED (Production)**
- **Description:** Backend API URL (alternative to `NEXT_PUBLIC_API_URL`)
- **Priority:** 2
- **Format:** `http://example.com` or `https://api.example.com`
- **Example:** `https://api.symphainy.com`
- **Fallback:** `NEXT_PUBLIC_API_URL` → **FAILS in production**
- **Used by:** Next.js rewrites, API proxy configuration
- **Note:** Should include `/api` if backend expects it

#### `NEXT_PUBLIC_API_BASE_URL` (Legacy)
- **Description:** Legacy API URL variable (deprecated)
- **Priority:** 3
- **Format:** `http://example.com`
- **Fallback:** **FAILS in production**
- **Note:** Use `NEXT_PUBLIC_API_URL` instead

#### `NEXT_PUBLIC_WEBSOCKET_URL` (Optional)
- **Description:** Direct WebSocket URL override
- **Format:** `ws://example.com/api/ws/agent` or `wss://example.com/api/ws/agent`
- **Default:** Derived from `NEXT_PUBLIC_API_URL` (http → ws, https → wss)
- **Used by:** WebSocket connections
- **Note:** Usually not needed - auto-derived from API URL

### Frontend Application URLs

#### `NEXT_PUBLIC_FRONTEND_URL` (Optional)
- **Description:** Frontend application URL (for CORS, redirects)
- **Format:** `http://example.com` or `https://app.example.com`
- **Default:** `window.location.origin` (client-side), fails in production (server-side)
- **Used by:** CORS configuration, redirect URLs

#### `NEXT_PUBLIC_APP_URL` (Optional)
- **Description:** Alternative frontend URL variable
- **Format:** `http://example.com`
- **Default:** `NEXT_PUBLIC_FRONTEND_URL` → `window.location.origin`
- **Used by:** Frontend URL utilities

### Feature Flags

#### `NEXT_PUBLIC_SMART_CITY_ENABLED` (Optional)
- **Description:** Enable Smart City integration features
- **Format:** `true` or `false`
- **Default:** `false`
- **Type:** Boolean string

#### `NEXT_PUBLIC_DEBUG_MODE` (Optional)
- **Description:** Enable debug mode (additional logging)
- **Format:** `true` or `false`
- **Default:** `false`
- **Type:** Boolean string
- **Note:** Should be `false` in production

#### `NEXT_PUBLIC_ANALYTICS_ENABLED` (Optional)
- **Description:** Enable analytics tracking
- **Format:** `true` or `false`
- **Default:** `false`
- **Type:** Boolean string

### Smart City Service URLs (Optional)

#### `NEXT_PUBLIC_TRAFFIC_COP_URL`
- **Description:** Traffic Cop service URL
- **Format:** `http://example.com/traffic-cop`
- **Default:** Empty string

#### `NEXT_PUBLIC_ARCHIVE_URL`
- **Description:** Archive service URL
- **Format:** `http://example.com/archive`
- **Default:** Empty string

#### `NEXT_PUBLIC_CONDUCTOR_URL`
- **Description:** Conductor service URL
- **Format:** `http://example.com/conductor`
- **Default:** Empty string

#### `NEXT_PUBLIC_POST_OFFICE_URL`
- **Description:** Post Office service URL
- **Format:** `http://example.com/post-office`
- **Default:** Empty string

---

## 🔧 Backend Environment Variables

### Database Configuration

#### `DATABASE_HOST` ⭐ **REQUIRED (Production)**
- **Description:** PostgreSQL database host
- **Format:** Hostname or IP address
- **Default:** `localhost` (development only)
- **Example:** `db.example.com` or `10.0.0.5`
- **Used by:** Database connection pool

#### `DATABASE_PORT` (Optional)
- **Description:** PostgreSQL database port
- **Format:** Integer
- **Default:** `5432`
- **Example:** `5432`

#### `DATABASE_NAME` ⭐ **REQUIRED (Production)**
- **Description:** PostgreSQL database name
- **Format:** String (alphanumeric, underscores)
- **Default:** `symphainy_platform` (development only)
- **Example:** `symphainy_production`

#### `DATABASE_USER` ⭐ **REQUIRED (Production)**
- **Description:** PostgreSQL database user
- **Format:** String
- **Default:** `postgres` (development only)
- **Example:** `symphainy_user`

#### `DATABASE_PASSWORD` ⭐ **REQUIRED (Production)**
- **Description:** PostgreSQL database password
- **Format:** String (secure password)
- **Default:** None (must be set)
- **Security:** Store in secrets manager, never commit
- **Example:** `SecurePassword123!`

#### `DATABASE_POOL_SIZE` (Optional)
- **Description:** Database connection pool size
- **Format:** Integer
- **Default:** `10`
- **Example:** `20`

#### `DATABASE_MAX_OVERFLOW` (Optional)
- **Description:** Maximum overflow connections
- **Format:** Integer
- **Default:** `20`
- **Example:** `30`

#### `DATABASE_POOL_TIMEOUT` (Optional)
- **Description:** Connection pool timeout (seconds)
- **Format:** Integer
- **Default:** `30`
- **Example:** `60`

#### `DATABASE_POOL_RECYCLE` (Optional)
- **Description:** Connection recycle time (seconds)
- **Format:** Integer
- **Default:** `3600`
- **Example:** `1800`

### Redis Configuration

#### `REDIS_URL` ⭐ **REQUIRED (Production - Option C)**
- **Description:** Full Redis connection URL
- **Format:** `redis://host:port` or `rediss://host:port` (SSL)
- **Default:** `redis://localhost:6379` (development only)
- **Example:** `redis://redis.example.com:6379` or `rediss://redis.example.com:6380`
- **Used by:** Redis client, caching, message queue
- **Note:** Option C: Use managed Redis service URL

#### `REDIS_HOST` (Optional - if not using REDIS_URL)
- **Description:** Redis host
- **Format:** Hostname or IP address
- **Default:** `localhost` (development only)
- **Example:** `redis.example.com`

#### `REDIS_PORT` (Optional - if not using REDIS_URL)
- **Description:** Redis port
- **Format:** Integer
- **Default:** `6379`
- **Example:** `6379` or `6380` (SSL)

#### `REDIS_DB` (Optional)
- **Description:** Redis database number
- **Format:** Integer (0-15)
- **Default:** `0`
- **Example:** `0`

#### `REDIS_PASSWORD` (Optional)
- **Description:** Redis password
- **Format:** String
- **Default:** `null` (no password)
- **Security:** Store in secrets manager
- **Example:** `SecureRedisPassword123!`

#### `REDIS_MAX_CONNECTIONS` (Optional)
- **Description:** Maximum Redis connections
- **Format:** Integer
- **Default:** `20`
- **Example:** `50`

#### `REDIS_SOCKET_TIMEOUT` (Optional)
- **Description:** Redis socket timeout (seconds)
- **Format:** Integer
- **Default:** `5`
- **Example:** `10`

#### `REDIS_SOCKET_CONNECT_TIMEOUT` (Optional)
- **Description:** Redis connection timeout (seconds)
- **Format:** Integer
- **Default:** `5`
- **Example:** `10`

### Service URLs (Option C Ready)

#### `ARANGO_URL` ⭐ **REQUIRED (Option C)**
- **Description:** ArangoDB service URL
- **Format:** `http://host:port` or `https://host:port`
- **Default:** `http://localhost:8529` (development only)
- **Example:** `https://arangodb-cloud.example.com:8529`
- **Used by:** ArangoDB adapter
- **Note:** Option C: Use managed ArangoDB Oasis URL

#### `CONSUL_URL` (Optional)
- **Description:** Consul service discovery URL
- **Format:** `http://host:port`
- **Default:** `http://localhost:8501`
- **Example:** `http://consul.example.com:8501`
- **Used by:** Service discovery

#### `GRAFANA_URL` (Optional)
- **Description:** Grafana monitoring URL
- **Format:** `http://host:port`
- **Default:** `http://localhost:3100`
- **Example:** `http://grafana.example.com:3100`
- **Used by:** Monitoring and observability

#### `TEMPO_URL` (Optional)
- **Description:** Tempo tracing URL
- **Format:** `http://host:port`
- **Default:** `http://localhost:3200`
- **Example:** `http://tempo.example.com:3200`
- **Used by:** Distributed tracing

#### `OTEL_COLLECTOR_HTTP_URL` (Optional)
- **Description:** OpenTelemetry collector HTTP endpoint
- **Format:** `http://host:port`
- **Default:** `http://localhost:4318`
- **Example:** `http://otel-collector.example.com:4318`
- **Used by:** Observability

#### `OTEL_COLLECTOR_GRPC_URL` (Optional)
- **Description:** OpenTelemetry collector gRPC endpoint
- **Format:** `http://host:port`
- **Default:** `http://localhost:4317`
- **Example:** `http://otel-collector.example.com:4317`
- **Used by:** Observability

#### `MCP_SERVER_URL` (Optional)
- **Description:** MCP (Model Context Protocol) server URL
- **Format:** `http://host:port`
- **Default:** `http://localhost:8000`
- **Example:** `http://mcp-server.example.com:8000`
- **Used by:** MCP client manager

### Authentication & Security

#### `JWT_SECRET` ⭐ **REQUIRED (Production)**
- **Description:** JWT signing secret key
- **Format:** String (minimum 32 characters, cryptographically random)
- **Default:** None (must be set)
- **Security:** Store in secrets manager, rotate regularly
- **Example:** `your-super-secret-jwt-key-minimum-32-chars`
- **Used by:** JWT token generation and validation

#### `JWT_ALGORITHM` (Optional)
- **Description:** JWT signing algorithm
- **Format:** String
- **Default:** `HS256`
- **Example:** `HS256` or `RS256`

#### `JWT_EXPIRATION` (Optional)
- **Description:** JWT token expiration (seconds)
- **Format:** Integer
- **Default:** `3600` (1 hour)
- **Example:** `7200` (2 hours)

#### `JWT_REFRESH_EXPIRATION` (Optional)
- **Description:** JWT refresh token expiration (seconds)
- **Format:** Integer
- **Default:** `604800` (7 days)
- **Example:** `2592000` (30 days)

### Supabase Configuration

#### `SUPABASE_URL` ⭐ **REQUIRED (Production)**
- **Description:** Supabase project URL
- **Format:** `https://project-id.supabase.co`
- **Default:** None (must be set)
- **Example:** `https://abcdefghijklmnop.supabase.co`
- **Used by:** Supabase adapter, authentication

#### `SUPABASE_ANON_KEY` ⭐ **REQUIRED (Production)**
- **Description:** Supabase anonymous/public key
- **Format:** String (JWT)
- **Default:** None (must be set)
- **Security:** Can be exposed in frontend, but still secure
- **Example:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Used by:** Supabase client initialization

#### `SUPABASE_SERVICE_ROLE_KEY` ⭐ **REQUIRED (Production)**
- **Description:** Supabase service role key (admin access)
- **Format:** String (JWT)
- **Default:** None (must be set)
- **Security:** **NEVER expose in frontend** - backend only, store in secrets
- **Example:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **Used by:** Backend Supabase operations

### Google Cloud Storage

#### `GCS_CREDENTIALS_JSON` ⭐ **REQUIRED (Production - if using GCS)**
- **Description:** Google Cloud Service Account credentials (JSON)
- **Format:** JSON string (entire service account key file)
- **Default:** None (must be set if using GCS)
- **Security:** Store in secrets manager, never commit
- **Example:** `{"type": "service_account", "project_id": "...", ...}`
- **Used by:** GCS file adapter

#### `GCS_PROJECT_ID` (Optional)
- **Description:** Google Cloud project ID
- **Format:** String
- **Default:** `symphainymvp-devbox`
- **Example:** `symphainy-production`

#### `GCS_BUCKET_NAME` (Optional)
- **Description:** Google Cloud Storage bucket name
- **Format:** String
- **Default:** `symphainy-bucket-2025`
- **Example:** `symphainy-production-files`

#### `GCS_DEFAULT_REGION` (Optional)
- **Description:** Google Cloud default region
- **Format:** String
- **Default:** `us-central1`
- **Example:** `us-east1`

### LLM Provider Configuration

#### `OPENAI_API_KEY` (Optional)
- **Description:** OpenAI API key
- **Format:** String
- **Default:** None
- **Security:** Store in secrets manager
- **Example:** `sk-...`
- **Used by:** OpenAI LLM adapter

#### `OPENAI_BASE_URL` (Optional)
- **Description:** OpenAI API base URL (for custom endpoints)
- **Format:** `https://api.openai.com/v1`
- **Default:** `https://api.openai.com/v1`
- **Example:** `https://api.openai.com/v1`

#### `ANTHROPIC_API_KEY` (Optional)
- **Description:** Anthropic (Claude) API key
- **Format:** String
- **Default:** None
- **Security:** Store in secrets manager
- **Example:** `sk-ant-...`
- **Used by:** Anthropic LLM adapter

#### `ANTHROPIC_BASE_URL` (Optional)
- **Description:** Anthropic API base URL
- **Format:** `https://api.anthropic.com`
- **Default:** `https://api.anthropic.com`
- **Example:** `https://api.anthropic.com`

### Monitoring & Observability

#### `SENTRY_DSN` (Optional)
- **Description:** Sentry error tracking DSN
- **Format:** `https://key@sentry.io/project-id`
- **Default:** None
- **Example:** `https://abc123@o123456.ingest.sentry.io/123456`
- **Used by:** Error tracking and monitoring

#### `JAEGER_ENDPOINT` (Optional)
- **Description:** Jaeger tracing endpoint
- **Format:** `http://host:port/api/traces`
- **Default:** `http://localhost:14268/api/traces`
- **Example:** `http://jaeger.example.com:14268/api/traces`
- **Used by:** Distributed tracing

#### `DATADOG_API_KEY` (Optional)
- **Description:** Datadog API key for metrics
- **Format:** String
- **Default:** None
- **Security:** Store in secrets manager
- **Example:** `abc123def456...`
- **Used by:** Metrics export

#### `DATADOG_SITE` (Optional)
- **Description:** Datadog site
- **Format:** String
- **Default:** `datadoghq.com`
- **Example:** `datadoghq.com` or `us3.datadoghq.com`

### Application Configuration

#### `NODE_ENV` (Optional)
- **Description:** Node.js environment
- **Format:** `development`, `production`, or `test`
- **Default:** `development`
- **Example:** `production`
- **Used by:** Frontend build, environment detection

#### `LOG_LEVEL` (Optional)
- **Description:** Logging level
- **Format:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Default:** `INFO`
- **Example:** `INFO` (production), `DEBUG` (development)

#### `API_WORKERS` (Optional)
- **Description:** Number of API server workers
- **Format:** Integer
- **Default:** `4`
- **Example:** `8`

#### `API_PORT` (Optional)
- **Description:** API server port
- **Format:** Integer
- **Default:** `8000`
- **Example:** `8000`

---

## 🐳 Docker Compose Environment Variables

### Network Configuration

#### `COMPOSE_PROJECT_NAME` (Optional)
- **Description:** Docker Compose project name
- **Format:** String
- **Default:** `symphainy`
- **Example:** `symphainy-production`

#### `NETWORK_NAME` (Optional)
- **Description:** Docker network name
- **Format:** String
- **Default:** `smart_city_net`
- **Example:** `symphainy_network`

### Traefik Configuration

#### `TRAEFIK_API_DASHBOARD` (Optional)
- **Description:** Enable Traefik dashboard
- **Format:** `true` or `false`
- **Default:** `true` (development), `false` (production)
- **Example:** `false`

#### `TRAEFIK_DASHBOARD_PORT` (Optional)
- **Description:** Traefik dashboard port
- **Format:** Integer
- **Default:** `8080`
- **Example:** `8080`

### Service IPs (Development Only)

**⚠️ NOTE:** These should be replaced with service discovery or environment variables in production.

#### `BACKEND_IP` (Development)
- **Description:** Backend service IP (development only)
- **Format:** IP address
- **Default:** `172.20.0.10`
- **Note:** Use service discovery in production

#### `FRONTEND_IP` (Development)
- **Description:** Frontend service IP (development only)
- **Format:** IP address
- **Default:** `172.20.0.20`
- **Note:** Use service discovery in production

---

## ☁️ Option C (Managed Services) Configuration

When migrating to Option C (fully managed services), configure these variables:

### Managed Database
- **PostgreSQL:** Use managed database connection string
  - `DATABASE_HOST`: Managed database host
  - `DATABASE_PORT`: Managed database port (usually 5432)
  - `DATABASE_SSL_MODE`: `require` (for managed databases)

### Managed Redis
- **Redis:** Use managed Redis service
  - `REDIS_URL`: Managed Redis connection URL (e.g., `rediss://redis-cloud.example.com:6380`)
  - `REDIS_PASSWORD`: Managed Redis password

### Managed ArangoDB
- **ArangoDB:** Use ArangoDB Oasis
  - `ARANGO_URL`: ArangoDB Oasis URL (e.g., `https://cluster.arangodb-cloud.com:8529`)

### Managed Search
- **Meilisearch:** Use Meilisearch Cloud
  - `MEILISEARCH_URL`: Meilisearch Cloud URL
  - `MEILISEARCH_API_KEY`: Meilisearch Cloud API key

### Managed Observability
- **Grafana Cloud:** Use Grafana Cloud
  - `GRAFANA_URL`: Grafana Cloud URL
  - `GRAFANA_API_KEY`: Grafana Cloud API key
  - `TEMPO_URL`: Tempo Cloud URL
  - `OTEL_COLLECTOR_HTTP_URL`: OpenTelemetry collector URL

---

## 📝 Environment Variable Files

### Development
Create `.env.development`:
```bash
# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000

# Backend
DATABASE_HOST=localhost
DATABASE_NAME=symphainy_platform
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
REDIS_URL=redis://localhost:6379

# Secrets (use local values)
JWT_SECRET=dev-secret-key-minimum-32-characters-long
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Staging
Create `.env.staging`:
```bash
# Frontend
NEXT_PUBLIC_API_URL=https://staging-api.symphainy.com
NEXT_PUBLIC_FRONTEND_URL=https://staging.symphainy.com

# Backend
DATABASE_HOST=staging-db.symphainy.com
DATABASE_NAME=symphainy_staging
DATABASE_USER=symphainy_staging
DATABASE_PASSWORD=<from-secrets-manager>
REDIS_URL=redis://staging-redis.symphainy.com:6379

# Secrets (from secrets manager)
JWT_SECRET=<from-secrets-manager>
SUPABASE_URL=https://staging-project.supabase.co
SUPABASE_ANON_KEY=<from-secrets-manager>
SUPABASE_SERVICE_ROLE_KEY=<from-secrets-manager>
```

### Production
Create `.env.production`:
```bash
# Frontend
NEXT_PUBLIC_API_URL=https://api.symphainy.com
NEXT_PUBLIC_FRONTEND_URL=https://app.symphainy.com

# Backend
DATABASE_HOST=production-db.symphainy.com
DATABASE_NAME=symphainy_production
DATABASE_USER=symphainy_production
DATABASE_PASSWORD=<from-secrets-manager>
REDIS_URL=rediss://production-redis.symphainy.com:6380

# Secrets (from secrets manager - REQUIRED)
JWT_SECRET=<from-secrets-manager>
SUPABASE_URL=https://production-project.supabase.co
SUPABASE_ANON_KEY=<from-secrets-manager>
SUPABASE_SERVICE_ROLE_KEY=<from-secrets-manager>

# Option C: Managed Services
ARANGO_URL=https://arangodb-cloud.example.com:8529
MEILISEARCH_URL=https://meilisearch-cloud.example.com
```

---

## 🔒 Security Best Practices

1. **Never commit secrets to version control**
   - Use `.env.secrets` (gitignored) or secrets manager
   - Use environment variable injection in CI/CD

2. **Use secrets manager in production**
   - AWS Secrets Manager
   - Google Cloud Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

3. **Rotate secrets regularly**
   - JWT secrets: Every 90 days
   - Database passwords: Every 180 days
   - API keys: As needed

4. **Use different secrets per environment**
   - Development, staging, production must have separate secrets
   - Never reuse production secrets in development

5. **Validate environment variables at startup**
   - Backend validates required variables on startup
   - Frontend fails fast in production if missing

---

## ✅ Validation Checklist

Before deploying to production, verify:

- [ ] All required variables are set (⭐ marked variables)
- [ ] No hardcoded values remain in code
- [ ] Secrets are stored in secrets manager (not in code)
- [ ] Different secrets for each environment
- [ ] `.env` files are in `.gitignore`
- [ ] Environment variable documentation is up to date
- [ ] Option C variables configured (if using managed services)

---

## 📚 Related Documentation

- [Option C Readiness Implementation Plan](./OPTION_C_READINESS_IMPLEMENTATION_PLAN.md)
- [Configuration Management](./CONFIGURATION_MANAGEMENT.md) (if exists)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) (if exists)

---

**Last Updated:** January 2025  
**Maintained by:** Platform Team




