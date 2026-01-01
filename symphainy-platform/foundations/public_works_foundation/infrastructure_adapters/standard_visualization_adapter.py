#!/usr/bin/env python3
"""
Standard Visualization Adapter

Infrastructure adapter for standard visualization capabilities using matplotlib, seaborn, plotly.

WHAT (Infrastructure Adapter Role): I provide standard visualization capabilities
HOW (Adapter Implementation): I wrap matplotlib, seaborn, plotly for visual displays
"""

import logging
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64
import io

from ..abstraction_contracts.visualization_protocol import VisualizationResult


class StandardVisualizationAdapter:
    """
    Standard Visualization Adapter
    
    Provides standard visualization capabilities using matplotlib, seaborn, plotly.
    """
    
    def __init__(self):
        """Initialize Standard Visualization Adapter."""
        self.logger = logging.getLogger("StandardVisualizationAdapter")
        self.logger.info("🏗️ StandardVisualizationAdapter initialized")
        
        # Set style for consistent plots
        plt.style.use('default')
        sns.set_palette("husl")
    
    async def create_summary_dashboard(self, pillar_outputs: Dict[str, Any]) -> VisualizationResult:
        """
        Create summary dashboard showing outputs from all pillars.
        
        Args:
            pillar_outputs: Summary outputs from Data, Insights, and Operations pillars
            
        Returns:
            VisualizationResult: Dashboard visualization
        """
        try:
            self.logger.info("Creating summary dashboard for pillar outputs...")
            
            # Create subplot layout
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    "Data Pillar Summary",
                    "Insights Pillar Summary", 
                    "Operations Pillar Summary",
                    "Overall Journey Progress"
                ],
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "scatter"}]]
            )
            
            # Data Pillar Summary
            data_summary = pillar_outputs.get("data_pillar", {})
            data_files = len(data_summary.get("files_uploaded", []))
            data_quality = data_summary.get("data_quality", "unknown")
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=data_files,
                    title={"text": "Files Uploaded"},
                    delta={"reference": 0},
                    domain={"row": 0, "column": 0}
                )
            )
            
            # Insights Pillar Summary
            insights_summary = pillar_outputs.get("insights_pillar", {})
            insights_count = len(insights_summary.get("insights", []))
            recommendations_count = len(insights_summary.get("recommendations", []))
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=insights_count,
                    title={"text": "Key Insights"},
                    delta={"reference": 0},
                    domain={"row": 0, "column": 1}
                )
            )
            
            # Operations Pillar Summary
            operations_summary = pillar_outputs.get("operations_pillar", {})
            blueprint = operations_summary.get("blueprint", {})
            improvements_count = len(blueprint.get("improvements", []))
            
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=improvements_count,
                    title={"text": "Process Improvements"},
                    delta={"reference": 0},
                    domain={"row": 1, "column": 0}
                )
            )
            
            # Overall Journey Progress
            progress_data = {
                "Data Upload": 100 if data_files > 0 else 0,
                "Insights Analysis": 100 if insights_count > 0 else 0,
                "Operations Blueprint": 100 if improvements_count > 0 else 0,
                "Business Outcomes": 0  # Will be completed after POC generation
            }
            
            fig.add_trace(
                go.Bar(
                    x=list(progress_data.keys()),
                    y=list(progress_data.values()),
                    name="Journey Progress",
                    marker_color=["green", "green", "green", "orange"]
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title="Business Outcomes Journey Summary",
                height=600,
                showlegend=False
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=800, height=600)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="summary_dashboard",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "standard",
                    "pillar_outputs": pillar_outputs,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create summary dashboard: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="summary_dashboard",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def create_roadmap_visualization(self, roadmap_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create roadmap visualization as standalone visual element.
        
        Args:
            roadmap_data: Roadmap data from Strategic Planning service
            
        Returns:
            VisualizationResult: Roadmap visualization
        """
        try:
            self.logger.info("Creating roadmap visualization...")
            
            # Extract phases and timeline data
            phases = roadmap_data.get("phases", [])
            timeline = roadmap_data.get("timeline", {})
            
            if not phases:
                return VisualizationResult(
                    success=False,
                    visualization_type="roadmap",
                    chart_data={},
                    image_base64="",
                    metadata={},
                    error="No phases data available for roadmap"
                )
            
            # Create Gantt chart
            fig = go.Figure()
            
            # Calculate cumulative timeline
            current_week = 0
            for i, phase in enumerate(phases):
                duration = phase.get("duration_weeks", 4)
                phase_name = phase.get("name", f"Phase {i+1}")
                
                fig.add_trace(go.Scatter(
                    x=[current_week, current_week + duration, current_week + duration, current_week, current_week],
                    y=[i, i, i+0.8, i+0.8, i],
                    fill="toself",
                    fillcolor=f"hsl({i*60}, 70%, 80%)",
                    line=dict(color=f"hsl({i*60}, 70%, 50%)", width=2),
                    name=phase_name,
                    text=f"{phase_name}<br>{duration} weeks",
                    textposition="middle center",
                    hoverinfo="text"
                ))
                
                current_week += duration
            
            # Update layout
            fig.update_layout(
                title="Strategic Roadmap Timeline",
                xaxis_title="Weeks",
                yaxis_title="Phases",
                height=400,
                showlegend=True,
                yaxis=dict(
                    tickmode="array",
                    tickvals=list(range(len(phases))),
                    ticktext=[phase.get("name", f"Phase {i+1}") for i, phase in enumerate(phases)]
                )
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=1000, height=400)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="roadmap",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "standard",
                    "phases_count": len(phases),
                    "total_duration_weeks": current_week,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create roadmap visualization: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="roadmap",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def create_financial_visualization(self, financial_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create financial analysis visualization.
        
        Args:
            financial_data: Financial analysis data
            
        Returns:
            VisualizationResult: Financial visualization
        """
        try:
            self.logger.info("Creating financial analysis visualization...")
            
            # Extract financial metrics
            roi_analysis = financial_data.get("roi_analysis", {})
            risk_assessment = financial_data.get("risk_assessment", {})
            
            # Create subplot layout
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=["ROI Analysis", "Risk Assessment"],
                specs=[[{"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # ROI Analysis
            roi_percentage = roi_analysis.get("roi_percentage", 0)
            npv = roi_analysis.get("npv", 0)
            
            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=roi_percentage,
                    title={"text": "ROI %"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 20], "color": "lightgray"},
                            {"range": [20, 50], "color": "yellow"},
                            {"range": [50, 100], "color": "green"}
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 20
                        }
                    },
                    domain={"row": 0, "column": 0}
                )
            )
            
            # Risk Assessment
            risk_score = risk_assessment.get("risk_score", 0)
            risk_level = risk_assessment.get("risk_level", "unknown")
            
            risk_color = "green" if risk_level == "low" else "yellow" if risk_level == "medium" else "red"
            
            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=risk_score * 100,
                    title={"text": "Risk Score"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": risk_color},
                        "steps": [
                            {"range": [0, 30], "color": "green"},
                            {"range": [30, 70], "color": "yellow"},
                            {"range": [70, 100], "color": "red"}
                        ]
                    },
                    domain={"row": 0, "column": 1}
                )
            )
            
            # Update layout
            fig.update_layout(
                title="Financial Analysis Dashboard",
                height=400
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=800, height=400)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="financial_analysis",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "standard",
                    "roi_percentage": roi_percentage,
                    "risk_level": risk_level,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create financial visualization: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="financial_analysis",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def create_metrics_dashboard(self, metrics_data: Dict[str, Any]) -> VisualizationResult:
        """
        Create business metrics dashboard.
        
        Args:
            metrics_data: Business metrics data
            
        Returns:
            VisualizationResult: Metrics dashboard
        """
        try:
            self.logger.info("Creating business metrics dashboard...")
            
            # Extract KPIs
            kpis = metrics_data.get("kpis", {})
            benchmark_results = metrics_data.get("benchmark_results", {})
            
            # Create subplot layout
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=["Performance Score", "Revenue vs Costs", "Benchmark Comparison", "Growth Metrics"],
                specs=[[{"type": "indicator"}, {"type": "scatter"}],
                       [{"type": "scatter"}, {"type": "indicator"}]]
            )
            
            # Performance Score
            performance_score = kpis.get("performance_score", 0)
            fig.add_trace(
                go.Indicator(
                    mode="number+gauge",
                    value=performance_score,
                    title={"text": "Performance Score"},
                    gauge={
                        "axis": {"range": [None, 100]},
                        "bar": {"color": "darkgreen"},
                        "steps": [
                            {"range": [0, 40], "color": "lightgray"},
                            {"range": [40, 70], "color": "yellow"},
                            {"range": [70, 100], "color": "green"}
                        ]
                    },
                    domain={"row": 0, "column": 0}
                )
            )
            
            # Revenue vs Costs
            revenue = kpis.get("revenue", 0)
            costs = kpis.get("costs", 0)
            profit = revenue - costs
            
            fig.add_trace(
                go.Bar(
                    x=["Revenue", "Costs", "Profit"],
                    y=[revenue, costs, profit],
                    name="Financial Metrics",
                    marker_color=["green", "red", "blue"],
                    text=[f"${revenue:,.0f}", f"${costs:,.0f}", f"${profit:,.0f}"],
                    textposition="auto"
                ),
                row=1, col=1
            )
            
            # Benchmark Comparison
            if benchmark_results:
                metrics = list(benchmark_results.keys())
                percentiles = [benchmark_results[metric].get("percentile", 0) for metric in metrics]
                
                fig.add_trace(
                    go.Bar(
                        x=metrics,
                        y=percentiles,
                        name="Benchmark Percentiles",
                        marker_color="lightblue",
                        text=[f"{p:.1f}%" for p in percentiles],
                        textposition="auto"
                    ),
                    row=2, col=1
                )
            
            # Growth Rate
            growth_rate = kpis.get("growth_rate", 0)
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=growth_rate,
                    title={"text": "Growth Rate %"},
                    delta={"reference": 0},
                    domain={"row": 2, "column": 1}
                )
            )
            
            # Update layout
            fig.update_layout(
                title="Business Metrics Dashboard",
                height=600,
                showlegend=True
            )
            
            # Convert to base64 for web display
            img_bytes = fig.to_image(format="png", width=1000, height=600)
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return VisualizationResult(
                success=True,
                visualization_type="metrics_dashboard",
                chart_data=fig.to_dict(),
                image_base64=img_base64,
                metadata={
                    "creation_method": "standard",
                    "performance_score": performance_score,
                    "growth_rate": growth_rate,
                    "created_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create metrics dashboard: {e}")
            return VisualizationResult(
                success=False,
                visualization_type="metrics_dashboard",
                chart_data={},
                image_base64="",
                metadata={},
                error=str(e)
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the adapter."""
        try:
            # Test basic functionality
            test_data = {
                "data_pillar": {"files_uploaded": ["test.csv"], "data_quality": "high"},
                "insights_pillar": {"insights": ["test insight"], "recommendations": ["test recommendation"]},
                "operations_pillar": {"blueprint": {"improvements": ["test improvement"]}}
            }
            
            result = await self.create_summary_dashboard(test_data)
            
            return {
                "status": "healthy" if result.success else "unhealthy",
                "adapter": "StandardVisualizationAdapter",
                "capabilities": [
                    "summary_dashboard",
                    "roadmap_visualization",
                    "financial_visualization",
                    "metrics_dashboard"
                ],
                "dependencies": {
                    "matplotlib": plt.matplotlib.__version__,
                    "seaborn": sns.__version__,
                    "plotly": go.__version__
                },
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "adapter": "StandardVisualizationAdapter",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
