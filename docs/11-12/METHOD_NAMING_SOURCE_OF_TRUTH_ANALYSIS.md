# Method Naming Source of Truth Analysis - Issue 4

**Date**: November 13, 2025  
**Purpose**: Determine the actual source of truth for method naming given that Semantic APIs were built first and protocols were added later

---

## Architecture Layers & Method Naming

### Layer 1: Semantic APIs (User-Facing)
**Built First** - These are the user-facing endpoints

**Content Pillar Semantic API**:
- `GET /api/content-pillar/get-file-details/{file_id}` → `get_file_details()`
- `GET /api/content-pillar/list-uploaded-files` → `list_uploaded_files()`
- `POST /api/content-pillar/upload-file` → `upload_file()`
- `POST /api/content-pillar/process-file/{file_id}` → `process_file()`

**Pattern**: Uses descriptive, user-focused names (`get_file_details`, not `get_file`)

### Layer 2: Orchestrators (Business Logic)
**Content Analysis Orchestrator**:
- `get_file_details(file_id, user_id)` ✅ Matches Semantic API
- `list_uploaded_files(user_id)` ✅ Matches Semantic API
- `upload_file(...)` ✅ Matches Semantic API
- `process_file(...)` ✅ Matches Semantic API

**Pattern**: Orchestrator methods match Semantic API method names

### Layer 3: Smart City Services (SOA APIs)
**Content Steward Service**:
- `retrieve_file(file_id)` ⚠️ **LEGACY NAME** - doesn't match Semantic API
- Internally calls: `file_management_abstraction.get_file(file_id)` ✅ Uses protocol

**Pattern**: Service has legacy `retrieve_file()` but internally uses protocol's `get_file()`

### Layer 4: Infrastructure Abstractions (Protocols)
**File Management Protocol**:
- `get_file(file_uuid)` ✅ Protocol standard
- `create_file(file_data)` ✅ Protocol standard
- `update_file(file_uuid, updates)` ✅ Protocol standard
- `delete_file(file_uuid)` ✅ Protocol standard

**Pattern**: Protocol uses concise, infrastructure-focused names

### Layer 5: Infrastructure Adapters (Implementation)
**Supabase File Management Adapter**:
- `get_file(file_uuid)` ✅ Matches protocol
- `create_file(file_data)` ✅ Matches protocol

**Pattern**: Adapters match protocol method names

---

## Current Flow Analysis

### Example: Getting File Details

```
User Request
  ↓
Semantic API: GET /api/content-pillar/get-file-details/{file_id}
  ↓
Content Analysis Orchestrator: get_file_details(file_id, user_id)
  ↓
Content Steward Service: retrieve_file(file_id) ⚠️ INCONSISTENCY
  ↓
File Management Abstraction: get_file(file_uuid) ✅ Protocol
  ↓
Supabase Adapter: get_file(file_uuid) ✅ Protocol
```

**Issue**: Content Steward's `retrieve_file()` is inconsistent with:
1. Semantic API pattern (`get_file_details`)
2. Protocol pattern (`get_file`)

---

## Source of Truth Determination

### Option A: Semantic APIs are Source of Truth (User-Facing Layer)
**Rationale**: 
- Built first in refactoring
- User-facing, so most visible
- Already established in frontend

**Implication**:
- Content Steward: `retrieve_file()` → `get_file_details()` (to match Semantic API)
- Protocol: `get_file()` → `get_file_details()` (to match Semantic API)
- **Problem**: This breaks infrastructure abstraction layer (protocols should be infrastructure-focused)

### Option B: Protocols are Source of Truth (Infrastructure Layer)
**Rationale**:
- Protocols define infrastructure contracts
- Abstractions and adapters already use protocol names
- Infrastructure layer should be stable

**Implication**:
- Content Steward: `retrieve_file()` → `get_file()` (to match protocol)
- Semantic API: `get_file_details()` → Keep as-is (user-facing can be different)
- **Problem**: Semantic API was built first, so this reverses the refactoring direction

### Option C: Layer-Specific Naming (Recommended)
**Rationale**:
- Different layers serve different purposes
- User-facing APIs can have descriptive names
- Infrastructure protocols can have concise names
- Services bridge between layers

**Implication**:
- **Semantic API Layer**: Keep `get_file_details()` (user-focused, descriptive)
- **Orchestrator Layer**: Keep `get_file_details()` (matches Semantic API)
- **Service Layer**: Update `retrieve_file()` → `get_file()` (matches protocol)
- **Protocol Layer**: Keep `get_file()` (infrastructure-focused)
- **Adapter Layer**: Keep `get_file()` (matches protocol)

**Mapping**:
- `get_file_details()` (Semantic/Orchestrator) → `get_file()` (Service/Protocol/Adapter)

---

## Recommendation: Option C (Layer-Specific Naming)

### Why This Works

1. **Semantic APIs** are user-facing and should be descriptive (`get_file_details`)
2. **Protocols** are infrastructure contracts and should be concise (`get_file`)
3. **Services** bridge layers and should use protocol names (infrastructure-focused)
4. **Orchestrators** can translate between Semantic API names and Service names

### Implementation

**Content Steward Service** should be updated:
```python
# OLD
async def retrieve_file(self, file_id: str) -> Optional[Dict[str, Any]]:
    file_record = await self.file_management_abstraction.get_file(file_id)

# NEW
async def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
    """
    Get file via file_management infrastructure (SOA API).
    
    Note: This matches the FileManagementProtocol.get_file() method.
    For user-facing APIs, use ContentAnalysisOrchestrator.get_file_details().
    """
    file_record = await self.file_management_abstraction.get_file(file_id)
```

**Content Analysis Orchestrator** should translate:
```python
async def get_file_details(self, file_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get file details (Semantic API method).
    
    Translates to Content Steward's get_file() method.
    """
    # Call Content Steward's protocol method
    file_record = await self.content_steward.get_file(file_id)
    # Add orchestrator-specific enhancements
    # ...
```

### Benefits

1. ✅ **Protocols remain stable** - Infrastructure contracts don't change
2. ✅ **Semantic APIs remain user-friendly** - Descriptive names for users
3. ✅ **Services align with infrastructure** - Use protocol method names
4. ✅ **Orchestrators translate** - Bridge between user-facing and infrastructure

---

## Conclusion

**Source of Truth**: **Protocols** (for infrastructure layer), **Semantic APIs** (for user-facing layer)

**Action**: Update Content Steward's `retrieve_file()` → `get_file()` to align with protocol, while keeping Semantic API's `get_file_details()` as the user-facing method name.

**Pattern**: 
- User-facing: Descriptive names (`get_file_details`)
- Infrastructure: Concise names (`get_file`)
- Services: Use infrastructure names (protocol alignment)

---

**Last Updated**: November 13, 2025






