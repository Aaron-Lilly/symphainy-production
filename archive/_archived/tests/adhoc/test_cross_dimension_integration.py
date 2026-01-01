#!/usr/bin/env python3
"""
Cross-Dimension Integration Test

Tests the complete integration between:
1. Experience Dimension (Frontend Integration, Experience Manager, Journey Manager)
2. Business Enablement Dimension (Content, Insights, Operations, Business Outcomes pillars)
3. Frontend (symphainy-frontend)

This test validates the full end-to-end workflow using real backend endpoints
extracted from business_orchestrator_old.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the services
from experience.services.frontend_integration_service import frontend_integration_service
from experience.services.experience_manager_service import experience_manager_service
from experience.services.journey_manager_service import journey_manager_service

# Import business enablement services (using the working implementations)
from backend.business_enablement.pillars.content_pillar.content_pillar_service import content_pillar_service
from backend.business_enablement.pillars.insights_pillar.insights_pillar_service import insights_pillar_service
from backend.business_enablement.pillars.operations_pillar.operations_pillar_service import operations_pillar_service
from backend.business_enablement.pillars.business_outcomes_pillar.business_outcomes_pillar_service import business_outcomes_pillar_service

# Import interfaces and types
from experience.interfaces.frontend_integration_interface import APIEndpoint, RequestMethod, DataFormat
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrossDimensionIntegrationTest:
    """Comprehensive cross-dimension integration test suite."""
    
    def __init__(self):
        self.test_results = {}
        self.user_context = None
        self.session_token = None
        
    async def setup_test_environment(self):
        """Set up the test environment with user context and session."""
        logger.info("🔧 Setting up test environment...")
        
        # Create test user context
        self.user_context = UserContext(
            user_id="integration_test_user_123",
            full_name="Integration Test User",
            email="integration.test@example.com",
            session_id="integration_test_session_123",
            permissions=["read", "write", "analyze", "visualize", "manage"]
        )
        
        # Generate session token
        self.session_token = f"test_session_{int(datetime.now().timestamp())}"
        
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
    
    async def test_business_enablement_dimension_initialization(self):
        """Test 2: Business Enablement Dimension services initialization."""
        logger.info("🧪 Test 2: Business Enablement Dimension services initialization")
        
        try:
            # Initialize Business Enablement services
            await content_pillar_service.initialize()
            await insights_pillar_service.initialize()
            await operations_pillar_service.initialize()
            await business_outcomes_pillar_service.initialize()
            
            # Test health checks
            content_health = await content_pillar_service.get_service_health()
            insights_health = await insights_pillar_service.get_service_health()
            operations_health = await operations_pillar_service.get_service_health()
            outcomes_health = await business_outcomes_pillar_service.get_service_health()
            
            # Validate health status
            assert content_health.get('status') == 'healthy', "Content Pillar should be healthy"
            assert insights_health.get('status') == 'healthy', "Insights Pillar should be healthy"
            assert operations_health.get('status') == 'healthy', "Operations Pillar should be healthy"
            assert outcomes_health.get('status') == 'healthy', "Business Outcomes Pillar should be healthy"
            
            self.test_results['business_enablement_init'] = {
                'success': True,
                'content_pillar': content_health,
                'insights_pillar': insights_health,
                'operations_pillar': operations_health,
                'business_outcomes_pillar': outcomes_health
            }
            
            logger.info("✅ Business Enablement Dimension services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Business Enablement Dimension initialization failed: {e}")
            self.test_results['business_enablement_init'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_frontend_to_backend_api_routing(self):
        """Test 3: Frontend to Backend API routing through Experience Dimension."""
        logger.info("🧪 Test 3: Frontend to Backend API routing")
        
        try:
            # Test routing to different pillars
            test_endpoints = [
                (APIEndpoint.INSIGHTS_HEALTH, "insights"),
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
            
            logger.info("✅ Frontend to Backend API routing successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ API routing failed: {e}")
            self.test_results['api_routing'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_content_pillar_workflow(self):
        """Test 4: Content Pillar workflow (file upload, parse, analyze)."""
        logger.info("🧪 Test 4: Content Pillar workflow")
        
        try:
            # Simulate file upload
            test_file_data = {
                'filename': 'test_document.pdf',
                'content': 'This is a test document for content analysis.',
                'file_type': 'pdf',
                'size': 1024
            }
            
            # Test file upload
            upload_response = await content_pillar_service.upload_file(
                file_data=test_file_data,
                user_context=self.user_context
            )
            
            assert upload_response.get('success') is True, "File upload should succeed"
            file_id = upload_response.get('data', {}).get('file_id')
            assert file_id is not None, "File ID should be returned"
            
            # Test file parsing
            parse_response = await content_pillar_service.parse_file(
                file_id=file_id,
                user_context=self.user_context
            )
            
            assert parse_response.get('success') is True, "File parsing should succeed"
            
            # Test file analysis
            analysis_response = await content_pillar_service.analyze_file(
                file_id=file_id,
                analysis_type="comprehensive",
                user_context=self.user_context
            )
            
            assert analysis_response.get('success') is True, "File analysis should succeed"
            
            self.test_results['content_pillar_workflow'] = {
                'success': True,
                'upload_response': upload_response,
                'parse_response': parse_response,
                'analysis_response': analysis_response
            }
            
            logger.info("✅ Content Pillar workflow successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Content Pillar workflow failed: {e}")
            self.test_results['content_pillar_workflow'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_insights_pillar_workflow(self):
        """Test 5: Insights Pillar workflow (data analysis, visualization, chat)."""
        logger.info("🧪 Test 5: Insights Pillar workflow")
        
        try:
            # Test dataset analysis
            test_dataset = {
                'data': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                'labels': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
                'metadata': {'source': 'test', 'type': 'numerical'}
            }
            
            analysis_response = await insights_pillar_service.analyze_dataset(
                dataset=test_dataset,
                analysis_type="comprehensive",
                user_context=self.user_context
            )
            
            assert analysis_response.get('success') is True, "Dataset analysis should succeed"
            
            # Test visualization creation
            visualization_response = await insights_pillar_service.create_visualization(
                dataset=test_dataset,
                visualization_type="auto",
                user_context=self.user_context
            )
            
            assert visualization_response.get('success') is True, "Visualization creation should succeed"
            
            # Test chat interaction
            chat_response = await insights_pillar_service.send_chat_message(
                message="What insights can you provide about this data?",
                dataset=test_dataset,
                user_context=self.user_context
            )
            
            assert chat_response.get('success') is True, "Chat interaction should succeed"
            
            self.test_results['insights_pillar_workflow'] = {
                'success': True,
                'analysis_response': analysis_response,
                'visualization_response': visualization_response,
                'chat_response': chat_response
            }
            
            logger.info("✅ Insights Pillar workflow successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Insights Pillar workflow failed: {e}")
            self.test_results['insights_pillar_workflow'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_operations_pillar_workflow(self):
        """Test 6: Operations Pillar workflow (SOP to Workflow conversion, coexistence)."""
        logger.info("🧪 Test 6: Operations Pillar workflow")
        
        try:
            # Test SOP to Workflow conversion
            test_sop = {
                'title': 'Customer Onboarding Process',
                'steps': [
                    {'id': 1, 'action': 'Collect customer information', 'responsible': 'Sales Team'},
                    {'id': 2, 'action': 'Verify customer identity', 'responsible': 'Compliance Team'},
                    {'id': 3, 'action': 'Set up customer account', 'responsible': 'IT Team'},
                    {'id': 4, 'action': 'Send welcome email', 'responsible': 'Marketing Team'}
                ],
                'metadata': {'department': 'Customer Success', 'priority': 'high'}
            }
            
            conversion_response = await operations_pillar_service.convert_sop_to_workflow(
                sop_data=test_sop,
                user_context=self.user_context
            )
            
            assert conversion_response.get('success') is True, "SOP to Workflow conversion should succeed"
            
            # Test coexistence blueprint creation
            coexistence_response = await operations_pillar_service.create_coexistence_blueprint(
                blueprint_data={
                    'title': 'AI-Human Collaboration Blueprint',
                    'description': 'Blueprint for AI and human collaboration in customer service',
                    'ai_capabilities': ['natural_language_processing', 'sentiment_analysis'],
                    'human_capabilities': ['empathy', 'complex_problem_solving'],
                    'collaboration_points': ['escalation', 'quality_assurance']
                },
                user_context=self.user_context
            )
            
            assert coexistence_response.get('success') is True, "Coexistence blueprint creation should succeed"
            
            self.test_results['operations_pillar_workflow'] = {
                'success': True,
                'conversion_response': conversion_response,
                'coexistence_response': coexistence_response
            }
            
            logger.info("✅ Operations Pillar workflow successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Operations Pillar workflow failed: {e}")
            self.test_results['operations_pillar_workflow'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_business_outcomes_pillar_workflow(self):
        """Test 7: Business Outcomes Pillar workflow (strategic planning, ROI analysis)."""
        logger.info("🧪 Test 7: Business Outcomes Pillar workflow")
        
        try:
            # Test strategic plan generation
            strategic_plan_data = {
                'title': 'Digital Transformation Strategic Plan',
                'objectives': [
                    'Improve operational efficiency by 25%',
                    'Enhance customer satisfaction scores',
                    'Reduce operational costs by 15%'
                ],
                'timeline': '12 months',
                'budget': 500000,
                'stakeholders': ['Executive Team', 'IT Department', 'Operations Team']
            }
            
            strategic_plan_response = await business_outcomes_pillar_service.generate_strategic_plan(
                plan_data=strategic_plan_data,
                user_context=self.user_context
            )
            
            assert strategic_plan_response.get('success') is True, "Strategic plan generation should succeed"
            
            # Test ROI analysis
            roi_data = {
                'investment': 500000,
                'expected_returns': [
                    {'year': 1, 'amount': 200000, 'description': 'Efficiency gains'},
                    {'year': 2, 'amount': 300000, 'description': 'Cost savings'},
                    {'year': 3, 'amount': 400000, 'description': 'Revenue growth'}
                ],
                'discount_rate': 0.1,
                'analysis_period': 3
            }
            
            roi_response = await business_outcomes_pillar_service.perform_roi_analysis(
                roi_data=roi_data,
                user_context=self.user_context
            )
            
            assert roi_response.get('success') is True, "ROI analysis should succeed"
            
            self.test_results['business_outcomes_pillar_workflow'] = {
                'success': True,
                'strategic_plan_response': strategic_plan_response,
                'roi_response': roi_response
            }
            
            logger.info("✅ Business Outcomes Pillar workflow successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Business Outcomes Pillar workflow failed: {e}")
            self.test_results['business_outcomes_pillar_workflow'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_cross_pillar_integration(self):
        """Test 8: Cross-pillar integration (Content -> Insights -> Operations -> Business Outcomes)."""
        logger.info("🧪 Test 8: Cross-pillar integration workflow")
        
        try:
            # Step 1: Content Pillar - Upload and analyze document
            test_document = {
                'filename': 'business_process_document.pdf',
                'content': 'This document describes our current business processes and identifies areas for improvement.',
                'file_type': 'pdf'
            }
            
            content_response = await content_pillar_service.upload_file(
                file_data=test_document,
                user_context=self.user_context
            )
            
            file_id = content_response.get('data', {}).get('file_id')
            
            # Step 2: Insights Pillar - Analyze the document content
            document_analysis = await insights_pillar_service.analyze_dataset(
                dataset={'document_id': file_id, 'content': test_document['content']},
                analysis_type="document_analysis",
                user_context=self.user_context
            )
            
            # Step 3: Operations Pillar - Create workflow based on insights
            workflow_data = {
                'title': 'Optimized Business Process Workflow',
                'description': 'Workflow created based on document analysis',
                'steps': [
                    {'action': 'Document Review', 'responsible': 'Analyst'},
                    {'action': 'Process Optimization', 'responsible': 'Operations Team'},
                    {'action': 'Implementation', 'responsible': 'Implementation Team'}
                ]
            }
            
            operations_response = await operations_pillar_service.convert_sop_to_workflow(
                sop_data=workflow_data,
                user_context=self.user_context
            )
            
            # Step 4: Business Outcomes Pillar - Measure impact
            impact_analysis = await business_outcomes_pillar_service.perform_roi_analysis(
                roi_data={
                    'investment': 100000,
                    'expected_returns': [
                        {'year': 1, 'amount': 150000, 'description': 'Process efficiency gains'}
                    ],
                    'discount_rate': 0.1,
                    'analysis_period': 1
                },
                user_context=self.user_context
            )
            
            # Validate all steps succeeded
            assert content_response.get('success') is True, "Content processing should succeed"
            assert document_analysis.get('success') is True, "Document analysis should succeed"
            assert operations_response.get('success') is True, "Workflow creation should succeed"
            assert impact_analysis.get('success') is True, "Impact analysis should succeed"
            
            self.test_results['cross_pillar_integration'] = {
                'success': True,
                'content_response': content_response,
                'document_analysis': document_analysis,
                'operations_response': operations_response,
                'impact_analysis': impact_analysis
            }
            
            logger.info("✅ Cross-pillar integration workflow successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cross-pillar integration failed: {e}")
            self.test_results['cross_pillar_integration'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_experience_dimension_coordination(self):
        """Test 9: Experience Dimension coordination (Experience Manager, Journey Manager)."""
        logger.info("🧪 Test 9: Experience Dimension coordination")
        
        try:
            # Test Experience Manager session management
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
            
            # Test Journey Manager flow tracking
            journey_data = {
                'session_id': session_id,
                'flow_type': 'data_analysis_workflow',
                'steps': [
                    {'step': 'data_upload', 'status': 'completed'},
                    {'step': 'data_analysis', 'status': 'in_progress'},
                    {'step': 'insights_generation', 'status': 'pending'}
                ]
            }
            
            journey_response = await journey_manager_service.track_journey(
                journey_data=journey_data,
                user_context=self.user_context
            )
            
            assert journey_response.get('success') is True, "Journey tracking should succeed"
            
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
            
            self.test_results['experience_dimension_coordination'] = {
                'success': True,
                'session_response': session_response,
                'journey_response': journey_response,
                'ui_state_response': ui_state_response
            }
            
            logger.info("✅ Experience Dimension coordination successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ Experience Dimension coordination failed: {e}")
            self.test_results['experience_dimension_coordination'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def test_end_to_end_workflow(self):
        """Test 10: Complete end-to-end workflow simulation."""
        logger.info("🧪 Test 10: Complete end-to-end workflow")
        
        try:
            # Simulate a complete business workflow
            workflow_steps = []
            
            # Step 1: User uploads a business document
            document_upload = await content_pillar_service.upload_file(
                file_data={
                    'filename': 'quarterly_report.pdf',
                    'content': 'Q3 2024 quarterly business report with financial data and operational metrics.',
                    'file_type': 'pdf'
                },
                user_context=self.user_context
            )
            workflow_steps.append(('document_upload', document_upload))
            
            # Step 2: System analyzes the document
            document_analysis = await insights_pillar_service.analyze_dataset(
                dataset={'document_id': document_upload.get('data', {}).get('file_id')},
                analysis_type="document_analysis",
                user_context=self.user_context
            )
            workflow_steps.append(('document_analysis', document_analysis))
            
            # Step 3: System creates optimized workflows
            workflow_creation = await operations_pillar_service.convert_sop_to_workflow(
                sop_data={
                    'title': 'Q3 Report Analysis Workflow',
                    'steps': [
                        {'action': 'Extract key metrics', 'responsible': 'AI System'},
                        {'action': 'Generate insights', 'responsible': 'Analytics Team'},
                        {'action': 'Create recommendations', 'responsible': 'Strategy Team'}
                    ]
                },
                user_context=self.user_context
            )
            workflow_steps.append(('workflow_creation', workflow_creation))
            
            # Step 4: System measures business impact
            impact_measurement = await business_outcomes_pillar_service.perform_roi_analysis(
                roi_data={
                    'investment': 50000,
                    'expected_returns': [
                        {'year': 1, 'amount': 75000, 'description': 'Improved decision making'},
                        {'year': 2, 'amount': 100000, 'description': 'Operational efficiency gains'}
                    ],
                    'discount_rate': 0.1,
                    'analysis_period': 2
                },
                user_context=self.user_context
            )
            workflow_steps.append(('impact_measurement', impact_measurement))
            
            # Step 5: Experience Dimension coordinates the entire process
            coordination_response = await experience_manager_service.create_session(
                session_data={
                    'user_id': self.user_context.user_id,
                    'session_type': 'end_to_end_workflow',
                    'context': {
                        'workflow_steps': len(workflow_steps),
                        'pillars_involved': ['content', 'insights', 'operations', 'business_outcomes']
                    }
                },
                user_context=self.user_context
            )
            workflow_steps.append(('coordination', coordination_response))
            
            # Validate all steps succeeded
            for step_name, step_response in workflow_steps:
                assert step_response.get('success') is True, f"Step {step_name} should succeed"
            
            self.test_results['end_to_end_workflow'] = {
                'success': True,
                'workflow_steps': workflow_steps,
                'total_steps': len(workflow_steps)
            }
            
            logger.info("✅ Complete end-to-end workflow successful")
            return True
            
        except Exception as e:
            logger.error(f"❌ End-to-end workflow failed: {e}")
            self.test_results['end_to_end_workflow'] = {
                'success': False,
                'error': str(e)
            }
            return False
    
    async def run_all_tests(self):
        """Run all cross-dimension integration tests."""
        logger.info("🚀 Starting Cross-Dimension Integration Tests...")
        
        # Setup
        await self.setup_test_environment()
        
        # Run all tests
        test_methods = [
            self.test_experience_dimension_initialization,
            self.test_business_enablement_dimension_initialization,
            self.test_frontend_to_backend_api_routing,
            self.test_content_pillar_workflow,
            self.test_insights_pillar_workflow,
            self.test_operations_pillar_workflow,
            self.test_business_outcomes_pillar_workflow,
            self.test_cross_pillar_integration,
            self.test_experience_dimension_coordination,
            self.test_end_to_end_workflow
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
            logger.info("🎉 All cross-dimension integration tests passed!")
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
    test_suite = CrossDimensionIntegrationTest()
    results = await test_suite.run_all_tests()
    
    # Print detailed results
    print("\n" + "="*80)
    print("CROSS-DIMENSION INTEGRATION TEST RESULTS")
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
        print("🎉 ALL TESTS PASSED! Cross-dimension integration is working perfectly!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the logs for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
