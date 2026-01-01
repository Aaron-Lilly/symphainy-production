#!/usr/bin/env python3
"""
Platform Gateway Foundation

Provides platform-wide governance and access control for realm-specific infrastructure abstractions.

WHAT (Platform Gateway Foundation Role): I provide governance and access control for all realms
HOW (Platform Gateway Foundation Implementation): I enforce realm-specific abstraction access policies
"""

from .platform_gateway_foundation_service import PlatformGatewayFoundationService

__all__ = ["PlatformGatewayFoundationService"]








