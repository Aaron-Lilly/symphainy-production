#!/usr/bin/env python3
"""
AGUI Communication Protocol

Protocol definition for AGUI communication infrastructure abstractions.
"""

from typing import Protocol, Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
import uuid


@dataclass
class AGUIMessage:
    """AGUI message definition."""
    message_id: str
    action: str
    payload: Dict[str, Any]
    timestamp: datetime
    connection_id: str


@dataclass
class AGUIResponse:
    """AGUI response definition."""
    response_id: str
    message_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class AGUIEvent:
    """AGUI event definition."""
    event_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime
    connection_id: str


class AGUICommunicationProtocol(Protocol):
    """Protocol for AGUI communication infrastructure abstractions."""
    
    async def send_message(self, connection_id: str, message: AGUIMessage) -> bool:
        """Send AGUI message."""
        ...
    
    async def broadcast_message(self, message: AGUIMessage, 
                              exclude_connections: List[str] = None) -> int:
        """Broadcast AGUI message."""
        ...
    
    async def send_event(self, connection_id: str, event: AGUIEvent) -> bool:
        """Send AGUI event."""
        ...
    
    async def broadcast_event(self, event: AGUIEvent, 
                            exclude_connections: List[str] = None) -> int:
        """Broadcast AGUI event."""
        ...
    
    def register_message_handler(self, action: str, handler: Callable):
        """Register message handler."""
        ...
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler."""
        ...
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        ...




