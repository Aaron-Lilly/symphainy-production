# Data Mash Implementation Plan

**Date:** December 28, 2025  
**Status:** 🎯 **COMPREHENSIVE IMPLEMENTATION PLAN**  
**Goal:** Implement semantic layer extraction pattern and refactor frontend to showcase "Data Mash" capability

---

## 🎯 Executive Summary

**Vision:** Transform the "Metadata Extraction" section into a **"Data Mash"** showcase that demonstrates the platform's powerful 3-layer semantic embeddings pattern.

**The 3-Layer Pattern:**
1. **Layer 1 (Infrastructure):** File parsing → stores parsed files
2. **Layer 2 (Business Enablement):** Embedding creation → extracts metadata FROM parsed files, creates embeddings
3. **Layer 3 (Semantic Layer):** Embeddings storage → stores embeddings + metadata in ArangoDB

**What We're Building:**
- ✅ Backend: Automatic embedding creation after parsing
- ✅ Backend: List/preview pattern for semantic layer (like parsing)
- ✅ Frontend: Rename "Metadata Extraction" → "Data Mash"
- ✅ Frontend: New component to display semantic layer
- ✅ Integration: Connect frontend to semantic layer endpoints

---

## 📊 Current State Analysis

### **Backend:**
- ✅ `EmbeddingService` exists and creates embeddings
- ✅ `SemanticDataAbstraction` stores embeddings + metadata
- ❌ Orchestrator doesn't automatically create embeddings after parsing
- ❌ No `list_embeddings()` or `preview_embeddings()` methods

### **Frontend:**
- ✅ `ParsePreview.tsx` exists for parsing preview
- ❌ No component for semantic layer display
- ❌ "Metadata Extraction" section doesn't exist in current frontend (only in legacy)
- ❌ No API methods for semantic layer

---

## 🏗️ Implementation Phases

### **Phase 1: Backend - Orchestrator Integration (HIGH PRIORITY)**

**Goal:** Add explicit embedding creation method with parsed file selection (dropdown pattern, similar to parsing) AND integrate with Data Solution Orchestrator pattern

**Architecture Pattern:**
- ✅ ContentJourneyOrchestrator is called BY DataSolutionOrchestratorService
- ✅ ContentJourneyOrchestrator should NOT call DataSolutionOrchestratorService (avoids circular dependency)
- ✅ ContentJourneyOrchestrator calls Content realm services directly (EmbeddingService)
- ✅ Data Solution Orchestrator has `orchestrate_data_embed()` that routes to ContentJourneyOrchestrator

**Files to Modify:**
- `symphainy-platform/backend/journey/orchestrators/content_journey_orchestrator/content_orchestrator.py`
- `symphainy-platform/backend/solution/services/data_solution_orchestrator_service/data_solution_orchestrator_service.py` (complete TODO)

**Changes:**

1. **Add `create_embeddings()` method (ContentJourneyOrchestrator):**

```python
async def process_file(
    self,
    file_id: str,
    user_id: str,
    copybook_file_id: Optional[str] = None,
    processing_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process file: parse → store → create embeddings (semantic layer).
    
    Flow:
    1. Parse file via FileParserService
    2. Store parsed file via ContentSteward
    3. Create embeddings via EmbeddingService (for structured data)
    4. Return parse_result + content_id (semantic layer ID)
    """
    try:
        # ... existing parsing logic ...
        
        # After storing parsed file:
        if parsed_file_id and parse_result.get("parsing_type") == "structured":
            # Create embeddings automatically (semantic layer creation)
            embedding_result = await self._create_embeddings_after_parsing(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                parse_result=parse_result,
                user_id=user_id
            )
            content_id = embedding_result.get("content_id")
            embeddings_count = embedding_result.get("embeddings_count", 0)
        else:
            content_id = None
            embeddings_count = 0
        
        # Update result to include semantic layer info
        result = {
            "success": True,
            "file_id": file_id,
            "parse_result": parse_summary,
            "parsed_file_id": parsed_file_id,
            "content_id": content_id,  # NEW: Semantic layer ID
            "embeddings_count": embeddings_count,  # NEW: Embedding count
            "file_details": file_details.get("file", {}),
            "copybook_file_id": copybook_file_id,
            "message": "Parsing and semantic layer creation completed successfully",
            "note": "Full parsed data stored as JSONL in GCS. Semantic layer (embeddings + metadata) stored in ArangoDB."
        }
        
        return result
    except Exception as e:
        # ... error handling ...
```

2. **Add helper method `_create_embeddings_after_parsing()`:**

```python
async def _create_embeddings_after_parsing(
    self,
    file_id: str,
    parsed_file_id: str,
    parse_result: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Create embeddings after parsing (semantic layer creation).
    
    This is called automatically after parsing structured files.
    """
    try:
        # Get EmbeddingService (Content realm service)
        from backend.content.services.embedding_service.embedding_service import EmbeddingService
        
        embedding_service = EmbeddingService(
            service_name="EmbeddingService",
            realm_name="content",
            platform_gateway=self.delivery_manager.platform_gateway,
            di_container=self.delivery_manager.di_container
        )
        await embedding_service.initialize()
        
        # Prepare content metadata from parse result
        content_metadata = {
            "file_id": file_id,
            "parsed_file_id": parsed_file_id,
            "parsing_type": parse_result.get("parsing_type"),
            "structure": parse_result.get("structure", {}),
            "metadata": parse_result.get("metadata", {}),
            "record_count": len(parse_result.get("records", [])) if parse_result.get("records") else 0
        }
        
        # Create embeddings
        user_context = {"user_id": user_id}
        embedding_result = await embedding_service.create_representative_embeddings(
            parsed_file_id=parsed_file_id,
            content_metadata=content_metadata,
            sampling_strategy="every_nth",
            n=10,  # Every 10th row
            user_context=user_context
        )
        
        if not embedding_result.get("success"):
            self.logger.warning(f"⚠️ Embedding creation failed: {embedding_result.get('error')}")
            return {
                "success": False,
                "content_id": None,
                "embeddings_count": 0,
                "error": embedding_result.get("error")
            }
        
        return {
            "success": True,
            "content_id": embedding_result.get("content_id"),
            "embeddings_count": embedding_result.get("embeddings_count", 0) or embedding_result.get("stored_count", 0)
        }
    except Exception as e:
        self.logger.error(f"❌ Failed to create embeddings after parsing: {e}", exc_info=True)
        return {
            "success": False,
            "content_id": None,
            "embeddings_count": 0,
            "error": str(e)
        }
```

**Time Estimate:** 2-3 hours

**Testing:**
- List parsed files (should show dropdown options)
- Select a parsed file and create embeddings
- Verify `content_id` is returned in response
- Verify embeddings stored in ArangoDB
- Test with different parsed file types (structured, unstructured)

---

### **Phase 2: Backend - List/Preview Pattern (HIGH PRIORITY)**

**Goal:** Enable listing and previewing semantic layer (like parsing pattern)

**Files to Modify:**
- `symphainy-platform/backend/journey/orchestrators/content_journey_orchestrator/content_orchestrator.py`

**Changes:**

1. **Add `list_embeddings()` method:**

```python
async def list_embeddings(
    self,
    file_id: Optional[str],
    user_id: str
) -> Dict[str, Any]:
    """
    List all embeddings for a file (or all for user).
    
    Similar to list_parsed_files().
    
    Args:
        file_id: Optional file ID to filter by
        user_id: User identifier
    
    Returns:
        List of embeddings with metadata
    """
    try:
        # Get SemanticDataAbstraction
        semantic_data = await self._get_semantic_data_abstraction()
        if not semantic_data:
            return {
                "success": False,
                "error": "SemanticDataAbstraction not available",
                "embeddings": []
            }
        
        # Build filter conditions
        filters = {}
        if file_id:
            filters["file_id"] = file_id
        
        user_context = {"user_id": user_id}
        
        # Query embeddings
        if file_id:
            # Get all embeddings for this file
            embeddings = await semantic_data.get_semantic_embeddings(
                content_id=None,  # We're filtering by file_id
                filters=filters,
                user_context=user_context
            )
        else:
            # Get all embeddings for user (across all files)
            embeddings = await semantic_data.get_semantic_embeddings(
                content_id=None,
                filters={},  # No file filter
                user_context=user_context
            )
        
        # Group by content_id and file_id
        grouped = {}
        for emb in embeddings:
            content_id = emb.get("content_id")
            file_id = emb.get("file_id")
            key = f"{file_id}_{content_id}"
            
            if key not in grouped:
                grouped[key] = {
                    "file_id": file_id,
                    "content_id": content_id,
                    "embeddings_count": 0,
                    "columns": [],
                    "created_at": emb.get("created_at")
                }
            
            grouped[key]["embeddings_count"] += 1
            grouped[key]["columns"].append({
                "column_name": emb.get("column_name"),
                "data_type": emb.get("data_type"),
                "semantic_meaning": emb.get("semantic_meaning"),
                "semantic_id": emb.get("semantic_id")
            })
        
        return {
            "success": True,
            "embeddings": list(grouped.values()),
            "total_count": len(grouped)
        }
    except Exception as e:
        self.logger.error(f"❌ Failed to list embeddings: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "embeddings": []
        }
```

2. **Add `preview_embeddings()` method:**

```python
async def preview_embeddings(
    self,
    content_id: str,
    user_id: str,
    max_columns: int = 20
) -> Dict[str, Any]:
    """
    Preview semantic layer (embeddings + metadata).
    
    Similar to preview_parsed_file().
    Reconstructs preview from embeddings + metadata (not raw parsed data).
    
    Args:
        content_id: Content ID (semantic layer ID)
        user_id: User identifier
        max_columns: Maximum columns to return (default: 20)
    
    Returns:
        Preview structure with columns, semantic meanings, sample values
    """
    try:
        # Get SemanticDataAbstraction
        semantic_data = await self._get_semantic_data_abstraction()
        if not semantic_data:
            return {
                "success": False,
                "error": "SemanticDataAbstraction not available"
            }
        
        user_context = {"user_id": user_id}
        
        # Get embeddings for this content_id
        embeddings = await semantic_data.get_semantic_embeddings(
            content_id=content_id,
            filters={},
            user_context=user_context
        )
        
        if not embeddings:
            return {
                "success": False,
                "error": f"No embeddings found for content_id: {content_id}"
            }
        
        # Get ContentMetadataAbstraction for structure info
        content_metadata_abstraction = await self._get_content_metadata_abstraction()
        content_metadata = None
        if content_metadata_abstraction:
            content_metadata = await content_metadata_abstraction.get_content_metadata(content_id)
        
        # Build preview from embeddings + metadata
        columns = []
        for emb in embeddings[:max_columns]:
            columns.append({
                "column_name": emb.get("column_name"),
                "data_type": emb.get("data_type", "unknown"),
                "semantic_meaning": emb.get("semantic_meaning", ""),
                "semantic_id": emb.get("semantic_id"),
                "sample_values": emb.get("sample_values", [])[:10],  # First 10 samples
                "column_position": emb.get("column_position", 0),
                "row_count": emb.get("row_count", 0),
                "semantic_model_recommendation": emb.get("semantic_model_recommendation")
            })
        
        # Sort by column_position
        columns.sort(key=lambda x: x.get("column_position", 0))
        
        return {
            "success": True,
            "content_id": content_id,
            "file_id": embeddings[0].get("file_id") if embeddings else None,
            "columns": columns,
            "structure": {
                "column_count": len(embeddings),
                "row_count": columns[0].get("row_count", 0) if columns else 0,
                "table_count": 1
            },
            "semantic_model": {
                "recommendations": [
                    {
                        "column_name": col["column_name"],
                        "semantic_id": col.get("semantic_id"),
                        "confidence": col.get("semantic_model_recommendation", {}).get("confidence", 0.0) if col.get("semantic_model_recommendation") else None,
                        "meaning": col.get("semantic_meaning", "")
                    }
                    for col in columns
                ]
            }
        }
    except Exception as e:
        self.logger.error(f"❌ Failed to preview embeddings: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
```

3. **Add helper methods:**

```python
async def _get_semantic_data_abstraction(self):
    """Get SemanticDataAbstraction from DI container."""
    try:
        return await self.delivery_manager.di_container.get_abstraction("SemanticDataAbstraction")
    except Exception as e:
        self.logger.warning(f"⚠️ SemanticDataAbstraction not available: {e}")
        return None

async def _get_content_metadata_abstraction(self):
    """Get ContentMetadataAbstraction from DI container."""
    try:
        return await self.delivery_manager.di_container.get_abstraction("ContentMetadataAbstraction")
    except Exception as e:
        self.logger.warning(f"⚠️ ContentMetadataAbstraction not available: {e}")
        return None
```

4. **Add routing in `execute()` method:**

```python
# In execute() method, add routing for semantic layer endpoints:

elif method == "GET" and path == "list-embeddings":
    file_id = request_body.get("file_id")
    return await self.list_embeddings(file_id, user_id)

elif method == "GET" and path.startswith("preview-embeddings/"):
    content_id = path.replace("preview-embeddings/", "").split("/")[0]
    return await self.preview_embeddings(content_id, user_id)
```

**Time Estimate:** 3-4 hours

**Testing:**
- List embeddings for a file
- Preview embeddings for a content_id
- Verify preview reconstructs from embeddings + metadata
- Test with multiple files

---

### **Phase 3: Frontend - API Integration (MEDIUM PRIORITY)**

**Goal:** Add frontend API methods for semantic layer

**Files to Create/Modify:**
- `ontikMVP/frontend/lib/api/content.ts` (or equivalent API manager)

**Changes:**

1. **Add API methods:**

```typescript
// Add to ContentAPIManager or content API file

/**
 * List all embeddings for a file (or all for user)
 */
export async function listEmbeddings(
  fileId?: string,
  token?: string
): Promise<{
  success: boolean;
  embeddings: Array<{
    file_id: string;
    content_id: string;
    embeddings_count: number;
    columns: Array<{
      column_name: string;
      data_type: string;
      semantic_meaning: string;
      semantic_id?: string;
    }>;
    created_at: string;
  }>;
  total_count: number;
  error?: string;
}> {
  const url = fileId
    ? `/api/v1/content-pillar/list-embeddings?file_id=${fileId}`
    : `/api/v1/content-pillar/list-embeddings`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });
  
  if (!response.ok) {
    throw new Error(`Failed to list embeddings: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Preview semantic layer (embeddings + metadata)
 */
export async function previewEmbeddings(
  contentId: string,
  token?: string
): Promise<{
  success: boolean;
  content_id: string;
  file_id?: string;
  columns: Array<{
    column_name: string;
    data_type: string;
    semantic_meaning: string;
    semantic_id?: string;
    sample_values: string[];
    column_position: number;
    row_count: number;
    semantic_model_recommendation?: any;
  }>;
  structure: {
    column_count: number;
    row_count: number;
    table_count: number;
  };
  semantic_model: {
    recommendations: Array<{
      column_name: string;
      semantic_id?: string;
      confidence?: number;
      meaning: string;
    }>;
  };
  error?: string;
}> {
  const response = await fetch(`/api/v1/content-pillar/preview-embeddings/${contentId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });
  
  if (!response.ok) {
    throw new Error(`Failed to preview embeddings: ${response.statusText}`);
  }
  
  return response.json();
}
```

**Time Estimate:** 1-2 hours

**Testing:**
- Test API methods with real backend
- Verify error handling
- Test with and without authentication

---

### **Phase 4: Frontend - Data Mash Component (HIGH PRIORITY)**

**Goal:** Create "Data Mash" component to display semantic layer

**Files to Create:**
- `ontikMVP/frontend/components/content/DataMash.tsx` (NEW)

**Component Structure:**

```typescript
'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader } from '@/components/ui/loader';
import { toast } from 'sonner';
import { Brain, Database, Layers, Sparkles } from 'lucide-react';
import { FileMetadata } from 'shared/types/file';
import { listEmbeddings, previewEmbeddings } from '@/lib/api/content';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';

interface DataMashProps {
  selectedFile?: FileMetadata;
}

interface EmbeddingFile {
  file_id: string;
  content_id: string;
  embeddings_count: number;
  columns: Array<{
    column_name: string;
    data_type: string;
    semantic_meaning: string;
    semantic_id?: string;
  }>;
  created_at: string;
}

interface SemanticLayerPreview {
  content_id: string;
  file_id?: string;
  columns: Array<{
    column_name: string;
    data_type: string;
    semantic_meaning: string;
    semantic_id?: string;
    sample_values: string[];
    column_position: number;
    row_count: number;
    semantic_model_recommendation?: any;
  }>;
  structure: {
    column_count: number;
    row_count: number;
    table_count: number;
  };
  semantic_model: {
    recommendations: Array<{
      column_name: string;
      semantic_id?: string;
      confidence?: number;
      meaning: string;
    }>;
  };
}

export default function DataMash({ selectedFile }: DataMashProps) {
  const { guideSessionToken } = useGlobalSession();
  
  const [loading, setLoading] = useState(false);
  const [embeddingFiles, setEmbeddingFiles] = useState<EmbeddingFile[]>([]);
  const [selectedContentId, setSelectedContentId] = useState<string | null>(null);
  const [preview, setPreview] = useState<SemanticLayerPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  // Load embeddings when file is selected
  useEffect(() => {
    if (selectedFile?.uuid) {
      loadEmbeddings(selectedFile.uuid);
    }
  }, [selectedFile]);

  // Load preview when content_id is selected
  useEffect(() => {
    if (selectedContentId) {
      loadPreview(selectedContentId);
    }
  }, [selectedContentId]);

  const loadEmbeddings = async (fileId: string) => {
    setLoading(true);
    try {
      const result = await listEmbeddings(fileId, guideSessionToken);
      if (result.success) {
        setEmbeddingFiles(result.embeddings);
        // Auto-select first embedding if available
        if (result.embeddings.length > 0) {
          setSelectedContentId(result.embeddings[0].content_id);
        }
      } else {
        toast.error(result.error || "Failed to load embeddings");
      }
    } catch (error) {
      toast.error(`Error loading embeddings: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const loadPreview = async (contentId: string) => {
    setPreviewLoading(true);
    try {
      const result = await previewEmbeddings(contentId, guideSessionToken);
      if (result.success) {
        setPreview(result);
      } else {
        toast.error(result.error || "Failed to load preview");
      }
    } catch (error) {
      toast.error(`Error loading preview: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setPreviewLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Data Mash - Semantic Layer
          </CardTitle>
          <CardDescription>
            AI-powered virtual data composition layer that dynamically stitches together data from different sources.
            This showcases the 3-layer semantic embeddings pattern: Infrastructure → Business Enablement → Semantic Layer.
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Embeddings List */}
      {selectedFile && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Semantic Layer Files
            </CardTitle>
            <CardDescription>
              Embeddings and metadata extracted from parsed files
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Loader />
            ) : embeddingFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No semantic layer data found for this file.</p>
                <p className="text-sm mt-2">Parse the file first to create embeddings.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {embeddingFiles.map((file) => (
                  <div
                    key={file.content_id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedContentId === file.content_id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedContentId(file.content_id)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">Content ID: {file.content_id.slice(0, 8)}...</div>
                        <div className="text-sm text-gray-500">
                          {file.embeddings_count} embeddings • {file.columns.length} columns
                        </div>
                      </div>
                      <Badge variant="outline">
                        {new Date(file.created_at).toLocaleDateString()}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Preview */}
      {selectedContentId && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5" />
              Semantic Layer Preview
            </CardTitle>
            <CardDescription>
              Preview reconstructed from embeddings + metadata (not raw parsed data)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {previewLoading ? (
              <Loader />
            ) : preview ? (
              <div className="space-y-6">
                {/* Structure Summary */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Columns</div>
                    <div className="text-2xl font-bold">{preview.structure.column_count}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Rows</div>
                    <div className="text-2xl font-bold">{preview.structure.row_count.toLocaleString()}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Tables</div>
                    <div className="text-2xl font-bold">{preview.structure.table_count}</div>
                  </div>
                </div>

                {/* Columns */}
                <div className="space-y-4">
                  <h3 className="font-semibold">Columns & Semantic Meanings</h3>
                  {preview.columns.map((column, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <div className="font-medium">{column.column_name}</div>
                          <div className="text-sm text-gray-500">{column.data_type}</div>
                        </div>
                        {column.semantic_id && (
                          <Badge variant="outline">{column.semantic_id}</Badge>
                        )}
                      </div>
                      {column.semantic_meaning && (
                        <div className="mt-2 text-sm text-gray-700">
                          <strong>Semantic Meaning:</strong> {column.semantic_meaning}
                        </div>
                      )}
                      {column.sample_values && column.sample_values.length > 0 && (
                        <div className="mt-2">
                          <div className="text-sm text-gray-500 mb-1">Sample Values:</div>
                          <div className="flex flex-wrap gap-2">
                            {column.sample_values.slice(0, 5).map((value, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">
                                {value}
                              </Badge>
                            ))}
                            {column.sample_values.length > 5 && (
                              <Badge variant="secondary" className="text-xs">
                                +{column.sample_values.length - 5} more
                              </Badge>
                            )}
                          </div>
                        </div>
                      )}
                      {column.semantic_model_recommendation && (
                        <div className="mt-2 text-sm">
                          <strong>Confidence:</strong>{' '}
                          <span className={column.semantic_model_recommendation.confidence >= 0.7 ? 'text-green-600' : 'text-yellow-600'}>
                            {(column.semantic_model_recommendation.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Semantic Model Recommendations */}
                {preview.semantic_model.recommendations.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-semibold">Semantic Model Recommendations</h3>
                    <div className="space-y-2">
                      {preview.semantic_model.recommendations.map((rec, index) => (
                        <div key={index} className="p-3 bg-blue-50 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium">{rec.column_name}</div>
                              <div className="text-sm text-gray-600">{rec.meaning}</div>
                            </div>
                            {rec.semantic_id && (
                              <Badge>{rec.semantic_id}</Badge>
                            )}
                            {rec.confidence !== undefined && (
                              <Badge variant={rec.confidence >= 0.7 ? 'default' : 'secondary'}>
                                {((rec.confidence || 0) * 100).toFixed(0)}%
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No preview available</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-sm">About Data Mash</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-700">
          <p className="mb-2">
            <strong>Data Mash</strong> is an AI-assisted, virtual data composition layer that dynamically stitches together data from different sources without physically moving it.
          </p>
          <p className="mb-2">
            The <strong>3-Layer Pattern</strong>:
          </p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li><strong>Layer 1 (Infrastructure):</strong> File parsing → stores parsed files</li>
            <li><strong>Layer 2 (Business Enablement):</strong> Embedding creation → extracts metadata FROM parsed files, creates embeddings</li>
            <li><strong>Layer 3 (Semantic Layer):</strong> Embeddings storage → stores embeddings + metadata in ArangoDB</li>
          </ul>
          <p className="mt-2">
            This preview is reconstructed from embeddings + metadata (not raw parsed data), demonstrating the power of the semantic layer.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Time Estimate:** 4-5 hours

**Testing:**
- Test component with real data
- Test loading states
- Test error handling
- Test with multiple files
- Test responsive design

---

### **Phase 5: Frontend - Integration into Content Page (MEDIUM PRIORITY)**

**Goal:** Add Data Mash component to Content Pillar page

**Files to Modify:**
- `ontikMVP/frontend/app/pillars/content/page.tsx` (or equivalent)

**Changes:**

1. **Import Data Mash component:**

```typescript
import DataMash from '@/components/content/DataMash';
```

2. **Add Data Mash section after Parse Preview:**

```typescript
{/* Parse Preview - Full Width */}
<Card>
  <CardHeader>
    <CardTitle>Parse Preview</CardTitle>
    <CardDescription>
      Preview parsed data with quality analysis and issue identification.
    </CardDescription>
  </CardHeader>
  <CardContent>
    <ParsePreviewDisplay 
      selectedFile={selectedFile} 
      onShareIssues={handleShareQualityIssues}
    />
  </CardContent>
</Card>

{/* Data Mash - Semantic Layer - Full Width */}
<Card>
  <CardHeader>
    <CardTitle>Data Mash - Semantic Layer</CardTitle>
    <CardDescription>
      AI-powered virtual data composition layer showcasing the 3-layer semantic embeddings pattern.
    </CardDescription>
  </CardHeader>
  <CardContent>
    <DataMash selectedFile={selectedFile} />
  </CardContent>
</Card>
```

**Time Estimate:** 1 hour

**Testing:**
- Verify component appears on page
- Test with file selection
- Test responsive layout

---

## 📋 Implementation Checklist

### **Phase 1: Backend - Orchestrator Integration**
- [x] Add `create_embeddings()` method
- [x] Add routing for `POST /create-embeddings` endpoint
- [x] Integrate with Data Solution Orchestrator pattern (no circular dependencies)
- [ ] Test with parsed file selection
- [ ] Verify `content_id` is returned in response
- [ ] Verify embeddings stored in ArangoDB

### **Phase 2: Backend - List/Preview Pattern**
- [ ] Add `list_embeddings()` method
- [ ] Add `preview_embeddings()` method
- [ ] Add `_get_semantic_data_abstraction()` helper
- [ ] Add `_get_content_metadata_abstraction()` helper
- [ ] Add routing in `execute()` method
- [ ] Test `list_embeddings()` with file_id
- [ ] Test `list_embeddings()` without file_id (all files)
- [ ] Test `preview_embeddings()` with content_id
- [ ] Verify preview reconstructs from embeddings + metadata

### **Phase 3: Frontend - API Integration**
- [ ] Add `listEmbeddings()` API method
- [ ] Add `previewEmbeddings()` API method
- [ ] Test API methods with real backend
- [ ] Verify error handling
- [ ] Test with authentication

### **Phase 4: Frontend - Data Mash Component**
- [ ] Create `DataMash.tsx` component
- [ ] Implement embeddings list display
- [ ] Implement preview display
- [ ] Add loading states
- [ ] Add error handling
- [ ] Add info card explaining Data Mash
- [ ] Test with real data
- [ ] Test responsive design

### **Phase 5: Frontend - Integration**
- [ ] Import Data Mash component
- [ ] Add to Content Pillar page
- [ ] Test with file selection
- [ ] Test responsive layout
- [ ] Verify component appears correctly

---

## 🎯 Success Criteria

### **Backend:**
- ✅ Embeddings created automatically after parsing structured files
- ✅ `list_embeddings()` returns all embeddings for a file/user
- ✅ `preview_embeddings()` reconstructs preview from embeddings + metadata
- ✅ All endpoints return proper error messages

### **Frontend:**
- ✅ Data Mash component displays semantic layer information
- ✅ Component shows embeddings list
- ✅ Component shows preview with columns, semantic meanings, sample values
- ✅ Component explains the 3-layer pattern
- ✅ Component integrated into Content Pillar page

### **Integration:**
- ✅ Frontend calls backend endpoints correctly
- ✅ Data flows from parsing → embeddings → display
- ✅ Error handling works end-to-end

---

## 📊 Time Estimates

| Phase | Task | Time Estimate |
|-------|------|---------------|
| Phase 1 | Backend - Orchestrator Integration | 2-3 hours |
| Phase 2 | Backend - List/Preview Pattern | 3-4 hours |
| Phase 3 | Frontend - API Integration | 1-2 hours |
| Phase 4 | Frontend - Data Mash Component | 4-5 hours |
| Phase 5 | Frontend - Integration | 1 hour |
| **Total** | **Complete Implementation** | **11-15 hours** |

---

## 🚀 Next Steps

1. **Start with Phase 1** (Backend Orchestrator Integration)
2. **Then Phase 2** (Backend List/Preview Pattern)
3. **Then Phase 3** (Frontend API Integration)
4. **Then Phase 4** (Frontend Data Mash Component)
5. **Finally Phase 5** (Frontend Integration)

**Priority Order:**
1. Phase 1 (HIGH) - Enable automatic embedding creation
2. Phase 2 (HIGH) - Enable list/preview pattern
3. Phase 4 (HIGH) - Create Data Mash component
4. Phase 3 (MEDIUM) - API integration
5. Phase 5 (MEDIUM) - Page integration

---

## 📝 Notes

- **Naming:** "Data Mash" aligns with the platform's Data Solution Orchestrator vision
- **Pattern:** Follows the same pattern as parsing (create → list → preview)
- **Semantic Layer:** Preview is reconstructed from embeddings + metadata (not raw parsed data)
- **3-Layer Pattern:** Component explains the pattern to users
- **Future:** Can extend to show cross-file correlations, semantic graph visualization, etc.

---

**Status:** Ready for implementation

