"""
Timeline Generator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class TimelineGenerator:
    """
    Timeline Generator following Smart City patterns.
    Generates project timelines for POC proposals.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("TimelineGenerator micro-module initialized")
    
    async def generate_timeline(self, preference: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Generate timeline based on preference and constraints."""
        try:
            # Get base timeline from constraints
            timeline_days = constraints.get("timeline_days", 90)
            
            # Adjust based on preference
            if preference == "60_days":
                timeline_days = 60
            elif preference == "120_days":
                timeline_days = 120
            elif preference == "180_days":
                timeline_days = 180
            
            # Calculate phases
            discovery_days = int(timeline_days * 0.15)  # 15% for discovery
            implementation_days = int(timeline_days * 0.60)  # 60% for implementation
            validation_days = int(timeline_days * 0.20)  # 20% for validation
            handoff_days = int(timeline_days * 0.05)  # 5% for handoff
            
            start_date = datetime.now()
            
            phases = [
                {
                    "name": "Discovery & Analysis",
                    "duration": f"{discovery_days} days",
                    "start_day": 1,
                    "end_day": discovery_days,
                    "description": "Requirements gathering, stakeholder interviews, and analysis"
                },
                {
                    "name": "Implementation",
                    "duration": f"{implementation_days} days",
                    "start_day": discovery_days + 1,
                    "end_day": discovery_days + implementation_days,
                    "description": "Core development, integration, and configuration"
                },
                {
                    "name": "Validation & Testing",
                    "duration": f"{validation_days} days",
                    "start_day": discovery_days + implementation_days + 1,
                    "end_day": discovery_days + implementation_days + validation_days,
                    "description": "Testing, validation, and performance optimization"
                },
                {
                    "name": "Handoff & Documentation",
                    "duration": f"{handoff_days} days",
                    "start_day": discovery_days + implementation_days + validation_days + 1,
                    "end_day": timeline_days,
                    "description": "Documentation, training, and knowledge transfer"
                }
            ]
            
            return {
                "total_duration_days": timeline_days,
                "start_date": start_date.isoformat(),
                "end_date": (start_date + timedelta(days=timeline_days)).isoformat(),
                "phases": phases,
                "milestones": self._generate_milestones(phases),
                "preference": preference
            }
            
        except Exception as e:
            self.logger.error(f"Error generating timeline: {e}")
            return {
                "total_duration_days": 90,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
                "phases": [],
                "milestones": [],
                "error": str(e)
            }
    
    def _generate_milestones(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate key milestones from phases."""
        milestones = []
        
        for i, phase in enumerate(phases):
            milestone = {
                "name": f"{phase['name']} Complete",
                "day": phase["end_day"],
                "description": f"Completion of {phase['name'].lower()} phase",
                "deliverables": self._get_phase_deliverables(phase["name"])
            }
            milestones.append(milestone)
        
        return milestones
    
    def _get_phase_deliverables(self, phase_name: str) -> List[str]:
        """Get deliverables for each phase."""
        deliverables_map = {
            "Discovery & Analysis": [
                "Requirements document",
                "Stakeholder analysis",
                "Technical architecture"
            ],
            "Implementation": [
                "Core platform components",
                "Integration modules",
                "Configuration files"
            ],
            "Validation & Testing": [
                "Test results report",
                "Performance metrics",
                "User acceptance testing"
            ],
            "Handoff & Documentation": [
                "User documentation",
                "Technical documentation",
                "Training materials"
            ]
        }
        
        return deliverables_map.get(phase_name, [])
