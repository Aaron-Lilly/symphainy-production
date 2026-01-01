#!/usr/bin/env python3
"""
SOP Builder Service

WHAT: Builds SOPs through a wizard interface
HOW: Manages wizard sessions, processes user input step-by-step, and generates structured SOPs

This service provides a wizard-based interface for creating SOPs, enabling
users to build comprehensive SOPs through guided steps.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class SOPBuilderService(RealmServiceBase):
    """
    SOP Builder Service for Journey realm.
    
    Provides wizard-based SOP creation:
    - Start wizard sessions
    - Process wizard steps with user input
    - Complete wizard and generate SOP
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize SOP Builder Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        
        # Wizard session storage (in-memory for MVP, can be moved to Librarian later)
        self.wizard_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self) -> bool:
        """
        Initialize SOP Builder Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "sop_builder_service_initialize_start",
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
                        "name": "sop_building",
                        "protocol": "SOPBuilderServiceProtocol",
                        "description": "Build SOPs through wizard interface",
                        "contracts": {
                            "soa_api": {
                                "api_name": "start_wizard_session",
                                "endpoint": "/api/v1/journey/sop-builder/start-wizard",
                                "method": "POST",
                                "handler": self.start_wizard_session,
                                "metadata": {
                                    "description": "Start SOP builder wizard session",
                                    "parameters": []
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "start_sop_wizard_tool",
                                "tool_definition": {
                                    "name": "start_sop_wizard_tool",
                                    "description": "Start SOP builder wizard",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {}
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.start_sop_wizard",
                            "semantic_api": "/api/v1/journey/sop-builder/start-wizard",
                            "user_journey": "start_sop_wizard"
                        }
                    },
                    {
                        "name": "wizard_processing",
                        "protocol": "SOPBuilderServiceProtocol",
                        "description": "Process wizard steps",
                        "contracts": {
                            "soa_api": {
                                "api_name": "process_wizard_step",
                                "endpoint": "/api/v1/journey/sop-builder/process-step",
                                "method": "POST",
                                "handler": self.process_wizard_step,
                                "metadata": {
                                    "description": "Process wizard step with user input",
                                    "parameters": ["session_token", "user_input"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "process_wizard_step_tool",
                                "tool_definition": {
                                    "name": "process_wizard_step_tool",
                                    "description": "Process wizard step",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "session_token": {"type": "string"},
                                            "user_input": {"type": "string"}
                                        },
                                        "required": ["session_token", "user_input"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.process_wizard_step",
                            "semantic_api": "/api/v1/journey/sop-builder/process-step",
                            "user_journey": "process_wizard_step"
                        }
                    },
                    {
                        "name": "wizard_completion",
                        "protocol": "SOPBuilderServiceProtocol",
                        "description": "Complete wizard and generate SOP",
                        "contracts": {
                            "soa_api": {
                                "api_name": "complete_wizard",
                                "endpoint": "/api/v1/journey/sop-builder/complete-wizard",
                                "method": "POST",
                                "handler": self.complete_wizard,
                                "metadata": {
                                    "description": "Complete wizard and generate SOP",
                                    "parameters": ["session_token"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "complete_wizard_tool",
                                "tool_definition": {
                                    "name": "complete_wizard_tool",
                                    "description": "Complete wizard and generate SOP",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "session_token": {"type": "string"}
                                        },
                                        "required": ["session_token"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "journey.complete_wizard",
                            "semantic_api": "/api/v1/journey/sop-builder/complete-wizard",
                            "user_journey": "complete_wizard"
                        }
                    }
                ],
                soa_apis=["start_wizard_session", "process_wizard_step", "complete_wizard"],
                mcp_tools=["start_sop_wizard_tool", "process_wizard_step_tool", "complete_wizard_tool"]
            )
            
            # Record health metric
            await self.record_health_metric(
                "sop_builder_service_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "sop_builder_service_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "sop_builder_service_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "sop_builder_service_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            return False
    
    async def start_wizard_session(
        self,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Start a new SOP builder wizard session.
        
        Returns:
            Dict with session_token and initial wizard state
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "start_wizard_session_start",
            success=True
        )
        
        try:
            # Generate session token
            session_token = f"wizard_{uuid.uuid4().hex[:12]}"
            
            # Initialize wizard session
            wizard_session = {
                "session_token": session_token,
                "status": "active",
                "current_step": 1,
                "total_steps": 5,  # Title, Description, Steps, Review, Complete
                "sop_data": {
                    "sop_id": f"sop_{uuid.uuid4().hex[:8]}",
                    "title": "",
                    "description": "",
                    "steps": [],
                    "created_at": datetime.utcnow().isoformat()
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store session
            self.wizard_sessions[session_token] = wizard_session
            
            # Record health metric (success)
            await self.record_health_metric("start_wizard_session_success", 1.0, {"session_token": session_token})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("start_wizard_session_complete", success=True, details={"session_token": session_token})
            
            return {
                "success": True,
                "session_token": session_token,
                "current_step": 1,
                "total_steps": 5,
                "message": "Wizard session started. Please provide the SOP title.",
                "next_prompt": "What is the title of this SOP?"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "start_wizard_session")
            
            # Record health metric (failure)
            await self.record_health_metric("start_wizard_session_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("start_wizard_session_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Failed to start wizard session: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_wizard_step(
        self,
        session_token: str,
        user_input: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a wizard step with user input.
        
        Args:
            session_token: Wizard session token
            user_input: User input for the current step
        
        Returns:
            Dict with updated wizard state and next prompt
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "process_wizard_step_start",
            success=True,
            details={"session_token": session_token, "step": "current"}
        )
        
        try:
            # Get wizard session
            if session_token not in self.wizard_sessions:
                return {"success": False, "error": f"Wizard session not found: {session_token}"}
            
            wizard_session = self.wizard_sessions[session_token]
            current_step = wizard_session["current_step"]
            sop_data = wizard_session["sop_data"]
            
            # Process step based on current step number
            if current_step == 1:
                # Step 1: Title
                sop_data["title"] = user_input.strip()
                wizard_session["current_step"] = 2
                next_prompt = "What is the description of this SOP?"
                
            elif current_step == 2:
                # Step 2: Description
                sop_data["description"] = user_input.strip()
                wizard_session["current_step"] = 3
                next_prompt = "Please provide the first step of the SOP. You can add more steps later."
                
            elif current_step == 3:
                # Step 3: Steps (can be called multiple times)
                # Check if user wants to finish adding steps
                if user_input.strip().lower() == "done":
                    wizard_session["current_step"] = 4
                    next_prompt = "Review your SOP. Type 'complete' to finish, or provide corrections."
                else:
                    # Add step
                    if not sop_data.get("steps"):
                        sop_data["steps"] = []
                    
                    step_number = len(sop_data["steps"]) + 1
                    sop_data["steps"].append({
                        "step_number": step_number,
                        "instruction": user_input.strip(),
                        "details": ""
                    })
                    
                    next_prompt = f"Step {step_number} added. Provide another step, or type 'done' to proceed to review."
                
            elif current_step == 4:
                # Step 4: Review
                if user_input.strip().lower() == "complete":
                    wizard_session["current_step"] = 5
                    next_prompt = "Wizard complete! Use complete_wizard() to generate the final SOP."
                else:
                    # User provided corrections - try to parse and update
                    # For MVP, just acknowledge
                    next_prompt = "Corrections noted. Type 'complete' to finish, or provide more corrections."
                
            else:
                # Step 5 or beyond - wizard should be completed
                return {
                    "success": False,
                    "error": "Wizard already complete. Use complete_wizard() to generate the SOP."
                }
            
            # Update session
            wizard_session["updated_at"] = datetime.utcnow().isoformat()
            wizard_session["sop_data"] = sop_data
            
            # Record health metric (success)
            await self.record_health_metric("process_wizard_step_success", 1.0, {"session_token": session_token, "step": current_step})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("process_wizard_step_complete", success=True, details={"session_token": session_token, "step": current_step})
            
            return {
                "success": True,
                "session_token": session_token,
                "current_step": wizard_session["current_step"],
                "total_steps": wizard_session["total_steps"],
                "message": "Step processed successfully",
                "next_prompt": next_prompt,
                "sop_progress": {
                    "title": sop_data.get("title", ""),
                    "description": sop_data.get("description", ""),
                    "steps_count": len(sop_data.get("steps", []))
                }
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "process_wizard_step", details={"session_token": session_token})
            
            # Record health metric (failure)
            await self.record_health_metric("process_wizard_step_failed", 1.0, {"session_token": session_token, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("process_wizard_step_complete", success=False, details={"session_token": session_token, "error": str(e)})
            
            self.logger.error(f"❌ Failed to process wizard step: {e}")
            return {"success": False, "error": str(e)}
    
    async def complete_wizard(
        self,
        session_token: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete wizard and generate final SOP.
        
        Args:
            session_token: Wizard session token
        
        Returns:
            Dict with generated SOP
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "complete_wizard_start",
            success=True,
            details={"session_token": session_token}
        )
        
        try:
            # Get wizard session
            if session_token not in self.wizard_sessions:
                return {"success": False, "error": f"Wizard session not found: {session_token}"}
            
            wizard_session = self.wizard_sessions[session_token]
            sop_data = wizard_session["sop_data"]
            
            # Validate SOP data
            if not sop_data.get("title"):
                return {"success": False, "error": "SOP title is required"}
            
            if not sop_data.get("steps") or len(sop_data["steps"]) == 0:
                return {"success": False, "error": "At least one SOP step is required"}
            
            # Finalize SOP
            sop = {
                "sop_id": sop_data["sop_id"],
                "title": sop_data["title"],
                "description": sop_data.get("description", ""),
                "steps": sop_data["steps"],
                "created_at": sop_data["created_at"],
                "completed_at": datetime.utcnow().isoformat(),
                "source": "wizard"
            }
            
            # Mark session as complete
            wizard_session["status"] = "completed"
            wizard_session["updated_at"] = datetime.utcnow().isoformat()
            
            # Record health metric (success)
            await self.record_health_metric("complete_wizard_success", 1.0, {"session_token": session_token})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("complete_wizard_complete", success=True, details={"session_token": session_token})
            
            return {
                "success": True,
                "sop": sop,
                "sop_content": sop,
                "sop_id": sop["sop_id"],
                "message": "SOP generated successfully from wizard",
                "session_token": session_token
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "complete_wizard", details={"session_token": session_token})
            
            # Record health metric (failure)
            await self.record_health_metric("complete_wizard_failed", 1.0, {"session_token": session_token, "error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("complete_wizard_complete", success=False, details={"session_token": session_token, "error": str(e)})
            
            self.logger.error(f"❌ Failed to complete wizard: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities for registration."""
        return {
            "service_name": self.service_name,
            "realm": self.realm_name,
            "capabilities": [
                "sop_building",
                "wizard_processing",
                "wizard_completion"
            ],
            "soa_apis": [
                "start_wizard_session",
                "process_wizard_step",
                "complete_wizard"
            ],
            "mcp_tools": [
                "start_sop_wizard_tool",
                "process_wizard_step_tool",
                "complete_wizard_tool"
            ]
        }

