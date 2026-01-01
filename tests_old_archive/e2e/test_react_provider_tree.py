"""
E2E Test: React Provider Tree - Reality Check
Tests that would have caught yesterday's "must be used within Provider" errors

This test validates that all required React Context providers are present
in the component tree and that hooks don't throw errors.
"""

import pytest
from playwright.async_api import async_playwright, Page, Browser
import os
import asyncio

BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")

@pytest.mark.e2e
@pytest.mark.critical
@pytest.mark.asyncio
@pytest.mark.timeout(60)
class TestReactProviderTree:
    """Test that all required React providers are in the component tree"""
    
    async def test_no_provider_errors_on_load(self):
        """Test that no 'must be used within Provider' errors appear"""
        
        async with async_playwright() as p:
            browser: Browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page: Page = await context.new_page()
            
            # Collect console errors
            console_errors = []
            
            def handle_console_message(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)
            
            page.on("console", handle_console_message)
            
            # Collect page errors
            page_errors = []
            
            def handle_page_error(error):
                page_errors.append(str(error))
            
            page.on("pageerror", handle_page_error)
            
            try:
                # Navigate to landing page
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                
                # Wait a bit for React to render
                await asyncio.sleep(2)
                
                # Check for provider errors
                provider_errors = [
                    error for error in console_errors + page_errors
                    if "must be used within" in error.lower()
                    or "provider" in error.lower()
                ]
                
                if provider_errors:
                    print("\n❌ PROVIDER ERRORS FOUND:")
                    for error in provider_errors:
                        print(f"  - {error}")
                    pytest.fail(
                        f"❌ FAILED: Found {len(provider_errors)} provider errors - "
                        "This was yesterday's bug!"
                    )
                
                print("✅ No 'must be used within Provider' errors")
                
            finally:
                await browser.close()
    
    async def test_app_provider_exists(self):
        """Test that AppProvider is in the tree"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            
            try:
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Check for AppProvider errors
                app_provider_errors = [
                    error for error in console_errors
                    if "useApp must be used within an AppProvider" in error
                ]
                
                assert len(app_provider_errors) == 0, \
                    f"❌ FAILED: AppProvider missing - This was yesterday's bug!"
                
                print("✅ AppProvider is present")
                
            finally:
                await browser.close()
    
    async def test_experience_layer_provider_exists(self):
        """Test that ExperienceLayerProvider is in the tree"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            
            try:
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Check for ExperienceLayerProvider errors
                exp_provider_errors = [
                    error for error in console_errors
                    if "useExperienceLayer must be used within an ExperienceLayerProvider" in error
                ]
                
                assert len(exp_provider_errors) == 0, \
                    f"❌ FAILED: ExperienceLayerProvider missing - This was yesterday's bug!"
                
                print("✅ ExperienceLayerProvider is present")
                
            finally:
                await browser.close()
    
    async def test_user_context_provider_exists(self):
        """Test that UserContextProvider is in the tree"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            
            try:
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Check for UserContextProvider errors
                user_provider_errors = [
                    error for error in console_errors
                    if "useUserContext must be used within a UserContextProvider" in error
                ]
                
                assert len(user_provider_errors) == 0, \
                    f"❌ FAILED: UserContextProvider missing - This was yesterday's bug!"
                
                print("✅ UserContextProvider is present")
                
            finally:
                await browser.close()
    
    async def test_no_undefined_property_access(self):
        """Test that there are no 'Cannot read properties of undefined' errors"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            console_errors = []
            page_errors = []
            
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            
            try:
                # Load landing page
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Try to navigate to login/register (where user.name error happened)
                try:
                    # Look for login/register buttons
                    await page.click("text=/login|register|sign in/i", timeout=5000)
                    await asyncio.sleep(2)
                except:
                    # Button might not exist, that's OK
                    pass
                
                # Check for undefined property access errors
                undefined_errors = [
                    error for error in console_errors + page_errors
                    if "cannot read propert" in error.lower() and "undefined" in error.lower()
                ]
                
                if undefined_errors:
                    print("\n❌ UNDEFINED PROPERTY ERRORS FOUND:")
                    for error in undefined_errors:
                        print(f"  - {error}")
                    pytest.fail(
                        f"❌ FAILED: Found {len(undefined_errors)} undefined property errors - "
                        "Like yesterday's user.name.charAt(0) bug!"
                    )
                
                print("✅ No undefined property access errors")
                
            finally:
                await browser.close()

@pytest.mark.e2e
@pytest.mark.asyncio
class TestReactProviderTreeOnAllPages:
    """Test provider tree on all major pages"""
    
    async def test_providers_on_all_pillar_pages(self):
        """Test that providers work on all 4 pillar pages"""
        
        pages_to_test = [
            ("Landing", ""),
            ("Content", "/content"),
            ("Insights", "/insights"),
            ("Operations", "/operations"),
            ("Business Outcomes", "/business-outcomes"),
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                for page_name, path in pages_to_test:
                    print(f"\nTesting providers on {page_name} page...")
                    
                    console_errors = []
                    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                    
                    # Navigate to page
                    await page.goto(f"{BASE_URL}{path}", wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(2)
                    
                    # Check for provider errors
                    provider_errors = [
                        error for error in console_errors
                        if "must be used within" in error.lower()
                        or ("provider" in error.lower() and "error" in error.lower())
                    ]
                    
                    if provider_errors:
                        print(f"  ❌ {page_name}: {len(provider_errors)} provider errors")
                        for error in provider_errors:
                            print(f"    - {error}")
                        pytest.fail(f"Provider errors on {page_name} page")
                    else:
                        print(f"  ✅ {page_name}: No provider errors")
                
                print("\n✅ All pages have correct provider tree")
                
            finally:
                await browser.close()

@pytest.mark.e2e
@pytest.mark.asyncio
class TestReactErrorBoundaries:
    """Test that error boundaries catch crashes"""
    
    async def test_error_boundary_prevents_white_screen(self):
        """Test that errors don't cause white screen of death"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
                
                # Check if page rendered something (not blank)
                body_content = await page.content()
                
                # Page should have substantial content
                assert len(body_content) > 1000, \
                    "Page appears blank (possible crash)"
                
                # Page should have visible elements
                visible_elements = await page.locator("body *:visible").count()
                assert visible_elements > 10, \
                    f"Page has very few visible elements ({visible_elements}), possible crash"
                
                print(f"✅ Page rendered successfully ({visible_elements} visible elements)")
                
            finally:
                await browser.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

