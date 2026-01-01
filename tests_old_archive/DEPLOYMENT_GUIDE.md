# Production Deployment Guide - GCE VM

**Target:** GCE VM at `35.215.64.103:3000`  
**Purpose:** Deploy SymphAIny Platform for CTO demo

---

## 🎯 **Quick Start**

### **Prerequisites:**
1. SSH access to GCE VM (35.215.64.103)
2. Docker and Docker Compose installed
3. Git repository access
4. `.env.secrets` file with all required secrets

---

## 📋 **Deployment Steps**

**Note:** The deployment script (`vm-staging-deploy.sh`) has been updated to:
- ✅ Start infrastructure services automatically (ArangoDB, Redis, Consul, Meilisearch, Celery, etc.)
- ✅ Handle dependencies automatically (Poetry installs during Docker build)
- ✅ Start services in proper order

You can use the script directly, or follow the manual steps below if you prefer.

### **Step 1: Initial VM Setup (One-Time)**

```bash
# SSH into VM
ssh founders@35.215.64.103

# Navigate to project directory
cd /home/founders/demoversion/symphainy_source

# Ensure Docker is running
sudo systemctl start docker
sudo systemctl enable docker

# Verify Docker Compose
docker-compose --version
```

### **Step 2: Verify Secrets**

**Since `.env.secrets` already exists, just verify it's on the VM and up-to-date:**

```bash
# On VM, verify file exists
ls -la /home/founders/demoversion/symphainy_source/symphainy-platform/.env.secrets

# Verify it has all required secrets (compare with config/secrets.example)
# Check for:
# - ARANGO_PASS
# - REDIS_PASSWORD
# - SUPABASE_URL, SUPABASE_SERVICE_KEY
# - LLM_OPENAI_API_KEY
# - SECRET_KEY, JWT_SECRET
```

**If file doesn't exist on VM or needs updating:**
```bash
# Option A: Transfer from local (if you have it locally)
scp symphainy-platform/.env.secrets founders@35.215.64.103:/home/founders/demoversion/symphainy_source/symphainy-platform/.env.secrets

# Option B: Create on VM from template (if needed)
cd /home/founders/demoversion/symphainy_source/symphainy-platform
cp config/secrets.example .env.secrets
# Edit .env.secrets with actual values
nano .env.secrets
```

### **Step 3: Deploy Frontend Environment Variables**

**Note:** You mentioned you already have both `.env` and `.env.local` updated. For production, Next.js will use:
- `.env.production` (if it exists)
- `.env.production.local` (if it exists, takes precedence)
- `.env.local` (fallback)
- `.env` (fallback)

**Verify your frontend environment variables:**

```bash
# On VM
cd /home/founders/demoversion/symphainy_source/symphainy-frontend

# Check existing files
ls -la .env* 

# For production, create .env.production (recommended)
cat > .env.production << EOF
NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103:8000
NEXT_PUBLIC_API_URL=http://35.215.64.103:8000
NEXT_PUBLIC_SUPABASE_URL=https://rmymvrifwvqpeffmxkwi.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here
EOF

# Or if you prefer to keep using .env.local, that's fine too
# Next.js will use it in production
```

**Required Variables:**
```bash
NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103:8000
NEXT_PUBLIC_API_URL=http://35.215.64.103:8000
NEXT_PUBLIC_SUPABASE_URL=https://rmymvrifwvqpeffmxkwi.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### **Step 4: Deploy Infrastructure Services**

**Important:** The deployment script (`vm-staging-deploy.sh`) now handles infrastructure startup automatically, but you can also start it manually first if needed.

**Infrastructure Services Included:**
- ✅ ArangoDB (database)
- ✅ Redis (cache/message broker)
- ✅ Consul (service discovery)
- ✅ Meilisearch (search engine)
- ✅ Celery Worker (background tasks)
- ✅ Celery Beat (task scheduler)
- ✅ Tempo (distributed tracing)
- ✅ OpenTelemetry Collector (observability)
- ✅ Grafana (monitoring)
- ✅ OPA (policy engine)

**Manual Start (Optional - script does this automatically):**

```bash
# On VM
cd /home/founders/demoversion/symphainy_source/symphainy-platform

# Start all infrastructure services
docker-compose -f docker-compose.infrastructure.yml up -d

# Wait for services to be ready
sleep 20

# Verify infrastructure
docker-compose -f docker-compose.infrastructure.yml ps
```

**Note:** The deployment script will start infrastructure automatically, so you don't need to do this manually unless you want to verify it separately.

### **Step 5: Deploy Application**

**Note About Dependencies:**
- **Docker containers:** Dependencies are installed automatically during `docker-compose build` (Poetry handles this in Dockerfile)
- **If running outside Docker:** Use `startup.sh` script which handles Poetry installation and dependency management

```bash
# On VM
cd /home/founders/demoversion/symphainy_source

# Use deployment script
chmod +x scripts/vm-staging-deploy.sh
./scripts/vm-staging-deploy.sh
```

**Or manually:**
```bash
# Build and start containers
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### **Step 6: Verify Deployment**

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 🔧 **Configuration Files**

### **Backend Secrets:**
- **Location:** `symphainy-platform/.env.secrets`
- **Required Variables:**
  - `ARANGO_PASS` - ArangoDB password
  - `REDIS_PASSWORD` - Redis password
  - `SUPABASE_URL` - Supabase project URL
  - `SUPABASE_SERVICE_KEY` - Supabase service key
  - `LLM_OPENAI_API_KEY` - OpenAI API key
  - `SECRET_KEY` - Platform secret key
  - `JWT_SECRET` - JWT signing secret

### **Frontend Environment:**
- **Location:** `symphainy-frontend/.env.production`
- **Required Variables:**
  - `NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103:8000`
  - `NEXT_PUBLIC_SUPABASE_URL` - Supabase URL
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key

### **Production Config:**
- **Location:** `symphainy-platform/config/production.env`
- **Status:** ✅ Already configured with correct CORS origins

---

## 🔥 **Firewall Configuration**

**GCE VM Firewall Rules Required:**

```bash
# Allow HTTP traffic on port 3000 (frontend)
gcloud compute firewall-rules create allow-frontend \
  --allow tcp:3000 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow frontend access"

# Allow HTTP traffic on port 8000 (backend - optional, may be internal only)
gcloud compute firewall-rules create allow-backend \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow backend API access"
```

**Or via GCP Console:**
1. Go to VPC Network > Firewall Rules
2. Create rule for port 3000 (frontend)
3. Create rule for port 8000 (backend, if needed externally)

---

## 🚀 **CI/CD Deployment (Automated - Optional)**

### **Option A: Manual Deployment (Recommended - Safest)**

Since you already have working SSH access, you can use manual deployment:

```bash
# Push to main branch
git push origin main

# Then SSH and deploy manually
ssh founders@35.215.64.103
cd /home/founders/demoversion/symphainy_source
git pull
./scripts/vm-staging-deploy.sh
```

**Benefits:**
- ✅ No risk to existing SSH access
- ✅ Full control over deployment timing
- ✅ Can verify before deploying

### **Option B: Automated CI/CD (If You Want Full Automation)**

If you want automated deployment, you can set up CI/CD:

#### **Setup GitHub Secrets (Only if using CI/CD):**

1. **Option B1: Use Existing SSH Key (If Available)**
   - If your existing SSH private key is available (not just on your local machine)
   - Add it to GitHub Secrets as `GCE_SSH_KEY`
   - CI/CD uses same key you use manually

2. **Option B2: Create Separate CI/CD Key (Safest for Automation)**
   - Generate NEW key specifically for CI/CD (different from your existing one):
     ```bash
     ssh-keygen -t ed25519 -C "github-actions-ci-cd" -f ~/.ssh/github_actions_deploy
     ```
   - Add public key to VM (as a NEW authorized key - doesn't replace existing):
     ```bash
     ssh-copy-id -i ~/.ssh/github_actions_deploy.pub founders@35.215.64.103
     ```
   - Add private key to GitHub Secrets:
     - Go to GitHub repository > Settings > Secrets and variables > Actions
     - Add secret: `GCE_SSH_KEY`
     - Value: Contents of `~/.ssh/github_actions_deploy` (private key)

**Why Option B2 is Safe:**
- ✅ Doesn't touch your existing SSH key
- ✅ Adds a new authorized key (doesn't remove existing ones)
- ✅ If something goes wrong, you still have your original SSH access
- ✅ Can be removed independently if needed

#### **Deploy via GitHub Actions:**

```bash
# Push to main branch triggers deployment
git push origin main

# Or trigger manually:
# GitHub > Actions > Deploy to Production > Run workflow
```

**Recommendation:** Start with **Option A (Manual Deployment)** for the CTO demo, then add CI/CD later if desired.

---

## 🔍 **Troubleshooting**

### **Backend Won't Start:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Check if .env.secrets exists
ls -la symphainy-platform/.env.secrets

# Check infrastructure services
docker-compose -f docker-compose.infrastructure.yml ps
```

### **Frontend Won't Start:**
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs frontend

# Check if .env.production exists
ls -la symphainy-frontend/.env.production

# Verify build
cd symphainy-frontend
npm run build
```

### **CORS Errors:**
```bash
# Verify CORS configuration
grep API_CORS_ORIGINS symphainy-platform/config/production.env

# Should show: API_CORS_ORIGINS=http://35.215.64.103:3000,http://localhost:3000
```

### **Port Already in Use:**
```bash
# Find process using port
sudo lsof -i :3000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 <PID>
```

---

## 📊 **Post-Deployment Verification**

### **1. Health Checks:**
```bash
# Backend
curl http://35.215.64.103:8000/health

# Frontend
curl http://35.215.64.103:3000
```

### **2. API Endpoints:**
```bash
# Test session creation
curl -X POST http://35.215.64.103:8000/api/v1/session/create-user-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "session_type": "mvp"}'
```

### **3. CTO Demo Scenarios:**
- Run production E2E tests
- Verify all 3 demo scenarios work
- Test file uploads
- Test all 4 pillars

---

## 🔄 **Update Process**

### **Manual Update:**
```bash
# SSH into VM
ssh founders@35.215.64.103

# Pull latest code
cd /home/founders/demoversion/symphainy_source
git pull origin main

# Redeploy
./scripts/vm-staging-deploy.sh
```

### **Automated Update (CI/CD):**
- Push to `main` branch
- GitHub Actions automatically deploys
- Health checks run automatically

---

## 📝 **Maintenance**

### **View Logs:**
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### **Restart Services:**
```bash
# Restart all
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### **Stop Services:**
```bash
# Stop application
docker-compose -f docker-compose.prod.yml down

# Stop infrastructure (careful - this stops databases)
docker-compose -f docker-compose.infrastructure.yml down
```

---

## ✅ **Pre-Demo Checklist**

- [ ] Infrastructure services running (ArangoDB, Redis, Consul)
- [ ] Backend deployed and healthy (`/health` returns 200)
- [ ] Frontend deployed and accessible
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] Firewall rules configured
- [ ] Health checks passing
- [ ] CTO demo scenarios tested
- [ ] Logs monitored for errors
- [ ] Backup of `.env.secrets` created

---

**Last Updated:** December 2024

