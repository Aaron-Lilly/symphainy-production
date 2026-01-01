#!/usr/bin/env python3
"""Initialization module for Semantic Enrichment Gateway."""

import os
from typing import Dict, Any, Optional


class Initialization:
    """Initialization module for Semantic Enrichment Gateway."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    async def initialize(self) -> bool:
        """
        Initialize Semantic Enrichment Gateway dependencies.
        
        Sets up:
        - Smart City service APIs (Librarian, SemanticDataAbstraction, Content Steward)
        - Nurse (for observability)
        - Curator registration
        """
        try:
            self.logger.info("🚀 Initializing Semantic Enrichment Gateway...")
            
            # Get Smart City service APIs
            self.service.librarian = await self.service.get_librarian_api()
            self.service.semantic_data = self.service.get_abstraction("semantic_data")
            self.service.content_steward = await self.service.get_content_steward_api()
            self.service.nurse = await self.service.get_nurse_api()
            
            # Log discovery results for debugging
            if not self.service.librarian:
                self.logger.warning("⚠️ Librarian API not discovered via Curator - metadata access may fail")
            else:
                self.logger.info(f"✅ Librarian API discovered: {type(self.service.librarian).__name__}")
            
            if not self.service.semantic_data:
                self.logger.error("❌ SemanticDataAbstraction not available - cannot store enriched embeddings")
                return False
            
            if not self.service.content_steward:
                self.logger.warning("⚠️ Content Steward API not discovered - enrichment service may not be available")
            else:
                self.logger.info(f"✅ Content Steward API discovered: {type(self.service.content_steward).__name__}")
            
            # Register with Curator
            try:
                await self.service.register_with_curator(
                    capabilities=[{
                        "name": "semantic_enrichment",
                        "protocol": "ISemanticEnrichmentGateway",
                        "description": "Request semantic enrichment without exposing parsed data",
                        "contracts": {
                            "mcp_tool": {
                                "tool_name": "enrich_semantic_layer",
                                "tool_definition": {
                                    "name": "enrich_semantic_layer",
                                    "description": "Request semantic enrichment when embeddings lack information. Maintains security boundary by requesting enrichment (not raw data) and storing new embeddings in semantic layer.",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "content_id": {
                                                "type": "string",
                                                "description": "Content metadata ID"
                                            },
                                            "enrichment_request": {
                                                "type": "object",
                                                "properties": {
                                                    "type": {
                                                        "type": "string",
                                                        "enum": ["column_values", "statistics", "correlations", "distributions"],
                                                        "description": "Type of enrichment needed"
                                                    },
                                                    "filters": {
                                                        "type": "object",
                                                        "description": "Optional: Which columns/rows needed"
                                                    },
                                                    "description": {
                                                        "type": "string",
                                                        "description": "Optional: Human-readable description"
                                                    }
                                                },
                                                "required": ["type"]
                                            }
                                        },
                                        "required": ["content_id", "enrichment_request"]
                                    }
                                }
                            }
                        }
                    }],
                    soa_apis=["enrich_semantic_layer"],
                    mcp_tools=["enrich_semantic_layer"]
                )
                self.logger.info("✅ Semantic Enrichment Gateway registered with Curator")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
                # Don't fail initialization if Curator registration fails
            
            self.logger.info("✅ Semantic Enrichment Gateway initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Semantic Enrichment Gateway: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False

