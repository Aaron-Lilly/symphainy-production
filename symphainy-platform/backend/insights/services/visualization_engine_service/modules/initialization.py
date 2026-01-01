#!/usr/bin/env python3
"""Initialization module for Visualization Engine Service."""

import os
from typing import Dict, Any, Optional


class Initialization:
    """Initialization module for Visualization Engine Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    async def initialize(self) -> bool:
        """
        Initialize Visualization Engine Service dependencies.
        
        Sets up:
        - Smart City service APIs (Librarian, SemanticDataAbstraction)
        - Nurse (for observability)
        - Curator registration
        """
        try:
            self.logger.info("🚀 Initializing Visualization Engine Service...")
            
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
                self.logger.error("❌ SemanticDataAbstraction not available - visualization cannot query embeddings")
                return False
            
            # Register with Curator
            try:
                await self.service.register_with_curator(
                    capabilities=[{
                        "name": "agui_visualization",
                        "protocol": "IVisualizationEngine",
                        "description": "Create AGUI-compliant visualization components (chart, dashboard, table)",
                        "contracts": {
                            "mcp_tool": {
                                "tool_name": "create_agui_visualization",
                                "tool_definition": {
                                    "name": "create_agui_visualization",
                                    "description": "Create AGUI-compliant visualization component (chart, dashboard, or table). Returns AGUI schema-compliant component, not raw code.",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {
                                            "content_id": {
                                                "type": "string",
                                                "description": "Content metadata ID"
                                            },
                                            "visualization_type": {
                                                "type": "string",
                                                "enum": ["chart", "dashboard", "table"],
                                                "description": "Type of visualization to create"
                                            },
                                            "visualization_spec": {
                                                "type": "object",
                                                "description": "Specification of what to visualize"
                                            }
                                        },
                                        "required": ["content_id", "visualization_type", "visualization_spec"]
                                    }
                                }
                            }
                        }
                    }],
                    soa_apis=["create_agui_visualization"],
                    mcp_tools=["create_agui_visualization"]
                )
                self.logger.info("✅ Visualization Engine Service registered with Curator")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
                # Don't fail initialization if Curator registration fails
            
            self.logger.info("✅ Visualization Engine Service initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Visualization Engine Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False

