#!/usr/bin/env python3
"""
Post Office MCP Server

MCP server for exposing Post Office Service capabilities as MCP tools.
Provides event routing, messaging, AGUI communication, and notification management.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from backend.smart_city.services.post_office.post_office_service import PostOfficeService
from backend.smart_city.protocols.mcp_server_protocol import MCPBaseServer
from backend.smart_city.protocols.mcp_server_protocol import MCPTool, MCPServerInfo


class PostOfficeMCPServer(MCPBaseServer):
    """
    Post Office MCP Server

    Exposes Post Office Service capabilities as MCP tools for external consumers.
    """

    def __init__(self, environment_loader=None, logger=None):
        """Initialize Post Office MCP Server."""
        super().__init__(environment_loader, logger)
        
        # Initialize Post Office Service
        self.post_office_service = PostOfficeService(environment_loader, logger)
        
        # Server info
        self.server_info = MCPServerInfo(
            server_name="PostOfficeMCPServer",
            version="1.0.0",
            description="MCP server for Post Office Service - event routing, messaging, AGUI communication, and notifications",
            interface_name="PostOfficeInterface",
            tools=[],
            capabilities=["event_routing", "messaging", "agui_communication", "notification_management"]
        )

        self.logger.info("📮 Post Office MCP Server initialized")

    async def initialize(self):
        """Initialize the MCP server."""
        try:
            await super().initialize()
            await self.post_office_service.initialize()
            self.logger.info("✅ Post Office MCP Server initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Post Office MCP Server: {e}")
            raise

    async def initialize_service_integration(self):
        """Initialize integration with the Post Office Service."""
        try:
            self.logger.info("🔗 Initializing Post Office Service integration...")
            
            # Initialize the underlying service
            await self.post_office_service.initialize()
            
            self.logger.info("✅ Post Office Service integration initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Post Office Service integration: {e}")
            raise

    def register_tools(self):
        """Register MCP tools with the server."""
        try:
            self.logger.info("🔧 Registering Post Office MCP tools...")
            
            # Tools are registered dynamically in get_tools()
            # This method is called during server initialization
            
            self.logger.info("✅ Post Office MCP tools registered")
        except Exception as e:
            self.logger.error(f"❌ Failed to register Post Office MCP tools: {e}")
            raise

    async def get_server_info(self) -> MCPServerInfo:
        """Get server information."""
        return self.server_info

    async def get_tools(self) -> List[MCPTool]:
        """Get available MCP tools."""
        return [
            # Event Routing Tools
            MCPTool(
                name="publish_event",
                description="Publish an event to the routing system",
                input_schema={
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string", "description": "Type of event"},
                        "source": {"type": "string", "description": "Event source"},
                        "target": {"type": "string", "description": "Event target"},
                        "scope": {"type": "string", "description": "Event scope (local, regional, global)"},
                        "priority": {"type": "string", "description": "Event priority"},
                        "payload": {"type": "object", "description": "Event payload data"},
                        "metadata": {"type": "object", "description": "Event metadata"},
                        "correlation_id": {"type": "string", "description": "Correlation ID for event tracking"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Event tags"}
                    },
                    "required": ["event_type", "source"]
                },
                handler=self._handle_publish_event,
                tags=["event", "routing", "publish"]
            ),
            MCPTool(
                name="subscribe_to_events",
                description="Subscribe to events matching given criteria",
                input_schema={
                    "type": "object",
                    "properties": {
                        "subscriber": {"type": "string", "description": "Subscriber identifier"},
                        "event_types": {"type": "array", "items": {"type": "string"}, "description": "Event types to subscribe to"},
                        "filters": {"type": "object", "description": "Event filters"},
                        "callback_url": {"type": "string", "description": "Callback URL for event delivery"},
                        "delivery_guarantee": {"type": "string", "description": "Delivery guarantee level"}
                    },
                    "required": ["subscriber"]
                },
                handler=self._handle_subscribe_to_events,
                tags=["event", "subscribe", "routing"]
            ),
            MCPTool(
                name="get_events",
                description="Get events matching given filters",
                input_schema={
                    "type": "object",
                    "properties": {
                        "filters": {"type": "object", "description": "Event filters"},
                        "limit": {"type": "integer", "description": "Maximum number of events to return"},
                        "offset": {"type": "integer", "description": "Number of events to skip"}
                    }
                },
                handler=self._handle_get_events,
                tags=["event", "get", "routing"]
            ),
            MCPTool(
                name="correlate_events",
                description="Correlate events based on correlation criteria",
                input_schema={
                    "type": "object",
                    "properties": {
                        "correlation_id": {"type": "string", "description": "Correlation ID to search for"}
                    },
                    "required": ["correlation_id"]
                },
                handler=self._handle_correlate_events,
                tags=["event", "correlate", "routing"]
            ),

            # Messaging Tools
            MCPTool(
                name="send_message",
                description="Send a message to recipients",
                input_schema={
                    "type": "object",
                    "properties": {
                        "message_type": {"type": "string", "description": "Type of message (text, email, sms, push, websocket, api)"},
                        "sender": {"type": "string", "description": "Message sender"},
                        "recipients": {"type": "array", "items": {"type": "string"}, "description": "Message recipients"},
                        "subject": {"type": "string", "description": "Message subject"},
                        "content": {"type": "string", "description": "Message content"},
                        "priority": {"type": "string", "description": "Message priority"},
                        "delivery_guarantee": {"type": "string", "description": "Delivery guarantee level"},
                        "expires_at": {"type": "string", "description": "Message expiration time"},
                        "metadata": {"type": "object", "description": "Message metadata"},
                        "template_id": {"type": "string", "description": "Message template ID"},
                        "attachments": {"type": "array", "items": {"type": "object"}, "description": "Message attachments"}
                    },
                    "required": ["recipients", "content"]
                },
                handler=self._handle_send_message,
                tags=["message", "send", "communication"]
            ),
            MCPTool(
                name="get_message_status",
                description="Get the status of a message",
                input_schema={
                    "type": "object",
                    "properties": {
                        "message_id": {"type": "string", "description": "Message ID"}
                    },
                    "required": ["message_id"]
                },
                handler=self._handle_get_message_status,
                tags=["message", "status", "communication"]
            ),
            MCPTool(
                name="create_message_template",
                description="Create a message template",
                input_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Template name"},
                        "description": {"type": "string", "description": "Template description"},
                        "message_type": {"type": "string", "description": "Message type"},
                        "subject_template": {"type": "string", "description": "Subject template"},
                        "content_template": {"type": "string", "description": "Content template"},
                        "variables": {"type": "array", "items": {"type": "string"}, "description": "Template variables"}
                    },
                    "required": ["name", "content_template"]
                },
                handler=self._handle_create_message_template,
                tags=["message", "template", "communication"]
            ),

            # AGUI Communication Tools
            MCPTool(
                name="register_agent",
                description="Register an AGUI agent",
                input_schema={
                    "type": "object",
                    "properties": {
                        "agent_name": {"type": "string", "description": "Agent name"},
                        "agent_type": {"type": "string", "description": "Agent type"},
                        "capabilities": {"type": "array", "items": {"type": "string"}, "description": "Agent capabilities"},
                        "endpoint_url": {"type": "string", "description": "Agent endpoint URL"},
                        "metadata": {"type": "object", "description": "Agent metadata"}
                    },
                    "required": ["agent_name", "agent_type"]
                },
                handler=self._handle_register_agent,
                tags=["agent", "register", "agui"]
            ),
            MCPTool(
                name="send_agent_message",
                description="Send a message to an AGUI agent",
                input_schema={
                    "type": "object",
                    "properties": {
                        "sender_agent_id": {"type": "string", "description": "Sender agent ID"},
                        "recipient_agent_id": {"type": "string", "description": "Recipient agent ID"},
                        "message_type": {"type": "string", "description": "Message type"},
                        "content": {"type": "string", "description": "Message content"},
                        "payload": {"type": "object", "description": "Message payload"},
                        "priority": {"type": "string", "description": "Message priority"},
                        "metadata": {"type": "object", "description": "Message metadata"}
                    },
                    "required": ["recipient_agent_id", "content"]
                },
                handler=self._handle_send_agent_message,
                tags=["agent", "message", "agui"]
            ),
            MCPTool(
                name="broadcast_to_agents",
                description="Broadcast a message to multiple agents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "sender_agent_id": {"type": "string", "description": "Sender agent ID"},
                        "message_type": {"type": "string", "description": "Message type"},
                        "content": {"type": "string", "description": "Message content"},
                        "target_agents": {"type": "array", "items": {"type": "string"}, "description": "Target agent IDs"},
                        "target_capabilities": {"type": "array", "items": {"type": "string"}, "description": "Target capabilities"},
                        "payload": {"type": "object", "description": "Message payload"},
                        "priority": {"type": "string", "description": "Message priority"},
                        "metadata": {"type": "object", "description": "Message metadata"}
                    },
                    "required": ["content"]
                },
                handler=self._handle_broadcast_to_agents,
                tags=["agent", "broadcast", "agui"]
            ),
            MCPTool(
                name="find_agents_by_capability",
                description="Find agents with a specific capability",
                input_schema={
                    "type": "object",
                    "properties": {
                        "capability": {"type": "string", "description": "Capability to search for"}
                    },
                    "required": ["capability"]
                },
                handler=self._handle_find_agents_by_capability,
                tags=["agent", "find", "agui"]
            ),

            # Notification Tools
            MCPTool(
                name="create_notification",
                description="Create a notification",
                input_schema={
                    "type": "object",
                    "properties": {
                        "notification_type": {"type": "string", "description": "Type of notification (info, warning, error, success, alert, reminder)"},
                        "title": {"type": "string", "description": "Notification title"},
                        "message": {"type": "string", "description": "Notification message"},
                        "recipients": {"type": "array", "items": {"type": "string"}, "description": "Notification recipients"},
                        "priority": {"type": "string", "description": "Notification priority"},
                        "channels": {"type": "array", "items": {"type": "string"}, "description": "Delivery channels"},
                        "scheduled_at": {"type": "string", "description": "Scheduled delivery time"},
                        "expires_at": {"type": "string", "description": "Notification expiration time"},
                        "metadata": {"type": "object", "description": "Notification metadata"},
                        "template_id": {"type": "string", "description": "Notification template ID"},
                        "action_url": {"type": "string", "description": "Action URL"},
                        "action_text": {"type": "string", "description": "Action button text"}
                    },
                    "required": ["title", "message", "recipients"]
                },
                handler=self._handle_create_notification,
                tags=["notification", "create", "alert"]
            ),
            MCPTool(
                name="get_user_notifications",
                description="Get notifications for a specific user",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User ID"},
                        "filters": {"type": "object", "description": "Notification filters"},
                        "limit": {"type": "integer", "description": "Maximum number of notifications to return"},
                        "offset": {"type": "integer", "description": "Number of notifications to skip"}
                    },
                    "required": ["user_id"]
                },
                handler=self._handle_get_user_notifications,
                tags=["notification", "get", "user"]
            ),
            MCPTool(
                name="mark_notification_read",
                description="Mark a notification as read",
                input_schema={
                    "type": "object",
                    "properties": {
                        "notification_id": {"type": "string", "description": "Notification ID"}
                    },
                    "required": ["notification_id"]
                },
                handler=self._handle_mark_notification_read,
                tags=["notification", "read", "user"]
            ),
            MCPTool(
                name="set_user_preferences",
                description="Set notification preferences for a user",
                input_schema={
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string", "description": "User ID"},
                        "preferences": {"type": "object", "description": "User preferences"}
                    },
                    "required": ["user_id", "preferences"]
                },
                handler=self._handle_set_user_preferences,
                tags=["notification", "preferences", "user"]
            ),

            # Service Management Tools
            MCPTool(
                name="get_service_health",
                description="Get comprehensive health status of the Post Office Service",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_service_health,
                tags=["service", "health", "status"]
            ),
            MCPTool(
                name="get_service_metrics",
                description="Get service metrics and statistics",
                input_schema={
                    "type": "object",
                    "properties": {}
                },
                handler=self._handle_get_service_metrics,
                tags=["service", "metrics", "statistics"]
            )
        ]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute an MCP tool."""
        try:
            self.logger.info(f"🔧 Executing tool: {tool_name}")

            # Event Routing Tools
            if tool_name == "publish_event":
                return await self.post_office_service.publish_event(arguments, user_context)
            elif tool_name == "subscribe_to_events":
                return await self.post_office_service.subscribe_to_events(arguments, user_context)
            elif tool_name == "get_events":
                return await self.post_office_service.get_events(arguments.get("filters"), user_context)
            elif tool_name == "correlate_events":
                return await self.post_office_service.correlate_events(arguments, user_context)

            # Messaging Tools
            elif tool_name == "send_message":
                return await self.post_office_service.send_message(arguments, user_context)
            elif tool_name == "get_message_status":
                return await self.post_office_service.get_message_status(arguments["message_id"], user_context)
            elif tool_name == "create_message_template":
                return await self.post_office_service.create_message_template(arguments, user_context)

            # AGUI Communication Tools
            elif tool_name == "register_agent":
                return await self.post_office_service.register_agent(arguments, user_context)
            elif tool_name == "send_agent_message":
                return await self.post_office_service.send_agent_message(arguments, user_context)
            elif tool_name == "broadcast_to_agents":
                return await self.post_office_service.broadcast_to_agents(arguments, user_context)
            elif tool_name == "find_agents_by_capability":
                return await self.post_office_service.find_agents_by_capability(arguments["capability"], user_context)

            # Notification Tools
            elif tool_name == "create_notification":
                return await self.post_office_service.create_notification(arguments, user_context)
            elif tool_name == "get_user_notifications":
                return await self.post_office_service.get_user_notifications(
                    arguments["user_id"], 
                    arguments.get("filters"), 
                    user_context
                )
            elif tool_name == "mark_notification_read":
                return await self.post_office_service.mark_notification_read(arguments["notification_id"], user_context)
            elif tool_name == "set_user_preferences":
                return await self.post_office_service.set_user_preferences(
                    arguments["user_id"], 
                    arguments["preferences"], 
                    user_context
                )

            # Service Management Tools
            elif tool_name == "get_service_health":
                return await self.post_office_service.get_health_status()
            elif tool_name == "get_service_metrics":
                return await self.post_office_service.get_metrics()

            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": [tool.name for tool in await self.get_tools()]
                }

        except Exception as e:
            self.logger.error(f"❌ Failed to execute tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }

    # ============================================================================
    # TOOL HANDLERS
    # ============================================================================

    async def _handle_publish_event(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle publish_event tool."""
        return await self.post_office_service.publish_event(arguments, user_context)

    async def _handle_send_message(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle send_message tool."""
        return await self.post_office_service.send_message(arguments, user_context)

    async def _handle_create_notification(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_notification tool."""
        return await self.post_office_service.create_notification(arguments, user_context)

    async def _handle_register_agent(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle register_agent tool."""
        return await self.post_office_service.register_agent(arguments, user_context)

    async def _handle_get_service_health(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_service_health tool."""
        return await self.post_office_service.get_health_status()

    async def _handle_get_service_metrics(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_service_metrics tool."""
        return await self.post_office_service.get_metrics()

    # Additional handler methods for remaining tools
    async def _handle_subscribe_to_events(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle subscribe_to_events tool."""
        return await self.post_office_service.subscribe_to_events(arguments, user_context)

    async def _handle_get_events(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_events tool."""
        return await self.post_office_service.get_events(arguments.get("filters"), user_context)

    async def _handle_correlate_events(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle correlate_events tool."""
        return await self.post_office_service.correlate_events(arguments, user_context)

    async def _handle_get_message_status(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_message_status tool."""
        return await self.post_office_service.get_message_status(arguments["message_id"], user_context)

    async def _handle_create_message_template(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle create_message_template tool."""
        return await self.post_office_service.create_message_template(arguments, user_context)

    async def _handle_send_agent_message(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle send_agent_message tool."""
        return await self.post_office_service.send_agent_message(arguments, user_context)

    async def _handle_broadcast_to_agents(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle broadcast_to_agents tool."""
        return await self.post_office_service.broadcast_to_agents(arguments, user_context)

    async def _handle_find_agents_by_capability(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle find_agents_by_capability tool."""
        return await self.post_office_service.find_agents_by_capability(arguments["capability"], user_context)

    async def _handle_get_user_notifications(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle get_user_notifications tool."""
        return await self.post_office_service.get_user_notifications(
            arguments["user_id"], 
            arguments.get("filters"), 
            user_context
        )

    async def _handle_mark_notification_read(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle mark_notification_read tool."""
        return await self.post_office_service.mark_notification_read(arguments["notification_id"], user_context)

    async def _handle_set_user_preferences(self, arguments: Dict[str, Any], user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Handle set_user_preferences tool."""
        return await self.post_office_service.set_user_preferences(
            arguments["user_id"], 
            arguments["preferences"], 
            user_context
        )

    async def cleanup(self):
        """Cleanup MCP server resources."""
        try:
            await self.post_office_service.cleanup()
            await super().cleanup()
            self.logger.info("✅ Post Office MCP Server cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup Post Office MCP Server: {e}")
