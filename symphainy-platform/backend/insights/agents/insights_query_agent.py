#!/usr/bin/env python3
"""
Insights Query Agent

Query Generation Agent for Insights Pillar.

Uses OpenAI LLM (not HF) for query generation.
Only used when semantic search isn't sufficient.
Generates query specs (not raw SQL/Pandas code) based on schema metadata.

WHAT (Business Enablement Role): I generate query specs from natural language
HOW (Agent): I use OpenAI LLM to interpret natural language queries and generate query specifications based on schema metadata
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from utilities import UserContext
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase


class InsightsQueryAgent(AgentBase):
    """
    Query Generation Agent for Insights Pillar.
    
    Uses OpenAI LLM (not HF) for query generation.
    Only used when semantic search isn't sufficient.
    Generates query specs (not raw SQL/Pandas code) based on schema metadata.
    
    Key Features:
    - Works with schema metadata from embeddings (not raw data)
    - Generates query specs (not raw code)
    - Uses OpenAI LLM for natural language understanding
    - Maintains security boundary (works with semantic embeddings)
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
        Initialize Insights Query Agent with full SDK dependencies.
        
        This agent is created via Agentic Foundation factory - all dependencies
        are provided by the factory.
        """
        agent_id = kwargs.get("agent_id", agent_name.lower().replace(" ", "_"))
        agent_description = kwargs.get(
            "agent_description",
            "Query generation agent that uses OpenAI LLM to generate query specs from natural language"
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
        Initialize Insights Query Agent.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        
        Note: Factory handles Curator registration (Agentic Foundation owns agent registry).
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "initialize_start",
                success=True,
                details={"agent_name": self.agent_name}
            )
            
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
                        self.logger.info("✅ Discovered InsightsOrchestrator")
                except Exception as e:
                    await self.handle_error_with_audit(e, "orchestrator_discovery", details={"orchestrator": "InsightsOrchestrator"})
                    self.logger.warning(f"⚠️ InsightsOrchestrator not available: {e}")
            
            self.is_initialized = True
            
            # Record health metric (success)
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.agent_name
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "initialize_complete",
                success=True,
                details={"agent_name": self.agent_name}
            )
            
            self.logger.info(f"✅ {self.agent_name} initialization complete")
            return True
        
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "initialize", details={"agent_name": self.agent_name})
            
            # Record health metric (failure)
            await self.record_health_metric("initialization_failed", 1.0, {
                "agent_name": self.agent_name,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "initialize_complete",
                success=False,
                details={"agent_name": self.agent_name, "error": str(e)}
            )
            
            self.is_initialized = False
            return False
    
    async def generate_query_from_nl(
        self,
        natural_language_query: str,
        content_id: str,
        schema_metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Generate SQL/Pandas query from natural language using OpenAI LLM.
        
        Flow:
        1. Get schema metadata from embeddings (if not provided)
        2. Use OpenAI LLM to generate query spec
        3. Return query spec (not raw code)
        
        Args:
            natural_language_query: User's natural language query
            content_id: Content ID for context
            schema_metadata: Optional schema metadata (if not provided, will fetch from embeddings)
            user_context: User context for security/tenant validation
        
        Returns:
            Query spec dictionary with:
            {
                "success": bool,
                "query_type": "sql" | "pandas" | "semantic_search",
                "query_spec": {
                    "type": str,
                    "filters": {...},
                    "columns": [...],
                    "aggregations": {...},
                    "order_by": {...},
                    "limit": int
                },
                "confidence": float,
                "content_id": str
            }
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "generate_query_from_nl_start",
                success=True,
                details={"content_id": content_id, "query": natural_language_query[:100]}
            )
            
            # Convert UserContext to dict if needed
            user_context_dict = self._convert_user_context(user_context)
            
            # Step 1: Get schema metadata if not provided
            if not schema_metadata:
                schema_metadata = await self._get_schema_metadata(content_id, user_context_dict)
                if not schema_metadata:
                    return {
                        "success": False,
                        "error": "No schema metadata found",
                        "content_id": content_id
                    }
            
            # Step 2: Use OpenAI LLM to generate query spec
            query_spec = await self._generate_query_spec_with_llm(
                natural_language_query=natural_language_query,
                schema_metadata=schema_metadata,
                user_context=user_context_dict
            )
            
            result = {
                "success": True,
                "content_id": content_id,
                "query_type": query_spec.get("query_type", "semantic_search"),
                "query_spec": query_spec.get("query_spec", {}),
                "confidence": query_spec.get("confidence", 0.0),
                "natural_language_query": natural_language_query
            }
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "generate_query_from_nl_complete",
                success=True,
                details={"content_id": content_id, "query_type": result["query_type"]}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e, "generate_query_from_nl",
                details={"content_id": content_id, "query": natural_language_query[:100]}
            )
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "generate_query_from_nl_complete",
                success=False,
                details={"content_id": content_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ Query generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }
    
    # ============================================================================
    # ABSTRACT METHODS IMPLEMENTATION (from AgentBase)
    # ============================================================================
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request using agent capabilities."""
        try:
            # Route to appropriate method based on request type
            request_type = request.get("type", "generate_query")
            
            if request_type == "generate_query":
                return await self.generate_query_from_nl(
                    natural_language_query=request.get("query", ""),
                    content_id=request.get("content_id", ""),
                    schema_metadata=request.get("schema_metadata"),
                    user_context=request.get("user_context")
                )
            else:
                return {
                    "success": False,
                    "message": f"Unknown request type: {request_type}",
                    "error": "unsupported_request_type"
                }
        except Exception as e:
            self.logger.error(f"❌ Failed to process request: {e}")
            return {
                "success": False,
                "message": f"Request processing failed: {str(e)}",
                "error": str(e)
            }
    
    async def get_agent_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return ["query_generation", "nl_to_query", "schema_based_querying"]
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Query Generation Agent - Generates query specs from natural language using OpenAI LLM"
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _convert_user_context(self, user_context: Optional[UserContext]) -> Dict[str, Any]:
        """Convert UserContext to dict if needed."""
        if user_context is None:
            return {}
        if isinstance(user_context, dict):
            return user_context
        return {
            "user_id": getattr(user_context, "user_id", None),
            "tenant_id": getattr(user_context, "tenant_id", None),
            "session_id": getattr(user_context, "session_id", None),
            "roles": getattr(user_context, "roles", [])
        }
    
    async def _get_schema_metadata(
        self,
        content_id: str,
        user_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get schema metadata from embeddings.
        
        Returns:
            Schema metadata dict with columns, types, etc.
        """
        try:
            # Use Content MCP tools for semantic data access (unified pattern)
            embeddings_result = await self.execute_mcp_tool(
                "content_get_semantic_embeddings",  # Cross-realm: Content realm MCP tool
                {
                    "content_id": content_id,
                    "filters": {"embedding_type": "schema"},
                    "user_context": user_context
                }
            )
            
            if not embeddings_result.get("success"):
                self.logger.warning(f"⚠️ Failed to get semantic embeddings: {embeddings_result.get('error')}")
                return None
            
            embeddings = embeddings_result.get("embeddings", [])
            
            if not embeddings:
                return None
            
            # Extract schema information from embeddings
            schema_metadata = {
                "columns": [],
                "column_types": {},
                "content_id": content_id
            }
            
            for emb in embeddings:
                column_name = emb.get("column_name")
                column_type = emb.get("column_type") or emb.get("data_type")
                if column_name:
                    schema_metadata["columns"].append(column_name)
                    if column_type:
                        schema_metadata["column_types"][column_name] = column_type
            
            return schema_metadata
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get schema metadata: {e}")
            return None
    
    async def _generate_query_spec_with_llm(
        self,
        natural_language_query: str,
        schema_metadata: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate query spec using OpenAI LLM.
        
        Uses agentic correlation tracking for LLM call.
        """
        try:
            # Build prompt for query generation
            prompt = self._build_query_generation_prompt(
                natural_language_query=natural_language_query,
                schema_metadata=schema_metadata
            )
            
            # Call LLM using simple helper (includes agentic correlation tracking)
            system_message = "You are a query generation assistant. Generate query specifications based on natural language queries and schema metadata. Return only valid JSON."
            response_text = await self._call_llm_simple(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o",  # Use GPT-4O for better query generation
                max_tokens=500,
                temperature=0.3,
                user_context=user_context,
                metadata={
                    "agent_name": self.agent_name,
                    "operation": "generate_query_spec",
                    "content_id": schema_metadata.get("content_id")
                }
            )
            
            # Parse LLM response to extract query spec
            query_spec = self._parse_query_spec_response(response_text)
            
            return query_spec
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate query spec with LLM: {e}")
            raise
    
    def _build_query_generation_prompt(
        self,
        natural_language_query: str,
        schema_metadata: Dict[str, Any]
    ) -> str:
        """Build prompt for query generation."""
        columns = schema_metadata.get("columns", [])
        column_types = schema_metadata.get("column_types", {})
        
        schema_info = "\n".join([
            f"- {col}: {column_types.get(col, 'unknown')}"
            for col in columns
        ])
        
        prompt = f"""Generate a query specification from the following natural language query.

Natural Language Query: {natural_language_query}

Available Schema:
{schema_info}

Generate a query specification in JSON format with the following structure:
{{
    "query_type": "sql" | "pandas" | "semantic_search",
    "query_spec": {{
        "type": "select" | "aggregate" | "filter" | "join",
        "filters": {{"column": "value", ...}},
        "columns": ["column1", "column2", ...],
        "aggregations": {{"column": "sum" | "avg" | "count" | "max" | "min", ...}},
        "order_by": {{"column": "asc" | "desc"}},
        "limit": number
    }},
    "confidence": 0.0-1.0
}}

If the query can be answered via semantic search, use "semantic_search" as query_type.
If the query requires SQL, use "sql" as query_type.
If the query requires Pandas operations, use "pandas" as query_type.

Return only the JSON, no additional text."""
        
        return prompt
    
    def _parse_query_spec_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response to extract query spec."""
        try:
            # Try to extract JSON from response
            # LLM might return JSON wrapped in markdown code blocks
            response_text = llm_response.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            
            # Parse JSON
            query_spec = json.loads(response_text)
            
            # Validate structure
            if "query_type" not in query_spec:
                query_spec["query_type"] = "semantic_search"
            if "query_spec" not in query_spec:
                query_spec["query_spec"] = {}
            if "confidence" not in query_spec:
                query_spec["confidence"] = 0.5
            
            return query_spec
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"⚠️ Failed to parse LLM response as JSON: {e}")
            # Return default semantic search query spec
            return {
                "query_type": "semantic_search",
                "query_spec": {},
                "confidence": 0.3
            }

