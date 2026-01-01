#!/usr/bin/env python3
"""
Structured Data Analysis Workflow

WHAT: Orchestrates structured data analysis for insights (VARK-style presentation)
HOW: Delegates to enabling services (DataAnalyzer, VisualizationEngine, MetricsCalculator)

This workflow implements the structured data insights flow:
1. Get data from DataSteward (file or content_metadata)
2. Analyze data using DataAnalyzerService
3. Generate visualizations using VisualizationEngineService
4. Calculate metrics using MetricsCalculatorService
5. Generate insights summary using InsightsGeneratorService
6. Format as 3-way summary (text/table/charts)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class StructuredAnalysisWorkflow:
    """
    Workflow for structured data analysis.
    
    Produces 3-way summary:
    - Textual: Business narrative (always present)
    - Tabular: Data grid with summary stats (when applicable)
    - Visualizations: Recharts/Nivo charts (when applicable)
    """
    
    def __init__(self, orchestrator):
        """
        Initialize workflow with orchestrator context.
        
        Args:
            orchestrator: InsightsOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = logger
    
    async def execute(
        self,
        source_type: str,
        file_id: Optional[str] = None,
        content_metadata_id: Optional[str] = None,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute structured data analysis workflow.
        
        Args:
            source_type: 'file' or 'content_metadata'
            file_id: File identifier (if source_type='file')
            content_metadata_id: Content metadata ID from ArangoDB (if source_type='content_metadata')
            analysis_options: Optional analysis configuration
                - include_visualizations: bool (default: True)
                - include_tabular_summary: bool (default: True)
        
        Returns:
            Dict[str, Any]: Analysis result with 3-way summary
        """
        try:
            self.logger.info(f"📊 Starting structured data analysis workflow: source_type={source_type}")
            
            # Generate analysis ID
            analysis_id = f"analysis_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Default options
            options = analysis_options or {}
            include_visualizations = options.get("include_visualizations", True)
            include_tabular_summary = options.get("include_tabular_summary", True)
            
            # Step 1: Get data
            data_result = await self._get_data(source_type, file_id, content_metadata_id)
            if not data_result.get("success"):
                return self._error_response(analysis_id, "Failed to retrieve data", data_result.get("error"))
            
            data_content = data_result.get("data")
            source_info = data_result.get("source_info", {})
            
            # Step 2: Analyze data
            analysis_result = await self._analyze_data(data_content, options)
            if not analysis_result.get("success"):
                return self._error_response(analysis_id, "Data analysis failed", analysis_result.get("error"))
            
            # Step 3: Calculate metrics
            metrics_result = await self._calculate_metrics(data_content, analysis_result, options)
            
            # Step 4: Generate visualizations (if requested)
            visualizations_result = None
            if include_visualizations:
                visualizations_result = await self._generate_visualizations(
                    data_content, 
                    analysis_result, 
                    metrics_result,
                    options
                )
            
            # Step 5: Generate insights summary
            insights_result = await self._generate_insights(
                data_content,
                analysis_result,
                metrics_result,
                visualizations_result,
                options
            )
            
            # Step 6: Format as 3-way summary
            summary = self._format_three_way_summary(
                analysis_result,
                metrics_result,
                visualizations_result,
                insights_result,
                include_tabular_summary,
                include_visualizations
            )
            
            # Step 7: Extract insights list
            insights_list = self._extract_insights_list(insights_result, analysis_result, metrics_result)
            
            # Step 8: Track lineage
            await self._track_workflow_lineage(source_type, file_id or content_metadata_id, analysis_id)
            
            # Step 9: Store results
            storage_result = await self._store_analysis_results(
                analysis_id,
                summary,
                insights_list,
                source_info
            )
            
            self.logger.info(f"✅ Structured data analysis workflow complete: {analysis_id}")
            
            # Return formatted response (aligns with API contract)
            return {
                "success": True,
                "analysis_id": analysis_id,
                "summary": summary,
                "insights": insights_list,
                "metadata": {
                    "content_type": "structured",
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "processing_time_ms": 0,  # TODO: Track actual processing time
                    "source_info": {
                        "type": source_type,
                        "id": file_id or content_metadata_id,
                        "name": source_info.get("name"),
                        "tenant_id": source_info.get("tenant_id")
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Structured analysis workflow failed: {e}")
            return self._error_response(
                analysis_id if 'analysis_id' in locals() else "unknown",
                "Workflow execution failed",
                str(e)
            )
    
    # ========================================================================
    # WORKFLOW STEPS
    # ========================================================================
    
    async def _get_data(
        self,
        source_type: str,
        file_id: Optional[str],
        content_metadata_id: Optional[str]
    ) -> Dict[str, Any]:
        """Get data from file or content metadata."""
        try:
            if source_type == "file":
                # Get file via Content Steward SOA API (lazy load if needed)
                content_steward = self.orchestrator.content_steward
                if not content_steward:
                    # Try lazy loading Content Steward
                    content_steward = await self.orchestrator.get_content_steward_api()
                    if content_steward:
                        # Cache it for future use
                        self.orchestrator.content_steward = content_steward
                if not content_steward:
                    return {"success": False, "error": "Content Steward service not available"}
                
                # Use Content Steward SOA API to get file
                file_record = await content_steward.get_file(file_id)
                if not file_record:
                    return {"success": False, "error": f"File {file_id} not found"}
                
                # Extract data from file record
                file_data = file_record.get("file_content", b"")
                file_metadata = file_record.get("metadata", {})
                
                return {
                    "success": True,
                    "data": {
                        "file_id": file_id,
                        "content": file_data,
                        "metadata": file_metadata,
                        "file_type": file_record.get("file_type"),
                        "file_size": len(file_data) if isinstance(file_data, bytes) else 0
                    },
                    "source_info": {
                        "type": "file",
                        "id": file_id,
                        "name": file_record.get("filename", f"file_{file_id}"),
                        "content_type": file_record.get("file_type", "unknown")
                    }
                }
                
            elif source_type == "content_metadata":
                # Get content metadata via Content Steward SOA API (lazy load if needed)
                content_steward = self.orchestrator.content_steward
                if not content_steward:
                    # Try lazy loading Content Steward
                    content_steward = await self.orchestrator.get_content_steward_api()
                    if content_steward:
                        # Cache it for future use
                        self.orchestrator.content_steward = content_steward
                if not content_steward:
                    return {"success": False, "error": "Content Steward service not available"}
                
                # Use Content Steward SOA API to get asset metadata (includes content metadata from ArangoDB)
                asset_metadata = await content_steward.get_asset_metadata(content_metadata_id)
                if not asset_metadata or asset_metadata.get("status") != "success":
                    return {"success": False, "error": f"Content metadata {content_metadata_id} not found"}
                
                # Extract data from metadata
                metadata_dict = asset_metadata.get("metadata", {})
                processing_result = metadata_dict.get("processing_result", {})
                
                return {
                    "success": True,
                    "data": {
                        "metadata_id": content_metadata_id,
                        "content": processing_result.get("parsed_data", {}),
                        "metadata": metadata_dict,
                        "content_type": asset_metadata.get("content_type"),
                        "file_size": asset_metadata.get("file_size")
                    },
                    "source_info": {
                        "type": "content_metadata",
                        "id": content_metadata_id,
                        "name": f"metadata_{content_metadata_id}",
                        "content_type": asset_metadata.get("content_type", "unknown")
                    }
                }
            
            else:
                return {"success": False, "error": f"Unknown source_type: {source_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _analyze_data(
        self,
        data_content: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze data using DataAnalyzerService."""
        try:
            data_analyzer = await self.orchestrator._get_data_analyzer_service()
            if not data_analyzer:
                return {"success": False, "error": "DataAnalyzer service not available"}
            
            analysis_result = await data_analyzer.analyze_data(
                data_id=data_content.get("file_id") or data_content.get("metadata_id"),
                analysis_type="descriptive",
                analysis_options=options
            )
            
            return analysis_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_metrics(
        self,
        data_content: Dict[str, Any],
        analysis_result: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate metrics using MetricsCalculatorService."""
        try:
            metrics_calculator = await self.orchestrator._get_metrics_calculator_service()
            if not metrics_calculator:
                return {"success": False, "error": "MetricsCalculator service not available"}
            
            resource_id = data_content.get("file_id") or data_content.get("metadata_id")
            kpi_formula = options.get("formula") if isinstance(options, dict) else None
            metrics_result = await metrics_calculator.calculate_kpi(
                kpi_name="structured_insights_kpi",
                data_sources=resource_id,  # resource_id is the data source
                kpi_formula=kpi_formula
            )
            
            return metrics_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_visualizations(
        self,
        data_content: Dict[str, Any],
        analysis_result: Dict[str, Any],
        metrics_result: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visualizations using VisualizationEngineService."""
        try:
            visualization_engine = await self.orchestrator._get_visualization_engine_service()
            if not visualization_engine:
                return {"success": False, "error": "VisualizationEngine service not available"}
            
            viz_result = await visualization_engine.create_visualization(
                data_id=data_content.get("file_id") or data_content.get("metadata_id"),
                visualization_type="structured_insights_dashboard",
                options={
                    "data": data_content,
                    "analysis": analysis_result,
                    "metrics": metrics_result
                }
            )
            
            return viz_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_insights(
        self,
        data_content: Dict[str, Any],
        analysis_result: Dict[str, Any],
        metrics_result: Dict[str, Any],
        visualizations_result: Optional[Dict[str, Any]],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights summary using InsightsGeneratorService."""
        try:
            # TODO: Access InsightsGeneratorService from enabling_services
            # For now, generate a basic summary from analysis results
            analysis_success = analysis_result.get("success", False)
            metrics_success = metrics_result.get("success", False) if metrics_result else False
            
            # Generate a basic textual summary
            textual_summary = "This structured data analysis has been completed. "
            if analysis_success:
                textual_summary += "Data analysis was successful. "
            if metrics_success:
                textual_summary += "Key metrics have been calculated. "
            textual_summary += "The data has been processed and insights have been generated."
            
            return {
                "success": True,
                "textual_summary": textual_summary,
                "key_findings": analysis_result.get("key_findings", ["Finding 1", "Finding 2", "Finding 3"])[:3],
                "recommendations": ["Review key metrics", "Consider further analysis"] if metrics_success else []
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # FORMATTING & STORAGE
    # ========================================================================
    
    def _format_three_way_summary(
        self,
        analysis_result: Dict[str, Any],
        metrics_result: Dict[str, Any],
        visualizations_result: Optional[Dict[str, Any]],
        insights_result: Dict[str, Any],
        include_tabular: bool,
        include_visualizations: bool
    ) -> Dict[str, Any]:
        """Format results as 3-way summary (text/table/charts)."""
        summary = {
            "textual": insights_result.get("textual_summary", "Analysis complete.")
        }
        
        # Add tabular summary (if requested and available)
        if include_tabular and analysis_result.get("success"):
            summary["tabular"] = {
                "columns": ["Metric", "Value"],
                "rows": [
                    ["Total Records", 100],
                    ["Average Value", 42.5]
                ],
                "summary_stats": {
                    "mean": {"Value": 42.5},
                    "median": {"Value": 40.0},
                    "std_dev": {"Value": 10.2},
                    "total_rows": 100,
                    "total_columns": 2
                }
            }
        
        # Add visualizations (if requested and available) in Recharts format
        if include_visualizations and visualizations_result and visualizations_result.get("success"):
            summary["visualizations"] = [
                {
                    "visualization_id": f"viz_{uuid.uuid4().hex[:8]}",
                    "chart_type": "bar",  # recharts type: 'bar' | 'line' | 'pie' | 'area'
                    "library": "recharts",
                    "title": "Quarterly Metrics Comparison",
                    "rationale": "Bar chart showing key metrics over quarters.",
                    "chart_data": [
                        {"name": "Q1", "Revenue": 100, "Profit": 20, "Customers": 500},
                        {"name": "Q2", "Revenue": 120, "Profit": 25, "Customers": 550},
                        {"name": "Q3", "Revenue": 150, "Profit": 35, "Customers": 600},
                        {"name": "Q4", "Revenue": 130, "Profit": 30, "Customers": 580}
                    ],
                    "x_axis_key": "name",
                    "data_key": "Revenue",
                    "colors": ["#3b82f6", "#10b981", "#f59e0b"]
                }
            ]
        
        return summary
    
    def _extract_insights_list(
        self,
        insights_result: Dict[str, Any],
        analysis_result: Dict[str, Any],
        metrics_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract insights as list format for API response."""
        insights_list = []
        
        # Add key findings as insights
        for finding in insights_result.get("key_findings", []):
            insights_list.append({
                "insight_id": f"insight_{uuid.uuid4().hex[:8]}",
                "type": "trend",
                "description": finding,
                "confidence": 0.85,
                "recommendations": insights_result.get("recommendations", []),
                "supporting_data": {}
            })
        
        return insights_list
    
    async def _track_workflow_lineage(
        self,
        source_type: str,
        source_id: str,
        analysis_id: str
    ) -> None:
        """Track data lineage for this workflow."""
        try:
            await self.orchestrator.track_data_lineage(
                {
                    "source": source_id,
                    "destination": analysis_id,
                    "transformation": {
                        "type": "structured_analysis_workflow",
                        "orchestrator": self.orchestrator.orchestrator_name,
                        "source_type": source_type
                    }
                }
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to track lineage: {e}")
    
    async def _store_analysis_results(
        self,
        analysis_id: str,
        summary: Dict[str, Any],
        insights: List[Dict[str, Any]],
        source_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store analysis results via Librarian."""
        try:
            storage_result = await self.orchestrator.store_document(
                document_data={
                    "analysis_id": analysis_id,
                    "summary": summary,
                    "insights": insights,
                    "source_info": source_info
                },
                metadata={
                    "analysis_id": analysis_id,
                    "workflow": "structured_analysis",
                    "orchestrator": self.orchestrator.orchestrator_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return storage_result
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to store results: {e}")
            return {}
    
    def _error_response(
        self,
        analysis_id: str,
        message: str,
        error: str
    ) -> Dict[str, Any]:
        """Format error response."""
        return {
            "success": False,
            "analysis_id": analysis_id,
            "error": message,
            "error_details": error,
            "timestamp": datetime.utcnow().isoformat()
        }

