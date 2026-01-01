"""
Business Case Generator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional


class BusinessCaseGenerator:
    """
    Business Case Generator following Smart City patterns.
    Generates business cases for POC proposals.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("BusinessCaseGenerator micro-module initialized")
    
    async def generate_business_case(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business case from context."""
        try:
            business_objectives = context.get("business_objectives", "")
            data_quality = context.get("data_quality", 0.8)
            market_size = context.get("market_size", 1000000)
            current_penetration = context.get("current_penetration", 0.1)
            process_complexity = context.get("process_complexity", 0.5)
            automation_readiness = context.get("automation_readiness", 0.7)
            operational_cost = context.get("operational_cost", 500000)
            
            # Calculate business focus
            business_focus = self._determine_business_focus(
                data_quality, market_size, current_penetration, 
                process_complexity, automation_readiness, operational_cost
            )
            
            # Generate opportunity description
            opportunity = self._generate_opportunity_description(
                business_objectives, business_focus, data_quality, 
                market_size, current_penetration, operational_cost
            )
            
            # Generate solution description
            solution = self._generate_solution_description(
                business_focus, data_quality, process_complexity, automation_readiness
            )
            
            # Calculate ROI
            roi = self._calculate_roi(
                market_size, current_penetration, operational_cost, 
                automation_readiness, process_complexity
            )
            
            return {
                "business_focus": business_focus,
                "opportunity": opportunity,
                "solution": solution,
                "roi": roi,
                "market_potential": market_size * (1 - current_penetration),
                "cost_savings_potential": operational_cost * automation_readiness * 0.3,
                "data_quality_impact": data_quality * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error generating business case: {e}")
            return {
                "business_focus": "ROI",
                "opportunity": "AI-powered platform optimization opportunity",
                "solution": "Comprehensive AI solution for business process improvement",
                "roi": 150,
                "error": str(e)
            }
    
    def _determine_business_focus(
        self, 
        data_quality: float, 
        market_size: int, 
        current_penetration: float,
        process_complexity: float, 
        automation_readiness: float, 
        operational_cost: int
    ) -> str:
        """Determine primary business focus based on context."""
        
        # Revenue growth potential
        revenue_potential = market_size * (1 - current_penetration)
        
        # Cost savings potential
        cost_savings_potential = operational_cost * automation_readiness * 0.3
        
        # Data quality impact
        data_impact = data_quality * 100
        
        if revenue_potential > cost_savings_potential and data_impact > 70:
            return "revenue_growth"
        elif cost_savings_potential > revenue_potential and process_complexity > 0.6:
            return "cost_saving"
        else:
            return "ROI"
    
    def _generate_opportunity_description(
        self, 
        business_objectives: str, 
        business_focus: str, 
        data_quality: float,
        market_size: int, 
        current_penetration: float, 
        operational_cost: int
    ) -> str:
        """Generate opportunity description."""
        
        market_potential = market_size * (1 - current_penetration)
        
        if business_focus == "revenue_growth":
            return f"Significant revenue growth opportunity with {market_potential:,.0f} potential market size and {data_quality*100:.0f}% data quality baseline. {business_objectives}"
        elif business_focus == "cost_saving":
            return f"Substantial cost reduction opportunity with ${operational_cost:,.0f} current operational costs and high automation readiness. {business_objectives}"
        else:
            return f"Balanced ROI opportunity combining revenue growth potential of {market_potential:,.0f} and cost savings from ${operational_cost:,.0f} operational costs. {business_objectives}"
    
    def _generate_solution_description(
        self, 
        business_focus: str, 
        data_quality: float, 
        process_complexity: float, 
        automation_readiness: float
    ) -> str:
        """Generate solution description."""
        
        if business_focus == "revenue_growth":
            return f"AI-powered platform leveraging {data_quality*100:.0f}% data quality to drive revenue growth through intelligent insights and market expansion capabilities."
        elif business_focus == "cost_saving":
            return f"Automated solution targeting {process_complexity*100:.0f}% process complexity with {automation_readiness*100:.0f}% automation readiness to reduce operational costs."
        else:
            return f"Comprehensive AI solution balancing revenue growth and cost optimization through data-driven insights and process automation."
    
    def _calculate_roi(
        self, 
        market_size: int, 
        current_penetration: float, 
        operational_cost: int,
        automation_readiness: float, 
        process_complexity: float
    ) -> float:
        """Calculate expected ROI."""
        
        # Revenue potential
        revenue_potential = market_size * (1 - current_penetration) * 0.1  # 10% capture rate
        
        # Cost savings
        cost_savings = operational_cost * automation_readiness * 0.3  # 30% savings
        
        # Total benefits
        total_benefits = revenue_potential + cost_savings
        
        # Investment (assume 20% of operational cost as POC investment)
        investment = operational_cost * 0.2
        
        # ROI calculation
        if investment > 0:
            roi = ((total_benefits - investment) / investment) * 100
        else:
            roi = 0
        
        return max(0, min(roi, 500))  # Cap ROI at 500%

