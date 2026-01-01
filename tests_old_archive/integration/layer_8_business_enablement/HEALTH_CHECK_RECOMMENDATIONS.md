# Docker Health Check Recommendations

## Summary

After investigating all container images, here's what we found:

### ✅ Current Configuration is Mostly Correct

1. **ArangoDB**: Using `wget` is correct (Alpine image doesn't have curl)
2. **Redis**: Using `redis-cli ping` is perfect (native tool)
3. **Celery**: Using `celery inspect ping` is perfect (native tool)
4. **Consul, Meilisearch, Tempo, Grafana, OPA**: All use `curl` which is available in their images

### 🔧 Recommended Improvements

#### 1. ArangoDB Health Check (IMPROVED)
**Before**:
```yaml
test: ["CMD", "wget", "--spider", "http://127.0.0.1:8529/_api/version"]
```

**After** (with better flags):
```yaml
test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://127.0.0.1:8529/_api/version"]
```

**Why**:
- `-q`: Quiet mode (suppresses output, cleaner logs)
- `-O /dev/null`: Explicitly discard output (some wget versions require output destination)
- `--spider`: Still checks URL without downloading

#### 2. Alternative: Use Shell Script for ArangoDB
If wget continues to cause issues, we could create a simple health check script:

```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --spider -q -O /dev/null http://127.0.0.1:8529/_api/version || exit 1"]
```

Or use a Python-based health check (if Python is available):
```yaml
healthcheck:
  test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8529/_api/version')"]
```

## Health Check Best Practices

### 1. Use Native Tools When Available
✅ **Redis**: `redis-cli ping`
✅ **Celery**: `celery inspect ping`

### 2. Use HTTP Endpoints with Available Tools
✅ **ArangoDB**: `wget` (Alpine has wget)
✅ **Consul**: `curl` (Consul image includes curl)
✅ **Meilisearch**: `curl` (Meilisearch image includes curl)
✅ **Tempo**: `curl` (Tempo image includes curl)
✅ **Grafana**: `curl` (Grafana image includes curl)
✅ **OPA**: `curl` (OPA image includes curl)

### 3. Handle Services Without HTTP Tools
✅ **OpenTelemetry Collector**: Use `depends_on` with `service_started` (no HTTP tools available)

## Testing Health Checks

To verify health checks work, test each one manually:

```bash
# ArangoDB
docker exec symphainy-arangodb wget --spider -q -O /dev/null http://127.0.0.1:8529/_api/version
echo $?  # Should return 0

# Consul
docker exec symphainy-consul curl -f http://localhost:8500/v1/status/leader
echo $?  # Should return 0

# Redis
docker exec symphainy-redis redis-cli ping
# Should return: PONG

# Meilisearch
docker exec symphainy-meilisearch curl -f http://localhost:7700/health
echo $?  # Should return 0
```

## Troubleshooting Health Check Failures

### If ArangoDB Health Check Fails:

1. **Check if wget is available**:
   ```bash
   docker exec symphainy-arangodb which wget
   ```

2. **Test wget manually**:
   ```bash
   docker exec symphainy-arangodb wget --spider -q -O /dev/null http://127.0.0.1:8529/_api/version
   ```

3. **Check ArangoDB logs**:
   ```bash
   docker logs symphainy-arangodb
   ```

4. **Verify ArangoDB is responding**:
   ```bash
   curl http://localhost:8529/_api/version
   ```

### If Health Checks Cause Restart Loops:

1. **Increase start_period**: Give services more time to start
2. **Increase timeout**: Some services are slow to respond
3. **Increase retries**: Allow more failures before marking unhealthy
4. **Check service logs**: The service might be failing to start

## Recommended Health Check Configuration

### ArangoDB (Alpine-based)
```yaml
healthcheck:
  test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://127.0.0.1:8529/_api/version"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s  # ArangoDB can be slow to start
```

### Consul (Alpine-based, includes curl)
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8500/v1/status/leader"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Redis (Native tool - best practice)
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Next Steps

1. ✅ Update ArangoDB health check with improved flags
2. Test all health checks manually
3. Monitor container logs for health check failures
4. Adjust timeouts/start_periods if services are slow to start
5. Consider creating a health check test script to verify all checks work

