#!/usr/bin/env python3
"""
Operations Pillar End-to-End Test

Comprehensive test of the Operations Pillar functionality including all micro-modules,
infrastructure abstractions, and public works services.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities.security_authorization.security_authorization_utility import UserContext

# Import Operations Pillar micro-modules
from backend.business_enablement.pillars.operations_pillar.micro_modules.sop_visualizer import SOPVisualizerModule
from backend.business_enablement.pillars.operations_pillar.micro_modules.workflow_to_sop_converter import WorkflowToSOPConverterModule
from backend.business_enablement.pillars.operations_pillar.micro_modules.sop_builder_wizard import SOPBuilderWizardModule
from backend.business_enablement.pillars.operations_pillar.micro_modules.sop_to_workflow_converter import SOPToWorkflowConverterModule
from backend.business_enablement.pillars.operations_pillar.micro_modules.workflow_visualizer import WorkflowVisualizerModule
from backend.business_enablement.pillars.operations_pillar.micro_modules.process_optimizer import ProcessOptimizerModule
from backend.business_enablement.pillars.operations_pillar.micro_modules.coexistence_evaluator import CoexistenceEvaluatorModule

# Import public works services
# from foundations.public_works_foundation.services.document_processing_service import DocumentProcessingService
# from foundations.public_works_foundation.services.workflow_management_service import WorkflowManagementService
# from foundations.public_works_foundation.services.process_analysis_service import ProcessAnalysisService

class MockEnvironmentLoader:
    """Mock environment loader for testing."""
    
    def get_content_pillar_config(self):
        return {
            "sop_visualization_config": {},
            "workflow_to_sop_config": {},
            "sop_wizard_config": {},
            "workflow_conversion_rules": {},
            "workflow_visualization_config": {},
            "process_optimization_rules": {},
            "coexistence_evaluation_criteria": {}
        }

async def test_operations_pillar_micro_modules():
    """Test all Operations Pillar micro-modules."""
    print("🧪 Testing Operations Pillar Micro-Modules...")
    
    # Create mock environment loader
    env_loader = MockEnvironmentLoader()
    
    # Test SOP Visualizer Module
    print("\n📄 Testing SOP Visualizer Module...")
    sop_visualizer = SOPVisualizerModule(env_loader)
    await sop_visualizer.initialize()
    
    test_sop_data = {
        "id": "test_sop",
        "title": "Customer Onboarding Process",
        "description": "Standard operating procedure for onboarding new customers",
        "steps": [
            {
                "id": "step_1",
                "order": 1,
                "title": "Collect Customer Information",
                "description": "Gather required customer details and documentation"
            },
            {
                "id": "step_2",
                "order": 2,
                "title": "Validate Information",
                "description": "Verify customer information and documentation"
            },
            {
                "id": "step_3",
                "order": 3,
                "title": "Create Customer Account",
                "description": "Set up customer account in the system"
            },
            {
                "id": "step_4",
                "order": 4,
                "title": "Send Welcome Email",
                "description": "Send confirmation and welcome materials"
            }
        ],
        "version": "1.0"
    }
    
    user_context = UserContext(
        user_id="test_user",
        email="test@example.com",
        full_name="Test User",
        session_id="test_session",
        permissions=["read", "write"]
    )
    
    # Test SOP visualization
    viz_result = await sop_visualizer.visualize_sop(test_sop_data, user_context, "test_session", "standard")
    print(f"SOP Visualization: {'✅' if viz_result['success'] else '❌'} - {viz_result.get('message', '')}")
    
    # Test Workflow to SOP Converter Module
    print("\n🔄 Testing Workflow to SOP Converter Module...")
    workflow_to_sop_converter = WorkflowToSOPConverterModule(env_loader)
    await workflow_to_sop_converter.initialize()
    
    test_workflow_data = {
        "id": "test_workflow",
        "name": "Customer Onboarding Workflow",
        "description": "Automated workflow for customer onboarding",
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "label": "Start Onboarding"
            },
            {
                "id": "task_1",
                "type": "task",
                "label": "Collect Information",
                "metadata": {"responsible": "AI"}
            },
            {
                "id": "task_2",
                "type": "task",
                "label": "Validate Data",
                "metadata": {"responsible": "AI"}
            },
            {
                "id": "task_3",
                "type": "task",
                "label": "Create Account",
                "metadata": {"responsible": "System"}
            },
            {
                "id": "end_1",
                "type": "end",
                "label": "Complete Onboarding"
            }
        ],
        "edges": [
            {"source": "start_1", "target": "task_1"},
            {"source": "task_1", "target": "task_2"},
            {"source": "task_2", "target": "task_3"},
            {"source": "task_3", "target": "end_1"}
        ]
    }
    
    # Test workflow to SOP conversion
    conversion_result = await workflow_to_sop_converter.convert_workflow_to_sop(
        test_workflow_data, user_context, "test_session", "sequential"
    )
    print(f"Workflow to SOP Conversion: {'✅' if conversion_result['success'] else '❌'} - {conversion_result.get('message', '')}")
    
    # Test SOP Builder Wizard Module
    print("\n📋 Testing SOP Builder Wizard Module...")
    sop_builder_wizard = SOPBuilderWizardModule(env_loader)
    await sop_builder_wizard.initialize()
    
    # Test SOP creation
    sop_creation_result = await sop_builder_wizard.create_sop(
        "Test Process Description", user_context, "test_session", {"sop_type": "standard"}
    )
    print(f"SOP Creation: {'✅' if sop_creation_result['success'] else '❌'} - {sop_creation_result.get('message', '')}")
    
    # Test SOP to Workflow Converter Module
    print("\n🔄 Testing SOP to Workflow Converter Module...")
    sop_to_workflow_converter = SOPToWorkflowConverterModule(env_loader)
    await sop_to_workflow_converter.initialize()
    
    # Test SOP to workflow conversion (convert SOP data to string)
    sop_text = f"{test_sop_data['title']}\n{test_sop_data['description']}\n\n"
    for step in test_sop_data['steps']:
        sop_text += f"{step['order']}. {step['title']}\n{step['description']}\n\n"
    
    sop_to_workflow_result = await sop_to_workflow_converter.convert_sop_to_workflow(
        sop_text, user_context, "test_session"
    )
    print(f"SOP to Workflow Conversion: {'✅' if sop_to_workflow_result['success'] else '❌'} - {sop_to_workflow_result.get('message', '')}")
    
    # Test Workflow Visualizer Module
    print("\n📊 Testing Workflow Visualizer Module...")
    workflow_visualizer = WorkflowVisualizerModule(env_loader)
    await workflow_visualizer.initialize()
    
    # Test workflow visualization
    workflow_viz_result = await workflow_visualizer.create_workflow_visualization(
        test_workflow_data, "flowchart", user_context, "test_session"
    )
    print(f"Workflow Visualization: {'✅' if workflow_viz_result['success'] else '❌'} - {workflow_viz_result.get('message', '')}")
    
    # Test Process Optimizer Module
    print("\n⚡ Testing Process Optimizer Module...")
    process_optimizer = ProcessOptimizerModule(env_loader)
    await process_optimizer.initialize()
    
    # Test process optimization
    optimization_result = await process_optimizer.optimize_process(
        test_sop_data, ["efficiency", "cost_reduction"], user_context, "test_session"
    )
    print(f"Process Optimization: {'✅' if optimization_result['success'] else '❌'} - {optimization_result.get('message', '')}")
    
    # Test Coexistence Evaluator Module
    print("\n🤝 Testing Coexistence Evaluator Module...")
    coexistence_evaluator = CoexistenceEvaluatorModule(env_loader)
    await coexistence_evaluator.initialize()
    
    # Test coexistence evaluation
    coexistence_result = await coexistence_evaluator.analyze_coexistence(
        test_sop_data, test_workflow_data, user_context, "test_session"
    )
    print(f"Coexistence Evaluation: {'✅' if coexistence_result['success'] else '❌'} - {coexistence_result.get('message', '')}")
    
    # Cleanup
    await sop_visualizer.shutdown()
    await workflow_to_sop_converter.shutdown()
    await sop_builder_wizard.shutdown()
    await sop_to_workflow_converter.shutdown()
    await workflow_visualizer.shutdown()
    await process_optimizer.shutdown()
    await coexistence_evaluator.shutdown()
    
    return all([
        viz_result['success'],
        conversion_result['success'],
        sop_creation_result['success'],
        sop_to_workflow_result['success'],
        workflow_viz_result['success'],
        optimization_result['success'],
        coexistence_result['success']
    ])

async def test_operations_pillar_services():
    """Test all Operations Pillar public works services."""
    print("\n🏗️ Testing Operations Pillar Public Works Services...")
    
    # Test Document Processing Service
    print("\n📄 Testing Document Processing Service...")
    doc_service = DocumentProcessingService()
    await doc_service.initialize()
    
    # Test SOP to Workflow conversion
    sop_to_workflow_result = await doc_service.convert_sop_to_workflow(test_sop_data)
    print(f"Document Service SOP→Workflow: {'✅' if sop_to_workflow_result['success'] else '❌'}")
    
    # Test Workflow to SOP conversion
    if sop_to_workflow_result['success']:
        workflow_to_sop_result = await doc_service.convert_workflow_to_sop(sop_to_workflow_result['workflow_data'])
        print(f"Document Service Workflow→SOP: {'✅' if workflow_to_sop_result['success'] else '❌'}")
    
    # Test Workflow Management Service
    print("\n🔄 Testing Workflow Management Service...")
    workflow_service = WorkflowManagementService()
    await workflow_service.initialize()
    
    # Test workflow creation
    workflow_creation_result = await workflow_service.create_workflow(test_workflow_data)
    print(f"Workflow Management Creation: {'✅' if workflow_creation_result['success'] else '❌'}")
    
    # Test Process Analysis Service
    print("\n📊 Testing Process Analysis Service...")
    analysis_service = ProcessAnalysisService()
    await analysis_service.initialize()
    
    # Test process consistency analysis
    consistency_result = await analysis_service.analyze_process_consistency(test_sop_data, test_workflow_data)
    print(f"Process Consistency Analysis: {'✅' if consistency_result['success'] else '❌'}")
    
    # Test optimization opportunities
    optimization_result = await analysis_service.identify_optimization_opportunities(test_sop_data)
    print(f"Optimization Opportunities: {'✅' if optimization_result['success'] else '❌'}")
    
    # Test coexistence blueprint
    blueprint_result = await analysis_service.generate_coexistence_blueprint(test_sop_data, test_workflow_data)
    print(f"Coexistence Blueprint: {'✅' if blueprint_result['success'] else '❌'}")
    
    return all([
        sop_to_workflow_result['success'],
        workflow_to_sop_result['success'] if sop_to_workflow_result['success'] else True,
        workflow_creation_result['success'],
        consistency_result['success'],
        optimization_result['success'],
        blueprint_result['success']
    ])

async def test_operations_pillar_integration():
    """Test Operations Pillar integration scenarios."""
    print("\n🔗 Testing Operations Pillar Integration Scenarios...")
    
    # Scenario 1: Complete SOP to Workflow to SOP round trip
    print("\n🔄 Scenario 1: SOP → Workflow → SOP Round Trip...")
    
    doc_service = DocumentProcessingService()
    await doc_service.initialize()
    
    # SOP to Workflow
    sop_to_workflow_result = await doc_service.convert_sop_to_workflow(test_sop_data)
    if not sop_to_workflow_result['success']:
        print("❌ SOP to Workflow conversion failed")
        return False
    
    workflow_data = sop_to_workflow_result['workflow_data']
    print(f"✅ SOP → Workflow: {len(workflow_data['nodes'])} nodes, {len(workflow_data['edges'])} edges")
    
    # Workflow to SOP
    workflow_to_sop_result = await doc_service.convert_workflow_to_sop(workflow_data)
    if not workflow_to_sop_result['success']:
        print("❌ Workflow to SOP conversion failed")
        return False
    
    converted_sop = workflow_to_sop_result['sop_data']
    print(f"✅ Workflow → SOP: {len(converted_sop['steps'])} steps")
    
    # Scenario 2: Process Analysis and Optimization
    print("\n⚡ Scenario 2: Process Analysis and Optimization...")
    
    analysis_service = ProcessAnalysisService()
    await analysis_service.initialize()
    
    # Analyze process consistency
    consistency_result = await analysis_service.analyze_process_consistency(test_sop_data, workflow_data)
    if consistency_result['success']:
        analysis = consistency_result['analysis_result']
        print(f"✅ Process Consistency: {analysis['similarity_score']:.2f} similarity score")
    
    # Identify optimization opportunities
    optimization_result = await analysis_service.identify_optimization_opportunities(test_sop_data)
    if optimization_result['success']:
        analysis = optimization_result['analysis_result']
        print(f"✅ Optimization Opportunities: {analysis['total_opportunities']} found")
    
    # Generate coexistence blueprint
    blueprint_result = await analysis_service.generate_coexistence_blueprint(test_sop_data, workflow_data)
    if blueprint_result['success']:
        blueprint = blueprint_result['blueprint']
        print(f"✅ Coexistence Blueprint: {len(blueprint['recommendations'])} recommendations")
    
    # Scenario 3: Workflow Visualization
    print("\n📊 Scenario 3: Workflow Visualization...")
    
    workflow_service = WorkflowManagementService()
    await workflow_service.initialize()
    
    # Create workflow visualization
    viz_result = await workflow_service.create_workflow_visualization(
        workflow_data.get("id", "test_workflow"), "flowchart"
    )
    if viz_result['success']:
        print(f"✅ Workflow Visualization: {viz_result['visualization_data']['type']} created")
    
    return True

async def main():
    """Run all Operations Pillar tests."""
    print("🚀 Starting Operations Pillar End-to-End Tests...")
    
    # Test micro-modules
    micro_modules_ok = await test_operations_pillar_micro_modules()
    
    # Test public works services
    services_ok = await test_operations_pillar_services()
    
    # Test integration scenarios
    integration_ok = await test_operations_pillar_integration()
    
    # Summary
    print("\n📊 Operations Pillar Test Summary:")
    print(f"Micro-Modules: {'✅' if micro_modules_ok else '❌'}")
    print(f"Public Works Services: {'✅' if services_ok else '❌'}")
    print(f"Integration Scenarios: {'✅' if integration_ok else '❌'}")
    
    overall_success = all([micro_modules_ok, services_ok, integration_ok])
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Operations Pillar is fully functional with real implementations!")
        print("   - All micro-modules working with public works services")
        print("   - Complete SOP ↔ Workflow conversion pipeline")
        print("   - Process analysis and optimization capabilities")
        print("   - Coexistence evaluation and blueprint generation")
        print("   - Workflow visualization and management")
    
    return overall_success

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Define test data
    test_sop_data = {
        "id": "test_sop",
        "title": "Customer Onboarding Process",
        "description": "Standard operating procedure for onboarding new customers",
        "steps": [
            {
                "id": "step_1",
                "order": 1,
                "title": "Collect Customer Information",
                "description": "Gather required customer details and documentation"
            },
            {
                "id": "step_2",
                "order": 2,
                "title": "Validate Information",
                "description": "Verify customer information and documentation"
            },
            {
                "id": "step_3",
                "order": 3,
                "title": "Create Customer Account",
                "description": "Set up customer account in the system"
            },
            {
                "id": "step_4",
                "order": 4,
                "title": "Send Welcome Email",
                "description": "Send confirmation and welcome materials"
            }
        ],
        "version": "1.0"
    }
    
    test_workflow_data = {
        "id": "test_workflow",
        "name": "Customer Onboarding Workflow",
        "description": "Automated workflow for customer onboarding",
        "nodes": [
            {
                "id": "start_1",
                "type": "start",
                "label": "Start Onboarding"
            },
            {
                "id": "task_1",
                "type": "task",
                "label": "Collect Information",
                "metadata": {"responsible": "AI"}
            },
            {
                "id": "task_2",
                "type": "task",
                "label": "Validate Data",
                "metadata": {"responsible": "AI"}
            },
            {
                "id": "task_3",
                "type": "task",
                "label": "Create Account",
                "metadata": {"responsible": "System"}
            },
            {
                "id": "end_1",
                "type": "end",
                "label": "Complete Onboarding"
            }
        ],
        "edges": [
            {"source": "start_1", "target": "task_1"},
            {"source": "task_1", "target": "task_2"},
            {"source": "task_2", "target": "task_3"},
            {"source": "task_3", "target": "end_1"}
        ]
    }
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
