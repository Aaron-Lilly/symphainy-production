# Safe Docker Commands Quick Reference

## Quick Inspection Commands

### Check Container Status (Safe - Fast)
```bash
# List all SymphAIny containers
docker ps -a --filter name=symphainy-

# Check specific container status
docker ps --filter name=symphainy-consul

# Check container state
docker inspect --format '{{.State.Status}}' symphainy-consul
```

### Check Container Health (Safe - Fast)
```bash
# Check health status
docker inspect --format '{{.State.Health.Status}}' symphainy-consul

# Check health with details
docker inspect --format '{{json .State.Health}}' symphainy-consul | jq

# Check failing streak (indicates restart loops)
docker inspect --format '{{.State.Health.FailingStreak}}' symphainy-consul
```

### Get Container Logs (Use Timeout!)
```bash
# SAFE: Limited lines with timeout
timeout 5 docker logs --tail 50 symphainy-consul

# SAFE: Recent logs only
timeout 5 docker logs --since 5m symphainy-consul

# SAFE: Last 100 lines
timeout 5 docker logs --tail 100 symphainy-consul
```

### Check Container Ports (Safe - Fast)
```bash
# Check port mappings
docker port symphainy-consul
docker port symphainy-arangodb
```

## Using the Safe Inspection Script

### Basic Usage
```bash
# Check all containers
python3 safe_docker_inspect.py --all

# Check specific container
python3 safe_docker_inspect.py symphainy-consul

# Check only health (faster)
python3 safe_docker_inspect.py --all --health

# Skip logs (faster)
python3 safe_docker_inspect.py --all --no-logs
```

### Output
The script saves results to a JSON file:
```bash
docker_inspect_20250115_143022.json
```

## Critical Container Checks

### Consul
```bash
# Quick health check
docker inspect --format '{{.State.Health.Status}}' symphainy-consul

# Check if running
docker ps --filter name=symphainy-consul --format '{{.Status}}'

# Safe log check
timeout 5 docker logs --tail 20 symphainy-consul
```

### ArangoDB
```bash
# Quick health check
docker inspect --format '{{.State.Health.Status}}' symphainy-arangodb

# Check if running
docker ps --filter name=symphainy-arangodb --format '{{.Status}}'

# Safe log check
timeout 5 docker logs --tail 20 symphainy-arangodb
```

### Redis
```bash
# Quick status check
docker ps --filter name=symphainy-redis --format '{{.Status}}'

# Test connection (safe - has timeout)
timeout 3 docker exec symphainy-redis redis-cli ping
```

## What to Avoid

### ❌ DON'T Run These Without Timeout
```bash
# BAD: Can hang if container is stuck
docker logs symphainy-consul

# BAD: Can hang if container is unresponsive
docker exec symphainy-consul curl http://localhost:8500/v1/status/leader

# BAD: Can hang if Docker daemon is slow
docker stats symphainy-consul
```

### ✅ DO Use These Safe Alternatives
```bash
# GOOD: With timeout
timeout 5 docker logs --tail 50 symphainy-consul

# GOOD: Use the safe script
python3 safe_docker_inspect.py symphainy-consul

# GOOD: Limited output
docker logs --tail 20 --since 1m symphainy-consul
```

## Emergency Procedures

### If Container is Stuck
```bash
# Check if container is running
docker ps --filter name=symphainy-consul

# Stop container (if needed)
docker stop symphainy-consul

# Restart container
docker restart symphainy-consul

# Remove and recreate (if needed)
docker-compose -f docker-compose.infrastructure.yml up -d consul
```

### If Test is Hanging
```bash
# Find pytest process
ps aux | grep pytest

# Kill specific test
pkill -f "pytest.*test_file_parser_core"

# Kill all pytest processes (use with caution)
pkill -9 pytest
```

## Monitoring Container Health

### Check for Restart Loops
```bash
# Check restart count
docker inspect --format '{{.RestartCount}}' symphainy-consul

# Check health failing streak
docker inspect --format '{{.State.Health.FailingStreak}}' symphainy-consul

# If failing_streak > 0, container is in restart loop
```

### Check Resource Usage
```bash
# Quick resource check (safe - limited output)
timeout 3 docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" symphainy-consul
```

## Best Practices

1. ✅ **Always use timeouts** for Docker commands that might hang
2. ✅ **Use the safe inspection script** for comprehensive checks
3. ✅ **Check health status first** before getting logs
4. ✅ **Limit log output** with `--tail` or `--since`
5. ✅ **Monitor restart counts** to detect restart loops
6. ✅ **Use `docker ps`** for quick status checks (fast, safe)

