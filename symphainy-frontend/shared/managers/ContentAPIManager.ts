/**
 * Content API Manager
 * 
 * Centralizes all Content pillar API calls and operations.
 * Provides a clean interface for all content-related functionality.
 */

// ============================================
// Content API Manager Types
// ============================================

export interface ContentFile {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadDate: string;
  status?: string; // File status: "uploaded", "parsed", etc.
  metadata?: any;
}

export interface UploadResponse {
  success: boolean;
  file?: ContentFile;
  error?: string;
}

export interface ProcessResponse {
  success: boolean;
  result?: any;
  error?: string;
}

// ============================================
// Content API Manager Class
// ============================================

export class ContentAPIManager {
  private baseURL: string;
  private sessionToken: string;

  constructor(sessionToken: string, baseURL?: string) {
    this.sessionToken = sessionToken;
    // Use configured API URL (Traefik route on port 80, not :8000)
    // Use centralized API config (NO hardcoded values)
    if (baseURL) {
      this.baseURL = baseURL.replace(':8000', '').replace(/\/$/, ''); // Remove port 8000 and trailing slash
    } else {
      // Import here to avoid circular dependency issues
      const { getApiUrl } = require('@/shared/config/api-config');
      this.baseURL = getApiUrl();
    }
  }

  /**
   * Authenticated fetch helper that automatically handles token refresh on 401 errors.
   * Updates sessionToken if refresh succeeds.
   */
  private async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    // Import authenticatedFetch dynamically to avoid circular dependencies
    const { authenticatedFetch } = await import('../../lib/utils/tokenRefresh');
    
    const response = await authenticatedFetch(url, {
      ...options,
      token: this.sessionToken,
    });
    
    // If token was refreshed, update our sessionToken
    // (authenticatedFetch handles the refresh internally, but we should update our token)
    // Note: In a real implementation, we might want to emit an event or use a callback
    // For now, the token refresh utility handles it via localStorage
    
    return response;
  }

  // ============================================
  // File Management
  // ============================================

  async listFiles(): Promise<ContentFile[]> {
    try {
      // Use semantic API path: /api/v1/content-pillar/list-uploaded-files
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/content-pillar/list-uploaded-files`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to list files: ${response.statusText}`);
      }

      const data = await response.json();
      const backendFiles = data.files || [];
      
      // Map backend response to ContentFile format
      // Backend returns: uuid, ui_name, file_type, size_bytes, uploaded_at, status, etc.
      // Frontend expects: id, name, type, size, uploadDate, status, metadata
      return backendFiles.map((file: any) => ({
        id: file.uuid || file.file_id || '',
        name: file.ui_name || file.original_filename || file.filename || 'Unnamed File',
        type: file.file_type || file.mime_type || '',
        size: file.size_bytes || file.file_size || 0,
        uploadDate: file.uploaded_at || file.created_at || new Date().toISOString(),
        status: file.status || 'uploaded', // Use status from backend, default to 'uploaded'
        metadata: {
          ...file,
          mime_type: file.mime_type,
          content_type: file.content_type,
          parsed: file.parsed || false
        }
      }));
    } catch (error) {
      console.error('Error listing files:', error);
      throw error;
    }
  }

  async uploadFile(
    file: File, 
    copybookFile?: File,
    contentType?: string,
    fileTypeCategory?: string
  ): Promise<UploadResponse> {
    try {
      // DEBUG: Verify file objects
      console.log('[ContentAPIManager] uploadFile called');
      console.log('[ContentAPIManager] file:', file);
      console.log('[ContentAPIManager] file.name:', file?.name);
      console.log('[ContentAPIManager] file.size:', file?.size);
      console.log('[ContentAPIManager] file.type:', file?.type);
      console.log('[ContentAPIManager] copybookFile:', copybookFile);
      console.log('[ContentAPIManager] copybookFile?.name:', copybookFile?.name);
      console.log('[ContentAPIManager] copybookFile?.size:', copybookFile?.size);
      
      if (!file || !(file instanceof File)) {
        console.error('[ContentAPIManager] ERROR: file is not a valid File object:', file);
        throw new Error('Invalid file: file must be a File object');
      }
      
      const formData = new FormData();
      formData.append('file', file);
      
      // Add optional copybook file for binary files
      if (copybookFile) {
        if (!(copybookFile instanceof File)) {
          console.error('[ContentAPIManager] ERROR: copybookFile is not a valid File object:', copybookFile);
          throw new Error('Invalid copybook file: copybookFile must be a File object');
        }
        formData.append('copybook', copybookFile);
      }
      
      // Add content_type and file_type_category if provided (for workflow/SOP files)
      if (contentType) {
        formData.append('content_type', contentType);
      }
      if (fileTypeCategory) {
        formData.append('file_type_category', fileTypeCategory);
      }
      
      // DEBUG: Verify FormData
      console.log('[ContentAPIManager] FormData entries:', Array.from(formData.entries()).map(([key, value]) => {
        if (value instanceof File) {
          return [key, { name: value.name, size: value.size, type: value.type }];
        }
        return [key, value];
      }));

      // Use centralized API config (NO hardcoded values)
      const { getApiEndpointUrl } = require('@/shared/config/api-config');
      const uploadURL = getApiEndpointUrl('/api/v1/content-pillar/upload-file');
      
      console.log('[ContentAPIManager] ⚠️ FILE UPLOAD: Using Traefik route (production setup)');
      console.log('[ContentAPIManager] Uploading to:', uploadURL);
      console.log('[ContentAPIManager] File size:', file.size, 'bytes');
      console.log('[ContentAPIManager] Copybook size:', copybookFile?.size || 0, 'bytes');
      console.log('[ContentAPIManager] File object:', file);
      console.log('[ContentAPIManager] File instanceof File:', file instanceof File);

      // Use direct backend URL (bypass Next.js rewrite for file uploads)
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      // Note: authenticatedFetch handles FormData correctly (doesn't set Content-Type)
      const response = await this.authenticatedFetch(uploadURL, {
        method: 'POST',
        headers: {
          'X-Session-Token': this.sessionToken
          // Don't set Content-Type - browser will set it with boundary for FormData
        },
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Upload failed'
        };
      }

      const data = await response.json();
      
      // Map semantic response to ContentFile format
      const contentFile: ContentFile = {
        id: data.file_id || data.uuid || '',
        name: data.ui_name || data.original_filename || data.file_name || '',
        type: data.file_type || data.file_extension || '',
        size: data.file_size || 0,
        uploadDate: data.uploaded_at || new Date().toISOString(),
        metadata: {
          original_filename: data.original_filename,
          file_extension: data.file_extension,
          mime_type: data.mime_type,
          content_type: data.content_type,
          file_type_category: data.file_type_category,
          copybook_file_id: data.copybook_file_id
        }
      };
      
      return {
        success: data.success,
        file: contentFile,
        error: data.error
      };
    } catch (error) {
      console.error('Error uploading file:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed'
      };
    }
  }

  async getFileMetadata(fileId: string): Promise<any> {
    try {
      // Use semantic API path: /api/v1/content-pillar/get-file-details/{fileId}
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/content-pillar/get-file-details/${fileId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to get file metadata: ${response.statusText}`);
      }

      const data = await response.json();
      return data.file || data;
    } catch (error) {
      console.error('Error getting file metadata:', error);
      throw error;
    }
  }

  async deleteFile(fileId: string): Promise<boolean> {
    try {
      // Use semantic API path: /api/v1/content-pillar/delete-file/{fileId}
      // FrontendGatewayService will route this to ContentJourneyOrchestrator.delete_file()
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const url = `${this.baseURL}/api/v1/content-pillar/delete-file/${fileId}`;
      
      const response = await this.authenticatedFetch(url, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: response.statusText }));
        console.error('[ContentAPIManager] Delete file failed:', {
          status: response.status,
          statusText: response.statusText,
          error: errorData
        });
        return false;
      }

      const data = await response.json().catch(() => ({ success: true }));
      // Check for success in response
      return data.success === true || (data.success !== false && response.ok);
    } catch (error) {
      console.error('[ContentAPIManager] Error deleting file:', error);
      return false;
    }
  }

  // ============================================
  // Content Processing
  // ============================================

  async processFile(fileId: string, copybookFileId?: string, processingOptions?: any): Promise<ProcessResponse> {
    try {
      const requestBody: any = {};
      if (copybookFileId) {
        requestBody.copybook_file_id = copybookFileId;
      }
      if (processingOptions) {
        requestBody.processing_options = processingOptions;
      }

      // Use semantic API path: /api/v1/content-pillar/process-file/{fileId}
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/v1/content-pillar/process-file/${fileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        },
        body: JSON.stringify(requestBody)  // Always send a body, even if empty
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || errorData.error || 'Processing failed'
        };
      }

      const data = await response.json();
      // Backend returns parse_result (not parsed_data) with preview data
      const parseResult = data.parse_result || {};
      return {
        success: data.success,
        result: {
          // Map backend parse_result to frontend expected structure
          parsed_data: parseResult.parsed_data || {
            format: parseResult.format || 'json_structured',
            chunks: parseResult.preview_records || [],
            structured_data: {
              tables: parseResult.preview_tables || [],
              records: parseResult.preview_records || []
            },
            preview_grid: parseResult.preview_tables?.[0]?.preview_data || [],
            text: parseResult.text_content || ''
          },
          metadata: parseResult.metadata || data.metadata,
          processing_status: data.processing_status,
          // Also include full parse_result for components that need it
          parse_result: parseResult,
          // Include parsed_file_id from backend response (for new parquet storage flow)
          parsed_file_id: data.parsed_file_id
        },
        error: data.error
      };
    } catch (error) {
      console.error('Error processing file:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Processing failed'
      };
    }
  }

  async extractMetadata(fileId: string): Promise<ProcessResponse> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/content/${fileId}/metadata`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || 'Metadata extraction failed'
        };
      }

      const data = await response.json();
      return {
        success: true,
        result: data.metadata
      };
    } catch (error) {
      console.error('Error extracting metadata:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Metadata extraction failed'
      };
    }
  }

  // ============================================
  // Content Analysis
  // ============================================

  async analyzeContent(fileId: string, analysisType: string): Promise<ProcessResponse> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/content/${fileId}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ analysisType })
      });

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.message || 'Analysis failed'
        };
      }

      const data = await response.json();
      return {
        success: true,
        result: data.analysis
      };
    } catch (error) {
      console.error('Error analyzing content:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Analysis failed'
      };
    }
  }

  // ============================================
  // Content Search
  // ============================================

  async searchContent(query: string, filters?: any): Promise<ContentFile[]> {
    try {
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/content/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query, filters })
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      console.error('Error searching content:', error);
      throw error;
    }
  }

  // ============================================
  // Content Health
  // ============================================

  async getHealthStatus(): Promise<any> {
    try {
      // Note: Semantic API may not have health endpoint yet
      // Using legacy endpoint for now, or implement if semantic endpoint exists
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const response = await this.authenticatedFetch(`${this.baseURL}/api/content/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking content health:', error);
      throw error;
    }
  }

  // ============================================
  // Parsed File Management
  // ============================================

  async listParsedFiles(fileId?: string): Promise<any[]> {
    try {
      // Use semantic API path: /api/v1/content-pillar/list-parsed-files
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const url = fileId 
        ? `${this.baseURL}/api/v1/content-pillar/list-parsed-files?file_id=${fileId}`
        : `${this.baseURL}/api/v1/content-pillar/list-parsed-files`;
      
      const response = await this.authenticatedFetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to list parsed files: ${response.statusText}`);
      }

      const data = await response.json();
      return data.parsed_files || [];
    } catch (error) {
      console.error('Error listing parsed files:', error);
      throw error;
    }
  }

  async previewParsedFile(parsedFileId: string, maxRows: number = 20, maxColumns: number = 20): Promise<any> {
    try {
      // Use semantic API path: /api/v1/content-pillar/preview-parsed-file/{parsedFileId}
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const url = `${this.baseURL}/api/v1/content-pillar/preview-parsed-file/${parsedFileId}?max_rows=${maxRows}&max_columns=${maxColumns}`;
      
      const response = await this.authenticatedFetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to preview parsed file: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error previewing parsed file:', error);
      throw error;
    }
  }

  // ============================================
  // Semantic Layer (Embeddings) Management
  // ============================================

  /**
   * List all embeddings for a file (or all for user)
   * 
   * Returns embeddings grouped by content_id with metadata.
   */
  async listEmbeddings(fileId?: string): Promise<{
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
      created_at?: string;
    }>;
    count: number;
    error?: string;
  }> {
    try {
      // Use semantic API path: /api/v1/content-pillar/list-embeddings
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const url = fileId
        ? `${this.baseURL}/api/v1/content-pillar/list-embeddings?file_id=${fileId}`
        : `${this.baseURL}/api/v1/content-pillar/list-embeddings`;
      
      const response = await this.authenticatedFetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: response.statusText }));
        throw new Error(errorData.error || `Failed to list embeddings: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: data.success !== false,
        embeddings: data.embeddings || [],
        count: data.count || 0,
        error: data.error
      };
    } catch (error) {
      console.error('Error listing embeddings:', error);
      throw error;
    }
  }

  /**
   * Preview semantic layer (embeddings + metadata) for a given content_id
   * 
   * Reconstructs a preview from the stored embeddings and their metadata.
   */
  async previewEmbeddings(contentId: string, maxColumns: number = 20): Promise<{
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
      semantic_insights_summary?: string[];
    };
    error?: string;
  }> {
    try {
      // Use semantic API path: /api/v1/content-pillar/preview-embeddings/{contentId}
      // ✅ Use authenticatedFetch for automatic token refresh on 401 errors
      const url = `${this.baseURL}/api/v1/content-pillar/preview-embeddings/${contentId}?max_columns=${maxColumns}`;
      
      const response = await this.authenticatedFetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Token': this.sessionToken
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: response.statusText }));
        throw new Error(errorData.error || `Failed to preview embeddings: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: data.success !== false,
        content_id: data.content_id || contentId,
        file_id: data.file_id,
        columns: data.columns || [],
        structure: data.structure || {
          column_count: data.columns?.length || 0,
          row_count: data.structure?.row_count || 0
        },
        error: data.error
      };
    } catch (error) {
      console.error('Error previewing embeddings:', error);
      throw error;
    }
  }
}





























