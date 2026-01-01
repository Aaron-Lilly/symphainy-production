#!/usr/bin/env python3
"""
Bases Module

Centralized location for cross-dimensional base classes used throughout the Symphainy Platform.
This provides a clean, intuitive location for foundational base classes that serve multiple dimensions.

Cross-Dimensional Base Classes:
- FoundationServiceBase: Base for all foundation services (outside main dimensions)
- ManagerServiceBase: Base for cross-dimensional manager services
- MCPServerBase: Base for cross-dimensional MCP servers
- SmartCityRoleBase: Base for Smart City roles with direct foundation access
- RealmServiceBase: Base for realm services with API access via Smart City Gateway

New Simplified Base Classes:
- SmartCityRoleBase: Direct foundation access (Public Works, Communication, Curator)
- RealmServiceBase: API access via Smart City Gateway (clean separation)
- RealmContext: Unified dependency injection for realm services
"""

from .foundation_service_base import FoundationServiceBase
from .mcp_server import MCPServerBase, MCPToolDefinition, MCPExecutionResult
from .smart_city_role_base import SmartCityRoleBase
from .realm_service_base import RealmServiceBase
from .orchestrator_base import OrchestratorBase
from .startup_policy import StartupPolicy

__all__ = [
    "FoundationServiceBase",
    "MCPServerBase",
    "MCPToolDefinition",
    "MCPExecutionResult",
    "SmartCityRoleBase",
    "RealmServiceBase",
    "OrchestratorBase",
    "StartupPolicy"
]









