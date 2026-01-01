#!/usr/bin/env python3
"""
Conductor Service Protocol

Realm-specific protocol for Conductor services.
Inherits standard methods from ServiceProtocol.

WHAT (Conductor Role): I orchestrate workflows, tasks, and real-time communication
HOW (Conductor Protocol): I provide workflow orchestration and WebSocket management
"""

from typing import Protocol, Dict, Any
from bases.protocols.service_protocol import ServiceProtocol


class ConductorServiceProtocol(ServiceProtocol, Protocol):
    """
    Protocol for Conductor services.
    Inherits standard methods from ServiceProtocol.
    """
    
    # Workflow Management
    async def create_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create new workflow."""
        ...
    
    async def execute_workflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with parameters."""
        ...
    
    async def get_workflow_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get workflow execution status."""
        ...
    
    # Real-time Communication
    async def orchestrate_websocket_connection(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate WebSocket connection management."""
        ...
    
    async def orchestrate_real_time_task(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate real-time task execution."""
        ...
    
    async def orchestrate_streaming_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate streaming data processing."""
        ...

