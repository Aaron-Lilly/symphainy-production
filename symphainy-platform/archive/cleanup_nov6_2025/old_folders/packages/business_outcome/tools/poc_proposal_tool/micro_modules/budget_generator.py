"""
Budget Generator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional


class BudgetGenerator:
    """
    Budget Generator following Smart City patterns.
    Generates budgets for POC proposals.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("BudgetGenerator micro-module initialized")
    
    async def generate_budget(self, budget_range: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Generate budget based on range and constraints."""
        try:
            # Get base budget from constraints
            base_budget = constraints.get("max_budget", {})
            base_cost = base_budget.get("base_cost", 50000)
            
            # Adjust based on budget range
            if budget_range == "low":
                multiplier = 0.7
                range_name = "Low Budget"
            elif budget_range == "high":
                multiplier = 1.5
                range_name = "High Budget"
            else:  # standard
                multiplier = 1.0
                range_name = "Standard Budget"
            
            total_cost = int(base_cost * multiplier)
            
            # Generate breakdown
            breakdown = self._generate_breakdown(total_cost, budget_range)
            
            # Calculate payment schedule
            payment_schedule = self._generate_payment_schedule(total_cost, budget_range)
            
            return {
                "total_cost": total_cost,
                "currency": base_budget.get("currency", "USD"),
                "range": range_name,
                "payment_schedule": payment_schedule,
                "breakdown": breakdown,
                "cost_per_day": total_cost / constraints.get("timeline_days", 90),
                "budget_range": budget_range
            }
            
        except Exception as e:
            self.logger.error(f"Error generating budget: {e}")
            return {
                "total_cost": 50000,
                "currency": "USD",
                "range": "Standard Budget",
                "payment_schedule": "milestone-based",
                "breakdown": {},
                "error": str(e)
            }
    
    def _generate_breakdown(self, total_cost: int, budget_range: str) -> Dict[str, int]:
        """Generate cost breakdown."""
        
        # Base percentages
        if budget_range == "low":
            breakdown = {
                "development": int(total_cost * 0.50),
                "testing": int(total_cost * 0.20),
                "deployment": int(total_cost * 0.15),
                "documentation": int(total_cost * 0.10),
                "contingency": int(total_cost * 0.05)
            }
        elif budget_range == "high":
            breakdown = {
                "development": int(total_cost * 0.40),
                "testing": int(total_cost * 0.25),
                "deployment": int(total_cost * 0.15),
                "documentation": int(total_cost * 0.10),
                "contingency": int(total_cost * 0.10)
            }
        else:  # standard
            breakdown = {
                "development": int(total_cost * 0.45),
                "testing": int(total_cost * 0.22),
                "deployment": int(total_cost * 0.15),
                "documentation": int(total_cost * 0.10),
                "contingency": int(total_cost * 0.08)
            }
        
        return breakdown
    
    def _generate_payment_schedule(self, total_cost: int, budget_range: str) -> List[Dict[str, Any]]:
        """Generate payment schedule."""
        
        if budget_range == "low":
            # 3 payments
            payments = [
                {
                    "milestone": "Project Kickoff",
                    "percentage": 30,
                    "amount": int(total_cost * 0.30),
                    "description": "Upon project start and requirements approval"
                },
                {
                    "milestone": "Implementation Complete",
                    "percentage": 50,
                    "amount": int(total_cost * 0.50),
                    "description": "Upon completion of core implementation"
                },
                {
                    "milestone": "Project Completion",
                    "percentage": 20,
                    "amount": int(total_cost * 0.20),
                    "description": "Upon final delivery and acceptance"
                }
            ]
        elif budget_range == "high":
            # 5 payments
            payments = [
                {
                    "milestone": "Project Kickoff",
                    "percentage": 20,
                    "amount": int(total_cost * 0.20),
                    "description": "Upon project start and requirements approval"
                },
                {
                    "milestone": "Design Phase Complete",
                    "percentage": 20,
                    "amount": int(total_cost * 0.20),
                    "description": "Upon completion of design and architecture"
                },
                {
                    "milestone": "Implementation Complete",
                    "percentage": 30,
                    "amount": int(total_cost * 0.30),
                    "description": "Upon completion of core implementation"
                },
                {
                    "milestone": "Testing Complete",
                    "percentage": 20,
                    "amount": int(total_cost * 0.20),
                    "description": "Upon completion of testing and validation"
                },
                {
                    "milestone": "Project Completion",
                    "percentage": 10,
                    "amount": int(total_cost * 0.10),
                    "description": "Upon final delivery and acceptance"
                }
            ]
        else:  # standard
            # 4 payments
            payments = [
                {
                    "milestone": "Project Kickoff",
                    "percentage": 25,
                    "amount": int(total_cost * 0.25),
                    "description": "Upon project start and requirements approval"
                },
                {
                    "milestone": "Design Complete",
                    "percentage": 25,
                    "amount": int(total_cost * 0.25),
                    "description": "Upon completion of design and architecture"
                },
                {
                    "milestone": "Implementation Complete",
                    "percentage": 35,
                    "amount": int(total_cost * 0.35),
                    "description": "Upon completion of core implementation"
                },
                {
                    "milestone": "Project Completion",
                    "percentage": 15,
                    "amount": int(total_cost * 0.15),
                    "description": "Upon final delivery and acceptance"
                }
            ]
        
        return payments
