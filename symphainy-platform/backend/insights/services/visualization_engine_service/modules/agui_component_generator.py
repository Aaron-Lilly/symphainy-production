#!/usr/bin/env python3
"""AGUI Component Generator module for Visualization Engine Service."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


class AGUIComponentGenerator:
    """AGUI Component Generator module for Visualization Engine Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
        self.utilities = service_instance.utilities_module
    
    async def create_chart_component(
        self,
        embeddings: List[Dict[str, Any]],
        visualization_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create AGUI chart component.
        
        AGUI chart component structure:
        {
            "type": "chart",
            "chart_type": "bar" | "line" | "scatter" | "histogram" | etc.,
            "data": [...],
            "config": {...},
            "metadata": {...}
        }
        
        Args:
            embeddings: List of embedding dictionaries
            visualization_spec: Chart specification:
                - chart_type: "bar", "line", "scatter", "histogram", etc.
                - x_axis: Column name for x-axis
                - y_axis: Column name for y-axis
                - title: Chart title
                - labels: Axis labels dict
                
        Returns:
            AGUI-compliant chart component
        """
        chart_type = visualization_spec.get("chart_type", "bar")
        
        # Validate chart type
        is_valid, error = self.utilities.validate_chart_type(chart_type)
        if not is_valid:
            raise ValueError(error)
        
        x_axis = visualization_spec.get("x_axis")
        y_axis = visualization_spec.get("y_axis")
        
        # Extract data from embeddings
        data = self._extract_chart_data_from_embeddings(embeddings, x_axis, y_axis, chart_type)
        
        # Generate visualization data using plotly (but format as AGUI component)
        chart_data = self._generate_chart_data(data, chart_type, x_axis, y_axis)
        
        # Create AGUI chart component
        component = {
            "type": "chart",
            "chart_type": chart_type,
            "data": chart_data,
            "config": {
                "x_axis": x_axis,
                "y_axis": y_axis,
                "title": visualization_spec.get("title", "Chart"),
                "labels": visualization_spec.get("labels", {}),
                "interactive": True
            },
            "metadata": {
                "content_id": visualization_spec.get("content_id"),
                "created_at": datetime.now().isoformat(),
                "data_points": len(data)
            }
        }
        
        return component
    
    async def create_dashboard_component(
        self,
        embeddings: List[Dict[str, Any]],
        visualization_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create AGUI dashboard component.
        
        AGUI dashboard component structure:
        {
            "type": "dashboard",
            "components": [...],  # Array of chart/table components
            "layout": {...},
            "metadata": {...}
        }
        
        Args:
            embeddings: List of embedding dictionaries
            visualization_spec: Dashboard specification:
                - components: List of component specs
                - layout: Layout configuration
                
        Returns:
            AGUI-compliant dashboard component
        """
        components = visualization_spec.get("components", [])
        
        # Create individual components
        dashboard_components = []
        for comp_spec in components:
            comp_type = comp_spec.get("type")
            if comp_type == "chart":
                comp = await self.create_chart_component(embeddings, comp_spec)
            elif comp_type == "table":
                comp = await self.create_table_component(embeddings, comp_spec)
            else:
                self.logger.warning(f"⚠️ Unknown component type in dashboard: {comp_type}")
                continue
            
            dashboard_components.append(comp)
        
        # Create AGUI dashboard component
        component = {
            "type": "dashboard",
            "components": dashboard_components,
            "layout": visualization_spec.get("layout", {
                "grid": "auto",
                "columns": 2,
                "responsive": True
            }),
            "metadata": {
                "content_id": visualization_spec.get("content_id"),
                "created_at": datetime.now().isoformat(),
                "component_count": len(dashboard_components)
            }
        }
        
        return component
    
    async def create_table_component(
        self,
        embeddings: List[Dict[str, Any]],
        visualization_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create AGUI table component.
        
        AGUI table component structure:
        {
            "type": "table",
            "columns": [...],
            "rows": [...],
            "config": {...},
            "metadata": {...}
        }
        
        Args:
            embeddings: List of embedding dictionaries
            visualization_spec: Table specification:
                - columns: List of column names
                - sortable: Whether table is sortable
                - filterable: Whether table is filterable
                - pageable: Whether table is pageable
                
        Returns:
            AGUI-compliant table component
        """
        # Extract table data from embeddings
        columns = visualization_spec.get("columns", [])
        
        # If columns not specified, extract from embeddings
        if not columns:
            columns = self.utilities.extract_column_names(embeddings)
        
        rows = self._extract_table_data_from_embeddings(embeddings, columns)
        
        # Create AGUI table component
        component = {
            "type": "table",
            "columns": [
                {
                    "name": col,
                    "label": col.replace("_", " ").title(),
                    "type": self._infer_column_type(embeddings, col)
                }
                for col in columns
            ],
            "rows": rows,
            "config": {
                "sortable": visualization_spec.get("sortable", True),
                "filterable": visualization_spec.get("filterable", True),
                "pageable": visualization_spec.get("pageable", True),
                "page_size": visualization_spec.get("page_size", 50)
            },
            "metadata": {
                "content_id": visualization_spec.get("content_id"),
                "created_at": datetime.now().isoformat(),
                "row_count": len(rows),
                "column_count": len(columns)
            }
        }
        
        return component
    
    def _extract_chart_data_from_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        x_axis: Optional[str],
        y_axis: Optional[str],
        chart_type: str
    ) -> List[Dict[str, Any]]:
        """
        Extract chart data from embeddings.
        
        Args:
            embeddings: List of embedding dictionaries
            x_axis: Column name for x-axis
            y_axis: Column name for y-axis
            chart_type: Type of chart
            
        Returns:
            List of data points
        """
        data = []
        
        # For schema embeddings, extract sample values
        for emb in embeddings:
            column_name = emb.get("column_name") or emb.get("column") or emb.get("field_name")
            if not column_name:
                continue
            
            sample_values = emb.get("sample_values") or emb.get("samples") or []
            metadata = emb.get("metadata") or {}
            
            # Create data points from sample values
            if sample_values and isinstance(sample_values, list):
                for idx, value in enumerate(sample_values[:100]):  # Limit to 100 samples
                    point = {
                        "index": idx,
                        "column": column_name
                    }
                    
                    # Add x-axis value
                    if x_axis:
                        if column_name == x_axis:
                            point["x"] = value
                        else:
                            # Try to get from metadata or use index
                            point["x"] = metadata.get("mean") or idx
                    
                    # Add y-axis value
                    if y_axis:
                        if column_name == y_axis:
                            point["y"] = value
                        else:
                            # Try to get from metadata or use index
                            point["y"] = metadata.get("mean") or idx
                    
                    # For single-axis charts (histogram), use value directly
                    if chart_type == "histogram" and not y_axis:
                        point["value"] = value
                    
                    if point:
                        data.append(point)
        
        return data
    
    def _generate_chart_data(
        self,
        data: List[Dict[str, Any]],
        chart_type: str,
        x_axis: Optional[str],
        y_axis: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate chart data using plotly (formatted as AGUI component data).
        
        Args:
            data: List of data points
            chart_type: Type of chart
            x_axis: X-axis column name
            y_axis: Y-axis column name
            
        Returns:
            Chart data dictionary (AGUI-compliant format)
        """
        if not data:
            return {"series": [], "categories": []}
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(data)
        
        # Generate chart data based on type
        if chart_type == "bar":
            if x_axis and y_axis:
                chart_data = {
                    "series": [
                        {
                            "name": y_axis,
                            "data": df["y"].tolist() if "y" in df.columns else []
                        }
                    ],
                    "categories": df["x"].tolist() if "x" in df.columns else []
                }
            else:
                # Group by column and count
                chart_data = {
                    "series": [
                        {
                            "name": "Count",
                            "data": df["column"].value_counts().tolist()
                        }
                    ],
                    "categories": df["column"].value_counts().index.tolist()
                }
        
        elif chart_type == "line":
            chart_data = {
                "series": [
                    {
                        "name": y_axis or "Value",
                        "data": df["y"].tolist() if "y" in df.columns else df["value"].tolist() if "value" in df.columns else []
                    }
                ],
                "categories": df["x"].tolist() if "x" in df.columns else list(range(len(df)))
            }
        
        elif chart_type == "scatter":
            chart_data = {
                "series": [
                    {
                        "name": "Data Points",
                        "data": [
                            {"x": row.get("x"), "y": row.get("y")}
                            for _, row in df.iterrows()
                            if "x" in row and "y" in row
                        ]
                    }
                ],
                "categories": []
            }
        
        elif chart_type == "histogram":
            values = df["value"].tolist() if "value" in df.columns else df["y"].tolist() if "y" in df.columns else []
            chart_data = {
                "series": [
                    {
                        "name": "Frequency",
                        "data": values
                    }
                ],
                "categories": list(range(len(values)))
            }
        
        else:
            # Default: bar chart
            chart_data = {
                "series": [
                    {
                        "name": "Value",
                        "data": df["value"].tolist() if "value" in df.columns else []
                    }
                ],
                "categories": list(range(len(df)))
            }
        
        return chart_data
    
    def _extract_table_data_from_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        columns: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Extract table data from embeddings.
        
        Args:
            embeddings: List of embedding dictionaries
            columns: List of column names to extract
            
        Returns:
            List of row dictionaries
        """
        rows = []
        
        for emb in embeddings:
            row = {}
            column_name = emb.get("column_name") or emb.get("column") or emb.get("field_name")
            
            # If column_name is in requested columns, add it
            if column_name in columns:
                row[column_name] = {
                    "value": emb.get("sample_values", [])[:10] if emb.get("sample_values") else [],
                    "metadata": emb.get("metadata", {}),
                    "data_type": emb.get("data_type", "unknown")
                }
            
            # Add other requested columns if they exist in embedding
            for col in columns:
                if col not in row and col in emb:
                    row[col] = emb[col]
            
            if row:
                rows.append(row)
        
        return rows
    
    def _infer_column_type(self, embeddings: List[Dict[str, Any]], column_name: str) -> str:
        """
        Infer column type from embeddings.
        
        Args:
            embeddings: List of embedding dictionaries
            column_name: Column name to infer type for
            
        Returns:
            Column type string
        """
        for emb in embeddings:
            if (emb.get("column_name") or emb.get("column") or emb.get("field_name")) == column_name:
                data_type = emb.get("data_type", "unknown")
                # Normalize to standard types
                if data_type.lower() in ["int", "integer", "float", "number", "numeric"]:
                    return "number"
                elif data_type.lower() in ["string", "str", "text"]:
                    return "string"
                elif data_type.lower() in ["bool", "boolean"]:
                    return "boolean"
                elif data_type.lower() in ["date", "datetime", "timestamp"]:
                    return "date"
                else:
                    return "string"
        
        return "string"
    
    def get_agui_schema_for_type(self, visualization_type: str) -> Dict[str, Any]:
        """
        Get AGUI schema for visualization type.
        
        Args:
            visualization_type: Type of visualization
            
        Returns:
            AGUI schema dictionary
        """
        # Fallback schema (can be enhanced with AGUI schema registry later)
        schemas = {
            "chart": {
                "type": "chart",
                "schema_version": "1.0",
                "properties": {
                    "chart_type": {"type": "string"},
                    "data": {"type": "object"},
                    "config": {"type": "object"}
                }
            },
            "dashboard": {
                "type": "dashboard",
                "schema_version": "1.0",
                "properties": {
                    "components": {"type": "array"},
                    "layout": {"type": "object"}
                }
            },
            "table": {
                "type": "table",
                "schema_version": "1.0",
                "properties": {
                    "columns": {"type": "array"},
                    "rows": {"type": "array"},
                    "config": {"type": "object"}
                }
            }
        }
        
        return schemas.get(visualization_type, {
            "type": visualization_type,
            "schema_version": "1.0"
        })

