# GitHub Secrets - What You Have vs What You Need

---

## 🔍 **ANALYSIS**

You have **two different CI/CD workflows** that require **different secrets**:

### **OLD Workflow: `ci-cd-pipeline.yml` (AWS-based)**

This was the generic workflow I created earlier, assuming AWS deployment.

**Required Secrets:**
- ✅ `AWS_ACCESS_KEY_ID` - For AWS deployments
- ✅ `AWS_SECRET_ACCESS_KEY` - For AWS deployments
- ✅ `SLACK_WEBHOOK` - For notifications

---

### **NEW Workflow: `three-tier-deployment.yml` (GCP-based)**

This is your **actual architecture** with GCP VM staging + Cloud Run production.

**Required Secrets:**
- 🆕 `GCP_VM_IP` - Your VM's external IP
- 🆕 `GCP_VM_USERNAME` - SSH username (probably "founders")
- 🆕 `GCP_VM_SSH_KEY` - SSH private key for VM access
- 🆕 `GCP_PROJECT_ID` - Your GCP project ID
- 🆕 `GCP_SA_KEY` - Service account key for Cloud Run
- ✅ `SLACK_WEBHOOK` - For notifications (same as before)

---

## 🎯 **WHAT YOU LIKELY HAVE**

If you set up secrets previously, you probably have:

| Secret | Status | Used By |
|--------|--------|---------|
| `AWS_ACCESS_KEY_ID` | ✅ Probably exists | OLD workflow only |
| `AWS_SECRET_ACCESS_KEY` | ✅ Probably exists | OLD workflow only |
| `SLACK_WEBHOOK` | ✅ Probably exists | Both workflows |

---

## 📋 **WHAT YOU NEED TO ADD**

For your **three-tier deployment** to work, you need to add:

| Secret | Priority | Purpose |
|--------|----------|---------|
| `GCP_VM_IP` | 🔴 **REQUIRED** | SSH into your VM for staging deployment |
| `GCP_VM_USERNAME` | 🔴 **REQUIRED** | SSH username |
| `GCP_VM_SSH_KEY` | 🔴 **REQUIRED** | SSH private key |
| `GCP_PROJECT_ID` | 🟡 **NEEDED FOR PROD** | Deploy to Cloud Run |
| `GCP_SA_KEY` | 🟡 **NEEDED FOR PROD** | Deploy to Cloud Run |

---

## ✅ **HOW TO VERIFY WHAT YOU HAVE**

### **Option 1: Use GitHub CLI**

```bash
# Install GitHub CLI (if not installed)
# Ubuntu/Debian: sudo apt install gh
# Mac: brew install gh

# Authenticate
gh auth login

# List secrets (shows names, not values)
gh secret list
```

### **Option 2: Check Manually in GitHub**

1. Go to: `https://github.com/YOUR_USERNAME/symphainy_sourcecode/settings/secrets/actions`
2. You'll see a list of secret **names** (values are hidden)
3. Compare with the required list above

---

## 🔧 **HOW TO ADD MISSING SECRETS**

### **Quick Setup (5 minutes):**

```bash
# 1. Get your VM IP
gcloud compute instances list
# Copy the EXTERNAL_IP

# 2. Get your GCP project ID
gcloud config get-value project
# Copy the project ID

# 3. Generate SSH key for GitHub Actions (if not exists)
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions_key -N ""
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# 4. Display the private key (copy this)
cat ~/.ssh/github_actions_key

# 5. Go to GitHub and add secrets:
# GitHub → Settings → Secrets and variables → Actions → New repository secret

# Add:
# - GCP_VM_IP: [paste VM IP]
# - GCP_VM_USERNAME: founders
# - GCP_VM_SSH_KEY: [paste entire private key]
# - GCP_PROJECT_ID: [paste project ID]
```

### **Full Setup with Service Account (for Cloud Run):**

See complete instructions in: `.github/THREE_TIER_SETUP.md`

---

## 🚀 **TESTING YOUR SECRETS**

### **Test VM Staging (After adding VM secrets):**

```bash
# Run the verification script
chmod +x scripts/check-github-secrets.sh
./scripts/check-github-secrets.sh

# Then test a deployment:
git checkout develop
echo "# Test" >> README.md
git commit -am "Test VM staging deployment"
git push origin develop

# Watch GitHub Actions:
# https://github.com/YOUR_USERNAME/symphainy_sourcecode/actions

# Should see:
# ✅ Tests pass
# ✅ Deploy to VM staging
# ✅ Slack notification
```

---

## 📊 **SUMMARY**

### **For VM Staging (Tier 2) - IMMEDIATE NEED:**

You need these **3 secrets** to deploy to your VM:

```
✅ GCP_VM_IP
✅ GCP_VM_USERNAME  
✅ GCP_VM_SSH_KEY
```

**Time to set up:** 5 minutes  
**Priority:** 🔴 HIGH (needed for Day 13-14)

---

### **For Cloud Run Production (Tier 3) - NEEDED LATER:**

You need these **2 additional secrets**:

```
✅ GCP_PROJECT_ID
✅ GCP_SA_KEY
```

**Time to set up:** 10 minutes  
**Priority:** 🟡 MEDIUM (needed for Day 15)

---

### **Optional but Recommended:**

```
✅ SLACK_WEBHOOK (might already have this)
```

**Time to set up:** 5 minutes  
**Priority:** 🟢 LOW (nice to have)

---

## 🎯 **RECOMMENDED ACTION**

### **Today (If you want to test staging deployment):**

```bash
# 1. Run the checker script
./scripts/check-github-secrets.sh

# 2. Add the 3 VM secrets (5 min)
# 3. Test deployment to VM staging
# 4. Verify at: http://YOUR_VM_IP:3000
```

### **Before Day 15 (Production deployment):**

```bash
# 1. Follow full setup guide
# 2. Add GCP_PROJECT_ID and GCP_SA_KEY
# 3. Set up production approval requirements
# 4. Test production deployment
```

---

## 🔐 **SECURITY NOTES**

1. **Never commit secrets to Git** ✅ You're doing this right
2. **GitHub Secrets are encrypted** - Nobody can read them (not even you!)
3. **SSH keys should be unique** - Don't reuse your personal SSH key
4. **Service accounts should have minimal permissions** - Only what's needed
5. **Rotate secrets periodically** - Especially after team changes

---

## 📞 **NEED HELP?**

Run this to get your current status:

```bash
./scripts/check-github-secrets.sh
```

Then add missing secrets following:

```bash
cat .github/THREE_TIER_SETUP.md
```

---

## ✅ **QUICK CHECKLIST**

**Before VM Staging Works:**
- [ ] GCP_VM_IP added to GitHub
- [ ] GCP_VM_USERNAME added to GitHub
- [ ] GCP_VM_SSH_KEY added to GitHub
- [ ] SSH key works (test: `ssh -i ~/.ssh/github_actions_key founders@VM_IP`)
- [ ] VM has Docker installed
- [ ] VM ports 8000/3000 accessible

**Before Cloud Run Works:**
- [ ] GCP_PROJECT_ID added to GitHub
- [ ] GCP_SA_KEY added to GitHub
- [ ] Service account has permissions
- [ ] Cloud Run API enabled
- [ ] Production environment configured with approvers

---

**TL;DR:** You probably have AWS secrets from before, but need to add **5 new GCP secrets** for your three-tier deployment. Start with the 3 VM secrets (5 min), then add the 2 Cloud Run secrets later.





