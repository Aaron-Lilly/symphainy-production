"""
Dependency Analyzer Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional


class DependencyAnalyzer:
    """
    Dependency Analyzer following Smart City patterns.
    Analyzes project dependencies and relationships.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("DependencyAnalyzer micro-module initialized")
    
    async def analyze_dependencies(
        self, 
        phases: List[Dict[str, Any]], 
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze project dependencies."""
        try:
            dependencies = []
            
            # Analyze phase dependencies
            phase_dependencies = self._analyze_phase_dependencies(phases)
            dependencies.extend(phase_dependencies)
            
            # Analyze resource dependencies
            resource_dependencies = self._analyze_resource_dependencies(requirements)
            dependencies.extend(resource_dependencies)
            
            # Analyze technical dependencies
            technical_dependencies = self._analyze_technical_dependencies(requirements)
            dependencies.extend(technical_dependencies)
            
            # Analyze external dependencies
            external_dependencies = self._analyze_external_dependencies(requirements)
            dependencies.extend(external_dependencies)
            
            self.logger.info(f"Analyzed {len(dependencies)} dependencies")
            return dependencies
            
        except Exception as e:
            self.logger.error(f"Error analyzing dependencies: {e}")
            return []
    
    def _analyze_phase_dependencies(self, phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze dependencies between phases."""
        dependencies = []
        
        for i, phase in enumerate(phases):
            phase_name = phase.get("name", f"Phase {i+1}")
            
            # Each phase depends on the previous phase
            if i > 0:
                prev_phase = phases[i-1]
                prev_phase_name = prev_phase.get("name", f"Phase {i}")
                
                dependencies.append({
                    "type": "phase_dependency",
                    "from": prev_phase_name,
                    "to": phase_name,
                    "description": f"{phase_name} depends on completion of {prev_phase_name}",
                    "criticality": "High",
                    "impact": "Phase cannot start until previous phase completes"
                })
            
            # Specific phase dependencies
            if "Implementation" in phase_name:
                dependencies.append({
                    "type": "deliverable_dependency",
                    "from": "Design & Planning",
                    "to": phase_name,
                    "description": f"{phase_name} requires design deliverables",
                    "criticality": "High",
                    "impact": "Implementation cannot proceed without design"
                })
            
            if "Testing" in phase_name:
                dependencies.append({
                    "type": "deliverable_dependency",
                    "from": "Implementation",
                    "to": phase_name,
                    "description": f"{phase_name} requires implementation deliverables",
                    "criticality": "High",
                    "impact": "Testing cannot proceed without implementation"
                })
        
        return dependencies
    
    def _analyze_resource_dependencies(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze resource dependencies."""
        dependencies = []
        
        # Team dependencies
        dependencies.append({
            "type": "resource_dependency",
            "from": "HR/Recruitment",
            "to": "Project Team",
            "description": "Project team must be assembled before project start",
            "criticality": "High",
            "impact": "Project cannot start without team"
        })
        
        # Environment dependencies
        dependencies.append({
            "type": "infrastructure_dependency",
            "from": "IT Infrastructure",
            "to": "Development Environment",
            "description": "Development environment must be set up",
            "criticality": "High",
            "impact": "Development cannot proceed without environment"
        })
        
        # Budget dependencies
        dependencies.append({
            "type": "financial_dependency",
            "from": "Budget Approval",
            "to": "Project Execution",
            "description": "Budget must be approved before project execution",
            "criticality": "High",
            "impact": "Project cannot proceed without budget approval"
        })
        
        return dependencies
    
    def _analyze_technical_dependencies(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze technical dependencies."""
        dependencies = []
        
        # Database dependencies
        dependencies.append({
            "type": "technical_dependency",
            "from": "Database Design",
            "to": "Backend Development",
            "description": "Backend development requires database schema",
            "criticality": "High",
            "impact": "Backend cannot be developed without database design"
        })
        
        # API dependencies
        dependencies.append({
            "type": "technical_dependency",
            "from": "API Design",
            "to": "Frontend Development",
            "description": "Frontend development requires API specification",
            "criticality": "High",
            "impact": "Frontend cannot integrate without API design"
        })
        
        # Integration dependencies
        dependencies.append({
            "type": "integration_dependency",
            "from": "External System APIs",
            "to": "System Integration",
            "description": "Integration requires external system availability",
            "criticality": "Medium",
            "impact": "Integration may be delayed if external systems unavailable"
        })
        
        return dependencies
    
    def _analyze_external_dependencies(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze external dependencies."""
        dependencies = []
        
        # Stakeholder dependencies
        dependencies.append({
            "type": "stakeholder_dependency",
            "from": "Stakeholder Availability",
            "to": "Requirements Gathering",
            "description": "Requirements gathering requires stakeholder participation",
            "criticality": "High",
            "impact": "Requirements cannot be gathered without stakeholder input"
        })
        
        # Vendor dependencies
        dependencies.append({
            "type": "vendor_dependency",
            "from": "Third-party Vendors",
            "to": "System Integration",
            "description": "Integration may depend on vendor deliverables",
            "criticality": "Medium",
            "impact": "Integration timeline may be affected by vendor delays"
        })
        
        # Regulatory dependencies
        dependencies.append({
            "type": "regulatory_dependency",
            "from": "Compliance Review",
            "to": "System Deployment",
            "description": "Deployment may require regulatory approval",
            "criticality": "Medium",
            "impact": "Deployment may be delayed pending regulatory approval"
        })
        
        return dependencies
