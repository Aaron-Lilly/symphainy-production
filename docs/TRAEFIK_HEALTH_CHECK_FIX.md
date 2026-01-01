# Traefik Health Check Fix

**Date:** 2025-12-05  
**Issue:** Traefik health check failing - `wget` command may not be available or `/ping` endpoint not enabled

---

## Problem

The Traefik health check was using:
```yaml
test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://localhost:8080/ping"]
```

**Issues:**
1. `/ping` endpoint not enabled (missing `--ping=true` in command)
2. Health check command syntax may need adjustment
3. Using `localhost` instead of `127.0.0.1` (less reliable in containers)

---

## Fix Applied

### 1. Enabled Ping Endpoint
Added `--ping=true` to Traefik command to enable the `/ping` health check endpoint.

### 2. Updated Health Check Command
Changed from:
```yaml
test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://localhost:8080/ping"]
```

To:
```yaml
test: ["CMD", "wget", "--spider", "--tries=1", "--no-verbose", "--timeout=5", "http://127.0.0.1:8080/ping"]
```

**Improvements:**
- Uses `127.0.0.1` instead of `localhost` (more reliable)
- Added `--tries=1` to prevent retries (health check should be quick)
- Added `--timeout=5` to prevent hanging
- Removed `-O /dev/null` (not needed with `--spider`)
- Added `--no-verbose` for cleaner output

---

## Alternative Health Check Options

If `wget` is still not available in the Traefik image, here are alternatives:

### Option 1: Use API Endpoint (If Available)
```yaml
healthcheck:
  # Use API endpoint instead of ping (API is already enabled)
  test: ["CMD", "wget", "--spider", "--tries=1", "--no-verbose", "--timeout=5", "http://127.0.0.1:8080/api/rawdata"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

### Option 2: Check if Process is Running (Less Reliable)
```yaml
healthcheck:
  # Check if Traefik process is running (fallback if no HTTP tools available)
  test: ["CMD-SHELL", "pgrep traefik || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s
```

**Note:** This only checks if the process is running, not if it's actually serving requests.

### Option 3: Use External Health Check (From Another Container)
If Traefik image truly has no HTTP tools, you could:
1. Remove the health check from Traefik itself
2. Use an external health check service
3. Or rely on Docker's automatic restart on failure

---

## Verification

After applying the fix:

1. **Restart Traefik:**
   ```bash
   docker-compose restart traefik
   ```

2. **Check Health Status:**
   ```bash
   docker ps | grep traefik
   # Should show "healthy" status
   ```

3. **Test Ping Endpoint Manually:**
   ```bash
   docker exec symphainy-traefik wget --spider --tries=1 --no-verbose http://127.0.0.1:8080/ping
   # Should return exit code 0 if working
   ```

4. **Check Traefik Logs:**
   ```bash
   docker logs symphainy-traefik | grep -i ping
   # Should show ping endpoint is enabled
   ```

---

## Traefik v3.0 Image Details

According to Traefik documentation:
- **Base Image:** Minimal Alpine-based image
- **Available Tools:** `wget` is included in Traefik v3.0 images
- **Ping Endpoint:** Requires `--ping=true` flag to enable

If `wget` is still not found, it may indicate:
1. Image version mismatch
2. Custom image build without wget
3. Image corruption

---

## Next Steps

1. ✅ **Applied Fix:** Added `--ping=true` and updated health check command
2. ⏳ **Test:** Restart Traefik and verify health check works
3. ⏳ **Monitor:** Watch Traefik logs for any health check errors

If health check still fails after this fix:
1. Check Traefik logs for specific error messages
2. Verify Traefik image version: `docker exec symphainy-traefik traefik version`
3. Test wget availability: `docker exec symphainy-traefik which wget`
4. Consider using alternative health check method above

---

**Status:** ✅ Fix applied, ready for testing


