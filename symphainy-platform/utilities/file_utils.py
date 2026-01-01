#!/usr/bin/env python3
"""
File Utility Functions

Utility functions for filename parsing and content type determination.
Used across the platform for consistent file handling.
"""

import os
from typing import Dict, Any


def parse_filename(filename: str) -> Dict[str, Any]:
    """
    Parse filename into components.
    
    Args:
        filename: Original filename (e.g., "userfile.docx")
        
    Returns:
        {
            "ui_name": "userfile",
            "file_extension": ".docx",
            "file_extension_clean": "docx",
            "original_filename": "userfile.docx"
        }
        
    Examples:
        >>> parse_filename("userfile.docx")
        {"ui_name": "userfile", "file_extension": ".docx", "file_extension_clean": "docx", "original_filename": "userfile.docx"}
        
        >>> parse_filename("data.csv")
        {"ui_name": "data", "file_extension": ".csv", "file_extension_clean": "csv", "original_filename": "data.csv"}
        
        >>> parse_filename("noextension")
        {"ui_name": "noextension", "file_extension": "", "file_extension_clean": "", "original_filename": "noextension"}
    """
    if '.' in filename:
        name, ext = os.path.splitext(filename)
        return {
            "ui_name": name,
            "file_extension": ext,  # Includes dot: ".docx"
            "file_extension_clean": ext.lstrip('.'),  # Without dot: "docx"
            "original_filename": filename
        }
    else:
        return {
            "ui_name": filename,
            "file_extension": "",
            "file_extension_clean": "",
            "original_filename": filename
        }


def determine_content_type(file_extension: str, mime_type: str) -> Dict[str, str]:
    """
    Determine content type and file type category.
    
    Args:
        file_extension: File extension (e.g., ".docx" or "docx")
        mime_type: MIME type (e.g., "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
    Returns:
        {
            "content_type": "unstructured" | "structured" | "hybrid",
            "file_type_category": "document" | "spreadsheet" | "binary" | "image" | "pdf" | "text" | "data_format" | "sop_workflow"
        }
        
    Examples:
        >>> determine_content_type(".docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        {"content_type": "unstructured", "file_type_category": "document"}
        
        >>> determine_content_type(".csv", "text/csv")
        {"content_type": "structured", "file_type_category": "spreadsheet"}
        
        >>> determine_content_type(".dat", "application/octet-stream")
        {"content_type": "structured", "file_type_category": "binary"}
    """
    # Normalize extension (remove dot if present, lowercase)
    ext_lower = file_extension.lower().lstrip('.')
    
    # Structured data - Spreadsheets
    spreadsheet_exts = ['csv', 'xlsx', 'xls', 'parquet']
    if ext_lower in spreadsheet_exts:
        return {
            "content_type": "structured",
            "file_type_category": "spreadsheet"
        }
    
    # Structured data - Data formats
    data_format_exts = ['json', 'xml', 'yaml']
    if ext_lower in data_format_exts:
        return {
            "content_type": "structured",
            "file_type_category": "data_format"
        }
    
    # Structured data - Binary files (with copybooks)
    binary_exts = ['dat', 'bin', 'cpy']
    if ext_lower in binary_exts:
        return {
            "content_type": "structured",
            "file_type_category": "binary"
        }
    
    # Unstructured documents
    doc_exts = ['doc', 'docx', 'txt', 'md', 'rtf']
    if ext_lower in doc_exts:
        return {
            "content_type": "unstructured",
            "file_type_category": "document"
        }
    
    # PDFs
    if ext_lower == 'pdf':
        return {
            "content_type": "unstructured",
            "file_type_category": "pdf"
        }
    
    # Images
    image_exts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']
    if ext_lower in image_exts:
        return {
            "content_type": "unstructured",
            "file_type_category": "image"
        }
    
    # BPMN (workflow)
    if ext_lower == 'bpmn':
        return {
            "content_type": "unstructured",
            "file_type_category": "sop_workflow"
        }
    
    # Default - treat as unstructured text
    return {
        "content_type": "unstructured",
        "file_type_category": "text"
    }






