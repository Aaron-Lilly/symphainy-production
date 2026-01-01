# Three-Tier Deployment Setup Guide
**Configure GitHub Secrets for VM Staging + Cloud Run Production**

---

## 🎯 **OVERVIEW**

Your three-tier deployment requires specific GitHub Secrets to enable:
1. **Tier 2:** SSH deployment to your GCP VM (staging)
2. **Tier 3:** Deployment to Google Cloud Run (production)

---

## 📝 **REQUIRED GITHUB SECRETS**

Go to: **GitHub → Settings → Secrets and variables → Actions → New repository secret**

### **For VM Staging (Tier 2):**

| Secret Name | Value | How to Get It |
|-------------|-------|---------------|
| `GCP_VM_IP` | Your VM's external IP | `gcloud compute instances list` |
| `GCP_VM_USERNAME` | SSH username (probably `founders`) | Your SSH username |
| `GCP_VM_SSH_KEY` | Private SSH key | See instructions below |

### **For Cloud Run Production (Tier 3):**

| Secret Name | Value | How to Get It |
|-------------|-------|---------------|
| `GCP_PROJECT_ID` | Your GCP project ID | `gcloud config get-value project` |
| `GCP_SA_KEY` | Service account JSON key | See instructions below |

### **For Notifications:**

| Secret Name | Value | How to Get It |
|-------------|-------|---------------|
| `SLACK_WEBHOOK` | Slack webhook URL | Slack → Create webhook |

---

## 🔧 **STEP-BY-STEP SETUP**

### **Step 1: Get VM External IP**

```bash
# On your VM or local machine with gcloud
gcloud compute instances list

# Look for your VM and note the EXTERNAL_IP
# Example: 34.123.45.67
```

Add to GitHub Secrets:
- Name: `GCP_VM_IP`
- Value: `34.123.45.67` (your actual IP)

---

### **Step 2: Create SSH Key for CI/CD**

**On your GCP VM:**

```bash
# SSH into your VM
ssh founders@YOUR_VM_IP

# Generate a new SSH key specifically for GitHub Actions
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_actions_key -N ""

# This creates:
# ~/.ssh/github_actions_key (private key)
# ~/.ssh/github_actions_key.pub (public key)

# Add the public key to authorized_keys
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# Display the private key (you'll copy this to GitHub)
cat ~/.ssh/github_actions_key

# Copy the ENTIRE output including:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ... (many lines) ...
# -----END OPENSSH PRIVATE KEY-----
```

Add to GitHub Secrets:
- Name: `GCP_VM_SSH_KEY`
- Value: (paste the entire private key)

Add to GitHub Secrets:
- Name: `GCP_VM_USERNAME`
- Value: `founders` (or your actual username)

**Test the SSH key:**
```bash
# From another machine (to verify CI/CD will work)
ssh -i ~/.ssh/github_actions_key founders@YOUR_VM_IP

# If this works, CI/CD will work!
```

---

### **Step 3: Create GCP Service Account for Cloud Run**

**On your local machine or VM:**

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create service account
gcloud iam service-accounts create github-actions-deploy \
  --display-name="GitHub Actions Deployment" \
  --description="Service account for CI/CD deployments"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create ~/github-actions-key.json \
  --iam-account=github-actions-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Display the key
cat ~/github-actions-key.json

# Copy the ENTIRE JSON output
```

Add to GitHub Secrets:
- Name: `GCP_SA_KEY`
- Value: (paste the entire JSON)

Add to GitHub Secrets:
- Name: `GCP_PROJECT_ID`
- Value: `your-project-id`

---

### **Step 4: Set Up Slack Notifications (Optional but Recommended)**

1. Go to: https://api.slack.com/messaging/webhooks
2. Click "Create your Slack app"
3. Choose "From scratch"
4. Name it "SymphAIny CI/CD"
5. Select your workspace
6. Go to "Incoming Webhooks"
7. Activate webhooks
8. Click "Add New Webhook to Workspace"
9. Select channel (e.g., #deployments)
10. Copy the webhook URL

Add to GitHub Secrets:
- Name: `SLACK_WEBHOOK`
- Value: (paste webhook URL)

---

### **Step 5: Configure VM Firewall (If Needed)**

Allow external access to staging ports:

```bash
# Allow access to ports 8000 and 3000
gcloud compute firewall-rules create allow-staging \
  --allow tcp:8000,tcp:3000 \
  --source-ranges 0.0.0.0/0 \
  --description="Allow access to staging environment"

# For production, you might want to restrict this:
# --source-ranges YOUR_OFFICE_IP/32,YOUR_HOME_IP/32
```

---

### **Step 6: Set Up GitHub Environments**

Go to: **GitHub → Settings → Environments**

**Create "vm-staging" environment:**
- Name: `vm-staging`
- URL: `http://YOUR_VM_IP:3000`
- Protection rules: (optional)
  - No approval required (develop branch auto-deploys)

**Create "production" environment:**
- Name: `production`
- URL: `https://symphainy.com`
- Protection rules: **REQUIRED**
  - ✅ Required reviewers: Add CTO, Tech Lead
  - ✅ Wait timer: 0 minutes (or 5 for safety)
  - ✅ Deployment branches: Only `main`

---

## ✅ **VERIFICATION CHECKLIST**

Before your first deployment, verify:

### **VM Staging (Tier 2):**
- [ ] `GCP_VM_IP` secret added to GitHub
- [ ] `GCP_VM_USERNAME` secret added to GitHub
- [ ] `GCP_VM_SSH_KEY` secret added to GitHub
- [ ] SSH key works (test manually)
- [ ] Docker installed on VM
- [ ] Docker Compose installed on VM
- [ ] Firewall allows ports 8000 and 3000
- [ ] `vm-staging` environment created in GitHub

### **Cloud Run Production (Tier 3):**
- [ ] `GCP_PROJECT_ID` secret added to GitHub
- [ ] `GCP_SA_KEY` secret added to GitHub
- [ ] Service account has correct permissions
- [ ] Cloud Run API enabled
- [ ] `production` environment created in GitHub
- [ ] Required reviewers set for production

### **Notifications:**
- [ ] `SLACK_WEBHOOK` secret added to GitHub
- [ ] Test notification sent to Slack channel

---

## 🧪 **TESTING YOUR SETUP**

### **Test VM Staging Deployment:**

```bash
# 1. Make a small change to code
echo "# Test change" >> symphainy-platform/README.md

# 2. Commit and push to develop
git checkout develop
git add .
git commit -m "Test VM staging deployment"
git push origin develop

# 3. Watch GitHub Actions
# Go to: GitHub → Actions → Watch "Three-Tier Deployment"

# 4. Should see:
# ✅ Lint
# ✅ Backend tests
# ✅ Frontend tests
# ✅ E2E tests
# ✅ Deploy to VM Staging

# 5. Check VM staging
curl http://YOUR_VM_IP:8000/health
curl http://YOUR_VM_IP:3000

# 6. Should get Slack notification
```

### **Test Cloud Run Production Deployment:**

```bash
# 1. After VM staging looks good, merge to main
git checkout main
git merge develop
git push origin main

# 2. Watch GitHub Actions
# Should pause and wait for approval

# 3. Approve deployment
# GitHub → Actions → Click workflow → "Review deployments" → Approve

# 4. Wait for Cloud Run deployment
# Should see URLs in Slack notification

# 5. Test production
curl https://YOUR_CLOUD_RUN_URL/health
```

---

## 🔄 **YOUR WORKFLOW (After Setup)**

```
┌─────────────────────────────────────────┐
│  TIER 1: Development (No CI/CD)        │
│  Work in Cursor on VM ports 8001/3001  │
└────────────┬────────────────────────────┘
             │ git push origin develop
             ↓
┌─────────────────────────────────────────┐
│  GitHub Actions (Automatic)             │
│  ├─ Run all tests                       │
│  ├─ Build Docker containers             │
│  └─ SSH into VM, deploy to :8000/:3000  │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│  TIER 2: VM Staging (Automatic)         │
│  http://YOUR_VM_IP:3000                 │
│  └─ Team validates here                 │
└────────────┬────────────────────────────┘
             │ git push origin main
             ↓
┌─────────────────────────────────────────┐
│  GitHub Actions (Wait for Approval)     │
│  ├─ Run all tests again                 │
│  ├─ Build containers                    │
│  ├─ Push to Google Container Registry   │
│  └─ Wait for CTO approval...            │
└────────────┬────────────────────────────┘
             │ Approved!
             ↓
┌─────────────────────────────────────────┐
│  TIER 3: Cloud Run Production           │
│  https://symphainy.com                  │
│  └─ Customers access here               │
└─────────────────────────────────────────┘
```

---

## 🐛 **TROUBLESHOOTING**

### **VM Staging Deployment Fails:**

```bash
# SSH into VM manually
ssh founders@YOUR_VM_IP

# Check Docker logs
docker-compose -f /home/founders/demoversion/symphainy_source/docker-compose.prod.yml logs

# Check if ports are blocked
sudo netstat -tlnp | grep -E '8000|3000'

# Check firewall
gcloud compute firewall-rules list

# Manually test deployment script
cd /home/founders/demoversion/symphainy_source
docker-compose -f docker-compose.prod.yml up --build
```

### **Cloud Run Deployment Fails:**

```bash
# Check service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:github-actions-deploy@*"

# Check Cloud Run services
gcloud run services list

# Check Cloud Run logs
gcloud run services logs read symphainy-backend --limit 50
```

### **Slack Notifications Not Working:**

```bash
# Test webhook manually
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test from CI/CD"}' \
  YOUR_SLACK_WEBHOOK_URL
```

---

## 📊 **COST ESTIMATE**

**VM Staging (Already Have):**
- No additional cost (uses existing VM)

**Cloud Run Production:**
- Backend: ~$50-200/month (depends on traffic)
- Frontend: ~$30-100/month (depends on traffic)
- Container Registry storage: ~$5/month
- **Total: ~$85-305/month**

**Savings:**
- No second VM needed (using existing for staging)
- Pay only for actual Cloud Run usage
- Auto-scales to zero when not used

---

## ✅ **YOU'RE READY!**

Once all secrets are configured:

1. ✅ Push to `develop` → Auto-deploys to VM staging
2. ✅ Team validates on VM
3. ✅ Merge to `main` → Waits for approval
4. ✅ CTO approves → Deploys to Cloud Run
5. ✅ Slack notifications at each step

**Your three-tier deployment is now fully automated!** 🚀





