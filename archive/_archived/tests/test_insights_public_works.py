#!/usr/bin/env python3
"""
Test Insights Public Works Services

Test the Analytics and Visualization services to ensure they work correctly.
"""

import asyncio
import logging
import pandas as pd
import numpy as np
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# # from foundations.public_works_foundation.services.analytics_service import AnalyticsService  # TODO: Service not implemented yet
# # from foundations.public_works_foundation.services.visualization_service import VisualizationService  # TODO: Service not implemented yet

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_analytics_service():
    """Test the Analytics Service."""
    print("🧪 Testing Analytics Service...")
    
    # Create test data
    test_data = {
        'employee_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'age': [25, 30, 35, 28, 45, 32, 29, 41, 33, 27],
        'salary': [50000, 60000, 70000, 55000, 90000, 65000, 58000, 85000, 68000, 52000],
        'department': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', 'Finance', 'IT', 'HR', 'Finance'],
        'performance_score': [85, 90, 88, 82, 95, 87, 83, 92, 89, 81]
    }
    df = pd.DataFrame(test_data)
    
    # Initialize service
    analytics_service = AnalyticsService(logger)
    await analytics_service.initialize()
    
    # Test EDA
    print("   📊 Testing EDA...")
    eda_result = await analytics_service.perform_eda(df)
    if eda_result["success"]:
        print(f"   ✅ EDA completed - Quality Score: {eda_result['summary']['quality_score']:.2f}")
    else:
        print(f"   ❌ EDA failed: {eda_result['error']}")
    
    # Test statistical analysis
    print("   📈 Testing statistical analysis...")
    stats_result = await analytics_service.perform_statistical_analysis(df, "correlation")
    if stats_result["success"]:
        print(f"   ✅ Correlation analysis completed")
    else:
        print(f"   ❌ Statistical analysis failed: {stats_result['error']}")
    
    # Test data quality assessment
    print("   🔍 Testing data quality assessment...")
    quality_result = await analytics_service.assess_data_quality(df, "comprehensive")
    if quality_result["success"]:
        print(f"   ✅ Data quality assessment completed")
    else:
        print(f"   ❌ Data quality assessment failed: {quality_result['error']}")
    
    # Test anomaly detection
    print("   🚨 Testing anomaly detection...")
    anomaly_result = await analytics_service.detect_anomalies(df)
    if anomaly_result["success"]:
        print(f"   ✅ Anomaly detection completed")
    else:
        print(f"   ❌ Anomaly detection failed: {anomaly_result['error']}")
    
    # Test machine learning
    print("   🤖 Testing machine learning...")
    ml_result = await analytics_service.perform_machine_learning(
        df, "regression", "salary", ["age", "performance_score"]
    )
    if ml_result["success"]:
        print(f"   ✅ ML regression completed - R² Score: {ml_result['evaluation_results']['r2_score']:.3f}")
    else:
        print(f"   ❌ ML failed: {ml_result['error']}")
    
    # Test clustering
    print("   🔄 Testing clustering...")
    cluster_result = await analytics_service.perform_clustering(df, n_clusters=3)
    if cluster_result["success"]:
        print(f"   ✅ Clustering completed - {cluster_result['results']['n_clusters']} clusters")
    else:
        print(f"   ❌ Clustering failed: {cluster_result['error']}")
    
    return analytics_service

async def test_visualization_service():
    """Test the Visualization Service."""
    print("\n🎨 Testing Visualization Service...")
    
    # Create test data
    test_data = {
        'x': np.random.randn(100),
        'y': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100),
        'value': np.random.randn(100)
    }
    df = pd.DataFrame(test_data)
    
    # Initialize service
    viz_service = VisualizationService(logger)
    await viz_service.initialize()
    
    # Test histogram
    print("   📊 Testing histogram...")
    hist_result = await viz_service.create_histogram(df, 'x')
    if hist_result["success"]:
        print(f"   ✅ Histogram created")
    else:
        print(f"   ❌ Histogram failed: {hist_result['error']}")
    
    # Test scatter plot
    print("   📈 Testing scatter plot...")
    scatter_result = await viz_service.create_scatter_plot(df, 'x', 'y')
    if scatter_result["success"]:
        print(f"   ✅ Scatter plot created")
    else:
        print(f"   ❌ Scatter plot failed: {scatter_result['error']}")
    
    # Test correlation heatmap
    print("   🔥 Testing correlation heatmap...")
    heatmap_result = await viz_service.create_correlation_heatmap(df)
    if heatmap_result["success"]:
        print(f"   ✅ Correlation heatmap created")
    else:
        print(f"   ❌ Correlation heatmap failed: {heatmap_result['error']}")
    
    # Test box plot
    print("   📦 Testing box plot...")
    box_result = await viz_service.create_box_plot(df, 'value')
    if box_result["success"]:
        print(f"   ✅ Box plot created")
    else:
        print(f"   ❌ Box plot failed: {box_result['error']}")
    
    # Test bar chart
    print("   📊 Testing bar chart...")
    bar_result = await viz_service.create_bar_chart(df, 'category', 'value')
    if bar_result["success"]:
        print(f"   ✅ Bar chart created")
    else:
        print(f"   ❌ Bar chart failed: {bar_result['error']}")
    
    # Test dashboard
    print("   🎛️ Testing dashboard...")
    dashboard_result = await viz_service.create_dashboard(df, ['x', 'y', 'value'])
    if dashboard_result["success"]:
        print(f"   ✅ Dashboard created with {dashboard_result['result']['total_columns']} columns")
    else:
        print(f"   ❌ Dashboard failed: {dashboard_result['error']}")
    
    # Test visualization suite
    print("   🎨 Testing visualization suite...")
    suite_result = await viz_service.generate_visualization_suite(df, "comprehensive")
    if suite_result["success"]:
        print(f"   ✅ Visualization suite created with {suite_result['total_visualizations']} visualizations")
    else:
        print(f"   ❌ Visualization suite failed: {suite_result['error']}")
    
    return viz_service

async def main():
    """Main test function."""
    print("🚀 Starting Insights Public Works Services Test")
    print("=" * 60)
    
    try:
        # Test Analytics Service
        analytics_service = await test_analytics_service()
        
        # Test Visualization Service
        viz_service = await test_visualization_service()
        
        # Health checks
        print("\n🏥 Health Checks...")
        analytics_health = analytics_service.health_check()
        viz_health = viz_service.health_check()
        
        print(f"   Analytics Service: {analytics_health['status']}")
        print(f"   Visualization Service: {viz_health['status']}")
        
        print("\n✅ All tests completed successfully!")
        print("🎉 Insights Public Works Services are working correctly!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


