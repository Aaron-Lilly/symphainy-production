#!/usr/bin/env python3
"""
Service Registration Protocol - Abstraction Contract

Generic service registration interface with no technology dependencies.
This is Layer 2 of the 5-layer architecture for Curator Foundation.

WHAT (Infrastructure Role): I define service registration contracts
HOW (Infrastructure Implementation): I use protocols with no technology dependencies
"""

from typing import Protocol, Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class ServiceRegistration:
    """Service registration data structure - no technology dependencies."""
    service_id: str
    service_name: str
    service_type: str
    address: str
    port: int
    tags: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.utcnow)
    health_status: str = "unknown"
    endpoints: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class ServiceHealth:
    """Service health data structure - no technology dependencies."""
    service_id: str
    service_name: str
    health_status: str
    last_check: datetime
    checks: List[Dict[str, Any]] = field(default_factory=list)
    uptime_seconds: Optional[int] = None

@dataclass(frozen=True)
class ServiceDiscovery:
    """Service discovery data structure - no technology dependencies."""
    service_name: str
    total_instances: int
    healthy_instances: int
    unhealthy_instances: int
    instances: List[ServiceRegistration] = field(default_factory=list)

class ServiceRegistrationProtocol(Protocol):
    """Generic service registration protocol - no technology dependencies."""

    async def register_service(self, service_info: Dict[str, Any]) -> Optional[ServiceRegistration]: ...
    async def discover_service(self, service_name: str) -> List[ServiceRegistration]: ...
    async def update_service(self, service_name: str, service_id: str, updates: Dict[str, Any]) -> bool: ...
    async def deregister_service(self, service_name: str, service_id: Optional[str] = None) -> bool: ...
    async def get_service_health(self, service_name: str) -> ServiceHealth: ...
    async def get_all_services(self) -> Dict[str, List[ServiceRegistration]]: ...
    async def get_healthy_services(self, service_name: str) -> List[ServiceRegistration]: ...
    async def get_service_instances(self, service_name: str) -> ServiceDiscovery: ...



