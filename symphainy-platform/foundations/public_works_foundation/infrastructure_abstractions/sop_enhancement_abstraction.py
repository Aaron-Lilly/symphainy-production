#!/usr/bin/env python3
"""
SOP Enhancement Abstraction

Infrastructure abstraction for SOP content enhancement capabilities.
Implements SOPEnhancementProtocol using SOPEnhancementAdapter.

WHAT (Infrastructure Abstraction Role): I provide unified SOP enhancement infrastructure
HOW (Infrastructure Abstraction Implementation): I coordinate SOP enhancement adapters
"""

from typing import Dict, Any
import logging

from ..abstraction_contracts.sop_enhancement_protocol import SOPEnhancementProtocol, EnhancementResult
from ..infrastructure_adapters.sop_enhancement_adapter import SOPEnhancementAdapter

class SOPEnhancementAbstraction(SOPEnhancementProtocol):
    """SOP enhancement abstraction using SOP enhancement adapter."""
    
    def __init__(self, sop_enhancement_adapter: SOPEnhancementAdapter, di_container=None, **kwargs):
        """
        Initialize SOP enhancement abstraction.
        
        Args:
            sop_enhancement_adapter: SOP enhancement adapter instance
            di_container: Dependency injection container
        """
        self.sop_enhancement_adapter = sop_enhancement_adapter
        self.di_container = di_container
        self.service_name = "sop_enhancement_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ SOP Enhancement Abstraction initialized")
    
    async def initialize(self):
        """Initialize the SOP enhancement abstraction."""
        try:
            self.logger.info("Initializing SOP enhancement abstraction...")
            # Adapter is already initialized
            self.logger.info("✅ SOP Enhancement Abstraction initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize SOP enhancement abstraction: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def enhance_sop_content(self, sop_text: str) -> EnhancementResult:
        """
        Enhance SOP content with better structure and clarity.
        
        Args:
            sop_text: Original SOP text content
            
        Returns:
            EnhancementResult with enhanced content and metadata
        """
        try:
            # Use adapter to enhance SOP content
            result = await self.sop_enhancement_adapter.enhance_sop_content(sop_text)
            
            if result.get("success"):
                enhancement_result = EnhancementResult(
                    success=True,
                    enhanced_content=result.get("enhanced_content", ""),
                    metadata=result.get("metadata", {}),
                    error=None
                )
                
                return enhancement_result
            else:
                return EnhancementResult(
                    success=False,
                    enhanced_content="",
                    metadata={},
                    error=result.get("error", "SOP enhancement failed")
                )
                
        except Exception as e:
            self.logger.error(f"❌ SOP content enhancement failed: {e}")
            raise  # Re-raise for service layer to handle
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the SOP enhancement abstraction."""
        try:
            # Check adapter health
            adapter_health = await self.sop_enhancement_adapter.health_check()
            
            health_status = {
                "healthy": adapter_health.get("healthy", False),
                "abstraction": "SOPEnhancementAbstraction",
                "adapter_health": adapter_health,
                "capabilities": [
                    "content_enhancement",
                    "structure_improvement",
                    "formatting_optimization"
                ]
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

            raise  # Re-raise for service layer to handle
