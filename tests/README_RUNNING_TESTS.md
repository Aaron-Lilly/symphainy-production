# Running Tests

## Quick Start

**Always run pytest from the `symphainy_source` directory (parent of `tests/`):**

```bash
cd /home/founders/demoversion/symphainy_source
python3 -m pytest tests/integration/smart_city/test_websocket_gateway_integration.py -v
```

## Why?

The `pytest.ini` file's `pythonpath` setting resolves paths relative to where pytest is run from. When you run pytest from the `symphainy_source` directory:

1. Pytest finds `tests/pytest.ini`
2. The `pythonpath` setting correctly resolves `../symphainy-platform` relative to the `tests/` directory
3. All imports work correctly

## Alternative: Run from tests/ directory

If you need to run from the `tests/` directory, the `conftest.py` file includes a fallback path setup that should work, but running from the parent directory is more reliable.

## Configuration

- **pytest.ini**: Configures Python path and test discovery
- **conftest.py**: Sets up Python path as fallback and provides shared fixtures
- **pytest_path_plugin.py**: Pytest plugin that ensures path is set early (additional fallback)

All three mechanisms work together to ensure imports work regardless of where pytest is run from.

