"""
POC Validation Service Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional


class POCValidationService:
    """
    POC Validation Service following Smart City patterns.
    Validates POC proposals against business rules.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("POCValidationService micro-module initialized")
    
    async def validate_poc_proposal(self, poc_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Validate POC proposal against business rules."""
        try:
            errors = []
            warnings = []
            recommendations = []
            
            # Validate required fields
            required_fields = [
                "title", "executive_summary", "business_case", 
                "poc_scope", "timeline", "budget", "success_metrics", 
                "risk_assessment", "next_steps"
            ]
            
            for field in required_fields:
                if field not in poc_proposal or not poc_proposal[field]:
                    errors.append(f"Missing required field: {field}")
            
            # Validate content quality
            if "executive_summary" in poc_proposal:
                summary = poc_proposal["executive_summary"]
                if len(summary) < 50:
                    warnings.append("Executive summary is quite short")
                elif len(summary) > 500:
                    warnings.append("Executive summary is quite long")
            
            # Validate scope
            if "poc_scope" in poc_proposal:
                scope = poc_proposal["poc_scope"]
                if not isinstance(scope, list):
                    errors.append("POC scope must be a list")
                elif len(scope) < 3:
                    warnings.append("POC scope has fewer than 3 items")
                elif len(scope) > 10:
                    warnings.append("POC scope has more than 10 items")
            
            # Validate timeline
            if "timeline" in poc_proposal:
                timeline = poc_proposal["timeline"]
                if isinstance(timeline, dict):
                    total_days = timeline.get("total_duration_days", 0)
                    if total_days < 30:
                        warnings.append("Timeline is quite short (less than 30 days)")
                    elif total_days > 180:
                        warnings.append("Timeline is quite long (more than 180 days)")
            
            # Validate budget
            if "budget" in poc_proposal:
                budget = poc_proposal["budget"]
                if isinstance(budget, dict):
                    total_cost = budget.get("total_cost", 0)
                    if total_cost < 10000:
                        warnings.append("Budget seems quite low for a POC")
                    elif total_cost > 200000:
                        warnings.append("Budget seems quite high for a POC")
            
            # Validate success metrics
            if "success_metrics" in poc_proposal:
                metrics = poc_proposal["success_metrics"]
                if not isinstance(metrics, list):
                    errors.append("Success metrics must be a list")
                elif len(metrics) < 2:
                    warnings.append("Success metrics should have at least 2 items")
            
            # Validate risk assessment
            if "risk_assessment" in poc_proposal:
                risks = poc_proposal["risk_assessment"]
                if not isinstance(risks, list):
                    errors.append("Risk assessment must be a list")
                elif len(risks) < 2:
                    warnings.append("Risk assessment should have at least 2 items")
            
            # Generate recommendations
            if not errors:
                recommendations.append("Proposal structure looks good")
                if len(warnings) == 0:
                    recommendations.append("Consider adding more detail to strengthen the proposal")
                else:
                    recommendations.append("Address the warnings to improve proposal quality")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "recommendations": recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Error validating POC proposal: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "recommendations": ["Fix validation error and retry"]
            }
