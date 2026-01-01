"""
Roadmap Builder Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class RoadmapBuilder:
    """
    Roadmap Builder following Smart City patterns.
    Builds comprehensive project roadmaps.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("RoadmapBuilder micro-module initialized")
    
    async def build_roadmap(
        self, 
        requirements: Dict[str, Any], 
        project_type: str, 
        timeline_preference: str, 
        complexity_level: str
    ) -> Dict[str, Any]:
        """Build comprehensive roadmap."""
        try:
            # Calculate timeline based on preference
            timeline_days = self._get_timeline_days(timeline_preference)
            
            # Adjust for complexity
            complexity_multiplier = self._get_complexity_multiplier(complexity_level)
            adjusted_timeline = int(timeline_days * complexity_multiplier)
            
            # Generate roadmap structure
            roadmap = {
                "project_name": requirements.get("project_name", "SymphAIny Platform Project"),
                "project_type": project_type,
                "timeline_days": adjusted_timeline,
                "complexity_level": complexity_level,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=adjusted_timeline)).isoformat(),
                "objectives": requirements.get("objectives", []),
                "constraints": requirements.get("constraints", []),
                "success_criteria": requirements.get("success_criteria", []),
                "stakeholders": requirements.get("stakeholders", []),
                "resources": self._estimate_resources(project_type, complexity_level, adjusted_timeline),
                "risks": self._identify_risks(project_type, complexity_level, requirements),
                "assumptions": self._identify_assumptions(project_type, requirements)
            }
            
            self.logger.info(f"Roadmap built for {project_type} project with {adjusted_timeline} days timeline")
            return roadmap
            
        except Exception as e:
            self.logger.error(f"Error building roadmap: {e}")
            return {
                "project_name": "Roadmap Generation Failed",
                "project_type": project_type,
                "timeline_days": 90,
                "error": str(e)
            }
    
    async def update_roadmap(
        self, 
        existing_roadmap: Dict[str, Any], 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing roadmap with new information."""
        try:
            updated_roadmap = existing_roadmap.copy()
            
            # Update fields that are provided
            for key, value in updates.items():
                if key in updated_roadmap:
                    updated_roadmap[key] = value
            
            # Recalculate timeline if complexity changed
            if "complexity_level" in updates:
                complexity_multiplier = self._get_complexity_multiplier(updates["complexity_level"])
                original_timeline = updated_roadmap.get("timeline_days", 90)
                updated_timeline = int(original_timeline * complexity_multiplier)
                updated_roadmap["timeline_days"] = updated_timeline
                
                # Update end date
                start_date = datetime.fromisoformat(updated_roadmap.get("start_date", datetime.now().isoformat()))
                updated_roadmap["end_date"] = (start_date + timedelta(days=updated_timeline)).isoformat()
            
            # Update resources if timeline or complexity changed
            if "timeline_days" in updated_roadmap or "complexity_level" in updated_roadmap:
                updated_roadmap["resources"] = self._estimate_resources(
                    updated_roadmap.get("project_type", "poc"),
                    updated_roadmap.get("complexity_level", "medium"),
                    updated_roadmap.get("timeline_days", 90)
                )
            
            updated_roadmap["last_updated"] = datetime.utcnow().isoformat()
            
            self.logger.info("Roadmap updated successfully")
            return updated_roadmap
            
        except Exception as e:
            self.logger.error(f"Error updating roadmap: {e}")
            return existing_roadmap
    
    def _get_timeline_days(self, timeline_preference: str) -> int:
        """Get timeline days from preference."""
        timeline_map = {
            "60_days": 60,
            "90_days": 90,
            "120_days": 120,
            "180_days": 180,
            "custom": 90
        }
        return timeline_map.get(timeline_preference, 90)
    
    def _get_complexity_multiplier(self, complexity_level: str) -> float:
        """Get complexity multiplier."""
        complexity_map = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.3
        }
        return complexity_map.get(complexity_level, 1.0)
    
    def _estimate_resources(self, project_type: str, complexity_level: str, timeline_days: int) -> Dict[str, Any]:
        """Estimate required resources."""
        base_resources = {
            "poc": {"team_size": 3, "hours_per_week": 40},
            "implementation": {"team_size": 5, "hours_per_week": 40},
            "migration": {"team_size": 4, "hours_per_week": 40}
        }
        
        complexity_multiplier = self._get_complexity_multiplier(complexity_level)
        
        base = base_resources.get(project_type, base_resources["poc"])
        
        return {
            "team_size": int(base["team_size"] * complexity_multiplier),
            "hours_per_week": base["hours_per_week"],
            "total_hours": int(base["team_size"] * base["hours_per_week"] * (timeline_days / 7) * complexity_multiplier),
            "roles": self._get_required_roles(project_type, complexity_level)
        }
    
    def _get_required_roles(self, project_type: str, complexity_level: str) -> List[str]:
        """Get required roles for project."""
        base_roles = {
            "poc": ["Project Manager", "Technical Lead", "Developer"],
            "implementation": ["Project Manager", "Technical Lead", "Senior Developer", "QA Engineer", "DevOps Engineer"],
            "migration": ["Project Manager", "Technical Lead", "Data Engineer", "QA Engineer"]
        }
        
        roles = base_roles.get(project_type, base_roles["poc"])
        
        if complexity_level == "high":
            roles.extend(["Solution Architect", "Business Analyst"])
        
        return roles
    
    def _identify_risks(self, project_type: str, complexity_level: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify project risks."""
        risks = [
            {
                "risk": "Timeline delays due to scope changes",
                "impact": "Medium",
                "probability": "Medium",
                "mitigation": "Regular scope reviews and change control"
            },
            {
                "risk": "Resource availability issues",
                "impact": "High",
                "probability": "Low",
                "mitigation": "Resource planning and backup team members"
            }
        ]
        
        if complexity_level == "high":
            risks.append({
                "risk": "Technical complexity causing delays",
                "impact": "High",
                "probability": "Medium",
                "mitigation": "Proof of concept and technical spikes"
            })
        
        if project_type == "migration":
            risks.append({
                "risk": "Data migration issues",
                "impact": "High",
                "probability": "Medium",
                "mitigation": "Comprehensive testing and rollback plan"
            })
        
        return risks
    
    def _identify_assumptions(self, project_type: str, requirements: Dict[str, Any]) -> List[str]:
        """Identify project assumptions."""
        assumptions = [
            "Stakeholder availability for requirements gathering",
            "Technical infrastructure meets project needs",
            "Budget approval process completed on time"
        ]
        
        if project_type == "poc":
            assumptions.append("POC environment available from project start")
        
        if project_type == "migration":
            assumptions.append("Source system data quality is acceptable")
        
        return assumptions
