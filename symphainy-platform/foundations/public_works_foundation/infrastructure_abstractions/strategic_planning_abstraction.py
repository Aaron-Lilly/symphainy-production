#!/usr/bin/env python3
"""
Strategic Planning Abstraction

Infrastructure abstraction for strategic planning capabilities.

WHAT (Infrastructure Abstraction Role): I provide a unified interface for strategic planning
HOW (Abstraction Implementation): I coordinate strategic planning adapters
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import logging

from ..abstraction_contracts.strategic_planning_protocol import StrategicPlanningProtocol, StrategicPlanningResult
from ..infrastructure_adapters.standard_strategic_planning_adapter import StandardStrategicPlanningAdapter

# HuggingFace adapter is optional (in future_abstractions/ for future use)
if TYPE_CHECKING:
    from ..infrastructure_adapters.future_abstractions.huggingface_strategic_planning_adapter import HuggingFaceStrategicPlanningAdapter
else:
    try:
        from ..infrastructure_adapters.future_abstractions.huggingface_strategic_planning_adapter import HuggingFaceStrategicPlanningAdapter
    except ImportError:
        self.logger.error(f"❌ Error: {e}")
        HuggingFaceStrategicPlanningAdapter = None  # Not available - will be None

        raise  # Re-raise for service layer to handle

class StrategicPlanningAbstraction(StrategicPlanningProtocol):
    """
    Strategic Planning Abstraction
    
    Provides a unified interface for strategic planning by coordinating
    underlying strategic planning adapters.
    """
    
    def __init__(self, standard_strategic_planning_adapter: StandardStrategicPlanningAdapter, 
                 huggingface_strategic_planning_adapter: Optional[Any] = None,
                 di_container=None):
        """
        Initialize Strategic Planning Abstraction.
        
        Args:
            standard_strategic_planning_adapter: The standard strategic planning adapter to use.
            huggingface_strategic_planning_adapter: Optional HuggingFace strategic planning adapter for AI-powered analysis.
            di_container: Dependency injection container
        """
        self.standard_strategic_planning_adapter = standard_strategic_planning_adapter
        self.huggingface_strategic_planning_adapter = huggingface_strategic_planning_adapter
        self.di_container = di_container
        self.service_name = "strategic_planning_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("🏗️ StrategicPlanningAbstraction initialized")
    
    async def generate_strategic_roadmap(self, business_context: Dict[str, Any], 
                                        roadmap_type: str = "hybrid") -> StrategicPlanningResult:
        """
        Generate a strategic roadmap based on business context.
        
        Args:
            business_context: Business context and requirements
            roadmap_type: Type of roadmap (agile, waterfall, hybrid, ai_enhanced)
            
        Returns:
            StrategicPlanningResult: Result of the roadmap generation
        """
        try:
            if roadmap_type == "ai_enhanced" and self.huggingface_strategic_planning_adapter:
                self.logger.debug("Delegating AI-enhanced roadmap generation to HuggingFace adapter...")
                result = await self.huggingface_strategic_planning_adapter.generate_ai_strategic_roadmap(business_context)
            else:
                self.logger.debug("Delegating roadmap generation to standard adapter...")
                result = await self.standard_strategic_planning_adapter.generate_strategic_roadmap(business_context, roadmap_type)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Strategic roadmap generation failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Track progress of strategic goals.
        
        Args:
            goals: List of goals to track
            
        Returns:
            StrategicPlanningResult: Result of goal tracking
        """
        try:
            self.logger.debug("Delegating goal tracking to standard adapter...")
            result = await self.standard_strategic_planning_adapter.track_goals(goals)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Goal tracking failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Analyze strategic performance against goals and metrics.
        
        Args:
            performance_data: Performance data and metrics
            
        Returns:
            StrategicPlanningResult: Result of performance analysis
        """
        try:
            self.logger.debug("Delegating performance analysis to standard adapter...")
            result = await self.standard_strategic_planning_adapter.analyze_strategic_performance(performance_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Strategic performance analysis failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Generate AI-powered strategic roadmap with advanced insights.
        
        Args:
            business_context: Business context and requirements
            
        Returns:
            StrategicPlanningResult: Result of the AI-powered roadmap generation
        """
        try:
            if self.huggingface_strategic_planning_adapter:
                self.logger.debug("Delegating AI roadmap generation to HuggingFace adapter...")
                result = await self.huggingface_strategic_planning_adapter.generate_ai_strategic_roadmap(business_context)
            else:
                self.logger.warning("HuggingFace adapter not available, using standard roadmap generation...")
                result = await self.standard_strategic_planning_adapter.generate_strategic_roadmap(business_context, "hybrid")
            
            return result
        except Exception as e:
            self.logger.error(f"❌ AI strategic roadmap generation failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle
    
            raise  # Re-raise for service layer to handle

        """
        Analyze strategic trends using AI models.
        
        Args:
            market_data: Market and industry data for trend analysis
            
        Returns:
            StrategicPlanningResult: Result of the trend analysis
        """
        try:
            if self.huggingface_strategic_planning_adapter:
                self.logger.debug("Delegating trend analysis to HuggingFace adapter...")
                result = await self.huggingface_strategic_planning_adapter.analyze_strategic_trends(market_data)
            else:
                self.logger.warning("HuggingFace adapter not available, using standard trend analysis...")
                result = await self._standard_trend_analysis(market_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Strategic trend analysis failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Generate AI-powered strategic recommendations.
        
        Args:
            strategic_data: Strategic data for recommendation generation
            
        Returns:
            StrategicPlanningResult: Result of the recommendation generation
        """
        try:
            if self.huggingface_strategic_planning_adapter:
                self.logger.debug("Delegating recommendation generation to HuggingFace adapter...")
                result = await self.huggingface_strategic_planning_adapter.generate_strategic_recommendations(strategic_data)
            else:
                self.logger.warning("HuggingFace adapter not available, using standard recommendations...")
                result = await self._standard_recommendation_generation(strategic_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Strategic recommendation generation failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _fallback_trend_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback standard trend analysis when AI adapter is not available."""
        try:
            # Simple trend analysis based on market data
            trends = market_data.get("trends", [])
            market_conditions = market_data.get("market_conditions", "stable")
            
            trend_analysis = {
                "trend_direction": "positive" if market_conditions == "favorable" else "neutral",
                "trend_strength": "moderate",
                "key_trends": trends,
                "trend_confidence": 0.7
            }
            
            trend_insights = []
            if market_conditions == "favorable":
                trend_insights.append("Favorable market conditions support strategic initiatives")
            else:
                trend_insights.append("Market conditions require careful strategic planning")
            
            strategic_implications = [
                "Monitor market trends for strategic adjustments",
                "Align strategic initiatives with market conditions"
            ]
            
            return StrategicPlanningResult(
                success=True,
                trend_analysis=trend_analysis,
                trend_insights=trend_insights,
                strategic_implications=strategic_implications,
                metadata={
                    "analysis_method": "standard",
                    "market_conditions": market_conditions
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _fallback_recommendation_generation(self, strategic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback standard recommendation generation when AI adapter is not available."""
        try:
            # Simple recommendation generation based on strategic data
            objectives = strategic_data.get("objectives", [])
            budget = strategic_data.get("budget", 0)
            
            recommendations = []
            
            if len(objectives) > 3:
                recommendations.append("Prioritize objectives to focus on most critical goals")
            
            if budget > 1000000:
                recommendations.append("Implement robust governance and oversight mechanisms")
            
            if "digital transformation" in str(objectives).lower():
                recommendations.append("Focus on change management and user adoption")
            
            priority_analysis = {
                "total_recommendations": len(recommendations),
                "high_priority_count": len([rec for rec in recommendations if "critical" in rec.lower() or "governance" in rec.lower()]),
                "priority_distribution": {
                    "high": len([rec for rec in recommendations if "critical" in rec.lower() or "governance" in rec.lower()]),
                    "medium": len([rec for rec in recommendations if "focus" in rec.lower()]),
                    "low": 0
                }
            }
            
            implementation_plan = {
                "implementation_phases": [
                    {"phase": "Immediate Actions", "duration": "1-2 months", "recommendations": recommendations[:2]},
                    {"phase": "Strategic Initiatives", "duration": "3-6 months", "recommendations": recommendations[2:]}
                ],
                "success_metrics": [
                    "Recommendation implementation rate",
                    "Strategic objective achievement"
                ]
            }
            
            return StrategicPlanningResult(
                success=True,
                recommendations=recommendations,
                priority_analysis=priority_analysis,
                implementation_plan=implementation_plan,
                metadata={
                    "generation_method": "standard",
                    "objectives_count": len(objectives),
                    "budget_range": "high" if budget > 1000000 else "medium" if budget > 100000 else "low"
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            raise  # Re-raise for service layer to handle

        """
        Perform a health check for the Strategic Planning Abstraction.
        
        Returns:
            Dict: Health check result
        """
        try:
            standard_health = await self.standard_strategic_planning_adapter.health_check()
            huggingface_health = None
            
            if self.huggingface_strategic_planning_adapter:
                huggingface_health = await self.huggingface_strategic_planning_adapter.health_check()
            
            return {
                "healthy": standard_health.get("healthy", False),
                "message": "Strategic Planning Abstraction is operational",
                "standard_adapter_health": standard_health,
                "huggingface_adapter_health": huggingface_health
            }
        except Exception as e:
            self.logger.error(f"❌ Strategic Planning Abstraction health check failed: {e}")

            raise  # Re-raise for service layer to handle
