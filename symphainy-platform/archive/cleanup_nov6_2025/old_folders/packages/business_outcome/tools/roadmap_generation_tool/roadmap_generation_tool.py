"""
Roadmap Generation Tool
Smart City Native + Micro-Modular Architecture
"""

from backend.bases.smart_city.base_mcp import BaseMCP
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
from backend.smart_city_library.architectural_components import traffic_cop, conductor, post_office
from .micro_modules.roadmap_builder import RoadmapBuilder
from .micro_modules.phase_planner import PhasePlanner
from .micro_modules.milestone_generator import MilestoneGenerator
from .micro_modules.dependency_analyzer import DependencyAnalyzer
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class RoadmapGenerationTool(BaseMCP):
    """
    Roadmap Generation Tool for Business Outcome pillar.
    Generates comprehensive roadmaps for POC and project planning.
    """
    
    def __init__(self):
        super().__init__()
        self.tool_name = "roadmap_generation_tool"
        self.pillar = "business_outcome"
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("RoadmapGenerationTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        # Smart City components
        self.traffic_cop = traffic_cop
        self.conductor = conductor
        self.post_office = post_office
        
        self._logger.info("RoadmapGenerationTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.roadmap_builder = RoadmapBuilder(self._logger, self._config)
            self.phase_planner = PhasePlanner(self._logger, self._config)
            self.milestone_generator = MilestoneGenerator(self._logger, self._config)
            self.dependency_analyzer = DependencyAnalyzer(self._logger, self._config)
            
            self._logger.info("RoadmapGenerationTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing RoadmapGenerationTool micro-modules: {e}")
            raise e
    
    async def generate_roadmap(
        self,
        requirements: Dict[str, Any],
        project_type: str = "poc",
        timeline_preference: str = "90_days",
        complexity_level: str = "medium",
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive roadmap.
        
        Args:
            requirements: Project requirements and constraints
            project_type: Type of project (poc, implementation, migration)
            timeline_preference: Preferred timeline (60_days, 90_days, 120_days, 180_days)
            complexity_level: Project complexity (low, medium, high)
            session_token: Session token for Smart City integration
            
        Returns:
            Comprehensive roadmap dictionary
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = self.traffic_cop.validate_session(session_token)
                if not session_valid:
                    return {
                        "error": "Invalid session token",
                        "success": False
                    }
            
            # Generate roadmap using micro-modules
            roadmap = await self.roadmap_builder.build_roadmap(
                requirements, project_type, timeline_preference, complexity_level
            )
            
            # Plan phases
            phases = await self.phase_planner.plan_phases(
                roadmap, project_type, complexity_level
            )
            
            # Generate milestones
            milestones = await self.milestone_generator.generate_milestones(
                phases, project_type, timeline_preference
            )
            
            # Analyze dependencies
            dependencies = await self.dependency_analyzer.analyze_dependencies(
                phases, requirements
            )
            
            # Combine all components
            comprehensive_roadmap = {
                "roadmap": roadmap,
                "phases": phases,
                "milestones": milestones,
                "dependencies": dependencies,
                "project_type": project_type,
                "timeline_preference": timeline_preference,
                "complexity_level": complexity_level,
                "generated_at": datetime.utcnow().isoformat(),
                "success": True
            }
            
            self._logger.info(f"Roadmap generated successfully for {project_type} project")
            return comprehensive_roadmap
            
        except Exception as e:
            self._logger.error(f"Error generating roadmap: {e}")
            return {
                "error": f"Failed to generate roadmap: {str(e)}",
                "success": False,
                "roadmap": "Roadmap generation failed due to technical error",
                "phases": [],
                "milestones": [],
                "dependencies": []
            }
    
    async def update_roadmap(
        self,
        existing_roadmap: Dict[str, Any],
        updates: Dict[str, Any],
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update existing roadmap with new information."""
        try:
            # Validate session if provided
            if session_token:
                session_valid = self.traffic_cop.validate_session(session_token)
                if not session_valid:
                    return {
                        "error": "Invalid session token",
                        "success": False
                    }
            
            # Update roadmap using roadmap builder
            updated_roadmap = await self.roadmap_builder.update_roadmap(
                existing_roadmap, updates
            )
            
            # Re-plan phases if needed
            if "requirements" in updates or "complexity_level" in updates:
                phases = await self.phase_planner.plan_phases(
                    updated_roadmap,
                    existing_roadmap.get("project_type", "poc"),
                    updates.get("complexity_level", existing_roadmap.get("complexity_level", "medium"))
                )
                updated_roadmap["phases"] = phases
            
            # Update milestones
            milestones = await self.milestone_generator.generate_milestones(
                updated_roadmap.get("phases", []),
                existing_roadmap.get("project_type", "poc"),
                existing_roadmap.get("timeline_preference", "90_days")
            )
            updated_roadmap["milestones"] = milestones
            
            # Update dependencies
            dependencies = await self.dependency_analyzer.analyze_dependencies(
                updated_roadmap.get("phases", []),
                updates.get("requirements", existing_roadmap.get("requirements", {}))
            )
            updated_roadmap["dependencies"] = dependencies
            
            updated_roadmap["updated_at"] = datetime.utcnow().isoformat()
            updated_roadmap["success"] = True
            
            self._logger.info("Roadmap updated successfully")
            return updated_roadmap
            
        except Exception as e:
            self._logger.error(f"Error updating roadmap: {e}")
            return {
                "error": f"Failed to update roadmap: {str(e)}",
                "success": False
            }
    
    async def get_roadmap_summary(self, roadmap: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of roadmap."""
        try:
            phases = roadmap.get("phases", [])
            milestones = roadmap.get("milestones", [])
            dependencies = roadmap.get("dependencies", [])
            
            total_duration = sum(phase.get("duration_days", 0) for phase in phases)
            
            return {
                "total_phases": len(phases),
                "total_milestones": len(milestones),
                "total_dependencies": len(dependencies),
                "total_duration_days": total_duration,
                "project_type": roadmap.get("project_type", "unknown"),
                "complexity_level": roadmap.get("complexity_level", "unknown"),
                "generated_at": roadmap.get("generated_at", ""),
                "last_updated": roadmap.get("updated_at", roadmap.get("generated_at", ""))
            }
            
        except Exception as e:
            self._logger.error(f"Error getting roadmap summary: {e}")
            return {"error": str(e)}
