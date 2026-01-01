# Development Workflow After Production Deployment

**Date:** December 2024  
**Purpose:** Guide for ongoing development after initial production deployment

---

## 🔄 **Standard Development Workflow**

### **1. Make Changes Locally**

```bash
# Navigate to project
cd /home/founders/demoversion/symphainy_source

# Make your changes
# ... edit files ...

# Test locally (recommended)
python3 -m pytest tests/e2e/production/smoke_tests/ -v
```

### **2. Commit and Push**

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Fix: Description of what you fixed"

# Push to repository
git push origin main
# or
git push origin develop  # if using develop branch
```

### **3. Deploy to Production**

#### **Option A: Manual Deployment (Current - Recommended)**

```bash
# SSH into VM
ssh founders@35.215.64.103

# Navigate to project
cd /home/founders/demoversion/symphainy_source

# Pull latest code
git pull origin main

# Deploy
./scripts/vm-staging-deploy.sh

# Verify deployment
curl http://localhost:8000/health
curl http://localhost:3000
```

#### **Option B: Automated CI/CD (If Configured)**

```bash
# Just push - CI/CD handles the rest
git push origin main

# Monitor deployment:
# GitHub > Actions > Deploy to Production
```

---

## 📋 **Common Development Scenarios**

### **Scenario 1: Small Bug Fix**

```bash
# 1. Fix the bug locally
# ... edit file ...

# 2. Quick test (smoke tests only - fast)
python3 -m pytest tests/e2e/production/smoke_tests/ -v

# 3. Commit and push
git add .
git commit -m "Fix: Bug description"
git push origin main

# 4. Deploy
ssh founders@35.215.64.103
cd /home/founders/demoversion/symphainy_source
git pull
./scripts/vm-staging-deploy.sh

# 5. Verify (30 seconds)
curl http://35.215.64.103:8000/health
```

**Time:** ~5-10 minutes

---

### **Scenario 2: New Feature**

```bash
# 1. Create feature branch
git checkout -b feature/new-feature-name

# 2. Develop feature
# ... make changes ...

# 3. Test thoroughly
python3 -m pytest tests/ -v

# 4. Commit to feature branch
git add .
git commit -m "Feature: New feature description"
git push origin feature/new-feature-name

# 5. Merge to main (after review/testing)
git checkout main
git merge feature/new-feature-name
git push origin main

# 6. Deploy
ssh founders@35.215.64.103
cd /home/founders/demoversion/symphainy_source
git pull
./scripts/vm-staging-deploy.sh
```

**Time:** ~30-60 minutes (depending on feature complexity)

---

### **Scenario 3: Hotfix (Urgent)**

```bash
# 1. Make fix directly on main
git checkout main
# ... make urgent fix ...

# 2. Quick smoke test (fast validation)
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
curl http://35.215.64.103:3000
```

**Time:** ~3-5 minutes

---

### **Scenario 4: Configuration Change**

```bash
# 1. Update configuration file
# ... edit config/production.env or .env.secrets ...

# 2. Commit (if config file is in repo)
git add config/production.env  # Only if this file is tracked
git commit -m "Config: Update production settings"
git push origin main

# 3. Deploy
ssh founders@35.215.64.103
cd /home/founders/demoversion/symphainy_source
git pull

# 4. Update .env.secrets on VM (if changed)
# Edit directly on VM (not in git)
nano symphainy-platform/.env.secrets

# 5. Restart services
./scripts/vm-staging-deploy.sh
```

**Note:** `.env.secrets` is not in git, so changes must be made directly on VM.

---

## 🧪 **Testing Strategy**

### **Before Deploying:**

1. **Local Testing (Recommended)**
   ```bash
   # Quick smoke tests (fast)
   python3 -m pytest tests/e2e/production/smoke_tests/ -v
   
   # Full test suite (if time permits)
   python3 -m pytest tests/e2e/production/ -v
   ```

2. **Test Specific Areas**
   ```bash
   # Test specific pillar
   python3 -m pytest tests/e2e/production/smoke_tests/test_content_pillar_smoke.py -v
   
   # Test CTO demo scenario
   python3 -m pytest tests/e2e/production/cto_demos/test_cto_demo_1_autonomous_vehicle.py -v
   ```

### **After Deploying:**

1. **Health Checks**
   ```bash
   curl http://35.215.64.103:8000/health
   curl http://35.215.64.103:3000
   ```

2. **Verify Critical Paths**
   - Test session creation
   - Test file upload
   - Test CTO demo scenarios

3. **Monitor Logs**
   ```bash
   # On VM
   docker-compose -f docker-compose.prod.yml logs -f
   ```

---

## 🔍 **Troubleshooting Workflow**

### **If Deployment Fails:**

```bash
# 1. Check logs
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# 2. Check infrastructure
docker-compose -f docker-compose.infrastructure.yml ps

# 3. Rollback if needed
git checkout <previous-commit-hash>
./scripts/vm-staging-deploy.sh
```

### **If Tests Fail:**

```bash
# 1. Run tests locally to reproduce
python3 -m pytest tests/e2e/production/ -v

# 2. Fix the issue
# ... make fixes ...

# 3. Test again
python3 -m pytest tests/e2e/production/ -v

# 4. Commit and deploy
git add .
git commit -m "Fix: Test failure description"
git push origin main
# ... deploy ...
```

---

## 📝 **Best Practices**

### **1. Always Test Before Deploying**
- Run at least smoke tests locally
- Or rely on CI/CD to run tests automatically

### **2. Use Descriptive Commit Messages**
```bash
# Good
git commit -m "Fix: CORS configuration for production URL"
git commit -m "Feature: Add new API endpoint for file processing"

# Bad
git commit -m "fix"
git commit -m "updates"
```

### **3. Keep Secrets Updated**
- If you add new secrets to code, update `.env.secrets` on VM
- Document new secrets in `config/secrets.example`

### **4. Monitor After Deployment**
- Check logs for errors
- Verify health endpoints
- Test critical user paths

### **5. Use Feature Branches for Big Changes**
- Keep main stable
- Merge after thorough testing

---

## 🚨 **Emergency Procedures**

### **If Production is Down:**

```bash
# 1. SSH into VM
ssh founders@35.215.64.103

# 2. Check service status
docker-compose -f docker-compose.prod.yml ps

# 3. Check logs
docker-compose -f docker-compose.prod.yml logs --tail=100

# 4. Restart services
docker-compose -f docker-compose.prod.yml restart

# 5. If still failing, rollback
cd /home/founders/demoversion/symphainy_source
git log --oneline -10  # Find previous working commit
git checkout <previous-commit-hash>
./scripts/vm-staging-deploy.sh
```

### **If You Need to Rollback:**

```bash
# On VM
cd /home/founders/demoversion/symphainy_source

# Find previous working commit
git log --oneline -10

# Checkout previous commit
git checkout <commit-hash>

# Redeploy
./scripts/vm-staging-deploy.sh
```

---

## 📊 **Development Workflow Summary**

```
┌─────────────────────────────────────────┐
│ 1. Develop Locally                      │
│    - Make changes                       │
│    - Test locally                       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. Commit & Push                        │
│    - git add .                           │
│    - git commit -m "..."                │
│    - git push origin main                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. Deploy                                │
│    - SSH into VM                         │
│    - git pull                            │
│    - ./scripts/vm-staging-deploy.sh      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. Verify                                │
│    - Health checks                       │
│    - Test critical paths                 │
│    - Monitor logs                        │
└─────────────────────────────────────────┘
```

---

**Last Updated:** December 2024


