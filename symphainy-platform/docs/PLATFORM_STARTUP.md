# SymphAIny Platform Startup Guide

## 📋 Table of Contents

1. [Current Architecture (EC2 Deployment)](#current-architecture-ec2-deployment)
2. [Startup Sequence](#startup-sequence)
3. [Configuration System](#configuration-system)
4. [Required Configuration](#required-configuration)
5. [Troubleshooting](#troubleshooting)
6. [Roadmap: Evolution to Option C](#roadmap-evolution-to-option-c)

---

## Current Architecture (EC2 Deployment)

### Overview

The SymphAIny Platform is currently deployed on EC2 using a containerized architecture with:
- **Infrastructure Layer**: Docker Compose (Redis, ArangoDB, Consul, Tempo, Grafana, OTel Collector)
- **Backend Layer**: FastAPI application with lazy-hydrating service mesh
- **Frontend Layer**: Next.js application (separate repository)

### Architecture Principles

- **5-Layer Security Architecture**: Adapter → Abstraction → Service → Role → Agent
- **Lazy Hydration**: Services load on-demand, not eagerly at startup
- **Foundation-First**: DI Container → Public Works Foundation → Smart City Gateway → Realms
- **Configuration Layering**: Secrets → Environment → Business Logic → Infrastructure → Defaults

---

## Startup Sequence

### Prerequisites

- Docker & Docker Compose installed
- Poetry installed (`curl -sSL https://install.python-poetry.org | python3 -`)
- Python 3.11+ installed
- `.env.secrets` file configured (see [Configuration System](#configuration-system))
- Ports available: 8000 (backend), 3000 (frontend), 8501 (Consul), 6379 (Redis), 8529 (ArangoDB), 3100 (Grafana)

### Step-by-Step Startup

#### Option 1: Using Startup Script (Recommended)

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Foreground mode (development)
./startup.sh

# Background mode (production)
./startup.sh --background

# Minimal mode (infrastructure already running)
./startup.sh --minimal
```

#### Option 2: Manual Startup

**Phase 1: Start Infrastructure**

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Start all infrastructure services
./scripts/start-infrastructure.sh

# Or use docker-compose directly
docker-compose -f docker-compose.infrastructure.yml up -d

# Verify services are healthy
docker-compose -f docker-compose.infrastructure.yml ps
```

**Phase 2: Start Backend**

```bash
# Ensure you're in the platform directory
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Set environment variables (if not using .env.secrets)
export ARANGO_URL="http://localhost:8529"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="your-secret-key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-anon-key"
export SUPABASE_SERVICE_KEY="your-supabase-service-key"

# Start backend using Poetry
poetry run python main.py --host 0.0.0.0 --port 8000

# Or with auto-reload (development)
poetry run python main.py --host 0.0.0.0 --port 8000 --reload
```

**Phase 3: Start Frontend** (Separate Repository)

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-frontend

# Development mode
npm run dev

# Production mode
npm run build
npm start
```

### Startup Phases Explained

1. **Phase 0: Validation**
   - Check Poetry environment
   - Validate platform structure
   - Verify Python version

2. **Phase 1: Infrastructure Services** (Docker Compose)
   - Consul (Service Discovery) - Port 8501
   - Redis (Caching/Sessions) - Port 6379
   - ArangoDB (Metadata/Graph) - Port 8529
   - Tempo (Tracing) - Port 3200
   - Grafana (Visualization) - Port 3100
   - OpenTelemetry Collector - Ports 4317, 4318, 8889

3. **Phase 2: Backend Services** (FastAPI)
   - DI Container initialization
   - Public Works Foundation (infrastructure adapters)
   - Smart City Gateway (City Manager)
   - Lazy Realm Hydration (on-demand service loading)
   - Background Health Watchers
   - Curator Auto-Discovery

4. **Phase 3: Frontend** (Next.js)
   - Next.js development server
   - Supabase authentication client
   - API client configuration

---

## Configuration System

### Configuration Architecture

The platform uses a **5-layer configuration system** with hierarchical loading:

```
Layer 1: Secrets (.env.secrets) - Highest Priority
    ↓
Layer 2: Environment (config/{env}.env)
    ↓
Layer 3: Business Logic (config/business-logic.yaml)
    ↓
Layer 4: Infrastructure (config/infrastructure.yaml)
    ↓
Layer 5: Defaults (Platform defaults) - Lowest Priority
```

### Configuration Loading Flow

1. **`main.py`** loads `.env.secrets` via `load_dotenv('.env.secrets')`
2. **`UnifiedConfigurationManager`** loads all layers into a unified config dict
3. **`ConfigAdapter`** reads from environment variables (set by UnifiedConfigurationManager)
4. **Foundation Services** use `ConfigAdapter` to access configuration

### Configuration Files

#### `.env.secrets` (Required - Not Committed)

Location: `symphainy-platform/.env.secrets`

**Critical Secrets:**
```bash
# Database Configuration
ARANGO_URL=http://localhost:8529
ARANGO_DB=symphainy_metadata
ARANGO_USER=root
ARANGO_PASS=

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# Supabase Configuration (Authentication & Business Data)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# Platform Security
SECRET_KEY=your-platform-secret-key

# LLM Configuration
LLM_OPENAI_API_KEY=your-openai-api-key
```

**Template:** See `config/secrets.example` for full template

#### `config/development.env` (Environment-Specific)

Location: `symphainy-platform/config/development.env`

Contains environment-specific settings:
- API server configuration
- Logging levels
- Debug flags
- Feature toggles

#### `config/business-logic.yaml` (Business Rules)

Location: `symphainy-platform/config/business-logic.yaml`

Contains business logic configuration:
- Workflow definitions
- Business rules
- Domain-specific settings

#### `config/infrastructure.yaml` (Infrastructure)

Location: `symphainy-platform/config/infrastructure.yaml`

Contains infrastructure configuration:
- Service endpoints
- Connection pools
- Timeout settings

---

## Required Configuration

### Critical Configuration (Must Have)

| Variable | Purpose | Example | Source |
|----------|---------|---------|--------|
| `ARANGO_URL` | ArangoDB connection | `http://localhost:8529` | `.env.secrets` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` | `.env.secrets` |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` | `.env.secrets` |
| `SUPABASE_KEY` | Supabase anon key | `eyJhbGc...` | `.env.secrets` |
| `SUPABASE_SERVICE_KEY` | Supabase service key | `eyJhbGc...` | `.env.secrets` |
| `SECRET_KEY` | Platform secret key | `sk-...` | `.env.secrets` |

### Optional Configuration (With Defaults)

| Variable | Purpose | Default | Source |
|----------|---------|---------|--------|
| `LLM_OPENAI_API_KEY` | OpenAI API key | None | `.env.secrets` |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket | None | `.env.secrets` |
| `OPA_URL` | Open Policy Agent URL | `http://localhost:8181` | `config/development.env` |
| `LOG_LEVEL` | Logging level | `INFO` | `config/development.env` |

### Deprecated Configuration (Do Not Use)

| Variable | Status | Reason |
|----------|--------|--------|
| `JWT_SECRET` | **DEPRECATED** | Supabase handles JWT tokens internally |
| `JWT_SECRET_KEY` | **DEPRECATED** | Supabase handles JWT tokens internally |
| `JWT_ALGORITHM` | **DEPRECATED** | Supabase handles JWT tokens internally |

**Note:** JWT configuration is no longer required. Supabase manages all authentication tokens. Internal JWT adapter may exist for legacy/internal tokens only.

---

## Troubleshooting

### Common Startup Issues

#### Issue: "Missing required configuration keys: ARANGO_URL, REDIS_URL, SECRET_KEY"

**Cause:** Configuration not loaded into environment variables

**Solution:**
1. Verify `.env.secrets` exists and contains required keys
2. Check that `load_dotenv('.env.secrets')` is called in `main.py`
3. Ensure `UnifiedConfigurationManager` sets environment variables after loading

#### Issue: "Port 3000 is occupied"

**Cause:** Grafana or frontend already running on port 3000

**Solution:**
```bash
# Check what's using port 3000
lsof -i :3000

# Kill the process or change Grafana port (already fixed to 3100)
# Frontend should use port 3000, Grafana uses 3100
```

#### Issue: "ArangoDB health check failed"

**Cause:** ArangoDB container not healthy or healthcheck misconfigured

**Solution:**
```bash
# Check ArangoDB logs
docker logs symphainy-arangodb

# Verify ArangoDB is accessible
curl http://localhost:8529/_api/version

# Restart infrastructure
docker-compose -f docker-compose.infrastructure.yml restart arangodb
```

#### Issue: "Supabase authentication failed"

**Cause:** Invalid Supabase credentials or network issue

**Solution:**
1. Verify Supabase credentials in `.env.secrets`
2. Test Supabase connection:
   ```bash
   python3 scripts/test_supabase_connection.py
   ```
3. Check Supabase dashboard for project status

#### Issue: "JWT_SECRET missing" (Legacy Error)

**Cause:** Legacy code still requiring JWT_SECRET

**Solution:**
- This is an anti-pattern - JWT_SECRET should not be required
- Update code to remove JWT_SECRET requirement
- Use Supabase token validation instead

### Health Checks

**Backend Health:**
```bash
curl http://localhost:8000/health
```

**Infrastructure Health:**
```bash
# Consul
curl http://localhost:8501/v1/status/leader

# Redis
redis-cli -h localhost -p 6379 ping

# ArangoDB
curl http://localhost:8529/_api/version

# Grafana
curl http://localhost:3100/api/health
```

---

## Roadmap: Evolution to Option C

### Current State: EC2 Deployment (MVP)

**Architecture:**
- All services on single EC2 instance
- Docker Compose for orchestration
- Self-hosted infrastructure (Redis, ArangoDB, Consul)
- Manual deployment process

**Characteristics:**
- ✅ Full control over infrastructure
- ✅ Cost-effective for MVP
- ❌ Manual scaling
- ❌ Single point of failure
- ❌ DevOps overhead

### Phase 1: Container Split (Near-Term)

**Goal:** Separate stateful from stateless services

**Changes:**
- Keep control plane (DI Container, Curator, Smart City) on EC2/GCE
- Move execution plane (Realms, Agents, APIs) to Cloud Run
- Keep data plane (Redis, ArangoDB) on EC2 with persistent volumes

**Benefits:**
- Autoscaling for stateless services
- Reduced infrastructure management
- Better resource utilization

### Phase 2: Hybrid Cloud (Mid-Term)

**Goal:** Move to managed services where possible

**Architecture:**
```
Control Plane (GKE StatefulSets)
├── DI Container
├── Curator (Consul)
└── Smart City Gateway

Data Plane (Managed Services)
├── Redis → GCP MemoryStore
├── ArangoDB → ArangoDB Oasis (or GCE with Persistent Disk)
└── Supabase → Supabase Cloud (already managed)

Execution Plane (Cloud Run)
├── Business Enablement Realms
├── Journey/Solution Managers
├── Agentic APIs
└── Frontend
```

**Benefits:**
- Managed database services (backups, scaling, monitoring)
- Serverless execution (pay-per-use)
- Reduced operational overhead

### Phase 3: Option C - Fully Managed SaaS (Long-Term)

**Goal:** Zero DevOps, fully managed infrastructure

**Architecture:**
```
Data Plane (Fully Managed)
├── Redis → Upstash / MemoryStore
├── ArangoDB → ArangoDB Oasis
├── Supabase → Supabase Cloud
├── Meilisearch → Meilisearch Cloud
└── Telemetry → Grafana Cloud

Control Plane (GKE StatefulSets)
├── DI Container
├── Curator
└── Smart City Gateway

Execution Plane (Cloud Run)
├── All Realms
├── All Agents
├── All APIs
└── Frontend
```

**Benefits:**
- ✅ Zero DevOps overhead
- ✅ Automatic scaling
- ✅ Managed backups and monitoring
- ✅ SOC 2/ISO certified isolation
- ✅ Pay-per-use pricing

**Trade-offs:**
- Less flexibility for custom configurations
- Vendor lock-in considerations
- Potentially higher costs at scale

### Migration Path

1. **Start with Data Plane** (Lowest Risk)
   - Migrate Redis to MemoryStore
   - Migrate ArangoDB to Oasis
   - Keep Supabase Cloud (already managed)

2. **Move Execution Plane** (Medium Risk)
   - Deploy Realms to Cloud Run
   - Deploy Agents to Cloud Run
   - Deploy Frontend to Cloud Run

3. **Control Plane Last** (Highest Risk)
   - Migrate DI Container to GKE StatefulSet
   - Migrate Curator to GKE StatefulSet
   - Migrate Smart City Gateway to GKE Deployment

### Configuration Evolution

**Current (EC2):**
- `.env.secrets` file on server
- Environment variables in shell
- Manual secret management

**Phase 2 (Hybrid):**
- Secrets in GCP Secret Manager
- Environment variables via GKE ConfigMaps
- Managed secret rotation

**Phase 3 (Option C):**
- All secrets in cloud secret managers
- Automatic secret rotation
- Zero-touch secret management

---

## Best Practices

### Development

1. **Always use `.env.secrets`** - Never commit secrets to version control
2. **Use `startup.sh`** - Ensures proper startup sequence
3. **Check logs** - Use `docker logs` and application logs for debugging
4. **Health checks** - Verify all services before starting next phase

### Production

1. **Infrastructure first** - Always start infrastructure before backend
2. **Health monitoring** - Set up alerts for service health
3. **Backup strategy** - Regular backups of ArangoDB and Redis
4. **Secret rotation** - Rotate secrets regularly
5. **Log aggregation** - Centralize logs for debugging

### Security

1. **Never commit `.env.secrets`** - Use `.gitignore`
2. **Use strong secrets** - Generate cryptographically secure keys
3. **Limit access** - Restrict who can access secrets
4. **Audit logs** - Monitor access to sensitive configuration

---

## Additional Resources

- **Architecture Documentation**: `docs/architecture-diagrams.md`
- **Configuration Guide**: `docs/111125_archive/CONFIGURATION_GUIDE.md`
- **Hybrid Cloud Strategy**: `../docs/hybridcloudstrategy.md`
- **Startup Warnings**: `docs/STARTUP_WARNINGS_AND_ISSUES.md`

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `docker logs <container-name>`
3. Check health endpoints
4. Review configuration files

---

**Last Updated:** 2025-01-XX
**Version:** 1.0
**Maintainer:** Platform Team




