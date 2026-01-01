#!/usr/bin/env python3
"""
Financial Analysis Composition Service

Composition service for financial analysis capabilities.

WHAT (Composition Service Role): I coordinate financial analysis capabilities
HOW (Composition Implementation): I integrate financial analysis abstractions
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..abstraction_contracts.financial_analysis_protocol import FinancialAnalysisResult
from ..infrastructure_abstractions.financial_analysis_abstraction import FinancialAnalysisAbstraction


class FinancialAnalysisCompositionService:
    """
    Financial Analysis Composition Service
    
    Coordinates financial analysis capabilities by integrating
    multiple financial analysis abstractions.
    """
    
    def __init__(self, financial_analysis_abstraction: FinancialAnalysisAbstraction, di_container=None):
        """
        Initialize Financial Analysis Composition Service.
        
        Args:
            financial_analysis_abstraction: The financial analysis abstraction to use.
            di_container: DI Container for utilities
        """
        self.financial_analysis_abstraction = financial_analysis_abstraction
        self.di_container = di_container
        self.service_name = "financial_analysis_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("FinancialAnalysisCompositionService")
        
        self.logger.info("🏗️ FinancialAnalysisCompositionService initialized")
    
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
    
    async def comprehensive_financial_analysis(self, investment_data: Dict[str, Any],
                                             user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive financial analysis including ROI, NPV, IRR, and risk assessment.
        
        Args:
            investment_data: Investment details and market data
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict containing comprehensive financial analysis results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "financial_analysis", "analyze"
                )
                if validation_error:
                    return validation_error
            
            self.logger.info("Performing comprehensive financial analysis...")
            
            # Calculate basic financial metrics
            roi_result = await self.financial_analysis_abstraction.calculate_roi(investment_data)
            
            # Calculate NPV if cash flows are provided
            npv_result = None
            if "cash_flows" in investment_data:
                cash_flows = investment_data["cash_flows"]
                discount_rate = investment_data.get("discount_rate", 0.1)
                npv_result = await self.financial_analysis_abstraction.calculate_npv(cash_flows, discount_rate)
            
            # Calculate IRR if cash flows are provided
            irr_result = None
            if "cash_flows" in investment_data:
                cash_flows = investment_data["cash_flows"]
                irr_result = await self.financial_analysis_abstraction.calculate_irr(cash_flows)
            
            # Calculate payback period
            payback_result = None
            if "initial_investment" in investment_data and "annual_cash_flow" in investment_data:
                initial_investment = investment_data["initial_investment"]
                annual_cash_flow = investment_data["annual_cash_flow"]
                payback_result = await self.financial_analysis_abstraction.calculate_payback_period(
                    initial_investment, annual_cash_flow
                )
            
            # Perform risk analysis
            risk_result = await self.financial_analysis_abstraction.analyze_financial_risk(investment_data)
            
            # Generate financial insights
            insights_result = await self.financial_analysis_abstraction.generate_financial_insights(investment_data)
            
            # Compile comprehensive results
            comprehensive_analysis = {
                "analysis_id": f"financial_analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.utcnow().isoformat(),
                "investment_data": investment_data,
                "roi_analysis": {
                    "success": roi_result.success,
                    "roi_percentage": roi_result.roi_percentage,
                    "roi_ratio": roi_result.roi_ratio,
                    "annualized_roi": roi_result.annualized_roi,
                    "net_profit": roi_result.net_profit,
                    "total_returns": roi_result.total_returns,
                    "error": roi_result.error
                },
                "npv_analysis": {
                    "success": npv_result.success if npv_result else False,
                    "npv": npv_result.npv if npv_result else 0,
                    "error": npv_result.error if npv_result else None
                } if npv_result else None,
                "irr_analysis": {
                    "success": irr_result.success if irr_result else False,
                    "irr": irr_result.irr if irr_result else 0,
                    "error": irr_result.error if irr_result else None
                } if irr_result else None,
                "payback_analysis": {
                    "success": payback_result.success if payback_result else False,
                    "payback_period_years": payback_result.payback_period_years if payback_result else 0,
                    "error": payback_result.error if payback_result else None
                } if payback_result else None,
                "risk_analysis": {
                    "success": risk_result.success,
                    "risk_score": risk_result.risk_score,
                    "risk_level": risk_result.risk_level,
                    "risk_factors": risk_result.risk_factors,
                    "error": risk_result.error
                },
                "insights": {
                    "success": insights_result.success,
                    "insights": insights_result.insights,
                    "recommendations": insights_result.recommendations,
                    "market_sentiment": insights_result.market_sentiment,
                    "error": insights_result.error
                },
                "overall_assessment": await self._generate_overall_assessment(
                    roi_result, npv_result, irr_result, payback_result, risk_result, insights_result
                )
            }
            
            self.logger.info("✅ Comprehensive financial analysis completed")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("comprehensive_financial_analysis", {
                    "success": True
                })
            
            return comprehensive_analysis
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "comprehensive_financial_analysis",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Comprehensive financial analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "FINANCIAL_ANALYSIS_ERROR",
                "message": "Comprehensive financial analysis failed"
            }
    
    async def calculate_investment_metrics(self, investment_data: Dict[str, Any],
                                         user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate key investment metrics for decision making.
        
        Args:
            investment_data: Investment details and expected returns
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict containing calculated investment metrics
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "financial_analysis", "calculate"
                )
                if validation_error:
                    return validation_error
            
            self.logger.info("Calculating investment metrics...")
            
            # Calculate ROI
            roi_result = await self.financial_analysis_abstraction.calculate_roi(investment_data)
            
            # Calculate additional metrics if cash flows are available
            npv_result = None
            irr_result = None
            
            if "cash_flows" in investment_data:
                cash_flows = investment_data["cash_flows"]
                discount_rate = investment_data.get("discount_rate", 0.1)
                
                npv_result = await self.financial_analysis_abstraction.calculate_npv(cash_flows, discount_rate)
                irr_result = await self.financial_analysis_abstraction.calculate_irr(cash_flows)
            
            # Compile metrics
            metrics = {
                "roi_percentage": roi_result.roi_percentage,
                "roi_ratio": roi_result.roi_ratio,
                "annualized_roi": roi_result.annualized_roi,
                "net_profit": roi_result.net_profit,
                "total_returns": roi_result.total_returns
            }
            
            if npv_result and npv_result.success:
                metrics["npv"] = npv_result.npv
            
            if irr_result and irr_result.success:
                metrics["irr"] = irr_result.irr
            
            # Add investment recommendation
            metrics["recommendation"] = await self._generate_investment_recommendation(metrics)
            
            result = {
                "success": True,
                "metrics": metrics,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("calculate_investment_metrics", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "calculate_investment_metrics",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Investment metrics calculation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "FINANCIAL_METRICS_CALCULATION_ERROR",
                "message": "Investment metrics calculation failed"
            }
    
    async def assess_investment_risk(self, investment_data: Dict[str, Any],
                                   user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Assess investment risk and provide risk mitigation recommendations.
        
        Args:
            investment_data: Investment details and market data
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict containing risk assessment results
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "financial_analysis", "assess"
                )
                if validation_error:
                    return validation_error
            
            self.logger.info("Assessing investment risk...")
            
            # Perform risk analysis
            risk_result = await self.financial_analysis_abstraction.analyze_financial_risk(investment_data)
            
            # Generate risk mitigation recommendations
            risk_mitigation = await self._generate_risk_mitigation_recommendations(risk_result)
            
            result = {
                "success": risk_result.success,
                "risk_score": risk_result.risk_score,
                "risk_level": risk_result.risk_level,
                "risk_factors": risk_result.risk_factors,
                "risk_mitigation": risk_mitigation,
                "assessed_at": datetime.utcnow().isoformat(),
                "error": risk_result.error
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("assess_investment_risk", {
                    "risk_score": risk_result.risk_score,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "assess_investment_risk",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Investment risk assessment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "FINANCIAL_RISK_ASSESSMENT_ERROR",
                "message": "Investment risk assessment failed"
            }
    
    async def _generate_overall_assessment(self, roi_result: FinancialAnalysisResult, 
                                         npv_result: Optional[FinancialAnalysisResult],
                                         irr_result: Optional[FinancialAnalysisResult],
                                         payback_result: Optional[FinancialAnalysisResult],
                                         risk_result: FinancialAnalysisResult,
                                         insights_result: FinancialAnalysisResult) -> Dict[str, Any]:
        """Generate overall investment assessment."""
        try:
            # Calculate overall score
            roi_score = min(100, max(0, roi_result.roi_percentage))
            risk_score = (1 - risk_result.risk_score) * 100 if risk_result.success else 50
            
            # Weight the scores
            overall_score = (roi_score * 0.6) + (risk_score * 0.4)
            
            # Determine recommendation
            if overall_score >= 80:
                recommendation = "Strong investment opportunity"
                confidence = "high"
            elif overall_score >= 60:
                recommendation = "Moderate investment opportunity"
                confidence = "medium"
            else:
                recommendation = "High-risk investment, proceed with caution"
                confidence = "low"
            
            return {
                "overall_score": round(overall_score, 1),
                "recommendation": recommendation,
                "confidence": confidence,
                "key_factors": {
                    "roi_percentage": roi_result.roi_percentage,
                    "risk_level": risk_result.risk_level,
                    "npv": npv_result.npv if npv_result and npv_result.success else None,
                    "irr": irr_result.irr if irr_result and irr_result.success else None
                }
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
                "overall_score": 0,
                "recommendation": "Unable to assess",
                "confidence": "low",
                "error": str(e),
                "error_code": "FINANCIAL_ASSESSMENT_GENERATION_ERROR"
            }
    
    async def _generate_investment_recommendation(self, metrics: Dict[str, Any]) -> str:
        """Generate investment recommendation based on metrics."""
        try:
            roi = metrics.get("roi_percentage", 0)
            npv = metrics.get("npv", 0)
            irr = metrics.get("irr", 0)
            
            if roi > 20 and npv > 0 and irr > 15:
                return "Strong investment - proceed"
            elif roi > 10 and npv > 0:
                return "Moderate investment - consider carefully"
            elif roi > 0:
                return "Weak investment - evaluate alternatives"
            else:
                return "Poor investment - avoid"
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_generate_investment_recommendation",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Investment recommendation generation failed: {e}")
            return "Unable to determine recommendation"
    
    async def _generate_risk_mitigation_recommendations(self, risk_result: FinancialAnalysisResult) -> List[str]:
        """Generate risk mitigation recommendations."""
        try:
            recommendations = []
            
            if risk_result.risk_level == "high":
                recommendations.extend([
                    "Implement comprehensive risk monitoring",
                    "Consider phased investment approach",
                    "Establish clear exit strategies"
                ])
            elif risk_result.risk_level == "medium":
                recommendations.extend([
                    "Monitor key risk indicators",
                    "Diversify investment portfolio",
                    "Regular risk assessment reviews"
                ])
            else:
                recommendations.extend([
                    "Standard risk monitoring",
                    "Regular performance reviews"
                ])
            
            return recommendations
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "_generate_risk_mitigation_recommendations",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Risk mitigation recommendations generation failed: {e}")
            return ["Unable to generate recommendations"]
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the Financial Analysis Composition Service.
        
        Returns:
            Dict: Health check result
        """
        try:
            abstraction_health = await self.financial_analysis_abstraction.health_check()
            
            return {
                "healthy": abstraction_health.get("healthy", False),
                "message": "Financial Analysis Composition Service is operational",
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
                self.logger.error(f"❌ Financial Analysis Composition Service health check failed: {e}")
            return {"healthy": False, "error_code": "FINANCIAL_ANALYSIS_HEALTH_CHECK_ERROR", "message": f"Health check failed: {str(e)}"}
