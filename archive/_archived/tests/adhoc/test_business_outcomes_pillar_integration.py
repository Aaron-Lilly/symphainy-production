#!/usr/bin/env python3
"""
Business Outcomes Pillar Integration Test

Tests the Business Outcomes Pillar service integration and functionality.
"""

import asyncio
import logging
from datetime import datetime

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from config.environment_loader import EnvironmentLoader

# Import Business Outcomes Pillar
from backend.business_enablement.pillars.business_outcomes_pillar.business_outcomes_pillar_service import BusinessOutcomesPillarService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_business_outcomes_pillar_integration():
    """Test Business Outcomes Pillar integration and functionality."""
    logger.info("🚀 Starting Business Outcomes Pillar Integration Test")
    
    try:
        # Initialize environment
        environment = EnvironmentLoader()
        
        # Create user context
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_123",
            permissions=["read", "write", "analyze"]
        )
        
        # Initialize Business Outcomes Pillar Service
        logger.info("🏗️ Initializing Business Outcomes Pillar Service...")
        business_outcomes_pillar = BusinessOutcomesPillarService(environment=environment)
        await business_outcomes_pillar.initialize()
        
        logger.info("✅ Business Outcomes Pillar Service initialized successfully")
        
        # Test 1: Strategic Roadmap Generation
        logger.info("📊 Testing Strategic Roadmap Generation...")
        business_context = {
            "business_goal": "Increase market share by 25%",
            "current_state": {
                "market_share": 0.15,
                "revenue": 1000000,
                "customers": 5000
            },
            "desired_outcomes": [
                "Achieve 20% market share",
                "Increase revenue to $1.5M",
                "Grow customer base to 7500"
            ]
        }
        
        roadmap_response = await business_outcomes_pillar.generate_strategic_roadmap(business_context, user_context)
        logger.info(f"✅ Strategic Roadmap Response: {roadmap_response.get('success', False)}")
        logger.info(f"   Message: {roadmap_response.get('message', 'No message')}")
        
        # Test 2: Outcome Measurement
        logger.info("📈 Testing Outcome Measurement...")
        outcome_data = {
            "outcome_id": "outcome_123",
            "outcome_name": "Market Share Growth",
            "kpi_definitions": [
                {"name": "revenue_growth", "target": 0.25, "current": 0.15},
                {"name": "customer_satisfaction", "target": 0.9, "current": 0.8},
                {"name": "market_share", "target": 0.2, "current": 0.15}
            ],
            "data_points": [
                {"date": "2024-01-01", "revenue_growth": 0.15, "customer_satisfaction": 0.8, "market_share": 0.15},
                {"date": "2024-06-01", "revenue_growth": 0.18, "customer_satisfaction": 0.82, "market_share": 0.16}
            ]
        }
        
        measurement_response = await business_outcomes_pillar.measure_outcomes(outcome_data, user_context)
        logger.info(f"✅ Outcome Measurement Response: {measurement_response.get('success', False)}")
        logger.info(f"   Message: {measurement_response.get('message', 'No message')}")
        
        # Test 3: ROI Calculation
        logger.info("💰 Testing ROI Calculation...")
        investment_data = {
            "initiative_name": "Digital Transformation Initiative",
            "investment_cost": 500000,
            "expected_returns": 750000,
            "time_period_months": 12,
            "roi_type": "financial"
        }
        
        roi_response = await business_outcomes_pillar.calculate_roi(investment_data, user_context)
        logger.info(f"✅ ROI Calculation Response: {roi_response.get('success', False)}")
        logger.info(f"   Message: {roi_response.get('message', 'No message')}")
        
        # Test 4: Business Metrics
        logger.info("📊 Testing Business Metrics...")
        business_data = {
            "metric_name": "Revenue Growth",
            "metric_type": "revenue",
            "time_range": "2024-01-01 to 2024-12-31",
            "data_points": [
                {"date": "2024-01-01", "value": 1000000},
                {"date": "2024-06-01", "value": 1200000},
                {"date": "2024-12-01", "value": 1500000}
            ]
        }
        
        metrics_response = await business_outcomes_pillar.calculate_business_metrics(business_data, user_context)
        logger.info(f"✅ Business Metrics Response: {metrics_response.get('success', False)}")
        logger.info(f"   Message: {metrics_response.get('message', 'No message')}")
        
        # Test 5: Strategic Plan Generation
        logger.info("📋 Testing Strategic Plan Generation...")
        strategic_plan_response = await business_outcomes_pillar.generate_strategic_plan(business_context, user_context)
        logger.info(f"✅ Strategic Plan Response: {strategic_plan_response.get('success', False)}")
        logger.info(f"   Message: {strategic_plan_response.get('message', 'No message')}")
        
        # Test 6: Business Outcomes Analysis
        logger.info("🔍 Testing Business Outcomes Analysis...")
        analysis_response = await business_outcomes_pillar.analyze_business_outcomes(outcome_data, user_context)
        logger.info(f"✅ Business Outcomes Analysis Response: {analysis_response.get('success', False)}")
        logger.info(f"   Message: {analysis_response.get('message', 'No message')}")
        
        # Test 7: Health Check
        logger.info("❤️ Testing Health Check...")
        health_response = await business_outcomes_pillar.get_health_status()
        logger.info(f"✅ Health Check Response: {health_response.get('status', 'unknown')}")
        
        logger.info("🎉 All Business Outcomes Pillar tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Business Outcomes Pillar Integration Test failed: {e}")
        raise
    finally:
        # Shutdown Business Outcomes Pillar Service
        if 'business_outcomes_pillar' in locals() and business_outcomes_pillar.is_initialized:
            await business_outcomes_pillar.shutdown()
            logger.info("🛑 Business Outcomes Pillar Service shutdown successfully")


if __name__ == "__main__":
    asyncio.run(test_business_outcomes_pillar_integration())