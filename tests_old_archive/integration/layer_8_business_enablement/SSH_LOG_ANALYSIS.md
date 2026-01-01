# SSH Log Analysis

## What the SSH Logs Show

### Normal SSH Activity ✅

The SSH logs you're seeing are **normal keepalive pings** - this is expected behavior:

1. **Keepalive Pings**: Every minute, the SSH connection sends a ping to keep the connection alive
   - Pattern: `[remote-ssh] Pinging remote server via 127.0.0.1:62383...`
   - All pings are successful (exit code 0)
   - This is **normal and healthy**

2. **Port Forwarding**: The logs show port forwarding is active:
   - ArangoDB: `localhost:65140 -> localhost:8529`
   - Consul: `localhost:65141 -> localhost:8500`
   - OpenTelemetry: `localhost:4317 -> localhost:4317`
   - Redis: `localhost:62519 -> localhost:6379`
   - This is **normal** - allows local access to remote services

3. **Connection Stability**: The connection appears stable:
   - No connection errors
   - All commands exit successfully
   - Multiplex server is running normally

## Potential Background Issues

While the SSH logs themselves look normal, there could be **background issues** affecting system resources:

### 1. Docker Container Restart Loops

**Symptom**: Containers restarting repeatedly
**Impact**: 
- Consumes CPU and memory
- Can cause system slowdown
- May affect SSH responsiveness

**Check**:
```bash
# Check restart counts
docker ps -a --format "{{.Names}}\t{{.RestartCount}}"

# Check health status
docker inspect --format '{{.State.Health.Status}}' symphainy-consul
docker inspect --format '{{.State.Health.Status}}' symphainy-arangodb
```

### 2. Resource Exhaustion

**Symptom**: High CPU/memory usage
**Impact**:
- System becomes unresponsive
- SSH commands may timeout
- Processes may hang

**Check**:
```bash
# Check memory
free -h

# Check CPU load
uptime

# Check disk space
df -h
```

### 3. Hanging Processes

**Symptom**: Processes consuming resources but not completing
**Impact**:
- Blocks system resources
- Can cause SSH timeouts
- May prevent new connections

**Check**:
```bash
# Check for hanging pytest processes
ps aux | grep pytest

# Check for high CPU processes
top -bn1 | head -20
```

### 4. Environment Variable Conflicts

**Symptom**: `GOOGLE_APPLICATION_CREDENTIALS` set incorrectly
**Impact**:
- Can break GCP authentication
- May affect SSH if using GCP credentials
- Could cause authentication failures

**Check**:
```bash
# Check if GOOGLE_APPLICATION_CREDENTIALS is set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Check if file exists
test -f "$GOOGLE_APPLICATION_CREDENTIALS" && echo "OK" || echo "MISSING"
```

## Using the Diagnostic Script

We've created `diagnose_background_issues.py` to check for these issues:

```bash
# Run diagnostic
python3 diagnose_background_issues.py

# This will check:
# - Docker container restart loops
# - Container health status
# - System resource usage
# - Hanging processes
# - Environment variable issues
```

## What We Fixed (Related to SSH)

### Previous Issue (Already Fixed)
- **Problem**: Tests were modifying `GOOGLE_APPLICATION_CREDENTIALS` globally
- **Impact**: Could break SSH access to GCP VMs
- **Fix**: ✅ Removed global modification - now uses test-specific variables

### Current Status
- ✅ SSH connection appears stable (normal keepalive pings)
- ✅ Port forwarding is working
- ✅ No connection errors in logs

## If You're Experiencing SSH Issues

### Quick Checks

1. **Check Docker containers**:
   ```bash
   python3 safe_docker_inspect.py --all --health
   ```

2. **Check for restart loops**:
   ```bash
   docker ps -a --format "{{.Names}}\t{{.RestartCount}}" | grep -v " 0$"
   ```

3. **Check system resources**:
   ```bash
   free -h && uptime && df -h /
   ```

4. **Check for hanging processes**:
   ```bash
   ps aux | grep -E "pytest|python" | grep -v grep
   ```

### If SSH is Actually Broken

1. **Check environment variables**:
   ```bash
   echo $GOOGLE_APPLICATION_CREDENTIALS
   ```

2. **If GOOGLE_APPLICATION_CREDENTIALS is set incorrectly**:
   ```bash
   unset GOOGLE_APPLICATION_CREDENTIALS
   # Or set to correct path
   export GOOGLE_APPLICATION_CREDENTIALS=/correct/path/to/credentials.json
   ```

3. **Check Docker daemon**:
   ```bash
   docker ps  # Should work quickly
   ```

4. **Check system load**:
   ```bash
   uptime  # Load should be reasonable
   ```

## Summary

**SSH Logs**: ✅ Normal - just keepalive pings (expected behavior)

**Potential Issues to Check**:
- Docker container restart loops
- System resource exhaustion
- Hanging processes
- Environment variable conflicts

**Next Steps**:
1. Run `diagnose_background_issues.py` to check for background issues
2. Run `safe_docker_inspect.py --all --health` to check container health
3. Check system resources if SSH is slow/unresponsive

The SSH logs themselves don't show errors - they're just normal connection maintenance. If you're experiencing issues, it's likely due to background resource consumption (Docker restart loops, hanging processes, etc.) rather than the SSH connection itself.

