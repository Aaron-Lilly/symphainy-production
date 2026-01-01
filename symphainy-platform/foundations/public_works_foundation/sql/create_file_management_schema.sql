-- =============================================================================
-- SUPABASE FILE MANAGEMENT SCHEMA
-- =============================================================================
-- This schema implements the FMS (File Management System) with deep lineage support
-- for the SymphAIny platform's "secure by design, open by policy" architecture.
-- =============================================================================

-- =============================================================================
-- PROJECT FILES TABLE
-- =============================================================================
-- Main table for file metadata and management
CREATE TABLE IF NOT EXISTS project_files (
  -- Core Identifiers
  uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,                    -- From UserContext (str, not UUID)
  tenant_id TEXT,                           -- From UserContext (str, not UUID)
  
  -- File Information
  ui_name TEXT NOT NULL,                    -- Display name for UI
  file_type TEXT NOT NULL,                  -- File extension/type
  mime_type TEXT,                           -- MIME type
  original_path TEXT NOT NULL,              -- Original file path
  parsed_path TEXT,                         -- Processed file path
  
  -- File Integrity & Security (secure by design, open by policy)
  file_size BIGINT,                         -- File size in bytes
  file_hash TEXT,                           -- SHA-256 hash
  file_checksum TEXT,                       -- Alternative checksum
  
  -- Status & Processing
  status TEXT NOT NULL DEFAULT 'uploaded',  -- uploaded, processing, completed, failed
  content_type TEXT CHECK (content_type IN ('structured', 'unstructured', 'hybrid')),
  processing_status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
  processing_errors JSONB,                  -- Error details if processing failed
  
  -- Security & Access (nullable for open by policy)
  created_by TEXT,                          -- user_id who uploaded
  updated_by TEXT,                          -- user_id who last modified
  access_level TEXT DEFAULT 'open',         -- open, private, restricted (default open)
  permissions JSONB,                        -- Fine-grained permissions (NULL = open)
  
  -- Audit Trail
  upload_source TEXT DEFAULT 'web_interface', -- web_interface, api, batch_upload
  client_ip INET,                           -- IP address of uploader
  user_agent TEXT,                          -- Browser/client info
  
  -- Compliance (nullable for open by policy)
  data_classification TEXT DEFAULT 'public', -- public, internal, confidential, restricted
  retention_policy TEXT,                    -- How long to keep file
  compliance_flags JSONB,                   -- GDPR, HIPAA, SOX flags (NULL = no restrictions)
  
  -- Platform Integration
  pillar_origin TEXT DEFAULT 'content_pillar', -- content_pillar, insights_pillar, etc.
  service_context JSONB,                    -- Service-specific metadata
  processing_pipeline JSONB,                -- Processing stages completed
  arango_content_id UUID,                   -- Reference to Arango content metadata
  
  -- Deep Lineage Support
  lineage_depth INTEGER DEFAULT 0,          -- How many generations deep
  root_file_uuid UUID,                      -- Original file (Generation 0)
  parent_file_uuid UUID,                    -- Direct parent
  generation INTEGER DEFAULT 0,             -- Generation number
  lineage_path TEXT,                        -- Full path: "root->parent->child"
  
  -- Version Control
  version INTEGER DEFAULT 1,                -- File version
  
  -- Metadata & Insights
  insights JSONB,                           -- Basic insights (keep for compatibility)
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  deleted BOOLEAN DEFAULT FALSE
);

-- =============================================================================
-- FILE LINKS TABLE
-- =============================================================================
-- Table for file relationships and lineage tracking
CREATE TABLE IF NOT EXISTS file_links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  parent_uuid UUID REFERENCES project_files(uuid) ON DELETE CASCADE,
  child_uuid UUID REFERENCES project_files(uuid) ON DELETE CASCADE,
  link_type TEXT CHECK (link_type IN (
    'parsed_from',           -- Original → Parsed
    'metadata_from',         -- Parsed → Content Metadata
    'insights_from',         -- Content Metadata → Insights
    'deliverable_from',      -- Insights → POC/Roadmap
    'variant_of',            -- Different format of same content
    'alternate_format',      -- Converted format
    'derived_from'           -- Any other derivation
  )),
  generation_gap INTEGER DEFAULT 1,         -- How many generations apart
  relationship_strength TEXT DEFAULT 'direct', -- 'direct', 'indirect', 'distant'
  created_at TIMESTAMPTZ DEFAULT now()
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Project Files Indexes
CREATE INDEX IF NOT EXISTS idx_project_files_user_id ON project_files(user_id);
CREATE INDEX IF NOT EXISTS idx_project_files_tenant_id ON project_files(tenant_id);
CREATE INDEX IF NOT EXISTS idx_project_files_content_type ON project_files(content_type);
CREATE INDEX IF NOT EXISTS idx_project_files_status ON project_files(status);
CREATE INDEX IF NOT EXISTS idx_project_files_processing_status ON project_files(processing_status);
CREATE INDEX IF NOT EXISTS idx_project_files_pillar_origin ON project_files(pillar_origin);
CREATE INDEX IF NOT EXISTS idx_project_files_created_at ON project_files(created_at);
CREATE INDEX IF NOT EXISTS idx_project_files_deleted ON project_files(deleted);
CREATE INDEX IF NOT EXISTS idx_project_files_parent_file_uuid ON project_files(parent_file_uuid);
CREATE INDEX IF NOT EXISTS idx_project_files_root_file_uuid ON project_files(root_file_uuid);
CREATE INDEX IF NOT EXISTS idx_project_files_lineage_depth ON project_files(lineage_depth);

-- File Links Indexes
CREATE INDEX IF NOT EXISTS idx_file_links_parent_uuid ON file_links(parent_uuid);
CREATE INDEX IF NOT EXISTS idx_file_links_child_uuid ON file_links(child_uuid);
CREATE INDEX IF NOT EXISTS idx_file_links_link_type ON file_links(link_type);
CREATE INDEX IF NOT EXISTS idx_file_links_created_at ON file_links(created_at);

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================
-- Enable RLS for multi-tenant security
ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_links ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own files
CREATE POLICY "Users can only see their own files" ON project_files
  FOR ALL USING (user_id = current_setting('app.current_user_id', true));

-- Policy: Users can only see file links for their own files
CREATE POLICY "Users can only see their own file links" ON file_links
  FOR ALL USING (
    parent_uuid IN (
      SELECT uuid FROM project_files 
      WHERE user_id = current_setting('app.current_user_id', true)
    )
  );

-- =============================================================================
-- FUNCTIONS FOR DEEP LINEAGE QUERIES
-- =============================================================================

-- Function to get complete lineage tree
CREATE OR REPLACE FUNCTION get_file_lineage_tree(root_uuid UUID)
RETURNS TABLE (
  uuid UUID,
  ui_name TEXT,
  file_type TEXT,
  content_type TEXT,
  generation INTEGER,
  lineage_depth INTEGER,
  lineage_path TEXT,
  level INTEGER
) AS $$
BEGIN
  RETURN QUERY
  WITH RECURSIVE file_lineage AS (
    -- Base case: start with root file
    SELECT 
      p.uuid, 
      p.ui_name, 
      p.file_type, 
      p.content_type,
      p.generation, 
      p.lineage_depth, 
      p.lineage_path,
      0 as level
    FROM project_files p 
    WHERE p.uuid = root_uuid AND p.deleted = false
    
    UNION ALL
    
    -- Recursive case: get children
    SELECT 
      p.uuid, 
      p.ui_name, 
      p.file_type, 
      p.content_type,
      p.generation, 
      p.lineage_depth, 
      p.lineage_path,
      fl.level + 1
    FROM project_files p
    JOIN file_links l ON p.uuid = l.child_uuid
    JOIN file_lineage fl ON l.parent_uuid = fl.uuid
    WHERE p.deleted = false
  )
  SELECT * FROM file_lineage ORDER BY level, generation;
END;
$$ LANGUAGE plpgsql;

-- Function to get all descendants of a file
CREATE OR REPLACE FUNCTION get_file_descendants(root_uuid UUID)
RETURNS TABLE (
  uuid UUID,
  ui_name TEXT,
  file_type TEXT,
  content_type TEXT,
  generation INTEGER,
  lineage_depth INTEGER
) AS $$
BEGIN
  RETURN QUERY
  WITH RECURSIVE descendants AS (
    -- Base case: start with root file
    SELECT p.uuid, p.ui_name, p.file_type, p.content_type, p.generation, p.lineage_depth
    FROM project_files p 
    WHERE p.uuid = root_uuid AND p.deleted = false
    
    UNION ALL
    
    -- Recursive case: get all descendants
    SELECT p.uuid, p.ui_name, p.file_type, p.content_type, p.generation, p.lineage_depth
    FROM project_files p
    JOIN file_links l ON p.uuid = l.child_uuid
    JOIN descendants d ON l.parent_uuid = d.uuid
    WHERE p.deleted = false
  )
  SELECT * FROM descendants ORDER BY generation, lineage_depth;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE project_files IS 'Main table for file metadata and management with deep lineage support';
COMMENT ON TABLE file_links IS 'File relationships and lineage tracking for complex file hierarchies';

COMMENT ON COLUMN project_files.content_type IS 'Content classification: structured, unstructured, or hybrid';
COMMENT ON COLUMN project_files.lineage_depth IS 'How many generations deep from root file';
COMMENT ON COLUMN project_files.root_file_uuid IS 'Original file that started the lineage chain';
COMMENT ON COLUMN project_files.parent_file_uuid IS 'Direct parent file in lineage chain';
COMMENT ON COLUMN project_files.generation IS 'Generation number in lineage chain';
COMMENT ON COLUMN project_files.lineage_path IS 'Human-readable path showing lineage chain';
COMMENT ON COLUMN project_files.arango_content_id IS 'Reference to detailed content metadata in ArangoDB';

COMMENT ON COLUMN file_links.link_type IS 'Type of relationship between files';
COMMENT ON COLUMN file_links.generation_gap IS 'How many generations apart the files are';
COMMENT ON COLUMN file_links.relationship_strength IS 'Strength of relationship: direct, indirect, distant';




