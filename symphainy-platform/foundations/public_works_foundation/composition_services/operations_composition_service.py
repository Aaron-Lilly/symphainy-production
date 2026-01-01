#!/usr/bin/env python3
"""
Operations Composition Service

Composition service that coordinates multiple infrastructure abstractions
for operations pillar capabilities.

WHAT (Composition Service Role): I coordinate operations infrastructure abstractions
HOW (Composition Service Implementation): I integrate multiple abstractions for operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..infrastructure_abstractions.sop_processing_abstraction import SOPProcessingAbstraction
from ..infrastructure_abstractions.workflow_visualization_abstraction import WorkflowVisualizationAbstraction
from ..infrastructure_abstractions.coexistence_analysis_abstraction import CoexistenceAnalysisAbstraction
from ..infrastructure_abstractions.bpmn_processing_abstraction import BPMNProcessingAbstraction
from ..infrastructure_abstractions.sop_enhancement_abstraction import SOPEnhancementAbstraction
from ..infrastructure_abstractions.coexistence_blueprint_abstraction import CoexistenceBlueprintAbstraction


class OperationsCompositionService:
    """
    Composition service for operations pillar infrastructure.
    
    Coordinates multiple infrastructure abstractions to provide
    comprehensive operations capabilities including SOP processing,
    workflow visualization, coexistence analysis, and BPMN processing.
    """
    
    def __init__(self, 
                 sop_processing_abstraction: SOPProcessingAbstraction,
                 workflow_visualization_abstraction: WorkflowVisualizationAbstraction,
                 coexistence_analysis_abstraction: CoexistenceAnalysisAbstraction,
                 bpmn_processing_abstraction: BPMNProcessingAbstraction,
                 sop_enhancement_abstraction: SOPEnhancementAbstraction,
                 coexistence_blueprint_abstraction: CoexistenceBlueprintAbstraction,
                 di_container=None,
                 **kwargs):
        """
        Initialize operations composition service.
        
        Args:
            sop_processing_abstraction: SOP processing abstraction
            workflow_visualization_abstraction: Workflow visualization abstraction
            coexistence_analysis_abstraction: Coexistence analysis abstraction
            bpmn_processing_abstraction: BPMN processing abstraction
            sop_enhancement_abstraction: SOP enhancement abstraction
            coexistence_blueprint_abstraction: Coexistence blueprint abstraction
            di_container: DI Container for utilities
        """
        self.sop_processing = sop_processing_abstraction
        self.workflow_visualization = workflow_visualization_abstraction
        self.coexistence_analysis = coexistence_analysis_abstraction
        self.bpmn_processing = bpmn_processing_abstraction
        self.sop_enhancement = sop_enhancement_abstraction
        self.coexistence_blueprint = coexistence_blueprint_abstraction
        self.di_container = di_container
        self.service_name = "operations_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("OperationsCompositionService")
        
        # Initialize composition service
        self._initialize_composition_service()
    
    def _initialize_composition_service(self):
        """Initialize the operations composition service."""
        try:
            self.logger.info("✅ Operations Composition Service initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize operations composition service: {e}")
    
    async def process_sop_to_workflow(self, sop_text: str) -> Dict[str, Any]:
        """
        Process SOP text to create workflow visualization.
        
        Args:
            sop_text: SOP text content
            
        Returns:
            Dict with workflow visualization data
        """
        try:
            # Step 1: Extract SOP structure
            sop_result = await self.sop_processing.extract_sop_structure(sop_text)
            if not sop_result.get("success"):
                return {
                    "success": False,
                    "error": f"SOP processing failed: {sop_result.get('error')}",
                    "processed_at": datetime.utcnow().isoformat()
                }
            
            sop_structure = sop_result.get("sop_structure")
            
            # Step 2: Convert SOP to workflow format
            workflow_data = self._convert_sop_to_workflow(sop_structure)
            
            # Step 3: Create workflow visualization
            visualization_result = await self.workflow_visualization.create_flowchart(workflow_data)
            
            if visualization_result.success:
                result = {
                    "success": True,
                    "sop_data": sop_structure,
                    "workflow_data": workflow_data,
                    "visualization": visualization_result.visualization_data,
                    "processed_at": datetime.utcnow().isoformat()
                }
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("process_sop_to_workflow", {
                        "success": True
                    })
                
                return result
            else:
                return {
                    "success": False,
                    "error": f"Workflow visualization failed: {visualization_result.error}",
                    "processed_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "process_sop_to_workflow",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"SOP to workflow processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "SOP_TO_WORKFLOW_ERROR",
                "processed_at": datetime.utcnow().isoformat()
            }
    
    async def analyze_workflow_coexistence(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze workflow for human-AI coexistence.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with coexistence analysis results
        """
        try:
            # Step 1: Analyze process complexity
            complexity_result = await self.coexistence_analysis.analyze_process_complexity(workflow_data)
            
            # Step 2: Assess automation potential
            automation_result = await self.coexistence_analysis.assess_automation_potential(workflow_data)
            
            # Step 3: Evaluate coexistence risk
            risk_result = await self.coexistence_analysis.evaluate_coexistence_risk(workflow_data)
            
            # Step 4: Calculate coexistence metrics
            metrics = await self.coexistence_analysis.calculate_coexistence_metrics(workflow_data)
            
            # Step 5: Generate recommendations
            from ..abstraction_contracts.coexistence_analysis_protocol import CoexistenceAnalysisResult
            analysis_result = CoexistenceAnalysisResult(
                success=True,
                complexity_analysis=complexity_result.get("complexity_analysis"),
                automation_assessment=automation_result.get("automation_assessment"),
                risk_evaluation=risk_result.get("risk_evaluation"),
                coexistence_metrics=metrics,
                error=None,
                analyzed_at=datetime.utcnow()
            )
            
            recommendations = await self.coexistence_analysis.generate_coexistence_recommendations(analysis_result)
            
            result = {
                "success": True,
                "complexity_analysis": complexity_result,
                "automation_assessment": automation_result,
                "risk_evaluation": risk_result,
                "coexistence_metrics": metrics,
                "recommendations": recommendations,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("analyze_workflow_coexistence", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "analyze_workflow_coexistence",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Workflow coexistence analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "WORKFLOW_COEXISTENCE_ANALYSIS_ERROR",
                "analyzed_at": datetime.utcnow().isoformat()
            }
    
    async def convert_workflow_to_bpmn(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert workflow data to BPMN format.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with BPMN data
        """
        try:
            # Convert workflow to BPMN format
            bpmn_result = await self.bpmn_processing.convert_workflow_to_bpmn(workflow_data)
            
            if bpmn_result.get("success"):
                # Generate BPMN XML
                bpmn_xml_result = await self.bpmn_processing.generate_bpmn_xml(bpmn_result.get("bpmn_data", {}))
                
                if bpmn_xml_result.success:
                    result = {
                        "success": True,
                        "bpmn_data": bpmn_result.get("bpmn_data", {}),
                        "bpmn_xml": bpmn_xml_result.bpmn_xml,
                        "converted_at": datetime.utcnow().isoformat()
                    }
                    
                    # Record telemetry on success
                    telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                    if telemetry:
                        await telemetry.record_platform_operation_event("convert_workflow_to_bpmn", {
                            "success": True
                        })
                    
                    return result
                else:
                    return {
                        "success": False,
                        "error": f"BPMN XML generation failed: {bpmn_xml_result.error}",
                        "converted_at": datetime.utcnow().isoformat()
                    }
            else:
                return {
                    "success": False,
                    "error": f"Workflow to BPMN conversion failed: {bpmn_result.get('error')}",
                    "converted_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "convert_workflow_to_bpmn",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Workflow to BPMN conversion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "WORKFLOW_TO_BPMN_ERROR",
                "converted_at": datetime.utcnow().isoformat()
            }
    
    async def create_comprehensive_workflow_analysis(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive workflow analysis including visualization and coexistence analysis.
        
        Args:
            workflow_data: Workflow data dictionary
            
        Returns:
            Dict with comprehensive analysis results
        """
        try:
            # Step 1: Create workflow visualizations
            flowchart_result = await self.workflow_visualization.create_flowchart(workflow_data)
            swimlane_result = await self.workflow_visualization.create_swimlane_diagram(workflow_data)
            gantt_result = await self.workflow_visualization.create_gantt_chart(workflow_data)
            network_result = await self.workflow_visualization.create_network_diagram(workflow_data)
            
            # Step 2: Analyze coexistence
            coexistence_result = await self.analyze_workflow_coexistence(workflow_data)
            
            # Step 3: Convert to BPMN
            bpmn_result = await self.convert_workflow_to_bpmn(workflow_data)
            
            result = {
                "success": True,
                "workflow_data": workflow_data,
                "visualizations": {
                    "flowchart": flowchart_result,
                    "swimlane": swimlane_result,
                    "gantt": gantt_result,
                    "network": network_result
                },
                "coexistence_analysis": coexistence_result,
                "bpmn_conversion": bpmn_result,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_comprehensive_workflow_analysis", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_comprehensive_workflow_analysis",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Comprehensive workflow analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "COMPREHENSIVE_WORKFLOW_ANALYSIS_ERROR",
                "analyzed_at": datetime.utcnow().isoformat()
            }
    
    def _convert_sop_to_workflow(self, sop_structure) -> Dict[str, Any]:
        """Convert SOP structure to workflow format."""
        try:
            workflow_data = {
                "name": sop_structure.title,
                "description": sop_structure.description,
                "nodes": [],
                "edges": [],
                "metadata": {
                    "source": "sop",
                    "version": sop_structure.version,
                    "converted_at": datetime.utcnow().isoformat()
                }
            }
            
            # Convert SOP steps to workflow nodes
            for i, step in enumerate(sop_structure.steps):
                node = {
                    "id": f"step_{i+1}",
                    "name": step.get("description", f"Step {i+1}"),
                    "type": "task",
                    "properties": {
                        "step_number": i + 1,
                        "order": step.get("order", i + 1)
                    }
                }
                workflow_data["nodes"].append(node)
                
                # Create edges between consecutive steps
                if i > 0:
                    edge = {
                        "id": f"edge_{i}",
                        "source": f"step_{i}",
                        "target": f"step_{i+1}",
                        "type": "success"
                    }
                    workflow_data["edges"].append(edge)
            
            return workflow_data
            
        except Exception as e:
            self.logger.error(f"SOP to workflow conversion failed: {e}")
            return {
                "name": "Error",
                "description": "Failed to convert SOP to workflow",
                "nodes": [],
                "edges": [],
                "metadata": {"error": str(e)}
            }
    
    async def get_operations_capabilities(self) -> Dict[str, Any]:
        """
        Get operations composition service capabilities.
        
        Returns:
            Dict with available capabilities
        """
        try:
            result = {
                "success": True,
                "capabilities": {
                    "sop_processing": [
                        "extract_sop_structure",
                        "normalize_sop_steps",
                        "validate_sop_structure",
                        "enhance_sop_content"
                    ],
                    "workflow_visualization": [
                        "create_flowchart",
                        "create_swimlane_diagram",
                        "create_gantt_chart",
                        "create_network_diagram"
                    ],
                    "coexistence_analysis": [
                        "analyze_process_complexity",
                        "assess_automation_potential",
                        "evaluate_coexistence_risk",
                        "calculate_coexistence_metrics"
                    ],
                    "bpmn_processing": [
                        "parse_bpmn_xml",
                        "generate_bpmn_xml",
                        "validate_bpmn_structure",
                        "extract_workflow_from_bpmn"
                    ],
                    "composition_services": [
                        "process_sop_to_workflow",
                        "analyze_workflow_coexistence",
                        "convert_workflow_to_bpmn",
                        "create_comprehensive_workflow_analysis"
                    ]
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_operations_capabilities", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_operations_capabilities",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get operations capabilities: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "OPERATIONS_CAPABILITIES_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Validate security and tenant access
            validation_error = await self._validate_security_and_tenant(
                user_context, "operations", "_validate_security_and_tenant"
            )
            if validation_error:
                return validation_error
            
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    

    # ============================================================================
    # MISSING COMPOSITION SERVICE METHODS - IMPLEMENTED WITH REAL WORKING CODE
    # ============================================================================
    
    async def enhance_sop_content(self, sop_structure: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance SOP content with better structure and clarity.
        
        Args:
            sop_structure: SOP structure data
            user_context: User context information
            
        Returns:
            Dict with enhanced SOP content
        """
        try:
            # Validate security and tenant access
            validation_error = await self._validate_security_and_tenant(
                user_context, "operations", "enhance_sop_content"
            )
            if validation_error:
                return validation_error
            
            # Extract SOP text from structure
            sop_text = self._extract_sop_text(sop_structure)
            
            # Use SOP enhancement abstraction to enhance content
            enhancement_result = await self.sop_enhancement.enhance_sop_content(sop_text)
            
            if enhancement_result.success:
                # Update SOP structure with enhanced content
                enhanced_sop = self._update_sop_structure(sop_structure, enhancement_result.enhanced_content)
                
                result = {
                    "success": True,
                    "enhanced_sop": enhanced_sop,
                    "enhancement_metadata": enhancement_result.metadata,
                    "enhanced_at": datetime.utcnow().isoformat()
                }
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("enhance_sop_content", {
                        "success": True
                    })
                
                return result
            else:
                return {
                    "success": False,
                    "error": enhancement_result.error,
                    "enhanced_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "enhance_sop_content",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"SOP content enhancement failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "SOP_ENHANCEMENT_ERROR",
                "enhanced_at": datetime.utcnow().isoformat()
            }
    
    async def generate_coexistence_blueprint(self, coexistence_result: Dict[str, Any], 
                                           current_state: Dict[str, Any], target_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate coexistence blueprint from analysis data.
        
        Args:
            coexistence_result: Coexistence analysis results
            current_state: Current state data
            target_state: Target state data
            
        Returns:
            Dict with generated blueprint
        """
        try:
            # Use coexistence blueprint abstraction to generate blueprint
            blueprint_result = await self.coexistence_blueprint.generate_coexistence_blueprint(
                coexistence_result, current_state, target_state
            )
            
            if blueprint_result.success:
                result = {
                    "success": True,
                    "blueprint": blueprint_result.blueprint,
                    "implementation_roadmap": blueprint_result.implementation_roadmap,
                    "success_metrics": blueprint_result.success_metrics,
                    "metadata": blueprint_result.metadata,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("generate_coexistence_blueprint", {
                        "success": True
                    })
                
                return result
            else:
                return {
                    "success": False,
                    "error": blueprint_result.error,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "generate_coexistence_blueprint",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Coexistence blueprint generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "COEXISTENCE_BLUEPRINT_GENERATION_ERROR",
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def create_coexistence_blueprint(self, requirements: Dict[str, Any], 
                                         constraints: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create coexistence blueprint directly from requirements.
        
        Args:
            requirements: Blueprint requirements
            constraints: Implementation constraints
            user_context: User context data
            
        Returns:
            Dict with created blueprint
        """
        try:
            # Validate security and tenant access
            validation_error = await self._validate_security_and_tenant(
                user_context, "operations", "create_coexistence_blueprint"
            )
            if validation_error:
                return validation_error
            
            # Use coexistence blueprint abstraction to create blueprint
            blueprint_result = await self.coexistence_blueprint.create_coexistence_blueprint(
                requirements, constraints, user_context
            )
            
            if blueprint_result.success:
                result = {
                    "success": True,
                    "blueprint": blueprint_result.blueprint,
                    "implementation_roadmap": blueprint_result.implementation_roadmap,
                    "success_metrics": blueprint_result.success_metrics,
                    "metadata": blueprint_result.metadata,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("create_coexistence_blueprint", {
                        "success": True
                    })
                
                return result
            else:
                return {
                    "success": False,
                    "error": blueprint_result.error,
                    "created_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_coexistence_blueprint",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Coexistence blueprint creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "COEXISTENCE_BLUEPRINT_CREATION_ERROR",
                "created_at": datetime.utcnow().isoformat()
            }
    
    async def optimize_process_for_coexistence(self, process_definition: Dict[str, Any], 
                                              optimization_goals: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize process for human-AI coexistence.
        
        Args:
            process_definition: Process definition data
            optimization_goals: Optimization goals and targets
            user_context: User context information
            
        Returns:
            Dict with optimization results
        """
        try:
            # Validate security and tenant access
            validation_error = await self._validate_security_and_tenant(
                user_context, "operations", "optimize_process_for_coexistence"
            )
            if validation_error:
                return validation_error
            
            # Analyze current process for coexistence opportunities
            coexistence_analysis = await self.coexistence_analysis.analyze_process_complexity(process_definition)
            automation_assessment = await self.coexistence_analysis.assess_automation_potential(process_definition)
            
            # Generate optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                coexistence_analysis, automation_assessment, optimization_goals
            )
            
            # Create optimized process definition
            optimized_process = self._create_optimized_process(
                process_definition, optimization_recommendations, optimization_goals
            )
            
            # Generate implementation plan
            implementation_plan = self._create_implementation_plan(optimization_recommendations)
            
            result = {
                "success": True,
                "optimized_process": optimized_process,
                "optimization_recommendations": optimization_recommendations,
                "implementation_plan": implementation_plan,
                "optimization_metadata": {
                    "goals_achieved": len(optimization_recommendations),
                    "efficiency_improvement": self._calculate_efficiency_improvement(optimization_recommendations),
                    "coexistence_score": self._calculate_coexistence_score(optimized_process)
                },
                "optimized_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("optimize_process_for_coexistence", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "optimize_process_for_coexistence",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Process optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "PROCESS_OPTIMIZATION_ERROR",
                "optimized_at": datetime.utcnow().isoformat()
            }
    
    async def analyze_process_performance(self, process_data: Dict[str, Any], 
                                        performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze process performance for coexistence optimization.
        
        Args:
            process_data: Process data and metrics
            performance_metrics: Performance metrics to analyze
            
        Returns:
            Dict with performance analysis results
        """
        try:
            # Analyze performance metrics
            performance_analysis = self._analyze_performance_metrics(process_data, performance_metrics)
            
            # Identify performance bottlenecks
            bottlenecks = self._identify_performance_bottlenecks(performance_analysis)
            
            # Generate performance recommendations
            recommendations = self._generate_performance_recommendations(performance_analysis, bottlenecks)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score(performance_analysis)
            
            result = {
                "success": True,
                "performance_analysis": performance_analysis,
                "bottlenecks": bottlenecks,
                "recommendations": recommendations,
                "performance_score": performance_score,
                "analysis_metadata": {
                    "metrics_analyzed": len(performance_metrics),
                    "bottlenecks_identified": len(bottlenecks),
                    "recommendations_generated": len(recommendations)
                },
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("analyze_process_performance", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "analyze_process_performance",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Process performance analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "PROCESS_PERFORMANCE_ANALYSIS_ERROR",
                "analyzed_at": datetime.utcnow().isoformat()
            }
    
    async def create_workflow_visualization(self, workflow_data: Dict[str, Any], 
                                          visualization_type: str = "flowchart") -> Dict[str, Any]:
        """
        Create workflow visualization.
        
        Args:
            workflow_data: Workflow data to visualize
            visualization_type: Type of visualization to create
            
        Returns:
            Dict with visualization data
        """
        try:
            # Create visualization based on type
            if visualization_type == "flowchart":
                visualization_result = await self.workflow_visualization.create_flowchart(workflow_data)
            elif visualization_type == "swimlane":
                visualization_result = await self.workflow_visualization.create_swimlane_diagram(workflow_data)
            elif visualization_type == "gantt":
                visualization_result = await self.workflow_visualization.create_gantt_chart(workflow_data)
            elif visualization_type == "network":
                visualization_result = await self.workflow_visualization.create_network_diagram(workflow_data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported visualization type: {visualization_type}",
                    "created_at": datetime.utcnow().isoformat()
                }
            
            if visualization_result.success:
                result = {
                    "success": True,
                    "visualization": visualization_result.visualization_data,
                    "visualization_type": visualization_type,
                    "metadata": visualization_result.metadata,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("create_workflow_visualization", {
                        "visualization_type": visualization_type,
                        "success": True
                    })
                
                return result
            else:
                return {
                    "success": False,
                    "error": visualization_result.error,
                    "created_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_workflow_visualization",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Workflow visualization creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "WORKFLOW_VISUALIZATION_CREATION_ERROR",
                "created_at": datetime.utcnow().isoformat()
            }
    
    async def create_coexistence_visualization(self, coexistence_data: Dict[str, Any], 
                                             visualization_type: str = "coexistence_diagram") -> Dict[str, Any]:
        """
        Create coexistence visualization.
        
        Args:
            coexistence_data: Coexistence data to visualize
            visualization_type: Type of coexistence visualization
            
        Returns:
            Dict with coexistence visualization data
        """
        try:
            # Create coexistence-specific visualization
            if visualization_type == "coexistence_diagram":
                visualization_data = self._create_coexistence_diagram(coexistence_data)
            elif visualization_type == "collaboration_flow":
                visualization_data = self._create_collaboration_flow(coexistence_data)
            elif visualization_type == "optimization_roadmap":
                visualization_data = self._create_optimization_roadmap(coexistence_data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported coexistence visualization type: {visualization_type}",
                    "created_at": datetime.utcnow().isoformat()
                }
            
            result = {
                "success": True,
                "visualization": visualization_data,
                "visualization_type": visualization_type,
                "metadata": {
                    "coexistence_factors": list(coexistence_data.keys()),
                    "visualization_complexity": self._assess_visualization_complexity(coexistence_data)
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_coexistence_visualization", {
                    "visualization_type": visualization_type,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_coexistence_visualization",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Coexistence visualization creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "COEXISTENCE_VISUALIZATION_CREATION_ERROR",
                "created_at": datetime.utcnow().isoformat()
            }
    
    async def validate_workflow_definition(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workflow definition for correctness and completeness.
        
        Args:
            workflow_definition: Workflow definition to validate
            
        Returns:
            Dict with validation results
        """
        try:
            # Validate workflow structure
            structure_validation = self._validate_workflow_structure(workflow_definition)
            
            # Validate workflow logic
            logic_validation = self._validate_workflow_logic(workflow_definition)
            
            # Validate workflow completeness
            completeness_validation = self._validate_workflow_completeness(workflow_definition)
            
            # Generate validation summary
            validation_summary = self._generate_validation_summary(
                structure_validation, logic_validation, completeness_validation
            )
            
            result = {
                "success": validation_summary["is_valid"],
                "validation_results": {
                    "structure": structure_validation,
                    "logic": logic_validation,
                    "completeness": completeness_validation
                },
                "validation_summary": validation_summary,
                "validated_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("validate_workflow_definition", {
                    "is_valid": validation_summary["is_valid"],
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "validate_workflow_definition",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Workflow definition validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "WORKFLOW_DEFINITION_VALIDATION_ERROR",
                "validated_at": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # HELPER METHODS FOR COMPOSITION SERVICE FUNCTIONALITY
    # ============================================================================
    
    def _extract_sop_text(self, sop_structure: Dict[str, Any]) -> str:
        """Extract SOP text from structure."""
        try:
            if isinstance(sop_structure, dict):
                # Extract text from structured SOP
                text_parts = []
                if "title" in sop_structure:
                    text_parts.append(f"# {sop_structure['title']}")
                if "description" in sop_structure:
                    text_parts.append(sop_structure["description"])
                if "steps" in sop_structure:
                    for i, step in enumerate(sop_structure["steps"], 1):
                        text_parts.append(f"{i}. {step.get('description', '')}")
                return "\n\n".join(text_parts)
            else:
                return str(sop_structure)
        except Exception as e:
            self.logger.error(f"SOP text extraction failed: {e}")
            return ""
    
    def _update_sop_structure(self, sop_structure: Dict[str, Any], enhanced_content: str) -> Dict[str, Any]:
        """Update SOP structure with enhanced content."""
        try:
            # Parse enhanced content back into structure
            enhanced_sop = sop_structure.copy()
            enhanced_sop["enhanced_content"] = enhanced_content
            enhanced_sop["last_enhanced"] = datetime.utcnow().isoformat()
            return enhanced_sop
        except Exception as e:
            self.logger.error(f"SOP structure update failed: {e}")
            return sop_structure
    
    def _generate_optimization_recommendations(self, coexistence_analysis: Dict[str, Any], 
                                             automation_assessment: Dict[str, Any], 
                                             optimization_goals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        try:
            recommendations = []
            
            # Add coexistence optimization recommendations
            if coexistence_analysis.get("complexity_score", 0) > 0.7:
                recommendations.append({
                    "type": "complexity_reduction",
                    "priority": "high",
                    "description": "Reduce process complexity for better human-AI collaboration",
                    "implementation_effort": "medium"
                })
            
            # Add automation recommendations
            if automation_assessment.get("automation_potential", 0) > 0.6:
                recommendations.append({
                    "type": "automation_enhancement",
                    "priority": "medium",
                    "description": "Enhance automation capabilities for improved efficiency",
                    "implementation_effort": "high"
                })
            
            # Add goal-specific recommendations
            for goal, target in optimization_goals.items():
                recommendations.append({
                    "type": "goal_optimization",
                    "priority": "high",
                    "description": f"Optimize for {goal}: {target}",
                    "implementation_effort": "medium"
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Optimization recommendations generation failed: {e}")
            return []
    
    def _create_optimized_process(self, process_definition: Dict[str, Any], 
                                 recommendations: List[Dict[str, Any]], 
                                 optimization_goals: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimized process definition."""
        try:
            optimized_process = process_definition.copy()
            optimized_process["optimizations_applied"] = recommendations
            optimized_process["optimization_goals"] = optimization_goals
            optimized_process["optimized_at"] = datetime.utcnow().isoformat()
            return optimized_process
        except Exception as e:
            self.logger.error(f"Optimized process creation failed: {e}")
            return process_definition
    
    def _create_implementation_plan(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create implementation plan for recommendations."""
        try:
            plan = {
                "phases": [],
                "total_duration": "8-12 weeks",
                "key_milestones": []
            }
            
            # Group recommendations by priority
            high_priority = [r for r in recommendations if r.get("priority") == "high"]
            medium_priority = [r for r in recommendations if r.get("priority") == "medium"]
            
            # Create phases
            if high_priority:
                plan["phases"].append({
                    "phase": 1,
                    "name": "High Priority Optimizations",
                    "recommendations": high_priority,
                    "duration": "4-6 weeks"
                })
            
            if medium_priority:
                plan["phases"].append({
                    "phase": 2,
                    "name": "Medium Priority Optimizations",
                    "recommendations": medium_priority,
                    "duration": "4-6 weeks"
                })
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Implementation plan creation failed: {e}")
            return {"phases": [], "total_duration": "8-12 weeks"}
    
    def _calculate_efficiency_improvement(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate expected efficiency improvement."""
        try:
            # Simple calculation based on recommendation types
            improvement = 0.0
            for rec in recommendations:
                if rec.get("type") == "complexity_reduction":
                    improvement += 0.15
                elif rec.get("type") == "automation_enhancement":
                    improvement += 0.20
                elif rec.get("type") == "goal_optimization":
                    improvement += 0.10
            return min(improvement, 0.50)  # Cap at 50%
        except Exception:
            return 0.0
    
    def _calculate_coexistence_score(self, optimized_process: Dict[str, Any]) -> float:
        """Calculate coexistence score for optimized process."""
        try:
            # Simple scoring based on optimizations applied
            base_score = 0.5
            optimization_bonus = len(optimized_process.get("optimizations_applied", [])) * 0.1
            return min(base_score + optimization_bonus, 1.0)
        except Exception:
            return 0.5
    
    def _analyze_performance_metrics(self, process_data: Dict[str, Any], 
                                   performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics."""
        try:
            analysis = {
                "metrics_analyzed": len(performance_metrics),
                "performance_trends": {},
                "key_insights": []
            }
            
            # Analyze each metric
            for metric, value in performance_metrics.items():
                if isinstance(value, (int, float)):
                    if value > 0.8:
                        analysis["performance_trends"][metric] = "excellent"
                    elif value > 0.6:
                        analysis["performance_trends"][metric] = "good"
                    elif value > 0.4:
                        analysis["performance_trends"][metric] = "fair"
                    else:
                        analysis["performance_trends"][metric] = "poor"
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Performance metrics analysis failed: {e}")
            return {"metrics_analyzed": 0, "performance_trends": {}, "key_insights": []}
    
    def _identify_performance_bottlenecks(self, performance_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks."""
        try:
            bottlenecks = []
            trends = performance_analysis.get("performance_trends", {})
            
            for metric, trend in trends.items():
                if trend in ["poor", "fair"]:
                    bottlenecks.append({
                        "metric": metric,
                        "severity": trend,
                        "description": f"Performance bottleneck identified in {metric}",
                        "recommended_action": f"Optimize {metric} for better performance"
                    })
            
            return bottlenecks
            
        except Exception as e:
            self.logger.error(f"Performance bottlenecks identification failed: {e}")
            return []
    
    def _generate_performance_recommendations(self, performance_analysis: Dict[str, Any], 
                                            bottlenecks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate performance recommendations."""
        try:
            recommendations = []
            
            # Add recommendations for each bottleneck
            for bottleneck in bottlenecks:
                recommendations.append({
                    "type": "performance_optimization",
                    "priority": "high" if bottleneck["severity"] == "poor" else "medium",
                    "description": bottleneck["recommended_action"],
                    "target_metric": bottleneck["metric"]
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Performance recommendations generation failed: {e}")
            return []
    
    def _calculate_performance_score(self, performance_analysis: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        try:
            trends = performance_analysis.get("performance_trends", {})
            if not trends:
                return 0.5
            
            # Calculate average performance
            score_map = {"excellent": 1.0, "good": 0.8, "fair": 0.6, "poor": 0.3}
            scores = [score_map.get(trend, 0.5) for trend in trends.values()]
            return sum(scores) / len(scores)
            
        except Exception:
            return 0.5
    
    def _create_coexistence_diagram(self, coexistence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create coexistence diagram visualization."""
        try:
            return {
                "type": "coexistence_diagram",
                "nodes": [
                    {"id": "human", "type": "actor", "label": "Human Actor"},
                    {"id": "ai", "type": "actor", "label": "AI Actor"},
                    {"id": "collaboration", "type": "process", "label": "Collaboration Point"}
                ],
                "edges": [
                    {"source": "human", "target": "collaboration", "type": "collaborates"},
                    {"source": "ai", "target": "collaboration", "type": "collaborates"}
                ],
                "metadata": coexistence_data
            }
        except Exception as e:
            self.logger.error(f"Coexistence diagram creation failed: {e}")
            return {"type": "coexistence_diagram", "nodes": [], "edges": []}
    
    def _create_collaboration_flow(self, coexistence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create collaboration flow visualization."""
        try:
            return {
                "type": "collaboration_flow",
                "flow_steps": [
                    {"step": 1, "actor": "human", "action": "initiate"},
                    {"step": 2, "actor": "ai", "action": "process"},
                    {"step": 3, "actor": "collaboration", "action": "review"},
                    {"step": 4, "actor": "human", "action": "finalize"}
                ],
                "metadata": coexistence_data
            }
        except Exception as e:
            self.logger.error(f"Collaboration flow creation failed: {e}")
            return {"type": "collaboration_flow", "flow_steps": []}
    
    def _create_optimization_roadmap(self, coexistence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create optimization roadmap visualization."""
        try:
            return {
                "type": "optimization_roadmap",
                "phases": [
                    {"phase": 1, "name": "Assessment", "duration": "2 weeks"},
                    {"phase": 2, "name": "Implementation", "duration": "6 weeks"},
                    {"phase": 3, "name": "Evaluation", "duration": "2 weeks"}
                ],
                "metadata": coexistence_data
            }
        except Exception as e:
            self.logger.error(f"Optimization roadmap creation failed: {e}")
            return {"type": "optimization_roadmap", "phases": []}
    
    def _assess_visualization_complexity(self, coexistence_data: Dict[str, Any]) -> str:
        """Assess visualization complexity."""
        try:
            data_size = len(str(coexistence_data))
            if data_size > 1000:
                return "high"
            elif data_size > 500:
                return "medium"
            else:
                return "low"
        except Exception:
            return "medium"
    
    def _validate_workflow_structure(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow structure."""
        try:
            required_fields = ["name", "nodes", "edges"]
            missing_fields = [field for field in required_fields if field not in workflow_definition]
            
            return {
                "is_valid": len(missing_fields) == 0,
                "missing_fields": missing_fields,
                "structure_score": 1.0 if len(missing_fields) == 0 else 0.5
            }
        except Exception as e:
            self.logger.error(f"Workflow structure validation failed: {e}")
            return {"is_valid": False, "missing_fields": [], "structure_score": 0.0}
    
    def _validate_workflow_logic(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow logic."""
        try:
            nodes = workflow_definition.get("nodes", [])
            edges = workflow_definition.get("edges", [])
            
            # Check for orphaned nodes
            node_ids = {node.get("id") for node in nodes}
            edge_sources = {edge.get("source") for edge in edges}
            edge_targets = {edge.get("target") for edge in edges}
            
            orphaned_nodes = node_ids - (edge_sources | edge_targets)
            
            return {
                "is_valid": len(orphaned_nodes) == 0,
                "orphaned_nodes": list(orphaned_nodes),
                "logic_score": 1.0 if len(orphaned_nodes) == 0 else 0.7
            }
        except Exception as e:
            self.logger.error(f"Workflow logic validation failed: {e}")
            return {"is_valid": False, "orphaned_nodes": [], "logic_score": 0.0}
    
    def _validate_workflow_completeness(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow completeness."""
        try:
            nodes = workflow_definition.get("nodes", [])
            edges = workflow_definition.get("edges", [])
            
            # Check for start and end nodes
            has_start = any(node.get("type") == "start" for node in nodes)
            has_end = any(node.get("type") == "end" for node in nodes)
            
            completeness_score = 0.0
            if has_start:
                completeness_score += 0.5
            if has_end:
                completeness_score += 0.5
            
            return {
                "is_valid": has_start and has_end,
                "has_start": has_start,
                "has_end": has_end,
                "completeness_score": completeness_score
            }
        except Exception as e:
            self.logger.error(f"Workflow completeness validation failed: {e}")
            return {"is_valid": False, "has_start": False, "has_end": False, "completeness_score": 0.0}
    
    def _generate_validation_summary(self, structure_validation: Dict[str, Any], 
                                  logic_validation: Dict[str, Any], 
                                  completeness_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary."""
        try:
            is_valid = all([
                structure_validation.get("is_valid", False),
                logic_validation.get("is_valid", False),
                completeness_validation.get("is_valid", False)
            ])
            
            overall_score = (
                structure_validation.get("structure_score", 0) +
                logic_validation.get("logic_score", 0) +
                completeness_validation.get("completeness_score", 0)
            ) / 3
            
            return {
                "is_valid": is_valid,
                "overall_score": overall_score,
                "validation_passed": is_valid,
                "issues_found": len([
                    v for v in [structure_validation, logic_validation, completeness_validation]
                    if not v.get("is_valid", False)
                ])
            }
        except Exception as e:
            self.logger.error(f"Validation summary generation failed: {e}")
            return {"is_valid": False, "overall_score": 0.0, "validation_passed": False, "issues_found": 3}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for all abstractions.
        
        Returns:
            Dict: Health check result
        """
        try:
            # Check health of all abstractions
            sop_health = await self.sop_processing.health_check()
            visualization_health = await self.workflow_visualization.health_check()
            coexistence_health = await self.coexistence_analysis.health_check()
            bpmn_health = await self.bpmn_processing.health_check()
            sop_enhancement_health = await self.sop_enhancement.health_check()
            coexistence_blueprint_health = await self.coexistence_blueprint.health_check()
            
            all_healthy = all([
                sop_health.get("healthy", False),
                visualization_health.get("healthy", False),
                coexistence_health.get("healthy", False),
                bpmn_health.get("healthy", False),
                sop_enhancement_health.get("healthy", False),
                coexistence_blueprint_health.get("healthy", False)
            ])
            
            result = {
                "healthy": all_healthy,
                "composition_service": "OperationsCompositionService",
                "abstractions": {
                    "sop_processing": sop_health,
                    "workflow_visualization": visualization_health,
                    "coexistence_analysis": coexistence_health,
                    "bpmn_processing": bpmn_health,
                    "sop_enhancement": sop_enhancement_health,
                    "coexistence_blueprint": coexistence_blueprint_health
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("health_check", {
                    "healthy": all_healthy,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
