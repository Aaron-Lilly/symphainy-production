#!/usr/bin/env python3
"""
SOP Parsing Adapter

Lightweight infrastructure adapter for SOP parsing capabilities.
Wraps specific SOP parsing libraries and provides consistent interface.

WHAT (Infrastructure Adapter Role): I provide lightweight SOP parsing infrastructure
HOW (Infrastructure Adapter Implementation): I wrap specific SOP parsing libraries
"""

import re
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class SOPParsingAdapter:
    """
    Lightweight infrastructure adapter for SOP parsing.
    
    Wraps specific SOP parsing libraries and provides consistent interface
    for SOP text extraction, normalization, and structure analysis.
    """
    
    def __init__(self, **kwargs):
        """Initialize SOP parsing adapter."""
        self.logger = logging.getLogger("SOPParsingAdapter")
        self.logger.info("✅ SOP Parsing Adapter initialized")
    
    async def extract_sop_structure(self, text: str) -> Dict[str, Any]:
        """
        Extract SOP structure from text.
        
        Args:
            text: SOP text content
            
        Returns:
            Dict with extracted SOP structure
        """
        try:
            # Extract steps using regex patterns
            steps = self._extract_steps(text)
            
            # Extract title and description
            title = self._extract_title(text)
            description = self._extract_description(text)
            
            return {
                "success": True,
                "title": title,
                "description": description,
                "steps": steps,
                "step_count": len(steps),
                "extracted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"SOP structure extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_at": datetime.utcnow().isoformat()
            }
    
    async def normalize_sop_steps(self, steps: List[str]) -> List[Dict[str, Any]]:
        """
        Normalize SOP steps for consistent structure.
        
        Args:
            steps: List of raw step strings
            
        Returns:
            List of normalized step dictionaries
        """
        try:
            normalized_steps = []
            
            for i, step in enumerate(steps):
                normalized_step = {
                    "step_id": f"step_{i+1}",
                    "description": step.strip(),
                    "order": i + 1,
                    "normalized": True
                }
                normalized_steps.append(normalized_step)
            
            return normalized_steps
            
        except Exception as e:
            self.logger.error(f"SOP step normalization failed: {e}")
            return []
    
    async def validate_sop_structure(self, sop_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate SOP structure.
        
        Args:
            sop_data: SOP data to validate
            
        Returns:
            Dict with validation results
        """
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check required fields
            if not sop_data.get("title"):
                validation_result["errors"].append("Title is required")
                validation_result["valid"] = False
            
            if not sop_data.get("steps"):
                validation_result["errors"].append("Steps are required")
                validation_result["valid"] = False
            
            # Check step structure
            steps = sop_data.get("steps", [])
            if len(steps) < 1:
                validation_result["warnings"].append("SOP should have at least one step")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"SOP validation failed: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def _extract_steps(self, text: str) -> List[str]:
        """Extract steps from SOP text using regex patterns."""
        try:
            # Common step patterns
            step_patterns = [
                r'^\d+\.\s+(.+)$',  # 1. Step description
                r'^Step\s+\d+:\s+(.+)$',  # Step 1: Description
                r'^\d+\)\s+(.+)$',  # 1) Step description
                r'^-\s+(.+)$',  # - Step description
                r'^\*\s+(.+)$'  # * Step description
            ]
            
            steps = []
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                for pattern in step_patterns:
                    match = re.match(pattern, line, re.IGNORECASE)
                    if match:
                        steps.append(match.group(1).strip())
                        break
            
            return steps
            
        except Exception as e:
            self.logger.error(f"Step extraction failed: {e}")
            return []
    
    def _extract_title(self, text: str) -> str:
        """Extract title from SOP text."""
        try:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 5 and len(line) < 100:
                    # Simple heuristic: first substantial line is likely the title
                    return line
            return "Untitled SOP"
            
        except Exception as e:
            self.logger.error(f"Title extraction failed: {e}")
            return "Untitled SOP"
    
    def _extract_description(self, text: str) -> str:
        """Extract description from SOP text."""
        try:
            lines = text.split('\n')
            description_lines = []
            
            for line in lines:
                line = line.strip()
                if line and not re.match(r'^\d+\.', line):  # Not a step
                    description_lines.append(line)
                    if len(description_lines) >= 3:  # Limit description length
                        break
            
            return ' '.join(description_lines) if description_lines else "No description available"
            
        except Exception as e:
            self.logger.error(f"Description extraction failed: {e}")
            return "No description available"
    
    async def health_check(self) -> Dict[str, Any]:
        """Check adapter health."""
        try:
            return {
                "healthy": True,
                "adapter": "SOPParsingAdapter",
                "capabilities": [
                    "extract_sop_structure",
                    "normalize_sop_steps", 
                    "validate_sop_structure"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


