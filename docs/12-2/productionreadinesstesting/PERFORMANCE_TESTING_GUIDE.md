# Performance Testing Guide

**Last Updated:** December 1, 2025  
**Version:** 2.0 (Post-Phase 1-4 Improvements)

---

## Overview

This guide explains how to write and run performance tests for the SymphAIny platform. Performance tests ensure the platform meets speed and scalability requirements.

---

## Performance Testing Types

### 1. Load Testing

**Purpose:** Test system under expected load

**Example:**
```python
# tests/performance/test_load.py
import pytest
import asyncio
import httpx
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.performance
@pytest.mark.load
async def test_api_under_load():
    """Test API handles expected load."""
    async with httpx.AsyncClient() as client:
        # Simulate 100 concurrent requests
        tasks = [
            client.get("http://localhost:8000/api/v1/health")
            for _ in range(100)
        ]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results)
        
        # Average response time < 500ms
        avg_time = sum(r.elapsed.total_seconds() for r in results) / len(results)
        assert avg_time < 0.5, f"Average response time too slow: {avg_time}s"
```

---

### 2. Stress Testing

**Purpose:** Test system limits

**Example:**
```python
@pytest.mark.performance
@pytest.mark.stress
async def test_api_stress():
    """Test API under stress conditions."""
    async with httpx.AsyncClient() as client:
        # Simulate 1000 concurrent requests
        tasks = [
            client.get("http://localhost:8000/api/v1/health")
            for _ in range(1000)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # At least 90% should succeed
        successes = sum(1 for r in results if not isinstance(r, Exception))
        success_rate = successes / len(results)
        assert success_rate >= 0.9, f"Success rate too low: {success_rate}"
```

---

### 3. Benchmark Testing

**Purpose:** Measure and track performance over time

**Example:**
```python
# tests/performance/test_benchmarks.py
import pytest
import time
from symphainy_platform.backend.feature import FeatureService

@pytest.mark.performance
@pytest.mark.benchmark
def test_feature_benchmark(benchmark):
    """Benchmark feature performance."""
    service = FeatureService()
    
    def process_data():
        return service.process({"key": "value"})
    
    result = benchmark(process_data)
    assert result["processed"] is True
```

**Run with pytest-benchmark:**
```bash
pytest tests/performance/test_benchmarks.py --benchmark-only
```

---

### 4. Response Time Testing

**Purpose:** Ensure response times meet requirements

**Example:**
```python
@pytest.mark.performance
async def test_api_response_time():
    """Test API response time requirements."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        start = time.time()
        response = await client.get("http://localhost:8000/api/v1/endpoint")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0, f"Response time too slow: {elapsed}s"
```

---

## Performance Test Structure

### Directory Structure

```
tests/
└── performance/
    ├── test_load.py          # Load tests
    ├── test_stress.py        # Stress tests
    ├── test_benchmarks.py    # Benchmark tests
    └── conftest.py           # Performance test fixtures
```

### Test Markers

```python
@pytest.mark.performance      # All performance tests
@pytest.mark.load             # Load tests
@pytest.mark.stress           # Stress tests
@pytest.mark.benchmark        # Benchmark tests
@pytest.mark.slow             # Slow tests (run separately)
```

---

## Performance Requirements

### API Endpoints

| Endpoint Type | Max Response Time | Throughput |
|--------------|-------------------|------------|
| Health Check | 100ms | 1000 req/s |
| Read Operations | 500ms | 100 req/s |
| Write Operations | 1000ms | 50 req/s |
| Complex Queries | 2000ms | 10 req/s |

### Database Operations

| Operation | Max Time |
|----------|----------|
| Simple Query | 100ms |
| Complex Query | 500ms |
| Write Operation | 200ms |
| Batch Operation | 1000ms |

### Frontend

| Metric | Target |
|--------|--------|
| Page Load | < 2s |
| Time to Interactive | < 3s |
| First Contentful Paint | < 1s |

---

## Running Performance Tests

### Locally

```bash
# Run all performance tests
pytest tests/performance/ -v -m performance

# Run load tests only
pytest tests/performance/ -v -m load

# Run benchmarks
pytest tests/performance/ -v -m benchmark --benchmark-only

# Run with detailed output
pytest tests/performance/ -v -m performance --durations=10
```

### In CI/CD

Performance tests run as part of the quality gates:

```yaml
- name: Run performance benchmarks
  run: |
    pytest tests/performance/ -v --benchmark-only
```

**Note:** Performance tests are non-blocking in CI/CD (warnings only).

---

## Performance Monitoring

### Metrics to Track

1. **Response Time**
   - Average
   - Median
   - 95th percentile
   - 99th percentile

2. **Throughput**
   - Requests per second
   - Transactions per second

3. **Resource Usage**
   - CPU usage
   - Memory usage
   - Database connections

4. **Error Rate**
   - Failed requests
   - Timeout rate

### Example Monitoring

```python
@pytest.mark.performance
async def test_api_with_monitoring():
    """Test API with performance monitoring."""
    import psutil
    import time
    
    process = psutil.Process()
    cpu_before = process.cpu_percent()
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    
    async with httpx.AsyncClient() as client:
        start = time.time()
        response = await client.get("http://localhost:8000/api/v1/endpoint")
        elapsed = time.time() - start
    
    cpu_after = process.cpu_percent()
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    
    # Assertions
    assert response.status_code == 200
    assert elapsed < 1.0
    assert (mem_after - mem_before) < 100  # Memory increase < 100MB
```

---

## Best Practices

### 1. Test Realistic Scenarios

**Don't:**
```python
# Unrealistic - all requests identical
for _ in range(100):
    client.get("/endpoint")
```

**Do:**
```python
# Realistic - varied requests
endpoints = ["/endpoint1", "/endpoint2", "/endpoint3"]
for _ in range(100):
    endpoint = random.choice(endpoints)
    client.get(endpoint)
```

### 2. Use Proper Test Data

**Don't:**
```python
# Too simple
data = {"key": "value"}
```

**Do:**
```python
# Realistic data
data = {
    "user_id": generate_user_id(),
    "timestamp": datetime.now().isoformat(),
    "payload": generate_realistic_payload()
}
```

### 3. Clean Up After Tests

```python
@pytest.fixture
async def cleanup_test_data():
    """Clean up test data after performance tests."""
    yield
    # Cleanup code
    await cleanup_performance_test_data()
```

### 4. Monitor Resource Usage

```python
@pytest.mark.performance
def test_memory_usage():
    """Test memory usage doesn't grow unbounded."""
    import tracemalloc
    
    tracemalloc.start()
    # Run operations
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    assert peak < 100 * 1024 * 1024  # < 100MB
```

---

## Performance Test Examples

### API Load Test

```python
@pytest.mark.performance
@pytest.mark.load
async def test_api_load():
    """Test API handles 100 concurrent requests."""
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get("http://localhost:8000/api/v1/health")
            for _ in range(100)
        ]
        results = await asyncio.gather(*tasks)
        
        # All succeed
        assert all(r.status_code == 200 for r in results)
        
        # Average < 500ms
        avg = sum(r.elapsed.total_seconds() for r in results) / len(results)
        assert avg < 0.5
```

### Database Performance Test

```python
@pytest.mark.performance
async def test_database_query_performance():
    """Test database query performance."""
    from symphainy_platform.backend.database import DatabaseService
    
    db = DatabaseService()
    
    start = time.time()
    results = await db.query("SELECT * FROM table WHERE condition = ?", [value])
    elapsed = time.time() - start
    
    assert len(results) > 0
    assert elapsed < 0.5  # Query < 500ms
```

### Frontend Performance Test

```python
@pytest.mark.performance
@pytest.mark.e2e
async def test_frontend_load_time():
    """Test frontend page load time."""
    async with httpx.AsyncClient() as client:
        start = time.time()
        response = await client.get("http://localhost:3000")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0  # Page load < 2s
```

---

## CI/CD Integration

### Performance Tests in Pipeline

Performance tests run as part of quality gates:

```yaml
- name: Run performance checks
  run: |
    pytest tests/performance/ -v --durations=10
```

**Status:** Non-blocking (warnings only)

### Performance Trends

Track performance over time:
- Store benchmark results
- Compare against baselines
- Alert on regressions

---

## Troubleshooting

### Tests Too Slow

**Optimize:**
- Use mocks for external services
- Reduce test data size
- Run tests in parallel

### Flaky Performance Tests

**Fix:**
- Add retries
- Increase timeouts
- Use more stable test data

### Resource Constraints

**Check:**
- Available memory
- CPU usage
- Network bandwidth

---

## Summary

**Performance Testing:**
- ✅ Load testing for expected load
- ✅ Stress testing for limits
- ✅ Benchmark testing for trends
- ✅ Response time validation

**Requirements:**
- ✅ API: < 500ms (read), < 1000ms (write)
- ✅ Database: < 500ms (queries)
- ✅ Frontend: < 2s (page load)

**CI/CD:**
- ✅ Runs in quality gates
- ✅ Non-blocking (warnings)
- ✅ Tracks trends over time

---

**Questions?** Contact the performance testing team.


