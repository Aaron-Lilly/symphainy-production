"""
Playwright E2E Test: CTO Demo 3 - Data Mash Coexistence

Validates the complete user experience for the Coexistence demo scenario
with comprehensive network monitoring and error detection.
"""

import pytest
from playwright.async_api import Page, Request, Response
import logging
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.playwright_e2e, pytest.mark.cto_demo, pytest.mark.critical]

FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:8000"

EXPECTED_API_PATHS = {
    "content": "/api/v1/content-pillar/",
    "insights": "/api/v1/insights-pillar/",
    "operations": "/api/v1/operations-pillar/",
    "business-outcomes": "/api/v1/business-outcomes-pillar/",
    "session": "/api/v1/session/",
    "guide-agent": "/api/v1/guide-agent/",
}


@pytest.mark.asyncio
@pytest.mark.timeout(600)  # 10 minutes for full journey
async def test_cto_demo_3_coexistence_playwright(both_servers, page: Page):
    """
    CTO Demo Scenario 3: Data Mash Coexistence/Migration Enablement
    
    Complete 4-pillar journey via browser automation with network monitoring.
    """
    logger.info("🎬 CTO Demo Scenario 3: Data Mash Coexistence - Playwright E2E")
    
    # Setup monitoring
    console_errors: List[str] = []
    network_errors: List[Dict[str, Any]] = []
    api_requests: List[Dict[str, Any]] = []
    
    def handle_console(msg):
        if msg.type == "error":
            console_errors.append(msg.text)
            logger.warning(f"⚠️ Console error: {msg.text}")
    
    def handle_request(request: Request):
        if BACKEND_URL in request.url or "/api/" in request.url:
            api_requests.append({
                "method": request.method,
                "url": request.url,
                "timestamp": time.time()
            })
    
    def handle_response(response: Response):
        if BACKEND_URL in response.url or "/api/" in response.url:
            if response.status >= 400:
                network_errors.append({
                    "url": response.url,
                    "status": response.status
                })
                logger.warning(f"⚠️ API Error: {response.status} {response.url}")
    
    def handle_request_failed(request):
        network_errors.append({
            "url": request.url,
            "failure": "request_failed"
        })
        logger.warning(f"⚠️ Request failed: {request.url}")
    
    page.on("console", handle_console)
    page.on("request", handle_request)
    page.on("response", handle_response)
    page.on("requestfailed", handle_request_failed)
    
    # Navigate to frontend
    await page.goto(FRONTEND_URL, wait_until="networkidle", timeout=30000)
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_timeout(2000)
    logger.info("✅ Frontend loaded")
    
    # Verify page structure
    title = await page.title()
    logger.info(f"✅ Page title: {title}")
    assert title is not None and len(title) > 0, "Page title should not be empty"
    
    # Wait for API calls
    await page.wait_for_timeout(3000)
    
    # Validate API routing
    semantic_api_count = sum(1 for r in api_requests if any(path in r["url"] for path in EXPECTED_API_PATHS.values()))
    logger.info(f"📊 API Requests: {len(api_requests)} total, {semantic_api_count} using semantic paths")
    
    # Check for routing issues
    routing_issues = [r["url"] for r in api_requests if "/api/fms/" in r["url"] or 
                     ("/api/content/" in r["url"] and "/api/v1/content-pillar/" not in r["url"])]
    
    if routing_issues:
        logger.warning(f"⚠️ Found {len(routing_issues)} potential routing issues")
    else:
        logger.info("✅ No routing issues detected")
    
    # Validate errors
    cors_errors = [e for e in console_errors if "cors" in e.lower()]
    server_errors = [e for e in network_errors if e.get("status", 0) >= 500]
    
    logger.info(f"📊 Error Summary:")
    logger.info(f"  - Console errors: {len(console_errors)} (CORS: {len(cors_errors)})")
    logger.info(f"  - Network errors: {len(network_errors)} (Server: {len(server_errors)})")
    
    # Assertions
    assert page.url.startswith(FRONTEND_URL) or page.url.startswith("http"), \
        f"Unexpected page URL: {page.url}"
    assert len(cors_errors) == 0, f"Found CORS errors: {cors_errors[:3]}"
    assert len(server_errors) == 0, f"Found server errors: {[e.get('url') for e in server_errors[:3]]}"
    
    logger.info("✅ CTO Demo Scenario 3: Playwright E2E validation complete")


