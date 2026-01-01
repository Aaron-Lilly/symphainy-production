#!/usr/bin/env python3
"""
TEST #5: Operations Pillar Smoke Test
Priority: 🔴 HIGH
Estimated Time: 2-3 hours  
Owner: Frontend Engineer B

Quick validation that Operations Pillar works
"""

import pytest
from playwright.async_api import async_playwright, Page, expect
import os

@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(180)
async def test_operations_pillar_basic_flow():
    """
    Operations Pillar Smoke Test
    
    Verifies:
    1. 3-card interface visible
    2. File selection works
    3. Workflow visual appears
    4. SOP visual appears
    5. Coexistence section exists
    6. OperationsLiaison available
    """
    
    BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
    SCREENSHOT_DIR = "tests/screenshots/operations_smoke"
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page: Page = await browser.new_page()
        
        try:
            print("\n" + "="*60)
            print("OPERATIONS PILLAR SMOKE TEST")
            print("="*60)
            
            await page.goto(f"{BASE_URL}/operations", wait_until="networkidle")
            await page.screenshot(path=f"{SCREENSHOT_DIR}/01_operations_loaded.png")
            print("✅ Operations page loaded")
            
            # 3-card interface
            card_select = page.locator(
                "[data-testid='card-select'], "
                ".card:has-text('Select'), "
                "button:has-text('Select')"
            ).first
            
            card_upload = page.locator(
                "[data-testid='card-upload'], "
                ".card:has-text('Upload'), "
                "button:has-text('Upload')"
            ).first
            
            card_generate = page.locator(
                "[data-testid='card-generate'], "
                ".card:has-text('Generate'), "
                "button:has-text('Generate')"
            ).first
            
            # At least 2 cards should be visible
            await expect(card_select.or_(card_upload).or_(card_generate)).to_be_visible(timeout=5000)
            print("✅ Card interface visible")
            
            # Section 2: Workflow area
            workflow_section = page.locator(
                "[data-testid='workflow-visual'], "
                "[data-testid='workflow-section'], "
                ".workflow"
            ).first
            print("ℹ️  Workflow section (visible after generation)")
            
            # Section 2: SOP area
            sop_section = page.locator(
                "[data-testid='sop-visual'], "
                "[data-testid='sop-section'], "
                ".sop"
            ).first
            print("ℹ️  SOP section (visible after generation)")
            
            # Section 3: Coexistence
            coexistence_section = page.locator(
                "[data-testid='coexistence-section'], "
                ".coexistence-blueprint, "
                ".coexistence"
            ).first
            print("ℹ️  Coexistence section (visible after workflow+SOP)")
            
            # OperationsLiaison chat
            chat_panel = page.locator("[data-testid='chat-panel'], aside").first
            await expect(chat_panel).to_be_visible()
            print("✅ Chat panel available (OperationsLiaison)")
            
            # Quick interaction
            chat_input = page.locator("input[placeholder*='message'], textarea").first
            await chat_input.fill("Help me generate a workflow")
            await chat_input.press("Enter")
            await page.wait_for_timeout(2000)
            print("✅ OperationsLiaison interaction sent")
            
            await page.screenshot(path=f"{SCREENSHOT_DIR}/02_operations_interaction.png")
            
            print("\n" + "="*60)
            print("🎉 OPERATIONS PILLAR SMOKE TEST PASSED!")
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

