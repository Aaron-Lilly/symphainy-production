#!/usr/bin/env python3
"""Utilities module for Semantic Enrichment Service."""

from typing import Dict, Any, Optional, List
import pandas as pd
import json


class Utilities:
    """Utilities module for Semantic Enrichment Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    def _convert_user_context(self, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert UserContext object to dict if needed.
        
        Args:
            user_context: UserContext object or dict
            
        Returns:
            Dict with user context information
        """
        if user_context is None:
            return {}
        
        # If it's already a dict, return as-is
        if isinstance(user_context, dict):
            return user_context
        
        # If it's a UserContext object, convert to dict
        if hasattr(user_context, 'user_id'):
            return {
                "user_id": getattr(user_context, 'user_id', None),
                "tenant_id": getattr(user_context, 'tenant_id', None),
                "email": getattr(user_context, 'email', None),
                "full_name": getattr(user_context, 'full_name', None),
                "session_id": getattr(user_context, 'session_id', None),
                "permissions": getattr(user_context, 'permissions', []),
                "roles": getattr(user_context, 'roles', [])
            }
        
        return {}
    
    def parse_parsed_file_to_dataframe(self, parsed_file: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """
        Parse parsed file dict to pandas DataFrame.
        
        Args:
            parsed_file: Parsed file dict from Content Steward
            
        Returns:
            pandas DataFrame or None if parsing fails
        """
        try:
            # Try to extract data from parsed file
            # Format depends on file type (CSV, JSON, Excel, etc.)
            
            if isinstance(parsed_file, dict):
                # Check for common parsed file formats
                if "data" in parsed_file:
                    data = parsed_file["data"]
                    if isinstance(data, list):
                        # List of dicts - convert to DataFrame
                        return pd.DataFrame(data)
                    elif isinstance(data, str):
                        # JSON string - parse and convert
                        data_dict = json.loads(data)
                        if isinstance(data_dict, list):
                            return pd.DataFrame(data_dict)
                        elif isinstance(data_dict, dict):
                            # Single dict - try to find data array
                            if "rows" in data_dict:
                                return pd.DataFrame(data_dict["rows"])
                            elif "records" in data_dict:
                                return pd.DataFrame(data_dict["records"])
                
                # Try direct DataFrame conversion
                if "rows" in parsed_file:
                    return pd.DataFrame(parsed_file["rows"])
                elif "records" in parsed_file:
                    return pd.DataFrame(parsed_file["records"])
            
            # If all else fails, try to convert dict directly
            if isinstance(parsed_file, dict):
                return pd.DataFrame([parsed_file])
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to parse parsed file to DataFrame: {e}")
            return None
    
    def filter_dataframe(self, df: pd.DataFrame, filters: Optional[Dict[str, Any]]) -> pd.DataFrame:
        """
        Filter DataFrame based on filters.
        
        Args:
            df: pandas DataFrame
            filters: Optional filters dict (e.g., {"columns": ["col1", "col2"]})
            
        Returns:
            Filtered DataFrame
        """
        if not filters or not isinstance(df, pd.DataFrame):
            return df
        
        try:
            # Filter by columns if specified
            if "columns" in filters:
                columns = filters["columns"]
                if isinstance(columns, list):
                    # Only keep specified columns
                    available_columns = [col for col in columns if col in df.columns]
                    if available_columns:
                        df = df[available_columns]
            
            # Filter by rows if specified (e.g., row indices)
            if "rows" in filters:
                rows = filters["rows"]
                if isinstance(rows, list):
                    # Filter by row indices
                    df = df.iloc[rows]
            
            return df
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to apply filters: {e}")
            return df

