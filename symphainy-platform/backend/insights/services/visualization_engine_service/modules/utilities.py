#!/usr/bin/env python3
"""Utilities module for Visualization Engine Service."""

from typing import Dict, Any, Optional, List


class Utilities:
    """Utilities module for Visualization Engine Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    def get_tenant_id(self, user_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Extract tenant ID from user context.
        
        Args:
            user_context: User context dictionary
            
        Returns:
            Tenant ID if available, None otherwise
        """
        if not user_context:
            return None
        
        # Try multiple possible keys
        tenant_id = (
            user_context.get("tenant_id") or
            user_context.get("tenant") or
            user_context.get("organization_id") or
            user_context.get("org_id")
        )
        
        return tenant_id
    
    def validate_visualization_type(self, visualization_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate visualization type.
        
        Args:
            visualization_type: Visualization type string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_types = ["chart", "dashboard", "table"]
        
        if visualization_type not in valid_types:
            return False, f"Invalid visualization type: {visualization_type}. Valid types: {valid_types}"
        
        return True, None
    
    def validate_chart_type(self, chart_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate chart type.
        
        Args:
            chart_type: Chart type string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_chart_types = ["bar", "line", "scatter", "histogram", "pie", "area", "box", "heatmap"]
        
        if chart_type not in valid_chart_types:
            return False, f"Invalid chart type: {chart_type}. Valid types: {valid_chart_types}"
        
        return True, None
    
    def extract_column_names(self, embeddings: List[Dict[str, Any]]) -> List[str]:
        """
        Extract column names from embeddings.
        
        Args:
            embeddings: List of embedding dictionaries
            
        Returns:
            List of column names
        """
        columns = set()
        
        for emb in embeddings:
            column_name = emb.get("column_name") or emb.get("column") or emb.get("field_name")
            if column_name:
                columns.add(column_name)
        
        return sorted(list(columns))

