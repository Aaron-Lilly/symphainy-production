# CI/CD Process - Complete How-To Guide

**Last Updated:** December 1, 2025  
**Version:** 2.0 (Post-Phase 1-3 Improvements)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [CI/CD Pipeline Architecture](#cicd-pipeline-architecture)
3. [How the Pipeline Works](#how-the-pipeline-works)
4. [Phase Gates Explained](#phase-gates-explained)
5. [For Developers](#for-developers)
6. [For DevOps/Platform Engineers](#for-devopsplatform-engineers)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)
9. [When to Consider Phase 5](#when-to-consider-phase-5)

---

## Overview

Our CI/CD pipeline ensures that only high-quality, tested, and secure code reaches production. The pipeline is divided into **4 phases** with multiple quality gates that must pass before deployment.

### Key Principles

- ✅ **Fail Fast** - Issues caught early in the pipeline
- ✅ **Quality First** - Multiple quality gates enforce standards
- ✅ **Security Built-In** - Security scanning at every stage
- ✅ **Automated Testing** - Comprehensive test coverage required
- ✅ **Environment Validation** - Test environment validation before production

---

## CI/CD Pipeline Architecture

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    CODE COMMIT / PUSH                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: CODE QUALITY & LINTING                            │
│  ✅ poetry.lock validation                                   │
│  ✅ Code formatting (Black)                                  │
│  ✅ Linting (Flake8, ESLint)                                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: TESTING                                            │
│  ✅ Backend Unit Tests (coverage >= 80%)                     │
│  ✅ Backend Integration Tests                                 │
│  ✅ Frontend Unit Tests (coverage >= 80%)                    │
│  ✅ E2E Tests (6 critical tests)                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: QUALITY GATES                                      │
│  ✅ Code Coverage Validation (>= 80%)                        │
│  ✅ Security Scanning (Bandit, Safety, pip-audit, npm audit) │
│  ✅ Code Quality Checks (Black, Flake8, ESLint)              │
│  ✅ Performance Monitoring                                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: TEST ENVIRONMENT VALIDATION                        │
│  ✅ Deploy to test environment                               │
│  ✅ Run smoke tests                                          │
│  ✅ Run integration tests                                    │
│  ✅ Validate service health                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: DEPLOYMENT                                          │
│  ✅ Staging Deployment (develop branch)                     │
│  ✅ Production Deployment (main branch)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## How the Pipeline Works

### Step-by-Step Process

#### 1. **Code Commit/Push**

When you push code to `develop` or `main` branch:

```bash
git add .
git commit -m "Your commit message"
git push origin develop  # or main
```

**What Happens:**
- GitHub Actions automatically triggers the CI/CD pipeline
- Pipeline runs in parallel where possible for speed

#### 2. **Phase 1: Code Quality & Linting**

**Duration:** ~2-5 minutes

**Checks:**
- ✅ `poetry.lock` file validation (prevents corrupted lock files)
- ✅ Python code formatting with Black
- ✅ Python linting with Flake8 (critical errors only)
- ✅ Frontend linting with ESLint

**What to Do if It Fails:**
```bash
# Fix formatting
black symphainy-platform tests

# Fix linting errors
flake8 symphainy-platform --count --select=E9,F63,F7,F82

# Fix frontend linting
cd symphainy-frontend
npm run lint -- --fix
```

**Gate:** ❌ **BLOCKS** deployment if failed

---

#### 3. **Phase 2: Testing**

**Duration:** ~10-20 minutes

**Backend Tests:**
- Unit tests (coverage >= 80% required)
- Integration tests
- Coverage reports generated

**Frontend Tests:**
- React component tests
- Jest unit tests
- Coverage >= 80% required

**E2E Tests:**
- 6 critical end-to-end tests
- Full platform validation
- Screenshots and videos captured

**What to Do if It Fails:**
```bash
# Run tests locally
cd tests
pytest unit/ -v --cov=../symphainy-platform --cov-fail-under=80

# Check coverage
pytest unit/ integration/ -v --cov=../symphainy-platform --cov-report=html
open htmlcov/index.html

# Run E2E tests
pytest e2e/test_complete_cto_demo_journey.py -v
```

**Gate:** ❌ **BLOCKS** deployment if failed

---

#### 4. **Phase 3: Quality Gates**

**Duration:** ~5-10 minutes

**Code Coverage:**
- Validates >= 80% coverage
- Generates coverage reports
- Uploads artifacts

**Security Scanning:**
- **Bandit** - Python security linter (non-blocking)
- **Safety** - Dependency vulnerabilities (blocking)
- **pip-audit** - Package vulnerabilities (blocking)
- **npm audit** - Frontend vulnerabilities (blocking)

**Code Quality:**
- Black formatting check (blocking)
- Flake8 critical errors (blocking)
- ESLint frontend linting (blocking)

**Performance:**
- Test execution time monitoring
- Performance benchmarks (non-blocking)

**What to Do if It Fails:**
```bash
# Check security vulnerabilities
cd symphainy-platform
safety check
pip-audit --desc

# Check frontend vulnerabilities
cd symphainy-frontend
npm audit --audit-level=moderate

# Fix security issues
# Update vulnerable dependencies
pip install --upgrade <package>
npm update <package>
```

**Gate:** ❌ **BLOCKS** deployment if failed

---

#### 5. **Phase 4: Test Environment Validation**

**Duration:** ~10-15 minutes

**Process:**
1. Deploys to isolated test environment
2. Starts all infrastructure services (Redis, ArangoDB, Consul, Meilisearch)
3. Starts backend and frontend services
4. Runs smoke tests
5. Runs integration tests
6. Validates service health
7. Cleans up test environment

**What to Do if It Fails:**
```bash
# Test locally
docker-compose -f docker-compose.test.yml up -d
cd tests
TEST_BACKEND_URL=http://localhost:8001 TEST_FRONTEND_URL=http://localhost:3001 pytest e2e/test_environment_smoke_tests.py -v

# Check service logs
docker logs symphainy-backend-test
docker logs symphainy-frontend-test
```

**Gate:** ❌ **BLOCKS** deployment if failed

---

#### 6. **Phase 5: Deployment**

**Duration:** ~5-10 minutes

**Staging Deployment** (develop branch):
- Deploys to staging environment
- Available for QA/testing

**Production Deployment** (main branch):
- Deploys to production environment
- Live for end users

**Gate:** ✅ Only runs if all previous phases pass

---

## Phase Gates Explained

### What is a Phase Gate?

A **phase gate** is a checkpoint that must pass before the pipeline continues. If a gate fails, the pipeline stops and deployment is blocked.

### Our Phase Gates

| Phase | Gate | Blocks Deployment? | Time |
|-------|------|-------------------|------|
| 1. Code Quality | poetry.lock validation | ✅ Yes | ~2 min |
| 1. Code Quality | Code formatting | ✅ Yes | ~1 min |
| 1. Code Quality | Linting | ✅ Yes | ~2 min |
| 2. Testing | Unit tests | ✅ Yes | ~5 min |
| 2. Testing | Integration tests | ✅ Yes | ~5 min |
| 2. Testing | E2E tests | ✅ Yes | ~10 min |
| 3. Quality Gates | Code coverage (>= 80%) | ✅ Yes | ~3 min |
| 3. Quality Gates | Security scanning | ✅ Yes | ~5 min |
| 3. Quality Gates | Code quality | ✅ Yes | ~2 min |
| 4. Test Environment | Smoke tests | ✅ Yes | ~5 min |
| 4. Test Environment | Integration tests | ✅ Yes | ~5 min |

**Total Pipeline Time:** ~30-50 minutes (depending on test execution time)

---

## For Developers

### Before You Push

1. **Run Tests Locally:**
   ```bash
   cd tests
   pytest unit/ -v --cov=../symphainy-platform --cov-fail-under=80
   pytest integration/ -v
   ```

2. **Check Code Formatting:**
   ```bash
   black --check symphainy-platform tests
   # If fails, fix with:
   black symphainy-platform tests
   ```

3. **Check Linting:**
   ```bash
   flake8 symphainy-platform --count --select=E9,F63,F7,F82
   ```

4. **Update poetry.lock (if needed):**
   ```bash
   cd symphainy-platform
   poetry lock
   git add poetry.lock
   ```

### Understanding Pipeline Status

**Green Checkmark (✅):** All gates passed, deployment successful

**Red X (❌):** One or more gates failed, deployment blocked

**Yellow Circle (⏳):** Pipeline in progress

### Common Issues and Fixes

#### Issue: "poetry.lock validation failed"
**Fix:**
```bash
cd symphainy-platform
poetry lock
git add poetry.lock
git commit -m "Update poetry.lock"
git push
```

#### Issue: "Code coverage below 80%"
**Fix:**
```bash
# Check coverage
pytest tests/unit/ -v --cov=../symphainy-platform --cov-report=html
open htmlcov/index.html

# Add tests for uncovered code
# Aim for >= 80% coverage
```

#### Issue: "Security vulnerabilities found"
**Fix:**
```bash
# Check vulnerabilities
cd symphainy-platform
safety check
pip-audit --desc

# Update vulnerable packages
pip install --upgrade <vulnerable-package>
# Update requirements.txt
# Update poetry.lock
```

#### Issue: "Test environment validation failed"
**Fix:**
```bash
# Test locally
docker-compose -f docker-compose.test.yml up -d
# Check logs
docker logs symphainy-backend-test
# Fix issues
docker-compose -f docker-compose.test.yml down
```

---

## For DevOps/Platform Engineers

### Pipeline Configuration

**Main Workflows:**
- `.github/workflows/ci-cd-pipeline.yml` - Main CI/CD pipeline
- `.github/workflows/three-tier-deployment.yml` - Three-tier deployment
- `.github/workflows/quality-gates.yml` - Quality gates workflow
- `.github/workflows/test-environment.yml` - Test environment workflow

### Environment Variables

**Required Secrets:**
- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `ARANGO_URL` - ArangoDB connection string
- `CONSUL_URL` - Consul connection string
- `MEILISEARCH_URL` - Meilisearch connection string

**Optional Secrets:**
- `CODECOV_TOKEN` - Code coverage reporting
- `SLACK_WEBHOOK_URL` - Slack notifications

### Monitoring Pipeline Health

**Key Metrics:**
- Pipeline success rate
- Average pipeline duration
- Test failure rate
- Coverage trends
- Security vulnerability count

**Dashboard:**
- GitHub Actions workflow runs
- Code coverage reports
- Security scan reports

### Troubleshooting Pipeline Issues

#### Pipeline Stuck/Hanging

1. Check GitHub Actions runner status
2. Check for resource constraints (disk space, memory)
3. Review workflow logs for errors
4. Cancel and restart if needed

#### Test Environment Issues

1. Check Docker resources
2. Verify infrastructure services are healthy
3. Review test environment logs
4. Clean up test environment: `docker-compose -f docker-compose.test.yml down -v`

#### Deployment Failures

1. Check deployment logs
2. Verify environment variables
3. Check service health endpoints
4. Review rollback procedures

---

## Troubleshooting

### Pipeline Not Triggering

**Check:**
- Branch name (must be `develop` or `main`)
- Workflow file syntax
- GitHub Actions permissions

**Fix:**
```bash
# Check workflow syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci-cd-pipeline.yml'))"
```

### Tests Failing Intermittently

**Common Causes:**
- Race conditions
- Timing issues
- Resource constraints
- Network issues

**Fix:**
- Add retries to flaky tests
- Increase timeouts
- Check for resource leaks
- Review test isolation

### Coverage Below Threshold

**Check:**
```bash
pytest tests/unit/ -v --cov=../symphainy-platform --cov-report=html
open htmlcov/index.html
```

**Fix:**
- Add tests for uncovered code
- Remove dead code
- Update coverage configuration if needed

---

## Best Practices

### For Developers

1. **Run Tests Locally First**
   - Catch issues before pushing
   - Save time and resources

2. **Keep Coverage High**
   - Aim for >= 80% coverage
   - Add tests for new features

3. **Fix Linting Issues**
   - Use `black` for formatting
   - Fix critical linting errors

4. **Update Dependencies Carefully**
   - Update `poetry.lock` when adding dependencies
   - Test after dependency updates

5. **Write Meaningful Commit Messages**
   - Helps with debugging
   - Improves code review process

### For DevOps

1. **Monitor Pipeline Health**
   - Track success rates
   - Monitor pipeline duration
   - Review failure patterns

2. **Keep Infrastructure Updated**
   - Update GitHub Actions versions
   - Keep security tools updated
   - Monitor resource usage

3. **Document Changes**
   - Update this guide when pipeline changes
   - Document new quality gates
   - Share best practices

4. **Optimize Pipeline Performance**
   - Use caching where possible
   - Run tests in parallel
   - Optimize test execution time

---

## When to Consider Phase 5

### What is Phase 5?

Phase 5 includes advanced deployment strategies:
- **Blue-Green Deployment** - Zero-downtime deployments
- **Canary Deployments** - Gradual rollout
- **Advanced Monitoring** - Real-time metrics and alerts
- **Automated Rollback** - Automatic failure recovery

### When Should You Consider Phase 5?

Consider Phase 5 when you have:

#### 1. **High Traffic/User Base**
- ✅ > 10,000 daily active users
- ✅ Critical business operations depend on platform
- ✅ Zero-downtime requirements

**Why:** Blue-green deployment ensures zero downtime during deployments.

#### 2. **Frequent Deployments**
- ✅ Multiple deployments per day
- ✅ Need for rapid iteration
- ✅ Quick rollback requirements

**Why:** Advanced deployment strategies reduce deployment risk and enable faster iteration.

#### 3. **Complex Infrastructure**
- ✅ Multiple services/environments
- ✅ Database migrations required
- ✅ Service dependencies

**Why:** Advanced monitoring and automated rollback handle complex scenarios.

#### 4. **Compliance/Security Requirements**
- ✅ Regulatory compliance needs
- ✅ Security audit requirements
- ✅ Data protection requirements

**Why:** Advanced monitoring and audit trails meet compliance needs.

#### 5. **Team Maturity**
- ✅ DevOps team in place
- ✅ Monitoring infrastructure ready
- ✅ Budget for advanced tooling

**Why:** Phase 5 requires more sophisticated infrastructure and expertise.

### Phase 5 Components

#### Blue-Green Deployment

**What:** Deploy new version alongside current version, switch traffic when ready.

**Benefits:**
- Zero downtime
- Instant rollback
- Safe testing of new version

**Requirements:**
- Load balancer support
- Database migration strategy
- Session management

#### Canary Deployment

**What:** Gradually roll out new version to subset of users.

**Benefits:**
- Risk mitigation
- Real-world testing
- Gradual rollout

**Requirements:**
- Traffic splitting capability
- Monitoring and alerting
- Rollback procedures

#### Advanced Monitoring

**What:** Real-time metrics, alerts, and dashboards.

**Benefits:**
- Early issue detection
- Performance optimization
- User experience insights

**Requirements:**
- Monitoring infrastructure (Prometheus, Grafana)
- Alerting system
- Log aggregation

#### Automated Rollback

**What:** Automatic rollback on failure detection.

**Benefits:**
- Reduced downtime
- Faster recovery
- Reduced manual intervention

**Requirements:**
- Health check endpoints
- Monitoring integration
- Rollback automation

### Current Status vs Phase 5

| Feature | Current (Phase 1-4) | Phase 5 |
|---------|-------------------|---------|
| Deployment Strategy | Direct deployment | Blue-green/Canary |
| Downtime | Minimal (seconds) | Zero |
| Rollback | Manual | Automated |
| Monitoring | Basic | Advanced |
| Traffic Splitting | No | Yes |
| Database Migrations | Manual | Automated |

### Migration Path to Phase 5

1. **Assess Current Needs**
   - Evaluate traffic patterns
   - Identify pain points
   - Define requirements

2. **Plan Infrastructure**
   - Design blue-green architecture
   - Plan monitoring setup
   - Design rollback procedures

3. **Implement Gradually**
   - Start with staging
   - Test thoroughly
   - Roll out to production

4. **Monitor and Optimize**
   - Track metrics
   - Optimize performance
   - Refine processes

### Recommendation

**Current Phase (1-4) is Sufficient If:**
- ✅ < 10,000 daily active users
- ✅ Few deployments per week
- ✅ Simple infrastructure
- ✅ Limited DevOps resources

**Consider Phase 5 If:**
- ✅ > 10,000 daily active users
- ✅ Multiple deployments per day
- ✅ Zero-downtime requirements
- ✅ Complex infrastructure
- ✅ DevOps team ready

---

## Summary

Our CI/CD pipeline ensures high-quality, secure code reaches production through:

1. **Code Quality Gates** - Formatting, linting, validation
2. **Comprehensive Testing** - Unit, integration, E2E tests
3. **Quality Gates** - Coverage, security, code quality
4. **Test Environment Validation** - Real environment testing
5. **Safe Deployment** - Staging → Production

**Pipeline Time:** ~30-50 minutes  
**Quality Standards:** 80%+ coverage, no vulnerabilities, code quality enforced  
**Deployment Safety:** Multiple gates ensure only validated code deploys

---

**Questions?** Contact the DevOps team or refer to the troubleshooting section.

**Last Updated:** December 1, 2025


