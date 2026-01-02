# Embedding Tests Configuration Guide

## Overview

This document describes how to configure and run the embedding/data mash tests for the Content Pillar.

## Environment Variables Required

### For Embedding Creation Tests

The embedding creation tests require HuggingFace configuration:

```bash
export TEST_HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
export TEST_HUGGINGFACE_EMBEDDINGS_API_KEY="your_huggingface_api_key"
```

Or use the non-prefixed versions (will be picked up automatically):
```bash
export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
export HUGGINGFACE_EMBEDDINGS_API_KEY="your_huggingface_api_key"
```

### For Semantic Layer Tests

The semantic layer tests require ArangoDB configuration:

```bash
export TEST_ARANGO_URL="http://localhost:8529"
export TEST_ARANGO_DB="symphainy_test"
export TEST_ARANGO_USER="root"
export TEST_ARANGO_PASS="your_arango_password"
```

### For Complete E2E Tests

E2E tests require all of the above plus:
- Supabase configuration (for file upload/parsing)
- API URL (for backend endpoint)

```bash
export TEST_API_URL="http://localhost:8000"  # or your backend URL
export TEST_SUPABASE_URL="your_supabase_url"
export TEST_SUPABASE_ANON_KEY="your_supabase_anon_key"
```

## Test Markers

The following markers are available for filtering tests:

- `@pytest.mark.embedding` - All embedding-related tests
- `@pytest.mark.data_mash` - Data mash workflow tests
- `@pytest.mark.semantic_layer` - Semantic layer tests

## Running Tests

### Run All Embedding Tests
```bash
cd /home/founders/demoversion/symphainy_source/tests
pytest -m "embedding" -v
```

### Run Unit Tests Only
```bash
pytest tests/unit/content/test_embedding*.py -v
```

### Run Integration Tests Only
```bash
pytest tests/integration/pillar/test_content_pillar_integration.py::TestContentPillarIntegration::test_embedding_workflow_integration -v
```

### Run E2E Tests Only
```bash
pytest tests/e2e/production/pillar_validation/test_content_pillar_e2e.py -m "embedding" -v
```

### Run with Real Infrastructure
```bash
TEST_USE_REAL_INFRASTRUCTURE=true pytest -m "embedding" -v
```

### Skip Tests if Infrastructure Missing
Tests will automatically skip if required infrastructure is not configured (via `skip_if_missing_real_infrastructure` helper).

## Test Files

### Unit Tests
- `tests/unit/content/test_embedding_creation.py` - Embedding creation unit tests
- `tests/unit/content/test_embedding_preview.py` - Embedding preview unit tests
- `tests/unit/content/test_embedding_listing.py` - Embedding listing unit tests

### Integration Tests
- `tests/integration/pillar/test_content_pillar_integration.py` - Contains embedding workflow integration tests

### E2E Tests
- `tests/e2e/production/pillar_validation/test_content_pillar_e2e.py` - Contains embedding E2E tests

## Test Coverage

### What's Tested
- ✅ Embedding creation from parsed files
- ✅ Embedding preview (semantic layer reconstruction)
- ✅ Embedding listing (all and filtered by file_id)
- ✅ Parsed files with embeddings listing
- ✅ Error handling (missing files, missing config, etc.)
- ✅ Lineage tracking during embedding creation
- ✅ Workflow ID propagation
- ✅ Solution context integration
- ✅ Complete E2E workflow (upload → parse → embed → preview)

### What's Not Tested (Yet)
- Performance/load testing for embedding creation
- Large file embedding creation (>10k rows)
- Embedding update/delete operations
- Embedding versioning

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'config.test_config'`, ensure you're running from the tests directory:
```bash
cd /home/founders/demoversion/symphainy_source/tests
pytest ...
```

### Missing Infrastructure
If tests skip with "Real infrastructure not available", check:
1. Environment variables are set correctly
2. Environment variables are exported (not just set)
3. Check `TestConfig.get_missing_infrastructure()` output

### HuggingFace Rate Limiting
If you encounter rate limiting errors:
- Use a HuggingFace Pro account for higher rate limits
- Add delays between test runs
- Use mock LLM for unit tests: `TEST_USE_MOCK_LLM=true`

### ArangoDB Connection Issues
If ArangoDB connection fails:
- Ensure ArangoDB is running: `docker ps | grep arango`
- Check connection string format
- Verify credentials are correct




