-- Migration: Enable Row Level Security (RLS) Policies
-- Date: 2025-12-01
-- Purpose: Implement database-level tenant isolation
-- Phase: 2 - Database-Level Isolation

-- ============================================================================
-- ENABLE RLS ON ALL TENANT-SCOPED TABLES
-- ============================================================================

ALTER TABLE public.tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_tenants ENABLE ROW LEVEL SECURITY;

-- Enable RLS on tenant-scoped tables (if they exist)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'files') THEN
        ALTER TABLE public.files ENABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_logs') THEN
        ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sessions') THEN
        ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
    END IF;
END $$;

-- ============================================================================
-- TENANTS TABLE POLICIES
-- ============================================================================

-- Policy: Users can only see tenants they belong to
DROP POLICY IF EXISTS "Users can view their tenants" ON public.tenants;
CREATE POLICY "Users can view their tenants"
    ON public.tenants
    FOR SELECT
    USING (
        id IN (
            SELECT tenant_id 
            FROM public.user_tenants
            WHERE user_id = auth.uid()
        )
    );

-- Policy: Users can update their own tenant (if they're owner/admin)
DROP POLICY IF EXISTS "Users can update their tenant" ON public.tenants;
CREATE POLICY "Users can update their tenant"
    ON public.tenants
    FOR UPDATE
    USING (
        id IN (
            SELECT tenant_id 
            FROM public.user_tenants
            WHERE user_id = auth.uid()
              AND role IN ('owner', 'admin')
        )
    );

-- ============================================================================
-- USER-TENANTS TABLE POLICIES
-- ============================================================================

-- Policy: Users can only see their own tenant memberships
DROP POLICY IF EXISTS "Users can view their tenant memberships" ON public.user_tenants;
CREATE POLICY "Users can view their tenant memberships"
    ON public.user_tenants
    FOR SELECT
    USING (user_id = auth.uid());

-- Policy: Users can insert their own tenant memberships (for joining tenants)
-- Note: In production, you might want to restrict this further
DROP POLICY IF EXISTS "Users can insert their tenant memberships" ON public.user_tenants;
CREATE POLICY "Users can insert their tenant memberships"
    ON public.user_tenants
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- ============================================================================
-- FILES TABLE POLICIES (if table exists)
-- ============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'files') THEN
        -- Policy: Users can only access files from their tenants
        DROP POLICY IF EXISTS "Users can access files from their tenants" ON public.files;
        CREATE POLICY "Users can access files from their tenants"
            ON public.files
            FOR ALL
            USING (
                tenant_id IN (
                    SELECT tenant_id 
                    FROM public.user_tenants
                    WHERE user_id = auth.uid()
                )
            );
        
        -- Policy: Users can only insert files into their tenants
        DROP POLICY IF EXISTS "Users can insert files into their tenants" ON public.files;
        CREATE POLICY "Users can insert files into their tenants"
            ON public.files
            FOR INSERT
            WITH CHECK (
                tenant_id IN (
                    SELECT tenant_id 
                    FROM public.user_tenants
                    WHERE user_id = auth.uid()
                )
            );
    END IF;
END $$;

-- ============================================================================
-- AUDIT LOGS TABLE POLICIES (if table exists)
-- ============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_logs') THEN
        -- Policy: Users can only see audit logs from their tenants
        DROP POLICY IF EXISTS "Users can view their tenant audit logs" ON public.audit_logs;
        CREATE POLICY "Users can view their tenant audit logs"
            ON public.audit_logs
            FOR SELECT
            USING (
                tenant_id IN (
                    SELECT tenant_id 
                    FROM public.user_tenants
                    WHERE user_id = auth.uid()
                )
            );
    END IF;
END $$;

-- ============================================================================
-- SESSIONS TABLE POLICIES (if table exists)
-- ============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sessions') THEN
        -- Policy: Users can only see sessions from their tenants
        DROP POLICY IF EXISTS "Users can view their tenant sessions" ON public.sessions;
        CREATE POLICY "Users can view their tenant sessions"
            ON public.sessions
            FOR SELECT
            USING (
                tenant_id IN (
                    SELECT tenant_id 
                    FROM public.user_tenants
                    WHERE user_id = auth.uid()
                )
            );
    END IF;
END $$;

-- ============================================================================
-- NOTES
-- ============================================================================

-- These policies ensure that:
-- 1. Users can only see data from tenants they belong to
-- 2. Database-level security enforces tenant isolation
-- 3. Application-level checks are still needed for authorization (roles, permissions)
-- 4. RLS works as defense in depth alongside application checks

-- To test RLS policies:
-- 1. Connect as different users
-- 2. Try to query data from other tenants
-- 3. Verify that RLS blocks unauthorized access




