# Nurse Interface Analysis

## What the Interface File Contains

### 1. **Enums** (Value Types)
- `HealthStatus`: HEALTHY, WARNING, CRITICAL, UNKNOWN
- `AlertSeverity`: LOW, MEDIUM, HIGH, CRITICAL  
- `MetricType`: COUNTER, GAUGE, HISTOGRAM, SUMMARY

### 2. **Request Models** (Pydantic BaseModel)
- `CollectTelemetryRequest` - Fields for collecting telemetry data
- `GetHealthMetricsRequest` - Fields for getting health metrics
- `SetAlertThresholdRequest` - Fields for setting alert thresholds
- `RunDiagnosticsRequest` - Fields for running diagnostics
- `GetSystemStatusRequest` - Fields for getting system status

### 3. **Response Models** (Pydantic BaseModel)
- `CollectTelemetryResponse` - Response for telemetry collection
- `GetHealthMetricsResponse` - Response for health metrics
- `SetAlertThresholdResponse` - Response for alert threshold setting
- `RunDiagnosticsResponse` - Response for diagnostics
- `GetSystemStatusResponse` - Response for system status

### 4. **Interface Contract** (ABC)
- `INurse` - Abstract methods defining the contract

## How Should We Handle This in Our New Architecture?

### **Option 1: Inline in Service File** (Current Approach)
**Pros:**
- Self-contained service
- No external dependencies
- Easy to understand

**Cons:**
- Dataclasses defined in service file (not reusable)
- If multiple services need same models, duplication

### **Option 2: Protocol File** (Better Approach)
**Pros:**
- Models defined alongside protocol
- Reusable across services
- Clear contract definition
- Aligns with our new architecture

**Cons:**
- Protocol file gets longer
- Need to import from protocol

### **Option 3: Separate Data Models File** (Best for Complex Cases)
**Pros:**
- Clean separation of concerns
- Models are reusable
- Easy to import where needed
- Can use Pydantic for validation

**Cons:**
- Additional file to manage
- Need to coordinate imports

## Recommendation: Option 2 (Protocol File)

For our new architecture:
1. **Data models should live in the protocol file** - They're part of the contract
2. **Use dataclasses** - Simpler than Pydantic for our use case
3. **Don't use inheritance** - Services implement methods directly
4. **Protocol defines the contract** - Both methods and data models

### Structure:
```
bases/protocols/nurse_protocol.py:
  - Enums (HealthStatus, MetricType, etc.)
  - Request dataclasses
  - Response dataclasses
  - NurseProtocol (methods that should be implemented)
  
backend/smart_city/services/nurse/nurse_service.py:
  - NurseService(SmartCityRoleBase)
  - Implements all protocol methods
  - No inheritance of interface
```

This approach:
- ✅ Uses protocols (no ABC inheritance)
- ✅ Defines contract in protocol file
- ✅ Keeps data models with the protocol
- ✅ Services just implement methods
- ✅ Pythonic and clean

## Current Issue

We need to:
1. Move the data models (request/response classes) to `nurse_protocol.py`
2. Import them in the service file
3. Remove inline definitions from service file

This aligns with our new architecture where protocols define both the method signatures AND the data models.

