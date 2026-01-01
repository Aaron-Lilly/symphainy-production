#!/usr/bin/env python3
"""
Playwright E2E Test Configuration

Browser-based end-to-end testing with Playwright.

WHAT (Playwright Test Role): I provide browser-based E2E testing
HOW (Playwright Test Implementation): I set up Playwright fixtures and browser automation
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import AsyncGenerator


@pytest.fixture(scope="session")
async def browser() -> AsyncGenerator[Browser, None]:
    """Browser fixture for Playwright tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # Set to False for debugging
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu"
            ]
        )
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Browser context fixture."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Page fixture."""
    page = await context.new_page()
    
    # Set up console logging
    page.on("console", lambda msg: print(f"Browser Console: {msg.type} - {msg.text}"))
    page.on("pageerror", lambda error: print(f"Browser Error: {error}"))
    
    yield page
    await page.close()


@pytest.fixture
def base_url():
    """Base URL for the application."""
    return "http://localhost:8000"


@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "test_password_123"
    }


@pytest.fixture
def test_file_path():
    """Path to test file."""
    import os
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "tests", "e2e", "test_data", "sample.csv")


# Test data setup
@pytest.fixture(autouse=True)
async def setup_test_data(page: Page, test_file_path: str):
    """Setup test data before each test."""
    # Ensure test file exists
    import os
    if not os.path.exists(test_file_path):
        os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
        with open(test_file_path, 'w') as f:
            f.write("name,age,city\nJohn,25,New York\nJane,30,Los Angeles\nBob,35,Chicago")
    
    yield
    
    # Cleanup after test if needed
    pass





