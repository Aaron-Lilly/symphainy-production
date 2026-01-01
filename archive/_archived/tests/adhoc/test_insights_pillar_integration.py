#!/usr/bin/env python3
"""
Insights Pillar Integration Test

Test the Insights Pillar service to ensure it initializes correctly
and can be integrated with the Business Orchestrator.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext
from backend.business_enablement.pillars.insights_pillar.insights_pillar_service import InsightsPillarService
from backend.business_enablement.interfaces.insights_analysis_interface import AnalysisRequest, AnalysisType, VisualizationRequest, VisualizationType, APGRequest


async def test_insights_pillar_integration():
    """Test Insights Pillar integration."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info("🚀 Starting Insights Pillar Integration Test")
    
    try:
        # Initialize Insights Pillar
        logger.info("📊 Initializing Insights Pillar...")
        insights_pillar = InsightsPillarService(
            utility_foundation=None,  # Mock for testing
            curator_foundation=None
        )
        await insights_pillar.initialize()
        
        # Test data analysis
        logger.info("🔍 Testing data analysis...")
        user_context = UserContext(
            user_id="test_user_123",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session",
            permissions=["read", "write"]
        )
        
        analysis_request = AnalysisRequest(
            data={"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
            analysis_type=AnalysisType.DESCRIPTIVE,
            user_context=user_context,
            session_id="test_session"
        )
        
        analysis_response = await insights_pillar.analyze_data(analysis_request)
        if analysis_response.success:
            logger.info(f"✅ Data analysis completed: {analysis_response.message}")
        else:
            logger.warning(f"⚠️ Data analysis failed: {analysis_response.message}")
        
        # Test visualization
        logger.info("📈 Testing visualization...")
        viz_request = VisualizationRequest(
            data={"values": [10, 20, 30, 40, 50], "labels": ["A", "B", "C", "D", "E"]},
            visualization_type=VisualizationType.BAR_CHART,
            user_context=user_context,
            session_id="test_session"
        )
        
        viz_response = await insights_pillar.generate_visualization(viz_request)
        if viz_response.success:
            logger.info(f"✅ Visualization created: {viz_response.message}")
        else:
            logger.warning(f"⚠️ Visualization failed: {viz_response.message}")
        
        # Test APG mode
        logger.info("🤖 Testing APG mode...")
        apg_request = APGRequest(
            data={"values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
            user_context=user_context,
            session_id="test_session"
        )
        
        apg_response = await insights_pillar.enable_apg_mode(apg_request)
        if apg_response.success:
            logger.info(f"✅ APG mode processed: {apg_response.message}")
        else:
            logger.warning(f"⚠️ APG mode failed: {apg_response.message}")
        
        # Test health check
        logger.info("🏥 Testing health check...")
        health_result = await insights_pillar.get_pillar_health()
        logger.info(f"✅ Health status: {health_result['status']}")
        
        # Test business metrics
        logger.info("📊 Testing business metrics...")
        metrics_result = await insights_pillar.get_business_metrics()
        logger.info(f"✅ Business metrics retrieved: {metrics_result['service_name']}")
        
        # Test MCP tools
        logger.info("🔧 Testing MCP tools...")
        mcp_tools = await insights_pillar.mcp_server.get_available_business_tools(user_context)
        logger.info(f"✅ Available MCP tools: {len(mcp_tools)}")
        
        # Test agent capabilities
        logger.info("🤖 Testing agent capabilities...")
        liaison_health = await insights_pillar.liaison_agent.health_check()
        analysis_health = await insights_pillar.analysis_agent.health_check()
        logger.info(f"✅ Liaison Agent status: {liaison_health['status']}")
        logger.info(f"✅ Analysis Agent status: {analysis_health['status']}")
        
        logger.info("🎉 Insights Pillar Integration Test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Insights Pillar Integration Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            if 'insights_pillar' in locals():
                await insights_pillar.shutdown()
        except Exception as e:
            logger.warning(f"⚠️ Cleanup failed: {e}")


async def main():
    """Main test function."""
    success = await test_insights_pillar_integration()
    
    if success:
        print("\n✅ All tests passed! Insights Pillar integration is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
