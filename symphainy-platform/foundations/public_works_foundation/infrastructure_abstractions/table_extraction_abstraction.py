#!/usr/bin/env python3
"""
Table Extraction Abstraction - Lightweight Infrastructure Coordination

Lightweight coordination of table extraction adapters.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I coordinate table extraction adapters
HOW (Infrastructure Implementation): I provide simple table extraction coordination

================================================================================
ARCHIVED: This abstraction is archived. File parsing now uses file type-specific
abstractions (pdf_processing, excel_processing, etc.) that implement FileParsingProtocol.

Unique Capabilities (not provided by new abstractions):
- Page-level table extraction: extract_tables(page_number=5)
- Page range table extraction: extract_tables(start_page=10, end_page=20)
- Table structure analysis: analyze_table_structure()
- Table statistics: get_table_statistics() (counts, averages, per-page stats)

If page-level table extraction is needed in the future, we can either:
1. Add page support to FileParsingRequest.options
2. Create new page-specific abstractions
3. Fix and use this archived abstraction

This abstraction is kept for reference only.
================================================================================
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.document_table_extraction_protocol import DocumentTableExtractionProtocol

logger = logging.getLogger(__name__)

# ============================================================================
# ARCHIVED: Legacy abstraction - kept for reference only
# ============================================================================
# File parsing now uses file type-specific abstractions (pdf_processing, etc.)
# that implement FileParsingProtocol. This abstraction is not instantiated
# or used anywhere in the codebase.
# ============================================================================
class TableExtractionAbstraction(DocumentTableExtractionProtocol):
    """
    Lightweight table extraction abstraction.
    
    Simple coordination of table extraction adapters with minimal business logic.
    """
    
    def __init__(self, table_extractor, di_container=None):
        """Initialize table extraction abstraction."""
        self.table_extractor = table_extractor
        self.di_container = di_container
        self.service_name = "table_extraction_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Table Extraction Abstraction initialized")
    
    async def extract_tables(self, 
                             file_path: str = None,
                             page_number: int = None,
                             start_page: int = None,
                             end_page: int = None) -> Dict[str, Any]:
        """Extract tables from document."""
        try:
            if page_number is not None:
                result = await self.table_extractor.extract_tables_from_page(file_path, page_number)
            elif start_page is not None and end_page is not None:
                result = await self.table_extractor.extract_tables_from_page_range(file_path, start_page, end_page)
            elif file_data is not None:
                result = await self.table_extractor.extract_tables_from_bytes(file_data)
            else:
                result = await self.table_extractor.extract_tables_from_file(file_path)
            
            return result
                
        except Exception as e:
            self.logger.error(f"❌ Table extraction failed: {e}")
            raise  # Re-raise for service layer to handle

        """Analyze table structure and content."""
        try:
            if file_data is not None:
                # For bytes, we need to create a temp file
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    temp_file.write(file_data)
                    temp_file_path = temp_file.name
                
                try:
                    result = await self.table_extractor.analyze_table_structure(temp_file_path)
                    return result
                finally:
                    os.unlink(temp_file_path)
            else:
                result = await self.table_extractor.analyze_table_structure(file_path)
                return result
                
        except Exception as e:
            self.logger.error(f"❌ Table structure analysis failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_table_statistics(self, file_path: str = None, file_data: bytes = None) -> Dict[str, Any]:
        """Get table statistics from document."""
        try:
            # Extract tables first
            table_result = await self.extract_tables(file_path=file_path, file_data=file_data)
            
            if not table_result.get("success"):
                return table_result
            
            tables = table_result.get("tables", [])
            
            # Calculate statistics
            total_tables = len(tables)
            total_rows = sum(len(table.get("rows", [])) for table in tables)
            total_columns = sum(table.get("column_count", 0) for table in tables)
            
            # Group by page
            pages_with_tables = {}
            for table in tables:
                page_num = table.get("page_number", 0)
                if page_num not in pages_with_tables:
                    pages_with_tables[page_num] = 0
                pages_with_tables[page_num] += 1
            
            result = {
                "success": True,
                "total_tables": total_tables,
                "total_rows": total_rows,
                "total_columns": total_columns,
                "pages_with_tables": len(pages_with_tables),
                "tables_per_page": pages_with_tables,
                "average_rows_per_table": total_rows / total_tables if total_tables > 0 else 0,
                "average_columns_per_table": total_columns / total_tables if total_tables > 0 else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Table statistics failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_table_extraction_capabilities(self) -> Dict[str, Any]:
        """Get table extraction capabilities."""
        try:
            result = await self.table_extractor.get_extractor_info()
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to get extraction capabilities: {e}")
            raise  # Re-raise for service layer to handle
