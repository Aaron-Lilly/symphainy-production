#!/usr/bin/env python3
"""
JSON Processing Adapter - Raw Technology Client

Raw json client wrapper for JSON document operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw JSON processing operations
HOW (Infrastructure Implementation): I use the json library with no business logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class JsonProcessingAdapter:
    """
    Raw json client wrapper - no business logic.
    
    This adapter provides direct access to json operations for
    JSON document processing.
    """
    
    def __init__(self):
        """Initialize JSON Processing Adapter."""
        logger.info("✅ JSON Processing Adapter initialized")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse JSON file from bytes.
        
        Args:
            file_data: JSON file content as bytes
            filename: Original filename (for logging)
            
        Returns:
            Dict[str, Any]: A dictionary containing parsed data and metadata.
        """
        try:
            # Decode bytes to string
            json_content = file_data.decode('utf-8')
            
            # Parse JSON
            parsed_json = json.loads(json_content)
            
            # If it's a list, treat as records
            if isinstance(parsed_json, list):
                records = parsed_json
                text_content = json.dumps(parsed_json, indent=2)
            elif isinstance(parsed_json, dict):
                records = [parsed_json]
                text_content = json.dumps(parsed_json, indent=2)
            else:
                records = [{"value": parsed_json}]
                text_content = str(parsed_json)
            
            return {
                "success": True,
                "text": text_content,
                "data": parsed_json,
                "records": records,
                "metadata": {
                    "file_type": "json",
                    "is_structured": True,
                    "record_count": len(records) if isinstance(records, list) else 1,
                    "filename": filename
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON file parsing failed (invalid JSON): {e}")
            return {
                "success": False,
                "error": f"Invalid JSON: {str(e)}",
                "text": "",
                "data": None,
                "records": [],
                "metadata": {},
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ JSON file parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "data": None,
                "records": [],
                "metadata": {},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_text(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text content from JSON file.
        
        Args:
            file_data: JSON file content as bytes
            filename: Original filename
            
        Returns:
            Dict[str, Any]: A dictionary containing extracted text.
        """
        result = await self.parse_file(file_data, filename)
        if result.get("success"):
            return {
                "success": True,
                "text": result.get("text", ""),
                "timestamp": datetime.utcnow().isoformat()
            }
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the adapter."""
        return {
            "adapter_name": "JsonProcessingAdapter",
            "status": "ready",
            "library_version": json.__version__ if hasattr(json, '__version__') else "builtin",
            "timestamp": datetime.utcnow().isoformat()
        }

