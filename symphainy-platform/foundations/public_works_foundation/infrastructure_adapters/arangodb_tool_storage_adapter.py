#!/usr/bin/env python3
"""
ArangoDB Tool Storage Adapter - Layer 1 (in-memory fallback)

Raw storage operations for tools. Uses in-memory dict for now to avoid config deps.
Swap later for real ArangoDB driver.
"""

from typing import Dict, Any, List, Optional

from foundations.public_works_foundation.abstraction_contracts.tool_storage_protocol import (
    ToolStorageProtocol, ToolDefinition
)


class ArangoDBToolStorageAdapter(ToolStorageProtocol):
    """In-memory implementation of tool storage adapter (ArangoDB-ready)."""

    def __init__(self, service_name: str = "arangodb_tool_storage_adapter", di_container=None):
        if not di_container:
            raise ValueError("DI Container is required for ArangoDBToolStorageAdapter initialization")
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(f"ArangoDBToolStorageAdapter-{service_name}")
        self._tools: Dict[str, Dict[str, ToolDefinition]] = {}
        self.logger.info("✅ ArangoDBToolStorageAdapter (in-memory) initialized")

    async def save_tool(self, tool: ToolDefinition) -> bool:
        versions = self._tools.setdefault(tool.name, {})
        versions[tool.version] = tool
        return True

    async def get_tool(self, name: str, version: Optional[str] = None) -> Optional[ToolDefinition]:
        versions = self._tools.get(name)
        if not versions:
            return None
        if version and version in versions:
            return versions[version]
        # return latest by string compare (simple fallback)
        latest_version = sorted(versions.keys())[-1]
        return versions[latest_version]

    async def delete_tool(self, name: str, version: Optional[str] = None) -> bool:
        if name not in self._tools:
            return False
        if version:
            return self._tools[name].pop(version, None) is not None
        del self._tools[name]
        return True

    async def list_tools(self, filters: Optional[Dict[str, Any]] = None) -> List[ToolDefinition]:
        results: List[ToolDefinition] = []
        for versions in self._tools.values():
            results.extend(versions.values())
        if not filters:
            return results
        def matches(tool: ToolDefinition) -> bool:
            for key, value in filters.items():
                tool_value = getattr(tool, key, None)
                if key == "tags" and isinstance(value, list) and isinstance(tool_value, list):
                    # For tags, check if any filter tag is in tool's tags
                    if not any(tag in tool_value for tag in value):
                        return False
                elif tool_value != value:
                    return False
            return True
        return [t for t in results if matches(t)]

    async def upsert_tools(self, tools: List[ToolDefinition]) -> int:
        count = 0
        for tool in tools:
            await self.save_tool(tool)
            count += 1
        return count


