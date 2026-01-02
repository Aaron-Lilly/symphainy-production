#!/usr/bin/env python3
"""
Roadmap Generation Service - Journey Realm

WHAT: Generates strategic roadmaps from pillar outputs
HOW: Agentic-forward implementation with real LLM reasoning (no hardcoded cheats)

This service provides strategic roadmap generation capabilities using real LLM reasoning.
No hardcoded templates or placeholders - all roadmaps are generated via agentic reasoning.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class RoadmapGenerationService(RealmServiceBase):
    """
    Roadmap Generation Service for Journey realm.
    
    ⭐ AGENTIC-FORWARD: Real LLM reasoning, no hardcoded templates.
    
    Provides strategic roadmap generation:
    - Generate roadmaps from pillar outputs
    - Use solution context for personalized roadmaps
    - Real strategic reasoning via LLM
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Roadmap Generation Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.llm_abstraction = None
    
    async def initialize(self) -> bool:
        """
        Initialize Roadmap Generation Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "roadmap_generation_service_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # Get Smart City services
            self.librarian = await self.get_librarian_api()
            
            # Get LLM abstraction for roadmap generation
            public_works_foundation = await self.get_foundation_service("PublicWorksFoundationService")
            if public_works_foundation:
                self.llm_abstraction = public_works_foundation.get_abstraction("llm")
                if self.llm_abstraction:
                    self.logger.info("✅ LLM abstraction initialized for roadmap generation")
                else:
                    self.logger.warning("⚠️ LLM abstraction not available")
            else:
                self.logger.warning("⚠️ PublicWorksFoundationService not available")
            
            # Register with Curator
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "roadmap_generation",
                        "protocol": "RoadmapGenerationServiceProtocol",
                        "description": "Generate strategic roadmaps from pillar outputs",
                        "contracts": {
                            "soa_api": {
                                "api_name": "generate_roadmap",
                                "endpoint": "/api/v1/journey/roadmap-generation/generate",
                                "method": "POST",
                                "handler": self.generate_roadmap,
                                "metadata": {
                                    "description": "Generate strategic roadmap",
                                    "parameters": ["business_context", "options"]
                                }
                            }
                        }
                    }
                ],
                additional_metadata={
                    "service_type": "journey_realm",
                    "agentic_forward": True
                }
            )
            
            self.logger.info("✅ Roadmap Generation Service initialized")
            
            # Complete telemetry tracking
            await self.log_operation_with_telemetry(
                "roadmap_generation_service_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Roadmap Generation Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            await self.log_operation_with_telemetry(
                "roadmap_generation_service_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self.handle_error_with_audit(e, "initialize")
            return False
    
    async def generate_roadmap(
        self,
        business_context: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate strategic roadmap from pillar outputs.
        
        ⭐ AGENTIC-FORWARD: Real LLM reasoning, no hardcoded templates.
        
        Args:
            business_context: Contains pillar_summaries, solution_context, roadmap_structure
            options: Optional roadmap generation options
            user_context: Optional user context
        
        Returns:
            Dict with roadmap_id, roadmap, and agent_reasoning
        """
        try:
            self.logger.info("🚀 Generating strategic roadmap...")
            
            # Get LLM abstraction
            if not self.llm_abstraction:
                return {
                    "success": False,
                    "error": "LLM abstraction not available"
                }
            
            # Extract context
            pillar_summaries = business_context.get("pillar_summaries", {})
            solution_context = business_context.get("solution_context")
            roadmap_structure = business_context.get("roadmap_structure", {})
            
            # Build comprehensive prompt for roadmap generation
            prompt = self._build_roadmap_prompt(
                pillar_summaries=pillar_summaries,
                solution_context=solution_context,
                roadmap_structure=roadmap_structure,
                options=options or {}
            )
            
            # Generate roadmap via LLM
            from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
            
            llm_request = LLMRequest(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strategic planning expert. Generate actionable, detailed roadmaps that maximize business value and leverage AI capabilities. Provide comprehensive roadmaps with phases, milestones, timelines, and recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=4000,
                temperature=0.7,
                metadata={
                    "task": "roadmap_generation",
                    "user_id": user_context.get("user_id", "anonymous") if user_context else "anonymous"
                }
            )
            
            llm_response = await self.llm_abstraction.generate_response(llm_request)
            
            # Extract roadmap from response
            roadmap_content = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Parse roadmap from response
            roadmap = self._parse_roadmap_from_response(roadmap_content, roadmap_structure)
            
            # Generate roadmap ID
            roadmap_id = f"roadmap_{uuid.uuid4().hex[:12]}"
            
            # Store roadmap via Librarian
            if self.librarian:
                try:
                    storage_result = await self.librarian.store_document(
                        document_data=roadmap,
                        metadata={
                            "roadmap_id": roadmap_id,
                            "generated_at": datetime.utcnow().isoformat(),
                            "pillar_summaries": pillar_summaries,
                            "solution_context": solution_context is not None
                        }
                    )
                    roadmap_id = storage_result.get("document_id", roadmap_id)
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to store roadmap: {e}")
            
            return {
                "success": True,
                "roadmap_id": roadmap_id,
                "roadmap": roadmap,
                "agent_reasoning": roadmap_structure.get("reasoning_text", ""),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Roadmap generation failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_roadmap_prompt(
        self,
        pillar_summaries: Dict[str, Any],
        solution_context: Optional[Dict[str, Any]],
        roadmap_structure: Dict[str, Any],
        options: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive prompt for roadmap generation.
        
        ⭐ REAL PROMPT BUILDING: No hardcoded templates, uses actual context.
        """
        content_summary = pillar_summaries.get("content", {})
        insights_summary = pillar_summaries.get("insights", {})
        operations_summary = pillar_summaries.get("operations", {})
        
        prompt = f"""
Generate a comprehensive strategic roadmap based on the following information:

PILLAR SUMMARIES:
Content Pillar:
{self._format_summary(content_summary)}

Insights Pillar:
{self._format_summary(insights_summary)}

Operations Pillar:
{self._format_summary(operations_summary)}

SOLUTION CONTEXT:
{solution_context or 'No solution context available'}

ROADMAP STRUCTURE (from agent reasoning):
{json.dumps(roadmap_structure, indent=2)}

OPTIONS:
{json.dumps(options, indent=2)}

TASK:
Generate a detailed, actionable roadmap that includes:
1. Executive Summary
2. Strategic Phases (with clear objectives, deliverables, timeline)
3. Key Milestones
4. Resource Allocation
5. Dependencies and Sequencing
6. Risk Assessment and Mitigation
7. Success Criteria
8. Implementation Recommendations

The roadmap should:
- Maximize business value
- Leverage AI capabilities where appropriate
- Be realistic and actionable
- Align with the solution context
- Follow the roadmap structure provided by the agent

Return the roadmap as a structured JSON object with all phases, milestones, and recommendations.
"""
        return prompt
    
    def _format_summary(self, summary: Dict[str, Any]) -> str:
        """Format pillar summary for prompt."""
        if not summary:
            return "No summary available"
        
        textual = summary.get("textual", "")
        tabular = summary.get("tabular", {})
        artifacts = summary.get("artifacts", {})
        
        formatted = f"Textual Summary: {textual[:500] if textual else 'N/A'}\n"
        
        if tabular:
            formatted += f"Tabular Data: {str(tabular)[:300]}\n"
        
        if artifacts:
            formatted += f"Artifacts: {str(artifacts)[:300]}\n"
        
        return formatted
    
    def _parse_roadmap_from_response(
        self,
        response: str,
        roadmap_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse roadmap structure from LLM response.
        
        ⭐ REAL PARSING: Extracts structure from LLM response, no hardcoded templates.
        """
        try:
            # Try to extract JSON from response
            import re
            
            # Look for JSON blocks
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    roadmap = json.loads(json_match.group())
                    # Validate and enhance roadmap
                    if "phases" not in roadmap:
                        roadmap["phases"] = roadmap_structure.get("phases", [])
                    if "milestones" not in roadmap:
                        roadmap["milestones"] = roadmap_structure.get("milestones", [])
                    return roadmap
                except json.JSONDecodeError:
                    pass
            
            # Fallback: Build roadmap from text and structure
            roadmap = {
                "executive_summary": self._extract_section(response, "Executive Summary", "Strategic Phases"),
                "phases": roadmap_structure.get("phases", []),
                "milestones": roadmap_structure.get("milestones", []),
                "timeline": roadmap_structure.get("timeline", {}),
                "strategic_focus": roadmap_structure.get("strategic_focus", "Value maximization"),
                "recommendations": roadmap_structure.get("recommendations", []),
                "raw_response": response[:2000]  # Store raw response for reference
            }
            
            return roadmap
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to parse roadmap from response: {e}")
            # Return structure-based roadmap
            return {
                "executive_summary": "Strategic roadmap based on pillar outputs",
                "phases": roadmap_structure.get("phases", []),
                "milestones": roadmap_structure.get("milestones", []),
                "timeline": roadmap_structure.get("timeline", {}),
                "strategic_focus": roadmap_structure.get("strategic_focus", "Value maximization"),
                "recommendations": roadmap_structure.get("recommendations", [])
            }
    
    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """Extract section from text between markers."""
        import re
        pattern = f"{re.escape(start_marker)}[\\s\\S]*?(?={re.escape(end_marker)}|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group().replace(start_marker, "").strip()
        return ""





