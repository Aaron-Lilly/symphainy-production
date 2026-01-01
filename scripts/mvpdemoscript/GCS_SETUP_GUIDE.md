# 📦 GCS Demo Files Setup Guide

**Purpose:** Generate realistic demo data and upload to Google Cloud Storage for easy access during testing.

---

## 🎯 WHAT THIS SCRIPT DOES

The enhanced `generate_symphainy_demo.py` script:
1. ✅ Generates **3 realistic demo scenarios** with various file types
2. ✅ Creates ZIP packages for each scenario
3. ✅ Uploads ZIP files to **Google Cloud Storage (GCS)**
4. ✅ Generates **signed download URLs** (valid for 7 days)
5. ✅ Provides multiple access methods

---

## 📊 DEMO SCENARIOS

### 1. **Defense_TnE** (Defense Test & Evaluation)
- **Files:**
  - `mission_plan.csv` (50 missions)
  - `telemetry_raw.bin` (binary sensor data)
  - `telemetry_copybook.cpy` (COBOL copybook)
  - `test_incident_reports.docx` (3 incidents)
  - `ai_insights.json` (analysis results)
- **Use Case:** Test file parsing (CSV, binary, DOCX), legacy format handling

### 2. **Underwriting_Insights** (Insurance Analytics)
- **Files:**
  - `policy_master.dat` (10,000 binary records)
  - `copybook.cpy` (COBOL copybook)
  - `claims.csv` (5,000 claims)
  - `reinsurance.xlsx` (Excel data)
  - `underwriting_notes.pdf` (50 paragraphs)
  - `ai_insights.json` (mortality trends)
- **Use Case:** Test data analysis, Excel parsing, PDF extraction, large datasets

### 3. **Coexistence** (Pre-Migration Data Mapping)
- **Files:**
  - `legacy_policy_export.csv` (50 policies)
  - `target_schema.json` (target system schema)
  - `alignment_map.json` (field mappings)
  - `ai_insights.json` (schema coverage)
- **Use Case:** Test schema mapping, data transformation, migration workflows

---

## 🔧 SETUP INSTRUCTIONS

### **Step 1: Install Required Python Packages**

```bash
# Navigate to script directory
cd /home/founders/demoversion/symphainy_source/scripts/mvpdemoscript

# Install dependencies
pip3 install faker pandas openpyxl python-docx fpdf google-cloud-storage
```

### **Step 2: Set Up Google Cloud Storage**

#### **Option A: Create New GCS Bucket (Recommended)**

1. **Go to GCS Console:**
   ```
   https://console.cloud.google.com/storage/browser
   ```

2. **Click "CREATE BUCKET"**

3. **Configure Bucket:**
   - **Name:** `symphainy-demo-files` (or your preferred name)
   - **Location type:** Region
   - **Location:** `us-central1` (or your preferred region)
   - **Storage class:** Standard
   - **Access control:** Uniform
   - **Protection tools:** None (for demo/testing)
   - **Click "CREATE"**

4. **Update Script:**
   - If you used a different bucket name, edit `generate_symphainy_demo.py`:
   ```python
   GCS_BUCKET_NAME = "your-bucket-name-here"
   ```

#### **Option B: Use Existing Bucket**

If you already have a GCS bucket:
1. Edit `generate_symphainy_demo.py`
2. Change `GCS_BUCKET_NAME = "your-existing-bucket-name"`

### **Step 3: Set Up GCS Authentication**

#### **Option A: Use gcloud CLI (Recommended for Development)**

```bash
# Install gcloud CLI (if not already installed)
# Follow: https://cloud.google.com/sdk/docs/install

# Authenticate with your Google account
gcloud auth application-default login

# This will open a browser for authentication
# After authentication, credentials are stored locally
```

#### **Option B: Use Service Account (For Production)**

1. **Create Service Account:**
   ```
   https://console.cloud.google.com/iam-admin/serviceaccounts
   ```

2. **Grant Permissions:**
   - Storage Admin (or Storage Object Admin for the specific bucket)

3. **Create Key:**
   - Click on service account → Keys → Add Key → Create new key
   - Choose JSON format
   - Download the key file

4. **Set Environment Variable:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
   ```

5. **Add to your shell profile** (to persist):
   ```bash
   echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"' >> ~/.bashrc
   source ~/.bashrc
   ```

---

## 🚀 RUNNING THE SCRIPT

### **Execute:**

```bash
cd /home/founders/demoversion/symphainy_source/scripts/mvpdemoscript
python3 generate_symphainy_demo.py
```

### **Expected Output:**

```
================================================================================
🎯 SymphAIny Demo Data Generator
================================================================================
📁 Base directory: /home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files
☁️  GCS Bucket: symphainy-demo-files
📦 Scenarios: Defense_TnE, Underwriting_Insights, Coexistence
================================================================================

🔨 Generating Defense_TnE...
  📦 Created ZIP: SymphAIny_Demo_Defense_TnE.zip
✅ Defense_TnE demo data generated!
  📤 Uploading SymphAIny_Demo_Defense_TnE.zip to GCS...
  ✅ Upload successful!

🔨 Generating Underwriting_Insights...
  📦 Created ZIP: SymphAIny_Demo_Underwriting_Insights.zip
✅ Underwriting_Insights demo data generated!
  📤 Uploading SymphAIny_Demo_Underwriting_Insights.zip to GCS...
  ✅ Upload successful!

🔨 Generating Coexistence...
  📦 Created ZIP: SymphAIny_Demo_Coexistence.zip
✅ Coexistence demo data generated!
  📤 Uploading SymphAIny_Demo_Coexistence.zip to GCS...
  ✅ Upload successful!

================================================================================
🎉 ALL DEMO FILES GENERATED & UPLOADED!
================================================================================

📥 DOWNLOAD LINKS (Valid for 7 days):

  📦 Defense_TnE:
     Size: 0.15 MB
     GCS Path: gs://symphainy-demo-files/demo_files/SymphAIny_Demo_Defense_TnE.zip
     Download URL:
     https://storage.googleapis.com/symphainy-demo-files/demo_files/SymphAIny_Demo_Defense_TnE.zip?...

  📦 Underwriting_Insights:
     Size: 2.50 MB
     GCS Path: gs://symphainy-demo-files/demo_files/SymphAIny_Demo_Underwriting_Insights.zip
     Download URL:
     https://storage.googleapis.com/symphainy-demo-files/demo_files/SymphAIny_Demo_Underwriting_Insights.zip?...

  📦 Coexistence:
     Size: 0.05 MB
     GCS Path: gs://symphainy-demo-files/demo_files/SymphAIny_Demo_Coexistence.zip
     Download URL:
     https://storage.googleapis.com/symphainy-demo-files/demo_files/SymphAIny_Demo_Coexistence.zip?...

================================================================================
```

---

## 📥 ACCESSING YOUR DEMO FILES

### **Method 1: Direct Download (Easiest!)**

1. **Copy the signed URL** from the script output
2. **Paste into your browser** (works from any device)
3. **File downloads automatically**
4. **Upload to SymphAIny** via the web interface

**✅ Recommended for quick testing!**

### **Method 2: Google Cloud Console (Visual Interface)**

1. **Go to:**
   ```
   https://console.cloud.google.com/storage/browser
   ```

2. **Navigate to your bucket:**
   - Click on `symphainy-demo-files`
   - Click on `demo_files/` folder
   - You'll see all 3 ZIP files

3. **Download:**
   - Click the **⋮** (three dots) next to a file
   - Select **"Download"**
   - File downloads to your local machine

4. **View/Share:**
   - Click **⋮** → **"Get public URL"** (if bucket is public)
   - Click **⋮** → **"Get signed URL"** (for private buckets)

### **Method 3: gsutil Command Line (For Automation)**

```bash
# Download all demo files
gsutil cp gs://symphainy-demo-files/demo_files/*.zip .

# Download specific file
gsutil cp gs://symphainy-demo-files/demo_files/SymphAIny_Demo_Defense_TnE.zip .

# List all files
gsutil ls gs://symphainy-demo-files/demo_files/

# Get file metadata
gsutil stat gs://symphainy-demo-files/demo_files/SymphAIny_Demo_Defense_TnE.zip
```

### **Method 4: Direct to Local Machine (No GCS)**

If GCS upload fails or you want files locally only:

```bash
# Files are saved locally at:
cd /home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files

# Copy to your local machine using scp (from your local terminal)
scp username@vm-ip:/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/*.zip .
```

---

## 🧪 TESTING WORKFLOW

### **Complete Testing Flow:**

```
1. Generate Demo Files
   ↓
   python3 generate_symphainy_demo.py

2. Download ZIP File
   ↓
   Click signed URL or use GCS console

3. Open SymphAIny Platform
   ↓
   http://VM_EXTERNAL_IP:3000

4. Login/Register
   ↓
   Create account or login

5. Navigate to Content Pillar
   ↓
   Click "Content" in navbar

6. Upload Demo File
   ↓
   Drag & drop or click to upload ZIP file

7. Test Parsing
   ↓
   Click "Parse" on uploaded file

8. Test Insights
   ↓
   Navigate to Insights Pillar
   Request analysis on parsed data

9. Test Operations
   ↓
   Navigate to Operations Pillar
   Generate SOP or workflow

10. Test Business Outcomes
    ↓
    Navigate to Business Outcomes Pillar
    Generate roadmap or POC proposal
```

---

## 🔍 TROUBLESHOOTING

### **Issue: `google-cloud-storage` not installed**
```bash
pip3 install google-cloud-storage
```

### **Issue: Authentication failed**
```bash
# Re-authenticate
gcloud auth application-default login

# Or check credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### **Issue: Bucket does not exist**
1. Go to: https://console.cloud.google.com/storage/browser
2. Verify bucket name matches script configuration
3. Update `GCS_BUCKET_NAME` in script if needed

### **Issue: Permission denied**
1. Check service account has "Storage Admin" role
2. Or authenticate with owner account:
   ```bash
   gcloud auth application-default login
   ```

### **Issue: Signed URL expired**
- Signed URLs are valid for **7 days** by default
- Re-run script to generate fresh URLs:
  ```bash
  python3 generate_symphainy_demo.py
  ```

### **Issue: Dependencies missing**
```bash
# Install all dependencies at once
pip3 install faker pandas openpyxl python-docx fpdf google-cloud-storage
```

---

## 📊 FILE SIZES & TYPES

| Scenario | Size | Key File Types | Record Count |
|----------|------|----------------|--------------|
| Defense_TnE | ~150 KB | CSV, Binary, DOCX, JSON | 50 missions |
| Underwriting_Insights | ~2.5 MB | Binary, CSV, XLSX, PDF | 15,000 records |
| Coexistence | ~50 KB | CSV, JSON | 50 policies |

---

## 🎯 NEXT STEPS

1. ✅ **Run the script** to generate & upload demo files
2. ✅ **Copy signed URLs** from script output
3. ✅ **Download files** using any of the 4 methods above
4. ✅ **Test the MVP** by uploading files through the web interface
5. ✅ **Verify all 4 pillars** work with realistic data

---

## 💡 PRO TIPS

1. **Signed URLs are valid for 7 days** - save them!
2. **Files are in `demo_files/` folder** in GCS - keeps things organized
3. **Script can be re-run** - it will overwrite old files with fresh data
4. **Start with Defense_TnE** - smallest file, fastest upload/parsing
5. **Use Underwriting_Insights** - best for testing large dataset handling

---

**Happy Testing!** 🚀

If you encounter any issues, check the troubleshooting section or review the script output for specific error messages.

