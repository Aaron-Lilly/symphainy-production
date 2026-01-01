#!/usr/bin/env python3
"""
SOP Enhancement Adapter

Lightweight infrastructure adapter for SOP content enhancement capabilities.
Wraps basic text processing and structure improvement functionality.

WHAT (Infrastructure Adapter Role): I provide lightweight SOP enhancement infrastructure
HOW (Infrastructure Adapter Implementation): I wrap text processing libraries for SOP improvement
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


class SOPEnhancementAdapter:
    """
    Lightweight infrastructure adapter for SOP enhancement.
    
    Provides basic SOP content enhancement using text processing libraries.
    """
    
    def __init__(self):
        """Initialize SOP enhancement adapter."""
        self.logger = logging.getLogger("SOPEnhancementAdapter")
        self.logger.info("✅ SOP Enhancement Adapter initialized")
    
    async def enhance_sop_content(self, sop_text: str) -> Dict[str, Any]:
        """
        Enhance SOP content with better structure and clarity.
        
        Args:
            sop_text: Original SOP text content
            
        Returns:
            Dict with enhanced SOP content
        """
        try:
            if not sop_text or not sop_text.strip():
                return {
                    "success": False,
                    "error": "Empty SOP text provided",
                    "enhanced_content": None
                }
            
            # Apply text enhancements
            enhanced_text = self._apply_text_enhancements(sop_text)
            
            # Extract and improve structure
            structure_improvements = self._analyze_structure_improvements(sop_text)
            
            # Generate enhancement metadata
            enhancement_metadata = {
                "original_length": len(sop_text),
                "enhanced_length": len(enhanced_text),
                "improvements_applied": structure_improvements,
                "enhanced_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "enhanced_content": enhanced_text,
                "metadata": enhancement_metadata
            }
            
        except Exception as e:
            self.logger.error(f"SOP content enhancement failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "enhanced_content": None
            }
    
    def _apply_text_enhancements(self, text: str) -> str:
        """Apply text enhancements to improve clarity and structure."""
        try:
            enhanced_text = text
            
            # Fix common formatting issues
            enhanced_text = re.sub(r'\n\s*\n\s*\n', '\n\n', enhanced_text)  # Remove excessive line breaks
            enhanced_text = re.sub(r'^\s+', '', enhanced_text, flags=re.MULTILINE)  # Remove leading whitespace
            enhanced_text = re.sub(r'\s+$', '', enhanced_text, flags=re.MULTILINE)  # Remove trailing whitespace
            
            # Improve step formatting
            enhanced_text = self._improve_step_formatting(enhanced_text)
            
            # Add structure improvements
            enhanced_text = self._add_structure_improvements(enhanced_text)
            
            return enhanced_text
            
        except Exception as e:
            self.logger.error(f"Text enhancement failed: {e}")
            return text
    
    def _improve_step_formatting(self, text: str) -> str:
        """Improve step formatting for better readability."""
        try:
            # Find numbered steps and improve formatting
            step_pattern = r'(\d+\.?\s*)([^\n]+)'
            def format_step(match):
                number = match.group(1).strip()
                content = match.group(2).strip()
                return f"{number} {content}"
            
            enhanced_text = re.sub(step_pattern, format_step, text)
            return enhanced_text
            
        except Exception as e:
            self.logger.error(f"Step formatting failed: {e}")
            return text
    
    def _add_structure_improvements(self, text: str) -> str:
        """Add structure improvements to SOP content."""
        try:
            # Add section headers if missing
            if not re.search(r'^#+\s+', text, re.MULTILINE):
                # Add basic structure
                structured_text = f"# Standard Operating Procedure\n\n{text}\n\n## Summary\nThis procedure outlines the steps for [process description]."
                return structured_text
            
            return text
            
        except Exception as e:
            self.logger.error(f"Structure improvement failed: {e}")
            return text
    
    def _analyze_structure_improvements(self, text: str) -> List[str]:
        """Analyze what structure improvements were applied."""
        try:
            improvements = []
            
            # Check for common issues and improvements
            if re.search(r'\n\s*\n\s*\n', text):
                improvements.append("Removed excessive line breaks")
            
            if not re.search(r'^\d+\.', text, re.MULTILINE):
                improvements.append("Improved step numbering")
            
            if not re.search(r'^#+\s+', text, re.MULTILINE):
                improvements.append("Added section headers")
            
            return improvements
            
        except Exception as e:
            self.logger.error(f"Structure analysis failed: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for SOP enhancement adapter."""
        try:
            # Test basic functionality
            test_result = await self.enhance_sop_content("Test SOP content")
            
            return {
                "healthy": test_result.get("success", False),
                "adapter": "SOPEnhancementAdapter",
                "capabilities": [
                    "text_enhancement",
                    "structure_improvement",
                    "formatting_optimization"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


