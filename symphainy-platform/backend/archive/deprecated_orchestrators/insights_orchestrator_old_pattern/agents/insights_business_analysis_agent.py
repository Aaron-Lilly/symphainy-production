#!/usr/bin/env python3
"""
Insights Business Analysis Agent

Business Analysis Agent for Insights Pillar.

Uses OpenAI LLM (not HF) for business analysis.
For structured data: Uses EDA tools, then interprets with OpenAI LLM.
For unstructured data: Reviews embeddings directly with OpenAI LLM.

WHAT (Business Enablement Role): I provide business analysis and insights
HOW (Agent): I use EDA tools for structured data, review embeddings for unstructured data, and interpret with OpenAI LLM
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from utilities import UserContext
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase


class InsightsBusinessAnalysisAgent(AgentBase):
    """
    Business Analysis Agent for Insights Pillar.
    
    Uses OpenAI LLM (not HF) for business analysis.
    For structured data: Uses EDA tools, then interprets with OpenAI LLM.
    For unstructured data: Reviews embeddings directly with OpenAI LLM.
    
    Key Features:
    - Deterministic EDA results (same input = same output)
    - Consistent LLM interpretation (same EDA = same interpretation)
    - Works with semantic embeddings (not raw parsed data)
    - Uses agentic correlation tracking
    """
    
    def __init__(
        self,
        agent_name: str,
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
        Initialize Insights Business Analysis Agent with full SDK dependencies.
        
        This agent is created via Agentic Foundation factory - all dependencies
        are provided by the factory.
        """
        agent_id = kwargs.get("agent_id", agent_name.lower().replace(" ", "_"))
        agent_description = kwargs.get(
            "agent_description",
            "Business analysis agent that uses EDA tools and OpenAI LLM for insights"
        )
        
        super().__init__(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_description=agent_description,
            capabilities=capabilities,
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            **kwargs
        )
        
        self.service_name = agent_name
        self.insights_orchestrator = None
        self.orchestrator = None  # Set by orchestrator for MCP tool access
    
    async def initialize(self):
        """
        Initialize Insights Business Analysis Agent.
        
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
            
            # Discover orchestrator via Curator (optional, agent can work independently)
            if self.curator_foundation:
                try:
                    registered_services = await self.curator_foundation.get_registered_services()
                    services_dict = registered_services.get("services", {})
                    if "InsightsOrchestratorService" in services_dict:
                        service_info = services_dict["InsightsOrchestratorService"]
                        self.insights_orchestrator = service_info.get("service_instance")
                        self.orchestrator = self.insights_orchestrator
                        self.logger.info("✅ Discovered InsightsOrchestrator")
                except Exception as e:
                    await self.handle_error_with_audit(
                        e, "orchestrator_discovery",
                        details={"orchestrator": "InsightsOrchestrator"}
                    )
                    self.logger.warning(f"⚠️ InsightsOrchestrator not available: {e}")
            
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
    
    async def analyze_structured_data(
        self,
        content_id: str,
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze structured data using EDA tools + LLM interpretation.
        
        Pattern:
        1. Get semantic embeddings (schema/metadata)
        2. Run EDA analysis tools (deterministic)
        3. LLM interprets EDA results (consistent - same EDA = same interpretation)
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with analysis results:
            {
                "success": bool,
                "content_id": str,
                "eda_results": {...},  # Deterministic
                "interpretation": {...},  # Consistent (same EDA = same interpretation)
                "embeddings_used": List[str]
            }
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "analyze_structured_data_start",
                success=True,
                details={"content_id": content_id}
            )
            
            # Convert UserContext to dict if needed
            user_context_dict = self._convert_user_context(user_context)
            
            # Step 1: Get semantic embeddings for schema via Data Solution Orchestrator (Phase 6)
            if self.orchestrator and hasattr(self.orchestrator, 'get_semantic_embeddings_via_data_solution'):
                embeddings = await self.orchestrator.get_semantic_embeddings_via_data_solution(
                    content_id=content_id,
                    embedding_type="schema",
                    user_context=user_context_dict
                )
            else:
                # Fallback: try semantic data abstraction (for backward compatibility)
                semantic_data = await self.get_business_abstraction("semantic_data")
                if semantic_data:
                    embeddings = await semantic_data.get_semantic_embeddings(
                        content_id=content_id,
                        filters={"embedding_type": "schema"},
                        user_context=user_context_dict
                    )
                else:
                    return {
                        "success": False,
                        "error": "Orchestrator and semantic data abstraction not available",
                        "content_id": content_id
                    }
            
            if not embeddings:
                return {
                    "success": False,
                    "error": "No schema embeddings found",
                    "content_id": content_id
                }
            
            # Step 2: Run EDA analysis tools (via MCP tool)
            eda_results = await self._call_eda_analysis_tool(
                content_id=content_id,
                user_context=user_context_dict
            )
            
            if not eda_results.get("success"):
                return {
                    "success": False,
                    "error": "EDA analysis failed",
                    "eda_error": eda_results.get("error"),
                    "content_id": content_id
                }
            
            # Step 3: LLM interprets EDA results (OpenAI, not HF)
            # Use agentic correlation tracking for LLM call
            interpretation = await self._interpret_eda_results_with_llm(
                eda_results=eda_results.get("eda_results", {}),
                schema_info=eda_results.get("schema_info", {}),
                user_context=user_context_dict
            )
            
            result = {
                "success": True,
                "content_id": content_id,
                "eda_results": eda_results.get("eda_results"),  # Deterministic
                "interpretation": interpretation,  # Consistent (same EDA = same interpretation)
                "embeddings_used": [emb.get("_key") or emb.get("id") for emb in embeddings if emb.get("_key") or emb.get("id")]
            }
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "analyze_structured_data_complete",
                success=True,
                details={"content_id": content_id}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e, "analyze_structured_data",
                details={"content_id": content_id}
            )
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "analyze_structured_data_complete",
                success=False,
                details={"content_id": content_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ Structured data analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }
    
    async def analyze_unstructured_data(
        self,
        content_id: str,
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze unstructured data by reviewing embeddings directly.
        
        Pattern:
        1. Get semantic embeddings (chunk embeddings)
        2. LLM reviews embeddings directly
        3. Generates business narrative
        
        Args:
            content_id: Content metadata ID
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with analysis results:
            {
                "success": bool,
                "content_id": str,
                "analysis": {...},
                "embeddings_reviewed": List[str]
            }
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "analyze_unstructured_data_start",
                success=True,
                details={"content_id": content_id}
            )
            
            # Convert UserContext to dict if needed
            user_context_dict = self._convert_user_context(user_context)
            
            # Step 1: Get chunk embeddings via Data Solution Orchestrator (Phase 6)
            if self.orchestrator and hasattr(self.orchestrator, 'get_semantic_embeddings_via_data_solution'):
                embeddings = await self.orchestrator.get_semantic_embeddings_via_data_solution(
                    content_id=content_id,
                    embedding_type="chunk",
                    user_context=user_context_dict
                )
            else:
                # Fallback: try semantic data abstraction (for backward compatibility)
                semantic_data = await self.get_business_abstraction("semantic_data")
                if semantic_data:
                    embeddings = await semantic_data.get_semantic_embeddings(
                        content_id=content_id,
                        filters={"embedding_type": "chunk"},
                        user_context=user_context_dict
                    )
                else:
                    return {
                        "success": False,
                        "error": "Orchestrator and semantic data abstraction not available",
                        "content_id": content_id
                    }
            
            if not embeddings:
                return {
                    "success": False,
                    "error": "No chunk embeddings found",
                    "content_id": content_id
                }
            
            # Step 2: LLM reviews embeddings directly
            # Use agentic correlation tracking for LLM call
            analysis = await self._review_embeddings_with_llm(
                embeddings=embeddings,
                user_context=user_context_dict
            )
            
            result = {
                "success": True,
                "content_id": content_id,
                "analysis": analysis,
                "embeddings_reviewed": [emb.get("_key") or emb.get("id") for emb in embeddings if emb.get("_key") or emb.get("id")]
            }
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "analyze_unstructured_data_complete",
                success=True,
                details={"content_id": content_id}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e, "analyze_unstructured_data",
                details={"content_id": content_id}
            )
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "analyze_unstructured_data_complete",
                success=False,
                details={"content_id": content_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ Unstructured data analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }
    
    async def _call_eda_analysis_tool(
        self,
        content_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call EDA analysis tool via MCP."""
        try:
            # Call tool with tracking
            tool_result = await self._execute_tool_with_tracking(
                tool_name="run_eda_analysis",
                parameters={
                    "content_id": content_id,
                    "analysis_types": ["statistics", "correlations", "distributions", "missing_values"]
                },
                tool_exec_func=self._exec_eda_tool,
                user_context=user_context
            )
            
            return tool_result
            
        except Exception as e:
            self.logger.error(f"❌ EDA tool call failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _exec_eda_tool(self, tool_name: str, parameters: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute EDA tool via MCP client manager."""
        if self.mcp_client_manager:
            try:
                return await self.mcp_client_manager.execute_tool(
                    tool_name=tool_name,
                    parameters=parameters
                )
            except Exception as e:
                self.logger.error(f"❌ MCP tool execution failed: {e}")
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "MCP client manager not available"}
    
    async def _interpret_eda_results_with_llm(
        self,
        eda_results: Dict[str, Any],
        schema_info: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Interpret EDA results using OpenAI LLM."""
        try:
            # Build prompt
            prompt = self._build_interpretation_prompt(eda_results, schema_info)
            
            # Call LLM using simple helper (includes agentic correlation tracking)
            system_message = "You are a business insights analyst. Analyze EDA results and provide business insights, key findings, and recommendations."
            response_text = await self._call_llm_simple(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o",  # Use GPT-4O for better analysis
                max_tokens=2000,
                temperature=0.7,
                user_context=user_context
            )
            
            # Parse response
            return {
                "success": True,
                "insights": response_text,
                "key_findings": self._extract_key_findings({"text": response_text}),
                "recommendations": self._extract_recommendations({"text": response_text})
            }
                
        except Exception as e:
            self.logger.error(f"❌ LLM interpretation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _review_embeddings_with_llm(
        self,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Review embeddings using OpenAI LLM."""
        try:
            # Build prompt
            prompt = self._build_unstructured_prompt(embeddings)
            
            # Call LLM using simple helper (includes agentic correlation tracking)
            system_message = "You are a business insights analyst. Review unstructured content and provide business insights, key themes, and a summary."
            response_text = await self._call_llm_simple(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o",  # Use GPT-4O for better analysis
                max_tokens=2000,
                temperature=0.7,
                user_context=user_context
            )
            
            # Parse response
            return {
                "success": True,
                "analysis": response_text,
                "key_themes": self._extract_key_themes({"text": response_text}),
                "summary": self._extract_summary({"text": response_text})
            }
                
        except Exception as e:
            self.logger.error(f"❌ LLM embedding review failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_interpretation_prompt(
        self,
        eda_results: Dict[str, Any],
        schema_info: Dict[str, Any]
    ) -> str:
        """Build prompt for LLM to interpret EDA results."""
        prompt = f"""
You are a business analyst reviewing exploratory data analysis (EDA) results.

EDA Results:
{json.dumps(eda_results, indent=2)}

Schema Information:
{json.dumps(schema_info, indent=2)}

Please provide:
1. Key insights from the data
2. Business implications
3. Recommendations
4. Potential issues or concerns

Be specific and reference the EDA results in your analysis.
Format your response as JSON with keys: "insights", "implications", "recommendations", "concerns".
"""
        return prompt
    
    def _build_unstructured_prompt(
        self,
        embeddings: List[Dict[str, Any]]
    ) -> str:
        """Build prompt for LLM to review unstructured embeddings."""
        # Extract text from embeddings
        texts = []
        for emb in embeddings[:10]:  # First 10 chunks
            text = emb.get("text") or emb.get("content") or emb.get("chunk_text")
            if text:
                texts.append(text)
        
        prompt = f"""
You are a business analyst reviewing unstructured content.

Content Chunks:
{json.dumps(texts, indent=2)}

Please provide:
1. Key themes and topics
2. Business insights
3. Recommendations
4. Summary

Be specific and reference the content in your analysis.
Format your response as JSON with keys: "themes", "insights", "recommendations", "summary".
"""
        return prompt
    
    def _extract_key_findings(self, response: Dict[str, Any]) -> List[str]:
        """Extract key findings from LLM response."""
        text = response.get("text", response.get("response", ""))
        # Simple extraction - can be enhanced
        if "key findings" in text.lower():
            # Extract findings (simplified)
            return [line.strip() for line in text.split("\n") if line.strip() and "-" in line]
        return []
    
    def _extract_recommendations(self, response: Dict[str, Any]) -> List[str]:
        """Extract recommendations from LLM response."""
        text = response.get("text", response.get("response", ""))
        # Simple extraction - can be enhanced
        if "recommendations" in text.lower():
            # Extract recommendations (simplified)
            return [line.strip() for line in text.split("\n") if line.strip() and "-" in line]
        return []
    
    def _extract_key_themes(self, response: Dict[str, Any]) -> List[str]:
        """Extract key themes from LLM response."""
        text = response.get("text", response.get("response", ""))
        # Simple extraction - can be enhanced
        if "themes" in text.lower():
            # Extract themes (simplified)
            return [line.strip() for line in text.split("\n") if line.strip() and "-" in line]
        return []
    
    def _extract_summary(self, response: Dict[str, Any]) -> str:
        """Extract summary from LLM response."""
        text = response.get("text", response.get("response", ""))
        # Simple extraction - can be enhanced
        if "summary" in text.lower():
            # Extract summary section
            summary_start = text.lower().find("summary")
            if summary_start >= 0:
                return text[summary_start:summary_start+500]  # First 500 chars
        return text[:200] if text else ""  # First 200 chars as fallback
    
    def _convert_user_context(self, user_context: Optional[UserContext]) -> Optional[Dict[str, Any]]:
        """Convert UserContext to dict if needed."""
        if user_context is None:
            return None
        if isinstance(user_context, dict):
            return user_context
        # Convert UserContext object to dict
        return {
            "user_id": getattr(user_context, "user_id", None),
            "tenant_id": getattr(user_context, "tenant_id", None),
            "session_id": getattr(user_context, "session_id", None),
            "workflow_id": getattr(user_context, "workflow_id", None)
        }
    
    async def get_smart_city_service(self, service_name: str):
        """Get Smart City service via MCP."""
        if self.mcp_client_manager:
            try:
                return await self.mcp_client_manager.connect_to_role(service_name.lower().replace("service", ""))
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to connect to {service_name}: {e}")
                return None
        return None
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Business analysis agent that uses EDA tools and OpenAI LLM for insights"
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process agent request.
        
        Routes to appropriate analysis method based on request type.
        """
        request_type = request.get("type", "structured")
        content_id = request.get("content_id")
        user_context = request.get("user_context")
        
        if not content_id:
            return {
                "success": False,
                "error": "content_id is required"
            }
        
        if request_type == "unstructured":
            return await self.analyze_unstructured_data(
                content_id=content_id,
                user_context=user_context
            )
        else:
            # Default to structured
            return await self.analyze_structured_data(
                content_id=content_id,
                user_context=user_context
            )

