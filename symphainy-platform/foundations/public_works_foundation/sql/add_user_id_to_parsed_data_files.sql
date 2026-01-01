-- =============================================================================
-- MIGRATION: Add user_id column to parsed_data_files table
-- =============================================================================
-- This migration adds user_id directly to parsed_data_files for simpler queries
-- No backwards compatibility needed - we're deleting old parsed files and re-parsing
-- =============================================================================

-- Add user_id column (references auth.users)
ALTER TABLE parsed_data_files 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Add index for fast user_id lookups
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_user_id ON parsed_data_files(user_id);

-- Add composite index for user_id + file_id lookups
CREATE INDEX IF NOT EXISTS idx_parsed_data_files_user_file ON parsed_data_files(user_id, file_id);

-- Update RLS policy to use user_id directly (simpler than JOIN)
DROP POLICY IF EXISTS "Users can only see parsed files for their own files" ON parsed_data_files;
CREATE POLICY "Users can only see parsed files for their own files" ON parsed_data_files
  FOR ALL USING (
    user_id = current_setting('app.current_user_id', true)::UUID
  );

-- Add comment
COMMENT ON COLUMN parsed_data_files.user_id IS 'User ID who owns the original file (for direct queries without JOIN)';

