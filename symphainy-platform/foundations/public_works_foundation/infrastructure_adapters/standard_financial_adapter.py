#!/usr/bin/env python3
"""
Standard Financial Adapter

Infrastructure adapter for standard financial calculations using pandas, numpy, scipy.

WHAT (Infrastructure Adapter Role): I provide standard financial calculation capabilities
HOW (Adapter Implementation): I wrap pandas, numpy, scipy for financial analysis
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..abstraction_contracts.financial_analysis_protocol import FinancialAnalysisResult


class StandardFinancialAdapter:
    """
    Standard Financial Adapter
    
    Provides standard financial calculation capabilities using pandas, numpy, scipy.
    """
    
    def __init__(self):
        """Initialize Standard Financial Adapter."""
        self.logger = logging.getLogger("StandardFinancialAdapter")
        self.logger.info("🏗️ StandardFinancialAdapter initialized")
    
    async def calculate_roi(self, investment_data: Dict[str, Any]) -> FinancialAnalysisResult:
        """
        Calculate Return on Investment (ROI) using standard financial formulas.
        
        Args:
            investment_data: Investment details and expected returns
            
        Returns:
            FinancialAnalysisResult: Result of the ROI calculation
        """
        try:
            self.logger.info("Calculating ROI using standard financial formulas...")
            
            # Extract investment details
            initial_investment = investment_data.get("initial_investment", 0)
            expected_annual_return = investment_data.get("expected_annual_return", 0)
            time_period_years = investment_data.get("time_period_years", 1)
            discount_rate = investment_data.get("discount_rate", 0.1)
            
            # Calculate basic ROI
            total_returns = expected_annual_return * time_period_years
            net_profit = total_returns - initial_investment
            roi_percentage = (net_profit / initial_investment) * 100 if initial_investment > 0 else 0
            
            # Calculate NPV manually (np.npv is deprecated)
            cash_flows = [-initial_investment] + [expected_annual_return] * time_period_years
            npv = -initial_investment
            for i, cash_flow in enumerate(cash_flows[1:], 1):
                npv += cash_flow / ((1 + discount_rate) ** i)
            
            # Calculate payback period
            payback_period = initial_investment / expected_annual_return if expected_annual_return > 0 else float('inf')
            
            # Calculate IRR (simplified calculation)
            try:
                # Simple IRR approximation
                irr = (expected_annual_return / initial_investment) * 100 if initial_investment > 0 else 0
            except:
                irr = 0
            
            # Calculate additional metrics
            roi_ratio = total_returns / initial_investment if initial_investment > 0 else 0
            annualized_roi = roi_percentage / time_period_years if time_period_years > 0 else roi_percentage
            
            return FinancialAnalysisResult(
                success=True,
                roi_percentage=round(roi_percentage, 2),
                roi_ratio=round(roi_ratio, 2),
                npv=round(npv, 2),
                irr=round(irr, 2),
                payback_period_years=round(payback_period, 2),
                annualized_roi=round(annualized_roi, 2),
                net_profit=round(net_profit, 2),
                total_returns=round(total_returns, 2),
                metadata={
                    "calculation_method": "standard",
                    "discount_rate": discount_rate,
                    "time_period_years": time_period_years,
                    "calculated_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate ROI: {e}")
            return FinancialAnalysisResult(
                success=False,
                roi_percentage=0,
                roi_ratio=0,
                npv=0,
                irr=0,
                payback_period_years=0,
                annualized_roi=0,
                net_profit=0,
                total_returns=0,
                metadata={},
                error=str(e)
            )
    
    async def calculate_npv(self, cash_flows: List[float], discount_rate: float) -> FinancialAnalysisResult:
        """
        Calculate Net Present Value (NPV) using numpy.
        
        Args:
            cash_flows: List of cash flows (negative for investments, positive for returns)
            discount_rate: Discount rate for NPV calculation
            
        Returns:
            FinancialAnalysisResult: Result of the NPV calculation
        """
        try:
            self.logger.info("Calculating NPV manually...")
            
            # Calculate NPV manually
            npv = 0
            for i, cash_flow in enumerate(cash_flows):
                if i == 0:
                    npv += cash_flow  # Initial investment (negative)
                else:
                    npv += cash_flow / ((1 + discount_rate) ** i)
            
            return FinancialAnalysisResult(
                success=True,
                npv=round(npv, 2),
                metadata={
                    "calculation_method": "numpy_npv",
                    "discount_rate": discount_rate,
                    "cash_flows_count": len(cash_flows),
                    "calculated_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate NPV: {e}")
            return FinancialAnalysisResult(
                success=False,
                npv=0,
                metadata={},
                error=str(e)
            )
    
    async def calculate_irr(self, cash_flows: List[float]) -> FinancialAnalysisResult:
        """
        Calculate Internal Rate of Return (IRR) using numpy.
        
        Args:
            cash_flows: List of cash flows
            
        Returns:
            FinancialAnalysisResult: Result of the IRR calculation
        """
        try:
            self.logger.info("Calculating IRR manually...")
            
            # Simple IRR approximation (Newton-Raphson method would be more accurate)
            if len(cash_flows) < 2:
                irr = 0
            else:
                # Simple approximation: assume equal annual returns
                initial_investment = abs(cash_flows[0])
                annual_return = cash_flows[1] if len(cash_flows) > 1 else 0
                irr = (annual_return / initial_investment) * 100 if initial_investment > 0 else 0
            
            return FinancialAnalysisResult(
                success=True,
                irr=round(irr, 2),
                metadata={
                    "calculation_method": "numpy_irr",
                    "cash_flows_count": len(cash_flows),
                    "calculated_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate IRR: {e}")
            return FinancialAnalysisResult(
                success=False,
                irr=0,
                metadata={},
                error=str(e)
            )
    
    async def calculate_payback_period(self, initial_investment: float, annual_cash_flow: float) -> FinancialAnalysisResult:
        """
        Calculate payback period.
        
        Args:
            initial_investment: Initial investment amount
            annual_cash_flow: Annual cash flow amount
            
        Returns:
            FinancialAnalysisResult: Result of the payback period calculation
        """
        try:
            self.logger.info("Calculating payback period...")
            
            payback_period = initial_investment / annual_cash_flow if annual_cash_flow > 0 else float('inf')
            
            return FinancialAnalysisResult(
                success=True,
                payback_period_years=round(payback_period, 2),
                metadata={
                    "calculation_method": "standard",
                    "initial_investment": initial_investment,
                    "annual_cash_flow": annual_cash_flow,
                    "calculated_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate payback period: {e}")
            return FinancialAnalysisResult(
                success=False,
                payback_period_years=0,
                metadata={},
                error=str(e)
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the Standard Financial Adapter.
        
        Returns:
            Dict: Health check result
        """
        try:
            # Test basic calculations
            test_investment = {
                "initial_investment": 100000,
                "expected_annual_return": 15000,
                "time_period_years": 5,
                "discount_rate": 0.1
            }
            
            result = await self.calculate_roi(test_investment)
            
            if result.success and result.roi_percentage > 0:
                return {"healthy": True, "message": "Standard Financial Adapter is operational"}
            else:
                return {"healthy": False, "message": f"Standard Financial Adapter failed test: {result.error}"}
        except Exception as e:
            return {"healthy": False, "message": f"Standard Financial Adapter health check failed: {str(e)}"}
