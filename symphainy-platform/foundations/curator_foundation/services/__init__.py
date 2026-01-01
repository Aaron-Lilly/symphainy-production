#!/usr/bin/env python3
"""
Curator Foundation Services

Micro-services for the Curator Foundation, providing focused functionality
for capability registration, pattern validation, anti-pattern detection,
and documentation generation.
"""

from .capability_registry_service import CapabilityRegistryService
from .pattern_validation_service import PatternValidationService
from .antipattern_detection_service import AntiPatternDetectionService
from .documentation_generation_service import DocumentationGenerationService

# New services (Phase 2 refactoring)
from .service_protocol_registry_service import ServiceProtocolRegistryService
from .route_registry_service import RouteRegistryService
from .service_mesh_metadata_reporter_service import ServiceMeshMetadataReporterService

# Agentic-specific services
from .agent_capability_registry_service import AgentCapabilityRegistryService
from .agent_specialization_management_service import AgentSpecializationManagementService
from .agui_schema_documentation_service import AGUISchemaDocumentationService
from .agent_health_monitoring_service import AgentHealthMonitoringService

# SOA Client Service (moved from Communication Foundation)
from .soa_client_service import SOAClientService

# Auto-Discovery Service (cloud-ready)
from .auto_discovery_service import AutoDiscoveryService

__all__ = [
    "CapabilityRegistryService",
    "PatternValidationService", 
    "AntiPatternDetectionService",
    "DocumentationGenerationService",
    "ServiceProtocolRegistryService",
    "RouteRegistryService",
    "ServiceMeshMetadataReporterService",
    "AgentCapabilityRegistryService",
    "AgentSpecializationManagementService",
    "AGUISchemaDocumentationService",
    "AgentHealthMonitoringService",
    "SOAClientService",
    "AutoDiscoveryService"
]


