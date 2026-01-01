# Trace ID Injection Implementation

**Date:** December 2024  
**Status:** ✅ **IMPLEMENTED**

---

## 🎯 **Objective**

Automatically inject `trace_id` from OpenTelemetry context into all log records, enabling log-to-trace correlation without modifying individual log calls.

---

## ✅ **Solution: Custom Formatter**

Created a centralized solution using a custom logging formatter that:
1. **Automatically extracts** `trace_id` from OpenTelemetry context
2. **Injects** it into every log record
3. **Works transparently** - no changes needed to existing log calls

---

## 📁 **Files Created/Modified**

### **New File:**
- `utilities/logging/trace_context_formatter.py`
  - Custom `TraceContextFormatter` class
  - Extracts trace_id from OpenTelemetry context
  - Adds trace_id to log records automatically

### **Modified File:**
- `utilities/logging/logging_service.py`
  - Updated `_setup_handlers()` to use `TraceContextFormatter`
  - Added `_get_trace_id()` helper method
  - Updated all log methods (`info`, `warning`, `error`, `debug`, `critical`) to include trace_id in `extra` dict

---

## 🔧 **How It Works**

### **1. Formatter Level (Automatic)**
```python
# TraceContextFormatter automatically:
# - Extracts trace_id from OpenTelemetry context
# - Adds it to log record as record.trace_id
# - Includes it in formatted output: [trace_id=...]
```

### **2. Log Method Level (Automatic)**
```python
# All log methods (info, warning, error, etc.) now:
# - Extract trace_id if not already in kwargs
# - Add it to extra dict for structured logging
# - Pass it through to logger
```

### **3. Log Aggregation (Already Supported)**
```python
# LogAggregationAbstraction already supports trace_id:
# - Checks log_entry.trace_id
# - Adds it as label: {"trace_id": "..."}
# - Enables log-to-trace correlation in Grafana
```

---

## 📊 **Result**

### **Before:**
```python
logger.info("Processing request")
# Output: 2024-12-01 12:00:00 - ServiceName - INFO - Processing request
```

### **After:**
```python
logger.info("Processing request")
# Output: 2024-12-01 12:00:00 - ServiceName - INFO - [trace_id=abc123...] - Processing request
# Also in extra dict: {"trace_id": "abc123..."}
```

---

## 🔗 **Integration Points**

### **1. OpenTelemetry Context**
- Uses `opentelemetry.trace.get_current_span()`
- Extracts `span_context.trace_id`
- Converts to hex string (32 characters)

### **2. Log Aggregation**
- `LogAggregationAbstraction` already supports `trace_id`
- Automatically adds as Loki label
- Enables Grafana log-to-trace correlation

### **3. Grafana Correlation**
- Grafana datasource configured with derived fields
- Log queries can link to traces via `trace_id`
- Automatic correlation in Explore view

---

## ✅ **Benefits**

1. **Zero Code Changes:** No need to modify existing log calls
2. **Automatic:** Works for all loggers created via DI Container
3. **Transparent:** Fails gracefully if OpenTelemetry not available
4. **Consistent:** All logs include trace_id when available
5. **Correlation Ready:** Works with existing Grafana configuration

---

## 🧪 **Testing**

### **Manual Test:**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# Setup OpenTelemetry
tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Create logger
from utilities.logging.logging_service import SmartCityLoggingService
logger = SmartCityLoggingService("test_service")

# Log within a trace
with trace.get_tracer("test").start_as_current_span("test_operation"):
    logger.info("This log should have trace_id")
    # Check output for [trace_id=...]
```

---

## 📝 **Notes**

- **Graceful Degradation:** If OpenTelemetry not installed, returns `None` (no trace_id)
- **Performance:** Minimal overhead - only extracts trace_id when logging
- **Compatibility:** Works with all existing log calls
- **Future Enhancement:** Could add span_id, parent_span_id for more detailed correlation

---

**Status:** ✅ **READY FOR USE**

