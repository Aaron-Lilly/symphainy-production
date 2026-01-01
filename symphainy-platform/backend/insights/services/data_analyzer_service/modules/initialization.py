#!/usr/bin/env python3
"""Initialization module for Data Analyzer Service."""

import os
from typing import Dict, Any, Optional


class Initialization:
    """Initialization module for Data Analyzer Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    async def initialize(self) -> bool:
        """
        Initialize Data Analyzer Service dependencies.
        
        Sets up:
        - Smart City service APIs (Librarian, SemanticDataAbstraction)
        - Nurse (for observability)
        - Curator registration
        """
        try:
            self.logger.info("🚀 Initializing Data Analyzer Service...")
            
            # Get Smart City service APIs (use same pattern as other enabling services)
            # Business Enablement services should use Smart City SOA APIs via helper methods
            self.service.librarian = await self.service.get_librarian_api()
            self.service.semantic_data = self.service.get_abstraction("semantic_data")
            self.service.nurse = await self.service.get_nurse_api()
            
            # Log discovery results for debugging
            if not self.service.librarian:
                self.logger.warning("⚠️ Librarian API not discovered via Curator - metadata access may fail")
            else:
                self.logger.info(f"✅ Librarian API discovered: {type(self.service.librarian).__name__}")
            
            if not self.service.semantic_data:
                self.logger.error("❌ SemanticDataAbstraction not available - EDA analysis cannot query embeddings")
                return False
            
            # Register with Curator
            try:
                await self.service.register_with_curator(
                    capabilities=[{
                        "name": "eda_analysis",
                        "protocol": "IDataAnalyzer",
                        "description": "Run EDA analysis on semantic embeddings",
                        "contracts": {
                            "mcp_tool": {
                                "tool_name": "run_eda_analysis",
                                "tool_definition": {
                                    "name": "run_eda_analysis",
                                    "description": "Run exploratory data analysis on semantic embeddings. Returns deterministic results that can be interpreted by LLM.",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "content_id": {
                                                "type": "string",
                                                "description": "Content metadata ID"
                                            },
                                            "analysis_types": {
                                                "type": "array",
                                                "items": {
                                                    "type": "string",
                                                    "enum": ["statistics", "correlations", "distributions", "missing_values"]
                                                },
                                                "description": "List of analysis types to run"
                                            }
                                        },
                                        "required": ["content_id", "analysis_types"]
                                    }
                                }
                            }
                        }
                    }],
                    soa_apis=["run_eda_analysis"],
                    mcp_tools=["run_eda_analysis"]
                )
                self.logger.info("✅ Data Analyzer Service registered with Curator")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
                # Don't fail initialization if Curator registration fails
            
            self.logger.info("✅ Data Analyzer Service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Data Analyzer Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False


