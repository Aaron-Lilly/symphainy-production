# OpenTelemetry Collector + Loki Implementation Plan

**Date:** December 2024  
**Status:** 📋 **PLAN - NO IMPLEMENTATION YET**  
**Architecture:** 5-Layer Public Works Foundation Pattern

---

## 🎯 **Executive Summary**

This plan implements OTel Collector + Loki log aggregation following the platform's 5-layer architecture pattern:
- **Layer 0:** Loki Adapter (raw technology client)
- **Layer 1:** Log Aggregation Abstraction (business logic)
- **Layer 2-4:** Registration in Public Works Foundation
- **Nurse Integration:** SOA APIs and MCP Tools exposure
- **Smart City MCP:** Tool registration for agent access

---

## 📐 **Architecture Overview**

### **5-Layer Pattern:**

```
Layer 0: LokiAdapter (Raw Technology)
    ↓
Layer 1: LogAggregationAbstraction (Business Logic)
    ↓
Layer 2: Composition Services (Orchestration)
    ↓
Layer 3: Infrastructure Registries (Discovery)
    ↓
Layer 4: Public Works Foundation Service (Exposure)
    ↓
Platform Gateway → Realms → Nurse (SOA APIs) → Smart City MCP (MCP Tools)
```

### **Data Flow:**

```
Docker Containers → OTel Collector → Loki (via LokiAdapter)
                                      ↓
                            LogAggregationAbstraction
                                      ↓
                            Nurse Service (SOA APIs)
                                      ↓
                            Smart City MCP Server (MCP Tools)
```

---

## 📋 **Implementation Plan**

### **Phase 1: Infrastructure Setup**

#### **1.1 Add Loki to Docker Compose**

**File:** `symphainy-platform/docker-compose.infrastructure.yml`

**Changes:**
```yaml
  # Loki - Log Aggregation Backend
  loki:
    image: grafana/loki:latest
    container_name: symphainy-loki
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki
      - ./loki-config.yaml:/etc/loki/local-config.yaml:ro
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - smart_city_net
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "-O", "/dev/null", "http://localhost:3100/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped

volumes:
  # ... existing volumes ...
  loki_data:
```

**Dependencies:**
- None (Loki is standalone)

---

#### **1.2 Create Loki Configuration**

**File:** `symphainy-platform/loki-config.yaml` (new file)

**Content:**
```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

# By default, Loki will send anonymous, but uniquely-identifiable usage and configuration
# analytics to Grafana Labs. These statistics are sent to https://stats.grafana.org/
#
# Statistics help us better understand how Loki is used, and they show us performance
# levels for most users. This helps us prioritize features and documentation.
# For more information on what's sent, look at
# https://github.com/grafana/loki/blob/main/pkg/analytics/stats.go
# Refer to the buildReport method to see what goes into a report.
#
# If you would like to disable reporting, uncomment the following lines:
analytics:
  reporting_enabled: false
```

---

#### **1.3 Update OTel Collector Configuration**

**File:** `symphainy-platform/otel-collector-config.yaml`

**Current State:**
- Has `traces` pipeline (exports to Tempo)
- Has `metrics` pipeline (exports to Prometheus)
- **Missing:** `logs` pipeline

**Changes Needed:**
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318
  # Add filelog receiver for Docker logs
  filelog:
    include:
      - /var/lib/docker/containers/*/*-json.log
    exclude:
      - /var/lib/docker/containers/*/*-json.log.gz
    start_at: end
    include_file_path: true
    include_file_path_resolved: true
    operators:
      - type: json_parser
        id: parser-docker
        output: extract_metadata_from_filepath
        timestamp:
          parse_from: attributes.time
          layout: '%Y-%m-%dT%H:%M:%S.%fZ'
      - type: regex_parser
        id: extract_metadata_from_filepath
        regex: '^.*containers/(?P<container_id>[^/]+)/.*\.log$'
        parse_from: attributes["log.file.path"]
      - type: add
        id: add_service_name
        field: attributes["service.name"]
        value: "{{ .container_id }}"
      - type: move
        id: move_container_id
        from: attributes.container_id
        to: resource["container.id"]

processors:
  batch:
    timeout: 1s
    send_batch_size: 1024
  memory_limiter:
    limit_mib: 512
    check_interval: 1s
  # Add resource processor for log enrichment
  resource:
    attributes:
      - key: service.name
        from_attribute: container.name
        action: insert
      - key: service.namespace
        value: "symphainy-platform"
        action: insert

exporters:
  otlp:
    endpoint: tempo:4317
    tls:
      insecure: true
  debug:
    verbosity: detailed
  prometheus:
    endpoint: "0.0.0.0:8890"
  # Add Loki exporter
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
    labels:
      resource:
        service.name: "service_name"
        service.namespace: "service_namespace"
      attributes:
        container.id: "container_id"
        log.level: "severity"
    tenant_id: "symphainy-platform"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp, debug]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus, debug]
    # Add logs pipeline
    logs:
      receivers: [filelog, otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [loki, debug]
```

**Note:** Filelog receiver requires access to Docker log files. May need volume mount or different approach.

**Alternative:** Use OTLP log receiver instead of filelog (simpler, but requires application changes).

---

### **Phase 2: Layer 0 - Loki Adapter**

#### **2.1 Create Loki Adapter**

**File:** `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/loki_adapter.py` (new file)

**Pattern:** Follow `arangodb_adapter.py` and `redis_adapter.py` patterns

**Key Methods:**
```python
class LokiAdapter:
    """Raw Loki client wrapper - no business logic."""
    
    def __init__(self, endpoint: str, tenant_id: str = None):
        """Initialize Loki adapter."""
        self.endpoint = endpoint
        self.tenant_id = tenant_id
        self._client = None  # Will use httpx for HTTP client
    
    async def connect(self) -> bool:
        """Connect to Loki (test connection)."""
        # Test connection with /ready endpoint
    
    async def push_logs(self, logs: List[Dict[str, Any]]) -> bool:
        """Push logs to Loki via /loki/api/v1/push."""
        # HTTP POST to Loki push endpoint
    
    async def query_logs(self, query: str, limit: int = 100, start: int = None, end: int = None) -> Dict[str, Any]:
        """Query logs from Loki via /loki/api/v1/query_range."""
        # HTTP GET to Loki query endpoint
    
    async def test_connection(self) -> bool:
        """Test Loki connection."""
        # GET /ready endpoint
```

**Dependencies:**

**Important Distinction:**
- **Loki SERVICE** → Added to `docker-compose.infrastructure.yml` (infrastructure service, like ArangoDB, Redis, Tempo)
- **Python CLIENT** → Uses `httpx` (already in `pyproject.toml`) - **NO NEW DEPENDENCIES NEEDED**

**Pattern Consistency:**
- ArangoDB service → `python-arango` client (in pyproject.toml)
- Redis service → `redis` client (in pyproject.toml)
- Loki service → `httpx` client (already in pyproject.toml)

**Why `httpx` instead of a dedicated Loki client?**
- Loki has a simple REST API (HTTP endpoints: `/loki/api/v1/push`, `/loki/api/v1/query_range`)
- `httpx` is already in dependencies and sufficient for HTTP requests
- No need for a dedicated client library (unlike ArangoDB which has complex protocol)
- Keeps dependencies minimal and follows REST API pattern

**Alternative (if needed later):**
- Could add `promtail` or `grafana-loki-client` to `pyproject.toml` if more features needed
- But `httpx` is recommended for simplicity

---

### **Phase 3: Layer 1 - Log Aggregation Abstraction**

#### **3.1 Create Log Aggregation Protocol**

**File:** `symphainy-platform/foundations/public_works_foundation/abstraction_contracts/log_aggregation_protocol.py` (new file)

**Pattern:** Follow `telemetry_protocol.py` pattern

**Key Methods:**
```python
class LogAggregationProtocol(Protocol):
    """Protocol for log aggregation operations."""
    
    async def push_logs(self, logs: List[LogEntry]) -> bool:
        """Push logs to aggregation backend."""
        ...
    
    async def query_logs(self, query: LogQuery) -> List[LogEntry]:
        """Query logs from aggregation backend."""
        ...
    
    async def search_logs(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Search logs with filters."""
        ...
    
    async def get_log_metrics(self, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """Get log volume and aggregation metrics."""
        ...
```

---

#### **3.2 Create Log Aggregation Abstraction**

**File:** `symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/log_aggregation_abstraction.py` (new file)

**Pattern:** Follow `telemetry_abstraction.py` pattern

**Key Features:**
- Accepts `LokiAdapter` via dependency injection
- Implements `LogAggregationProtocol`
- Infrastructure-level error handling and retries
- Log enrichment (add trace IDs, request IDs, etc.)

**Key Methods:**
```python
class LogAggregationAbstraction:
    """Log aggregation abstraction with infrastructure coordination."""
    
    def __init__(self, loki_adapter: LogAggregationProtocol, ...):
        """Initialize with injected adapter."""
        self.adapter = loki_adapter
    
    async def push_logs(self, logs: List[LogEntry]) -> bool:
        """Push logs with retry logic."""
    
    async def query_logs(self, query: LogQuery) -> List[LogEntry]:
        """Query logs with error handling."""
    
    async def enrich_log_with_trace(self, log_entry: LogEntry, trace_id: str) -> LogEntry:
        """Enrich log with trace ID for correlation."""
```

---

### **Phase 4: Layer 2-4 - Public Works Foundation Integration**

#### **4.1 Create Loki Adapter in Public Works Foundation**

**File:** `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py`

**Location:** In `_create_all_adapters()` method (around line 1546)

**Changes:**
```python
# Log Aggregation Adapters
from .infrastructure_adapters.loki_adapter import LokiAdapter

# Loki Adapter (connects to Loki)
loki_config = self.config_adapter.get("LOKI_ENDPOINT", "http://localhost:3100")
loki_tenant = self.config_adapter.get("LOKI_TENANT_ID", "symphainy-platform")

self.loki_adapter = LokiAdapter(
    endpoint=loki_config,
    tenant_id=loki_tenant
)
self.logger.info("✅ Loki adapter created")

# Test connection
try:
    loki_connected = await self.loki_adapter.connect()
    if loki_connected:
        self.logger.info(f"✅ Loki connected successfully ({loki_config})")
    else:
        self.logger.warning(f"⚠️ Loki connection test returned False ({loki_config})")
except Exception as e:
    self.logger.warning(f"⚠️ Loki connection test failed (non-critical): {e}")
    # Don't raise - log aggregation is optional
```

---

#### **4.2 Create Log Aggregation Abstraction in Public Works Foundation**

**File:** `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py`

**Location:** In `_create_all_abstractions()` method (around line 1800)

**Changes:**
```python
# Log Aggregation Abstraction
from .infrastructure_abstractions.log_aggregation_abstraction import LogAggregationAbstraction

self.log_aggregation_abstraction = LogAggregationAbstraction(
    loki_adapter=self.loki_adapter,
    config_adapter=self.config_adapter,
    di_container=self.di_container
)
self.logger.info("✅ Log Aggregation abstraction created")
```

---

#### **4.3 Register Log Aggregation Abstraction**

**File:** `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py`

**Location:** In `_initialize_and_register_abstractions()` method (around line 1900)

**Changes:**
```python
# Register log aggregation abstraction
self.abstraction_map["log_aggregation"] = self.log_aggregation_abstraction
self.logger.info("✅ Log Aggregation abstraction registered")
```

**Also update `get_abstraction()` method:**
```python
def get_abstraction(self, name: str) -> Any:
    """Get infrastructure abstraction by name."""
    abstraction_map = {
        # ... existing abstractions ...
        "log_aggregation": self.log_aggregation_abstraction,
    }
    return abstraction_map.get(name)
```

---

### **Phase 5: Configuration**

#### **5.1 Add Loki Configuration to Config Files**

**File:** `symphainy-platform/config/production.env`

**Changes:**
```ini
# ===================================================================
# LOKI CONFIGURATION
# ===================================================================
# Docker Deployment: Use container name for service discovery
LOKI_ENDPOINT=http://symphainy-loki:3100
LOKI_TENANT_ID=symphainy-platform
```

**File:** `symphainy-platform/config/production.env.example`

**Changes:**
```ini
# ===================================================================
# LOKI CONFIGURATION
# ===================================================================
LOKI_ENDPOINT=${LOKI_ENDPOINT:-http://symphainy-loki:3100}
LOKI_TENANT_ID=${LOKI_TENANT_ID:-symphainy-platform}
```

---

#### **5.2 Update Unified Configuration Manager**

**File:** `symphainy-platform/utilities/configuration/unified_configuration_manager.py`

**Changes:**
```python
def get_loki_config(self) -> Dict[str, Any]:
    """Get Loki configuration."""
    return {
        "endpoint": self.get_string("LOKI_ENDPOINT", "http://localhost:3100"),
        "tenant_id": self.get_string("LOKI_TENANT_ID", "symphainy-platform")
    }
```

---

### **Phase 6: Nurse Service Integration**

#### **6.1 Add Log Aggregation Methods to Nurse**

**File:** `symphainy-platform/backend/smart_city/services/nurse/modules/telemetry_health.py`

**Changes:**
```python
async def monitor_log_aggregation(self) -> Dict[str, Any]:
    """
    Monitor log aggregation health and metrics.
    
    Collects metrics for:
    - Log volume
    - Log aggregation status
    - Query performance
    """
    try:
        if not self.service.is_infrastructure_connected:
            raise Exception("Infrastructure not connected")
        
        # Get log aggregation abstraction
        platform_gateway = self.service.di_container.service_registry.get("PlatformInfrastructureGateway")
        if not platform_gateway:
            raise Exception("Platform Gateway not available")
        
        log_abstraction = platform_gateway.get_abstraction("log_aggregation")
        if not log_abstraction:
            return {
                "status": "error",
                "error": "Log aggregation abstraction not available"
            }
        
        # Get log metrics
        metrics = await log_abstraction.get_log_metrics({
            "start": datetime.utcnow() - timedelta(hours=1),
            "end": datetime.utcnow()
        })
        
        # Collect telemetry
        await self.collect_telemetry(
            "log_aggregation",
            "log_volume",
            metrics.get("volume", 0),
            {"status": "healthy" if metrics.get("status") == "success" else "degraded"}
        )
        
        return {
            "status": "success",
            "metrics": metrics,
            "monitored_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        await self.service.handle_error_with_audit(e, "monitor_log_aggregation")
        return {
            "status": "error",
            "error": str(e)
        }
```

---

#### **6.2 Add SOA APIs to Nurse**

**File:** `symphainy-platform/backend/smart_city/services/nurse/modules/soa_mcp.py`

**Location:** In `initialize_soa_api_exposure()` method (around line 20)

**Changes:**
```python
self.service.soa_apis = {
    # ... existing SOA APIs ...
    "monitor_log_aggregation": {
        "endpoint": "/api/nurse/logs/aggregation",
        "method": "GET",
        "description": "Monitor log aggregation health and metrics",
        "parameters": []
    },
    "query_logs": {
        "endpoint": "/api/nurse/logs/query",
        "method": "POST",
        "description": "Query logs from aggregation backend",
        "parameters": ["query", "limit", "start", "end"]
    },
    "search_logs": {
        "endpoint": "/api/nurse/logs/search",
        "method": "POST",
        "description": "Search logs with filters",
        "parameters": ["filters", "time_range"]
    },
    "get_log_metrics": {
        "endpoint": "/api/nurse/logs/metrics",
        "method": "GET",
        "description": "Get log volume and aggregation metrics",
        "parameters": ["time_range"]
    }
}
```

---

#### **6.3 Add MCP Tools to Nurse**

**File:** `symphainy-platform/backend/smart_city/services/nurse/modules/soa_mcp.py`

**Location:** In `initialize_mcp_tool_integration()` method (around line 70)

**Changes:**
```python
self.service.mcp_tools = {
    # ... existing MCP tools ...
    "monitor_log_aggregation": {
        "name": "nurse_monitor_log_aggregation",
        "description": "Monitor log aggregation health and collect metrics",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "query_logs": {
        "name": "nurse_query_logs",
        "description": "Query logs from aggregation backend using Loki query language",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "LogQL query string"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of log entries to return",
                    "default": 100
                },
                "start": {
                    "type": "string",
                    "description": "Start time (ISO 8601 or Unix timestamp)"
                },
                "end": {
                    "type": "string",
                    "description": "End time (ISO 8601 or Unix timestamp)"
                }
            },
            "required": ["query"]
        }
    },
    "search_logs": {
        "name": "nurse_search_logs",
        "description": "Search logs with filters (service, level, time range)",
        "input_schema": {
            "type": "object",
            "properties": {
                "filters": {
                    "type": "object",
                    "description": "Search filters (service_name, level, etc.)"
                },
                "time_range": {
                    "type": "object",
                    "description": "Time range for search"
                }
            },
            "required": ["filters"]
        }
    },
    "get_log_metrics": {
        "name": "nurse_get_log_metrics",
        "description": "Get log volume and aggregation metrics",
        "input_schema": {
            "type": "object",
            "properties": {
                "time_range": {
                    "type": "object",
                    "description": "Time range for metrics (hours, days, etc.)"
                }
            },
            "required": []
        }
    }
}
```

---

#### **6.4 Implement SOA API Handlers in Nurse**

**File:** `symphainy-platform/backend/smart_city/services/nurse/nurse_service.py`

**Location:** Add new methods or extend existing handler methods

**Changes:**
```python
async def handle_monitor_log_aggregation(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle monitor_log_aggregation SOA API request."""
    return await self.telemetry_health_module.monitor_log_aggregation()

async def handle_query_logs(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle query_logs SOA API request."""
    platform_gateway = self.di_container.service_registry.get("PlatformInfrastructureGateway")
    log_abstraction = platform_gateway.get_abstraction("log_aggregation")
    
    query = request.get("query")
    limit = request.get("limit", 100)
    start = request.get("start")
    end = request.get("end")
    
    return await log_abstraction.query_logs({
        "query": query,
        "limit": limit,
        "start": start,
        "end": end
    })

# Similar handlers for search_logs and get_log_metrics
```

---

#### **6.5 Implement MCP Tool Handlers in Nurse**

**File:** `symphainy-platform/backend/smart_city/services/nurse/modules/soa_mcp.py`

**Location:** Add tool handler methods

**Changes:**
```python
async def handle_nurse_monitor_log_aggregation(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle nurse_monitor_log_aggregation MCP tool."""
    return await self.service.telemetry_health_module.monitor_log_aggregation()

async def handle_nurse_query_logs(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle nurse_query_logs MCP tool."""
    # Get log abstraction and query
    # Return results
    pass

# Similar handlers for other tools
```

**Note:** Tool handlers need to be registered with the MCP tool registry. Check how other Nurse tools are registered.

---

### **Phase 7: Smart City MCP Server Integration**

#### **7.1 Register Nurse Log Tools in Smart City MCP**

**File:** `symphainy-platform/backend/smart_city/mcp_server/smart_city_mcp_server.py`

**Status:** ✅ **AUTOMATIC**

**How it works:**
- Smart City MCP Server automatically discovers tools from Nurse's `mcp_tools` dict
- Tools are registered with prefix `nurse_` (e.g., `nurse_monitor_log_aggregation`)
- No manual registration needed if Nurse's `mcp_tools` is properly populated

**Verification:**
- Check that Nurse's `mcp_tools` dict includes log aggregation tools
- Verify Smart City MCP Server picks them up in `_register_service_tools()`

---

### **Phase 8: Grafana Integration**

#### **8.1 Add Loki Datasource to Grafana**

**File:** `symphainy-platform/docker-compose.infrastructure.yml`

**Location:** Grafana service configuration (around line 230)

**Changes:**
```yaml
  grafana:
    # ... existing config ...
    environment:
      # ... existing env vars ...
      - GF_DATASOURCES_PROVISIONING_ENABLED=true
    volumes:
      # ... existing volumes ...
      - ./grafana-datasources.yaml:/etc/grafana/provisioning/datasources/datasources.yaml:ro
```

---

#### **8.2 Create Grafana Datasources Configuration**

**File:** `symphainy-platform/grafana-datasources.yaml` (new file)

**Content:**
```yaml
apiVersion: 1

datasources:
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    isDefault: false
    jsonData:
      maxLines: 1000
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: "trace_id=(\\w+)"
          name: TraceID
          url: '$${__value.raw}'
  
  - name: Tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
    isDefault: false
    jsonData:
      tracesToLogs:
        datasourceUid: Loki
        tags: ['job', 'instance', 'pod', 'namespace']
        mappedTags: [{ key: 'service.name', value: 'service' }]
        mapTagNamesEnabled: false
        spanStartTimeShift: '1h'
        spanEndTimeShift: '1h'
        filterByTraceID: false
        filterBySpanID: false
```

**Benefits:**
- Automatic datasource provisioning
- Log-to-trace correlation
- Unified Grafana dashboard

---

### **Phase 9: Update Background Tasks**

#### **9.1 Add Log Aggregation Monitoring to Nurse Background Task**

**File:** `symphainy-platform/main.py`

**Location:** In `_run_nurse_background_task()` method (around line 514)

**Changes:**
```python
# Log aggregation monitoring (every 5 minutes)
if nurse and hasattr(nurse, 'telemetry_health_module'):
    if current_time - last_log_check >= 300:  # 5 minutes
        try:
            log_result = await nurse.telemetry_health_module.monitor_log_aggregation()
            if log_result.get("status") == "success":
                self.logger.debug("✅ Log aggregation monitoring completed")
            else:
                self.logger.warning(f"⚠️ Log aggregation monitoring issue: {log_result.get('error')}")
        except Exception as log_error:
            self.logger.error(f"❌ Log aggregation monitoring failed: {log_error}", exc_info=True)
        last_log_check = current_time
```

---

## 📊 **File Summary**

### **New Files:**
1. `symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/loki_adapter.py`
2. `symphainy-platform/foundations/public_works_foundation/abstraction_contracts/log_aggregation_protocol.py`
3. `symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/log_aggregation_abstraction.py`
4. `symphainy-platform/loki-config.yaml`
5. `symphainy-platform/grafana-datasources.yaml`

### **Modified Files:**
1. `symphainy-platform/docker-compose.infrastructure.yml` - Add Loki service
2. `symphainy-platform/otel-collector-config.yaml` - Add logs pipeline
3. `symphainy-platform/foundations/public_works_foundation/public_works_foundation_service.py` - Create adapter/abstraction, register
4. `symphainy-platform/utilities/configuration/unified_configuration_manager.py` - Add `get_loki_config()`
5. `symphainy-platform/config/production.env` - Add Loki config
6. `symphainy-platform/config/production.env.example` - Add Loki config
7. `symphainy-platform/backend/smart_city/services/nurse/modules/telemetry_health.py` - Add `monitor_log_aggregation()`
8. `symphainy-platform/backend/smart_city/services/nurse/modules/soa_mcp.py` - Add SOA APIs and MCP tools
9. `symphainy-platform/backend/smart_city/services/nurse/nurse_service.py` - Add SOA API handlers
10. `symphainy-platform/main.py` - Add log aggregation monitoring to background task

### **No Changes Needed:**
- `symphainy-platform/backend/smart_city/mcp_server/smart_city_mcp_server.py` - Auto-discovers tools from Nurse
- `symphainy-platform/pyproject.toml` - **No new Python dependencies needed** (uses existing `httpx`)

**Note:** Loki is a **service** (like ArangoDB, Redis, Tempo), not a Python package. We interact with it via HTTP using `httpx` (already in dependencies), similar to how we use `python-arango` for ArangoDB or `redis` for Redis. The service runs in Docker, the client library is in Python.

---

## 🔄 **Implementation Order**

### **Recommended Sequence:**

1. **Phase 1** - Infrastructure Setup (Loki service, config)
2. **Phase 2** - Layer 0 (Loki Adapter)
3. **Phase 3** - Layer 1 (Log Aggregation Abstraction)
4. **Phase 4** - Layer 2-4 (Public Works Foundation integration)
5. **Phase 5** - Configuration
6. **Phase 6** - Nurse Integration (SOA APIs, MCP Tools)
7. **Phase 7** - Smart City MCP (automatic, verify)
8. **Phase 8** - Grafana Integration
9. **Phase 9** - Background Tasks

---

## ✅ **Verification Checklist**

### **Infrastructure:**
- [ ] Loki container starts successfully
- [ ] Loki health check passes
- [ ] OTel Collector logs pipeline configured
- [ ] OTel Collector can export to Loki

### **Layer 0 (Adapter):**
- [ ] LokiAdapter can connect to Loki
- [ ] LokiAdapter can push logs
- [ ] LokiAdapter can query logs

### **Layer 1 (Abstraction):**
- [ ] LogAggregationAbstraction initialized
- [ ] Abstraction can push logs via adapter
- [ ] Abstraction can query logs via adapter
- [ ] Error handling works

### **Layer 2-4 (Foundation):**
- [ ] LokiAdapter created in Public Works Foundation
- [ ] LogAggregationAbstraction created in Public Works Foundation
- [ ] Abstraction registered in abstraction_map
- [ ] Abstraction accessible via Platform Gateway

### **Nurse Integration:**
- [ ] SOA APIs exposed (`/api/nurse/logs/*`)
- [ ] MCP Tools registered in Nurse
- [ ] SOA API handlers implemented
- [ ] MCP Tool handlers implemented

### **Smart City MCP:**
- [ ] Tools auto-discovered from Nurse
- [ ] Tools registered with `nurse_` prefix
- [ ] Tools callable via MCP

### **Grafana:**
- [ ] Loki datasource configured
- [ ] Log-to-trace correlation works
- [ ] Can query logs in Grafana

### **Background Tasks:**
- [ ] Log aggregation monitoring runs every 5 minutes
- [ ] Metrics collected via telemetry
- [ ] Errors logged properly

---

## 🎯 **Success Criteria**

1. ✅ Loki running and healthy
2. ✅ OTel Collector exporting logs to Loki
3. ✅ LogAggregationAbstraction accessible via Platform Gateway
4. ✅ Nurse SOA APIs functional (`/api/nurse/logs/*`)
5. ✅ Nurse MCP Tools callable (`nurse_query_logs`, etc.)
6. ✅ Smart City MCP Server exposes tools
7. ✅ Grafana can query logs
8. ✅ Log-to-trace correlation works
9. ✅ Background monitoring collects metrics

---

## 📝 **Notes**

### **OTel Collector Log Receiver Options:**

**Option A: Filelog Receiver** (Current plan)
- Pros: Works with existing Docker logging
- Cons: Requires volume mount, file path access

**Option B: OTLP Log Receiver** (Alternative)
- Pros: Simpler, no file access needed
- Cons: Requires application changes to send logs via OTLP

**Recommendation:** Start with OTLP receiver (simpler), add filelog later if needed.

### **Loki Query Language (LogQL):**
- Nurses and agents will need LogQL knowledge
- Consider adding helper methods for common queries
- Document LogQL patterns in Nurse service

### **Performance Considerations:**
- Loki is efficient but may need tuning for high volume
- Consider log sampling for high-traffic services
- Monitor Loki memory usage

---

**Ready to implement?** This plan follows your 5-layer architecture pattern and integrates with existing Nurse and MCP infrastructure.

