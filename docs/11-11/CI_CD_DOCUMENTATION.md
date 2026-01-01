# CI/CD Pipeline Documentation
**For:** Team B (Deployment & Testing Team)  
**Purpose:** Automated testing and deployment  
**Status:** ✅ Ready to use

---

## 🎯 **OVERVIEW**

This CI/CD pipeline automatically:
1. **Runs tests** on every push/PR
2. **Generates reports** with screenshots and videos
3. **Deploys to staging** when tests pass on `develop` branch
4. **Deploys to production** when tests pass on `main` branch (with manual approval)
5. **Sends notifications** to Slack on success/failure

---

## 📋 **WORKFLOWS**

### **1. Main CI/CD Pipeline** (`ci-cd-pipeline.yml`)

**Triggers:**
- Push to `main`, `develop`, or `phase*` branches
- Pull requests to `main` or `develop`
- Manual trigger via GitHub Actions UI

**Jobs:**
1. **Lint** - Code quality checks (flake8, black, eslint)
2. **Backend Tests** - Unit & integration tests with coverage
3. **Frontend Tests** - Component tests with coverage
4. **E2E Tests** - 6 critical tests + full journey
5. **Test Report** - Generate comprehensive report
6. **Deploy Staging** - Auto-deploy to staging (develop branch)
7. **Deploy Production** - Manual approval deploy (main branch)
8. **Notify** - Slack notifications and GitHub issues on failure

**Runtime:** ~20-30 minutes for full pipeline

---

### **2. E2E Test Runner** (`test-runner.yml`)

**For Team B to run tests on demand**

**Triggers:**
- Manual trigger (GitHub Actions → Run workflow)
- Scheduled daily at 2 AM UTC

**Options:**
- **Critical** - Run 6 critical tests only (~10 min)
- **Full** - Run all E2E tests (~30 min)
- **Single** - Run one specific test file (~5 min)

---

## 🚀 **QUICK START FOR TEAM B**

### **Run Tests Manually:**

1. Go to GitHub Actions: `https://github.com/your-org/symphainy/actions`
2. Click "E2E Test Runner" workflow
3. Click "Run workflow" button
4. Choose test suite:
   - **critical** - Quick validation (6 tests)
   - **full** - Complete test suite
   - **single** - Specific test file
5. Click "Run workflow" (green button)
6. Wait for results (~10-30 min)
7. Download artifacts (screenshots, videos, reports)

### **View Test Results:**

1. Click on workflow run
2. Click on "Artifacts" section at bottom
3. Download:
   - `e2e-screenshots` - Screenshots at each step
   - `e2e-videos` - Video recordings of tests
   - `test-summary` - Combined report

---

## 🛠️ **RUNNING TESTS LOCALLY**

### **Option 1: Using Docker Compose** (Recommended)

```bash
# Build and start all services
docker-compose -f docker-compose.ci.yml up --build

# Run just E2E tests
docker-compose -f docker-compose.ci.yml up e2e-tests

# View logs
docker-compose -f docker-compose.ci.yml logs -f

# Stop all services
docker-compose -f docker-compose.ci.yml down
```

### **Option 2: Manual Setup**

```bash
# Terminal 1: Start backend
cd symphainy-platform
python3 main.py

# Terminal 2: Start frontend
cd symphainy-frontend
npm run dev

# Terminal 3: Run tests
cd tests
export TEST_FRONTEND_URL=http://localhost:3000
export TEST_BACKEND_URL=http://localhost:8000
pytest e2e/ -v -s
```

---

## 📊 **TEST SUITE BREAKDOWN**

### **6 Critical Tests (Priority 1):**

| Test | File | Time | Purpose |
|------|------|------|---------|
| #1 | `test_complete_cto_demo_journey.py` | 5-8 min | Complete user journey |
| #2 | `test_persistent_ui.py` | 2-3 min | Navbar + chat on all pages |
| #3 | `test_content_pillar_smoke.py` | 2-3 min | Content pillar basic flow |
| #4 | `test_insights_pillar_smoke.py` | 2-3 min | Insights pillar basic flow |
| #5 | `test_operations_pillar_smoke.py` | 2-3 min | Operations pillar basic flow |
| #6 | `test_business_outcomes_pillar_smoke.py` | 2-3 min | Business outcomes basic flow |

**Total:** ~10-15 minutes for all 6 critical tests

### **Full Test Suite (All Phases):**

- **Critical Tests:** 6 tests
- **Phase 1 Tests:** 21 tests (15 new + 6 critical)
- **Phase 2 Tests:** 55 tests total
- **Total Runtime:** ~30-40 minutes

---

## 🔧 **CONFIGURATION**

### **Environment Variables:**

Set these as **GitHub Secrets** (Settings → Secrets → Actions):

**Required:**
```
AWS_ACCESS_KEY_ID          # For deployments
AWS_SECRET_ACCESS_KEY      # For deployments
SLACK_WEBHOOK              # For notifications
```

**Optional:**
```
CODECOV_TOKEN             # For coverage reports
DATABASE_URL              # For integration tests
```

### **GitHub Environments:**

Create these in Settings → Environments:

1. **staging**
   - URL: https://staging.symphainy.com
   - Auto-deploy on `develop` branch

2. **production**
   - URL: https://symphainy.com
   - Manual approval required
   - Reviewers: Add team leads

---

## 📦 **DEPLOYMENT PROCESS**

### **To Staging (Automatic):**

1. Merge PR to `develop` branch
2. CI/CD runs automatically
3. If all tests pass → Auto-deploy to staging
4. Smoke tests run on staging
5. Slack notification sent

### **To Production (Manual):**

1. Merge PR to `main` branch
2. CI/CD runs automatically
3. If all tests pass → Waits for approval
4. Designated reviewers approve deployment
5. Deploys to production
6. Smoke tests run on production
7. Slack notification sent

### **Rollback Procedure:**

```bash
# Option 1: Revert via GitHub
git revert <commit-hash>
git push origin main

# Option 2: Manual rollback (if deployed via AWS)
aws ecs update-service \
  --cluster production \
  --service symphainy-backend \
  --task-definition symphainy-backend:PREVIOUS_VERSION \
  --force-new-deployment
```

---

## 📈 **MONITORING & ALERTS**

### **Where to Check Status:**

1. **GitHub Actions Tab**
   - See all workflow runs
   - View logs and artifacts
   - Trigger manual runs

2. **Slack Notifications**
   - Success/failure alerts
   - Deployment notifications
   - Test failure summaries

3. **GitHub Issues**
   - Auto-created on main branch failures
   - Tagged with `bug` and `ci-cd`

### **Key Metrics to Track:**

- **Test Pass Rate:** Should be >95%
- **Pipeline Duration:** Aim for <30 min
- **Deployment Frequency:** Track per week
- **Mean Time to Recovery:** How fast bugs are fixed

---

## 🐛 **TROUBLESHOOTING**

### **Tests Failing in CI but Pass Locally:**

1. Check environment differences
2. Verify timeouts (CI may be slower)
3. Check for race conditions
4. Review screenshots/videos from CI

### **E2E Tests Timing Out:**

1. Increase timeout in workflow: `timeout-minutes: 60`
2. Check if services started properly
3. Review service startup logs
4. Verify health checks passing

### **Deployment Failed:**

1. Check AWS credentials
2. Verify Docker images built successfully
3. Review deployment logs
4. Check infrastructure capacity

### **Playwright Installation Issues:**

```bash
# In CI, add this step if Playwright fails:
- name: Install Playwright dependencies
  run: |
    playwright install-deps
    playwright install chromium
```

---

## 📝 **COMMON TASKS FOR TEAM B**

### **Task 1: Run Critical Tests Before Demo**

```bash
# Via GitHub Actions
1. Go to Actions → E2E Test Runner
2. Click "Run workflow"
3. Select "critical"
4. Wait ~10 minutes
5. Download screenshots to verify
```

### **Task 2: Test Specific Feature**

```bash
# Via GitHub Actions
1. Go to Actions → E2E Test Runner
2. Click "Run workflow"
3. Select "single"
4. Enter test file name (e.g., test_content_pillar_smoke.py)
5. View results
```

### **Task 3: Deploy to Staging**

```bash
# Automatic on develop branch merge
git checkout develop
git merge feature-branch
git push origin develop
# CI/CD will auto-deploy if tests pass
```

### **Task 4: Review Failed Test**

```bash
# 1. Go to failed workflow run
# 2. Download "e2e-screenshots" artifact
# 3. Look for "FAILURE.png" screenshots
# 4. Check step that failed
# 5. Fix issue and re-run
```

---

## 🔐 **SECURITY BEST PRACTICES**

1. **Never commit secrets** to repository
2. **Use GitHub Secrets** for sensitive data
3. **Rotate credentials** quarterly
4. **Limit deployment access** to authorized personnel
5. **Review pull requests** before merging to main
6. **Enable branch protection** on main/develop

---

## 📚 **USEFUL COMMANDS**

### **View CI Logs:**
```bash
gh run list                    # List recent runs
gh run view RUN_ID             # View specific run
gh run watch RUN_ID            # Watch run in real-time
```

### **Download Artifacts:**
```bash
gh run download RUN_ID         # Download all artifacts
gh run download RUN_ID -n e2e-screenshots  # Download specific artifact
```

### **Trigger Workflow:**
```bash
gh workflow run "E2E Test Runner" --ref develop -f test_suite=critical
```

### **Cancel Running Workflow:**
```bash
gh run cancel RUN_ID
```

---

## 🎯 **SUCCESS CRITERIA**

### **Pipeline is healthy when:**
- ✅ Tests pass >95% of the time
- ✅ Pipeline completes in <30 minutes
- ✅ Deployments succeed on first try
- ✅ Rollbacks work smoothly if needed
- ✅ Team is notified of all failures
- ✅ Screenshots/videos help debug issues

### **Team B is successful when:**
- ✅ Can run tests on demand
- ✅ Can interpret test results
- ✅ Can debug failures using artifacts
- ✅ Can deploy to staging confidently
- ✅ Can coordinate production deployments
- ✅ Can rollback if needed

---

## 📞 **SUPPORT**

### **Need Help?**

1. Check this documentation
2. Review workflow logs
3. Check Slack #ci-cd channel
4. Contact DevOps lead
5. Create GitHub issue with `ci-cd` label

### **Report Issues:**

Create GitHub issue with:
- Workflow run URL
- Error message
- Screenshots/logs
- Expected vs actual behavior

---

## 🚀 **NEXT STEPS FOR TEAM B**

### **Week 1:**
- [ ] Review this documentation
- [ ] Set up GitHub Secrets
- [ ] Configure Slack webhook
- [ ] Run critical tests manually
- [ ] Review test artifacts

### **Week 2:**
- [ ] Monitor daily test runs
- [ ] Practice deployments to staging
- [ ] Set up monitoring dashboards
- [ ] Document any issues found

### **Ongoing:**
- [ ] Monitor test health
- [ ] Review deployment logs
- [ ] Update documentation as needed
- [ ] Improve pipeline based on feedback

---

**Last Updated:** November 6, 2025  
**Maintained By:** DevOps Team  
**Questions?** Slack: #ci-cd





