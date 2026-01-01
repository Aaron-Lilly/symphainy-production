# Inline Deployment Guide - Step by Step

**Date:** December 2024  
**Purpose:** Deploy together and troubleshoot in real-time

---

## 🚀 **Step-by-Step Deployment**

Run each command and report back what you see. We'll troubleshoot as we go!

---

### **Step 1: Connect to VM and Check Current State**

```bash
# SSH into VM
ssh founders@35.215.64.103

# Navigate to project
cd /home/founders/demoversion/symphainy_source

# Check current directory
pwd
```

**Report back:** What directory are you in?

---

### **Step 2: Check Git Status**

```bash
# Check git status
git status

# Check current branch
git branch
```

**Report back:** 
- What branch are you on?
- Are there any uncommitted changes?

---

### **Step 3: Pull Latest Code**

```bash
# Pull latest code
git fetch origin
git pull origin main
# OR if you're on develop:
# git pull origin develop

# Check what we got
git log -1 --oneline
```

**Report back:** 
- Did the pull succeed?
- What's the latest commit?

---

### **Step 4: Verify Required Files**

```bash
# Check .env.secrets exists
ls -la symphainy-platform/.env.secrets

# Check frontend env files
ls -la symphainy-frontend/.env*

# Check deployment script exists and is executable
ls -la scripts/vm-staging-deploy.sh
chmod +x scripts/vm-staging-deploy.sh
```

**Report back:**
- Does `.env.secrets` exist?
- What frontend env files do you see?
- Is the deployment script executable?

---

### **Step 5: Check Docker**

```bash
# Check Docker is running
docker --version
docker-compose --version

# Check if Docker daemon is running
docker ps
```

**Report back:**
- Docker versions?
- Is Docker daemon running?

---

### **Step 6: Check Current Containers**

```bash
# See what's currently running
docker ps -a

# Check infrastructure services
cd symphainy-platform
docker-compose -f docker-compose.infrastructure.yml ps 2>/dev/null || echo "Infrastructure not running"
cd ..
```

**Report back:**
- What containers are running?
- Are infrastructure services already up?

---

### **Step 7: Run Deployment Script**

```bash
# Make sure we're in the right directory
cd /home/founders/demoversion/symphainy_source

# Run deployment script
./scripts/vm-staging-deploy.sh
```

**Report back:**
- What output do you see?
- Any errors?
- Does it complete successfully?

---

### **Step 8: Verify Infrastructure Services**

```bash
# Check infrastructure services are running
cd symphainy-platform
docker-compose -f docker-compose.infrastructure.yml ps

# Check specific services
docker ps | grep -E "arangodb|redis|consul|meilisearch|celery"
```

**Report back:**
- Are all infrastructure services running?
- Any services failing?

---

### **Step 9: Verify Application Services**

```bash
# Check application services
cd /home/founders/demoversion/symphainy_source
docker-compose -f docker-compose.prod.yml ps

# Check logs if needed
docker-compose -f docker-compose.prod.yml logs backend | tail -20
docker-compose -f docker-compose.prod.yml logs frontend | tail -20
```

**Report back:**
- Are backend and frontend running?
- Any errors in logs?

---

### **Step 10: Health Checks**

```bash
# Check backend health
curl -f http://localhost:8000/health

# Check frontend
curl -f http://localhost:3000

# Check from outside (if firewall allows)
curl -f http://35.215.64.103:8000/health
curl -f http://35.215.64.103:3000
```

**Report back:**
- Do health checks pass?
- Can you access from outside?

---

## 🔍 **Troubleshooting Commands**

If something goes wrong, run these and share the output:

```bash
# Check all container logs
docker-compose -f docker-compose.prod.yml logs --tail=50

# Check infrastructure logs
cd symphainy-platform
docker-compose -f docker-compose.infrastructure.yml logs --tail=50

# Check Docker system
docker system df
docker ps -a

# Check disk space
df -h

# Check if ports are in use
sudo lsof -i :8000
sudo lsof -i :3000
sudo lsof -i :8529
sudo lsof -i :6379
```

---

## 📋 **Quick Checklist**

- [ ] Connected to VM
- [ ] In correct directory
- [ ] Git status checked
- [ ] Latest code pulled
- [ ] Required files verified
- [ ] Docker running
- [ ] Deployment script executed
- [ ] Infrastructure services running
- [ ] Application services running
- [ ] Health checks passing

---

**Let's start with Step 1! Run the commands and tell me what you see.**

