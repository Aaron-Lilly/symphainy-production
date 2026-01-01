# Frontend Container Issue - Resolved ✅

**Date:** December 4, 2024  
**Issue:** Frontend container taking too long to start, health check failing  
**Status:** ✅ **RESOLVED**

---

## 🔍 **Root Cause**

The frontend container was failing health checks because Next.js was binding to the container's specific IP address (`172.18.0.15:3000`) instead of `0.0.0.0:3000`. This caused:

1. **Health check failures**: The health check tried to connect to `localhost:3000`, but Next.js wasn't listening on localhost
2. **Container marked as unhealthy**: Docker health check kept failing
3. **Traefik route not discovered**: Traefik couldn't route to the frontend because it was unhealthy

### Why This Happened

Next.js standalone builds use the `HOSTNAME` environment variable to determine which interface to bind to. Docker automatically sets `HOSTNAME` to the container's hostname (container ID), which overrides any default value in the code.

The `server.js` file uses:
```javascript
const hostname = process.env.HOSTNAME || '0.0.0.0'
```

Since Docker sets `HOSTNAME=a8a613aed2a8`, Next.js was binding to that specific IP instead of all interfaces.

---

## ✅ **Solution**

### 1. Added HOSTNAME=0.0.0.0 to Dockerfile
```dockerfile
ENV HOSTNAME=0.0.0.0
```

### 2. Added HOSTNAME=0.0.0.0 to docker-compose.prod.yml
```yaml
environment:
  - HOSTNAME=0.0.0.0
```

This ensures Next.js binds to all interfaces (`0.0.0.0:3000`), making it accessible from:
- `localhost:3000` (for health checks)
- Container IP (for Traefik routing)
- All network interfaces

---

## 📊 **Results**

### Before Fix
- ❌ Health check: FAILING
- ❌ Container status: `unhealthy`
- ❌ Next.js listening on: `172.18.0.15:3000` (container IP only)
- ❌ Traefik route: Not discovered

### After Fix
- ✅ Health check: PASSING
- ✅ Container status: `healthy`
- ✅ Next.js listening on: `0.0.0.0:3000` (all interfaces)
- ✅ Traefik route: Discovered and working
- ✅ Frontend accessible: `http://localhost`

---

## 🔧 **Files Modified**

1. **`symphainy-frontend/Dockerfile`**
   - Added `ENV HOSTNAME=0.0.0.0`

2. **`docker-compose.prod.yml`**
   - Added `HOSTNAME=0.0.0.0` to frontend environment variables
   - Fixed middleware reference: `frontend-chain@file` (was `frontend-chain`)

---

## ✅ **Verification**

```bash
# Container is healthy
docker ps | grep frontend
# Output: ... (healthy) ...

# Next.js listening on all interfaces
docker exec symphainy-frontend-prod netstat -tlnp | grep 3000
# Output: tcp  0.0.0.0:3000  LISTEN

# Health check passes
docker exec symphainy-frontend-prod wget --spider http://localhost:3000
# Output: ✅ Health check: PASSED

# Traefik discovered route
curl http://localhost:8080/api/http/routers | grep frontend
# Output: "name": "frontend@docker"

# Frontend accessible
curl http://localhost
# Output: HTML content (not 404)
```

---

## 📝 **Lessons Learned**

1. **Docker HOSTNAME variable**: Docker automatically sets `HOSTNAME` to the container's hostname, which can override application defaults
2. **Next.js standalone builds**: Need explicit `HOSTNAME=0.0.0.0` to bind to all interfaces
3. **Health checks**: Must match the actual listening interface
4. **Traefik discovery**: Requires healthy containers to discover routes

---

## 🎯 **Status**

✅ **Frontend container is now healthy and working correctly!**

The frontend is:
- Starting quickly (Ready in ~76ms)
- Passing health checks
- Accessible through Traefik
- Ready for production use

