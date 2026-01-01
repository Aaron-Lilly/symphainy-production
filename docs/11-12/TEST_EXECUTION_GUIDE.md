# Test Execution Guide - Self-Service Testing

**Goal**: Run and troubleshoot tests without heavy Cursor agent usage (saves Cursor tokens)

---

## 🎯 Quick Reference

### Run Tests (No Cursor Agent Needed)

```bash
# Fast tests only (< 30 seconds)
cd tests && python3 run_tests.py --fast

# Unit tests only (< 2 minutes)
cd tests && python3 run_tests.py --unit

# Specific test file
cd tests && pytest unit/foundations/test_di_container.py -v

# Specific test function
cd tests && pytest unit/foundations/test_di_container.py::TestDIContainerService::test_initialization -v

# Last failed tests only
cd tests && pytest --lf -v
```

### Troubleshoot Failures (Minimal Cursor Usage)

1. **Read the error message** (usually tells you what's wrong)
2. **Check the traceback** (shows where it failed)
3. **Run just that test** (isolate the issue)
4. **Check test documentation** (see below)

---

## 📋 Test Execution Strategies

### Strategy 1: Incremental Testing (Recommended)

**Don't run all tests at once!**

```bash
# Step 1: Run fast tests first (30 seconds)
python3 run_tests.py --fast

# Step 2: If fast tests pass, run unit tests (2 minutes)
python3 run_tests.py --unit

# Step 3: If unit tests pass, run integration tests (5 minutes)
python3 run_tests.py --integration

# Step 4: Only run E2E tests when everything else passes (10+ minutes)
python3 run_tests.py --e2e
```

**Why**: Catches issues early, faster feedback, less Cursor analysis needed

### Strategy 2: Targeted Testing

**Run tests for what you changed**

```bash
# Changed Content Orchestrator?
pytest tests/business_enablement/orchestrators/test_content_analysis_orchestrator.py -v

# Changed MCP Server?
pytest tests/unit/mcp_servers/ -v

# Changed enabling service?
pytest tests/unit/enabling_services/test_file_parser_service.py -v
```

**Why**: Faster, focused, easier to debug

### Strategy 3: Failure-First Testing

**Only run what failed before**

```bash
# Run only last failed tests
pytest --lf -v

# Run failed tests + related tests
pytest --ff -v  # Failed first, then others
```

**Why**: Fix issues incrementally, don't re-run passing tests

---

## 🔍 Troubleshooting Guide (Self-Service)

### Common Error Patterns

#### 1. Import Errors

**Error**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```bash
# Check if you're in the right directory
pwd  # Should be in project root or tests/

# Check Python path
python3 -c "import sys; print(sys.path)"

# Try running from project root
cd /home/founders/demoversion/symphainy_source
python3 -m pytest tests/unit/foundations/test_di_container.py
```

#### 2. Async Errors

**Error**: `RuntimeError: Event loop is closed` or `coroutine was never awaited`

**Solution**:
- Tests should use `@pytest.mark.asyncio`
- Check if fixture is async: `async def fixture_name()`
- Check if test is async: `async def test_name()`

#### 3. Mock Not Working

**Error**: Test calls real service instead of mock

**Solution**:
```python
# Make sure mock is injected before service initialization
@pytest.fixture
async def service_with_mock(mock_dependency):
    service = MyService()
    service.dependency = mock_dependency  # Inject BEFORE initialize()
    await service.initialize()
    return service
```

#### 4. Test Timeout

**Error**: Test hangs or times out

**Solution**:
```bash
# Run with timeout
pytest --timeout=30 tests/path/to/test.py

# Or add to test
@pytest.mark.timeout(30)
async def test_something():
    pass
```

### Debugging Workflow

**Step 1: Isolate the Failure**
```bash
# Run just the failing test
pytest tests/path/to/test.py::TestClass::test_method -v -s
```

**Step 2: Read the Error**
- **First line**: Usually tells you what failed
- **Traceback**: Shows where it failed
- **Last line**: Usually the root cause

**Step 3: Check Test Documentation**
- Look for test docstring
- Check if test has known issues
- Review test comments

**Step 4: Check Related Code**
- Read the code being tested
- Check if code changed recently
- Look for similar tests that pass

**Step 5: Add Debug Output** (if needed)
```python
async def test_something():
    result = await service.do_something()
    print(f"DEBUG: result = {result}")  # Add temporary debug
    assert result["success"] is True
```

**Step 6: Run with Verbose Output**
```bash
pytest -vv -s tests/path/to/test.py  # Very verbose + show prints
```

---

## 🛠️ Test Automation (Reduce Cursor Usage)

### Pre-Commit Hook (Run Tests Before Committing)

**Create `.git/hooks/pre-commit`**:
```bash
#!/bin/bash
# Run fast tests before commit
cd /home/founders/demoversion/symphainy_source/tests
python3 run_tests.py --fast
if [ $? -ne 0 ]; then
    echo "Fast tests failed! Fix before committing."
    exit 1
fi
```

**Why**: Catch issues before commit, less Cursor troubleshooting needed

### Test Scripts (Common Scenarios)

**Create `tests/scripts/quick_check.sh`**:
```bash
#!/bin/bash
# Quick test check (30 seconds)
cd /home/founders/demoversion/symphainy_source/tests
python3 run_tests.py --fast --verbose
```

**Create `tests/scripts/test_changed.sh`**:
```bash
#!/bin/bash
# Test only changed files
git diff --name-only HEAD | grep -E '\.py$' | while read file; do
    test_file="tests/$(echo $file | sed 's|symphainy-platform/||')"
    if [ -f "$test_file" ]; then
        pytest "$test_file" -v
    fi
done
```

---

## 📊 Test Output Interpretation

### Understanding Test Results

**✅ PASS**: Test passed, no action needed

**❌ FAIL**: Test failed
- Read error message
- Check traceback
- Look for assertion that failed

**⚠️ SKIP**: Test was skipped
- Check skip reason: `@pytest.mark.skip(reason="...")`
- Usually means dependency not available

**⏱️ SLOW**: Test took > 5 seconds
- Consider optimizing
- May indicate real API calls (check for mocks)

### Test Summary Reading

```
tests/unit/test_service.py::TestService::test_method PASSED    [ 10%]
tests/unit/test_service.py::TestService::test_other FAILED     [ 20%]
tests/integration/test_integration.py::TestIntegration SKIPPED  [ 30%]

========================= 1 failed, 1 passed, 1 skipped in 2.34s =========================
```

**What this tells you**:
- 1 test passed ✅
- 1 test failed ❌ (needs fixing)
- 1 test skipped ⚠️ (dependency missing)
- Total time: 2.34 seconds

---

## 🎓 Learning Path (Minimal Cursor Usage)

### Level 1: Run Tests (5 minutes)

**Goal**: Run tests without Cursor agent

```bash
# Learn these commands:
python3 run_tests.py --fast        # Fast tests
python3 run_tests.py --unit        # Unit tests
pytest tests/path/to/test.py -v    # Specific test
pytest --lf                        # Last failed
```

**When to use Cursor**: Only if you can't figure out the error after reading it

### Level 2: Read Test Failures (10 minutes)

**Goal**: Understand what failed without Cursor analysis

1. **Read the error message** (first line usually tells you)
2. **Check the traceback** (shows where it failed)
3. **Look at the assertion** (what was expected vs actual)

**Example**:
```
AssertionError: assert result["success"] is True
```
**Translation**: Test expected `result["success"]` to be `True`, but it wasn't

**When to use Cursor**: Only if error message is unclear

### Level 3: Fix Simple Issues (30 minutes)

**Goal**: Fix common issues without Cursor

**Common fixes**:
- Import errors → Fix import path
- Mock not working → Inject mock before initialization
- Async errors → Add `@pytest.mark.asyncio`
- Assertion failures → Check what value was returned

**When to use Cursor**: Only for complex architectural issues

---

## 🚀 Recommended Workflow

### Daily Development

1. **Before coding**: Run fast tests (30 seconds)
   ```bash
   python3 run_tests.py --fast
   ```

2. **After changes**: Run relevant tests (2 minutes)
   ```bash
   pytest tests/business_enablement/orchestrators/test_content_analysis_orchestrator.py -v
   ```

3. **Before commit**: Run unit tests (5 minutes)
   ```bash
   python3 run_tests.py --unit
   ```

4. **Only use Cursor agent**: For complex failures you can't understand

### When Tests Fail

1. **Read the error** (30 seconds)
2. **Run just that test** (10 seconds)
   ```bash
   pytest tests/path/to/test.py::TestClass::test_method -v
   ```
3. **Check test documentation** (1 minute)
4. **Try simple fix** (5 minutes)
5. **If still stuck**: Use Cursor agent (but with specific question, not "fix all tests")

---

## 💡 Pro Tips

### Tip 1: Use Test Markers

```bash
# Run only fast tests
pytest -m "fast"

# Run only unit tests
pytest -m "unit"

# Skip slow tests
pytest -m "not slow"
```

### Tip 2: Use Test Output

```bash
# Show print statements
pytest -s

# Very verbose
pytest -vv

# Show local variables on failure
pytest -l
```

### Tip 3: Use Test Caching

```bash
# Cache test results (faster reruns)
pytest --cache-clear  # Clear cache
pytest --cache-show   # Show cache
```

### Tip 4: Parallel Execution

```bash
# Run tests in parallel (faster)
pytest -n auto  # Auto-detect CPU cores
pytest -n 4     # Use 4 workers
```

### Tip 5: Stop on First Failure

```bash
# Stop after first failure (faster feedback)
pytest -x

# Stop after N failures
pytest --maxfail=3
```

---

## 🔧 Test Maintenance (Reduce Future Cursor Usage)

### Keep Tests Simple

**❌ BAD**: Complex test that's hard to debug
```python
async def test_complex_flow():
    # 50 lines of setup
    # 30 lines of execution
    # 20 lines of assertions
    # Hard to debug when it fails
```

**✅ GOOD**: Simple, focused test
```python
async def test_parse_file_returns_content():
    """Test file parser returns content in result."""
    result = await parser.parse_file("test.pdf")
    assert result["success"] is True
    assert "content" in result
```

### Add Clear Error Messages

**❌ BAD**: Generic assertion
```python
assert result
```

**✅ GOOD**: Specific assertion with message
```python
assert result["success"] is True, f"Expected success=True, got {result}"
assert "content" in result, f"Expected 'content' key, got keys: {list(result.keys())}"
```

### Document Known Issues

```python
@pytest.mark.skip(reason="Requires real database - use integration test")
async def test_requires_database():
    pass

@pytest.mark.xfail(reason="Known issue: Mock not working for this case")
async def test_known_issue():
    pass
```

---

## 📚 Test Documentation

### Test File Structure

Each test file should have:
1. **Docstring**: What is being tested
2. **Test class docstring**: What the class tests
3. **Test method docstring**: What the specific test verifies

```python
"""
Content Analysis Orchestrator Tests

Tests for the Content Analysis Orchestrator that composes enabling services.
"""

class TestContentAnalysisOrchestrator:
    """Test Content Analysis Orchestrator functionality."""
    
    async def test_parse_file_returns_content(self, orchestrator):
        """Test that parse_file returns content in result.
        
        Verifies:
        - parse_file() returns success=True
        - Result contains 'content' key
        - Content is not empty
        """
        result = await orchestrator.parse_file("test.pdf")
        assert result["success"] is True
        assert "content" in result
        assert len(result["content"]) > 0
```

---

## 🎯 Cursor Usage Optimization

### When to Use Cursor Agent

**✅ GOOD**: Use Cursor for:
- Complex architectural questions
- Understanding new code patterns
- Fixing non-obvious bugs
- Code generation (not test execution)

**❌ BAD**: Don't use Cursor for:
- Running tests (use command line)
- Reading error messages (read them yourself)
- Simple fixes (try yourself first)
- Test execution troubleshooting (use this guide)

### Efficient Cursor Queries

**❌ BAD**: "Fix all test failures"
- Too broad, expensive, hard to follow

**✅ GOOD**: "This test is failing with 'ModuleNotFoundError: X'. The import path should be Y based on the new architecture. Can you fix the import?"
- Specific, focused, cheaper

**❌ BAD**: "Why are tests slow?"
- Requires analysis of all tests

**✅ GOOD**: "This specific test takes 30 seconds. It's in tests/unit/test_X.py::test_method. Can you check if it's making real API calls?"
- Specific, actionable, cheaper

---

## 📋 Quick Reference Card

### Run Tests
```bash
python3 run_tests.py --fast      # Fast tests (30s)
python3 run_tests.py --unit      # Unit tests (2m)
pytest tests/path/to/test.py -v  # Specific test
pytest --lf                      # Last failed
```

### Debug Failures
1. Read error message
2. Run just that test: `pytest tests/path/to/test.py::TestClass::test_method -v`
3. Check traceback
4. Try simple fix
5. Use Cursor only if stuck

### Common Commands
```bash
pytest -v          # Verbose
pytest -s          # Show prints
pytest -x          # Stop on first failure
pytest -n auto     # Parallel
pytest --timeout=30 # Timeout
```

---

## 🎓 Next Steps

1. **Try running tests yourself** (5 minutes)
   - Start with `python3 run_tests.py --fast`
   - Read any errors that appear

2. **Practice reading errors** (10 minutes)
   - Run a test that fails
   - Read the error message
   - Try to understand what it's saying

3. **Fix one simple issue** (30 minutes)
   - Pick an easy failure (import error, typo, etc.)
   - Fix it yourself
   - Run test again to verify

4. **Use Cursor only when needed**
   - After you've tried reading the error
   - After you've tried simple fixes
   - With a specific, focused question

---

## 💰 Cost Savings

**Before** (Heavy Cursor Usage):
- Run all tests with Cursor agent: ~$X per run
- Cursor analyzes failures: ~$Y per failure
- Multiple runs: Exponential costs

**After** (Self-Service):
- Run tests yourself: $0 (just your time)
- Read errors yourself: $0
- Use Cursor only for complex issues: ~$Z (much less)

**Expected Savings**: 80-90% reduction in Cursor costs

---

## 🆘 When to Ask for Help

**Use Cursor agent when**:
- Error message is unclear after reading it
- You've tried simple fixes and they didn't work
- You need to understand a complex architectural pattern
- You need help with test structure/organization

**Don't use Cursor agent for**:
- Running tests (use command line)
- Reading error messages (read them yourself)
- Simple import/typo fixes (fix yourself)
- Test execution (use this guide)

---

## 📝 Summary

**Key Principle**: Run and debug tests yourself first, use Cursor only when stuck

**Workflow**:
1. Run tests yourself (`python3 run_tests.py --fast`)
2. Read errors yourself (they usually tell you what's wrong)
3. Try simple fixes yourself (imports, typos, mocks)
4. Use Cursor only for complex issues (with specific questions)

**Result**: 80-90% reduction in Cursor costs, faster feedback, better understanding

