#!/usr/bin/env python3
"""
TEST #3: Content Pillar Smoke Test
Priority: 🔴 HIGH
Estimated Time: 2-3 hours
Owner: Frontend Engineer A

Quick validation that Content Pillar basic flow works
"""

import pytest
from playwright.async_api import async_playwright, Page, expect
import os
import tempfile

@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.asyncio
@pytest.mark.timeout(180)
async def test_content_pillar_basic_flow():
    """
    Content Pillar Smoke Test
    
    Verifies:
    1. Dashboard/file list visible
    2. File uploader works
    3. Parse functionality works
    4. Preview shows data
    5. ContentLiaison chat available
    """
    
    BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
    SCREENSHOT_DIR = "tests/screenshots/content_smoke"
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page: Page = await browser.new_page()
        
        try:
            print("\n" + "="*60)
            print("CONTENT PILLAR SMOKE TEST")
            print("="*60)
            
            # Navigate to Content Pillar
            await page.goto(f"{BASE_URL}/content", wait_until="networkidle")
            await page.screenshot(path=f"{SCREENSHOT_DIR}/01_content_loaded.png")
            print("✅ Content page loaded")
            
            # Assert: File dashboard or uploader visible
            dashboard = page.locator(
                "[data-testid='file-dashboard'], "
                "[data-testid='file-uploader'], "
                ".file-dashboard, "
                ".file-list"
            ).first
            await expect(dashboard).to_be_visible(timeout=5000)
            print("✅ File dashboard/uploader visible")
            
            # Assert: ContentLiaison indicator (may be in chat panel)
            # This is optional - just verify chat panel exists
            chat_panel = page.locator("[data-testid='chat-panel'], aside, .chat").first
            await expect(chat_panel).to_be_visible()
            print("✅ Chat panel available (ContentLiaison)")
            
            # Create a test CSV file
            sample_csv = "customer_id,name,amount\n1,Test Corp,5000\n2,Demo Inc,3000\n"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                f.write(sample_csv)
                temp_file_path = f.name
            
            try:
                # Find file input
                file_input = page.locator("input[type='file']").first
                
                # Upload file
                await file_input.set_input_files(temp_file_path)
                await page.wait_for_timeout(2000)
                await page.screenshot(path=f"{SCREENSHOT_DIR}/02_file_uploaded.png")
                print("✅ File uploaded")
                
                # Look for parse button (might be automatic)
                parse_button = page.locator("button:has-text('Parse'), button:has-text('Process')").first
                if await parse_button.is_visible(timeout=2000):
                    await parse_button.click()
                    await page.wait_for_timeout(3000)
                    print("✅ Parse button clicked")
                else:
                    print("ℹ️  Parsing may be automatic")
                    await page.wait_for_timeout(3000)
                
                # Assert: Preview or data grid appears
                preview = page.locator(
                    "[data-testid='parse-preview'], "
                    "[data-testid='data-grid'], "
                    "table, "
                    "[role='grid']"
                ).first
                await expect(preview).to_be_visible(timeout=10000)
                await page.screenshot(path=f"{SCREENSHOT_DIR}/03_preview_visible.png")
                print("✅ Data preview visible")
                
                # Assert: Preview contains our data
                # Look for "Test Corp" or similar data from our CSV
                data_content = await preview.text_content()
                assert any(text in data_content for text in ["Test Corp", "Demo Inc", "customer_id"]), \
                    "Preview should show uploaded data"
                print("✅ Preview shows uploaded data")
                
                # Quick ContentLiaison interaction
                chat_input = page.locator("input[placeholder*='message'], textarea").first
                await chat_input.fill("What files do I have?")
                await chat_input.press("Enter")
                await page.wait_for_timeout(2000)
                print("✅ ContentLiaison interaction sent")
                
                print("\n" + "="*60)
                print("🎉 CONTENT PILLAR SMOKE TEST PASSED!")
                print("="*60)
                
            finally:
                # Cleanup temp file
                os.unlink(temp_file_path)
            
        except Exception as e:
            await page.screenshot(path=f"{SCREENSHOT_DIR}/FAILURE.png")
            print(f"\n❌ TEST FAILED: {str(e)}")
            raise
        
        finally:
            await browser.close()

@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_content_pillar_file_types():
    """Test that different file types are supported"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
        await page.goto(f"{BASE_URL}/content")
        
        # Look for file type options/buttons
        csv_option = page.locator("button:has-text('CSV'), [data-testid='file-type-csv']").first
        pdf_option = page.locator("button:has-text('PDF'), [data-testid='file-type-pdf']").first
        excel_option = page.locator("button:has-text('Excel'), [data-testid='file-type-excel']").first
        
        # At least one should be visible
        options_visible = (
            await csv_option.is_visible(timeout=3000) or
            await pdf_option.is_visible(timeout=1000) or
            await excel_option.is_visible(timeout=1000)
        )
        
        assert options_visible, "Should show file type options"
        print("✅ File type options available")
        
        await browser.close()

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))

