"""
E2E Test Configuration and Fixtures

Provides fixtures for starting/stopping the backend server for E2E tests.
"""

import pytest
import subprocess
import time
import httpx
import os
import signal
import sys
from typing import Optional, Generator
import logging

logger = logging.getLogger(__name__)

# Configuration
BACKEND_PORT = int(os.getenv("TEST_BACKEND_PORT", "8000"))
BACKEND_HOST = os.getenv("TEST_BACKEND_HOST", "localhost")
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
BACKEND_STARTUP_TIMEOUT = int(os.getenv("TEST_BACKEND_STARTUP_TIMEOUT", "120"))  # 2 minutes
BACKEND_HEALTH_CHECK_INTERVAL = 2  # Check every 2 seconds

# Path to backend main.py
BACKEND_MAIN_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "symphainy-platform",
    "main.py"
)

# Frontend configuration
FRONTEND_PORT = int(os.getenv("TEST_FRONTEND_PORT", "3000"))
FRONTEND_HOST = os.getenv("TEST_FRONTEND_HOST", "localhost")
FRONTEND_URL = f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"
FRONTEND_STARTUP_TIMEOUT = int(os.getenv("TEST_FRONTEND_STARTUP_TIMEOUT", "60"))  # 1 minute
FRONTEND_HEALTH_CHECK_INTERVAL = 2  # Check every 2 seconds

# Path to frontend directory
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "symphainy-frontend"
)


@pytest.fixture(scope="session")
def backend_server() -> Generator[None, None, None]:
    """
    Fixture that starts the backend server before tests and stops it after.
    
    This fixture:
    1. Starts the backend server in a subprocess
    2. Waits for it to be healthy (health check passes)
    3. Yields control to tests
    4. Stops the server after all tests complete
    
    Usage:
        @pytest.mark.asyncio
        async def test_something(backend_server):
            # Server is running and ready
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BACKEND_URL}/health")
                assert response.status_code == 200
    """
    server_process: Optional[subprocess.Popen] = None
    
    try:
        logger.info(f"🚀 Starting backend server on {BACKEND_URL}...")
        
        # Check if server is already running
        if _is_server_running():
            logger.info(f"✅ Backend server already running on {BACKEND_URL}")
            yield
            return
        
        # Start backend server
        server_process = _start_backend_server()
        
        # Wait for server to be ready
        if not _wait_for_server_ready():
            # Check if we should skip tests or fail
            skip_on_failure = os.getenv("TEST_SKIP_IF_SERVER_DOWN", "false").lower() == "true"
            if skip_on_failure:
                pytest.skip(
                    f"Backend server not available - skipping E2E tests. "
                    f"Start server manually or set TEST_SKIP_IF_SERVER_DOWN=false to fail tests."
                )
            else:
                raise RuntimeError(
                    f"Backend server failed to start within {BACKEND_STARTUP_TIMEOUT} seconds. "
                    f"Check logs at tests/e2e/backend_server.log for errors. "
                    f"Ensure infrastructure (Redis, ArangoDB) is running."
                )
        
        logger.info(f"✅ Backend server ready at {BACKEND_URL}")
        
        # Yield control to tests
        yield
        
    except Exception as e:
        logger.error(f"❌ Backend server fixture error: {e}")
        raise
    finally:
        # Stop server
        if server_process:
            logger.info("🛑 Stopping backend server...")
            _stop_backend_server(server_process)
            logger.info("✅ Backend server stopped")


def _start_backend_server() -> subprocess.Popen:
    """Start the backend server in a subprocess."""
    try:
        # Change to backend directory
        backend_dir = os.path.dirname(BACKEND_MAIN_PATH)
        
        # Create log file for server output
        log_file_path = os.path.join(os.path.dirname(__file__), "backend_server.log")
        log_file = open(log_file_path, "w")
        
        # Start server process
        process = subprocess.Popen(
            [sys.executable, "main.py", "--port", str(BACKEND_PORT), "--host", "0.0.0.0"],
            cwd=backend_dir,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        logger.info(f"✅ Backend server process started (PID: {process.pid})")
        logger.info(f"📝 Server logs: {log_file_path}")
        return process
        
    except Exception as e:
        logger.error(f"❌ Failed to start backend server: {e}")
        raise


def _stop_backend_server(process: subprocess.Popen) -> None:
    """Stop the backend server process."""
    try:
        # Try graceful shutdown first
        process.terminate()
        
        # Wait up to 10 seconds for graceful shutdown
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown fails
            logger.warning("⚠️ Server didn't stop gracefully, forcing kill...")
            process.kill()
            process.wait()
        
        logger.info("✅ Backend server process stopped")
        
    except Exception as e:
        logger.error(f"❌ Error stopping backend server: {e}")


def _is_server_running() -> bool:
    """Check if the backend server is already running."""
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _wait_for_server_ready() -> bool:
    """
    Wait for the backend server to be ready by checking health endpoint.
    
    Returns:
        True if server is ready, False if timeout
    """
    start_time = time.time()
    elapsed = 0
    
    logger.info(f"⏳ Waiting for backend server to be ready (timeout: {BACKEND_STARTUP_TIMEOUT}s)...")
    logger.info(f"💡 Tip: If server fails to start, check logs at tests/e2e/backend_server.log")
    
    while elapsed < BACKEND_STARTUP_TIMEOUT:
        try:
            response = httpx.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Backend server is ready! (took {elapsed:.1f}s)")
                return True
        except httpx.ConnectError:
            # Server not ready yet, continue waiting
            if elapsed % 10 == 0:  # Log every 10 seconds
                logger.info(f"⏳ Still waiting... ({elapsed:.0f}s / {BACKEND_STARTUP_TIMEOUT}s)")
                logger.info(f"   (Server may need infrastructure - Redis, ArangoDB, etc.)")
        except Exception as e:
            # Other errors - log but continue
            if elapsed % 10 == 0:
                logger.debug(f"Health check error: {e}")
        
        time.sleep(BACKEND_HEALTH_CHECK_INTERVAL)
        elapsed = time.time() - start_time
    
    logger.error(f"❌ Backend server failed to start within {BACKEND_STARTUP_TIMEOUT} seconds")
    log_file_path = os.path.join(os.path.dirname(__file__), "backend_server.log")
    if os.path.exists(log_file_path):
        logger.error(f"📝 Check server logs: {log_file_path}")
        # Show last 20 lines of log
        try:
            with open(log_file_path, "r") as f:
                lines = f.readlines()
                if lines:
                    logger.error("Last 20 lines of server log:")
                    for line in lines[-20:]:
                        logger.error(f"   {line.rstrip()}")
        except Exception:
            pass
    return False


@pytest.fixture
def backend_url() -> str:
    """Fixture that provides the backend URL."""
    return BACKEND_URL


@pytest.fixture
async def http_client():
    """Fixture that provides an async HTTP client for tests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
def frontend_server(request) -> Generator[None, None, None]:
    """
    Fixture that starts the frontend server before tests and stops it after.
    
    This fixture:
    1. Starts the frontend server in a subprocess
    2. Waits for it to be healthy (responds to HTTP requests)
    3. Yields control to tests
    4. Stops the server after all tests complete
    
    Usage:
        @pytest.mark.asyncio
        async def test_something(frontend_server):
            # Frontend is running and ready
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{FRONTEND_URL}")
                assert response.status_code == 200
    """
    server_process: Optional[subprocess.Popen] = None
    
    try:
        logger.info(f"🚀 Starting frontend server on {FRONTEND_URL}...")
        
        # Check if server is already running
        if _is_frontend_running():
            logger.info(f"✅ Frontend server already running on {FRONTEND_URL}")
            yield
            return
        
        # Start frontend server
        server_process = _start_frontend_server()
        
        # Wait for server to be ready
        if not _wait_for_frontend_ready():
            skip_on_failure = os.getenv("TEST_SKIP_IF_SERVER_DOWN", "false").lower() == "true"
            if skip_on_failure:
                pytest.skip(
                    f"Frontend server not available - skipping E2E tests. "
                    f"Start server manually or set TEST_SKIP_IF_SERVER_DOWN=false to fail tests."
                )
            else:
                raise RuntimeError(
                    f"Frontend server failed to start within {FRONTEND_STARTUP_TIMEOUT} seconds. "
                    f"Check logs at tests/e2e/frontend_server.log for errors."
                )
        
        logger.info(f"✅ Frontend server ready at {FRONTEND_URL}")
        
        # Yield control to tests
        yield
        
    except Exception as e:
        logger.error(f"❌ Frontend server fixture error: {e}")
        raise
    finally:
        # Stop server
        if server_process:
            logger.info("🛑 Stopping frontend server...")
            _stop_frontend_server(server_process)
            logger.info("✅ Frontend server stopped")


def _start_frontend_server() -> subprocess.Popen:
    """Start the frontend server in a subprocess."""
    try:
        # Check if npm/node is available
        import shutil
        npm_path = shutil.which("npm")
        if not npm_path:
            raise RuntimeError("npm not found in PATH. Please install Node.js and npm.")
        
        # Create log file for server output
        log_file_path = os.path.join(os.path.dirname(__file__), "frontend_server.log")
        log_file = open(log_file_path, "w")
        
        # Start server process (use 'dev' for development, 'start' for production)
        # Check if we should use production build
        use_production = os.getenv("TEST_FRONTEND_PRODUCTION", "false").lower() == "true"
        npm_command = "start" if use_production else "dev"
        
        process = subprocess.Popen(
            [npm_path, "run", npm_command],
            cwd=FRONTEND_DIR,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env={**os.environ, "PORT": str(FRONTEND_PORT)}
        )
        
        logger.info(f"✅ Frontend server process started (PID: {process.pid}, command: npm run {npm_command})")
        logger.info(f"📝 Server logs: {log_file_path}")
        return process
        
    except Exception as e:
        logger.error(f"❌ Failed to start frontend server: {e}")
        raise


def _stop_frontend_server(process: subprocess.Popen) -> None:
    """Stop the frontend server process."""
    try:
        # Try graceful shutdown first
        process.terminate()
        
        # Wait up to 10 seconds for graceful shutdown
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            # Force kill if graceful shutdown fails
            logger.warning("⚠️ Frontend server didn't stop gracefully, forcing kill...")
            process.kill()
            process.wait()
        
        logger.info("✅ Frontend server process stopped")
        
    except Exception as e:
        logger.error(f"❌ Error stopping frontend server: {e}")


def _is_frontend_running() -> bool:
    """Check if the frontend server is already running."""
    try:
        response = httpx.get(FRONTEND_URL, timeout=2, follow_redirects=True)
        return response.status_code in [200, 301, 302]  # Accept redirects
    except Exception:
        return False


def _wait_for_frontend_ready() -> bool:
    """
    Wait for the frontend server to be ready by checking HTTP endpoint.
    
    Returns:
        True if server is ready, False if timeout
    """
    start_time = time.time()
    elapsed = 0
    
    logger.info(f"⏳ Waiting for frontend server to be ready (timeout: {FRONTEND_STARTUP_TIMEOUT}s)...")
    logger.info(f"💡 Tip: If server fails to start, check logs at tests/e2e/frontend_server.log")
    
    while elapsed < FRONTEND_STARTUP_TIMEOUT:
        try:
            response = httpx.get(FRONTEND_URL, timeout=5, follow_redirects=True)
            if response.status_code in [200, 301, 302]:
                logger.info(f"✅ Frontend server is ready! (took {elapsed:.1f}s)")
                return True
        except httpx.ConnectError:
            # Server not ready yet, continue waiting
            if elapsed % 10 == 0:  # Log every 10 seconds
                logger.info(f"⏳ Still waiting... ({elapsed:.0f}s / {FRONTEND_STARTUP_TIMEOUT}s)")
        except Exception as e:
            # Other errors - log but continue
            if elapsed % 10 == 0:
                logger.debug(f"Frontend health check error: {e}")
        
        time.sleep(FRONTEND_HEALTH_CHECK_INTERVAL)
        elapsed = time.time() - start_time
    
    logger.error(f"❌ Frontend server failed to start within {FRONTEND_STARTUP_TIMEOUT} seconds")
    log_file_path = os.path.join(os.path.dirname(__file__), "frontend_server.log")
    if os.path.exists(log_file_path):
        logger.error(f"📝 Check server logs: {log_file_path}")
        # Show last 20 lines of log
        try:
            with open(log_file_path, "r") as f:
                lines = f.readlines()
                if lines:
                    logger.error("Last 20 lines of server log:")
                    for line in lines[-20:]:
                        logger.error(f"   {line.rstrip()}")
        except Exception:
            pass
    return False


@pytest.fixture(scope="session")
def both_servers(backend_server, frontend_server):
    """
    Combined fixture that starts both backend and frontend servers.
    
    Use this for Playwright E2E tests that need both servers running.
    
    Usage:
        from playwright.async_api import async_playwright
        
        @pytest.mark.asyncio
        async def test_with_playwright(both_servers):
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(FRONTEND_URL)
                # ... test code ...
    """
    # Both servers are started by their respective fixtures
    # This fixture just ensures both are available
    yield


@pytest.fixture
def frontend_url() -> str:
    """Fixture that provides the frontend URL."""
    return FRONTEND_URL

