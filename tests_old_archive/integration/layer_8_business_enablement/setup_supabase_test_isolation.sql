-- Supabase Test Isolation Setup
-- This script sets up test isolation for Supabase project_files table
-- Run this in your Supabase SQL editor

-- Option 1: Use existing table with tenant_id filter (Recommended)
-- No schema changes needed - just use tenant_id = 'test_tenant' for all test records

-- Option 2: Create cleanup function for test data
CREATE OR REPLACE FUNCTION cleanup_test_files()
RETURNS void AS $$
BEGIN
    -- Delete test files older than 7 days
    DELETE FROM project_files
    WHERE tenant_id = 'test_tenant'
      AND created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Option 3: Create scheduled cleanup (if Supabase supports cron)
-- This would run daily to clean up old test files
-- Note: Supabase doesn't support cron directly, but you can:
--   - Use pg_cron extension (if enabled)
--   - Use external cron job calling the function
--   - Use Supabase Edge Functions with scheduled triggers

-- Create index for faster test data queries
CREATE INDEX IF NOT EXISTS idx_project_files_test_tenant 
ON project_files(tenant_id, created_at) 
WHERE tenant_id = 'test_tenant';

-- Grant necessary permissions (if using RLS)
-- ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Test tenant can access test files"
--   ON project_files FOR ALL
--   USING (tenant_id = 'test_tenant');

-- Verify setup
SELECT 
    COUNT(*) as total_files,
    COUNT(*) FILTER (WHERE tenant_id = 'test_tenant') as test_files
FROM project_files;

