#!/usr/bin/env python3
"""
Workflow Conversion Service

WHAT: Converts between SOPs and workflows, and analyzes files for conversion
HOW: Uses Librarian for file access, Content Steward for parsing, and generates structured workflows/SOPs

This service provides bidirectional conversion between SOPs and workflows,
enabling process documentation to be converted to executable workflows and vice versa.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class WorkflowConversionService(RealmServiceBase):
    """
    Workflow Conversion Service for Journey realm.
    
    Provides bidirectional conversion between SOPs and workflows:
    - Convert SOP files/content to executable workflows
    - Convert workflow files/content to SOP documentation
    - Analyze files to determine appropriate output type
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Workflow Conversion Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.content_steward = None
    
    async def initialize(self) -> bool:
        """
        Initialize Workflow Conversion Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "workflow_conversion_service_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # Get Smart City services
            self.librarian = await self.get_librarian_api()
            self.content_steward = await self.get_content_steward_api()
            
            # Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "workflow_conversion",
                        "protocol": "WorkflowConversionServiceProtocol",
                        "description": "Convert between SOPs and workflows",
                        "contracts": {
                            "soa_api": {
                                "api_name": "convert_sop_to_workflow",
                                "endpoint": "/api/v1/journey/workflow-conversion/sop-to-workflow",
                                "method": "POST",
                                "handler": self.convert_sop_to_workflow,
                                "metadata": {
                                    "description": "Convert SOP to workflow",
                                    "parameters": ["sop_file_uuid"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "convert_sop_to_workflow_tool",
                                "tool_definition": {
                                    "name": "convert_sop_to_workflow_tool",
                                    "description": "Convert SOP to workflow",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "sop_file_uuid": {"type": "string"}
                                        },
                                        "required": ["sop_file_uuid"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.convert_sop_to_workflow",
                            "semantic_api": "/api/v1/journey/workflow-conversion/sop-to-workflow",
                            "user_journey": "convert_sop_to_workflow"
                        }
                    },
                    {
                        "name": "sop_conversion",
                        "protocol": "WorkflowConversionServiceProtocol",
                        "description": "Convert workflows to SOPs",
                        "contracts": {
                            "soa_api": {
                                "api_name": "convert_workflow_to_sop",
                                "endpoint": "/api/v1/journey/workflow-conversion/workflow-to-sop",
                                "method": "POST",
                                "handler": self.convert_workflow_to_sop,
                                "metadata": {
                                    "description": "Convert workflow to SOP",
                                    "parameters": ["workflow_file_uuid"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "convert_workflow_to_sop_tool",
                                "tool_definition": {
                                    "name": "convert_workflow_to_sop_tool",
                                    "description": "Convert workflow to SOP",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "workflow_file_uuid": {"type": "string"}
                                        },
                                        "required": ["workflow_file_uuid"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.convert_workflow_to_sop",
                            "semantic_api": "/api/v1/journey/workflow-conversion/workflow-to-sop",
                            "user_journey": "convert_workflow_to_sop"
                        }
                    },
                    {
                        "name": "file_analysis",
                        "protocol": "WorkflowConversionServiceProtocol",
                        "description": "Analyze files for conversion",
                        "contracts": {
                            "soa_api": {
                                "api_name": "analyze_file",
                                "endpoint": "/api/v1/journey/workflow-conversion/analyze-file",
                                "method": "POST",
                                "handler": self.analyze_file,
                                "metadata": {
                                    "description": "Analyze file and determine output type",
                                    "parameters": ["input_file_uuid", "output_type"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "analyze_file_tool",
                                "tool_definition": {
                                    "name": "analyze_file_tool",
                                    "description": "Analyze file for conversion",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "input_file_uuid": {"type": "string"},
                                            "output_type": {"type": "string", "enum": ["workflow", "sop"]}
                                        },
                                        "required": ["input_file_uuid", "output_type"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.analyze_file",
                            "semantic_api": "/api/v1/journey/workflow-conversion/analyze-file",
                            "user_journey": "analyze_file"
                        }
                    }
                ],
                soa_apis=["convert_sop_to_workflow", "convert_workflow_to_sop", "analyze_file"],
                mcp_tools=["convert_sop_to_workflow_tool", "convert_workflow_to_sop_tool", "analyze_file_tool"]
            )
            
            # Record health metric
            await self.record_health_metric(
                "workflow_conversion_service_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "workflow_conversion_service_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "workflow_conversion_service_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "workflow_conversion_service_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            return False
    
    async def convert_sop_to_workflow(
        self,
        workflow_structure: Dict[str, Any],
        sop_content: Optional[Dict[str, Any]] = None,
        sop_file_uuid: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert SOP to workflow (Agentic-Forward Pattern).
        
        This service executes the workflow structure that the agent determined through
        critical reasoning. The agent has already:
        - Analyzed process content
        - Identified where workflows add value
        - Determined optimal workflow structure
        - Specified steps, decision points, and automation opportunities
        
        Args:
            workflow_structure: REQUIRED - Agent-specified workflow structure from critical reasoning
                {
                    "steps": [...],  # Agent-specified workflow steps (required)
                    "decision_points": [...],  # Agent-identified decision points
                    "automation_opportunities": [...],  # What can be automated
                    "recommended_approach": str
                }
            sop_content: Optional SOP content (for reference)
            sop_file_uuid: Optional SOP file UUID (for reference)
        
        Returns:
            Dict with workflow definition and metadata
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "convert_sop_to_workflow_start",
            success=True,
            details={"phases_count": len(workflow_structure.get("steps", []))}
        )
        
        try:
            self.logger.info("📊 Converting SOP to workflow from agent-specified structure")
            
            # Validate agent-specified structure
            if not workflow_structure.get("steps"):
                return {
                    "success": False,
                    "error": "No steps specified in workflow structure",
                    "message": "Agent must specify steps in workflow_structure"
                }
            
            # Execute agent's strategic decisions
            workflow = {
                "workflow_id": f"workflow_{uuid.uuid4().hex[:8]}",
                "title": sop_content.get("title", "Workflow") if sop_content else "Workflow",
                "description": workflow_structure.get("description", "Workflow from agent-specified structure"),
                "steps": workflow_structure.get("steps", []),
                "decision_points": workflow_structure.get("decision_points", []),
                "automation_opportunities": workflow_structure.get("automation_opportunities", []),
                "conversion_type": "sop_to_workflow",
                "source_file_uuid": sop_file_uuid,
                "recommended_approach": workflow_structure.get("recommended_approach", ""),
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("convert_sop_to_workflow_success", 1.0, {
                "steps_count": len(workflow.get("steps", []))
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("convert_sop_to_workflow_complete", success=True, details={
                "workflow_id": workflow["workflow_id"]
            })
            
            return {
                "success": True,
                "workflow": workflow,
                "workflow_content": workflow,
                "workflow_id": workflow["workflow_id"],
                "message": "SOP converted to workflow successfully"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "convert_sop_to_workflow", details={"sop_file_uuid": sop_file_uuid})
            
            # Record health metric (failure)
            await self.record_health_metric("convert_sop_to_workflow_failed", 1.0, {"sop_file_uuid": sop_file_uuid, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("convert_sop_to_workflow_complete", success=False, details={"sop_file_uuid": sop_file_uuid, "error": str(e)})
            
            self.logger.error(f"❌ Failed to convert SOP to workflow: {e}")
            return {"success": False, "error": str(e)}
    
    async def convert_workflow_to_sop(
        self,
        sop_structure: Dict[str, Any],
        workflow_content: Optional[Dict[str, Any]] = None,
        workflow_file_uuid: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Convert workflow to SOP (Agentic-Forward Pattern).
        
        This service executes the SOP structure that the agent determined through
        critical reasoning. The agent has already:
        - Analyzed workflow content
        - Determined optimal SOP structure
        - Identified AI assistance points
        - Specified steps and documentation requirements
        
        Args:
            sop_structure: REQUIRED - Agent-specified SOP structure from critical reasoning
                {
                    "title": str,  # Agent-specified title (required)
                    "description": str,  # Agent-specified description
                    "steps": [...],  # Agent-specified SOP steps (required)
                    "ai_assistance_points": [...]  # Where AI can assist
                }
            workflow_content: Optional workflow content (for reference)
            workflow_file_uuid: Optional workflow file UUID (for reference)
        
        Returns:
            Dict with SOP definition and metadata
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "convert_workflow_to_sop_start",
            success=True,
            details={"steps_count": len(sop_structure.get("steps", []))}
        )
        
        try:
            self.logger.info("📄 Converting workflow to SOP from agent-specified structure")
            
            # Validate agent-specified structure (allow both steps and sections)
            if not sop_structure.get("title"):
                return {
                    "success": False,
                    "error": "Invalid SOP structure",
                    "message": "Agent must specify title in sop_structure"
                }
            
            # Check if we have steps or sections
            has_steps = bool(sop_structure.get("steps"))
            has_sections = bool(sop_structure.get("sections"))
            if not has_steps and not has_sections:
                return {
                    "success": False,
                    "error": "Invalid SOP structure",
                    "message": "Agent must specify either steps or sections in sop_structure"
                }
            
            # Execute agent's strategic decisions
            sop = {
                "sop_id": f"sop_{uuid.uuid4().hex[:8]}",
                "title": sop_structure.get("title"),
                "description": sop_structure.get("description", "SOP from agent-specified structure"),
                "steps": sop_structure.get("steps", []),
                "ai_assistance_points": sop_structure.get("ai_assistance_points", []),
                "conversion_type": "workflow_to_sop",
                "source_file_uuid": workflow_file_uuid,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Convert workflow steps to SOP steps
            workflow_steps = workflow_content.get("steps", [])
            for idx, step in enumerate(workflow_steps):
                if isinstance(step, str):
                    sop["steps"].append({
                        "step_number": idx + 1,
                        "instruction": step,
                        "details": step
                    })
                elif isinstance(step, dict):
                    sop["steps"].append({
                        "step_number": step.get("order", idx + 1),
                        "instruction": step.get("name", f"Step {idx + 1}"),
                        "details": step.get("description", "")
                    })
            
            # Record health metric (success)
            await self.record_health_metric("convert_workflow_to_sop_success", 1.0, {"workflow_file_uuid": workflow_file_uuid})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("convert_workflow_to_sop_complete", success=True, details={"workflow_file_uuid": workflow_file_uuid})
            
            return {
                "success": True,
                "sop": sop,
                "sop_content": sop,
                "sop_id": sop["sop_id"],
                "message": "Workflow converted to SOP successfully"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "convert_workflow_to_sop", details={"workflow_file_uuid": workflow_file_uuid})
            
            # Record health metric (failure)
            await self.record_health_metric("convert_workflow_to_sop_failed", 1.0, {"workflow_file_uuid": workflow_file_uuid, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("convert_workflow_to_sop_complete", success=False, details={"workflow_file_uuid": workflow_file_uuid, "error": str(e)})
            
            self.logger.error(f"❌ Failed to convert workflow to SOP: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_file(self, input_file_uuid: str, output_type: str) -> Dict[str, Any]:
        """
        Analyze file and convert to desired output type.
        
        Args:
            input_file_uuid: UUID of the input file
            output_type: Desired output type ("workflow" or "sop")
        
        Returns:
            Dict with converted content
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "analyze_file_start",
            success=True,
            details={"input_file_uuid": input_file_uuid, "output_type": output_type}
        )
        
        try:
            self.logger.info(f"🔍 Analyzing file: {input_file_uuid} → {output_type}")
            
            # Validate output type
            if output_type not in ["workflow", "sop"]:
                return {"success": False, "error": f"Invalid output_type: {output_type}. Must be 'workflow' or 'sop'"}
            
            # Get file from Librarian
            if not self.librarian:
                return {"success": False, "error": "Librarian service not available"}
            
            file_doc = await self.librarian.get_document(document_id=input_file_uuid)
            if not file_doc:
                return {"success": False, "error": f"File not found: {input_file_uuid}"}
            
            # Determine conversion direction based on file metadata
            file_metadata = file_doc.get("metadata", {})
            file_type = file_metadata.get("file_type", "").lower()
            
            # Convert based on output type
            if output_type == "workflow":
                result = await self.convert_sop_to_workflow(input_file_uuid)
            else:  # output_type == "sop"
                result = await self.convert_workflow_to_sop(input_file_uuid)
            
            # Record health metric (success)
            await self.record_health_metric("analyze_file_success", 1.0, {"input_file_uuid": input_file_uuid, "output_type": output_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("analyze_file_complete", success=True, details={"input_file_uuid": input_file_uuid, "output_type": output_type})
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "analyze_file", details={"input_file_uuid": input_file_uuid, "output_type": output_type})
            
            # Record health metric (failure)
            await self.record_health_metric("analyze_file_failed", 1.0, {"input_file_uuid": input_file_uuid, "output_type": output_type, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("analyze_file_complete", success=False, details={"input_file_uuid": input_file_uuid, "output_type": output_type, "error": str(e)})
            
            self.logger.error(f"❌ Failed to analyze file: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities for registration."""
        return {
            "service_name": self.service_name,
            "realm": self.realm_name,
            "capabilities": [
                "workflow_conversion",
                "sop_conversion",
                "file_analysis"
            ],
            "soa_apis": [
                "convert_sop_to_workflow",
                "convert_workflow_to_sop",
                "analyze_file"
            ],
            "mcp_tools": [
                "convert_sop_to_workflow_tool",
                "convert_workflow_to_sop_tool",
                "analyze_file_tool"
            ]
        }

