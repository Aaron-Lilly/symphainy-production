-- =============================================================================
-- SUPABASE PARSED DATA FILES SCHEMA
-- =============================================================================
-- This schema implements storage for parsed file metadata, linking parsed files
-- to their original files and supporting the Smart City data flow:
-- File Upload → Parse → Store Parsed Files → Extract Metadata → Store Embeddings
-- =============================================================================

-- =============================================================================
-- PARSED DATA FILES TABLE
-- =============================================================================
-- Table for storing metadata about parsed files (Parquet, JSON chunks, etc.)
-- Parsed files themselves are stored in GCS, metadata is stored here.
CREATE TABLE IF NOT EXISTS parsed_data_files (
  -- Core Identifiers
  uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  file_id UUID NOT NULL,                    -- Original file UUID (from project_files)
  parsed_file_id TEXT NOT NULL,             -- GCS path or identifier for parsed file
  
  -- Data Classification
  data_classification TEXT NOT NULL CHECK (data_classification IN ('platform', 'client')),
  tenant_id TEXT,                           -- Required if data_classification = 'client'
  
  -- Parsed Data Information
  format_type TEXT NOT NULL,                -- 'parquet', 'json_structured', 'json_chunks'
  content_type TEXT CHECK (content_type IN ('structured', 'unstructured', 'hybrid')),
  
  -- File Information
  file_size BIGINT,                         -- Parsed file size in bytes
  row_count INTEGER,                         -- Number of rows (for structured data)
  column_count INTEGER,                      -- Number of columns (for structured data)
  column_names JSONB,                       -- Array of column names
  data_types JSONB,                         -- Column data types
  
  -- Processing Information
  parsed_at TIMESTAMPTZ DEFAULT now(),
  parsed_by TEXT,                           -- Service/user that performed parsing
  parse_options JSONB,                      -- Options used for parsing
  
  -- Status & Processing
  status TEXT NOT NULL DEFAULT 'parsed',    -- parsed, processing, completed, failed
  processing_status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
  processing_errors JSONB,                  -- Error details if processing failed
  
  -- Metadata
  metadata JSONB,                           -- Additional metadata
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Core lookup indexes
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_file_id ON parsed_data_files(file_id);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_parsed_file_id ON parsed_data_files(parsed_file_id);

-- Data classification indexes
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_data_classification ON parsed_data_files(data_classification);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_tenant_id ON parsed_data_files(tenant_id);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_classification_tenant ON parsed_data_files(data_classification, tenant_id);

-- Status indexes
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_status ON parsed_data_files(status);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_processing_status ON parsed_data_files(processing_status);

-- Format and content type indexes
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_format_type ON parsed_data_files(format_type);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_content_type ON parsed_data_files(content_type);

-- Timestamp indexes
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_parsed_at ON parsed_data_files(parsed_at);
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_created_at ON parsed_data_files(created_at);

-- =============================================================================
-- FOREIGN KEY CONSTRAINTS
-- =============================================================================

-- Link to original file (optional - allows orphaned parsed files for now)
-- ALTER TABLE parsed_data_files ADD CONSTRAINT fk_parsed_data_files_file_id 
--   FOREIGN KEY (file_id) REFERENCES project_files(uuid) ON DELETE CASCADE;

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================
-- Enable RLS for multi-tenant security
ALTER TABLE parsed_data_files ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see parsed files for their own files
-- Note: This assumes parsed files inherit tenant_id from original file
CREATE POLICY "Users can only see parsed files for their own files" ON parsed_data_files
  FOR ALL USING (
    file_id IN (
      SELECT uuid FROM project_files 
      WHERE user_id = current_setting('app.current_user_id', true)
    )
  );

-- Policy: Platform data is accessible to all authenticated users
CREATE POLICY "Platform parsed data is accessible to authenticated users" ON parsed_data_files
  FOR ALL USING (
    data_classification = 'platform' AND
    current_setting('app.current_user_id', true) IS NOT NULL
  );

-- =============================================================================
-- FUNCTIONS FOR PARSED DATA QUERIES
-- =============================================================================

-- Function to get parsed files for a file
CREATE OR REPLACE FUNCTION get_parsed_files_for_file(file_uuid UUID)
RETURNS TABLE (
  uuid UUID,
  parsed_file_id TEXT,
  format_type TEXT,
  content_type TEXT,
  status TEXT,
  parsed_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.uuid,
    p.parsed_file_id,
    p.format_type,
    p.content_type,
    p.status,
    p.parsed_at
  FROM parsed_data_files p
  WHERE p.file_id = file_uuid
  ORDER BY p.parsed_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get latest parsed file for a file
CREATE OR REPLACE FUNCTION get_latest_parsed_file(file_uuid UUID)
RETURNS TABLE (
  uuid UUID,
  parsed_file_id TEXT,
  format_type TEXT,
  content_type TEXT,
  status TEXT,
  parsed_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.uuid,
    p.parsed_file_id,
    p.format_type,
    p.content_type,
    p.status,
    p.parsed_at
  FROM parsed_data_files p
  WHERE p.file_id = file_uuid
  ORDER BY p.parsed_at DESC
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE parsed_data_files IS 'Metadata for parsed files stored in GCS, linking to original files';
COMMENT ON COLUMN parsed_data_files.file_id IS 'Original file UUID from project_files table';
COMMENT ON COLUMN parsed_data_files.parsed_file_id IS 'GCS path or identifier for the parsed file';
COMMENT ON COLUMN parsed_data_files.data_classification IS 'Data classification: platform or client';
COMMENT ON COLUMN parsed_data_files.tenant_id IS 'Tenant ID (required for client data, NULL for platform data)';
COMMENT ON COLUMN parsed_data_files.format_type IS 'Format of parsed file: parquet, json_structured, json_chunks';
COMMENT ON COLUMN parsed_data_files.content_type IS 'Content classification: structured, unstructured, or hybrid';
COMMENT ON COLUMN parsed_data_files.status IS 'Status of parsed file: parsed, processing, completed, failed';
COMMENT ON COLUMN parsed_data_files.processing_status IS 'Processing pipeline status: pending, processing, completed, failed';



