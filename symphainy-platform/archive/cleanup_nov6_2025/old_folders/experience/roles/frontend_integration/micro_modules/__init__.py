#!/usr/bin/env python3
"""
Frontend Integration Micro-Modules

Micro-modules for the Frontend Integration role following Smart City architectural patterns.
"""

from .api_router import APIRouterModule
from .request_transformer import RequestTransformerModule
from .response_transformer import ResponseTransformerModule
from .error_handler import ErrorHandlerModule
from .authentication_manager import AuthenticationManagerModule
from .session_coordinator import SessionCoordinatorModule
from .pillar_api_handlers import PillarAPIHandlers

__all__ = [
    "APIRouterModule",
    "RequestTransformerModule", 
    "ResponseTransformerModule",
    "ErrorHandlerModule",
    "AuthenticationManagerModule",
    "SessionCoordinatorModule",
    "PillarAPIHandlers"
]