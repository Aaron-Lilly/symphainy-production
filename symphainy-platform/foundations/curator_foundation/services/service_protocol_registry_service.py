#!/usr/bin/env python3
"""
Service Protocol Registry Service

Registers and manages service protocols (Python typing.Protocol) for the Curator Foundation.
Aligns with existing Protocol pattern in codebase (ServiceProtocol, RealmServiceProtocol).

WHAT (Service Role): I need to manage service protocol registration and discovery
HOW (Service Implementation): I maintain a protocol registry with method contracts and semantic mappings
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Import utilities directly
from utilities import (
    ValidationUtility, SerializationUtility, ConfigurationUtility,
    HealthManagementUtility
)


class ServiceProtocolRegistryService(FoundationServiceBase):
    """
    Service Protocol Registry Service - Protocol registration and discovery
    
    Manages service protocol registration (Python typing.Protocol) with method
    contracts and semantic mappings. Aligns with existing Protocol architecture.
    
    WHAT (Service Role): I need to manage service protocol registration and discovery
    HOW (Service Implementation): I maintain a protocol registry with method contracts and semantic mappings
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize Service Protocol Registry Service."""
        super().__init__("service_protocol_registry", di_container)
        
        # Store public works foundation reference
        self.public_works_foundation = public_works_foundation
        
        # Protocol registry: service_name -> protocol_name -> protocol_definition
        self.protocol_registry: Dict[str, Dict[str, Dict[str, Any]]] = {}
        
        self.logger.info("📋 Service Protocol Registry Service initialized")
    
    async def initialize(self):
        """Initialize the Service Protocol Registry Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("service_protocol_registry_initialize_start", success=True)
            
            await super().initialize()
            self.logger.info("🚀 Initializing Service Protocol Registry Service...")
            
            self.logger.info("✅ Service Protocol Registry Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("service_protocol_registry_initialized", 1.0, {"service": "service_protocol_registry"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("service_protocol_registry_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "service_protocol_registry_initialize")
            raise
    
    async def register_service_protocol(
        self,
        service_name: str,
        protocol_name: str,
        protocol: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> bool:
        """
        Register a service protocol (Python typing.Protocol).
        
        Protocols are Python typing.Protocol definitions (not interfaces).
        Aligns with existing Protocol pattern (ServiceProtocol, RealmServiceProtocol).
        
        Args:
            service_name: Name of the service (e.g., "FileParserService")
            protocol_name: Name of the protocol (e.g., "IFileParser")
            protocol: Protocol definition with method contracts
            user_context: Optional user context for security and tenant validation
        
        Protocol definition format:
        {
            "methods": {
                "parse_file": {
                    "input_schema": {...},
                    "output_schema": {...},
                    "semantic_mapping": {
                        "domain_capability": "content.upload_file",
                        "user_journey": "upload_document_for_analysis"
                    }
                }
            }
        }
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "register_service_protocol_start",
                success=True,
                details={"service_name": service_name, "protocol_name": protocol_name}
            )
            
            # Validate inputs
            if not service_name or not protocol_name:
                raise ValueError("service_name and protocol_name are required")
            
            if not protocol or not isinstance(protocol, dict):
                raise ValueError("protocol must be a dictionary")
            
            # Initialize service entry if needed
            if service_name not in self.protocol_registry:
                self.protocol_registry[service_name] = {}
            
            # Store protocol definition
            self.protocol_registry[service_name][protocol_name] = {
                "protocol_name": protocol_name,
                "protocol": protocol,
                "registered_at": datetime.utcnow().isoformat(),
                "user_context": user_context
            }
            
            self.logger.info(f"✅ Protocol registered: {service_name}.{protocol_name}")
            
            # Record health metric
            await self.record_health_metric(
                "protocol_registered",
                1.0,
                {"service_name": service_name, "protocol_name": protocol_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "register_service_protocol_complete",
                success=True,
                details={"service_name": service_name, "protocol_name": protocol_name}
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(
                e,
                "register_service_protocol",
                details={"service_name": service_name, "protocol_name": protocol_name}
            )
            return False
    
    async def get_service_protocol(
        self,
        service_name: str,
        protocol_name: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get service protocol(s).
        
        Args:
            service_name: Name of the service
            protocol_name: Optional specific protocol name (if None, returns all protocols for service)
        
        Returns:
            Protocol definition(s) or None if not found
        """
        try:
            if service_name not in self.protocol_registry:
                return None
            
            if protocol_name:
                return self.protocol_registry[service_name].get(protocol_name)
            else:
                return self.protocol_registry[service_name]
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get service protocol: {e}")
            return None
    
    async def list_protocols(
        self,
        service_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        List all registered protocols.
        
        Args:
            service_name: Optional service name filter
        
        Returns:
            List of protocol definitions
        """
        try:
            protocols = []
            
            if service_name:
                if service_name in self.protocol_registry:
                    for protocol_name, protocol_data in self.protocol_registry[service_name].items():
                        protocols.append({
                            "service_name": service_name,
                            "protocol_name": protocol_name,
                            "registered_at": protocol_data.get("registered_at")
                        })
            else:
                for svc_name, svc_protocols in self.protocol_registry.items():
                    for protocol_name, protocol_data in svc_protocols.items():
                        protocols.append({
                            "service_name": svc_name,
                            "protocol_name": protocol_name,
                            "registered_at": protocol_data.get("registered_at")
                        })
            
            return protocols
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list protocols: {e}")
            return []

