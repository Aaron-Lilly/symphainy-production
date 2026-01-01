# Loki Integration Testing Guide

**Date:** December 2024  
**Status:** ✅ **READY FOR TESTING**

---

## 🧪 **Quick Test Checklist**

### **1. Infrastructure Verification**

```bash
# Start Loki service
cd /home/founders/demoversion/symphainy_source/symphainy-platform
docker-compose -f docker-compose.infrastructure.yml up -d loki

# Wait a few seconds, then check health
curl http://localhost:3101/ready
# Expected: "ready"

# Check logs
docker logs symphainy-loki
# Should show: "Loki started successfully"
```

### **2. OTel Collector Verification**

```bash
# Start OTel Collector
docker-compose -f docker-compose.infrastructure.yml up -d otel-collector

# Check logs
docker logs symphainy-otel-collector
# Should show: "Everything is ready. Begin running and processing data."

# Verify logs pipeline is configured
docker exec symphainy-otel-collector cat /etc/otel-collector-config.yaml | grep -A 5 "logs:"
# Should show logs pipeline with loki exporter
```

### **3. Platform Integration Test**

```bash
# Start platform (from project root)
cd /home/founders/demoversion/symphainy_source
python3 symphainy-platform/main.py

# Watch for initialization messages:
# ✅ Loki adapter created
# ✅ Log Aggregation abstraction created
# ✅ Log Aggregation abstraction registered

# Check for background monitoring (after 5 minutes):
# ✅ Log aggregation monitoring completed
```

### **4. Nurse Service Test**

```python
# In Python REPL or script
from backend.smart_city.services.nurse.nurse_service import NurseService

# Get Nurse service from DI container (after platform startup)
nurse = di_container.get_service("NurseService")

# Test monitor_log_aggregation
result = await nurse.monitor_log_aggregation()
print(result)
# Expected: {"status": "success", "metrics": {...}, ...}

# Test query_logs
result = await nurse.query_logs(
    query='{service_name="backend"}',
    limit=10
)
print(result)
# Expected: {"status": "success", "count": N, "logs": [...]}
```

### **5. Grafana Verification**

```bash
# Start Grafana
docker-compose -f docker-compose.infrastructure.yml up -d grafana

# Access Grafana
# URL: http://localhost:3100
# Login: admin / admin

# Check datasources:
# 1. Go to Configuration > Data Sources
# 2. Verify "Loki" datasource exists
# 3. Click "Test" - should show "Data source is working"

# Query logs:
# 1. Go to Explore
# 2. Select "Loki" datasource
# 3. Enter query: {service_name="backend"}
# 4. Click "Run query"
# 5. Should see log entries (if any exist)
```

### **6. MCP Tool Test**

```python
# Test via Smart City MCP Server
# Tools should be auto-registered:
# - nurse_monitor_log_aggregation
# - nurse_query_logs
# - nurse_search_logs
# - nurse_get_log_metrics

# Call via MCP:
result = await mcp_server.call_tool(
    "nurse_monitor_log_aggregation",
    {}
)
```

---

## 🔍 **Troubleshooting**

### **Issue: Loki not accessible**
```bash
# Check if Loki is running
docker ps | grep loki

# Check Loki logs
docker logs symphainy-loki

# Check network
docker network inspect symphainy-platform_smart_city_net | grep loki
```

### **Issue: OTel Collector not exporting logs**
```bash
# Check OTel Collector logs
docker logs symphainy-otel-collector

# Verify config
docker exec symphainy-otel-collector cat /etc/otel-collector-config.yaml

# Check if Loki exporter is configured
docker exec symphainy-otel-collector cat /etc/otel-collector-config.yaml | grep -A 10 "loki:"
```

### **Issue: Log Aggregation abstraction not found**
```bash
# Check Public Works Foundation logs for:
# ✅ Loki adapter created
# ✅ Log Aggregation abstraction created

# Verify abstraction is registered:
python3 -c "
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
# After initialization:
abstraction = foundation.get_abstraction('log_aggregation')
print('Abstraction:', abstraction)
"
```

### **Issue: Nurse methods not found**
```bash
# Verify methods exist:
python3 -c "
from backend.smart_city.services.nurse.nurse_service import NurseService
import inspect
methods = [m for m in dir(NurseService) if 'log' in m.lower()]
print('Log methods:', methods)
"
# Should show: monitor_log_aggregation, query_logs, search_logs, get_log_metrics
```

---

## 📊 **Expected Results**

### **Successful Integration:**
- ✅ Loki service running and healthy
- ✅ OTel Collector exporting logs to Loki
- ✅ Log Aggregation abstraction accessible
- ✅ Nurse can monitor log aggregation
- ✅ Grafana can query logs
- ✅ Background monitoring collects metrics
- ✅ MCP tools callable

### **Sample Log Query Results:**
```json
{
  "status": "success",
  "query": "{service_name=\"backend\"}",
  "count": 42,
  "logs": [
    {
      "line": "Application started",
      "timestamp": "2024-12-01T12:00:00Z",
      "level": "info",
      "service_name": "backend",
      "labels": {
        "service_name": "backend",
        "level": "info"
      }
    }
  ]
}
```

---

## 🎯 **Next Steps After Testing**

1. **Verify all tests pass**
2. **Check Grafana dashboards** (create custom dashboards if needed)
3. **Monitor log volume** (ensure Loki has enough storage)
4. **Test log-to-trace correlation** (click trace ID in logs)
5. **Production deployment** (if all tests pass)

---

**Ready to test!** 🚀

