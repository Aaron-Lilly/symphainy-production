#!/usr/bin/env python3
"""
Response Transformer Micro-Module

Transforms response data between different formats.

WHAT (Micro-Module): I transform response data between formats
HOW (Implementation): I convert data between JSON, XML, form data, etc.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from config.environment_loader import EnvironmentLoader
from experience.interfaces.frontend_integration_interface import DataFormat


class ResponseTransformerModule:
    """
    Response Transformer Micro-Module
    
    Transforms response data between different formats (JSON, XML, form data, etc.).
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None, environment: Optional[EnvironmentLoader] = None):
        """Initialize Response Transformer Module."""
        self.logger = logger or logging.getLogger(__name__)
        self.environment = environment
        self.is_initialized = False
        
        self.logger.info("🔄 Response Transformer Module initialized")
    
    async def initialize(self):
        """Initialize the Response Transformer Module."""
        self.logger.info("🚀 Initializing Response Transformer Module...")
        self.is_initialized = True
        self.logger.info("✅ Response Transformer Module initialized successfully")
    
    async def transform_response(
        self, 
        data: Dict[str, Any], 
        source_format: DataFormat, 
        target_format: DataFormat
    ) -> Dict[str, Any]:
        """
        Transform response data between different formats.
        
        Args:
            data: The data to transform
            source_format: The source data format
            target_format: The target data format
            
        Returns:
            Transformed data in the target format
        """
        self.logger.info(f"Transforming response data: {source_format.value} -> {target_format.value}")
        
        try:
            if source_format == target_format:
                return data
            
            # Convert to intermediate format (dict)
            intermediate_data = await self._to_dict(data, source_format)
            
            # Convert from intermediate format to target format
            result = await self._from_dict(intermediate_data, target_format)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to transform response data: {str(e)}")
            return data  # Return original data if transformation fails
    
    async def _to_dict(self, data: Any, source_format: DataFormat) -> Dict[str, Any]:
        """Convert data to dictionary format."""
        if source_format == DataFormat.JSON:
            if isinstance(data, str):
                return json.loads(data)
            return data
        elif source_format == DataFormat.XML:
            # For MVP, assume XML is already parsed to dict
            return data
        elif source_format == DataFormat.FORM_DATA:
            # Convert form data to dict
            if isinstance(data, str):
                form_dict = {}
                for pair in data.split('&'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        form_dict[key] = value
                return form_dict
            return data
        elif source_format == DataFormat.MULTIPART:
            # For MVP, assume multipart is already parsed
            return data
        elif source_format == DataFormat.BINARY:
            # Convert binary to base64 string in dict
            return {"data": data, "format": "binary"}
        else:
            return data
    
    async def _from_dict(self, data: Dict[str, Any], target_format: DataFormat) -> Any:
        """Convert data from dictionary format."""
        if target_format == DataFormat.JSON:
            return data
        elif target_format == DataFormat.XML:
            # For MVP, return as dict (would convert to XML in real implementation)
            return data
        elif target_format == DataFormat.FORM_DATA:
            # Convert dict to form data string
            form_pairs = []
            for key, value in data.items():
                form_pairs.append(f"{key}={value}")
            return "&".join(form_pairs)
        elif target_format == DataFormat.MULTIPART:
            # For MVP, return as dict (would create multipart in real implementation)
            return data
        elif target_format == DataFormat.BINARY:
            # Extract binary data from dict
            return data.get("data", data)
        else:
            return data
    
    async def standardize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize response format for frontend consumption."""
        self.logger.info("Standardizing response format")
        
        try:
            # Ensure response has standard fields
            standardized = {
                "success": response.get("success", True),
                "data": response.get("data", response),
                "message": response.get("message", "Request completed successfully"),
                "timestamp": response.get("timestamp", datetime.utcnow().isoformat()),
                "status_code": response.get("status_code", 200)
            }
            
            # Add error information if present
            if "error" in response:
                standardized["error"] = response["error"]
            
            # Add metadata if present
            if "metadata" in response:
                standardized["metadata"] = response["metadata"]
            
            return standardized
            
        except Exception as e:
            self.logger.error(f"Failed to standardize response: {str(e)}")
            return response
    
    async def validate_response_format(self, data: Any, expected_format: DataFormat) -> bool:
        """Validate that response data matches the expected format."""
        try:
            if expected_format == DataFormat.JSON:
                if isinstance(data, dict):
                    return True
                if isinstance(data, str):
                    json.loads(data)
                    return True
                return False
            elif expected_format == DataFormat.FORM_DATA:
                if isinstance(data, str) and '=' in data:
                    return True
                if isinstance(data, dict):
                    return True
                return False
            elif expected_format == DataFormat.BINARY:
                return isinstance(data, (bytes, str))
            else:
                return True
        except Exception:
            return False
    
    async def get_supported_formats(self) -> list[DataFormat]:
        """Get list of supported data formats."""
        return [
            DataFormat.JSON,
            DataFormat.XML,
            DataFormat.FORM_DATA,
            DataFormat.MULTIPART,
            DataFormat.BINARY
        ]
