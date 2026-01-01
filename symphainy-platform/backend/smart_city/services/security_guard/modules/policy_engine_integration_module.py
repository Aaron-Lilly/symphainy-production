#!/usr/bin/env python3
"""
Policy Engine Integration Module - Security Guard Micro-Module

Handles policy engine integration and Supabase RLS policy enforcement.
Part of the Security Guard Service micro-modular architecture.

WHAT (Policy Role): I handle policy engine integration and enforcement
HOW (Policy Implementation): I integrate with policy engines and enforce policies
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

# Import security protocols
from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import SecurityContext

# Import policy engines
from engines.default_policy_engine import DefaultPolicyEngine
from engines.supabase_rls_policy_engine import SupabaseRLSEngine


class PolicyEngineIntegrationModule:
    """
    Policy Engine Integration Module - Security Guard Micro-Module
    
    Handles policy engine integration and Supabase RLS policy enforcement.
    Part of the Security Guard Service micro-modular architecture.
    
    WHAT (Policy Role): I handle policy engine integration and enforcement
    HOW (Policy Implementation): I integrate with policy engines and enforce policies
    """
    
    def __init__(self, service_name: str = "policy_engine_integration_module"):
        """Initialize Policy Engine Integration Module."""
        self.service_name = service_name
        self.logger = self.service.di_container.get_logger(f"PolicyEngineIntegration-{service_name}")
        
        # Policy engines
        self.default_policy_engine = DefaultPolicyEngine()
        self.supabase_rls_engine = SupabaseRLSEngine()
        self.active_policy_engine = self.default_policy_engine
        
        # Policy enforcement statistics
        self.policy_stats = {
            "policy_checks": 0,
            "policy_allowed": 0,
            "policy_denied": 0,
            "supabase_rls_checks": 0,
            "default_policy_checks": 0
        }
        
        self.logger.info(f"✅ Policy Engine Integration Module '{service_name}' initialized")
    
    async def initialize(self):
        """Initialize Policy Engine Integration Module."""
        try:
            self.logger.info(f"🚀 Initializing Policy Engine Integration Module '{self.service_name}'...")
            
            # Initialize policy engines
            await self.default_policy_engine.initialize() if hasattr(self.default_policy_engine, 'initialize') else None
            await self.supabase_rls_engine.initialize() if hasattr(self.supabase_rls_engine, 'initialize') else None
            
            self.logger.info(f"✅ Policy Engine Integration Module '{self.service_name}' initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Policy Engine Integration Module '{self.service_name}': {e}")
            raise
    
    async def enforce_policy(self, action: str, resource: str, context: SecurityContext, 
                           policy_engine: str = "default") -> Dict[str, Any]:
        """Enforce policy using specified policy engine."""
        try:
            self.policy_stats["policy_checks"] += 1
            
            # Select policy engine
            if policy_engine == "supabase_rls":
                self.policy_stats["supabase_rls_checks"] += 1
                result = await self.supabase_rls_engine.is_allowed(action, resource, context)
            else:
                self.policy_stats["default_policy_checks"] += 1
                result = await self.default_policy_engine.is_allowed(action, resource, context)
            
            # Update statistics
            if result.allowed:
                self.policy_stats["policy_allowed"] += 1
            else:
                self.policy_stats["policy_denied"] += 1
            
            self.logger.info(f"Policy enforcement: {action} on {resource} - {'Allowed' if result.allowed else 'Denied'}")
            return {
                "success": result.allowed,
                "message": result.reason,
                "policy_engine": policy_engine,
                "policy_id": result.policy_id,
                "context": result.context
            }
            
        except Exception as e:
            self.logger.error(f"❌ Policy enforcement failed: {e}")
            return {
                "success": False,
                "message": f"Policy enforcement failed: {e}",
                "policy_engine": policy_engine
            }
    
    async def enforce_tenant_policy(self, tenant_id: str, action: str, resource: str, 
                                   context: SecurityContext) -> Dict[str, Any]:
        """Enforce tenant-specific policy using Supabase RLS."""
        try:
            # Use Supabase RLS for tenant isolation
            result = await self.enforce_policy(action, resource, context, "supabase_rls")
            
            # Additional tenant isolation check
            if context.tenant_id != tenant_id:
                result["success"] = False
                result["message"] = "Tenant isolation policy violation"
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Tenant policy enforcement failed: {e}")
            return {
                "success": False,
                "message": f"Tenant policy enforcement failed: {e}"
            }
    
    async def enforce_feature_policy(self, feature: str, context: SecurityContext) -> Dict[str, Any]:
        """Enforce feature access policy."""
        try:
            # Check if feature is allowed for user's tenant
            result = await self.enforce_policy("access", f"feature:{feature}", context, "default")
            
            # Additional feature-specific checks
            if feature in ["admin", "super_admin"] and "admin" not in context.roles:
                result["success"] = False
                result["message"] = f"Feature '{feature}' requires admin role"
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Feature policy enforcement failed: {e}")
            return {
                "success": False,
                "message": f"Feature policy enforcement failed: {e}"
            }
    
    def set_active_policy_engine(self, policy_engine: str):
        """Set active policy engine."""
        try:
            if policy_engine == "supabase_rls":
                self.active_policy_engine = self.supabase_rls_engine
            else:
                self.active_policy_engine = self.default_policy_engine
            
            self.logger.info(f"✅ Active policy engine set to: {policy_engine}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to set active policy engine: {e}")
    
    async def get_policy_metrics(self) -> Dict[str, Any]:
        """Get policy enforcement metrics."""
        try:
            total_checks = self.policy_stats["policy_checks"]
            allow_rate = (self.policy_stats["policy_allowed"] / total_checks * 100) if total_checks > 0 else 0
            
            return {
                "total_policy_checks": self.policy_stats["policy_checks"],
                "policy_allowed": self.policy_stats["policy_allowed"],
                "policy_denied": self.policy_stats["policy_denied"],
                "allow_rate": f"{allow_rate:.2f}%",
                "supabase_rls_checks": self.policy_stats["supabase_rls_checks"],
                "default_policy_checks": self.policy_stats["default_policy_checks"],
                "active_policy_engine": self.active_policy_engine.__class__.__name__
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get policy metrics: {e}")
            return {}
    
    def get_capabilities(self) -> list:
        """Get module capabilities."""
        return [
            "policy_enforcement",
            "tenant_policy_enforcement",
            "feature_policy_enforcement",
            "policy_engine_selection",
            "policy_metrics"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "module": "PolicyEngineIntegration",
            "service_name": self.service_name,
            "status": "active",
            "capabilities": self.get_capabilities(),
            "active_policy_engine": self.active_policy_engine.__class__.__name__,
            "metrics": await self.get_policy_metrics()
        }



