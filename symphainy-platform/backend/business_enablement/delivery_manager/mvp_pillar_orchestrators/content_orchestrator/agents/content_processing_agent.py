#!/usr/bin/env python3
"""
Content Processing Agent - Refactored

Specialist agent for the Content Pillar Service that uses MCP server tools
for autonomous content processing and optimization.

WHAT (Business Enablement Role): I autonomously process and optimize content
HOW (Smart City Role): I use MCP server tools for autonomous processing
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from utilities import UserContext
from backend.business_enablement.protocols.business_specialist_agent_protocol import BusinessSpecialistAgentBase, SpecialistCapability
from foundations.di_container.di_container_service import DIContainerService


class ContentProcessingAgent(BusinessSpecialistAgentBase):
    """
    Content Processing Agent - Refactored
    
    Specialist agent that autonomously processes and optimizes content using MCP server tools.
    Provides advanced content management capabilities through direct MCP tool access.
    
    Uses full Agentic SDK via Agentic Foundation factory.
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
        Initialize Content Processing Agent with full SDK dependencies.
        
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
            specialist_capability=kwargs.get("specialist_capability", SpecialistCapability.CONTENT_PROCESSING),
            **{k: v for k, v in kwargs.items() if k != "specialist_capability"}
        )
        
        self.service_name = agent_name
        
        # Orchestrator (set by orchestrator for MCP server access)
        self.content_orchestrator = None
        self.orchestrator = None  # Alias for consistency with other agents
        
        # MCP server (optional, for tool access)
        self.mcp_server = None
        
        # Processing state
        self.processing_queue: List[Dict[str, Any]] = []
        self.processing_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
    
    async def initialize(self):
        """
        Initialize Content Processing Agent.
        
        Includes full utility usage:
        - Telemetry tracking (via AgentBase utility methods)
        - Error handling with audit (via AgentBase utility methods)
        - Health metrics (via AgentBase utility methods)
        
        Note: Factory handles Curator registration (Agentic Foundation owns agent registry).
        """
        try:
            # Start telemetry tracking (using AgentBase utility method)
            await self.log_operation_with_telemetry("initialize_start", success=True, details={
                "agent_name": self.service_name
            })
            
            # Call parent initialize (BusinessSpecialistAgentBase)
            await super().initialize()
            
            # Discover orchestrator via Curator (optional, agent can work independently)
            if self.curator_foundation:
                try:
                    registered_services = await self.curator_foundation.get_registered_services()
                    services_dict = registered_services.get("services", {})
                    if "ContentAnalysisOrchestratorService" in services_dict:
                        service_info = services_dict["ContentAnalysisOrchestratorService"]
                        self.content_orchestrator = service_info.get("service_instance")
                        self.logger.info("✅ Discovered ContentAnalysisOrchestrator")
                except Exception as e:
                    self.logger.warning(f"⚠️ ContentAnalysisOrchestrator not available: {e}")
            
            # REMOVED: Self-registration with Curator
            # Factory handles registration (Agentic Foundation owns agent registry)
            
            self.is_initialized = True
            
            # Record health metric (success) - using AgentBase utility method
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.service_name
            })
            
            # End telemetry tracking - using AgentBase utility method
            await self.log_operation_with_telemetry("initialize_complete", success=True, details={
                "agent_name": self.service_name
            })
            
            self.logger.info(f"✅ {self.service_name} initialization complete")
            return True
        
        except Exception as e:
            # Error handling with audit - using AgentBase utility method
            await self.handle_error_with_audit(e, "initialize", details={
                "agent_name": self.service_name
            })
            
            # Record health metric (failure) - using AgentBase utility method
            await self.record_health_metric("initialization_failed", 1.0, {
                "agent_name": self.service_name,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure - using AgentBase utility method
            await self.log_operation_with_telemetry("initialize_complete", success=False, details={
                "agent_name": self.service_name,
                "error": str(e)
            })
            
            self.is_initialized = False
            return False
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference for MCP server access."""
        self.orchestrator = orchestrator
        self.content_orchestrator = orchestrator  # Alias for backwards compatibility
        self.logger.info("✅ Orchestrator reference set for MCP tool access")
    
    async def execute_business_capability(self, capability_name: str, params: Dict[str, Any], 
                                        user_context: UserContext) -> Dict[str, Any]:
        """
        Execute a specific business capability using MCP server tools.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            capability_name: Name of the capability to execute
            params: Parameters for the capability
            user_context: User context for authorization and tenant validation
            
        Returns:
            Capability execution result
        """
        try:
            # Start telemetry tracking - using AgentBase utility method
            await self.log_operation_with_telemetry("execute_business_capability_start", success=True, details={
                "capability_name": capability_name,
                "agent_name": self.service_name
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    # Convert UserContext to dict for security check
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, f"capability_{capability_name}", "execute"):
                        # Record health metric (access denied) - using AgentBase utility method
                        await self.record_health_metric("execute_business_capability_access_denied", 1.0, {
                            "capability_name": capability_name
                        })
                        # End telemetry tracking - using AgentBase utility method
                        await self.log_operation_with_telemetry("execute_business_capability_complete", success=False, details={
                            "capability_name": capability_name,
                            "status": "access_denied"
                        })
                        raise PermissionError(f"Access denied: insufficient permissions to execute capability '{capability_name}'")
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
                            # Record health metric (tenant denied) - using AgentBase utility method
                            await self.record_health_metric("execute_business_capability_tenant_denied", 1.0, {
                                "capability_name": capability_name,
                                "tenant_id": tenant_id
                            })
                            # End telemetry tracking - using AgentBase utility method
                            await self.log_operation_with_telemetry("execute_business_capability_complete", success=False, details={
                                "capability_name": capability_name,
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            
            # Map capability names to MCP tool names
            capability_to_tool = {
                "process_file": "process_file",
                "optimize_content": "optimize_content",
                "extract_data": "extract_data",
                "convert_format": "convert_format",
                "assess_quality": "assess_quality",
                "batch_process": "batch_process"
            }
            
            tool_name = capability_to_tool.get(capability_name)
            if not tool_name:
                # Record health metric (capability not found) - using AgentBase utility method
                await self.record_health_metric("execute_business_capability_not_found", 1.0, {
                    "capability_name": capability_name
                })
                # End telemetry tracking - using AgentBase utility method
                await self.log_operation_with_telemetry("execute_business_capability_complete", success=False, details={
                    "capability_name": capability_name,
                    "status": "not_found"
                })
                return {
                    "success": False,
                    "message": f"Capability '{capability_name}' not supported",
                    "error_details": {"capability_name": capability_name}
                }
            
            # Execute MCP tool
            result = await self.mcp_server.execute_tool(tool_name, params, user_context)
            
            if result.get("success"):
                # Add to processing history for tracking
                self.processing_history.append({
                    "capability": capability_name,
                    "tool": tool_name,
                    "params": params,
                    "result": result,
                    "executed_at": datetime.utcnow().isoformat()
                })
                
                # Record health metric (success) - using AgentBase utility method
                await self.record_health_metric("execute_business_capability_success", 1.0, {
                    "capability_name": capability_name
                })
                
                # End telemetry tracking - using AgentBase utility method
                await self.log_operation_with_telemetry("execute_business_capability_complete", success=True, details={
                    "capability_name": capability_name,
                    "status": "success"
                })
                
                return {
                    "success": True,
                    "message": f"Capability '{capability_name}' executed successfully",
                    "result": result.get("result", result)
                }
            else:
                # Record health metric (failure) - using AgentBase utility method
                await self.record_health_metric("execute_business_capability_failed", 1.0, {
                    "capability_name": capability_name,
                    "error": result.get("error", "unknown")
                })
                
                # End telemetry tracking - using AgentBase utility method
                await self.log_operation_with_telemetry("execute_business_capability_complete", success=False, details={
                    "capability_name": capability_name,
                    "status": "failed"
                })
                
                return {
                    "success": False,
                    "message": f"Capability '{capability_name}' failed: {result.get('error', 'Unknown error')}",
                    "error_details": result
                }
                
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit - using AgentBase utility method
            await self.handle_error_with_audit(e, "execute_business_capability", details={
                "capability_name": capability_name
            })
            
            # Record health metric (failure) - using AgentBase utility method
            await self.record_health_metric("execute_business_capability_error", 1.0, {
                "capability_name": capability_name,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure - using AgentBase utility method
            await self.log_operation_with_telemetry("execute_business_capability_complete", success=False, details={
                "capability_name": capability_name,
                "status": "error",
                "error": str(e)
            })
            
            return {
                "success": False,
                "message": f"Failed to execute capability {capability_name}: {str(e)}",
                "error_details": {"error": str(e)}
            }
    
    async def get_supported_capabilities(self, user_context: UserContext = None) -> List[str]:
        """
        Get a list of business capabilities supported by this specialist agent.
        
        Args:
            user_context: User context for authorization
            
        Returns:
            List of supported capabilities
        """
        try:
            return self.capabilities
        except Exception as e:
            self.logger.error(f"❌ Failed to get supported capabilities: {e}")
            return []
    
    async def analyze_situation(self, situation_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Analyze a given content processing situation using MCP server tools.
        
        Args:
            situation_data: Data about the content processing situation
            user_context: User context for authorization
            
        Returns:
            Analysis and recommendations
        """
        try:
            situation_type = situation_data.get("type", "content_analysis")
            
            # Use MCP server for situation analysis
            result = await self.mcp_server.execute_tool("analyze_content_situation", {
                "situation_data": situation_data,
                "analysis_type": situation_type
            }, user_context)
            
            if result.get("success"):
                return {
                    "success": True,
                    "analysis": result.get("result", result),
                    "message": "Content situation analyzed successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Situation analysis failed: {result.get('error', 'Unknown error')}",
                    "error_details": result
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze situation: {e}")
            return {
                "success": False,
                "message": f"Situation analysis failed: {str(e)}",
                "error_details": {"error": str(e)}
            }
    
    async def get_processing_metrics(self, user_context: UserContext) -> Dict[str, Any]:
        """
        Get processing performance metrics using MCP server tools.
        
        Args:
            user_context: User context for authorization
            
        Returns:
            Processing metrics
        """
        try:
            # Use MCP server for metrics retrieval
            result = await self.mcp_server.execute_tool("get_processing_metrics", {
                "time_period": "24h"
            }, user_context)
            
            if result.get("success"):
                return {
                    "success": True,
                    "metrics": result.get("result", result),
                    "message": "Processing metrics retrieved successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Metrics retrieval failed: {result.get('error', 'Unknown error')}",
                    "error_details": result
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get processing metrics: {e}")
            return {
                "success": False,
                "message": f"Metrics retrieval failed: {str(e)}",
                "error_details": {"error": str(e)}
            }
    
    async def process_file_autonomous(self, file_id: str, user_context: UserContext, 
                                    processing_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Autonomously process a file with intelligent decision-making.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            file_id: ID of the file to process
            user_context: User context for authorization and tenant validation
            processing_options: Optional processing options
            
        Returns:
            Processing result with autonomous decisions
        """
        try:
            # Start telemetry tracking - using AgentBase utility method
            await self.log_operation_with_telemetry("process_file_autonomous_start", success=True, details={
                "file_id": file_id,
                "agent_name": self.service_name
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "file_processing", "execute"):
                        # Record health metric (access denied) - using AgentBase utility method
                        await self.record_health_metric("process_file_autonomous_access_denied", 1.0, {
                            "file_id": file_id
                        })
                        # End telemetry tracking - using AgentBase utility method
                        await self.log_operation_with_telemetry("process_file_autonomous_complete", success=False, details={
                            "file_id": file_id,
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions to process file")
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
                            # Record health metric (tenant denied) - using AgentBase utility method
                            await self.record_health_metric("process_file_autonomous_tenant_denied", 1.0, {
                                "file_id": file_id,
                                "tenant_id": tenant_id
                            })
                            # End telemetry tracking - using AgentBase utility method
                            await self.log_operation_with_telemetry("process_file_autonomous_complete", success=False, details={
                                "file_id": file_id,
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            # Step 1: Analyze the file to determine optimal processing strategy
            analysis_result = await self.analyze_situation({
                "type": "content_analysis",
                "content_id": file_id,
                "file_id": file_id
            }, user_context)
            
            if not analysis_result.get("success"):
                return analysis_result
            
            # Step 2: Determine processing strategy based on analysis
            analysis = analysis_result.get("analysis", {})
            findings = analysis.get("findings", {})
            
            # Autonomous decision-making based on file characteristics
            processing_type = "standard"
            if findings.get("processing_complexity") == "high":
                processing_type = "advanced"
            elif findings.get("file_size", "").endswith("MB") and float(findings.get("file_size", "0MB").replace("MB", "")) > 10:
                processing_type = "batch_optimized"
            
            # Step 3: Execute processing with autonomous decisions
            processing_result = await self.execute_business_capability("process_file", {
                "file_id": file_id,
                "processing_type": processing_type,
                "options": processing_options or {}
            }, user_context)
            
            if not processing_result.get("success"):
                return processing_result
            
            # Step 4: Post-processing optimization if needed
            if findings.get("quality_score", 0) < 0.8:
                optimization_result = await self.execute_business_capability("optimize_content", {
                    "content_id": file_id,
                    "optimization_goals": ["quality", "efficiency"]
                }, user_context)
                
                if optimization_result.get("success"):
                    processing_result["optimization"] = optimization_result.get("result")
            
            # Step 5: Quality assessment
            quality_result = await self.execute_business_capability("assess_quality", {
                "content_id": file_id,
                "assessment_criteria": ["completeness", "accuracy", "consistency"]
            }, user_context)
            
            if quality_result.get("success"):
                processing_result["quality_assessment"] = quality_result.get("result")
            
            # Record health metric (success) - using AgentBase utility method
            await self.record_health_metric("process_file_autonomous_success", 1.0, {
                "file_id": file_id,
                "processing_type": processing_type
            })
            
            # End telemetry tracking - using AgentBase utility method
            await self.log_operation_with_telemetry("process_file_autonomous_complete", success=True, details={
                "file_id": file_id,
                "status": "success"
            })
            
            return {
                "success": True,
                "message": f"File {file_id} processed autonomously",
                "autonomous_decisions": {
                    "processing_type": processing_type,
                    "optimization_applied": findings.get("quality_score", 0) < 0.8,
                    "quality_assessed": True
                },
                "processing_result": processing_result,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit - using AgentBase utility method
            await self.handle_error_with_audit(e, "process_file_autonomous", details={
                "file_id": file_id
            })
            
            # Record health metric (failure) - using AgentBase utility method
            await self.record_health_metric("process_file_autonomous_error", 1.0, {
                "file_id": file_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure - using AgentBase utility method
            await self.log_operation_with_telemetry("process_file_autonomous_complete", success=False, details={
                "file_id": file_id,
                "status": "error",
                "error": str(e)
            })
            
            return {
                "success": False,
                "message": f"Autonomous file processing failed: {str(e)}",
                "error_details": {"error": str(e)}
            }
    
    async def batch_process_autonomous(self, file_ids: List[str], user_context: UserContext,
                                     batch_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Autonomously process multiple files with intelligent batching.
        
        Args:
            file_ids: List of file IDs to process
            user_context: User context for authorization
            batch_options: Optional batch processing options
            
        Returns:
            Batch processing result with autonomous decisions
        """
        try:
            # Step 1: Analyze batch for optimal processing strategy
            batch_analysis = {
                "type": "batch_analysis",
                "file_count": len(file_ids),
                "file_ids": file_ids
            }
            
            analysis_result = await self.analyze_situation(batch_analysis, user_context)
            
            # Step 2: Determine batch processing strategy
            batch_size = 5  # Default batch size
            if len(file_ids) > 20:
                batch_size = 10  # Larger batches for many files
            elif len(file_ids) < 5:
                batch_size = len(file_ids)  # Process all at once for small batches
            
            # Step 3: Execute batch processing
            batch_result = await self.execute_business_capability("batch_process", {
                "file_ids": file_ids,
                "processing_type": "batch_optimized",
                "batch_options": {
                    "batch_size": batch_size,
                    "parallel_processing": True,
                    **(batch_options or {})
                }
            }, user_context)
            
            if not batch_result.get("success"):
                return batch_result
            
            # Step 4: Post-batch analysis and recommendations
            metrics_result = await self.get_processing_metrics(user_context)
            
            return {
                "success": True,
                "message": f"Batch processing completed for {len(file_ids)} files",
                "autonomous_decisions": {
                    "batch_size": batch_size,
                    "parallel_processing": True,
                    "optimization_strategy": "batch_optimized"
                },
                "batch_result": batch_result,
                "processing_metrics": metrics_result.get("metrics", {}),
                "batch_processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Autonomous batch processing failed: {e}")
            return {
                "success": False,
                "message": f"Autonomous batch processing failed: {str(e)}",
                "error_details": {"error": str(e)}
            }
    
    def get_mcp_server_info(self) -> Dict[str, Any]:
        """Get information about the associated MCP server."""
        try:
            return self.mcp_server.get_server_info()
        except Exception as e:
            self.logger.error(f"❌ Failed to get MCP server info: {e}")
            return {"error": str(e)}
    
    def get_mcp_server_health(self) -> Dict[str, Any]:
        """Get health status of the associated MCP server."""
        try:
            return self.mcp_server.get_health()
        except Exception as e:
            self.logger.error(f"❌ Failed to get MCP server health: {e}")
            return {"error": str(e)}
    
    def get_mcp_server_tools(self) -> List[str]:
        """Get list of available MCP server tools."""
        try:
            return self.mcp_server.get_tool_list()
        except Exception as e:
            self.logger.error(f"❌ Failed to get MCP server tools: {e}")
            return []
    
    # ========================================================================
    # POST-PARSING ENHANCEMENT METHODS (Using MCP Tools)
    # ========================================================================
    
    async def enhance_metadata_extraction(
        self,
        parsed_result: Dict[str, Any],
        file_id: str
    ) -> Dict[str, Any]:
        """
        Enhance metadata extraction from parsed results using MCP tools.
        
        POST-PARSING ONLY: Works with parsed results in AI-friendly formats.
        
        Args:
            parsed_result: Parsed content dictionary
            file_id: File identifier
        
        Returns:
            Enhanced metadata
        """
        try:
            self.logger.info(f"🤖 Enhancing metadata extraction for file: {file_id}")
            
            # Use MCP tool to get analysis (orchestrator calls enabling services)
            if self.orchestrator and hasattr(self.orchestrator, 'mcp_server'):
                mcp_server = self.orchestrator.mcp_server
                try:
                    analysis = await mcp_server.execute_tool(
                        "analyze_document_tool",
                        {
                            "document_id": file_id,
                            "analysis_types": ["metadata", "entities"]
                        }
                    )
                    # Agent enhances with reasoning
                    enhanced = self._apply_agent_reasoning_to_metadata(analysis, parsed_result)
                    return enhanced
                except Exception as mcp_error:
                    self.logger.warning(f"⚠️ MCP tool enhancement failed: {mcp_error}, using parsed result")
            
            # Fallback: Use parsed result directly
            return {
                "success": True,
                "metadata": parsed_result.get("metadata", {}),
                "enhanced": False,
                "note": "MCP server not available"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Metadata enhancement failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def enhance_content_insights(
        self,
        parsed_result: Dict[str, Any],
        file_id: str
    ) -> Dict[str, Any]:
        """
        Enhance content insights from parsed results using MCP tools.
        
        POST-PARSING ONLY: Works with parsed results in AI-friendly formats.
        
        Args:
            parsed_result: Parsed content dictionary
            file_id: File identifier
        
        Returns:
            Enhanced insights
        """
        try:
            self.logger.info(f"🤖 Enhancing content insights for file: {file_id}")
            
            # Use MCP tool to get analysis (orchestrator calls enabling services)
            if self.orchestrator and hasattr(self.orchestrator, 'mcp_server'):
                mcp_server = self.orchestrator.mcp_server
                try:
                    analysis = await mcp_server.execute_tool(
                        "analyze_document_tool",
                        {
                            "document_id": file_id,
                            "analysis_types": ["structure", "entities", "semantic"]
                        }
                    )
                    # Agent enhances with reasoning
                    enhanced = self._apply_agent_reasoning_to_insights(analysis, parsed_result)
                    return enhanced
                except Exception as mcp_error:
                    self.logger.warning(f"⚠️ MCP tool enhancement failed: {mcp_error}, using parsed result")
            
            # Fallback: Use parsed result directly
            return {
                "success": True,
                "insights": parsed_result.get("insights", {}),
                "enhanced": False,
                "note": "MCP server not available"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Content insights enhancement failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def recommend_format_optimization(
        self,
        parsed_result: Dict[str, Any],
        file_id: str
    ) -> Dict[str, Any]:
        """
        Recommend format optimization based on content using MCP tools.
        
        POST-PARSING ONLY: Works with parsed results in AI-friendly formats.
        
        Args:
            parsed_result: Parsed content dictionary
            file_id: File identifier
        
        Returns:
            Format recommendation
        """
        try:
            self.logger.info(f"🤖 Recommending format optimization for file: {file_id}")
            
            # Use MCP tool to get format recommendation (orchestrator calls FormatComposerService)
            if self.orchestrator and hasattr(self.orchestrator, 'mcp_server'):
                mcp_server = self.orchestrator.mcp_server
                try:
                    # Analyze content structure
                    analysis = await mcp_server.execute_tool(
                        "analyze_document_tool",
                        {
                            "document_id": file_id,
                            "analysis_types": ["structure"]
                        }
                    )
                    # Agent recommends format based on content structure
                    recommendation = self._recommend_format_from_structure(analysis, parsed_result)
                    return recommendation
                except Exception as mcp_error:
                    self.logger.warning(f"⚠️ MCP tool recommendation failed: {mcp_error}")
            
            # Fallback: Basic recommendation
            return {
                "success": True,
                "recommended_format": "json_chunks",  # Default
                "reason": "Unable to analyze structure",
                "note": "MCP server not available"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Format recommendation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _apply_agent_reasoning_to_metadata(
        self,
        analysis: Dict[str, Any],
        parsed_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply agent reasoning to enhance metadata."""
        metadata = parsed_result.get("metadata", {})
        analysis_metadata = analysis.get("metadata", {})
        
        # Merge and enhance
        enhanced_metadata = {**metadata, **analysis_metadata}
        
        # Add agent-generated insights
        enhanced_metadata["agent_enhanced"] = True
        enhanced_metadata["enhancement_timestamp"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "metadata": enhanced_metadata,
            "enhanced": True
        }
    
    def _apply_agent_reasoning_to_insights(
        self,
        analysis: Dict[str, Any],
        parsed_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply agent reasoning to enhance insights."""
        insights = parsed_result.get("insights", {})
        analysis_insights = analysis.get("insights", {})
        
        # Merge and enhance
        enhanced_insights = {**insights, **analysis_insights}
        
        # Add agent-generated insights
        enhanced_insights["agent_enhanced"] = True
        enhanced_insights["enhancement_timestamp"] = datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "insights": enhanced_insights,
            "enhanced": True
        }
    
    def _recommend_format_from_structure(
        self,
        analysis: Dict[str, Any],
        parsed_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Recommend format based on content structure."""
        structure = analysis.get("structure", {})
        content_type = structure.get("content_type", "unstructured")
        
        # Format recommendation logic
        if content_type == "structured" or structure.get("has_tables"):
            recommended_format = "parquet"
            reason = "Structured/tabular data detected"
        elif content_type == "semi_structured":
            recommended_format = "json_structured"
            reason = "Semi-structured data detected"
        else:
            recommended_format = "json_chunks"
            reason = "Unstructured text content"
        
        return {
            "success": True,
            "recommended_format": recommended_format,
            "reason": reason,
            "content_type": content_type
        }
