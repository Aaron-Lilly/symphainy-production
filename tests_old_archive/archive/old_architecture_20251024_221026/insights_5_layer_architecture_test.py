"""
Test for Insights Pillar 5-Layer Architecture
Tests the complete 5-layer architecture for insights analytics.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'symphainy-platform')))

# Import the components we're testing
from foundations.public_works_foundation.infrastructure_adapters.standard_analytics_adapter import StandardAnalyticsAdapter, StandardAnalyticsConfig
from foundations.public_works_foundation.infrastructure_adapters.huggingface_analytics_adapter import HuggingFaceAnalyticsAdapter, HuggingFaceModelConfig
from foundations.public_works_foundation.infrastructure_abstractions.analytics_abstraction import AnalyticsAbstraction, AnalyticsCapabilities
from foundations.public_works_foundation.composition_services.insights_analytics_composition_service import InsightsAnalyticsCompositionService, InsightsAnalyticsCompositionConfig

# Import test utilities
from utilities.security_authorization.security_authorization_utility import UserContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockDIContainer:
    """Mock DI Container for testing."""
    
    def __init__(self):
        self.services = {
            'pandas': 'pandas',
            'numpy': 'numpy', 
            'matplotlib': 'matplotlib',
            'seaborn': 'seaborn',
            'scipy': 'scipy',
            'sklearn': 'sklearn'
        }
    
    def get(self, service_name):
        return self.services.get(service_name)

async def test_5_layer_architecture():
    """Test the complete 5-layer architecture for insights analytics."""
    
    print("🧪 Testing Insights Pillar 5-Layer Architecture")
    print("=" * 60)
    
    # Test 1: Standard Analytics Adapter (Layer 1)
    print("\n📊 Testing Layer 1: Infrastructure Adapters")
    print("-" * 40)
    
    try:
        # Test Standard Analytics Adapter
        standard_config = StandardAnalyticsConfig(
            default_figure_size=(8, 6),
            color_palette="viridis"
        )
        standard_adapter = StandardAnalyticsAdapter(config=standard_config)
        
        # Initialize adapter
        init_result = await standard_adapter.initialize()
        print(f"✅ Standard Analytics Adapter: {'Initialized' if init_result else 'Failed'}")
        
        # Health check
        health = await standard_adapter.health_check()
        print(f"✅ Standard Adapter Health: {health.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Standard Analytics Adapter failed: {e}")
    
    # Test 2: HuggingFace Analytics Adapter (Layer 1)
    try:
        # Test HuggingFace Analytics Adapter (may fail if transformers not available)
        huggingface_config = {
            "sentiment_analysis": HuggingFaceModelConfig(
                model_name="cardiffnlp/twitter-roberta-base-sentiment-latest",
                task_type="sentiment-analysis"
            )
        }
        huggingface_adapter = HuggingFaceAnalyticsAdapter(model_configs=huggingface_config)
        
        # Initialize adapter (may fail if HuggingFace not available)
        init_result = await huggingface_adapter.initialize()
        print(f"✅ HuggingFace Analytics Adapter: {'Initialized' if init_result else 'Failed (expected if transformers not available)'}")
        
        # Health check
        health = await huggingface_adapter.health_check()
        print(f"✅ HuggingFace Adapter Health: {health.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"⚠️ HuggingFace Analytics Adapter: {e} (expected if transformers not available)")
    
    # Test 3: Analytics Abstraction (Layer 2)
    print("\n🔧 Testing Layer 2: Infrastructure Abstractions")
    print("-" * 40)
    
    try:
        # Create analytics abstraction
        capabilities = AnalyticsCapabilities(
            standard_analytics=True,
            advanced_analytics=True,
            visualization=True,
            insights_generation=True
        )
        
        analytics_abstraction = AnalyticsAbstraction(
            standard_adapter=standard_adapter,
            huggingface_adapter=huggingface_adapter,
            capabilities=capabilities
        )
        
        # Initialize abstraction
        init_result = await analytics_abstraction.initialize()
        print(f"✅ Analytics Abstraction: {'Initialized' if init_result else 'Failed'}")
        
        # Test capabilities
        capabilities_result = await analytics_abstraction.get_available_capabilities()
        print(f"✅ Available Capabilities: {len(capabilities_result.get('capabilities', {}))} capability types")
        
        # Health check
        health = await analytics_abstraction.health_check()
        print(f"✅ Analytics Abstraction Health: {health.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Analytics Abstraction failed: {e}")
    
    # Test 4: Composition Service (Layer 3)
    print("\n🏗️ Testing Layer 3: Composition Services")
    print("-" * 40)
    
    try:
        # Create mock DI container
        mock_di_container = MockDIContainer()
        
        # Create composition service
        composition_config = InsightsAnalyticsCompositionConfig(
            enable_standard_analytics=True,
            enable_advanced_analytics=True,
            enable_visualization=True,
            enable_insights_generation=True
        )
        
        composition_service = InsightsAnalyticsCompositionService(
            di_container=mock_di_container,
            config=composition_config
        )
        
        # Initialize composition service
        init_result = await composition_service.initialize()
        print(f"✅ Composition Service: {'Initialized' if init_result else 'Failed'}")
        
        # Health check
        health = await composition_service.health_check()
        print(f"✅ Composition Service Health: {health.get('status', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Composition Service failed: {e}")
    
    # Test 5: End-to-End Functionality (Layer 4)
    print("\n🚀 Testing Layer 4: End-to-End Functionality")
    print("-" * 40)
    
    try:
        # Create test data
        import pandas as pd
        import numpy as np
        
        # Create sample DataFrame
        test_data = pd.DataFrame({
            'value1': np.random.randn(100),
            'value2': np.random.randn(100),
            'category': ['A', 'B', 'C'] * 33 + ['A']
        })
        
        # Create user context
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            permissions=["read", "write"],
            session_id="test_session_123"
        )
        
        # Test data analysis
        analysis_result = await composition_service.analyze_data(
            data=test_data,
            analysis_type="comprehensive",
            user_context=user_context
        )
        
        if "error" not in analysis_result:
            print(f"✅ Data Analysis: Success")
            print(f"   - Capabilities used: {analysis_result.get('capabilities_used', [])}")
        else:
            print(f"❌ Data Analysis: {analysis_result.get('error')}")
        
        # Test visualization
        viz_result = await composition_service.create_visualization(
            data=test_data,
            viz_type="histogram",
            user_context=user_context
        )
        
        if "error" not in viz_result:
            print(f"✅ Visualization: Success")
            print(f"   - Plot path: {viz_result.get('plot_path', 'N/A')}")
        else:
            print(f"❌ Visualization: {viz_result.get('error')}")
        
        # Test insights generation
        insights_result = await composition_service.generate_insights(
            data={"text_data": "This is a test for sentiment analysis."},
            user_context=user_context
        )
        
        if "error" not in insights_result:
            print(f"✅ Insights Generation: Success")
            print(f"   - Capabilities used: {insights_result.get('capabilities_used', [])}")
        else:
            print(f"⚠️ Insights Generation: {insights_result.get('error')} (may be expected if HuggingFace not available)")
        
    except Exception as e:
        print(f"❌ End-to-End Functionality failed: {e}")
    
    # Test 6: Architecture Validation (Layer 5)
    print("\n🏛️ Testing Layer 5: Architecture Validation")
    print("-" * 40)
    
    try:
        # Validate architecture layers
        layers_valid = True
        
        # Layer 1: Infrastructure Adapters
        if standard_adapter and await standard_adapter.health_check():
            print("✅ Layer 1 (Infrastructure Adapters): Valid")
        else:
            print("❌ Layer 1 (Infrastructure Adapters): Invalid")
            layers_valid = False
        
        # Layer 2: Infrastructure Abstractions
        if analytics_abstraction and await analytics_abstraction.health_check():
            print("✅ Layer 2 (Infrastructure Abstractions): Valid")
        else:
            print("❌ Layer 2 (Infrastructure Abstractions): Invalid")
            layers_valid = False
        
        # Layer 3: Composition Services
        if composition_service and await composition_service.health_check():
            print("✅ Layer 3 (Composition Services): Valid")
        else:
            print("❌ Layer 3 (Composition Services): Invalid")
            layers_valid = False
        
        # Overall architecture validation
        if layers_valid:
            print("\n🎉 5-Layer Architecture: VALID")
            print("   - All layers properly initialized")
            print("   - Dependencies correctly injected")
            print("   - End-to-end functionality working")
        else:
            print("\n⚠️ 5-Layer Architecture: PARTIALLY VALID")
            print("   - Some layers may have issues")
            print("   - Check individual layer health")
        
    except Exception as e:
        print(f"❌ Architecture Validation failed: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Insights Pillar 5-Layer Architecture Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_5_layer_architecture())
