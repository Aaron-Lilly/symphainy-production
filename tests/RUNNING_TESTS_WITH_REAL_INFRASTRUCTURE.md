# Running Tests with Real Infrastructure

## Overview

This guide explains how to run integration and E2E tests with real infrastructure to validate that the platform actually works.

## Container Requirements

### For Integration Tests

**Required Containers (already running):**
- ✅ **ArangoDB** (`symphainy-arangodb`) - Port 8529
- ✅ **Redis** (`symphainy-redis`) - Port 6379
- ✅ **Consul** (`symphainy-consul`) - Port 8500
- ✅ **Meilisearch** (`symphainy-meilisearch`) - Port 7700

**Status:** All required containers are running and healthy.

### For E2E Tests

**Required:**
- ✅ **Backend Container** (`symphainy-backend-prod`) - Port 8000 (already running and healthy)
- ✅ **Frontend Container** (`symphainy-frontend-prod`) - Port 3000 (already running)
- ⚠️ **Supabase** - Cloud service (needs configuration via environment variables)

**Note:** E2E tests require Supabase credentials because they test the full flow including file upload/authentication.

## Environment Variables Setup

### For Integration Tests (No Supabase Required)

```bash
export TEST_USE_REAL_INFRASTRUCTURE=true
export TEST_BACKEND_URL="http://localhost:8000"
export TEST_ARANGO_URL="http://localhost:8529"
export TEST_ARANGO_DB="symphainy_test"
export TEST_ARANGO_USER="root"
export TEST_ARANGO_PASS=""  # Empty password for local ArangoDB
export TEST_REDIS_URL="redis://localhost:6379"
export TEST_CONSUL_HOST="localhost"
export TEST_CONSUL_PORT="8500"
export TEST_USE_REAL_LLM=false  # Use mocks for LLM to avoid API costs
```

### For E2E Tests (Supabase Required)

Add these to the above:
```bash
export TEST_SUPABASE_URL="your_supabase_project_url"
export TEST_SUPABASE_ANON_KEY="your_supabase_anon_key"
export TEST_SUPABASE_SERVICE_KEY="your_supabase_service_key"  # Optional
```

### For Embedding Tests (HuggingFace Required)

```bash
export TEST_HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
export TEST_HUGGINGFACE_EMBEDDINGS_API_KEY="your_huggingface_api_key"
```

## Running Tests

### Integration Tests

```bash
cd /home/founders/demoversion/symphainy_source/tests

# Set environment variables (see above)
export TEST_USE_REAL_INFRASTRUCTURE=true
export TEST_BACKEND_URL="http://localhost:8000"
export TEST_ARANGO_URL="http://localhost:8529"
export TEST_ARANGO_DB="symphainy_test"
export TEST_ARANGO_USER="root"
export TEST_ARANGO_PASS=""
export TEST_REDIS_URL="redis://localhost:6379"
export TEST_CONSUL_HOST="localhost"
export TEST_CONSUL_PORT="8500"
export TEST_USE_REAL_LLM=false

# Run integration tests
pytest integration/pillar/test_content_pillar_integration.py -v -k "embedding"
```

### E2E Tests

```bash
# Add Supabase configuration
export TEST_SUPABASE_URL="your_supabase_url"
export TEST_SUPABASE_ANON_KEY="your_supabase_anon_key"

# Run E2E tests
pytest e2e/production/pillar_validation/test_content_pillar_e2e.py -v -k "embedding"
```

## Container Status Check

```bash
# Check if containers are running
docker ps | grep symphainy

# Check backend health
curl http://localhost:8000/health

# Check ArangoDB
curl http://localhost:8529/_api/version

# Check Redis
redis-cli -h localhost ping

# Check Consul
curl http://localhost:8500/v1/status/leader
```

## Do We Need to Start Containers?

**Answer: No, containers are already running!**

All required infrastructure containers are already up and healthy:
- ✅ ArangoDB (port 8529)
- ✅ Redis (port 6379)
- ✅ Consul (port 8500)
- ✅ Meilisearch (port 7700)
- ✅ Backend (port 8000)
- ✅ Frontend (port 3000)

**The only thing needed is:**
1. Environment variables configured (see above)
2. For E2E tests: Supabase credentials (cloud service, not a container)

## Troubleshooting

### Tests Skipped Due to Missing Infrastructure

If tests are skipped with "Real infrastructure not available", check:
1. Containers are running: `docker ps | grep symphainy`
2. Environment variables are set: `env | grep TEST_`
3. Ports are accessible: `curl http://localhost:8529/_api/version`

### Integration Test Failures

If integration tests fail:
1. Check that mocks are set up correctly
2. Verify that the code path being tested actually calls the mocked methods
3. Check logs for actual errors vs. assertion failures

### E2E Test Failures

If E2E tests fail:
1. Verify backend is healthy: `curl http://localhost:8000/health`
2. Check Supabase credentials are correct
3. Verify network connectivity between test runner and backend

## Summary

- **Containers:** Already running ✅
- **Integration Tests:** Can run with current setup (just need env vars) ✅
- **E2E Tests:** Need Supabase credentials ⚠️
- **Backend:** Healthy and accessible ✅




