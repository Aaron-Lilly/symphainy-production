#!/usr/bin/env python3
"""
Document Processing Infrastructure Adapter

Raw document processing client wrapper for APG document intelligence.
Thin wrapper around document processing libraries with no business logic.
"""

from typing import Dict, Any, List, Optional
import logging
import hashlib
import json
from datetime import datetime

try:
    import spacy
    from sentence_transformers import SentenceTransformer
except ImportError:
    spacy = None
    SentenceTransformer = None


class DocumentProcessingAdapter:
    """Raw document processing adapter for APG document intelligence."""
    
    def __init__(self, spacy_model: str = "en_core_web_sm", 
                 sentence_transformer_model: str = "all-MiniLM-L6-v2", **kwargs):
        """
        Initialize document processing adapter.
        
        Args:
            spacy_model: SpaCy model name
            sentence_transformer_model: Sentence transformer model name
        """
        self.spacy_model_name = spacy_model
        self.sentence_transformer_model_name = sentence_transformer_model
        self.logger = logging.getLogger("DocumentProcessingAdapter")
        
        # Processing models
        self.spacy_model = None
        self.sentence_transformer = None
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize document processing models."""
        try:
            # Initialize SpaCy model
            if spacy is not None:
                self.spacy_model = spacy.load(self.spacy_model_name)
                self.logger.info(f"✅ SpaCy model loaded: {self.spacy_model_name}")
            else:
                self.logger.warning("SpaCy not available")
            
            # Initialize sentence transformer
            if SentenceTransformer is not None:
                self.sentence_transformer = SentenceTransformer(self.sentence_transformer_model_name)
                self.logger.info(f"✅ Sentence transformer loaded: {self.sentence_transformer_model_name}")
            else:
                self.logger.warning("SentenceTransformer not available")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize document processing models: {e}")
    
    async def parse_document(self, file_data: bytes, filename: str, 
                           options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Parse document content.
        
        Args:
            file_data: Document file data
            filename: Document filename
            options: Parsing options
            
        Returns:
            Dict: Parsed document content
        """
        try:
            # Calculate file hash
            file_hash = hashlib.md5(file_data).hexdigest()
            
            # Basic document parsing (placeholder - would use actual document parsing)
            parsed_content = {
                "file_hash": file_hash,
                "filename": filename,
                "file_hash": file_hash,
                "text": "Sample document content...",  # Would be parsed from file_data
                "page_count": 50,
                "tables": [],
                "metadata": {
                    "filename": filename,
                    "file_size": len(file_data),
                    "parsed_at": datetime.now().isoformat()
                }
            }
            
            self.logger.info(f"✅ Document parsed: {filename}")
            return parsed_content
            
        except Exception as e:
            self.logger.error(f"Failed to parse document {filename}: {e}")
            return {"error": str(e)}
    
    async def chunk_text(self, text: str, chunk_size: int = 1000, 
                        chunk_overlap: int = 200) -> List[Dict[str, Any]]:
        """
        Chunk text into smaller pieces.
        
        Args:
            text: Input text
            chunk_size: Chunk size
            chunk_overlap: Chunk overlap
            
        Returns:
            List[Dict]: Text chunks
        """
        try:
            chunks = []
            start = 0
            
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk_text = text[start:end]
                
                chunks.append({
                    "text": chunk_text,
                    "start": start,
                    "end": end,
                    "length": len(chunk_text)
                })
                
                start = end - chunk_overlap
                if start >= len(text):
                    break
            
            self.logger.info(f"✅ Text chunked into {len(chunks)} pieces")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to chunk text: {e}")
            return []
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text using SpaCy.
        
        Args:
            text: Input text
            
        Returns:
            List[Dict]: Extracted entities
        """
        if not self.spacy_model:
            return []
            
        try:
            import asyncio
            
            # CRITICAL: Wrap blocking spacy_model() call with timeout to prevent SSH session crashes
            # SpaCy processing can be slow for long texts, so we need timeout protection
            try:
                doc = await asyncio.wait_for(
                    asyncio.to_thread(self.spacy_model, text),
                    timeout=15.0  # 15 second timeout for entity extraction
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"⚠️ Entity extraction timed out after 15 seconds. Text length: {len(text)}")
                return []  # Return empty entities instead of failing
            
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 1.0  # SpaCy doesn't provide confidence scores
                })
            
            self.logger.info(f"✅ Extracted {len(entities)} entities")
            return entities
            
        except Exception as e:
            self.logger.error(f"Failed to extract entities: {e}")
            return []
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List[List[float]]: Embeddings
        """
        if not self.sentence_transformer:
            return []
            
        try:
            import asyncio
            
            # CRITICAL: Wrap blocking encode() call with timeout to prevent SSH session crashes
            # Embedding generation can be slow for many texts, so we need timeout protection
            try:
                embeddings = await asyncio.wait_for(
                    asyncio.to_thread(self.sentence_transformer.encode, texts),
                    timeout=30.0  # 30 second timeout for embedding generation
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"⚠️ Embedding generation timed out after 30 seconds. Text count: {len(texts)}")
                return []  # Return empty embeddings instead of failing
            
            self.logger.info(f"✅ Generated embeddings for {len(texts)} texts")
            return embeddings.tolist()
            
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            return []
    
    async def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            float: Similarity score
        """
        if not self.sentence_transformer:
            return 0.0
            
        try:
            embeddings = self.sentence_transformer.encode([text1, text2])
            similarity = self.sentence_transformer.similarity(embeddings[0], embeddings[1])
            
            self.logger.info(f"✅ Calculated similarity: {similarity}")
            return float(similarity)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            health_status = {
                "healthy": True,
                "components": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check SpaCy model
            if self.spacy_model:
                try:
                    # Test with simple text
                    doc = self.spacy_model("Test")
                    health_status["components"]["spacy"] = {
                        "healthy": True,
                        "model": self.spacy_model_name
                    }
                except Exception as e:
                    health_status["components"]["spacy"] = {
                        "healthy": False,
                        "error": str(e)
                    }
                    health_status["healthy"] = False
            else:
                health_status["components"]["spacy"] = {
                    "healthy": False,
                    "error": "SpaCy model not loaded"
                }
                health_status["healthy"] = False
            
            # Check sentence transformer
            if self.sentence_transformer:
                try:
                    # Test with simple text
                    embeddings = self.sentence_transformer.encode(["Test"])
                    health_status["components"]["sentence_transformer"] = {
                        "healthy": True,
                        "model": self.sentence_transformer_model_name
                    }
                except Exception as e:
                    health_status["components"]["sentence_transformer"] = {
                        "healthy": False,
                        "error": str(e)
                    }
                    health_status["healthy"] = False
            else:
                health_status["components"]["sentence_transformer"] = {
                    "healthy": False,
                    "error": "Sentence transformer not loaded"
                }
                health_status["healthy"] = False
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }




