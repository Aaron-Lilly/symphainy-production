#!/usr/bin/env python3
"""
SOA/MCP Module - Post Office Service

Handles SOA API exposure and MCP tool integration.
"""

from typing import Dict, Any


class SoaMcp:
    """SOA/MCP module for Post Office Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities."""
        self.service.soa_apis = {
            "send_message": {
                "endpoint": "/api/post-office/send-message",
                "method": "POST",
                "description": "Send message with routing and delivery",
                "parameters": ["request"]
            },
            "get_messages": {
                "endpoint": "/api/post-office/messages",
                "method": "GET",
                "description": "Get messages for recipient",
                "parameters": ["request"]
            },
            "route_event": {
                "endpoint": "/api/post-office/route-event",
                "method": "POST",
                "description": "Route event to appropriate service",
                "parameters": ["request"]
            },
            "publish_event": {
                "endpoint": "/api/post-office/publish-event",
                "method": "POST",
                "description": "Publish event via Post Office",
                "parameters": ["request"]
            },
            "subscribe_to_events": {
                "endpoint": "/api/post-office/subscribe-to-events",
                "method": "POST",
                "description": "Subscribe to events via Post Office",
                "parameters": ["request"]
            },
            "unsubscribe_from_events": {
                "endpoint": "/api/post-office/unsubscribe-from-events",
                "method": "POST",
                "description": "Unsubscribe from events via Post Office",
                "parameters": ["request"]
            },
            "register_agent": {
                "endpoint": "/api/post-office/register-agent",
                "method": "POST",
                "description": "Register agent for communication",
                "parameters": ["request"]
            },
            "orchestrate_pillar_coordination": {
                "endpoint": "/api/post-office/orchestrate/pillar-coordination",
                "method": "POST",
                "description": "Orchestrate communication between pillars",
                "parameters": ["pattern_name", "trigger_data"]
            },
            "orchestrate_realm_communication": {
                "endpoint": "/api/post-office/orchestrate/realm-communication",
                "method": "POST",
                "description": "Orchestrate communication between realms",
                "parameters": ["source_realm", "target_realm", "communication_data"]
            },
            "orchestrate_event_driven_communication": {
                "endpoint": "/api/post-office/orchestrate/event-driven",
                "method": "POST",
                "description": "Orchestrate event-driven communication patterns",
                "parameters": ["event_type", "event_data"]
            }
        }
    
    async def initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for communication operations."""
        self.service.mcp_tools = {
            "message_sender": {
                "name": "message_sender",
                "description": "Send messages with routing and delivery",
                "parameters": ["request", "routing_options"]
            },
            "event_router": {
                "name": "event_router",
                "description": "Route events to appropriate services",
                "parameters": ["request", "routing_rules"]
            },
            "agent_registrar": {
                "name": "agent_registrar",
                "description": "Register agents for communication",
                "parameters": ["request", "agent_config"]
            },
            "communication_orchestrator": {
                "name": "communication_orchestrator",
                "description": "Orchestrate communication patterns",
                "parameters": ["pattern_type", "pattern_data", "orchestration_options"]
            }
        }
    
    async def register_capabilities(self) -> Dict[str, Any]:
        """Register Post Office capabilities with Curator using Phase 2 pattern (simplified for Smart City)."""
        from datetime import datetime
        
        try:
            # Build capabilities list with SOA API and MCP Tool contracts
            capabilities = []
            
            # Create messaging capability
            capabilities.append({
                "name": "messaging",
                "protocol": "PostOfficeServiceProtocol",
                "description": "Message sending and retrieval",
                "contracts": {
                    "soa_api": {
                        "api_name": "send_message",
                        "endpoint": self.service.soa_apis.get("send_message", {}).get("endpoint", "/soa/post-office/send_message"),
                        "method": self.service.soa_apis.get("send_message", {}).get("method", "POST"),
                        "handler": getattr(self.service, "send_message", None),
                        "metadata": {
                            "description": "Send message with routing and delivery",
                            "apis": ["send_message", "get_messages"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "post_office_message_sender",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "post_office_message_sender",
                            "description": "Send messages with routing and delivery",
                            "input_schema": {
                                "type": "object",
                                "properties": {
                                    "request": {"type": "object"},
                                    "routing_options": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            })
            
            # Create event_routing capability
            capabilities.append({
                "name": "event_routing",
                "protocol": "PostOfficeServiceProtocol",
                "description": "Event routing, publishing, and subscription",
                "contracts": {
                    "soa_api": {
                        "api_name": "route_event",
                        "endpoint": self.service.soa_apis.get("route_event", {}).get("endpoint", "/soa/post-office/route_event"),
                        "method": self.service.soa_apis.get("route_event", {}).get("method", "POST"),
                        "handler": getattr(self.service, "route_event", None),
                        "metadata": {
                            "description": "Event routing, publishing, and subscription",
                            "apis": ["route_event", "publish_event", "subscribe_to_events", "unsubscribe_from_events"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "post_office_event_router",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "post_office_event_router",
                            "description": "Route events to appropriate services",
                            "input_schema": {
                                "type": "object",
                                "properties": {
                                    "request": {"type": "object"},
                                    "routing_rules": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            })
            
            # Create event_publishing capability
            capabilities.append({
                "name": "event_publishing",
                "protocol": "PostOfficeServiceProtocol",
                "description": "Event publishing via Post Office",
                "contracts": {
                    "soa_api": {
                        "api_name": "publish_event",
                        "endpoint": self.service.soa_apis.get("publish_event", {}).get("endpoint", "/soa/post-office/publish_event"),
                        "method": self.service.soa_apis.get("publish_event", {}).get("method", "POST"),
                        "handler": getattr(self.service, "publish_event", None),
                        "metadata": {
                            "description": "Publish event via Post Office"
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "post_office_event_publisher",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "post_office_event_publisher",
                            "description": "Publish events via Post Office",
                            "input_schema": {
                                "type": "object",
                                "properties": {
                                    "request": {"type": "object"},
                                    "event_type": {"type": "string"},
                                    "event_data": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            })
            
            # Create event_subscription capability
            capabilities.append({
                "name": "event_subscription",
                "protocol": "PostOfficeServiceProtocol",
                "description": "Event subscription via Post Office",
                "contracts": {
                    "soa_api": {
                        "api_name": "subscribe_to_events",
                        "endpoint": self.service.soa_apis.get("subscribe_to_events", {}).get("endpoint", "/soa/post-office/subscribe_to_events"),
                        "method": self.service.soa_apis.get("subscribe_to_events", {}).get("method", "POST"),
                        "handler": getattr(self.service, "subscribe_to_events", None),
                        "metadata": {
                            "description": "Subscribe to events via Post Office",
                            "apis": ["subscribe_to_events", "unsubscribe_from_events"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "post_office_event_subscriber",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "post_office_event_subscriber",
                            "description": "Subscribe/unsubscribe to events via Post Office",
                            "input_schema": {
                                "type": "object",
                                "properties": {
                                    "request": {"type": "object"},
                                    "event_type": {"type": "string"},
                                    "handler_id": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            })
            
            # Create communication_orchestration capability
            capabilities.append({
                "name": "communication_orchestration",
                "protocol": "PostOfficeServiceProtocol",
                "description": "Communication orchestration across pillars and realms",
                "contracts": {
                    "soa_api": {
                        "api_name": "orchestrate_pillar_coordination",
                        "endpoint": self.service.soa_apis.get("orchestrate_pillar_coordination", {}).get("endpoint", "/soa/post-office/orchestrate_pillar_coordination"),
                        "method": self.service.soa_apis.get("orchestrate_pillar_coordination", {}).get("method", "POST"),
                        "handler": getattr(self.service, "orchestrate_pillar_coordination", None),
                        "metadata": {
                            "description": "Orchestrate communication between pillars",
                            "apis": ["orchestrate_pillar_coordination", "orchestrate_realm_communication", "orchestrate_event_driven_communication"]
                        }
                    },
                    "mcp_tool": {
                        "tool_name": "post_office_communication_orchestrator",
                        "mcp_server": "smart_city_mcp_server",
                        "tool_definition": {
                            "name": "post_office_communication_orchestrator",
                            "description": "Orchestrate communication patterns",
                            "input_schema": {
                                "type": "object",
                                "properties": {
                                    "pattern_type": {"type": "string"},
                                    "pattern_data": {"type": "object"},
                                    "orchestration_options": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            })
            
            # Register using register_with_curator (simplified Phase 2 pattern)
            soa_api_names = list(self.service.soa_apis.keys())
            mcp_tool_names = [f"post_office_{tool}" for tool in self.service.mcp_tools.keys()]
            
            success = await self.service.register_with_curator(
                capabilities=capabilities,
                soa_apis=soa_api_names,
                mcp_tools=mcp_tool_names,
                protocols=[{
                    "name": "PostOfficeServiceProtocol",
                    "definition": {
                        "methods": {api: {"input_schema": {}, "output_schema": {}} for api in soa_api_names}
                    }
                }]
            )
            
            if success:
                if hasattr(self.service, '_log'):
                    self.service._log("info", f"✅ Post Office registered with Curator (Phase 2 pattern - Smart City): {len(capabilities)} capabilities")
            else:
                if hasattr(self.service, '_log'):
                    self.service._log("warning", "⚠️ Failed to register Post Office with Curator")
                    
        except Exception as e:
            if hasattr(self.service, '_log'):
                self.service._log("error", f"❌ Failed to register Post Office capabilities: {e}")
                import traceback
                self.service._log("error", f"Traceback: {traceback.format_exc()}")
        
        # Return capabilities metadata
        return await self._get_post_office_capabilities_dict()
    
    async def _get_post_office_capabilities_dict(self) -> Dict[str, Any]:
        """Get Post Office capabilities metadata dict."""
        from datetime import datetime
        return {
            "service_name": "PostOfficeService",
            "service_type": "strategic_communication_orchestrator",
            "realm": "smart_city",
            "capabilities": [
                "strategic_communication_orchestration",
                "cross_pillar_coordination",
                "realm_orchestration",
                "event_driven_communication",
                "message_routing",
                "agent_registration",
                "infrastructure_integration"
            ],
            "infrastructure_connections": {
                "messaging": "Redis",
                "event_management": "Redis",
                "session": "Redis"
            },
            "soa_apis": self.service.soa_apis,
            "mcp_tools": self.service.mcp_tools,
            "status": "active",
            "infrastructure_connected": getattr(self.service, "is_infrastructure_connected", False),
            "infrastructure_correct_from_start": True,
            "timestamp": datetime.utcnow().isoformat()
        }

