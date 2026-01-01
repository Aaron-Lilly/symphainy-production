-- Migration: Backfill Tenant Data for Existing Users
-- Date: 2025-12-01
-- Purpose: Create tenants for existing users and link them
-- Phase: 1 - MVP Security Fixes
-- 
-- WARNING: Run this AFTER migrations 001 and 002
-- This script creates tenants for existing users who don't have one

-- ============================================================================
-- CREATE TENANTS FOR EXISTING USERS
-- ============================================================================
-- This creates a tenant for each existing user who doesn't have one
INSERT INTO public.tenants (name, slug, type, owner_id, status)
SELECT 
    'Tenant for ' || COALESCE(email, id::text),
    'tenant-' || SUBSTRING(id::text, 1, 8),
    'individual',
    id,
    'active'
FROM auth.users
WHERE id NOT IN (
    SELECT DISTINCT owner_id 
    FROM public.tenants 
    WHERE owner_id IS NOT NULL
)
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- LINK USERS TO THEIR TENANTS
-- ============================================================================
-- Create user_tenants relationships for existing users
INSERT INTO public.user_tenants (user_id, tenant_id, role, is_primary)
SELECT 
    u.id,
    t.id,
    'owner',
    TRUE
FROM auth.users u
JOIN public.tenants t ON t.owner_id = u.id
WHERE NOT EXISTS (
    SELECT 1 
    FROM public.user_tenants ut 
    WHERE ut.user_id = u.id AND ut.tenant_id = t.id
);

-- ============================================================================
-- BACKFILL TENANT_ID IN EXISTING TABLES
-- ============================================================================

-- Backfill files table (if exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'files') THEN
        UPDATE public.files f
        SET tenant_id = (
            SELECT ut.tenant_id
            FROM public.user_tenants ut
            WHERE ut.user_id = f.user_id
              AND ut.is_primary = TRUE
            LIMIT 1
        )
        WHERE f.tenant_id IS NULL;
    END IF;
END $$;

-- Backfill audit_logs table (if exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'audit_logs') THEN
        UPDATE public.audit_logs al
        SET tenant_id = (
            SELECT ut.tenant_id
            FROM public.user_tenants ut
            WHERE ut.user_id = al.user_id
              AND ut.is_primary = TRUE
            LIMIT 1
        )
        WHERE al.tenant_id IS NULL;
    END IF;
END $$;

-- Backfill sessions table (if exists)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'sessions') THEN
        UPDATE public.sessions s
        SET tenant_id = (
            SELECT ut.tenant_id
            FROM public.user_tenants ut
            WHERE ut.user_id = s.user_id
              AND ut.is_primary = TRUE
            LIMIT 1
        )
        WHERE s.tenant_id IS NULL;
    END IF;
END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify the backfill worked:

-- Check users without tenants
-- SELECT u.id, u.email 
-- FROM auth.users u
-- LEFT JOIN public.user_tenants ut ON ut.user_id = u.id
-- WHERE ut.id IS NULL;

-- Check files without tenant_id
-- SELECT COUNT(*) as files_without_tenant
-- FROM public.files
-- WHERE tenant_id IS NULL;




