#!/usr/bin/env python3
"""Initialization module for Embedding Service."""

import os
from typing import Dict, Any, Optional


class Initialization:
    """Initialization module for Embedding Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    async def initialize(self) -> bool:
        """
        Initialize Embedding Service dependencies.
        
        Sets up:
        - Smart City service APIs (Librarian, Content Steward, SemanticDataAbstraction)
        - StatelessHFInferenceAgent (for embedding generation)
        - Nurse (for observability)
        """
        try:
            self.logger.info("🚀 Initializing Embedding Service...")
            
            # Get Smart City service APIs (use same pattern as FileParserService)
            # Business Enablement services should use Smart City SOA APIs via helper methods
            self.service.librarian = await self.service.get_librarian_api()
            self.service.content_steward = await self.service.get_content_steward_api()
            self.service.data_steward = await self.service.get_data_steward_api()
            # Get SemanticDataAbstraction via Platform Gateway (Content realm now has access)
            self.service.semantic_data = self.service.get_abstraction("semantic_data")
            self.service.nurse = await self.service.get_nurse_api()
            
            # Log discovery results for debugging
            if not self.service.content_steward:
                self.logger.warning("⚠️ Content Steward API not discovered via Curator - file retrieval may fail")
            else:
                self.logger.info(f"✅ Content Steward API discovered: {type(self.service.content_steward).__name__}")
            
            if not self.service.semantic_data:
                self.logger.error("❌ SemanticDataAbstraction not available - embeddings cannot be stored")
                return False
            
            # Get HuggingFaceAdapter for embedding generation (PRIMARY PATHWAY ONLY)
            # This is the only supported method - no fallbacks
            try:
                public_works = self.service.di_container.get_foundation_service("PublicWorksFoundationService")
                if public_works and hasattr(public_works, 'huggingface_adapter'):
                    self.service.hf_adapter = public_works.huggingface_adapter
                    self.logger.info("✅ Got HuggingFaceAdapter from Public Works Foundation")
                else:
                    # Try to create directly using ConfigAdapter (preferred) or environment
                    from foundations.public_works_foundation.infrastructure_adapters.huggingface_adapter import HuggingFaceAdapter
                    
                    # Get ConfigAdapter from PublicWorksFoundationService if available
                    config_adapter = None
                    try:
                        if self.service.di_container and hasattr(self.service.di_container, 'get_foundation_service'):
                            public_works = self.service.di_container.get_foundation_service("PublicWorksFoundationService")
                            if public_works and hasattr(public_works, 'config_adapter'):
                                config_adapter = public_works.config_adapter
                    except Exception:
                        pass
                    
                    if config_adapter:
                        endpoint_url = config_adapter.get("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
                        api_key = config_adapter.get("HUGGINGFACE_EMBEDDINGS_API_KEY") or config_adapter.get("HUGGINGFACE_API_KEY")
                    else:
                        endpoint_url = os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
                        api_key = os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
                        if endpoint_url or api_key:
                            self.logger.warning("⚠️ [EMBEDDING_SERVICE] Using os.getenv() - consider accessing ConfigAdapter via PublicWorksFoundationService")
                    
                    if endpoint_url and api_key:
                        self.service.hf_adapter = HuggingFaceAdapter(
                            endpoint_url=endpoint_url, 
                            api_key=api_key,
                            config_adapter=config_adapter  # Pass ConfigAdapter for centralized configuration
                        )
                        self.logger.info("✅ Created HuggingFaceAdapter directly")
                    else:
                        self.logger.error("❌ HuggingFace endpoint not configured - HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL and HUGGINGFACE_EMBEDDINGS_API_KEY required")
                        self.service.hf_adapter = None
                        return False  # Fail initialization if HF adapter not available
            except Exception as e:
                self.logger.error(f"❌ Failed to get HuggingFaceAdapter: {e}")
                self.service.hf_adapter = None
                return False  # Fail initialization if HF adapter not available
            
            if not self.service.hf_adapter:
                self.logger.error("❌ HuggingFaceAdapter not available - EmbeddingService cannot function without it")
                return False
            
            # Get LLM abstraction for semantic meaning inference (optional but recommended)
            try:
                public_works_foundation = await self.service.get_foundation_service("PublicWorksFoundationService")
                if public_works_foundation:
                    self.service.llm_abstraction = public_works_foundation.get_abstraction("llm")
                    if self.service.llm_abstraction:
                        self.logger.info("✅ LLM abstraction initialized for semantic meaning inference")
                    else:
                        self.logger.warning("⚠️ LLM abstraction not available - will use column name as semantic meaning")
                else:
                    self.logger.warning("⚠️ PublicWorksFoundationService not available - will use column name as semantic meaning")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get LLM abstraction: {e} - will use column name as semantic meaning")
            
            self.logger.info("✅ Embedding Service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Embedding Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False

