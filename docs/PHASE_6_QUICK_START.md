# Phase 6 Frontend - Quick Start Guide

**Status:** ✅ Complete  
**Purpose:** Quick reference for using the new Data Mapping UI

---

## 🚀 Getting Started

### 1. Access Data Mapping

Navigate to: **Insights Pillar** → **Data Mapping Section**

The Data Mapping section is the third section on the Insights page, below:
- Insights from Structured Data
- Insights from Unstructured Data
- **Data Mapping** ← New!

---

## 📋 Step-by-Step Usage

### Step 1: Select Source File
1. Click on **Source File** card
2. Use the file selector to choose your source file
   - Examples: License PDF, legacy policy records JSONL, etc.

### Step 2: Select Target File
1. Click on **Target File** card
2. Use the file selector to choose your target file
   - Examples: Excel template, new data model JSON, etc.

### Step 3: Configure Mapping Options
1. **Mapping Type:**
   - **Auto-detect** (recommended) - Automatically determines mapping type
   - **Unstructured → Structured** - For PDF to Excel, etc.
   - **Structured → Structured** - For legacy records to new model

2. **Quality Validation** (only for structured→structured):
   - Enable to validate data quality and generate cleanup actions

3. **Minimum Confidence:**
   - Set threshold (50-100%)
   - Only mappings above this confidence will be included

4. **Include Citations:**
   - Show source location for each mapped field

### Step 4: Execute Mapping
1. Click **Execute Mapping** button
2. Wait for mapping to complete (progress indicator shown)
3. Results will appear below

---

## 📊 Understanding Results

### Overview Tab
- **Summary Stats:** Mapped records, mapping rules, average confidence
- **Quality Report Summary:** Overall score, pass rate, completeness, accuracy
- **Cleanup Actions Summary:** Number of recommended actions

### Mapping Rules Tab
- Table showing all source → target field mappings
- Confidence scores for each mapping
- Extraction method (LLM, regex, semantic)
- Transformation rules (if any)

### Sample Data Tab
- Preview of first 10 mapped records
- Shows how source data was transformed to target format

### Citations Tab
- Source locations for each mapped field
- Confidence scores for citations
- Helps verify data accuracy

### Quality Tab (structured→structured only)
- **Quality Metrics:** Overall score, pass rate, completeness, accuracy
- **Issues Breakdown:** By type and severity
- **Quality Issues Table:** Filterable list of all issues
- **Record Metrics:** Total, passed, failed, with issues

### Cleanup Tab (structured→structured only)
- **Prioritized Actions:** High, medium, low priority
- **Action Details:** Description, affected records, examples
- **Suggested Transformations:** Code examples for fixes
- **Export:** Download cleanup report

---

## 💾 Exporting Results

### Export Options
1. **Excel** - Download as .xlsx file
2. **JSON** - Download as .json file
3. **CSV** - Download as .csv file

### Export Location
- Click export buttons in **Mapping Results Display** header
- Files download to your default download folder

---

## 🔍 Tips & Best Practices

### For Unstructured → Structured Mapping
- ✅ Use clear, well-formatted source documents
- ✅ Provide a complete target template
- ✅ Set minimum confidence to 0.8+ for high-quality results
- ✅ Enable citations to verify source locations

### For Structured → Structured Mapping
- ✅ Enable Quality Validation for data quality checks
- ✅ Review Quality Dashboard for issues
- ✅ Use Cleanup Actions to fix source data
- ✅ Export cleanup report for source file teams

### General Tips
- ✅ Start with "Auto-detect" mapping type
- ✅ Review mapping rules before accepting results
- ✅ Check citations for accuracy
- ✅ Export results for further processing

---

## ❓ Troubleshooting

### "Please select both source and target files"
- **Solution:** Make sure both Source File and Target File are selected

### "Mapping failed" error
- **Check:** File IDs are valid
- **Check:** Files are accessible
- **Check:** Backend service is running
- **Solution:** Try again or contact support

### No results displayed
- **Check:** Mapping completed successfully (check status)
- **Check:** Results tab is selected
- **Solution:** Try refreshing or re-executing mapping

### Quality Dashboard shows no issues
- **This is good!** Your data quality is high
- Quality validation only runs for structured→structured mappings

---

## 🔗 Related Documentation

- `PHASE_6_FRONTEND_EVALUATION.md` - Detailed evaluation and plan
- `PHASE_6_FRONTEND_IMPLEMENTATION_COMPLETE.md` - Implementation details
- `DATA_MAPPING_UNIFIED_DESIGN.md` - Backend design and architecture
- `DATA_MAPPING_IMPLEMENTATION_SUMMARY.md` - Backend implementation summary

---

**Status:** ✅ Ready for Use  
**Support:** See troubleshooting section or contact development team













