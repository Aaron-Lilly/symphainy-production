#!/usr/bin/env python3
"""
Solution Manager Service - Initialization Module

Micro-module for Solution Manager service initialization with proper infrastructure connections.
"""

import logging
from typing import Any


class Initialization:
    """Initialization module for Solution Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def initialize_infrastructure_connections(self):
        """Initialize infrastructure connections using mixin methods."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔌 Connecting to Public Works infrastructure abstractions...")
            
            # Get Public Works Foundation from DI Container
            if not hasattr(self.service, 'di_container') or not self.service.di_container:
                raise Exception("Solution Manager Service does not have di_container - initialization order issue")
            
            public_works_foundation = self.service.di_container.get_foundation_service("PublicWorksFoundationService")
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Solution Manager should use Smart City services (Traffic Cop) for session/state management
            # NOT direct infrastructure abstractions (architectural pattern to prevent spaghetti code)
            # Session and state management will be handled via Traffic Cop SOA API (discovered below)
            # We don't set session_abstraction or state_management_abstraction directly
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("ℹ️ Session and state management will be handled via Traffic Cop service")
            
            # Analytics abstraction (optional - may not be available in all environments)
            try:
                self.service.analytics_abstraction = self.service.get_analytics_abstraction()
            except:
                self.service.analytics_abstraction = None
                if self.service.logger:
                    self.service.logger.warning("⚠️ Analytics Abstraction not available (optional)")
            
            # Discover Smart City services via Curator for business-level operations
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔍 Discovering Smart City services via Curator...")
            
            # Security Guard - Authentication/Authorization
            self.service.security_guard = await self.service.get_security_guard_api()
            if not self.service.security_guard and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Security Guard service not available")
            
            # Traffic Cop - Session routing, state sync
            self.service.traffic_cop = await self.service.get_traffic_cop_api()
            if not self.service.traffic_cop and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Traffic Cop service not available")
            
            # Conductor - Workflow orchestration
            self.service.conductor = await self.service.get_conductor_api()
            if not self.service.conductor and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Conductor service not available")
            
            # Post Office - Structured messaging
            self.service.post_office = await self.service.get_post_office_api()
            if not self.service.post_office and hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.warning("⚠️ Post Office service not available")
            
            self.service.is_infrastructure_connected = True
            
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("✅ Infrastructure connections established")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to connect to infrastructure: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            raise e
    
    async def initialize_solution_manager_capabilities(self):
        """Initialize Solution Manager-specific capabilities."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🎯 Initializing Solution Manager capabilities...")
            
            # Initialize solution initiators
            self.service.solution_initiators = {
                "dashboard": {
                    "initiator_name": "DashboardInitiator",
                    "description": "Dashboard orchestration and realm health monitoring",
                    "capabilities": ["realm_health_monitoring", "cross_realm_aggregation", "dashboard_coordination"]
                },
                "mvp": {
                    "initiator_name": "MVPSolutionInitiator",
                    "description": "MVP solution orchestration and business outcome coordination",
                    "capabilities": ["solution_context_propagation", "mvp_journey_orchestration", "business_outcome_coordination"]
                },
                "future": {
                    "initiator_name": "FutureSolutionInitiator",
                    "description": "Future solution types and custom orchestration",
                    "capabilities": ["custom_solution_orchestration", "industry_specific_solutions", "enterprise_patterns"]
                }
            }
            
            # Initialize platform governance
            self.service.platform_governance = {
                "solution_discovery": {},
                "cross_solution_coordination": {},
                "platform_health": {},
                "governance_policies": {}
            }
            
            # Initialize capability flags
            self.service.platform_orchestration_enabled = True
            self.service.solution_discovery_enabled = True
            self.service.cross_solution_coordination_enabled = True
            self.service.platform_governance_enabled = True
            
            if self.service.logger:
                self.service.logger.info("✅ Solution Manager capabilities initialized")
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to initialize capabilities: {str(e)}")
            raise e


