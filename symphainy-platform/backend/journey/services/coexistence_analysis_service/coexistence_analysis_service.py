#!/usr/bin/env python3
"""
Coexistence Analysis Service

WHAT: Analyzes coexistence between SOPs and workflows, generating optimization blueprints
HOW: Compares SOP and workflow structures, identifies gaps and opportunities, generates blueprints

This service analyzes the coexistence between SOPs and workflows, identifying
optimization opportunities and generating blueprints for process improvement.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class CoexistenceAnalysisService(RealmServiceBase):
    """
    Coexistence Analysis Service for Journey realm.
    
    Provides coexistence analysis between SOPs and workflows:
    - Analyze coexistence from content
    - Generate coexistence blueprints
    - Identify optimization opportunities
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Coexistence Analysis Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
    
    async def initialize(self) -> bool:
        """
        Initialize Coexistence Analysis Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "coexistence_analysis_service_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # Get Smart City services
            self.librarian = await self.get_librarian_api()
            
            # Register with Curator (Phase 2 pattern)
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "coexistence_analysis",
                        "protocol": "CoexistenceAnalysisServiceProtocol",
                        "description": "Analyze coexistence between SOPs and workflows",
                        "contracts": {
                            "soa_api": {
                                "api_name": "analyze_coexistence",
                                "endpoint": "/api/v1/journey/coexistence-analysis/analyze",
                                "method": "POST",
                                "handler": self.analyze_coexistence,
                                "metadata": {
                                    "description": "Analyze coexistence between SOP and workflow content",
                                    "parameters": ["sop_content", "workflow_content"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "analyze_coexistence_tool",
                                "tool_definition": {
                                    "name": "analyze_coexistence_tool",
                                    "description": "Analyze coexistence between SOP and workflow",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "sop_content": {"type": "string"},
                                            "workflow_content": {"type": "object"}
                                        },
                                        "required": ["sop_content", "workflow_content"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.analyze_coexistence",
                            "semantic_api": "/api/v1/journey/coexistence-analysis/analyze",
                            "user_journey": "analyze_coexistence"
                        }
                    },
                    {
                        "name": "blueprint_generation",
                        "protocol": "CoexistenceAnalysisServiceProtocol",
                        "description": "Generate coexistence blueprints",
                        "contracts": {
                            "soa_api": {
                                "api_name": "create_blueprint",
                                "endpoint": "/api/v1/journey/coexistence-analysis/create-blueprint",
                                "method": "POST",
                                "handler": self.create_blueprint,
                                "metadata": {
                                    "description": "Create coexistence blueprint from SOP and workflow IDs",
                                    "parameters": ["sop_id", "workflow_id"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "create_blueprint_tool",
                                "tool_definition": {
                                    "name": "create_blueprint_tool",
                                    "description": "Create coexistence blueprint",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "sop_id": {"type": "string"},
                                            "workflow_id": {"type": "string"}
                                        },
                                        "required": ["sop_id", "workflow_id"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.create_blueprint",
                            "semantic_api": "/api/v1/journey/coexistence-analysis/create-blueprint",
                            "user_journey": "create_blueprint"
                        }
                    }
                ],
                soa_apis=["analyze_coexistence", "create_blueprint"],
                mcp_tools=["analyze_coexistence_tool", "create_blueprint_tool"]
            )
            
            # Record health metric
            await self.record_health_metric(
                "coexistence_analysis_service_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "coexistence_analysis_service_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "coexistence_analysis_service_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "coexistence_analysis_service_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            return False
    
    async def analyze_coexistence(
        self,
        coexistence_structure: Dict[str, Any],
        sop_content: Optional[str] = None,
        workflow_content: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze coexistence between SOP and workflow (Agentic-Forward Pattern).
        
        This service executes the coexistence structure that the agent determined through
        critical reasoning. The agent has already:
        - Analyzed SOP and workflow content
        - Determined optimal coexistence structure
        - Identified handoff points and AI augmentation opportunities
        - Specified collaboration patterns
        
        Args:
            coexistence_structure: REQUIRED - Agent-specified coexistence structure from critical reasoning
                {
                    "handoff_points": [...],  # Agent-identified handoff points
                    "ai_augmentation_points": [...],  # Where AI can augment
                    "human_driven_steps": [...],  # Steps that should be human-driven
                    "ai_driven_steps": [...],  # Steps that should be AI-driven
                    "collaboration_pattern": str  # Recommended collaboration pattern
                }
            sop_content: Optional SOP content (for reference)
            workflow_content: Optional workflow content (for reference)
        
        Returns:
            Dict with analysis results and blueprint
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "analyze_coexistence_start",
            success=True,
            details={"handoff_points_count": len(coexistence_structure.get("handoff_points", []))}
        )
        
        try:
            self.logger.info("🔄 Analyzing coexistence from agent-specified structure")
            
            # Validate agent-specified structure
            if not coexistence_structure.get("collaboration_pattern"):
                return {
                    "success": False,
                    "error": "Invalid coexistence structure",
                    "message": "Agent must specify collaboration_pattern in coexistence_structure"
                }
            
            # Extract SOP and workflow data from content
            sop_data = {}
            if isinstance(sop_content, dict):
                sop_data = sop_content
            elif isinstance(sop_content, str):
                try:
                    import json
                    sop_data = json.loads(sop_content)
                except:
                    sop_data = {"title": "SOP", "content": sop_content}
            
            workflow_data = workflow_content if isinstance(workflow_content, dict) else {}
            
            # Extract steps from SOP (handle both sections and direct steps)
            sop_steps = []
            if "sections" in sop_data:
                for section in sop_data.get("sections", []):
                    sop_steps.extend(section.get("steps", []))
            elif "steps" in sop_data:
                sop_steps = sop_data.get("steps", [])
            
            # Extract steps from workflow
            workflow_steps = workflow_data.get("steps", []) if isinstance(workflow_data, dict) else []
            
            # Execute agent's strategic decisions
            analysis = {
                "analysis_id": f"analysis_{uuid.uuid4().hex[:8]}",
                "handoff_points": coexistence_structure.get("handoff_points", []),
                "ai_augmentation_points": coexistence_structure.get("ai_augmentation_points", []),
                "human_driven_steps": coexistence_structure.get("human_driven_steps", []),
                "ai_driven_steps": coexistence_structure.get("ai_driven_steps", []),
                "collaboration_pattern": coexistence_structure.get("collaboration_pattern", "ai_augmented"),
                "gaps": [],
                "opportunities": [],
                "recommendations": [],
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Generate recommendations
            if len(sop_steps) != len(workflow_steps):
                analysis["recommendations"].append({
                    "type": "step_count_mismatch",
                    "description": f"SOP has {len(sop_steps)} steps, workflow has {len(workflow_steps)} steps. Consider aligning them.",
                    "priority": "medium"
                })
            
            if not analysis["gaps"] and not analysis["opportunities"]:
                analysis["recommendations"].append({
                    "type": "alignment_good",
                    "description": "SOP and workflow are well-aligned",
                    "priority": "low"
                })
            
            # Generate blueprint
            blueprint = {
                "blueprint_id": f"blueprint_{uuid.uuid4().hex[:8]}",
                "title": f"Coexistence Blueprint: {sop_data.get('title', 'SOP')} ↔ {workflow_data.get('title', 'Workflow')}",
                "description": "Blueprint generated from coexistence analysis",
                "sop_summary": {
                    "title": sop_data.get("title", "SOP"),
                    "step_count": len(sop_steps),
                    "steps": sop_steps[:5] if sop_steps else []  # First 5 steps for summary
                },
                "workflow_summary": {
                    "title": workflow_data.get("title", "Workflow"),
                    "step_count": len(workflow_steps),
                    "steps": workflow_steps[:5] if workflow_steps else []  # First 5 steps for summary
                },
                "analysis": analysis,
                "optimization_opportunities": analysis["opportunities"],
                "gaps_to_address": analysis["gaps"],
                "recommendations": analysis["recommendations"],
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("analyze_coexistence_success", 1.0, {})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("analyze_coexistence_complete", success=True)
            
            return {
                "success": True,
                "analysis": analysis,
                "blueprint": blueprint,
                "coexistence_blueprint": blueprint,  # Alias for compatibility
                "message": "Coexistence analysis completed successfully"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "analyze_coexistence")
            
            # Record health metric (failure)
            await self.record_health_metric("analyze_coexistence_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("analyze_coexistence_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Failed to analyze coexistence: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_blueprint(self, sop_id: str, workflow_id: str) -> Dict[str, Any]:
        """
        Create coexistence blueprint from SOP and workflow IDs.
        
        Args:
            sop_id: SOP ID or file UUID
            workflow_id: Workflow ID or file UUID
        
        Returns:
            Dict with generated blueprint
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "create_blueprint_start",
            success=True,
            details={"sop_id": sop_id, "workflow_id": workflow_id}
        )
        
        try:
            self.logger.info(f"💾 Creating blueprint from SOP: {sop_id}, Workflow: {workflow_id}")
            
            # Get files from Librarian
            if not self.librarian:
                return {"success": False, "error": "Librarian service not available"}
            
            sop_doc = await self.librarian.get_document(document_id=sop_id)
            workflow_doc = await self.librarian.get_document(document_id=workflow_id)
            
            if not sop_doc:
                return {"success": False, "error": f"SOP not found: {sop_id}"}
            
            if not workflow_doc:
                return {"success": False, "error": f"Workflow not found: {workflow_id}"}
            
            # Extract content
            sop_content = sop_doc.get("data", {})
            workflow_content = workflow_doc.get("data", {})
            
            # Normalize content
            if isinstance(sop_content, str):
                import json
                try:
                    sop_content = json.loads(sop_content)
                except:
                    sop_content = {"content": sop_content}
            
            if isinstance(workflow_content, str):
                import json
                try:
                    workflow_content = json.loads(workflow_content)
                except:
                    workflow_content = {"content": workflow_content}
            
            # Analyze coexistence
            analysis_result = await self.analyze_coexistence(sop_content, workflow_content)
            
            if not analysis_result.get("success"):
                return analysis_result
            
            blueprint = analysis_result.get("blueprint", {})
            blueprint["sop_id"] = sop_id
            blueprint["workflow_id"] = workflow_id
            
            # Record health metric (success)
            await self.record_health_metric("create_blueprint_success", 1.0, {"sop_id": sop_id, "workflow_id": workflow_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_blueprint_complete", success=True, details={"sop_id": sop_id, "workflow_id": workflow_id})
            
            return {
                "success": True,
                "blueprint": blueprint,
                "blueprint_id": blueprint.get("blueprint_id"),
                "message": "Blueprint created successfully"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "create_blueprint", details={"sop_id": sop_id, "workflow_id": workflow_id})
            
            # Record health metric (failure)
            await self.record_health_metric("create_blueprint_failed", 1.0, {"sop_id": sop_id, "workflow_id": workflow_id, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("create_blueprint_complete", success=False, details={"sop_id": sop_id, "workflow_id": workflow_id, "error": str(e)})
            
            self.logger.error(f"❌ Failed to create blueprint: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities for registration."""
        return {
            "service_name": self.service_name,
            "realm": self.realm_name,
            "capabilities": [
                "coexistence_analysis",
                "blueprint_generation"
            ],
            "soa_apis": [
                "analyze_coexistence",
                "create_blueprint"
            ],
            "mcp_tools": [
                "analyze_coexistence_tool",
                "create_blueprint_tool"
            ]
        }

