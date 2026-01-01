#!/usr/bin/env python3
"""
Test Operations Infrastructure

Test the newly created Operations Pillar infrastructure abstractions and services.
"""

import asyncio
import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.infrastructure_foundation.abstractions.docx_processing_abstraction import DocxProcessingAbstraction
from foundations.infrastructure_foundation.abstractions.bpmn_processing_abstraction import BpmnProcessingAbstraction
from foundations.infrastructure_foundation.abstractions.sop_parsing_abstraction import SopParsingAbstraction
from foundations.infrastructure_foundation.abstractions.workflow_visualization_abstraction import WorkflowVisualizationAbstraction

# from foundations.public_works_foundation.services.document_processing_service import DocumentProcessingService
# from foundations.public_works_foundation.services.workflow_management_service import WorkflowManagementService
# from foundations.public_works_foundation.services.process_analysis_service import ProcessAnalysisService

async def test_infrastructure_abstractions():
    """Test all infrastructure abstractions."""
    print("🧪 Testing Infrastructure Abstractions...")
    
    # Test DOCX Processing Abstraction
    print("\n📄 Testing DOCX Processing Abstraction...")
    docx_abstraction = DocxProcessingAbstraction()
    docx_health = await docx_abstraction.health_check()
    print(f"DOCX Health: {'✅' if docx_health['success'] else '❌'} - {docx_health['message']}")
    
    # Test BPMN Processing Abstraction
    print("\n🔄 Testing BPMN Processing Abstraction...")
    bpmn_abstraction = BpmnProcessingAbstraction()
    bpmn_health = await bpmn_abstraction.health_check()
    print(f"BPMN Health: {'✅' if bpmn_health['success'] else '❌'} - {bpmn_health['message']}")
    
    # Test SOP Parsing Abstraction
    print("\n📋 Testing SOP Parsing Abstraction...")
    sop_parsing_abstraction = SopParsingAbstraction()
    sop_parsing_health = await sop_parsing_abstraction.health_check()
    print(f"SOP Parsing Health: {'✅' if sop_parsing_health['success'] else '❌'} - {sop_parsing_health['message']}")
    
    # Test Workflow Visualization Abstraction
    print("\n📊 Testing Workflow Visualization Abstraction...")
    workflow_viz_abstraction = WorkflowVisualizationAbstraction()
    workflow_viz_health = await workflow_viz_abstraction.health_check()
    print(f"Workflow Visualization Health: {'✅' if workflow_viz_health['success'] else '❌'} - {workflow_viz_health['message']}")
    
    return all([
        docx_health['success'],
        bpmn_health['success'],
        sop_parsing_health['success'],
        workflow_viz_health['success']
    ])

async def test_public_works_services():
    """Test all public works services."""
    print("\n🏗️ Testing Public Works Services...")
    
    # Test Document Processing Service
    print("\n📄 Testing Document Processing Service...")
    doc_service = DocumentProcessingService()
    await doc_service.initialize()
    doc_service_info = await doc_service.get_service_info()
    print(f"Document Processing Service: {'✅' if doc_service_info['initialized'] else '❌'}")
    print(f"  Capabilities: {len(doc_service_info['capabilities'])}")
    
    # Test Workflow Management Service
    print("\n🔄 Testing Workflow Management Service...")
    workflow_service = WorkflowManagementService()
    await workflow_service.initialize()
    workflow_service_info = await workflow_service.get_service_info()
    print(f"Workflow Management Service: {'✅' if workflow_service_info['initialized'] else '❌'}")
    print(f"  Capabilities: {len(workflow_service_info['capabilities'])}")
    
    # Test Process Analysis Service
    print("\n📊 Testing Process Analysis Service...")
    analysis_service = ProcessAnalysisService()
    await analysis_service.initialize()
    analysis_service_info = await analysis_service.get_service_info()
    print(f"Process Analysis Service: {'✅' if analysis_service_info['initialized'] else '❌'}")
    print(f"  Capabilities: {len(analysis_service_info['capabilities'])}")
    
    return all([
        doc_service_info['initialized'],
        workflow_service_info['initialized'],
        analysis_service_info['initialized']
    ])

async def test_sop_workflow_conversion():
    """Test SOP ↔ Workflow conversion functionality."""
    print("\n🔄 Testing SOP ↔ Workflow Conversion...")
    
    # Create test SOP data
    test_sop_data = {
        "id": "test_sop",
        "title": "Test Standard Operating Procedure",
        "description": "A test SOP for conversion testing",
        "steps": [
            {
                "id": "step_1",
                "order": 1,
                "title": "Start Process",
                "description": "Begin the operational process"
            },
            {
                "id": "step_2",
                "order": 2,
                "title": "Execute Task",
                "description": "Perform the main operational task"
            },
            {
                "id": "step_3",
                "order": 3,
                "title": "Validate Results",
                "description": "Check and validate the task results"
            },
            {
                "id": "step_4",
                "order": 4,
                "title": "Complete Process",
                "description": "Finalize and complete the process"
            }
        ],
        "version": "1.0"
    }
    
    # Test SOP to Workflow conversion
    doc_service = DocumentProcessingService()
    await doc_service.initialize()
    
    sop_to_workflow_result = await doc_service.convert_sop_to_workflow(test_sop_data)
    print(f"SOP → Workflow: {'✅' if sop_to_workflow_result['success'] else '❌'}")
    if sop_to_workflow_result['success']:
        workflow_data = sop_to_workflow_result['workflow_data']
        print(f"  Generated {len(workflow_data['nodes'])} nodes and {len(workflow_data['edges'])} edges")
    
    # Test Workflow to SOP conversion
    if sop_to_workflow_result['success']:
        workflow_to_sop_result = await doc_service.convert_workflow_to_sop(sop_to_workflow_result['workflow_data'])
        print(f"Workflow → SOP: {'✅' if workflow_to_sop_result['success'] else '❌'}")
        if workflow_to_sop_result['success']:
            converted_sop = workflow_to_sop_result['sop_data']
            print(f"  Generated {len(converted_sop['steps'])} steps")
    
    return sop_to_workflow_result['success'] and workflow_to_sop_result['success']

async def test_process_analysis():
    """Test process analysis functionality."""
    print("\n📊 Testing Process Analysis...")
    
    # Create test data
    test_sop_data = {
        "id": "test_sop",
        "title": "Customer Onboarding Process",
        "description": "Process for onboarding new customers",
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
        ]
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
    
    # Test process analysis
    analysis_service = ProcessAnalysisService()
    await analysis_service.initialize()
    
    # Test consistency analysis
    consistency_result = await analysis_service.analyze_process_consistency(test_sop_data, test_workflow_data)
    print(f"Process Consistency Analysis: {'✅' if consistency_result['success'] else '❌'}")
    if consistency_result['success']:
        analysis = consistency_result['analysis_result']
        print(f"  Similarity Score: {analysis['similarity_score']:.2f}")
        print(f"  Is Consistent: {analysis['is_consistent']}")
    
    # Test optimization opportunities
    optimization_result = await analysis_service.identify_optimization_opportunities(test_sop_data)
    print(f"Optimization Analysis: {'✅' if optimization_result['success'] else '❌'}")
    if optimization_result['success']:
        analysis = optimization_result['analysis_result']
        print(f"  Opportunities Found: {analysis['total_opportunities']}")
        print(f"  High Impact: {analysis['high_impact_opportunities']}")
    
    # Test coexistence blueprint
    blueprint_result = await analysis_service.generate_coexistence_blueprint(test_sop_data, test_workflow_data)
    print(f"Coexistence Blueprint: {'✅' if blueprint_result['success'] else '❌'}")
    if blueprint_result['success']:
        blueprint = blueprint_result['blueprint']
        print(f"  Recommendations: {len(blueprint['recommendations'])}")
        print(f"  Implementation Phases: {len(blueprint['implementation_plan'])}")
    
    return all([
        consistency_result['success'],
        optimization_result['success'],
        blueprint_result['success']
    ])

async def main():
    """Run all tests."""
    print("🚀 Starting Operations Infrastructure Tests...")
    
    # Test infrastructure abstractions
    abstractions_ok = await test_infrastructure_abstractions()
    
    # Test public works services
    services_ok = await test_public_works_services()
    
    # Test SOP ↔ Workflow conversion
    conversion_ok = await test_sop_workflow_conversion()
    
    # Test process analysis
    analysis_ok = await test_process_analysis()
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"Infrastructure Abstractions: {'✅' if abstractions_ok else '❌'}")
    print(f"Public Works Services: {'✅' if services_ok else '❌'}")
    print(f"SOP ↔ Workflow Conversion: {'✅' if conversion_ok else '❌'}")
    print(f"Process Analysis: {'✅' if analysis_ok else '❌'}")
    
    overall_success = all([abstractions_ok, services_ok, conversion_ok, analysis_ok])
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


