#!/usr/bin/env python3
"""Utilities module for Data Analyzer Service."""

from typing import Dict, Any, Optional, List


class Utilities:
    """Utilities module for Data Analyzer Service."""
    
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
    
    def validate_analysis_types(self, analysis_types: List[str]) -> tuple[bool, Optional[str]]:
        """
        Validate analysis types.
        
        Args:
            analysis_types: List of analysis type strings
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_types = ["statistics", "correlations", "distributions", "missing_values"]
        
        if not analysis_types:
            return False, "analysis_types cannot be empty"
        
        invalid_types = [t for t in analysis_types if t not in valid_types]
        if invalid_types:
            return False, f"Invalid analysis types: {invalid_types}. Valid types: {valid_types}"
        
        return True, None
    
    def normalize_data_type(self, data_type: str) -> str:
        """
        Normalize data type string to standard format.
        
        Args:
            data_type: Data type string from embeddings
            
        Returns:
            Normalized data type string
        """
        # Normalize to lowercase
        data_type_lower = data_type.lower() if data_type else "unknown"
        
        # Map variations to standard types
        type_mapping = {
            "int": ["int", "integer", "int64", "int32", "int16", "int8"],
            "float": ["float", "float64", "float32", "double", "decimal", "numeric"],
            "number": ["number", "num", "numeric"],
            "string": ["string", "str", "text", "varchar", "char"],
            "object": ["object", "dict", "json"],
            "bool": ["bool", "boolean"],
            "date": ["date", "datetime", "timestamp", "time"]
        }
        
        for standard_type, variations in type_mapping.items():
            if data_type_lower in variations:
                return standard_type
        
        return data_type_lower if data_type_lower else "unknown"


