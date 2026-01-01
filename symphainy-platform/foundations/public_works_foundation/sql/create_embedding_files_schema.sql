-- =============================================================================
-- SUPABASE EMBEDDING FILES SCHEMA
-- =============================================================================
-- This schema implements storage for embedding file metadata, linking embeddings
-- to their parsed files and original files. This enables UI-friendly display
-- of embeddings as first-class "files" in the platform.
-- =============================================================================

-- =============================================================================
-- EMBEDDING FILES TABLE
-- =============================================================================
-- Table for storing metadata about embedding files (semantic embeddings)
-- Embeddings themselves are stored in ArangoDB, metadata is stored here.
CREATE TABLE IF NOT EXISTS embedding_files (
  -- Core Identifiers
  uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_id TEXT NOT NULL,                      -- Original file UUID (from project_files)
  parsed_file_id TEXT NOT NULL,              -- Parsed file UUID (from parsed_data_files)
  
  -- Data Classification
  data_classification TEXT NOT NULL CHECK (data_classification IN ('platform', 'client')),
  tenant_id TEXT,                             -- Required if data_classification = 'client'
  user_id TEXT NOT NULL,                     -- User who created the embeddings
  
  -- UI-Friendly Display
  ui_name TEXT NOT NULL,                     -- UI-friendly name (e.g., "Embeddings: sales_data.csv")
  
  -- Embedding Information
  content_id TEXT,                            -- Content metadata ID (optional)
  embeddings_count INTEGER DEFAULT 0,        -- Number of embeddings in this "file"
  embedding_type TEXT,                        -- 'structured', 'unstructured', 'hybrid'
  
  -- Processing Information
  created_at TIMESTAMPTZ DEFAULT now(),
  created_by TEXT,                            -- Service/user that created embeddings
  updated_at TIMESTAMPTZ DEFAULT now(),
  
  -- Status & Processing
  status TEXT NOT NULL DEFAULT 'active',      -- active, deleted, archived
  processing_status TEXT DEFAULT 'completed', -- completed, processing, failed
  processing_errors JSONB,                   -- Error details if processing failed
  
  -- Metadata
  metadata JSONB                              -- Additional metadata (model used, etc.)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Core lookup indexes
CREATE INDEX IF NOT EXISTS idx_embedding_files_file_id ON embedding_files(file_id);
CREATE INDEX IF NOT EXISTS idx_embedding_files_parsed_file_id ON embedding_files(parsed_file_id);
CREATE INDEX IF NOT EXISTS idx_embedding_files_user_id ON embedding_files(user_id);
CREATE INDEX IF NOT EXISTS idx_embedding_files_content_id ON embedding_files(content_id);

-- Data classification indexes
CREATE INDEX IF NOT EXISTS idx_embedding_files_data_classification ON embedding_files(data_classification);
CREATE INDEX IF NOT EXISTS idx_embedding_files_tenant_id ON embedding_files(tenant_id);
CREATE INDEX IF NOT EXISTS idx_embedding_files_classification_tenant ON embedding_files(data_classification, tenant_id);

-- Status indexes
CREATE INDEX IF NOT EXISTS idx_embedding_files_status ON embedding_files(status);
CREATE INDEX IF NOT EXISTS idx_embedding_files_processing_status ON embedding_files(processing_status);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_embedding_files_user_status ON embedding_files(user_id, status);
CREATE INDEX IF NOT EXISTS idx_embedding_files_parsed_file_status ON embedding_files(parsed_file_id, status);

-- Timestamp indexes
CREATE INDEX IF NOT EXISTS idx_embedding_files_created_at ON embedding_files(created_at);
CREATE INDEX IF NOT EXISTS idx_embedding_files_updated_at ON embedding_files(updated_at);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================

-- Link to parsed file (optional - allows orphaned embedding files for now)
-- ALTER TABLE embedding_files ADD CONSTRAINT fk_embedding_files_parsed_file_id 
--   FOREIGN KEY (parsed_file_id) REFERENCES parsed_data_files(parsed_file_id) ON DELETE CASCADE;

-- Link to original file (optional - allows orphaned embedding files for now)
-- ALTER TABLE embedding_files ADD CONSTRAINT fk_embedding_files_file_id 
--   FOREIGN KEY (file_id) REFERENCES project_files(uuid) ON DELETE CASCADE;

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================
-- Enable RLS for multi-tenant security
ALTER TABLE embedding_files ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see embedding files for their own files
CREATE POLICY "Users can only see embedding files for their own files" ON embedding_files
  FOR ALL USING (
    user_id = current_setting('app.current_user_id', true)::TEXT
  );

-- Policy: Platform data is accessible to all authenticated users
CREATE POLICY "Platform embedding data is accessible to authenticated users" ON embedding_files
  FOR ALL USING (
    data_classification = 'platform' AND
    current_setting('app.current_user_id', true) IS NOT NULL
  );

-- =============================================================================
-- FUNCTIONS FOR EMBEDDING FILE QUERIES
-- =============================================================================

-- Function to get embedding files for a parsed file
CREATE OR REPLACE FUNCTION get_embedding_files_for_parsed_file(parsed_file_uuid TEXT)
RETURNS TABLE (
  uuid UUID,
  file_id TEXT,
  parsed_file_id TEXT,
  ui_name TEXT,
  embeddings_count INTEGER,
  status TEXT,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.uuid,
    e.file_id,
    e.parsed_file_id,
    e.ui_name,
    e.embeddings_count,
    e.status,
    e.created_at
  FROM embedding_files e
  WHERE e.parsed_file_id = parsed_file_uuid
    AND e.status = 'active'
  ORDER BY e.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get embedding files for an original file
CREATE OR REPLACE FUNCTION get_embedding_files_for_file(file_uuid TEXT)
RETURNS TABLE (
  uuid UUID,
  file_id TEXT,
  parsed_file_id TEXT,
  ui_name TEXT,
  embeddings_count INTEGER,
  status TEXT,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.uuid,
    e.file_id,
    e.parsed_file_id,
    e.ui_name,
    e.embeddings_count,
    e.status,
    e.created_at
  FROM embedding_files e
  WHERE e.file_id = file_uuid
    AND e.status = 'active'
  ORDER BY e.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE embedding_files IS 'Metadata for embedding files stored in ArangoDB, linking to parsed files and original files';
COMMENT ON COLUMN embedding_files.file_id IS 'Original file UUID from project_files table';
COMMENT ON COLUMN embedding_files.parsed_file_id IS 'Parsed file UUID from parsed_data_files table';
COMMENT ON COLUMN embedding_files.ui_name IS 'UI-friendly display name for the embedding file';
COMMENT ON COLUMN embedding_files.embeddings_count IS 'Number of embeddings (columns/chunks) in this embedding file';
COMMENT ON COLUMN embedding_files.data_classification IS 'Data classification: platform or client';
COMMENT ON COLUMN embedding_files.tenant_id IS 'Tenant ID (required for client data, NULL for platform data)';
COMMENT ON COLUMN embedding_files.status IS 'Status of embedding file: active, deleted, archived';
COMMENT ON COLUMN embedding_files.processing_status IS 'Processing pipeline status: completed, processing, failed';

