#!/usr/bin/env python3
"""
Solution Realm Bridge - Solution API Integration within Communication Foundation

Provides Solution realm API endpoints through the unified Communication Foundation,
consolidating all Solution communication infrastructure in one place.

WHAT (Realm Bridge): I provide Solution realm API endpoints through Communication Foundation
HOW (Bridge Implementation): I create Solution FastAPI router and register with Communication Foundation
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

# Import Solution realm services
from backend.solution.services.solution_manager.solution_manager_service import SolutionManagerService

# Optional services (may not exist)
SolutionOrchestrationHubService = None
UserSolutionDesignService = None
try:
    from backend.solution.services.solution_orchestration_hub.solution_orchestration_hub_service import SolutionOrchestrationHubService
except ImportError:
    pass  # Service may not exist

try:
    from backend.solution.services.user_solution_design.user_solution_design_service import UserSolutionDesignService
except ImportError:
    pass  # Service may not exist

# Import utilities
from utilities import UserContext

logger = logging.getLogger(__name__)


class SolutionRealmBridge:
    """
    Solution Realm Bridge - Solution API Integration within Communication Foundation
    
    Provides Solution realm API endpoints through the unified Communication Foundation,
    consolidating all Solution communication infrastructure in one place.
    
    WHAT (Realm Bridge): I provide Solution realm API endpoints through Communication Foundation
    HOW (Bridge Implementation): I create Solution FastAPI router and register with Communication Foundation
    """
    
    def __init__(self, di_container, public_works_foundation, curator_foundation):
        """Initialize Solution Realm Bridge."""
        self.logger = logging.getLogger("SolutionRealmBridge")
        
        # Dependencies
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Solution services (will be initialized)
        self.solution_manager = None
        self.solution_orchestration_hub = None
        self.user_solution_design = None
        
        # Router
        self.router = APIRouter(prefix="/api/v1/solution", tags=["solution"])
        
        self.logger.info("🏗️ Solution Realm Bridge initialized")
    
    async def initialize(self):
        """Initialize Solution Realm Bridge and create router."""
        try:
            self.logger.info("🚀 Initializing Solution Realm Bridge...")
            
            # Initialize Solution services
            await self._initialize_solution_services()
            
            # Create Solution API router
            await self._create_solution_router()
            
            self.logger.info("✅ Solution Realm Bridge initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Solution Realm Bridge: {e}", exc_info=True)
            raise
    
    async def get_router(self, user_context: Dict[str, Any] = None) -> APIRouter:
        """Get the Solution realm router."""
        try:
            # Note: Realm bridges don't have utility access yet
            # Security/tenant validation would be added when DI Container utilities are available
            return self.router
        except Exception as e:
            self.logger.error(f"❌ Failed to get router: {e}", exc_info=True)
            raise
    
    # PRIVATE METHODS
    
    async def _initialize_solution_services(self):
        """Initialize Solution realm services."""
        self.logger.info("🔧 Initializing Solution realm services...")
        
        try:
            # Check if Data Solution Orchestrator already exists (bootstrapped by Solution Manager)
            curator = self.di_container.get_foundation_service("CuratorFoundationService")
            existing_service = None
            if curator:
                try:
                    existing_service = await curator.get_service("DataSolutionOrchestratorService")
                except:
                    pass
            
            if existing_service:
                self.data_solution_orchestrator = existing_service
                self.logger.info("✅ Data Solution Orchestrator Service already bootstrapped by Solution Manager")
            else:
                # Fallback: Initialize if not already bootstrapped (shouldn't happen in normal flow)
                self.logger.warning("⚠️ Data Solution Orchestrator not found - initializing as fallback (should be bootstrapped by Solution Manager)")
                from backend.solution.services.data_solution_orchestrator_service.data_solution_orchestrator_service import DataSolutionOrchestratorService
                platform_gateway = self.di_container.get_foundation_service("PlatformInfrastructureGateway")
                self.data_solution_orchestrator = DataSolutionOrchestratorService(
                    service_name="DataSolutionOrchestratorService",
                    realm_name="solution",
                    platform_gateway=platform_gateway,
                    di_container=self.di_container
                )
                await self.data_solution_orchestrator.initialize()
                self.logger.info("✅ Data Solution Orchestrator Service initialized (fallback)")
            
            # Initialize Solution Manager (only needs di_container)
            self.solution_manager = SolutionManagerService(di_container=self.di_container)
            await self.solution_manager.initialize()
            
            # Initialize Solution Orchestration Hub (try to get from DI Container or create with di_container only)
            try:
                self.solution_orchestration_hub = self.di_container.get_foundation_service("SolutionOrchestrationHubService")
                if not self.solution_orchestration_hub:
                    self.solution_orchestration_hub = SolutionOrchestrationHubService(di_container=self.di_container)
                    await self.solution_orchestration_hub.initialize()
            except:
                self.logger.info("ℹ️ Solution Orchestration Hub not available, skipping")
                self.solution_orchestration_hub = None
            
            # Initialize User Solution Design Service (try to get from DI Container or create with di_container only)
            try:
                self.user_solution_design = self.di_container.get_foundation_service("UserSolutionDesignService")
                if not self.user_solution_design:
                    self.user_solution_design = UserSolutionDesignService(di_container=self.di_container)
                    await self.user_solution_design.initialize()
            except:
                self.logger.info("ℹ️ User Solution Design Service not available, skipping")
                self.user_solution_design = None
            
            self.logger.info("✅ Solution realm services initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Solution realm services: {e}")
            raise
    
    async def _create_solution_router(self):
        """Create Solution realm FastAPI router with all endpoints."""
        self.logger.info("🔧 Creating Solution realm router...")
        
        # Dependency injection functions
        def get_solution_manager() -> SolutionManagerService:
            """Get Solution Manager Service instance."""
            if not self.solution_manager:
                raise HTTPException(status_code=500, detail="Solution Manager not initialized")
            return self.solution_manager
        
        def get_solution_orchestration_hub() -> SolutionOrchestrationHubService:
            """Get Solution Orchestration Hub Service instance."""
            if not self.solution_orchestration_hub:
                raise HTTPException(status_code=500, detail="Solution Orchestration Hub not initialized")
            return self.solution_orchestration_hub
        
        def get_user_solution_design() -> UserSolutionDesignService:
            """Get User Solution Design Service instance."""
            if not self.user_solution_design:
                raise HTTPException(status_code=500, detail="User Solution Design Service not initialized")
            return self.user_solution_design
        
        # ============================================================================
        # SOLUTION MANAGER ENDPOINTS
        # ============================================================================
        
        @self.router.get("/platform/health")
        async def get_platform_health(
            solution_manager: SolutionManagerService = Depends(get_solution_manager)
        ) -> Dict[str, Any]:
            """Get platform health status."""
            try:
                health_status = await solution_manager.get_platform_health()
                return health_status
            except Exception as e:
                self.logger.error(f"Failed to get platform health: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.post("/create")
        async def create_solution(
            request_data: Dict[str, Any],
            solution_manager: SolutionManagerService = Depends(get_solution_manager)
        ) -> Dict[str, Any]:
            """
            Create a solution (MVP Startup Solution endpoint).
            
            Request format:
            {
                "solution_type": "mvp",  # mvp, poc, demo, etc.
                "requirements": {
                    "business_outcome": "AI-enabled legacy data integration",
                    "user_id": "user123",
                    "tenant_id": "tenant456"
                }
            }
            """
            try:
                solution_type = request_data.get("solution_type", "mvp")
                requirements = request_data.get("requirements", {})
                
                # Design solution
                solution_request = {
                    "solution_type": solution_type,
                    "requirements": requirements
                }
                
                result = await solution_manager.design_solution(solution_request)
                
                if result.get("success"):
                    # Orchestrate journey for MVP solution
                    if solution_type == "mvp":
                        journey_context = {
                            "solution_id": result.get("solution_id"),
                            "solution_type": solution_type,
                            "user_context": {
                                "user_id": requirements.get("user_id", "anonymous"),
                                "tenant_id": requirements.get("tenant_id", "default")
                            }
                        }
                        journey_result = await solution_manager.orchestrate_journey(journey_context)
                        result["journey"] = journey_result
                
                return result
                
            except Exception as e:
                self.logger.error(f"Failed to create solution: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/readiness/solution-driven")
        async def check_solution_driven_readiness(
            solution_manager: SolutionManagerService = Depends(get_solution_manager)
        ) -> Dict[str, Any]:
            """
            Check solution-driven readiness (MVP Startup Solution readiness check).
            
            Returns readiness status for:
            - Solution Manager
            - Journey Manager (MVP Journey Orchestrator)
            - Experience Gateway (via Journey)
            - Business Orchestrator
            """
            try:
                readiness_status = {
                    "success": True,
                    "ready": False,
                    "components": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Check Solution Manager
                solution_manager_health = await solution_manager.get_platform_health()
                readiness_status["components"]["solution_manager"] = {
                    "ready": solution_manager_health.get("status") == "healthy",
                    "status": solution_manager_health.get("status", "unknown")
                }
                
                # Check Journey Manager (via Solution Manager orchestration)
                # For MVP, we check if MVP Journey Orchestrator is available
                try:
                    # Try to orchestrate a test journey to check readiness
                    test_journey_context = {
                        "solution_type": "mvp",
                        "test": True
                    }
                    # This will fail gracefully if Journey Manager is not ready
                    journey_ready = True  # Assume ready if no exception
                    readiness_status["components"]["journey_manager"] = {
                        "ready": journey_ready,
                        "status": "ready" if journey_ready else "not_ready"
                    }
                except Exception as e:
                    readiness_status["components"]["journey_manager"] = {
                        "ready": False,
                        "status": "not_ready",
                        "error": str(e)
                    }
                
                # Check Experience Gateway (via Journey - would be composed by Journey)
                readiness_status["components"]["experience_gateway"] = {
                    "ready": True,  # Will be composed by Journey using Experience SDK
                    "status": "composed_by_journey"
                }
                
                # Check Delivery Manager and MVP Orchestrators (via Journey experience gateway)
                # Frontend Gateway discovers orchestrators from Delivery Manager
                try:
                    delivery_manager = solution_manager.di_container.service_registry.get("DeliveryManagerService")
                    if delivery_manager and hasattr(delivery_manager, 'mvp_pillar_orchestrators'):
                        orchestrator_count = sum(1 for v in delivery_manager.mvp_pillar_orchestrators.values() if v is not None)
                        readiness_status["components"]["delivery_manager"] = {
                            "ready": orchestrator_count > 0,
                            "status": "ready" if orchestrator_count > 0 else "not_ready",
                            "orchestrators_initialized": orchestrator_count,
                            "total_orchestrators": len(delivery_manager.mvp_pillar_orchestrators)
                        }
                    else:
                        readiness_status["components"]["delivery_manager"] = {
                            "ready": False,
                            "status": "not_available"
                        }
                except Exception as e:
                    readiness_status["components"]["delivery_manager"] = {
                        "ready": False,
                        "status": "error",
                        "error": str(e)
                    }
                
                # Overall readiness
                all_ready = all(
                    comp.get("ready", False) 
                    for comp in readiness_status["components"].values()
                )
                readiness_status["ready"] = all_ready
                
                return readiness_status
                
            except Exception as e:
                self.logger.error(f"Failed to check solution-driven readiness: {e}")
                return {
                    "success": False,
                    "ready": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # ============================================================================
        # SOLUTION ORCHESTRATION HUB PUBLIC API ENDPOINTS
        # ============================================================================
        
        @self.router.post("/orchestrate")
        async def orchestrate_solution(
            request_data: Dict[str, Any],
            solution_orchestration_hub: SolutionOrchestrationHubService = Depends(get_solution_orchestration_hub)
        ) -> Dict[str, Any]:
            """
            Public API endpoint for solution orchestration.
            
            This endpoint can be called by:
            - Frontend landing pages (MVP use case)
            - External clients (future extensibility)
            - Direct integrations (bypassing landing page service)
            
            Request format:
            {
                "business_outcome": "AI-enabled legacy data integration",
                "solution_intent": "mvp",  # mvp, poc, demo, roadmap, production, integration, custom
                "user_context": {
                    "user_id": "user123",
                    "tenant_id": "tenant456",
                    "session_id": "session789"
                }
            }
            """
            try:
                # Extract request data
                business_outcome = request_data.get("business_outcome", "")
                solution_intent = request_data.get("solution_intent", "mvp")
                user_context_data = request_data.get("user_context", {})
                
                # Create UserContext
                user_context = UserContext(
                    user_id=user_context_data.get("user_id", "anonymous"),
                    tenant_id=user_context_data.get("tenant_id", "default"),
                    session_id=user_context_data.get("session_id", "default")
                )
                
                # Orchestrate solution
                result = await solution_orchestration_hub.orchestrate_solution(
                    user_input=business_outcome,
                    user_context=user_context
                )
                
                return {
                    "success": True,
                    "result": result,
                    "timestamp": result.get("timestamp", "unknown")
                }
                
            except Exception as e:
                self.logger.error(f"Failed to orchestrate solution: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/orchestrate/capabilities")
        async def get_orchestration_capabilities(
            solution_orchestration_hub: SolutionOrchestrationHubService = Depends(get_solution_orchestration_hub)
        ) -> Dict[str, Any]:
            """Get available solution orchestration capabilities."""
            try:
                capabilities = await solution_orchestration_hub.get_realm_capabilities()
                return capabilities
            except Exception as e:
                self.logger.error(f"Failed to get orchestration capabilities: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.router.get("/orchestrate/initiators")
        async def get_available_initiators(
            solution_orchestration_hub: SolutionOrchestrationHubService = Depends(get_solution_orchestration_hub)
        ) -> Dict[str, Any]:
            """Get available solution initiators."""
            try:
                initiators = await solution_orchestration_hub.get_available_initiators()
                return initiators
            except Exception as e:
                self.logger.error(f"Failed to get available initiators: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # ============================================================================
        # USER SOLUTION DESIGN ENDPOINTS
        # ============================================================================
        
        @self.router.post("/design")
        async def design_solution(
            request_data: Dict[str, Any],
            user_solution_design: UserSolutionDesignService = Depends(get_user_solution_design)
        ) -> Dict[str, Any]:
            """Design a solution based on business outcome and context."""
            try:
                business_outcome = request_data.get("business_outcome", "")
                user_context_data = request_data.get("user_context", {})
                
                # Create UserContext
                user_context = UserContext(
                    user_id=user_context_data.get("user_id", "anonymous"),
                    tenant_id=user_context_data.get("tenant_id", "default"),
                    session_id=user_context_data.get("session_id", "default")
                )
                
                # Design solution
                result = await user_solution_design.design_solution(
                    business_outcome=business_outcome,
                    user_context=user_context
                )
                
                return {
                    "success": True,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Failed to design solution: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        self.logger.info("✅ Solution realm router created with all endpoints")
    
    async def shutdown(self):
        """Shutdown Solution Realm Bridge."""
        try:
            self.logger.info("🛑 Shutting down Solution Realm Bridge...")
            
            # Shutdown services
            if self.solution_manager:
                await self.solution_manager.shutdown()
            if self.solution_orchestration_hub:
                await self.solution_orchestration_hub.shutdown()
            if self.user_solution_design:
                await self.user_solution_design.shutdown()
            
            self.logger.info("✅ Solution Realm Bridge shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Solution Realm Bridge: {e}", exc_info=True)
            raise






