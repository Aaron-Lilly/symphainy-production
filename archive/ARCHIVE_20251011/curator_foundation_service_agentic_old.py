#!/usr/bin/env python3
"""
Enhanced Curator Foundation Service - Agentic Integration

Platform-wide pattern enforcement and registry management service that coordinates
8 focused micro-services including 4 new agentic-specific services for comprehensive
platform governance and agentic dimension management.

WHAT (Foundation Role): I provide platform-wide pattern enforcement, registry management, and agentic dimension coordination
HOW (Foundation Service): I coordinate specialized micro-services for comprehensive platform governance including agentic capabilities
"""

import os
import sys
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from bases.foundation_services import FoundationServices
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService

# Import existing micro-services
from .services import (
    CapabilityRegistryService,
    PatternValidationService,
    AntiPatternDetectionService,
    DocumentationGenerationService
)

# Import new agentic micro-services
from .services.agent_capability_registry_service import AgentCapabilityRegistryService
from .services.agent_specialization_management_service import AgentSpecializationManagementService
from .services.agui_schema_documentation_service import AGUISchemaDocumentationService
from .services.agent_health_monitoring_service import AgentHealthMonitoringService

# Import models from micro-modules
from .models import CapabilityDefinition, PatternDefinition, AntiPatternViolation


class CuratorFoundationServiceAgentic:
    """
    Enhanced Curator Foundation Service - Agentic Integration
    
    Coordinates 8 specialized micro-services to provide comprehensive platform governance
    including full agentic dimension management. This service acts as a coordinator and 
    provides access to focused micro-services.
    
    Core Micro-Services:
    - CapabilityRegistryService: Service capability registration and discovery
    - PatternValidationService: Architectural pattern validation and rule enforcement
    - AntiPatternDetectionService: Code scanning and violation tracking
    - DocumentationGenerationService: OpenAPI and documentation generation
    
    Agentic Micro-Services:
    - AgentCapabilityRegistryService: Real-time agent capability reporting and management
    - AgentSpecializationManagementService: Agent specialization registration and management
    - AGUISchemaDocumentationService: AGUI schema documentation generation
    - AgentHealthMonitoringService: Agent-specific health monitoring and operational status
    
    WHAT (Foundation Role): I coordinate platform-wide pattern enforcement, registry management, and agentic dimension coordination
    HOW (Foundation Service): I coordinate specialized micro-services for comprehensive platform governance including agentic capabilities
    """
    
    def __init__(self, foundation_services: FoundationServices, 
                 public_works_foundation: Optional[PublicWorksFoundationService] = None):
        """Initialize Enhanced Curator Foundation Service with Agentic Integration."""
        self.foundation_services = foundation_services
        self.public_works_foundation = public_works_foundation
        
        # Get utilities from foundation services
        self.logger = foundation_services.get_logger("curator_foundation_agentic")
        self.config = foundation_services.get_config()
        self.health = foundation_services.get_health()
        self.telemetry = foundation_services.get_telemetry()
        self.security = foundation_services.get_security()
        self.error_handler = foundation_services.get_error_handler()
        self.tenant = foundation_services.get_tenant()
        
        # Initialize core micro-services
        self.capability_registry = CapabilityRegistryService(
            self.foundation_services, self.public_works_foundation
        )
        self.pattern_validation = PatternValidationService(
            self.foundation_services, self.public_works_foundation
        )
        self.antipattern_detection = AntiPatternDetectionService(
            self.foundation_services, self.public_works_foundation
        )
        self.documentation_generation = DocumentationGenerationService(
            self.foundation_services, self.public_works_foundation
        )
        
        # Initialize agentic micro-services
        self.agent_capability_registry = AgentCapabilityRegistryService(
            self.foundation_services, self.public_works_foundation
        )
        self.agent_specialization_management = AgentSpecializationManagementService(
            self.foundation_services, self.public_works_foundation
        )
        self.agui_schema_documentation = AGUISchemaDocumentationService(
            self.foundation_services, self.public_works_foundation
        )
        self.agent_health_monitoring = AgentHealthMonitoringService(
            self.foundation_services, self.public_works_foundation
        )
        
        self.logger.info("🏛️ Enhanced Curator Foundation Service with Agentic Integration initialized")
    
    async def initialize(self):
        """Initialize the Enhanced Curator Foundation Service and all micro-services."""
        try:
            self.logger.info("🚀 Initializing Enhanced Curator Foundation Service with Agentic Integration...")
            
            # Initialize core micro-services
            await self.capability_registry.initialize()
            await self.pattern_validation.initialize()
            await self.antipattern_detection.initialize()
            await self.documentation_generation.initialize()
            
            # Initialize agentic micro-services
            await self.agent_capability_registry.initialize()
            await self.agent_specialization_management.initialize()
            await self.agui_schema_documentation.initialize()
            await self.agent_health_monitoring.initialize()
            
            # Register with Public Works Foundation if available
            if self.public_works_foundation:
                await self._register_with_public_works()
            
            # Register agentic capabilities
            await self._register_agentic_capabilities()
            
            self.logger.info("✅ Enhanced Curator Foundation Service with Agentic Integration initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Enhanced Curator Foundation Service: {e}")
            self.error_handler.handle_error(e, "curator_foundation_agentic_initialization_failed")
            raise
    
    async def _register_with_public_works(self):
        """Register Curator Foundation with Public Works Foundation."""
        try:
            if self.public_works_foundation:
                # Register curator capabilities
                curator_capabilities = {
                    "pattern_validation": "Architectural pattern validation and enforcement",
                    "antipattern_detection": "Code scanning and violation detection",
                    "capability_registry": "Service capability registration and discovery",
                    "documentation_generation": "OpenAPI and documentation generation",
                    "agent_capability_registry": "Real-time agent capability reporting",
                    "agent_specialization_management": "Agent specialization registration",
                    "agui_schema_documentation": "AGUI schema documentation generation",
                    "agent_health_monitoring": "Agent health monitoring and status tracking"
                }
                
                await self.public_works_foundation.register_foundation_capabilities(
                    "curator_foundation", curator_capabilities
                )
                
                self.logger.info("✅ Registered Curator Foundation capabilities with Public Works")
                
        except Exception as e:
            self.logger.error(f"Failed to register with Public Works Foundation: {e}")
            self.error_handler.handle_error(e, "register_with_public_works_failed")
    
    async def _register_agentic_capabilities(self):
        """Register agentic-specific capabilities."""
        try:
            # Register agentic capabilities with the capability registry
            agentic_capabilities = [
                {
                    "name": "agent_capability_reporting",
                    "type": "agentic",
                    "description": "Real-time agent capability reporting and management",
                    "version": "1.0.0",
                    "status": "active"
                },
                {
                    "name": "agent_specialization_management",
                    "type": "agentic",
                    "description": "Agent specialization registration and management",
                    "version": "1.0.0",
                    "status": "active"
                },
                {
                    "name": "agui_schema_documentation",
                    "type": "agentic",
                    "description": "AGUI schema documentation generation",
                    "version": "1.0.0",
                    "status": "active"
                },
                {
                    "name": "agent_health_monitoring",
                    "type": "agentic",
                    "description": "Agent health monitoring and operational status tracking",
                    "version": "1.0.0",
                    "status": "active"
                }
            ]
            
            for capability in agentic_capabilities:
                await self.capability_registry.register_capability(capability)
            
            self.logger.info("✅ Registered agentic capabilities with Curator Foundation")
            
        except Exception as e:
            self.logger.error(f"Failed to register agentic capabilities: {e}")
            self.error_handler.handle_error(e, "register_agentic_capabilities_failed")
    
    # ============================================================================
    # AGENTIC INTEGRATION API METHODS
    # ============================================================================
    
    async def register_agent_with_curator(self, agent_id: str, agent_name: str, 
                                        agent_config: Dict[str, Any]) -> bool:
        """
        Register an agent with the Curator Foundation for comprehensive management.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            agent_config: Agent configuration including capabilities, specialization, etc.
            
        Returns:
            bool: True if registration successful
        """
        try:
            self.logger.info(f"📝 Registering agent {agent_name} with Curator Foundation")
            
            # Register agent capabilities
            capabilities = agent_config.get("capabilities", [])
            if capabilities:
                await self.agent_capability_registry.register_agent_capabilities(
                    agent_id, agent_name, capabilities,
                    pillar=agent_config.get("pillar"),
                    specialization=agent_config.get("specialization")
                )
            
            # Register agent specialization
            specialization_config = agent_config.get("specialization_config")
            if specialization_config:
                await self.agent_specialization_management.register_agent_specialization(
                    agent_id, agent_name, specialization_config
                )
            
            # Generate AGUI documentation
            await self.agui_schema_documentation.generate_agent_documentation(
                agent_name, "api"
            )
            await self.agui_schema_documentation.generate_agent_documentation(
                agent_name, "user_guide"
            )
            
            # Register for health monitoring
            await self.agent_health_monitoring.register_agent_for_monitoring(
                agent_id, agent_name
            )
            
            self.logger.info(f"✅ Successfully registered agent {agent_name} with Curator Foundation")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register agent {agent_name} with Curator Foundation: {e}")
            self.error_handler.handle_error(e, f"register_agent_with_curator_failed_{agent_id}")
            return False
    
    async def get_agent_curator_report(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive Curator report for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Comprehensive agent report or None if not found
        """
        try:
            # Get capability report
            capability_report = await self.agent_capability_registry.get_agent_capability_report(agent_id)
            
            # Get specialization info
            specialization = await self.agent_specialization_management.get_agent_specialization(agent_id)
            
            # Get documentation info
            agent_name = capability_report.agent_name if capability_report else f"Agent_{agent_id}"
            documentation = await self.agui_schema_documentation.get_agent_documentation(agent_name)
            
            # Get health report
            health_report = await self.agent_health_monitoring.get_agent_health_report(agent_id)
            
            return {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "capability_report": capability_report.__dict__ if capability_report else None,
                "specialization": specialization.__dict__ if specialization else None,
                "documentation": [doc.__dict__ for doc in documentation] if documentation else [],
                "health_report": health_report.__dict__ if health_report else None,
                "generated_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate Curator report for agent {agent_id}: {e}")
            self.error_handler.handle_error(e, f"get_agent_curator_report_failed_{agent_id}")
            return None
    
    async def get_agentic_dimension_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of the agentic dimension."""
        try:
            # Get all agent capability reports
            capability_reports = await self.agent_capability_registry.get_all_agent_reports()
            
            # Get all specialization analytics
            specialization_analytics = await self.agent_specialization_management.get_all_specialization_analytics()
            
            # Get documentation report
            documentation_report = await self.agui_schema_documentation.get_documentation_report()
            
            # Get health summary
            health_summary = await self.agent_health_monitoring.get_health_summary()
            
            # Get capability analytics
            capability_analytics = await self.agent_capability_registry.get_capability_analytics()
            
            return {
                "total_agents": len(capability_reports),
                "capability_summary": {
                    "total_capabilities": sum(report.total_capabilities for report in capability_reports),
                    "active_capabilities": sum(report.active_capabilities for report in capability_reports),
                    "capabilities_by_type": capability_analytics.get("type_distribution", {}),
                    "capabilities_by_pillar": capability_analytics.get("pillar_distribution", {})
                },
                "specialization_summary": {
                    "total_specializations": len(specialization_analytics),
                    "specializations_by_pillar": {spec.pillar: 1 for spec in specialization_analytics},
                    "average_success_rate": sum(spec.average_success_rate for spec in specialization_analytics) / len(specialization_analytics) if specialization_analytics else 0.0
                },
                "documentation_summary": {
                    "documentation_coverage": documentation_report.documentation_coverage,
                    "quality_score": documentation_report.quality_score,
                    "documentation_types": documentation_report.documentation_types
                },
                "health_summary": health_summary,
                "generated_at": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate agentic dimension summary: {e}")
            self.error_handler.handle_error(e, "get_agentic_dimension_summary_failed")
            return {}
    
    async def update_agent_usage(self, agent_id: str, capability_name: str, 
                               success: bool = True, usage_data: Dict[str, Any] = None) -> bool:
        """
        Update agent usage statistics across all relevant services.
        
        Args:
            agent_id: Agent identifier
            capability_name: Name of the capability used
            success: Whether the usage was successful
            usage_data: Additional usage data
            
        Returns:
            bool: True if update successful
        """
        try:
            # Update capability usage
            await self.agent_capability_registry.update_capability_usage(
                capability_name, agent_id, usage_data
            )
            
            # Update specialization usage
            await self.agent_specialization_management.update_specialization_usage(
                agent_id, success, capability_name
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update agent usage for {agent_id}: {e}")
            self.error_handler.handle_error(e, f"update_agent_usage_failed_{agent_id}")
            return False
    
    # ============================================================================
    # CORE CURATOR API METHODS (Delegated to micro-services)
    # ============================================================================
    
    async def register_capability(self, capability_definition: Dict[str, Any]) -> bool:
        """Register a capability with the Curator Foundation."""
        return await self.capability_registry.register_capability(capability_definition)
    
    async def validate_pattern(self, pattern_definition: Dict[str, Any]) -> bool:
        """Validate an architectural pattern."""
        return await self.pattern_validation.validate_pattern(pattern_definition)
    
    async def detect_antipatterns(self, code_path: str) -> List[AntiPatternViolation]:
        """Detect anti-patterns in code."""
        return await self.antipattern_detection.detect_antipatterns(code_path)
    
    async def generate_documentation(self, service_name: str, documentation_type: str = "openapi") -> bool:
        """Generate documentation for a service."""
        return await self.documentation_generation.generate_documentation(service_name, documentation_type)
    
    # ============================================================================
    # HEALTH AND STATUS METHODS
    # ============================================================================
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Curator Foundation Service."""
        try:
            # Get status from all micro-services
            core_services_status = {
                "capability_registry": await self.capability_registry.get_status(),
                "pattern_validation": await self.pattern_validation.get_status(),
                "antipattern_detection": await self.antipattern_detection.get_status(),
                "documentation_generation": await self.documentation_generation.get_status()
            }
            
            agentic_services_status = {
                "agent_capability_registry": "healthy",  # These services don't have get_status yet
                "agent_specialization_management": "healthy",
                "agui_schema_documentation": "healthy",
                "agent_health_monitoring": "healthy"
            }
            
            # Determine overall status
            all_statuses = list(core_services_status.values()) + list(agentic_services_status.values())
            overall_status = "healthy" if all(status == "healthy" for status in all_statuses) else "degraded"
            
            return {
                "service_name": "curator_foundation_agentic",
                "overall_status": overall_status,
                "core_services": core_services_status,
                "agentic_services": agentic_services_status,
                "total_services": len(core_services_status) + len(agentic_services_status),
                "healthy_services": len([s for s in all_statuses if s == "healthy"]),
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get Curator Foundation status: {e}")
            self.error_handler.handle_error(e, "get_curator_foundation_status_failed")
            return {
                "service_name": "curator_foundation_agentic",
                "overall_status": "error",
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check for the Curator Foundation Service."""
        try:
            self.logger.info("🔍 Running Curator Foundation health check...")
            
            # Get status
            status = await self.get_status()
            
            # Get agentic dimension summary
            agentic_summary = await self.get_agentic_dimension_summary()
            
            # Determine health
            overall_health = "healthy" if status["overall_status"] == "healthy" else "degraded"
            
            return {
                "service_name": "curator_foundation_agentic",
                "overall_health": overall_health,
                "status": status,
                "agentic_dimension": agentic_summary,
                "health_checks": {
                    "core_services": status["healthy_services"],
                    "total_services": status["total_services"],
                    "agentic_integration": "active"
                },
                "timestamp": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.error_handler.handle_error(e, "curator_foundation_health_check_failed")
            return {
                "service_name": "curator_foundation_agentic",
                "overall_health": "unhealthy",
                "error": str(e),
                "timestamp": self._get_current_timestamp()
            }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def cleanup(self):
        """Cleanup the Curator Foundation Service and all micro-services."""
        try:
            self.logger.info("🧹 Cleaning up Curator Foundation Service...")
            
            # Cleanup core micro-services
            if hasattr(self.capability_registry, 'cleanup'):
                await self.capability_registry.cleanup()
            if hasattr(self.pattern_validation, 'cleanup'):
                await self.pattern_validation.cleanup()
            if hasattr(self.antipattern_detection, 'cleanup'):
                await self.antipattern_detection.cleanup()
            if hasattr(self.documentation_generation, 'cleanup'):
                await self.documentation_generation.cleanup()
            
            # Cleanup agentic micro-services
            await self.agent_capability_registry.cleanup()
            await self.agent_specialization_management.cleanup()
            await self.agui_schema_documentation.cleanup()
            await self.agent_health_monitoring.cleanup()
            
            self.logger.info("✅ Curator Foundation Service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            self.error_handler.handle_error(e, "curator_foundation_cleanup_failed")
