# Backward Compatibility Cleanup Required

## Services That Still Import from Old Interface Files

### 1. **Post Office Service**
**File**: `backend/smart_city/services/post_office/post_office_service.py`
**Line 41**: `from backend.smart_city.interfaces.post_office_interface import`

**What's imported:**
- `MessageStatus`, `EventType`, `MessagePriority`, `AgentStatus`
- `SendMessageRequest`, `SendMessageResponse`
- `RouteEventRequest`, `RouteEventResponse`
- `RegisterAgentRequest`, `RegisterAgentResponse`
- `GetMessagesRequest`, `GetMessagesResponse`
- `GetMessageStatusRequest`, `GetMessageStatusResponse`

**Action Required:**
- Move all data models to `post_office_protocol.py`
- Update service to import from protocol

### 2. **Security Guard Service**
**File**: `backend/smart_city/services/security_guard/security_guard_service.py`
**Line 36**: `from backend.smart_city.interfaces.security_guard_interface import`

**What's imported:**
- `AuthenticateUserRequest`, `AuthenticateUserResponse`
- `AuthorizeActionRequest`, `AuthorizeActionResponse`
- `CreateSessionRequest`, `CreateSessionResponse`
- `ValidateSessionRequest`, `ValidateSessionResponse`

**Action Required:**
- Move all data models to `security_guard_protocol.py`
- Update service to import from protocol

### 3. **Conductor Service**
**File**: `backend/smart_city/services/conductor/conductor_service.py`
**Line 37**: `from backend.smart_city.interfaces.conductor_interface import`

**What's imported:**
- `CreateWorkflowRequest`, `CreateWorkflowResponse`
- `ExecuteWorkflowRequest`, `ExecuteWorkflowResponse`
- `GetWorkflowStatusRequest`, `GetWorkflowStatusResponse`
- `UpdateWorkflowRequest`, `UpdateWorkflowResponse`
- `WorkflowStatus`, `WorkflowPriority`, `TaskStatus`

**Action Required:**
- Move all data models to `conductor_protocol.py`
- Update service to import from protocol

### 4. **Traffic Cop Service**
**File**: `backend/smart_city/services/traffic_cop/traffic_cop_service.py`
**Line 37**: `from backend.smart_city.interfaces.traffic_cop_interface import`

**What's imported:**
- `SessionRequest`, `SessionResponse`
- `RoutingRequest`, `RoutingResponse`
- `StateRequest`, `StateResponse`
- `SyncRequest`, `SyncResponse`
- `AnalyticsRequest`, `AnalyticsResponse`
- `HealthCheckRequest`, `HealthCheckResponse`

**Action Required:**
- Move all data models to `traffic_cop_protocol.py`
- Update service to import from protocol

## Services That Still Use Old Base Classes

### 5. **Librarian Service**
**File**: `backend/smart_city/services/librarian/librarian_service.py`
**Line 44**: `class LibrarianService(RealmServiceBase, ILibrarian)`

**Action Required:**
- Refactor to use `SmartCityRoleBase`
- Remove `ILibrarian` interface inheritance
- Import data models from `librarian_protocol.py`

## Pattern to Follow (From Nurse Service Refactoring)

✅ **Nurse Service** - Already refactored correctly
- Imports all data models from `nurse_protocol.py`
- Uses `SmartCityRoleBase`
- No interface inheritance
- No backward compatibility imports

### Example from Nurse Service:

```python
# In nurse_protocol.py
@dataclass
class CollectTelemetryRequest:
    service_name: str
    metric_name: str
    metric_value: float
    ...

# In nurse_service.py
from bases.protocols.nurse_protocol import (
    CollectTelemetryRequest, CollectTelemetryResponse,
    ...
)
```

## Action Plan

1. **Move data models from interface files to protocol files** (for Post Office, Security Guard, Conductor, Traffic Cop)
2. **Update imports in service files** to use protocol imports
3. **Refactor Librarian Service** to use SmartCityRoleBase (already has protocol created)
4. **Verify no old interface imports remain**

## Priority

1. **Traffic Cop** - Refactored but still imports from interface
2. **Conductor** - Refactored but still imports from interface
3. **Security Guard** - New version but still imports from interface
4. **Post Office** - Refactored but still imports from interface
5. **Librarian** - Needs full refactoring (has protocol, needs service refactor)

