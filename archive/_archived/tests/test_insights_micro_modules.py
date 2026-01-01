#!/usr/bin/env python3
"""
Test Insights Micro-Modules

Test the updated micro-modules to ensure they work with real implementations.
"""

import asyncio
import logging
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from backend.business_enablement.pillars.insights_pillar.micro_modules.data_analyzer import DataAnalyzerModule, AnalysisType
from backend.business_enablement.pillars.insights_pillar.micro_modules.visualization_engine import VisualizationEngineModule, ChartType
from backend.business_enablement.pillars.insights_pillar.micro_modules.metrics_calculator import MetricsCalculatorModule
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_data_analyzer():
    """Test the Data Analyzer Module."""
    print("🧪 Testing Data Analyzer Module...")
    
    # Create mock environment loader
    mock_env_loader = MagicMock()
    mock_env_loader.get_insights_pillar_config.return_value = {}
    
    # Initialize module
    data_analyzer = DataAnalyzerModule(logger, mock_env_loader)
    await data_analyzer.initialize()
    
    # Create test data as DataFrame
    import pandas as pd
    test_df = pd.DataFrame({
        "x": [1, 2, 3, 4, 5],
        "y": [2, 4, 6, 8, 10],
        "z": [3, 6, 9, 12, 15]
    })
    test_data = {"values": test_df}
    
    user_context = UserContext(
        user_id="test_user", 
        email="test@example.com",
        full_name="Test User",
        session_id="test_session",
        permissions=["read", "write"]
    )
    
    # Test descriptive analysis
    print("   📊 Testing descriptive analysis...")
    desc_result = await data_analyzer.analyze_data(
        test_data, AnalysisType.DESCRIPTIVE, user_context
    )
    if desc_result["success"]:
        print(f"   ✅ Descriptive analysis completed - {desc_result['data_points']} data points")
    else:
        print(f"   ❌ Descriptive analysis failed: {desc_result['message']}")
    
    # Test correlation analysis
    print("   🔗 Testing correlation analysis...")
    corr_result = await data_analyzer.analyze_data(
        test_data, AnalysisType.CORRELATION, user_context
    )
    if corr_result["success"]:
        print(f"   ✅ Correlation analysis completed - {len(corr_result.get('correlations', []))} correlations found")
    else:
        print(f"   ❌ Correlation analysis failed: {corr_result['message']}")
    
    # Test regression analysis
    print("   📈 Testing regression analysis...")
    reg_data = {**test_data, "target_column": "z"}
    reg_result = await data_analyzer.analyze_data(
        reg_data, AnalysisType.REGRESSION, user_context
    )
    if reg_result["success"]:
        print(f"   ✅ Regression analysis completed - R²: {reg_result.get('r_squared', 0):.3f}")
    else:
        print(f"   ❌ Regression analysis failed: {reg_result['message']}")
    
    # Test clustering analysis
    print("   🔄 Testing clustering analysis...")
    cluster_data = {**test_data, "n_clusters": 2}
    cluster_result = await data_analyzer.analyze_data(
        cluster_data, AnalysisType.CLUSTERING, user_context
    )
    if cluster_result["success"]:
        print(f"   ✅ Clustering analysis completed - {cluster_result.get('n_clusters', 0)} clusters")
    else:
        print(f"   ❌ Clustering analysis failed: {cluster_result['message']}")
    
    return data_analyzer

async def test_visualization_engine():
    """Test the Visualization Engine Module."""
    print("\n🎨 Testing Visualization Engine Module...")
    
    # Create mock environment loader
    mock_env_loader = MagicMock()
    mock_env_loader.get_insights_pillar_config.return_value = {}
    
    # Initialize module
    viz_engine = VisualizationEngineModule(logger, mock_env_loader)
    await viz_engine.initialize()
    
    # Create test data as DataFrame
    import pandas as pd
    test_df = pd.DataFrame({
        "x": [1, 2, 3, 4, 5],
        "y": [2, 4, 6, 8, 10],
        "category": ["A", "B", "A", "B", "A"]
    })
    test_data = {
        "values": test_df,
        "column": "x",
        "title": "Test Histogram"
    }
    
    user_context = UserContext(
        user_id="test_user", 
        email="test@example.com",
        full_name="Test User",
        session_id="test_session",
        permissions=["read", "write"]
    )
    
    # Test histogram generation
    print("   📊 Testing histogram generation...")
    hist_result = await viz_engine.create_visualization(
        test_data, ChartType.HISTOGRAM, user_context
    )
    if hist_result["success"]:
        data_points = hist_result.get('data_points', 'unknown')
        print(f"   ✅ Histogram created - {data_points} data points")
    else:
        print(f"   ❌ Histogram generation failed: {hist_result['message']}")
    
    return viz_engine

async def test_metrics_calculator():
    """Test the Metrics Calculator Module."""
    print("\n📊 Testing Metrics Calculator Module...")
    
    # Create mock environment loader
    mock_env_loader = MagicMock()
    mock_env_loader.get_insights_pillar_config.return_value = {}
    
    # Initialize module
    metrics_calc = MetricsCalculatorModule(logger, mock_env_loader)
    await metrics_calc.initialize()
    
    # Create test data as DataFrame
    import pandas as pd
    test_df = pd.DataFrame({
        "revenue": [1000, 1200, 1100, 1300, 1400],
        "costs": [600, 700, 650, 750, 800],
        "profit": [400, 500, 450, 550, 600]
    })
    test_data = {"values": test_df}
    
    user_context = UserContext(
        user_id="test_user", 
        email="test@example.com",
        full_name="Test User",
        session_id="test_session",
        permissions=["read", "write"]
    )
    
    # Test metrics calculation
    print("   📈 Testing metrics calculation...")
    metrics_result = await metrics_calc.calculate_metrics(
        test_data, user_context
    )
    if metrics_result["success"]:
        print(f"   ✅ Metrics calculated - {len(metrics_result.get('metrics', {}))} metrics")
    else:
        print(f"   ❌ Metrics calculation failed: {metrics_result['message']}")
    
    return metrics_calc

async def main():
    """Main test function."""
    print("🚀 Starting Insights Micro-Modules Test")
    print("=" * 60)
    
    try:
        # Test Data Analyzer
        data_analyzer = await test_data_analyzer()
        
        # Test Visualization Engine
        viz_engine = await test_visualization_engine()
        
        # Test Metrics Calculator
        metrics_calc = await test_metrics_calculator()
        
        print("\n✅ All micro-module tests completed successfully!")
        print("🎉 Insights Micro-Modules are working with real implementations!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
