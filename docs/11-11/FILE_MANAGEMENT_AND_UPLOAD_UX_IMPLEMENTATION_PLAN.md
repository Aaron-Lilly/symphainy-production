# File Management and Upload UX Implementation Plan

## Overview

This plan combines two critical improvements:
1. **File ID and Filename Architecture Fix** - Proper UUID handling, filename parsing, and field mapping
2. **Content Pillar Upload UX Redesign** - MECE content type structure aligned with backend

## Goals

- ✅ Fix `file_id` = "None" issue in tests
- ✅ Preserve original filenames for user display
- ✅ Enable proper file type classification
- ✅ Support derivative file naming
- ✅ Align frontend UX with backend architecture
- ✅ Handle special cases (binary+copybook, SOP/Workflow routing)

---

## Phase 1: Backend File ID and Filename Architecture

### Step 1.1: Create File Utility Functions

**File:** `symphainy-platform/foundations/public_works_foundation/utilities/file_utils.py`

```python
#!/usr/bin/env python3
"""
File Utility Functions

Utility functions for filename parsing and content type determination.
"""

import os
from typing import Dict, Any, Tuple


def parse_filename(filename: str) -> Dict[str, Any]:
    """
    Parse filename into components.
    
    Args:
        filename: Original filename (e.g., "userfile.docx")
        
    Returns:
        {
            "ui_name": "userfile",
            "file_extension": ".docx",
            "file_extension_clean": "docx",
            "original_filename": "userfile.docx"
        }
    """
    if '.' in filename:
        name, ext = os.path.splitext(filename)
        return {
            "ui_name": name,
            "file_extension": ext,  # Includes dot: ".docx"
            "file_extension_clean": ext.lstrip('.'),  # Without dot: "docx"
            "original_filename": filename
        }
    else:
        return {
            "ui_name": filename,
            "file_extension": "",
            "file_extension_clean": "",
            "original_filename": filename
        }


def determine_content_type(file_extension: str, mime_type: str) -> Dict[str, str]:
    """
    Determine content type and file type category.
    
    Args:
        file_extension: File extension (e.g., ".docx")
        mime_type: MIME type
        
    Returns:
        {
            "content_type": "unstructured" | "structured" | "hybrid",
            "file_type_category": "document" | "spreadsheet" | "binary" | "image" | "pdf" | "text"
        }
    """
    ext_lower = file_extension.lower().lstrip('.')
    
    # Structured data
    structured_exts = ['csv', 'xlsx', 'xls', 'json', 'xml', 'parquet', 'yaml']
    if ext_lower in structured_exts:
        return {
            "content_type": "structured",
            "file_type_category": "spreadsheet" if ext_lower in ['xlsx', 'xls', 'csv'] else "data_format"
        }
    
    # Binary files (with copybooks)
    binary_exts = ['dat', 'bin', 'cpy']
    if ext_lower in binary_exts:
        return {
            "content_type": "structured",
            "file_type_category": "binary"
        }
    
    # Unstructured documents
    doc_exts = ['doc', 'docx', 'txt', 'md', 'rtf']
    if ext_lower in doc_exts:
        return {
            "content_type": "unstructured",
            "file_type_category": "document"
        }
    
    # PDFs
    if ext_lower == 'pdf':
        return {
            "content_type": "unstructured",
            "file_type_category": "pdf"
        }
    
    # Images
    image_exts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']
    if ext_lower in image_exts:
        return {
            "content_type": "unstructured",
            "file_type_category": "image"
        }
    
    # BPMN (workflow)
    if ext_lower == 'bpmn':
        return {
            "content_type": "unstructured",
            "file_type_category": "sop_workflow"
        }
    
    # Default
    return {
        "content_type": "unstructured",
        "file_type_category": "text"
    }
```

**Acceptance Criteria:**
- ✅ `parse_filename("userfile.docx")` returns `{"ui_name": "userfile", "file_extension": ".docx", ...}`
- ✅ `determine_content_type(".docx", "application/...")` returns `{"content_type": "unstructured", "file_type_category": "document"}`
- ✅ Handles edge cases (no extension, multiple dots, etc.)

---

### Step 1.2: Update Content Analysis Orchestrator

**File:** `symphainy-platform/backend/business_enablement/business_orchestrator/use_cases/mvp/content_analysis_orchestrator/content_analysis_orchestrator.py`

**Changes:**
1. Import file utilities
2. Parse filename in `handle_content_upload()`
3. Determine content type
4. Map fields correctly to Content Steward
5. Return proper `file_id` (UUID) in response

```python
from foundations.public_works_foundation.utilities.file_utils import (
    parse_filename,
    determine_content_type
)

async def handle_content_upload(
    self,
    file_data: bytes,
    filename: str,  # Original filename: "userfile.docx"
    file_type: str,  # MIME type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    user_id: str = "api_user",
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Handle file upload with proper filename parsing."""
    
    # Step 1: Parse filename
    file_components = parse_filename(filename)
    
    # Step 2: Determine content type
    content_info = determine_content_type(
        file_components["file_extension"],
        file_type
    )
    
    # Step 3: Prepare metadata for Content Steward
    metadata = {
        "user_id": user_id,
        "ui_name": file_components["ui_name"],  # ✅ Correct field name
        "file_type": file_components["file_extension_clean"],  # ✅ Extension, not MIME
        "mime_type": file_type,  # ✅ MIME type separately
        "original_filename": file_components["original_filename"],  # ✅ Full original name
        "content_type": content_info["content_type"],  # ✅ For Supabase schema
        "file_type_category": content_info["file_type_category"],  # ✅ For processing logic
        "uploaded_at": datetime.utcnow().isoformat(),
        "size_bytes": len(file_data)
    }
    
    # Step 4: Upload via Content Steward
    upload_result = await content_steward.process_upload(
        file_data, 
        file_type,  # MIME type
        metadata
    )
    
    # Step 5: Return with proper field names
    file_uuid = upload_result.get("uuid") or upload_result.get("file_id")
    
    if not file_uuid:
        raise Exception("File upload failed: no UUID returned")
    
    return {
        "success": True,
        "file_id": file_uuid,  # ✅ Use UUID as file_id
        "uuid": file_uuid,  # ✅ Also return as uuid for clarity
        "ui_name": file_components["ui_name"],  # ✅ User-friendly name
        "original_filename": file_components["original_filename"],  # ✅ Full original name
        "file_extension": file_components["file_extension"],  # ✅ Extension with dot
        "file_type": file_components["file_extension_clean"],  # ✅ Extension without dot
        "mime_type": file_type,  # ✅ MIME type
        "content_type": content_info["content_type"],  # ✅ Classification
        "file_type_category": content_info["file_type_category"],  # ✅ Category
        "size": len(file_data),
        "message": "File uploaded successfully",
        "mode": "gcs_supabase",
        "workflow_id": workflow_id,
        "orchestrator": "ContentAnalysisOrchestrator"
    }
```

**Acceptance Criteria:**
- ✅ `file_id` is always a valid UUID (never `None` or `"None"`)
- ✅ `ui_name` is extracted correctly (e.g., "userfile" from "userfile.docx")
- ✅ `file_type` is extension (e.g., "docx"), not MIME type
- ✅ `content_type` is set correctly (structured/unstructured/hybrid)
- ✅ All fields mapped correctly to Content Steward

---

### Step 1.3: Update Content Steward File Processing

**File:** `symphainy-platform/backend/smart_city/services/content_steward/modules/file_processing.py`

**Changes:**
1. Ensure `ui_name` is always set (fallback to parsing filename if missing)
2. Map `file_type` correctly (extension, not MIME)
3. Return `uuid` as `file_id` in response (never `None`)

```python
async def process_upload(
    self, 
    file_data: bytes, 
    content_type: str,  # MIME type
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process uploaded file with proper metadata mapping."""
    
    # Ensure ui_name is set
    if not metadata or "ui_name" not in metadata:
        # Fallback: extract from filename if provided
        filename = metadata.get("filename") if metadata else None
        if filename:
            from foundations.public_works_foundation.utilities.file_utils import parse_filename
            file_components = parse_filename(filename)
            ui_name = file_components["ui_name"]
        else:
            ui_name = f"file_{uuid.uuid4()}"
    else:
        ui_name = metadata["ui_name"]
    
    # Get file_type (extension) from metadata, fallback to extracting from mime_type
    file_type = metadata.get("file_type") if metadata else None
    if not file_type:
        # Try to extract from original_filename if available
        original_filename = metadata.get("original_filename") if metadata else None
        if original_filename:
            from foundations.public_works_foundation.utilities.file_utils import parse_filename
            file_components = parse_filename(original_filename)
            file_type = file_components["file_extension_clean"]
        else:
            file_type = "unknown"
    
    # Prepare file record for abstraction layer
    file_record = {
        "user_id": metadata.get("user_id") if metadata else "system",
        "ui_name": ui_name,  # ✅ User-friendly name
        "file_type": file_type,  # ✅ Extension
        "mime_type": content_type,  # ✅ MIME type
        "file_content": file_data,
        "metadata": {
            "original_filename": metadata.get("original_filename"),
            "file_extension": metadata.get("file_extension"),
            "content_type": metadata.get("content_type"),
            "file_type_category": metadata.get("file_type_category"),
            **(metadata.get("metadata", {}) or {})
        },
        "status": "uploaded"
    }
    
    # Create file (generates UUID, stores in GCS + Supabase)
    result = await self.service.file_management_abstraction.create_file(file_record)
    
    file_uuid = result.get("uuid")
    if not file_uuid:
        raise Exception("File creation failed: no UUID returned from abstraction layer")
    
    # Return with UUID
    return {
        "success": True,
        "uuid": file_uuid,  # ✅ UUID from Supabase
        "file_id": file_uuid,  # ✅ Alias for compatibility
        "ui_name": result.get("ui_name"),
        "file_type": result.get("file_type"),
        "mime_type": result.get("mime_type"),
        "status": result.get("status")
    }
```

**Acceptance Criteria:**
- ✅ Always returns `uuid` and `file_id` (never `None`)
- ✅ `ui_name` is always set (parsed from filename if not provided)
- ✅ `file_type` is extension (not MIME type)
- ✅ Metadata includes `content_type` and `file_type_category`

---

### Step 1.4: Update Semantic API Router Response Models

**File:** `symphainy-platform/backend/experience/api/semantic/content_pillar_router.py`

**Changes:**
1. Update `UploadFileResponse` to include new fields
2. Map response correctly from orchestrator

```python
class UploadFileResponse(BaseModel):
    """Semantic response model for file upload."""
    success: bool
    file_id: Optional[str] = None  # UUID
    uuid: Optional[str] = None  # UUID (alias)
    ui_name: Optional[str] = None  # User-friendly name
    original_filename: Optional[str] = None  # Full original name
    file_extension: Optional[str] = None  # Extension with dot
    file_type: Optional[str] = None  # Extension without dot
    mime_type: Optional[str] = None  # MIME type
    content_type: Optional[str] = None  # structured/unstructured/hybrid
    file_type_category: Optional[str] = None  # document/spreadsheet/binary/etc.
    file_size: Optional[int] = None
    uploaded_at: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
```

**Acceptance Criteria:**
- ✅ Response includes all new fields
- ✅ `file_id` is always a valid UUID
- ✅ Frontend can display `ui_name` to users

---

## Phase 2: Frontend Content Pillar Upload UX

### Step 2.1: Update TypeScript Types

**File:** `symphainy-frontend/shared/types/file.ts`

**Changes:**
1. Add `ContentType` enum
2. Add `FileTypeCategory` enum
3. Add `FileTypeConfig` interface
4. Update `FileMetadata` to include new fields

```typescript
// Content Type (Primary - aligns with backend)
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
  icon?: string;
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
    ],
    icon: "📈"
  },
  {
    contentType: ContentType.STRUCTURED,
    category: FileTypeCategory.BINARY,
    label: "Binary File",
    extensions: [".bin", ".dat"],
    mimeTypes: ["application/octet-stream"],
    requiresCopybook: true,
    description: "Requires copybook file for parsing",
    icon: "💾"
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
    ],
    icon: "📋"
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
    ],
    icon: "📝"
  },
  {
    contentType: ContentType.UNSTRUCTURED,
    category: FileTypeCategory.PDF,
    label: "PDF",
    extensions: [".pdf"],
    mimeTypes: ["application/pdf"],
    icon: "📑"
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
    ],
    icon: "🖼️"
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
    description: "Uploaded in Content Pillar, parsed in Operations Pillar",
    icon: "⚙️"
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
    description: "Documents with embedded structured data",
    icon: "🔀"
  }
];

// Updated FileMetadata interface
export interface FileMetadata {
  uuid: string;
  file_id?: string;  // Alias for uuid
  user_id?: string | null;
  team_id?: string;
  ui_name: string;  // User-friendly name
  original_filename?: string;  // Full original filename
  file_extension?: string;  // Extension with dot
  file_type: string;  // Extension without dot (legacy compatibility)
  content_type?: ContentType;  // structured/unstructured/hybrid
  file_type_category?: FileTypeCategory;  // document/spreadsheet/etc.
  mime_type?: string;
  original_path: string;
  parsed_path?: string;
  status: FileStatus;
  metadata?: Record<string, any>;
  insights?: Record<string, any>;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
  deleted: boolean;
}
```

**Acceptance Criteria:**
- ✅ Types align with backend schema
- ✅ All file type configurations included
- ✅ Special cases (binary, SOP/Workflow) marked

---

### Step 2.2: Create New Content Pillar Upload Component

**File:** `symphainy-frontend/app/pillars/content/components/ContentPillarUpload.tsx`

**Features:**
1. Two-step selection (Content Type → File Category)
2. Special handling for binary files (copybook upload)
3. Special handling for SOP/Workflow (notification)
4. Integration with semantic API

```typescript
"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { UploadCloud, File, CheckCircle, AlertCircle, Loader2, Info } from 'lucide-react';
import { ContentType, FileTypeCategory, FILE_TYPE_CONFIGS, FileMetadata } from '@/shared/types/file';
import { useAuth } from '@/shared/agui/AuthProvider';
import { toast } from 'sonner';

interface UploadState {
  step: "content_type" | "file_category" | "upload";
  contentType: ContentType | null;
  fileCategory: FileTypeCategory | null;
  selectedFile: File | null;
  copybookFile: File | null;
  uploading: boolean;
  error: string | null;
  success: boolean;
}

export function ContentPillarUpload() {
  const { isAuthenticated, user } = useAuth();
  const [uploadState, setUploadState] = useState<UploadState>({
    step: "content_type",
    contentType: null,
    fileCategory: null,
    selectedFile: null,
    copybookFile: null,
    uploading: false,
    error: null,
    success: false,
  });

  // Get available file categories for selected content type
  const availableCategories = uploadState.contentType
    ? FILE_TYPE_CONFIGS.filter(config => config.contentType === uploadState.contentType)
    : [];

  // Get selected file type config
  const selectedConfig = uploadState.fileCategory
    ? FILE_TYPE_CONFIGS.find(config => config.category === uploadState.fileCategory)
    : null;

  // Handle content type selection
  const handleContentTypeSelect = (contentType: ContentType) => {
    setUploadState(prev => ({
      ...prev,
      contentType,
      step: "file_category",
      fileCategory: null,
      selectedFile: null,
      copybookFile: null,
      error: null
    }));
  };

  // Handle file category selection
  const handleFileCategorySelect = (category: FileTypeCategory) => {
    setUploadState(prev => ({
      ...prev,
      fileCategory: category,
      step: "upload",
      selectedFile: null,
      copybookFile: null,
      error: null
    }));
  };

  // Handle file drop
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setUploadState(prev => ({
        ...prev,
        selectedFile: acceptedFiles[0],
        error: null
      }));
    }
  }, []);

  // Handle copybook file selection
  const handleCopybookChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploadState(prev => ({
        ...prev,
        copybookFile: e.target.files![0],
        error: null
      }));
    }
  };

  // Get accept object for dropzone
  const getAcceptObject = () => {
    if (!selectedConfig) return undefined;
    
    const accept: Record<string, string[]> = {};
    selectedConfig.mimeTypes.forEach(mimeType => {
      accept[mimeType] = selectedConfig.extensions;
    });
    return accept;
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getAcceptObject(),
    multiple: false,
    disabled: !selectedConfig || !isAuthenticated,
  });

  // Handle upload
  const handleUpload = async () => {
    if (!uploadState.selectedFile || !selectedConfig) return;
    
    // Validate binary file has copybook
    if (selectedConfig.requiresCopybook && !uploadState.copybookFile) {
      setUploadState(prev => ({
        ...prev,
        error: "Please upload a copybook file for binary files."
      }));
      return;
    }

    setUploadState(prev => ({ ...prev, uploading: true, error: null }));

    try {
      // TODO: Replace with semantic API call
      const formData = new FormData();
      formData.append("file", uploadState.selectedFile);
      formData.append("user_id", user?.id || "anonymous");
      
      // Add copybook if required
      if (uploadState.copybookFile) {
        formData.append("copybook", uploadState.copybookFile);
      }

      const response = await fetch("/api/content-pillar/upload-file", {
        method: "POST",
        body: formData,
        headers: {
          "X-Session-Token": sessionStorage.getItem("session_token") || ""
        }
      });

      const result = await response.json();

      if (result.success) {
        setUploadState(prev => ({
          ...prev,
          uploading: false,
          success: true
        }));

        // Show notification for SOP/Workflow
        if (selectedConfig.processingPillar === "operations_pillar") {
          toast.info("File uploaded to Content Pillar", {
            description: "This file will be parsed in Operations Pillar"
          });
        } else {
          toast.success("File uploaded successfully!");
        }

        // Reset after delay
        setTimeout(() => {
          setUploadState({
            step: "content_type",
            contentType: null,
            fileCategory: null,
            selectedFile: null,
            copybookFile: null,
            uploading: false,
            error: null,
            success: false,
          });
        }, 2000);
      } else {
        throw new Error(result.error || "Upload failed");
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Upload failed";
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        error: errorMessage
      }));
      toast.error("Upload failed", { description: errorMessage });
    }
  };

  // Render content type selection
  if (uploadState.step === "content_type") {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Upload File</CardTitle>
          <CardDescription>
            What type of content are you uploading?
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <button
            onClick={() => handleContentTypeSelect(ContentType.STRUCTURED)}
            className="w-full p-4 text-left border rounded-lg hover:bg-accent transition-colors"
          >
            <div className="flex items-center space-x-3">
              <span className="text-2xl">📊</span>
              <div>
                <div className="font-medium">Structured Data</div>
                <div className="text-sm text-muted-foreground">
                  Tabular data, spreadsheets, binary files
                </div>
              </div>
            </div>
          </button>

          <button
            onClick={() => handleContentTypeSelect(ContentType.UNSTRUCTURED)}
            className="w-full p-4 text-left border rounded-lg hover:bg-accent transition-colors"
          >
            <div className="flex items-center space-x-3">
              <span className="text-2xl">📄</span>
              <div>
                <div className="font-medium">Unstructured Documents</div>
                <div className="text-sm text-muted-foreground">
                  Text, PDFs, images, documents
                </div>
              </div>
            </div>
          </button>

          <button
            onClick={() => handleContentTypeSelect(ContentType.HYBRID)}
            className="w-full p-4 text-left border rounded-lg hover:bg-accent transition-colors"
          >
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🔄</span>
              <div>
                <div className="font-medium">Hybrid Content</div>
                <div className="text-sm text-muted-foreground">
                  Complex documents with mixed content
                </div>
              </div>
            </div>
          </button>
        </CardContent>
      </Card>
    );
  }

  // Render file category selection
  if (uploadState.step === "file_category") {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Select File Type</CardTitle>
          <CardDescription>
            Choose the specific file type category
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {availableCategories.map(config => (
            <button
              key={config.category}
              onClick={() => handleFileCategorySelect(config.category)}
              className="w-full p-4 text-left border rounded-lg hover:bg-accent transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{config.icon}</span>
                  <div>
                    <div className="font-medium flex items-center space-x-2">
                      <span>{config.label}</span>
                      {config.requiresCopybook && (
                        <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                          ⚠️ Copybook Required
                        </span>
                      )}
                      {config.processingPillar && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          ℹ️ Parsed in {config.processingPillar === "operations_pillar" ? "Operations" : "Content"}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {config.extensions.join(", ")}
                    </div>
                    {config.description && (
                      <div className="text-xs text-muted-foreground mt-1">
                        {config.description}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </button>
          ))}

          <Button
            variant="outline"
            onClick={() => setUploadState(prev => ({ ...prev, step: "content_type", contentType: null }))}
            className="w-full mt-4"
          >
            ← Back
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Render upload area
  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload {selectedConfig?.label}</CardTitle>
        <CardDescription>
          {selectedConfig?.extensions.join(", ")} files
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main file upload */}
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors
            ${isDragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          `}
        >
          <input {...getInputProps()} />
          {uploadState.selectedFile ? (
            <div className="space-y-2">
              <CheckCircle className="h-8 w-8 text-green-500 mx-auto" />
              <div className="font-medium text-green-700">{uploadState.selectedFile.name}</div>
              <div className="text-sm text-green-600">
                {(uploadState.selectedFile.size / 1024).toFixed(2)} KB
              </div>
            </div>
          ) : (
            <div className="space-y-2">
              <UploadCloud className="h-8 w-8 text-gray-400 mx-auto" />
              <div className="font-medium text-gray-700">
                {isDragActive ? 'Drop the file here' : 'Drag & drop a file here'}
              </div>
              <div className="text-sm text-gray-500">
                or click to select a file
              </div>
            </div>
          )}
        </div>

        {/* Copybook upload (for binary files) */}
        {selectedConfig?.requiresCopybook && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Copybook File (Required) ⚠️</label>
            <input
              type="file"
              accept=".cpy,.copybook,.txt"
              onChange={handleCopybookChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
            {uploadState.copybookFile && (
              <div className="text-sm text-green-600">
                ✓ Selected: {uploadState.copybookFile.name}
              </div>
            )}
          </div>
        )}

        {/* SOP/Workflow notification */}
        {selectedConfig?.processingPillar === "operations_pillar" && (
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              This file will be uploaded to Content Pillar but parsed in Operations Pillar.
            </AlertDescription>
          </Alert>
        )}

        {/* Upload button */}
        <Button
          onClick={handleUpload}
          disabled={uploadState.uploading || !uploadState.selectedFile || (selectedConfig?.requiresCopybook && !uploadState.copybookFile)}
          className="w-full"
        >
          {uploadState.uploading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <UploadCloud className="h-4 w-4 mr-2" />
              Upload File
            </>
          )}
        </Button>

        {/* Error display */}
        {uploadState.error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{uploadState.error}</AlertDescription>
          </Alert>
        )}

        {/* Back button */}
        <Button
          variant="outline"
          onClick={() => setUploadState(prev => ({
            ...prev,
            step: "file_category",
            fileCategory: null,
            selectedFile: null,
            copybookFile: null
          }))}
          className="w-full"
        >
          ← Back
        </Button>
      </CardContent>
    </Card>
  );
}
```

**Acceptance Criteria:**
- ✅ Two-step selection flow works
- ✅ Binary files require copybook
- ✅ SOP/Workflow shows notification
- ✅ File uploads successfully
- ✅ Response includes all new fields

---

### Step 2.3: Update File Dashboard to Show New Fields

**File:** `symphainy-frontend/app/pillars/content/components/FileDashboardNew.tsx`

**Changes:**
1. Display `ui_name` instead of `file_type` for file names
2. Show `content_type` badge
3. Show `file_type_category` badge
4. Display `original_filename` in tooltip

**Acceptance Criteria:**
- ✅ Files display with user-friendly names
- ✅ Content type badges visible
- ✅ File type categories shown

---

## Phase 3: Binary File + Copybook Handling

### Step 3.1: Update Semantic API for Binary + Copybook

**File:** `symphainy-platform/backend/experience/api/semantic/content_pillar_router.py`

**Changes:**
1. Accept optional `copybook` file in upload endpoint
2. Upload both files
3. Create file link between them

```python
@router.post("/upload-file", response_model=UploadFileResponse)
async def upload_file_to_content_pillar(
    file: UploadFile = File(...),
    copybook: Optional[UploadFile] = File(None),  # NEW: Optional copybook
    user_id: str = Form(default="anonymous"),
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """Upload a file to the content pillar."""
    
    # Upload main file
    file_data = await file.read()
    result = await content_orch.handle_content_upload(
        file_data=file_data,
        filename=file.filename,
        file_type=file.content_type,
        user_id=user_id,
        session_id=session_id
    )
    
    file_uuid = result.get("file_id")
    
    # Upload copybook if provided
    copybook_uuid = None
    if copybook:
        copybook_data = await copybook.read()
        copybook_result = await content_orch.handle_content_upload(
            file_data=copybook_data,
            filename=copybook.filename,
            file_type=copybook.content_type,
            user_id=user_id,
            session_id=session_id
        )
        copybook_uuid = copybook_result.get("file_id")
        
        # Create file link: copybook → parsed_from → binary file
        # TODO: Implement file link creation via File Management Abstraction
    
    return UploadFileResponse(
        success=True,
        file_id=file_uuid,
        copybook_file_id=copybook_uuid,  # NEW
        # ... other fields
    )
```

**Acceptance Criteria:**
- ✅ Binary file uploads successfully
- ✅ Copybook uploads successfully
- ✅ File link created between them
- ✅ Parsing uses both files

---

## Phase 4: SOP/Workflow Routing

### Step 4.1: Mark Files for Operations Pillar Processing

**File:** `symphainy-platform/backend/business_enablement/business_orchestrator/use_cases/mvp/content_analysis_orchestrator/content_analysis_orchestrator.py`

**Changes:**
1. Check if `file_type_category` is `"sop_workflow"`
2. Set `processing_pillar: "operations_pillar"` in metadata
3. Store in Supabase with this flag

**Acceptance Criteria:**
- ✅ SOP/Workflow files marked correctly
- ✅ Operations Pillar can query for these files
- ✅ Files appear in both pillars appropriately

---

## Phase 5: Testing

### Step 5.1: Update Test Suite

**File:** `tests/e2e/test_semantic_apis_e2e.py`

**Changes:**
1. Test filename parsing
2. Test binary + copybook upload
3. Test SOP/Workflow routing
4. Verify `file_id` is always UUID

**Test Cases:**
- ✅ Upload `userfile.docx` → `file_id` is UUID, `ui_name` is "userfile"
- ✅ Upload binary file without copybook → error
- ✅ Upload binary file with copybook → both uploaded, linked
- ✅ Upload SOP document → marked for operations pillar
- ✅ All file types return proper `file_id` (never `None`)

---

## Implementation Timeline

### Day 1 (4 hours)
- ✅ Step 1.1: Create file utility functions
- ✅ Step 1.2: Update Content Analysis Orchestrator
- ✅ Step 1.3: Update Content Steward File Processing

### Day 2 (4 hours)
- ✅ Step 1.4: Update Semantic API Router
- ✅ Step 2.1: Update TypeScript Types
- ✅ Step 2.2: Create New Upload Component

### Day 3 (4 hours)
- ✅ Step 2.3: Update File Dashboard
- ✅ Step 3.1: Binary + Copybook Handling
- ✅ Step 4.1: SOP/Workflow Routing

### Day 4 (4 hours)
- ✅ Step 5.1: Update Test Suite
- ✅ Run full test suite
- ✅ Fix any issues
- ✅ Documentation

**Total: 16 hours (2 days full-time)**

---

## Success Criteria

1. ✅ All tests pass (including the `file_id` = "None" fix)
2. ✅ Files upload with proper UUIDs
3. ✅ Original filenames preserved for display
4. ✅ Content types correctly classified
5. ✅ Binary files require and link copybooks
6. ✅ SOP/Workflow files routed to Operations Pillar
7. ✅ Frontend UX is intuitive and MECE
8. ✅ Backend and frontend fully aligned

---

## Rollback Plan

If issues arise:
1. Keep old file upload component as fallback
2. Old API endpoints remain functional
3. Gradual migration (feature flag)

---

## Next Steps After Implementation

1. Run full E2E test suite
2. Test all 3 demo scenarios
3. Verify file display in dashboard
4. Test binary + copybook parsing
5. Test SOP/Workflow operations pillar integration






