#!/usr/bin/env python3
"""
File Parsing Module - File Parser Service

Refactored to use parsing orchestrator with parsing type determination.
Phase 1.1a: Structured parsing vertical slice - structured path only for now.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class FileParsing:
    """File parsing module for File Parser Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def parse_file(
        self,
        file_id: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse file into structured format (SOA API).
        
        NEW FLOW (Phase 1.1a):
        1. Retrieve file → Content Steward
        2. Detect file type
        3. Determine parsing type (structured/unstructured/hybrid/workflow/sop)
        4. Route to parsing orchestrator
        5. Return parsed result
        
        Args:
            file_id: File identifier
            parse_options: Optional parsing options
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Parsed result dictionary
        """
        try:
            # Start telemetry tracking
            await self.service.log_operation_with_telemetry("parse_file_start", success=True, metadata={"file_id": file_id})
            
            # 1. Retrieve file via Content Steward SOA API
            document = await self.service.file_retrieval_module.retrieve_document(file_id)
            if not document or document.get("success") is False:
                await self.service.record_health_metric("parse_file_file_not_found", 1.0, {"file_id": file_id})
                await self.service.log_operation_with_telemetry("parse_file_complete", success=False, details={"file_id": file_id, "error": "file_not_found"})
                error_msg = document.get("message") if document else "File not found"
                return {
                    "success": False,
                    "message": error_msg,
                    "file_id": file_id,
                    "error": document.get("error") if document else "FILE_NOT_FOUND"
                }
            
            # Get file data and filename
            # Content Steward returns file_content, but some sources might use "data"
            file_data = document.get("file_content") or document.get("data")
            if isinstance(file_data, str):
                file_data = file_data.encode('utf-8')
            elif not isinstance(file_data, bytes):
                file_data = bytes(file_data) if file_data else b""
            
            # Get filename from various possible fields
            filename = document.get("ui_name") or document.get("filename") or document.get("original_filename") or file_id
            
            # 2. Detect file type
            file_type = self.service.utilities_module.get_file_extension(filename)
            
            # If no extension, try to get from document metadata
            if not file_type:
                file_type = document.get("file_type") or ""
            
            # If still no file type, try to infer from content_type
            if not file_type:
                content_type = document.get("content_type") or ""
                if content_type:
                    content_type_lower = content_type.lower()
                    # Check for full MIME types
                    if "spreadsheetml" in content_type_lower or "excel" in content_type_lower:
                        file_type = "xlsx"
                    elif "wordprocessingml" in content_type_lower or "msword" in content_type_lower:
                        file_type = "docx"
                    elif "pdf" in content_type_lower:
                        file_type = "pdf"
                    elif "html" in content_type_lower:
                        file_type = "html"
                    elif "text" in content_type_lower:
                        file_type = "txt"
                    elif "csv" in content_type_lower:
                        file_type = "csv"
                    elif "json" in content_type_lower:
                        file_type = "json"
                    elif "image" in content_type_lower or "jpeg" in content_type_lower or "png" in content_type_lower:
                        file_type = "jpg"  # Default to jpg for images
                    # Also check for simple extensions
                    elif content_type_lower in ["xlsx", "xls"]:
                        file_type = "xlsx"
                    elif content_type_lower in ["docx", "doc"]:
                        file_type = "docx"
                    elif content_type_lower == "pdf":
                        file_type = "pdf"
                    elif content_type_lower in ["html", "htm"]:
                        file_type = "html"
                    elif content_type_lower in ["txt", "text"]:
                        file_type = "txt"
                    elif content_type_lower == "csv":
                        file_type = "csv"
                    elif content_type_lower == "json":
                        file_type = "json"
            
            # 3. Check document metadata for explicit parsing type (from upload)
            # If file was uploaded with workflow_sop content_type, use that to determine parsing type
            if not parse_options:
                parse_options = {}
            
            # Check document metadata for content_type and file_type_category
            document_content_type = document.get("content_type")
            document_file_type_category = document.get("file_type_category")
            document_parsing_type = document.get("parsing_type")  # Set during upload
            
            # If document has explicit parsing_type, use it
            if document_parsing_type and document_parsing_type in ["workflow", "sop"]:
                parse_options["parsing_type"] = document_parsing_type
                self.service.logger.info(f"📋 Using explicit parsing_type from document metadata: {document_parsing_type}")
            # If document has workflow_sop content_type, determine parsing type from file_type_category
            elif document_content_type == "workflow_sop":
                if document_file_type_category == "workflow":
                    parse_options["parsing_type"] = "workflow"
                    self.service.logger.info(f"📋 Determined parsing_type 'workflow' from content_type=workflow_sop, file_type_category=workflow")
                elif document_file_type_category == "sop":
                    parse_options["parsing_type"] = "sop"
                    self.service.logger.info(f"📋 Determined parsing_type 'sop' from content_type=workflow_sop, file_type_category=sop")
            
            # 4. Handle copybook_file_id if present - load copybook content
            # FileParserService owns all parsing concerns, including copybook retrieval
            if "copybook_file_id" in parse_options:
                copybook_file_id = parse_options.pop("copybook_file_id")
                try:
                    self.service.logger.info(f"📎 Loading copybook from file: {copybook_file_id}")
                    # Retrieve copybook file using same method as main file
                    copybook_doc = await self.service.file_retrieval_module.retrieve_document(copybook_file_id)
                    if copybook_doc:
                        # Extract copybook content from document
                        copybook_data = copybook_doc.get("file_content") or copybook_doc.get("data") or copybook_doc.get("content")
                        if isinstance(copybook_data, str):
                            copybook_data = copybook_data.encode('utf-8')
                        elif not isinstance(copybook_data, bytes):
                            copybook_data = bytes(copybook_data) if copybook_data else b""
                        
                        # Add copybook data to parse_options as 'copybook' (string content)
                        # MainframeProcessingAbstraction expects 'copybook' as string content
                        parse_options["copybook"] = copybook_data.decode('utf-8') if copybook_data else ""
                        self.service.logger.info(f"✅ Copybook loaded: {copybook_file_id} (length: {len(parse_options.get('copybook', ''))})")
                    else:
                        self.service.logger.warning(f"⚠️ Copybook file not found: {copybook_file_id}")
                        # Don't fail here - let the parsing abstraction handle missing copybook
                except Exception as e:
                    self.service.logger.warning(f"⚠️ Failed to retrieve copybook file {copybook_file_id}: {e}")
                    import traceback
                    self.service.logger.debug(f"Traceback: {traceback.format_exc()}")
                    # Don't fail here - let the parsing abstraction handle missing copybook
            
            # 5. Determine parsing type (NEW - Phase 1.1a)
            # Note: parse_options may already have parsing_type set from document metadata above
            parsing_type = self.service.utilities_module.get_parsing_type(
                file_type=file_type,
                parse_options=parse_options
            )
            
            self.service.logger.info(f"📋 Parsing type determined: {parsing_type} for file_type: {file_type}")
            
            # 6. Route to parsing orchestrator (NEW - Phase 1.1b)
            # Phase 3: Workflow and SOP parsing now implemented
            if parsing_type in ["structured", "unstructured", "hybrid", "workflow", "sop"]:
                parsing_result = await self.service.parsing_orchestrator_module.parse_by_type(
                    parsing_type=parsing_type,
                    file_data=file_data,
                    file_type=file_type,
                    filename=filename,
                    parse_options=parse_options,
                    user_context=user_context
                )
            else:
                error_msg = f"Unknown parsing type: {parsing_type}"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.record_health_metric("parse_file_unknown_type", 1.0, {
                    "file_id": file_id,
                    "parsing_type": parsing_type
                })
                await self.service.log_operation_with_telemetry("parse_file_complete", success=False, details={
                    "file_id": file_id,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_id": file_id,
                    "parsing_type": parsing_type,
                    "error": "unknown_parsing_type"
                }
            
            if not parsing_result.get("success"):
                return parsing_result
            
            # 5. Add file_id to result (for compatibility)
            parsing_result["file_id"] = file_id
            
            # Record health metric (success)
            await self.service.record_health_metric("files_parsed", 1.0, {
                "file_id": file_id,
                "file_type": file_type,
                "parsing_type": parsing_type,
                "success": True
            })
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "parse_file_complete",
                success=True,
                details={
                    "file_id": file_id,
                    "file_type": file_type,
                    "parsing_type": parsing_type
                }
            )
            
            self.service.logger.info(f"✅ File parsed successfully: {file_id} (type: {parsing_type})")
            
            return parsing_result
            
        except Exception as e:
            # Use enhanced error handling with audit
            self.service.logger.error(f"❌ File parsing failed: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self.service.handle_error_with_audit(e, "parse_file")
            await self.service.record_health_metric("files_parsed", 0.0, {
                "file_id": file_id,
                "success": False,
                "error": str(e)
            })
            await self.service.log_operation_with_telemetry("parse_file_complete", success=False, details={
                "file_id": file_id,
                "error": str(e)
            })
            return {
                "success": False,
                "message": f"File parsing exception: {e}",
                "file_id": file_id,
                "error": str(e)
            }
    
    async def detect_file_type(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """Detect file type from file ID or content (SOA API)."""
        try:
            document = await self.service.file_retrieval_module.retrieve_document(file_id)
            if not document:
                return "unknown"
            
            filename = document.get("ui_name") or document.get("filename") or document.get("original_filename") or file_id
            file_type = self.service.utilities_module.get_file_extension(filename)
            
            if not file_type:
                file_type = document.get("file_type") or "unknown"
            
            return file_type
            
        except Exception as e:
            self.service.logger.error(f"❌ File type detection failed: {e}")
            return "unknown"
    
    async def extract_content(self, file_id: str) -> Dict[str, Any]:
        """Extract plain text content from file (SOA API)."""
        try:
            parse_result = await self.parse_file(file_id)
            if parse_result.get("success"):
                return {
                    "success": True,
                    "content": parse_result.get("text_content", ""),
                    "file_id": file_id
                }
            else:
                return {
                    "success": False,
                    "error": parse_result.get("error", "Content extraction failed"),
                    "file_id": file_id
                }
        except Exception as e:
            self.service.logger.error(f"❌ Content extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id
            }
    
    async def extract_metadata(self, file_id: str) -> Dict[str, Any]:
        """Extract metadata from file (SOA API)."""
        try:
            parse_result = await self.parse_file(file_id)
            if parse_result.get("success"):
                return {
                    "success": True,
                    "metadata": parse_result.get("metadata", {}),
                    "file_id": file_id
                }
            else:
                return {
                    "success": False,
                    "error": parse_result.get("error", "Metadata extraction failed"),
                    "file_id": file_id
                }
        except Exception as e:
            self.service.logger.error(f"❌ Metadata extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id
            }

