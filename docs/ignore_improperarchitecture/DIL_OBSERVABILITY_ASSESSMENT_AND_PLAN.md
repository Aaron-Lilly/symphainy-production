# Observability Assessment & Base Capability Plan

**Date:** January 2025  
**Status:** 🔍 **ASSESSMENT COMPLETE** → 📋 **PLAN READY**  
**Approach:** Secure by design, open by policy - base capability now, advanced features later

---

## Executive Summary

This document assesses current observability capabilities and creates a plan for base observability capability that enables reasonable platform observability while following "secure by design, open by policy" pattern.

**Key Finding:** Observability infrastructure exists but needs streamlining and DIL SDK integration for unified platform data storage.

---

## 1. Current State Assessment

### 1.1 Infrastructure Components

**✅ What Exists:**
- **OpenTelemetry Collector** - Already in `docker-compose.infrastructure.yml`
- **Tempo** - Distributed tracing backend (already configured)
- **Grafana** - Visualization (already in infrastructure)
- **Telemetry Abstractions** - OpenTelemetry-based telemetry collection
- **Nurse Service** - Health monitoring and telemetry collection

**⚠️ What's Partially Working:**
- **Log Aggregation** - Docker JSON logging exists, but no centralized aggregation
- **Metrics Storage** - OpenTelemetry metrics collected, but storage unclear
- **Trace Correlation** - Traces exist, but correlation with logs/metrics unclear

**❌ What's Missing:**
- **Unified Observability Interface** - No single SDK for all observability operations
- **Platform Data Storage** - Observability data not stored in DIL (platform data)
- **Correlation** - Logs, traces, metrics not properly correlated
- **DIL SDK Integration** - Observability not integrated with DIL SDK

### 1.2 Nurse Service Capabilities

**✅ What Works:**
- `collect_telemetry()` - Collects telemetry via OpenTelemetry
- `get_health_metrics()` - Gets health metrics via Health Abstraction
- `start_trace()` / `add_span()` / `end_trace()` - Distributed tracing via Tempo
- `get_trace()` - Retrieves trace data from Tempo
- `set_alert_threshold()` - Sets alert thresholds via Redis
- `run_diagnostics()` - Runs system diagnostics

**⚠️ What's Partially Working:**
- **Telemetry Collection** - Works but not stored in DIL
- **Health Metrics** - Collected but not unified
- **Tracing** - Works but correlation unclear

**❌ What's Missing:**
- **Platform Data Storage** - Observability data not in DIL
- **Unified Interface** - No DIL SDK observability module
- **Agent Execution Tracking** - Not integrated with DIL
- **Semantic Metrics** - Not tracked

### 1.3 Observability Patterns Across Platform

**Current Pattern (Fragmented):**
```python
# Services use different patterns
await nurse.collect_telemetry(...)  # Some services
await telemetry_utility.record_metric(...)  # Other services
await log_operation_with_telemetry(...)  # Base classes
await record_health_metric(...)  # Base classes
```

**Issues:**
- ❌ Multiple observability patterns
- ❌ No unified interface
- ❌ Observability data not stored in DIL
- ❌ No correlation between logs, traces, metrics

---

## 2. Assessment Results

### What's Working ✅

1. **OpenTelemetry Infrastructure**
   - ✅ OpenTelemetry Collector exists
   - ✅ Tempo for tracing exists
   - ✅ Telemetry abstractions work

2. **Nurse Service**
   - ✅ Telemetry collection works
   - ✅ Health metrics collection works
   - ✅ Distributed tracing works

3. **Base Classes**
   - ✅ `log_operation_with_telemetry()` works
   - ✅ `record_health_metric()` works

### What's Broken ❌

1. **Unified Interface**
   - ❌ No single SDK for observability
   - ❌ Multiple patterns across services
   - ❌ No DIL SDK integration

2. **Platform Data Storage**
   - ❌ Observability data not stored in DIL
   - ❌ No platform data classification
   - ❌ No unified observability data model

3. **Correlation**
   - ❌ Logs, traces, metrics not correlated
   - ❌ No trace ID propagation
   - ❌ No unified request ID

4. **Agent Execution Tracking**
   - ❌ Agent execution not tracked in DIL
   - ❌ No agent execution logs
   - ❌ No agent tool registry

### What Needs Streamlining ⚠️

1. **Duplicate Code**
   - ⚠️ Multiple telemetry utilities
   - ⚠️ Multiple health metric patterns
   - ⚠️ Multiple logging patterns

2. **Infrastructure Complexity**
   - ⚠️ OpenTelemetry + Tempo + Grafana (complex)
   - ⚠️ No unified configuration
   - ⚠️ No centralized observability management

---

## 3. Base Capability Plan

### 3.1 Secure by Design: Build Frameworks Now

**What We Build:**
1. **DIL SDK Observability Module** - Unified interface for all observability
2. **Platform Data Storage** - Store observability data in DIL
3. **Correlation Framework** - Trace ID propagation, request ID correlation
4. **Agent Execution Tracking** - Track agent execution in DIL
5. **Unified Observability Interface** - Single SDK for all observability

**What We Defer (Open by Policy):**
1. **Advanced Analytics** - Predictive monitoring, anomaly detection
2. **Automated Remediation** - Auto-fix based on observability
3. **Multi-Tenant Observability** - Tenant-specific observability dashboards
4. **Long-Term Retention** - Extended observability data retention
5. **Real-Time Alerting** - Advanced alerting rules

### 3.2 DIL SDK Observability Module

**API:**
```python
from dil import observability

# Platform Event Recording
await dil.observability.record_platform_event(
    event_type: str,  # "error", "operation", "metric", "agent_execution"
    event_data: Dict[str, Any],
    trace_id: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

# Agent Execution Tracking
await dil.observability.record_agent_execution(
    agent_id: str,
    prompt_hash: str,
    response: Optional[str],
    trace_id: str,
    execution_metadata: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

# Semantic Metrics
await dil.observability.record_semantic_metric(
    metric_name: str,
    value: float,
    tags: Dict[str, Any],
    trace_id: Optional[str] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

# Trace Correlation
await dil.observability.get_trace(
    trace_id: str,
    include_logs: bool = True,
    include_metrics: bool = True,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

# Metrics Aggregation
await dil.observability.get_metrics(
    metric_names: List[str],
    time_range: Dict[str, Any],
    filters: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

# Platform Data Queries
await dil.observability.query_platform_data(
    filters: Dict[str, Any],
    time_range: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

### 3.3 Platform Data Storage

**Storage Strategy:**
- **ArangoDB Collections:**
  - `platform_events` - Platform events (errors, operations, metrics)
  - `agent_execution_logs` - Agent execution logs
  - `semantic_metrics` - Semantic metrics
  - `observability_traces` - Trace correlation data

- **Classification:**
  - All observability data classified as `"platform"` data
  - `tenant_id` optional (for attribution)
  - `data_classification` = `"platform"`

- **Indexes:**
  - `platform_events`: Index on `event_type`, `trace_id`, `timestamp`
  - `agent_execution_logs`: Index on `agent_id`, `trace_id`, `timestamp`
  - `semantic_metrics`: Index on `metric_name`, `trace_id`, `timestamp`
  - `observability_traces`: Index on `trace_id`, `timestamp`

### 3.4 Correlation Framework

**Trace ID Propagation:**
```python
# All operations include trace_id
trace_id = user_context.get("trace_id") or str(uuid.uuid4())

# Propagate trace_id through all operations
await dil.observability.record_platform_event(
    event_type="operation",
    event_data={...},
    trace_id=trace_id,
    user_context=user_context
)

# Correlation via trace_id
trace_data = await dil.observability.get_trace(
    trace_id=trace_id,
    include_logs=True,
    include_metrics=True
)
```

**Request ID Correlation:**
```python
# Generate request ID at entry point
request_id = str(uuid.uuid4())

# Include in user_context
user_context = {
    "request_id": request_id,
    "trace_id": trace_id,
    ...
}

# All operations use request_id for correlation
```

### 3.5 Agent Execution Tracking

**Integration:**
```python
# In AgentBase or agent initialization
async def execute_agent(self, prompt, tools, user_context):
    # Get trace_id
    trace_id = user_context.get("trace_id") or str(uuid.uuid4())
    
    # Track execution via DIL SDK
    await dil.observability.record_agent_execution(
        agent_id=self.agent_name,
        prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
        response=None,  # Will be updated after execution
        trace_id=trace_id,
        execution_metadata={
            "tools": [tool.name for tool in tools],
            "started_at": datetime.utcnow().isoformat()
        },
        user_context=user_context
    )
    
    # Execute agent
    response = await self._execute(prompt, tools, user_context)
    
    # Update execution log
    await dil.observability.record_agent_execution(
        agent_id=self.agent_name,
        prompt_hash=hashlib.sha256(prompt.encode()).hexdigest(),
        response=response,
        trace_id=trace_id,
        execution_metadata={
            "tools": [tool.name for tool in tools],
            "completed_at": datetime.utcnow().isoformat(),
            "success": True
        },
        user_context=user_context
    )
    
    return response
```

---

## 4. Implementation Plan

### Phase 0: Foundation (Week 1-2)

**Goal:** Establish DIL SDK observability module and platform data storage

**Deliverables:**
1. **DIL SDK Observability Module**
   - `dil.observability.record_platform_event()`
   - `dil.observability.record_agent_execution()`
   - `dil.observability.record_semantic_metric()`
   - `dil.observability.get_trace()`
   - `dil.observability.get_metrics()`
   - `dil.observability.query_platform_data()`

2. **Platform Data Storage**
   - ArangoDB collections: `platform_events`, `agent_execution_logs`, `semantic_metrics`, `observability_traces`
   - Indexes on all collections
   - Data classification as `"platform"`

3. **Correlation Framework**
   - Trace ID propagation
   - Request ID correlation
   - Unified correlation interface

**Acceptance Criteria:**
- [ ] DIL SDK observability module operational
- [ ] Platform data storage working
- [ ] Trace ID propagation working
- [ ] Request ID correlation working

### Phase 1: Integration (Week 3-4)

**Goal:** Integrate DIL SDK observability with Nurse and base classes

**Deliverables:**
1. **Nurse Integration**
   - Nurse uses DIL SDK for observability storage
   - Nurse exposes DIL SDK observability via SOA APIs
   - Nurse queries platform data via DIL SDK

2. **Base Class Integration**
   - `log_operation_with_telemetry()` uses DIL SDK
   - `record_health_metric()` uses DIL SDK
   - All base classes use DIL SDK for observability

3. **Agent Execution Tracking**
   - AgentBase tracks execution via DIL SDK
   - All agents track execution
   - Agent execution logs stored in DIL

**Acceptance Criteria:**
- [ ] Nurse uses DIL SDK for observability
- [ ] Base classes use DIL SDK for observability
- [ ] Agent execution tracking working
- [ ] All observability data stored in DIL

### Phase 2: Streamlining (Week 5-6)

**Goal:** Streamline existing observability capabilities

**Deliverables:**
1. **Consolidate Duplicate Code**
   - Remove duplicate telemetry utilities
   - Unify health metric patterns
   - Unify logging patterns

2. **Unified Configuration**
   - Single observability configuration
   - Unified OpenTelemetry configuration
   - Centralized observability management

3. **Correlation Enhancement**
   - Log-to-trace correlation
   - Metric-to-trace correlation
   - Request-to-trace correlation

**Acceptance Criteria:**
- [ ] Duplicate code removed
- [ ] Unified configuration working
- [ ] Correlation enhanced
- [ ] Observability streamlined

---

## 5. Success Criteria

### Base Capability Complete When:

1. ✅ **DIL SDK Observability Module**
   - All API methods implemented
   - Platform data storage working
   - Trace ID propagation working

2. ✅ **Nurse Integration**
   - Nurse uses DIL SDK for observability
   - Nurse exposes DIL SDK via SOA APIs
   - Nurse queries platform data

3. ✅ **Base Class Integration**
   - All base classes use DIL SDK
   - Observability unified across platform

4. ✅ **Agent Execution Tracking**
   - All agents track execution
   - Agent execution logs in DIL

5. ✅ **Streamlining**
   - Duplicate code removed
   - Unified configuration
   - Correlation working

6. ✅ **Platform Observability**
   - Can observe platform health
   - Can correlate logs, traces, metrics
   - Can query platform data
   - Can track agent execution

---

## 6. Deferred Capabilities (Open by Policy)

**These are built but not enforced until use case demands:**

1. **Advanced Analytics**
   - Predictive monitoring
   - Anomaly detection
   - Trend analysis

2. **Automated Remediation**
   - Auto-fix based on observability
   - Self-healing capabilities

3. **Multi-Tenant Observability**
   - Tenant-specific dashboards
   - Tenant isolation for observability

4. **Long-Term Retention**
   - Extended data retention
   - Historical analysis

5. **Real-Time Alerting**
   - Advanced alerting rules
   - Alert routing

---

## 7. Next Steps

1. **Review and approve this plan**
2. **Start Phase 0: Foundation**
3. **Implement DIL SDK observability module**
4. **Set up platform data storage**
5. **Integrate with Nurse and base classes**
6. **Streamline existing capabilities**

---

## Conclusion

**Assessment:** Observability infrastructure exists but needs streamlining and DIL SDK integration.

**Plan:** Build base capability (secure by design) with DIL SDK integration, defer advanced features (open by policy).

**Outcome:** Unified observability interface, platform data storage, correlation framework, agent execution tracking - enabling reasonable platform observability.


