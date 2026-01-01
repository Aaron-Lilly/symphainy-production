# Infrastructure Testing Strategy for Business Enablement Realm

## Problem Statement

File storage tests require GCS and Supabase infrastructure, but:
- Test environment may not have valid credentials
- We need to test actual infrastructure to ensure it "ACTUALLY WORKS"
- We also need fast, isolated tests for development

## Recommended Approach: Hybrid Strategy

### **Tier 1: Real Infrastructure with Test Isolation** (Primary)

**Goal:** Test actual infrastructure with isolated test data

**Implementation:**
1. **Test Buckets/Tables in Production Infrastructure**
   - GCS: `symphainy-bucket-2025-test` (or `symphainy-bucket-2025/test/`)
   - Supabase: `project_files_test` table (or `project_files` with `test_tenant_id`)
   - Use test-specific prefixes: `test/files/`, `test/metadata/`

2. **Test Configuration**
   - Environment variable: `TEST_INFRASTRUCTURE_ENABLED=true`
   - Test credentials: Separate service account for tests
   - Auto-cleanup: Tests clean up after themselves

3. **Benefits:**
   - ✅ Tests actual infrastructure (catches real issues)
   - ✅ Isolated from production data
   - ✅ Validates end-to-end flow
   - ✅ Catches infrastructure configuration issues

4. **Drawbacks:**
   - Requires credentials setup
   - Slightly slower (network calls)
   - Need cleanup mechanism

**When to Use:**
- Integration tests (Layer 8+)
- Pre-deployment validation
- CI/CD pipeline (with credentials)

---

### **Tier 2: Mock Infrastructure** (Development/Fast Tests)

**Goal:** Fast, isolated unit tests without infrastructure dependencies

**Implementation:**
1. **Mock Adapters**
   - `MockGCSAdapter`: In-memory file storage
   - `MockSupabaseAdapter`: In-memory metadata storage
   - Return realistic responses matching real adapters

2. **Test Fixtures**
   - Provide mock adapters when infrastructure unavailable
   - Tests can run without credentials

3. **Benefits:**
   - ✅ Fast (no network calls)
   - ✅ No credentials needed
   - ✅ Deterministic
   - ✅ Easy to test edge cases

4. **Drawbacks:**
   - Doesn't test real infrastructure
   - Might miss integration issues

**When to Use:**
- Unit tests
- Development (no credentials)
- Fast feedback loops

---

### **Tier 3: Hybrid Tests** (Recommended)

**Goal:** Tests that work with either real or mock infrastructure

**Implementation:**
```python
@pytest.fixture
async def file_storage_backend(request):
    """Provide file storage backend (real or mock)."""
    use_real = os.getenv("TEST_INFRASTRUCTURE_ENABLED", "false").lower() == "true"
    
    if use_real:
        # Real infrastructure with test isolation
        gcs_adapter = GCSFileAdapter(
            bucket_name="symphainy-bucket-2025-test",
            credentials_path=os.getenv("TEST_GCS_CREDENTIALS")
        )
        supabase_adapter = SupabaseFileManagementAdapter(
            url=os.getenv("TEST_SUPABASE_URL"),
            service_key=os.getenv("TEST_SUPABASE_KEY")
        )
        yield FileManagementAbstraction(gcs_adapter, supabase_adapter)
        
        # Cleanup test data
        await cleanup_test_files(gcs_adapter, supabase_adapter)
    else:
        # Mock infrastructure
        yield MockFileManagementAbstraction()
```

**Benefits:**
- ✅ Works in all environments
- ✅ Developers can run tests without credentials
- ✅ CI/CD can use real infrastructure
- ✅ Best of both worlds

---

## Recommended Implementation Plan

### Phase 1: Test Infrastructure Setup (Immediate)

1. **Create Test Resources**
   - GCS bucket: `symphainy-bucket-2025-test` (or subfolder)
   - Supabase: Use existing `project_files` with test prefix or separate table
   - Service account: `test-service-account@project.iam.gserviceaccount.com`

2. **Configuration**
   ```bash
   # .env.test
   TEST_INFRASTRUCTURE_ENABLED=true
   TEST_GCS_BUCKET=symphainy-bucket-2025-test
   TEST_GCS_CREDENTIALS=/path/to/test-credentials.json
   TEST_SUPABASE_URL=https://xxx.supabase.co
   TEST_SUPABASE_KEY=test_service_key
   TEST_TENANT_ID=test_tenant
   ```

3. **Test Isolation Strategy**
   - **Option A: Separate Bucket/Table** (Recommended)
     - GCS: `symphainy-bucket-2025-test`
     - Supabase: `project_files_test` table
     - Complete isolation, easy cleanup
   
   - **Option B: Prefix-Based Isolation**
     - GCS: `symphainy-bucket-2025/test/` prefix
     - Supabase: `project_files` with `test_tenant_id`
     - Shared infrastructure, prefix-based cleanup

4. **Auto-Cleanup**
   ```python
   @pytest.fixture(autouse=True)
   async def cleanup_test_files():
       """Clean up test files after each test."""
       yield
       if TEST_INFRASTRUCTURE_ENABLED:
           await cleanup_test_prefix("test/")
   ```

---

### Phase 2: Mock Infrastructure (Development)

1. **Create Mock Adapters**
   ```python
   class MockGCSAdapter:
       def __init__(self):
           self.files = {}  # In-memory storage
       
       async def upload_file(self, blob_name, file_data, **kwargs):
           self.files[blob_name] = file_data
           return True
       
       async def download_file(self, blob_name):
           return self.files.get(blob_name)
   ```

2. **Update Test Fixtures**
   - Detect infrastructure availability
   - Fall back to mocks if unavailable
   - Log which backend is being used

---

### Phase 3: Hybrid Test Pattern

1. **Update Test Utilities**
   ```python
   class TestFileManager:
       @staticmethod
       async def get_file_storage_backend():
           """Get file storage backend (real or mock)."""
           if os.getenv("TEST_INFRASTRUCTURE_ENABLED") == "true":
               return await create_real_backend()
           return MockFileStorageBackend()
   ```

2. **Update Tests**
   - Tests work with either backend
   - Mark tests that require real infrastructure
   - Skip gracefully if unavailable

---

## My Recommendation

### **Option A: Test Buckets/Tables (Recommended for Your Use Case)**

**Why:**
- You emphasized "bulletproof" and "actually works"
- Real infrastructure testing catches real issues
- Test isolation prevents production data contamination
- Matches your testing philosophy

**Implementation:**
1. **GCS**: Create `symphainy-bucket-2025-test` bucket
   - Same region as production
   - Lifecycle policy: Delete files older than 7 days
   - IAM: Test service account with read/write access

2. **Supabase**: Use `project_files` table with test isolation
   - Option 1: `tenant_id = 'test_tenant'` filter
   - Option 2: `project_files_test` table (if schema allows)
   - Auto-cleanup: Delete test records after tests

3. **Test Configuration**
   ```python
   # tests/integration/conftest.py
   @pytest.fixture(scope="session")
   def test_infrastructure_config():
       return {
           "gcs_bucket": os.getenv("TEST_GCS_BUCKET", "symphainy-bucket-2025-test"),
           "supabase_table": "project_files",
           "test_tenant_id": "test_tenant",
           "test_prefix": "test/"
       }
   ```

4. **Cleanup Strategy**
   ```python
   @pytest.fixture(autouse=True)
   async def cleanup_test_data(test_infrastructure_config):
       """Clean up test data after each test."""
       yield
       # Delete files with test prefix
       await cleanup_test_files(test_infrastructure_config["test_prefix"])
   ```

---

### **Option B: Hybrid with Mocks (More Flexible)**

**Why:**
- Developers can run tests without credentials
- CI/CD can use real infrastructure
- Fast feedback for development

**Implementation:**
- Use real infrastructure when `TEST_INFRASTRUCTURE_ENABLED=true`
- Use mocks otherwise
- Tests work in both modes

---

## Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Real Infrastructure (Test Isolation)** | Tests actual infrastructure, catches real issues | Requires credentials, slower | Integration tests, CI/CD |
| **Mock Infrastructure** | Fast, no dependencies | Doesn't test real infrastructure | Unit tests, development |
| **Hybrid** | Best of both worlds | More complex setup | **Recommended** |

---

## Recommended Next Steps

1. **Immediate (Today)**
   - Set up test GCS bucket: `symphainy-bucket-2025-test`
   - Configure test Supabase access (test tenant or test table)
   - Create test service account credentials
   - Add test configuration to `.env.test`

2. **Short-term (This Week)**
   - Implement test isolation (prefix-based or separate resources)
   - Add auto-cleanup mechanism
   - Update test fixtures to use test infrastructure
   - Verify tests work with real infrastructure

3. **Medium-term (Next Week)**
   - Create mock adapters for development
   - Implement hybrid pattern (real or mock)
   - Update all Business Enablement tests
   - Document infrastructure testing patterns

---

## Questions to Consider

1. **Do you have GCS/Supabase credentials for testing?**
   - If yes: Use real infrastructure (Option A)
   - If no: Start with mocks, add real infrastructure later

2. **What's your cleanup strategy?**
   - Automatic (preferred): Tests clean up after themselves
   - Manual: Periodic cleanup job
   - Lifecycle policies: GCS/Supabase auto-delete

3. **CI/CD Integration?**
   - Use real infrastructure in CI/CD
   - Use mocks for local development
   - Hybrid: Real in CI, mocks locally

---

## My Specific Recommendation

Given your emphasis on "bulletproof" and "actually works", I recommend:

**Start with Option A (Real Infrastructure with Test Isolation)**
- Set up test bucket and test tenant/table
- Use prefix-based isolation (`test/` prefix)
- Implement auto-cleanup
- This ensures tests validate actual infrastructure

**Add Option B (Mocks) Later**
- For faster development feedback
- For developers without credentials
- As a fallback when infrastructure unavailable

This gives you:
- ✅ Real infrastructure testing (validates actual behavior)
- ✅ Test isolation (no production data contamination)
- ✅ Auto-cleanup (no manual maintenance)
- ✅ Flexibility (can add mocks later)

Would you like me to:
1. Set up the test infrastructure configuration?
2. Create the test isolation and cleanup mechanisms?
3. Update the test fixtures to use test infrastructure?

