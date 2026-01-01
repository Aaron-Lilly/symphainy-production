#!/usr/bin/env python3
"""
Frontend Integration Role

Frontend Integration role following Smart City architectural patterns.

WHAT (Experience Dimension Role): I manage frontend-backend integration and API communication
HOW (Smart City Role): I use micro-modules, MCP server, and service for integration
"""

from .frontend_integration_service import FrontendIntegrationService, create_frontend_integration_service

# Create service instance (will be properly initialized with DI when used)
frontend_integration_service = None  # Will be created with proper DI

__all__ = [
    "FrontendIntegrationService",
    "create_frontend_integration_service",
    "frontend_integration_service"
]


