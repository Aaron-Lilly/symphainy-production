# CI/CD Quick Reference

**Status:** Manual Trigger Only (Development Mode)

---

## 🚀 How to Run CI/CD

### Option 1: GitHub Actions UI
1. Go to: https://github.com/Aaron-Lilly/symphainy_sourcecode/actions
2. Click "CI/CD Pipeline" workflow
3. Click "Run workflow" dropdown
4. Select branch
5. Click "Run workflow" button

### Option 2: GitHub CLI
```bash
gh workflow run ci-cd-pipeline.yml --ref main
```

---

## 🧪 Test Users

All tests use pre-authorized test users (no email spam):

```bash
# Email
testuser0@symphainy.com

# Password
TestPassword123!
```

**Setup test users if needed:**
```bash
python3 scripts/setup_test_users.py
```

---

## 📝 What Changed

| Before | After |
|--------|-------|
| Auto-runs on every push | Manual trigger only |
| Creates new test users | Uses pre-authorized users |
| Sends confirmation emails | No emails sent |
| Causes email bounces | Zero bounces |
| GitHub notification spam | No spam |

---

## ✅ When to Run CI/CD

- Before merging PRs to main
- After completing major features
- Before deployment
- Manual verification needed

---

## 🔄 Re-Enable Automatic CI/CD

**When production-ready**, edit `.github/workflows/ci-cd-pipeline.yml`:

Uncomment lines 10-18:
```yaml
on:
  push:
    branches:
      - main
      - develop
  pull_request:
    branches:
      - main
      - develop
  workflow_dispatch:
```

---

## 📚 Related Docs

- `SUPABASE_EMAIL_BOUNCE_ANALYSIS.md` - Root cause analysis
- `SUPABASE_EMAIL_FIX_COMPLETE.md` - Complete solution documentation
- `scripts/setup_test_users.py` - Test user setup script




