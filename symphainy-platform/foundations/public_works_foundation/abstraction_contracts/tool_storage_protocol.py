#!/usr/bin/env python3
"""
Tool Storage Protocol - Abstraction Contract (Layer 0)

Defines the contract for storing and retrieving tool definitions.
Enables swappable storage backends (ArangoDB, Redis, Postgres, in-memory).

WHAT (Infrastructure Role): I define storage contracts for tools
HOW (Protocol): I use abstract methods and data classes without tech deps
"""

from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ToolDefinition:
    """Tool definition stored in the registry storage layer."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    realm: Optional[str] = None
    pillar: Optional[str] = None
    owner_agent: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ToolStorageProtocol(Protocol):
    """Protocol for tool storage backends."""

    async def save_tool(self, tool: ToolDefinition) -> bool:
        ...

    async def get_tool(self, name: str, version: Optional[str] = None) -> Optional[ToolDefinition]:
        ...

    async def delete_tool(self, name: str, version: Optional[str] = None) -> bool:
        ...

    async def list_tools(self, filters: Optional[Dict[str, Any]] = None) -> List[ToolDefinition]:
        ...

    async def upsert_tools(self, tools: List[ToolDefinition]) -> int:
        ...




