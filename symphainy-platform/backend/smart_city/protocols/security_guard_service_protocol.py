#!/usr/bin/env python3
"""
Security Guard Service Protocol

Realm-specific protocol for Security Guard services.
Inherits standard methods from ServiceProtocol.

WHAT (Security Guard Role): I orchestrate authentication, authorization, and zero-trust security
HOW (Security Guard Protocol): I provide security communication gateway and policy enforcement
"""

from typing import Protocol, Dict, Any
from bases.protocols.service_protocol import ServiceProtocol


class SecurityGuardServiceProtocol(ServiceProtocol, Protocol):
    """
    Protocol for Security Guard services.
    Inherits standard methods from ServiceProtocol.
    """
    
    # Authentication Methods
    async def authenticate_user(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user credentials."""
        ...
    
    # Authorization Methods
    async def authorize_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Authorize user action on resource."""
        ...
    
    # Security Orchestration
    async def orchestrate_security_communication(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate security communication gateway."""
        ...
    
    async def orchestrate_zero_trust_policy(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate zero-trust policy enforcement."""
        ...
    
    async def orchestrate_tenant_isolation(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate tenant isolation and multi-tenancy."""
        ...
