"""
Phase Planner Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional


class PhasePlanner:
    """
    Phase Planner following Smart City patterns.
    Plans project phases and activities.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("PhasePlanner micro-module initialized")
    
    async def plan_phases(
        self, 
        roadmap: Dict[str, Any], 
        project_type: str, 
        complexity_level: str
    ) -> List[Dict[str, Any]]:
        """Plan project phases."""
        try:
            timeline_days = roadmap.get("timeline_days", 90)
            
            if project_type == "poc":
                phases = self._plan_poc_phases(timeline_days, complexity_level)
            elif project_type == "implementation":
                phases = self._plan_implementation_phases(timeline_days, complexity_level)
            elif project_type == "migration":
                phases = self._plan_migration_phases(timeline_days, complexity_level)
            else:
                phases = self._plan_poc_phases(timeline_days, complexity_level)
            
            self.logger.info(f"Planned {len(phases)} phases for {project_type} project")
            return phases
            
        except Exception as e:
            self.logger.error(f"Error planning phases: {e}")
            return []
    
    def _plan_poc_phases(self, timeline_days: int, complexity_level: str) -> List[Dict[str, Any]]:
        """Plan POC phases."""
        phases = [
            {
                "name": "Discovery & Analysis",
                "duration_days": int(timeline_days * 0.20),
                "description": "Requirements gathering, stakeholder interviews, and analysis",
                "activities": [
                    "Stakeholder interviews",
                    "Requirements documentation",
                    "Technical architecture design",
                    "Risk assessment"
                ],
                "deliverables": [
                    "Requirements document",
                    "Technical architecture",
                    "Risk register"
                ]
            },
            {
                "name": "Design & Planning",
                "duration_days": int(timeline_days * 0.15),
                "description": "Solution design and detailed planning",
                "activities": [
                    "Solution design",
                    "Database design",
                    "API design",
                    "Test planning"
                ],
                "deliverables": [
                    "Solution design document",
                    "Database schema",
                    "API specification",
                    "Test plan"
                ]
            },
            {
                "name": "Implementation",
                "duration_days": int(timeline_days * 0.45),
                "description": "Core development and integration",
                "activities": [
                    "Backend development",
                    "Frontend development",
                    "API integration",
                    "Database implementation"
                ],
                "deliverables": [
                    "Backend application",
                    "Frontend application",
                    "API endpoints",
                    "Database"
                ]
            },
            {
                "name": "Testing & Validation",
                "duration_days": int(timeline_days * 0.15),
                "description": "Testing and validation of POC",
                "activities": [
                    "Unit testing",
                    "Integration testing",
                    "User acceptance testing",
                    "Performance testing"
                ],
                "deliverables": [
                    "Test results",
                    "Performance metrics",
                    "User feedback"
                ]
            },
            {
                "name": "Documentation & Handoff",
                "duration_days": int(timeline_days * 0.05),
                "description": "Documentation and knowledge transfer",
                "activities": [
                    "Technical documentation",
                    "User documentation",
                    "Knowledge transfer",
                    "Project closure"
                ],
                "deliverables": [
                    "Technical documentation",
                    "User guide",
                    "Handoff materials"
                ]
            }
        ]
        
        return phases
    
    def _plan_implementation_phases(self, timeline_days: int, complexity_level: str) -> List[Dict[str, Any]]:
        """Plan implementation phases."""
        phases = [
            {
                "name": "Project Initiation",
                "duration_days": int(timeline_days * 0.10),
                "description": "Project setup and team formation",
                "activities": [
                    "Project kickoff",
                    "Team formation",
                    "Environment setup",
                    "Tool configuration"
                ],
                "deliverables": [
                    "Project charter",
                    "Team structure",
                    "Development environment"
                ]
            },
            {
                "name": "Requirements & Design",
                "duration_days": int(timeline_days * 0.20),
                "description": "Detailed requirements and design",
                "activities": [
                    "Detailed requirements",
                    "System design",
                    "Database design",
                    "Security design"
                ],
                "deliverables": [
                    "Detailed requirements",
                    "System architecture",
                    "Security plan"
                ]
            },
            {
                "name": "Development",
                "duration_days": int(timeline_days * 0.50),
                "description": "Core development work",
                "activities": [
                    "Backend development",
                    "Frontend development",
                    "Integration development",
                    "Database development"
                ],
                "deliverables": [
                    "Complete application",
                    "Integration modules",
                    "Database implementation"
                ]
            },
            {
                "name": "Testing & Quality Assurance",
                "duration_days": int(timeline_days * 0.15),
                "description": "Comprehensive testing",
                "activities": [
                    "Unit testing",
                    "Integration testing",
                    "System testing",
                    "User acceptance testing"
                ],
                "deliverables": [
                    "Test results",
                    "Quality metrics",
                    "User acceptance"
                ]
            },
            {
                "name": "Deployment & Go-Live",
                "duration_days": int(timeline_days * 0.05),
                "description": "Production deployment",
                "activities": [
                    "Production deployment",
                    "Go-live support",
                    "Monitoring setup",
                    "Documentation"
                ],
                "deliverables": [
                    "Production system",
                    "Monitoring dashboard",
                    "Deployment documentation"
                ]
            }
        ]
        
        return phases
    
    def _plan_migration_phases(self, timeline_days: int, complexity_level: str) -> List[Dict[str, Any]]:
        """Plan migration phases."""
        phases = [
            {
                "name": "Assessment & Planning",
                "duration_days": int(timeline_days * 0.25),
                "description": "Current state assessment and migration planning",
                "activities": [
                    "Current system analysis",
                    "Data mapping",
                    "Migration strategy",
                    "Risk assessment"
                ],
                "deliverables": [
                    "Current state analysis",
                    "Data mapping document",
                    "Migration strategy"
                ]
            },
            {
                "name": "Preparation & Setup",
                "duration_days": int(timeline_days * 0.20),
                "description": "Migration environment and tool setup",
                "activities": [
                    "Target environment setup",
                    "Migration tools setup",
                    "Data validation setup",
                    "Testing environment"
                ],
                "deliverables": [
                    "Target environment",
                    "Migration tools",
                    "Validation framework"
                ]
            },
            {
                "name": "Migration Execution",
                "duration_days": int(timeline_days * 0.40),
                "description": "Actual data and system migration",
                "activities": [
                    "Data migration",
                    "System migration",
                    "Configuration migration",
                    "Integration migration"
                ],
                "deliverables": [
                    "Migrated data",
                    "Migrated systems",
                    "Migration reports"
                ]
            },
            {
                "name": "Validation & Cutover",
                "duration_days": int(timeline_days * 0.15),
                "description": "Validation and production cutover",
                "activities": [
                    "Data validation",
                    "System validation",
                    "User acceptance testing",
                    "Production cutover"
                ],
                "deliverables": [
                    "Validation results",
                    "Production system",
                    "Cutover documentation"
                ]
            }
        ]
        
        return phases
