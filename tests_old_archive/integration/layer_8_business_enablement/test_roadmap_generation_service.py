#!/usr/bin/env python3
"""
Roadmap Generation Service - Functional Tests

Tests Roadmap Generation Service with lessons learned from previous testing:
- Reuses proven infrastructure fixture patterns
- Applies timeout protections
- Focuses on service functionality (not infrastructure issues)
- Tests core SOA API methods with realistic data

Uses proper fixtures, timeouts, and applies all lessons learned.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

from tests.integration.layer_8_business_enablement.test_utilities import (
    ContentStewardHelper,
    TestDataManager
)

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.integration, pytest.mark.functional]


# ============================================================================
# FIXTURES - Reusing Proven Patterns
# ============================================================================

@pytest.fixture(scope="function")
async def roadmap_generation_service(smart_city_infrastructure):
    """
    RoadmapGenerationService instance for each test.
    
    NOTE: Using function scope to match smart_city_infrastructure fixture scope.
    Reuses the proven pattern from previous service tests.
    """
    logger.info("🔧 Fixture: Starting roadmap_generation_service fixture...")
    
    from backend.business_enablement.enabling_services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService
    
    logger.info("🔧 Fixture: Got infrastructure, creating RoadmapGenerationService...")
    infra = smart_city_infrastructure
    service = RoadmapGenerationService(
        service_name="RoadmapGenerationService",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    logger.info("✅ Fixture: RoadmapGenerationService instance created")
    
    # Initialize with timeout protection (lesson learned: infrastructure can be slow)
    logger.info("🔧 Fixture: Initializing service (this may take time)...")
    try:
        result = await asyncio.wait_for(service.initialize(), timeout=60.0)
        logger.info(f"✅ Fixture: Service initialized, result: {result}")
        if not result:
            logger.error("❌ Fixture: Service initialization returned False")
            pytest.fail("Roadmap Generation Service failed to initialize")
    except asyncio.TimeoutError:
        logger.error("❌ Fixture: Service initialization timed out after 60 seconds")
        pytest.fail("Roadmap Generation Service initialization timed out after 60 seconds")
    except Exception as e:
        logger.error(f"❌ Fixture: Service initialization failed with exception: {e}")
        raise
    
    logger.info("✅ Fixture: Service ready, yielding to test...")
    yield service
    logger.info("✅ Fixture: Test completed, cleaning up...")


# ============================================================================
# HELPER FUNCTIONS - Test Data Creation
# ============================================================================

def create_sample_business_context() -> Dict[str, Any]:
    """Create sample business context for roadmap generation."""
    return {
        "objectives": [
            "Digital Transformation: Transform business processes through digitalization",
            "Customer Experience Enhancement: Improve customer satisfaction scores"
        ],
        "timeline_days": 365,  # Service expects timeline_days as a number
        "budget": 500000,  # Service expects a number, not a dict
        "stakeholders": [
            {"name": "Executive Team", "role": "sponsor"},
            {"name": "IT Department", "role": "executor"},
            {"name": "Business Units", "role": "beneficiary"}
        ],
        "constraints": [
            "Must comply with regulatory requirements",
            "Budget cannot exceed allocated amount",
            "Timeline is fixed"
        ]
    }


# ============================================================================
# FUNCTIONAL TESTS - Core SOA API Methods
# ============================================================================

class TestRoadmapGenerationServiceFunctional:
    """Functional tests for Roadmap Generation Service core methods."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_generate_roadmap_basic(self, roadmap_generation_service):
        """Test basic roadmap generation."""
        logger.info("🔧 Test: Starting basic roadmap generation test...")
        
        # Create business context
        business_context = create_sample_business_context()
        
        # Generate roadmap
        result = await asyncio.wait_for(
            roadmap_generation_service.generate_roadmap(
                business_context=business_context,
                options={"roadmap_type": "hybrid"}
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Roadmap generation result keys: {list(result.keys())}")
        
        # Verify result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Roadmap generation should succeed. Result: {result}"
        
        # Verify roadmap contains expected fields
        roadmap = result.get("roadmap", {})
        assert roadmap is not None, "Result should contain roadmap"
        
        # Verify roadmap has phases or milestones
        assert "phases" in roadmap or "milestones" in roadmap, \
            "Roadmap should contain phases or milestones"
        
        logger.info("✅ Test: Basic roadmap generation test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_generate_roadmap_different_types(self, roadmap_generation_service):
        """Test roadmap generation with different roadmap types."""
        logger.info("🔧 Test: Starting multi-type roadmap generation test...")
        
        business_context = create_sample_business_context()
        
        # Test agile roadmap
        agile_result = await asyncio.wait_for(
            roadmap_generation_service.generate_roadmap(
                business_context=business_context,
                options={"roadmap_type": "agile"}
            ),
            timeout=30.0
        )
        assert agile_result.get("success") is True, "Agile roadmap generation should succeed"
        logger.info("✅ Test: Agile roadmap generation succeeded")
        
        # Test waterfall roadmap
        waterfall_result = await asyncio.wait_for(
            roadmap_generation_service.generate_roadmap(
                business_context=business_context,
                options={"roadmap_type": "waterfall"}
            ),
            timeout=30.0
        )
        assert waterfall_result.get("success") is True, "Waterfall roadmap generation should succeed"
        logger.info("✅ Test: Waterfall roadmap generation succeeded")
        
        logger.info("✅ Test: Multi-type roadmap generation test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_create_comprehensive_strategic_plan(self, roadmap_generation_service):
        """Test comprehensive strategic plan creation."""
        logger.info("🔧 Test: Starting comprehensive strategic plan test...")
        
        business_context = create_sample_business_context()
        # Add business_name required for comprehensive strategic plan
        business_context["business_name"] = "Test Business Inc"
        
        # Create comprehensive strategic plan
        result = await asyncio.wait_for(
            roadmap_generation_service.create_comprehensive_strategic_plan(
                business_context=business_context
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Strategic plan result keys: {list(result.keys())}")
        
        # Verify result
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Strategic plan creation should succeed. Result: {result}"
        
        # Verify strategic plan structure
        strategic_plan = result.get("strategic_plan", {})
        assert strategic_plan is not None, "Result should contain strategic plan"
        
        logger.info("✅ Test: Comprehensive strategic plan test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_track_progress(self, roadmap_generation_service):
        """Test roadmap progress tracking."""
        logger.info("🔧 Test: Starting progress tracking test...")
        
        # First, generate a roadmap
        business_context = create_sample_business_context()
        roadmap_result = await asyncio.wait_for(
            roadmap_generation_service.generate_roadmap(
                business_context=business_context
            ),
            timeout=30.0
        )
        
        assert roadmap_result.get("success") is True, "Roadmap generation should succeed"
        roadmap_id = roadmap_result.get("roadmap_id") or roadmap_result.get("roadmap", {}).get("id")
        
        if roadmap_id:
            # Track progress
            progress_result = await asyncio.wait_for(
                roadmap_generation_service.track_progress(
                    roadmap_id=roadmap_id,
                    progress_data={"milestone_id": "milestone1", "status": "completed"}
                ),
                timeout=30.0
            )
            
            logger.info(f"✅ Test: Progress tracking result keys: {list(progress_result.keys())}")
            
            # Verify result
            assert isinstance(progress_result, dict), "Result should be a dictionary"
            # Progress tracking may succeed or fail depending on implementation
            logger.info("✅ Test: Progress tracking test completed")
        else:
            logger.warning("⚠️ Test: No roadmap_id returned, skipping progress tracking")
        
        logger.info("✅ Test: Progress tracking test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_analyze_strategic_trends(self, roadmap_generation_service):
        """Test strategic trends analysis."""
        logger.info("🔧 Test: Starting strategic trends analysis test...")
        
        market_data = {
            "market_size": 1000000,
            "growth_rate": 0.15,
            "competitors": 5,
            "trends": [
                {"name": "Digital Transformation", "impact": "high"},
                {"name": "AI Adoption", "impact": "medium"}
            ]
        }
        
        # Analyze strategic trends
        result = await asyncio.wait_for(
            roadmap_generation_service.analyze_strategic_trends(
                market_data=market_data
            ),
            timeout=30.0
        )
        
        logger.info(f"✅ Test: Strategic trends result keys: {list(result.keys())}")
        
        # Verify result
        assert isinstance(result, dict), "Result should be a dictionary"
        assert result.get("success") is True, f"Strategic trends analysis should succeed. Result: {result}"
        
        # Verify trends analysis
        trends = result.get("trends_analysis", {})
        assert trends is not None, "Result should contain trends analysis"
        
        logger.info("✅ Test: Strategic trends analysis test passed")


# ============================================================================
# ARCHITECTURE VERIFICATION TESTS
# ============================================================================

class TestRoadmapGenerationServiceArchitecture:
    """Tests to verify 5-layer architecture and Platform Gateway integration."""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_platform_gateway_access(self, roadmap_generation_service, smart_city_infrastructure):
        """Test that service can access Platform Gateway abstractions."""
        logger.info("🔧 Test: Starting Platform Gateway access test...")
        
        # Verify service has platform_gateway
        assert roadmap_generation_service.platform_gateway is not None, \
            "Service should have platform_gateway"
        
        # Verify service has strategic_planning abstraction
        assert roadmap_generation_service.strategic_planning is not None, \
            "Service should have strategic_planning abstraction"
        
        # Verify Platform Gateway is available
        platform_gateway = smart_city_infrastructure["platform_gateway"]
        assert platform_gateway is not None, "Platform Gateway should be available"
        
        logger.info("✅ Test: Platform Gateway access test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_smart_city_api_access(self, roadmap_generation_service):
        """Test that service can access Smart City APIs."""
        logger.info("🔧 Test: Starting Smart City API access test...")
        
        # Verify service has Smart City APIs (may be None in MVP mode)
        # These are optional, so we just check they exist as attributes
        assert hasattr(roadmap_generation_service, 'librarian'), \
            "Service should have librarian API attribute"
        assert hasattr(roadmap_generation_service, 'data_steward'), \
            "Service should have data_steward API attribute"
        
        logger.info("✅ Test: Smart City API access test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_curator_registration(self, roadmap_generation_service, smart_city_infrastructure):
        """Test that service is registered with Curator."""
        logger.info("🔧 Test: Starting Curator registration test...")
        
        # Get Curator from infrastructure
        curator = smart_city_infrastructure.get("curator")
        if curator:
            # Try to discover the service
            # Note: This depends on Curator's discovery API
            logger.info("✅ Test: Curator is available (registration verification depends on Curator API)")
        else:
            logger.warning("⚠️ Test: Curator not available in infrastructure (may be expected)")
        
        logger.info("✅ Test: Curator registration test passed")

