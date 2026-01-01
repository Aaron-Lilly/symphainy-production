"""
SOP Validator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class SOPValidator:
    """
    SOP Validator following Smart City patterns.
    Handles SOP validation and quality assessment.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("SOPValidator micro-module initialized")
    
    async def validate_sop_for_publishing(self, sop: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate SOP before publishing."""
        try:
            if not sop:
                return {
                    "valid": False,
                    "errors": ["No SOP provided"],
                    "warnings": [],
                    "score": 0
                }
            
            errors = []
            warnings = []
            score = 100
            
            # Check title
            if not sop.get("title") or sop["title"] == "Untitled SOP":
                errors.append("SOP needs a proper title")
                score -= 20
            elif len(sop["title"]) < 5:
                warnings.append("SOP title is quite short")
                score -= 5
            
            # Check description
            if not sop.get("description"):
                warnings.append("SOP description is missing")
                score -= 10
            elif len(sop["description"]) < 10:
                warnings.append("SOP description is quite short")
                score -= 5
            
            # Check steps
            steps = sop.get("steps", [])
            if not steps:
                errors.append("SOP must have at least one step")
                score -= 30
            else:
                # Check step quality
                for i, step in enumerate(steps):
                    if not step.get("description") or len(step["description"].strip()) < 5:
                        warnings.append(f"Step {i+1} description is quite short")
                        score -= 5
                    
                    if not step.get("title") or step["title"] == f"Step {i+1}":
                        warnings.append(f"Step {i+1} needs a proper title")
                        score -= 3
                    
                    if not step.get("responsible_role"):
                        warnings.append(f"Step {i+1} doesn't specify responsible role")
                        score -= 2
                    
                    if not step.get("expected_output"):
                        warnings.append(f"Step {i+1} doesn't specify expected output")
                        score -= 2
            
            # Check version
            if not sop.get("version"):
                warnings.append("SOP version is missing")
                score -= 5
            
            # Ensure score is not negative
            score = max(0, score)
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "score": score
            }
            
        except Exception as e:
            self.logger.error(f"Error validating SOP: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "score": 0
            }
    
    async def get_sop_statistics(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about the SOP."""
        try:
            steps = sop.get("steps", [])
            total_steps = len(steps)
            
            # Calculate statistics
            total_chars = sum(len(step.get("description", "")) for step in steps)
            avg_chars_per_step = total_chars / total_steps if total_steps > 0 else 0
            
            # Count roles
            roles = {}
            for step in steps:
                role = step.get("responsible_role", "Unspecified")
                roles[role] = roles.get(role, 0) + 1
            
            # Count steps with expected outputs
            steps_with_outputs = sum(1 for step in steps if step.get("expected_output"))
            
            return {
                "total_steps": total_steps,
                "total_characters": total_chars,
                "average_chars_per_step": round(avg_chars_per_step, 2),
                "role_distribution": roles,
                "steps_with_outputs": steps_with_outputs,
                "output_coverage": round(steps_with_outputs / total_steps * 100, 2) if total_steps > 0 else 0,
                "created_at": sop.get("created_at"),
                "updated_at": sop.get("updated_at"),
                "version": sop.get("version", "1.0.0")
            }
            
        except Exception as e:
            self.logger.error(f"Error getting SOP statistics: {e}")
            return {"error": str(e)}
    
    async def get_comprehensive_validation_report(self, sop: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive validation report."""
        try:
            validation_result = await self.validate_sop_for_publishing(sop)
            statistics = await self.get_sop_statistics(sop)
            
            # Additional quality metrics
            steps = sop.get("steps", [])
            quality_metrics = {
                "completeness": 0,
                "clarity": 0,
                "consistency": 0,
                "actionability": 0
            }
            
            if steps:
                # Completeness: steps with all required fields
                complete_steps = sum(1 for step in steps if all([
                    step.get("title"),
                    step.get("description"),
                    step.get("responsible_role"),
                    step.get("expected_output")
                ]))
                quality_metrics["completeness"] = round(complete_steps / len(steps) * 100, 2)
                
                # Clarity: average description length
                avg_desc_length = sum(len(step.get("description", "")) for step in steps) / len(steps)
                quality_metrics["clarity"] = min(100, round(avg_desc_length / 50 * 100, 2))
                
                # Consistency: role distribution
                roles = [step.get("responsible_role") for step in steps if step.get("responsible_role")]
                if roles:
                    most_common_role = max(set(roles), key=roles.count)
                    role_consistency = roles.count(most_common_role) / len(roles)
                    quality_metrics["consistency"] = round(role_consistency * 100, 2)
                
                # Actionability: steps with expected outputs
                quality_metrics["actionability"] = statistics.get("output_coverage", 0)
            
            return {
                "validation": validation_result,
                "statistics": statistics,
                "quality_metrics": quality_metrics,
                "overall_quality": round(sum(quality_metrics.values()) / len(quality_metrics), 2),
                "recommendations": await self.get_validation_recommendations(validation_result)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive validation report: {e}")
            return {"error": str(e)}
    
    async def get_validation_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Get validation recommendations."""
        try:
            recommendations = []
            errors = validation_result.get("errors", [])
            warnings = validation_result.get("warnings", [])
            
            # Error-based recommendations
            if "No SOP provided" in errors:
                recommendations.append("Start by creating a new SOP")
            if "SOP needs a proper title" in errors:
                recommendations.append("Add a descriptive title for your SOP")
            if "SOP must have at least one step" in errors:
                recommendations.append("Add at least one step to your SOP")
            
            # Warning-based recommendations
            if any("title is quite short" in warning for warning in warnings):
                recommendations.append("Make SOP and step titles more descriptive")
            if any("description is quite short" in warning for warning in warnings):
                recommendations.append("Add more detail to descriptions")
            if any("responsible role" in warning for warning in warnings):
                recommendations.append("Specify responsible roles for each step")
            if any("expected output" in warning for warning in warnings):
                recommendations.append("Define expected outputs for each step")
            if any("version is missing" in warning for warning in warnings):
                recommendations.append("Add a version number to your SOP")
            
            # General recommendations
            if not recommendations:
                if validation_result.get("valid", False):
                    recommendations.append("Your SOP looks good! Consider adding more detail to make it even better.")
                else:
                    recommendations.append("Address the errors above to make your SOP publishable.")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting validation recommendations: {e}")
            return [f"Error generating recommendations: {str(e)}"]

