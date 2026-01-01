#!/usr/bin/env python3
"""
Document Intelligence Contract Data Structures

Data structures (dataclasses) used for document intelligence abstraction contracts.
These define the shape of data passed to/from document intelligence abstractions.

Moved from foundations/public_works_foundation/abstraction_contracts/document_intelligence_protocol.py
to make them accessible to all realms without architectural violations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class DocumentProcessingRequest:
    """Document processing request definition."""
    file_data: bytes
    filename: str
    options: Optional[Dict[str, Any]] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None


@dataclass
class DocumentProcessingResult:
    """Document processing result definition."""
    result_id: str
    filename: str
    success: bool
    file_hash: Optional[str] = None
    text_length: Optional[int] = None
    page_count: Optional[int] = None
    chunks: Optional[List['DocumentChunk']] = None
    entities: Optional[List['DocumentEntity']] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class DocumentChunk:
    """Document chunk definition."""
    chunk_id: str
    text: str
    start_position: int
    end_position: int
    length: int


@dataclass
class DocumentEntity:
    """Document entity definition."""
    entity_id: str
    text: str
    label: str
    start_position: int
    end_position: int
    confidence: float


@dataclass
class DocumentSimilarity:
    """Document similarity definition."""
    similarity_id: str
    similarity_score: float
    is_similar: bool
    threshold: float
    error: Optional[str] = None
    timestamp: Optional[datetime] = None

