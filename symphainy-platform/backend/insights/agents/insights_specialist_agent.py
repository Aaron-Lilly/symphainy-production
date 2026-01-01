#!/usr/bin/env python3
"""
Insights Specialist Agent - AI Showcase

AI Showcase Agent - Demonstrates how agents use data science tools to generate
grounded insights without hallucination.

WHAT (Business Enablement Role): I orchestrate data science tools to generate business insights
HOW (Specialist Agent): I use DataAnalyzer, MetricsCalculator, and VisualizationEngine to analyze
     data, then explain results in plain English

Key Principle: Insights come from ACTUAL data analysis, not LLM generation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
import os
import sys
sys.path.insert(0, os.path.abspath('../../../../../../'))

from utilities import UserContext
from backend.business_enablement.protocols.business_specialist_agent_protocol import (
    BusinessSpecialistAgentBase,
    SpecialistCapability
)


class InsightsSpecialistAgent(BusinessSpecialistAgentBase):
    """
    Insights Specialist Agent - Data Science Orchestrator
    
    This agent showcases how AI can use data science tools to generate
    grounded insights without hallucination.
    
    Core Capabilities:
    1. Orchestrate data science tools (DataAnalyzer, MetricsCalculator, VisualizationEngine)
    2. Generate grounded insights from actual data analysis
    3. Explain data science results in plain English
    4. Enable "double-click" exploration of insights
    5. Generate comprehensive insights summaries with recommendations
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
        """Initialize Insights Specialist Agent with full SDK dependencies."""
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
            specialist_capability=kwargs.get("specialist_capability", SpecialistCapability.DATA_ANALYSIS),
            **{k: v for k, v in kwargs.items() if k != "specialist_capability"}
        )
        
        self.service_name = agent_name
        self.insights_orchestrator = None
        self.orchestrator = None  # Set by orchestrator for MCP tool access
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference for MCP tool access."""
        self.orchestrator = orchestrator
        self.insights_orchestrator = orchestrator
        self.logger.info("✅ Orchestrator reference set for MCP tool access")
    
    async def initialize(self):
        """
        Initialize Insights Specialist Agent.
        
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
                    await self.handle_error_with_audit(e, "orchestrator_discovery", details={"orchestrator": "InsightsOrchestrator"})
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
    
    # ========================================================================
    # CORE CAPABILITIES (AI Showcase - No Hallucination)
    # ========================================================================
    
    async def generate_grounded_insights(
        self,
        resource_id: str,
        analysis_options: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous",
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Generate grounded insights by orchestrating data science tools via MCP.
        
        AI Showcase: This demonstrates how agents use data science tools to generate
        insights without hallucination. All insights come from actual data analysis.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Flow:
        1. Use MCP tool to call DataAnalyzerService (via orchestrator)
        2. Use MCP tool to call MetricsCalculatorService (via orchestrator)
        3. Use MCP tool to call VisualizationEngineService (via orchestrator)
        4. Generate business narrative from ACTUAL data science results
        5. Provide plain English explanation
        
        Args:
            resource_id: Data resource identifier
            analysis_options: Optional analysis configuration
            user_id: User identifier
            user_context: User context for authorization
        
        Returns:
            Grounded insights with business narrative
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("generate_grounded_insights_start", success=True, details={
                "resource_id": resource_id,
                "user_id": user_id
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None) or user_id,
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "insights", "generate"):
                        await self.record_health_metric("generate_grounded_insights_access_denied", 1.0, {
                            "resource_id": resource_id
                        })
                        await self.log_operation_with_telemetry("generate_grounded_insights_complete", success=False, details={
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions to generate insights")
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
                            await self.record_health_metric("generate_grounded_insights_tenant_denied", 1.0, {
                                "resource_id": resource_id,
                                "tenant_id": tenant_id
                            })
                            await self.log_operation_with_telemetry("generate_grounded_insights_complete", success=False, details={
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            
            self.logger.info(f"🤖 Generating grounded insights for resource: {resource_id}")
            
            if not self.orchestrator or not hasattr(self.orchestrator, 'mcp_server'):
                return {
                    "success": False,
                    "error": "MCP server not available"
                }
            
            mcp_server = self.orchestrator.mcp_server
            analysis_options = analysis_options or {}
            
            # Step 1: Use MCP tool to calculate metrics (orchestrator calls MetricsCalculatorService)
            metrics_result = await mcp_server.execute_tool(
                "calculate_metrics_tool",
                {
                    "resource_id": resource_id,
                    "options": analysis_options
                }
            )
            
            # Step 2: Use MCP tool to create visualization (orchestrator calls VisualizationEngineService)
            visualization_result = await mcp_server.execute_tool(
                "create_visualization_tool",
                {
                    "resource_id": resource_id,
                    "options": analysis_options
                }
            )
            
            # Step 3: Use MCP tool to analyze data (orchestrator calls DataAnalyzerService)
            analysis_result = await mcp_server.execute_tool(
                "analyze_content_for_insights_tool",
                {
                    "resource_id": resource_id,
                    "options": analysis_options
                }
            )
            
            # Step 4: Agent generates business narrative from ACTUAL data science results
            # (No LLM generation - grounded in data)
            business_narrative = self._generate_business_narrative(
                metrics_result,
                visualization_result,
                analysis_result
            )
            
            # Step 5: Generate insights summary
            insights_summary = self._generate_insights_summary(
                metrics_result,
                visualization_result,
                analysis_result,
                business_narrative
            )
            
            self.logger.info(f"✅ Grounded insights generated successfully")
            
            # Record health metric (success)
            await self.record_health_metric("generate_grounded_insights_success", 1.0, {
                "resource_id": resource_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_grounded_insights_complete", success=True)
            
            return {
                "success": True,
                "resource_id": resource_id,
                "metrics": metrics_result,
                "visualization": visualization_result,
                "analysis": analysis_result,
                "business_narrative": business_narrative,
                "insights_summary": insights_summary,
                "grounded": True,  # Indicates insights are from data, not LLM
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "generate_grounded_insights", details={
                "resource_id": resource_id,
                "user_id": user_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("generate_grounded_insights_error", 1.0, {
                "resource_id": resource_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("generate_grounded_insights_complete", success=False, details={
                "error": str(e)
            })
            
            self.logger.error(f"❌ Grounded insights generation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_double_click_query(
        self,
        query: str,
        resource_id: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Process "double-click" query for deep exploration via MCP.
        
        Example: "I see I have a lot of customers who are more than 90 days late. 
                 can you show me who those customers are?"
        
        Flow:
        1. Parse query intent
        2. Use MCP tools to query actual data
        3. Generate appropriate visualization
        4. Provide plain English explanation
        
        Args:
            query: User query for deep exploration
            resource_id: Data resource identifier
            context: Optional context data
            user_id: User identifier
        
        Returns:
            Deep exploration results with explanation
        """
        try:
            self.logger.info(f"🔍 Processing double-click query: {query}")
            
            if not self.orchestrator or not hasattr(self.orchestrator, 'mcp_server'):
                return {
                    "success": False,
                    "error": "MCP server not available"
                }
            
            mcp_server = self.orchestrator.mcp_server
            context = context or {}
            
            # Step 1: Parse query intent
            query_intent = self._parse_query_intent(query)
            
            # Step 2: Use MCP tool to query analysis results (orchestrator calls DataAnalyzerService)
            query_result = await mcp_server.execute_tool(
                "query_analysis_results_tool",
                {
                    "query": query,
                    "resource_id": resource_id,
                    "query_intent": query_intent,
                    "options": context
                }
            )
            
            # Step 3: Use MCP tool to create visualization for query results
            visualization_result = await mcp_server.execute_tool(
                "create_visualization_tool",
                {
                    "resource_id": resource_id,
                    "data": query_result.get("results", {}),
                    "options": {
                        "chart_type": query_intent.get("preferred_chart_type", "table"),
                        "query_context": query
                    }
                }
            )
            
            # Step 4: Generate plain English explanation
            explanation = self._explain_query_results(
                query,
                query_result,
                visualization_result,
                query_intent
            )
            
            # Step 5: Generate follow-up suggestions
            follow_ups = self._generate_follow_up_suggestions(
                query_intent,
                query_result
            )
            
            self.logger.info(f"✅ Double-click query processed successfully")
            
            return {
                "success": True,
                "query": query,
                "query_intent": query_intent,
                "results": query_result,
                "visualization": visualization_result,
                "explanation": explanation,
                "follow_up_suggestions": follow_ups,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Double-click query processing failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_insights_summary(
        self,
        resource_id: str,
        insights_data: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights summary with recommendations via MCP.
        
        Flow:
        1. Compile insights from previous analyses
        2. Use MCP tools to get additional metrics/visualizations if needed
        3. Generate summary narrative
        4. Generate recommendations based on data
        5. Create appropriate visualization
        
        Args:
            resource_id: Data resource identifier
            insights_data: Optional pre-computed insights
            user_id: User identifier
        
        Returns:
            Comprehensive insights summary with recommendations
        """
        try:
            self.logger.info(f"📊 Generating insights summary for resource: {resource_id}")
            
            if not self.orchestrator or not hasattr(self.orchestrator, 'mcp_server'):
                return {
                    "success": False,
                    "error": "MCP server not available"
                }
            
            mcp_server = self.orchestrator.mcp_server
            
            # Step 1: Get insights data (or use provided)
            if not insights_data:
                insights_data = await self.generate_grounded_insights(
                    resource_id=resource_id,
                    user_id=user_id
                )
            
            # Step 2: Compile summary from insights
            summary = self._compile_insights_summary(insights_data)
            
            # Step 3: Generate recommendations based on data
            recommendations = self._generate_data_driven_recommendations(
                insights_data,
                summary
            )
            
            # Step 4: Create summary visualization
            summary_visualization = await mcp_server.execute_tool(
                "create_visualization_tool",
                {
                    "resource_id": resource_id,
                    "data": summary,
                    "options": {
                        "chart_type": "summary",
                        "include_recommendations": True
                    }
                }
            )
            
            self.logger.info(f"✅ Insights summary generated successfully")
            
            return {
                "success": True,
                "resource_id": resource_id,
                "summary": summary,
                "recommendations": recommendations,
                "visualization": summary_visualization,
                "insights_data": insights_data,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Insights summary generation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def explain_data_science_results(
        self,
        analysis_result: Dict[str, Any],
        metrics_result: Optional[Dict[str, Any]] = None,
        visualization_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Explain data science results in plain English.
        
        This is the key differentiator: Agent explains ACTUAL data science results
        in business terms, not generating insights from LLM.
        
        Args:
            analysis_result: Data analysis results
            metrics_result: Optional metrics results
            visualization_result: Optional visualization results
        
        Returns:
            Plain English explanation of data science results
        """
        try:
            self.logger.info("📝 Explaining data science results in plain English")
            
            explanation = self._generate_plain_english_explanation(
                analysis_result,
                metrics_result,
                visualization_result
            )
            
            return {
                "success": True,
                "explanation": explanation,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Explanation generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _generate_business_narrative(
        self,
        metrics_result: Dict[str, Any],
        visualization_result: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> str:
        """Generate business narrative from data science results."""
        narrative_parts = []
        
        # Extract key metrics
        if metrics_result.get("success"):
            metrics = metrics_result.get("metrics", {})
            narrative_parts.append(f"Key metrics show: {self._format_metrics(metrics)}")
        
        # Extract key findings from analysis
        if analysis_result.get("success"):
            findings = analysis_result.get("insights", {}).get("key_findings", [])
            if findings:
                narrative_parts.append(f"Analysis reveals: {', '.join(findings[:3])}")
        
        # Reference visualization
        if visualization_result.get("success"):
            narrative_parts.append("Visual representation available for detailed exploration.")
        
        return " ".join(narrative_parts) if narrative_parts else "Data analysis completed successfully."
    
    def _generate_insights_summary(
        self,
        metrics_result: Dict[str, Any],
        visualization_result: Dict[str, Any],
        analysis_result: Dict[str, Any],
        business_narrative: str
    ) -> Dict[str, Any]:
        """Generate insights summary from data science results."""
        return {
            "narrative": business_narrative,
            "key_metrics": metrics_result.get("metrics", {}),
            "key_findings": analysis_result.get("insights", {}).get("key_findings", []),
            "visualization_available": visualization_result.get("success", False),
            "data_quality": analysis_result.get("data_quality", {}),
            "confidence": "high"  # High confidence because insights are from data, not LLM
        }
    
    def _parse_query_intent(self, query: str) -> Dict[str, Any]:
        """Parse query intent for double-click exploration."""
        query_lower = query.lower()
        
        intent = {
            "type": "exploration",
            "entities": [],
            "filters": {},
            "preferred_chart_type": "table"
        }
        
        # Detect filter intent
        if "who" in query_lower or "which" in query_lower:
            intent["type"] = "filter"
            intent["preferred_chart_type"] = "table"
        elif "how many" in query_lower or "count" in query_lower:
            intent["type"] = "aggregation"
            intent["preferred_chart_type"] = "bar"
        elif "trend" in query_lower or "over time" in query_lower:
            intent["type"] = "trend"
            intent["preferred_chart_type"] = "line"
        
        return intent
    
    def _explain_query_results(
        self,
        query: str,
        query_result: Dict[str, Any],
        visualization_result: Dict[str, Any],
        query_intent: Dict[str, Any]
    ) -> str:
        """Generate plain English explanation of query results."""
        results = query_result.get("results", {})
        count = results.get("count", 0)
        
        explanation = f"Based on your query '{query}', I found {count} matching results. "
        
        if visualization_result.get("success"):
            explanation += "A visualization has been created to help you explore these results. "
        
        if query_intent.get("type") == "filter":
            explanation += "You can see the detailed list in the table below."
        elif query_intent.get("type") == "aggregation":
            explanation += "The bar chart shows the distribution of values."
        elif query_intent.get("type") == "trend":
            explanation += "The line chart shows how this metric changes over time."
        
        return explanation
    
    def _generate_follow_up_suggestions(
        self,
        query_intent: Dict[str, Any],
        query_result: Dict[str, Any]
    ) -> List[str]:
        """Generate follow-up exploration suggestions."""
        suggestions = []
        
        if query_intent.get("type") == "filter":
            suggestions.append("Would you like to see trends for these filtered results?")
            suggestions.append("Can I show you related metrics for these items?")
        elif query_intent.get("type") == "aggregation":
            suggestions.append("Would you like to drill down into specific categories?")
            suggestions.append("Can I show you the distribution over time?")
        
        return suggestions
    
    def _compile_insights_summary(self, insights_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compile insights summary from insights data."""
        return {
            "key_insights": insights_data.get("insights_summary", {}).get("key_findings", []),
            "metrics_summary": insights_data.get("metrics", {}),
            "narrative": insights_data.get("business_narrative", ""),
            "data_quality": insights_data.get("analysis", {}).get("data_quality", {})
        }
    
    def _generate_data_driven_recommendations(
        self,
        insights_data: Dict[str, Any],
        summary: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on actual data (not LLM generation)."""
        recommendations = []
        
        # Generate recommendations based on metrics
        metrics = insights_data.get("metrics", {})
        if metrics.get("performance", {}).get("below_target"):
            recommendations.append("Consider reviewing processes that are performing below target.")
        
        # Generate recommendations based on findings
        findings = summary.get("key_insights", [])
        if findings:
            recommendations.append(f"Focus on addressing the key finding: {findings[0]}")
        
        return recommendations
    
    def _generate_plain_english_explanation(
        self,
        analysis_result: Dict[str, Any],
        metrics_result: Optional[Dict[str, Any]],
        visualization_result: Optional[Dict[str, Any]]
    ) -> str:
        """Generate plain English explanation of data science results."""
        explanation_parts = []
        
        if analysis_result.get("success"):
            insights = analysis_result.get("insights", {})
            explanation_parts.append(f"Analysis shows: {insights.get('summary', 'Data analyzed successfully')}")
        
        if metrics_result and metrics_result.get("success"):
            metrics = metrics_result.get("metrics", {})
            explanation_parts.append(f"Key metrics: {self._format_metrics(metrics)}")
        
        if visualization_result and visualization_result.get("success"):
            explanation_parts.append("Visual representation created to help you understand the data.")
        
        return " ".join(explanation_parts) if explanation_parts else "Data science analysis completed."
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics for narrative."""
        formatted = []
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                formatted.append(f"{key}: {value}")
        return ", ".join(formatted[:3])  # Limit to 3 metrics for readability
    
    async def analyze_aar_document(
        self,
        text_data: str,
        processing_result: Optional[Dict[str, Any]] = None,
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze After Action Review (AAR) document using agentic-forward pattern.
        
        This method performs critical reasoning to identify and extract AAR-specific sections:
        - Lessons learned
        - Risks identified
        - Recommendations
        - Timeline of events
        
        Uses LLM abstraction for critical reasoning, then guides service execution.
        
        Args:
            text_data: The AAR document text content
            processing_result: Optional previous processing results (from APGProcessorService)
            user_context: Optional user context for authorization
        
        Returns:
            Dict with structured AAR analysis:
            {
                "success": bool,
                "aar_data": {
                    "lessons_learned": List[str],
                    "risks": List[str],
                    "recommendations": List[str],
                    "timeline": List[Dict[str, Any]]
                },
                "reasoning": str,  # Agent's critical reasoning
                "extraction_strategy": Dict[str, Any]  # Strategy for service execution
            }
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("analyze_aar_document_start", success=True, details={
                "text_length": len(text_data) if text_data else 0
            })
            
            # Security validation (zero-trust)
            if user_context and self.security:
                try:
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None) or "anonymous",
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "insights", "analyze_aar"):
                        await self.record_health_metric("analyze_aar_document_access_denied", 1.0)
                        await self.log_operation_with_telemetry("analyze_aar_document_complete", success=False, details={
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions to analyze AAR documents")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            self.logger.info("🤖 Analyzing AAR document using agentic-forward pattern")
            
            # ✅ AGENTIC-FORWARD PATTERN: Critical reasoning first
            # Use LLM abstraction for strategic analysis of AAR document structure
            reasoning_prompt = f"""You are analyzing an After Action Review (AAR) document. Your task is to:
1. Identify the structure and key sections of the AAR
2. Determine the best strategy for extracting:
   - Lessons learned (what worked well, what didn't)
   - Risks identified (potential issues, concerns)
   - Recommendations (suggested improvements, actions)
   - Timeline of events (chronological sequence)

AAR Document Text:
{text_data[:5000]}  # Limit to first 5000 chars for prompt

Previous Processing Results:
{str(processing_result)[:1000] if processing_result else "None"}

Provide your analysis in JSON format:
{{
    "document_structure": {{
        "has_lessons_learned": bool,
        "has_risks": bool,
        "has_recommendations": bool,
        "has_timeline": bool,
        "sections_identified": List[str]
    }},
    "extraction_strategy": {{
        "lessons_learned_approach": str,
        "risks_approach": str,
        "recommendations_approach": str,
        "timeline_approach": str
    }},
    "reasoning": str
}}"""
            
            # Use LLM abstraction for critical reasoning
            reasoning_result = await self.llm_abstraction.generate_response(
                prompt=reasoning_prompt,
                system_prompt="You are an expert at analyzing After Action Review documents. Provide strategic analysis and extraction strategies.",
                response_format="json_object",
                max_tokens=2000
            )
            
            if not reasoning_result.get("success"):
                self.logger.error("❌ AAR analysis reasoning failed")
                return {
                    "success": False,
                    "error": "Failed to perform critical reasoning for AAR analysis",
                    "aar_data": {
                        "lessons_learned": [],
                        "risks": [],
                        "recommendations": [],
                        "timeline": []
                    }
                }
            
            # Parse reasoning result
            reasoning_text = reasoning_result.get("response_text", "{}")
            try:
                import json
                reasoning_data = json.loads(reasoning_text) if isinstance(reasoning_text, str) else reasoning_text
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to parse reasoning JSON: {e}")
                reasoning_data = {}
            
            # Extract strategy from reasoning
            extraction_strategy = reasoning_data.get("extraction_strategy", {})
            document_structure = reasoning_data.get("document_structure", {})
            reasoning_summary = reasoning_data.get("reasoning", "AAR document analyzed")
            
            # ✅ SERVICE EXECUTION: Use services based on agent's strategic decisions
            # The agent has determined the strategy, now services execute the extraction
            # For now, we'll use a simplified extraction based on the agent's reasoning
            # In a full implementation, this would guide APGProcessorService or InsightsGeneratorService
            
            # Extract lessons learned
            lessons_prompt = f"""Based on the AAR document analysis, extract lessons learned (what worked well, what didn't work, key takeaways).

AAR Document:
{text_data[:3000]}

Extraction Strategy: {extraction_strategy.get('lessons_learned_approach', 'general')}

Provide a JSON array of lessons learned, each as a string: ["lesson1", "lesson2", ...]"""
            
            lessons_result = await self.llm_abstraction.generate_response(
                prompt=lessons_prompt,
                system_prompt="Extract lessons learned from the AAR document as a JSON array of strings.",
                response_format="json_object",
                max_tokens=1000
            )
            
            lessons_learned = []
            if lessons_result.get("success"):
                try:
                    lessons_text = lessons_result.get("response_text", "{}")
                    lessons_data = json.loads(lessons_text) if isinstance(lessons_text, str) else lessons_text
                    lessons_learned = lessons_data.get("lessons_learned", []) or lessons_data.get("lessons", [])
                    if not isinstance(lessons_learned, list):
                        lessons_learned = [lessons_learned] if lessons_learned else []
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to parse lessons learned: {e}")
            
            # Extract risks
            risks_prompt = f"""Based on the AAR document analysis, extract identified risks (potential issues, concerns, problems).

AAR Document:
{text_data[:3000]}

Extraction Strategy: {extraction_strategy.get('risks_approach', 'general')}

Provide a JSON array of risks, each as a string: ["risk1", "risk2", ...]"""
            
            risks_result = await self.llm_abstraction.generate_response(
                prompt=risks_prompt,
                system_prompt="Extract risks from the AAR document as a JSON array of strings.",
                response_format="json_object",
                max_tokens=1000
            )
            
            risks = []
            if risks_result.get("success"):
                try:
                    risks_text = risks_result.get("response_text", "{}")
                    risks_data = json.loads(risks_text) if isinstance(risks_text, str) else risks_text
                    risks = risks_data.get("risks", [])
                    if not isinstance(risks, list):
                        risks = [risks] if risks else []
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to parse risks: {e}")
            
            # Extract recommendations
            recommendations_prompt = f"""Based on the AAR document analysis, extract recommendations (suggested improvements, actions to take).

AAR Document:
{text_data[:3000]}

Extraction Strategy: {extraction_strategy.get('recommendations_approach', 'general')}

Provide a JSON array of recommendations, each as a string: ["recommendation1", "recommendation2", ...]"""
            
            recommendations_result = await self.llm_abstraction.generate_response(
                prompt=recommendations_prompt,
                system_prompt="Extract recommendations from the AAR document as a JSON array of strings.",
                response_format="json_object",
                max_tokens=1000
            )
            
            recommendations = []
            if recommendations_result.get("success"):
                try:
                    rec_text = recommendations_result.get("response_text", "{}")
                    rec_data = json.loads(rec_text) if isinstance(rec_text, str) else rec_text
                    recommendations = rec_data.get("recommendations", [])
                    if not isinstance(recommendations, list):
                        recommendations = [recommendations] if recommendations else []
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to parse recommendations: {e}")
            
            # Extract timeline
            timeline_prompt = f"""Based on the AAR document analysis, extract timeline of events (chronological sequence).

AAR Document:
{text_data[:3000]}

Extraction Strategy: {extraction_strategy.get('timeline_approach', 'general')}

Provide a JSON array of timeline events, each as: {{"event": "description", "timestamp": "optional"}}"""
            
            timeline_result = await self.llm_abstraction.generate_response(
                prompt=timeline_prompt,
                system_prompt="Extract timeline from the AAR document as a JSON array of event objects.",
                response_format="json_object",
                max_tokens=1000
            )
            
            timeline = []
            if timeline_result.get("success"):
                try:
                    timeline_text = timeline_result.get("response_text", "{}")
                    timeline_data = json.loads(timeline_text) if isinstance(timeline_text, str) else timeline_text
                    timeline = timeline_data.get("timeline", []) or timeline_data.get("events", [])
                    if not isinstance(timeline, list):
                        timeline = [timeline] if timeline else []
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to parse timeline: {e}")
            
            # Compile AAR analysis result
            aar_data = {
                "lessons_learned": lessons_learned,
                "risks": risks,
                "recommendations": recommendations,
                "timeline": timeline
            }
            
            # Record health metric (success)
            await self.record_health_metric("analyze_aar_document_success", 1.0, {
                "lessons_count": len(lessons_learned),
                "risks_count": len(risks),
                "recommendations_count": len(recommendations),
                "timeline_count": len(timeline)
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("analyze_aar_document_complete", success=True, details={
                "lessons_count": len(lessons_learned),
                "risks_count": len(risks),
                "recommendations_count": len(recommendations),
                "timeline_count": len(timeline)
            })
            
            self.logger.info(f"✅ AAR analysis complete: {len(lessons_learned)} lessons, {len(risks)} risks, {len(recommendations)} recommendations, {len(timeline)} timeline events")
            
            return {
                "success": True,
                "aar_data": aar_data,
                "reasoning": reasoning_summary,
                "extraction_strategy": extraction_strategy,
                "document_structure": document_structure
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "analyze_aar_document")
            
            # Record health metric (failure)
            await self.record_health_metric("analyze_aar_document_failed", 1.0, {
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("analyze_aar_document_complete", success=False, details={
                "error": str(e)
            })
            
            self.logger.error(f"❌ AAR analysis failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            return {
                "success": False,
                "error": str(e),
                "aar_data": {
                    "lessons_learned": [],
                    "risks": [],
                    "recommendations": [],
                    "timeline": []
                }
            }

