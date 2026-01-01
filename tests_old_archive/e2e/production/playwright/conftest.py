"""
Shared fixtures for Playwright E2E tests.
"""

import pytest
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import os
import logging

logger = logging.getLogger(__name__)

# Note: backend_server and frontend_server fixtures are available from parent conftest
# via pytest's fixture discovery

FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
async def browser() -> Browser:
    """Launch browser for Playwright tests."""
    async with async_playwright() as p:
        # Use headless mode by default, can be overridden with HEADED=true
        headless = os.getenv("HEADED", "false").lower() != "true"
        browser = await p.chromium.launch(headless=headless)
        logger.info(f"🌐 Browser launched (headless={headless})")
        yield browser
        await browser.close()
        logger.info("🌐 Browser closed")


@pytest.fixture
async def page(browser: Browser) -> Page:
    """Create new page for each test."""
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True
    )
    page = await context.new_page()
    
    # Set up console logging
    def handle_console(msg):
        if msg.type == "error":
            logger.warning(f"Browser console error: {msg.text}")
    
    page.on("console", handle_console)
    
    yield page
    
    await context.close()


@pytest.fixture(scope="session")
async def both_servers():
    """Ensure both backend and frontend servers are running."""
    # This fixture is available from tests.e2e.conftest
    # We just need to ensure it's used
    yield

