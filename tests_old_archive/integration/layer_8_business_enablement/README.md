# Business Enablement Realm - Test Infrastructure

## 📋 Overview

This directory contains comprehensive tests for the Business Enablement realm, including test infrastructure setup for GCS and Supabase.

## 🚀 Quick Start

**Fastest way to get started:**

```bash
cd tests/integration/layer_8_business_enablement
./setup_test_infrastructure.sh
```

Then follow the prompts and update `.env.test` with your Supabase credentials.

**See `QUICK_START.md` for detailed instructions.**

---

## 📁 Files Overview

### Setup Scripts
- **`setup_test_infrastructure.sh`** - Automated GCS bucket and service account setup
- **`setup_supabase_test_isolation.sql`** - SQL script for Supabase test isolation
- **`verify_test_infrastructure.py`** - Verification script to check setup

### Test Files
- **`test_file_parser_core.py`** - Core File Parser tests (4 file types, error handling)
- **`test_file_parser_comprehensive.py`** - Comprehensive File Parser tests (all file types, formats)
- **`test_enabling_services_comprehensive.py`** - Tests for enabling services
- **`test_utilities.py`** - Test utilities (file creation, Content Steward helpers)
- **`test_infrastructure_setup.py`** - Test infrastructure fixtures

### Documentation
- **`QUICK_START.md`** - Quick setup guide (start here!)
- **`INFRASTRUCTURE_SETUP_GUIDE.md`** - Detailed infrastructure setup guide
- **`INFRASTRUCTURE_TESTING_STRATEGY.md`** - Testing strategy and approach
- **`ROOT_CAUSE_ANALYSIS.md`** - Root cause analysis of bugs fixed
- **`EXECUTION_PLAN.md`** - Phased execution plan for comprehensive testing
- **`COMPREHENSIVE_TEST_STRATEGY.md`** - Overall test strategy

---

## 🏗️ Test Infrastructure

### Architecture

**Real Infrastructure with Test Isolation:**
- **GCS**: Test bucket `symphainy-bucket-2025-test` with `test/` prefix
- **Supabase**: Existing `project_files` table with `tenant_id = 'test_tenant'`
- **Auto-cleanup**: Lifecycle policies delete test data after 7 days

### Configuration

Test infrastructure is configured via `.env.test`:

```bash
TEST_INFRASTRUCTURE_ENABLED=true
TEST_GCS_BUCKET=symphainy-bucket-2025-test
TEST_GCS_CREDENTIALS=/path/to/test-credentials.json
TEST_SUPABASE_URL=https://xxx.supabase.co
TEST_SUPABASE_SERVICE_KEY=your_service_key
TEST_TENANT_ID=test_tenant
```

### Running Tests

**With Infrastructure:**
```bash
export TEST_INFRASTRUCTURE_ENABLED=true
pytest tests/integration/layer_8_business_enablement/ -v
```

**Without Infrastructure (Tests Skip):**
```bash
# Don't set TEST_INFRASTRUCTURE_ENABLED
pytest tests/integration/layer_8_business_enablement/ -v
```

---

## ✅ Current Status

### Completed ✅
- [x] Test infrastructure setup scripts
- [x] Test utilities (file creation, Content Steward helpers)
- [x] Core File Parser tests (4 file types, error handling)
- [x] Root cause analysis and bug fixes
- [x] Test infrastructure fixtures
- [x] Graceful handling of missing infrastructure

### In Progress 🚧
- [ ] Comprehensive File Parser tests (all file types, formats)
- [ ] Priority services tests (Validation, Transformation, Data Analyzer, Schema Mapper)
- [ ] Remaining enabling services tests

### Planned 📋
- [ ] Orchestrator tests
- [ ] Delivery Manager tests
- [ ] Integration tests
- [ ] End-to-end workflow tests

---

## 🔧 Setup Instructions

### Step 1: Run Setup Script

```bash
cd tests/integration/layer_8_business_enablement
./setup_test_infrastructure.sh
```

This creates:
- GCS test bucket
- Service account
- Credentials file
- `.env.test` configuration

### Step 2: Configure Supabase

Edit `.env.test` and add Supabase credentials:

```bash
TEST_SUPABASE_URL=https://xxx.supabase.co
TEST_SUPABASE_SERVICE_KEY=your_service_key
```

### Step 3: Set Up Supabase Test Isolation

Run `setup_supabase_test_isolation.sql` in Supabase SQL Editor.

### Step 4: Verify

```bash
python3 verify_test_infrastructure.py
```

### Step 5: Run Tests

```bash
export TEST_INFRASTRUCTURE_ENABLED=true
pytest tests/integration/layer_8_business_enablement/ -v
```

---

## 🐛 Troubleshooting

### GCS Issues

**Authentication Error:**
```bash
gcloud auth activate-service-account --key-file=test-credentials.json
gsutil ls gs://symphainy-bucket-2025-test/
```

**Bucket Not Found:**
```bash
gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://symphainy-bucket-2025-test
```

### Supabase Issues

**Connection Error:**
```bash
curl -H "apikey: YOUR_SERVICE_KEY" https://xxx.supabase.co/rest/v1/
```

**Test Data Not Isolated:**
- Verify `tenant_id = 'test_tenant'` is used in tests
- Check Supabase RLS policies (if enabled)

### Test Issues

**Tests Skipping:**
- Check `TEST_INFRASTRUCTURE_ENABLED=true`
- Verify credentials are correct
- Run `verify_test_infrastructure.py`

**File Storage Failing:**
- Check GCS bucket exists and is accessible
- Verify service account has permissions
- Check Supabase connection

---

## 📚 Documentation

- **Quick Start**: `QUICK_START.md` - Get started in 5 minutes
- **Setup Guide**: `INFRASTRUCTURE_SETUP_GUIDE.md` - Detailed setup instructions
- **Strategy**: `INFRASTRUCTURE_TESTING_STRATEGY.md` - Testing approach and rationale
- **Root Cause**: `ROOT_CAUSE_ANALYSIS.md` - Bugs fixed and why
- **Execution Plan**: `EXECUTION_PLAN.md` - Phased testing approach

---

## 🔒 Security

**Important Security Notes:**

1. **Never commit credentials!**
   - `test-credentials.json` is in `.gitignore`
   - `.env.test` is in `.gitignore`
   - Always verify before committing

2. **Use separate service account**
   - Test service account is separate from production
   - Limited permissions (Storage Object Admin only)

3. **Test data isolation**
   - All test files use `test/` prefix in GCS
   - All test records use `tenant_id = 'test_tenant'` in Supabase
   - Auto-cleanup after 7 days

---

## 📊 Test Coverage

### File Parser Service
- ✅ Text files (.txt)
- ✅ COBOL copybook files (.cpy)
- ✅ Mainframe binary files (.bin)
- ✅ HTML files (.html)
- ✅ Error handling (invalid file ID, missing file)
- 🚧 JSON/XML output formats
- 🚧 PDF, Excel, Word files
- 🚧 Image files with OCR

### Enabling Services
- 🚧 Validation Engine
- 🚧 Transformation Engine
- 🚧 Data Analyzer
- 🚧 Schema Mapper
- 🚧 Remaining 20 services

### Orchestrators
- 🚧 Content Analysis Orchestrator
- 🚧 Insights Orchestrator
- 🚧 Operations Orchestrator
- 🚧 Business Outcomes Orchestrator

### Manager Services
- 🚧 Delivery Manager Service

---

## 🎯 Next Steps

1. **Complete File Parser tests** (all file types, formats)
2. **Priority services** (Validation, Transformation, Data Analyzer, Schema Mapper)
3. **Remaining services** (batch approach)
4. **Orchestrators** (integration focus)
5. **Delivery Manager** (end-to-end)
6. **Integration tests** (cross-service workflows)

---

## 💡 Tips

- **Start with infrastructure setup** - Run `setup_test_infrastructure.sh` first
- **Verify before testing** - Use `verify_test_infrastructure.py`
- **Check logs** - Tests provide detailed error messages
- **Use test isolation** - All test data is isolated from production
- **Auto-cleanup** - Lifecycle policies handle cleanup automatically

---

## 🤝 Contributing

When adding new tests:
1. Use test utilities from `test_utilities.py`
2. Follow patterns in `test_file_parser_core.py`
3. Use test infrastructure fixtures from `test_infrastructure_setup.py`
4. Ensure tests work with and without infrastructure
5. Document any new test patterns

---

## 📞 Support

For issues or questions:
1. Check `QUICK_START.md` for common issues
2. Review `ROOT_CAUSE_ANALYSIS.md` for known fixes
3. Run `verify_test_infrastructure.py` to diagnose issues
4. Check test logs for detailed error messages

