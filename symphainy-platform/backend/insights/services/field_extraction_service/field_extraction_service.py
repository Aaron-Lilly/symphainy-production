#!/usr/bin/env python3
"""
Field Extraction Service - Insights Realm

WHAT: Extracts structured fields from unstructured documents
HOW: Uses LLM + regex patterns to extract fields with citations

Use cases:
- License PDF → Extract expiration date, regulations, etc.
- Contract PDF → Extract parties, dates, terms
- Policy PDF → Extract coverage, limits, etc.
"""

import os
import sys
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase


class FieldExtractionService(RealmServiceBase):
    """
    Field Extraction Service - Extracts structured fields from unstructured documents.
    
    Provides field extraction capabilities using:
    - LLM for intelligent field extraction
    - Regex patterns for validation and fallback
    - Citation tracking for extracted values
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Field Extraction Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Smart City service APIs (will be initialized in initialize())
        self.data_steward = None
        self.librarian = None
        self.nurse = None
        
        # LLM service (for field extraction)
        self.llm_composition = None
    
    async def initialize(self) -> bool:
        """Initialize Field Extraction Service."""
        await super().initialize()
        
        try:
            self.logger.info("🚀 Initializing Field Extraction Service...")
            
            # Get Smart City services
            self.data_steward = await self.get_smart_city_service("DataStewardService")
            self.librarian = await self.get_smart_city_service("LibrarianService")
            self.nurse = await self.get_smart_city_service("NurseService")
            
            # Get LLM Composition Service (for field extraction)
            self.llm_composition = await self.get_business_abstraction("llm_composition")
            
            self.logger.info("✅ Field Extraction Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Field Extraction Service: {e}")
            await self.handle_error_with_audit(e, "initialize")
            return False
    
    async def extract_fields(
        self,
        file_id: str,
        extraction_schema: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract fields from file based on extraction schema.
        
        Args:
            file_id: File identifier
            extraction_schema: {
                "fields": [
                    {
                        "field_name": "license_expiration_date",
                        "field_type": "date",
                        "description": "Date when license expires",
                        "patterns": ["expires", "expiration", "valid until"],
                        "required": True
                    },
                    ...
                ]
            }
            user_context: Optional user context
        
        Returns:
        {
            "success": bool,
            "extracted_fields": {
                "license_expiration_date": {
                    "value": "2025-12-31",
                    "citation": "Page 2, Section 3",
                    "confidence": 0.92,
                    "source_text": "..."
                },
                ...
            },
            "unmatched_fields": [...]
        }
        """
        try:
            await self.log_operation_with_telemetry("extract_fields_start", success=True, metadata={"file_id": file_id})
            
            # Step 1: Get file content
            if not self.data_steward:
                self.data_steward = await self.get_smart_city_service("DataStewardService")
            
            if not self.data_steward:
                return {
                    "success": False,
                    "error": "Content Steward service not available"
                }
            
            # Get parsed file (should already be parsed)
            parsed_file = await self.data_steward.get_parsed_file(file_id)
            if not parsed_file:
                return {
                    "success": False,
                    "error": f"Parsed file not found: {file_id}. File must be parsed first."
                }
            
            # Get text content from parsed file
            text_content = parsed_file.get("parsed_content") or parsed_file.get("text_content") or ""
            if not text_content:
                return {
                    "success": False,
                    "error": "No text content found in parsed file"
                }
            
            # Step 2: Extract fields using LLM + regex
            fields = extraction_schema.get("fields", [])
            extracted_fields = {}
            unmatched_fields = []
            
            for field_def in fields:
                field_name = field_def.get("field_name")
                field_type = field_def.get("field_type", "string")
                description = field_def.get("description", "")
                patterns = field_def.get("patterns", [])
                required = field_def.get("required", False)
                
                # Try LLM extraction first
                llm_result = await self._extract_field_with_llm(
                    text_content, field_name, field_type, description, patterns
                )
                
                if llm_result.get("success"):
                    extracted_fields[field_name] = llm_result.get("field_data")
                else:
                    # Fallback to regex patterns
                    regex_result = await self._extract_field_with_regex(
                        text_content, field_name, field_type, patterns
                    )
                    
                    if regex_result.get("success"):
                        extracted_fields[field_name] = regex_result.get("field_data")
                    else:
                        if required:
                            unmatched_fields.append({
                                "field_name": field_name,
                                "reason": "Required field not found",
                                "patterns_tried": patterns
                            })
            
            await self.log_operation_with_telemetry("extract_fields_complete", success=True, details={
                "file_id": file_id,
                "fields_extracted": len(extracted_fields),
                "unmatched_fields": len(unmatched_fields)
            })
            
            return {
                "success": True,
                "extracted_fields": extracted_fields,
                "unmatched_fields": unmatched_fields,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Field extraction failed: {e}")
            await self.handle_error_with_audit(e, "extract_fields")
            await self.log_operation_with_telemetry("extract_fields_complete", success=False, details={"error": str(e)})
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _extract_field_with_llm(
        self,
        text_content: str,
        field_name: str,
        field_type: str,
        description: str,
        patterns: List[str]
    ) -> Dict[str, Any]:
        """Extract field using LLM."""
        try:
            if not self.llm_composition:
                return {"success": False, "error": "LLM service not available"}
            
            # Build prompt for field extraction
            prompt = f"""Extract the following field from the document:

Field Name: {field_name}
Field Type: {field_type}
Description: {description}
Search Patterns: {', '.join(patterns) if patterns else 'None'}

Document Text:
{text_content[:5000]}  # Limit to first 5000 chars for LLM

Please extract the value for this field and provide:
1. The extracted value
2. The location in the document (page number, section, or approximate location)
3. The source text that contains this value
4. Your confidence level (0.0 to 1.0)

Return your response as JSON:
{{
    "value": "...",
    "location": "...",
    "source_text": "...",
    "confidence": 0.0
}}
"""
            
            # Call LLM
            llm_response = await self.llm_composition.generate_text(
                prompt=prompt,
                max_tokens=500,
                temperature=0.1  # Low temperature for deterministic extraction
            )
            
            # Parse LLM response
            import json
            try:
                # Try to extract JSON from response
                response_text = llm_response.get("text", "") if isinstance(llm_response, dict) else str(llm_response)
                
                # Look for JSON in response
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    field_data = json.loads(json_match.group())
                    
                    return {
                        "success": True,
                        "field_data": {
                            "value": field_data.get("value"),
                            "citation": field_data.get("location", "Unknown location"),
                            "confidence": float(field_data.get("confidence", 0.5)),
                            "source_text": field_data.get("source_text", ""),
                            "extraction_method": "llm"
                        }
                    }
                else:
                    # Fallback: try to extract value directly
                    return {
                        "success": False,
                        "error": "Could not parse LLM response"
                    }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "LLM response is not valid JSON"
                }
            
        except Exception as e:
            self.logger.warning(f"⚠️ LLM field extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _extract_field_with_regex(
        self,
        text_content: str,
        field_name: str,
        field_type: str,
        patterns: List[str]
    ) -> Dict[str, Any]:
        """Extract field using regex patterns."""
        try:
            if not patterns:
                return {"success": False, "error": "No patterns provided"}
            
            # Try each pattern
            for pattern in patterns:
                # Build regex pattern (case-insensitive)
                regex_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
                matches = regex_pattern.finditer(text_content)
                
                for match in matches:
                    # Extract value from match
                    value = match.group(0) if match.group(0) else match.group(1) if match.groups() else None
                    
                    if value:
                        # Try to find context around the match
                        start = max(0, match.start() - 100)
                        end = min(len(text_content), match.end() + 100)
                        context = text_content[start:end]
                        
                        # Estimate location (simple: line number)
                        line_number = text_content[:match.start()].count('\n') + 1
                        
                        return {
                            "success": True,
                            "field_data": {
                                "value": value.strip(),
                                "citation": f"Line {line_number}",
                                "confidence": 0.7,  # Lower confidence for regex
                                "source_text": context.strip(),
                                "extraction_method": "regex"
                            }
                        }
            
            return {"success": False, "error": "No matches found"}
            
        except Exception as e:
            self.logger.warning(f"⚠️ Regex field extraction failed: {e}")
            return {"success": False, "error": str(e)}













