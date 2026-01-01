"""
POC Template Manager Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class POCTemplateManager:
    """
    POC Template Manager following Smart City patterns.
    Handles POC proposal validation and template management.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("POCTemplateManager micro-module initialized")
        
        # Required fields for POC proposal
        self.required_fields = [
            "title", "executive_summary", "business_case", 
            "poc_scope", "timeline", "budget", "success_metrics", 
            "risk_assessment", "next_steps"
        ]
        
        # Optional fields
        self.optional_fields = [
            "assumptions", "stakeholders", "deliverables", 
            "technical_requirements", "success_criteria"
        ]
    
    async def validate_poc_proposal(self, poc_proposal: Dict[str, Any]) -> tuple[bool, List[str], Dict[str, Any]]:
        """Validate POC proposal data."""
        try:
            warnings = []
            validated_data = poc_proposal.copy()
            
            # Check required fields
            missing_fields = []
            for field in self.required_fields:
                if field not in poc_proposal or not poc_proposal[field]:
                    missing_fields.append(field)
            
            if missing_fields:
                return False, [f"Missing required fields: {', '.join(missing_fields)}"], {}
            
            # Validate field content
            if len(poc_proposal.get("title", "")) < 5:
                warnings.append("Title is quite short")
            
            if len(poc_proposal.get("executive_summary", "")) < 50:
                warnings.append("Executive summary is quite short")
            
            if not isinstance(poc_proposal.get("poc_scope", []), list) or len(poc_proposal["poc_scope"]) == 0:
                warnings.append("POC scope should be a non-empty list")
            
            if not isinstance(poc_proposal.get("success_metrics", []), list) or len(poc_proposal["success_metrics"]) == 0:
                warnings.append("Success metrics should be a non-empty list")
            
            if not isinstance(poc_proposal.get("risk_assessment", []), list) or len(poc_proposal["risk_assessment"]) == 0:
                warnings.append("Risk assessment should be a non-empty list")
            
            # Add validation timestamp
            validated_data["validated_at"] = datetime.utcnow().isoformat()
            
            return True, warnings, validated_data
            
        except Exception as e:
            self.logger.error(f"Error validating POC proposal: {e}")
            return False, [f"Validation error: {str(e)}"], {}
    
    async def get_quality_score(self, poc_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality score for POC proposal."""
        try:
            score = 100
            deductions = []
            
            # Check title quality
            title = poc_proposal.get("title", "")
            if len(title) < 10:
                score -= 10
                deductions.append("Title too short")
            elif len(title) > 100:
                score -= 5
                deductions.append("Title too long")
            
            # Check executive summary quality
            exec_summary = poc_proposal.get("executive_summary", "")
            if len(exec_summary) < 100:
                score -= 15
                deductions.append("Executive summary too short")
            elif len(exec_summary) > 500:
                score -= 5
                deductions.append("Executive summary too long")
            
            # Check scope quality
            scope = poc_proposal.get("poc_scope", [])
            if len(scope) < 3:
                score -= 10
                deductions.append("POC scope too limited")
            elif len(scope) > 10:
                score -= 5
                deductions.append("POC scope too broad")
            
            # Check metrics quality
            metrics = poc_proposal.get("success_metrics", [])
            if len(metrics) < 2:
                score -= 10
                deductions.append("Insufficient success metrics")
            
            # Check risk assessment quality
            risks = poc_proposal.get("risk_assessment", [])
            if len(risks) < 2:
                score -= 10
                deductions.append("Insufficient risk assessment")
            
            # Ensure score is not negative
            score = max(0, score)
            
            return {
                "overall_score": score,
                "deductions": deductions,
                "grade": self._get_grade(score),
                "recommendations": self._get_recommendations(score, deductions)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {e}")
            return {"error": str(e)}
    
    async def create_document_outline(self, poc_proposal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create document outline from POC proposal."""
        try:
            outline = [
                {"section": "Executive Summary", "page": 1, "content": "High-level overview"},
                {"section": "Business Case", "page": 2, "content": "Business justification and value proposition"},
                {"section": "POC Scope", "page": 3, "content": "Detailed scope and deliverables"},
                {"section": "Timeline", "page": 4, "content": "Project timeline and milestones"},
                {"section": "Budget", "page": 5, "content": "Cost breakdown and financial details"},
                {"section": "Success Metrics", "page": 6, "content": "Measurable success criteria"},
                {"section": "Risk Assessment", "page": 7, "content": "Identified risks and mitigation strategies"},
                {"section": "Next Steps", "page": 8, "content": "Implementation roadmap and actions"}
            ]
            
            return outline
            
        except Exception as e:
            self.logger.error(f"Error creating document outline: {e}")
            return []
    
    async def get_required_fields(self) -> List[str]:
        """Get list of required fields."""
        return self.required_fields.copy()
    
    async def get_optional_fields(self) -> List[str]:
        """Get list of optional fields."""
        return self.optional_fields.copy()
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _get_recommendations(self, score: int, deductions: List[str]) -> List[str]:
        """Get recommendations based on score and deductions."""
        recommendations = []
        
        if score < 70:
            recommendations.append("Consider expanding content in key sections")
        
        if "Title too short" in deductions:
            recommendations.append("Make the title more descriptive and specific")
        
        if "Executive summary too short" in deductions:
            recommendations.append("Expand the executive summary with more detail")
        
        if "POC scope too limited" in deductions:
            recommendations.append("Add more scope items to make the POC more comprehensive")
        
        if "Insufficient success metrics" in deductions:
            recommendations.append("Define more specific and measurable success metrics")
        
        if "Insufficient risk assessment" in deductions:
            recommendations.append("Identify and assess more potential risks")
        
        if not recommendations:
            recommendations.append("Proposal quality is good, consider minor refinements")
        
        return recommendations

