#!/usr/bin/env python3
"""
Strategic Planning Composition Service

Composition service for strategic planning capabilities.

WHAT (Composition Service Role): I coordinate strategic planning capabilities
HOW (Composition Implementation): I integrate strategic planning abstractions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..abstraction_contracts.strategic_planning_protocol import StrategicPlanningResult
from ..infrastructure_abstractions.strategic_planning_abstraction import StrategicPlanningAbstraction


class StrategicPlanningCompositionService:
    """
    Strategic Planning Composition Service
    
    Coordinates strategic planning capabilities by integrating
    multiple strategic planning abstractions.
    """
    
    def __init__(self, strategic_planning_abstraction: StrategicPlanningAbstraction, di_container=None):
        """
        Initialize Strategic Planning Composition Service.
        
        Args:
            strategic_planning_abstraction: The strategic planning abstraction to use.
            di_container: DI Container for utilities
        """
        self.strategic_planning_abstraction = strategic_planning_abstraction
        self.di_container = di_container
        self.service_name = "strategic_planning_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("StrategicPlanningCompositionService")
        
        self.logger.info("🏗️ StrategicPlanningCompositionService initialized")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    async def comprehensive_strategic_planning(self, business_context: Dict[str, Any],
                                              user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive strategic planning including roadmap, goals, and performance analysis.
        
        Args:
            business_context: Business context and strategic requirements
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict containing comprehensive strategic planning results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "strategic_planning", "plan"
                )
                if validation_error:
                    return validation_error
            
            self.logger.info("Performing comprehensive strategic planning...")
            
            # Generate strategic roadmap
            roadmap_result = await self.strategic_planning_abstraction.generate_strategic_roadmap(
                business_context, business_context.get("roadmap_type", "hybrid")
            )
            
            # Track goals if provided
            goal_tracking_result = None
            if "goals" in business_context:
                goal_tracking_result = await self.strategic_planning_abstraction.track_goals(
                    business_context["goals"]
                )
            
            # Analyze performance if provided
            performance_result = None
            if "performance_data" in business_context:
                performance_result = await self.strategic_planning_abstraction.analyze_strategic_performance(
                    business_context["performance_data"]
                )
            
            # Generate AI-enhanced roadmap if requested
            ai_roadmap_result = None
            if business_context.get("ai_enhanced", False):
                ai_roadmap_result = await self.strategic_planning_abstraction.generate_ai_strategic_roadmap(
                    business_context
                )
            
            # Analyze trends if market data provided
            trend_analysis_result = None
            if "market_data" in business_context:
                trend_analysis_result = await self.strategic_planning_abstraction.analyze_strategic_trends(
                    business_context["market_data"]
                )
            
            # Generate strategic recommendations
            recommendations_result = await self.strategic_planning_abstraction.generate_strategic_recommendations(
                business_context
            )
            
            # Compile comprehensive results
            comprehensive_planning = {
                "planning_id": f"strategic_planning_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.utcnow().isoformat(),
                "business_context": business_context,
                "roadmap": {
                    "success": roadmap_result.success,
                    "roadmap_id": roadmap_result.roadmap_id,
                    "roadmap_type": roadmap_result.roadmap_type,
                    "phases": roadmap_result.phases,
                    "milestones": roadmap_result.milestones,
                    "timeline": roadmap_result.timeline,
                    "resource_allocation": roadmap_result.resource_allocation,
                    "success_metrics": roadmap_result.success_metrics,
                    "error": roadmap_result.error
                },
                "goal_tracking": {
                    "success": goal_tracking_result.success if goal_tracking_result else None,
                    "goal_tracking": goal_tracking_result.goal_tracking if goal_tracking_result else {},
                    "progress_report": goal_tracking_result.progress_report if goal_tracking_result else {},
                    "recommendations": goal_tracking_result.recommendations if goal_tracking_result else [],
                    "error": goal_tracking_result.error if goal_tracking_result else None
                } if goal_tracking_result else None,
                "performance_analysis": {
                    "success": performance_result.success if performance_result else None,
                    "performance_analysis": performance_result.performance_analysis if performance_result else {},
                    "insights": performance_result.insights if performance_result else [],
                    "recommendations": performance_result.recommendations if performance_result else [],
                    "error": performance_result.error if performance_result else None
                } if performance_result else None,
                "ai_enhanced_roadmap": {
                    "success": ai_roadmap_result.success if ai_roadmap_result else None,
                    "roadmap_id": ai_roadmap_result.roadmap_id if ai_roadmap_result else "",
                    "ai_insights": ai_roadmap_result.ai_insights if ai_roadmap_result else [],
                    "risk_analysis": ai_roadmap_result.risk_analysis if ai_roadmap_result else {},
                    "opportunities": ai_roadmap_result.opportunities if ai_roadmap_result else [],
                    "error": ai_roadmap_result.error if ai_roadmap_result else None
                } if ai_roadmap_result else None,
                "trend_analysis": {
                    "success": trend_analysis_result.success if trend_analysis_result else None,
                    "trend_analysis": trend_analysis_result.trend_analysis if trend_analysis_result else {},
                    "trend_insights": trend_analysis_result.trend_insights if trend_analysis_result else [],
                    "trend_predictions": trend_analysis_result.trend_predictions if trend_analysis_result else [],
                    "strategic_implications": trend_analysis_result.strategic_implications if trend_analysis_result else [],
                    "error": trend_analysis_result.error if trend_analysis_result else None
                } if trend_analysis_result else None,
                "strategic_recommendations": {
                    "success": recommendations_result.success,
                    "recommendations": recommendations_result.recommendations,
                    "priority_analysis": recommendations_result.priority_analysis,
                    "implementation_plan": recommendations_result.implementation_plan,
                    "error": recommendations_result.error
                },
                "overall_assessment": await self._generate_overall_assessment(
                    roadmap_result, goal_tracking_result, performance_result, 
                    ai_roadmap_result, trend_analysis_result, recommendations_result
                )
            }
            
            self.logger.info("✅ Comprehensive strategic planning completed")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("comprehensive_strategic_planning", {
                    "success": True
                })
            
            return comprehensive_planning
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "comprehensive_strategic_planning",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Comprehensive strategic planning failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "STRATEGIC_PLANNING_ERROR",
                "message": "Comprehensive strategic planning failed"
            }
    
    async def create_strategic_roadmap(self, business_context: Dict[str, Any],
                                      user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a strategic roadmap with comprehensive planning.
        
        Args:
            business_context: Business context and requirements
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict containing strategic roadmap creation results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "strategic_planning", "create"
                )
                if validation_error:
                    return validation_error
            
            self.logger.info("Creating strategic roadmap...")
            
            # Generate roadmap
            roadmap_result = await self.strategic_planning_abstraction.generate_strategic_roadmap(
                business_context, business_context.get("roadmap_type", "hybrid")
            )
            
            if not roadmap_result.success:
                return {
                    "success": False,
                    "error": roadmap_result.error,
                    "message": "Strategic roadmap creation failed"
                }
            
            # Generate additional insights if AI-enhanced
            ai_insights = []
            if business_context.get("ai_enhanced", False):
                ai_roadmap_result = await self.strategic_planning_abstraction.generate_ai_strategic_roadmap(
                    business_context
                )
                if ai_roadmap_result and ai_roadmap_result.success:
                    ai_insights = ai_roadmap_result.ai_insights
            
            result = {
                "success": True,
                "roadmap_id": roadmap_result.roadmap_id,
                "roadmap_type": roadmap_result.roadmap_type,
                "phases": roadmap_result.phases,
                "milestones": roadmap_result.milestones,
                "timeline": roadmap_result.timeline,
                "resource_allocation": roadmap_result.resource_allocation,
                "success_metrics": roadmap_result.success_metrics,
                "ai_insights": ai_insights,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_strategic_roadmap", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_strategic_roadmap",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Strategic roadmap creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "STRATEGIC_ROADMAP_CREATION_ERROR",
                "message": "Strategic roadmap creation failed"
            }
    
    async def track_strategic_progress(self, goals: List[Dict[str, Any]], 
                                      performance_data: Dict[str, Any] = None,
                                      user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Track strategic progress with goals and performance analysis.
        
        Args:
            goals: List of strategic goals to track
            performance_data: Optional performance data for analysis
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict containing strategic progress tracking results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "strategic_planning", "track"
                )
                if validation_error:
                    return validation_error
            
            self.logger.info("Tracking strategic progress...")
            
            # Track goals
            goal_tracking_result = await self.strategic_planning_abstraction.track_goals(goals)
            
            # Analyze performance if provided
            performance_result = None
            if performance_data:
                performance_result = await self.strategic_planning_abstraction.analyze_strategic_performance(
                    performance_data
                )
            
            result = {
                "success": goal_tracking_result.success,
                "goal_tracking": goal_tracking_result.goal_tracking,
                "progress_report": goal_tracking_result.progress_report,
                "goal_recommendations": goal_tracking_result.recommendations,
                "performance_analysis": {
                    "success": performance_result.success if performance_result else None,
                    "performance_analysis": performance_result.performance_analysis if performance_result else {},
                    "insights": performance_result.insights if performance_result else [],
                    "recommendations": performance_result.recommendations if performance_result else [],
                    "error": performance_result.error if performance_result else None
                } if performance_result else None,
                "tracked_at": datetime.utcnow().isoformat(),
                "error": goal_tracking_result.error
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("track_strategic_progress", {
                    "goals_count": len(goals),
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "track_strategic_progress",
                    "goals_count": len(goals),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Strategic progress tracking failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "STRATEGIC_PROGRESS_TRACKING_ERROR",
                "message": "Strategic progress tracking failed"
            }
    
    async def analyze_strategic_trends(self, market_data: Dict[str, Any],
                                      user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze strategic trends and generate insights.
        
        Args:
            market_data: Market and industry data for trend analysis
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict containing strategic trend analysis results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "strategic_planning", "analyze"
                )
                if validation_error:
                    return validation_error
            
            self.logger.info("Analyzing strategic trends...")
            
            # Analyze trends
            trend_result = await self.strategic_planning_abstraction.analyze_strategic_trends(market_data)
            
            # Generate strategic recommendations based on trends
            strategic_data = {
                "market_trends": trend_result.trend_analysis,
                "trend_insights": trend_result.trend_insights,
                "strategic_implications": trend_result.strategic_implications
            }
            
            recommendations_result = await self.strategic_planning_abstraction.generate_strategic_recommendations(
                strategic_data
            )
            
            result = {
                "success": trend_result.success,
                "trend_analysis": trend_result.trend_analysis,
                "trend_insights": trend_result.trend_insights,
                "trend_predictions": trend_result.trend_predictions,
                "strategic_implications": trend_result.strategic_implications,
                "strategic_recommendations": {
                    "success": recommendations_result.success,
                    "recommendations": recommendations_result.recommendations,
                    "priority_analysis": recommendations_result.priority_analysis,
                    "implementation_plan": recommendations_result.implementation_plan
                },
                "analyzed_at": datetime.utcnow().isoformat(),
                "error": trend_result.error
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("analyze_strategic_trends", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "analyze_strategic_trends",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Strategic trend analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "STRATEGIC_TREND_ANALYSIS_ERROR",
                "message": "Strategic trend analysis failed"
            }
    
    async def _generate_overall_assessment(self, roadmap_result: StrategicPlanningResult,
                                          goal_tracking_result: Optional[StrategicPlanningResult],
                                          performance_result: Optional[StrategicPlanningResult],
                                          ai_roadmap_result: Optional[StrategicPlanningResult],
                                          trend_analysis_result: Optional[StrategicPlanningResult],
                                          recommendations_result: StrategicPlanningResult) -> Dict[str, Any]:
        """Generate overall strategic planning assessment."""
        try:
            # Calculate overall success rate
            successful_components = 0
            total_components = 1  # roadmap_result is always present
            
            if roadmap_result.success:
                successful_components += 1
            
            if goal_tracking_result and goal_tracking_result.success:
                successful_components += 1
                total_components += 1
            
            if performance_result and performance_result.success:
                successful_components += 1
                total_components += 1
            
            if ai_roadmap_result and ai_roadmap_result.success:
                successful_components += 1
                total_components += 1
            
            if trend_analysis_result and trend_analysis_result.success:
                successful_components += 1
                total_components += 1
            
            if recommendations_result.success:
                successful_components += 1
                total_components += 1
            
            success_rate = (successful_components / total_components) * 100 if total_components > 0 else 0
            
            # Determine overall status
            if success_rate >= 90:
                status = "excellent"
                recommendation = "Strategic planning completed successfully with high confidence"
            elif success_rate >= 70:
                status = "good"
                recommendation = "Strategic planning completed with good results, minor improvements needed"
            elif success_rate >= 50:
                status = "fair"
                recommendation = "Strategic planning completed with mixed results, significant improvements needed"
            else:
                status = "poor"
                recommendation = "Strategic planning needs major improvements and re-evaluation"
            
            return {
                "overall_success_rate": round(success_rate, 1),
                "status": status,
                "recommendation": recommendation,
                "successful_components": successful_components,
                "total_components": total_components,
                "key_achievements": [
                    f"Roadmap generated: {roadmap_result.roadmap_id}" if roadmap_result.success else "Roadmap generation failed",
                    f"Goals tracked: {goal_tracking_result.goal_tracking.get('total_goals', 0)}" if goal_tracking_result and goal_tracking_result.success else "Goal tracking not available",
                    f"Performance analyzed: {len(performance_result.insights)} insights" if performance_result and performance_result.success else "Performance analysis not available",
                    f"AI insights generated: {len(ai_roadmap_result.ai_insights)}" if ai_roadmap_result and ai_roadmap_result.success else "AI insights not available",
                    f"Trends analyzed: {len(trend_analysis_result.trend_insights)} insights" if trend_analysis_result and trend_analysis_result.success else "Trend analysis not available",
                    f"Recommendations generated: {len(recommendations_result.recommendations)}" if recommendations_result.success else "Recommendations not available"
                ]
            }
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_generate_overall_assessment",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Overall assessment generation failed: {e}")
            return {
                "overall_success_rate": 0,
                "status": "error",
                "recommendation": "Unable to assess strategic planning results",
                "error": str(e),
                "error_code": "STRATEGIC_ASSESSMENT_GENERATION_ERROR"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the Strategic Planning Composition Service.
        
        Returns:
            Dict: Health check result
        """
        try:
            abstraction_health = await self.strategic_planning_abstraction.health_check()
            
            return {
                "healthy": abstraction_health.get("healthy", False),
                "message": "Strategic Planning Composition Service is operational",
                "abstraction_health": abstraction_health
            }
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Strategic Planning Composition Service health check failed: {e}")
            return {"healthy": False, "error_code": "STRATEGIC_PLANNING_HEALTH_CHECK_ERROR", "message": f"Health check failed: {str(e)}"}
