#!/usr/bin/env python3
"""
Smart City Service Protocols

Realm-specific protocols for Smart City services.
All protocols inherit from ServiceProtocol for standard methods.

WHAT (Smart City Protocols): I define contracts for all Smart City services
HOW (Smart City Protocols): I provide service-specific methods with standard base methods
"""

from .post_office_service_protocol import PostOfficeServiceProtocol
from .security_guard_service_protocol import SecurityGuardServiceProtocol
from .conductor_service_protocol import ConductorServiceProtocol
from .traffic_cop_service_protocol import TrafficCopServiceProtocol
from .nurse_service_protocol import NurseServiceProtocol
from .librarian_service_protocol import LibrarianServiceProtocol

__all__ = [
    # Smart City Service Protocols
    "PostOfficeServiceProtocol",
    "SecurityGuardServiceProtocol",
    "ConductorServiceProtocol",
    "TrafficCopServiceProtocol",
    "NurseServiceProtocol",
    "LibrarianServiceProtocol",
]

