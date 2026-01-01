-- Migration: Add tenant_id to Existing Tables
-- Date: 2025-12-01
-- Purpose: Add tenant isolation to existing tables
-- Phase: 1 - MVP Security Fixes

-- ============================================================================
-- FILES TABLE (if exists)
-- ============================================================================
-- Add tenant_id column to files table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'files') THEN
        -- Add tenant_id column if it doesn't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'files' 
            AND column_name = 'tenant_id'
        ) THEN
            ALTER TABLE public.files 
            ADD COLUMN tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE;
            
            CREATE INDEX IF NOT EXISTS idx_files_tenant_id ON public.files(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_files_tenant_user ON public.files(tenant_id, user_id);
            
            COMMENT ON COLUMN public.files.tenant_id IS 'Tenant isolation: files belong to a specific tenant';
        END IF;
    END IF;
END $$;

-- ============================================================================
-- AUDIT LOGS TABLE (if exists)
-- ============================================================================
-- Add tenant_id column to audit_logs table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_logs') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'audit_logs' 
            AND column_name = 'tenant_id'
        ) THEN
            ALTER TABLE public.audit_logs 
            ADD COLUMN tenant_id UUID REFERENCES public.tenants(id) ON DELETE SET NULL;
            
            CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON public.audit_logs(tenant_id);
            
            COMMENT ON COLUMN public.audit_logs.tenant_id IS 'Tenant isolation: audit logs are scoped to tenant';
        END IF;
    END IF;
END $$;

-- ============================================================================
-- SESSIONS TABLE (if exists)
-- ============================================================================
-- Add tenant_id column to sessions table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sessions') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'sessions' 
            AND column_name = 'tenant_id'
        ) THEN
            ALTER TABLE public.sessions 
            ADD COLUMN tenant_id UUID REFERENCES public.tenants(id) ON DELETE SET NULL;
            
            CREATE INDEX IF NOT EXISTS idx_sessions_tenant_id ON public.sessions(tenant_id);
            
            COMMENT ON COLUMN public.sessions.tenant_id IS 'Tenant isolation: sessions are scoped to tenant';
        END IF;
    END IF;
END $$;

-- ============================================================================
-- NOTE: Backfill existing data
-- ============================================================================
-- After running this migration, you'll need to backfill tenant_id for existing records
-- This should be done via a separate migration script or admin tool
-- See: 003_backfill_tenant_data.sql




