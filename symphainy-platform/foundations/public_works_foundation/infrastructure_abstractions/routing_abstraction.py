#!/usr/bin/env python3
"""
Routing Abstraction - Layer 2 of 5-Layer Architecture

This abstraction provides a protocol for routing operations, abstracting away
the specific implementation (Traefik, nginx, etc.).

WHAT (Infrastructure Role): I provide routing capabilities to all Smart City roles
HOW (Infrastructure Implementation): I abstract routing operations from specific implementations
WHY: To enable swap-ability between routing solutions (Traefik, nginx, Istio, etc.)
"""

from typing import Protocol, Dict, Any, Optional, List
from abc import ABC, abstractmethod


class RoutingAbstraction(Protocol):
    """
    Routing Abstraction Protocol.
    
    Defines the contract for routing operations, enabling swap-ability
    between different routing implementations (Traefik, nginx, etc.).
    """
    
    async def discover_routes(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover routes from the routing infrastructure.
        
        Args:
            service_name: Optional service name to filter routes
            
        Returns:
            List of route dictionaries with service, router, and rule information
        """
        ...
    
    async def get_service_routes(self, service_name: str) -> List[Dict[str, Any]]:
        """
        Get all routes for a specific service.
        
        Args:
            service_name: Service name to get routes for
            
        Returns:
            List of route dictionaries for the service
        """
        ...
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """
        Get health status for a service via routing infrastructure.
        
        Args:
            service_name: Service name to check health for
            
        Returns:
            Dictionary with health status information
        """
        ...
    
    async def get_dashboard_info(self) -> Dict[str, Any]:
        """
        Get routing infrastructure dashboard information.
        
        Returns:
            Dictionary with dashboard URL and version information
        """
        ...


class TraefikRoutingAbstraction:
    """
    Traefik Routing Abstraction Implementation.
    
    Implements RoutingAbstraction protocol using TraefikAdapter.
    This is the concrete implementation that other services will use.
    """
    
    def __init__(self, traefik_adapter):
        """Initialize Traefik Routing Abstraction with Traefik adapter."""
        self.traefik_adapter = traefik_adapter
    
    async def discover_routes(self, service_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discover routes from Traefik."""
        return await self.traefik_adapter.discover_routes(service_name)
    
    async def get_service_routes(self, service_name: str) -> List[Dict[str, Any]]:
        """Get all routes for a specific service from Traefik."""
        return await self.traefik_adapter.get_service_routes(service_name)
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status for a service via Traefik."""
        return await self.traefik_adapter.get_service_health(service_name)
    
    async def get_dashboard_info(self) -> Dict[str, Any]:
        """Get Traefik dashboard information."""
        return await self.traefik_adapter.get_dashboard_info()


