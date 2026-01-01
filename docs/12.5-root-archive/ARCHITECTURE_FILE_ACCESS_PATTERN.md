# File Access Architecture Pattern

## The Correct Pattern

### Layer Architecture
```
┌─────────────────────────────────────────────────────────────┐
│ Business Enablement (FileParserService)                      │
│ - Uses Smart City SOA APIs                                   │
│ - NO direct infrastructure access                            │
└────────────────────┬────────────────────────────────────────┘
                     │ SOA API Call
                     │ content_steward.retrieve_file(file_id)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Smart City (ContentStewardService)                           │
│ - Exposes SOA APIs to Business Enablement                    │
│ - CAN access infrastructure directly                         │
│ - Wraps infrastructure abstractions                          │
└────────────────────┬────────────────────────────────────────┘
                     │ Infrastructure Access
                     │ file_management.get_file(file_id)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Infrastructure (Public Works Foundation)                     │
│ - FileManagementAbstraction (GCS)                            │
│ - Abstractions over adapters                                 │
│ - Accessed by Smart City services only                       │
└─────────────────────────────────────────────────────────────┘
```

## Implementation

### ✅ CORRECT: Business Enablement → Smart City SOA API

**FileParserService (Business Enablement)**:
```python
class FileParserService(RealmServiceBase):
    async def initialize(self):
        # Discover Smart City services
        self.content_steward = await self.get_content_steward_api()
    
    async def retrieve_document(self, file_id: str):
        # Use Smart City SOA API
        return await self.content_steward.retrieve_file(file_id)
```

### ✅ CORRECT: Smart City → Infrastructure

**ContentStewardService (Smart City)**:
```python
class ContentStewardService(SmartCityRoleBase):
    async def retrieve_file(self, file_id: str):
        """SOA API exposed to Business Enablement."""
        # Smart City CAN access infrastructure directly
        file_management = self.get_abstraction("file_management")
        return await file_management.get_file(file_id)
```

### ❌ WRONG: Business Enablement → Infrastructure (Direct)

```python
class FileParserService(RealmServiceBase):
    async def initialize(self):
        # ❌ WRONG: Business Enablement accessing infrastructure directly
        self.file_management = self.get_abstraction("file_management")
        # This violates architecture and triggers realm access control errors
```

## Why This Pattern?

### Separation of Concerns
1. **Infrastructure Layer** - Raw capabilities (GCS, Supabase, Redis)
2. **Smart City Layer** - Domain services with business logic
3. **Business Enablement Layer** - Use case orchestration

### Benefits
1. **Encapsulation**: Infrastructure changes don't affect Business Enablement
2. **Reusability**: Multiple Business Enablement services use same Smart City APIs
3. **Security**: Realm access control enforces proper layering
4. **Testability**: Can mock Smart City APIs without mocking infrastructure

### Content Steward SOA APIs

**Available APIs for Business Enablement**:
```python
# File Operations
await content_steward.retrieve_file(file_id)           # Get file with content
await content_steward.get_file_metadata(file_id)       # Get metadata only
await content_steward.update_file_metadata(file_id, updates)

# Content Processing
await content_steward.process_file_content(file_id, options)
await content_steward.validate_content(content_data, content_type)
await content_steward.convert_file_format(file_id, source_fmt, target_fmt)

# Quality & Metrics
await content_steward.get_quality_metrics(asset_id)
```

## File Storage Details

### Upload Flow
```
1. User uploads file → API Router
2. API Router → ContentAnalysisOrchestrator
3. ContentAnalysisOrchestrator → ContentStewardService.process_upload()
4. ContentSteward:
   - Stores file content → GCS (files/{uuid})
   - Stores file metadata → Supabase (client_files table)
   - Metadata includes: service_context.gcs_blob_name
```

### Retrieval Flow
```
1. FileParserService needs file
2. FileParser → ContentSteward.retrieve_file(file_id)
3. ContentSteward:
   - Gets metadata from Supabase
   - Gets content from GCS using gcs_blob_name
   - Combines and returns complete file record
4. FileParser receives file with content
```

## Key Takeaways

1. **Business Enablement services NEVER access infrastructure directly**
2. **Smart City services expose SOA APIs for Business Enablement**
3. **Smart City services CAN access infrastructure directly**
4. **Realm access control enforces this pattern**
5. **Content Steward is the primary file access API for Business Enablement**

---

**Document Created**: 2025-11-12  
**Status**: Architectural pattern established and implemented





