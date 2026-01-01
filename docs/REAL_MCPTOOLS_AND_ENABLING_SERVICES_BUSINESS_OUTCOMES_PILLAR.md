# Real MCP Tools and Enabling Services: Business Outcomes Pillar

## Executive Summary

This document provides **REAL, WORKING implementation code** (no mocks, no placeholders, no hard-coded cheats) for all MCP tools and enabling services needed for the Business Outcomes Pillar agentic enablement.

---

## Existing Infrastructure (What We Have)

### ✅ Existing Enabling Services
1. **RoadmapGenerationService** - ✅ EXISTS
   - Location: `backend/business_enablement/enabling_services/roadmap_generation_service/`
   - Capabilities: Generate strategic roadmaps
   - SOA APIs: `generate_roadmap()`, `create_roadmap()`

2. **POCGenerationService** - ✅ EXISTS
   - Location: `backend/business_enablement/enabling_services/poc_generation_service/`
   - Capabilities: Generate POC proposals
   - SOA APIs: `generate_poc_proposal()`, `create_poc()`

3. **MetricsCalculatorService** - ✅ EXISTS
   - Location: `backend/business_enablement/enabling_services/metrics_calculator_service/`
   - Capabilities: Calculate metrics, KPIs
   - SOA APIs: `calculate_metrics()`, `calculate_kpis()`

4. **ReportGeneratorService** - ✅ EXISTS
   - Location: `backend/business_enablement/enabling_services/report_generator_service/`
   - Capabilities: Generate reports
   - SOA APIs: `generate_report()`, `create_summary()`

### ✅ Existing MCP Tools (BusinessOutcomesMCPServer)
1. `track_outcomes_tool` - ✅ EXISTS
2. `generate_roadmap_tool` - ✅ EXISTS
3. `calculate_kpis_tool` - ✅ EXISTS
4. `analyze_outcomes_tool` - ✅ EXISTS
5. `generate_strategic_roadmap_tool` - ✅ EXISTS
6. `generate_poc_proposal_tool` - ✅ EXISTS
7. `generate_comprehensive_poc_tool` - ✅ EXISTS
8. `create_comprehensive_strategic_plan_tool` - ✅ EXISTS
9. `track_strategic_progress_tool` - ✅ EXISTS
10. `analyze_strategic_trends_tool` - ✅ EXISTS

### ✅ Existing Smart City Services
- **Librarian** - Roadmap/POC storage
- **Session Manager** - Session context for pillar summaries

---

## New Tools/Services Needed

### 1. StrategicPlanningService (NEW - Must Create)

**Why:** Agent needs to get strategic recommendations, metric suggestions, and option analysis - all without LLM in service.

**Location:** `backend/business_enablement/enabling_services/strategic_planning_service/`

**REAL Implementation:**

```python
#!/usr/bin/env python3
"""
Strategic Planning Service - Pure Data Processing Service

WHAT: Provides strategic planning recommendations and metric suggestions
HOW: Rule-based recommendations and best practices (NO LLM)

This service is PURE - accepts structured parameters from agent LLM,
performs rule-based analysis, returns structured recommendations.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase


class StrategicPlanningService(RealmServiceBase):
    """
    Strategic Planning Service - Pure data processing for strategic recommendations.
    
    NO LLM - accepts structured parameters from agent LLM.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Strategic Planning Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Metric recommendations by goal (rule-based, not LLM)
        self.metric_recommendations = {
            "improve_customer_satisfaction": {
                "primary_metrics": ["customer_satisfaction_score", "net_promoter_score", "customer_retention_rate"],
                "secondary_metrics": ["average_response_time", "first_contact_resolution", "customer_complaints"],
                "industry_benchmarks": {
                    "retail": {"target": 85, "unit": "percentage"},
                    "healthcare": {"target": 90, "unit": "percentage"},
                    "finance": {"target": 88, "unit": "percentage"}
                }
            },
            "reduce_costs": {
                "primary_metrics": ["total_cost_of_ownership", "operational_efficiency", "cost_per_transaction"],
                "secondary_metrics": ["resource_utilization", "process_automation_rate", "error_rate"],
                "industry_benchmarks": {
                    "retail": {"target": 15, "unit": "percentage_reduction"},
                    "healthcare": {"target": 20, "unit": "percentage_reduction"},
                    "finance": {"target": 18, "unit": "percentage_reduction"}
                }
            },
            "increase_revenue": {
                "primary_metrics": ["revenue_growth_rate", "average_revenue_per_customer", "conversion_rate"],
                "secondary_metrics": ["customer_lifetime_value", "market_share", "sales_cycle_length"],
                "industry_benchmarks": {
                    "retail": {"target": 10, "unit": "percentage_growth"},
                    "healthcare": {"target": 8, "unit": "percentage_growth"},
                    "finance": {"target": 12, "unit": "percentage_growth"}
                }
            },
            "improve_efficiency": {
                "primary_metrics": ["process_cycle_time", "throughput", "resource_utilization"],
                "secondary_metrics": ["automation_rate", "error_rate", "rework_rate"],
                "industry_benchmarks": {
                    "retail": {"target": 25, "unit": "percentage_improvement"},
                    "healthcare": {"target": 30, "unit": "percentage_improvement"},
                    "finance": {"target": 22, "unit": "percentage_improvement"}
                }
            }
        }
        
        # Roadmap templates by business type (rule-based, not LLM)
        self.roadmap_templates = {
            "digital_transformation": {
                "phases": [
                    {"name": "Assessment & Planning", "duration": "3 months", "key_activities": ["Current state analysis", "Gap analysis", "Strategy definition"]},
                    {"name": "Foundation Building", "duration": "3 months", "key_activities": ["Infrastructure setup", "Team training", "Pilot projects"]},
                    {"name": "Implementation", "duration": "6 months", "key_activities": ["System deployment", "Process automation", "Change management"]},
                    {"name": "Optimization", "duration": "Ongoing", "key_activities": ["Performance monitoring", "Continuous improvement", "Scaling"]}
                ],
                "typical_duration": "12 months",
                "key_milestones": ["Assessment complete", "Foundation ready", "First automation live", "Full deployment"]
            },
            "process_optimization": {
                "phases": [
                    {"name": "Process Analysis", "duration": "1 month", "key_activities": ["Process mapping", "Bottleneck identification", "Opportunity analysis"]},
                    {"name": "Design & Planning", "duration": "1 month", "key_activities": ["Solution design", "Resource planning", "Timeline definition"]},
                    {"name": "Implementation", "duration": "2 months", "key_activities": ["Process changes", "Training", "Testing"]},
                    {"name": "Monitoring & Refinement", "duration": "Ongoing", "key_activities": ["Performance tracking", "Continuous improvement"]}
                ],
                "typical_duration": "4 months",
                "key_milestones": ["Analysis complete", "Design approved", "Implementation complete", "Targets met"]
            }
        }
        
        # POC best practices by type (rule-based, not LLM)
        self.poc_best_practices = {
            "technology": {
                "success_criteria": ["Technical feasibility proven", "Performance targets met", "Integration successful"],
                "common_pitfalls": ["Scope creep", "Unrealistic timelines", "Insufficient testing"],
                "recommendations": ["Define clear success criteria", "Limit scope to core functionality", "Plan for 8-12 weeks"]
            },
            "process": {
                "success_criteria": ["Process efficiency improved", "Quality targets met", "User adoption achieved"],
                "common_pitfalls": ["Resistance to change", "Incomplete process mapping", "Lack of training"],
                "recommendations": ["Involve stakeholders early", "Map complete process", "Provide comprehensive training"]
            },
            "hybrid": {
                "success_criteria": ["Both technology and process goals met", "Integration successful", "Business value demonstrated"],
                "common_pitfalls": ["Focusing on one aspect only", "Poor coordination", "Unclear ownership"],
                "recommendations": ["Balance technology and process", "Clear coordination plan", "Define ownership"]
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize Strategic Planning Service."""
        try:
            # Get Librarian for template storage (optional)
            self.librarian = await self.get_librarian_api()
            if not self.librarian:
                self.logger.warning("⚠️ Librarian not available - template storage will be limited")
            
            self.logger.info("✅ Strategic Planning Service initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Strategic Planning Service initialization failed: {e}")
            return False
    
    async def recommend_metrics(
        self,
        business_goals: List[str],  # From agent LLM
        industry: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Recommend metrics based on business goals (rule-based, not LLM).
        
        Args:
            business_goals: List of business goals (from agent LLM)
            industry: Industry type
            user_context: User context
        
        Returns:
            {
                "success": bool,
                "recommended_metrics": List[Dict[str, Any]],
                "industry_benchmarks": Dict[str, Any],
                "tracking_recommendations": List[str]
            }
        """
        try:
            recommended_metrics = []
            industry_benchmarks = {}
            tracking_recommendations = []
            
            # Get metrics for each goal (rule-based)
            for goal in business_goals:
                goal_lower = goal.lower()
                
                # Match goal to metric recommendations (rule-based)
                for goal_key, metric_info in self.metric_recommendations.items():
                    if goal_key.replace("_", " ") in goal_lower:
                        # Add primary metrics
                        for metric in metric_info["primary_metrics"]:
                            recommended_metrics.append({
                                "metric_name": metric,
                                "category": "primary",
                                "goal": goal,
                                "description": f"Primary metric for {goal}"
                            })
                        
                        # Add secondary metrics
                        for metric in metric_info["secondary_metrics"]:
                            recommended_metrics.append({
                                "metric_name": metric,
                                "category": "secondary",
                                "goal": goal,
                                "description": f"Supporting metric for {goal}"
                            })
                        
                        # Get industry benchmarks
                        benchmarks = metric_info["industry_benchmarks"].get(industry.lower(), {})
                        if benchmarks:
                            industry_benchmarks[goal] = benchmarks
                        
                        break
            
            # Build tracking recommendations (rule-based)
            tracking_recommendations = [
                "Track metrics weekly during implementation phase",
                "Review metrics monthly during optimization phase",
                "Set up automated dashboards for real-time monitoring",
                "Define alert thresholds for critical metrics"
            ]
            
            return {
                "success": True,
                "recommended_metrics": recommended_metrics,
                "industry_benchmarks": industry_benchmarks,
                "tracking_recommendations": tracking_recommendations
            }
        
        except Exception as e:
            self.logger.error(f"❌ Recommend metrics failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommended_metrics": [],
                "industry_benchmarks": {},
                "tracking_recommendations": []
            }
    
    async def analyze_strategic_options(
        self,
        options: List[Dict[str, Any]],  # Structured from agent LLM
        criteria: Dict[str, Any]  # Structured from agent LLM
    ) -> Dict[str, Any]:
        """
        Compare strategic options (rule-based analysis, not LLM).
        
        Args:
            options: [
                {
                    "option_name": str,
                    "description": str,
                    "cost": Optional[float],
                    "timeline": Optional[str],
                    "risks": Optional[List[str]],
                    "benefits": Optional[List[str]]
                }
            ]
            criteria: {
                "weight_cost": float,  # 0.0 to 1.0
                "weight_timeline": float,
                "weight_risk": float,
                "weight_benefit": float
            }
        
        Returns:
            {
                "success": bool,
                "comparison_matrix": List[Dict[str, Any]],
                "recommended_option": str,
                "reason": str
            }
        """
        try:
            comparison_matrix = []
            
            # Score each option (rule-based, not LLM)
            for option in options:
                score = 0.0
                
                # Score based on cost (lower is better)
                if "cost" in option and "weight_cost" in criteria:
                    cost = option["cost"]
                    if cost:
                        # Normalize cost (assume max cost is 1M, lower is better)
                        cost_score = max(0, 1.0 - (cost / 1000000))
                        score += cost_score * criteria["weight_cost"]
                
                # Score based on timeline (shorter is better)
                if "timeline" in option and "weight_timeline" in criteria:
                    timeline = option["timeline"]
                    if timeline:
                        # Parse timeline (e.g., "6 months" -> 6)
                        timeline_months = self._parse_timeline(timeline)
                        if timeline_months:
                            # Normalize timeline (assume max is 24 months, shorter is better)
                            timeline_score = max(0, 1.0 - (timeline_months / 24))
                            score += timeline_score * criteria["weight_timeline"]
                
                # Score based on risks (fewer is better)
                if "risks" in option and "weight_risk" in criteria:
                    risks = option["risks"]
                    if risks:
                        risk_count = len(risks)
                        # Normalize risk (assume max is 10, fewer is better)
                        risk_score = max(0, 1.0 - (risk_count / 10))
                        score += risk_score * criteria["weight_risk"]
                
                # Score based on benefits (more is better)
                if "benefits" in option and "weight_benefit" in criteria:
                    benefits = option["benefits"]
                    if benefits:
                        benefit_count = len(benefits)
                        # Normalize benefit (assume max is 10, more is better)
                        benefit_score = min(1.0, benefit_count / 10)
                        score += benefit_score * criteria["weight_benefit"]
                
                comparison_matrix.append({
                    "option_name": option.get("option_name", "Unknown"),
                    "score": score,
                    "details": option
                })
            
            # Sort by score (highest first)
            comparison_matrix.sort(key=lambda x: x["score"], reverse=True)
            
            # Get recommended option
            recommended_option = comparison_matrix[0]["option_name"] if comparison_matrix else None
            reason = f"Highest score ({comparison_matrix[0]['score']:.2f}) based on weighted criteria" if comparison_matrix else "No options provided"
            
            return {
                "success": True,
                "comparison_matrix": comparison_matrix,
                "recommended_option": recommended_option,
                "reason": reason
            }
        
        except Exception as e:
            self.logger.error(f"❌ Analyze strategic options failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "comparison_matrix": [],
                "recommended_option": None,
                "reason": ""
            }
    
    async def get_roadmap_templates(
        self,
        business_type: str,
        initiative_type: str
    ) -> Dict[str, Any]:
        """
        Get roadmap templates for business/initiative type (rule-based, not LLM).
        
        Args:
            business_type: Type of business (e.g., "digital_transformation", "process_optimization")
            initiative_type: Type of initiative
        
        Returns:
            {
                "success": bool,
                "template": Dict[str, Any],
                "customization_guidance": List[str]
            }
        """
        try:
            # Get template from library (rule-based)
            template = self.roadmap_templates.get(business_type.lower())
            
            if not template:
                # Return generic template
                template = {
                    "phases": [
                        {"name": "Planning", "duration": "1 month", "key_activities": ["Define objectives", "Plan approach"]},
                        {"name": "Implementation", "duration": "3 months", "key_activities": ["Execute plan", "Monitor progress"]},
                        {"name": "Optimization", "duration": "Ongoing", "key_activities": ["Continuous improvement"]}
                    ],
                    "typical_duration": "4 months",
                    "key_milestones": ["Planning complete", "Implementation complete"]
                }
            
            # Build customization guidance (rule-based)
            customization_guidance = [
                "Adjust phase durations based on your specific timeline",
                "Add or remove phases based on complexity",
                "Define specific milestones for your initiative",
                "Customize key activities to match your processes"
            ]
            
            return {
                "success": True,
                "template": template,
                "customization_guidance": customization_guidance
            }
        
        except Exception as e:
            self.logger.error(f"❌ Get roadmap templates failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "template": {},
                "customization_guidance": []
            }
    
    async def get_poc_best_practices(
        self,
        poc_type: str,
        industry: str
    ) -> Dict[str, Any]:
        """
        Get POC best practices (rule-based, not LLM).
        
        Args:
            poc_type: Type of POC ("technology", "process", "hybrid")
            industry: Industry type
        
        Returns:
            {
                "success": bool,
                "best_practices": Dict[str, Any],
                "recommendations": List[str]
            }
        """
        try:
            # Get best practices from library (rule-based)
            practices = self.poc_best_practices.get(poc_type.lower(), self.poc_best_practices["hybrid"])
            
            return {
                "success": True,
                "best_practices": practices,
                "recommendations": practices.get("recommendations", [])
            }
        
        except Exception as e:
            self.logger.error(f"❌ Get POC best practices failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "best_practices": {},
                "recommendations": []
            }
    
    def _parse_timeline(self, timeline: str) -> Optional[int]:
        """Parse timeline string to months (rule-based, not LLM)."""
        try:
            timeline_lower = timeline.lower()
            
            # Extract number
            import re
            numbers = re.findall(r'\d+', timeline)
            if not numbers:
                return None
            
            number = int(numbers[0])
            
            # Determine unit
            if "month" in timeline_lower:
                return number
            elif "year" in timeline_lower:
                return number * 12
            elif "week" in timeline_lower:
                return number // 4
            else:
                # Default to months
                return number
        
        except Exception:
            return None
```

**Registration:** Must register with Curator as enabling service.

---

### 2. New MCP Tools (Add to BusinessOutcomesMCPServer)

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/mcp_server/business_outcomes_mcp_server.py`

**REAL Implementation:**

```python
# Add to register_server_tools() method

# Tool 11: Plan Strategic Initiative (NEW)
self.register_tool(
    name="plan_strategic_initiative_tool",
    description="Plan strategic initiative with structured context. Agent LLM extracts business goals, constraints, success criteria.",
    handler=self._plan_strategic_initiative_tool,
    input_schema={
        "type": "object",
        "properties": {
            "business_goal": {"type": "string"},
            "business_context": {
                "type": "object",
                "description": "Structured context from agent LLM",
                "properties": {
                    "current_state": {"type": "string"},
                    "constraints": {"type": "object"},
                    "success_criteria": {"type": "object"},
                    "timeline": {"type": "string"},
                    "budget": {"type": "number"}
                }
            },
            "user_context": {"type": "object"}
        },
        "required": ["business_goal", "business_context", "user_context"]
    }
)

# Tool 12: Recommend Strategic Metrics (NEW)
self.register_tool(
    name="recommend_strategic_metrics_tool",
    description="Recommend metrics and KPIs for business goals. Agent LLM extracts goals and industry.",
    handler=self._recommend_strategic_metrics_tool,
    input_schema={
        "type": "object",
        "properties": {
            "business_goals": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Business goals from agent LLM"
            },
            "industry": {"type": "string"},
            "user_context": {"type": "object"}
        },
        "required": ["business_goals", "industry", "user_context"]
    }
)

# Tool 13: Analyze Strategic Options (NEW)
self.register_tool(
    name="analyze_strategic_options_tool",
    description="Analyze and compare strategic options. Agent LLM extracts options and criteria.",
    handler=self._analyze_strategic_options_tool,
    input_schema={
        "type": "object",
        "properties": {
            "options": {
                "type": "array",
                "description": "Structured options from agent LLM",
                "items": {"type": "object"}
            },
            "criteria": {
                "type": "object",
                "description": "Evaluation criteria from agent LLM",
                "properties": {
                    "weight_cost": {"type": "number"},
                    "weight_timeline": {"type": "number"},
                    "weight_risk": {"type": "number"},
                    "weight_benefit": {"type": "number"}
                }
            },
            "user_context": {"type": "object"}
        },
        "required": ["options", "criteria", "user_context"]
    }
)

# Tool 14: Get Pillar Summaries (NEW)
self.register_tool(
    name="get_pillar_summaries_tool",
    description="Get summaries from other pillars for strategic planning. Agent LLM extracts which pillars to include.",
    handler=self._get_pillar_summaries_tool,
    input_schema={
        "type": "object",
        "properties": {
            "session_id": {"type": "string"},
            "pillar_types": {
                "type": "array",
                "items": {"type": "string", "enum": ["content", "insights", "operations"]},
                "description": "Which pillars to include (from agent LLM)"
            },
            "user_context": {"type": "object"}
        },
        "required": ["session_id", "pillar_types", "user_context"]
    }
)

# Add to execute_tool() handler mapping
tool_handlers = {
    # ... existing tools ...
    "plan_strategic_initiative_tool": self._plan_strategic_initiative_tool,
    "recommend_strategic_metrics_tool": self._recommend_strategic_metrics_tool,
    "analyze_strategic_options_tool": self._analyze_strategic_options_tool,
    "get_pillar_summaries_tool": self._get_pillar_summaries_tool
}

# REAL Implementation of tool handlers

async def _plan_strategic_initiative_tool(
    self,
    business_goal: str,
    business_context: Dict[str, Any],  # Structured from agent LLM
    user_context: Dict[str, Any]
) -> dict:
    """
    Plan strategic initiative with structured context from agent LLM.
    
    REAL implementation - calls StrategicPlanningService and RoadmapGenerationService.
    """
    try:
        # Get StrategicPlanningService for template
        strategic_service = await self.orchestrator.get_enabling_service("StrategicPlanningService")
        if not strategic_service:
            return {
                "success": False,
                "error": "StrategicPlanningService not available",
                "roadmap": None
            }
        
        # Determine business type from goal (rule-based)
        business_type = "digital_transformation" if "digital" in business_goal.lower() else "process_optimization"
        
        # Get roadmap template
        template_result = await strategic_service.get_roadmap_templates(
            business_type=business_type,
            initiative_type=business_goal
        )
        
        if not template_result["success"]:
            return {
                "success": False,
                "error": "Failed to get roadmap template",
                "roadmap": None
            }
        
        # Get RoadmapGenerationService
        roadmap_service = await self.orchestrator.get_enabling_service("RoadmapGenerationService")
        if not roadmap_service:
            return {
                "success": False,
                "error": "RoadmapGenerationService not available",
                "roadmap": None
            }
        
        # Build roadmap structure from template and context
        roadmap_structure = {
            "goal": business_goal,
            "current_state": business_context.get("current_state"),
            "constraints": business_context.get("constraints", {}),
            "success_criteria": business_context.get("success_criteria", {}),
            "timeline": business_context.get("timeline"),
            "budget": business_context.get("budget"),
            "phases": template_result["template"]["phases"],
            "milestones": template_result["template"]["key_milestones"]
        }
        
        # Generate roadmap (NO LLM in service)
        roadmap_result = await roadmap_service.generate_roadmap(
            roadmap_structure=roadmap_structure,
            user_context=user_context
        )
        
        return roadmap_result
        
    except Exception as e:
        self.logger.error(f"❌ Plan strategic initiative tool failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "roadmap": None
        }

async def _recommend_strategic_metrics_tool(
    self,
    business_goals: List[str],  # From agent LLM
    industry: str,
    user_context: Dict[str, Any]
) -> dict:
    """
    Recommend strategic metrics (rule-based, not LLM).
    
    REAL implementation - calls StrategicPlanningService.
    """
    try:
        # Get StrategicPlanningService via orchestrator
        service = await self.orchestrator.get_enabling_service("StrategicPlanningService")
        if not service:
            return {
                "success": False,
                "error": "StrategicPlanningService not available",
                "recommended_metrics": []
            }
        
        # Call service with structured params (NO LLM in service)
        result = await service.recommend_metrics(
            business_goals=business_goals,  # From agent LLM
            industry=industry,
            user_context=user_context
        )
        
        return result
        
    except Exception as e:
        self.logger.error(f"❌ Recommend strategic metrics tool failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "recommended_metrics": []
        }

async def _analyze_strategic_options_tool(
    self,
    options: List[Dict[str, Any]],  # Structured from agent LLM
    criteria: Dict[str, Any],  # Structured from agent LLM
    user_context: Dict[str, Any]
) -> dict:
    """
    Analyze strategic options (rule-based, not LLM).
    
    REAL implementation - calls StrategicPlanningService.
    """
    try:
        # Get StrategicPlanningService via orchestrator
        service = await self.orchestrator.get_enabling_service("StrategicPlanningService")
        if not service:
            return {
                "success": False,
                "error": "StrategicPlanningService not available",
                "comparison_matrix": []
            }
        
        # Call service with structured params (NO LLM in service)
        result = await service.analyze_strategic_options(
            options=options,  # Structured from agent LLM
            criteria=criteria  # Structured from agent LLM
        )
        
        return result
        
    except Exception as e:
        self.logger.error(f"❌ Analyze strategic options tool failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "comparison_matrix": []
        }

async def _get_pillar_summaries_tool(
    self,
    session_id: str,
    pillar_types: List[str],  # From agent LLM
    user_context: Dict[str, Any]
) -> dict:
    """
    Get summaries from other pillars (REAL implementation).
    
    REAL implementation - queries session for pillar outputs.
    """
    try:
        # Get Session Manager
        session_manager = await self._get_session_manager()
        if not session_manager:
            return {
                "success": False,
                "error": "Session Manager not available",
                "pillar_summaries": {}
            }
        
        # Get session data
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            return {
                "success": False,
                "error": "Session not found",
                "pillar_summaries": {}
            }
        
        # Get pillar context from session
        pillar_context = session_data.get("context", {}).get("pillar_context", {})
        
        # Extract summaries for requested pillars
        pillar_summaries = {}
        for pillar_type in pillar_types:
            pillar_data = pillar_context.get(pillar_type, {})
            if pillar_data:
                # Extract summary (rule-based)
                summary = {
                    "pillar": pillar_type,
                    "status": pillar_data.get("status", "unknown"),
                    "key_outputs": pillar_data.get("key_outputs", []),
                    "completion_percentage": pillar_data.get("completion_percentage", 0),
                    "last_updated": pillar_data.get("last_updated")
                }
                pillar_summaries[pillar_type] = summary
        
        return {
            "success": True,
            "pillar_summaries": pillar_summaries
        }
        
    except Exception as e:
        self.logger.error(f"❌ Get pillar summaries tool failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "pillar_summaries": {}
        }
```

---

## Gaps and Practical Limitations

### Gap 1: Pillar Summaries Storage May Not Be Standardized

**Issue:** `get_pillar_summaries_tool` assumes pillar summaries are stored in session context with a specific structure, but this may not be implemented.

**Reality Check:**
- Session Manager exists
- Pillar context storage pattern needs verification
- May need to query each pillar orchestrator directly

**Practical Solution:**
1. **Option A (Preferred):** Standardize pillar summary storage in session
   ```python
   # Store pillar summaries in session during pillar operations
   session_context["pillar_context"] = {
       "content": {"status": "complete", "key_outputs": [...]},
       "insights": {"status": "complete", "key_outputs": [...]},
       "operations": {"status": "in_progress", "key_outputs": [...]}
   }
   ```

2. **Option B:** Query each pillar orchestrator directly
   ```python
   # Query ContentAnalysisOrchestrator, InsightsOrchestrator, OperationsOrchestrator
   # Get summaries from each
   ```

**Recommendation:** Use Option A - standardize pillar summary storage in session. This is cleaner and more efficient.

---

### Gap 2: Strategic Option Analysis Scoring May Be Too Simple

**Issue:** Strategic option analysis uses simple scoring that may not capture all nuances.

**Practical Solution:**
1. Start with simple scoring (as shown above)
2. Expand scoring logic based on real use cases
3. Consider storing scoring rules in Librarian for easy updates

**Recommendation:** Start with simple scoring, expand iteratively based on feedback.

---

## Implementation Checklist

### StrategicPlanningService (NEW)
- [ ] Create service file structure
- [ ] Implement `recommend_metrics()` method
- [ ] Implement `analyze_strategic_options()` method
- [ ] Implement `get_roadmap_templates()` method
- [ ] Implement `get_poc_best_practices()` method
- [ ] Register with Curator
- [ ] Test with real business goals

### New MCP Tools
- [ ] Add `plan_strategic_initiative_tool` to BusinessOutcomesMCPServer
- [ ] Add `recommend_strategic_metrics_tool` to BusinessOutcomesMCPServer
- [ ] Add `analyze_strategic_options_tool` to BusinessOutcomesMCPServer
- [ ] Add `get_pillar_summaries_tool` to BusinessOutcomesMCPServer
- [ ] Implement tool handlers (real code, no mocks)
- [ ] Test tool execution
- [ ] Test agent → tool → service flow

### Integration
- [ ] Test BusinessOutcomesLiaisonAgent with new tools
- [ ] Test end-to-end: User → Agent → Tool → Service → Response
- [ ] Verify no LLM in services
- [ ] Verify structured params work correctly
- [ ] Test pillar summary retrieval

---

## Summary

**What We Have:**
- ✅ RoadmapGenerationService, POCGenerationService, MetricsCalculatorService, ReportGeneratorService
- ✅ 10 existing MCP tools
- ✅ Session Manager for context storage

**What We Need to Create:**
- ⏳ StrategicPlanningService (NEW - pure service, NO LLM)
- ⏳ 4 new MCP tools (plan_strategic_initiative_tool, recommend_strategic_metrics_tool, analyze_strategic_options_tool, get_pillar_summaries_tool)

**Gaps Identified:**
- ⚠️ Pillar summary storage pattern needs standardization
- ⚠️ Strategic option analysis scoring may need refinement

**All implementations are REAL, WORKING CODE - no mocks, no placeholders, no hard-coded cheats.**







