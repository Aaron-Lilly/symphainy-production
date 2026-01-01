#!/usr/bin/env python3
"""
Curator Integration Helper

Provides standard integration patterns for services to register with the Curator Foundation.
Follows the remediation plan patterns for consistent service integration.

WHAT (Helper Role): I provide standard integration patterns for Curator Foundation registration
HOW (Helper Implementation): I provide templates and utilities for consistent service integration
"""

import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))


class CuratorIntegrationHelper:
    """
    Curator Integration Helper
    
    Provides standard integration patterns and utilities for services to register
    with the Curator Foundation following the remediation plan patterns.
    
    Features:
    - Standard service registration template
    - Anti-pattern removal utilities
    - Service metadata validation
    - Curator integration status tracking
    - Error handling standardization
    """
    
    @staticmethod
    def create_service_metadata(service_name: str, service_type: str, 
                              capabilities: List[Dict[str, Any]], 
                              endpoints: List[str] = None,
                              tags: List[str] = None,
                              address: str = "localhost",
                              port: int = None,
                              version: str = "1.0.0",
                              architecture: str = "microservice") -> Dict[str, Any]:
        """
        Create standardized service metadata for Curator Foundation registration.
        
        Args:
            service_name: Name of the service
            service_type: Type of service (smart_city, business_enablement, experience, agentic)
            capabilities: List of service capabilities
            endpoints: List of service endpoints
            tags: List of service tags
            address: Service address
            port: Service port
            version: Service version
            architecture: Service architecture
            
        Returns:
            Standardized service metadata
        """
        return {
            "service_name": service_name,
            "service_type": service_type,
            "capabilities": capabilities,
            "endpoints": endpoints or [],
            "tags": tags or [service_type],
            "address": address,
            "port": port,
            "version": version,
            "architecture": architecture,
            "registered_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_capability_definition(name: str, capability_type: str, 
                                   description: str, parameters: Dict[str, Any] = None,
                                   dependencies: List[str] = None,
                                   version: str = "1.0.0",
                                   status: str = "active") -> Dict[str, Any]:
        """
        Create standardized capability definition.
        
        Args:
            name: Capability name
            capability_type: Type of capability
            description: Capability description
            parameters: Capability parameters
            dependencies: Capability dependencies
            version: Capability version
            status: Capability status
            
        Returns:
            Standardized capability definition
        """
        return {
            "name": name,
            "type": capability_type,
            "description": description,
            "parameters": parameters or {},
            "dependencies": dependencies or [],
            "version": version,
            "status": status
        }
    
    @staticmethod
    async def register_with_curator(service_instance, curator_foundation, 
                                  service_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard service registration with Curator Foundation.
        
        Args:
            service_instance: The service instance to register
            curator_foundation: Curator Foundation Service instance
            service_metadata: Service metadata
            
        Returns:
            Registration result
        """
        try:
            if not curator_foundation:
                return {"success": False, "message": "Curator Foundation not available"}
            
            # Check if already registered
            if hasattr(service_instance, 'is_registered_with_curator') and service_instance.is_registered_with_curator:
                return {"success": True, "message": "Service already registered"}
            
            # Register with Curator Foundation
            registration_result = await curator_foundation.register_service(service_instance, service_metadata)
            
            if registration_result["success"]:
                # Update service registration status
                service_instance.is_registered_with_curator = True
                service_instance.curator_registration_id = registration_result.get("registration_id")
                
                return {
                    "success": True, 
                    "registration_id": registration_result.get("registration_id"),
                    "message": f"Service {service_metadata['service_name']} registered successfully"
                }
            else:
                return {
                    "success": False, 
                    "error": registration_result.get("error"),
                    "message": f"Failed to register service {service_metadata['service_name']}"
                }
                
        except Exception as e:
            # Use proper error handling if available
            if hasattr(service_instance, 'error_handler'):
                return service_instance.error_handler.handle_error("service_registration", e)
            else:
                return {"success": False, "error": str(e)}
    
    @staticmethod
    def validate_service_metadata(service_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate service metadata for Curator Foundation registration.
        
        Args:
            service_metadata: Service metadata to validate
            
        Returns:
            Validation result with errors if any
        """
        errors = []
        
        # Required fields
        required_fields = ["service_name", "service_type", "capabilities"]
        for field in required_fields:
            if field not in service_metadata:
                errors.append(f"Missing required field: {field}")
        
        # Validate service type
        valid_service_types = ["smart_city", "business_enablement", "experience", "agentic"]
        service_type = service_metadata.get("service_type")
        if service_type and service_type not in valid_service_types:
            errors.append(f"Invalid service type: {service_type}. Must be one of: {valid_service_types}")
        
        # Validate capabilities
        capabilities = service_metadata.get("capabilities", [])
        if not isinstance(capabilities, list):
            errors.append("Capabilities must be a list")
        else:
            for i, capability in enumerate(capabilities):
                if not isinstance(capability, dict):
                    errors.append(f"Capability {i} must be a dictionary")
                else:
                    if "name" not in capability:
                        errors.append(f"Capability {i} missing required field: name")
                    if "type" not in capability:
                        errors.append(f"Capability {i} missing required field: type")
                    if "description" not in capability:
                        errors.append(f"Capability {i} missing required field: description")
        
        # Validate endpoints
        endpoints = service_metadata.get("endpoints", [])
        if not isinstance(endpoints, list):
            errors.append("Endpoints must be a list")
        
        # Validate tags
        tags = service_metadata.get("tags", [])
        if not isinstance(tags, list):
            errors.append("Tags must be a list")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    @staticmethod
    def create_standard_service_template(service_name: str, service_type: str) -> str:
        """
        Create a standard service template with Curator Foundation integration.
        
        Args:
            service_name: Name of the service
            service_type: Type of service
            
        Returns:
            Service template code
        """
        template = f'''#!/usr/bin/env python3
"""
{service_name} - {service_type.title()} Service

Standard service template with Curator Foundation integration.

WHAT (Service Role): I provide [service functionality]
HOW (Service Implementation): I implement [service implementation details]
"""

import sys
import os
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.curator_foundation.curator_integration_helper import CuratorIntegrationHelper


class {service_name.replace(' ', '').replace('_', '')}Service:
    """
    {service_name} Service with Curator Foundation integration.
    
    WHAT (Service Role): I provide [service functionality]
    HOW (Service Implementation): I implement [service implementation details]
    """
    
    def __init__(self, public_works_foundation: PublicWorksFoundationService, 
                 curator_foundation: Optional[CuratorFoundationService] = None):
        """Initialize {service_name} Service."""
        self.service_name = "{service_name}"
        self.service_type = "{service_type}"
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Use proper utilities from foundation (following remediation plan)
        self.error_handler = public_works_foundation.error_handler_abstraction
        self.tenant_management = public_works_foundation.tenant_management_abstraction
        self.logger = public_works_foundation.logger_abstraction
        self.config = public_works_foundation.config_abstraction
        self.health = public_works_foundation.health_abstraction
        self.telemetry = public_works_foundation.telemetry_abstraction
        self.security = public_works_foundation.security_authorization_abstraction
        
        # Curator Foundation integration
        self.is_registered_with_curator = False
        self.curator_registration_id = None
        
        # Service configuration
        self.service_version = "1.0.0"
        self.service_port = 8000  # Update as needed
        self.architecture = "microservice"
        
        # Service capabilities
        self.supported_operations = [
            # Define your service operations here
        ]
        
        # SOA endpoints
        self.soa_endpoints = [
            # Define your SOA endpoints here
        ]
        
        self.logger.info(f"{{self.service_name}} Service initialized with Curator Foundation integration")
    
    async def initialize(self):
        """Initialize the service and register with Curator Foundation."""
        try:
            self.logger.info(f"🚀 Initializing {{self.service_name}} Service...")
            
            # Initialize service-specific functionality
            await self._initialize_service()
            
            # Register with Curator Foundation
            if self.curator_foundation:
                await self._register_with_curator()
            
            self.logger.info(f"✅ {{self.service_name}} Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {{self.service_name}} Service: {{e}}")
            self.get_error_handler().handle_error(e, f"{{self.service_name.lower()}}_initialization_failed")
            raise
    
    async def _initialize_service(self):
        """Initialize service-specific functionality."""
        # Implement your service initialization logic here
        pass
    
    async def _register_with_curator(self) -> Dict[str, Any]:
        """Register this service with the Curator Foundation."""
        try:
            # Create service metadata
            service_metadata = CuratorIntegrationHelper.create_service_metadata(
                service_name=self.service_name,
                service_type=self.service_type,
                capabilities=self._get_service_capabilities(),
                endpoints=[endpoint.get("path", endpoint) for endpoint in self.soa_endpoints],
                tags=[self.service_type, "microservice"],
                address="localhost",
                port=self.service_port,
                version=self.service_version,
                architecture=self.architecture
            )
            
            # Register with Curator Foundation
            registration_result = await CuratorIntegrationHelper.register_with_curator(
                self, self.curator_foundation, service_metadata
            )
            
            if registration_result["success"]:
                self.logger.info(f"✅ {{self.service_name}} registered with Curator Foundation")
            else:
                self.logger.warning(f"⚠️ Failed to register {{self.service_name}} with Curator Foundation: {{registration_result.get('error')}}")
            
            return registration_result
            
        except Exception as e:
            self.logger.error(f"Failed to register {{self.service_name}} with Curator Foundation: {{e}}")
            return self.get_error_handler().handle_error("service_registration", e)
    
    def _get_service_capabilities(self) -> List[Dict[str, Any]]:
        """Get service capabilities for Curator Foundation registration."""
        capabilities = []
        
        for operation in self.supported_operations:
            capability = CuratorIntegrationHelper.create_capability_definition(
                name=operation,
                capability_type="operation",
                description=f"{{operation}} operation for {{self.service_name}}",
                version=self.service_version,
                status="active"
            )
            capabilities.append(capability)
        
        return capabilities
    
    async def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {{
            "service_name": self.service_name,
            "service_type": self.service_type,
            "status": "healthy",
            "version": self.service_version,
            "is_registered_with_curator": self.is_registered_with_curator,
            "curator_registration_id": self.curator_registration_id,
            "timestamp": datetime.now().isoformat()
        }}
    
    async def cleanup(self):
        """Cleanup the service."""
        try:
            self.logger.info(f"🧹 Cleaning up {{self.service_name}} Service...")
            
            # Unregister from Curator Foundation if registered
            if self.curator_foundation and self.is_registered_with_curator:
                await self.curator_foundation.unregister_service(self.service_name)
            
            self.logger.info(f"✅ {{self.service_name}} Service cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during {{self.service_name}} cleanup: {{e}}")
            self.get_error_handler().handle_error(e, f"{{self.service_name.lower()}}_cleanup_failed")
'''
        
        return template
    
    @staticmethod
    def create_anti_pattern_removal_checklist() -> Dict[str, List[str]]:
        """
        Create anti-pattern removal checklist for services.
        
        Returns:
            Checklist for removing anti-patterns
        """
        return {
            "error_handling_anti_patterns": [
                "❌ Remove custom try/except blocks that should use error_handler",
                "❌ Remove custom error logging that should use error_handler.handle_error()",
                "❌ Remove parallel error handling implementations",
                "❌ Remove custom error formatting that should use error_handler",
                "✅ Use self.get_error_handler().handle_error() for all error handling",
                "✅ Use self.error_handler.log_error() for error logging",
                "✅ Use self.error_handler.format_error() for error formatting"
            ],
            "multi_tenancy_anti_patterns": [
                "❌ Remove custom tenant validation logic that should use tenant_management",
                "❌ Remove custom tenant context handling",
                "❌ Remove parallel multi-tenancy implementations",
                "❌ Remove custom tenant isolation logic",
                "✅ Use self.tenant_management.validate_tenant() for tenant validation",
                "✅ Use self.tenant_management.get_tenant_context() for tenant context",
                "✅ Use self.tenant_management.is_multi_tenant_enabled() for tenant checks"
            ],
            "curator_integration_anti_patterns": [
                "❌ Remove custom service registration logic",
                "❌ Remove custom capability registration",
                "❌ Remove parallel service discovery implementations",
                "❌ Remove custom service metadata handling",
                "✅ Use CuratorIntegrationHelper for service registration",
                "✅ Use CuratorIntegrationHelper for capability creation",
                "✅ Use standard service metadata templates"
            ],
            "utility_usage_anti_patterns": [
                "❌ Remove direct utility imports that should come from foundation",
                "❌ Remove custom utility initialization",
                "❌ Remove parallel utility implementations",
                "❌ Remove custom utility configuration",
                "✅ Use utilities from public_works_foundation",
                "✅ Use proper utility abstractions",
                "✅ Use standard utility access patterns"
            ]
        }
    
    @staticmethod
    def create_service_integration_guide() -> str:
        """
        Create service integration guide for Curator Foundation.
        
        Returns:
            Integration guide text
        """
        return """
# Curator Foundation Service Integration Guide

## Overview
This guide provides step-by-step instructions for integrating services with the Curator Foundation following the remediation plan patterns.

## Step 1: Service Initialization
1. Use proper utilities from `public_works_foundation`
2. Initialize Curator Foundation integration
3. Set up service metadata

## Step 2: Capability Registration
1. Define service capabilities using `CuratorIntegrationHelper.create_capability_definition()`
2. Create service metadata using `CuratorIntegrationHelper.create_service_metadata()`
3. Register with Curator Foundation using `CuratorIntegrationHelper.register_with_curator()`

## Step 3: Anti-Pattern Removal
1. Remove custom error handling implementations
2. Remove custom multi-tenancy implementations
3. Remove parallel utility implementations
4. Use standard utility access patterns

## Step 4: Testing
1. Test service registration with Curator Foundation
2. Test capability discovery
3. Test service health monitoring
4. Test error handling and multi-tenancy

## Step 5: Documentation
1. Update service documentation
2. Document Curator Foundation integration
3. Document anti-pattern removal
4. Document utility usage patterns

## Best Practices
- Always use proper utilities from foundation
- Follow standard service registration patterns
- Remove all anti-patterns before integration
- Test thoroughly before deployment
- Document all changes and integrations
"""
