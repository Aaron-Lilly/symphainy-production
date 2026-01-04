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
        - Smart City service APIs (Librarian, Data Steward, SemanticDataAbstraction)
        - StatelessHFInferenceAgent (for embedding generation)
        - Nurse (for observability)
        Note: Content Steward consolidated into Data Steward
        """
        try:
            self.logger.info("🚀 Initializing Embedding Service...")
            
            # Get Smart City service APIs (use same pattern as FileParserService)
            # Business Enablement services should use Smart City SOA APIs via helper methods
            self.service.librarian = await self.service.get_librarian_api()
            # Note: Content Steward consolidated into Data Steward
            self.service.data_steward = await self.service.get_data_steward_api()
            # Get SemanticDataAbstraction via Platform Gateway (Content realm now has access)
            self.service.semantic_data = self.service.get_abstraction("semantic_data")
            self.service.nurse = await self.service.get_nurse_api()
            
            # Log discovery results for debugging
            if not self.service.data_steward:
                self.logger.warning("⚠️ Data Steward API not discovered via Curator - file retrieval may fail")
            else:
                self.logger.info(f"✅ Data Steward API discovered: {type(self.service.data_steward).__name__}")
            
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
                    
                    # Get ConfigAdapter from PublicWorksFoundationService (required)
                    if not self.service.di_container:
                        raise ValueError("DI Container not available - cannot get ConfigAdapter")
                    
                    if not hasattr(self.service.di_container, 'get_foundation_service'):
                        raise ValueError("DI Container does not have get_foundation_service method")
                    
                    public_works = self.service.di_container.get_foundation_service("PublicWorksFoundationService")
                    if not public_works:
                        raise ValueError("Public Works Foundation Service not available - cannot get ConfigAdapter")
                    
                    if not hasattr(public_works, 'config_adapter') or not public_works.config_adapter:
                        raise ValueError("ConfigAdapter not available in Public Works Foundation")
                    
                    config_adapter = public_works.config_adapter
                    endpoint_url = config_adapter.get("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
                    api_key = config_adapter.get("HUGGINGFACE_EMBEDDINGS_API_KEY") or config_adapter.get("HUGGINGFACE_API_KEY")
                    
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
            
            # Get agent for semantic meaning inference (via Agentic Foundation SDK - NO direct LLM access)
            # CRITICAL RULE: LLMs must ONLY be accessed via agents (for governance, traceability, and cost control)
            try:
                agentic_foundation = await self.service.get_foundation_service("AgenticFoundationService")
                if agentic_foundation:
                    # Create a lightweight agent for semantic meaning inference
                    from foundations.agentic_foundation.agent_sdk.lightweight_llm_agent import LightweightLLMAgent
                    from foundations.agentic_foundation.agui_schema_registry import AGUISchema, AGUIComponent
                    
                    # Create simple AGUI schema for semantic meaning inference
                    agui_schema = AGUISchema(
                        agent_name="SemanticMeaningInferenceAgent",
                        version="1.0.0",
                        description="Agent for inferring semantic meaning of database columns",
                        components=[
                            AGUIComponent(
                                type="text_output",
                                title="Semantic Meaning",
                                description="The inferred semantic meaning of the column",
                                required=True,
                                properties={
                                    "semantic_meaning": "The semantic meaning text (1-5 words)"
                                }
                            )
                        ],
                        metadata={"task": "semantic_meaning_inference"}
                    )
                    
                    # Create lightweight agent via Agentic Foundation SDK
                    self.service.semantic_meaning_agent = await agentic_foundation.create_agent(
                        agent_class=LightweightLLMAgent,
                        agent_name="SemanticMeaningInferenceAgent",
                        agent_type="specialist",
                        realm_name="content",
                        di_container=self.service.di_container,
                        orchestrator=None,
                        user_context=None,
                        capabilities=["semantic_meaning_inference"],
                        required_roles=[],
                        agui_schema=agui_schema
                    )
                    
                    if self.service.semantic_meaning_agent:
                        self.logger.info("✅ Semantic meaning inference agent initialized (via Agentic Foundation SDK)")
                    else:
                        self.logger.warning("⚠️ Semantic meaning inference agent not available - will use column name as semantic meaning")
                else:
                    self.logger.warning("⚠️ AgenticFoundationService not available - will use column name as semantic meaning")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to get semantic meaning inference agent: {e} - will use column name as semantic meaning")
            
            self.logger.info("✅ Embedding Service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Embedding Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False

