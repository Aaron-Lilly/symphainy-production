#!/usr/bin/env python3
"""
Pattern Validation Service (Refactored)

Handles pattern validation and rule checking for architectural patterns
across the platform. Refactored into micro-modules for better maintainability.

WHAT (Service Role): I need to validate architectural patterns and enforce rules
HOW (Service Implementation): I coordinate micro-modules for pattern validation
"""

import os
import sys
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Import utilities directly
from utilities import (
    ValidationUtility, SerializationUtility, ConfigurationUtility,
    HealthManagementUtility, MCPUtilities
)
from ..models import PatternDefinition
from foundations.utility_foundation.utilities.tenant.tenant_management_utility import TenantManagementUtility
from foundations.utility_foundation.utilities.security.security_service import SecurityService, UserContext

# Import micro-modules
from .micro_modules.pattern_initialization import PatternInitializationModule
from .micro_modules.pattern_validation_engine import PatternValidationEngineModule
from .micro_modules.pattern_management import PatternManagementModule
from .micro_modules.pattern_tenant_compliance import PatternTenantComplianceModule


class PatternValidationService(FoundationServiceBase):
    """
    Pattern Validation Service - Architectural pattern validation and rule enforcement
    
    Validates patterns against architectural rules and maintains pattern definitions
    for consistent platform architecture. Refactored into micro-modules.
    
    WHAT (Service Role): I need to validate architectural patterns and enforce rules
    HOW (Service Implementation): I coordinate micro-modules for pattern validation
    """
    
    def __init__(self, validation_utility, serialization_utility, config_utility, health_utility, mcp_utilities, env_loader=None, security_service: SecurityService = None):
        """Initialize Pattern Validation Service."""
        super().__init__("pattern_validation")
        
        # Store utilities
        self.validation_utility = validation_utility
        self.serialization_utility = serialization_utility
        self.config_utility = config_utility
        self.health_utility = health_utility
        self.mcp_utilities = mcp_utilities
        self.env_loader = env_loader
        self.security_service = security_service
        
        # Initialize micro-modules
        self.pattern_initialization = PatternInitializationModule(self.logger)
        self.pattern_validation_engine = PatternValidationEngineModule(self.logger)
        self.pattern_management = PatternManagementModule(self.logger)
        self.pattern_tenant_compliance = PatternTenantComplianceModule(self.logger, security_service)
        
        # Pattern registry
        self.pattern_registry: Dict[str, PatternDefinition] = {}
        
        self.logger.info("🔍 Pattern Validation Service initialized")
    
    async def initialize(self):
        """Initialize the Pattern Validation Service."""
        try:
            await super().initialize()
            self.logger.info("🚀 Initializing Pattern Validation Service...")
            
            # Initialize default patterns
            self.pattern_registry = self.pattern_initialization.initialize_default_patterns()
            
            self.logger.info("✅ Pattern Validation Service initialized successfully")
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="pattern_validation_initialize")
            raise
    
    # ============================================================================
    # PATTERN VALIDATION
    
    async def validate_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a pattern against architectural rules."""
        return await self.pattern_validation_engine.validate_pattern(pattern, self.pattern_registry)
    
    # ============================================================================
    # PATTERN MANAGEMENT
    
    async def add_pattern(self, pattern: PatternDefinition) -> bool:
        """Add a new pattern to the registry."""
        return await self.pattern_management.add_pattern(pattern, self.pattern_registry)
    
    async def remove_pattern(self, pattern_name: str) -> bool:
        """Remove a pattern from the registry."""
        return await self.pattern_management.remove_pattern(pattern_name, self.pattern_registry)
    
    async def get_pattern(self, pattern_name: str) -> PatternDefinition:
        """Get a specific pattern from the registry."""
        return await self.pattern_management.get_pattern(pattern_name, self.pattern_registry)
    
    async def list_patterns(self, pattern_type: str = None) -> List[PatternDefinition]:
        """List all patterns, optionally filtered by type."""
        return await self.pattern_management.list_patterns(pattern_type, self.pattern_registry)
    
    async def get_pattern_status(self) -> Dict[str, Any]:
        """Get pattern registry status and statistics."""
        return await self.pattern_management.get_pattern_status(self.pattern_registry)
    
    # ============================================================================
    # TENANT COMPLIANCE
    
    async def check_tenant_compliance(self, tenant_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Check tenant compliance with architectural patterns."""
        return await self.pattern_tenant_compliance.check_tenant_compliance(tenant_id, user_context, self.pattern_registry)
