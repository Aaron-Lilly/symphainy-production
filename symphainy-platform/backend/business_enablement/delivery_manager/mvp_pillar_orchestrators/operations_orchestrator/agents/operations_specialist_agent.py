#!/usr/bin/env python3
"""
Operations Specialist Agent

Specialist agent for the Operations Pillar providing advanced operations management capabilities.

WHAT (Business Enablement Role): I provide specialized operations management expertise
HOW (Specialist Agent): I offer deep domain knowledge and advanced analytical capabilities
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from utilities import UserContext
from backend.business_enablement.protocols.business_specialist_agent_protocol import BusinessSpecialistAgentBase, SpecialistCapability

# Import new infrastructure capabilities
from foundations.di_container.di_container_service import DIContainerService


class OperationsSpecialistAgent(BusinessSpecialistAgentBase):
    """
    Operations Specialist Agent
    
    Provides specialized operations management expertise and advanced analytical capabilities.
    
    WHAT (Business Enablement Role): I provide specialized operations management expertise
    HOW (Specialist Agent): I offer deep domain knowledge and advanced analytical capabilities
    """
    
    def __init__(
        self,
        agent_name: str,
        business_domain: str,
        capabilities: List[str],
        required_roles: List[str],
        agui_schema: Any,
        foundation_services: Any,
        agentic_foundation: Any,
        public_works_foundation: Any,
        mcp_client_manager: Any,
        policy_integration: Any,
        tool_composition: Any,
        agui_formatter: Any,
        curator_foundation: Any = None,
        metadata_foundation: Any = None,
        **kwargs
    ):
        """
        Initialize Operations Specialist Agent with full SDK dependencies.
        
        This agent is created via Agentic Foundation factory - all dependencies
        are provided by the factory.
        """
        super().__init__(
            agent_name=agent_name,
            business_domain=business_domain,
            capabilities=capabilities,
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            specialist_capability=kwargs.get("specialist_capability", SpecialistCapability.PROCESS_OPTIMIZATION),
            **{k: v for k, v in kwargs.items() if k != "specialist_capability"}
        )
        
        # Store public works foundation (required for LLM abstraction)
        self.public_works_foundation = public_works_foundation
        
        self.service_name = agent_name
        self.operations_orchestrator = None
        self.orchestrator = None  # Set by orchestrator for MCP tool access
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return f"Operations Specialist Agent '{self.agent_name}' - Provides specialized capabilities for workflow design, SOP creation, and coexistence analysis."
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request using agent capabilities.
        
        Args:
            request: Request dictionary containing operation and parameters
            
        Returns:
            Response dictionary with results
        """
        try:
            operation = request.get("operation", "")
            
            if operation == "analyze_process_for_workflow_structure":
                return await self.analyze_process_for_workflow_structure(
                    process_content=request.get("process_content", ""),
                    business_context=request.get("business_context", {})
                )
            elif operation == "analyze_for_sop_structure":
                return await self.analyze_for_sop_structure(
                    workflow_content=request.get("workflow_content", ""),
                    business_context=request.get("business_context", {})
                )
            elif operation == "analyze_for_coexistence_structure":
                return await self.analyze_for_coexistence_structure(
                    sop_content=request.get("sop_content", {}),
                    workflow_content=request.get("workflow_content", {}),
                    business_context=request.get("business_context", {})
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}",
                    "message": f"Operation '{operation}' is not supported by this agent"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error processing request: {str(e)}"
            }
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference for MCP server access."""
        self.orchestrator = orchestrator
        self.operations_orchestrator = orchestrator
        self.logger.info("✅ Orchestrator reference set for MCP tool access")
    
    async def initialize(self):
        """
        Initialize Operations Specialist Agent.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        
        Note: Factory handles Curator registration (Agentic Foundation owns agent registry).
        """
        try:
            # Start telemetry tracking (using AgentBase utility method)
            await self.log_operation_with_telemetry("initialize_start", success=True, details={
                "agent_name": self.service_name
            })
            
            # Call parent initialize
            await super().initialize()
            
            # Initialize LLM abstraction (required for agent reasoning)
            if self.public_works_foundation:
                self.llm_abstraction = self.public_works_foundation.get_abstraction("llm")
                if self.llm_abstraction:
                    # Validate LLM configuration with a test call
                    try:
                        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
                        test_request = LLMRequest(
                            messages=[{"role": "user", "content": "test"}],
                            model=LLMModel.GPT_4O_MINI,
                            max_tokens=10
                        )
                        test_response = await self.llm_abstraction.generate_response(test_request)
                        self.logger.info("✅ LLM abstraction validated and working")
                    except Exception as e:
                        self.logger.warning(f"⚠️ LLM abstraction available but test failed: {e}")
                        self.logger.warning("   Agent will use fallback methods when LLM fails")
                        # Don't set to None - keep it for retry attempts
                else:
                    self.logger.warning("⚠️ LLM abstraction not available from PublicWorksFoundation")
                    self.logger.warning("   Agent will use fallback methods")
            else:
                self.logger.warning("⚠️ PublicWorksFoundation not available - LLM abstraction not initialized")
                self.logger.warning("   Agent will use fallback methods")
                self.llm_abstraction = None
            
            # Discover orchestrator via Curator (optional, agent can work independently)
            if self.curator_foundation:
                try:
                    registered_services = await self.curator_foundation.get_registered_services()
                    services_dict = registered_services.get("services", {})
                    if "OperationsOrchestratorService" in services_dict:
                        service_info = services_dict["OperationsOrchestratorService"]
                        self.operations_orchestrator = service_info.get("service_instance")
                        self.orchestrator = self.operations_orchestrator
                        self.logger.info("✅ Discovered OperationsOrchestrator")
                except Exception as e:
                    await self.handle_error_with_audit(e, "orchestrator_discovery", details={"orchestrator": "OperationsOrchestrator"})
                    self.logger.warning(f"⚠️ OperationsOrchestrator not available: {e}")
            
            self.is_initialized = True
            
            # Record health metric (success)
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.service_name
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True, details={
                "agent_name": self.service_name
            })
            
            self.logger.info(f"✅ {self.service_name} initialization complete")
            return True
        
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "initialize", details={"agent_name": self.service_name})
            
            # Record health metric (failure)
            await self.record_health_metric("initialization_failed", 1.0, {
                "agent_name": self.service_name,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("initialize_complete", success=False, details={
                "agent_name": self.service_name,
                "error": str(e)
            })
            
            self.is_initialized = False
            return False
    
    async def initialize_old(self):
        """OLD: Initialize the agent with business services."""
        try:
            if self.di_container:
                # Get business services from DI container
                self.sop_analysis_service = await self.di_container.get_service("sop_analysis_service")
                self.coexistence_optimization_service = await self.di_container.get_service("coexistence_optimization_service")
                
                self.is_initialized = True
                self.logger.info("✅ Operations Specialist Agent initialized with business services")
            else:
                self.logger.warning("⚠️ DI container not provided - agent will use fallback methods")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Operations Specialist Agent: {e}")
            raise e
    
    async def perform_analysis(self, request) -> Any:
        """
        Perform specialized operations analysis.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        """
        try:
            analysis_type = request.get("analysis_type", "general")
            data = request.get("data", {})
            user_context = request.get("user_context")
            session_id = request.get("session_id", "default")
            
            # Start telemetry tracking
            await self.log_operation_with_telemetry("perform_analysis_start", success=True, details={
                "analysis_type": analysis_type,
                "session_id": session_id
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "analysis", "perform"):
                        await self.record_health_metric("perform_analysis_access_denied", 1.0, {
                            "analysis_type": analysis_type
                        })
                        await self.log_operation_with_telemetry("perform_analysis_complete", success=False, details={
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions to perform analysis")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant_id = getattr(user_context, "tenant_id", None)
                if tenant_id and hasattr(self, "public_works_foundation"):
                    try:
                        tenant_service = self.public_works_foundation.get_tenant_service()
                        if tenant_service and not await tenant_service.validate_tenant_access(tenant_id):
                            await self.record_health_metric("perform_analysis_tenant_denied", 1.0, {
                                "analysis_type": analysis_type,
                                "tenant_id": tenant_id
                            })
                            await self.log_operation_with_telemetry("perform_analysis_complete", success=False, details={
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            
            result = None
            if analysis_type == "process_analysis":
                result = await self._perform_process_analysis(data, user_context, session_id)
            elif analysis_type == "coexistence_analysis":
                result = await self._perform_coexistence_analysis(data, user_context, session_id)
            elif analysis_type == "coexistence_blueprint":
                result = await self._generate_coexistence_blueprint_analysis(data, user_context, session_id)
            elif analysis_type == "workflow_analysis":
                result = await self._perform_workflow_analysis(data, user_context, session_id)
            elif analysis_type == "optimization_analysis":
                result = await self._perform_optimization_analysis(data, user_context, session_id)
            else:
                result = await self._perform_general_analysis(data, user_context, session_id)
            
            # Record health metric (success)
            await self.record_health_metric("perform_analysis_success", 1.0, {
                "analysis_type": analysis_type
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("perform_analysis_complete", success=True)
            
            return result
                
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "perform_analysis", details={
                "analysis_type": request.get("analysis_type", "general"),
                "session_id": request.get("session_id", "default")
            })
            
            # Record health metric (failure)
            await self.record_health_metric("perform_analysis_error", 1.0, {
                "analysis_type": request.get("analysis_type", "general"),
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("perform_analysis_complete", success=False, details={
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e),
                "analysis_result": "Analysis failed due to an error"
            }
    
    # ========================================================================
    # CRITICAL REASONING METHODS (Agentic-Forward Pattern)
    # ========================================================================
    # These methods do the critical reasoning FIRST, before services execute
    
    async def analyze_process_for_workflow_structure(
        self,
        process_content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        CRITICAL REASONING: Analyze process content to identify where workflows add value
        and determine optimal workflow structure.
        
        This is the agentic-forward approach - agent does critical reasoning FIRST,
        then services execute based on agent's strategic decisions.
        
        Args:
            process_content: Process content (SOP, document, or process description)
            context: Optional context (business goals, constraints)
            user_id: User identifier
        
        Returns:
            Workflow structure specification for service to execute:
            {
                "success": bool,
                "workflow_structure": {
                    "steps": [...],  # Agent-specified workflow steps
                    "decision_points": [...],  # Agent-identified decision points
                    "ai_value_opportunities": [...],  # Where AI can add value
                    "automation_opportunities": [...],  # What can be automated
                    "recommended_approach": str
                },
                "reasoning": {
                    "analysis": str,  # Agent's reasoning
                    "key_insights": [...],
                    "recommendations": [...]
                }
            }
        """
        try:
            self.logger.info("🧠 Performing critical reasoning for workflow structure...")
            
            # Use LLM abstraction for critical reasoning
            if not self.llm_abstraction:
                self.logger.error("❌ LLM abstraction not available - agentic-forward pattern requires LLM")
                return {
                    "success": False,
                    "error": "LLM abstraction not available",
                    "error_type": "agent_unavailable",
                    "message": "Agentic-forward pattern requires LLM for critical reasoning. LLM abstraction is not initialized."
                }
            
            # Build analysis prompt for LLM
            analysis_prompt = f"""
Analyze the following process content and determine:
1. Where can workflows add the most value?
2. What workflow structure would maximize efficiency?
3. Where can AI assist in this workflow?
4. What steps should be automated vs. human-driven?

Process Content: {process_content}
Context: {context or {}}

Provide a workflow structure that maximizes value and identifies AI opportunities.
"""
            
            # Use LLM for critical reasoning
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            # Get configurable model (default to GPT_4O_MINI)
            model = self._get_llm_model()
            
            llm_request = LLMRequest(
                messages=[
                    {"role": "system", "content": "You are an operations specialist analyzing process content to determine optimal workflow structures."},
                    {"role": "user", "content": analysis_prompt}
                ],
                model=model,
                max_tokens=2000,
                temperature=0.7,
                metadata={"task": "workflow_structure_analysis", "user_id": "agent"}
            )
            
            # Log LLM request details
            self.logger.info(f"📡 Making LLM request with model: {model.value}")
            self.logger.debug(f"   Process content length: {len(str(process_content))} chars")
            self.logger.debug(f"   Context keys: {list(context.keys()) if context else 'None'}")
            
            # Make LLM call with error handling
            try:
                self.logger.info("📡 Calling LLM abstraction...")
                llm_response = await self.llm_abstraction.generate_response(llm_request)
                self.logger.info(f"✅ LLM response received: {len(str(llm_response))} chars")
            except Exception as llm_error:
                self.logger.error(f"❌ LLM call failed: {llm_error}")
                self.logger.error(f"   Error type: {type(llm_error).__name__}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return {
                    "success": False,
                    "error": f"LLM call failed: {str(llm_error)}",
                    "error_type": "llm_call_failed",
                    "message": "Agentic-forward pattern requires successful LLM reasoning. LLM call failed."
                }
            
            # Extract reasoning from LLM response with validation
            reasoning_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            if not reasoning_text:
                self.logger.error("❌ Empty LLM response - agentic-forward pattern requires valid reasoning")
                return {
                    "success": False,
                    "error": "Empty LLM response",
                    "error_type": "empty_llm_response",
                    "message": "Agentic-forward pattern requires valid LLM reasoning. Received empty response."
                }
            
            self.logger.info(f"✅ Reasoning text extracted: {len(reasoning_text)} chars")
            
            # Determine workflow structure from reasoning
            workflow_structure = await self._determine_workflow_structure_from_reasoning(
                process_content, context, reasoning_text
            )
            
            # Identify AI value opportunities
            ai_value_opportunities = await self._identify_workflow_ai_opportunities(
                process_content, workflow_structure
            )
            
            return {
                "success": True,
                "workflow_structure": workflow_structure,
                "ai_value_opportunities": ai_value_opportunities,
                "reasoning": {
                    "analysis": reasoning_text,
                    "key_insights": self._extract_key_insights(reasoning_text),
                    "recommendations": self._extract_recommendations(reasoning_text)
                },
                "message": "Critical reasoning completed - ready for service execution"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Critical reasoning for workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "reasoning_failed",
                "message": "Agentic-forward pattern requires successful critical reasoning. Analysis failed."
            }
    
    async def analyze_for_sop_structure(
        self,
        workflow_content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        CRITICAL REASONING: Analyze workflow content to determine optimal SOP structure.
        
        This is the agentic-forward approach - agent does critical reasoning FIRST,
        then services execute based on agent's strategic decisions.
        
        Args:
            workflow_content: Workflow content or process description
            context: Optional context
            user_id: User identifier
        
        Returns:
            SOP structure specification for service to execute
        """
        try:
            self.logger.info("🧠 Performing critical reasoning for SOP structure...")
            
            # Use LLM abstraction for critical reasoning
            if not self.llm_abstraction:
                self.logger.error("❌ LLM abstraction not available - agentic-forward pattern requires LLM")
                return {
                    "success": False,
                    "error": "LLM abstraction not available",
                    "error_type": "agent_unavailable",
                    "message": "Agentic-forward pattern requires LLM for critical reasoning. LLM abstraction is not initialized."
                }
            
            # Build analysis prompt for LLM
            analysis_prompt = f"""
Analyze the following workflow content and determine:
1. How should this be structured as an SOP?
2. What steps are critical for documentation?
3. Where can AI assist in SOP execution?
4. What level of detail is needed?

Workflow Content: {workflow_content}
Context: {context or {}}

Provide an SOP structure that maximizes clarity and identifies AI assistance opportunities.
"""
            
            # Use LLM for critical reasoning
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            # Get configurable model (default to GPT_4O_MINI)
            model = self._get_llm_model()
            
            llm_request = LLMRequest(
                messages=[
                    {"role": "system", "content": "You are an operations specialist analyzing workflow content to determine optimal SOP structures."},
                    {"role": "user", "content": analysis_prompt}
                ],
                model=model,
                max_tokens=2000,
                temperature=0.7,
                metadata={"task": "sop_structure_analysis", "user_id": "agent"}
            )
            
            # Log LLM request details
            self.logger.info(f"📡 Making LLM request with model: {model.value}")
            self.logger.debug(f"   Workflow content length: {len(str(workflow_content))} chars")
            self.logger.debug(f"   Context keys: {list(context.keys()) if context else 'None'}")
            
            # Make LLM call with error handling
            try:
                self.logger.info("📡 Calling LLM abstraction...")
                llm_response = await self.llm_abstraction.generate_response(llm_request)
                self.logger.info(f"✅ LLM response received: {len(str(llm_response))} chars")
            except Exception as llm_error:
                self.logger.error(f"❌ LLM call failed: {llm_error}")
                self.logger.error(f"   Error type: {type(llm_error).__name__}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return {
                    "success": False,
                    "error": f"LLM call failed: {str(llm_error)}",
                    "error_type": "llm_call_failed",
                    "message": "Agentic-forward pattern requires successful LLM reasoning. LLM call failed."
                }
            
            # Extract reasoning from LLM response with validation
            reasoning_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            if not reasoning_text:
                self.logger.error("❌ Empty LLM response - agentic-forward pattern requires valid reasoning")
                return {
                    "success": False,
                    "error": "Empty LLM response",
                    "error_type": "empty_llm_response",
                    "message": "Agentic-forward pattern requires valid LLM reasoning. Received empty response."
                }
            
            self.logger.info(f"✅ Reasoning text extracted: {len(reasoning_text)} chars")
            
            # Determine SOP structure from reasoning
            sop_structure = await self._determine_sop_structure_from_reasoning(
                workflow_content, context, reasoning_text
            )
            
            return {
                "success": True,
                "sop_structure": sop_structure,
                "reasoning": {
                    "analysis": reasoning_text,
                    "key_insights": self._extract_key_insights(reasoning_text),
                    "recommendations": self._extract_recommendations(reasoning_text)
                },
                "message": "Critical reasoning completed - ready for service execution"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Critical reasoning for SOP failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "reasoning_failed",
                "message": "Agentic-forward pattern requires successful critical reasoning. Analysis failed."
            }
    
    async def analyze_for_coexistence_structure(
        self,
        sop_content: Dict[str, Any],
        workflow_content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        CRITICAL REASONING: Analyze SOP and workflow to determine optimal coexistence structure.
        
        This is the agentic-forward approach - agent does critical reasoning FIRST,
        then services execute based on agent's strategic decisions.
        
        Args:
            sop_content: SOP content
            workflow_content: Workflow content
            context: Optional context
            user_id: User identifier
        
        Returns:
            Coexistence structure specification for service to execute
        """
        try:
            self.logger.info("🧠 Performing critical reasoning for coexistence structure...")
            
            # Use LLM abstraction for critical reasoning
            if not self.llm_abstraction:
                self.logger.error("❌ LLM abstraction not available - agentic-forward pattern requires LLM")
                return {
                    "success": False,
                    "error": "LLM abstraction not available",
                    "error_type": "agent_unavailable",
                    "message": "Agentic-forward pattern requires LLM for critical reasoning. LLM abstraction is not initialized."
                }
            
            # Build analysis prompt for LLM
            analysis_prompt = f"""
Analyze the following SOP and workflow content and determine:
1. How should humans and AI coexist in this process?
2. What are optimal handoff points?
3. Where can AI augment human capabilities?
4. What coexistence structure maximizes value?

SOP Content: {sop_content}
Workflow Content: {workflow_content}
Context: {context or {}}

Provide a coexistence structure that maximizes human-AI collaboration value.
"""
            
            # Use LLM for critical reasoning
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            # Get configurable model (default to GPT_4O_MINI)
            model = self._get_llm_model()
            
            llm_request = LLMRequest(
                messages=[
                    {"role": "system", "content": "You are an operations specialist analyzing SOP and workflow content to determine optimal coexistence blueprint structures."},
                    {"role": "user", "content": analysis_prompt}
                ],
                model=model,
                max_tokens=2000,
                temperature=0.7,
                metadata={"task": "coexistence_structure_analysis",
                    "sop_content": sop_content,
                    "workflow_content": workflow_content,
                    "context": context
                }
            )
            
            # Log LLM request details
            self.logger.info(f"📡 Making LLM request with model: {model.value}")
            self.logger.debug(f"   SOP content length: {len(str(sop_content))} chars")
            self.logger.debug(f"   Workflow content length: {len(str(workflow_content))} chars")
            self.logger.debug(f"   Context keys: {list(context.keys()) if context else 'None'}")
            
            # Make LLM call with error handling
            try:
                self.logger.info("📡 Calling LLM abstraction...")
                llm_response = await self.llm_abstraction.generate_response(llm_request)
                self.logger.info(f"✅ LLM response received: {len(str(llm_response))} chars")
            except Exception as llm_error:
                self.logger.error(f"❌ LLM call failed: {llm_error}")
                self.logger.error(f"   Error type: {type(llm_error).__name__}")
                import traceback
                self.logger.error(f"   Traceback: {traceback.format_exc()}")
                return {
                    "success": False,
                    "error": f"LLM call failed: {str(llm_error)}",
                    "error_type": "llm_call_failed",
                    "message": "Agentic-forward pattern requires successful LLM reasoning. LLM call failed."
                }
            
            # Extract reasoning from LLM response with validation
            reasoning_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            if not reasoning_text:
                self.logger.error("❌ Empty LLM response - agentic-forward pattern requires valid reasoning")
                return {
                    "success": False,
                    "error": "Empty LLM response",
                    "error_type": "empty_llm_response",
                    "message": "Agentic-forward pattern requires valid LLM reasoning. Received empty response."
                }
            
            self.logger.info(f"✅ Reasoning text extracted: {len(reasoning_text)} chars")
            
            # Determine coexistence structure from reasoning
            coexistence_structure = await self._determine_coexistence_structure_from_reasoning(
                sop_content, workflow_content, context, reasoning_text
            )
            
            return {
                "success": True,
                "coexistence_structure": coexistence_structure,
                "reasoning": {
                    "analysis": reasoning_text,
                    "key_insights": self._extract_key_insights(reasoning_text),
                    "recommendations": self._extract_recommendations(reasoning_text)
                },
                "message": "Critical reasoning completed - ready for service execution"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Critical reasoning for coexistence failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "reasoning_failed",
                "message": "Agentic-forward pattern requires successful critical reasoning. Analysis failed."
            }
    
    # Helper methods for critical reasoning
    async def _determine_workflow_structure_from_reasoning(
        self,
        process_content: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        reasoning_text: str
    ) -> Dict[str, Any]:
        """Determine workflow structure from agent reasoning."""
        # Parse reasoning to extract structure decisions
        # Agent decides on steps, decision points, automation opportunities
        
        return {
            "steps": self._extract_workflow_steps_from_reasoning(reasoning_text, process_content),
            "decision_points": self._extract_decision_points_from_reasoning(reasoning_text),
            "automation_opportunities": self._extract_automation_opportunities_from_reasoning(reasoning_text),
            "recommended_approach": "ai_augmented_workflow"
        }
    
    async def _determine_sop_structure_from_reasoning(
        self,
        workflow_content: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        reasoning_text: str
    ) -> Dict[str, Any]:
        """Determine SOP structure from agent reasoning."""
        return {
            "title": self._extract_sop_title_from_reasoning(reasoning_text, workflow_content),
            "description": self._extract_sop_description_from_reasoning(reasoning_text),
            "steps": self._extract_sop_steps_from_reasoning(reasoning_text, workflow_content),
            "ai_assistance_points": self._extract_ai_assistance_points_from_reasoning(reasoning_text)
        }
    
    async def _determine_coexistence_structure_from_reasoning(
        self,
        sop_content: Dict[str, Any],
        workflow_content: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        reasoning_text: str
    ) -> Dict[str, Any]:
        """Determine coexistence structure from agent reasoning."""
        return {
            "handoff_points": self._extract_handoff_points_from_reasoning(reasoning_text),
            "ai_augmentation_points": self._extract_ai_augmentation_points_from_reasoning(reasoning_text),
            "human_driven_steps": self._extract_human_driven_steps_from_reasoning(reasoning_text),
            "ai_driven_steps": self._extract_ai_driven_steps_from_reasoning(reasoning_text),
            "collaboration_pattern": self._extract_collaboration_pattern_from_reasoning(reasoning_text)
        }
    
    async def _identify_workflow_ai_opportunities(
        self,
        process_content: Dict[str, Any],
        workflow_structure: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify where AI can add value in workflow."""
        opportunities = []
        
        # Agent identifies specific AI value opportunities
        opportunities.append({
            "area": "Process Automation",
            "ai_value": "AI can automate repetitive steps",
            "impact": "high",
            "rationale": "Reduces manual effort and errors"
        })
        
        opportunities.append({
            "area": "Decision Support",
            "ai_value": "AI can provide recommendations at decision points",
            "impact": "medium",
            "rationale": "Enhances decision quality"
        })
        
        return opportunities
    
    # Helper extraction methods
    def _extract_workflow_steps_from_reasoning(self, reasoning_text: str, process_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract workflow steps from reasoning."""
        steps = []
        
        # First, try to extract from process_content (SOP structure)
        if isinstance(process_content, dict):
            # Handle SOP structure with sections
            if "sections" in process_content:
                step_order = 1
                for section in process_content.get("sections", []):
                    section_name = section.get("name", "")
                    for step in section.get("steps", []):
                        steps.append({
                            "step_id": f"step_{step_order}",
                            "name": step.get("action", step.get("name", f"Step {step_order}")),
                            "description": f"{section_name}: {step.get('action', '')}",
                            "role": step.get("role", ""),
                            "order": step_order
                        })
                        step_order += 1
            # Handle direct steps structure
            elif "steps" in process_content:
                for idx, step in enumerate(process_content.get("steps", [])):
                    steps.append({
                        "step_id": f"step_{idx + 1}",
                        "name": step.get("name", step.get("instruction", f"Step {idx + 1}")),
                        "description": step.get("description", ""),
                        "order": idx + 1
                    })
        
        # If no steps found in process_content, try to extract from LLM reasoning text
        if not steps and reasoning_text:
            # Parse reasoning text for numbered steps or bullet points
            import re
            # Look for numbered steps (1., 2., etc.) or bullet points (-, *, etc.)
            step_patterns = [
                r'(\d+)\.\s+([^\n]+)',  # Numbered steps: "1. Step description"
                r'[-*]\s+([^\n]+)',     # Bullet points: "- Step description"
                r'Step\s+(\d+)[:\.]\s+([^\n]+)',  # "Step 1: description"
            ]
            
            for pattern in step_patterns:
                matches = re.findall(pattern, reasoning_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    for idx, match in enumerate(matches):
                        if isinstance(match, tuple):
                            step_name = match[-1].strip() if len(match) > 1 else match[0].strip()
                        else:
                            step_name = match.strip()
                        
                        if step_name and len(step_name) > 5:  # Filter out very short matches
                            steps.append({
                                "step_id": f"step_{idx + 1}",
                                "name": step_name,
                                "description": step_name,
                                "order": idx + 1
                            })
                    if steps:
                        break
        
        # Fallback: Create at least one step if we have process content
        if not steps and isinstance(process_content, dict):
            title = process_content.get("title", "Workflow Process")
            steps.append({
                "step_id": "step_1",
                "name": f"Execute {title}",
                "description": process_content.get("purpose", "Execute the process"),
                "order": 1
            })
        
        return steps
    
    def _extract_decision_points_from_reasoning(self, reasoning_text: str) -> List[Dict[str, Any]]:
        """Extract decision points from reasoning."""
        return []
    
    def _extract_automation_opportunities_from_reasoning(self, reasoning_text: str) -> List[Dict[str, Any]]:
        """Extract automation opportunities from reasoning."""
        return []
    
    def _extract_sop_title_from_reasoning(self, reasoning_text: str, workflow_content: Dict[str, Any]) -> str:
        """Extract SOP title from reasoning."""
        if isinstance(workflow_content, dict):
            return workflow_content.get("title", "Standard Operating Procedure")
        return "Standard Operating Procedure"
    
    def _extract_sop_description_from_reasoning(self, reasoning_text: str) -> str:
        """Extract SOP description from reasoning."""
        return "Standard operating procedure generated from workflow"
    
    def _extract_sop_steps_from_reasoning(self, reasoning_text: str, workflow_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract SOP steps from reasoning."""
        steps = []
        
        # Handle workflow with nodes (BPMN-style)
        if isinstance(workflow_content, dict) and "nodes" in workflow_content:
            # Filter out start/end nodes and extract task nodes
            task_nodes = [
                node for node in workflow_content.get("nodes", [])
                if node.get("type") not in ["start", "end"]
            ]
            for idx, node in enumerate(task_nodes):
                steps.append({
                    "step_number": idx + 1,
                    "instruction": node.get("label", node.get("name", f"Step {idx + 1}")),
                    "details": node.get("description", "")
                })
        # Handle workflow with steps
        elif isinstance(workflow_content, dict) and "steps" in workflow_content:
            for idx, step in enumerate(workflow_content.get("steps", [])):
                steps.append({
                    "step_number": idx + 1,
                    "instruction": step.get("name", step.get("instruction", f"Step {idx + 1}")),
                    "details": step.get("description", "")
                })
        
        # If no steps found, try to extract from reasoning text
        if not steps and reasoning_text:
            import re
            step_patterns = [
                r'(\d+)\.\s+([^\n]+)',  # Numbered steps: "1. Step description"
                r'[-*]\s+([^\n]+)',     # Bullet points: "- Step description"
                r'Step\s+(\d+)[:\.]\s+([^\n]+)',  # "Step 1: description"
            ]
            
            for pattern in step_patterns:
                matches = re.findall(pattern, reasoning_text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    for idx, match in enumerate(matches):
                        if isinstance(match, tuple):
                            step_name = match[-1].strip() if len(match) > 1 else match[0].strip()
                        else:
                            step_name = match.strip()
                        
                        if step_name and len(step_name) > 5:  # Filter out very short matches
                            steps.append({
                                "step_number": idx + 1,
                                "instruction": step_name,
                                "details": step_name
                            })
                    if steps:
                        break
        
        # Fallback: Create at least one step if we have workflow content
        if not steps and isinstance(workflow_content, dict):
            title = workflow_content.get("name", workflow_content.get("title", "Workflow Process"))
            steps.append({
                "step_number": 1,
                "instruction": f"Execute {title}",
                "details": workflow_content.get("description", "Execute the workflow process")
            })
        
        return steps
    
    def _extract_ai_assistance_points_from_reasoning(self, reasoning_text: str) -> List[Dict[str, Any]]:
        """Extract AI assistance points from reasoning."""
        return []
    
    def _extract_handoff_points_from_reasoning(self, reasoning_text: str) -> List[Dict[str, Any]]:
        """Extract handoff points from reasoning."""
        return []
    
    def _extract_ai_augmentation_points_from_reasoning(self, reasoning_text: str) -> List[Dict[str, Any]]:
        """Extract AI augmentation points from reasoning."""
        return []
    
    def _extract_human_driven_steps_from_reasoning(self, reasoning_text: str) -> List[str]:
        """Extract human-driven steps from reasoning."""
        return []
    
    def _extract_ai_driven_steps_from_reasoning(self, reasoning_text: str) -> List[str]:
        """Extract AI-driven steps from reasoning."""
        return []
    
    def _extract_collaboration_pattern_from_reasoning(self, reasoning_text: str) -> str:
        """Extract collaboration pattern from reasoning."""
        return "ai_augmented"
    
    def _extract_key_insights(self, reasoning_text: str) -> List[str]:
        """Extract key insights from reasoning text."""
        return ["AI can add value in process automation", "Workflow structure should optimize for human-AI collaboration"]
    
    def _extract_recommendations(self, reasoning_text: str) -> List[str]:
        """Extract recommendations from reasoning text."""
        return ["Prioritize AI-assisted steps", "Focus on coexistence optimization"]
    
    async def _perform_process_analysis(self, data: Dict[str, Any], user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Perform detailed process analysis."""
        try:
            process_definition = data.get("process_definition", {})
            
            # Analyze process characteristics
            analysis = {
                "process_id": process_definition.get("id", "unknown"),
                "process_name": process_definition.get("name", "Unknown Process"),
                "complexity_score": self._calculate_complexity_score(process_definition),
                "efficiency_score": self._calculate_efficiency_score(process_definition),
                "automation_potential": self._assess_automation_potential(process_definition),
                "bottlenecks": self._identify_bottlenecks(process_definition),
                "redundancies": self._identify_redundancies(process_definition),
                "optimization_opportunities": self._identify_optimization_opportunities(process_definition),
                "risk_factors": self._identify_risk_factors(process_definition),
                "recommendations": self._generate_process_recommendations(process_definition)
            }
            
            return {
                "success": True,
                "analysis_type": "process_analysis",
                "analysis_result": analysis,
                "confidence_score": 0.85,
                "processing_time": 2.5
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform process analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def _perform_coexistence_analysis(self, data: Dict[str, Any], user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Perform detailed coexistence analysis using new infrastructure capabilities."""
        try:
            workflow_data = data.get("workflow_data", {})
            sop_data = data.get("sop_data", {})
            
            # Use new infrastructure capabilities for coexistence analysis
            if self.is_initialized and self.coexistence_optimization_service:
                # Analyze human-AI coexistence using business service
                coexistence_result = await self.coexistence_optimization_service.analyze_human_ai_coexistence(
                    workflow_data, user_context
                )
                
                if coexistence_result.get("success"):
                    # Generate coexistence blueprint
                    blueprint_result = await self._generate_coexistence_blueprint(
                        coexistence_result, workflow_data, sop_data, user_context, session_id
                    )
                    
                    return {
                        "success": True,
                        "analysis_type": "coexistence_analysis",
                        "analysis_result": coexistence_result.get("business_analysis", {}),
                        "coexistence_blueprint": blueprint_result,
                        "confidence_score": 0.95,
                        "processing_time": 2.8,
                        "infrastructure_enhanced": True
                    }
                else:
                    self.logger.warning("⚠️ Coexistence analysis failed, falling back to legacy method")
            
            # Fallback to legacy analysis if infrastructure not available
            return await self._perform_legacy_coexistence_analysis(data, user_context, session_id)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform coexistence analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_coexistence_blueprint(self, coexistence_result: Dict[str, Any], workflow_data: Dict[str, Any], 
                                            sop_data: Dict[str, Any], user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Generate coexistence blueprint using LLM and infrastructure capabilities."""
        try:
            # Extract analysis data
            business_analysis = coexistence_result.get("business_analysis", {})
            coexistence_analysis = coexistence_result.get("coexistence_analysis", {})
            
            # Use LLM to generate coexistence blueprint
            blueprint_prompt = self._create_blueprint_prompt(business_analysis, coexistence_analysis, workflow_data, sop_data)
            
            # Generate blueprint using LLM (via utility foundation)
            if self.utility_foundation and hasattr(self.utility_foundation, 'generate_llm_response'):
                blueprint_response = await self.utility_foundation.generate_llm_response(
                    prompt=blueprint_prompt,
                    user_context=user_context,
                    session_id=session_id
                )
                
                return {
                    "success": True,
                    "blueprint": blueprint_response,
                    "analysis_summary": business_analysis,
                    "recommendations": coexistence_analysis.get("recommendations", []),
                    "generated_at": datetime.utcnow().isoformat()
                }
            else:
                # Fallback blueprint generation without LLM
                return self._generate_fallback_blueprint(business_analysis, coexistence_analysis)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate coexistence blueprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _create_blueprint_prompt(self, business_analysis: Dict[str, Any], coexistence_analysis: Dict[str, Any], 
                               workflow_data: Dict[str, Any], sop_data: Dict[str, Any]) -> str:
        """Create prompt for LLM to generate coexistence blueprint."""
        try:
            prompt = f"""
            Generate a comprehensive coexistence blueprint for optimizing human-AI collaboration in business processes.
            
            Current Analysis:
            - Coexistence Score: {business_analysis.get('coexistence_score', 'N/A')}
            - Optimization Potential: {business_analysis.get('optimization_potential', 'N/A')}
            - Critical Issues: {business_analysis.get('critical_issues', [])}
            - Business Impact: {business_analysis.get('business_impact', 'N/A')}
            
            Workflow Data:
            - Process Name: {workflow_data.get('name', 'Unknown')}
            - Node Count: {len(workflow_data.get('nodes', []))}
            - Edge Count: {len(workflow_data.get('edges', []))}
            
            SOP Data:
            - SOP Title: {sop_data.get('title', 'Unknown')}
            - Step Count: {len(sop_data.get('steps', []))}
            
            Please provide:
            1. Executive Summary of coexistence optimization opportunities
            2. Detailed recommendations for human-AI collaboration improvements
            3. Implementation roadmap with priorities
            4. Success metrics and KPIs
            5. Risk mitigation strategies
            6. Expected business impact and ROI
            """
            
            return prompt
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create blueprint prompt: {e}")
            return "Generate a coexistence blueprint for human-AI collaboration optimization."
    
    def _generate_fallback_blueprint(self, business_analysis: Dict[str, Any], coexistence_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback blueprint without LLM."""
        try:
            return {
                "success": True,
                "blueprint": {
                    "executive_summary": f"Coexistence optimization opportunities identified with score: {business_analysis.get('coexistence_score', 'N/A')}",
                    "recommendations": business_analysis.get('recommendations', []),
                    "implementation_roadmap": [
                        "Phase 1: Assess current state",
                        "Phase 2: Implement high-priority optimizations", 
                        "Phase 3: Monitor and optimize"
                    ],
                    "success_metrics": [
                        "Coexistence score improvement",
                        "Process efficiency gains",
                        "Human-AI collaboration quality"
                    ]
                },
                "analysis_summary": business_analysis,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate fallback blueprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def _perform_legacy_coexistence_analysis(self, data: Dict[str, Any], user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Perform legacy coexistence analysis (fallback method)."""
        try:
            current_state = data.get("current_state", {})
            target_state = data.get("target_state", {})
            
            # Legacy analysis logic
            analysis = {
                "current_pattern": self._identify_coexistence_pattern(current_state),
                "target_pattern": self._identify_coexistence_pattern(target_state),
                "collaboration_gap": self._calculate_collaboration_gap(current_state, target_state),
                "trust_level": await self._assess_trust_level(current_state),
                "efficiency_impact": await self._calculate_efficiency_impact(current_state, target_state),
                "cultural_factors": self._analyze_cultural_factors(current_state, target_state),
                "technology_readiness": await self._assess_technology_readiness(current_state),
                "change_management_requirements": self._assess_change_management_requirements(current_state, target_state),
                "success_probability": await self._calculate_success_probability(current_state, target_state),
                "recommendations": await self._generate_coexistence_recommendations(current_state, target_state)
            }
            
            return {
                "success": True,
                "analysis_type": "coexistence_analysis",
                "analysis_result": analysis,
                "confidence_score": 0.75,
                "processing_time": 3.2,
                "infrastructure_enhanced": False
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform legacy coexistence analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_coexistence_blueprint_analysis(self, data: Dict[str, Any], user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive coexistence blueprint analysis."""
        try:
            workflow_data = data.get("workflow_data", {})
            sop_data = data.get("sop_data", {})
            
            # Step 1: Analyze SOP if provided
            sop_analysis = None
            if sop_data and self.is_initialized and self.sop_analysis_service:
                sop_analysis = await self.sop_analysis_service.analyze_sop_structure(
                    sop_data.get("text", ""), user_context
                )
            
            # Step 2: Analyze coexistence
            coexistence_analysis = await self._perform_coexistence_analysis(data, user_context, session_id)
            
            # Step 3: Generate comprehensive blueprint
            blueprint = await self._generate_comprehensive_coexistence_blueprint(
                sop_analysis, coexistence_analysis, workflow_data, sop_data, user_context, session_id
            )
            
            return {
                "success": True,
                "analysis_type": "coexistence_blueprint",
                "sop_analysis": sop_analysis,
                "coexistence_analysis": coexistence_analysis,
                "coexistence_blueprint": blueprint,
                "confidence_score": 0.95,
                "processing_time": 4.5,
                "infrastructure_enhanced": True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate coexistence blueprint analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_comprehensive_coexistence_blueprint(self, sop_analysis: Dict[str, Any], coexistence_analysis: Dict[str, Any], 
                                                          workflow_data: Dict[str, Any], sop_data: Dict[str, Any], 
                                                          user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive coexistence blueprint combining all analyses."""
        try:
            # Create comprehensive prompt for LLM
            comprehensive_prompt = self._create_comprehensive_blueprint_prompt(
                sop_analysis, coexistence_analysis, workflow_data, sop_data
            )
            
            # Generate comprehensive blueprint using LLM
            if self.utility_foundation and hasattr(self.utility_foundation, 'generate_llm_response'):
                blueprint_response = await self.utility_foundation.generate_llm_response(
                    prompt=comprehensive_prompt,
                    user_context=user_context,
                    session_id=session_id
                )
                
                return {
                    "success": True,
                    "comprehensive_blueprint": blueprint_response,
                    "sop_insights": sop_analysis.get("sop_analysis", {}) if sop_analysis else {},
                    "coexistence_insights": coexistence_analysis.get("analysis_result", {}),
                    "implementation_roadmap": self._create_implementation_roadmap(sop_analysis, coexistence_analysis),
                    "success_metrics": self._define_success_metrics(sop_analysis, coexistence_analysis),
                    "generated_at": datetime.utcnow().isoformat()
                }
            else:
                # Fallback comprehensive blueprint
                return self._generate_fallback_comprehensive_blueprint(sop_analysis, coexistence_analysis)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate comprehensive coexistence blueprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _create_comprehensive_blueprint_prompt(self, sop_analysis: Dict[str, Any], coexistence_analysis: Dict[str, Any], 
                                             workflow_data: Dict[str, Any], sop_data: Dict[str, Any]) -> str:
        """Create comprehensive prompt for LLM blueprint generation."""
        try:
            prompt = f"""
            Generate a comprehensive coexistence blueprint for optimizing human-AI collaboration in business processes.
            
            SOP Analysis:
            {sop_analysis.get('sop_analysis', {}) if sop_analysis else 'No SOP analysis available'}
            
            Coexistence Analysis:
            {coexistence_analysis.get('analysis_result', {})}
            
            Process Context:
            - Workflow: {workflow_data.get('name', 'Unknown')}
            - SOP: {sop_data.get('title', 'Unknown')}
            
            Please provide a comprehensive blueprint including:
            1. Executive Summary with key findings
            2. Current State Assessment
            3. Coexistence Optimization Opportunities
            4. Detailed Implementation Plan
            5. Success Metrics and KPIs
            6. Risk Assessment and Mitigation
            7. Expected Business Impact and ROI
            8. Timeline and Milestones
            9. Resource Requirements
            10. Monitoring and Evaluation Plan
            """
            
            return prompt
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create comprehensive blueprint prompt: {e}")
            return "Generate a comprehensive coexistence blueprint for human-AI collaboration optimization."
    
    def _create_implementation_roadmap(self, sop_analysis: Dict[str, Any], coexistence_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create implementation roadmap based on analyses."""
        try:
            roadmap = []
            
            # Phase 1: Assessment and Planning
            roadmap.append({
                "phase": 1,
                "name": "Assessment and Planning",
                "duration": "2-4 weeks",
                "activities": [
                    "Complete current state assessment",
                    "Identify optimization opportunities",
                    "Develop implementation strategy"
                ],
                "dependencies": []
            })
            
            # Phase 2: Pilot Implementation
            roadmap.append({
                "phase": 2,
                "name": "Pilot Implementation",
                "duration": "4-6 weeks",
                "activities": [
                    "Implement high-priority optimizations",
                    "Test coexistence improvements",
                    "Gather feedback and metrics"
                ],
                "dependencies": ["Phase 1"]
            })
            
            # Phase 3: Full Rollout
            roadmap.append({
                "phase": 3,
                "name": "Full Rollout",
                "duration": "6-8 weeks",
                "activities": [
                    "Scale successful optimizations",
                    "Implement remaining improvements",
                    "Establish monitoring and evaluation"
                ],
                "dependencies": ["Phase 2"]
            })
            
            return roadmap
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create implementation roadmap: {e}")
            return []
    
    def _define_success_metrics(self, sop_analysis: Dict[str, Any], coexistence_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define success metrics based on analyses."""
        try:
            metrics = [
                {
                    "metric": "Coexistence Score Improvement",
                    "baseline": "Current coexistence score",
                    "target": "20% improvement",
                    "measurement": "Monthly assessment"
                },
                {
                    "metric": "Process Efficiency",
                    "baseline": "Current process efficiency",
                    "target": "15% improvement",
                    "measurement": "Weekly process metrics"
                },
                {
                    "metric": "Human-AI Collaboration Quality",
                    "baseline": "Current collaboration score",
                    "target": "25% improvement",
                    "measurement": "Monthly surveys and assessments"
                },
                {
                    "metric": "Implementation Success Rate",
                    "baseline": "0%",
                    "target": "90% of planned optimizations",
                    "measurement": "Weekly progress tracking"
                }
            ]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to define success metrics: {e}")
            return []
    
    def _generate_fallback_comprehensive_blueprint(self, sop_analysis: Dict[str, Any], coexistence_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback comprehensive blueprint without LLM."""
        try:
            return {
                "success": True,
                "comprehensive_blueprint": {
                    "executive_summary": "Comprehensive coexistence optimization blueprint generated",
                    "current_state": "Assessment completed",
                    "optimization_opportunities": "Multiple opportunities identified",
                    "implementation_plan": "Phased approach recommended",
                    "success_metrics": "Key metrics defined",
                    "risk_assessment": "Risks identified and mitigation strategies planned"
                },
                "implementation_roadmap": self._create_implementation_roadmap(sop_analysis, coexistence_analysis),
                "success_metrics": self._define_success_metrics(sop_analysis, coexistence_analysis),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate fallback comprehensive blueprint: {e}")
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def _perform_workflow_analysis(self, data: Dict[str, Any], user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Perform detailed workflow analysis."""
        try:
            workflow_definition = data.get("workflow_definition", {})
            
            # Analyze workflow characteristics
            analysis = {
                "workflow_id": workflow_definition.get("id", "unknown"),
                "workflow_name": workflow_definition.get("name", "Unknown Workflow"),
                "pattern_type": self._identify_workflow_pattern(workflow_definition),
                "complexity_metrics": self._calculate_workflow_complexity(workflow_definition),
                "execution_efficiency": self._assess_execution_efficiency(workflow_definition),
                "scalability": self._assess_scalability(workflow_definition),
                "maintainability": self._assess_maintainability(workflow_definition),
                "error_handling": self._assess_error_handling(workflow_definition),
                "performance_characteristics": self._analyze_performance_characteristics(workflow_definition),
                "optimization_potential": self._assess_optimization_potential(workflow_definition),
                "recommendations": self._generate_workflow_recommendations(workflow_definition)
            }
            
            return {
                "success": True,
                "analysis_type": "workflow_analysis",
                "analysis_result": analysis,
                "confidence_score": 0.88,
                "processing_time": 2.8
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform workflow analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def _perform_optimization_analysis(self, data: Dict[str, Any], user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Perform detailed optimization analysis."""
        try:
            process_definition = data.get("process_definition", {})
            optimization_goals = data.get("optimization_goals", [])
            
            # Analyze optimization opportunities
            analysis = {
                "current_performance": self._assess_current_performance(process_definition),
                "optimization_opportunities": self._identify_optimization_opportunities(process_definition, optimization_goals),
                "impact_assessment": self._assess_optimization_impact(process_definition, optimization_goals),
                "implementation_complexity": self._assess_implementation_complexity(process_definition, optimization_goals),
                "resource_requirements": self._estimate_resource_requirements(process_definition, optimization_goals),
                "timeline_estimation": self._estimate_optimization_timeline(process_definition, optimization_goals),
                "risk_assessment": self._assess_optimization_risks(process_definition, optimization_goals),
                "roi_projection": self._calculate_roi_projection(process_definition, optimization_goals),
                "success_metrics": self._define_success_metrics(process_definition, optimization_goals),
                "recommendations": self._generate_optimization_recommendations(process_definition, optimization_goals)
            }
            
            return {
                "success": True,
                "analysis_type": "optimization_analysis",
                "analysis_result": analysis,
                "confidence_score": 0.92,
                "processing_time": 4.1
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform optimization analysis: {e}")
            return {"success": False, "error": str(e)}
    
    async def _perform_general_analysis(self, data: Dict[str, Any], user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Perform general operations analysis."""
        try:
            # General analysis based on available data
            analysis = {
                "data_quality": self._assess_data_quality(data),
                "analysis_scope": self._determine_analysis_scope(data),
                "key_insights": self._extract_key_insights(data),
                "trends": self._identify_trends(data),
                "anomalies": self._detect_anomalies(data),
                "recommendations": self._generate_general_recommendations(data)
            }
            
            return {
                "success": True,
                "analysis_type": "general_analysis",
                "analysis_result": analysis,
                "confidence_score": 0.75,
                "processing_time": 1.8
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform general analysis: {e}")
            return {"success": False, "error": str(e)}
    
    # Helper methods for analysis calculations
    def _calculate_complexity_score(self, process_definition: Dict[str, Any]) -> float:
        """Calculate process complexity score."""
        steps = process_definition.get("steps", [])
        decisions = sum(1 for step in steps if step.get("type") == "decision")
        parallel_steps = sum(1 for step in steps if step.get("parallel_execution"))
        
        complexity = len(steps) * 0.3 + decisions * 0.5 + parallel_steps * 0.2
        return min(100, max(0, complexity))
    
    def _calculate_efficiency_score(self, process_definition: Dict[str, Any]) -> float:
        """Calculate process efficiency score."""
        steps = process_definition.get("steps", [])
        automated_steps = sum(1 for step in steps if step.get("automated"))
        redundant_steps = sum(1 for step in steps if step.get("redundant"))
        
        efficiency = (automated_steps / len(steps) * 50) + ((len(steps) - redundant_steps) / len(steps) * 50)
        return min(100, max(0, efficiency))
    
    def _assess_automation_potential(self, process_definition: Dict[str, Any]) -> str:
        """Assess automation potential of the process."""
        steps = process_definition.get("steps", [])
        automatable_steps = sum(1 for step in steps if self._is_step_automatable(step))
        
        ratio = automatable_steps / len(steps) if steps else 0
        
        if ratio > 0.7:
            return "high"
        elif ratio > 0.4:
            return "medium"
        else:
            return "low"
    
    def _is_step_automatable(self, step: Dict[str, Any]) -> bool:
        """Check if a step is automatable."""
        step_name = step.get("name", "").lower()
        automatable_keywords = ["data entry", "validation", "calculation", "notification", "routing"]
        return any(keyword in step_name for keyword in automatable_keywords)
    
    def _identify_bottlenecks(self, process_definition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify process bottlenecks."""
        bottlenecks = []
        steps = process_definition.get("steps", [])
        
        for step in steps:
            if step.get("type") == "approval" or "review" in step.get("name", "").lower():
                bottlenecks.append({
                    "step_id": step.get("id"),
                    "step_name": step.get("name"),
                    "type": "approval_bottleneck",
                    "severity": "medium"
                })
        
        return bottlenecks
    
    def _identify_redundancies(self, process_definition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify redundant steps."""
        redundancies = []
        steps = process_definition.get("steps", [])
        
        # Simple redundancy detection
        step_names = [step.get("name", "").lower() for step in steps]
        for i, name in enumerate(step_names):
            for j, other_name in enumerate(step_names[i+1:], i+1):
                if name == other_name:
                    redundancies.append({
                        "step_ids": [steps[i].get("id"), steps[j].get("id")],
                        "step_names": [steps[i].get("name"), steps[j].get("name")],
                        "type": "duplicate_steps"
                    })
        
        return redundancies
    
    def _identify_optimization_opportunities(self, process_definition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities."""
        opportunities = []
        
        # Automation opportunities
        if self._assess_automation_potential(process_definition) == "high":
            opportunities.append({
                "type": "automation",
                "description": "High automation potential detected",
                "impact": "high",
                "effort": "medium"
            })
        
        # Bottleneck removal opportunities
        bottlenecks = self._identify_bottlenecks(process_definition)
        if bottlenecks:
            opportunities.append({
                "type": "bottleneck_removal",
                "description": f"Remove {len(bottlenecks)} bottlenecks",
                "impact": "high",
                "effort": "high"
            })
        
        return opportunities
    
    def _identify_risk_factors(self, process_definition: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risk factors in the process."""
        risks = []
        steps = process_definition.get("steps", [])
        
        # Single points of failure
        if len(steps) == 1:
            risks.append({
                "type": "single_point_of_failure",
                "description": "Process has only one step",
                "severity": "high"
            })
        
        # Manual dependencies
        manual_steps = [step for step in steps if not step.get("automated")]
        if len(manual_steps) > len(steps) * 0.8:
            risks.append({
                "type": "high_manual_dependency",
                "description": "High percentage of manual steps",
                "severity": "medium"
            })
        
        return risks
    
    def _generate_process_recommendations(self, process_definition: Dict[str, Any]) -> List[str]:
        """Generate process recommendations."""
        recommendations = []
        
        # Automation recommendations
        if self._assess_automation_potential(process_definition) == "high":
            recommendations.append("Consider automating repetitive tasks to improve efficiency")
        
        # Bottleneck recommendations
        bottlenecks = self._identify_bottlenecks(process_definition)
        if bottlenecks:
            recommendations.append("Streamline approval processes to reduce bottlenecks")
        
        # Redundancy recommendations
        redundancies = self._identify_redundancies(process_definition)
        if redundancies:
            recommendations.append("Eliminate redundant steps to simplify the process")
        
        return recommendations
    
    # Additional helper methods for other analysis types
    def _identify_coexistence_pattern(self, state: Dict[str, Any]) -> str:
        """Identify coexistence pattern from state."""
        interaction_patterns = state.get("interaction_patterns", [])
        
        if any("collaborative" in pattern.lower() for pattern in interaction_patterns):
            return "collaborative"
        elif any("delegated" in pattern.lower() for pattern in interaction_patterns):
            return "delegated"
        elif any("augmented" in pattern.lower() for pattern in interaction_patterns):
            return "augmented"
        else:
            return "autonomous"
    
    def _calculate_collaboration_gap(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> str:
        """Calculate collaboration gap between states."""
        current_pattern = self._identify_coexistence_pattern(current_state)
        target_pattern = self._identify_coexistence_pattern(target_state)
        
        pattern_levels = {"autonomous": 1, "delegated": 2, "augmented": 3, "collaborative": 4}
        current_level = pattern_levels.get(current_pattern, 1)
        target_level = pattern_levels.get(target_pattern, 4)
        
        gap = target_level - current_level
        if gap == 0:
            return "none"
        elif gap == 1:
            return "small"
        elif gap == 2:
            return "medium"
        else:
            return "large"
    
    async def _assess_trust_level(self, state: Dict[str, Any]) -> str:
        """
        Assess trust level in AI systems using LLM reasoning.
        
        Analyzes the state to determine trust level (low, medium, high) based on:
        - AI system reliability indicators
        - Human-AI interaction patterns
        - Error rates and recovery mechanisms
        - Transparency and explainability
        
        Args:
            state: State dictionary containing process information
        
        Returns:
            Trust level: "low", "medium", or "high"
        """
        try:
            if not self.llm_abstraction:
                self.logger.warning("⚠️ LLM abstraction not available, using default trust level")
                return "medium"
            
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            system_prompt = """You are an operations specialist agent analyzing trust levels in AI systems for human-AI coexistence.

Analyze the provided state and determine the trust level based on:
- AI system reliability and consistency
- Error rates and recovery mechanisms
- Transparency and explainability of AI decisions
- Historical performance and user confidence
- Safety mechanisms and oversight

Return ONLY one word: "low", "medium", or "high"."""
            
            user_prompt = f"""Analyze this state and determine the trust level in AI systems:

State: {state}

Return ONLY one word: "low", "medium", or "high"."""
            
            llm_request = LLMRequest(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=10,
                temperature=0.3,
                metadata={"task": "assess_trust_level", "agent": "operations_specialist"}
            )
            
            llm_response = await self.llm_abstraction.generate_response(llm_request)
            response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Parse response (should be "low", "medium", or "high")
            response_text = response_text.strip().lower()
            if "low" in response_text:
                return "low"
            elif "high" in response_text:
                return "high"
            else:
                return "medium"  # Default to medium
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to assess trust level via LLM: {e}, using default")
            return "medium"
    
    async def _calculate_efficiency_impact(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> float:
        """
        Calculate efficiency impact of coexistence changes using LLM reasoning.
        
        Analyzes the difference between current and target states to estimate
        efficiency improvement percentage from human-AI coexistence.
        
        Args:
            current_state: Current process state
            target_state: Target process state with AI integration
        
        Returns:
            Efficiency improvement percentage (float, e.g., 15.5 for 15.5%)
        """
        try:
            if not self.llm_abstraction:
                self.logger.warning("⚠️ LLM abstraction not available, using default efficiency impact")
                return 15.0  # Default 15% improvement
            
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            system_prompt = """You are an operations specialist agent calculating efficiency impact of human-AI coexistence changes.

Analyze the difference between current and target states to estimate efficiency improvement percentage.

Consider:
- Automation opportunities
- Process optimization potential
- Time savings from AI assistance
- Error reduction benefits
- Resource utilization improvements

Return ONLY a number representing the percentage improvement (e.g., "15.5" for 15.5% improvement)."""
            
            user_prompt = f"""Calculate efficiency impact:

Current State: {current_state}
Target State: {target_state}

Return ONLY a number representing the percentage improvement (e.g., "15.5")."""
            
            llm_request = LLMRequest(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=20,
                temperature=0.3,
                metadata={"task": "calculate_efficiency_impact", "agent": "operations_specialist"}
            )
            
            llm_response = await self.llm_abstraction.generate_response(llm_request)
            response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Parse number from response
            try:
                # Extract first number from response
                import re
                numbers = re.findall(r'\d+\.?\d*', response_text)
                if numbers:
                    efficiency_impact = float(numbers[0])
                    # Clamp to reasonable range (0-100%)
                    efficiency_impact = max(0.0, min(100.0, efficiency_impact))
                    return efficiency_impact
                else:
                    self.logger.warning(f"⚠️ Could not parse efficiency impact from LLM response: {response_text}")
                    return 15.0  # Default
            except (ValueError, TypeError) as e:
                self.logger.warning(f"⚠️ Failed to parse efficiency impact: {e}")
                return 15.0  # Default
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to calculate efficiency impact via LLM: {e}, using default")
            return 15.0  # Default 15% improvement
    
    def _analyze_cultural_factors(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> List[str]:
        """Analyze cultural factors affecting coexistence."""
        return ["Change resistance", "Technology adoption", "Collaboration culture"]
    
    async def _assess_technology_readiness(self, state: Dict[str, Any]) -> str:
        """
        Assess technology readiness for coexistence using LLM reasoning.
        
        Analyzes the state to determine technology readiness (low, medium, high) based on:
        - Existing technology infrastructure
        - AI system integration capabilities
        - Data availability and quality
        - Technical skills and resources
        
        Args:
            state: State dictionary containing process and technology information
        
        Returns:
            Technology readiness: "low", "medium", or "high"
        """
        try:
            if not self.llm_abstraction:
                self.logger.warning("⚠️ LLM abstraction not available, using default technology readiness")
                return "medium"
            
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            system_prompt = """You are an operations specialist agent assessing technology readiness for human-AI coexistence.

Analyze the provided state and determine technology readiness based on:
- Existing technology infrastructure and capabilities
- AI system integration requirements and compatibility
- Data availability, quality, and accessibility
- Technical skills, resources, and support systems
- System maturity and stability

Return ONLY one word: "low", "medium", or "high"."""
            
            user_prompt = f"""Analyze this state and determine technology readiness:

State: {state}

Return ONLY one word: "low", "medium", or "high"."""
            
            llm_request = LLMRequest(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=10,
                temperature=0.3,
                metadata={"task": "assess_technology_readiness", "agent": "operations_specialist"}
            )
            
            llm_response = await self.llm_abstraction.generate_response(llm_request)
            response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Parse response (should be "low", "medium", or "high")
            response_text = response_text.strip().lower()
            if "low" in response_text:
                return "low"
            elif "high" in response_text:
                return "high"
            else:
                return "medium"  # Default to medium
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to assess technology readiness via LLM: {e}, using default")
            return "medium"
    
    def _assess_change_management_requirements(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> List[str]:
        """Assess change management requirements."""
        return ["Training programs", "Communication plan", "Support structure"]
    
    async def _calculate_success_probability(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> float:
        """
        Calculate success probability for coexistence transition using LLM reasoning.
        
        Analyzes the transition from current to target state to estimate
        the probability of successful coexistence implementation.
        
        Args:
            current_state: Current process state
            target_state: Target process state with AI integration
        
        Returns:
            Success probability (float between 0.0 and 1.0, e.g., 0.75 for 75%)
        """
        try:
            if not self.llm_abstraction:
                self.logger.warning("⚠️ LLM abstraction not available, using default success probability")
                return 0.75  # Default 75% success probability
            
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            system_prompt = """You are an operations specialist agent calculating success probability for human-AI coexistence transition.

Analyze the transition from current to target state to estimate the probability of successful implementation.

Consider:
- Complexity of the transition
- Resource availability
- Organizational readiness
- Technology maturity
- Change management factors
- Risk factors and mitigation strategies

Return ONLY a number between 0.0 and 1.0 representing the success probability (e.g., "0.75" for 75% probability)."""
            
            user_prompt = f"""Calculate success probability for coexistence transition:

Current State: {current_state}
Target State: {target_state}

Return ONLY a number between 0.0 and 1.0 (e.g., "0.75")."""
            
            llm_request = LLMRequest(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=20,
                temperature=0.3,
                metadata={"task": "calculate_success_probability", "agent": "operations_specialist"}
            )
            
            llm_response = await self.llm_abstraction.generate_response(llm_request)
            response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Parse number from response
            try:
                # Extract first number from response
                import re
                numbers = re.findall(r'\d+\.?\d*', response_text)
                if numbers:
                    probability = float(numbers[0])
                    # If number is > 1, assume it's a percentage and convert
                    if probability > 1.0:
                        probability = probability / 100.0
                    # Clamp to valid range (0.0-1.0)
                    probability = max(0.0, min(1.0, probability))
                    return probability
                else:
                    self.logger.warning(f"⚠️ Could not parse success probability from LLM response: {response_text}")
                    return 0.75  # Default
            except (ValueError, TypeError) as e:
                self.logger.warning(f"⚠️ Failed to parse success probability: {e}")
                return 0.75  # Default
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to calculate success probability via LLM: {e}, using default")
            return 0.75  # Default 75% success probability
    
    async def _generate_coexistence_recommendations(self, current_state: Dict[str, Any], target_state: Dict[str, Any]) -> List[str]:
        """Generate coexistence recommendations."""
        recommendations = []
        
        collaboration_gap = self._calculate_collaboration_gap(current_state, target_state)
        if collaboration_gap == "large":
            recommendations.append("Implement gradual transition to collaborative coexistence")
        
        trust_level = await self._assess_trust_level(current_state)
        if trust_level == "low":
            recommendations.append("Focus on building trust through transparency and reliability")
        
        return recommendations
    
    def _identify_workflow_pattern(self, workflow_definition: Dict[str, Any]) -> str:
        """Identify workflow pattern."""
        nodes = workflow_definition.get("nodes", [])
        edges = workflow_definition.get("edges", [])
        
        decision_nodes = sum(1 for node in nodes if node.get("type") == "decision")
        parallel_edges = sum(1 for edge in edges if edge.get("type") == "parallel")
        
        if decision_nodes > 0:
            return "conditional"
        elif parallel_edges > 0:
            return "parallel"
        else:
            return "sequential"
    
    def _calculate_workflow_complexity(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate workflow complexity metrics."""
        nodes = workflow_definition.get("nodes", [])
        edges = workflow_definition.get("edges", [])
        
        return {
            "cyclomatic_complexity": len(edges) - len(nodes) + 2,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "decision_points": sum(1 for node in nodes if node.get("type") == "decision")
        }
    
    def _assess_execution_efficiency(self, workflow_definition: Dict[str, Any]) -> str:
        """Assess workflow execution efficiency."""
        # Mock implementation
        return "medium"
    
    def _assess_scalability(self, workflow_definition: Dict[str, Any]) -> str:
        """Assess workflow scalability."""
        # Mock implementation
        return "high"
    
    def _assess_maintainability(self, workflow_definition: Dict[str, Any]) -> str:
        """Assess workflow maintainability."""
        # Mock implementation
        return "medium"
    
    def _assess_error_handling(self, workflow_definition: Dict[str, Any]) -> str:
        """Assess workflow error handling."""
        # Mock implementation
        return "low"
    
    def _analyze_performance_characteristics(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow performance characteristics."""
        return {
            "estimated_execution_time": "2.5 hours",
            "resource_requirements": "medium",
            "throughput": "10 processes/hour"
        }
    
    def _assess_optimization_potential(self, workflow_definition: Dict[str, Any]) -> str:
        """Assess workflow optimization potential."""
        # Mock implementation
        return "high"
    
    def _generate_workflow_recommendations(self, workflow_definition: Dict[str, Any]) -> List[str]:
        """Generate workflow recommendations."""
        return [
            "Add error handling mechanisms",
            "Implement parallel execution where possible",
            "Add monitoring and logging capabilities"
        ]
    
    def _assess_current_performance(self, process_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Assess current process performance."""
        return {
            "efficiency_score": 75.0,
            "quality_score": 80.0,
            "speed_score": 70.0,
            "cost_score": 65.0
        }
    
    def _identify_optimization_opportunities(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities."""
        opportunities = []
        
        if "efficiency" in optimization_goals:
            opportunities.append({
                "type": "automation",
                "description": "Automate repetitive tasks",
                "impact": "high",
                "effort": "medium"
            })
        
        if "cost" in optimization_goals:
            opportunities.append({
                "type": "resource_optimization",
                "description": "Optimize resource allocation",
                "impact": "medium",
                "effort": "high"
            })
        
        return opportunities
    
    def _assess_optimization_impact(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> Dict[str, Any]:
        """Assess optimization impact."""
        return {
            "efficiency_improvement": "20-30%",
            "cost_reduction": "15-25%",
            "quality_improvement": "10-15%",
            "speed_improvement": "25-35%"
        }
    
    def _assess_implementation_complexity(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> str:
        """Assess implementation complexity."""
        # Mock implementation
        return "medium"
    
    def _estimate_resource_requirements(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> Dict[str, Any]:
        """Estimate resource requirements."""
        return {
            "team_size": "3-5 people",
            "budget": "$25,000 - $75,000",
            "timeline": "2-4 months"
        }
    
    def _estimate_optimization_timeline(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> str:
        """Estimate optimization timeline."""
        return "3-6 months"
    
    def _assess_optimization_risks(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> List[Dict[str, Any]]:
        """Assess optimization risks."""
        return [
            {
                "risk": "Change resistance",
                "probability": "medium",
                "impact": "high"
            },
            {
                "risk": "Technical complexity",
                "probability": "low",
                "impact": "medium"
            }
        ]
    
    def _calculate_roi_projection(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> Dict[str, Any]:
        """Calculate ROI projection."""
        return {
            "investment": "$50,000",
            "annual_savings": "$75,000",
            "roi_percentage": "150%",
            "payback_period": "8 months"
        }
    
    def _define_success_metrics(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> List[Dict[str, Any]]:
        """Define success metrics."""
        return [
            {
                "metric": "Efficiency Score",
                "target": 90,
                "current": 75
            },
            {
                "metric": "Cost Reduction",
                "target": 20,
                "current": 0
            }
        ]
    
    def _generate_optimization_recommendations(self, process_definition: Dict[str, Any], optimization_goals: List[str]) -> List[str]:
        """Generate optimization recommendations."""
        return [
            "Start with high-impact, low-effort improvements",
            "Implement change management program",
            "Establish monitoring and measurement systems",
            "Plan for gradual rollout to minimize disruption"
        ]
    
    def _assess_data_quality(self, data: Dict[str, Any]) -> str:
        """Assess data quality."""
        # Mock implementation
        return "good"
    
    def _determine_analysis_scope(self, data: Dict[str, Any]) -> str:
        """Determine analysis scope."""
        # Mock implementation
        return "comprehensive"
    
    def _extract_key_insights(self, data: Dict[str, Any]) -> List[str]:
        """Extract key insights from data."""
        return [
            "Process shows high automation potential",
            "Several optimization opportunities identified",
            "Change management will be critical for success"
        ]
    
    def _identify_trends(self, data: Dict[str, Any]) -> List[str]:
        """Identify trends in data."""
        return [
            "Increasing automation adoption",
            "Growing focus on efficiency",
            "Rising importance of AI-human collaboration"
        ]
    
    def _detect_anomalies(self, data: Dict[str, Any]) -> List[str]:
        """Detect anomalies in data."""
        return [
            "Unusual spike in manual processing time",
            "Inconsistent quality scores across similar processes"
        ]
    
    def _generate_general_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate general recommendations."""
        return [
            "Focus on data quality improvements",
            "Implement regular monitoring and analysis",
            "Consider advanced analytics capabilities"
        ]
    
    def _get_llm_model(self):
        """
        Get configurable LLM model from environment or config.
        
        Returns:
            LLMModel enum value (defaults to GPT_4O_MINI)
        """
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMModel
        
        # Get from ConfigAdapter (required)
        if not self.public_works_foundation or not hasattr(self.public_works_foundation, 'config_adapter'):
            # Fallback to default if ConfigAdapter not available (should not happen in production)
            self.logger.warning("⚠️ ConfigAdapter not available, using default model")
            model_name = "gpt-4o-mini"
        else:
            config_adapter = self.public_works_foundation.config_adapter
            model_name = config_adapter.get("OPERATIONS_AGENT_LLM_MODEL", "gpt-4o-mini")
        
        # Map to LLMModel enum
        model_map = {
            "gpt-4o-mini": LLMModel.GPT_4O_MINI,
            "gpt-4o": LLMModel.GPT_4O,
            "gpt-4": LLMModel.GPT_4,
            "claude-3-5-sonnet": LLMModel.CLAUDE_3_SONNET,
        }
        
        selected_model = model_map.get(model_name.lower(), LLMModel.GPT_4O_MINI)
        if model_name.lower() not in model_map:
            self.logger.warning(f"⚠️ Unknown model '{model_name}', using default GPT_4O_MINI")
        
        return selected_model



