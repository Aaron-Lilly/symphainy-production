#!/usr/bin/env python3
"""
Base Class Mixins

Focused mixins for base class functionality - extracts valuable patterns
from base classes into reusable, testable components.

WHAT (Mixin Role): I provide focused, reusable functionality patterns
HOW (Mixin Implementation): I centralize specific responsibilities with clear interfaces
"""

from .utility_access_mixin import UtilityAccessMixin
from .infrastructure_access_mixin import InfrastructureAccessMixin
from .security_mixin import SecurityMixin
from .performance_monitoring_mixin import PerformanceMonitoringMixin
from .platform_capabilities_mixin import PlatformCapabilitiesMixin
from .micro_module_support_mixin import MicroModuleSupportMixin
from .communication_mixin import CommunicationMixin

__all__ = [
    # Mixins
    "UtilityAccessMixin",
    "InfrastructureAccessMixin", 
    "SecurityMixin",
    "PerformanceMonitoringMixin",
    "PlatformCapabilitiesMixin",
    "MicroModuleSupportMixin",
    "CommunicationMixin",
]

