# GitHub Secrets - Simple Checklist
**Exactly what you need (no AWS, no Slack)**

---

## ✅ **5 SECRETS YOU NEED**

That's it! Just 5 secrets total.

---

## 📋 **QUICK SETUP (10 Minutes)**

### **Secret 1-3: VM Staging Access**

```bash
# 1. Get your VM IP
VM_IP=$(gcloud compute instances list --format="get(networkInterfaces[0].accessConfigs[0].natIP)" | head -1)
echo "Your VM IP: $VM_IP"

# 2. Generate SSH key for GitHub Actions
ssh-keygen -t rsa -b 4096 -C "github-actions" -f ~/.ssh/github_actions_key -N ""
cat ~/.ssh/github_actions_key.pub >> ~/.ssh/authorized_keys

# 3. Display the private key (you'll copy this)
echo "==== Copy everything below (including BEGIN/END lines) ===="
cat ~/.ssh/github_actions_key
echo "==== End of key ===="
```

**Add to GitHub:**

Go to: `https://github.com/YOUR_USERNAME/symphainy_sourcecode/settings/secrets/actions`

1. Click "New repository secret"
   - Name: `GCP_VM_IP`
   - Value: [paste your VM IP from above]

2. Click "New repository secret"
   - Name: `GCP_VM_USERNAME`
   - Value: `founders`

3. Click "New repository secret"
   - Name: `GCP_VM_SSH_KEY`
   - Value: [paste entire private key including BEGIN/END lines]

---

### **Secret 4-5: Cloud Run Production**

```bash
# 1. Get your project ID
PROJECT_ID=$(gcloud config get-value project)
echo "Your project ID: $PROJECT_ID"

# 2. Create service account (if doesn't exist)
gcloud iam service-accounts create github-actions-deploy \
  --display-name="GitHub Actions Deploy" 2>/dev/null || echo "Service account already exists"

# 3. Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# 4. Create key
gcloud iam service-accounts keys create ~/github-actions-key.json \
  --iam-account=github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com

# 5. Display the key
echo "==== Copy everything below ===="
cat ~/github-actions-key.json
echo "==== End of key ===="
```

**Add to GitHub:**

4. Click "New repository secret"
   - Name: `GCP_PROJECT_ID`
   - Value: [paste your project ID from above]

5. Click "New repository secret"
   - Name: `GCP_SA_KEY`
   - Value: [paste entire JSON key]

---

## ✅ **VERIFICATION**

After adding all 5 secrets, you should see:

```
Secrets (5)
├─ GCP_VM_IP
├─ GCP_VM_USERNAME
├─ GCP_VM_SSH_KEY
├─ GCP_PROJECT_ID
└─ GCP_SA_KEY
```

---

## 🧪 **TEST IT**

```bash
# Test VM staging deployment
git checkout develop
echo "# Test" >> README.md
git commit -am "Test deployment"
git push origin develop

# Watch at: https://github.com/YOUR_USERNAME/symphainy_sourcecode/actions
# Should deploy to: http://YOUR_VM_IP:3000
```

---

## 📧 **NOTIFICATIONS**

**You'll get notified via:**
- Email (you already have this connected)
- GitHub mobile app (if installed)
- Commit comments (automatic)

**No Slack needed!**

See: `.github/GITHUB_NOTIFICATIONS.md` for details

---

## 🎯 **PRIORITY**

| When | What | Why |
|------|------|-----|
| **Now** | Secrets 1-3 (VM) | For Days 13-14 staging deployment |
| **Day 15** | Secrets 4-5 (Cloud Run) | For production deployment |

---

## ❓ **NEED HELP?**

Run this to check your setup:
```bash
./scripts/check-github-secrets.sh
```

---

**TL;DR:** Just 5 GCP secrets. No AWS. No Slack. 10 minutes to set up.





