"""
Serialization Utility

Platform-specific serialization utility for Smart City services.
Handles common serialization patterns used across the platform.

WHAT (Utility Role): I provide standardized serialization for platform operations
HOW (Utility Implementation): I serialize dataclasses, format responses, and handle data conversion
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict, is_dataclass
from enum import Enum


class SerializationUtility:
    """
    Platform-specific serialization utility for Smart City services.
    
    Provides common serialization patterns used across the platform including:
    - Dataclass to/from dictionary conversion
    - JSON serialization for MCP responses
    - Error response formatting
    - UserContext serialization
    - Timestamp serialization
    - Enum value serialization
    """
    
    def __init__(self, service_name: str):
        """Initialize serialization utility."""
        self.service_name = service_name
        self.logger = logging.getLogger(f"SerializationUtility-{service_name}")
        
        self.logger.info(f"Serialization utility initialized for {service_name}")
    
    # ============================================================================
    # DATACLASS SERIALIZATION
    # ============================================================================
    
    def dataclass_to_dict(self, obj: Any) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        if obj is None:
            return {}
        
        if is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return obj
        else:
            self.logger.warning(f"Object is not a dataclass and has no to_dict method: {type(obj)}")
            return {}
    
    def dict_to_dataclass(self, data: Dict[str, Any], dataclass_class: type) -> Any:
        """Convert dictionary to dataclass instance."""
        if not data:
            return None
        
        try:
            return dataclass_class(**data)
        except Exception as e:
            self.logger.error(f"Failed to convert dict to dataclass {dataclass_class.__name__}: {e}")
            return None
    
    def serialize_dataclass_list(self, obj_list: List[Any]) -> List[Dict[str, Any]]:
        """Serialize a list of dataclasses to dictionaries."""
        if not obj_list:
            return []
        
        return [self.dataclass_to_dict(obj) for obj in obj_list]
    
    # ============================================================================
    # JSON SERIALIZATION
    # ============================================================================
    
    def to_json(self, obj: Any, indent: int = None) -> str:
        """Convert object to JSON string."""
        try:
            if is_dataclass(obj):
                obj = asdict(obj)
            elif hasattr(obj, 'to_dict'):
                obj = obj.to_dict()
            
            return json.dumps(obj, indent=indent, default=self._json_serializer)
        except Exception as e:
            self.logger.error(f"JSON serialization failed: {e}")
            return json.dumps({"error": "Serialization failed", "details": str(e)})
    
    def from_json(self, json_str: str) -> Any:
        """Convert JSON string to Python object."""
        try:
            return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"JSON deserialization failed: {e}")
            return None
    
    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for special types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return str(obj)
    
    # ============================================================================
    # RESPONSE FORMATTING
    # ============================================================================
    
    def format_success_response(self, data: Any = None, message: str = None) -> Dict[str, Any]:
        """Format a standard success response."""
        response = {
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = self.dataclass_to_dict(data) if data is not None else data
        
        if message:
            response["message"] = message
        
        return response
    
    def format_error_response(self, error: str, error_code: str = None, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format a standard error response."""
        response = {
            "success": False,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if error_code:
            response["error_code"] = error_code
        
        if details:
            response["details"] = details
        
        return response
    
    def format_mcp_response(self, result: Any, is_success: bool = True) -> str:
        """Format response for MCP tools."""
        if is_success:
            response = self.format_success_response(result)
        else:
            response = self.format_error_response(str(result))
        
        return self.to_json(response)
    
    # ============================================================================
    # USER CONTEXT SERIALIZATION
    # ============================================================================
    
    def serialize_user_context(self, user_context: Any) -> Dict[str, Any]:
        """Serialize UserContext for cross-service communication."""
        if user_context is None:
            return {}
        
        if hasattr(user_context, 'to_dict'):
            return user_context.to_dict()
        elif isinstance(user_context, dict):
            return user_context
        else:
            self.logger.warning(f"UserContext is not serializable: {type(user_context)}")
            return {}
    
    def deserialize_user_context(self, data: Dict[str, Any], user_context_class: type) -> Any:
        """Deserialize UserContext from dictionary."""
        if not data:
            return None
        
        try:
            return user_context_class(**data)
        except Exception as e:
            self.logger.error(f"Failed to deserialize UserContext: {e}")
            return None
    
    # ============================================================================
    # TIMESTAMP SERIALIZATION
    # ============================================================================
    
    def serialize_timestamp(self, timestamp: datetime) -> str:
        """Serialize datetime to ISO format string."""
        if timestamp is None:
            return None
        
        return timestamp.isoformat()
    
    def deserialize_timestamp(self, timestamp_str: str) -> datetime:
        """Deserialize ISO format string to datetime."""
        if not timestamp_str:
            return None
        
        try:
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception as e:
            self.logger.error(f"Failed to deserialize timestamp '{timestamp_str}': {e}")
            return None
    
    # ============================================================================
    # ENUM SERIALIZATION
    # ============================================================================
    
    def serialize_enum(self, enum_value: Enum) -> str:
        """Serialize enum to its string value."""
        if enum_value is None:
            return None
        
        return enum_value.value if hasattr(enum_value, 'value') else str(enum_value)
    
    def deserialize_enum(self, value: str, enum_class: type) -> Enum:
        """Deserialize string value to enum."""
        if not value:
            return None
        
        try:
            # Try to match by value
            for enum_item in enum_class:
                if enum_item.value == value:
                    return enum_item
            return None
        except Exception as e:
            self.logger.error(f"Failed to deserialize enum '{value}' to {enum_class.__name__}: {e}")
            return None
    
    # ============================================================================
    # BULK SERIALIZATION
    # ============================================================================
    
    def serialize_bulk_data(self, data_list: List[Any], include_metadata: bool = True) -> Dict[str, Any]:
        """Serialize a list of data objects with metadata."""
        serialized_items = []
        
        for item in data_list:
            serialized_items.append(self.dataclass_to_dict(item))
        
        result = {
            "items": serialized_items,
            "count": len(serialized_items)
        }
        
        if include_metadata:
            result.update({
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name
            })
        
        return result
    
    def serialize_paginated_data(self, 
                               data_list: List[Any], 
                               page: int, 
                               page_size: int, 
                               total_count: int) -> Dict[str, Any]:
        """Serialize paginated data with pagination metadata."""
        serialized_items = [self.dataclass_to_dict(item) for item in data_list]
        
        return {
            "items": serialized_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size,
                "has_next": page * page_size < total_count,
                "has_previous": page > 1
            },
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name
        }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def log_serialization_result(self, operation: str, success: bool, details: str = None):
        """Log serialization operation result."""
        if success:
            self.logger.debug(f"Serialization successful for {operation}")
        else:
            self.logger.error(f"Serialization failed for {operation}: {details}")
    
    def get_serialization_summary(self) -> Dict[str, Any]:
        """Get serialization utility status."""
        return {
            "service_name": self.service_name,
            "utility_type": "serialization",
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat()
        }

