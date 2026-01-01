#!/usr/bin/env python3
"""
City Manager Service - Initialization Module

Micro-module for City Manager service initialization with proper infrastructure connections.
"""

from typing import Any


class Initialization:
    """Initialization module for City Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_infrastructure_connections(self):
        """
        Initialize infrastructure connections using direct foundation access.
        
        City Manager uses SmartCityRoleBase which provides direct Public Works access
        (Smart City privilege - ALL abstractions, not selective via Platform Gateway).
        """
        try:
            if self.service.logger:
                self.service.logger.info("🔌 Connecting to Public Works infrastructure abstractions (direct access)...")
            
            # City Manager has direct foundation access via SmartCityRoleBase
            # Use mixin methods which access via DI Container (direct, not Platform Gateway)
            self.service.session_abstraction = self.service.get_session_abstraction()
            if not self.service.session_abstraction:
                raise Exception("Session Abstraction not available")
            
            self.service.state_management_abstraction = self.service.get_state_management_abstraction()
            if not self.service.state_management_abstraction:
                raise Exception("State Management Abstraction not available")
            
            # Use same abstractions as Post Office Service
            self.service.messaging_abstraction = self.service.get_messaging_abstraction()
            if not self.service.messaging_abstraction:
                raise Exception("Messaging Abstraction not available")
            
            self.service.event_management_abstraction = self.service.get_event_management_abstraction()
            if not self.service.event_management_abstraction:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Event Management Abstraction not available (City Manager doesn't need it directly)")
            
            # File management abstraction (other services need this, but City Manager doesn't use it directly)
            try:
                self.service.file_management_abstraction = self.service.get_file_management_abstraction()
            except:
                self.service.file_management_abstraction = None
                if self.service.logger:
                    self.service.logger.warning("⚠️ File Management Abstraction not available (City Manager doesn't need it directly)")
            
            # Analytics abstraction (optional - may not be available in all environments)
            try:
                self.service.analytics_abstraction = self.service.get_analytics_abstraction()
            except:
                self.service.analytics_abstraction = None
                if self.service.logger:
                    self.service.logger.warning("⚠️ Analytics Abstraction not available (optional)")
            
            # Health abstraction (utility capability - optional for City Manager)
            try:
                self.service.health_abstraction = self.service.get_health_abstraction()
            except:
                self.service.health_abstraction = None
                if self.service.logger:
                    self.service.logger.warning("⚠️ Health Abstraction not available (optional for City Manager)")
            
            # Telemetry abstraction (utility capability - optional for City Manager)
            try:
                self.service.telemetry_abstraction = self.service.get_telemetry_abstraction()
            except:
                self.service.telemetry_abstraction = None
                if self.service.logger:
                    self.service.logger.warning("⚠️ Telemetry Abstraction not available (optional for City Manager)")
            
            self.service.is_infrastructure_connected = True
            
            if self.service.logger:
                self.service.logger.info("✅ Infrastructure connections established (direct foundation access)")
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to connect to infrastructure: {str(e)}")
            raise e
    
    async def initialize_direct_libraries(self):
        """Initialize direct library injection for business logic."""
        try:
            if self.service.logger:
                self.service.logger.info("📚 Initializing direct library injection...")
            
            # Get libraries from DI Container
            # httpx is typically not needed as a service - it's a standard library
            # If needed, it can be imported directly: import httpx
            # For now, skip httpx initialization
            self.service.httpx = None
            
            # asyncio is already available
            self.service.asyncio = __import__('asyncio')
            
            if self.service.logger:
                self.service.logger.info("✅ Direct libraries initialized")
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to initialize direct libraries: {str(e)}")
            raise e
    
    async def initialize_city_manager_capabilities(self):
        """Initialize City Manager specific capabilities."""
        try:
            if self.service.logger:
                self.service.logger.info("🏛️ Initializing City Manager capabilities...")
            
            # Initialize Smart City service registry
            self.service.smart_city_services = {
                "security_guard": {"status": "initialized", "instance": None},
                "traffic_cop": {"status": "initialized", "instance": None},
                "nurse": {"status": "initialized", "instance": None},
                "librarian": {"status": "initialized", "instance": None},
                "data_steward": {"status": "initialized", "instance": None},
                "content_steward": {"status": "initialized", "instance": None},
                "post_office": {"status": "initialized", "instance": None},
                "conductor": {"status": "initialized", "instance": None}
            }
            
            # Initialize manager hierarchy
            # Note: Experience is now a Foundation (not a Manager)
            self.service.manager_hierarchy = {
                "solution_manager": {"status": "pending", "instance": None},
                "journey_manager": {"status": "pending", "instance": None},
                "delivery_manager": {"status": "pending", "instance": None}
            }
            
            # Initialize bootstrapping state
            self.service.bootstrapping_complete = False
            self.service.realm_startup_complete = False
            
            if self.service.logger:
                self.service.logger.info("✅ City Manager capabilities initialized")
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to initialize City Manager capabilities: {str(e)}")
            raise e

