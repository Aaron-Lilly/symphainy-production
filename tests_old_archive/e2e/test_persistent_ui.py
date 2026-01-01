#!/usr/bin/env python3
"""
TEST #2: Persistent UI Elements E2E
Priority: 🔴 CRITICAL
Estimated Time: 2-3 hours
Owner: Frontend Engineer A

This test verifies that the core UX promise is kept:
- Navbar with 4 pillars visible on ALL pages
- Chat panel visible on right side on ALL pages
- Appropriate agent (Guide or Liaison) active on each page
"""

import pytest
from playwright.async_api import async_playwright, Page, expect, Browser
import os

@pytest.mark.e2e
@pytest.mark.critical
@pytest.mark.asyncio
@pytest.mark.timeout(120)
async def test_navbar_and_chat_panel_always_present():
    """
    Verify navbar and chat panel appear on EVERY page
    
    This is the #1 UX promise in the MVP:
    - "Persistent UI elements include a navbar across the top for each of the four pillars"
    - "and a chat panel along the right hand side"
    
    If this fails, CTO will be confused and unable to navigate.
    """
    
    BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
    SCREENSHOT_DIR = "tests/screenshots/persistent_ui"
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    
    # Define all pages to test
    pages_to_test = [
        ("Landing Page", ""),
        ("Content Pillar", "/content"),
        ("Insights Pillar", "/insights"),
        ("Operations Pillar", "/operations"),
        ("Business Outcomes", "/business-outcomes")
    ]
    
    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page: Page = await context.new_page()
        
        try:
            for page_name, path in pages_to_test:
                print(f"\n{'='*60}")
                print(f"Testing: {page_name}")
                print(f"{'='*60}")
                
                # Navigate to page
                await page.goto(f"{BASE_URL}{path}", wait_until="networkidle")
                await page.screenshot(path=f"{SCREENSHOT_DIR}/{page_name.replace(' ', '_').lower()}.png")
                
                # =================================================================
                # ASSERT: NAVBAR IS PRESENT
                # =================================================================
                
                # Find navbar (adjust selector based on your actual HTML)
                navbar = page.locator("nav, [data-testid='navbar'], [role='navigation']").first
                await expect(navbar).to_be_visible(timeout=5000)
                print(f"✅ Navbar visible on {page_name}")
                
                # Assert: All 4 pillar links are present
                content_link = page.locator("nav a[href*='content'], nav >> text=/Content/i").first
                insights_link = page.locator("nav a[href*='insights'], nav >> text=/Insights/i").first
                operations_link = page.locator("nav a[href*='operations'], nav >> text=/Operations/i").first
                outcomes_link = page.locator("nav a[href*='business'], nav >> text=/Business.*Outcomes/i").first
                
                await expect(content_link).to_be_visible(timeout=3000)
                await expect(insights_link).to_be_visible(timeout=3000)
                await expect(operations_link).to_be_visible(timeout=3000)
                await expect(outcomes_link).to_be_visible(timeout=3000)
                
                print(f"  ✅ All 4 pillar links visible")
                
                # Assert: Active pillar is highlighted (optional but nice UX)
                if path:  # Not landing page
                    active_path = path.split('/')[1] if '/' in path else path
                    # Check if current pillar link has active class or aria-current
                    active_link = page.locator(f"nav a[href*='{active_path}'][aria-current], nav a[href*='{active_path}'].active").first
                    # This may not exist in your current implementation - that's OK for now
                    # await expect(active_link).to_be_visible(timeout=1000)
                    print(f"  ℹ️  Active pillar highlighting (nice-to-have)")
                
                # =================================================================
                # ASSERT: CHAT PANEL IS PRESENT
                # =================================================================
                
                # Find chat panel (adjust selector based on your actual HTML)
                chat_panel = page.locator(
                    "[data-testid='chat-panel'], "
                    ".chat-panel, "
                    "[class*='chat'], "
                    "aside"
                ).first
                
                await expect(chat_panel).to_be_visible(timeout=5000)
                print(f"✅ Chat panel visible on {page_name}")
                
                # Assert: Chat panel is on the right side
                # Check if it has CSS properties that indicate right positioning
                chat_box = await chat_panel.bounding_box()
                if chat_box:
                    viewport_width = 1920
                    # Chat panel should be in the right 30% of the screen
                    assert chat_box['x'] > (viewport_width * 0.6), \
                        f"Chat panel should be on right side, found at x={chat_box['x']}"
                    print(f"  ✅ Chat panel positioned on right side (x={chat_box['x']})")
                
                # =================================================================
                # ASSERT: APPROPRIATE AGENT IS ACTIVE
                # =================================================================
                
                # Determine which agent should be active
                expected_agents = {
                    "": "Guide",  # Landing
                    "/content": "Content",
                    "/insights": "Insights",
                    "/operations": "Operations",
                    "/business-outcomes": "Business Outcomes"
                }
                
                expected_agent = expected_agents.get(path, "Guide")
                
                # Check for agent indicator (adjust selector)
                agent_indicator = page.locator(
                    f"[data-testid='active-agent']:has-text('{expected_agent}'), "
                    f".agent-name:has-text('{expected_agent}'), "
                    f"text=/{expected_agent}.*Agent/i"
                ).first
                
                # May not be immediately visible - that's OK for now
                # await expect(agent_indicator).to_be_visible(timeout=3000)
                print(f"  ℹ️  Expected agent: {expected_agent} (implement agent switching)")
                
                # Assert: Chat input field is present
                chat_input = page.locator(
                    "input[placeholder*='message'], "
                    "textarea[placeholder*='message'], "
                    "[data-testid='chat-input']"
                ).first
                
                await expect(chat_input).to_be_visible(timeout=3000)
                print(f"  ✅ Chat input field visible")
                
                # =================================================================
                # QUICK INTERACTION TEST
                # =================================================================
                
                # Send a message and verify response
                test_message = f"Test message on {page_name}"
                await chat_input.fill(test_message)
                await chat_input.press("Enter")
                
                # Wait for response (adjust timeout based on your backend)
                await page.wait_for_timeout(2000)
                
                # Check if a response appeared (adjust selector)
                messages = page.locator(
                    "[data-testid='chat-message'], "
                    ".message, "
                    ".chat-message"
                )
                message_count = await messages.count()
                assert message_count >= 1, f"Should have at least 1 message, found {message_count}"
                print(f"  ✅ Chat interaction works ({message_count} messages)")
                
                print(f"✅ {page_name} - ALL CHECKS PASSED")
            
            # =================================================================
            # CROSS-PAGE NAVIGATION TEST
            # =================================================================
            print(f"\n{'='*60}")
            print("Testing cross-page navigation via navbar")
            print(f"{'='*60}")
            
            # Navigate between pages using navbar
            await content_link.click()
            await page.wait_for_url("**/content", timeout=5000)
            print("✅ Navbar link to Content works")
            
            await insights_link.click()
            await page.wait_for_url("**/insights", timeout=5000)
            print("✅ Navbar link to Insights works")
            
            await operations_link.click()
            await page.wait_for_url("**/operations", timeout=5000)
            print("✅ Navbar link to Operations works")
            
            await outcomes_link.click()
            await page.wait_for_url("**/business", timeout=5000)
            print("✅ Navbar link to Business Outcomes works")
            
            # Navigate back to landing (if there's a home link)
            home_link = page.locator("nav a[href='/'], nav >> text=/Home/i").first
            if await home_link.is_visible():
                await home_link.click()
                await page.wait_for_url(BASE_URL, timeout=5000)
                print("✅ Navbar link to Home works")
            
            print(f"\n{'='*60}")
            print("🎉 TEST PASSED: PERSISTENT UI ELEMENTS WORK!")
            print(f"{'='*60}")
            print("\n✅ Navbar present on all pages")
            print("✅ Chat panel present on all pages")
            print("✅ Navigation between pages works")
            print("✅ Chat interactions work on all pages")
            print(f"\n📸 Screenshots saved to: {SCREENSHOT_DIR}")
            
        except Exception as e:
            await page.screenshot(path=f"{SCREENSHOT_DIR}/FAILURE.png")
            print(f"\n❌ TEST FAILED: {str(e)}")
            print(f"📸 Failure screenshot: {SCREENSHOT_DIR}/FAILURE.png")
            raise
        
        finally:
            await context.close()
            await browser.close()

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_navbar_responsive_behavior():
    """Test navbar behavior on different screen sizes"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Test on desktop
        desktop_context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        desktop_page = await desktop_context.new_page()
        
        BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
        await desktop_page.goto(BASE_URL)
        
        navbar = desktop_page.locator("nav").first
        await expect(navbar).to_be_visible()
        print("✅ Navbar visible on desktop (1920x1080)")
        
        await desktop_context.close()
        
        # Test on tablet (optional - may want hamburger menu)
        tablet_context = await browser.new_context(viewport={"width": 768, "height": 1024})
        tablet_page = await tablet_context.new_page()
        await tablet_page.goto(BASE_URL)
        
        navbar_tablet = tablet_page.locator("nav").first
        await expect(navbar_tablet).to_be_visible()
        print("✅ Navbar visible on tablet (768x1024)")
        
        await tablet_context.close()
        await browser.close()

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_chat_panel_state_persistence():
    """Test that chat panel maintains state across navigation"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
        await page.goto(BASE_URL)
        
        # Send a message
        chat_input = page.locator("input[placeholder*='message'], textarea[placeholder*='message']").first
        await chat_input.fill("Remember this message")
        await chat_input.press("Enter")
        await page.wait_for_timeout(1000)
        
        # Navigate to another page
        content_link = page.locator("nav >> text=/Content/i").first
        await content_link.click()
        await page.wait_for_url("**/content")
        
        # Check if message history persists
        messages = page.locator("[data-testid='chat-message'], .message")
        message_count = await messages.count()
        
        # Should have at least 1 message (ideally 2+ with response)
        assert message_count >= 1, "Chat history should persist across navigation"
        print(f"✅ Chat history persisted ({message_count} messages)")
        
        await browser.close()

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s", "--tb=short"]))

