"""
Quality Recommendations Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List


class QualityRecommendations:
    """
    Quality recommendations generator following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("QualityRecommendations micro-module initialized")
    
    async def generate_recommendation(
        self, 
        quality_score: float, 
        top_issues: List[str], 
        context: str = ""
    ) -> str:
        """
        Generate quality recommendation based on score and issues.
        
        Args:
            quality_score: Overall quality score (0-100)
            top_issues: List of top quality issues
            context: Additional context for recommendation
            
        Returns:
            Recommendation string
        """
        try:
            # Generate recommendation based on score
            if quality_score >= 90:
                recommendation = await self._generate_excellent_recommendation(context)
            elif quality_score >= 80:
                recommendation = await self._generate_good_recommendation(top_issues, context)
            elif quality_score >= 60:
                recommendation = await self._generate_warning_recommendation(top_issues, context)
            else:
                recommendation = await self._generate_critical_recommendation(top_issues, context)
            
            self.logger.info(f"Quality recommendation generated for score {quality_score}")
            return recommendation
            
        except Exception as e:
            self.logger.error(f"Error generating recommendation: {e}")
            return "Please review your data quality and consider data cleaning before analysis."
    
    async def _generate_excellent_recommendation(self, context: str) -> str:
        """Generate recommendation for excellent quality data."""
        recommendations = [
            "Your data quality is excellent and ready for analysis.",
            "Data is in great condition for advanced analytics and modeling.",
            "Consider proceeding with confidence to insights generation."
        ]
        
        if context and "analysis" in context.lower():
            return "Data quality is excellent and perfect for the requested analysis."
        
        return recommendations[0]
    
    async def _generate_good_recommendation(self, top_issues: List[str], context: str) -> str:
        """Generate recommendation for good quality data."""
        if not top_issues or len(top_issues) == 0:
            return "Data quality is good and suitable for most analyses."
        
        # Check for specific issue types
        if any("missing" in issue.lower() for issue in top_issues):
            return "Data quality is good with minor missing value issues. Consider data imputation for optimal results."
        elif any("duplicate" in issue.lower() for issue in top_issues):
            return "Data quality is good with some duplicate records. Consider deduplication for cleaner analysis."
        else:
            return "Data quality is good with minor issues. Review the identified problems before proceeding."
    
    async def _generate_warning_recommendation(self, top_issues: List[str], context: str) -> str:
        """Generate recommendation for warning quality data."""
        if not top_issues or len(top_issues) == 0:
            return "Data quality needs improvement before analysis. Consider data cleaning and validation."
        
        # Check for critical issues
        critical_issues = [issue for issue in top_issues if any(word in issue.lower() for word in ["critical", "50%", "high"])]
        
        if critical_issues:
            return "Data quality has significant issues that require attention. Focus on data cleaning and validation before analysis."
        else:
            return "Data quality needs improvement. Address the identified issues to ensure reliable analysis results."
    
    async def _generate_critical_recommendation(self, top_issues: List[str], context: str) -> str:
        """Generate recommendation for critical quality data."""
        if not top_issues or len(top_issues) == 0:
            return "Data quality is critical and requires extensive cleaning before any analysis."
        
        # Check for specific critical issues
        if any("missing" in issue.lower() and "50%" in issue for issue in top_issues):
            return "Critical missing data issues detected. Consider data collection or alternative data sources before analysis."
        elif any("duplicate" in issue.lower() and "20%" in issue for issue in top_issues):
            return "High duplicate rate detected. Implement deduplication strategy before analysis."
        else:
            return "Data quality is critical with multiple serious issues. Extensive data cleaning and validation required before analysis."
    
    async def get_specific_recommendations(self, issues: List[str]) -> List[str]:
        """
        Get specific recommendations for individual issues.
        
        Args:
            issues: List of specific issues
            
        Returns:
            List of specific recommendations
        """
        try:
            recommendations = []
            
            for issue in issues:
                if "missing" in issue.lower():
                    if "50%" in issue or "critical" in issue.lower():
                        recommendations.append("Consider data imputation or removing incomplete records")
                    else:
                        recommendations.append("Review missing value patterns and consider imputation")
                
                elif "duplicate" in issue.lower():
                    if "20%" in issue or "high" in issue.lower():
                        recommendations.append("Implement comprehensive deduplication strategy")
                    else:
                        recommendations.append("Review and remove duplicate entries")
                
                elif "mixed" in issue.lower() or "type" in issue.lower():
                    recommendations.append("Standardize data types and formats")
                
                elif "format" in issue.lower():
                    recommendations.append("Standardize data formats and validation rules")
                
                else:
                    recommendations.append("Review data quality and implement appropriate cleaning")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating specific recommendations: {e}")
            return ["Please review data quality issues and implement appropriate solutions"]

