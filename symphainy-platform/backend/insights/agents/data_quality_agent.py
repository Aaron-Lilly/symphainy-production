#!/usr/bin/env python3
"""
Data Quality Agent - Insights Realm

WHAT: Analyzes data quality and generates cleanup recommendations
HOW: Uses LLM to analyze quality issues and suggest actionable fixes

This agent provides:
- Quality issue analysis
- Cleanup action generation with prioritization
- Transformation suggestions
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../'))


class DataQualityAgent:
    """
    Data Quality Agent - Analyzes data quality and generates cleanup recommendations.
    
    This is a simplified agent class that can be instantiated directly
    by the orchestrator (not via Agentic Foundation factory).
    """
    
    def __init__(self, orchestrator):
        """
        Initialize Data Quality Agent.
        
        Args:
            orchestrator: InsightsJourneyOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = orchestrator.logger if hasattr(orchestrator, 'logger') else None
        if not self.logger:
            import logging
            self.logger = logging.getLogger(__name__)
        
        # Services (lazy initialization)
        self._llm_composition = None
    
    async def _get_llm_composition(self):
        """Get LLM Composition Service."""
        if self._llm_composition is None:
            self._llm_composition = await self.orchestrator.get_business_abstraction("llm_composition")
        return self._llm_composition
    
    async def analyze_quality_issues(
        self,
        quality_results: Dict[str, Any],
        source_file_id: str
    ) -> Dict[str, Any]:
        """
        Analyze quality issues and generate insights.
        
        Args:
            quality_results: Quality validation results from DataQualityValidationService
            source_file_id: Source file identifier
        
        Returns:
        {
            "success": True,
            "analysis": {
                "root_causes": [...],
                "patterns": [...],
                "recommendations": [...]
            }
        }
        """
        try:
            self.logger.info("🔍 Analyzing quality issues")
            
            summary = quality_results.get("summary", {})
            validation_results = quality_results.get("validation_results", [])
            
            # Extract common patterns
            issue_patterns = {}
            for result in validation_results:
                for issue in result.get("issues", []):
                    pattern_key = f"{issue['issue_type']}:{issue['field']}"
                    if pattern_key not in issue_patterns:
                        issue_patterns[pattern_key] = {
                            "count": 0,
                            "examples": []
                        }
                    issue_patterns[pattern_key]["count"] += 1
                    if len(issue_patterns[pattern_key]["examples"]) < 3:
                        issue_patterns[pattern_key]["examples"].append(issue)
            
            # Use LLM to analyze root causes
            llm_analysis = await self._analyze_with_llm(quality_results, issue_patterns)
            
            return {
                "success": True,
                "analysis": {
                    "root_causes": llm_analysis.get("root_causes", []),
                    "patterns": [
                        {
                            "pattern": key,
                            "count": info["count"],
                            "percentage": (info["count"] / len(validation_results)) * 100,
                            "examples": info["examples"]
                        }
                        for key, info in sorted(issue_patterns.items(), key=lambda x: x[1]["count"], reverse=True)
                    ],
                    "recommendations": llm_analysis.get("recommendations", [])
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Quality issue analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _analyze_with_llm(
        self,
        quality_results: Dict[str, Any],
        issue_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to analyze quality issues and suggest root causes."""
        try:
            llm_composition = await self._get_llm_composition()
            if not llm_composition:
                return {
                    "root_causes": [],
                    "recommendations": []
                }
            
            summary = quality_results.get("summary", {})
            common_issues = summary.get("common_issues", [])
            
            prompt = f"""Analyze the following data quality issues and provide root causes and recommendations.

Quality Summary:
- Total Records: {summary.get('total_records', 0)}
- Valid Records: {summary.get('valid_records', 0)}
- Invalid Records: {summary.get('invalid_records', 0)}
- Overall Quality Score: {summary.get('overall_quality_score', 0.0)}

Common Issues:
{json.dumps(common_issues, indent=2)}

Please analyze and provide:
1. Root causes for these quality issues
2. Actionable recommendations to fix them

Return JSON:
{{
    "root_causes": [
        {{
            "cause": "Description of root cause",
            "affected_fields": ["field1", "field2"],
            "severity": "high|medium|low"
        }}
    ],
    "recommendations": [
        {{
            "recommendation": "Actionable recommendation",
            "priority": "high|medium|low",
            "estimated_effort": "Description of effort needed"
        }}
    ]
}}
"""
            
            llm_response = await llm_composition.generate_text(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.2
            )
            
            # Parse LLM response
            response_text = llm_response.get("text", "") if isinstance(llm_response, dict) else str(llm_response)
            
            # Extract JSON
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return {
                "root_causes": [],
                "recommendations": []
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ LLM quality analysis failed: {e}")
            return {
                "root_causes": [],
                "recommendations": []
            }
    
    async def enhance_cleanup_actions(
        self,
        cleanup_actions: List[Dict[str, Any]],
        quality_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enhance cleanup actions with LLM-generated insights.
        
        Args:
            cleanup_actions: Cleanup actions from DataQualityValidationService
            quality_analysis: Analysis from analyze_quality_issues
        
        Returns:
            Enhanced cleanup actions with additional recommendations
        """
        try:
            self.logger.info("✨ Enhancing cleanup actions")
            
            # Merge LLM recommendations into cleanup actions
            llm_recommendations = quality_analysis.get("analysis", {}).get("recommendations", [])
            
            # Add LLM insights to relevant cleanup actions
            for action in cleanup_actions:
                field = action.get("affected_fields", [None])[0] if action.get("affected_fields") else None
                if field:
                    # Find matching LLM recommendation
                    matching_rec = next(
                        (r for r in llm_recommendations if field.lower() in r.get("recommendation", "").lower()),
                        None
                    )
                    if matching_rec:
                        action["llm_insight"] = matching_rec.get("recommendation")
                        action["llm_priority"] = matching_rec.get("priority", "medium")
            
            return cleanup_actions
            
        except Exception as e:
            self.logger.warning(f"⚠️ Cleanup action enhancement failed: {e}")
            return cleanup_actions













