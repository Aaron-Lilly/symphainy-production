# 🎯 CTO Demo Checklist - Production Verification

**Date:** December 2024  
**Purpose:** Verify all CTO demo cases work in production environment

---

## 📋 **Quick Reference**

### **Key URLs (Local)**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Consul UI: `http://localhost:8500/ui`
- Grafana: `http://localhost:3100` (admin/admin)
- ArangoDB: `http://localhost:8529`

### **Key URLs (Production - GCP VM)**
- Frontend: `http://35.215.64.103:3000`
- Backend API: `http://35.215.64.103:8000`
- Grafana: `http://35.215.64.103:3100`

### **Key Container Names**
- `symphainy-backend-prod` - Backend service
- `symphainy-frontend-prod` - Frontend service
- `symphainy-arangodb` - ArangoDB database
- `symphainy-redis` - Redis cache
- `symphainy-consul` - Consul service discovery
- `symphainy-meilisearch` - Meilisearch engine
- `symphainy-celery-worker` - Celery worker
- `symphainy-celery-beat` - Celery scheduler
- `symphainy-grafana` - Grafana monitoring
- `symphainy-loki` - Loki log aggregation
- `symphainy-tempo` - Tempo tracing
- `symphainy-otel-collector` - OpenTelemetry collector
- `symphainy-opa` - Open Policy Agent

### **Quick Commands**
```bash
# View all containers
docker ps | grep symphainy

# View logs (last 50 lines)
docker logs --tail 50 <container-name>

# Follow logs (real-time)
docker logs -f <container-name>

# Restart a service
docker restart <container-name>

# Check health
curl http://localhost:8000/health | python3 -m json.tool
```

---

## 🚀 **Quick Start Commands**

### **Start Platform**
```bash
cd /home/founders/demoversion/symphainy_source

# Start infrastructure (if not running)
cd symphainy-platform
docker-compose -f docker-compose.infrastructure.yml up -d
cd ..

# Start application services
docker-compose -f docker-compose.prod.yml up -d

# Wait for health checks (~60 seconds for full initialization)
echo "⏳ Waiting for services to initialize..."
sleep 60

# Verify backend is healthy
echo "🔍 Checking backend health..."
curl http://localhost:8000/health | python3 -m json.tool

# Verify frontend is responding
echo "🔍 Checking frontend..."
curl -I http://localhost:3000

# Quick status check
echo "📊 Container status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep symphainy
```

### **Stop Platform**
```bash
cd /home/founders/demoversion/symphainy_source

# Stop application services
docker-compose -f docker-compose.prod.yml down

# Stop infrastructure (optional - can leave running)
cd symphainy-platform
docker-compose -f docker-compose.infrastructure.yml down
cd ..
```

### **Quick Status Check**
```bash
# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}" | grep symphainy

# Check backend logs (last 50 lines)
docker logs --tail 50 symphainy-backend-prod

# Check frontend logs (last 50 lines)
docker logs --tail 50 symphainy-frontend-prod

# Check infrastructure services
cd /home/founders/demoversion/symphainy_source/symphainy-platform
docker-compose -f docker-compose.infrastructure.yml ps
```

---

## ✅ **Pre-Demo Verification**

### **0. Pre-Flight Checklist**
Before starting the demo, ensure:
- [ ] Docker and Docker Compose are installed and running
- [ ] Ports 3000, 8000, 8529, 6379, 8500, 7700, 3100, 3101, 3200 are available
- [ ] `.env.secrets` file exists in `symphainy-platform/` directory (if required)
- [ ] Sufficient disk space and memory available
- [ ] Network connectivity is working
- [ ] Previous containers are stopped (if restarting): `docker-compose -f docker-compose.prod.yml down`

---

### **1. System Health Check**
- [ ] Backend health endpoint returns `"platform_status": "operational"`
- [ ] Foundation services show as healthy (check `/foundation/services` endpoint)
- [ ] All 11 infrastructure services show as healthy (ArangoDB, Redis, Consul, Meilisearch, Tempo, OTel Collector, Celery Worker, Celery Beat, Grafana, Loki, OPA)
- [ ] Frontend responds with HTTP 200
- [ ] All containers are running (2 app + 11 infrastructure = 13 total)

**Quick Verification:**
```bash
# Check health status
curl http://localhost:8000/health | python3 -m json.tool | grep -E "(platform_status|foundation_services|infrastructure_services)"

# Count running containers
docker ps | grep symphainy | wc -l

# Check foundation services
curl http://localhost:8000/foundation/services | python3 -m json.tool
```

### **2. Infrastructure Services**
- [ ] ArangoDB: `http://localhost:8529` (or check health endpoint)
- [ ] Redis: `docker exec symphainy-redis redis-cli ping` returns `PONG`
- [ ] Consul: `http://localhost:8500/ui` (UI accessible)
- [ ] Meilisearch: `curl http://localhost:7700/health` returns healthy
- [ ] Tempo: `curl http://localhost:3200/status` returns status
- [ ] OTel Collector: Check logs for "Everything is ready"
- [ ] Celery Worker: `docker exec symphainy-celery-worker celery -A celery_app inspect ping` returns pong
- [ ] Celery Beat: Check logs for scheduled tasks
- [ ] Grafana: `http://localhost:3100` accessible (default: admin/admin)
- [ ] Loki: `curl http://localhost:3101/ready` returns `ready`
- [ ] OPA: `curl http://localhost:8181/health` returns healthy

**Quick Verification Script:**
```bash
# Test all infrastructure services
echo "Testing infrastructure services..."
echo "ArangoDB:" && curl -s http://localhost:8529/_api/version | head -1
echo "Redis:" && docker exec symphainy-redis redis-cli ping
echo "Consul:" && curl -s http://localhost:8500/v1/status/leader | head -1
echo "Meilisearch:" && curl -s http://localhost:7700/health | python3 -m json.tool | grep status
echo "Tempo:" && curl -s http://localhost:3200/status | head -1
echo "Grafana:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:3100
echo "Loki:" && curl -s http://localhost:3101/ready
echo "OPA:" && curl -s http://localhost:8181/health | python3 -m json.tool | grep -q healthy && echo "OK" || echo "Check logs"
```

### **3. Logging & Observability**
- [ ] Backend logs show trace_id in log entries
- [ ] Loki is receiving logs (check Grafana)
- [ ] Trace correlation working (trace_id in logs)

---

## 🎯 **CTO Demo Cases**

### **Case 1: Platform Startup & Health**
- [ ] Platform starts successfully
- [ ] Health validation passes (ArangoDB, Redis, Consul)
- [ ] All foundation services initialize
- [ ] Background tasks start (Nurse, Conductor, etc.)

**Verification:**
```bash
# Basic health check
curl http://localhost:8000/health | python3 -m json.tool

# Expected response includes:
# - "platform_status": "operational" (not "initializing")
# - "health_validation": {"status": "healthy"} (if validation completed)
# - "foundation_services": {...} (list of services)
# - "infrastructure_services": {...} (list of services)

# Detailed status
curl http://localhost:8000/platform/status | python3 -m json.tool

# Check foundation services
curl http://localhost:8000/foundation/services | python3 -m json.tool

# Check managers
curl http://localhost:8000/managers | python3 -m json.tool
```

---

### **Case 2: Content Pillar - File Upload & Processing**
- [ ] Upload a file through frontend
- [ ] File is processed successfully
- [ ] Metadata is extracted
- [ ] Content is stored in ArangoDB
- [ ] File is accessible via Supabase/GCS

**Verification:**
- Frontend: `http://localhost:3000/pillars/content` (or `http://35.215.64.103:3000/pillars/content` for production)
- Check backend logs: `docker logs --tail 100 -f symphainy-backend-prod | grep -i "content\|upload\|file"`
- Verify file appears in database (check ArangoDB or via API)
- Test API endpoint: `curl http://localhost:8000/api/v1/content-pillar/list-uploaded-files`

---

### **Case 3: Insights Pillar - Data Analysis**
- [ ] Insights are generated from uploaded content
- [ ] Charts/visualizations render correctly
- [ ] Data analysis completes successfully
- [ ] Results are stored and retrievable

**Verification:**
- Frontend: `http://localhost:3000/pillars/insights` (or `http://35.215.64.103:3000/pillars/insights` for production)
- Check for chart rendering (@nivo packages working)
- Verify analysis results in database
- Test API endpoint: `curl http://localhost:8000/api/v1/insights-pillar/analyze-content` (POST with content)
- Check backend logs: `docker logs --tail 100 -f symphainy-backend-prod | grep -i "insights\|analysis"`

---

### **Case 4: Operations Pillar - Process Optimization**
- [ ] Operations dashboard loads
- [ ] Process metrics are displayed
- [ ] Optimization recommendations appear
- [ ] Background tasks are monitored

**Verification:**
- Frontend: `http://localhost:3000/pillars/operation` (or `http://35.215.64.103:3000/pillars/operation` for production)
- Check operations API: `curl http://localhost:8000/api/v1/operations-pillar/health`
- Check backend logs: `docker logs --tail 100 -f symphainy-backend-prod | grep -i "operations\|workflow"`
- Verify process metrics are displayed
- Check Celery worker logs: `docker logs --tail 50 symphainy-celery-worker`

---

### **Case 5: Business Outcomes Pillar - Strategic Planning**
- [ ] Business outcomes dashboard loads
- [ ] Financial analysis displays correctly
- [ ] Strategic recommendations appear
- [ ] AI collaboration features work

**Verification:**
- Frontend: `http://localhost:3000/pillars/business-outcomes` (or `http://35.215.64.103:3000/pillars/business-outcomes` for production)
- Check for financial calculations
- Verify AI agent interactions
- Check backend logs: `docker logs --tail 100 -f symphainy-backend-prod | grep -i "business\|outcomes\|financial"`
- Test AI agent endpoints if available

---

### **Case 6: API Endpoints**
- [ ] `/health` endpoint returns correct status
- [ ] `/api/*` endpoints respond correctly
- [ ] Authentication works (if applicable)
- [ ] Rate limiting is active (if configured)

**Verification:**
```bash
# Health check
curl http://localhost:8000/health | python3 -m json.tool

# Platform status
curl http://localhost:8000/platform/status | python3 -m json.tool

# Foundation services
curl http://localhost:8000/foundation/services | python3 -m json.tool

# Managers list
curl http://localhost:8000/managers | python3 -m json.tool

# Test pillar API endpoints
curl http://localhost:8000/api/v1/content-pillar/health
curl http://localhost:8000/api/v1/insights-pillar/health
curl http://localhost:8000/api/v1/operations-pillar/health

# Check API documentation
open http://localhost:8000/docs

# Check rate limiting (make multiple rapid requests)
for i in {1..10}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/health; done
```

---

### **Case 7: Observability & Logging**
- [ ] Logs include trace_id for correlation
- [ ] Loki is aggregating logs
- [ ] Grafana dashboards show metrics
- [ ] Trace-to-log correlation works

**Verification:**
- Check backend logs for trace_id: `docker logs --tail 100 symphainy-backend-prod | grep trace_id`
- Grafana: `http://localhost:3100` (or `http://35.215.64.103:3100` for production)
  - Default login: admin/admin
  - Check for Loki datasource configured
  - Check for Tempo datasource configured
- Loki query: `curl "http://localhost:3101/loki/api/v1/query_range?query={service_name=\"backend\"}"`
- Check trace correlation in logs
- View logs in Grafana: Explore → Loki → Query: `{container_name="symphainy-backend-prod"}`

---

### **Case 8: Error Handling & Resilience**
- [ ] Graceful error handling
- [ ] Services recover from failures
- [ ] Health checks catch issues
- [ ] Background tasks handle errors

**Verification:**
- Check logs for error handling
- Verify services restart on failure
- Test with invalid inputs

---

## 📊 **Performance Checks**

### **Resource Usage**
- [ ] CPU usage within limits
- [ ] Memory usage within limits
- [ ] No resource exhaustion
- [ ] Services respond within acceptable time

**Verification:**
```bash
docker stats --no-stream
# Check CPU and memory usage
```

### **Response Times**
- [ ] Health endpoint: < 1 second
- [ ] API endpoints: < 2 seconds
- [ ] Frontend page load: < 3 seconds
- [ ] File upload: < 10 seconds (depends on size)

---

## 🐛 **Troubleshooting**

### **If Backend Won't Start**
1. Check logs: `docker logs symphainy-backend-prod` (or `docker logs --tail 200 symphainy-backend-prod`)
2. Verify infrastructure services are running: `cd symphainy-platform && docker-compose -f docker-compose.infrastructure.yml ps`
3. Check `.env.secrets` file exists in `symphainy-platform/` directory
4. Verify network connectivity: `docker network inspect symphainy-platform_smart_city_net`
5. Check if port 8000 is already in use: `lsof -i :8000` or `netstat -tuln | grep 8000`
6. Verify backend can reach infrastructure:
   - `docker exec symphainy-backend-prod ping -c 1 symphainy-arangodb`
   - `docker exec symphainy-backend-prod ping -c 1 symphainy-redis`
   - `docker exec symphainy-backend-prod ping -c 1 symphainy-consul`

### **If Frontend Won't Load**
1. Check logs: `docker logs symphainy-frontend-prod` (or `docker logs --tail 200 symphainy-frontend-prod`)
2. Verify backend is responding: `curl http://localhost:8000/health`
3. Check CORS configuration in backend
4. Verify port 3000 is accessible: `curl -I http://localhost:3000`
5. Check if port 3000 is already in use: `lsof -i :3000` or `netstat -tuln | grep 3000`
6. Verify frontend can reach backend: `docker exec symphainy-frontend-prod ping -c 1 backend`
7. Check environment variables: `docker exec symphainy-frontend-prod env | grep NEXT_PUBLIC`
8. Rebuild if needed: `docker-compose -f docker-compose.prod.yml up -d --build frontend`

### **If Services Are Unhealthy**
1. Check individual service logs:
   ```bash
   docker logs symphainy-backend-prod
   docker logs symphainy-frontend-prod
   docker logs symphainy-arangodb
   docker logs symphainy-redis
   docker logs symphainy-consul
   ```
2. Verify network connectivity: `docker network inspect symphainy-platform_smart_city_net`
3. Check resource limits: `docker stats --no-stream`
4. Verify configuration files exist and are correct
5. Check health endpoints directly:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8529/_api/version
   docker exec symphainy-redis redis-cli ping
   ```
6. Restart unhealthy service: `docker restart <container-name>`
7. Check for port conflicts: `lsof -i :8000 -i :3000 -i :8529 -i :6379`

---

## 📝 **Demo Notes Template**

```
Date: ___________
Tester: ___________

Case 1: [ ] Pass / [ ] Fail / [ ] Notes: ___________
Case 2: [ ] Pass / [ ] Fail / [ ] Notes: ___________
Case 3: [ ] Pass / [ ] Fail / [ ] Notes: ___________
Case 4: [ ] Pass / [ ] Fail / [ ] Notes: ___________
Case 5: [ ] Pass / [ ] Fail / [ ] Notes: ___________
Case 6: [ ] Pass / [ ] Fail / [ ] Notes: ___________
Case 7: [ ] Pass / [ ] Fail / [ ] Notes: ___________
Case 8: [ ] Pass / [ ] Fail / [ ] Notes: ___________

Issues Found:
1. ___________
2. ___________
3. ___________

Overall Status: [ ] Ready for CTO Demo / [ ] Issues to Fix
```

---

## 🎉 **Success Criteria**

The demo is successful if:
- ✅ All 8 demo cases pass
- ✅ No critical errors in logs
- ✅ Performance is acceptable
- ✅ All services remain healthy throughout
- ✅ Observability features work correctly

---

---

## 🔧 **Common Issues & Solutions**

### **Issue: Backend shows "initializing" instead of "operational"**
**Solution:**
- Wait longer (platform initialization can take 60-90 seconds)
- Check logs: `docker logs --tail 100 symphainy-backend-prod`
- Verify infrastructure services are healthy
- Check if foundation services completed: `curl http://localhost:8000/platform/status | python3 -m json.tool`

### **Issue: Frontend can't connect to backend**
**Solution:**
- Verify backend is running: `curl http://localhost:8000/health`
- Check frontend environment variable: `docker exec symphainy-frontend-prod env | grep NEXT_PUBLIC_API_URL`
- Should be: `NEXT_PUBLIC_API_URL=http://backend:8000` (internal) or `http://localhost:8000` (external)
- Check network: `docker network inspect symphainy-platform_smart_city_net`

### **Issue: Infrastructure services won't start**
**Solution:**
- Check if ports are already in use: `lsof -i :8529 -i :6379 -i :8500`
- Verify docker-compose file path: `cd symphainy-platform && docker-compose -f docker-compose.infrastructure.yml ps`
- Check logs for specific service: `docker logs <service-name>`
- Try restarting: `docker-compose -f docker-compose.infrastructure.yml restart <service-name>`

### **Issue: Health check fails**
**Solution:**
- Check if service is actually running: `docker ps | grep <service-name>`
- Verify health check endpoint: `curl http://localhost:<port>/health`
- Check service logs for errors
- Increase start_period in docker-compose if service needs more time

### **Issue: "Network not found" error**
**Solution:**
- Create network manually: `docker network create symphainy-platform_smart_city_net`
- Or start infrastructure first to create network: `cd symphainy-platform && docker-compose -f docker-compose.infrastructure.yml up -d`

---

## 📝 **Demo Execution Tips**

1. **Start Early**: Infrastructure services can take 30-60 seconds to fully initialize
2. **Monitor Logs**: Keep a terminal open with `docker logs -f symphainy-backend-prod` during demo
3. **Have Backup Plan**: Know how to quickly restart services if needed
4. **Test Endpoints First**: Verify health endpoints before demo starts
5. **Document Issues**: Note any issues in the Demo Notes Template section
6. **Check Resource Usage**: Monitor `docker stats` to ensure no resource exhaustion

---

**Good luck with the demo! 🚀**

