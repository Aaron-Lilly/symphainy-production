#!/usr/bin/env python3
"""
Delivery Manager Interface

Defines the contract for the Delivery Manager, which provides cross-realm coordination
between Business Enablement, Smart City, and Experience dimensions.

WHAT (Smart City Role): I coordinate across realms (Business Enablement ↔ Smart City ↔ Experience)
HOW (Interface): I define the contract for cross-realm coordination operations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from utilities import UserContext


class RealmType(str, Enum):
    """Supported realms for cross-realm coordination."""
    BUSINESS_ENABLEMENT = "business_enablement"
    SMART_CITY = "smart_city"
    EXPERIENCE = "experience"


class CoordinationType(str, Enum):
    """Types of cross-realm coordination."""
    SERVICE_DISCOVERY = "service_discovery"
    REQUEST_ROUTING = "request_routing"
    STATE_SYNCHRONIZATION = "state_synchronization"
    WORKFLOW_COORDINATION = "workflow_coordination"
    EVENT_PROPAGATION = "event_propagation"


class IDeliveryManager(ABC):
    """
    Delivery Manager Interface
    
    Defines the contract for the Delivery Manager, which provides cross-realm coordination
    between Business Enablement, Smart City, and Experience dimensions.
    """
    
    @abstractmethod
    async def coordinate_cross_realm(self, coordination_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Coordinate activities across multiple realms.
        
        Args:
            coordination_data: Data for cross-realm coordination
            user_context: User context for authorization
            
        Returns:
            Dict with coordination results
        """
        pass
    
    @abstractmethod
    async def route_to_realm(self, target_realm: RealmType, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Route a request to a specific realm.
        
        Args:
            target_realm: Target realm for routing
            request_data: Request data to route
            user_context: User context for authorization
            
        Returns:
            Dict with routing results
        """
        pass
    
    @abstractmethod
    async def discover_realm_services(self, realm: RealmType, user_context: UserContext) -> Dict[str, Any]:
        """
        Discover available services in a specific realm.
        
        Args:
            realm: Target realm to discover services in
            user_context: User context for authorization
            
        Returns:
            Dict with discovered services
        """
        pass
    
    @abstractmethod
    async def manage_cross_realm_state(self, state_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Manage state across multiple realms.
        
        Args:
            state_data: State data to manage
            user_context: User context for authorization
            
        Returns:
            Dict with state management results
        """
        pass
    
    @abstractmethod
    async def get_cross_realm_health(self) -> Dict[str, Any]:
        """
        Get health status across all realms.
        
        Returns:
            Dict with cross-realm health status
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Get health status of the Delivery Manager.
        
        Returns:
            Dict with health status information
        """
        pass


