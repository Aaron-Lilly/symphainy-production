#!/usr/bin/env python3
"""
SOP Processing Abstraction

Infrastructure abstraction for SOP processing capabilities.
Implements SOPProcessingProtocol using SOPParsingAdapter.

WHAT (Infrastructure Abstraction Role): I provide unified SOP processing infrastructure
HOW (Infrastructure Abstraction Implementation): I coordinate SOP parsing adapters
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..abstraction_contracts.sop_processing_protocol import (
    SOPProcessingProtocol, SOPStructure, SOPValidationResult
)
from ..infrastructure_adapters.sop_parsing_adapter import SOPParsingAdapter

class SOPProcessingAbstraction(SOPProcessingProtocol):
    """SOP processing abstraction using SOP parsing adapter."""
    
    def __init__(self, sop_parsing_adapter: SOPParsingAdapter, di_container=None, **kwargs):
        """
        Initialize SOP processing abstraction.
        
        Args:
            sop_parsing_adapter: SOP parsing adapter instance
            di_container: Dependency injection container
        """
        self.sop_parsing_adapter = sop_parsing_adapter
        self.di_container = di_container
        self.service_name = "sop_processing_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Initialize abstraction
        self._initialize_abstraction()
    
    def _initialize_abstraction(self):
        """Initialize the SOP processing abstraction."""
        try:
            self.logger.info("✅ SOP Processing Abstraction initialized")
            
        except Exception as e:
            # Sync method - just use logger (error_handler is async)
            self.logger.error(f"❌ Failed to initialize SOP processing abstraction: {e}")
    
            raise  # Re-raise for service layer to handle

        """
        Extract SOP structure from text.
        
        Args:
            text: SOP text content
            
        Returns:
            Dict with extracted SOP structure
        """
    async def extract_sop_structure(self, text: str) -> Dict[str, Any]:
        """Extract SOP structure from text."""
        try:
            # Use adapter to extract SOP structure
            result = await self.sop_parsing_adapter.extract_sop_structure(text)
            
            if result.get("success"):
                # Create SOP structure object
                sop_structure = SOPStructure(
                    title=result.get("title", ""),
                    description=result.get("description", ""),
                    steps=result.get("steps", []),
                    version="1.0",
                    metadata={
                        "extracted_at": datetime.utcnow().isoformat(),
                        "step_count": result.get("step_count", 0),
                        "source": "text_parsing"
                    }
                )
                
                extraction_result = {
                    "success": True,
                    "sop_structure": sop_structure,
                    "extracted_at": datetime.utcnow().isoformat()
                }
                
                return extraction_result
            else:
                return {
                    "success": False,
                    "error": result.get("error", "SOP structure extraction failed"),
                    "extracted_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ SOP structure extraction failed: {e}")
            raise  # Re-raise for service layer to handle

        """
        Normalize SOP steps for consistent structure.
        
        Args:
            steps: List of raw step strings
            
        Returns:
            List of normalized step dictionaries
        """
    async def normalize_sop_steps(self, steps: List[str]) -> List[Dict[str, Any]]:
        """Normalize SOP steps for consistent structure."""
        try:
            # Use adapter to normalize steps
            normalized_steps = await self.sop_parsing_adapter.normalize_sop_steps(steps)
            
            return normalized_steps
            
        except Exception as e:
            self.logger.error(f"❌ SOP step normalization failed: {e}")
            raise  # Re-raise for service layer to handle

    async def validate_sop_structure(self, sop_data: Dict[str, Any]) -> SOPValidationResult:
        """
        Validate SOP structure.
        
        Args:
            sop_data: SOP data to validate
            
        Returns:
            SOPValidationResult with validation results
        """
        try:
            # Use adapter to validate SOP structure
            validation_result = await self.sop_parsing_adapter.validate_sop_structure(sop_data)
            
            validation_result_obj = SOPValidationResult(
                valid=validation_result.get("valid", False),
                errors=validation_result.get("errors", []),
                warnings=validation_result.get("warnings", []),
                validation_timestamp=datetime.utcnow()
            )
            
            return validation_result_obj
            
        except Exception as e:
            self.logger.error(f"❌ SOP validation failed: {e}")
            raise  # Re-raise for service layer to handle

    async def enhance_sop_content(self, sop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance SOP content with additional information.
        
        Args:
            sop_data: SOP data to enhance
            
        Returns:
            Dict with enhanced SOP data
        """
        try:
            # Add enhancement logic here
            enhanced_data = sop_data.copy()
            
            # Add metadata
            enhanced_data["enhanced_at"] = datetime.utcnow().isoformat()
            enhanced_data["enhancement_version"] = "1.0"
            
            # Add step numbering
            steps = enhanced_data.get("steps", [])
            for i, step in enumerate(steps):
                if isinstance(step, dict):
                    step["step_number"] = i + 1
                else:
                    steps[i] = {
                        "step_number": i + 1,
                        "description": step
                    }
            
            enhanced_data["steps"] = steps
            
            enhancement_result = {
                "success": True,
                "enhanced_sop_data": enhanced_data,
                "enhanced_at": datetime.utcnow().isoformat()
            }
            
            return enhancement_result
            
        except Exception as e:
            self.logger.error(f"❌ SOP content enhancement failed: {e}")
            raise  # Re-raise for service layer to handle

    async def get_sop_metadata(self, sop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get SOP metadata information.
        
        Args:
            sop_data: SOP data to analyze
            
        Returns:
            Dict with SOP metadata
        """
        try:
            # Extract metadata from SOP data
            metadata = {
                "title": sop_data.get("title", ""),
                "description": sop_data.get("description", ""),
                "step_count": len(sop_data.get("steps", [])),
                "version": sop_data.get("version", "1.0"),
                "created_at": sop_data.get("created_at", datetime.utcnow().isoformat()),
                "metadata": sop_data.get("metadata", {}),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            metadata_result = {
                "success": True,
                "metadata": metadata,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            
            return metadata_result
            
        except Exception as e:
            self.logger.error(f"❌ SOP metadata extraction failed: {e}")
            raise  # Re-raise for service layer to handle

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.
        
        Returns:
            Dict: Health check result
        """
        try:
            # Get adapter health
            adapter_health = await self.sop_parsing_adapter.health_check()
            
            health_status = {
                "healthy": adapter_health.get("healthy", False),
                "adapter": adapter_health,
                "abstraction": {
                    "name": "SOPProcessingAbstraction",
                    "status": "active"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")

            raise  # Re-raise for service layer to handle
