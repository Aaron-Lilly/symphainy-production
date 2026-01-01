# E2E Testing Quick Start Guide
**For:** Frontend Engineering Team  
**Goal:** Get Test #1 running in < 1 hour  
**Then:** Build 54 more tests over 12 days

---

## 🚀 **GET STARTED IN 5 MINUTES**

### **Prerequisites:**
```bash
# Install Playwright
pip install playwright pytest-playwright

# Install browsers
playwright install chromium

# Verify installation
playwright --version
```

### **Run Test #1:**
```bash
# From project root
cd /home/founders/demoversion/symphainy_source

# Set environment variables
export TEST_FRONTEND_URL="http://localhost:3000"
export TEST_BACKEND_URL="http://localhost:8000"

# Run the critical test
pytest tests/e2e/test_complete_cto_demo_journey.py::test_complete_cto_demo_journey -v -s

# Or run all E2E tests
pytest tests/e2e/ -v -s
```

---

## 📋 **WHAT TO DO ON DAY 1**

### **Morning (2-3 hours):**
1. **Get Test #1 running**
   - Don't worry if it fails - that's expected!
   - Take notes on what breaks
   - Fix one selector at a time

2. **Update selectors in test**
   - Find your actual HTML elements
   - Update `data-testid` attributes or CSS selectors
   - Test again

### **Afternoon (3-5 hours):**
3. **Make Test #1 pass through STEP 1**
   - Landing page loads
   - Navbar visible
   - Chat panel visible
   - GuideAgent responds

4. **Make Test #1 pass through STEP 2**
   - Content Pillar loads
   - File upload works
   - Parse and preview work

---

## 🎯 **YOUR 6 CRITICAL TESTS (Day 1-2)**

### **Test #1: Complete CTO Demo Journey** ⭐ **START HERE**
- **File:** `test_complete_cto_demo_journey.py`
- **Time:** 6-8 hours
- **Priority:** 🔴 CRITICAL
- **Status:** ✅ Template created
- **What to do:** Fix selectors, make it pass

### **Test #2: Persistent UI**
- **File:** `test_persistent_ui.py`
- **Time:** 2-3 hours
- **Priority:** 🔴 CRITICAL
- **Status:** ❌ Need to create
- **Template below** ⬇️

### **Test #3-6: Pillar Smoke Tests**
- **Files:** 
  - `test_content_pillar_smoke.py`
  - `test_insights_pillar_smoke.py`
  - `test_operations_pillar_smoke.py`
  - `test_business_outcomes_pillar_smoke.py`
- **Time:** 2-3 hours each
- **Priority:** 🔴 HIGH
- **Status:** ❌ Need to create
- **Templates in execution plan** ⬇️

---

## 📖 **TEST STRUCTURE**

### **Every E2E test should:**
1. **Import required libraries**
```python
import pytest
from playwright.async_api import async_playwright, expect
```

2. **Mark as E2E test**
```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_something():
```

3. **Launch browser**
```python
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=False)
    page = await browser.new_page()
```

4. **Navigate and interact**
```python
await page.goto("http://localhost:3000")
await page.click("button#upload")
```

5. **Assert results**
```python
await expect(page.locator(".result")).to_be_visible()
```

6. **Take screenshots on failure**
```python
try:
    # test code
except Exception as e:
    await page.screenshot(path="failure.png")
    raise
```

---

## 🛠️ **USEFUL PLAYWRIGHT COMMANDS**

### **Navigation:**
```python
await page.goto("http://localhost:3000")
await page.wait_for_url("**/content")
await page.reload()
```

### **Interaction:**
```python
# Click
await page.click("button#submit")
await page.locator("text=Upload").click()

# Type
await page.fill("input#message", "Hello")
await page.press("input#message", "Enter")

# Select dropdown
await page.select_option("select#file", label="sample.csv")
```

### **Assertions:**
```python
# Visibility
await expect(page.locator("#navbar")).to_be_visible()
await expect(page.locator(".error")).not_to_be_visible()

# Text content
await expect(page.locator("h1")).to_have_text("Welcome")
await expect(page.locator(".message")).to_contain_text("Success")

# Count
await expect(page.locator(".file-item")).to_have_count(3)

# URL
await expect(page).to_have_url("http://localhost:3000/content")
```

### **Waiting:**
```python
# Wait for element
await page.wait_for_selector("#content", state="visible")

# Wait for timeout
await page.wait_for_timeout(2000)  # 2 seconds

# Wait for network
await page.wait_for_load_state("networkidle")

# Wait for function
await page.wait_for_function("document.readyState === 'complete'")
```

---

## 🎨 **TEST #2 TEMPLATE: PERSISTENT UI**

Create `/tests/e2e/test_persistent_ui.py`:

```python
import pytest
from playwright.async_api import async_playwright, expect
import os

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_navbar_and_chat_panel_always_present():
    """Verify navbar and chat panel appear on EVERY page"""
    
    BASE_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
    pages = [
        ("landing", ""),
        ("content", "/content"),
        ("insights", "/insights"),
        ("operations", "/operations"),
        ("business_outcomes", "/business-outcomes")
    ]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        for page_name, path in pages:
            print(f"Testing {page_name} page...")
            
            # Navigate
            await page.goto(f"{BASE_URL}{path}")
            await page.wait_for_load_state("networkidle")
            
            # Assert navbar visible with 4 pillar links
            navbar = page.locator("nav")  # Adjust selector
            await expect(navbar).to_be_visible()
            
            content_link = page.locator("nav >> text=Content")
            insights_link = page.locator("nav >> text=Insights")
            operations_link = page.locator("nav >> text=Operations")
            outcomes_link = page.locator("nav >> text=Business Outcomes")
            
            await expect(content_link).to_be_visible()
            await expect(insights_link).to_be_visible()
            await expect(operations_link).to_be_visible()
            await expect(outcomes_link).to_be_visible()
            
            print(f"  ✅ Navbar with 4 pillars visible on {page_name}")
            
            # Assert chat panel visible on right side
            chat_panel = page.locator("[data-testid='chat-panel']")  # Adjust
            await expect(chat_panel).to_be_visible()
            print(f"  ✅ Chat panel visible on {page_name}")
            
            # Assert GuideAgent or appropriate liaison is active
            # This will vary by page - GuideAgent on landing, Liaison on pillars
            agent_indicator = page.locator("[data-testid='active-agent']")  # Adjust
            # await expect(agent_indicator).to_be_visible()  # Optional
            
        await browser.close()
        print("\n✅ All pages have navbar and chat panel!")
```

---

## 🔍 **DEBUGGING TIPS**

### **Test fails immediately:**
- Check if frontend is running: `curl http://localhost:3000`
- Check if backend is running: `curl http://localhost:8000/health`
- Check environment variables are set

### **Can't find element:**
- Run test with `headless=False` to see browser
- Inspect element in browser to get correct selector
- Add `await page.pause()` to pause and inspect
- Use `page.locator("selector").screenshot()` to debug

### **Test is slow:**
- Reduce `wait_for_timeout` values
- Use `wait_for_selector` instead of fixed timeouts
- Check network requests in browser DevTools

### **Screenshots not helping:**
- Record video: `record_video_dir="./videos"`
- Use `page.pause()` to step through manually
- Add more `print()` statements

---

## 📊 **TRACK YOUR PROGRESS**

### **Day 1 Goal:**
- [ ] Test #1 running (even if failing)
- [ ] Test #1 passes through STEP 1 (landing page)
- [ ] Test #1 passes through STEP 2 (content pillar)
- [ ] Test #2 created and passing
- [ ] Test #3 started

### **Day 2 Goal:**
- [ ] Test #1 fully passing (all 5 steps)
- [ ] Tests #2-6 all passing
- [ ] 6 critical tests complete
- [ ] Screenshots/videos saved
- [ ] Confidence: 60% → **READY FOR PHASE 1**

---

## 🆘 **NEED HELP?**

### **Common Issues:**

**Issue:** `playwright` not found
```bash
pip install playwright pytest-playwright
playwright install
```

**Issue:** Test hangs forever
```bash
# Add timeout to test
@pytest.mark.timeout(60)  # 60 seconds
```

**Issue:** Can't find elements
```bash
# Use Playwright Inspector
PWDEBUG=1 pytest tests/e2e/test_complete_cto_demo_journey.py
```

**Issue:** Frontend not responding
```bash
# Check if it's running
curl http://localhost:3000
# Or navigate in browser: http://localhost:3000
```

---

## 📚 **RESOURCES**

- **Playwright Docs:** https://playwright.dev/python/docs/intro
- **Execution Plan:** `/OPTION_C_EXECUTION_PLAN.md`
- **Coverage Audit:** `/tests/MVP_TEST_COVERAGE_AUDIT.md`
- **Demo Readiness:** `/CTO_DEMO_READINESS_REPORT.md`

---

## 🎯 **YOUR MISSION**

**Week 1 (Days 1-2):** Get these 6 tests passing
**Week 2 (Days 3-9):** Build 49 more tests
**Week 2 (Days 10-12):** Polish and demo

**Remember:** Quality over speed. One passing test is better than five half-done tests.

**Let's build tests that make us confident, not embarrassed!** 🚀





