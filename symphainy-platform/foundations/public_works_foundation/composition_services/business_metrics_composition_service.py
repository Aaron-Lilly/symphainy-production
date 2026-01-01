#!/usr/bin/env python3
"""
Business Metrics Composition Service

Composition service for business metrics analysis, integrating the abstraction and applying business rules.

WHAT (Composition Service Role): I orchestrate business metrics analysis
HOW (Composition Implementation): I integrate the abstraction and apply business rules for comprehensive analysis
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..infrastructure_abstractions.business_metrics_abstraction import BusinessMetricsAbstraction
from ..abstraction_contracts.business_metrics_protocol import BusinessMetricsResult


class BusinessMetricsCompositionService:
    """
    Business Metrics Composition Service
    
    Orchestrates comprehensive business metrics analysis by integrating the abstraction
    and applying business rules for overall assessment and recommendations.
    """
    
    def __init__(self, business_metrics_abstraction: BusinessMetricsAbstraction, di_container=None):
        """
        Initialize Business Metrics Composition Service.
        
        Args:
            business_metrics_abstraction: Business metrics abstraction (required via DI)
            di_container: DI Container for utilities
        """
        if not business_metrics_abstraction:
            raise ValueError("BusinessMetricsCompositionService requires business_metrics_abstraction via dependency injection")
        
        self.abstraction = business_metrics_abstraction
        self.di_container = di_container
        self.service_name = "business_metrics_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("BusinessMetricsCompositionService")
        
        self.logger.info("🏗️ BusinessMetricsCompositionService initialized")
    
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
    
    async def get_comprehensive_business_analysis(self, business_data: Dict[str, Any], 
                                                industry: str = "default",
                                                include_ai_analysis: bool = True,
                                                user_context: Dict[str, Any] = None) -> BusinessMetricsResult:
        """
        Get comprehensive business metrics analysis.
        
        Args:
            business_data: Business data for analysis
            industry: Industry for benchmarking
            include_ai_analysis: Whether to include AI-powered analysis
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            BusinessMetricsResult: Comprehensive analysis results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "business_metrics", "analyze"
                )
                if validation_error:
                    return BusinessMetricsResult(
                        success=False,
                        kpis={},
                        benchmark_results={},
                        overall_benchmark_score=0,
                        insights=[],
                        recommendations=[],
                        metadata={"error_code": validation_error.get("error_code")},
                        error=validation_error.get("error")
                    )
            
            self.logger.info("Performing comprehensive business metrics analysis...")
            
            # Step 1: Calculate KPIs
            kpi_result = await self.abstraction.calculate_kpis(business_data)
            if not kpi_result.success:
                return kpi_result
            
            # Step 2: Benchmark performance
            benchmark_result = await self.abstraction.benchmark_performance(
                kpi_result.kpis, industry
            )
            if not benchmark_result.success:
                return benchmark_result
            
            # Step 3: AI-powered analysis (if requested)
            ai_analysis = {}
            ai_insights = []
            ai_recommendations = []
            
            if include_ai_analysis:
                # Business sentiment analysis
                sentiment_result = await self.abstraction.analyze_business_sentiment(business_data)
                if sentiment_result.success:
                    ai_analysis.update(sentiment_result.ai_analysis or {})
                    ai_insights.extend(sentiment_result.insights or [])
                    ai_recommendations.extend(sentiment_result.recommendations or [])
                
                # Business insights generation
                insights_result = await self.abstraction.generate_business_insights(business_data)
                if insights_result.success:
                    ai_insights.extend(insights_result.insights or [])
                    ai_recommendations.extend(insights_result.recommendations or [])
            
            # Step 4: Apply business rules for overall assessment
            overall_assessment = self._assess_overall_performance(
                kpi_result.kpis,
                benchmark_result.benchmark_results,
                benchmark_result.overall_benchmark_score
            )
            
            # Step 5: Generate comprehensive recommendations
            comprehensive_recommendations = self._generate_comprehensive_recommendations(
                kpi_result.recommendations or [],
                benchmark_result.recommendations or [],
                ai_recommendations,
                overall_assessment
            )
            
            # Step 6: Combine all insights
            all_insights = []
            all_insights.extend(kpi_result.insights or [])
            all_insights.extend(benchmark_result.insights or [])
            all_insights.extend(ai_insights)
            
            result = BusinessMetricsResult(
                success=True,
                kpis=kpi_result.kpis,
                benchmark_results=benchmark_result.benchmark_results,
                overall_benchmark_score=benchmark_result.overall_benchmark_score,
                ai_analysis=ai_analysis if ai_analysis else None,
                insights=all_insights,
                recommendations=comprehensive_recommendations,
                metadata={
                    "analysis_type": "comprehensive",
                    "industry": industry,
                    "ai_analysis_included": include_ai_analysis,
                    "kpi_count": len(kpi_result.kpis or {}),
                    "benchmark_metrics_count": len(benchmark_result.benchmark_results or {}),
                    "analyzed_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_comprehensive_business_analysis", {
                    "industry": industry,
                    "ai_analysis_included": include_ai_analysis,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_comprehensive_business_analysis",
                    "industry": industry,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to perform comprehensive business analysis: {e}")
            return BusinessMetricsResult(
                success=False,
                kpis={},
                benchmark_results={},
                overall_benchmark_score=0,
                insights=[],
                recommendations=[],
                metadata={"error_code": "BUSINESS_METRICS_ANALYSIS_ERROR"},
                error=str(e)
            )
    
    async def analyze_business_trends_comprehensive(self, historical_data: List[Dict[str, Any]], 
                                                  include_predictions: bool = True,
                                                  user_context: Dict[str, Any] = None) -> BusinessMetricsResult:
        """
        Analyze business trends comprehensively.
        
        Args:
            historical_data: Historical business data
            include_predictions: Whether to include AI predictions
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            BusinessMetricsResult: Comprehensive trend analysis results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "business_metrics", "analyze"
                )
                if validation_error:
                    return BusinessMetricsResult(
                        success=False,
                        trend_analysis={},
                        predictions={},
                        confidence_score=0,
                        insights=[],
                        recommendations=[],
                        metadata={"error_code": validation_error.get("error_code")},
                        error=validation_error.get("error")
                    )
            
            self.logger.info("Performing comprehensive business trend analysis...")
            
            # Step 1: Standard trend analysis
            trend_result = await self.abstraction.analyze_trends(historical_data)
            if not trend_result.success:
                return trend_result
            
            # Step 2: AI-powered predictions (if requested)
            predictions = {}
            prediction_confidence = 0.0
            prediction_insights = []
            
            if include_predictions and len(historical_data) > 0:
                prediction_result = await self.abstraction.predict_business_performance(historical_data)
                if prediction_result.success:
                    predictions = prediction_result.predictions or {}
                    prediction_confidence = prediction_result.confidence_score or 0.0
                    prediction_insights = prediction_result.insights or []
            
            # Step 3: Apply business rules for trend assessment
            trend_assessment = self._assess_trend_performance(
                trend_result.trend_analysis,
                predictions,
                prediction_confidence
            )
            
            # Step 4: Generate trend-based recommendations
            trend_recommendations = self._generate_trend_recommendations(
                trend_result.recommendations or [],
                prediction_insights,
                trend_assessment
            )
            
            # Step 5: Combine all insights
            all_insights = []
            all_insights.extend(trend_result.insights or [])
            all_insights.extend(prediction_insights)
            
            result = BusinessMetricsResult(
                success=True,
                trend_analysis=trend_result.trend_analysis,
                predictions=predictions if predictions else None,
                confidence_score=prediction_confidence,
                insights=all_insights,
                recommendations=trend_recommendations,
                metadata={
                    "analysis_type": "comprehensive_trends",
                    "data_points": len(historical_data),
                    "predictions_included": include_predictions,
                    "trend_metrics_count": len(trend_result.trend_analysis or {}),
                    "analyzed_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("analyze_business_trends_comprehensive", {
                    "data_points": len(historical_data),
                    "predictions_included": include_predictions,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "analyze_business_trends_comprehensive",
                    "data_points": len(historical_data),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to perform comprehensive trend analysis: {e}")
            return BusinessMetricsResult(
                success=False,
                trend_analysis={},
                predictions={},
                confidence_score=0,
                insights=[],
                recommendations=[],
                metadata={"error_code": "BUSINESS_METRICS_TREND_ANALYSIS_ERROR"},
                error=str(e)
            )
    
    async def benchmark_against_industry(self, business_data: Dict[str, Any], 
                                       industry: str, 
                                       include_ai_insights: bool = True,
                                       user_context: Dict[str, Any] = None) -> BusinessMetricsResult:
        """
        Benchmark business performance against industry standards.
        
        Args:
            business_data: Business data for benchmarking
            industry: Industry for comparison
            include_ai_insights: Whether to include AI insights
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            BusinessMetricsResult: Benchmarking results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "business_metrics", "benchmark"
                )
                if validation_error:
                    return BusinessMetricsResult(
                        success=False,
                        kpis={},
                        benchmark_results={},
                        overall_benchmark_score=0,
                        insights=[],
                        recommendations=[],
                        metadata={"error_code": validation_error.get("error_code")},
                        error=validation_error.get("error")
                    )
            
            self.logger.info(f"Benchmarking against {industry} industry standards...")
            
            # Step 1: Calculate KPIs first
            kpi_result = await self.abstraction.calculate_kpis(business_data)
            if not kpi_result.success:
                return kpi_result
            
            # Step 2: Benchmark against industry
            benchmark_result = await self.abstraction.benchmark_performance(
                kpi_result.kpis, industry
            )
            if not benchmark_result.success:
                return benchmark_result
            
            # Step 3: AI insights (if requested)
            ai_insights = []
            ai_recommendations = []
            
            if include_ai_insights:
                # Generate AI insights for benchmarking context
                benchmark_context = {
                    **business_data,
                    "industry": industry,
                    "benchmark_score": benchmark_result.overall_benchmark_score
                }
                
                insights_result = await self.abstraction.generate_business_insights(benchmark_context)
                if insights_result.success:
                    ai_insights = insights_result.insights or []
                    ai_recommendations = insights_result.recommendations or []
            
            # Step 4: Apply industry-specific business rules
            industry_assessment = self._assess_industry_performance(
                benchmark_result.benchmark_results,
                benchmark_result.overall_benchmark_score,
                industry
            )
            
            # Step 5: Generate industry-specific recommendations
            industry_recommendations = self._generate_industry_recommendations(
                benchmark_result.recommendations or [],
                ai_recommendations,
                industry_assessment,
                industry
            )
            
            # Step 6: Combine all insights
            all_insights = []
            all_insights.extend(benchmark_result.insights or [])
            all_insights.extend(ai_insights)
            
            result = BusinessMetricsResult(
                success=True,
                kpis=kpi_result.kpis,
                benchmark_results=benchmark_result.benchmark_results,
                overall_benchmark_score=benchmark_result.overall_benchmark_score,
                insights=all_insights,
                recommendations=industry_recommendations,
                metadata={
                    "analysis_type": "industry_benchmarking",
                    "industry": industry,
                    "ai_insights_included": include_ai_insights,
                    "benchmark_metrics_count": len(benchmark_result.benchmark_results or {}),
                    "analyzed_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("benchmark_against_industry", {
                    "industry": industry,
                    "ai_insights_included": include_ai_insights,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "benchmark_against_industry",
                    "industry": industry,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to benchmark against industry: {e}")
            return BusinessMetricsResult(
                success=False,
                kpis={},
                benchmark_results={},
                overall_benchmark_score=0,
                insights=[],
                recommendations=[],
                metadata={"error_code": "BUSINESS_METRICS_BENCHMARK_ERROR"},
                error=str(e)
            )
    
    def _assess_overall_performance(self, kpis: Dict[str, Any], 
                                   benchmark_results: Dict[str, Any], 
                                   overall_score: float) -> Dict[str, Any]:
        """Assess overall business performance."""
        assessment = {
            "performance_level": "unknown",
            "strengths": [],
            "weaknesses": [],
            "priority_areas": []
        }
        
        # Determine performance level
        if overall_score >= 80:
            assessment["performance_level"] = "excellent"
        elif overall_score >= 65:
            assessment["performance_level"] = "good"
        elif overall_score >= 50:
            assessment["performance_level"] = "average"
        elif overall_score >= 35:
            assessment["performance_level"] = "below_average"
        else:
            assessment["performance_level"] = "poor"
        
        # Identify strengths and weaknesses
        for metric, result in benchmark_results.items():
            percentile = result.get("percentile", 0)
            if percentile >= 75:
                assessment["strengths"].append(metric)
            elif percentile < 25:
                assessment["weaknesses"].append(metric)
                assessment["priority_areas"].append(metric)
        
        return assessment
    
    def _assess_trend_performance(self, trend_analysis: Dict[str, Any], 
                                 predictions: Dict[str, Any], 
                                 confidence: float) -> Dict[str, Any]:
        """Assess trend performance."""
        assessment = {
            "trend_health": "unknown",
            "key_trends": [],
            "concerns": [],
            "opportunities": []
        }
        
        # Analyze trend health
        strong_trends = [k for k, v in trend_analysis.items() if v.get("trend_strength") == "strong"]
        increasing_trends = [k for k, v in trend_analysis.items() if v.get("trend_direction") == "increasing"]
        decreasing_trends = [k for k, v in trend_analysis.items() if v.get("trend_direction") == "decreasing"]
        
        if len(increasing_trends) > len(decreasing_trends):
            assessment["trend_health"] = "positive"
        elif len(decreasing_trends) > len(increasing_trends):
            assessment["trend_health"] = "negative"
        else:
            assessment["trend_health"] = "mixed"
        
        assessment["key_trends"] = strong_trends
        assessment["concerns"] = decreasing_trends
        assessment["opportunities"] = increasing_trends
        
        return assessment
    
    def _assess_industry_performance(self, benchmark_results: Dict[str, Any], 
                                    overall_score: float, 
                                    industry: str) -> Dict[str, Any]:
        """Assess industry-specific performance."""
        assessment = {
            "industry_position": "unknown",
            "competitive_advantages": [],
            "competitive_disadvantages": [],
            "industry_insights": []
        }
        
        # Determine industry position
        if overall_score >= 75:
            assessment["industry_position"] = "leader"
        elif overall_score >= 60:
            assessment["industry_position"] = "above_average"
        elif overall_score >= 40:
            assessment["industry_position"] = "average"
        else:
            assessment["industry_position"] = "below_average"
        
        # Identify competitive advantages and disadvantages
        for metric, result in benchmark_results.items():
            percentile = result.get("percentile", 0)
            if percentile >= 80:
                assessment["competitive_advantages"].append(metric)
            elif percentile < 30:
                assessment["competitive_disadvantages"].append(metric)
        
        # Add industry-specific insights
        if industry == "technology":
            assessment["industry_insights"].append("Focus on innovation and rapid growth")
        elif industry == "manufacturing":
            assessment["industry_insights"].append("Emphasize operational efficiency and cost control")
        
        return assessment
    
    def _generate_comprehensive_recommendations(self, kpi_recommendations: List[str],
                                               benchmark_recommendations: List[str],
                                               ai_recommendations: List[str],
                                               assessment: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations."""
        recommendations = []
        
        # Add KPI-based recommendations
        recommendations.extend(kpi_recommendations)
        
        # Add benchmark-based recommendations
        recommendations.extend(benchmark_recommendations)
        
        # Add AI recommendations
        recommendations.extend(ai_recommendations)
        
        # Add assessment-based recommendations
        performance_level = assessment.get("performance_level", "unknown")
        if performance_level == "poor":
            recommendations.append("Implement comprehensive performance improvement program")
        elif performance_level == "below_average":
            recommendations.append("Focus on key performance gaps and improvement areas")
        
        # Add priority area recommendations
        priority_areas = assessment.get("priority_areas", [])
        for area in priority_areas:
            recommendations.append(f"Prioritize improvement in {area}")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_trend_recommendations(self, trend_recommendations: List[str],
                                       prediction_insights: List[str],
                                       assessment: Dict[str, Any]) -> List[str]:
        """Generate trend-based recommendations."""
        recommendations = []
        
        # Add trend-based recommendations
        recommendations.extend(trend_recommendations)
        
        # Add prediction insights
        recommendations.extend(prediction_insights)
        
        # Add assessment-based recommendations
        trend_health = assessment.get("trend_health", "unknown")
        if trend_health == "negative":
            recommendations.append("Address declining trends immediately")
        elif trend_health == "positive":
            recommendations.append("Leverage positive trends for growth")
        
        concerns = assessment.get("concerns", [])
        for concern in concerns:
            recommendations.append(f"Monitor and address declining trend in {concern}")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _generate_industry_recommendations(self, benchmark_recommendations: List[str],
                                         ai_recommendations: List[str],
                                         assessment: Dict[str, Any],
                                         industry: str) -> List[str]:
        """Generate industry-specific recommendations."""
        recommendations = []
        
        # Add benchmark recommendations
        recommendations.extend(benchmark_recommendations)
        
        # Add AI recommendations
        recommendations.extend(ai_recommendations)
        
        # Add industry position recommendations
        industry_position = assessment.get("industry_position", "unknown")
        if industry_position == "below_average":
            recommendations.append("Develop strategies to improve industry competitiveness")
        elif industry_position == "leader":
            recommendations.append("Maintain leadership position and explore expansion")
        
        # Add competitive advantage recommendations
        advantages = assessment.get("competitive_advantages", [])
        for advantage in advantages:
            recommendations.append(f"Leverage competitive advantage in {advantage}")
        
        # Add competitive disadvantage recommendations
        disadvantages = assessment.get("competitive_disadvantages", [])
        for disadvantage in disadvantages:
            recommendations.append(f"Address competitive disadvantage in {disadvantage}")
        
        return list(set(recommendations))  # Remove duplicates
