#!/usr/bin/env python3
"""
Unstructured Parsing Module - File Parser Service

Handles unstructured data parsing (PDF, Word, Text).
Returns text chunks for semantic processing.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime


class UnstructuredParsing:
    """Handles unstructured data parsing."""
    
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
        Parse unstructured file (PDF, Word, Text).
        
        Returns text chunks for semantic processing (embeddings, analysis).
        
        Args:
            file_data: File data as bytes
            file_type: File extension (e.g., "pdf", "docx", "txt")
            filename: Original filename
            parse_options: Optional parsing options
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Parsed result dictionary with text chunks
        """
        try:
            # Start telemetry tracking
            await self.service.log_operation_with_telemetry("unstructured_parse_start", success=True, metadata={
                "file_type": file_type,
                "filename": filename
            })
            
            # 1. Get abstraction name for file type
            abstraction_name = self.service.utilities_module.get_abstraction_name_for_file_type(file_type)
            
            if not abstraction_name:
                error_msg = f"Unsupported unstructured file type: {file_type or 'unknown'}"
                self.service.logger.warning(f"⚠️ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "unstructured_parse")
                await self.service.record_health_metric("unstructured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "unsupported_file_type"
                })
                await self.service.log_operation_with_telemetry("unstructured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "unsupported_file_type",
                    "parsing_type": "unstructured"
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
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "unstructured_parse")
                await self.service.record_health_metric("unstructured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "abstraction_not_available"
                })
                await self.service.log_operation_with_telemetry("unstructured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "abstraction_not_available",
                    "parsing_type": "unstructured"
                }
            
            if not file_parser:
                error_msg = f"Abstraction '{abstraction_name}' is None"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "unstructured_parse")
                await self.service.record_health_metric("unstructured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "abstraction_is_none"
                })
                await self.service.log_operation_with_telemetry("unstructured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "abstraction_is_none",
                    "parsing_type": "unstructured"
                }
            
            # 3. Create FileParsingRequest
            from foundations.public_works_foundation.abstraction_contracts.file_parsing_protocol import FileParsingRequest
            
            request = FileParsingRequest(
                file_data=file_data,
                filename=filename,
                options=parse_options
            )
            
            # 4. Parse file via abstraction (with timeout)
            try:
                result = await asyncio.wait_for(
                    file_parser.parse_file(request),
                    timeout=60.0  # 60 second timeout for file parsing
                )
            except asyncio.TimeoutError:
                error_msg = f"Unstructured file parsing timed out after 60 seconds for {file_type} file"
                self.service.logger.error(f"❌ {error_msg}")
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "unstructured_parse")
                await self.service.record_health_metric("unstructured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "file_parsing_timeout"
                })
                await self.service.log_operation_with_telemetry("unstructured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": error_msg,
                    "file_type": file_type,
                    "error": "file_parsing_timeout",
                    "parsing_type": "unstructured"
                }
            
            if not result.success:
                error_msg = result.error or "Unknown error during unstructured file parsing"
                await self.service.handle_error_with_audit(RuntimeError(error_msg), "unstructured_parse")
                await self.service.record_health_metric("unstructured_files_parsed", 0.0, {
                    "file_type": file_type,
                    "success": False,
                    "error": "file_parsing_failed"
                })
                await self.service.log_operation_with_telemetry("unstructured_parse_complete", success=False, details={
                    "file_type": file_type,
                    "error": error_msg
                })
                return {
                    "success": False,
                    "message": f"Unstructured file parsing failed: {error_msg}",
                    "file_type": file_type,
                    "error": error_msg,
                    "parsing_type": "unstructured"
                }
            
            # 5. Convert FileParsingResult to unstructured format (chunks)
            # For unstructured files, we return text chunks for semantic processing
            text_content = result.text_content or ""
            
            # Split into chunks (simple chunking - can be enhanced later)
            # For now, split by paragraphs or fixed size
            chunk_size = parse_options.get("chunk_size", 1000) if parse_options else 1000
            chunks = self._create_text_chunks(text_content, chunk_size)
            
            parsed_result = {
                "success": True,
                "parsing_type": "unstructured",  # ✅ Explicit parsing type
                "file_type": file_type,
                "data": chunks,  # ✅ JSON chunks array
                "chunks": chunks,  # ✅ For compatibility
                "content": text_content,  # ✅ Full text content
                "text_content": text_content,
                "structure": {
                    "chunk_count": len(chunks),
                    "total_chars": len(text_content),
                    "page_count": result.metadata.get("page_count", 1),
                    "table_count": 0  # Unstructured files don't have tables
                },
                "metadata": result.metadata or {},
                "parsed_at": result.timestamp or datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.service.record_health_metric("unstructured_files_parsed", 1.0, {
                "file_type": file_type,
                "chunk_count": len(chunks),
                "total_chars": len(text_content),
                "success": True
            })
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "unstructured_parse_complete",
                success=True,
                details={
                    "file_type": file_type,
                    "chunk_count": len(chunks),
                    "total_chars": len(text_content)
                }
            )
            
            self.service.logger.info(f"✅ Unstructured file parsed successfully: {file_type} (abstraction: {abstraction_name}, chunks: {len(chunks)})")
            
            return parsed_result
            
        except Exception as e:
            # Use enhanced error handling with audit
            self.service.logger.error(f"❌ Unstructured parsing failed: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self.service.handle_error_with_audit(e, "unstructured_parse")
            await self.service.record_health_metric("unstructured_files_parsed", 0.0, {
                "file_type": file_type,
                "success": False,
                "error": str(e)
            })
            await self.service.log_operation_with_telemetry("unstructured_parse_complete", success=False, details={
                "file_type": file_type,
                "error": str(e)
            })
            return {
                "success": False,
                "message": f"Unstructured parsing exception: {e}",
                "file_type": file_type,
                "error": str(e),
                "parsing_type": "unstructured"
            }
    
    def _create_text_chunks(self, text: str, chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """
        Create text chunks from unstructured text.
        
        Simple chunking strategy:
        - Split by paragraphs first (double newline)
        - If paragraph too large, split by sentences
        - If still too large, split by fixed size
        
        Args:
            text: Full text content
            chunk_size: Target chunk size in characters
        
        Returns:
            List of chunk dictionaries
        """
        if not text:
            return []
        
        chunks = []
        
        # Try splitting by paragraphs first
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph would exceed chunk_size, save current chunk
            if current_chunk and len(current_chunk) + len(para) + 2 > chunk_size:
                chunks.append({
                    "text": current_chunk.strip(),
                    "chunk_index": len(chunks),
                    "char_count": len(current_chunk)
                })
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            
            # If single paragraph is too large, split it by sentences
            if len(current_chunk) > chunk_size * 1.5:
                sentences = current_chunk.split('. ')
                sentence_chunk = ""
                for sentence in sentences:
                    if sentence_chunk and len(sentence_chunk) + len(sentence) + 2 > chunk_size:
                        chunks.append({
                            "text": sentence_chunk.strip() + ".",
                            "chunk_index": len(chunks),
                            "char_count": len(sentence_chunk)
                        })
                        sentence_chunk = sentence
                    else:
                        if sentence_chunk:
                            sentence_chunk += ". " + sentence
                        else:
                            sentence_chunk = sentence
                
                if sentence_chunk:
                    current_chunk = sentence_chunk
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "chunk_index": len(chunks),
                "char_count": len(current_chunk)
            })
        
        return chunks
