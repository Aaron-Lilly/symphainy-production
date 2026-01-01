#!/usr/bin/env python3
"""
Structured Parsing Module - File Parser Service

Handles structured data parsing (Excel, CSV, JSON, Binary + Copybook).
PRESERVES all existing binary + copybook support.
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime


class StructuredParsing:
    """Handles structured data parsing."""
    
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
        Parse structured file (Excel, CSV, JSON, Binary + Copybook).
        
        PRESERVES binary + copybook support:
        - Copybook provided in parse_options["copybook"] or parse_options["copybook_path"]
        - Uses MainframeProcessingAbstraction for binary files
        - FileParsingRequest includes options with copybook
        
        Args:
            file_data: File data as bytes
            file_type: File extension (e.g., "xlsx", "csv", "bin")
            filename: Original filename
            parse_options: Optional parsing options (includes copybook for binary files)
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Parsed result dictionary with structured data
        """
        try:
            # Start telemetry tracking
            await self.service.log_operation_with_telemetry("structured_parse_start", success=True, metadata={
                "file_type": file_type,
                "filename": filename
            })
            
            # 1. Get abstraction name for file type
            abstraction_name = self.service.utilities_module.get_abstraction_name_for_file_type(file_type)
            
            if not abstraction_name:
                error_msg = f"Unsupported structured file type: {file_type or 'unknown'}"
                self.service.logger.warning(f"⚠️ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "structured_parse")
                await self.service.record_health_metric("structured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "unsupported_file_type"
                })
                await self.service.log_operation_with_telemetry("structured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "unsupported_file_type",
                    "parsing_type": "structured"
                }
            
            # 2. Get abstraction via Platform Gateway
            try:
                file_parser = self.service.platform_gateway.get_abstraction(
                    realm_name=self.service.realm_name,
                    abstraction_name=abstraction_name
                )
            except Exception as e:
                error_msg = f"Failed to get abstraction '{abstraction_name}': {e}"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "structured_parse")
                await self.service.record_health_metric("structured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "abstraction_not_available"
                })
                await self.service.log_operation_with_telemetry("structured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "abstraction_not_available",
                    "parsing_type": "structured"
                }
            
            if not file_parser:
                error_msg = f"Abstraction '{abstraction_name}' is None"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "structured_parse")
                await self.service.record_health_metric("structured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "abstraction_is_none"
                })
                await self.service.log_operation_with_telemetry("structured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "abstraction_is_none",
                    "parsing_type": "structured"
                }
            
            # 3. Create FileParsingRequest (PRESERVES copybook support)
            from foundations.public_works_foundation.abstraction_contracts.file_parsing_protocol import FileParsingRequest
            
            # Log copybook presence for binary files (debugging)
            if parse_options and file_type in ["bin", "binary"]:
                has_copybook = "copybook" in parse_options or "copybook_path" in parse_options
                if has_copybook:
                    copybook_length = len(str(parse_options.get("copybook", "")))
                    self.service.logger.info(f"📋 Binary file with copybook: copybook_length={copybook_length}")
                else:
                    self.service.logger.warning(f"⚠️ Binary file without copybook - may fail parsing")
            
            request = FileParsingRequest(
                file_data=file_data,
                filename=filename,
                options=parse_options  # ✅ PRESERVES copybook for binary files
            )
            
            # 4. Parse file via abstraction (with timeout)
            # For binary files with many fields (OCCURS expansion), parsing can take longer
            # Increased timeout to 300 seconds (5 minutes) to handle large copybooks
            timeout_seconds = 300.0 if file_type in ["bin", "binary"] else 60.0
            try:
                result = await asyncio.wait_for(
                    file_parser.parse_file(request),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                error_msg = f"Structured file parsing timed out after {timeout_seconds} seconds for {file_type} file"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "structured_parse")
                await self.service.record_health_metric("structured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "file_parsing_timeout"
                })
                await self.service.log_operation_with_telemetry("structured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "file_parsing_timeout",
                    "parsing_type": "structured"
                }
            
            if not result.success:
                error_msg = result.error or "Unknown error during structured file parsing"
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "structured_parse")
                await self.service.record_health_metric("structured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "file_parsing_failed"
                })
                await self.service.log_operation_with_telemetry("structured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": f"Structured file parsing failed: {error_msg}",
                    "file_type": file_type,
                    "error": error_msg,
                    "parsing_type": "structured"
                }
            
            # 5. Convert FileParsingResult to structured format
            # PRESERVES all existing data structures
            metadata = result.metadata or {}
            
            parsed_result = {
                "success": True,
                "parsing_type": "structured",  # ✅ NEW: Explicit parsing type
                "file_type": file_type,
                "data": result.structured_data if result.structured_data else {},  # ✅ Structured data
                "content": result.text_content,  # ✅ Text content (for compatibility)
                "text_content": result.text_content,
                "structure": {
                    "chunks": 0,  # Chunking is separate (not part of parsing)
                    "entities": 0,  # Entity extraction is separate (not part of parsing)
                    "page_count": result.metadata.get("page_count", 1),
                    "table_count": result.metadata.get("table_count", 0) if result.structured_data else 0
                },
                "metadata": metadata,
                "tables": result.structured_data.get("tables", []) if result.structured_data else [],
                "records": result.structured_data.get("records", []) if result.structured_data else [],
                "parsed_at": result.timestamp or datetime.utcnow().isoformat()
            }
            
            # Extract validation_rules from metadata if present (from MainframeProcessingAdapter for binary files)
            # validation_rules contains 88-level fields and level-01 metadata records
            if "validation_rules" in metadata:
                parsed_result["validation_rules"] = metadata["validation_rules"]
            
            # Record health metric (success)
            await self.service.record_health_metric("structured_files_parsed", 1.0, {
                "file_type": file_type,
                "chunks": parsed_result["structure"]["chunks"],
                "entities": parsed_result["structure"]["entities"],
                "table_count": parsed_result["structure"]["table_count"],
                "success": True
            })
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "structured_parse_complete",
                success=True,
                details={
                    "file_type": file_type,
                    "chunks": parsed_result["structure"]["chunks"],
                    "entities": parsed_result["structure"]["entities"],
                    "table_count": parsed_result["structure"]["table_count"]
                }
            )
            
            self.service.logger.info(f"✅ Structured file parsed successfully: {file_type} (abstraction: {abstraction_name})")
            
            return parsed_result
            
        except Exception as e:
            # Use enhanced error handling with audit
            self.service.logger.error(f"❌ Structured parsing failed: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self.service.handle_error_with_audit(e, "structured_parse")
            await self.service.record_health_metric("structured_files_parsed", 0.0, {
                "file_type": file_type,
                "success": False,
                "error": str(e)
            })
            await self.service.log_operation_with_telemetry("structured_parse_complete", success=False, details={
                "file_type": file_type,
                "error": str(e)
            })
            return {
                "success": False,
                "message": f"Structured parsing exception: {e}",
                "file_type": file_type,
                "error": str(e),
                "parsing_type": "structured"
            }



