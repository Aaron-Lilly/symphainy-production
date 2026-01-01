#!/usr/bin/env python3
"""
Experience Protocols

Protocols that define the implementation standards for experience dimension capabilities.
Each protocol defines HOW experience dimension roles implement their capabilities.

WHAT (Experience): I define implementation standards for experience dimension capabilities
HOW (Protocols): I provide abstract base classes and standards for experience operations
"""

# from .experience_service_base import ExperienceServiceBase, ExperienceServiceType, ExperienceOperationType
from .experience_soa_service_protocol import ExperienceServiceProtocol

__all__ = [
    # "ExperienceServiceBase",
    # "ExperienceServiceType", 
    # "ExperienceOperationType",
    "ExperienceServiceProtocol"
]
























