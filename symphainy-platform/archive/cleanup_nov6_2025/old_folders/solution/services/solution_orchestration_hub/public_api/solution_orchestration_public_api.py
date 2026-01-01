#!/usr/bin/env python3
"""
Solution Orchestration Public API

Public API for the Solution Orchestration Hub that can be called directly by:
- Frontend landing pages (MVP use case)
- External clients (future extensibility)
- Direct integrations (bypassing landing page services)

WHAT (Solution Role): I provide public API access to solution orchestration
HOW (Public API): I expose REST endpoints for direct solution orchestration
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from enum import Enum

from utilities import UserContext


class SolutionIntentRequest(BaseModel):
    """Request model for solution orchestration."""
    solution_intent: str = Field(..., description="Solution intent (mvp, poc, roadmap, production, integration, demo, custom)")
    business_outcome: str = Field(..., description="Business outcome description")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User context information")
    solution_context: Optional[Dict[str, Any]] = Field(None, description="Additional solution context")


class SolutionOrchestrationResponse(BaseModel):
    """Response model for solution orchestration."""
    success: bool
    solution_id: Optional[str] = None
    intent_analysis: Optional[Dict[str, Any]] = None
    solution_scope: Optional[str] = None
    solution_initiator: Optional[str] = None
    orchestration_result: Optional[Dict[str, Any]] = None
    next_steps: Optional[List[str]] = None
    error: Optional[str] = None
    timestamp: str


class SolutionStatusResponse(BaseModel):
    """Response model for solution status."""
    success: bool
    solution_id: str
    status: str
    progress: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str


class SolutionOrchestrationPublicAPI:
    """
    Solution Orchestration Public API
    
    Public API that exposes solution orchestration capabilities as REST endpoints.
    Can be called directly by frontends, external clients, and integrations.
    """
    
    def __init__(self, solution_orchestration_hub_service=None):
        """Initialize Solution Orchestration Public API."""
        self.solution_orchestration_hub = solution_orchestration_hub_service
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # API state
        self.active_solutions = {}
        self.api_version = "1.0.0"
        
        self.logger.info("🌐 Solution Orchestration Public API initialized")
    
    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI application with solution orchestration endpoints."""
        app = FastAPI(
            title="Solution Orchestration Public API",
            description="Public API for solution orchestration and discovery",
            version=self.api_version,
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add CORS middleware for frontend integration
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register endpoints
        self._register_endpoints(app)
        
        return app
    
    def _register_endpoints(self, app: FastAPI):
        """Register API endpoints."""
        
        @app.post("/api/v1/solutions/orchestrate", response_model=SolutionOrchestrationResponse)
        async def orchestrate_solution(request: SolutionIntentRequest):
            """Orchestrate a solution based on intent and business outcome."""
            try:
                self.logger.info(f"🎯 Public API: Orchestrating solution for intent: {request.solution_intent}")
                
                # Create user context
                user_context = UserContext(
                    user_id=request.user_context.get("user_id", "anonymous") if request.user_context else "anonymous",
                    tenant_id=request.user_context.get("tenant_id", "default") if request.user_context else "default",
                    session_id=request.user_context.get("session_id", f"api_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}") if request.user_context else f"api_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                )
                
                # Orchestrate solution using the hub
                if not self.solution_orchestration_hub:
                    raise HTTPException(status_code=503, detail="Solution Orchestration Hub not available")
                
                result = await self.solution_orchestration_hub.orchestrate_solution(
                    user_input=request.business_outcome,
                    user_context=user_context
                )
                
                if result.get("success", False):
                    # Generate solution ID
                    solution_id = f"sol_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_context.session_id[:8]}"
                    
                    # Store active solution
                    self.active_solutions[solution_id] = {
                        "solution_id": solution_id,
                        "intent": request.solution_intent,
                        "business_outcome": request.business_outcome,
                        "user_context": user_context,
                        "orchestration_result": result,
                        "status": "orchestrated",
                        "created_at": datetime.utcnow()
                    }
                    
                    # Generate next steps
                    next_steps = await self._generate_next_steps(result, request.solution_intent)
                    
                    return SolutionOrchestrationResponse(
                        success=True,
                        solution_id=solution_id,
                        intent_analysis=result.get("intent_analysis"),
                        solution_scope=result.get("solution_scope"),
                        solution_initiator=result.get("solution_initiator"),
                        orchestration_result=result.get("orchestration_result"),
                        next_steps=next_steps,
                        timestamp=datetime.utcnow().isoformat()
                    )
                else:
                    return SolutionOrchestrationResponse(
                        success=False,
                        error=result.get("error", "Solution orchestration failed"),
                        timestamp=datetime.utcnow().isoformat()
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to orchestrate solution: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/v1/solutions/{solution_id}/status", response_model=SolutionStatusResponse)
        async def get_solution_status(solution_id: str):
            """Get the status of a solution."""
            try:
                if solution_id not in self.active_solutions:
                    raise HTTPException(status_code=404, detail="Solution not found")
                
                solution = self.active_solutions[solution_id]
                
                return SolutionStatusResponse(
                    success=True,
                    solution_id=solution_id,
                    status=solution["status"],
                    progress=solution.get("orchestration_result", {}),
                    timestamp=datetime.utcnow().isoformat()
                )
                
            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"Failed to get solution status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/v1/solutions/intents")
        async def get_available_intents():
            """Get available solution intents."""
            return {
                "success": True,
                "intents": [
                    {
                        "intent": "mvp",
                        "description": "Minimum Viable Product - Basic implementation for validation",
                        "scope": "mvp_implementation"
                    },
                    {
                        "intent": "poc",
                        "description": "Proof of Concept - Validate specific concept or idea",
                        "scope": "proof_of_concept"
                    },
                    {
                        "intent": "roadmap",
                        "description": "Strategic Roadmap - Long-term evolution plan",
                        "scope": "strategic_roadmap"
                    },
                    {
                        "intent": "production",
                        "description": "Production Ready - Full production deployment",
                        "scope": "production_ready"
                    },
                    {
                        "intent": "integration",
                        "description": "Integration - Connect with existing systems",
                        "scope": "enterprise_scale"
                    },
                    {
                        "intent": "demo",
                        "description": "Demonstration - Show capabilities and examples",
                        "scope": "quick_demo"
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @app.get("/api/v1/solutions/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "success": True,
                "status": "healthy",
                "active_solutions": len(self.active_solutions),
                "api_version": self.api_version,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @app.get("/api/v1/solutions")
        async def list_solutions():
            """List active solutions."""
            return {
                "success": True,
                "solutions": [
                    {
                        "solution_id": solution_id,
                        "intent": solution["intent"],
                        "status": solution["status"],
                        "created_at": solution["created_at"].isoformat()
                    }
                    for solution_id, solution in self.active_solutions.items()
                ],
                "count": len(self.active_solutions),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _generate_next_steps(self, orchestration_result: Dict[str, Any], solution_intent: str) -> List[str]:
        """Generate next steps based on orchestration result."""
        if orchestration_result.get("success", False):
            if solution_intent == "mvp":
                return [
                    "MVP solution orchestrated successfully",
                    "Proceed to journey orchestration",
                    "Begin MVP implementation",
                    "Monitor progress and gather feedback"
                ]
            elif solution_intent == "poc":
                return [
                    "POC solution orchestrated successfully",
                    "Proceed to POC development",
                    "Validate concept and gather insights",
                    "Prepare for production scaling"
                ]
            elif solution_intent == "demo":
                return [
                    "Demo solution orchestrated successfully",
                    "Proceed to demo development",
                    "Prepare demonstration materials",
                    "Schedule stakeholder presentations"
                ]
            else:
                return [
                    "Solution orchestrated successfully",
                    "Proceed to implementation",
                    "Monitor progress and adjust as needed",
                    "Prepare for next phase"
                ]
        else:
            return [
                "Review solution requirements",
                "Contact support for assistance",
                "Try alternative solution approaches",
                "Provide additional context if needed"
            ]
    
    def set_solution_orchestration_hub(self, solution_orchestration_hub_service):
        """Set the solution orchestration hub service."""
        self.solution_orchestration_hub = solution_orchestration_hub_service
        self.logger.info("✅ Solution Orchestration Hub connected to Public API")
    
    async def get_api_capabilities(self) -> Dict[str, Any]:
        """Get API capabilities."""
        return {
            "api_name": "Solution Orchestration Public API",
            "version": self.api_version,
            "endpoints": [
                "POST /api/v1/solutions/orchestrate",
                "GET /api/v1/solutions/{solution_id}/status",
                "GET /api/v1/solutions/intents",
                "GET /api/v1/solutions/health",
                "GET /api/v1/solutions"
            ],
            "active_solutions": len(self.active_solutions),
            "capabilities": [
                "solution_orchestration",
                "intent_analysis",
                "status_tracking",
                "health_monitoring"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }


# Create public API instance
solution_orchestration_public_api = SolutionOrchestrationPublicAPI()






