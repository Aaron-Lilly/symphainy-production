#!/usr/bin/env python3
"""
Curator Foundation Service - Coordinator

Platform-wide pattern enforcement and registry management service that coordinates
4 focused micro-services for capability registration, pattern validation, 
anti-pattern detection, and OpenAPI generation.

WHAT (Foundation Role): I need to provide platform-wide pattern enforcement and registry management
HOW (Foundation Service): I coordinate specialized micro-services for comprehensive platform governance
"""

import os
import sys
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from bases.foundation_service_base import FoundationServiceBase
from common.utilities import UserContext

# Import micro-services
from .services import (
    CapabilityRegistryService,
    PatternValidationService,
    AntiPatternDetectionService,
    DocumentationGenerationService
)

# Import models from micro-modules
from .models import CapabilityDefinition, PatternDefinition, AntiPatternViolation


class CuratorFoundationService(FoundationServiceBase):
    """
    Curator Foundation Service - Platform-wide pattern enforcement and registry management coordinator
    
    Coordinates 4 specialized micro-services to provide comprehensive platform governance:
    - CapabilityRegistryService: Service capability registration and discovery
    - PatternValidationService: Architectural pattern validation and rule enforcement
    - AntiPatternDetectionService: Code scanning and violation tracking
    - DocumentationGenerationService: OpenAPI and documentation generation
    
    WHAT (Foundation Role): I need to provide platform-wide pattern enforcement and registry management
    HOW (Foundation Service): I coordinate specialized micro-services for comprehensive platform governance
    """
    
    def __init__(self, utility_foundation, public_works_foundation=None):
        """Initialize Curator Foundation Service."""
        super().__init__("curator_foundation", utility_foundation)
        
        self.utility_foundation = utility_foundation
        self.public_works_foundation = public_works_foundation
        
        # Initialize micro-services
        self.capability_registry = CapabilityRegistryService(utility_foundation, public_works_foundation)
        self.pattern_validation = PatternValidationService(utility_foundation)
        self.antipattern_detection = AntiPatternDetectionService(utility_foundation, self.pattern_validation)
        self.documentation_generation = DocumentationGenerationService(utility_foundation, self.capability_registry)
        
        self.logger.info("🏛️ Curator Foundation Service initialized as Platform Registry Coordinator")
    
    async def initialize(self):
        """Initialize the Curator Foundation Service and all micro-services."""
        try:
            await super().initialize()
            self.logger.info("🚀 Initializing Curator Foundation Service...")
            
        # Initialize all micro-services
        await self.capability_registry.initialize()
        await self.pattern_validation.initialize()
        await self.antipattern_detection.initialize()
        await self.documentation_generation.initialize()
            
        # Register with Public Works Foundation if available
        if self.public_works_foundation:
                await self._register_with_public_works()
            
        self.logger.info("✅ Curator Foundation Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Curator Foundation Service: {e}")
            await self.error_handler.handle_error(e)
            raise
    
    async def _register_with_public_works(self):
        """Register Curator Foundation Service with Public Works Foundation."""
        try:
            if self.public_works_foundation:
                # Register Curator as a foundation service
                await self.public_works_foundation.register_foundation_service(
                    "curator_foundation", 
                    self
                )
                self.logger.info("📝 Registered with Public Works Foundation")
            except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Public Works Foundation: {e}")
    
    # ============================================================================
    # CAPABILITY REGISTRATION (Delegated to CapabilityRegistryService)
    
    async def register_capability(self, service_name: str, capability: Dict[str, Any]) -> Dict[str, Any]:
        """Register a service capability in the central registry."""
        try:
            # Register capability
            result = await self.capability_registry.register_capability(service_name, capability)
            
        # Validate patterns for the registered service
        if result.get("success"):
                capability_def = await self.capability_registry.get_capability(service_name)
                if capability_def:
                    await self._validate_service_patterns(service_name, capability_def)
            
        return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register capability for {service_name}: {e}")
            await self.handle_error(e, f"register_capability_{service_name}")
            raise
    
    async def _validate_service_patterns(self, service_name: str, capability: CapabilityDefinition):
        """Validate service patterns for a registered capability."""
        try:
            # Validate interface naming
            interface_pattern = {
                "name": f"{service_name}_interface",
                "type": "interface",
                "value": capability.interface_name
            }
            interface_validation = await self.pattern_validation.validate_pattern(interface_pattern)
            
        # Validate endpoint patterns
        endpoint_violations = []
        for endpoint in capability.endpoints:
                endpoint_pattern = {
                    "name": f"{service_name}_endpoint",
                    "type": "api",
                    "value": endpoint
                }
                endpoint_validation = await self.pattern_validation.validate_pattern(endpoint_pattern)
                endpoint_violations.extend(endpoint_validation['violations'])
            
        # Log validation results
        total_violations = len(interface_validation['violations']) + len(endpoint_violations)
        if total_violations > 0:
                self.logger.warning(f"⚠️ Service {service_name} has {total_violations} pattern violations")
        else:
                self.logger.info(f"✅ Service {service_name} passed all pattern validations")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to validate patterns for {service_name}: {e}")
    
    async def get_capability(self, service_name: str) -> Optional[CapabilityDefinition]:
        """Get a registered capability."""
        return await self.capability_registry.get_capability(service_name)
    
    async def list_capabilities(self, realm: str = None) -> List[CapabilityDefinition]:
        """List all registered capabilities, optionally filtered by realm."""
        return await self.capability_registry.list_capabilities(realm)
    
    # ============================================================================
    # PATTERN VALIDATION (Delegated to PatternValidationService)
    
    async def validate_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a pattern against architectural rules."""
        return await self.pattern_validation.validate_pattern(pattern)
    
    # ============================================================================
    # ANTI-PATTERN DETECTION (Delegated to AntiPatternDetectionService)
    
    async def detect_anti_patterns(self, service_code: str, file_path: str = None) -> List[AntiPatternViolation]:
        """Detect anti-patterns in service code."""
        return await self.antipattern_detection.detect_anti_patterns(service_code, file_path)
    
    async def get_violations(self, pattern_name: str = None, severity: str = None) -> List[AntiPatternViolation]:
        """Get anti-pattern violations with optional filtering."""
        return await self.antipattern_detection.get_violations(pattern_name, severity)
    
    async def clear_violations(self, pattern_name: str = None):
        """Clear anti-pattern violations."""
        await self.antipattern_detection.clear_violations(pattern_name)
    
    # ============================================================================
    # OPENAPI GENERATION (Delegated to DocumentationGenerationService)
    
    async def generate_openapi_spec(self, service_name: str) -> Dict[str, Any]:
        """Generate OpenAPI specification for a service."""
        return await self.documentation_generation.generate_openapi_spec(service_name)
    
    async def generate_docs(self, service_name: str) -> Dict[str, Any]:
        """Generate documentation for a service."""
        return await self.documentation_generation.generate_docs(service_name)
    
    # ============================================================================
    # REGISTRY MANAGEMENT (Aggregated from micro-services)
    
    async def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive registry status and statistics."""
        try:
            # Get status from all micro-services
            capability_status = await self.capability_registry.get_registry_status()
            pattern_status = await self.pattern_validation.get_pattern_status()
            violation_summary = await self.antipattern_detection.get_violation_summary()
            doc_status = await self.documentation_generation.get_documentation_status()
            
        # Aggregate status
        status = {
                "curator_foundation": {
                    "service_name": "curator_foundation",
                    "micro_services": [
                        "capability_registry",
                        "pattern_validation", 
                        "antipattern_detection",
                        "documentation_generation"
                    ],
                    "last_updated": capability_status.get("last_updated")
                },
                "capability_registry": capability_status,
                "pattern_validation": pattern_status,
                "antipattern_detection": violation_summary,
                "documentation_generation": doc_status
        }
            
        await self.log_operation_with_telemetry("get_registry_status", details=status)
        return status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get registry status: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # MICRO-SERVICE ACCESS
    
    @property
    def capability_registry_service(self) -> CapabilityRegistryService:
        """Get the capability registry service."""
        return self.capability_registry
    
    @property
    def pattern_validation_service(self) -> PatternValidationService:
        """Get the pattern validation service."""
        return self.pattern_validation
    
    @property
    def antipattern_detection_service(self) -> AntiPatternDetectionService:
        """Get the anti-pattern detection service."""
        return self.antipattern_detection
    
    @property
    def documentation_generation_service(self) -> DocumentationGenerationService:
        """Get the documentation generation service."""
        return self.documentation_generation


