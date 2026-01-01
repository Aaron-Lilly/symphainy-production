#!/usr/bin/env python3
"""
Tool Storage Abstraction - Layer 2

Infrastructure abstraction coordinating the tool storage adapter with
simple validation and error handling.
"""

from typing import Dict, Any, List, Optional

from foundations.public_works_foundation.abstraction_contracts.tool_storage_protocol import (
    ToolStorageProtocol, ToolDefinition
)

class ToolStorageAbstraction(ToolStorageProtocol):
    """Abstraction over a ToolStorageProtocol adapter."""

    def __init__(self, storage_adapter: ToolStorageProtocol, service_name: str = "tool_storage_abstraction", di_container=None):
        if not di_container:
            raise ValueError("DI Container is required for ToolStorageAbstraction initialization")
        
        self.storage_adapter = storage_adapter
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"ToolStorageAbstraction-{service_name}")
        self.logger.info("✅ ToolStorageAbstraction initialized")

    async def save_tool(self, tool: ToolDefinition) -> bool:
        try:
            if not tool or not tool.name:
                raise ValueError("Tool must have a name")
            
            result = await self.storage_adapter.save_tool(tool)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save tool: {e}")
            raise

            raise  # Re-raise for service layer to handle
    async def get_tool(self, name: str, version: Optional[str] = None) -> Optional[ToolDefinition]:
        try:
            if not name:
                raise ValueError("Tool name is required")
            
            result = await self.storage_adapter.get_tool(name, version)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get tool {name}: {e}")
            raise

            raise  # Re-raise for service layer to handle
    async def delete_tool(self, name: str, version: Optional[str] = None) -> bool:
        try:
            if not name:
                raise ValueError("Tool name is required")
            
            result = await self.storage_adapter.delete_tool(name, version)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete tool {name}: {e}")
            raise

            raise  # Re-raise for service layer to handle
    async def list_tools(self, filters: Optional[Dict[str, Any]] = None) -> List[ToolDefinition]:
        try:
            result = await self.storage_adapter.list_tools(filters)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list tools: {e}")
            raise

            raise  # Re-raise for service layer to handle
    async def upsert_tools(self, tools: List[ToolDefinition]) -> int:
        try:
            result = await self.storage_adapter.upsert_tools(tools)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to upsert tools: {e}")
            raise

            raise  # Re-raise for service layer to handle