# Running Complete New Test Suite

**Quick Reference Guide - All Tests Created Tonight**

---

## 🚀 Quick Run

### Option 1: Using the Python Script (Recommended)

```bash
cd /home/founders/demoversion/symphainy_source
python3 tests/run_complete_new_test_suite.py
```

### Option 2: Using the Shell Script

```bash
cd /home/founders/demoversion/symphainy_source
./tests/run_new_tests.sh
```

---

## 📊 What It Does

The script runs **ALL** newly created tests from tonight (complete bottom-up test suite):

1. **Layer 0: Infrastructure Adapters** (14 tests)
   - GCS, Supabase, Redis variants, ArangoDB, Meilisearch, OpenTelemetry, Tempo, Celery

2. **Infrastructure Abstractions** (12 tests)
   - File Management, Auth, Session, Messaging, Event Management, Telemetry, Cache, Task Management, Knowledge Discovery, LLM, Content Schema, Content Insights

3. **Platform Gateway** (2 tests)
   - PlatformGatewayFoundationService, PlatformInfrastructureGateway

4. **Layer 3: Enabling Services** (5 tests)
   - File Parser, Format Composer, Data Analyzer, Roadmap Generation, POC Generation

5. **Layer 4: Orchestrators** (4 tests)
   - Content Analysis, Business Outcomes, Insights, Operations

6. **Layer 5: MCP Servers** (4 tests)
   - Business Outcomes, Content Analysis, Insights, Operations

7. **Layer 6: Agents** (4 tests)
   - Business Outcomes Specialist, Insights Specialist, Content Processing, Operations Specialist

**Total: 45+ test files covering the complete bottom-up test strategy**

---

## 📋 Output Format

The script provides:

1. **Category-by-category results**
   - Shows pass/fail for each test file
   - Shows test counts (passed/failed/skipped)

2. **Overall summary**
   - Total tests run
   - Success rate
   - Pass/fail/skip counts

3. **Failed tests section**
   - Lists all failed tests
   - Shows key error messages
   - Ready for tomorrow's troubleshooting

---

## ⚙️ Options

### Run with more verbose output

```bash
python3 tests/run_new_infrastructure_tests.py 2>&1 | tee test_results.log
```

### Run specific category

```bash
# Layer 0: Infrastructure Adapters
pytest tests/unit/infrastructure_adapters/ -v

# Infrastructure Abstractions
pytest tests/unit/infrastructure_abstractions/ -v

# Platform Gateway
pytest tests/unit/foundations/platform_gateway_foundation/ tests/unit/platform_infrastructure/test_platform_gateway.py -v

# Layer 3: Enabling Services
pytest tests/unit/enabling_services/ -v

# Layer 4: Orchestrators
pytest tests/unit/orchestrators/ -v

# Layer 5: MCP Servers
pytest tests/unit/mcp_servers/ -v

# Layer 6: Agents
pytest tests/unit/agents/ -v
```

---

## 🐛 Troubleshooting

If you see import errors or missing dependencies:

1. **Check Python path**
   ```bash
   cd /home/founders/demoversion/symphainy_source
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Install pytest-json-report** (optional, for better summaries)
   ```bash
   pip install pytest-json-report
   ```

3. **Run individual test** to see detailed errors
   ```bash
   pytest tests/unit/infrastructure_adapters/test_gcs_file_adapter.py -v
   ```

---

## 📝 Notes

- Tests use mocks, so they should run quickly
- Some tests may fail due to import path issues (to be fixed tomorrow)
- The script catches all errors gracefully
- Failed tests are clearly marked for tomorrow's work

---

**Happy testing!** 🎉

