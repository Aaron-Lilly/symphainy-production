#!/usr/bin/env python3
"""
SOP Visualization Workflow

WHAT: Prepares SOP structures for visualization/display
HOW: Formats parsed SOP data for frontend document rendering

This workflow implements the SOP visualization flow:
1. Retrieve SOP structure (from file_id via data mash or provided content)
2. Format sections/steps for document rendering (Markdown, HTML, etc.)
3. Return visualization-ready data

Key Principle: This is for DISPLAY/VISUALIZATION, not conversion.
Separate from WorkflowToSOPWorkflow which converts Workflow → SOP.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class SOPVisualizationWorkflow:
    """
    Workflow for preparing SOP structures for visualization.
    
    Takes parsed SOP structure and formats it for frontend document rendering.
    Supports multiple document formats: Markdown, HTML, structured JSON, etc.
    """
    
    def __init__(self, orchestrator):
        """
        Initialize workflow with orchestrator context.
        
        Args:
            orchestrator: OperationsJourneyOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = logger
    
    async def execute(
        self,
        sop_file_id: Optional[str] = None,
        sop_content: Optional[Dict[str, Any]] = None,
        visualization_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute SOP visualization workflow.
        
        Args:
            sop_file_id: Optional SOP file identifier (will fetch from data mash)
            sop_content: Optional SOP content (structure from parsing)
            visualization_options: Optional visualization options
                - format: "markdown" (default), "html", "structured"
                - style: "default", "compact", "detailed"
            user_context: Optional user context (includes workflow_id, solution_context)
        
        Returns:
            Dict with visualization_data (formatted sections, steps, metadata), format_type, etc.
        """
        try:
            self.logger.info("📊 Starting SOP visualization workflow")
            
            # Generate visualization ID
            visualization_id = f"viz_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            
            # Default options
            options = visualization_options or {}
            format_type = options.get("format", "markdown")  # markdown, html, structured
            style = options.get("style", "default")  # default, compact, detailed
            
            # Step 1: Get SOP content (from file_id or provided)
            if sop_file_id and not sop_content:
                # Fetch from data mash via Data Solution Orchestrator
                self.logger.info(f"📊 Fetching SOP content from data mash: {sop_file_id}")
                
                # Get Data Solution Orchestrator
                curator = await self.orchestrator.get_foundation_service("CuratorFoundationService")
                if curator:
                    data_orchestrator = await curator.discover_service_by_name("DataSolutionOrchestratorService")
                    if data_orchestrator:
                        sop_data = await data_orchestrator.orchestrate_data_mash(
                            client_data_query={"type": "file_id:" + sop_file_id},
                            user_context=user_context
                        )
                        if sop_data.get("success") and sop_data.get("client_data", {}).get("file"):
                            file_data = sop_data["client_data"]["file"]
                            parsed_files = sop_data["client_data"].get("parsed_files", [])
                            if parsed_files:
                                parse_result = parsed_files[0].get("metadata", {}).get("parse_result", {})
                                if parse_result.get("parsing_type") == "sop":
                                    sop_content = parse_result.get("structure", {})
                                    self.logger.info(f"✅ Extracted SOP structure: {len(sop_content.get('sections', []))} sections")
                                else:
                                    return {
                                        "success": False,
                                        "error": f"File {sop_file_id} is not a parsed SOP file",
                                        "visualization_id": visualization_id,
                                        "workflow_id": workflow_id
                                    }
            
            if not sop_content:
                return {
                    "success": False,
                    "error": "SOP content not provided and could not be fetched from data mash",
                    "visualization_id": visualization_id,
                    "workflow_id": workflow_id
                }
            
            # Step 2: Format SOP structure for visualization
            visualization_data = await self._format_for_visualization(
                sop_content=sop_content,
                format_type=format_type,
                style=style
            )
            
            # Step 3: Build result
            result = {
                "success": True,
                "visualization_id": visualization_id,
                "workflow_id": workflow_id,
                "format_type": format_type,
                "style": style,
                "visualization_data": visualization_data,
                "metadata": {
                    "section_count": len(sop_content.get("sections", [])),
                    "step_count": sum(len(s.get("steps", [])) for s in sop_content.get("sections", [])),
                    "role_count": len(sop_content.get("roles", [])),
                    "sop_file_id": sop_file_id
                }
            }
            
            self.logger.info(f"✅ SOP visualization complete: {visualization_id} ({len(sop_content.get('sections', []))} sections)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ SOP visualization workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            workflow_id = user_context.get("workflow_id") if user_context else str(uuid.uuid4())
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    async def _format_for_visualization(
        self,
        sop_content: Dict[str, Any],
        format_type: str,
        style: str
    ) -> Dict[str, Any]:
        """
        Format SOP structure for visualization.
        
        Args:
            sop_content: SOP structure from parsing
            format_type: Format type ("markdown", "html", "structured")
            style: Style ("default", "compact", "detailed")
        
        Returns:
            Formatted visualization data with sections, steps, metadata
        """
        title = sop_content.get("title", "Untitled SOP")
        sections = sop_content.get("sections", [])
        roles = sop_content.get("roles", [])
        dependencies = sop_content.get("dependencies", [])
        
        if format_type == "markdown":
            # Format as Markdown
            markdown_content = f"# {title}\n\n"
            
            if roles:
                markdown_content += "## Roles\n\n"
                for role in roles:
                    markdown_content += f"- {role}\n"
                markdown_content += "\n"
            
            if dependencies:
                markdown_content += "## Dependencies\n\n"
                for dep in dependencies:
                    markdown_content += f"- {dep}\n"
                markdown_content += "\n"
            
            for section in sections:
                heading = section.get("heading", "")
                content = section.get("content", "")
                steps = section.get("steps", [])
                
                markdown_content += f"## {heading}\n\n"
                
                if content:
                    markdown_content += f"{content}\n\n"
                
                if steps:
                    for step in steps:
                        step_text = step.get("text", "") or step.get("content", "")
                        markdown_content += f"- {step_text}\n"
                    markdown_content += "\n"
            
            return {
                "format": "markdown",
                "content": markdown_content,
                "structured": {
                    "title": title,
                    "sections": sections,
                    "roles": roles,
                    "dependencies": dependencies
                }
            }
        
        elif format_type == "html":
            # Format as HTML
            html_content = f"<h1>{title}</h1>\n"
            
            if roles:
                html_content += "<h2>Roles</h2>\n<ul>\n"
                for role in roles:
                    html_content += f"<li>{role}</li>\n"
                html_content += "</ul>\n"
            
            if dependencies:
                html_content += "<h2>Dependencies</h2>\n<ul>\n"
                for dep in dependencies:
                    html_content += f"<li>{dep}</li>\n"
                html_content += "</ul>\n"
            
            for section in sections:
                heading = section.get("heading", "")
                content = section.get("content", "")
                steps = section.get("steps", [])
                
                html_content += f"<h2>{heading}</h2>\n"
                
                if content:
                    html_content += f"<p>{content}</p>\n"
                
                if steps:
                    html_content += "<ul>\n"
                    for step in steps:
                        step_text = step.get("text", "") or step.get("content", "")
                        html_content += f"<li>{step_text}</li>\n"
                    html_content += "</ul>\n"
            
            return {
                "format": "html",
                "content": html_content,
                "structured": {
                    "title": title,
                    "sections": sections,
                    "roles": roles,
                    "dependencies": dependencies
                }
            }
        
        else:  # structured
            # Return structured format (for frontend to render)
            return {
                "format": "structured",
                "structured": {
                    "title": title,
                    "sections": sections,
                    "roles": roles,
                    "dependencies": dependencies
                }
            }









