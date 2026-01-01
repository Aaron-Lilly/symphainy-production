#!/usr/bin/env python3
"""
MCP Tool Definition

Data structures and classes for MCP tool definitions and execution results.

WHAT (Micro-Module Role): I provide data structures for MCP tool definitions
HOW (Micro-Module Implementation): I define dataclasses for tool definitions and execution results
"""

from typing import Dict, Any, List, Callable
from datetime import datetime
from dataclasses import dataclass


@dataclass
class MCPToolDefinition:
    """MCP tool definition for registration."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable
    tags: List[str] = None
    requires_tenant: bool = True
    tenant_scope: str = "user"
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class MCPExecutionResult:
    """Result of MCP tool execution."""
    success: bool
    result: Any = None
    error: str = None
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }




























