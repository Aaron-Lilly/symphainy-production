#!/usr/bin/env python3
"""
POC Generation Service

WHAT: Generates POC proposals with financials from pillar outputs
HOW: Analyzes Content, Insights, and Operations pillar summaries to create comprehensive POC proposals

This service generates POC proposals by analyzing outputs from:
- Content Pillar: Semantic data model complexity (scope estimation)
- Insights Pillar: Key findings and recommendations (value calculation)
- Operations Pillar: Artifacts and process optimization (effort estimation)

POC proposals include:
- Objectives and scope
- Timeline and resource requirements
- Financial analysis (ROI, NPV, IRR, payback period)
- Success criteria
- Executive summary
"""

import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import math

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class POCGenerationService(RealmServiceBase):
    """
    POC Generation Service for Solution realm.
    
    Generates comprehensive POC proposals from pillar outputs:
    - Content: Data transformation scope
    - Insights: Business value calculation
    - Operations: Process improvement scope
    - Combined: Comprehensive POC proposal
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize POC Generation Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.librarian = None
        self.solution_composer = None
    
    async def initialize(self) -> bool:
        """
        Initialize POC Generation Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "poc_generation_service_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # Get Smart City services
            self.librarian = await self.get_librarian_api()
            
            # Get Solution Composer for artifact creation
            self.solution_composer = await self._get_solution_composer()
            
            # Register with Curator
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "poc_generation",
                        "protocol": "POCGenerationServiceProtocol",
                        "description": "Generate POC proposals with financials from pillar outputs",
                        "contracts": {
                            "soa_api": {
                                "api_name": "generate_poc_proposal",
                                "endpoint": "/api/v1/solution/poc-generation/generate-poc-proposal",
                                "method": "POST",
                                "handler": self.generate_poc_proposal,
                                "metadata": {
                                    "description": "Generate POC proposal from pillar outputs",
                                    "parameters": ["pillar_outputs", "poc_type", "options"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "generate_poc_proposal_tool",
                                "tool_definition": {
                                    "name": "generate_poc_proposal_tool",
                                    "description": "Generate POC proposal from pillar outputs",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "pillar_outputs": {"type": "object"},
                                            "poc_type": {"type": "string", "enum": ["hybrid", "data_focused", "analytics_focused", "process_focused"]},
                                            "options": {"type": "object"}
                                        },
                                        "required": ["pillar_outputs"]
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "solution.generate_poc_proposal",
                            "semantic_api": "/api/v1/solution/poc-generation/generate-poc-proposal",
                            "user_journey": "generate_poc_proposal"
                        }
                    },
                    {
                        "name": "financial_analysis",
                        "protocol": "POCGenerationServiceProtocol",
                        "description": "Calculate financials (ROI, NPV, IRR) for POC proposals",
                        "contracts": {
                            "soa_api": {
                                "api_name": "calculate_financials",
                                "endpoint": "/api/v1/solution/poc-generation/calculate-financials",
                                "method": "POST",
                                "handler": self.calculate_financials,
                                "metadata": {
                                    "description": "Calculate financials for POC proposal",
                                    "parameters": ["poc_proposal"]
                                }
                            }
                        }
                    }
                ],
                soa_apis=["generate_poc_proposal", "calculate_financials", "generate_executive_summary", "validate_poc_proposal"],
                mcp_tools=["generate_poc_proposal_tool"]
            )
            
            # Record health metric
            await self.record_health_metric(
                "poc_generation_service_initialized",
                1.0,
                {"service": self.service_name}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "poc_generation_service_initialize_complete",
                success=True
            )
            
            self.logger.info(f"✅ {self.service_name} initialized successfully")
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "poc_generation_service_initialize")
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "poc_generation_service_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            return False
    
    async def _get_solution_composer(self):
        """Get Solution Composer Service for artifact creation."""
        try:
            # Try Curator discovery first
            solution_composer = await self.get_enabling_service("SolutionComposerService")
            if solution_composer:
                return solution_composer
            
            # Fallback: Direct import
            from backend.solution.services.solution_composer_service.solution_composer_service import SolutionComposerService
            
            service = SolutionComposerService(
                service_name="SolutionComposerService",
                realm_name="solution",
                platform_gateway=self.platform_gateway,
                di_container=self.di_container
            )
            await service.initialize()
            return service
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not get Solution Composer: {e}")
            return None
    
    async def generate_poc_proposal(
        self,
        poc_structure: Dict[str, Any],
        poc_type: str = "hybrid",
        options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate POC proposal from agent-specified structure (Agentic-Forward Pattern).
        
        This service executes the POC structure that the agent determined through
        critical reasoning. The agent has already:
        - Analyzed pillar outputs
        - Determined how to structure POC to maximize value
        - Identified where AI can add value
        - Specified scope, objectives, and success criteria
        
        Args:
            poc_structure: REQUIRED - Agent-specified POC structure from critical reasoning
                {
                    "scope": {...},  # Agent-specified scope (required)
                    "objectives": [...],  # Agent-identified objectives (required)
                    "success_criteria": [...],  # Agent-determined criteria
                    "ai_value_propositions": [...],  # Where AI adds value
                    "recommended_focus": str
                }
            poc_type: Type of POC ("hybrid", "data_focused", "analytics_focused", "process_focused")
            options: Optional POC options (budget, timeline, scope)
            user_context: Optional user context
        
        Returns:
            Dict with POC proposal:
            {
                "success": bool,
                "poc_proposal": {
                    "proposal_id": str,
                    "objectives": [...],
                    "scope": {...},
                    "timeline": {...},
                    "resource_requirements": {...},
                    "success_criteria": [...],
                    "financials": {...}  # ROI, NPV, IRR, payback
                }
            }
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "generate_poc_proposal_start",
            success=True,
            details={"poc_type": poc_type, "objectives_count": len(poc_structure.get("objectives", []))}
        )
        
        try:
            self.logger.info(f"📋 Generating POC proposal from agent-specified structure (type: {poc_type})")
            
            options = options or {}
            
            # Validate agent-specified structure
            if not poc_structure.get("scope") or not poc_structure.get("objectives"):
                return {
                    "success": False,
                    "error": "Invalid POC structure",
                    "message": "Agent must specify scope and objectives in poc_structure"
                }
            
            # Use agent-specified structure (agent has already done critical reasoning)
            scope = poc_structure.get("scope", {})
            objectives = poc_structure.get("objectives", [])
            success_criteria = poc_structure.get("success_criteria", [])
            ai_value_propositions = poc_structure.get("ai_value_propositions", [])
            
            # Generate proposal ID
            proposal_id = f"poc_{uuid.uuid4().hex[:8]}"
            
            # Calculate timeline from agent-specified scope
            timeline = self._calculate_timeline(scope, options)
            
            # Calculate resource requirements from agent-specified scope and timeline
            resource_requirements = self._calculate_resource_requirements(scope, timeline)
            
            # Calculate financials
            financials = self._calculate_financials_internal(
                scope=scope,
                timeline=timeline,
                resource_requirements=resource_requirements,
                options=options
            )
            
            # Create POC proposal structure (executing agent's strategic decisions)
            poc_proposal = {
                "proposal_id": proposal_id,
                "poc_type": poc_type,
                "name": options.get("name", f"POC Proposal - {poc_type.title()}"),
                "description": f"POC proposal with {poc_structure.get('recommended_focus', 'AI value demonstration')} focus",
                "objectives": objectives,
                "scope": scope,
                "timeline": timeline,
                "resource_requirements": resource_requirements,
                "success_criteria": success_criteria,
                "financials": financials,
                "ai_value_propositions": ai_value_propositions,
                "recommended_focus": poc_structure.get("recommended_focus", ""),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(poc_proposal)
            poc_proposal["executive_summary"] = executive_summary
            
            # Record health metric (success)
            await self.record_health_metric("generate_poc_proposal_success", 1.0, {"proposal_id": proposal_id, "poc_type": poc_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("generate_poc_proposal_complete", success=True, details={"proposal_id": proposal_id})
            
            return {
                "success": True,
                "poc_proposal": poc_proposal,
                "message": f"POC proposal generated successfully ({poc_type})"
            }
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "generate_poc_proposal", details={"poc_type": poc_type, "pillar_outputs_keys": list(pillar_outputs.keys())})
            
            # Record health metric (failure)
            await self.record_health_metric("generate_poc_proposal_failed", 1.0, {"error": type(e).__name__})
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("generate_poc_proposal_complete", success=False, details={"error": str(e)})
            
            self.logger.error(f"❌ Generate POC proposal failed: {e}")
            return {
                "success": False,
                "error": "POC proposal generation failed",
                "error_details": str(e)
            }
    
    def _calculate_scope(
        self,
        pillar_outputs: Dict[str, Any],
        poc_type: str,
        available_pillars: List[str]
    ) -> Dict[str, Any]:
        """Calculate POC scope from pillar outputs."""
        scope = {
            "in_scope": [],
            "out_of_scope": [],
            "assumptions": [],
            "risks": []
        }
        
        # Content pillar scope
        if "content" in available_pillars:
            content_summary = pillar_outputs.get("content_pillar", {})
            semantic_model = content_summary.get("semantic_data_model", {})
            structured_count = semantic_model.get("structured_files", {}).get("count", 0)
            unstructured_count = semantic_model.get("unstructured_files", {}).get("count", 0)
            
            if structured_count > 0 or unstructured_count > 0:
                scope["in_scope"].append({
                    "item": "Data Migration & Semantic Model",
                    "description": f"Migrate {structured_count + unstructured_count} files and create semantic data model",
                    "complexity": "medium" if (structured_count + unstructured_count) < 10 else "high"
                })
        
        # Insights pillar scope
        if "insights" in available_pillars:
            insights_summary = pillar_outputs.get("insights_pillar", {})
            insights_data = insights_summary.get("summary", {})
            
            if insights_data.get("textual") or insights_data.get("tabular"):
                scope["in_scope"].append({
                    "item": "Analytics Implementation",
                    "description": "Implement analytics based on insights findings",
                    "complexity": "medium"
                })
        
        # Operations pillar scope
        if "operations" in available_pillars:
            operations_summary = pillar_outputs.get("operations_pillar", {})
            artifacts = operations_summary.get("artifacts", {})
            workflow_count = len(artifacts.get("workflows", []))
            sop_count = len(artifacts.get("sops", []))
            blueprint_count = len(artifacts.get("coexistence_blueprints", []))
            
            if workflow_count > 0 or sop_count > 0:
                scope["in_scope"].append({
                    "item": "Process Optimization",
                    "description": f"Implement {workflow_count} workflows and {sop_count} SOPs",
                    "complexity": "medium" if (workflow_count + sop_count) < 5 else "high"
                })
            
            if blueprint_count > 0:
                scope["in_scope"].append({
                    "item": "Coexistence Blueprint Implementation",
                    "description": f"Implement {blueprint_count} coexistence blueprint(s)",
                    "complexity": "high"
                })
        
        # Default scope if no specific items
        if not scope["in_scope"]:
            scope["in_scope"].append({
                "item": "Platform Implementation",
                "description": "Implement platform capabilities based on available pillar outputs",
                "complexity": "medium"
            })
        
        # Add assumptions
        scope["assumptions"].append("Client will provide necessary access and resources")
        scope["assumptions"].append("Timeline estimates are based on standard implementation patterns")
        
        # Add risks
        scope["risks"].append({
            "risk": "Scope Creep",
            "mitigation": "Regular review meetings and change control process"
        })
        
        return scope
    
    def _calculate_timeline(
        self,
        scope: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate POC timeline from scope."""
        # Base timeline from options or calculate from scope
        base_days = options.get("timeline_days", 90)
        
        # Adjust based on scope complexity
        high_complexity_items = sum(1 for item in scope.get("in_scope", []) if item.get("complexity") == "high")
        medium_complexity_items = sum(1 for item in scope.get("in_scope", []) if item.get("complexity") == "medium")
        
        # Add days for complexity
        additional_days = (high_complexity_items * 15) + (medium_complexity_items * 7)
        total_days = base_days + additional_days
        
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=total_days)
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration_days": total_days,
            "phases": [
                {
                    "phase": "Phase 1: Setup & Foundation",
                    "duration_days": int(total_days * 0.3),
                    "start_date": start_date.isoformat()
                },
                {
                    "phase": "Phase 2: Implementation",
                    "duration_days": int(total_days * 0.5),
                    "start_date": (start_date + timedelta(days=int(total_days * 0.3))).isoformat()
                },
                {
                    "phase": "Phase 3: Validation & Handoff",
                    "duration_days": int(total_days * 0.2),
                    "start_date": (start_date + timedelta(days=int(total_days * 0.8))).isoformat()
                }
            ]
        }
    
    def _calculate_resource_requirements(
        self,
        scope: Dict[str, Any],
        timeline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate resource requirements from scope and timeline."""
        # Base team size
        team_size = 3  # Project manager, technical lead, developer
        
        # Adjust based on scope complexity
        high_complexity_items = sum(1 for item in scope.get("in_scope", []) if item.get("complexity") == "high")
        if high_complexity_items > 0:
            team_size += 1  # Add specialist
        
        # Calculate effort (person-days)
        duration_days = timeline.get("duration_days", 90)
        effort_person_days = team_size * duration_days
        
        return {
            "team_size": team_size,
            "roles": [
                "Project Manager",
                "Technical Lead",
                "Developer",
                "Specialist" if high_complexity_items > 0 else None
            ],
            "effort_person_days": effort_person_days,
            "estimated_cost": effort_person_days * 1000  # $1000 per person-day (placeholder)
        }
    
    def _generate_objectives(
        self,
        pillar_outputs: Dict[str, Any],
        poc_type: str,
        available_pillars: List[str]
    ) -> List[str]:
        """Generate POC objectives from pillar outputs."""
        objectives = []
        
        if "content" in available_pillars:
            objectives.append("Demonstrate semantic data model creation and value")
        
        if "insights" in available_pillars:
            objectives.append("Showcase analytics capabilities and insights generation")
        
        if "operations" in available_pillars:
            objectives.append("Validate process optimization through workflows and SOPs")
        
        if len(available_pillars) >= 2:
            objectives.append("Prove platform value through integrated pillar workflows")
        
        if not objectives:
            objectives.append("Demonstrate platform capabilities and value")
        
        return objectives
    
    def _generate_success_criteria(
        self,
        pillar_outputs: Dict[str, Any],
        poc_type: str,
        available_pillars: List[str]
    ) -> List[str]:
        """Generate success criteria from pillar outputs."""
        criteria = []
        
        if "content" in available_pillars:
            criteria.append("Semantic data model successfully created and accessible")
        
        if "insights" in available_pillars:
            criteria.append("Analytics insights generated and validated")
        
        if "operations" in available_pillars:
            criteria.append("Workflows and SOPs implemented and operational")
        
        criteria.append("Client satisfaction with POC deliverables")
        criteria.append("Platform performance meets or exceeds expectations")
        
        return criteria
    
    def _calculate_financials_internal(
        self,
        scope: Dict[str, Any],
        timeline: Dict[str, Any],
        resource_requirements: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate financials (ROI, NPV, IRR, payback period)."""
        # Get costs
        estimated_cost = resource_requirements.get("estimated_cost", 0)
        duration_days = timeline.get("duration_days", 90)
        
        # Estimate benefits (simplified calculation)
        # Base value from scope items
        base_value = len(scope.get("in_scope", [])) * 50000  # $50K per scope item
        
        # Annual benefits (simplified)
        annual_benefits = base_value * 0.3  # 30% of base value per year
        
        # Calculate ROI
        roi = ((annual_benefits - estimated_cost) / estimated_cost * 100) if estimated_cost > 0 else 0
        
        # Calculate NPV (3-year horizon, 10% discount rate)
        discount_rate = 0.10
        npv = -estimated_cost
        for year in range(1, 4):
            npv += annual_benefits / ((1 + discount_rate) ** year)
        
        # Calculate IRR (simplified - iterative approximation)
        irr = self._calculate_irr_simplified(estimated_cost, annual_benefits, 3)
        
        # Calculate payback period
        payback_period_years = estimated_cost / annual_benefits if annual_benefits > 0 else float('inf')
        
        return {
            "estimated_cost": estimated_cost,
            "annual_benefits": annual_benefits,
            "roi_percentage": round(roi, 2),
            "npv": round(npv, 2),
            "irr_percentage": round(irr * 100, 2),
            "payback_period_years": round(payback_period_years, 2),
            "currency": "USD",
            "calculation_date": datetime.utcnow().isoformat()
        }
    
    def _calculate_irr_simplified(self, initial_investment: float, annual_cash_flow: float, years: int) -> float:
        """Calculate IRR using simplified approximation."""
        if initial_investment <= 0 or annual_cash_flow <= 0:
            return 0.0
        
        # Simple approximation: (annual_cash_flow / initial_investment) ^ (1/years) - 1
        try:
            irr = ((annual_cash_flow / initial_investment) ** (1.0 / years)) - 1
            return max(0.0, min(irr, 1.0))  # Cap between 0% and 100%
        except:
            return 0.0
    
    def _generate_executive_summary(self, poc_proposal: Dict[str, Any]) -> str:
        """Generate executive summary from POC proposal."""
        financials = poc_proposal.get("financials", {})
        timeline = poc_proposal.get("timeline", {})
        objectives = poc_proposal.get("objectives", [])
        
        summary = f"""
Executive Summary

This POC proposal outlines a {poc_proposal.get('poc_type', 'hybrid')} proof of concept designed to demonstrate platform value through {len(objectives)} key objective(s).

Timeline: {timeline.get('duration_days', 0)} days
Estimated Investment: ${financials.get('estimated_cost', 0):,.0f}
Expected ROI: {financials.get('roi_percentage', 0):.1f}%
Payback Period: {financials.get('payback_period_years', 0):.1f} years

The POC will validate platform capabilities and provide a foundation for full-scale implementation.
        """.strip()
        
        return summary
    
    async def calculate_financials(
        self,
        poc_proposal: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate financials for POC proposal.
        
        Args:
            poc_proposal: POC proposal structure
            user_context: Optional user context
        
        Returns:
            Financials calculation
        """
        scope = poc_proposal.get("scope", {})
        timeline = poc_proposal.get("timeline", {})
        resource_requirements = poc_proposal.get("resource_requirements", {})
        
        financials = self._calculate_financials_internal(
            scope=scope,
            timeline=timeline,
            resource_requirements=resource_requirements,
            options={}
        )
        
        return {
            "success": True,
            "financials": financials
        }
    
    async def generate_executive_summary(
        self,
        poc_proposal: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate executive summary for POC proposal.
        
        Args:
            poc_proposal: POC proposal structure
            user_context: Optional user context
        
        Returns:
            Executive summary
        """
        executive_summary = self._generate_executive_summary(poc_proposal)
        
        return {
            "success": True,
            "executive_summary": executive_summary
        }
    
    async def validate_poc_proposal(
        self,
        poc_proposal: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate POC proposal completeness.
        
        Args:
            poc_proposal: POC proposal structure
            user_context: Optional user context
        
        Returns:
            Validation result
        """
        required_fields = ["objectives", "scope", "timeline", "resource_requirements", "success_criteria", "financials"]
        missing_fields = [field for field in required_fields if field not in poc_proposal]
        
        is_valid = len(missing_fields) == 0
        
        return {
            "success": is_valid,
            "is_valid": is_valid,
            "missing_fields": missing_fields,
            "message": "POC proposal is valid" if is_valid else f"POC proposal missing: {', '.join(missing_fields)}"
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities."""
        return {
            "service_name": self.service_name,
            "service_type": "poc_generation",
            "capabilities": [
                "generate_poc_proposal",
                "calculate_financials",
                "generate_executive_summary",
                "validate_poc_proposal"
            ],
            "realm": self.realm_name
        }

