# GCS Bucket Access - Improvement Plan

## 🎯 Current Challenges

### **1. Complex Path Resolution**
- **Issue**: Credentials path resolution is fragile and depends on current working directory
- **Impact**: Tests fail when run from different directories
- **Current State**: Simplified but still has issues

### **2. Multiple Abstraction Layers**
- **Current Stack**:
  1. `GCSFileAdapter` (raw GCS client)
  2. `FileManagementAbstraction` (business logic)
  3. `FileManagementCompositionService` (composition)
  4. `ContentSteward` (Smart City service)
  5. `FileParserService` (enabling service)
- **Issue**: Tests need to navigate through multiple layers
- **Impact**: Complex test setup, hard to debug failures

### **3. Configuration Scattered**
- **Locations**:
  - `.env.secrets` - Production config
  - `test_infrastructure_config` - Test config
  - `GCS_CREDENTIALS_PATH` - Environment variable
  - `TEST_GCS_CREDENTIALS` - Test-specific variable
- **Issue**: Unclear which config is used when
- **Impact**: Confusion, hard to debug credential issues

### **4. Test Setup Complexity**
- **Current**: Each test creates its own adapters/abstractions
- **Example**:
  ```python
  gcs_adapter = GCSFileAdapter(...)
  supabase_adapter = SupabaseFileManagementAdapter(...)
  file_abstraction = FileManagementAbstraction(...)
  content_steward = ContentStewardService(...)
  ```
- **Issue**: Repetitive, error-prone setup
- **Impact**: Tests are verbose, hard to maintain

### **5. No Unified Test Helper**
- **Issue**: Tests use different approaches:
  - Some use `ContentStewardHelper`
  - Some use `file_storage_backend` fixture
  - Some create adapters directly
- **Impact**: Inconsistent test patterns, hard to maintain

---

## ✅ Recommended Improvements

### **Improvement 1: Unified Test Fixture for GCS Access**

**Goal**: Single, simple fixture that provides GCS access for all tests

**Implementation**:
```python
# tests/integration/layer_8_business_enablement/conftest.py

@pytest.fixture(scope="function")
async def gcs_file_storage(smart_city_infrastructure):
    """
    Unified GCS file storage fixture.
    
    Provides direct access to file storage via Content Steward (recommended)
    or FileManagementAbstraction (fallback).
    
    Returns:
        ContentSteward API (preferred) or FileManagementAbstraction
    """
    infra = smart_city_infrastructure
    
    # Tier 1: Use Content Steward (Smart City service - recommended)
    content_steward = infra["smart_city_services"].get("content_steward")
    if content_steward:
        yield content_steward
        return
    
    # Tier 2: Fallback to FileManagementAbstraction
    file_abstraction = infra["public_works_foundation"].get_file_management_abstraction()
    if file_abstraction:
        yield file_abstraction
        return
    
    # Tier 3: Fail with helpful message
    pytest.fail(
        "GCS file storage not available. "
        "Ensure Content Steward or FileManagementAbstraction is initialized."
    )
```

**Benefits**:
- ✅ Single fixture for all tests
- ✅ Automatic fallback chain
- ✅ Clear error messages
- ✅ Uses Smart City services (recommended pattern)

---

### **Improvement 2: Simplified Configuration Management**

**Goal**: Single source of truth for GCS configuration

**Implementation**:
```python
# tests/integration/layer_8_business_enablement/gcs_config.py

class GCSConfig:
    """Unified GCS configuration for tests."""
    
    @staticmethod
    def get_credentials_path() -> Optional[str]:
        """
        Get GCS credentials path with proper resolution.
        
        Priority:
        1. TEST_GCS_CREDENTIALS (test-specific)
        2. GCS_CREDENTIALS_PATH (shared)
        3. None (use Application Default Credentials)
        """
        import os
        from pathlib import Path
        
        # Try test-specific first
        creds_path = os.getenv("TEST_GCS_CREDENTIALS")
        if creds_path:
            return GCSConfig._resolve_path(creds_path)
        
        # Try shared config
        creds_path = os.getenv("GCS_CREDENTIALS_PATH")
        if creds_path:
            return GCSConfig._resolve_path(creds_path)
        
        # Use Application Default Credentials
        return None
    
    @staticmethod
    def _resolve_path(path: str) -> str:
        """Resolve relative path to absolute."""
        if os.path.isabs(path):
            return path
        
        # Try relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        resolved = (project_root / "symphainy-platform" / path).resolve()
        if resolved.exists():
            return str(resolved)
        
        # Try relative to current working directory
        resolved = Path(path).resolve()
        if resolved.exists():
            return str(resolved)
        
        # Return as-is (will fail later with clear error)
        return path
    
    @staticmethod
    def get_bucket_name() -> str:
        """Get GCS bucket name."""
        return os.getenv("TEST_GCS_BUCKET") or os.getenv("GCS_BUCKET_NAME") or "symphainy-bucket-2025"
    
    @staticmethod
    def get_project_id() -> str:
        """Get GCP project ID."""
        return os.getenv("GCS_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT") or "symphainymvp-devbox"
```

**Benefits**:
- ✅ Single source of truth
- ✅ Clear priority order
- ✅ Proper path resolution
- ✅ Easy to test and debug

---

### **Improvement 3: Enhanced ContentStewardHelper**

**Goal**: Make ContentStewardHelper the standard way to access GCS in tests

**Current Issues**:
- Helper exists but not all tests use it
- Some tests create adapters directly
- Inconsistent patterns

**Improvements**:
```python
# tests/integration/layer_8_business_enablement/test_utilities.py

class ContentStewardHelper:
    """Enhanced helper for Content Steward integration in tests."""
    
    def __init__(self, content_steward_api: Any, user_context: Dict[str, Any]):
        """Initialize with automatic validation."""
        if not content_steward_api:
            raise ValueError("Content Steward API is required")
        if not user_context:
            raise ValueError("User context is required")
        
        self.content_steward = content_steward_api
        self.user_context = user_context
        self.stored_files: list = []
    
    async def store_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store file and return file_id.
        
        Raises:
            ValueError: If storage fails
        """
        file_id = await self._store_file_internal(file_data, filename, content_type, metadata)
        if not file_id:
            raise ValueError(f"Failed to store file: {filename}")
        return file_id
    
    async def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get file by ID.
        
        Raises:
            ValueError: If file not found
        """
        file_record = await self.content_steward.get_file(file_id)
        if not file_record:
            raise ValueError(f"File not found: {file_id}")
        return file_record
    
    async def cleanup(self):
        """Clean up all stored test files."""
        # Implementation with error handling
        pass
```

**Benefits**:
- ✅ Consistent API
- ✅ Better error messages
- ✅ Automatic cleanup
- ✅ Type hints and validation

---

### **Improvement 4: Mock Support for Development**

**Goal**: Allow tests to run without GCS credentials (for development)

**Implementation**:
```python
# tests/integration/layer_8_business_enablement/conftest.py

@pytest.fixture(scope="function")
async def gcs_file_storage(smart_city_infrastructure, request):
    """
    GCS file storage with automatic mocking if unavailable.
    """
    # Check if mocking is enabled
    use_mock = os.getenv("TEST_USE_MOCK_GCS", "false").lower() == "true"
    
    if use_mock:
        from tests.utils.mock_gcs import MockGCSFileStorage
        yield MockGCSFileStorage()
        return
    
    # Try real infrastructure
    # ... (existing implementation)
```

**Mock Implementation**:
```python
# tests/utils/mock_gcs.py

class MockGCSFileStorage:
    """In-memory mock GCS storage for tests."""
    
    def __init__(self):
        self.files: Dict[str, bytes] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    async def store_file(self, file_data: bytes, filename: str, **kwargs) -> str:
        """Store file in memory."""
        file_id = str(uuid.uuid4())
        self.files[file_id] = file_data
        self.metadata[file_id] = {
            "uuid": file_id,
            "filename": filename,
            **kwargs
        }
        return file_id
    
    async def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get file from memory."""
        if file_id not in self.files:
            return None
        return {
            "uuid": file_id,
            "file_content": self.files[file_id],
            **self.metadata[file_id]
        }
```

**Benefits**:
- ✅ Tests can run without credentials
- ✅ Faster development cycle
- ✅ Still test real infrastructure when available
- ✅ Easy to switch between mock and real

---

### **Improvement 5: Simplified Credential Path Resolution**

**Goal**: Eliminate path resolution complexity

**Current Approach**:
- Complex path resolution in adapter
- Multiple fallback strategies
- Depends on current working directory

**Recommended Approach**:
```python
# symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/gcs_file_adapter.py

def __init__(self, project_id: str, bucket_name: str, credentials_path: str = None):
    """
    Initialize with credentials path.
    
    CRITICAL: credentials_path should be absolute or None.
    Caller is responsible for path resolution.
    """
    if credentials_path and not os.path.isabs(credentials_path):
        # Log warning but don't fail - let GCS client handle it
        logger.warning(
            f"⚠️ Credentials path is relative: {credentials_path}. "
            f"Consider using absolute path or resolving before passing to adapter."
        )
    
    # Simple: Pass to GCS client as-is
    if credentials_path and os.path.exists(credentials_path):
        self._client = storage.Client.from_service_account_json(credentials_path, project=project_id)
    else:
        self._client = storage.Client(project=project_id)
```

**Path Resolution in Config Layer**:
```python
# symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/config_adapter.py

def get_gcs_credentials_path(self) -> Optional[str]:
    """Get and resolve GCS credentials path."""
    raw_path = self.get("GCS_CREDENTIALS_PATH")
    if not raw_path:
        return None
    
    # Resolve at config layer (knows about project structure)
    return self._resolve_credentials_path(raw_path)

def _resolve_credentials_path(self, path: str) -> str:
    """Resolve credentials path relative to project root."""
    if os.path.isabs(path):
        return path
    
    # Resolve relative to symphainy-platform directory
    project_root = Path(__file__).parent.parent.parent.parent
    resolved = (project_root / path).resolve()
    
    if resolved.exists():
        return str(resolved)
    
    # Return as-is (will fail with clear error from GCS client)
    return path
```

**Benefits**:
- ✅ Separation of concerns: Config layer handles resolution
- ✅ Adapter is simple: Just uses the path
- ✅ Clear error messages from GCS client
- ✅ Easier to test and debug

---

## 📋 Migration Plan

### **Phase 1: Create Unified Fixture** ✅
1. Create `gcs_file_storage` fixture
2. Update existing tests to use it
3. Document usage patterns

### **Phase 2: Simplify Configuration** ✅
1. Create `GCSConfig` class
2. Update adapters to use it
3. Remove duplicate path resolution logic

### **Phase 3: Enhance Helpers** ✅
1. Improve `ContentStewardHelper`
2. Add validation and error handling
3. Update all tests to use helper

### **Phase 4: Add Mock Support** ✅
1. Create `MockGCSFileStorage`
2. Add fixture option for mocking
3. Document when to use mocks vs real

### **Phase 5: Clean Up** ✅
1. Remove duplicate code
2. Update documentation
3. Add examples

---

## 🎯 Expected Benefits

### **For Tests**
- ✅ **Simpler**: Single fixture, no complex setup
- ✅ **Faster**: Mock support for development
- ✅ **Clearer**: Better error messages
- ✅ **Consistent**: All tests use same pattern

### **For Development**
- ✅ **Easier**: No credential setup needed for basic tests
- ✅ **Faster**: Mock support speeds up development
- ✅ **Clearer**: Single source of truth for config

### **For Debugging**
- ✅ **Better Errors**: Clear messages when things fail
- ✅ **Easier Tracing**: Single code path to follow
- ✅ **Less Confusion**: No multiple config sources

---

## 📚 Usage Examples

### **Example 1: Simple File Storage Test**
```python
@pytest.mark.asyncio
async def test_store_file(gcs_file_storage, user_context):
    """Store a file using unified fixture."""
    helper = ContentStewardHelper(gcs_file_storage, user_context)
    
    file_data = b"test content"
    file_id = await helper.store_file(file_data, "test.txt")
    
    assert file_id is not None
    
    # Cleanup
    await helper.cleanup()
```

### **Example 2: Using Mock for Development**
```python
# Set environment variable
# TEST_USE_MOCK_GCS=true

@pytest.mark.asyncio
async def test_with_mock(gcs_file_storage, user_context):
    """Test with mock GCS (no credentials needed)."""
    helper = ContentStewardHelper(gcs_file_storage, user_context)
    
    # Works without real GCS credentials
    file_id = await helper.store_file(b"test", "test.txt")
    assert file_id is not None
```

### **Example 3: Direct Configuration Access**
```python
from tests.integration.layer_8_business_enablement.gcs_config import GCSConfig

def test_config_access():
    """Access GCS configuration directly."""
    creds_path = GCSConfig.get_credentials_path()
    bucket_name = GCSConfig.get_bucket_name()
    
    # Use configuration
    assert bucket_name is not None
```

---

## ✅ Summary

**Key Improvements**:
1. ✅ **Unified Fixture**: Single `gcs_file_storage` fixture for all tests
2. ✅ **Simplified Config**: `GCSConfig` class with proper path resolution
3. ✅ **Enhanced Helper**: Better `ContentStewardHelper` with validation
4. ✅ **Mock Support**: In-memory mock for development
5. ✅ **Cleaner Adapter**: Simple adapter, config handles resolution

**Result**: 
- Simpler test code
- Easier development
- Better error messages
- Consistent patterns
- No credential setup needed for basic tests

