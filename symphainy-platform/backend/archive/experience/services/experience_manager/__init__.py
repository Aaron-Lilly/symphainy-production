#!/usr/bin/env python3
"""
Experience Manager Role

Experience Manager role following Smart City architectural patterns.

WHAT (Experience Dimension Role): I orchestrate user experience and manage UI state
HOW (Smart City Role): I use micro-modules, MCP server, and service for experience management
"""

from .experience_manager_service import ExperienceManagerService
# Temporarily disabled MCP server import due to missing dependencies
# from .mcp_server.experience_manager_mcp_server import experience_manager_mcp_server

__all__ = [
    "ExperienceManagerService",
    # "experience_manager_mcp_server"  # Temporarily disabled
]


