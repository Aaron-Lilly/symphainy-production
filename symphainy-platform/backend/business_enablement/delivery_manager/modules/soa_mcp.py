#!/usr/bin/env python3
"""
Delivery Manager Service - SOA/MCP Module

Micro-module for SOA API exposure and MCP tool integration.
"""

from typing import Any, Dict
from datetime import datetime


class SoaMcp:
    """SOA/MCP module for Delivery Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Delivery Manager capabilities."""
        self.service.soa_apis = {
            "deliver_capability": {
                "endpoint": "/api/delivery-manager/capability",
                "method": "POST",
                "description": "Deliver a business capability via business enablement pillars",
                "parameters": ["capability_request"]
            },
            "orchestrate_pillars": {
                "endpoint": "/api/delivery-manager/pillars/orchestrate",
                "method": "POST",
                "description": "Orchestrate all 5 business enablement pillars",
                "parameters": ["business_context"]
            },
            "track_outcomes": {
                "endpoint": "/api/delivery-manager/outcomes",
                "method": "POST",
                "description": "Track business outcomes",
                "parameters": ["outcome_request"]
            },
            "orchestrate_business_enablement": {
                "endpoint": "/api/delivery-manager/business-enablement/orchestrate",
                "method": "POST",
                "description": "Orchestrate business enablement via Business Orchestrator (top-down flow)",
                "parameters": ["business_context"]
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ SOA APIs exposed: {len(self.service.soa_apis)} endpoints")
    
    async def initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for delivery management."""
        self.service.mcp_tools = {
            "deliver_capability_tool": {
                "name": "deliver_capability_tool",
                "description": "Deliver a business capability via business enablement pillars",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "capability_request": {
                            "type": "object",
                            "properties": {
                                "capability_type": {"type": "string"},
                                "context": {"type": "object"}
                            }
                        }
                    }
                }
            },
            "track_outcomes_tool": {
                "name": "track_outcomes_tool",
                "description": "Track business outcomes",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "outcome_request": {
                            "type": "object",
                            "properties": {
                                "outcome_type": {"type": "string"},
                                "metrics": {"type": "object"}
                            }
                        }
                    }
                }
            },
            "orchestrate_business_enablement_tool": {
                "name": "orchestrate_business_enablement_tool",
                "description": "Orchestrate business enablement via Business Orchestrator (top-down flow: Delivery → Business Enablement)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "business_context": {"type": "object"}
                    }
                }
            }
        }
        
        if self.service.logger:
            self.service.logger.info(f"✅ MCP Tools registered: {len(self.service.mcp_tools)} tools")
    
    async def register_delivery_manager_capabilities(self):
        """
        Register Delivery Manager capabilities with Curator using Phase 2 pattern.
        
        Uses CapabilityDefinition structure with contracts for SOA APIs and MCP tools.
        """
        try:
            if not self.service.di_container:
                if self.service.logger:
                    self.service.logger.warning("⚠️ DI Container not available - skipping Curator registration")
                return
            
            # Use RealmServiceBase's register_with_curator method (Phase 2 pattern)
            await self.service.register_with_curator(
                capabilities=[
                    {
                        "name": "capability_delivery",
                        "protocol": "DeliveryManagerProtocol",
                        "description": "Deliver business capabilities via business enablement pillars",
                        "contracts": {
                            "soa_api": {
                                "api_name": "deliver_capability",
                                "endpoint": "/api/delivery-manager/capability",
                                "method": "POST",
                                "handler": self.service.deliver_capability,
                                "metadata": {
                                    "description": "Deliver a business capability via business enablement pillars",
                                    "parameters": ["capability_request", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "deliver_capability_tool",
                                "tool_definition": {
                                    "name": "deliver_capability_tool",
                                    "description": "Deliver a business capability via business enablement pillars",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "capability_request": {
                                                "type": "object",
                                                "properties": {
                                                    "capability_type": {"type": "string"},
                                                    "context": {"type": "object"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "delivery.deliver_capability",
                            "semantic_api": "/api/delivery-manager/capability",
                            "user_journey": "deliver_capability"
                        }
                    },
                    {
                        "name": "pillar_orchestration",
                        "protocol": "DeliveryManagerProtocol",
                        "description": "Orchestrate all 5 business enablement pillars",
                        "contracts": {
                            "soa_api": {
                                "api_name": "orchestrate_pillars",
                                "endpoint": "/api/delivery-manager/pillars/orchestrate",
                                "method": "POST",
                                "handler": self.service.orchestrate_pillars,
                                "metadata": {
                                    "description": "Orchestrate all 5 business enablement pillars",
                                    "parameters": ["business_context", "user_context"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "delivery.orchestrate_pillars",
                            "semantic_api": "/api/delivery-manager/pillars/orchestrate",
                            "user_journey": "orchestrate_pillars"
                        }
                    },
                    {
                        "name": "outcome_tracking",
                        "protocol": "DeliveryManagerProtocol",
                        "description": "Track business outcomes",
                        "contracts": {
                            "soa_api": {
                                "api_name": "track_outcomes",
                                "endpoint": "/api/delivery-manager/outcomes",
                                "method": "POST",
                                "handler": self.service.track_outcomes,
                                "metadata": {
                                    "description": "Track business outcomes",
                                    "parameters": ["outcome_request", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "track_outcomes_tool",
                                "tool_definition": {
                                    "name": "track_outcomes_tool",
                                    "description": "Track business outcomes",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "outcome_request": {
                                                "type": "object",
                                                "properties": {
                                                    "outcome_type": {"type": "string"},
                                                    "metrics": {"type": "object"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "delivery.track_outcomes",
                            "semantic_api": "/api/delivery-manager/outcomes",
                            "user_journey": "track_outcomes"
                        }
                    },
                    {
                        "name": "business_enablement_orchestration",
                        "protocol": "DeliveryManagerProtocol",
                        "description": "Orchestrate business enablement via Business Orchestrator",
                        "contracts": {
                            "soa_api": {
                                "api_name": "orchestrate_business_enablement",
                                "endpoint": "/api/delivery-manager/business-enablement/orchestrate",
                                "method": "POST",
                                "handler": self.service.orchestrate_business_enablement,
                                "metadata": {
                                    "description": "Orchestrate business enablement via Business Orchestrator (top-down flow)",
                                    "parameters": ["business_context", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "orchestrate_business_enablement_tool",
                                "tool_definition": {
                                    "name": "orchestrate_business_enablement_tool",
                                    "description": "Orchestrate business enablement via Business Orchestrator (top-down flow: Delivery → Business Enablement)",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "business_context": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "delivery.orchestrate_business_enablement",
                            "semantic_api": "/api/delivery-manager/business-enablement/orchestrate",
                            "user_journey": "orchestrate_business_enablement"
                        }
                    }
                ],
                soa_apis=["deliver_capability", "orchestrate_pillars", "track_outcomes", "orchestrate_business_enablement"],
                mcp_tools=["deliver_capability_tool", "track_outcomes_tool", "orchestrate_business_enablement_tool"]
            )
            
            if self.service.logger:
                self.service.logger.info("✅ Delivery Manager registered with Curator (Phase 2)")
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to register with Curator: {str(e)}")
            import traceback
            if self.service.logger:
                self.service.logger.error(f"Traceback: {traceback.format_exc()}")






