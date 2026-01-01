# 🎯 E2E Test Execution Plan - Top-Down MVP Validation

**Date:** November 6, 2024  
**Goal:** Validate MVP vision from the top down with frontend E2E tests  
**Complement:** Team B's bottom-up layer validation  
**Critical Test:** Complete CTO Demo Journey

---

## 📋 PRE-FLIGHT CHECKLIST

### **1. Playwright Browser Setup** ⚠️ **NEEDS ATTENTION**

**Current Status:**
- ✅ Playwright library installed (v1.55.0)
- ✅ pytest-playwright installed (v0.7.1)
- ❌ Chromium browser NOT installed

**Required Action:**
```bash
# Install Chromium browser for Playwright
python3 -m playwright install chromium

# Verify installation
python3 -m playwright --version
```

**Why:** Playwright needs an actual browser to run tests. The library is just the driver.

---

### **2. Frontend Service** ⚠️ **NEEDS TO BE RUNNING**

**Current Status:**
- ❌ Frontend not running on port 3000

**Required Action:**
```bash
# Option A: Start frontend in development mode
cd /home/founders/demoversion/symphainy_source/symphainy-frontend
npm install  # If not already done
npm run dev

# Option B: Start via Docker (if containerized)
docker-compose up symphainy-frontend

# Verify it's running
curl http://localhost:3000
# Should return HTML or redirect to landing page
```

**Expected:** Frontend accessible at `http://localhost:3000`

---

### **3. Backend Service** ⚠️ **NEEDS TO BE RUNNING**

**Current Status:**
- ❌ Backend not running on port 8000

**Required Action:**
```bash
# Option A: Start backend directly
cd /home/founders/demoversion/symphainy_source/symphainy-platform
python3 main.py

# Option B: Start via Docker
docker-compose up symphainy-backend

# Verify it's running
curl http://localhost:8000/health
# Should return {"status": "healthy"} or similar
```

**Expected:** Backend accessible at `http://localhost:8000`

**Critical:** With our newly restored manager hierarchy, this should now:
1. Start City Manager
2. Bootstrap all 5 managers in sequence
3. Initialize all realm services
4. Be ready to serve API requests

---

## 🎯 THE CRITICAL TEST

### **Test #1: Complete CTO Demo Journey** ⭐

**File:** `tests/e2e/test_complete_cto_demo_journey.py`  
**Priority:** 🔴 CRITICAL  
**Duration:** ~5 minutes to run  
**Coverage:** 80% of embarrassment risk

**What It Tests:**
```
Landing Page
    ↓ GuideAgent interaction
Content Pillar
    ↓ Upload → Parse → Preview → ContentLiaison
Insights Pillar
    ↓ Analysis → Visualization → InsightsLiaison
Operations Pillar
    ↓ Workflow → SOP → Coexistence → OperationsLiaison
Business Outcomes
    ↓ Summaries → Roadmap → POC → BusinessOutcomesLiaison
```

**This ONE test validates:**
- ✅ All 4 pillars load
- ✅ Navbar persists across pages
- ✅ Chat panel works everywhere
- ✅ GuideAgent routes correctly
- ✅ All 4 Liaison agents respond
- ✅ File upload works
- ✅ Backend processing works
- ✅ Frontend displays results
- ✅ Complete user journey flows

**If this passes, the CTO demo will work!**

---

## 🚀 EXECUTION SEQUENCE

### **Step 1: Setup (15 minutes)**

```bash
cd /home/founders/demoversion/symphainy_source

# Install Playwright browser
python3 -m playwright install chromium

# Verify installation
python3 -c "from playwright.sync_api import sync_playwright; print('✅ Playwright ready')"
```

---

### **Step 2: Start Services (5 minutes)**

**Terminal 1 - Backend:**
```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
python3 main.py

# Watch for:
# ✅ City Manager initialized
# ✅ Solution Manager bootstrapped
# ✅ Journey Manager bootstrapped
# ✅ Experience Manager bootstrapped
# ✅ Delivery Manager bootstrapped
# ✅ Server running on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd /home/founders/demoversion/symphainy_source/symphainy-frontend
npm run dev

# Watch for:
# ✅ Next.js compiled
# ✅ Ready on http://localhost:3000
```

**Terminal 3 - Verification:**
```bash
# Test backend
curl http://localhost:8000/health
# Expected: {"status": "healthy"} or similar

# Test frontend
curl http://localhost:3000
# Expected: HTML response

echo "✅ Both services ready!"
```

---

### **Step 3: Run The Critical Test (5 minutes)**

**Terminal 4 - E2E Test:**
```bash
cd /home/founders/demoversion/symphainy_source

# Set environment variables
export TEST_FRONTEND_URL="http://localhost:3000"
export TEST_BACKEND_URL="http://localhost:8000"

# Run the test (in visible mode for first run)
pytest tests/e2e/test_complete_cto_demo_journey.py::test_complete_cto_demo_journey -v -s

# Alternative: Run with Playwright inspector for debugging
PWDEBUG=1 pytest tests/e2e/test_complete_cto_demo_journey.py::test_complete_cto_demo_journey -v -s
```

**What You'll See:**
1. Browser window opens automatically
2. Test navigates to http://localhost:3000
3. Clicks through all 4 pillars
4. Takes screenshots at each step
5. Saves video recording
6. Reports PASS or FAIL with details

**Screenshots saved to:** `tests/screenshots/cto_demo_journey/`  
**Videos saved to:** `tests/screenshots/cto_demo_journey/videos/`

---

## 📊 EXPECTED OUTCOMES

### **Scenario A: Test Passes** ✅

**What It Means:**
- 🎉 Complete user journey works!
- 🎉 All 4 pillars functional
- 🎉 All agents responding correctly
- 🎉 Backend processing working
- 🎉 CTO demo will likely succeed
- 🎉 60%+ confidence in MVP

**Next Steps:**
1. Run remaining pillar smoke tests
2. Run persistent UI test
3. Build confidence to 90%+
4. Schedule CTO demo

---

### **Scenario B: Test Fails** ⚠️

**What It Means:**
- We found issues BEFORE the CTO saw them! ✅
- Screenshots show exactly what broke
- Video shows the failure sequence
- We know what to fix

**Common First-Run Issues:**

1. **"Element not found"**
   - Frontend HTML doesn't match test selectors
   - Need to update `data-testid` attributes
   - **Fix:** Update selectors in test or add data-testid to components

2. **"Backend not responding"**
   - API endpoint missing or wrong path
   - Manager hierarchy not initialized correctly
   - **Fix:** Check backend logs, verify managers bootstrapped

3. **"Agent not responding"**
   - GuideAgent or Liaison not initialized
   - MCP tools not registered
   - **Fix:** Check agent logs, verify Curator registration

4. **"File upload fails"**
   - Backend file handling broken
   - Storage abstraction not connected
   - **Fix:** Check Librarian service, verify Public Works

5. **"Navigation breaks"**
   - Frontend routing issue
   - Session not persisted
   - **Fix:** Check TrafficCop, verify session management

**Debugging Strategy:**
1. Look at screenshot at failure point
2. Check browser console in video
3. Review backend logs for errors
4. Fix ONE issue at a time
5. Re-run test
6. Repeat until green

---

## 🎯 SUCCESS CRITERIA

### **Minimum Viable Demo (60% confidence):**
- ✅ Test #1 passes through all 5 steps
- ✅ No critical errors (500s, crashes)
- ✅ Basic functionality works

### **Professional Quality (90% confidence):**
- ✅ Test #1 passes consistently (3/3 runs)
- ✅ Tests #2-6 all passing (persistent UI + 4 pillar smokes)
- ✅ No embarrassing UX issues
- ✅ Performance acceptable (<3s page loads)

---

## 📋 TEST SUITE OVERVIEW

We have **55 E2E tests planned** (from Option C). Here's the priority order:

### **Tier 1: Critical (Day 1-2)** 🔴
1. **test_complete_cto_demo_journey.py** ⭐ **START HERE**
2. test_persistent_ui.py
3. test_content_pillar_smoke.py
4. test_insights_pillar_smoke.py
5. test_operations_pillar_smoke.py
6. test_business_outcomes_pillar_smoke.py

**Goal:** If these 6 pass, CTO demo will probably work.

### **Tier 2: High Priority (Day 3-5)** 🟠
7-20. Individual pillar feature tests
21-30. Agent interaction tests
31-40. Cross-pillar flow tests

**Goal:** Build confidence from 60% → 85%

### **Tier 3: Polish (Day 6-12)** 🟡
41-55. Edge cases, error handling, performance tests

**Goal:** Build confidence from 85% → 95%+

---

## 🔄 INTEGRATION WITH TEAM B

### **Team B (Bottom-Up):**
- Testing layer by layer: Smart City → Business Enablement → Experience → Journey → Solution
- Validates: Services work, APIs correct, composition works
- When done: Foundation is solid

### **Your Team (Top-Down):**
- Testing user journey: Landing → Content → Insights → Operations → Outcomes
- Validates: User experience works, full flow works, MVP vision realized
- When done: User-facing functionality proven

### **Together:**
```
Team B validates:  [Smart City] → [Business] → [Experience] → [Journey] → [Solution]
                          ↑                                                      ↑
Your team validates:  [User Journey: Landing → Content → Insights → Operations → Outcomes]
```

**When both complete:**
- ✅ Foundation tested (Team B)
- ✅ User experience tested (Your team)
- ✅ Full stack validated
- ✅ MVP proven end-to-end
- ✅ CTO demo ready

---

## 🆘 TROUBLESHOOTING

### **"Playwright browser not found"**
```bash
python3 -m playwright install chromium
```

### **"Frontend won't start"**
```bash
cd symphainy-frontend
npm install
npm run dev
```

### **"Backend crashes on startup"**
```bash
cd symphainy-platform
python3 main.py

# Check logs for manager bootstrapping errors
# Verify all 5 managers initialize successfully
```

### **"Test hangs forever"**
```bash
# Test has 300s timeout, but you can stop it with Ctrl+C
# Check if services are responding:
curl http://localhost:3000
curl http://localhost:8000/health
```

### **"Can't understand failure"**
```bash
# Run with Playwright inspector (pauses at each step)
PWDEBUG=1 pytest tests/e2e/test_complete_cto_demo_journey.py -v -s

# Check screenshots
ls tests/screenshots/cto_demo_journey/

# Watch video
# Open .webm file in Chrome/Firefox
```

---

## 📚 RESOURCES

### **Test Files:**
- `tests/e2e/test_complete_cto_demo_journey.py` - The critical test
- `tests/e2e/README_QUICK_START.md` - Quick start guide
- `OPTION_C_EXECUTION_PLAN.md` - Full 12-day plan
- `tests/MVP_TEST_COVERAGE_AUDIT.md` - What needs testing

### **Playwright Docs:**
- https://playwright.dev/python/docs/intro
- https://playwright.dev/python/docs/selectors
- https://playwright.dev/python/docs/assertions

### **Architecture Docs:**
- `MANAGER_HIERARCHY_ARCHITECTURAL_AUDIT.md` - Manager hierarchy
- `MANAGER_HIERARCHY_RESTORATION_COMPLETE.md` - Restoration summary
- `DEPLOYMENT_STRATEGY_UPDATED.md` - Deployment guide

---

## 🎯 YOUR MISSION

**Immediate Goal:** Get Test #1 passing

**Strategy:**
1. ✅ Install Playwright browser (15 min)
2. ✅ Start backend + frontend (5 min)
3. ✅ Run Test #1 (5 min)
4. 🔧 Fix failures one by one (varies)
5. ✅ Get to green (celebrate!)
6. 🔄 Repeat for Tests #2-6

**Timeline:**
- **Today:** Get Test #1 running (even if failing)
- **Tomorrow:** Get Test #1 passing + Tests #2-6 running
- **Day 3:** All 6 critical tests passing
- **Week 2:** Build remaining 49 tests
- **Day 12:** CTO demo ready

---

## 🎉 NEXT STEPS

**Right Now:**
```bash
# 1. Install browser
python3 -m playwright install chromium

# 2. Start backend (Terminal 1)
cd symphainy-platform && python3 main.py

# 3. Start frontend (Terminal 2)
cd symphainy-frontend && npm run dev

# 4. Run test (Terminal 3)
cd /home/founders/demoversion/symphainy_source
export TEST_FRONTEND_URL="http://localhost:3000"
export TEST_BACKEND_URL="http://localhost:8000"
pytest tests/e2e/test_complete_cto_demo_journey.py::test_complete_cto_demo_journey -v -s
```

**Then:** Review results, fix issues, iterate until green!

**Remember:** Every failure is a gift - it's something we found BEFORE the CTO saw it!

---

**Status:** 🚀 **READY TO START TOP-DOWN VALIDATION**  
**Goal:** Validate MVP vision from user perspective  
**Complement:** Team B's bottom-up foundation validation  
**Outcome:** End-to-end confidence in platform + MVP




