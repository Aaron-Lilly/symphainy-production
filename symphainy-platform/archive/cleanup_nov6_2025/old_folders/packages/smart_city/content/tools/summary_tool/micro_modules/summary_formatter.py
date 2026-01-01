"""
Summary Formatter Micro-Module
Smart City Native + Micro-Modular Architecture
"""

from typing import Dict, Any, List
import pandas as pd


class SummaryFormatter:
    """
    Summary formatting following Smart City patterns.
    Ported from CrewAI tool with Smart City integration.
    """
    
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.logger.info("SummaryFormatter micro-module initialized")
    
    async def format_summary(self, summary: str, insights: List[str], highlights: List[str]) -> Dict[str, Any]:
        """
        Format summary for frontend display.
        
        Args:
            summary: Main summary text
            insights: List of insights
            highlights: List of highlights
            
        Returns:
            Formatted summary dictionary
        """
        try:
            formatted = {
                "summary_text": summary,
                "insights": insights,
                "highlights": highlights,
                "formatted_sections": {
                    "overview": summary,
                    "key_findings": insights[:5],  # Top 5 insights
                    "data_highlights": highlights[:3]  # Top 3 highlights
                },
                "metadata": {
                    "insight_count": len(insights),
                    "highlight_count": len(highlights),
                    "summary_length": len(summary)
                }
            }
            
            return formatted
            
        except Exception as e:
            self.logger.error(f"Error formatting summary: {e}")
            return {
                "summary_text": summary,
                "insights": insights,
                "highlights": highlights,
                "formatted_sections": {
                    "overview": summary,
                    "key_findings": insights,
                    "data_highlights": highlights
                },
                "metadata": {
                    "insight_count": len(insights),
                    "highlight_count": len(highlights),
                    "summary_length": len(summary)
                }
            }
    
    async def format_for_export(self, summary_data: Dict[str, Any], format_type: str = "json") -> str:
        """
        Format summary for export.
        
        Args:
            summary_data: Summary data to format
            format_type: Export format (json, text, markdown)
            
        Returns:
            Formatted export string
        """
        try:
            if format_type == "json":
                return await self._format_json_export(summary_data)
            elif format_type == "text":
                return await self._format_text_export(summary_data)
            elif format_type == "markdown":
                return await self._format_markdown_export(summary_data)
            else:
                return await self._format_default_export(summary_data)
                
        except Exception as e:
            self.logger.error(f"Error formatting for export: {e}")
            return f"Error formatting export: {str(e)}"
    
    async def _format_json_export(self, summary_data: Dict[str, Any]) -> str:
        """Format as JSON export."""
        try:
            import json
            return json.dumps(summary_data, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error formatting JSON export: {e}")
            return "{}"
    
    async def _format_text_export(self, summary_data: Dict[str, Any]) -> str:
        """Format as text export."""
        try:
            text_parts = []
            
            # Summary
            text_parts.append("SUMMARY")
            text_parts.append("=" * 50)
            text_parts.append(summary_data.get("summary_text", ""))
            text_parts.append("")
            
            # Key findings
            insights = summary_data.get("insights", [])
            if insights:
                text_parts.append("KEY FINDINGS")
                text_parts.append("-" * 30)
                for i, insight in enumerate(insights, 1):
                    text_parts.append(f"{i}. {insight}")
                text_parts.append("")
            
            # Data highlights
            highlights = summary_data.get("highlights", [])
            if highlights:
                text_parts.append("DATA HIGHLIGHTS")
                text_parts.append("-" * 30)
                for i, highlight in enumerate(highlights, 1):
                    text_parts.append(f"{i}. {highlight}")
                text_parts.append("")
            
            return "\n".join(text_parts)
            
        except Exception as e:
            self.logger.error(f"Error formatting text export: {e}")
            return "Error formatting text export"
    
    async def _format_markdown_export(self, summary_data: Dict[str, Any]) -> str:
        """Format as markdown export."""
        try:
            markdown_parts = []
            
            # Summary
            markdown_parts.append("# Summary")
            markdown_parts.append("")
            markdown_parts.append(summary_data.get("summary_text", ""))
            markdown_parts.append("")
            
            # Key findings
            insights = summary_data.get("insights", [])
            if insights:
                markdown_parts.append("## Key Findings")
                markdown_parts.append("")
                for insight in insights:
                    markdown_parts.append(f"- {insight}")
                markdown_parts.append("")
            
            # Data highlights
            highlights = summary_data.get("highlights", [])
            if highlights:
                markdown_parts.append("## Data Highlights")
                markdown_parts.append("")
                for highlight in highlights:
                    markdown_parts.append(f"- {highlight}")
                markdown_parts.append("")
            
            return "\n".join(markdown_parts)
            
        except Exception as e:
            self.logger.error(f"Error formatting markdown export: {e}")
            return "# Error\n\nError formatting markdown export"
    
    async def _format_default_export(self, summary_data: Dict[str, Any]) -> str:
        """Format as default export (text)."""
        return await self._format_text_export(summary_data)
    
    async def validate_summary_data(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate summary data structure.
        
        Args:
            summary_data: Summary data to validate
            
        Returns:
            Validation result dictionary
        """
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": []
            }
            
            # Check required fields
            required_fields = ["summary_text", "insights", "highlights"]
            for field in required_fields:
                if field not in summary_data:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
            
            # Check data types
            if "insights" in summary_data and not isinstance(summary_data["insights"], list):
                validation_result["errors"].append("Insights must be a list")
                validation_result["valid"] = False
            
            if "highlights" in summary_data and not isinstance(summary_data["highlights"], list):
                validation_result["errors"].append("Highlights must be a list")
                validation_result["valid"] = False
            
            # Check content quality
            if "summary_text" in summary_data:
                summary_text = summary_data["summary_text"]
                if len(summary_text) < 10:
                    validation_result["warnings"].append("Summary text is very short")
                elif len(summary_text) > 1000:
                    validation_result["warnings"].append("Summary text is very long")
            
            # Check insights quality
            if "insights" in summary_data:
                insights = summary_data["insights"]
                if len(insights) == 0:
                    validation_result["warnings"].append("No insights provided")
                elif len(insights) > 10:
                    validation_result["suggestions"].append("Consider limiting insights to top 10")
            
            # Check highlights quality
            if "highlights" in summary_data:
                highlights = summary_data["highlights"]
                if len(highlights) == 0:
                    validation_result["warnings"].append("No highlights provided")
                elif len(highlights) > 5:
                    validation_result["suggestions"].append("Consider limiting highlights to top 5")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating summary data: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "suggestions": []
            }

