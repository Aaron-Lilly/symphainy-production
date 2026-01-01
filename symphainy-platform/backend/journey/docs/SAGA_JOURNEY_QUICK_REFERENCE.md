# 🎭 Saga Journey Orchestrator - Quick Reference

**Quick reference guide for Saga Journey Orchestrator usage.**

---

## 🚀 Quick Start

### 1. Design Saga Journey

```python
saga_journey = await saga_orchestrator.design_saga_journey(
    journey_type="enterprise_migration",
    requirements={
        "source": "legacy_system",
        "target": "new_system"
    },
    compensation_handlers={
        "upload_content": "delete_uploaded_content",
        "analyze_content": "revert_analysis",
        "transform_data": "revert_transformation"
    },
    user_context=user_context
)
```

### 2. Execute Saga Journey

```python
execution = await saga_orchestrator.execute_saga_journey(
    journey_id=saga_journey["journey_id"],
    user_id="user_123",
    context={"migration_id": "mig_001"},
    user_context=user_context
)

saga_id = execution["saga_id"]
```

### 3. Advance Saga Steps

```python
result = await saga_orchestrator.advance_saga_step(
    saga_id=saga_id,
    journey_id=saga_journey["journey_id"],
    user_id="user_123",
    step_result={"status": "complete", "files_uploaded": 150},
    user_context=user_context
)
```

### 4. Check Saga Status

```python
status = await saga_orchestrator.get_saga_status(saga_id, user_context)
# Returns: status, completed_milestones, compensated_milestones, etc.
```

---

## 📋 When to Use

| Use Case | Use Saga? |
|----------|-----------|
| Multi-service workflows requiring atomicity | ✅ **YES** |
| Financial transactions | ✅ **YES** |
| Enterprise migrations with rollback | ✅ **YES** |
| Simple single-service operations | ❌ **NO** (use Structured) |
| Free-form navigation | ❌ **NO** (use Session/MVP) |
| No compensation needed | ❌ **NO** (use Structured) |

---

## 🎯 Key Concepts

### Compensation Handlers

Domain-specific operations that undo milestone work:

```python
compensation_handlers = {
    "milestone_id": "compensation_handler_name"
}
```

**Requirements:**
- ✅ Idempotent (safe to retry)
- ✅ Domain-specific (understand "undo" semantics)
- ✅ Reliable (must eventually succeed)

### Saga States

- **IN_PROGRESS**: Saga executing, milestones completing
- **COMPENSATING**: Milestone failed, compensation in progress
- **COMPLETED**: All milestones completed successfully
- **FAILED**: Compensation completed (or compensation failed)

### Reverse-Order Compensation

When milestone fails, compensate previous milestones in reverse order:

```
Milestone 1 ✅ → Milestone 2 ✅ → Milestone 3 ❌
  ↓ Compensation Order:
  1. Compensate Milestone 2
  2. Compensate Milestone 1
```

---

## 🔧 Common Patterns

### Enterprise Migration

```python
compensation_handlers = {
    "upload_content": "delete_uploaded_content",
    "analyze_content": "revert_analysis",
    "transform_data": "revert_transformation",
    "validate_results": "revert_validation"
}
```

### Order Processing

```python
compensation_handlers = {
    "create_order": "cancel_order",
    "process_payment": "refund_payment",
    "reserve_inventory": "release_inventory",
    "ship_product": "cancel_shipment"
}
```

### Financial Transaction

```python
compensation_handlers = {
    "debit_account": "credit_account",
    "reserve_funds": "release_funds",
    "transfer_funds": "reverse_transfer"
}
```

---

## ⚠️ Important Notes

1. **Compensation handlers must be idempotent** - Safe to retry
2. **Use only when atomicity is required** - Adds overhead
3. **Test compensation scenarios** - Ensure handlers work correctly
4. **Monitor Saga state** - Track compensation progress

---

## 📚 Full Documentation

See [Saga Journey Orchestrator Complete Guide](./SAGA_JOURNEY_ORCHESTRATOR.md) for:
- Detailed architecture
- Implementation details
- Advanced usage examples
- Troubleshooting guide

---

**Last Updated:** December 2024



