-- Migration: Create Tenant Management Tables
-- Date: 2025-12-01
-- Purpose: Enable multi-tenant architecture with proper tenant isolation
-- Phase: 1 - MVP Security Fixes

-- ============================================================================
-- TENANTS TABLE
-- ============================================================================
-- Stores tenant/organization information
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('individual', 'organization', 'enterprise')),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    owner_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for tenant lookups
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON public.tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_owner_id ON public.tenants(owner_id);
CREATE INDEX IF NOT EXISTS idx_tenants_status ON public.tenants(status);
CREATE INDEX IF NOT EXISTS idx_tenants_type ON public.tenants(type);

-- ============================================================================
-- USER-TENANT RELATIONSHIP TABLE
-- ============================================================================
-- Junction table for many-to-many relationship between users and tenants
-- Supports users being members of multiple tenants
CREATE TABLE IF NOT EXISTS public.user_tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    is_primary BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, tenant_id)
);

-- Indexes for user-tenant lookups
CREATE INDEX IF NOT EXISTS idx_user_tenants_user_id ON public.user_tenants(user_id);
CREATE INDEX IF NOT EXISTS idx_user_tenants_tenant_id ON public.user_tenants(tenant_id);
CREATE INDEX IF NOT EXISTS idx_user_tenants_primary ON public.user_tenants(user_id, is_primary) WHERE is_primary = TRUE;
CREATE INDEX IF NOT EXISTS idx_user_tenants_role ON public.user_tenants(role);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get user's primary tenant
CREATE OR REPLACE FUNCTION public.get_user_primary_tenant(user_uuid UUID)
RETURNS UUID AS $$
    SELECT tenant_id
    FROM public.user_tenants
    WHERE user_id = user_uuid
      AND is_primary = TRUE
    LIMIT 1;
$$ LANGUAGE sql SECURITY DEFINER;

-- Function to check if user belongs to tenant
CREATE OR REPLACE FUNCTION public.user_belongs_to_tenant(user_uuid UUID, tenant_uuid UUID)
RETURNS BOOLEAN AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.user_tenants
        WHERE user_id = user_uuid
          AND tenant_id = tenant_uuid
    );
$$ LANGUAGE sql SECURITY DEFINER;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON public.tenants
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE public.tenants IS 'Stores tenant/organization information for multi-tenant architecture';
COMMENT ON TABLE public.user_tenants IS 'Junction table linking users to tenants with roles';
COMMENT ON COLUMN public.tenants.slug IS 'Unique URL-friendly identifier for tenant';
COMMENT ON COLUMN public.tenants.type IS 'Tenant type: individual, organization, or enterprise';
COMMENT ON COLUMN public.user_tenants.is_primary IS 'Indicates the primary tenant for a user (users can belong to multiple tenants)';
COMMENT ON COLUMN public.user_tenants.role IS 'User role within the tenant: owner, admin, member, or viewer';




