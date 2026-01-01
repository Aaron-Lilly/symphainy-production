#!/usr/bin/env python3
"""
SOP Parsing Module - File Parser Service

Handles SOP document parsing with structure extraction.
Extracts sections, steps, roles, and procedures from SOP documents.
"""

import asyncio
import re
from typing import Dict, Any, Optional, List
from datetime import datetime


class SOPParsing:
    """Handles SOP document parsing with structure extraction."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def parse(
        self,
        file_data: bytes,
        file_type: str,
        filename: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse SOP file into structured format.
        
        Extracts:
        - Title
        - Sections (with headings and content)
        - Steps/Procedures
        - Roles/Responsibilities
        - Dependencies
        - Timeline/Sequence
        
        Args:
            file_data: File data as bytes
            file_type: File extension (e.g., "docx", "pdf", "txt")
            filename: Original filename
            parse_options: Optional parsing options
            user_context: Optional user context
        
        Returns:
            Parsed result dictionary with structured SOP data
        """
        try:
            # Start telemetry tracking
            await self.service.log_operation_with_telemetry("sop_parse_start", success=True, metadata={
                "file_type": file_type,
                "filename": filename
            })
            
            # Step 1: Extract text using unstructured parsing approach
            # Get abstraction name for file type
            abstraction_name = self.service.utilities_module.get_abstraction_name_for_file_type(file_type)
            
            if not abstraction_name:
                error_msg = f"Unsupported SOP file type: {file_type or 'unknown'}"
                self.service.logger.warning(f"⚠️ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "sop_parse")
                await self.service.record_health_metric("sop_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "unsupported_file_type"
                })
                await self.service.log_operation_with_telemetry("sop_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "unsupported_file_type",
                    "parsing_type": "sop"
                }
            
            # Step 2: Get abstraction via Platform Gateway
            try:
                file_parser = self.service.platform_gateway.get_abstraction(
                    realm_name=self.service.realm_name,
                    abstraction_name=abstraction_name
                )
            except Exception as e:
                error_msg = f"Failed to get abstraction '{abstraction_name}': {e}"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "sop_parse")
                await self.service.record_health_metric("sop_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "abstraction_not_available"
                })
                await self.service.log_operation_with_telemetry("sop_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "abstraction_not_available",
                    "parsing_type": "sop"
                }
            
            if not file_parser:
                error_msg = f"Abstraction '{abstraction_name}' is None"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "sop_parse")
                await self.service.record_health_metric("sop_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "abstraction_is_none"
                })
                await self.service.log_operation_with_telemetry("sop_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "abstraction_is_none",
                    "parsing_type": "sop"
                }
            
            # Step 3: Create FileParsingRequest
            from foundations.public_works_foundation.abstraction_contracts.file_parsing_protocol import FileParsingRequest
            
            request = FileParsingRequest(
                file_data=file_data,
                filename=filename,
                options=parse_options
            )
            
            # Step 4: Parse file via abstraction (with timeout)
            try:
                result = await asyncio.wait_for(
                    file_parser.parse_file(request),
                    timeout=60.0  # 60 second timeout for file parsing
                )
            except asyncio.TimeoutError:
                error_msg = f"SOP file parsing timed out after 60 seconds for {file_type} file"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "sop_parse")
                await self.service.record_health_metric("sop_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "file_parsing_timeout"
                })
                await self.service.log_operation_with_telemetry("sop_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "file_parsing_timeout",
                    "parsing_type": "sop"
                }
            
            if not result.success:
                error_msg = result.error or "Unknown error during SOP file parsing"
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "sop_parse")
                await self.service.record_health_metric("sop_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "file_parsing_failed"
                })
                await self.service.log_operation_with_telemetry("sop_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": f"SOP file parsing failed: {error_msg}",
                    "file_type": file_type,
                    "error": error_msg,
                    "parsing_type": "sop"
                }
            
            # Step 5: Extract text content
            text_content = result.text_content or ""
            
            # Step 6: Extract SOP structure from text
            sop_structure = await self._extract_sop_structure(text_content, filename)
            
            # Step 7: Build parsed result
            parsed_result = {
                "success": True,
                "parsing_type": "sop",
                "file_type": file_type,
                "structure": sop_structure,
                "raw_content": text_content,
                "content": text_content,  # For compatibility
                "text_content": text_content,
                "metadata": {
                    "title": sop_structure.get("title", filename),
                    "section_count": len(sop_structure.get("sections", [])),
                    "step_count": sum(len(s.get("steps", [])) for s in sop_structure.get("sections", [])),
                    "role_count": len(sop_structure.get("roles", [])),
                    "page_count": result.metadata.get("page_count", 1),
                    "total_chars": len(text_content)
                },
                "parsed_at": result.timestamp or datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.service.record_health_metric("sop_files_parsed", 1.0, {
                "file_type": file_type,
                "section_count": len(sop_structure.get("sections", [])),
                "step_count": sum(len(s.get("steps", [])) for s in sop_structure.get("sections", [])),
                "success": True
            })
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "sop_parse_complete",
                success=True,
                details={
                    "file_type": file_type,
                    "section_count": len(sop_structure.get("sections", [])),
                    "step_count": sum(len(s.get("steps", [])) for s in sop_structure.get("sections", []))
                }
            )
            
            self.service.logger.info(f"✅ SOP file parsed successfully: {file_type} (sections: {len(sop_structure.get('sections', []))}, steps: {sum(len(s.get('steps', [])) for s in sop_structure.get('sections', []))})")
            
            return parsed_result
            
        except Exception as e:
            # Use enhanced error handling with audit
            self.service.logger.error(f"❌ SOP parsing failed: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self.service.handle_error_with_audit(e, "sop_parse")
            await self.service.record_health_metric("sop_files_parsed", 0.0, {
                "file_type": file_type,
                "success": False,
                "error": str(e)
            })
            await self.service.log_operation_with_telemetry("sop_parse_complete", success=False, details={
                "file_type": file_type,
                "error": str(e)
            })
            return {
                "success": False,
                "message": f"SOP parsing exception: {e}",
                "file_type": file_type,
                "error": str(e),
                "parsing_type": "sop"
            }
    
    async def _extract_sop_structure(self, text_content: str, filename: str) -> Dict[str, Any]:
        """
        Extract SOP structure from text content.
        
        Identifies:
        - Title (first line or heading)
        - Sections (marked by headings, numbered sections, etc.)
        - Steps (numbered or bulleted lists)
        - Roles (mentions of job titles, responsibilities)
        - Dependencies (references to other steps/sections)
        
        Args:
            text_content: Full text content of SOP
            filename: Original filename (used as fallback title)
        
        Returns:
            Dictionary with structured SOP data
        """
        structure = {
            "title": filename.replace(".docx", "").replace(".pdf", "").replace(".txt", "").replace(".md", ""),
            "sections": [],
            "roles": [],
            "dependencies": []
        }
        
        if not text_content:
            return structure
        
        # Extract title (first non-empty line or first heading)
        lines = text_content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) > 5 and len(line) < 200:
                # Check if it looks like a title (not all caps, not a list item)
                if not line.startswith(('-', '*', '•', '1.', '2.', '3.')) and not line.isupper():
                    structure["title"] = line
                    break
        
        # Extract sections (look for headings: all caps, numbered sections, bold patterns)
        current_section = None
        current_steps = []
        
        # Patterns for section headings
        section_patterns = [
            r'^(\d+\.?\s+[A-Z][^\n]+)$',  # Numbered sections: "1. Introduction"
            r'^([A-Z][A-Z\s]{3,})$',  # All caps headings: "INTRODUCTION"
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:?)$',  # Title case: "Introduction" or "Introduction:"
            r'^#{1,3}\s+(.+)$',  # Markdown headings: "# Section"
        ]
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line matches a section heading pattern
            is_section_heading = False
            section_title = None
            
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    is_section_heading = True
                    section_title = match.group(1) if match.groups() else line
                    # Clean up section title
                    section_title = section_title.strip().lstrip('#').strip()
                    break
            
            if is_section_heading:
                # Save previous section if exists
                if current_section:
                    current_section["steps"] = current_steps
                    structure["sections"].append(current_section)
                
                # Start new section
                current_section = {
                    "id": f"section_{len(structure['sections']) + 1}",
                    "heading": section_title,
                    "content": "",
                    "steps": []
                }
                current_steps = []
            else:
                # Check if line is a step (numbered or bulleted)
                step_match = re.match(r'^(\d+[\.\)]|\-|\*|\•)\s+(.+)$', line)
                if step_match:
                    step_text = step_match.group(2).strip()
                    step_num = step_match.group(1).strip()
                    
                    step = {
                        "id": f"step_{len(current_steps) + 1}",
                        "step_number": step_num,
                        "text": step_text,
                        "content": step_text
                    }
                    current_steps.append(step)
                    
                    # Extract roles from step text
                    role_patterns = [
                        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:will|shall|must|should|is responsible|manages|handles)\b',
                        r'\b(?:the|a|an)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:will|shall|must|should)\b',
                    ]
                    for role_pattern in role_patterns:
                        role_matches = re.findall(role_pattern, step_text, re.IGNORECASE)
                        for role in role_matches:
                            if role not in structure["roles"] and len(role.split()) <= 3:
                                structure["roles"].append(role)
                else:
                    # Regular content line
                    if current_section:
                        if current_section["content"]:
                            current_section["content"] += "\n" + line
                        else:
                            current_section["content"] = line
        
        # Save last section
        if current_section:
            current_section["steps"] = current_steps
            structure["sections"].append(current_section)
        
        # If no sections found, create a single section with all content
        if not structure["sections"]:
            structure["sections"] = [{
                "id": "section_1",
                "heading": "Content",
                "content": text_content,
                "steps": []
            }]
        
        return structure
