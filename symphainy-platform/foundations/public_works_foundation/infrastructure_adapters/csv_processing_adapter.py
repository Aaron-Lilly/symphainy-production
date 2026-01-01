#!/usr/bin/env python3
"""
CSV Processing Adapter - Raw Technology Client

Raw pandas/csv client wrapper for CSV document operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw CSV processing operations
HOW (Infrastructure Implementation): I use the pandas/csv library with no business logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import io
import csv

try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)

class CsvProcessingAdapter:
    """
    Raw pandas/csv client wrapper - no business logic.
    
    This adapter provides direct access to pandas/csv operations for
    CSV document processing.
    """
    
    def __init__(self):
        """Initialize CSV Processing Adapter."""
        self.pandas_available = pd is not None
        if not self.pandas_available:
            logger.warning("⚠️ 'pandas' library not found. CSV operations will use csv module.")
        logger.info("✅ CSV Processing Adapter initialized")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse CSV file from bytes.
        
        Args:
            file_data: CSV file content as bytes
            filename: Original filename (for logging)
            
        Returns:
            Dict[str, Any]: A dictionary containing parsed data, tables, and metadata.
        """
        try:
            # Decode bytes to string
            try:
                csv_content = file_data.decode('utf-8', errors='ignore')
            except Exception:
                csv_content = file_data.decode('latin-1', errors='ignore')
            
            csv_file = io.StringIO(csv_content)
            
            # Try pandas first (better handling)
            if self.pandas_available:
                try:
                    df = pd.read_csv(csv_file)
                    records = df.to_dict('records')
                    text_content = df.to_string()
                    
                    return {
                        "success": True,
                        "text": text_content,
                        "tables": [{
                            "data": records,
                            "columns": list(df.columns),
                            "row_count": len(df)
                        }],
                        "data": records,
                        "records": records,
                        "metadata": {
                            "file_type": "csv",
                            "row_count": len(df),
                            "column_count": len(df.columns),
                            "columns": list(df.columns),
                            "filename": filename
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    logger.warning(f"⚠️ Pandas CSV parsing failed, falling back to csv module: {e}")
                    csv_file.seek(0)
            
            # Fallback to csv module
            reader = csv.DictReader(csv_file)
            records = list(reader)
            text_content = "\n".join([str(record) for record in records])
            
            columns = list(records[0].keys()) if records else []
            
            return {
                "success": True,
                "text": text_content,
                "tables": [{
                    "data": records,
                    "columns": columns,
                    "row_count": len(records)
                }],
                "data": records,
                "records": records,
                "metadata": {
                    "file_type": "csv",
                    "row_count": len(records),
                    "column_count": len(columns),
                    "columns": columns,
                    "filename": filename
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ CSV file parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "tables": [],
                "metadata": {},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_text(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text content from CSV file.
        
        Args:
            file_data: CSV file content as bytes
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
            "adapter_name": "CsvProcessingAdapter",
            "status": "ready",
            "pandas_available": self.pandas_available,
            "library_version": pd.__version__ if self.pandas_available else "csv_module",
            "timestamp": datetime.utcnow().isoformat()
        }

