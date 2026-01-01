# Write-Ahead Logging (WAL) Module - Implementation Specification

**Date:** December 2024  
**Service:** Data Steward Service  
**Module:** Write-Ahead Logging  
**Pattern:** Netflix WAL-inspired governance capability

---

## 🎯 Overview

The Write-Ahead Logging (WAL) module is a **Data Steward governance capability** that logs all critical operations BEFORE execution, providing durability, audit trails, and replay capability for the platform.

### **Key Principles**

1. **Governance-First**: WAL is a governance capability, not an operational service
2. **Durability**: Every critical operation logged BEFORE execution
3. **Audit Trail**: Complete operation history for compliance
4. **Replay Capability**: Recover from failures by replaying logs
5. **Integration**: Seamlessly integrates with existing Data Steward capabilities

---

## 🏗️ Architecture

### **Module Location**

```
backend/smart_city/services/data_steward/
├── data_steward_service.py
└── modules/
    ├── policy_management.py
    ├── lineage_tracking.py
    ├── quality_compliance.py
    └── write_ahead_logging.py  ⭐ NEW
```

### **Integration with Data Steward**

```python
class DataStewardService(SmartCityRoleBase):
    def __init__(self, ...):
        # Existing modules
        self.policy_management_module = PolicyManagement(self)
        self.lineage_tracking_module = LineageTracking(self)
        self.quality_compliance_module = QualityCompliance(self)
        
        # NEW: Write-Ahead Logging module
        self.write_ahead_logging_module = WriteAheadLogging(self)
    
    # WAL SOA APIs (exposed via Data Steward)
    async def write_to_log(self, ...):
        """Write to WAL - governance capability."""
        return await self.write_ahead_logging_module.write_to_log(...)
    
    async def replay_log(self, ...):
        """Replay from WAL - governance capability."""
        return await self.write_ahead_logging_module.replay_log(...)
```

---

## 📋 API Specification

### **1. write_to_log()**

**Purpose:** Log operation BEFORE execution for durability and audit.

**Signature:**
```python
async def write_to_log(
    self,
    namespace: str,
    payload: Dict[str, Any],
    target: str,
    lifecycle: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | str | Yes | Logical group (e.g., "saga_execution", "canonical_model", "routing_engine") |
| `payload` | Dict[str, Any] | Yes | Operation data to log |
| `target` | str | Yes | Where to send after logging (Kafka topic, queue, service name) |
| `lifecycle` | Dict[str, Any] | No | Retry count, delay, TTL, backoff strategy |
| `user_context` | Dict[str, Any] | No | User context for multi-tenancy and security |

**Lifecycle Options:**
```python
lifecycle = {
    "retry_count": 3,           # Number of retries on failure
    "delay": 60,                 # Delay in seconds before retry
    "backoff": "exponential",    # "exponential" | "linear" | "fixed"
    "ttl": 86400,                # Time-to-live in seconds (default: 7 days)
    "priority": "normal"         # "high" | "normal" | "low"
}
```

**Returns:**
```python
{
    "success": True,
    "log_id": "wal_abc123...",
    "durable": True,              # Confirms durable storage
    "timestamp": "2024-12-01T10:00:00Z",
    "namespace": "saga_execution",
    "target": "saga_execution_queue"
}
```

**Error Response:**
```python
{
    "success": False,
    "error": "Error message",
    "error_code": "WAL_WRITE_ERROR"
}
```

### **2. replay_log()**

**Purpose:** Replay operations from WAL for recovery, debugging, or audit.

**Signature:**
```python
async def replay_log(
    self,
    namespace: str,
    from_timestamp: datetime,
    to_timestamp: datetime,
    filters: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `namespace` | str | Yes | Logical group to replay |
| `from_timestamp` | datetime | Yes | Start timestamp |
| `to_timestamp` | datetime | Yes | End timestamp |
| `filters` | Dict[str, Any] | No | Additional filters (operation, target, etc.) |
| `user_context` | Dict[str, Any] | No | User context for security |

**Filters:**
```python
filters = {
    "operation": "execute_saga",      # Filter by operation type
    "target": "saga_execution_queue", # Filter by target
    "status": "completed",            # Filter by status
    "correlation_id": "saga_123"     # Filter by correlation ID
}
```

**Returns:**
```python
[
    {
        "log_id": "wal_abc123...",
        "namespace": "saga_execution",
        "timestamp": "2024-12-01T10:00:00Z",
        "payload": {...},
        "target": "saga_execution_queue",
        "status": "completed",
        "correlation_id": "saga_123"
    },
    ...
]
```

---

## 🔧 Implementation Details

### **Storage Strategy**

WAL entries are stored using **Knowledge Governance Abstraction** (ArangoDB):

```python
# Storage structure
wal_entry = {
    "log_id": "wal_{namespace}_{timestamp}_{uuid}",
    "namespace": namespace,
    "timestamp": datetime.utcnow().isoformat(),
    "payload": payload,
    "target": target,
    "lifecycle": lifecycle,
    "status": "pending",  # pending | completed | failed | retrying
    "retry_count": 0,
    "correlation_id": correlation_id,  # For linking related operations
    "metadata": {
        "user_id": user_context.get("user_id"),
        "tenant_id": user_context.get("tenant_id"),
        "operation": payload.get("operation")
    }
}
```

### **Integration with Lineage Tracking**

WAL entries automatically feed into Data Steward's lineage tracking:

```python
async def write_to_log(self, ...):
    # 1. Write to WAL
    log_entry = await self._write_to_durable_storage(...)
    
    # 2. Automatically record lineage
    await self.service.lineage_tracking_module.record_lineage({
        "asset_id": log_entry["log_id"],
        "operation": payload.get("operation"),
        "source": namespace,
        "target": target,
        "timestamp": log_entry["timestamp"]
    })
    
    return log_entry
```

### **Retry and Delayed Queue Support**

WAL supports delayed retry via lifecycle configuration:

```python
# Example: Retry with exponential backoff
lifecycle = {
    "retry_count": 5,
    "delay": 60,  # Start with 60 seconds
    "backoff": "exponential"  # 60s, 120s, 240s, 480s, 960s
}

# WAL automatically:
# 1. Stores entry with retry configuration
# 2. Consumer processes entry
# 3. On failure, schedules retry with backoff
# 4. Updates retry_count and status
```

### **Cross-Region Replication**

WAL entries can be replicated across regions via Knowledge Governance Abstraction:

```python
# Configuration
wal_config = {
    "namespace": "saga_execution",
    "replication": {
        "enabled": True,
        "regions": ["us-east-1", "us-west-2", "eu-west-1"]
    }
}
```

---

## 🔄 Consumer Pattern

WAL entries are consumed by target services:

```python
# Consumer (e.g., Saga Journey Orchestrator)
async def consume_wal_entry(self, log_entry: Dict[str, Any]):
    """
    Consume WAL entry and execute operation.
    """
    try:
        # Execute operation
        result = await self._execute_operation(log_entry["payload"])
        
        # Update WAL entry status
        await self.data_steward.update_log_status(
            log_id=log_entry["log_id"],
            status="completed",
            result=result
        )
    except Exception as e:
        # Check retry configuration
        if log_entry["retry_count"] < log_entry["lifecycle"]["retry_count"]:
            # Schedule retry
            await self.data_steward.schedule_retry(log_entry["log_id"])
        else:
            # Mark as failed
            await self.data_steward.update_log_status(
                log_id=log_entry["log_id"],
                status="failed",
                error=str(e)
            )
```

---

## 📊 Usage Examples

### **Example 1: Saga Journey Execution**

```python
# Saga Journey writes to WAL before execution
await data_steward.write_to_log(
    namespace="saga_execution",
    payload={
        "saga_id": "saga_123",
        "operation": "execute_saga",
        "journey_id": "journey_456",
        "context": {...}
    },
    target="saga_execution_queue",
    lifecycle={
        "retry_count": 3,
        "delay": 60,
        "backoff": "exponential"
    },
    user_context=user_context
)
```

### **Example 2: Canonical Model Registration**

```python
# Canonical Model Service writes to WAL before registration
await data_steward.write_to_log(
    namespace="canonical_model",
    payload={
        "operation": "register_model",
        "model_name": "policy_v1",
        "version": "1.0.0",
        "schema": {...}
    },
    target="canonical_model_registry",
    lifecycle={"retry_count": 3},
    user_context=user_context
)
```

### **Example 3: Routing Decision**

```python
# Routing Engine writes to WAL before routing
await data_steward.write_to_log(
    namespace="routing_engine",
    payload={
        "operation": "evaluate_routing",
        "policy_id": "policy_123",
        "routing_decision": "NewPlatformAPI"
    },
    target="routing_evaluation_queue",
    lifecycle={"retry_count": 1},
    user_context=user_context
)
```

### **Example 4: Replay for Recovery**

```python
# Replay WAL entries after system crash
replayed_entries = await data_steward.replay_log(
    namespace="saga_execution",
    from_timestamp=datetime(2024, 12, 1, 10, 0, 0),
    to_timestamp=datetime(2024, 12, 1, 11, 0, 0),
    filters={
        "status": "pending"  # Only replay incomplete operations
    },
    user_context=user_context
)

# Re-execute operations
for entry in replayed_entries:
    await saga_orchestrator.execute_operation(entry["payload"])
```

---

## 🔒 Security & Compliance

### **Multi-Tenancy**

WAL entries are tenant-isolated:

```python
# Tenant validation
if user_context:
    tenant_id = user_context.get("tenant_id")
    if tenant_id:
        # WAL entry tagged with tenant_id
        wal_entry["metadata"]["tenant_id"] = tenant_id
        
        # Replay only returns entries for same tenant
        if replaying:
            if entry["metadata"]["tenant_id"] != tenant_id:
                continue  # Skip entry
```

### **Access Control**

WAL operations require governance permissions:

```python
# Security validation
if user_context:
    security = self.service.get_security()
    if security:
        if not await security.check_permissions(
            user_context, 
            "data_governance", 
            "write"  # For write_to_log
        ):
            raise PermissionError("Access denied")
```

### **Audit Trail**

All WAL operations are themselves logged:

```python
# WAL writes are logged for audit
audit_entry = {
    "operation": "wal_write",
    "log_id": log_entry["log_id"],
    "namespace": namespace,
    "user_id": user_context.get("user_id"),
    "timestamp": datetime.utcnow().isoformat()
}
await self.service.store_document(audit_entry, metadata={"type": "wal_audit"})
```

---

## 📈 Performance Considerations

### **Async Writes**

WAL writes are asynchronous to minimize latency:

```python
async def write_to_log(self, ...):
    # 1. Write to durable storage (async)
    log_entry = await self._write_to_durable_storage(...)
    
    # 2. Return immediately (don't wait for consumer)
    return {
        "success": True,
        "log_id": log_entry["log_id"],
        "durable": True
    }
    
    # 3. Consumer processes asynchronously
```

### **Batching**

WAL supports batch writes for high-throughput scenarios:

```python
async def write_to_log_batch(
    self,
    entries: List[Dict[str, Any]],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Write multiple entries in batch for performance.
    """
    # Batch write to durable storage
    log_entries = await self._write_batch_to_durable_storage(entries)
    return {"success": True, "log_ids": [e["log_id"] for e in log_entries]}
```

### **Indexing**

WAL entries are indexed for fast replay:

```python
# Indexes on ArangoDB
indexes = [
    {"fields": ["namespace", "timestamp"]},  # For namespace queries
    {"fields": ["correlation_id"]},          # For correlation queries
    {"fields": ["status", "timestamp"]},    # For status queries
    {"fields": ["metadata.tenant_id"]}        # For tenant isolation
]
```

---

## 🧪 Testing Strategy

### **Unit Tests**

```python
# Test WAL write
async def test_write_to_log():
    result = await wal_module.write_to_log(
        namespace="test",
        payload={"operation": "test"},
        target="test_queue"
    )
    assert result["success"] == True
    assert result["durable"] == True

# Test WAL replay
async def test_replay_log():
    entries = await wal_module.replay_log(
        namespace="test",
        from_timestamp=datetime.now() - timedelta(hours=1),
        to_timestamp=datetime.now()
    )
    assert len(entries) > 0
```

### **Integration Tests**

```python
# Test WAL with Saga Journey
async def test_saga_journey_wal_integration():
    # Write to WAL
    await data_steward.write_to_log(
        namespace="saga_execution",
        payload={"saga_id": "test_saga"},
        target="saga_execution_queue"
    )
    
    # Simulate crash
    # Replay from WAL
    entries = await data_steward.replay_log(
        namespace="saga_execution",
        from_timestamp=datetime.now() - timedelta(minutes=5),
        to_timestamp=datetime.now()
    )
    
    # Verify replay
    assert len(entries) > 0
    assert entries[0]["payload"]["saga_id"] == "test_saga"
```

---

## 📚 Related Documentation

- [Netflix WAL Case Study](../writeaheadlogging.md)
- [Data Steward Service](../symphainy-platform/backend/smart_city/services/data_steward/data_steward_service.py)
- [Knowledge Governance Abstraction](../symphainy-platform/foundations/public_works_foundation/abstraction_contracts/knowledge_governance_protocol.py)

---

**Last Updated:** December 2024  
**Status:** Ready for Implementation











