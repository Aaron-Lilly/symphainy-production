#!/usr/bin/env python3
"""
Startup Policy Enum

Defines startup policies for services in the platform.
Used to determine when services should be initialized (eager, lazy, or ephemeral).
"""

from enum import Enum


class StartupPolicy(Enum):
    """
    Startup policy for services.
    
    Determines when a service should be initialized:
    - EAGER: Always start during platform boot (foundations, Smart City Gateway)
    - LAZY: Start on first use (managers, orchestrators, realm services)
    - EPHEMERAL: Start, serve, then dissolve (future: serverless capabilities)
    """
    EAGER = "eager"           # Always start during platform boot
    LAZY = "lazy"             # Start on first use (lazy initialization)
    EPHEMERAL = "ephemeral"   # Start, serve, then dissolve (future: serverless)






