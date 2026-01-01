#!/usr/bin/env python3
"""
Smart City Protocols Package

The Smart City protocols have been refactored to use the new protocol structure in bases/protocols/
that extends SmartCityRoleProtocol with role-specific capabilities.

NEW APPROACH:
- All Smart City roles now extend SmartCityRoleProtocol (in bases/protocols/)
- Role-specific protocols define capabilities in bases/protocols/
- Services implement protocols directly without inheritance

USE THESE PROTOCOLS:
- bases.protocols.smart_city_role_protocol: SmartCityRoleProtocol (base)
- bases.protocols.traffic_cop_protocol: TrafficCopProtocol
- bases.protocols.conductor_protocol: ConductorProtocol
- bases.protocols.security_guard_protocol: SecurityGuardProtocol
- bases.protocols.realm_service_protocol: RealmServiceProtocol

ARCHIVED:
- Old protocols have been moved to protocols/archived/
- These use ABC inheritance and are replaced by the new Protocol-based approach
"""

__all__ = []