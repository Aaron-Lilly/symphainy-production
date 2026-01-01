"""
Guide Cross-Domain Agent - Declarative Implementation

This agent is now configuration-driven, providing cross-domain navigation
and holistic guidance using LLM reasoning.

Key Features (now in configuration):
- Cross-Domain Intent Analysis: Interprets user intent across different solution domains
- Dynamic Liaison Agent Discovery: Routes users to appropriate liaison agents
- User Journey Tracking: Guides users through multi-domain workflows
- Holistic Guidance: Provides high-level strategic advice
- Solution-Agnostic Configuration: Adapts to different solution contexts (MVP, Data Mash, APG)

Interface Methods (maintained for compatibility):
- handle_user_request(): Main entry point for user interactions
- configure_for_solution(): Configures the agent for a specific solution
"""

from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path

from foundations.di_container.di_container_service import DIContainerService
from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
from foundations.agentic_foundation.agent_sdk.mcp_client_manager import MCPClientManager
from foundations.agentic_foundation.agent_sdk.policy_integration import PolicyIntegration
from foundations.agentic_foundation.agent_sdk.tool_composition import ToolComposition
from foundations.agentic_foundation.agent_sdk.agui_output_formatter import AGUIOutputFormatter

from backend.business_enablement.agents.declarative_agent_base import DeclarativeAgentBase


class GuideCrossDomainAgent(DeclarativeAgentBase):
    """
    Guide Cross-Domain Agent - Declarative Implementation.
    
    This agent is now configuration-driven, providing cross-domain navigation
    and holistic guidance using LLM reasoning.
    
    Located in Journey realm as it's responsible for user journey guidance.
    """
    
    def __init__(self,
                 agent_name: str = "MVP Guide Agent",
                 foundation_services: DIContainerService = None,
                 agentic_foundation: AgenticFoundationService = None,
                 mcp_client_manager: MCPClientManager = None,
                 policy_integration: PolicyIntegration = None,
                 tool_composition: ToolComposition = None,
                 agui_formatter: AGUIOutputFormatter = None,
                 curator_foundation=None,
                 metadata_foundation=None,
                 public_works_foundation=None,
                 solution_config: Optional[Dict[str, Any]] = None,
                 logger: Optional[logging.Logger] = None,
                 **kwargs):  # Accept **kwargs to ignore agent_name and other params from orchestrator
        """
        Initialize Guide Cross-Domain Agent with declarative configuration.
        
        Args:
            agent_name: Name of the agent (default: "MVP Guide Agent")
            foundation_services: DI container service
            agentic_foundation: Agentic foundation service
            mcp_client_manager: MCP client manager
            policy_integration: Policy integration service
            tool_composition: Tool composition service
            agui_formatter: AGUI output formatter
            curator_foundation: Curator foundation (optional)
            metadata_foundation: Metadata foundation (optional)
            public_works_foundation: Public works foundation (optional)
            solution_config: Solution configuration (optional, will use YAML config if not provided)
            logger: Logger instance (optional)
        """
        # Get configuration file path (now in journey realm)
        config_path = Path(__file__).parent / "configs" / "mvp_guide_agent.yaml"
        
        # Initialize declarative agent base
        super().__init__(
            agent_config_path=str(config_path),
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            public_works_foundation=public_works_foundation,
            logger=logger or logging.getLogger("GuideCrossDomainAgent")
        )
        
        # Store solution config (from YAML or parameter)
        self.solution_config = solution_config or self.agent_config.get("solution_config", {})
        self.configured_domains = self.solution_config.get("domains", [])
        self.solution_type = self.solution_config.get("name", "").lower()
        
        self.logger.info(f"🧭 GuideCrossDomainAgent initialized for solution: {self.solution_type} with domains: {self.configured_domains}")
    
    async def handle_user_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle cross-domain user request using the declarative agent's LLM reasoning.
        
        This method acts as the public interface, delegating the core logic to the
        DeclarativeAgentBase's process_request method.
        
        Args:
            request: User request containing:
                - message: User message
                - user_context: User context
                - conversation_history: Optional conversation history (handled by base class)
        
        Returns:
            Response with guidance, suggested routes, and results.
        """
        # The base class's process_request will handle conversation history if stateful is true
        result = await self.process_request(request)
        
        # Extract intent and suggested routes from LLM response
        intent = self._extract_intent(result)
        suggested_routes = self._extract_suggested_routes(result)
        
        # The LLM's response (result) is expected to contain the conversational output
        # and potentially suggested routes or tool calls.
        
        response = {
            "type": "guide_response",
            "agent_type": self.agent_name,
            "message": result.get("response", "I'm sorry, I couldn't process your request."),
            "intent": intent,
            "suggested_routes": suggested_routes,
            "configured_domains": self.configured_domains
        }
        
        # Preserve Priority 2 metadata (cost_info, conversation_history_length)
        if "cost_info" in result:
            response["cost_info"] = result["cost_info"]
        if "conversation_history_length" in result:
            response["conversation_history_length"] = result["conversation_history_length"]
        
        return response
    
    async def configure_for_solution(self, solution_type: str) -> Dict[str, Any]:
        """
        Configure Guide Agent for a specific solution.
        
        In the declarative pattern, this configuration is primarily driven by the YAML.
        This method can be used to re-initialize the agent with a different config if needed,
        or simply to confirm the current configuration.
        
        Args:
            solution_type: Type of solution ("mvp", "data_mash", "apg", etc.)
        
        Returns:
            Configuration results.
        """
        # For a declarative agent, the solution configuration is loaded from the YAML at init.
        # This method can be used to verify or dynamically adjust if multiple YAMLs were supported.
        # For now, we'll just confirm the loaded config.
        
        if self.solution_type.lower() != solution_type.lower():
            self.logger.warning(f"⚠️ Attempted to configure Guide Agent for '{solution_type}', but it's initialized for '{self.solution_type}'. Re-initialization with a different config might be needed.")
        
        return {
            "success": True,
            "solution_type": self.solution_type,
            "domains_configured": self.configured_domains,
            "message": f"Guide Agent is configured for '{self.solution_type}' solution."
        }
    
    def _extract_intent(self, result: Dict[str, Any]) -> str:
        """
        Extract intent from LLM response.
        
        Args:
            result: Result from process_request
            
        Returns:
            Extracted intent (default: "general")
        """
        # Try to extract intent from reasoning or response
        reasoning = result.get("reasoning", "")
        if not isinstance(reasoning, str):
            reasoning = str(reasoning) if reasoning is not None else ""
        
        # Look for domain-specific intent keywords
        intent_keywords = {
            "content": "content_management",
            "insights": "insights_analysis",
            "operations": "operations_management",
            "business": "business_outcomes"
        }
        
        reasoning_lower = reasoning.lower()
        for keyword, intent in intent_keywords.items():
            if keyword in reasoning_lower:
                return intent
        
        return result.get("intent", "general")
    
    def _extract_suggested_routes(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract suggested routes from LLM response.
        
        Args:
            result: Result from process_request
            
        Returns:
            List of suggested routes
        """
        # Try to extract from tool calls
        tool_calls = result.get("tool_calls", [])
        if tool_calls:
            routes = []
            for tc in tool_calls:
                if tc.get("name") == "route_to_liaison_agent_tool":
                    params = tc.get("parameters", {})
                    routes.append({
                        "domain": params.get("domain_name"),
                        "description": params.get("user_query", "")
                    })
            if routes:
                return routes
        
        # Try to extract from response text
        response_text = result.get("response", "")
        if not isinstance(response_text, str):
            response_text = str(response_text) if response_text is not None else ""
        
        # Look for domain mentions in response
        routes = []
        for domain in self.configured_domains:
            if domain.replace("_", " ") in response_text.lower():
                routes.append({
                    "domain": domain,
                    "description": f"Navigate to {domain} domain"
                })
        
        return routes
    
    async def handle_user_message(
        self,
        user_message: str,
        session_token: str,
        conversation_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle user message for WebSocket compatibility.
        
        This method provides a simplified interface for WebSocket communication,
        wrapping the more comprehensive handle_user_request() method.
        
        Args:
            user_message: User's message text
            session_token: Session token for user identification
            conversation_id: Optional conversation ID for context
            user_context: Optional user context dictionary
        
        Returns:
            Response dictionary compatible with WebSocket format:
            {
                "type": "response" | "error",
                "message": "agent response",
                "agent_type": "guide",
                "conversation_id": "...",
                ...
            }
        """
        try:
            # Build request dictionary for handle_user_request
            request = {
                "message": user_message,
                "user_context": user_context or {
                    "user_id": session_token or "anonymous",
                    "session_id": session_token or "anonymous"
                }
            }
            
            # Add conversation_id if provided
            if conversation_id:
                request["conversation_id"] = conversation_id
            
            # Call handle_user_request (which uses process_request internally)
            response = await self.handle_user_request(request)
            
            # Transform response to WebSocket-compatible format
            # The response from handle_user_request has:
            # - type: "guide_response"
            # - agent_type: self.agent_name
            # - message: response text
            # - intent: intent analysis
            # - suggested_routes: suggested routes
            
            # Transform to unified websocket format
            websocket_response = {
                "type": "response",
                "message": response.get("message", "I'm sorry, I couldn't process your request."),
                "agent_type": "guide",
                "response": response.get("message", ""),  # Also include as "response" for compatibility
            }
            
            # Add conversation_id if provided
            if conversation_id:
                websocket_response["conversation_id"] = conversation_id
            
            # Preserve additional metadata
            if "intent" in response:
                websocket_response["intent"] = response["intent"]
            if "suggested_routes" in response:
                websocket_response["suggested_routes"] = response["suggested_routes"]
            if "cost_info" in response:
                websocket_response["cost_info"] = response["cost_info"]
            if "conversation_history_length" in response:
                websocket_response["conversation_history_length"] = response["conversation_history_length"]
            
            return websocket_response
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle user message: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "type": "error",
                "message": f"Failed to process message: {str(e)}",
                "agent_type": "guide",
                "conversation_id": conversation_id
            }
    
    # ========================================================================
    # CRITICAL REASONING METHODS (Agentic-Forward Pattern)
    # ========================================================================
    # These methods do the critical reasoning FIRST, before services execute
    
    async def analyze_user_goals_for_solution_structure(
        self,
        user_goals: str,
        user_context: Optional[Dict[str, Any]] = None,
        existing_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        CRITICAL REASONING: Analyze user goals to determine optimal solution structure.
        
        This is the agentic-forward approach - agent does critical reasoning FIRST,
        then services execute based on agent's strategic decisions.
        
        The agent determines:
        - Which pillars to include and in what order
        - What data types are needed
        - What customizations make sense
        - What workflows would be valuable
        - Strategic priorities and focus areas
        
        Args:
            user_goals: User's stated goals, challenges, or desired outcomes
            user_context: Optional user context (industry, role, constraints)
            existing_data: Optional existing data/files the user has
        
        Returns:
            Solution structure specification for services to execute:
            {
                "success": bool,
                "solution_structure": {
                    "pillars": [
                        {
                            "name": "content" | "insights" | "operations" | "business-outcomes",
                            "enabled": bool,
                            "priority": int,  # 1-4, lower is higher priority
                            "customizations": {
                                "focus_areas": [...],
                                "workflows": [...],
                                "data_types": [...]
                            },
                            "navigation_order": int  # Order in which to visit
                        }
                    ],
                    "recommended_data_types": [...],
                    "strategic_focus": str,
                    "customization_options": {
                        "workflow_creation": bool,
                        "interactive_guidance": bool,
                        "automated_analysis": bool
                    }
                },
                "reasoning": {
                    "analysis": str,  # Agent's reasoning
                    "key_insights": [...],
                    "recommendations": [...],
                    "confidence": float  # 0.0-1.0
                }
            }
        """
        try:
            self.logger.info("🧠 Performing critical reasoning for solution structure...")
            
            # Use LLM abstraction for critical reasoning
            if not self.llm_abstraction:
                self.logger.warning("⚠️ LLM abstraction not available, using fallback reasoning")
                return await self._fallback_solution_structure_analysis(user_goals, user_context)
            
            # Build analysis prompt for LLM
            analysis_prompt = f"""
You are an expert solution architect analyzing user goals to create a customized solution structure.

User Goals: {user_goals}
User Context: {user_context or {}}
Existing Data: {existing_data or {}}

Available Pillars:
1. Content: File upload, parsing, semantic data model creation
2. Insights: Data analysis, visualization, data mapping, quality validation
3. Operations: Workflow/SOP generation, coexistence blueprint creation
4. Business Outcomes: Roadmap generation, POC proposal creation

Analyze the user's goals and determine:
1. Which pillars are relevant and in what priority order?
2. What data types should the user focus on?
3. What customizations would maximize value?
4. What workflows would be most valuable?
5. What is the strategic focus area?

Provide a structured solution specification that services can execute.
"""
            
            # Use LLM for critical reasoning
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            llm_request = LLMRequest(
                prompt=analysis_prompt,
                model=LLMModel.GPT_4O_MINI,  # Use configured model from agent config
                temperature=0.3,  # Lower temperature for more deterministic reasoning
                max_tokens=2000
            )
            
            llm_response = await self.llm_abstraction.generate_content(llm_request)
            
            # Parse LLM response to extract solution structure
            solution_structure = self._parse_solution_structure_from_llm_response(
                llm_response,
                user_goals,
                user_context
            )
            
            # Extract reasoning
            reasoning = {
                "analysis": llm_response.get("content", ""),
                "key_insights": self._extract_key_insights(llm_response),
                "recommendations": self._extract_recommendations(llm_response),
                "confidence": self._calculate_confidence(llm_response, user_goals)
            }
            
            self.logger.info("✅ Critical reasoning completed for solution structure")
            
            return {
                "success": True,
                "solution_structure": solution_structure,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.logger.error(f"❌ Critical reasoning failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "solution_structure": await self._fallback_solution_structure_analysis(user_goals, user_context)
            }
    
    def _parse_solution_structure_from_llm_response(
        self,
        llm_response: Dict[str, Any],
        user_goals: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Parse LLM response to extract structured solution specification.
        
        Args:
            llm_response: LLM response from generate_content
            user_goals: Original user goals
            user_context: User context
        
        Returns:
            Structured solution specification
        """
        # Default structure (all pillars enabled, standard order)
        default_pillars = [
            {"name": "content", "enabled": True, "priority": 1, "navigation_order": 1, "customizations": {}},
            {"name": "insights", "enabled": True, "priority": 2, "navigation_order": 2, "customizations": {}},
            {"name": "operations", "enabled": True, "priority": 3, "navigation_order": 3, "customizations": {}},
            {"name": "business-outcomes", "enabled": True, "priority": 4, "navigation_order": 4, "customizations": {}}
        ]
        
        # Try to extract structured data from LLM response
        content = llm_response.get("content", "")
        if not content:
            return {
                "pillars": default_pillars,
                "recommended_data_types": [],
                "strategic_focus": "general",
                "customization_options": {
                    "workflow_creation": True,
                    "interactive_guidance": True,
                    "automated_analysis": True
                }
            }
        
        # Parse JSON if LLM returned structured data
        try:
            import json
            # Try to find JSON in the response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                parsed = json.loads(content[json_start:json_end])
                if "pillars" in parsed:
                    return parsed
        except:
            pass
        
        # Fallback: Use keyword analysis to customize default structure
        content_lower = content.lower()
        goals_lower = user_goals.lower()
        
        # Analyze keywords to determine priorities
        pillar_keywords = {
            "content": ["data", "file", "upload", "parse", "document", "content"],
            "insights": ["analyze", "insight", "visualization", "mapping", "quality", "report"],
            "operations": ["workflow", "process", "sop", "operation", "automation", "blueprint"],
            "business-outcomes": ["roadmap", "strategy", "poc", "proposal", "outcome", "business"]
        }
        
        # Calculate pillar priorities based on keyword matches
        pillar_scores = {}
        for pillar_name, keywords in pillar_keywords.items():
            score = sum(1 for keyword in keywords if keyword in goals_lower or keyword in content_lower)
            pillar_scores[pillar_name] = score
        
        # Sort by score (higher score = higher priority)
        sorted_pillars = sorted(pillar_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Update default structure with priorities
        for idx, (pillar_name, score) in enumerate(sorted_pillars):
            for pillar in default_pillars:
                if pillar["name"] == pillar_name:
                    pillar["priority"] = idx + 1
                    pillar["navigation_order"] = idx + 1
                    if score > 0:
                        pillar["customizations"] = {
                            "focus_areas": [f"High relevance based on goals: {score} matches"],
                            "workflows": [],
                            "data_types": []
                        }
        
        # Extract recommended data types
        data_type_keywords = {
            "csv": ["csv", "spreadsheet", "tabular", "data"],
            "json": ["json", "api", "structured"],
            "pdf": ["pdf", "document", "report"],
            "xml": ["xml", "structured"],
            "text": ["text", "txt", "log"]
        }
        
        recommended_data_types = []
        for data_type, keywords in data_type_keywords.items():
            if any(kw in goals_lower or kw in content_lower for kw in keywords):
                recommended_data_types.append(data_type)
        
        # Determine strategic focus
        strategic_focus = "general"
        if any(kw in goals_lower for kw in ["automation", "workflow", "process"]):
            strategic_focus = "operations"
        elif any(kw in goals_lower for kw in ["analyze", "insight", "visualization"]):
            strategic_focus = "insights"
        elif any(kw in goals_lower for kw in ["roadmap", "strategy", "poc"]):
            strategic_focus = "business-outcomes"
        elif any(kw in goals_lower for kw in ["data", "file", "content"]):
            strategic_focus = "content"
        
        return {
            "pillars": default_pillars,
            "recommended_data_types": recommended_data_types if recommended_data_types else ["csv", "json", "pdf"],
            "strategic_focus": strategic_focus,
            "customization_options": {
                "workflow_creation": any(kw in goals_lower for kw in ["workflow", "process", "automation"]),
                "interactive_guidance": True,  # Always enable
                "automated_analysis": any(kw in goals_lower for kw in ["analyze", "insight", "automated"])
            }
        }
    
    def _extract_key_insights(self, llm_response: Dict[str, Any]) -> List[str]:
        """Extract key insights from LLM response."""
        content = llm_response.get("content", "")
        # Simple extraction - look for bullet points or numbered lists
        lines = content.split("\n")
        insights = []
        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("*") or (line[0].isdigit() and "." in line[:3]):
                insights.append(line.lstrip("-* ").lstrip("0123456789. "))
        return insights[:5]  # Limit to top 5
    
    def _extract_recommendations(self, llm_response: Dict[str, Any]) -> List[str]:
        """Extract recommendations from LLM response."""
        # Similar to key insights
        return self._extract_key_insights(llm_response)
    
    def _calculate_confidence(self, llm_response: Dict[str, Any], user_goals: str) -> float:
        """Calculate confidence score based on response quality and goal clarity."""
        content = llm_response.get("content", "")
        if not content or len(content) < 100:
            return 0.5  # Low confidence if response is too short
        
        if len(user_goals) < 10:
            return 0.6  # Lower confidence if goals are vague
        
        # Higher confidence if response is detailed and goals are clear
        return min(0.95, 0.7 + (len(content) / 1000) * 0.25)
    
    async def _fallback_solution_structure_analysis(
        self,
        user_goals: str,
        user_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Fallback solution structure analysis when LLM is not available.
        
        Uses simple keyword matching to determine structure.
        """
        self.logger.info("🔄 Using fallback solution structure analysis")
        
        goals_lower = user_goals.lower()
        
        # Default: all pillars enabled
        pillars = [
            {"name": "content", "enabled": True, "priority": 1, "navigation_order": 1, "customizations": {}},
            {"name": "insights", "enabled": True, "priority": 2, "navigation_order": 2, "customizations": {}},
            {"name": "operations", "enabled": True, "priority": 3, "navigation_order": 3, "customizations": {}},
            {"name": "business-outcomes", "enabled": True, "priority": 4, "navigation_order": 4, "customizations": {}}
        ]
        
        # Simple keyword-based customization
        recommended_data_types = []
        if any(kw in goals_lower for kw in ["csv", "spreadsheet", "data"]):
            recommended_data_types.append("csv")
        if any(kw in goals_lower for kw in ["json", "api"]):
            recommended_data_types.append("json")
        if any(kw in goals_lower for kw in ["pdf", "document"]):
            recommended_data_types.append("pdf")
        
        return {
            "pillars": pillars,
            "recommended_data_types": recommended_data_types if recommended_data_types else ["csv", "json"],
            "strategic_focus": "general",
            "customization_options": {
                "workflow_creation": True,
                "interactive_guidance": True,
                "automated_analysis": True
            }
        }





