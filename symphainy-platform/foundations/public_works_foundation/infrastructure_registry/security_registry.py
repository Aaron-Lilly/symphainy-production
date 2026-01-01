#!/usr/bin/env python3
"""
Security Registry - Infrastructure Registry (Exposure/Discovery Layer)

Registry for exposing and discovering security infrastructure abstractions.
This is Layer 5 of the 5-layer security architecture.

WHAT (Infrastructure Role): I expose and manage security infrastructure abstractions
HOW (Infrastructure Implementation): I provide discovery and health monitoring for registered abstractions

NOTE: This registry does NOT create adapters or abstractions.
      All creation happens in Public Works Foundation Service.
      This registry only holds references and provides discovery.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SecurityRegistry:
    """
    Security infrastructure registry - exposure/discovery layer only.
    
    This registry holds references to abstractions created by Public Works Foundation Service.
    It provides discovery, health monitoring, and service registration capabilities.
    
    Does NOT create adapters or abstractions - that's Public Works Foundation's responsibility.
    """
    
    def __init__(self):
        """Initialize Security Registry (exposure only, no creation)."""
        self.logger = logging.getLogger("SecurityRegistry")
        
        # Infrastructure abstractions (registered by Public Works Foundation)
        self._abstractions = {}
        
        # Policy engines (registered by Public Works Foundation)
        self._policy_engines = {}
        
        self.logger.info("✅ Security Registry initialized (exposure/discovery layer)")
    
    # ============================================================================
    # REGISTRATION METHODS (Called by Public Works Foundation)
    # ============================================================================
    
    def register_abstraction(self, name: str, abstraction: Any) -> None:
        """
        Register an abstraction (created by Public Works Foundation).
        
        Args:
            name: Abstraction name (e.g., "auth", "session", "authorization", "tenant")
            abstraction: Abstraction instance (already created with dependency injection)
        """
        if not abstraction:
            raise ValueError(f"Cannot register None for abstraction '{name}'")
        
        self._abstractions[name] = abstraction
        self.logger.info(f"✅ Registered '{name}' abstraction")
    
    def register_policy_engine(self, name: str, policy_engine: Any) -> None:
        """
        Register a policy engine (created by Public Works Foundation).
        
        Args:
            name: Policy engine name (e.g., "default", "supabase_rls")
            policy_engine: Policy engine instance (already created)
        """
        if not policy_engine:
            raise ValueError(f"Cannot register None for policy engine '{name}'")
        
        self._policy_engines[name] = policy_engine
        self.logger.info(f"✅ Registered '{name}' policy engine")
    
    # ============================================================================
    # DISCOVERY METHODS (Called by Platform Gateway, Services, etc.)
    # ============================================================================
    
    def get_abstraction(self, name: str) -> Any:
        """
        Get infrastructure abstraction by name (discovery method).
        
        Args:
            name: Abstraction name
            
        Returns:
            Abstraction instance
            
        Raises:
            ValueError: If abstraction not registered
        """
        if name not in self._abstractions:
            available = list(self._abstractions.keys())
            raise ValueError(
                f"Abstraction '{name}' not registered. "
                f"Available: {available}"
            )
        return self._abstractions[name]
    
    def get_policy_engine(self, name: str = "default") -> Any:
        """
        Get policy engine by name.
        
        Args:
            name: Policy engine name (default: "default")
            
        Returns:
            Policy engine instance or None if not found
        """
        return self._policy_engines.get(name)
    
    def get_all_abstractions(self) -> Dict[str, Any]:
        """Get all registered abstractions."""
        return self._abstractions.copy()
    
    def get_all_policy_engines(self) -> Dict[str, Any]:
        """Get all registered policy engines."""
        return self._policy_engines.copy()
    
    # ============================================================================
    # HEALTH MONITORING
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Aggregate health check for all registered abstractions.
        
        Returns:
            Dict containing health status for all abstractions
        """
        health = {
            "status": "healthy",
            "abstractions": {},
            "policy_engines_count": len(self._policy_engines)
        }
        
        for name, abstraction in self._abstractions.items():
            try:
                if hasattr(abstraction, 'health_check'):
                    abstraction_health = await abstraction.health_check()
                    health["abstractions"][name] = abstraction_health
                    
                    # Check if abstraction is unhealthy
                    if isinstance(abstraction_health, dict):
                        if abstraction_health.get("status") != "healthy":
                            health["status"] = "degraded"
                    elif not abstraction_health:
                        health["status"] = "degraded"
                else:
                    # No health check method - assume healthy
                    health["abstractions"][name] = {"status": "unknown"}
            except Exception as e:
                health["abstractions"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health["status"] = "unhealthy"
        
        return health
    
    # ============================================================================
    # STATUS METHODS
    # ============================================================================
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status information."""
        return {
            "abstractions_count": len(self._abstractions),
            "policy_engines_count": len(self._policy_engines),
            "abstractions": list(self._abstractions.keys()),
            "policy_engines": list(self._policy_engines.keys())
        }
    
    def is_ready(self) -> bool:
        """
        Check if registry is ready (has required abstractions).
        
        Returns:
            bool: True if all required abstractions are registered
        """
        required = ["auth", "session", "authorization", "tenant"]
        return all(name in self._abstractions for name in required)
    
    @property
    def is_initialized(self) -> bool:
        """Alias for is_ready() for backward compatibility."""
        return self.is_ready()
