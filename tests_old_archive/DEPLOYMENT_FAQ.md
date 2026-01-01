# Deployment FAQ - Answers to Common Questions

**Date:** December 2024

---

## 1. `.env.secrets` Already Exists - What Changes?

**Question:** We already have `symphainy-platform/.env.secrets`. Does this change the deployment setup?

**Answer:** ✅ **Yes - This Simplifies Deployment!**

Since `.env.secrets` already exists, you don't need to create it from scratch. However, you should:

### **Pre-Deployment Checklist:**
1. ✅ **Verify `.env.secrets` is on VM** (if deploying from local)
   ```bash
   # On VM, check if file exists
   ls -la /home/founders/demoversion/symphainy_source/symphainy-platform/.env.secrets
   ```

2. ✅ **Verify it has all required secrets** (compare with `config/secrets.example`)
   - Database passwords
   - API keys
   - Supabase credentials
   - JWT secrets

3. ✅ **Update if needed** (add any new secrets that were added to codebase)

### **Updated Deployment Steps:**
- **Skip:** "Create .env.secrets from template"
- **Do:** "Verify .env.secrets exists and has all required values"
- **Do:** "Update .env.secrets if new secrets were added"

---

## 2. SSH Connection Already Works - Do We Need a Separate One?

**Question:** We already have SSH access to the VM. Do we need a separate SSH key for CI/CD?

**Answer:** ⚠️ **It Depends - But We Can Avoid It!**

### **Option A: Use Existing SSH (Recommended - Safer)**

Since you already have working SSH access, you have two safe options:

#### **Option A1: Manual Deployment (Safest)**
- Keep using your existing SSH connection
- Deploy manually when needed
- No risk of breaking existing access
- **Workflow:** Push to repo → SSH into VM → Pull and deploy

#### **Option A2: Use Existing SSH Key in CI/CD (If Available)**
- If your existing SSH private key is available (not just in your local machine)
- Add it to GitHub Secrets as `GCE_SSH_KEY`
- CI/CD uses same key you use manually
- **Risk:** Low (same key you already use)

### **Option B: Create Separate CI/CD Key (If You Want Full Automation)**

If you want automated CI/CD, create a **separate** SSH key **only for CI/CD**:

```bash
# Generate NEW key specifically for CI/CD (different from your existing one)
ssh-keygen -t ed25519 -C "github-actions-ci-cd" -f ~/.ssh/github_actions_deploy

# Add public key to VM (as a NEW authorized key - doesn't replace existing)
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub founders@35.215.64.103

# Add private key to GitHub Secrets
# GitHub > Settings > Secrets > Actions > New secret
# Name: GCE_SSH_KEY
# Value: Contents of ~/.ssh/github_actions_deploy (private key)
```

**Why This is Safe:**
- ✅ Doesn't touch your existing SSH key
- ✅ Adds a new authorized key (doesn't remove existing ones)
- ✅ If something goes wrong, you still have your original SSH access
- ✅ Can be removed independently if needed

### **Recommendation:**

**For Now (CTO Demo):** Use **Option A1 (Manual Deployment)**
- Zero risk to existing SSH access
- Simple and reliable
- You can always add CI/CD later

**Later (If You Want Automation):** Use **Option B (Separate CI/CD Key)**
- Full automation
- Safe (doesn't touch existing access)
- Can be tested without affecting your main SSH

---

## 3. How to Incorporate Tests into CI/CD?

**Question:** How should we think about incorporating our robust `/tests/` environment into CI/CD?

**Answer:** ✅ **Run Tests Before Deployment!**

### **Recommended CI/CD Flow:**

```
1. Code Push → Trigger CI/CD
2. Run Tests → If tests pass, continue
3. Build Docker Images → If build succeeds, continue
4. Deploy to VM → If deployment succeeds, continue
5. Health Checks → Verify deployment
```

### **Updated CI/CD Pipeline:**

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd symphainy-platform
          pip install poetry
          poetry install
      
      - name: Run tests
        run: |
          cd tests
          pytest tests/e2e/production/ -v
        env:
          TEST_BACKEND_URL: http://localhost:8000
  
  deploy:
    needs: test  # Only deploy if tests pass
    runs-on: ubuntu-latest
    if: success()  # Only run if test job succeeded
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to GCE VM
        # ... deployment steps
```

### **Test Strategy in CI/CD:**

1. **Smoke Tests (Fast - ~10 seconds)**
   - Run first
   - Quick validation
   - Fail fast if basic issues

2. **API Contract Tests (Medium - ~30 seconds)**
   - Verify API endpoints exist
   - Check response structures

3. **CTO Demo Tests (Slower - ~2 minutes)**
   - Full E2E validation
   - Run if smoke tests pass

4. **Playwright Tests (Optional - ~5 minutes)**
   - Run in separate job (can be parallel)
   - Or run only on manual trigger

### **Alternative: Test on VM Before Deployment**

If you want to test on the actual VM environment:

```yaml
test-on-vm:
  runs-on: ubuntu-latest
  steps:
    - name: Run tests on VM
      uses: appleboy/ssh-action@master
      with:
        host: 35.215.64.103
        username: founders
        key: ${{ secrets.GCE_SSH_KEY }}
        script: |
          cd /home/founders/demoversion/symphainy_source
          python3 -m pytest tests/e2e/production/ -v
```

---

## 4. Development Workflow After Deployment

**Question:** What does our development process look like after deployment?

**Answer:** 📋 **Here's the Recommended Workflow:**

### **Development Workflow:**

```
┌─────────────────────────────────────────────────────────┐
│ 1. Develop Locally                                      │
│    - Make changes                                       │
│    - Test locally                                       │
│    - Run tests: pytest tests/e2e/production/ -v        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Commit & Push                                        │
│    - Commit to feature branch or main                   │
│    - Push to GitHub                                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. CI/CD Pipeline (If Configured)                      │
│    - Run tests automatically                            │
│    - If tests pass → Deploy automatically               │
│    - If tests fail → Stop, notify, fix                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Manual Deployment (If No CI/CD)                      │
│    - SSH into VM                                        │
│    - Pull latest code                                    │
│    - Run deployment script                               │
│    - Verify health checks                                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Verify & Monitor                                     │
│    - Check logs                                          │
│    - Run health checks                                   │
│    - Test CTO demo scenarios                             │
└─────────────────────────────────────────────────────────┘
```

### **Detailed Workflow:**

#### **Scenario A: Small Fix/Update**

```bash
# 1. Make changes locally
cd /home/founders/demoversion/symphainy_source
# ... edit files ...

# 2. Test locally (optional but recommended)
python3 -m pytest tests/e2e/production/smoke_tests/ -v

# 3. Commit and push
git add .
git commit -m "Fix: Description of fix"
git push origin main

# 4. Deploy (if manual)
ssh founders@35.215.64.103
cd /home/founders/demoversion/symphainy_source
git pull
./scripts/vm-staging-deploy.sh

# 5. Verify
curl http://35.215.64.103:8000/health
curl http://35.215.64.103:3000
```

#### **Scenario B: New Feature**

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Develop and test locally
# ... make changes ...
python3 -m pytest tests/ -v

# 3. Commit to feature branch
git add .
git commit -m "Feature: New feature description"
git push origin feature/new-feature

# 4. Merge to main (after review)
git checkout main
git merge feature/new-feature
git push origin main

# 5. Deploy (automatic if CI/CD, manual if not)
```

#### **Scenario C: Hotfix (Urgent Fix Needed)**

```bash
# 1. Make fix directly on main (or hotfix branch)
git checkout main
# ... make urgent fix ...

# 2. Test quickly (smoke tests only)
python3 -m pytest tests/e2e/production/smoke_tests/ -v

# 3. Commit and push
git add .
git commit -m "Hotfix: Urgent fix description"
git push origin main

# 4. Deploy immediately
ssh founders@35.215.64.103
cd /home/founders/demoversion/symphainy_source
git pull
./scripts/vm-staging-deploy.sh

# 5. Verify immediately
curl http://35.215.64.103:8000/health
```

### **Best Practices:**

1. **Always Test Before Deploying**
   - Run at least smoke tests locally
   - Or rely on CI/CD to run tests

2. **Use Feature Branches for New Features**
   - Keep main stable
   - Merge after testing

3. **Monitor After Deployment**
   - Check logs: `docker-compose logs -f`
   - Verify health endpoints
   - Test critical paths

4. **Rollback Plan**
   ```bash
   # If deployment fails, rollback to previous version
   git checkout <previous-commit-hash>
   ./scripts/vm-staging-deploy.sh
   ```

5. **Keep Secrets Updated**
   - If you add new secrets to code, update `.env.secrets` on VM
   - Document new secrets in `config/secrets.example`

---

## Summary

1. **`.env.secrets` exists:** ✅ Just verify it has all required values, no need to create from scratch

2. **SSH connection:** ✅ Use existing connection for manual deployment (safest), or create separate CI/CD key if you want automation (doesn't affect existing access)

3. **Tests in CI/CD:** ✅ Run tests before deployment - add test job to CI/CD pipeline

4. **Development workflow:** ✅ Develop → Test → Commit → Deploy → Verify

---

**Last Updated:** December 2024


