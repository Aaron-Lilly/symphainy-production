# ⚡ Quick Reference Card
**Print this or keep it handy during execution**

---

## 📚 **DOCUMENTS TO READ (In Order)**

1. **START_HERE.md** - Master guide (343 lines)
2. **OPTION_C_EXECUTION_PLAN.md** - Day-by-day plan (964 lines)
3. **tests/e2e/README_QUICK_START.md** - Technical setup (357 lines)
4. **CI_CD_DOCUMENTATION.md** - For Team B (1,100+ lines)

---

## 🧪 **RUN TESTS LOCALLY**

```bash
# Quick (6 critical tests, ~10 min)
./scripts/run-tests-locally.sh critical

# Full suite (~30 min)
./scripts/run-tests-locally.sh full

# Single test
./scripts/run-tests-locally.sh single test_complete_cto_demo_journey.py
```

---

## ☁️ **RUN TESTS IN CI (GitHub Actions)**

1. Go to: `github.com/your-org/symphainy/actions`
2. Click: "E2E Test Runner"
3. Click: "Run workflow"
4. Select: `critical` / `full` / `single`
5. Download artifacts after completion

---

## 🐳 **DOCKER TESTING**

```bash
# Start all services + run tests
docker-compose -f docker-compose.ci.yml up --build

# Just E2E tests
docker-compose -f docker-compose.ci.yml up e2e-tests

# Stop everything
docker-compose -f docker-compose.ci.yml down
```

---

## 📊 **12-DAY TIMELINE**

| Days | Phase | Tests | Confidence |
|------|-------|-------|------------|
| 1-2 | Quick Win | 6 | 60% |
| 3-4 | Phase 1 | 21 | 75% |
| 5-7 | Phase 2A | 46 | 85% |
| 8-9 | Phase 2B | 55 | 93% |
| 10-11 | QA | 55 | 95% |
| 12 | Demo | - | 🎉 |

---

## 📋 **DAILY STANDUP (15 min)**

1. Yesterday: What tests passed?
2. Today: What tests planned?
3. Blockers: Any issues?
4. Confidence: Current %?

---

## ✅ **6 CRITICAL TESTS**

1. **test_complete_cto_demo_journey.py** - Full journey (5-8 min)
2. **test_persistent_ui.py** - Navbar + chat (2-3 min)
3. **test_content_pillar_smoke.py** - Content flow (2-3 min)
4. **test_insights_pillar_smoke.py** - Insights flow (2-3 min)
5. **test_operations_pillar_smoke.py** - Operations flow (2-3 min)
6. **test_business_outcomes_pillar_smoke.py** - Outcomes flow (2-3 min)

**Total:** ~10-15 minutes

---

## 🚨 **TROUBLESHOOTING**

### Test Fails:
1. Check screenshots: `tests/screenshots/`
2. Check if services running: `curl localhost:8000/health`
3. Read error message carefully
4. Check selector is correct
5. Ask team for help

### Services Won't Start:
```bash
# Check ports
lsof -i :3000
lsof -i :8000

# Kill if needed
kill -9 PID

# Restart
cd symphainy-platform && python3 main.py &
cd symphainy-frontend && npm run dev &
```

---

## 🎯 **SUCCESS CRITERIA**

**Day 2:** 6 tests passing → 60% confidence
**Day 4:** 21 tests passing → 75% confidence  
**Day 9:** 55 tests passing → 93% confidence
**Day 12:** Demo ready → 95% confidence → 🎉

---

## 📞 **GET HELP**

- **Tech Issues:** #dev-team Slack
- **CI/CD Issues:** #ci-cd Slack
- **Questions:** Read docs first, then ask
- **Blockers:** Raise immediately in standup

---

## 💪 **TEAM MOTTO**

> "No embarrassment. No excuses. Just excellence."

**One test at a time. One day at a time. One week to excellence.**

---

**Print this card and keep it visible during the sprint!**




