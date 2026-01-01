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
        """Initialize infrastructure connections via Platform Gateway and Smart City services."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔌 Connecting to infrastructure via Platform Gateway...")
            
            # Verify Platform Gateway is available (passed in __init__)
            if not hasattr(self.service, 'platform_gateway') or not self.service.platform_gateway:
                # This is a warning, not an error - managers can work with limited functionality
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.warning("⚠️ Platform Gateway not available - operating with limited infrastructure access")
            else:
                if hasattr(self.service, 'logger') and self.service.logger:
                    self.service.logger.info("✅ Platform Gateway available for selective infrastructure access")
            
            # Solution Manager uses Smart City services for platform capabilities
            # This maintains proper architectural separation: Smart City = HOW, Managers = WHAT
            # Session and state management will be handled via Traffic Cop SOA API (discovered below)
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("ℹ️ Session and state management will be handled via Smart City services (Traffic Cop)")
            
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
    
    async def bootstrap_solution_foundation_services(self):
        """
        Bootstrap foundational Solution realm services (EAGER).
        
        This follows the City Manager pattern - Solution Manager bootstraps
        foundational Solution realm services before dependent services need them.
        
        Currently bootstraps:
        - DataSolutionOrchestratorService (foundational for all data operations)
        """
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🚀 Bootstrapping Solution foundation services...")
            
            # Bootstrap Data Solution Orchestrator Service (foundational)
            from backend.solution.services.data_solution_orchestrator_service.data_solution_orchestrator_service import DataSolutionOrchestratorService
            
            platform_gateway = self.service.di_container.get_foundation_service("PlatformInfrastructureGateway")
            if not platform_gateway:
                if self.service.logger:
                    self.service.logger.warning("⚠️ PlatformInfrastructureGateway not available - Data Solution Orchestrator will be lazy-loaded")
                return False
            
            # Initialize Data Solution Orchestrator Service
            data_solution_orchestrator = DataSolutionOrchestratorService(
                service_name="DataSolutionOrchestratorService",
                realm_name="solution",
                platform_gateway=platform_gateway,
                di_container=self.service.di_container
            )
            await data_solution_orchestrator.initialize()
            
            # Store reference for later use
            if not hasattr(self.service, 'solution_services'):
                self.service.solution_services = {}
            self.service.solution_services['data_solution_orchestrator'] = data_solution_orchestrator
            
            if self.service.logger:
                self.service.logger.info("✅ Data Solution Orchestrator Service bootstrapped (EAGER)")
            
            return True
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to bootstrap Solution foundation services: {e}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise - allow Solution Manager to continue initialization
            # Service will be lazy-loaded if needed
            return False
    
    async def discover_solution_realm_services(self):
        """Discover Solution realm services via Curator."""
        try:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.info("🔍 Discovering Solution realm services via Curator...")
            
            # Get Curator from DI Container
            curator = self.service.di_container.get_foundation_service("CuratorFoundationService")
            
            if not curator:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Curator not available - Solution services will not be discovered")
                return
            
            # Discover Solution Composer Service
            try:
                solution_composer_info = await curator.discover_service_by_name("SolutionComposerService")
                if solution_composer_info:
                    # Store service info for later access
                    if not hasattr(self.service, 'solution_services'):
                        self.service.solution_services = {}
                    self.service.solution_services['composer'] = solution_composer_info
                    if self.service.logger:
                        self.service.logger.info("✅ Discovered Solution Composer Service")
                else:
                    if self.service.logger:
                        self.service.logger.warning("⚠️ Solution Composer Service not found")
            except Exception as e:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Failed to discover Solution Composer: {str(e)}")
            
            # Discover Data Solution Orchestrator Service
            try:
                data_solution_info = await curator.discover_service_by_name("DataSolutionOrchestratorService")
                if data_solution_info:
                    if not hasattr(self.service, 'solution_services'):
                        self.service.solution_services = {}
                    self.service.solution_services['data_solution'] = data_solution_info
                    if self.service.logger:
                        self.service.logger.info("✅ Discovered Data Solution Orchestrator Service")
                else:
                    if self.service.logger:
                        self.service.logger.warning("⚠️ Data Solution Orchestrator Service not found")
            except Exception as e:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Failed to discover Data Solution Orchestrator: {str(e)}")
            
            # Discover Solution Analytics Service
            try:
                analytics_info = await curator.discover_service_by_name("SolutionAnalyticsService")
                if analytics_info:
                    if not hasattr(self.service, 'solution_services'):
                        self.service.solution_services = {}
                    self.service.solution_services['analytics'] = analytics_info
                    if self.service.logger:
                        self.service.logger.info("✅ Discovered Solution Analytics Service")
                else:
                    if self.service.logger:
                        self.service.logger.warning("⚠️ Solution Analytics Service not found")
            except Exception as e:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Failed to discover Solution Analytics: {str(e)}")
            
            # Discover Solution Deployment Manager Service
            try:
                deployment_info = await curator.discover_service_by_name("SolutionDeploymentManagerService")
                if deployment_info:
                    if not hasattr(self.service, 'solution_services'):
                        self.service.solution_services = {}
                    self.service.solution_services['deployment_manager'] = deployment_info
                    if self.service.logger:
                        self.service.logger.info("✅ Discovered Solution Deployment Manager Service")
                else:
                    if self.service.logger:
                        self.service.logger.warning("⚠️ Solution Deployment Manager Service not found")
            except Exception as e:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Failed to discover Solution Deployment Manager: {str(e)}")
            
            if hasattr(self.service, 'logger') and self.service.logger:
                discovered_count = len(self.service.solution_services) if hasattr(self.service, 'solution_services') else 0
                self.service.logger.info(f"✅ Solution realm service discovery complete ({discovered_count}/4 services found)")
            
        except Exception as e:
            if hasattr(self.service, 'logger') and self.service.logger:
                self.service.logger.error(f"❌ Failed to discover Solution services: {str(e)}")
                import traceback
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")
            # Don't raise - discovery failure shouldn't break initialization
    
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


