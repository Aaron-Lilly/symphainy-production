#!/usr/bin/env python3
"""
Business Metrics Infrastructure Abstraction

Infrastructure abstraction for business metrics analysis, coordinating standard and AI adapters.

WHAT (Infrastructure Abstraction Role): I coordinate business metrics capabilities
HOW (Abstraction Implementation): I delegate to standard and AI adapters based on requirements
"""

from typing import Dict, Any, List, Optional
import logging

from ..abstraction_contracts.business_metrics_protocol import BusinessMetricsProtocol, BusinessMetricsResult
from ..infrastructure_adapters.standard_business_metrics_adapter import StandardBusinessMetricsAdapter
from ..infrastructure_adapters.huggingface_business_metrics_adapter import HuggingFaceBusinessMetricsAdapter

class BusinessMetricsAbstraction(BusinessMetricsProtocol):
    """
    Business Metrics Infrastructure Abstraction
    
    Coordinates business metrics analysis using standard and AI-powered adapters.
    """
    
    def __init__(self,
                 standard_adapter: StandardBusinessMetricsAdapter,
                 ai_adapter: HuggingFaceBusinessMetricsAdapter,
                 di_container=None):
        """
        Initialize Business Metrics Abstraction.
        
        Args:
            standard_adapter: Standard business metrics adapter (required via DI)
            ai_adapter: AI-powered business metrics adapter (required via DI)
            di_container: Dependency injection container
        """
        if not standard_adapter:
            raise ValueError("BusinessMetricsAbstraction requires standard_adapter via dependency injection")
        if not ai_adapter:
            raise ValueError("BusinessMetricsAbstraction requires ai_adapter via dependency injection")
        
        self.standard_adapter = standard_adapter
        self.ai_adapter = ai_adapter
        self.di_container = di_container
        self.service_name = "business_metrics_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("🏗️ BusinessMetricsAbstraction initialized")
    
    async def calculate_kpis(self, business_data: Dict[str, Any]) -> BusinessMetricsResult:
        """
        Calculate Key Performance Indicators (KPIs).
        
        Args:
            business_data: Business data for KPI calculation
            
        Returns:
            BusinessMetricsResult: Result of the KPI calculation
        """
        try:
            self.logger.info("Calculating KPIs using standard business metrics adapter...")
            
            # Use standard adapter for KPI calculation
            result = await self.standard_adapter.calculate_kpis(business_data)
            
            if result.success:
                self.logger.info("✅ KPI calculation completed successfully")
                
                # Record platform operation event
            else:
                self.logger.error(f"❌ KPI calculation failed: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate KPIs: {e}")
            raise  # Re-raise for service layer to handle

        """
        Benchmark performance against industry standards.
        
        Args:
            metrics_data: Business metrics data
            industry: Industry for benchmarking
            
        Returns:
            BusinessMetricsResult: Result of the benchmarking
        """
        try:
            self.logger.info(f"Benchmarking performance against {industry} industry standards...")
            
            # Use standard adapter for benchmarking
            result = await self.standard_adapter.benchmark_performance(metrics_data, industry)
            
            if result.success:
                self.logger.info("✅ Performance benchmarking completed successfully")
                
                # Record platform operation event
            else:
                self.logger.error(f"❌ Performance benchmarking failed: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to benchmark performance: {e}")
            raise  # Re-raise for service layer to handle

        """
        Analyze business trends from historical data.
        
        Args:
            historical_data: Historical business data
            
        Returns:
            BusinessMetricsResult: Result of the trend analysis
        """
        try:
            self.logger.info("Analyzing business trends from historical data...")
            
            # Use standard adapter for trend analysis
            result = await self.standard_adapter.analyze_trends(historical_data)
            
            if result.success:
                self.logger.info("✅ Trend analysis completed successfully")
                
                # Record platform operation event
            else:
                self.logger.error(f"❌ Trend analysis failed: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze trends: {e}")
            raise  # Re-raise for service layer to handle

        """
        Analyze business sentiment using AI models.
        
        Args:
            business_data: Business data for sentiment analysis
            
        Returns:
            BusinessMetricsResult: Result of the sentiment analysis
        """
        try:
            self.logger.info("Analyzing business sentiment using AI models...")
            
            # Use AI adapter for sentiment analysis
            result = await self.ai_adapter.analyze_business_sentiment(business_data)
            
            if result.success:
                self.logger.info("✅ Business sentiment analysis completed successfully")
                
                # Record platform operation event
            else:
                self.logger.error(f"❌ Business sentiment analysis failed: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze business sentiment: {e}")
            raise  # Re-raise for service layer to handle

        """
        Predict business performance using AI models.
        
        Args:
            historical_data: Historical business data for prediction
            
        Returns:
            BusinessMetricsResult: Result of the performance prediction
        """
        try:
            self.logger.info("Predicting business performance using AI models...")
            
            # Use AI adapter for performance prediction
            result = await self.ai_adapter.predict_business_performance(historical_data)
            
            if result.success:
                self.logger.info("✅ Business performance prediction completed successfully")
                
                # Record platform operation event
            else:
                self.logger.error(f"❌ Business performance prediction failed: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to predict business performance: {e}")
            raise  # Re-raise for service layer to handle

        """
        Generate AI-powered business insights.
        
        Args:
            business_data: Business data for insight generation
            
        Returns:
            BusinessMetricsResult: Result of the insight generation
        """
        try:
            self.logger.info("Generating AI-powered business insights...")
            
            # Use AI adapter for insight generation
            result = await self.ai_adapter.generate_business_insights(business_data)
            
            if result.success:
                self.logger.info("✅ Business insights generation completed successfully")
                
                # Record platform operation event
            else:
                self.logger.error(f"❌ Business insights generation failed: {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate business insights: {e}")
            raise  # Re-raise for service layer to handle

        """
        Perform health check on the business metrics abstraction.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            self.logger.info("Performing health check on business metrics abstraction...")
            
            # Check standard adapter
            standard_health = await self.standard_adapter.health_check()
            
            # Check AI adapter
            ai_health = await self.ai_adapter.health_check()
            
            # Determine overall health
            overall_status = "healthy"
            if standard_health.get("status") != "healthy":
                overall_status = "degraded"
            if ai_health.get("status") == "unhealthy":
                overall_status = "limited"
            
            return {
                "status": overall_status,
                "abstraction": "BusinessMetricsAbstraction",
                "standard_adapter": standard_health,
                "ai_adapter": ai_health,
                "capabilities": [
                    "kpi_calculation",
                    "performance_benchmarking",
                    "trend_analysis",
                    "business_sentiment_analysis",
                    "performance_prediction",
                    "insight_generation"
                ],
                "last_check": self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
    
            raise  # Re-raise for service layer to handle

        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
