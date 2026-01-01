#!/usr/bin/env python3
"""
Financial Analysis Abstraction

Infrastructure abstraction for financial analysis capabilities.

WHAT (Infrastructure Abstraction Role): I provide a unified interface for financial analysis
HOW (Abstraction Implementation): I coordinate financial analysis adapters
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
import logging

from ..abstraction_contracts.financial_analysis_protocol import FinancialAnalysisProtocol, FinancialAnalysisResult
from ..infrastructure_adapters.standard_financial_adapter import StandardFinancialAdapter

# HuggingFace adapter is optional (in future_abstractions/ for future use)
if TYPE_CHECKING:
    from ..infrastructure_adapters.future_abstractions.huggingface_financial_adapter import HuggingFaceFinancialAdapter
else:
    try:
        from ..infrastructure_adapters.future_abstractions.huggingface_financial_adapter import HuggingFaceFinancialAdapter
    except ImportError:
        self.logger.error(f"❌ Error: {e}")
        HuggingFaceFinancialAdapter = None  # Not available - will be None

        raise  # Re-raise for service layer to handle

class FinancialAnalysisAbstraction(FinancialAnalysisProtocol):
    """
    Financial Analysis Abstraction
    
    Provides a unified interface for financial analysis by coordinating
    underlying financial analysis adapters.
    """
    
    def __init__(self, standard_financial_adapter: StandardFinancialAdapter, 
                 huggingface_financial_adapter: Optional[Any] = None,
                 di_container=None):
        """
        Initialize Financial Analysis Abstraction.
        
        Args:
            standard_financial_adapter: The standard financial adapter to use.
            huggingface_financial_adapter: Optional HuggingFace financial adapter for AI-powered analysis.
            di_container: Dependency injection container
        """
        self.standard_financial_adapter = standard_financial_adapter
        self.huggingface_financial_adapter = huggingface_financial_adapter
        self.di_container = di_container
        self.service_name = "financial_analysis_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("🏗️ FinancialAnalysisAbstraction initialized")
    
    async def calculate_roi(self, investment_data: Dict[str, Any]) -> FinancialAnalysisResult:
        """
        Calculate Return on Investment (ROI) and related financial metrics.
        
        Args:
            investment_data: Investment details and expected returns
            
        Returns:
            FinancialAnalysisResult: Result of the ROI calculation
        """
        try:
            self.logger.debug("Delegating ROI calculation to standard adapter...")
            result = await self.standard_financial_adapter.calculate_roi(investment_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ ROI calculation failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Calculate Net Present Value (NPV) for a series of cash flows.
        
        Args:
            cash_flows: List of cash flows (negative for investments, positive for returns)
            discount_rate: Discount rate for NPV calculation
            
        Returns:
            FinancialAnalysisResult: Result of the NPV calculation
        """
        try:
            self.logger.debug("Delegating NPV calculation to standard adapter...")
            result = await self.standard_financial_adapter.calculate_npv(cash_flows, discount_rate)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ NPV calculation failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Calculate Internal Rate of Return (IRR) for a series of cash flows.
        
        Args:
            cash_flows: List of cash flows
            
        Returns:
            FinancialAnalysisResult: Result of the IRR calculation
        """
        try:
            self.logger.debug("Delegating IRR calculation to standard adapter...")
            result = await self.standard_financial_adapter.calculate_irr(cash_flows)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ IRR calculation failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Calculate payback period for an investment.
        
        Args:
            initial_investment: Initial investment amount
            annual_cash_flow: Annual cash flow amount
            
        Returns:
            FinancialAnalysisResult: Result of the payback period calculation
        """
        try:
            self.logger.debug("Delegating payback period calculation to standard adapter...")
            result = await self.standard_financial_adapter.calculate_payback_period(initial_investment, annual_cash_flow)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Payback period calculation failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Analyze financial risk using AI models.
        
        Args:
            investment_data: Investment details and market data
            
        Returns:
            FinancialAnalysisResult: Result of the risk analysis
        """
        try:
            if self.huggingface_financial_adapter:
                self.logger.debug("Delegating risk analysis to HuggingFace adapter...")
                result = await self.huggingface_financial_adapter.analyze_financial_risk(investment_data)
            else:
                self.logger.warning("HuggingFace adapter not available, using standard risk assessment...")
                result = await self._standard_risk_assessment(investment_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Risk analysis failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Predict financial performance using AI models.
        
        Args:
            historical_data: Historical financial data for prediction
            
        Returns:
            FinancialAnalysisResult: Result of the performance prediction
        """
        try:
            if self.huggingface_financial_adapter:
                self.logger.debug("Delegating performance prediction to HuggingFace adapter...")
                return await self.huggingface_financial_adapter.predict_financial_performance(historical_data)
            else:
                self.logger.warning("HuggingFace adapter not available, using standard prediction...")
                return await self._standard_performance_prediction(historical_data)
        except Exception as e:
            self.logger.error(f"❌ Performance prediction failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """
        Generate financial insights using AI models.
        
        Args:
            financial_data: Financial data for insight generation
            
        Returns:
            FinancialAnalysisResult: Result of the insight generation
        """
        try:
            if self.huggingface_financial_adapter:
                self.logger.debug("Delegating insight generation to HuggingFace adapter...")
                result = await self.huggingface_financial_adapter.generate_financial_insights(financial_data)
            else:
                self.logger.warning("HuggingFace adapter not available, using standard insights...")
                result = await self._standard_insight_generation(financial_data)
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Insight generation failed at abstraction level: {e}")
            raise  # Re-raise for service layer to handle

        """Fallback standard risk assessment when AI adapter is not available."""
        try:
            # Simple risk assessment based on investment data
            volatility = investment_data.get("volatility", 0.1)
            time_period = investment_data.get("time_period_years", 1)
            
            # Calculate basic risk score
            risk_score = min(1.0, volatility * (1 + time_period * 0.1))
            risk_level = "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high"
            
            risk_factors = []
            if volatility > 0.2:
                risk_factors.append("High volatility detected")
            if time_period > 5:
                risk_factors.append("Long-term investment risk")
            
            return FinancialAnalysisResult(
                success=True,
                risk_score=risk_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                metadata={
                    "assessment_method": "standard",
                    "volatility": volatility,
                    "time_period_years": time_period
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            raise  # Re-raise for service layer to handle

        """Fallback standard performance prediction when AI adapter is not available."""
        try:
            # Simple performance prediction based on historical data
            historical_roi = historical_data.get("historical_roi", 0.1)
            market_trend = historical_data.get("market_trend", "stable")
            
            # Adjust prediction based on market trend
            if market_trend == "growing":
                predicted_roi = historical_roi * 1.2
            elif market_trend == "declining":
                predicted_roi = historical_roi * 0.8
            else:
                predicted_roi = historical_roi
            
            return FinancialAnalysisResult(
                success=True,
                predicted_roi=predicted_roi,
                confidence_interval={
                    "lower_bound": predicted_roi * 0.8,
                    "upper_bound": predicted_roi * 1.2,
                    "confidence_level": 0.8
                },
                metadata={
                    "prediction_method": "standard",
                    "historical_roi": historical_roi,
                    "market_trend": market_trend
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            raise  # Re-raise for service layer to handle

        """Fallback standard insight generation when AI adapter is not available."""
        try:
            # Simple insight generation based on financial data
            roi = financial_data.get("roi_percentage", 0)
            insights = []
            recommendations = []
            
            if roi > 20:
                insights.append("Strong ROI potential identified")
                recommendations.append("Consider proceeding with investment")
            elif roi > 10:
                insights.append("Moderate ROI potential")
                recommendations.append("Evaluate risk factors carefully")
            else:
                insights.append("Low ROI potential")
                recommendations.append("Consider alternative investments")
            
            return FinancialAnalysisResult(
                success=True,
                insights=insights,
                recommendations=recommendations,
                market_sentiment="neutral",
                metadata={
                    "insight_method": "standard",
                    "roi_percentage": roi
                }
            )
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
            raise  # Re-raise for service layer to handle

        """
        Perform a health check for the Financial Analysis Abstraction.
        
        Returns:
            Dict: Health check result
        """
        try:
            standard_health = await self.standard_financial_adapter.health_check()
            huggingface_health = None
            
            if self.huggingface_financial_adapter:
                huggingface_health = await self.huggingface_financial_adapter.health_check()
            
            return {
                "healthy": standard_health.get("healthy", False),
                "message": "Financial Analysis Abstraction is operational",
                "standard_adapter_health": standard_health,
                "huggingface_adapter_health": huggingface_health
            }
        except Exception as e:
            self.logger.error(f"❌ Financial Analysis Abstraction health check failed: {e}")

            raise  # Re-raise for service layer to handle
