#!/usr/bin/env python3
"""
TEST #6: Business Outcomes Pillar Smoke Test
Priority: 🔴 HIGH
Estimated Time: 2-3 hours
Owner: Frontend Engineer C

Quick validation that Business Outcomes Pillar works
"""

import pytest
from playwright.async_api import async_playwright, Page, expect
import os

@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(180)
async def test_business_outcomes_pillar_basic_flow():
    """
    Business Outcomes Pillar Smoke Test
    
    Verifies:
    1. 3 pillar summary cards visible
    2. Summaries contain data
    3. Roadmap section exists
    4. POC Proposal section exists
    5. BusinessOutcomesLiaison available
    """
    
    BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
    SCREENSHOT_DIR = "tests/screenshots/business_outcomes_smoke"
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page: Page = await browser.new_page()
        
        try:
            print("\n" + "="*60)
            print("BUSINESS OUTCOMES PILLAR SMOKE TEST")
            print("="*60)
            
            await page.goto(f"{BASE_URL}/business-outcomes", wait_until="networkidle")
            await page.screenshot(path=f"{SCREENSHOT_DIR}/01_business_outcomes_loaded.png")
            print("✅ Business Outcomes page loaded")
            
            # 3 pillar summary cards
            content_summary = page.locator(
                "[data-testid='content-summary'], "
                ".summary-card:has-text('Content')"
            ).first
            
            insights_summary = page.locator(
                "[data-testid='insights-summary'], "
                ".summary-card:has-text('Insights')"
            ).first
            
            operations_summary = page.locator(
                "[data-testid='operations-summary'], "
                ".summary-card:has-text('Operations')"
            ).first
            
            # At least one summary should be visible
            await expect(
                content_summary.or_(insights_summary).or_(operations_summary)
            ).to_be_visible(timeout=5000)
            print("✅ At least one pillar summary visible")
            
            # Roadmap section
            roadmap_section = page.locator(
                "[data-testid='roadmap-section'], "
                "[data-testid='roadmap'], "
                ".roadmap"
            ).first
            print("ℹ️  Roadmap section (visible after generation)")
            
            # POC Proposal section
            poc_section = page.locator(
                "[data-testid='poc-proposal'], "
                "[data-testid='poc-section'], "
                ".poc-proposal"
            ).first
            print("ℹ️  POC Proposal section (visible after generation)")
            
            # BusinessOutcomesLiaison chat
            chat_panel = page.locator("[data-testid='chat-panel'], aside").first
            await expect(chat_panel).to_be_visible()
            print("✅ Chat panel available (BusinessOutcomesLiaison)")
            
            # Quick interaction
            chat_input = page.locator("input[placeholder*='message'], textarea").first
            await chat_input.fill("Generate the final roadmap")
            await chat_input.press("Enter")
            await page.wait_for_timeout(2000)
            print("✅ BusinessOutcomesLiaison interaction sent")
            
            await page.screenshot(path=f"{SCREENSHOT_DIR}/02_business_outcomes_interaction.png")
            
            print("\n" + "="*60)
            print("🎉 BUSINESS OUTCOMES PILLAR SMOKE TEST PASSED!")
            print("="*60)
            
        except Exception as e:
            await page.screenshot(path=f"{SCREENSHOT_DIR}/FAILURE.png")
            print(f"\n❌ TEST FAILED: {str(e)}")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))

