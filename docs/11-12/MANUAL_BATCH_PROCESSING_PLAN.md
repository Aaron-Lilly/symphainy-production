# Manual Batch Processing Plan for Remaining Abstractions

## Current Status
- **Completed**: 15/52 abstractions (28.8%)
- **Remaining**: 37 abstractions (71.2%)
- **Pattern**: Well-established and validated on 2 test files

## Approach
Manual batch processing in groups of 3-5 files, following the established pattern.

## Established Pattern

### 1. Constructor Update
```python
def __init__(self, ..., di_container=None):
    """
    ...
    Args:
        ...
        di_container: Dependency injection container
    """
    # ... existing assignments ...
    self.di_container = di_container
    self.service_name = "<name>_abstraction"
    
    # Get logger from DI Container if available
    if di_container and hasattr(di_container, 'get_logger'):
        self.logger = di_container.get_logger(self.service_name)
    else:
        self.logger = logging.getLogger(__name__)
    
    self.logger.info("✅ <Class> initialized")
```

### 2. Exception Handler Update
```python
except Exception as e:
    # Use error handler with telemetry
    error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
    telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
    if error_handler:
        await error_handler.handle_error(e, {
            "operation": "<method_name>",
            "service": self.service_name
        }, telemetry=telemetry)
    else:
        self.logger.error(f"❌ Operation failed: {e}")
    # Preserve existing raise/return
```

### 3. Telemetry (Success Paths)
```python
# Before return statement
# Record platform operation event
telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
if telemetry:
    await telemetry.record_platform_operation_event("<operation_name>", {
        "relevant_context": value,
        "success": True
    })

return result
```

## Batch Processing Strategy

### Batch 6 (Next): Communication & Messaging
1. `authorization_abstraction.py` - 7 methods
2. `messaging_abstraction.py` - TBD
3. `event_management_abstraction.py` - TBD
4. `session_management_abstraction.py` - TBD

### Batch 7: Processing Abstractions
1. `html_processing_abstraction.py`
2. `word_processing_abstraction.py`
3. `bpmn_processing_abstraction.py`
4. `sop_processing_abstraction.py`

### Batch 8: Analysis & Metrics
1. `financial_analysis_abstraction.py`
2. `business_metrics_abstraction.py`
3. `coexistence_analysis_abstraction.py`
4. `coexistence_blueprint_abstraction.py`

### Remaining Batches
- Continue in logical groups of 3-5 files
- Test after each batch
- Update foundation service to pass di_container

## Estimated Time
- Per file: ~5-10 minutes (constructor + exception handlers + telemetry)
- Per batch (4 files): ~20-40 minutes
- Total remaining: ~3-4 hours

## Quality Checks
After each batch:
1. Import test
2. Constructor signature check
3. Quick syntax validation












