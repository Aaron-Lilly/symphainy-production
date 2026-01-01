# Log Aggregation Configuration

**Date:** December 2024  
**Status:** ✅ **IMPLEMENTED**

---

## ✅ **Implementation**

### **1. Docker Logging Driver Configuration**

**Approach:** JSON file logging driver with rotation (simplest, production-ready)

**Configuration Added:**
- All services in `docker-compose.prod.yml` and `docker-compose.infrastructure.yml`
- Log rotation: 10MB max size, 3 files retained
- Labels for service identification

**Benefits:**
- Logs accessible via `docker logs <container>`
- Logs stored in Docker's default location (`/var/lib/docker/containers/`)
- Automatic rotation prevents disk space issues
- Can be extended to external log aggregation services

---

## 🔄 **Future Enhancements**

### **Option 1: GCP Cloud Logging** (Recommended for GCE deployment)

**Configuration:**
```yaml
logging:
  driver: "gcplogs"
  options:
    gcp-project: "${GCS_PROJECT_ID}"
    gcp-log-cmd: "true"
    labels: "service,environment"
```

**Benefits:**
- Native GCP integration
- Centralized log management
- Built-in search and filtering
- No additional infrastructure needed

### **Option 2: Fluentd/Fluent Bit** (For multi-cloud)

**Configuration:**
```yaml
logging:
  driver: "fluentd"
  options:
    fluentd-address: "localhost:24224"
    tag: "docker.{{.Name}}"
```

**Benefits:**
- Flexible routing
- Multiple output destinations
- Works across cloud providers

### **Option 3: OpenTelemetry Collector** (Already in infrastructure)

**Configuration:**
- Use existing OTel Collector to forward logs
- Configure log exporter in `docker-compose.infrastructure.yml`
- Nurse can monitor log metrics via telemetry

**Benefits:**
- Uses existing infrastructure
- Unified observability (logs, metrics, traces)
- Platform-native integration

---

## 📊 **Nurse Integration**

**Status:** ⚠️ **RECOMMENDATION**

Nurse can monitor log aggregation health by:
1. Checking Docker log file sizes
2. Monitoring log rotation events
3. Collecting log volume metrics
4. Alerting on log aggregation failures

**Implementation:**
- Extend Nurse's `telemetry_health` module
- Add `monitor_log_aggregation()` method
- Collect metrics via existing `collect_telemetry()` method

---

## 📋 **Current Configuration**

**Services Configured:**
- ✅ Backend (`symphainy-backend-prod`)
- ✅ Frontend (`symphainy-frontend-prod`)
- ✅ ArangoDB (`symphainy-arangodb`)
- ✅ Redis (`symphainy-redis`)

**Log Location:**
- Docker default: `/var/lib/docker/containers/<container-id>/<container-id>-json.log`
- Accessible via: `docker logs <container-name>`

**Rotation:**
- Max size: 10MB per file
- Max files: 3 (30MB total per container)
- Automatic rotation on size limit

---

**Last Updated:** December 2024

