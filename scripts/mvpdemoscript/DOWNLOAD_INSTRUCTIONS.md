# 📥 Download Your Demo Files

## ✅ Files Generated Successfully!

All 3 demo scenarios are ready on the VM:

- ✅ **Defense_TnE.zip** (44 KB) - CSV, Binary, DOCX, JSON
- ✅ **Underwriting_Insights.zip** (639 KB) - Binary, CSV, XLSX, PDF, JSON
- ✅ **Coexistence.zip** (3.7 KB) - CSV, JSON

---

## 🚀 Quick Download (Copy & Paste!)

### **From Your Local Machine Terminal:**

```bash
# Download all 3 files at once
scp "founders@35.215.64.103:/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/*.zip" .
```

### **Or Download Individually:**

```bash
# Defense scenario (smallest, good for first test)
scp founders@35.215.64.103:/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/SymphAIny_Demo_Defense_TnE.zip .

# Underwriting scenario (largest, comprehensive test)
scp founders@35.215.64.103:/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/SymphAIny_Demo_Underwriting_Insights.zip .

# Coexistence scenario (schema mapping test)
scp founders@35.215.64.103:/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/SymphAIny_Demo_Coexistence.zip .
```

---

## 🎯 After Download: Test in SymphAIny

1. **Open SymphAIny:** http://35.215.64.103:3000
2. **Login** with your account
3. **Navigate to Content Pillar** (navbar)
4. **Upload a demo ZIP file**
5. **Test parsing, insights, operations, business outcomes!**

---

## 📦 What's In Each File?

### **Defense_TnE** (44 KB)
- `mission_plan.csv` - 50 mission records
- `telemetry_raw.bin` - Binary sensor data
- `telemetry_copybook.cpy` - COBOL copybook
- `test_incident_reports.docx` - 3 incident reports
- `ai_insights.json` - Analysis results

**Test:** File parsing, legacy formats, COBOL, binary data

---

### **Underwriting_Insights** (639 KB)
- `policy_master.dat` - 10,000 binary policy records
- `claims.csv` - 5,000 claim records
- `reinsurance.xlsx` - Excel reinsurance data
- `underwriting_notes.pdf` - 50 paragraphs of notes
- `copybook.cpy` - COBOL copybook
- `ai_insights.json` - Mortality trends analysis

**Test:** Large datasets, Excel parsing, PDF extraction, analytics

---

### **Coexistence** (3.7 KB)
- `legacy_policy_export.csv` - 50 legacy policies
- `target_schema.json` - Target system schema
- `alignment_map.json` - Field mapping configuration
- `ai_insights.json` - Schema coverage analysis

**Test:** Schema mapping, data transformation, migration workflows

---

## 🐛 Troubleshooting

### **Permission Denied**
```bash
# Make sure you can SSH to the VM first
ssh founders@35.215.64.103

# If that works, scp should work too
```

### **Files Not Found**
```bash
# Verify files exist on VM
ssh founders@35.215.64.103 "ls -lh /home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/*.zip"
```

### **Different SSH Key**
```bash
# If you use a specific SSH key
scp -i /path/to/your/key "founders@35.215.64.103:/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files/*.zip" .
```

---

## 💡 Alternative: Upload to GCS Manually

If you prefer to use GCS:

1. Download files via SCP (as above)
2. From your local machine with GCS access:
   ```bash
   gsutil cp *.zip gs://symphainy-demo-files/demo_files/
   ```
3. Files will be publicly accessible at:
   ```
   https://storage.googleapis.com/symphainy-demo-files/demo_files/SymphAIny_Demo_Defense_TnE.zip
   https://storage.googleapis.com/symphainy-demo-files/demo_files/SymphAIny_Demo_Underwriting_Insights.zip
   https://storage.googleapis.com/symphainy-demo-files/demo_files/SymphAIny_Demo_Coexistence.zip
   ```

---

## 🎉 You're Ready to Test!

1. Download files using commands above
2. Open SymphAIny in browser
3. Upload & test all 4 pillars
4. Verify complete MVP functionality

**Happy Testing!** 🚀

