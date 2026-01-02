# Data Mapping User Flow Guide

**Date:** January 2025  
**Purpose:** Step-by-step guide for using the Data Mapping feature

---

## ✅ Your Proposed Flow is Correct!

Your flow matches exactly what we've built. Here's the detailed step-by-step process:

---

## 📋 Step-by-Step Flow

### Step 1: Upload Files to Content Pillar ✅

1. Navigate to **Content Pillar**
2. Upload your **license PDF** (source file)
3. Upload your **sample data model** (target file - Excel/CSV/JSON)
4. Both files should appear in your file list

**What happens:**
- Files are stored in Content Pillar
- Each file gets a unique `file_id`

---

### Step 2: Parse Files ✅

1. For each file, click **Parse** (or use bulk parse if available)
2. Wait for parsing to complete
3. Verify parsing was successful

**What happens:**
- Files are parsed using FileParserService
- Parsed data is stored
- A `parsed_file` record is created with `content_metadata_id`

**For License PDF:**
- Text extraction (PyPDF2)
- Table extraction (pdfplumber) if tables exist
- Result: Parsed text and/or structured tables

**For Sample Data Model (Excel/CSV):**
- Column extraction
- Schema detection
- Result: Structured data with schema

---

### Step 3: Complete Metadata Extraction / Embeddings / Semantic Data Layer ✅

**This step is critical for data mapping!**

1. Ensure **metadata extraction** is complete
   - File metadata (name, type, size, etc.)
   - Content metadata (schema, structure, etc.)

2. Ensure **embeddings** are created
   - Semantic embeddings for schema/metadata
   - Content embeddings for text/data
   - These are used for semantic matching in mapping

3. Ensure **semantic data layer** is populated
   - Embeddings stored in ArangoDB
   - Content metadata linked to embeddings
   - Ready for semantic search/matching

**What happens:**
- ContentSteward creates content_metadata records
- Semantic data abstraction stores embeddings
- Links between files, parsed data, and embeddings are established

**Why this matters:**
- The mapping workflow uses embeddings for semantic field matching
- Without embeddings, mapping will fall back to basic matching
- Quality of embeddings = quality of mapping

---

### Step 4: Navigate to Insights Pillar ✅

1. Navigate to **Insights Pillar**
2. Scroll down to **Section 3: Data Mapping**
3. You should see:
   - **Source File** card (left)
   - **Target File** card (right)
   - **Mapping Options** card (below)

---

### Step 5: Select Files for Mapping ✅

1. **Select Source File:**
   - Click on **Source File** card
   - Use the file selector dropdown
   - Select your **license PDF**
   - File should appear as selected

2. **Select Target File:**
   - Click on **Target File** card
   - Use the file selector dropdown
   - Select your **sample data model** (Excel/CSV)
   - File should appear as selected

**What happens:**
- File selector loads files from Content Pillar using `ContentAPIManager.listFiles()`
- Files are filtered by type (unstructured for source, structured for target)
- Selected file IDs are stored in component state

---

### Step 6: Configure Mapping Options (Optional) ✅

1. **Mapping Type:**
   - Usually **Auto-detect** works best
   - Or select **Unstructured → Structured** explicitly

2. **Minimum Confidence:**
   - Default: 80%
   - Adjust slider if needed

3. **Include Citations:**
   - Recommended: **Enabled**
   - Shows source location for each mapped field

4. **Quality Validation:**
   - Only for structured→structured mappings
   - Not needed for PDF → Excel

---

### Step 7: Execute Mapping ✅

1. Click **Execute Mapping** button
2. Wait for mapping to complete (progress indicator shown)
3. Results will appear below

**What happens behind the scenes:**
1. Frontend calls `/api/v1/insights-solution/mapping` with:
   - `source_file_id`: Your license PDF file ID
   - `target_file_id`: Your sample data model file ID
   - `mapping_options`: Your configuration

2. Backend workflow:
   - Detects mapping type (unstructured→structured)
   - Gets file metadata from ContentSteward
   - Gets parsed files from ContentSteward
   - Gets embeddings from semantic data abstraction
   - Extracts schemas from source and target
   - Generates mapping rules using semantic matching
   - Extracts fields from PDF using Field Extraction Service
   - Transforms data to target format
   - Generates output file
   - Returns complete results

3. Frontend displays:
   - Mapping rules table
   - Sample mapped records
   - Citations (source locations)
   - Export options

---

## 🎯 Expected Results

### For License PDF → Excel Mapping:

**You should see:**
1. **Mapping Rules:**
   - Source fields (from PDF) → Target fields (from Excel)
   - Confidence scores for each mapping
   - Extraction method (LLM, regex, semantic)

2. **Sample Data:**
   - Preview of mapped records
   - Shows how PDF data was transformed to Excel format

3. **Citations:**
   - Source location for each field (e.g., "Page 1, Section 2")
   - Confidence scores

4. **Export Options:**
   - Download as Excel, JSON, or CSV

---

## ⚠️ Important Notes

### Prerequisites:
- ✅ Files must be **parsed** (Step 2)
- ✅ **Embeddings must be created** (Step 3) - Critical!
- ✅ Files must be accessible via Content Pillar

### If Mapping Fails:
1. **Check file parsing:**
   - Verify files are parsed successfully
   - Check parsed data is available

2. **Check embeddings:**
   - Verify embeddings were created
   - Check semantic data layer is populated

3. **Check file IDs:**
   - Verify correct files are selected
   - Check file IDs are valid

4. **Check backend logs:**
   - Look for errors in mapping workflow
   - Check service availability

---

## 🔍 Troubleshooting

### "Files not showing in selector"
- **Solution:** Ensure files are uploaded and parsed in Content Pillar
- **Check:** File list API returns your files

### "Mapping failed - file not found"
- **Solution:** Verify file IDs are correct
- **Check:** Files exist in Content Pillar

### "Mapping failed - no embeddings"
- **Solution:** Complete Step 3 (metadata extraction/embeddings)
- **Check:** Semantic data layer has embeddings for your files

### "Low confidence scores"
- **Solution:** Ensure embeddings are high quality
- **Check:** Source and target schemas are clear

---

## 📊 What Gets Created

### Output Files:
- **Mapped Excel file** (or JSON/CSV based on target)
- Contains transformed data from source
- Includes citations and confidence scores

### Metadata:
- **Mapping ID:** Unique identifier for this mapping
- **Workflow ID:** Tracks the mapping operation
- **Lineage:** Tracks data transformation history

---

## ✅ Success Criteria

Your mapping is successful if:
1. ✅ Mapping rules are generated
2. ✅ Mapped records are created
3. ✅ Citations are available
4. ✅ Output file is generated
5. ✅ You can export the results

---

**Your flow is perfect!** Just make sure Step 3 (embeddings) is complete before mapping. 🚀













