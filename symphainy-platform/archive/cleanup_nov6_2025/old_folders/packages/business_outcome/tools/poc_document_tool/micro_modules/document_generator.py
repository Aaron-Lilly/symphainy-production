"""
POC Document Generator Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class POCDocumentGenerator:
    """
    POC Document Generator following Smart City patterns.
    Handles document structure creation.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("POCDocumentGenerator micro-module initialized")
    
    async def create_document_structure(self, poc_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Create document structure from POC proposal."""
        try:
            document = {
                "title": poc_proposal.get("title", "POC Proposal"),
                "sections": [
                    {
                        "name": "Executive Summary",
                        "content": poc_proposal.get("executive_summary", ""),
                        "order": 1
                    },
                    {
                        "name": "Business Case",
                        "content": poc_proposal.get("business_case", ""),
                        "order": 2
                    },
                    {
                        "name": "POC Scope",
                        "content": self._format_scope(poc_proposal.get("poc_scope", [])),
                        "order": 3
                    },
                    {
                        "name": "Timeline",
                        "content": self._format_timeline(poc_proposal.get("timeline", {})),
                        "order": 4
                    },
                    {
                        "name": "Budget",
                        "content": self._format_budget(poc_proposal.get("budget", {})),
                        "order": 5
                    },
                    {
                        "name": "Success Metrics",
                        "content": self._format_metrics(poc_proposal.get("success_metrics", [])),
                        "order": 6
                    },
                    {
                        "name": "Risk Assessment",
                        "content": self._format_risks(poc_proposal.get("risk_assessment", [])),
                        "order": 7
                    },
                    {
                        "name": "Next Steps",
                        "content": poc_proposal.get("next_steps", ""),
                        "order": 8
                    }
                ],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "proposal_id": poc_proposal.get("id", "unknown")
                }
            }
            
            return document
            
        except Exception as e:
            self.logger.error(f"Error creating document structure: {e}")
            return {"error": str(e)}
    
    def _format_scope(self, scope: List[str]) -> str:
        """Format POC scope for document."""
        if not scope:
            return "No scope items defined."
        
        formatted = "The POC will include the following scope items:\n\n"
        for i, item in enumerate(scope, 1):
            formatted += f"{i}. {item}\n"
        
        return formatted
    
    def _format_timeline(self, timeline: Dict[str, Any]) -> str:
        """Format timeline for document."""
        if not timeline:
            return "No timeline information provided."
        
        formatted = f"Total Duration: {timeline.get('total_duration_days', 'Unknown')} days\n\n"
        
        phases = timeline.get("phases", [])
        if phases:
            formatted += "Project Phases:\n\n"
            for phase in phases:
                formatted += f"• {phase.get('name', 'Unknown Phase')}: {phase.get('duration', 'Unknown duration')}\n"
        
        return formatted
    
    def _format_budget(self, budget: Dict[str, Any]) -> str:
        """Format budget for document."""
        if not budget:
            return "No budget information provided."
        
        formatted = f"Total Cost: {budget.get('total_cost', 'Unknown')} {budget.get('currency', 'USD')}\n"
        formatted += f"Budget Range: {budget.get('range', 'Not specified')}\n\n"
        
        breakdown = budget.get("breakdown", {})
        if breakdown:
            formatted += "Cost Breakdown:\n\n"
            for category, amount in breakdown.items():
                formatted += f"• {category}: {amount}\n"
        
        return formatted
    
    def _format_metrics(self, metrics: List[str]) -> str:
        """Format success metrics for document."""
        if not metrics:
            return "No success metrics defined."
        
        formatted = "Success will be measured by the following metrics:\n\n"
        for i, metric in enumerate(metrics, 1):
            formatted += f"{i}. {metric}\n"
        
        return formatted
    
    def _format_risks(self, risks: List[Dict[str, Any]]) -> str:
        """Format risk assessment for document."""
        if not risks:
            return "No risk assessment provided."
        
        formatted = "Risk Assessment:\n\n"
        for i, risk in enumerate(risks, 1):
            if isinstance(risk, dict):
                formatted += f"{i}. {risk.get('risk', 'Unknown risk')}\n"
                formatted += f"   Impact: {risk.get('impact', 'Unknown')}\n"
                formatted += f"   Probability: {risk.get('probability', 'Unknown')}\n"
                formatted += f"   Mitigation: {risk.get('mitigation', 'Not specified')}\n\n"
            else:
                formatted += f"{i}. {risk}\n"
        
        return formatted

