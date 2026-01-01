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
from foundations.utility_foundation.utilities import UserContext

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
    Curator Foundation Service - Platform Registry Coordinator
    
    Coordinates 4 specialized micro-services to provide comprehensive platform governance.
    This service acts as a coordinator and provides access to focused micro-services.
    
    Micro-Services:
    - CapabilityRegistryService: Service capability registration and discovery
    - PatternValidationService: Architectural pattern validation and rule enforcement
    - AntiPatternDetectionService: Code scanning and violation tracking
    - DocumentationGenerationService: OpenAPI and documentation generation
    
    IMPORTANT: This service no longer provides backward compatibility methods.
    Services must use the micro-services directly via the provided properties.
    
    WHAT (Foundation Role): I need to coordinate platform-wide pattern enforcement and registry management
    HOW (Foundation Service): I coordinate specialized micro-services for comprehensive platform governance
    """
    
    def __init__(self, validation_utility, serialization_utility, config_utility, health_utility, mcp_utilities, public_works_foundation=None):
        """Initialize Curator Foundation Service."""
        super().__init__("curator_foundation")
        
        # Store utilities
        self.validation_utility = validation_utility
        self.serialization_utility = serialization_utility
        self.config_utility = config_utility
        self.health_utility = health_utility
        self.mcp_utilities = mcp_utilities
        
        
        self.public_works_foundation = public_works_foundation
        
        # Initialize micro-services
        self.capability_registry = CapabilityRegistryService(
        self.validation_utility, self.serialization_utility, self.config_utility,
        self.health_utility, self.mcp_utilities, public_works_foundation)
        self.pattern_validation = PatternValidationService(utility_foundation)
        self.antipattern_detection = AntiPatternDetectionService(
        self.validation_utility, self.serialization_utility, self.config_utility,
        self.health_utility, self.mcp_utilities, self.pattern_validation)
        self.documentation_generation = DocumentationGenerationService(
        self.validation_utility, self.serialization_utility, self.config_utility,
        self.health_utility, self.mcp_utilities, self.capability_registry)
        
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
            
            # Register APG Document Intelligence capabilities
            await self._register_apg_capabilities()
            
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
    # COORDINATOR STATUS
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """Get comprehensive coordinator status and statistics."""
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
                    "role": "Platform Registry Coordinator",
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
            
            await self.log_operation_with_telemetry("get_coordinator_status", details=status)
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get coordinator status: {e}")
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
    
    async def _register_apg_capabilities(self):
        """Register APG Document Intelligence capabilities."""
        try:
            self.logger.info("📄 Registering APG Document Intelligence capabilities...")
            
            # Register APG Document Intelligence Infrastructure Abstraction
            apg_infrastructure_capability = {
                "interface": "IAPGDocumentIntelligenceInfrastructure",
                "endpoints": [
                    {
                        "name": "process_aar_document",
                        "method": "POST",
                        "path": "/apg/process-aar",
                        "description": "Process After Action Report document with cost optimization"
                    },
                    {
                        "name": "process_multiple_aars",
                        "method": "POST", 
                        "path": "/apg/process-multiple-aars",
                        "description": "Process multiple AAR documents efficiently"
                    },
                    {
                        "name": "get_knowledge_base_summary",
                        "method": "GET",
                        "path": "/apg/knowledge-base-summary",
                        "description": "Get summary of accumulated knowledge from processed AARs"
                    }
                ],
                "tools": [
                    {
                        "name": "aar_processor",
                        "description": "Process AAR documents for exercise planning insights",
                        "capabilities": ["document_parsing", "lesson_extraction", "risk_assessment"]
                    },
                    {
                        "name": "knowledge_extractor",
                        "description": "Extract lessons learned and risk factors from documents",
                        "capabilities": ["pattern_detection", "content_analysis", "insight_generation"]
                    },
                    {
                        "name": "outcome_forecaster",
                        "description": "Generate outcome forecasts based on historical patterns",
                        "capabilities": ["forecasting", "pattern_analysis", "risk_prediction"]
                    }
                ],
                "description": "APG Document Intelligence Infrastructure Abstraction for cost-optimized AAR processing",
                "realm": "infrastructure"
            }
            
            await self.capability_registry.register_capability(
                "apg_document_intelligence_infrastructure", 
                apg_infrastructure_capability
            )
            
            # Register APG Document Intelligence Business Abstraction
            apg_business_capability = {
                "interface": "IAPGDocumentIntelligenceBusiness",
                "endpoints": [
                    {
                        "name": "process_aar_document",
                        "method": "POST",
                        "path": "/apg/business/process-aar",
                        "description": "Process AAR document with business logic and knowledge storage"
                    },
                    {
                        "name": "process_multiple_aars",
                        "method": "POST",
                        "path": "/apg/business/process-multiple-aars", 
                        "description": "Process multiple AARs with batch optimization"
                    },
                    {
                        "name": "get_exercise_planning_insights",
                        "method": "GET",
                        "path": "/apg/business/exercise-planning-insights",
                        "description": "Get exercise planning insights based on historical data"
                    },
                    {
                        "name": "assess_exercise_risks",
                        "method": "POST",
                        "path": "/apg/business/assess-exercise-risks",
                        "description": "Assess risks for proposed exercise plan"
                    }
                ],
                "tools": [
                    {
                        "name": "exercise_planner",
                        "description": "Generate exercise planning recommendations based on historical data",
                        "capabilities": ["planning", "recommendation_generation", "insight_analysis"]
                    },
                    {
                        "name": "risk_assessor",
                        "description": "Assess risks for exercise plans using historical patterns",
                        "capabilities": ["risk_analysis", "mitigation_planning", "pattern_matching"]
                    },
                    {
                        "name": "knowledge_manager",
                        "description": "Manage lessons learned and risk factors knowledge base",
                        "capabilities": ["knowledge_storage", "pattern_detection", "insight_aggregation"]
                    }
                ],
                "description": "APG Document Intelligence Business Abstraction for exercise planning and risk assessment",
                "realm": "business"
            }
            
            await self.capability_registry.register_capability(
                "apg_document_intelligence_business",
                apg_business_capability
            )
            
            self.logger.info("✅ APG Document Intelligence capabilities registered successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register APG capabilities: {e}")
            # Don't raise - this is not critical for core functionality
