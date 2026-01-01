#!/usr/bin/env python3
"""Initialization module for Semantic Enrichment Service."""

import os
from typing import Dict, Any, Optional


class Initialization:
    """Initialization module for Semantic Enrichment Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    async def initialize(self) -> bool:
        """
        Initialize Semantic Enrichment Service dependencies.
        
        Sets up:
        - Smart City service APIs (Librarian, Content Steward)
        - Nurse (for observability)
        - Curator registration (optional - this is a secure boundary service)
        """
        try:
            self.logger.info("🚀 Initializing Semantic Enrichment Service (secure boundary)...")
            
            # Get Smart City service APIs
            self.service.librarian = await self.service.get_librarian_api()
            self.service.content_steward = await self.service.get_content_steward_api()
            self.service.nurse = await self.service.get_nurse_api()
            
            # Log discovery results for debugging
            if not self.service.librarian:
                self.logger.warning("⚠️ Librarian API not discovered via Curator - metadata access may fail")
            else:
                self.logger.info(f"✅ Librarian API discovered: {type(self.service.librarian).__name__}")
            
            if not self.service.content_steward:
                self.logger.error("❌ Content Steward API not discovered - cannot access parsed files")
                return False
            else:
                self.logger.info(f"✅ Content Steward API discovered: {type(self.service.content_steward).__name__}")
            
            # Note: This service may not need Curator registration since it's called internally
            # by SemanticEnrichmentGateway, not directly by agents
            # But we can register it for service discovery if needed
            
            self.logger.info("✅ Semantic Enrichment Service initialized (secure boundary)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Semantic Enrichment Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False

