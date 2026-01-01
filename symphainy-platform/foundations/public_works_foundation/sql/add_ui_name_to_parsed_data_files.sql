-- =============================================================================
-- MIGRATION: Add ui_name to parsed_data_files table
-- =============================================================================
-- This migration standardizes the parsed_data_files table to include ui_name,
-- matching the pattern used in project_files and embedding_files tables.
-- This enables unified query patterns across all three file metadata tables.
-- =============================================================================

-- Add ui_name column to parsed_data_files
ALTER TABLE parsed_data_files 
ADD COLUMN IF NOT EXISTS ui_name TEXT;

-- Create index for ui_name lookups
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_ui_name ON parsed_data_files(ui_name);

-- Update existing records: Extract ui_name from metadata or construct from original file
-- This backfills existing parsed files with their ui_name
UPDATE parsed_data_files p
SET ui_name = COALESCE(
    -- Try to get from metadata first
    (p.metadata->>'ui_name')::TEXT,
    -- Fallback: construct from parsed_file_id if available
    CASE 
        WHEN p.parsed_file_id IS NOT NULL THEN 
            'parsed_' || p.parsed_file_id::TEXT
        ELSE 
            'parsed_file_' || p.uuid::TEXT
    END
)
WHERE ui_name IS NULL;

-- Add comment for documentation
COMMENT ON COLUMN parsed_data_files.ui_name IS 'UI-friendly display name for the parsed file (e.g., "parsed_Balances")';

