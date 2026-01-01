#!/usr/bin/env python3
"""
Comprehensive All Pillars Integration Test

Tests the complete integration of all 4 business pillars:
- Content Pillar (file processing, storage, metadata)
- Insights Pillar (analytics, visualization, APG analysis)
- Operations Pillar (workflow, SOP, process optimization)
- Business Outcomes Pillar (strategic planning, ROI, metrics)

This test validates end-to-end workflows and cross-pillar data flow.
"""

import asyncio
import logging
import sys
import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Import all pillar services
from backend.business_enablement.pillars.content_pillar.content_pillar_service import ContentPillarService
from backend.business_enablement.pillars.insights_pillar.insights_pillar_service import InsightsPillarService
from backend.business_enablement.pillars.operations_pillar.operations_pillar_service import OperationsPillarService
from backend.business_enablement.pillars.business_outcomes_pillar.business_outcomes_pillar_service import BusinessOutcomesPillarService
from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockEnvironmentLoader:
    """Mock environment loader for testing."""
    
    def get_content_pillar_config(self):
        return {
            "file_processing_enabled": True,
            "supported_formats": ["pdf", "docx", "txt", "csv", "xlsx"],
            "max_file_size": 10485760,  # 10MB
            "storage_backend": "local"
        }
    
    def get_insights_pillar_config(self):
        return {
            "analytics_enabled": True,
            "visualization_enabled": True,
            "apg_enabled": True,
            "llm_settings": {
                "model": "gpt-4",
                "temperature": 0.3,
                "max_tokens": 1000
            }
        }
    
    def get_operations_pillar_config(self):
        return {
            "workflow_management_enabled": True,
            "sop_processing_enabled": True,
            "process_optimization_enabled": True,
            "coexistence_analysis_enabled": True
        }
    
    def get_business_outcomes_pillar_config(self):
        return {
            "strategic_planning_enabled": True,
            "roi_calculation_enabled": True,
            "metrics_tracking_enabled": True,
            "visualization_enabled": True
        }

class AllPillarsIntegrationTester:
    """Comprehensive integration tester for all business pillars."""
    
    def __init__(self):
        self.logger = logger
        self.test_results = []
        self.user_context = None
        self.test_session_id = str(uuid.uuid4())
        
        # Pillar services
        self.content_service = None
        self.insights_service = None
        self.operations_service = None
        self.business_outcomes_service = None
        
        # Test data
        self.uploaded_files = []
        self.analysis_results = []
        self.workflow_results = []
        self.strategic_plans = []
        
    async def setup(self):
        """Set up the test environment and initialize all pillar services."""
        try:
            self.logger.info("🚀 Setting up All Pillars Integration Test Environment...")
            
            # Create test user context
            self.user_context = UserContext(
                user_id="integration_test_user",
                email="test@integration.com",
                full_name="Integration Test User",
                session_id=self.test_session_id,
                permissions=["content", "insights", "operations", "business_outcomes", "admin"]
            )
            
            # Initialize environment loader
            env_loader = MockEnvironmentLoader()
            
            # Initialize all pillar services
            self.logger.info("📁 Initializing Content Pillar Service...")
            self.content_service = ContentPillarService()
            await self.content_service.initialize()
            
            self.logger.info("📊 Initializing Insights Pillar Service...")
            self.insights_service = InsightsPillarService()
            await self.insights_service.initialize()
            
            self.logger.info("⚙️ Initializing Operations Pillar Service...")
            self.operations_service = OperationsPillarService()
            await self.operations_service.initialize()
            
            self.logger.info("🎯 Initializing Business Outcomes Pillar Service...")
            self.business_outcomes_service = BusinessOutcomesPillarService()
            await self.business_outcomes_service.initialize()
            
            self.logger.info("✅ All Pillars Integration Test Environment ready")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup All Pillars Integration Test: {e}")
            return False
    
    async def test_content_pillar_integration(self) -> bool:
        """Test Content Pillar integration with file processing and storage."""
        self.logger.info("🧪 Testing Content Pillar Integration...")
        
        try:
            # Test 1: File Upload
            self.logger.info("  📤 Testing file upload...")
            test_file_data = b"Sample business report content for testing integration across all pillars."
            test_filename = "business_report.txt"
            
            # Create upload request
            from backend.business_enablement.interfaces.content_management_interface import UploadRequest
            upload_request = UploadRequest(
                file_data=test_file_data,
                filename=test_filename,
                content_type="text/plain",
                user_id=self.user_context.user_id,
                session_id=self.test_session_id
            )
            
            upload_result = await self.content_service.upload_file(
                request=upload_request,
                user_context=self.user_context
            )
            
            if not upload_result.get("success"):
                self.logger.error(f"❌ File upload failed: {upload_result.get('message')}")
                return False
            
            file_id = upload_result.get("file_id")
            self.uploaded_files.append(file_id)
            self.logger.info(f"  ✅ File uploaded successfully: {file_id}")
            
            # Test 2: File Parsing
            self.logger.info("  🔍 Testing file parsing...")
            parse_result = await self.content_service.parse_file(
                file_id=file_id,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not parse_result.get("success"):
                self.logger.error(f"❌ File parsing failed: {parse_result.get('message')}")
                return False
            
            self.logger.info("  ✅ File parsed successfully")
            
            # Test 3: Metadata Extraction
            self.logger.info("  📋 Testing metadata extraction...")
            metadata_result = await self.content_service.metadata_extractor(
                file_id=file_id,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not metadata_result.get("success"):
                self.logger.error(f"❌ Metadata extraction failed: {metadata_result.get('message')}")
                return False
            
            self.logger.info("  ✅ Metadata extracted successfully")
            
            # Test 4: File Listing
            self.logger.info("  📝 Testing file listing...")
            list_result = await self.content_service.list_user_files(
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not list_result.get("success"):
                self.logger.error(f"❌ File listing failed: {list_result.get('message')}")
                return False
            
            files = list_result.get("files", [])
            if len(files) == 0:
                self.logger.error("❌ No files found in listing")
                return False
            
            self.logger.info(f"  ✅ Found {len(files)} files")
            
            self.logger.info("✅ Content Pillar Integration passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Content Pillar integration test failed: {e}")
            return False
    
    async def test_insights_pillar_integration(self) -> bool:
        """Test Insights Pillar integration with analytics and visualization."""
        self.logger.info("🧪 Testing Insights Pillar Integration...")
        
        try:
            if not self.uploaded_files:
                self.logger.error("❌ No uploaded files available for insights analysis")
                return False
            
            file_id = self.uploaded_files[0]
            
            # Test 1: Data Analysis
            self.logger.info("  📊 Testing data analysis...")
            analysis_data = {
                "values": [
                    {"x": 1, "y": 10, "category": "A"},
                    {"x": 2, "y": 15, "category": "A"},
                    {"x": 3, "y": 12, "category": "B"},
                    {"x": 4, "y": 18, "category": "A"},
                    {"x": 5, "y": 14, "category": "B"}
                ]
            }
            
            analysis_result = await self.insights_service.analyze_data(
                data=analysis_data,
                analysis_type="descriptive",
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not analysis_result.get("success"):
                self.logger.error(f"❌ Data analysis failed: {analysis_result.get('message')}")
                return False
            
            self.analysis_results.append(analysis_result)
            self.logger.info("  ✅ Data analysis completed successfully")
            
            # Test 2: Visualization Generation
            self.logger.info("  📈 Testing visualization generation...")
            viz_data = {
                "values": analysis_data["values"],
                "column": "y",
                "title": "Test Visualization"
            }
            
            viz_result = await self.insights_service.create_visualization(
                data=viz_data,
                visualization_type="histogram",
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not viz_result.get("success"):
                self.logger.error(f"❌ Visualization generation failed: {viz_result.get('message')}")
                return False
            
            self.logger.info("  ✅ Visualization generated successfully")
            
            # Test 3: APG Analysis
            self.logger.info("  🤖 Testing APG analysis...")
            apg_data = {
                "text": "Business performance shows strong growth trends with seasonal variations and some anomalies in Q3.",
                "metadata": {"source": "integration_test", "type": "business_report"}
            }
            
            apg_result = await self.insights_service.process_apg_mode(
                data=apg_data,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not apg_result.get("success"):
                self.logger.error(f"❌ APG analysis failed: {apg_result.get('message')}")
                return False
            
            self.logger.info("  ✅ APG analysis completed successfully")
            
            self.logger.info("✅ Insights Pillar Integration passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Insights Pillar integration test failed: {e}")
            return False
    
    async def test_operations_pillar_integration(self) -> bool:
        """Test Operations Pillar integration with workflow and SOP management."""
        self.logger.info("🧪 Testing Operations Pillar Integration...")
        
        try:
            # Test 1: SOP Creation
            self.logger.info("  📋 Testing SOP creation...")
            sop_data = {
                "title": "Customer Onboarding Process",
                "description": "Standard process for onboarding new customers",
                "steps": [
                    "Collect customer information",
                    "Verify identity documents",
                    "Set up customer account",
                    "Configure services",
                    "Send welcome package"
                ],
                "department": "Customer Service",
                "version": "1.0"
            }
            
            sop_result = await self.operations_service.create_sop(
                sop_data=sop_data,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not sop_result.get("success"):
                self.logger.error(f"❌ SOP creation failed: {sop_result.get('message')}")
                return False
            
            sop_id = sop_result.get("sop_id")
            self.workflow_results.append({"type": "sop", "id": sop_id})
            self.logger.info(f"  ✅ SOP created successfully: {sop_id}")
            
            # Test 2: SOP to Workflow Conversion
            self.logger.info("  🔄 Testing SOP to workflow conversion...")
            workflow_result = await self.operations_service.convert_sop_to_workflow(
                sop_id=sop_id,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not workflow_result.get("success"):
                self.logger.error(f"❌ SOP to workflow conversion failed: {workflow_result.get('message')}")
                return False
            
            workflow_id = workflow_result.get("workflow_id")
            self.workflow_results.append({"type": "workflow", "id": workflow_id})
            self.logger.info(f"  ✅ Workflow created successfully: {workflow_id}")
            
            # Test 3: Process Optimization
            self.logger.info("  ⚡ Testing process optimization...")
            process_data = {
                "process_name": "Customer Onboarding",
                "current_steps": sop_data["steps"],
                "metrics": {
                    "avg_time": 45,  # minutes
                    "success_rate": 0.85,
                    "cost_per_customer": 25.50
                }
            }
            
            optimization_result = await self.operations_service.optimize_process(
                process_data=process_data,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not optimization_result.get("success"):
                self.logger.error(f"❌ Process optimization failed: {optimization_result.get('message')}")
                return False
            
            self.logger.info("  ✅ Process optimization completed successfully")
            
            # Test 4: Coexistence Analysis
            self.logger.info("  🤝 Testing coexistence analysis...")
            coexistence_data = {
                "human_tasks": ["Customer verification", "Account setup"],
                "ai_tasks": ["Document scanning", "Data validation"],
                "collaboration_points": ["Information review", "Decision making"]
            }
            
            coexistence_result = await self.operations_service.analyze_coexistence(
                coexistence_data=coexistence_data,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not coexistence_result.get("success"):
                self.logger.error(f"❌ Coexistence analysis failed: {coexistence_result.get('message')}")
                return False
            
            self.logger.info("  ✅ Coexistence analysis completed successfully")
            
            self.logger.info("✅ Operations Pillar Integration passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Operations Pillar integration test failed: {e}")
            return False
    
    async def test_business_outcomes_pillar_integration(self) -> bool:
        """Test Business Outcomes Pillar integration with strategic planning."""
        self.logger.info("🧪 Testing Business Outcomes Pillar Integration...")
        
        try:
            # Test 1: Strategic Roadmap Generation
            self.logger.info("  🗺️ Testing strategic roadmap generation...")
            roadmap_data = {
                "objectives": [
                    "Increase customer satisfaction by 20%",
                    "Reduce operational costs by 15%",
                    "Improve process efficiency by 30%"
                ],
                "timeline": "12 months",
                "budget": 500000,
                "department": "Operations"
            }
            
            roadmap_result = await self.business_outcomes_service.generate_strategic_roadmap(
                objectives=roadmap_data["objectives"],
                timeline=roadmap_data["timeline"],
                budget=roadmap_data["budget"],
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not roadmap_result.get("success"):
                self.logger.error(f"❌ Strategic roadmap generation failed: {roadmap_result.get('message')}")
                return False
            
            roadmap_id = roadmap_result.get("roadmap_id")
            self.strategic_plans.append({"type": "roadmap", "id": roadmap_id})
            self.logger.info(f"  ✅ Strategic roadmap created successfully: {roadmap_id}")
            
            # Test 2: ROI Calculation
            self.logger.info("  💰 Testing ROI calculation...")
            roi_data = {
                "investment_amount": 100000,
                "expected_returns": [25000, 30000, 35000, 40000, 45000],  # 5 years
                "discount_rate": 0.08,
                "project_name": "Process Automation Initiative"
            }
            
            roi_result = await self.business_outcomes_service.calculate_roi(
                investment_data=roi_data,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not roi_result.get("success"):
                self.logger.error(f"❌ ROI calculation failed: {roi_result.get('message')}")
                return False
            
            self.logger.info("  ✅ ROI calculation completed successfully")
            
            # Test 3: Visual Dashboard Creation
            self.logger.info("  📊 Testing visual dashboard creation...")
            dashboard_data = {
                "metrics": {
                    "revenue": 1000000,
                    "customers": 5000,
                    "satisfaction": 4.2,
                    "efficiency": 0.85
                },
                "timeframe": "Q4 2024",
                "department": "Business Operations"
            }
            
            dashboard_result = await self.business_outcomes_service.create_outcome_metrics_display(
                metrics_data=dashboard_data,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not dashboard_result.get("success"):
                self.logger.error(f"❌ Dashboard creation failed: {dashboard_result.get('message')}")
                return False
            
            self.logger.info("  ✅ Visual dashboard created successfully")
            
            # Test 4: Cross-Pillar Data Integration
            self.logger.info("  🔗 Testing cross-pillar data integration...")
            integration_data = {
                "content_metrics": len(self.uploaded_files),
                "insights_analyses": len(self.analysis_results),
                "operations_workflows": len(self.workflow_results),
                "business_objectives": len(roadmap_data["objectives"])
            }
            
            # This would typically call a cross-pillar integration method
            # For now, we'll validate that we have data from all pillars
            if integration_data["content_metrics"] == 0:
                self.logger.error("❌ No content metrics available for integration")
                return False
            
            if integration_data["insights_analyses"] == 0:
                self.logger.error("❌ No insights analyses available for integration")
                return False
            
            if integration_data["operations_workflows"] == 0:
                self.logger.error("❌ No operations workflows available for integration")
                return False
            
            self.logger.info("  ✅ Cross-pillar data integration validated")
            
            self.logger.info("✅ Business Outcomes Pillar Integration passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Business Outcomes Pillar integration test failed: {e}")
            return False
    
    async def test_cross_pillar_workflows(self) -> bool:
        """Test cross-pillar workflows and data flow."""
        self.logger.info("🧪 Testing Cross-Pillar Workflows...")
        
        try:
            # Test 1: Content → Insights Workflow
            self.logger.info("  📁→📊 Testing Content to Insights workflow...")
            if not self.uploaded_files:
                self.logger.error("❌ No uploaded files for cross-pillar workflow")
                return False
            
            file_id = self.uploaded_files[0]
            
            # Get file content for analysis
            file_content = await self.content_service.get_file_content(
                file_id=file_id,
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not file_content.get("success"):
                self.logger.error("❌ Failed to get file content for cross-pillar analysis")
                return False
            
            # Analyze the content
            analysis_data = {"text": file_content.get("content", "")}
            analysis_result = await self.insights_service.analyze_data(
                data=analysis_data,
                analysis_type="descriptive",
                user_context=self.user_context,
                session_id=self.test_session_id
            )
            
            if not analysis_result.get("success"):
                self.logger.error("❌ Cross-pillar content analysis failed")
                return False
            
            self.logger.info("  ✅ Content to Insights workflow successful")
            
            # Test 2: Insights → Operations Workflow
            self.logger.info("  📊→⚙️ Testing Insights to Operations workflow...")
            
            # Use insights to create an optimized process
            if self.analysis_results:
                insights = self.analysis_results[0]
                process_data = {
                    "process_name": "Data-Driven Customer Process",
                    "insights": insights,
                    "optimization_goals": ["efficiency", "accuracy", "customer_satisfaction"]
                }
                
                optimization_result = await self.operations_service.optimize_process(
                    process_data=process_data,
                    user_context=self.user_context,
                    session_id=self.test_session_id
                )
                
                if not optimization_result.get("success"):
                    self.logger.error("❌ Cross-pillar insights to operations workflow failed")
                    return False
                
                self.logger.info("  ✅ Insights to Operations workflow successful")
            
            # Test 3: Operations → Business Outcomes Workflow
            self.logger.info("  ⚙️→🎯 Testing Operations to Business Outcomes workflow...")
            
            # Use operations data for strategic planning
            if self.workflow_results:
                operations_metrics = {
                    "workflows_created": len(self.workflow_results),
                    "processes_optimized": 1,
                    "efficiency_improvements": ["automation", "standardization"]
                }
                
                strategic_data = {
                    "objectives": ["Leverage operational improvements for business growth"],
                    "timeline": "6 months",
                    "budget": 200000,
                    "operations_context": operations_metrics
                }
                
                strategic_result = await self.business_outcomes_service.generate_strategic_roadmap(
                    objectives=strategic_data["objectives"],
                    timeline=strategic_data["timeline"],
                    budget=strategic_data["budget"],
                    user_context=self.user_context,
                    session_id=self.test_session_id
                )
                
                if not strategic_result.get("success"):
                    self.logger.error("❌ Cross-pillar operations to business outcomes workflow failed")
                    return False
                
                self.logger.info("  ✅ Operations to Business Outcomes workflow successful")
            
            # Test 4: End-to-End Workflow
            self.logger.info("  🔄 Testing complete end-to-end workflow...")
            
            # Create a comprehensive workflow that uses all pillars
            end_to_end_data = {
                "content_files": len(self.uploaded_files),
                "insights_analyses": len(self.analysis_results),
                "operations_workflows": len(self.workflow_results),
                "strategic_plans": len(self.strategic_plans),
                "integration_timestamp": datetime.utcnow().isoformat()
            }
            
            # Validate that all pillars have contributed data
            if end_to_end_data["content_files"] == 0:
                self.logger.error("❌ Content pillar not contributing to end-to-end workflow")
                return False
            
            if end_to_end_data["insights_analyses"] == 0:
                self.logger.error("❌ Insights pillar not contributing to end-to-end workflow")
                return False
            
            if end_to_end_data["operations_workflows"] == 0:
                self.logger.error("❌ Operations pillar not contributing to end-to-end workflow")
                return False
            
            if end_to_end_data["strategic_plans"] == 0:
                self.logger.error("❌ Business Outcomes pillar not contributing to end-to-end workflow")
                return False
            
            self.logger.info("  ✅ Complete end-to-end workflow successful")
            
            self.logger.info("✅ Cross-Pillar Workflows passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Cross-pillar workflows test failed: {e}")
            return False
    
    async def test_performance_and_scalability(self) -> bool:
        """Test performance and scalability across all pillars."""
        self.logger.info("🧪 Testing Performance and Scalability...")
        
        try:
            # Test concurrent operations across all pillars
            start_time = datetime.utcnow()
            
            # Create concurrent tasks for all pillars
            tasks = []
            
            # Content pillar tasks
            for i in range(3):
                file_data = f"Performance test file {i+1} content for scalability testing.".encode()
                tasks.append(
                    self.content_service.upload_file(
                        file_data=file_data,
                        filename=f"perf_test_{i+1}.txt",
                        user_context=self.user_context,
                        session_id=f"{self.test_session_id}_perf_{i+1}"
                    )
                )
            
            # Insights pillar tasks
            for i in range(3):
                analysis_data = {
                    "values": [{"x": j, "y": j*2, "category": "A" if j%2==0 else "B"} for j in range(10)]
                }
                tasks.append(
                    self.insights_service.analyze_data(
                        data=analysis_data,
                        analysis_type="descriptive",
                        user_context=self.user_context,
                        session_id=f"{self.test_session_id}_perf_{i+1}"
                    )
                )
            
            # Operations pillar tasks
            for i in range(3):
                sop_data = {
                    "title": f"Performance Test SOP {i+1}",
                    "description": f"Test SOP for performance testing {i+1}",
                    "steps": [f"Step {j+1}" for j in range(5)],
                    "department": "Testing"
                }
                tasks.append(
                    self.operations_service.create_sop(
                        sop_data=sop_data,
                        user_context=self.user_context,
                        session_id=f"{self.test_session_id}_perf_{i+1}"
                    )
                )
            
            # Business Outcomes pillar tasks
            for i in range(3):
                objectives = [f"Performance objective {i+1}.{j+1}" for j in range(3)]
                tasks.append(
                    self.business_outcomes_service.generate_strategic_roadmap(
                        objectives=objectives,
                        timeline="6 months",
                        budget=100000,
                        user_context=self.user_context,
                        session_id=f"{self.test_session_id}_perf_{i+1}"
                    )
                )
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = datetime.utcnow()
            total_time = (end_time - start_time).total_seconds()
            
            # Analyze results
            successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
            failed_results = [r for r in results if not isinstance(r, dict) or not r.get("success")]
            
            success_rate = len(successful_results) / len(tasks) * 100
            throughput = len(tasks) / total_time
            
            self.logger.info(f"  📊 Performance Results:")
            self.logger.info(f"    - Total tasks: {len(tasks)}")
            self.logger.info(f"    - Successful: {len(successful_results)}")
            self.logger.info(f"    - Failed: {len(failed_results)}")
            self.logger.info(f"    - Success rate: {success_rate:.1f}%")
            self.logger.info(f"    - Total time: {total_time:.2f}s")
            self.logger.info(f"    - Throughput: {throughput:.2f} tasks/second")
            
            if success_rate < 80:
                self.logger.error(f"❌ Success rate too low: {success_rate:.1f}%")
                return False
            
            if throughput < 10:
                self.logger.error(f"❌ Throughput too low: {throughput:.2f} tasks/second")
                return False
            
            self.logger.info("✅ Performance and Scalability passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Performance and scalability test failed: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all integration tests for all pillars."""
        self.logger.info("🚀 Starting All Pillars Integration Tests...")
        
        # Setup
        if not await self.setup():
            return False
        
        # Test suite
        tests = [
            ("Content Pillar Integration", self.test_content_pillar_integration),
            ("Insights Pillar Integration", self.test_insights_pillar_integration),
            ("Operations Pillar Integration", self.test_operations_pillar_integration),
            ("Business Outcomes Pillar Integration", self.test_business_outcomes_pillar_integration),
            ("Cross-Pillar Workflows", self.test_cross_pillar_workflows),
            ("Performance and Scalability", self.test_performance_and_scalability)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"Running: {test_name}")
            self.logger.info(f"{'='*80}")
            
            try:
                if await test_func():
                    passed += 1
                    self.logger.info(f"✅ {test_name} PASSED")
                else:
                    self.logger.error(f"❌ {test_name} FAILED")
            except Exception as e:
                self.logger.error(f"❌ {test_name} FAILED with exception: {e}")
        
        # Summary
        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"All Pillars Integration Test Summary")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Tests Passed: {passed}/{total}")
        self.logger.info(f"Success Rate: {(passed/total)*100:.1f}%")
        self.logger.info(f"Test Session ID: {self.test_session_id}")
        
        # Pillar-specific results
        self.logger.info(f"\nPillar Results:")
        self.logger.info(f"  📁 Content: {len(self.uploaded_files)} files processed")
        self.logger.info(f"  📊 Insights: {len(self.analysis_results)} analyses completed")
        self.logger.info(f"  ⚙️ Operations: {len(self.workflow_results)} workflows created")
        self.logger.info(f"  🎯 Business Outcomes: {len(self.strategic_plans)} strategic plans generated")
        
        if passed == total:
            self.logger.info("🎉 ALL TESTS PASSED! All Pillars Integration is working correctly.")
            return True
        else:
            self.logger.error(f"⚠️ {total-passed} tests failed. Check the logs above for details.")
            return False

async def main():
    """Run the all pillars integration tests."""
    tester = AllPillarsIntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ All Pillars Integration Testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ All Pillars Integration Testing failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
