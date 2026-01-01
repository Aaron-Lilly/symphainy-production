# Docker Health Check Analysis

## Current State

### Services and Their Health Checks

1. **ArangoDB** (line 20): Uses `wget --spider`
2. **Redis** (line 40): Uses `redis-cli ping` ✅ (native tool)
3. **Meilisearch** (line 62): Uses `curl`
4. **Consul** (line 92): Uses `curl`
5. **Tempo** (line 116): Uses `curl`
6. **Grafana** (line 230): Uses `curl`
7. **OPA** (line 249): Uses `curl`
8. **Celery Worker/Beat** (lines 171, 205): Uses `celery inspect ping` ✅ (native tool)
9. **OpenTelemetry Collector** (line 139): No health check (relies on service_started)

## Container Image Analysis

### ArangoDB 3.11
**Base Image**: Alpine Linux (minimal)
**Available Tools**: 
- `wget` - ✅ Available (Alpine includes busybox wget)
- `curl` - ❌ NOT available by default
- Native: ArangoDB HTTP API at `/_api/version`

**Current Health Check**:
```yaml
test: ["CMD", "wget", "--spider", "http://127.0.0.1:8529/_api/version"]
```

**Recommendation**: ✅ **KEEP wget** - This is correct for Alpine-based images
- Alternative: Use ArangoDB's built-in HTTP endpoint
- Note: `--spider` flag makes wget not download, just check availability

### Consul (hashicorp/consul:latest)
**Base Image**: Alpine Linux
**Available Tools**:
- `curl` - ✅ Available (Consul image includes curl)
- `wget` - ✅ Available (Alpine includes busybox wget)
- Native: Consul HTTP API at `/v1/status/leader`

**Current Health Check**:
```yaml
test: ["CMD", "curl", "-f", "http://localhost:8500/v1/status/leader"]
```

**Recommendation**: ✅ **KEEP curl** - Consul image includes curl

### Redis (redislabs/redisgraph:latest)
**Base Image**: Debian/Ubuntu
**Available Tools**:
- `redis-cli` - ✅ Available (native Redis tool)
- `curl` - ✅ Available
- `wget` - ✅ Available

**Current Health Check**:
```yaml
test: ["CMD", "redis-cli", "ping"]
```

**Recommendation**: ✅ **PERFECT** - Using native Redis tool (best practice)

### Meilisearch (getmeili/meilisearch:v1.5)
**Base Image**: Debian/Ubuntu
**Available Tools**:
- `curl` - ✅ Available
- `wget` - ✅ Available
- Native: HTTP endpoint at `/health`

**Current Health Check**:
```yaml
test: ["CMD", "curl", "-f", "http://localhost:7700/health"]
```

**Recommendation**: ✅ **KEEP curl** - Meilisearch image includes curl

### Tempo (grafana/tempo:latest)
**Base Image**: Alpine Linux
**Available Tools**:
- `curl` - ✅ Available (Grafana images include curl)
- `wget` - ✅ Available (Alpine includes busybox wget)
- Native: HTTP endpoint at `/status`

**Current Health Check**:
```yaml
test: ["CMD", "curl", "-f", "http://localhost:3200/status"]
```

**Recommendation**: ✅ **KEEP curl** - Tempo image includes curl

### Grafana (grafana/grafana:latest)
**Base Image**: Alpine Linux
**Available Tools**:
- `curl` - ✅ Available (Grafana images include curl)
- `wget` - ✅ Available (Alpine includes busybox wget)
- Native: HTTP endpoint at `/api/health`

**Current Health Check**:
```yaml
test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
```

**Recommendation**: ✅ **KEEP curl** - Grafana image includes curl

### OPA (openpolicyagent/opa:latest)
**Base Image**: Alpine Linux
**Available Tools**:
- `curl` - ✅ Available (OPA image includes curl)
- `wget` - ✅ Available (Alpine includes busybox wget)
- Native: HTTP endpoint at `/health`

**Current Health Check**:
```yaml
test: ["CMD", "curl", "-f", "http://localhost:8181/health"]
```

**Recommendation**: ✅ **KEEP curl** - OPA image includes curl

### OpenTelemetry Collector (otel/opentelemetry-collector-contrib:latest)
**Base Image**: Alpine Linux (distroless-like)
**Available Tools**:
- `curl` - ❌ NOT available
- `wget` - ❌ NOT available
- Native: No built-in health endpoint

**Current Health Check**: None (relies on `service_started`)

**Recommendation**: ✅ **CORRECT** - OTel collector doesn't include HTTP tools
- Alternative: Use `depends_on` with `condition: service_started` (current approach)
- Alternative: Check logs for "Everything is ready" message
- Alternative: Use Prometheus metrics endpoint if configured

### Celery Worker/Beat (Custom Dockerfile)
**Base Image**: python:3.10-slim (Debian)
**Available Tools**:
- `celery` - ✅ Available (installed via pip)
- `curl` - ✅ Available (if installed in Dockerfile)
- `wget` - ✅ Available

**Current Health Check**:
```yaml
test: ["CMD", "celery", "-A", "main.celery", "inspect", "ping"]
```

**Recommendation**: ✅ **PERFECT** - Using native Celery tool (best practice)

## Best Practices Summary

### ✅ Good Practices (Already Implemented)
1. **Redis**: Uses native `redis-cli ping` ✅
2. **Celery**: Uses native `celery inspect ping` ✅
3. **ArangoDB**: Uses `wget` (correct for Alpine) ✅
4. **OpenTelemetry Collector**: No health check (correct - tool not available) ✅

### ⚠️ Potential Issues

1. **ArangoDB wget command**: Current command is correct, but let's verify the exact syntax
   - Current: `["CMD", "wget", "--spider", "http://127.0.0.1:8529/_api/version"]`
   - Should work, but `--spider` might need `-q` flag for quiet mode
   - Alternative: `["CMD", "wget", "--spider", "-q", "http://127.0.0.1:8529/_api/version"]`

2. **Health check timeouts**: Some may be too short
   - ArangoDB: 10s timeout (good)
   - Consul: 10s timeout (good)
   - Tempo: 5s timeout (might be tight)

3. **Start periods**: Some services need more time
   - ArangoDB: 60s start_period ✅ (good - ArangoDB can be slow to start)
   - Consul: 40s start_period ✅ (good)
   - Meilisearch: 20s start_period (might need more)

## Recommended Health Check Strategy

### Option 1: Use Native Tools (Best Practice)
When a service provides a native health check tool, use it:
- ✅ Redis: `redis-cli ping`
- ✅ Celery: `celery inspect ping`

### Option 2: Use HTTP Endpoints with Available Tools
When native tools aren't available, use HTTP endpoints:
- ✅ ArangoDB: `wget --spider` (Alpine has wget)
- ✅ Consul: `curl` (Consul image includes curl)
- ✅ Meilisearch: `curl` (Meilisearch image includes curl)
- ✅ Tempo: `curl` (Tempo image includes curl)
- ✅ Grafana: `curl` (Grafana image includes curl)
- ✅ OPA: `curl` (OPA image includes curl)

### Option 3: Use Service Dependencies
When no tools are available:
- ✅ OpenTelemetry Collector: Use `depends_on` with `service_started`

## Recommended Fixes

### 1. ArangoDB Health Check (Improve)
```yaml
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "http://127.0.0.1:8529/_api/version"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```
**Change**: Add `-q` flag for quiet mode (suppresses output)

### 2. Verify All Health Checks Work
Test each health check manually:
```bash
# Test ArangoDB
docker exec symphainy-arangodb wget --spider -q http://127.0.0.1:8529/_api/version

# Test Consul
docker exec symphainy-consul curl -f http://localhost:8500/v1/status/leader

# Test Redis
docker exec symphainy-redis redis-cli ping

# Test Meilisearch
docker exec symphainy-meilisearch curl -f http://localhost:7700/health
```

### 3. Consider Alternative: ArangoDB HTTP Client
If wget continues to cause issues, we could:
- Install curl in a custom ArangoDB image
- Use a Python script with requests library
- Use ArangoDB's built-in health endpoint differently

## Conclusion

**Current configuration is mostly correct!** The issue is likely:
1. ArangoDB wget command syntax (add `-q` flag)
2. Health check timing (intervals/timeouts)
3. Container restart loops due to failed health checks

**Next Steps**:
1. Add `-q` flag to ArangoDB wget command
2. Test all health checks manually
3. Monitor container logs for health check failures
4. Adjust timeouts/start_periods if needed

