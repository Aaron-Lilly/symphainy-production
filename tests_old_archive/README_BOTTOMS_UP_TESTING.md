# Bottom-Up Testing Implementation

## Overview

This directory contains the bottom-up testing strategy implementation, focusing on:
1. **Real Infrastructure Testing** - Using actual infrastructure (not mocks) to catch real issues
2. **Critical Output Validation** - Ensuring roadmap and POC proposals are impressive
3. **Platform Gateway Validation** - Verifying abstraction exposure patterns
4. **Production Readiness Validation** - Ensuring no placeholders, proper access patterns, graceful failures

## Test Structure

```
tests/
├── docker-compose.test.yml          # Real infrastructure containers
├── fixtures/
│   └── real_infrastructure_fixtures.py  # Real infrastructure fixtures
├── integration/
│   ├── orchestrators/
│   │   ├── test_business_outcomes_roadmap_output.py  # CRITICAL
│   │   ├── test_business_outcomes_poc_output.py      # CRITICAL
│   │   └── test_orchestrator_access_patterns.py     # CRITICAL (NEW)
│   ├── enabling_services/
│   │   └── test_enabling_service_access_patterns.py # CRITICAL (NEW)
│   ├── production_readiness/
│   │   ├── test_no_placeholders.py                  # CRITICAL (NEW)
│   │   ├── test_no_placeholder_tokens.py            # CRITICAL (NEW)
│   │   ├── test_real_quality_scores.py              # CRITICAL (NEW)
│   │   ├── test_graceful_failures.py                # HIGH (NEW)
│   │   └── test_error_code_consistency.py          # HIGH (NEW)
│   ├── deployment/
│   │   ├── test_frontend_config.py                  # MEDIUM (NEW)
│   │   └── test_backend_config.py                   # MEDIUM (NEW)
│   ├── infrastructure_adapters/     # Layer 1 tests (TODO)
│   ├── foundations/                 # Layer 2 tests (TODO)
│   └── platform_gateway/            # Layer 2 tests (TODO)
└── README_BOTTOMS_UP_TESTING.md     # This file
```

## Setup

### 1. Start Test Infrastructure

```bash
# Start real infrastructure containers
docker-compose -f tests/docker-compose.test.yml up -d

# Verify containers are healthy
docker-compose -f tests/docker-compose.test.yml ps
```

### 2. Run Tests

```bash
# Run critical orchestrator output tests
pytest tests/integration/orchestrators/test_business_outcomes_roadmap_output.py -v
pytest tests/integration/orchestrators/test_business_outcomes_poc_output.py -v

# Run critical production readiness tests (NEW)
pytest tests/integration/production_readiness/ -v -m critical
pytest tests/integration/orchestrators/test_orchestrator_access_patterns.py -v

# Run all integration tests
pytest tests/integration/ -v

# Run with markers
pytest -m critical -v  # Run only critical tests
pytest -m integration -v  # Run all integration tests
```

## Test Priorities

### ✅ Completed (Critical)
- [x] Test infrastructure setup (docker-compose.test.yml)
- [x] Real infrastructure fixtures
- [x] Roadmap output tests (Layer 4)
- [x] POC proposal output tests (Layer 4)

### 🔄 In Progress (Critical - Production Readiness)
- [ ] Access pattern tests (Layer 7) - Four-tier/three-tier validation
- [ ] No placeholder tests (Layer 8) - Validate no mock data
- [ ] Graceful failure tests (Layer 9) - Validate error handling

### 🔄 In Progress (High Priority)
- [ ] Redis adapter real infrastructure tests (Layer 1)
- [ ] ArangoDB adapter real infrastructure tests (Layer 1)
- [ ] Meilisearch adapter real infrastructure tests (Layer 1)
- [ ] Smart City abstraction access tests (Layer 2)
- [ ] Platform Gateway realm access tests (Layer 2)

### 📋 TODO (Medium Priority)
- [ ] Enabling service tests (Layer 3)
- [ ] CTO demo scenario tests (Layer 5)
- [ ] MVP requirements tests (Layer 6)
- [ ] EC2 deployment configuration tests (Layer 10)

## Key Test Patterns

### Real Infrastructure Testing

Tests use **real infrastructure** (not mocks) to catch actual issues:

```python
@pytest.fixture
async def real_public_works_foundation():
    """Real Public Works Foundation with real adapters."""
    foundation = PublicWorksFoundationService(...)
    await foundation.initialize_foundation()
    yield foundation
    await foundation.shutdown()
```

### Output Quality Validation

Tests validate that outputs are **impressive** (not generic):

```python
# Validate roadmap is impressive
executive_summary = roadmap.get("executive_summary", "")
assert len(executive_summary) > 500, "Too short for impressive output"

# Check for context-specific content
context_indicators = ["defense", "testing", "safety"]
has_context = any(indicator in summary_lower for indicator in context_indicators)
assert has_context, "Roadmap appears generic"
```

### Access Pattern Validation (NEW)

Tests validate four-tier/three-tier access patterns:

```python
# Test orchestrator four-tier pattern
result = await orchestrator.get_capability("file_parsing", file_id="test123")
assert result is not None  # Never return None
assert result["success"] is False or "data" in result
if not result["success"]:
    assert "error_code" in result
    assert "message" in result
```

### No Placeholder Validation (NEW)

Tests ensure no placeholder data:

```python
# Check for placeholder text
placeholder_indicators = ["This is placeholder", "placeholder text content"]
for indicator in placeholder_indicators:
    assert indicator.lower() not in text_content.lower()
```

## Success Criteria

### Roadmap Output
- ✅ Executive summary > 500 words
- ✅ At least 3 phases
- ✅ Context-specific (not generic)
- ✅ Integrates all pillar outputs

### POC Proposal Output
- ✅ Executive summary > 800 words
- ✅ Business case > 500 words
- ✅ Includes financial analysis (ROI, NPV, IRR)
- ✅ Context-specific (not generic)
- ✅ Integrates all pillar outputs

### Access Patterns (NEW)
- ✅ Orchestrators use four-tier pattern
- ✅ Enabling services use three-tier pattern
- ✅ Never return None silently
- ✅ All failures return structured errors

### No Placeholders (NEW)
- ✅ No placeholder text in responses
- ✅ No placeholder tokens
- ✅ No placeholder quality scores
- ✅ All data is real or properly error-handled

## Alignment with Production Readiness Fix Plan

This testing strategy directly supports the Production Readiness Fix Plan:

- **Phase 1 (Critical)**: Layer 8 (No Placeholder Tests) validates removal of all placeholders
- **Phase 2 (High Priority)**: Layer 7 (Access Pattern Tests) validates four-tier/three-tier patterns
- **Phase 3 (Configuration)**: Layer 10 (EC2 Deployment Tests) validates configuration correctness

## Troubleshooting

### Infrastructure Not Available

If tests fail with "infrastructure not available":
1. Ensure docker-compose containers are running
2. Check container health: `docker-compose -f tests/docker-compose.test.yml ps`
3. Verify ports are not in use: `netstat -tuln | grep -E '6379|8529|7700|8500'`

### Import Errors

If you see import errors:
1. Ensure you're running from project root: `cd /home/founders/demoversion/symphainy_source`
2. Check Python path includes symphainy-platform
3. Verify dependencies are installed: `pip install -r requirements.txt`

## Next Steps

1. **Complete Layer 7 tests** - Access pattern validation (CRITICAL)
2. **Complete Layer 8 tests** - No placeholder validation (CRITICAL)
3. **Complete Layer 9 tests** - Graceful failure validation (HIGH)
4. **Complete Layer 1 tests** - Real infrastructure adapter tests
5. **Complete Layer 2 tests** - Abstraction exposure tests
6. **Run critical tests** - Validate roadmap/POC outputs are impressive

## References

- [Bottom-Up Testing Strategy](../../docs/11-12/BOTTOMS_UP_TESTING_STRATEGY.md)
- [Production Readiness Fix Plan](../../docs/11-12/PRODUCTION_READINESS_FIX_PLAN.md)
- [Platform Patterns](../../docs/11-12/PLATFORM_WIDE_PATTERNS_AND_LESSONS_LEARNED.md)
