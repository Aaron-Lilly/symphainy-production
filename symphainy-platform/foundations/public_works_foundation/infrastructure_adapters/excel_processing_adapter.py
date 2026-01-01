#!/usr/bin/env python3
"""
Excel Processing Adapter - Raw Technology Client

Raw pandas/openpyxl client wrapper for Excel document operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw Excel processing operations
HOW (Infrastructure Implementation): I use the pandas/openpyxl library with no business logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import asyncio
import io

try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)

class ExcelProcessingAdapter:
    """
    Raw pandas/openpyxl client wrapper - no business logic.
    
    This adapter provides direct access to pandas/openpyxl operations for
    Excel document processing (XLSX, XLS).
    """
    
    def __init__(self):
        """Initialize Excel Processing Adapter."""
        self.pandas_available = pd is not None
        if not self.pandas_available:
            logger.warning("⚠️ 'pandas' library not found. Excel operations will be limited.")
        logger.info("✅ Excel Processing Adapter initialized")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse Excel file from bytes.
        
        Args:
            file_data: Excel file content as bytes
            filename: Original filename (for logging)
            
        Returns:
            Dict[str, Any]: A dictionary containing parsed data, tables, and metadata.
        """
        if not self.pandas_available:
            return {
                "success": False,
                "error": "pandas library not available",
                "text": "",
                "tables": [],
                "metadata": {},
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            excel_file = io.BytesIO(file_data)
            
            # CRITICAL: Wrap blocking pd.read_excel() call with timeout to prevent SSH session crashes
            # Excel parsing can be slow for large files, so we need timeout protection
            try:
                excel_data = await asyncio.wait_for(
                    asyncio.to_thread(pd.read_excel, excel_file, sheet_name=None),
                    timeout=30.0  # 30 second timeout for Excel parsing
                )
            except asyncio.TimeoutError:
                error_msg = f"Excel parsing timed out after 30 seconds. File size: {len(file_data)} bytes"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "text": "",
                    "tables": [],
                    "metadata": {},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            tables = []
            text_content = ""
            
            for sheet_name, df in excel_data.items():
                # Convert DataFrame to list of dicts
                table_data = df.to_dict('records')
                tables.append({
                    "sheet_name": sheet_name,
                    "data": table_data,
                    "columns": list(df.columns),
                    "row_count": len(df)
                })
                
                # Add sheet name and summary to text
                text_content += f"Sheet: {sheet_name}\n"
                text_content += f"Rows: {len(df)}, Columns: {len(df.columns)}\n"
                
                # Add column headers
                if len(df.columns) > 0:
                    text_content += "\t".join(str(col) for col in df.columns) + "\n"
                    text_content += "-" * (len("\t".join(str(col) for col in df.columns))) + "\n"
                
                # Add actual cell values (data rows)
                for _, row in df.iterrows():
                    text_content += "\t".join(str(val) if pd.notna(val) else "" for val in row.values) + "\n"
                
                text_content += "\n"
            
            return {
                "success": True,
                "text": text_content.strip(),
                "tables": tables,
                "data": tables,  # For format composer
                "records": [row for table in tables for row in table.get("data", [])],  # Flattened records
                "metadata": {
                    "file_type": "excel",
                    "sheet_count": len(excel_data),
                    "table_count": len(tables),
                    "filename": filename
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Excel file parsing failed: {e}")
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
        Extract text content from Excel file.
        
        Args:
            file_data: Excel file content as bytes
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
    
    async def extract_tables(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract tables from Excel file.
        
        Args:
            file_data: Excel file content as bytes
            filename: Original filename
            
        Returns:
            Dict[str, Any]: A dictionary containing extracted tables.
        """
        result = await self.parse_file(file_data, filename)
        if result.get("success"):
            return {
                "success": True,
                "tables": result.get("tables", []),
                "table_count": len(result.get("tables", [])),
                "timestamp": datetime.utcnow().isoformat()
            }
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of the adapter."""
        return {
            "adapter_name": "ExcelProcessingAdapter",
            "status": "ready" if self.pandas_available else "limited",
            "pandas_available": self.pandas_available,
            "library_version": pd.__version__ if self.pandas_available else "not_available",
            "timestamp": datetime.utcnow().isoformat()
        }

