#!/usr/bin/env python3
"""
Experience Dimension Integration Test

Tests the complete Experience Dimension integration:
1. Experience Manager
2. Journey Manager  
3. Frontend Integration Service

This test validates the Experience Dimension components and their integration
with the extracted working patterns from business_orchestrator_old.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the Experience Dimension services
from experience.services.frontend_integration_service import frontend_integration_service
from experience.services.experience_manager_service import experience_manager_service
from experience.services.journey_manager_service import journey_manager_service

# Import interfaces and types
from experience.interfaces.frontend_integration_interface import APIEndpoint, RequestMethod, DataFormat
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperienceDimensionIntegrationTest:
    """Experience Dimension integration test suite."""
    
    def __init__(self):
        self.test_results = {}
        self.user_context = None
        self.session_token = None
        
    async def setup_test_environment(self):
        """Set up the test environment with user context and session."""
        logger.info("🔧 Setting up test environment...")
        
        # Create test user context
        self.user_context = UserContext(
            user_id="experience_test_user_123",
            full_name="Experience Test User",
            email="experience.test@example.com",
            session_id="experience_test_session_123",
            permissions=["read", "write", "analyze", "visualize", "manage"]
        )
        
        # Generate session token
        self.session_token = f"experience_test_session_{int(datetime.now().timestamp())}"
        
        logger.info("✅ Test environment setup complete")
        
    async def test_experience_dimension_initialization(self):
        """Test 1: Experience Dimension services initialization."""
        logger.info("🧪 Test 1: Experience Dimension services initialization")
        
        try:
            # Initialize Experience Dimension services
            await frontend_integration_service.initialize()
            await experience_manager_service.initialize()
            await journey_manager_service.initialize()
            
            # Test health checks
            frontend_health = await frontend_integration_service.get_service_health()
            experience_health = await experience_manager_service.get_service_health()
            journey_health = await journey_manager_service.get_service_health()
            
            # Validate health status
            assert frontend_health.get('status') == 'healthy', "Frontend Integration should be healthy"
            assert experience_health.get('status') == 'healthy', "Experience Manager should be healthy"
            assert journey_health.get('status') == 'healthy', "Journey Manager should be healthy"
            
            self.test_results['experience_dimension_init'] = {
                'success': True,
                'frontend_integration': frontend_health,
                'experience_manager': experience_health,
                'journey_manager': journey_health
            }
            
            logger.info("✅ Experience Dimension services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Experience Dimension initialization failed: {e}")
            self.test_results['experience_dimension_init'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_frontend_integration_api_routing(self):
        """Test 2: Frontend Integration API routing with extracted patterns."""
        logger.info("🧪 Test 2: Frontend Integration API routing")
        
        try:
            # Test routing to different pillars using extracted patterns
            test_endpoints = [
                (APIEndpoint.INSIGHTS_HEALTH, "insights"),
                (APIEndpoint.INSIGHTS_ANALYZE, "insights"),
                (APIEndpoint.INSIGHTS_VISUALIZE, "insights"),
                (APIEndpoint.INSIGHTS_CHAT, "insights"),
                (APIEndpoint.CONTENT_UPLOAD, "content"),
                (APIEndpoint.OPERATIONS_HEALTH, "operations"),
                (APIEndpoint.BUSINESS_OUTCOMES_STRATEGIC_PLAN, "business_outcomes")
            ]
            
            routing_results = {}
            
            for endpoint, expected_pillar in test_endpoints:
                # Test API routing
                response = await frontend_integration_service.route_api_request(
                    endpoint=endpoint,
                    method=RequestMethod.GET,
                    user_context=self.user_context,
                    session_token=self.session_token
                )
                
                # Validate response
                assert response.get('success') is True, f"API routing should succeed for {endpoint.value}"
                
                routing_results[endpoint.value] = {
                    'success': True,
                    'expected_pillar': expected_pillar,
                    'response': response
                }
                
                logger.info(f"  ✅ {endpoint.value} -> {expected_pillar}")
            
            self.test_results['api_routing'] = {
                'success': True,
                'routing_results': routing_results
            }
            
            logger.info("✅ Frontend Integration API routing successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ API routing failed: {e}")
            self.test_results['api_routing'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_experience_manager_functionality(self):
        """Test 3: Experience Manager functionality."""
        logger.info("🧪 Test 3: Experience Manager functionality")
        
        try:
            # Test session management
            session_data = {
                'user_id': self.user_context.user_id,
                'session_type': 'business_analysis',
                'context': {'pillar': 'insights', 'workflow': 'data_analysis'}
            }
            
            session_response = await experience_manager_service.create_session(
                session_data=session_data,
                user_context=self.user_context
            )
            
            assert session_response.get('success') is True, "Session creation should succeed"
            session_id = session_response.get('data', {}).get('session_id')
            assert session_id is not None, "Session ID should be returned"
            
            # Test UI state management
            ui_state_data = {
                'session_id': session_id,
                'current_view': 'insights_dashboard',
                'state': {
                    'selected_dataset': 'test_dataset',
                    'analysis_type': 'comprehensive',
                    'visualization_type': 'auto'
                }
            }
            
            ui_state_response = await experience_manager_service.update_ui_state(
                ui_state_data=ui_state_data,
                user_context=self.user_context
            )
            
            assert ui_state_response.get('success') is True, "UI state update should succeed"
            
            # Test real-time coordination
            real_time_data = {
                'session_id': session_id,
                'event_type': 'data_analysis_complete',
                'data': {'analysis_id': 'analysis_123', 'status': 'completed'}
            }
            
            real_time_response = await experience_manager_service.coordinate_real_time(
                real_time_data=real_time_data,
                user_context=self.user_context
            )
            
            assert real_time_response.get('success') is True, "Real-time coordination should succeed"
            
            self.test_results['experience_manager'] = {
                'success': True,
                'session_response': session_response,
                'ui_state_response': ui_state_response,
                'real_time_response': real_time_response
            }
            
            logger.info("✅ Experience Manager functionality successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Experience Manager functionality failed: {e}")
            self.test_results['experience_manager'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_journey_manager_functionality(self):
        """Test 4: Journey Manager functionality."""
        logger.info("🧪 Test 4: Journey Manager functionality")
        
        try:
            # Test journey tracking
            journey_data = {
                'user_id': self.user_context.user_id,
                'journey_type': 'data_analysis_workflow',
                'steps': [
                    {'step': 'data_upload', 'status': 'completed', 'timestamp': datetime.now().isoformat()},
                    {'step': 'data_analysis', 'status': 'in_progress', 'timestamp': datetime.now().isoformat()},
                    {'step': 'insights_generation', 'status': 'pending', 'timestamp': None}
                ]
            }
            
            journey_response = await journey_manager_service.track_journey(
                journey_data=journey_data,
                user_context=self.user_context
            )
            
            assert journey_response.get('success') is True, "Journey tracking should succeed"
            journey_id = journey_response.get('data', {}).get('journey_id')
            assert journey_id is not None, "Journey ID should be returned"
            
            # Test flow management
            flow_data = {
                'journey_id': journey_id,
                'flow_type': 'data_analysis_workflow',
                'current_step': 'data_analysis',
                'next_steps': ['insights_generation', 'visualization_creation']
            }
            
            flow_response = await journey_manager_service.manage_flow(
                flow_data=flow_data,
                user_context=self.user_context
            )
            
            assert flow_response.get('success') is True, "Flow management should succeed"
            
            # Test journey analytics
            analytics_response = await journey_manager_service.get_journey_analytics(
                journey_id=journey_id,
                user_context=self.user_context
            )
            
            assert analytics_response.get('success') is True, "Journey analytics should succeed"
            
            self.test_results['journey_manager'] = {
                'success': True,
                'journey_response': journey_response,
                'flow_response': flow_response,
                'analytics_response': analytics_response
            }
            
            logger.info("✅ Journey Manager functionality successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Journey Manager functionality failed: {e}")
            self.test_results['journey_manager'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_cross_dimension_coordination(self):
        """Test 5: Cross-dimension coordination between Experience services."""
        logger.info("🧪 Test 5: Cross-dimension coordination")
        
        try:
            # Create a session in Experience Manager
            session_data = {
                'user_id': self.user_context.user_id,
                'session_type': 'cross_dimension_test',
                'context': {'test_type': 'coordination', 'pillars': ['experience', 'business_enablement']}
            }
            
            session_response = await experience_manager_service.create_session(
                session_data=session_data,
                user_context=self.user_context
            )
            
            session_id = session_response.get('data', {}).get('session_id')
            
            # Track the journey in Journey Manager
            journey_data = {
                'user_id': self.user_context.user_id,
                'journey_type': 'cross_dimension_coordination',
                'session_id': session_id,
                'steps': [
                    {'step': 'session_creation', 'status': 'completed'},
                    {'step': 'journey_tracking', 'status': 'in_progress'},
                    {'step': 'coordination_test', 'status': 'pending'}
                ]
            }
            
            journey_response = await journey_manager_service.track_journey(
                journey_data=journey_data,
                user_context=self.user_context
            )
            
            journey_id = journey_response.get('data', {}).get('journey_id')
            
            # Test API routing through Frontend Integration
            api_response = await frontend_integration_service.route_api_request(
                endpoint=APIEndpoint.INSIGHTS_HEALTH,
                method=RequestMethod.GET,
                user_context=self.user_context,
                session_token=self.session_token
            )
            
            # Validate coordination
            assert session_response.get('success') is True, "Session creation should succeed"
            assert journey_response.get('success') is True, "Journey tracking should succeed"
            assert api_response.get('success') is True, "API routing should succeed"
            
            self.test_results['cross_dimension_coordination'] = {
                'success': True,
                'session_response': session_response,
                'journey_response': journey_response,
                'api_response': api_response
            }
            
            logger.info("✅ Cross-dimension coordination successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cross-dimension coordination failed: {e}")
            self.test_results['cross_dimension_coordination'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_end_to_end_experience_workflow(self):
        """Test 6: Complete end-to-end Experience Dimension workflow."""
        logger.info("🧪 Test 6: Complete end-to-end Experience workflow")
        
        try:
            workflow_steps = []
            
            # Step 1: Create user session
            session_creation = await experience_manager_service.create_session(
                session_data={
                    'user_id': self.user_context.user_id,
                    'session_type': 'end_to_end_workflow',
                    'context': {'workflow': 'complete_experience_test'}
                },
                user_context=self.user_context
            )
            workflow_steps.append(('session_creation', session_creation))
            
            # Step 2: Track user journey
            journey_tracking = await journey_manager_service.track_journey(
                journey_data={
                    'user_id': self.user_context.user_id,
                    'journey_type': 'end_to_end_workflow',
                    'steps': [
                        {'step': 'session_creation', 'status': 'completed'},
                        {'step': 'journey_tracking', 'status': 'in_progress'},
                        {'step': 'api_routing', 'status': 'pending'},
                        {'step': 'workflow_completion', 'status': 'pending'}
                    ]
                },
                user_context=self.user_context
            )
            workflow_steps.append(('journey_tracking', journey_tracking))
            
            # Step 3: Route API requests
            api_routing = await frontend_integration_service.route_api_request(
                endpoint=APIEndpoint.INSIGHTS_ANALYZE,
                method=RequestMethod.POST,
                data={'dataset': {'test': 'data'}},
                user_context=self.user_context,
                session_token=self.session_token
            )
            workflow_steps.append(('api_routing', api_routing))
            
            # Step 4: Update UI state
            ui_state_update = await experience_manager_service.update_ui_state(
                ui_state_data={
                    'session_id': session_creation.get('data', {}).get('session_id'),
                    'current_view': 'workflow_complete',
                    'state': {'workflow_status': 'completed', 'steps_completed': len(workflow_steps)}
                },
                user_context=self.user_context
            )
            workflow_steps.append(('ui_state_update', ui_state_update))
            
            # Step 5: Complete journey
            journey_completion = await journey_manager_service.complete_journey(
                journey_id=journey_tracking.get('data', {}).get('journey_id'),
                completion_data={'status': 'success', 'steps_completed': len(workflow_steps)},
                user_context=self.user_context
            )
            workflow_steps.append(('journey_completion', journey_completion))
            
            # Validate all steps succeeded
            for step_name, step_response in workflow_steps:
                assert step_response.get('success') is True, f"Step {step_name} should succeed"
            
            self.test_results['end_to_end_workflow'] = {
                'success': True,
                'workflow_steps': workflow_steps,
                'total_steps': len(workflow_steps)
            }
            
            logger.info("✅ Complete end-to-end Experience workflow successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ End-to-end Experience workflow failed: {e}")
            self.test_results['end_to_end_workflow'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def run_all_tests(self):
        """Run all Experience Dimension integration tests."""
        logger.info("🚀 Starting Experience Dimension Integration Tests...")
        
        # Setup
        await self.setup_test_environment()
        
        # Run all tests
        test_methods = [
            self.test_experience_dimension_initialization,
            self.test_frontend_integration_api_routing,
            self.test_experience_manager_functionality,
            self.test_journey_manager_functionality,
            self.test_cross_dimension_coordination,
            self.test_end_to_end_experience_workflow
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                result = await test_method()
                if result:
                    passed_tests += 1
            except Exception as e:
                logger.error(f"❌ Test {test_method.__name__} failed with exception: {e}")
        
        # Generate summary
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"🎯 Test Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate == 100:
            logger.info("🎉 All Experience Dimension integration tests passed!")
        else:
            logger.warning(f"⚠️ {total_tests - passed_tests} tests failed")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate,
            'test_results': self.test_results
        }


async def main():
    """Main test runner."""
    test_suite = ExperienceDimensionIntegrationTest()
    results = await test_suite.run_all_tests()
    
    # Print detailed results
    print("\n" + "="*80)
    print("EXPERIENCE DIMENSION INTEGRATION TEST RESULTS")
    print("="*80)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed Tests: {results['passed_tests']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print("="*80)
    
    for test_name, test_result in results['test_results'].items():
        status = "✅ PASS" if test_result.get('success') else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not test_result.get('success') and 'error' in test_result:
            print(f"  Error: {test_result['error']}")
    
    print("="*80)
    
    if results['success_rate'] == 100:
        print("🎉 ALL TESTS PASSED! Experience Dimension integration is working perfectly!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the logs for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
