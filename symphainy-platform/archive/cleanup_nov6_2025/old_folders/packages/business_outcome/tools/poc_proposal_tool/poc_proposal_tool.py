"""
POC Proposal Tool
Smart City Native + Micro-Modular Architecture
"""

from backend.bases.smart_city.base_mcp import BaseMCP
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
from backend.smart_city_library.architectural_components import traffic_cop, conductor, post_office
from .micro_modules.business_case_generator import BusinessCaseGenerator
from .micro_modules.assumptions_service import POCAssumptionsService
from .micro_modules.validation_service import POCValidationService
from .micro_modules.timeline_generator import TimelineGenerator
from .micro_modules.budget_generator import BudgetGenerator
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class POCProposalTool(BaseMCP):
    """
    POC Proposal Tool for Business Outcome pillar.
    Generates business proposals for SymphAIny coexistence platform POCs.
    """
    
    def __init__(self):
        super().__init__()
        self.tool_name = "poc_proposal_tool"
        self.pillar = "business_outcome"
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("POCProposalTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        # Smart City components
        self.traffic_cop = traffic_cop
        self.conductor = conductor
        self.post_office = post_office
        
        self._logger.info("POCProposalTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.business_case_generator = BusinessCaseGenerator(self._logger, self._config)
            self.assumptions_service = POCAssumptionsService(self._logger, self._config)
            self.validation_service = POCValidationService(self._logger, self._config)
            self.timeline_generator = TimelineGenerator(self._logger, self._config)
            self.budget_generator = BudgetGenerator(self._logger, self._config)
            
            self._logger.info("POCProposalTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing POCProposalTool micro-modules: {e}")
            raise e
    
    async def generate_proposal(
        self,
        insights_summary: Dict[str, Any],
        operations_coexistence: Dict[str, Any],
        roadmap_data: Dict[str, Any],
        business_context: str = "",
        budget_range: str = "standard",
        timeline_preference: str = "90_days",
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a business POC proposal using micro-module architecture.
        
        Args:
            insights_summary: Insights pillar analysis results
            operations_coexistence: Operations pillar analysis results
            roadmap_data: Roadmap data
            business_context: Business context and objectives
            budget_range: Budget range preference
            timeline_preference: Timeline preference
            session_token: Session token for Smart City integration
            
        Returns:
            POC proposal dictionary
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = self.traffic_cop.validate_session(session_token)
                if not session_valid:
                    return {
                        "error": "Invalid session token",
                        "success": False
                    }
            
            # Generate business POC proposal using micro-modules
            poc_proposal = await self._generate_business_proposal(
                insights_summary=insights_summary,
                operations_coexistence=operations_coexistence,
                roadmap_data=roadmap_data,
                business_context=business_context,
                budget_range=budget_range,
                timeline_preference=timeline_preference
            )
            
            # Validate the proposal using business rules
            validation_result = await self.validation_service.validate_poc_proposal(poc_proposal)
            
            # Add validation results to the proposal
            poc_proposal["validation"] = {
                "valid": validation_result.get("valid", False),
                "errors": validation_result.get("errors", []),
                "warnings": validation_result.get("warnings", []),
                "recommendations": validation_result.get("recommendations", [])
            }
            
            # Add MVP assumptions to the proposal
            poc_proposal["assumptions"] = await self.assumptions_service.get_assumptions_summary()
            
            return poc_proposal
            
        except Exception as e:
            self._logger.error(f"Error generating POC proposal: {e}")
            return {
                "error": f"Failed to generate POC proposal: {str(e)}",
                "title": "POC Proposal Generation Failed",
                "executive_summary": "Unable to generate proposal due to technical error.",
                "business_case": "Please try again or contact support.",
                "poc_scope": [],
                "timeline": {},
                "budget": {},
                "success_metrics": [],
                "risk_assessment": [],
                "next_steps": "Retry the operation or contact technical support."
            }
    
    async def _generate_business_proposal(
        self,
        insights_summary: Dict[str, Any],
        operations_coexistence: Dict[str, Any],
        roadmap_data: Dict[str, Any],
        business_context: str,
        budget_range: str,
        timeline_preference: str
    ) -> Dict[str, Any]:
        """Generate a business POC proposal using micro-modules."""
        
        # Get MVP constraints and assumptions
        mvp_constraints = await self.assumptions_service.get_mvp_constraints()
        
        # Generate business case using business case generator
        business_case_context = {
            "business_objectives": business_context,
            "insights_data": insights_summary,
            "operations_data": operations_coexistence,
            "data_quality": insights_summary.get("data_quality", 0.8),
            "market_size": insights_summary.get("market_size", 1000000),
            "current_penetration": insights_summary.get("current_penetration", 0.1),
            "process_complexity": operations_coexistence.get("process_complexity", 0.5),
            "automation_readiness": operations_coexistence.get("automation_readiness", 0.7),
            "operational_cost": operations_coexistence.get("operational_cost", 500000)
        }
        
        business_case = await self.business_case_generator.generate_business_case(business_case_context)
        
        # Generate POC scope based on MVP constraints
        poc_scope = await self._generate_poc_scope(insights_summary, operations_coexistence, mvp_constraints)
        
        # Create timeline using timeline generator
        timeline = await self.timeline_generator.generate_timeline(timeline_preference, mvp_constraints)
        
        # Generate budget using budget generator
        budget = await self.budget_generator.generate_budget(budget_range, mvp_constraints)
        
        # Define success metrics using business logic
        success_metrics = await self._generate_success_metrics(business_case.get("business_focus", "ROI"), mvp_constraints)
        
        # Assess risks using business logic
        risk_assessment = await self._assess_risks(insights_summary, operations_coexistence, mvp_constraints)
        
        # Generate next steps
        next_steps = await self._generate_next_steps(timeline, mvp_constraints)
        
        # Create executive summary using business logic
        executive_summary = await self._generate_executive_summary(business_case, success_metrics, mvp_constraints)
        
        return {
            "title": "SymphAIny Coexistence Platform POC Proposal",
            "executive_summary": executive_summary,
            "business_case": business_case.get("opportunity", ""),
            "poc_scope": poc_scope,
            "timeline": timeline,
            "budget": budget,
            "success_metrics": success_metrics,
            "risk_assessment": risk_assessment,
            "next_steps": next_steps,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _generate_poc_scope(
        self, 
        insights_summary: Dict[str, Any], 
        operations_coexistence: Dict[str, Any], 
        constraints: Dict[str, Any]
    ) -> List[str]:
        """Generate POC scope based on MVP constraints and business context."""
        scope_items = []
        
        # Add core scope items based on insights and operations
        if insights_summary.get("data_quality_issues"):
            scope_items.append("Data quality improvement and validation")
        
        if operations_coexistence.get("manual_processes"):
            scope_items.append("Process automation and workflow optimization")
        
        if insights_summary.get("integration_needs"):
            scope_items.append("System integration and data flow")
        
        # Ensure scope meets MVP constraints
        if len(scope_items) < 3:
            scope_items.extend([
                "Requirements gathering and analysis",
                "Solution design and implementation",
                "Testing and validation"
            ])
        
        # Limit to MVP constraints
        return scope_items[:5]  # Max 5 scope items for MVP
    
    async def _generate_success_metrics(
        self, 
        business_focus: str, 
        constraints: Dict[str, Any]
    ) -> List[str]:
        """Generate success metrics based on business focus and MVP constraints."""
        metrics_framework = constraints.get("success_metrics", {})
        
        if business_focus == "revenue_growth":
            return metrics_framework.get("business_value", [])[:3]  # Top 3 metrics
        elif business_focus == "cost_saving":
            return metrics_framework.get("efficiency", [])[:3]  # Top 3 metrics
        else:  # ROI focus
            business_metrics = metrics_framework.get("business_value", [])[:2]
            efficiency_metrics = metrics_framework.get("efficiency", [])[:1]
            return business_metrics + efficiency_metrics
    
    async def _assess_risks(
        self, 
        insights_summary: Dict[str, Any], 
        operations_coexistence: Dict[str, Any], 
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Assess risks based on business context and MVP constraints."""
        risks = []
        
        # Data quality risks
        if insights_summary.get("data_quality_issues"):
            risks.append({
                "risk": "Data quality issues affecting solution accuracy",
                "impact": "Medium",
                "probability": "Medium",
                "mitigation": "Implement data validation and quality checks"
            })
        
        # Integration risks
        if operations_coexistence.get("complex_integrations"):
            risks.append({
                "risk": "Integration complexity and delays",
                "impact": "High",
                "probability": "Medium",
                "mitigation": "Use phased approach and proof of concept"
            })
        
        # Timeline risks
        timeline_days = constraints.get("timeline_days", 90)
        if timeline_days < 60:
            risks.append({
                "risk": "Aggressive timeline may impact quality",
                "impact": "Medium",
                "probability": "High",
                "mitigation": "Focus on core deliverables and scope management"
            })
        
        # Add standard MVP risks
        risks.extend([
            {
                "risk": "Stakeholder availability and engagement",
                "impact": "Medium",
                "probability": "Low",
                "mitigation": "Regular communication and milestone reviews"
            },
            {
                "risk": "Technical infrastructure readiness",
                "impact": "Medium",
                "probability": "Low",
                "mitigation": "Infrastructure assessment and planning"
            }
        ])
        
        return risks[:5]  # Limit to top 5 risks for MVP
    
    async def _generate_next_steps(
        self, 
        timeline: Dict[str, Any], 
        constraints: Dict[str, Any]
    ) -> str:
        """Generate next steps based on timeline and MVP constraints."""
        phases = timeline.get("phases", [])
        next_steps = [
            "Stakeholder approval and project kickoff",
            "Resource allocation and team formation"
        ]
        
        if phases:
            for phase in phases:
                phase_name = phase.get("name", "Unknown Phase")
                start_day = phase.get("start_day", 1)
                end_day = phase.get("end_day", 30)
                next_steps.append(f"{phase_name} (Week {start_day}-{end_day})")
        else:
            next_steps.extend([
                "Detailed requirements gathering (Week 1-2)",
                "Solution design and architecture planning (Week 3-6)",
                "Implementation and development (Week 7-10)",
                "Testing and validation (Week 11-12)"
            ])
        
        next_steps.append("Project handoff and knowledge transfer")
        
        return "\n".join(next_steps)
    
    async def _generate_executive_summary(
        self, 
        business_case: Dict[str, Any], 
        success_metrics: List[str], 
        constraints: Dict[str, Any]
    ) -> str:
        """Generate executive summary using business logic."""
        solution = business_case.get("solution", "AI-powered coexistence platform")
        timeline_days = constraints.get("timeline_days", 90)
        budget_range = constraints.get("max_budget", {}).get("range", "standard")
        
        summary = f"This POC will implement {solution[:100]}... "
        summary += f"Expected outcomes include {', '.join(success_metrics[:2])} "
        summary += f"within a {timeline_days}-day timeline and {budget_range} budget. "
        summary += f"The solution focuses on core business objectives to ensure focused, deliverable results."
        
        return summary

