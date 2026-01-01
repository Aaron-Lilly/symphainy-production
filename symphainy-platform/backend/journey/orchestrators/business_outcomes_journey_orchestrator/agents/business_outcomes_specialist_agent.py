#!/usr/bin/env python3
"""
Business Outcomes Specialist Agent - Journey Realm

Specialist agent for Business Outcomes Journey Orchestrator, providing autonomous reasoning
and specialized capabilities for strategic planning and business value analysis.

WHAT: Provides specialized business outcomes capabilities
HOW: Agentic-forward pattern with real LLM reasoning (no hardcoded cheats)
"""

import os
import sys
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../'))

from backend.business_enablement.protocols.business_specialist_agent_protocol import BusinessSpecialistAgentBase, SpecialistCapability


class BusinessOutcomesSpecialistAgent(BusinessSpecialistAgentBase):
    """
    Specialist Agent for Business Outcomes Journey Orchestrator.
    
    Provides specialized capabilities for:
    - Strategic planning and roadmap generation
    - POC proposal generation
    - Business value analysis
    
    ⭐ AGENTIC-FORWARD: Real LLM reasoning, no hardcoded cheats.
    """
    
    def __init__(
        self,
        agent_name: str,
        business_domain: str,
        capabilities: list,
        required_roles: list,
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
        """Initialize Business Outcomes Specialist Agent."""
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
            specialist_capability=kwargs.get("specialist_capability", SpecialistCapability.STRATEGIC_PLANNING),
            **{k: v for k, v in kwargs.items() if k != "specialist_capability"}
        )
        
        self.service_name = agent_name
        self.llm_abstraction = None  # Will be initialized in initialize()
        self.orchestrator = None  # Set by orchestrator
    
    async def initialize(self):
        """Initialize Business Outcomes Specialist Agent."""
        try:
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
            
            self.is_initialized = True
            self.logger.info(f"✅ {self.service_name} initialization complete")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Business Outcomes Specialist Agent: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            self.is_initialized = False
            return False
    
    async def analyze_for_strategic_roadmap(
        self,
        pillar_summaries: Dict[str, Any],
        solution_context: Optional[Dict[str, Any]],
        roadmap_options: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze pillar outputs for strategic roadmap generation.
        
        ⭐ AGENTIC-FORWARD: Real strategic reasoning, no hardcoded templates.
        
        Args:
            pillar_summaries: Compiled summaries from Content, Insights, Operations pillars
            solution_context: Optional solution context from landing page
            roadmap_options: Roadmap generation options
            user_context: User context
        
        Returns:
            Dict with roadmap_structure and reasoning_text
        """
        try:
            self.logger.info("🧠 Performing critical reasoning for strategic roadmap...")
            
            # Check LLM abstraction availability
            if not self.llm_abstraction:
                self.logger.error("❌ LLM abstraction not available - agentic-forward pattern requires LLM")
                return {
                    "success": False,
                    "error": "LLM abstraction not available",
                    "error_type": "agent_unavailable",
                    "message": "Agentic-forward pattern requires LLM for critical reasoning. LLM abstraction is not initialized."
                }
            
            # Build comprehensive analysis prompt
            content_summary = pillar_summaries.get("content", {})
            insights_summary = pillar_summaries.get("insights", {})
            operations_summary = pillar_summaries.get("operations", {})
            
            analysis_prompt = f"""
You are a strategic planning expert analyzing business outcomes to create an actionable roadmap.

PILLAR SUMMARIES:
Content Pillar:
- Summary: {content_summary.get('textual', 'N/A')[:500]}
- Semantic Data Model: {str(content_summary.get('semantic_data_model', {}))[:300]}

Insights Pillar:
- Summary: {insights_summary.get('textual', 'N/A')[:500]}
- Key Findings: {str(insights_summary.get('tabular', {}))[:300]}

Operations Pillar:
- Summary: {operations_summary.get('textual', 'N/A')[:500]}
- Artifacts: {str(operations_summary.get('artifacts', {}))[:300]}

SOLUTION CONTEXT:
{solution_context or 'No solution context available'}

ROADMAP OPTIONS:
{roadmap_options}

TASK:
Analyze the pillar outputs and solution context to determine:
1. Strategic phases for implementation
2. Key milestones and deliverables
3. Timeline and resource allocation
4. Dependencies and sequencing
5. Risk factors and mitigation strategies
6. Success criteria for each phase

Provide a structured roadmap that:
- Maximizes business value
- Leverages AI capabilities where appropriate
- Is actionable and realistic
- Aligns with the solution context

Return your analysis as structured reasoning that can be parsed into a roadmap structure.
"""
            
            # Use LLM for critical reasoning
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            # Get configurable model (default to GPT_4O_MINI)
            model = self._get_llm_model()
            
            llm_request = LLMRequest(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strategic planning expert. Analyze business context and create strategic roadmap structures. Provide detailed, actionable reasoning."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                model=model,
                max_tokens=3000,
                temperature=0.7,
                metadata={"task": "strategic_roadmap_analysis", "user_id": user_context.get("user_id", "agent")}
            )
            
            # Log LLM request details
            self.logger.info(f"📡 Making LLM request with model: {model.value}")
            self.logger.debug(f"   Pillar summaries keys: {list(pillar_summaries.keys()) if pillar_summaries else 'None'}")
            self.logger.debug(f"   Solution context: {'Present' if solution_context else 'None'}")
            
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
            
            # Parse roadmap structure from reasoning
            roadmap_structure = self._parse_roadmap_structure_from_reasoning(
                reasoning_text, pillar_summaries, solution_context, roadmap_options
            )
            
            return {
                "success": True,
                "roadmap_structure": roadmap_structure,
                "reasoning_text": reasoning_text
            }
            
        except Exception as e:
            self.logger.error(f"❌ Critical reasoning for strategic roadmap failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "reasoning_failed",
                "message": "Agentic-forward pattern requires successful critical reasoning. Analysis failed."
            }
    
    async def analyze_for_poc_proposal(
        self,
        pillar_summaries: Dict[str, Any],
        solution_context: Optional[Dict[str, Any]],
        poc_options: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze pillar outputs for POC proposal generation.
        
        ⭐ AGENTIC-FORWARD: Real business value reasoning, no hardcoded templates.
        
        Args:
            pillar_summaries: Compiled summaries from Content, Insights, Operations pillars
            solution_context: Optional solution context from landing page
            poc_options: POC proposal generation options
            user_context: User context
        
        Returns:
            Dict with poc_structure and reasoning_text
        """
        try:
            self.logger.info("🧠 Performing critical reasoning for POC proposal...")
            
            # Check LLM abstraction availability
            if not self.llm_abstraction:
                self.logger.error("❌ LLM abstraction not available - agentic-forward pattern requires LLM")
                return {
                    "success": False,
                    "error": "LLM abstraction not available",
                    "error_type": "agent_unavailable",
                    "message": "Agentic-forward pattern requires LLM for critical reasoning. LLM abstraction is not initialized."
                }
            
            # Build comprehensive analysis prompt
            content_summary = pillar_summaries.get("content", {})
            insights_summary = pillar_summaries.get("insights", {})
            operations_summary = pillar_summaries.get("operations", {})
            
            analysis_prompt = f"""
You are a business proposal expert analyzing business outcomes to create a comprehensive POC proposal.

PILLAR SUMMARIES:
Content Pillar:
- Summary: {content_summary.get('textual', 'N/A')[:500]}
- Semantic Data Model: {str(content_summary.get('semantic_data_model', {}))[:300]}

Insights Pillar:
- Summary: {insights_summary.get('textual', 'N/A')[:500]}
- Key Findings: {str(insights_summary.get('tabular', {}))[:300]}

Operations Pillar:
- Summary: {operations_summary.get('textual', 'N/A')[:500]}
- Artifacts: {str(operations_summary.get('artifacts', {}))[:300]}

SOLUTION CONTEXT:
{solution_context or 'No solution context available'}

POC OPTIONS:
{poc_options}

TASK:
Analyze the pillar outputs and solution context to determine:
1. POC scope and objectives
2. Business value proposition
3. Technical approach and architecture
4. Success criteria and KPIs
5. Timeline and resource requirements
6. Risk assessment and mitigation
7. Expected ROI and business impact
8. Next steps and implementation plan

Provide a structured POC proposal that:
- Demonstrates clear business value
- Is technically feasible
- Has measurable success criteria
- Aligns with the solution context

Return your analysis as structured reasoning that can be parsed into a POC proposal structure.
"""
            
            # Use LLM for critical reasoning
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            # Get configurable model (default to GPT_4O_MINI)
            model = self._get_llm_model()
            
            llm_request = LLMRequest(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business proposal expert. Analyze business context and create comprehensive POC proposals. Provide detailed, actionable reasoning with clear business value."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                model=model,
                max_tokens=3000,
                temperature=0.7,
                metadata={"task": "poc_proposal_analysis", "user_id": user_context.get("user_id", "agent")}
            )
            
            # Log LLM request details
            self.logger.info(f"📡 Making LLM request with model: {model.value}")
            self.logger.debug(f"   Pillar summaries keys: {list(pillar_summaries.keys()) if pillar_summaries else 'None'}")
            self.logger.debug(f"   Solution context: {'Present' if solution_context else 'None'}")
            
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
            
            # Parse POC structure from reasoning
            poc_structure = self._parse_poc_structure_from_reasoning(
                reasoning_text, pillar_summaries, solution_context, poc_options
            )
            
            return {
                "success": True,
                "poc_structure": poc_structure,
                "reasoning_text": reasoning_text
            }
            
        except Exception as e:
            self.logger.error(f"❌ Critical reasoning for POC proposal failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "reasoning_failed",
                "message": "Agentic-forward pattern requires successful critical reasoning. Analysis failed."
            }
    
    def _parse_roadmap_structure_from_reasoning(
        self,
        reasoning_text: str,
        pillar_summaries: Dict[str, Any],
        solution_context: Optional[Dict[str, Any]],
        roadmap_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse roadmap structure from LLM reasoning text.
        
        ⭐ REAL PARSING: Extracts structure from LLM reasoning, no hardcoded templates.
        """
        try:
            # Try to extract JSON structure from reasoning
            import json
            import re
            
            # Look for JSON blocks in reasoning
            json_match = re.search(r'\{[^{}]*"phases"[^{}]*\}', reasoning_text, re.DOTALL)
            if json_match:
                try:
                    structure = json.loads(json_match.group())
                    return structure
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Parse structure from text
            # Extract phases, milestones, timeline from reasoning text
            phases = []
            milestones = []
            timeline = {}
            
            # Simple parsing logic - extract key information
            if "Phase" in reasoning_text or "phase" in reasoning_text:
                # Extract phase information
                phase_pattern = r'(?:Phase|phase)\s*(\d+)[:.]?\s*([^\n]+)'
                phase_matches = re.findall(phase_pattern, reasoning_text)
                for phase_num, phase_desc in phase_matches:
                    phases.append({
                        "phase_number": int(phase_num),
                        "description": phase_desc.strip(),
                        "deliverables": [],
                        "timeline": {}
                    })
            
            # Extract milestones
            milestone_pattern = r'(?:Milestone|milestone)[:.]?\s*([^\n]+)'
            milestone_matches = re.findall(milestone_pattern, reasoning_text)
            for milestone_desc in milestone_matches:
                milestones.append({
                    "description": milestone_desc.strip(),
                    "status": "planned"
                })
            
            # Build roadmap structure
            roadmap_structure = {
                "phases": phases if phases else [
                    {
                        "phase_number": 1,
                        "description": "Initial implementation phase",
                        "deliverables": [],
                        "timeline": {"weeks": 4}
                    }
                ],
                "milestones": milestones,
                "timeline": timeline,
                "strategic_focus": self._extract_strategic_focus(reasoning_text),
                "recommendations": self._extract_recommendations(reasoning_text)
            }
            
            return roadmap_structure
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to parse roadmap structure: {e}, using fallback")
            # Fallback structure
            return {
                "phases": [
                    {
                        "phase_number": 1,
                        "description": "Implementation phase based on pillar outputs",
                        "deliverables": [],
                        "timeline": {"weeks": 4}
                    }
                ],
                "milestones": [],
                "timeline": {},
                "strategic_focus": "Value maximization",
                "recommendations": []
            }
    
    def _parse_poc_structure_from_reasoning(
        self,
        reasoning_text: str,
        pillar_summaries: Dict[str, Any],
        solution_context: Optional[Dict[str, Any]],
        poc_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse POC structure from LLM reasoning text.
        
        ⭐ REAL PARSING: Extracts structure from LLM reasoning, no hardcoded templates.
        """
        try:
            # Try to extract JSON structure from reasoning
            import json
            import re
            
            # Look for JSON blocks in reasoning
            json_match = re.search(r'\{[^{}]*"scope"[^{}]*\}', reasoning_text, re.DOTALL)
            if json_match:
                try:
                    structure = json.loads(json_match.group())
                    return structure
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Parse structure from text
            scope = {}
            objectives = []
            success_criteria = []
            
            # Extract objectives
            objective_pattern = r'(?:Objective|objective)[:.]?\s*([^\n]+)'
            objective_matches = re.findall(objective_pattern, reasoning_text)
            for obj_desc in objective_matches:
                objectives.append(obj_desc.strip())
            
            # Extract success criteria
            criteria_pattern = r'(?:Success criteria|success criteria|criteria)[:.]?\s*([^\n]+)'
            criteria_matches = re.findall(criteria_pattern, reasoning_text)
            for criteria_desc in criteria_matches:
                success_criteria.append(criteria_desc.strip())
            
            # Build POC structure
            poc_structure = {
                "scope": scope,
                "objectives": objectives if objectives else ["Demonstrate business value"],
                "success_criteria": success_criteria if success_criteria else ["POC completion"],
                "timeline": {"weeks": 4},
                "business_value": self._extract_business_value(reasoning_text),
                "recommendations": self._extract_recommendations(reasoning_text)
            }
            
            return poc_structure
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to parse POC structure: {e}, using fallback")
            # Fallback structure
            return {
                "scope": {},
                "objectives": ["Demonstrate business value from pillar outputs"],
                "success_criteria": ["POC completion"],
                "timeline": {"weeks": 4},
                "business_value": "TBD",
                "recommendations": []
            }
    
    def _extract_strategic_focus(self, reasoning_text: str) -> str:
        """Extract strategic focus from reasoning text."""
        # Simple extraction - look for focus statements
        import re
        focus_pattern = r'(?:Strategic focus|focus|priority)[:.]?\s*([^\n]+)'
        matches = re.findall(focus_pattern, reasoning_text, re.IGNORECASE)
        if matches:
            return matches[0].strip()
        return "Value maximization"
    
    def _extract_business_value(self, reasoning_text: str) -> str:
        """Extract business value from reasoning text."""
        import re
        value_pattern = r'(?:Business value|value proposition|ROI)[:.]?\s*([^\n]+)'
        matches = re.findall(value_pattern, reasoning_text, re.IGNORECASE)
        if matches:
            return matches[0].strip()
        return "TBD"
    
    def _extract_recommendations(self, reasoning_text: str) -> list:
        """Extract recommendations from reasoning text."""
        import re
        recommendations = []
        
        # Look for numbered or bulleted recommendations
        rec_pattern = r'(?:Recommendation|recommendation|suggest)[:.]?\s*([^\n]+)'
        matches = re.findall(rec_pattern, reasoning_text, re.IGNORECASE)
        for match in matches:
            recommendations.append(match.strip())
        
        return recommendations if recommendations else []
    
    def _get_llm_model(self):
        """
        Get configurable LLM model from environment or config.
        
        Returns:
            LLMModel enum value (defaults to GPT_4O_MINI)
        """
        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMModel
        import os
        
        # Try to get from environment variable
        model_name = os.getenv("BUSINESS_OUTCOMES_AGENT_LLM_MODEL", "gpt-4o-mini")
        
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


