#!/usr/bin/env python3
"""
Roadmap Generation Service

WHAT: Generates strategic roadmaps from pillar outputs
HOW: Analyzes Content, Insights, and Operations pillar summaries to create phased roadmaps

This service generates strategic roadmaps by analyzing outputs from:
- Content Pillar: Semantic data model complexity
- Insights Pillar: Key findings and recommendations
- Operations Pillar: Artifacts and process optimization opportunities

Roadmaps are flexible and work with partial inputs (doesn't require all pillars).
"""

import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class RoadmapGenerationService(RealmServiceBase):
    """
    Roadmap Generation Service for Solution realm.
    
    Generates strategic roadmaps from pillar outputs:
    - Content: Data migration/transformation phases
    - Insights: Analytics implementation phases
    - Operations: Process optimization phases
    - Combined: Comprehensive roadmap
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Roadmap Generation Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.solution_composer = None
    
    async def initialize(self) -> bool:
        """
        Initialize Roadmap Generation Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "roadmap_generation_service_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # Get Smart City services
            self.librarian = await self.get_librarian_api()
            
            # Get Solution Composer for artifact creation
            self.solution_composer = await self._get_solution_composer()
            
            # Register with Curator
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "roadmap_generation",
                        "protocol": "RoadmapGenerationServiceProtocol",
                        "description": "Generate strategic roadmaps from pillar outputs",
                        "contracts": {
                            "soa_api": {
                                "api_name": "generate_roadmap",
                                "endpoint": "/api/v1/solution/roadmap-generation/generate-roadmap",
                                "method": "POST",
                                "handler": self.generate_roadmap,
                                "metadata": {
                                    "description": "Generate strategic roadmap from pillar outputs",
                                    "parameters": ["pillar_outputs", "business_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "generate_roadmap_tool",
                                "tool_definition": {
                                    "name": "generate_roadmap_tool",
                                    "description": "Generate strategic roadmap from pillar outputs",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "pillar_outputs": {"type": "object"},
                                            "business_context": {"type": "object"}
                                        },
                                        "required": ["pillar_outputs"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.generate_roadmap",
                            "semantic_api": "/api/v1/solution/roadmap-generation/generate-roadmap",
                            "user_journey": "generate_roadmap"
                        }
                    },
                    {
                        "name": "comprehensive_strategic_planning",
                        "protocol": "RoadmapGenerationServiceProtocol",
                        "description": "Create comprehensive strategic plan with roadmap, goals, and performance metrics",
                        "contracts": {
                            "soa_api": {
                                "api_name": "create_comprehensive_strategic_plan",
                                "endpoint": "/api/v1/solution/roadmap-generation/comprehensive-strategic-plan",
                                "method": "POST",
                                "handler": self.create_comprehensive_strategic_plan,
                                "metadata": {
                                    "description": "Create comprehensive strategic plan",
                                    "parameters": ["business_context"]
                                }
                            }
                        }
                    }
                ],
                soa_apis=["generate_roadmap", "create_comprehensive_strategic_plan", "update_roadmap", "visualize_roadmap"],
                mcp_tools=["generate_roadmap_tool"]
            )
            
            # Record health metric
            await self.record_health_metric(
                "roadmap_generation_service_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "roadmap_generation_service_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "roadmap_generation_service_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "roadmap_generation_service_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            return False
    
    async def _get_solution_composer(self):
        """Get Solution Composer Service for artifact creation."""
        try:
            # Try Curator discovery first
            solution_composer = await self.get_enabling_service("SolutionComposerService")
            if solution_composer:
                return solution_composer
            
            # Fallback: Direct import
            from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
            
            service = SolutionComposerService(
                service_name="SolutionComposerService",
                realm_name="solution",
                platform_gateway=self.platform_gateway,
                di_container=self.di_container
            )
            await service.initialize()
            return service
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not get Solution Composer: {e}")
            return None
    
    async def generate_roadmap(
        self,
        roadmap_structure: Dict[str, Any],
        business_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate strategic roadmap from agent-specified structure (Agentic-Forward Pattern).
        
        This service executes the roadmap structure that the agent determined through
        critical reasoning. The agent has already:
        - Analyzed pillar outputs
        - Identified where AI can add value
        - Determined optimal roadmap structure
        - Specified phases, priorities, and approach
        
        Args:
            roadmap_structure: REQUIRED - Agent-specified roadmap structure from critical reasoning
                {
                    "phases": [...],  # Agent-specified phases (required)
                    "priorities": [...],  # Agent-identified priorities
                    "ai_value_opportunities": [...],  # Where AI can add value
                    "strategic_focus": str,  # Agent-determined focus
                    "recommended_approach": str
                }
            business_context: Optional business context (objectives, budget, timeline)
            user_context: Optional user context
        
        Returns:
            Dict with roadmap structure:
            {
                "success": bool,
                "roadmap_id": str,
                "roadmap": {
                    "phases": [...],
                    "milestones": [...],
                    "timeline": {...},
                    "dependencies": [...]
                },
                "visualization": {...}  # For frontend display
            }
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "generate_roadmap_start",
            success=True,
            details={"phases_count": len(roadmap_structure.get("phases", []))}
        )
        
        try:
            self.logger.info("🗺️ Generating strategic roadmap from agent-specified structure")
            
            # Validate agent-specified structure
            if not roadmap_structure.get("phases"):
                return {
                    "success": False,
                    "error": "No phases specified in roadmap structure",
                    "message": "Agent must specify phases in roadmap_structure"
                }
            
            # Use agent-specified phases (agent has already done critical reasoning)
            agent_phases = roadmap_structure.get("phases", [])
            priorities = roadmap_structure.get("priorities", [])
            ai_value_opportunities = roadmap_structure.get("ai_value_opportunities", [])
            
            # Convert agent-specified phases to roadmap format
            phases = []
            milestones = []
            dependencies = []
            current_date = datetime.utcnow()
            cumulative_days = 0
            
            for idx, agent_phase in enumerate(agent_phases):
                phase_id = agent_phase.get("phase_id", f"phase_{idx + 1}")
                phase_name = agent_phase.get("name", f"Phase {idx + 1}")
                phase_duration = agent_phase.get("estimated_duration_days", 30)
                
                phase = {
                    "phase_id": phase_id,
                    "name": phase_name,
                    "description": agent_phase.get("description", f"{phase_name} phase"),
                    "duration_days": phase_duration,
                    "start_date": (current_date + timedelta(days=cumulative_days)).isoformat(),
                    "priority": agent_phase.get("priority", "medium"),
                    "ai_value": agent_phase.get("ai_value", ""),
                    "tasks": agent_phase.get("tasks", [])
                }
                phases.append(phase)
                
                # Create milestone for phase completion
                milestones.append({
                    "milestone_id": f"milestone_{idx + 1}",
                    "name": f"{phase_name} Complete",
                    "phase_id": phase_id,
                    "target_date": (current_date + timedelta(days=cumulative_days + phase_duration)).isoformat(),
                    "status": "planned"
                })
                
                cumulative_days += phase_duration
            
            # Generate timeline from agent-specified phases
            total_duration = sum(phase.get("duration_days", 0) for phase in phases)
            timeline = {
                "start_date": current_date.isoformat(),
                "end_date": (current_date + timedelta(days=total_duration)).isoformat(),
                "total_duration_days": total_duration,
                "phases": len(phases)
            }
            
            # Generate dependencies from agent-specified structure
            for phase in phases:
                for task in phase.get("tasks", []):
                    task_deps = task.get("dependencies", [])
                    if task_deps:
                        dependencies.append({
                            "from": task_deps[0],
                            "to": task["task_id"],
                            "type": "finish_to_start"
                        })
            
            # Generate roadmap ID
            roadmap_id = f"roadmap_{uuid.uuid4().hex[:8]}"
            
            # Create roadmap structure (executing agent's strategic decisions)
            roadmap = {
                "roadmap_id": roadmap_id,
                "name": business_context.get("business_name", "Strategic Roadmap") if business_context else "Strategic Roadmap",
                "description": f"Strategic roadmap with {roadmap_structure.get('strategic_focus', 'AI value maximization')} focus",
                "phases": phases,
                "milestones": milestones,
                "timeline": timeline,
                "dependencies": dependencies,
                "priorities": priorities,
                "ai_value_opportunities": ai_value_opportunities,
                "strategic_focus": roadmap_structure.get("strategic_focus", ""),
                "recommended_approach": roadmap_structure.get("recommended_approach", ""),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Generate visualization data
            visualization = {
                "type": "roadmap_timeline",
                "data": {
                    "phases": [
                        {
                            "id": phase["phase_id"],
                            "name": phase["name"],
                            "start": phase.get("start_date", ""),
                            "duration": phase.get("duration_days", 0),
                            "tasks_count": len(phase.get("tasks", []))
                        }
                        for phase in phases
                    ],
                    "milestones": [
                        {
                            "id": milestone["milestone_id"],
                            "name": milestone["name"],
                            "date": milestone["target_date"]
                        }
                        for milestone in milestones
                    ]
                }
            }
            
            # Record health metric (success)
            await self.record_health_metric("generate_roadmap_success", 1.0, {"roadmap_id": roadmap_id, "phases": len(phases)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_roadmap_complete", success=True, details={"roadmap_id": roadmap_id})
            
            return {
                "success": True,
                "roadmap_id": roadmap_id,
                "roadmap": roadmap,
                "visualization": visualization,
                "message": f"Roadmap generated successfully with {len(phases)} phase(s)"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "generate_roadmap", details={"pillar_outputs_keys": list(pillar_outputs.keys())})
            
            # Record health metric (failure)
            await self.record_health_metric("generate_roadmap_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("generate_roadmap_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Generate roadmap failed: {e}")
            return {
                "success": False,
                "error": "Roadmap generation failed",
                "error_details": str(e)
            }
    
    async def create_comprehensive_strategic_plan(
        self,
        business_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive strategic plan (includes roadmap, goals, performance metrics).
        
        This method is called by BusinessOutcomesOrchestrator.generate_strategic_roadmap().
        
        Args:
            business_context: Business context with pillar_outputs and other options
                {
                    "pillar_outputs": {...},
                    "objectives": [...],
                    "business_name": str,
                    "budget": int,
                    "timeline_days": int,
                    "roadmap_type": str
                }
            user_context: Optional user context
        
        Returns:
            Dict with comprehensive strategic plan:
            {
                "success": bool,
                "plan_id": str,
                "comprehensive_planning": {
                    "roadmap": {...},
                    "goals": [...],
                    "performance_metrics": {...}
                }
            }
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "create_comprehensive_strategic_plan_start",
            success=True
        )
        
        try:
            self.logger.info("📋 Creating comprehensive strategic plan")
            
            pillar_outputs = business_context.get("pillar_outputs", {})
            
            # Generate roadmap
            roadmap_result = await self.generate_roadmap(
                pillar_outputs=pillar_outputs,
                business_context=business_context,
                user_context=user_context
            )
            
            if not roadmap_result.get("success"):
                return roadmap_result
            
            roadmap = roadmap_result.get("roadmap", {})
            roadmap_id = roadmap_result.get("roadmap_id")
            
            # Extract objectives from business context or pillar outputs
            objectives = business_context.get("objectives", [])
            if not objectives:
                objectives = self._extract_objectives_from_pillars(pillar_outputs)
            
            # Generate goals from roadmap phases
            goals = []
            for phase in roadmap.get("phases", []):
                goals.append({
                    "goal_id": f"goal_{phase['phase_id']}",
                    "name": phase["name"],
                    "description": phase["description"],
                    "target_date": phase.get("start_date", ""),
                    "status": "planned",
                    "phase_id": phase["phase_id"]
                })
            
            # Generate performance metrics
            performance_metrics = {
                "total_phases": len(roadmap.get("phases", [])),
                "total_milestones": len(roadmap.get("milestones", [])),
                "total_tasks": sum(len(phase.get("tasks", [])) for phase in roadmap.get("phases", [])),
                "estimated_duration_days": roadmap.get("timeline", {}).get("total_duration_days", 0),
                "pillar_coverage": roadmap.get("pillar_sources", [])
            }
            
            # Generate plan ID
            plan_id = f"strategic_plan_{uuid.uuid4().hex[:8]}"
            
            comprehensive_plan = {
                "plan_id": plan_id,
                "roadmap": roadmap,
                "goals": goals,
                "performance_metrics": performance_metrics,
                "objectives": objectives,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("create_comprehensive_strategic_plan_success", 1.0, {"plan_id": plan_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_comprehensive_strategic_plan_complete", success=True, details={"plan_id": plan_id})
            
            return {
                "success": True,
                "plan_id": plan_id,
                "comprehensive_planning": comprehensive_plan,
                "message": "Comprehensive strategic plan created successfully"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "create_comprehensive_strategic_plan")
            
            # Record health metric (failure)
            await self.record_health_metric("create_comprehensive_strategic_plan_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("create_comprehensive_strategic_plan_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Create comprehensive strategic plan failed: {e}")
            return {
                "success": False,
                "error": "Strategic plan creation failed",
                "error_details": str(e)
            }
    
    def _extract_objectives_from_pillars(self, pillar_outputs: Dict[str, Any]) -> List[str]:
        """Extract objectives from pillar outputs."""
        objectives = []
        
        # Content pillar objectives
        content_summary = pillar_outputs.get("content_pillar", {})
        if content_summary.get("success"):
            semantic_model = content_summary.get("semantic_data_model", {})
            if semantic_model.get("structured_files", {}).get("count", 0) > 0:
                objectives.append("Establish semantic data model for structured data")
            if semantic_model.get("unstructured_files", {}).get("count", 0) > 0:
                objectives.append("Create semantic graph for unstructured data")
        
        # Insights pillar objectives
        insights_summary = pillar_outputs.get("insights_pillar", {})
        if insights_summary.get("success"):
            objectives.append("Implement analytics based on insights findings")
        
        # Operations pillar objectives
        operations_summary = pillar_outputs.get("operations_pillar", {})
        if operations_summary.get("success"):
            artifacts = operations_summary.get("artifacts", {})
            if artifacts.get("workflows") or artifacts.get("sops"):
                objectives.append("Optimize processes using workflows and SOPs")
            if artifacts.get("coexistence_blueprints"):
                objectives.append("Implement coexistence blueprints")
        
        return objectives if objectives else ["Deliver strategic value through platform implementation"]
    
    async def update_roadmap(
        self,
        roadmap_id: str,
        updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update roadmap with new information.
        
        Args:
            roadmap_id: Roadmap identifier
            updates: Updates to apply
            user_context: Optional user context
        
        Returns:
            Updated roadmap
        """
        # TODO: Implement roadmap update logic
        return {
            "success": False,
            "error": "Not yet implemented",
            "message": "Roadmap update functionality coming soon"
        }
    
    async def visualize_roadmap(
        self,
        roadmap_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate roadmap visualization.
        
        Args:
            roadmap_id: Roadmap identifier
            user_context: Optional user context
        
        Returns:
            Visualization data
        """
        # TODO: Implement roadmap visualization logic
        return {
            "success": False,
            "error": "Not yet implemented",
            "message": "Roadmap visualization functionality coming soon"
        }
    
    async def track_progress(
        self,
        roadmap_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track roadmap progress.
        
        Args:
            roadmap_id: Roadmap identifier
            user_context: Optional user context
        
        Returns:
            Progress tracking data
        """
        # TODO: Implement progress tracking logic
        return {
            "success": False,
            "error": "Not yet implemented",
            "message": "Progress tracking functionality coming soon"
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities."""
        return {
            "service_name": self.service_name,
            "service_type": "roadmap_generation",
            "capabilities": [
                "generate_roadmap",
                "create_comprehensive_strategic_plan",
                "update_roadmap",
                "visualize_roadmap",
                "track_progress"
            ],
            "realm": self.realm_name
        }

