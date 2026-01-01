#!/usr/bin/env python3
"""
pdfplumber Table Extractor Adapter - Raw Technology Client

Raw pdfplumber client wrapper for PDF table extraction operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw pdfplumber table extraction operations
HOW (Infrastructure Implementation): I use real pdfplumber client with no business logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    class pdfplumber:
        @staticmethod
        def open(file_path): return None

import logging

logger = logging.getLogger(__name__)

class PdfplumberTableExtractor:
    """
    Raw pdfplumber client wrapper for table extraction - no business logic.
    
    This adapter provides direct access to pdfplumber table extraction operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self):
        """Initialize pdfplumber table extractor adapter."""
        self.extractor_name = "pdfplumber_table_extractor"
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"✅ {self.extractor_name} initialized")
    
    # ============================================================================
    # RAW TABLE EXTRACTION OPERATIONS
    # ============================================================================
    
    async def extract_tables_from_file(self, file_path: str) -> Dict[str, Any]:
        """Raw table extraction from file path - no business logic."""
        try:
            tables = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables from this page
                    page_tables = page.extract_tables()
                    
                    if page_tables:
                        for table_num, table in enumerate(page_tables):
                            # Structure the table data
                            structured_table = {
                                "table_id": f"page_{page_num}_table_{table_num}",
                                "page_number": page_num,
                                "table_number": table_num,
                                "rows": table,
                                "row_count": len(table),
                                "column_count": len(table[0]) if table else 0,
                                "extractor": self.extractor_name,
                                "extraction_timestamp": datetime.utcnow().isoformat()
                            }
                            tables.append(structured_table)
            
            return {
                "success": True,
                "tables": tables,
                "table_count": len(tables),
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ pdfplumber table extraction failed from file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tables": [],
                "table_count": 0,
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_tables_from_bytes(self, file_data: bytes) -> Dict[str, Any]:
        """Raw table extraction from bytes - no business logic."""
        try:
            import io
            
            tables = []
            
            # Create file-like object from bytes
            file_like = io.BytesIO(file_data)
            
            with pdfplumber.open(file_like) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables from this page
                    page_tables = page.extract_tables()
                    
                    if page_tables:
                        for table_num, table in enumerate(page_tables):
                            # Structure the table data
                            structured_table = {
                                "table_id": f"page_{page_num}_table_{table_num}",
                                "page_number": page_num,
                                "table_number": table_num,
                                "rows": table,
                                "row_count": len(table),
                                "column_count": len(table[0]) if table else 0,
                                "extractor": self.extractor_name,
                                "extraction_timestamp": datetime.utcnow().isoformat()
                            }
                            tables.append(structured_table)
            
            return {
                "success": True,
                "tables": tables,
                "table_count": len(tables),
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ pdfplumber table extraction failed from bytes: {e}")
            return {
                "success": False,
                "error": str(e),
                "tables": [],
                "table_count": 0,
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_tables_from_page(self, file_path: str, page_number: int) -> Dict[str, Any]:
        """Raw table extraction from specific page - no business logic."""
        try:
            tables = []
            
            with pdfplumber.open(file_path) as pdf:
                # Validate page number
                if page_number < 0 or page_number >= len(pdf.pages):
                    return {
                        "success": False,
                        "error": f"Page number {page_number} out of range (0-{len(pdf.pages)-1})",
                        "tables": [],
                        "extractor": self.extractor_name
                    }
                
                # Extract tables from specific page
                page = pdf.pages[page_number]
                page_tables = page.extract_tables()
                
                if page_tables:
                    for table_num, table in enumerate(page_tables):
                        # Structure the table data
                        structured_table = {
                            "table_id": f"page_{page_number}_table_{table_num}",
                            "page_number": page_number,
                            "table_number": table_num,
                            "rows": table,
                            "row_count": len(table),
                            "column_count": len(table[0]) if table else 0,
                            "extractor": self.extractor_name,
                            "extraction_timestamp": datetime.utcnow().isoformat()
                        }
                        tables.append(structured_table)
            
            return {
                "success": True,
                "tables": tables,
                "table_count": len(tables),
                "page_number": page_number,
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ pdfplumber table extraction failed from page {page_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tables": [],
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    async def extract_tables_from_page_range(self, file_path: str, start_page: int, end_page: int) -> Dict[str, Any]:
        """Raw table extraction from page range - no business logic."""
        try:
            tables = []
            
            with pdfplumber.open(file_path) as pdf:
                # Validate page range
                total_pages = len(pdf.pages)
                if start_page < 0 or end_page >= total_pages or start_page > end_page:
                    return {
                        "success": False,
                        "error": f"Invalid page range {start_page}-{end_page} (total pages: {total_pages})",
                        "tables": [],
                        "extractor": self.extractor_name
                    }
                
                # Extract tables from page range
                for page_num in range(start_page, end_page + 1):
                    page = pdf.pages[page_num]
                    page_tables = page.extract_tables()
                    
                    if page_tables:
                        for table_num, table in enumerate(page_tables):
                            # Structure the table data
                            structured_table = {
                                "table_id": f"page_{page_num}_table_{table_num}",
                                "page_number": page_num,
                                "table_number": table_num,
                                "rows": table,
                                "row_count": len(table),
                                "column_count": len(table[0]) if table else 0,
                                "extractor": self.extractor_name,
                                "extraction_timestamp": datetime.utcnow().isoformat()
                            }
                            tables.append(structured_table)
            
            return {
                "success": True,
                "tables": tables,
                "table_count": len(tables),
                "start_page": start_page,
                "end_page": end_page,
                "pages_processed": end_page - start_page + 1,
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ pdfplumber table extraction failed from page range {start_page}-{end_page}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tables": [],
                "extractor": self.extractor_name,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # RAW TABLE ANALYSIS OPERATIONS
    # ============================================================================
    
    async def analyze_table_structure(self, file_path: str) -> Dict[str, Any]:
        """Raw table structure analysis - no business logic."""
        try:
            table_analysis = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables from this page
                    page_tables = page.extract_tables()
                    
                    if page_tables:
                        for table_num, table in enumerate(page_tables):
                            # Analyze table structure
                            analysis = {
                                "table_id": f"page_{page_num}_table_{table_num}",
                                "page_number": page_num,
                                "table_number": table_num,
                                "row_count": len(table),
                                "column_count": len(table[0]) if table else 0,
                                "has_header": self._detect_header(table),
                                "data_types": self._analyze_data_types(table),
                                "empty_cells": self._count_empty_cells(table),
                                "extractor": self.extractor_name,
                                "analysis_timestamp": datetime.utcnow().isoformat()
                            }
                            table_analysis.append(analysis)
            
            return {
                "success": True,
                "table_analysis": table_analysis,
                "total_tables": len(table_analysis),
                "extractor": self.extractor_name,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ pdfplumber table structure analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_analysis": [],
                "extractor": self.extractor_name,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    def _detect_header(self, table: List[List[str]]) -> bool:
        """Detect if table has a header row - no business logic."""
        if not table or len(table) < 2:
            return False
        
        # Simple heuristic: first row has more text than numbers
        first_row = table[0]
        text_count = sum(1 for cell in first_row if cell and isinstance(cell, str) and cell.strip())
        return text_count > len(first_row) / 2
    
    def _analyze_data_types(self, table: List[List[str]]) -> Dict[str, Any]:
        """Analyze data types in table - no business logic."""
        if not table:
            return {}
        
        # Analyze each column
        column_types = []
        for col_idx in range(len(table[0])):
            column_data = [row[col_idx] for row in table if col_idx < len(row)]
            
            # Count data types
            numeric_count = 0
            text_count = 0
            empty_count = 0
            
            for cell in column_data:
                if not cell or not str(cell).strip():
                    empty_count += 1
                elif str(cell).replace('.', '').replace('-', '').isdigit():
                    numeric_count += 1
                else:
                    text_count += 1
            
            # Determine dominant type
            total = numeric_count + text_count + empty_count
            if total == 0:
                dominant_type = "empty"
            elif numeric_count > text_count:
                dominant_type = "numeric"
            else:
                dominant_type = "text"
            
            column_types.append({
                "column_index": col_idx,
                "dominant_type": dominant_type,
                "numeric_count": numeric_count,
                "text_count": text_count,
                "empty_count": empty_count,
                "total_cells": total
            })
        
        return {
            "column_analysis": column_types,
            "total_columns": len(column_types)
        }
    
    def _count_empty_cells(self, table: List[List[str]]) -> int:
        """Count empty cells in table - no business logic."""
        empty_count = 0
        for row in table:
            for cell in row:
                if not cell or not str(cell).strip():
                    empty_count += 1
        return empty_count
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def test_extraction(self) -> Dict[str, Any]:
        """Test pdfplumber table extraction capability - no business logic."""
        try:
            # Test with a simple PDF creation and table extraction
            import io
            
            # Create a simple test PDF with table in memory
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            
            # Create PDF in memory
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            
            # Create test table
            test_data = [
                ['Name', 'Age', 'City'],
                ['John', '25', 'New York'],
                ['Jane', '30', 'Los Angeles']
            ]
            
            table = Table(test_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            doc.build([table])
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            # Test extraction
            result = await self.extract_tables_from_bytes(pdf_bytes)
            
            return {
                "success": True,
                "message": "pdfplumber table extraction test successful",
                "test_result": result,
                "extractor": self.extractor_name,
                "test_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ pdfplumber table extraction test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "extractor": self.extractor_name,
                "test_timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_extractor_info(self) -> Dict[str, Any]:
        """Get pdfplumber extractor information - no business logic."""
        return {
            "extractor_name": self.extractor_name,
            "extractor_type": "table_extraction",
            "library": "pdfplumber",
            "version": pdfplumber.__version__ if hasattr(pdfplumber, '__version__') else "unknown",
            "capabilities": [
                "table_extraction",
                "table_analysis",
                "page_range_extraction",
                "structure_analysis"
            ],
            "supported_formats": ["pdf"],
            "timestamp": datetime.utcnow().isoformat()
        }




















