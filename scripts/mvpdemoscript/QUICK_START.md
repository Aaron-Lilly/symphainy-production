# ⚡ Quick Start - Demo Files for Testing

## 🚀 30-Second Setup

```bash
# 1. Install dependencies
pip3 install faker pandas openpyxl python-docx fpdf google-cloud-storage

# 2. Authenticate with GCS
gcloud auth application-default login

# 3. Run the script
cd /home/founders/demoversion/symphainy_source/scripts/mvpdemoscript
python3 generate_symphainy_demo.py
```

## 📥 Get Your Files

**Script outputs download URLs like this:**

```
📥 DOWNLOAD LINKS (Valid for 7 days):

  📦 Defense_TnE:
     Download URL:
     https://storage.googleapis.com/symphainy-demo-files/demo_files/...
```

**Just click the URL** → File downloads → Upload to SymphAIny!

---

## 🎯 What You Get

| Scenario | Files | Size | Use For |
|----------|-------|------|---------|
| **Defense_TnE** | CSV, Binary, DOCX | 150 KB | File parsing, legacy formats |
| **Underwriting_Insights** | Binary, CSV, XLSX, PDF | 2.5 MB | Large datasets, analytics |
| **Coexistence** | CSV, JSON | 50 KB | Schema mapping, transformation |

---

## 📍 Access Files 3 Ways

1. **Click URL** (from script output) → Downloads automatically
2. **GCS Console:** https://console.cloud.google.com/storage/browser
3. **Command line:** `gsutil cp gs://symphainy-demo-files/demo_files/*.zip .`

---

## 🐛 Quick Fixes

**No google-cloud-storage?**
```bash
pip3 install google-cloud-storage
```

**Authentication failed?**
```bash
gcloud auth application-default login
```

**Bucket doesn't exist?**
1. Go to https://console.cloud.google.com/storage/browser
2. Click "CREATE BUCKET"
3. Name it: `symphainy-demo-files`

---

## 💡 Pro Tips

- ✅ Signed URLs valid for **7 days**
- ✅ Start testing with **Defense_TnE** (smallest)
- ✅ Re-run script anytime for fresh URLs
- ✅ Files organized in `demo_files/` folder

---

**Full guide:** See `GCS_SETUP_GUIDE.md`

