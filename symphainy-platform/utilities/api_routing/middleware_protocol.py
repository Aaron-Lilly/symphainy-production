#!/usr/bin/env python3
"""
API Routing Middleware Protocol

Protocol definition for API routing middleware to avoid circular imports.

WHAT (Utility Role): I provide the middleware protocol definition
HOW (Utility Implementation): I define the interface that all middleware must implement
"""

from typing import Callable, Protocol, TYPE_CHECKING
from utilities import UserContext

# Avoid circular import
if TYPE_CHECKING:
    from .api_routing_utility import RequestContext, ResponseContext
else:
    # Forward references for runtime
    RequestContext = 'RequestContext'
    ResponseContext = 'ResponseContext'


class Middleware(Protocol):
    """Protocol for API middleware."""
    
    async def __call__(
        self, 
        request_context: 'RequestContext', 
        user_context: UserContext,
        next_handler: Callable
    ) -> 'ResponseContext':
        """Process request through middleware."""
        ...


