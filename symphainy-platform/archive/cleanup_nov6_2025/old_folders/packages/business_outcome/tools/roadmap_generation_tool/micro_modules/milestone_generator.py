"""
Milestone Generator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class MilestoneGenerator:
    """
    Milestone Generator following Smart City patterns.
    Generates project milestones and checkpoints.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("MilestoneGenerator micro-module initialized")
    
    async def generate_milestones(
        self, 
        phases: List[Dict[str, Any]], 
        project_type: str, 
        timeline_preference: str
    ) -> List[Dict[str, Any]]:
        """Generate milestones from phases."""
        try:
            milestones = []
            current_day = 1
            
            for i, phase in enumerate(phases):
                phase_duration = phase.get("duration_days", 0)
                phase_name = phase.get("name", f"Phase {i+1}")
                
                # Create phase completion milestone
                milestone = {
                    "name": f"{phase_name} Complete",
                    "day": current_day + phase_duration - 1,
                    "phase": phase_name,
                    "description": f"Completion of {phase_name.lower()} phase",
                    "deliverables": phase.get("deliverables", []),
                    "success_criteria": self._get_success_criteria(phase_name, project_type),
                    "dependencies": self._get_milestone_dependencies(phase_name, i),
                    "risk_level": self._assess_milestone_risk(phase_name, project_type)
                }
                
                milestones.append(milestone)
                
                # Add mid-phase checkpoints for longer phases
                if phase_duration > 14:  # More than 2 weeks
                    checkpoint_day = current_day + (phase_duration // 2)
                    checkpoint = {
                        "name": f"{phase_name} Checkpoint",
                        "day": checkpoint_day,
                        "phase": phase_name,
                        "description": f"Mid-phase checkpoint for {phase_name.lower()}",
                        "deliverables": self._get_checkpoint_deliverables(phase_name),
                        "success_criteria": self._get_checkpoint_criteria(phase_name),
                        "dependencies": [],
                        "risk_level": "Low"
                    }
                    milestones.append(checkpoint)
                
                current_day += phase_duration
            
            # Add project-level milestones
            project_milestones = self._add_project_milestones(phases, project_type)
            milestones.extend(project_milestones)
            
            # Sort by day
            milestones.sort(key=lambda x: x["day"])
            
            self.logger.info(f"Generated {len(milestones)} milestones for {project_type} project")
            return milestones
            
        except Exception as e:
            self.logger.error(f"Error generating milestones: {e}")
            return []
    
    def _get_success_criteria(self, phase_name: str, project_type: str) -> List[str]:
        """Get success criteria for phase."""
        criteria_map = {
            "Discovery & Analysis": [
                "All stakeholders interviewed",
                "Requirements document approved",
                "Technical architecture validated"
            ],
            "Design & Planning": [
                "Solution design approved",
                "Database schema finalized",
                "API specification complete"
            ],
            "Implementation": [
                "All planned features implemented",
                "Code review completed",
                "Unit tests passing"
            ],
            "Testing & Validation": [
                "All tests passing",
                "Performance requirements met",
                "User acceptance achieved"
            ],
            "Documentation & Handoff": [
                "Documentation complete",
                "Knowledge transfer completed",
                "Project closure approved"
            ]
        }
        
        return criteria_map.get(phase_name, ["Phase deliverables completed"])
    
    def _get_milestone_dependencies(self, phase_name: str, phase_index: int) -> List[str]:
        """Get milestone dependencies."""
        if phase_index == 0:
            return []
        
        # Simple dependency: previous phase must be complete
        return [f"Phase {phase_index} Complete"]
    
    def _assess_milestone_risk(self, phase_name: str, project_type: str) -> str:
        """Assess milestone risk level."""
        high_risk_phases = ["Implementation", "Migration Execution", "Deployment & Go-Live"]
        medium_risk_phases = ["Testing & Validation", "Validation & Cutover"]
        
        if phase_name in high_risk_phases:
            return "High"
        elif phase_name in medium_risk_phases:
            return "Medium"
        else:
            return "Low"
    
    def _get_checkpoint_deliverables(self, phase_name: str) -> List[str]:
        """Get checkpoint deliverables."""
        checkpoint_map = {
            "Implementation": [
                "50% of features implemented",
                "Core functionality working",
                "Integration tests passing"
            ],
            "Development": [
                "Backend core complete",
                "Frontend framework ready",
                "Database structure implemented"
            ]
        }
        
        return checkpoint_map.get(phase_name, ["Phase progress validated"])
    
    def _get_checkpoint_criteria(self, phase_name: str) -> List[str]:
        """Get checkpoint success criteria."""
        return [
            "On track for phase completion",
            "No major blockers identified",
            "Quality standards maintained"
        ]
    
    def _add_project_milestones(self, phases: List[Dict[str, Any]], project_type: str) -> List[Dict[str, Any]]:
        """Add project-level milestones."""
        project_milestones = []
        
        # Project kickoff milestone
        project_milestones.append({
            "name": "Project Kickoff",
            "day": 1,
            "phase": "Project Initiation",
            "description": "Project officially started",
            "deliverables": ["Project charter", "Team assembled"],
            "success_criteria": ["Stakeholder alignment", "Resources allocated"],
            "dependencies": [],
            "risk_level": "Low"
        })
        
        # Mid-project review milestone
        total_days = sum(phase.get("duration_days", 0) for phase in phases)
        mid_project_day = total_days // 2
        
        project_milestones.append({
            "name": "Mid-Project Review",
            "day": mid_project_day,
            "phase": "Project Management",
            "description": "Mid-project status review and adjustment",
            "deliverables": ["Progress report", "Risk assessment update"],
            "success_criteria": ["On track for completion", "Issues identified and addressed"],
            "dependencies": ["Project Kickoff"],
            "risk_level": "Medium"
        })
        
        # Project completion milestone
        project_milestones.append({
            "name": "Project Completion",
            "day": total_days,
            "phase": "Project Closure",
            "description": "Project successfully completed",
            "deliverables": ["Final deliverables", "Project closure report"],
            "success_criteria": ["All objectives met", "Stakeholder satisfaction"],
            "dependencies": [f"{phases[-1]['name']} Complete"] if phases else [],
            "risk_level": "Low"
        })
        
        return project_milestones
