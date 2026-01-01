#!/usr/bin/env python3
"""
Cost Tracking for Tests

Track LLM API costs during tests to prevent budget overruns.
"""

from typing import Dict, Any
from datetime import datetime

class TestCostTracker:
    """Track LLM API costs during tests."""
    
    def __init__(self, max_cost: float = 1.00):
        """
        Initialize cost tracker.
        
        Args:
            max_cost: Maximum cost allowed per test run (default: $1.00)
        """
        self.costs: Dict[str, float] = {}
        self.total_cost = 0.0
        self.max_cost = max_cost
        self.call_count = 0
    
    def record_cost(self, test_name: str, tokens: int, model: str):
        """
        Record cost for a test.
        
        Args:
            test_name: Name of the test
            tokens: Number of tokens used
            model: Model name
        """
        # Model pricing (per 1M tokens) - as of 2024
        pricing = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            "claude-3-sonnet": {"input": 3.00, "output": 15.00}
        }
        
        model_pricing = pricing.get(model.lower(), pricing["gpt-4o-mini"])
        
        # Rough estimate: assume 50/50 input/output split
        # More accurate would be to track input/output separately
        avg_price = (model_pricing["input"] + model_pricing["output"]) / 2
        cost = (tokens / 1_000_000) * avg_price
        
        self.costs[test_name] = self.costs.get(test_name, 0.0) + cost
        self.total_cost += cost
        self.call_count += 1
        
        if self.total_cost > self.max_cost:
            raise RuntimeError(
                f"Test cost limit exceeded: ${self.total_cost:.4f} > ${self.max_cost:.2f}. "
                f"Stop tests to prevent further costs."
            )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        return {
            "total_cost": round(self.total_cost, 4),
            "total_calls": self.call_count,
            "test_costs": {k: round(v, 4) for k, v in self.costs.items()},
            "max_cost": self.max_cost,
            "remaining_budget": round(self.max_cost - self.total_cost, 4),
            "timestamp": datetime.now().isoformat()
        }
    
    def reset(self):
        """Reset cost tracker."""
        self.costs = {}
        self.total_cost = 0.0
        self.call_count = 0

# Global cost tracker instance
_global_cost_tracker = None

def get_cost_tracker(max_cost: float = 1.00) -> TestCostTracker:
    """Get global cost tracker instance."""
    global _global_cost_tracker
    if _global_cost_tracker is None:
        _global_cost_tracker = TestCostTracker(max_cost=max_cost)
    return _global_cost_tracker

def reset_cost_tracker():
    """Reset global cost tracker."""
    global _global_cost_tracker
    if _global_cost_tracker:
        _global_cost_tracker.reset()







