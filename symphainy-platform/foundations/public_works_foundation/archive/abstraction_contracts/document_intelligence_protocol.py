#!/usr/bin/env python3
"""
Document Intelligence Protocol

Protocol definition for document intelligence infrastructure abstractions.

Note: Data structures (dataclasses) have been moved to bases/contracts/document_intelligence.py
for access by all realms. Import from bases.contracts.document_intelligence instead.
"""

from typing import Protocol, Dict, Any, List, Optional
from bases.contracts.document_intelligence import (
    DocumentProcessingRequest,
    DocumentProcessingResult,
    DocumentChunk,
    DocumentEntity,
    DocumentSimilarity
)


class DocumentIntelligenceProtocol(Protocol):
    """Protocol for document intelligence infrastructure abstractions."""
    
    async def process_document(self, request: DocumentProcessingRequest) -> DocumentProcessingResult:
        """Process document for intelligence extraction."""
        ...
    
    async def calculate_document_similarity(self, text1: str, text2: str) -> DocumentSimilarity:
        """Calculate similarity between two documents."""
        ...
    
    async def generate_document_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents."""
        ...
    
    async def extract_document_entities(self, text: str) -> List[DocumentEntity]:
        """Extract entities from document text."""
        ...
    
    async def chunk_document(self, text: str, chunk_size: int = None, 
                           chunk_overlap: int = None) -> List[DocumentChunk]:
        """Chunk document text."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        ...




