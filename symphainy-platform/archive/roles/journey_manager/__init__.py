#!/usr/bin/env python3
"""
Journey Manager Role

Journey Manager role following Smart City architectural patterns.

WHAT (Experience Dimension Role): I manage user journeys and optimize user experience flows
HOW (Smart City Role): I use micro-modules, MCP server, and service for journey management
"""

from .journey_manager_service import journey_manager_service
# Temporarily disabled MCP server import due to missing dependencies
# from .mcp_server.journey_manager_mcp_server import journey_manager_mcp_server

__all__ = [
    "journey_manager_service",
    # "journey_manager_mcp_server"  # Temporarily disabled
]


