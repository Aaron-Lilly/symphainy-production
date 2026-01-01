#!/usr/bin/env python3
"""
Content Steward Service Package

Content Steward Service using micro-modular architecture with aggregator pattern.
Implements client data processing with governance integration.

WHAT (Content Processing Role): I provide client data processing, policy enforcement, and metadata extraction
HOW (Content Processing Implementation): I use micro-modules with aggregator pattern
"""

from .content_steward_service import ContentStewardService

__all__ = ['ContentStewardService']

