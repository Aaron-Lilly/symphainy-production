# Content Pillar Upload UX Recommendation

## Current Issues

### Non-MECE Tiles
Current structure has overlapping categories:
- **PDF** tile includes both PDF and DOCX (mixing formats)
- **SOP/Workflow** also includes DOCX and PDF (duplication)
- **Image** is separate but should be part of unstructured
- **Binary** is separate but should be part of structured (with special handling)

### Misalignment with Backend
- Frontend uses: `Structured`, `Image`, `PDF`, `Binary`, `SOP/Workflow`
- Backend uses: `structured`, `unstructured`, `hybrid` (content_type)
- No clear mapping between frontend categories and backend classification

## Recommended Structure

### Primary Selection: Content Type (MECE)

Use the 3 content types as the primary selector, aligned with backend:

1. **Structured Data** (`structured`)
   - Tabular/spreadsheet data
   - Binary files with copybooks
   - Machine-readable formats
   
2. **Unstructured Documents** (`unstructured`)
   - Text documents
   - PDFs
   - Images
   - Rich text formats
   
3. **Hybrid Content** (`hybrid`)
   - Documents with embedded structured data
   - Complex formats requiring special handling

### Secondary Selection: File Type Category

After selecting content type, show relevant file type categories:

#### Structured Data → File Types:
- **Spreadsheets**: `.csv`, `.xlsx`, `.xls`, `.parquet`
- **Binary Files**: `.bin`, `.dat` (⚠️ requires copybook)
- **Data Formats**: `.json`, `.xml`, `.yaml`

#### Unstructured Documents → File Types:
- **Documents**: `.docx`, `.doc`, `.txt`, `.md`, `.rtf`
- **PDFs**: `.pdf`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`
- **SOP/Workflow**: `.docx`, `.pdf`, `.bpmn`, `.txt`, `.json` (⚠️ parsed in operations pillar)

#### Hybrid Content → File Types:
- **Complex Documents**: `.docx` (with tables), `.pdf` (with forms)
- **Multi-format**: Files that contain both structured and unstructured data

## Recommended UI Flow

### Option 1: Two-Step Selection (Recommended)

**Step 1: Select Content Type**
```
┌─────────────────────────────────────────┐
│  What type of content are you uploading? │
├─────────────────────────────────────────┤
│  [📊 Structured Data]                    │
│  Tabular data, spreadsheets, binary     │
│                                         │
│  [📄 Unstructured Documents]             │
│  Text, PDFs, images, documents          │
│                                         │
│  [🔄 Hybrid Content]                     │
│  Complex documents with mixed content   │
└─────────────────────────────────────────┘
```

**Step 2: Select File Type Category**
After selecting "Structured Data":
```
┌─────────────────────────────────────────┐
│  Select file type:                      │
├─────────────────────────────────────────┤
│  [📈 Spreadsheet]                       │
│  .csv, .xlsx, .xls, .parquet            │
│                                         │
│  [💾 Binary File] ⚠️                     │
│  .bin, .dat (copybook required)          │
│                                         │
│  [📋 Data Format]                        │
│  .json, .xml, .yaml                     │
└─────────────────────────────────────────┘
```

After selecting "Unstructured Documents:
```
┌─────────────────────────────────────────┐
│  Select file type:                      │
├─────────────────────────────────────────┤
│  [📝 Document]                           │
│  .docx, .doc, .txt, .md, .rtf            │
│                                         │
│  [📑 PDF]                                │
│  .pdf                                   │
│                                         │
│  [🖼️ Image]                              │
│  .jpg, .jpeg, .png, .gif, .bmp, .svg    │
│                                         │
│  [⚙️ SOP/Workflow] ⚠️                    │
│  .docx, .pdf, .bpmn, .txt, .json        │
│  (Parsed in Operations pillar)          │
└─────────────────────────────────────────┘
```

### Option 2: Single Selection with Grouping (Alternative)

Show all options in one view, grouped by content type:

```
┌─────────────────────────────────────────┐
│  Select file type:                      │
├─────────────────────────────────────────┤
│  📊 STRUCTURED DATA                      │
│  ┌─────────────────────────────────────┐│
│  │ 📈 Spreadsheet (.csv, .xlsx, .xls)  ││
│  │ 💾 Binary (.bin, .dat) ⚠️            ││
│  │ 📋 Data Format (.json, .xml)         ││
│  └─────────────────────────────────────┘│
│                                         │
│  📄 UNSTRUCTURED DOCUMENTS               │
│  ┌─────────────────────────────────────┐│
│  │ 📝 Document (.docx, .doc, .txt)      ││
│  │ 📑 PDF (.pdf)                        ││
│  │ 🖼️ Image (.jpg, .png, .gif)          ││
│  │ ⚙️ SOP/Workflow (.docx, .pdf) ⚠️     ││
│  └─────────────────────────────────────┘│
│                                         │
│  🔄 HYBRID CONTENT                       │
│  ┌─────────────────────────────────────┐│
│  │ 🔀 Complex Document (.docx, .pdf)    ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## Special Cases Handling

### 1. Binary Files (Require Copybook)

**UI Flow:**
1. User selects "Structured Data" → "Binary File"
2. Upload area shows:
   ```
   ┌─────────────────────────────────────────┐
   │  Step 1: Upload Binary File              │
   │  [Drop binary file here]                 │
   │  Selected: policy_master.dat             │
   ├─────────────────────────────────────────┤
   │  Step 2: Upload Copybook (Required) ⚠️   │
   │  [Drop copybook file here]               │
   │  Selected: copybook.cpy                 │
   └─────────────────────────────────────────┘
   ```
3. Upload button disabled until both files selected
4. Both files uploaded together with metadata linking them

**Backend Handling:**
- Upload binary file → get `file_id_1`
- Upload copybook → get `file_id_2`
- Create file link: `file_id_2` → `parsed_from` → `file_id_1`
- When parsing, use both files

### 2. SOP/Workflow Files (Parsed in Operations Pillar)

**UI Flow:**
1. User selects "Unstructured Documents" → "SOP/Workflow"
2. Upload proceeds normally in Content Pillar
3. After upload, show notification:
   ```
   ✅ File uploaded to Content Pillar
   ℹ️ This file will be parsed in Operations Pillar
   ```
4. File appears in:
   - Content Pillar: Uploaded files list
   - Operations Pillar: Files ready for parsing

**Backend Handling:**
- Upload to Content Pillar (normal flow)
- Set `pillar_origin: "content_pillar"` in metadata
- Set `processing_pillar: "operations_pillar"` in metadata
- Operations Pillar queries for files with `processing_pillar: "operations_pillar"`

## Implementation Details

### TypeScript Types

```typescript
// Content Type (Primary)
export enum ContentType {
  STRUCTURED = "structured",
  UNSTRUCTURED = "unstructured",
  HYBRID = "hybrid"
}

// File Type Category (Secondary)
export enum FileTypeCategory {
  // Structured
  SPREADSHEET = "spreadsheet",
  BINARY = "binary",
  DATA_FORMAT = "data_format",
  
  // Unstructured
  DOCUMENT = "document",
  PDF = "pdf",
  IMAGE = "image",
  SOP_WORKFLOW = "sop_workflow",
  
  // Hybrid
  COMPLEX_DOCUMENT = "complex_document"
}

// File Type Configuration
export interface FileTypeConfig {
  contentType: ContentType;
  category: FileTypeCategory;
  label: string;
  extensions: string[];
  mimeTypes: string[];
  requiresCopybook?: boolean;
  processingPillar?: "content_pillar" | "operations_pillar";
  description?: string;
}

export const FILE_TYPE_CONFIGS: FileTypeConfig[] = [
  // Structured Data
  {
    contentType: ContentType.STRUCTURED,
    category: FileTypeCategory.SPREADSHEET,
    label: "Spreadsheet",
    extensions: [".csv", ".xlsx", ".xls", ".parquet"],
    mimeTypes: [
      "text/csv",
      "application/vnd.ms-excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "application/parquet"
    ]
  },
  {
    contentType: ContentType.STRUCTURED,
    category: FileTypeCategory.BINARY,
    label: "Binary File",
    extensions: [".bin", ".dat"],
    mimeTypes: ["application/octet-stream"],
    requiresCopybook: true,
    description: "Requires copybook file for parsing"
  },
  {
    contentType: ContentType.STRUCTURED,
    category: FileTypeCategory.DATA_FORMAT,
    label: "Data Format",
    extensions: [".json", ".xml", ".yaml"],
    mimeTypes: [
      "application/json",
      "application/xml",
      "application/yaml"
    ]
  },
  
  // Unstructured Documents
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.DOCUMENT,
    label: "Document",
    extensions: [".docx", ".doc", ".txt", ".md", ".rtf"],
    mimeTypes: [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
      "text/plain",
      "text/markdown",
      "application/rtf"
    ]
  },
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.PDF,
    label: "PDF",
    extensions: [".pdf"],
    mimeTypes: ["application/pdf"]
  },
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.IMAGE,
    label: "Image",
    extensions: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    mimeTypes: [
      "image/jpeg",
      "image/png",
      "image/gif",
      "image/bmp",
      "image/svg+xml"
    ]
  },
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.SOP_WORKFLOW,
    label: "SOP/Workflow",
    extensions: [".docx", ".pdf", ".bpmn", ".txt", ".json"],
    mimeTypes: [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/pdf",
      "application/xml",
      "text/plain",
      "application/json"
    ],
    processingPillar: "operations_pillar",
    description: "Uploaded in Content Pillar, parsed in Operations Pillar"
  },
  
  // Hybrid Content
  {
    contentType: ContentType.HYBRID,
    category: FileTypeCategory.COMPLEX_DOCUMENT,
    label: "Complex Document",
    extensions: [".docx", ".pdf"],
    mimeTypes: [
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/pdf"
    ],
    description: "Documents with embedded structured data"
  }
];
```

### Component Structure

```typescript
// ContentPillarUpload.tsx
interface UploadState {
  step: "content_type" | "file_category" | "upload";
  contentType: ContentType | null;
  fileCategory: FileTypeCategory | null;
  selectedFile: File | null;
  copybookFile: File | null; // For binary files
  uploading: boolean;
}

// Two-step flow:
// 1. Select ContentType → shows relevant FileTypeCategory options
// 2. Select FileTypeCategory → shows upload area with special handling
// 3. Upload → handles binary+copybook or SOP/Workflow routing
```

## Benefits

1. **MECE Structure**: Content types are mutually exclusive and collectively exhaustive
2. **Backend Alignment**: Maps directly to `content_type` in Supabase schema
3. **Clear User Journey**: Progressive disclosure (content type → file category → upload)
4. **Special Case Handling**: Binary copybook and SOP/Workflow routing are explicit
5. **Extensible**: Easy to add new file types to existing categories
6. **User-Friendly**: Shows supported extensions for each category

## Migration Path

1. **Phase 1**: Add new content type selector (keep old tiles as fallback)
2. **Phase 2**: Update file upload component to use new structure
3. **Phase 3**: Update backend to receive `content_type` and `file_type_category`
4. **Phase 4**: Remove old tile-based selection
5. **Phase 5**: Update file dashboard to show content type badges

## Example User Flow

**Scenario 1: Upload Binary File with Copybook**
1. User clicks "Upload File"
2. Selects "Structured Data"
3. Selects "Binary File" → sees "⚠️ Copybook required"
4. Drops `policy_master.dat`
5. Drops `copybook.cpy`
6. Clicks "Upload" → both files uploaded, linked in backend

**Scenario 2: Upload SOP Document**
1. User clicks "Upload File"
2. Selects "Unstructured Documents"
3. Selects "SOP/Workflow" → sees "ℹ️ Parsed in Operations Pillar"
4. Drops `standard_operating_procedure.docx`
5. Clicks "Upload" → file uploaded to Content Pillar, marked for Operations parsing

**Scenario 3: Upload Spreadsheet**
1. User clicks "Upload File"
2. Selects "Structured Data"
3. Selects "Spreadsheet"
4. Drops `claims_data.xlsx`
5. Clicks "Upload" → file uploaded, ready for parsing in Content Pillar






