#!/usr/bin/env python3
"""Utilities module for Embedding Service."""

from typing import Dict, Any, Optional


class Utilities:
    """Utility functions for Embedding Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger


