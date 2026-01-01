# ArangoDB Test Setup Guide

## Current Situation

- **ArangoDB Config:** In `config/development.env` (ARANGO_URL, ARANGO_DB, ARANGO_USER, ARANGO_PASS)
- **ArangoDB Location:** Running as container in GCE VM
- **Startup:** Need to start infrastructure containers first

---

## Step 1: Start Infrastructure Containers

**Option A: Use Infrastructure Orchestration Script (Recommended)**

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
./scripts/infrastructure-orchestration.sh
```

This script:
- Starts Redis, Consul, ArangoDB
- Waits for services to be ready
- Performs health checks

**Option B: Use Start Infrastructure Script**

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
./scripts/start-infrastructure.sh
```

This script starts:
- Consul (Service Discovery)
- Redis (Cache & Message Broker)
- ArangoDB (Metadata Storage)
- Tempo (Distributed Tracing)
- OpenTelemetry Collector
- Celery Worker
- Celery Beat
- Grafana

**Option C: Use Docker Compose Directly**

```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
docker-compose -f docker-compose.infrastructure.yml up -d arangodb
```

---

## Step 2: Verify ArangoDB is Running

```bash
# Check if ArangoDB container is running
docker ps | grep arangodb

# Check if ArangoDB is responding
curl http://localhost:8529/_api/version

# Should return JSON with version info
```

---

## Step 3: Load Environment Variables

The test script needs these environment variables (from `config/development.env`):

```bash
# Load from development.env (if using environment loader)
# Or set manually:
export ARANGO_URL="http://localhost:8529"
export ARANGO_DB="symphainy_metadata"
export ARANGO_USER="root"
export ARANGO_PASS=""  # Default is empty
```

**Note:** If your platform's environment loader is running, these should already be loaded from `config/development.env`.

---

## Step 4: Run Test

```bash
cd /home/founders/demoversion/symphainy_source
python3 scripts/test_arango_embeddings.py
```

---

## Troubleshooting

### "Connection refused" or "Failed to connect"
- **Cause:** ArangoDB container not running
- **Solution:** Start infrastructure containers first (Step 1)

### "Authentication failed"
- **Cause:** Wrong username/password
- **Solution:** Check ARANGO_USER and ARANGO_PASS in `config/development.env`

### "Database not found"
- **Cause:** Database doesn't exist
- **Solution:** ArangoDB will create database on first connection, or create manually:
  ```bash
  docker exec -it symphainy-arangodb arangosh --server.authentication false
  db._createDatabase("symphainy_metadata")
  ```

### Environment variables not loaded
- **Cause:** Platform environment loader not running
- **Solution:** Either:
  1. Start platform (which loads config)
  2. Or set environment variables manually before running test

---

## Quick Test (Without Full Platform)

If you just want to test ArangoDB connection without starting the full platform:

```bash
# 1. Start just ArangoDB
cd /home/founders/demoversion/symphainy_source/symphainy-platform
docker-compose -f docker-compose.infrastructure.yml up -d arangodb

# 2. Wait for it to be ready
sleep 10

# 3. Set environment variables manually
export ARANGO_URL="http://localhost:8529"
export ARANGO_DB="symphainy_metadata"
export ARANGO_USER="root"
export ARANGO_PASS=""

# 4. Run test
cd /home/founders/demoversion/symphainy_source
python3 scripts/test_arango_embeddings.py
```

---

## Which Startup Script to Use?

**For Testing (Minimal):**
- Use `infrastructure-orchestration.sh` - starts only essential services (Redis, Consul, ArangoDB)

**For Full Development:**
- Use `start-infrastructure.sh` - starts all infrastructure services (10+ containers)

**For Platform Development:**
- Use `start-dev-environment.sh` - starts infrastructure → backend → frontend

**For MVP/Testing:** Start with `infrastructure-orchestration.sh` - it's the simplest and fastest.






