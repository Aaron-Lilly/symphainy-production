#!/usr/bin/env python3
"""
Hybrid Parsing Module - File Parser Service

Handles hybrid parsing (structured + unstructured).
Outputs 3 JSON files: structured data, unstructured chunks, and correlation map.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime


class HybridParsing:
    """Handles hybrid data parsing."""
    
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
        Parse hybrid file (structured + unstructured).
        
        Outputs 3 JSON files:
        1. Structured data (JSON structured)
        2. Unstructured chunks (JSON chunks array)
        3. Correlation map (lightweight JSON mapping)
        
        Args:
            file_data: File data as bytes
            file_type: File extension (e.g., "excel_with_text")
            filename: Original filename
            parse_options: Optional parsing options
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Parsed result dictionary with 3 parsed files
        """
        try:
            # Start telemetry tracking
            await self.service.log_operation_with_telemetry("hybrid_parse_start", success=True, metadata={
                "file_type": file_type,
                "filename": filename
            })
            
            # Get structured and unstructured parsing modules
            from .structured_parsing import StructuredParsing
            from .unstructured_parsing import UnstructuredParsing
            
            structured_parsing = StructuredParsing(self.service)
            unstructured_parsing = UnstructuredParsing(self.service)
            
            # 1. Parse structured portion
            self.service.logger.info(f"📊 Parsing structured portion of hybrid file...")
            structured_result = await structured_parsing.parse(
                file_data=file_data,
                file_type=file_type,
                filename=filename,
                parse_options=parse_options,
                user_context=user_context
            )
            
            if not structured_result.get("success"):
                return {
                    "success": False,
                    "error": f"Structured parsing failed: {structured_result.get('error')}",
                    "parsing_type": "hybrid"
                }
            
            # 2. Parse unstructured portion
            self.service.logger.info(f"📝 Parsing unstructured portion of hybrid file...")
            unstructured_result = await unstructured_parsing.parse(
                file_data=file_data,
                file_type=file_type,
                filename=filename,
                parse_options=parse_options,
                user_context=user_context
            )
            
            if not unstructured_result.get("success"):
                return {
                    "success": False,
                    "error": f"Unstructured parsing failed: {unstructured_result.get('error')}",
                    "parsing_type": "hybrid"
                }
            
            # 3. Create correlation map
            self.service.logger.info(f"🔗 Creating correlation map...")
            correlation_map = await self._create_correlation_map(
                structured_result=structured_result,
                unstructured_result=unstructured_result
            )
            
            # 4. Build result with 3 parsed files
            parsed_result = {
                "success": True,
                "parsing_type": "hybrid",  # ✅ Explicit parsing type
                "file_type": file_type,
                "parsed_files": {
                    "structured": {
                        "data": structured_result.get("data", {}),  # ✅ JSON structured data
                        "format": "json_structured",
                        "tables": structured_result.get("tables", []),
                        "records": structured_result.get("records", [])
                    },
                    "unstructured": {
                        "data": unstructured_result.get("chunks", []),  # ✅ JSON chunks array
                        "format": "json_chunks",
                        "chunk_count": len(unstructured_result.get("chunks", []))
                    },
                    "correlation_map": {
                        "data": correlation_map,  # ✅ Lightweight correlation map
                        "format": "json"
                    }
                },
                "metadata": {
                    "structured_metadata": structured_result.get("metadata", {}),
                    "unstructured_metadata": unstructured_result.get("metadata", {}),
                    "table_count": len(structured_result.get("tables", [])),
                    "chunk_count": len(unstructured_result.get("chunks", []))
                },
                "parsed_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.service.record_health_metric("hybrid_files_parsed", 1.0, {
                "file_type": file_type,
                "table_count": len(structured_result.get("tables", [])),
                "chunk_count": len(unstructured_result.get("chunks", [])),
                "success": True
            })
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "hybrid_parse_complete",
                success=True,
                details={
                    "file_type": file_type,
                    "table_count": len(structured_result.get("tables", [])),
                    "chunk_count": len(unstructured_result.get("chunks", []))
                }
            )
            
            self.service.logger.info(f"✅ Hybrid file parsed successfully: {file_type} (tables: {len(structured_result.get('tables', []))}, chunks: {len(unstructured_result.get('chunks', []))})")
            
            return parsed_result
            
        except Exception as e:
            # Use enhanced error handling with audit
            self.service.logger.error(f"❌ Hybrid parsing failed: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self.service.handle_error_with_audit(e, "hybrid_parse")
            await self.service.record_health_metric("hybrid_files_parsed", 0.0, {
                "file_type": file_type,
                "success": False,
                "error": str(e)
            })
            await self.service.log_operation_with_telemetry("hybrid_parse_complete", success=False, details={
                "file_type": file_type,
                "error": str(e)
            })
            return {
                "success": False,
                "message": f"Hybrid parsing exception: {e}",
                "file_type": file_type,
                "error": str(e),
                "parsing_type": "hybrid"
            }
    
    async def _create_correlation_map(
        self,
        structured_result: Dict[str, Any],
        unstructured_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create lightweight correlation map between structured and unstructured data.
        
        This map helps correlate:
        - Tables/records in structured data
        - Chunks in unstructured data
        - Metadata relationships
        
        Args:
            structured_result: Structured parsing result
            unstructured_result: Unstructured parsing result
        
        Returns:
            Correlation map dictionary
        """
        try:
            correlation_map = {
                "structured_to_unstructured": {},
                "unstructured_to_structured": {},
                "confidence_scores": {},
                "metadata_correlations": {}
            }
            
            # Get structured data
            tables = structured_result.get("tables", [])
            records = structured_result.get("records", [])
            
            # Get unstructured chunks
            chunks = unstructured_result.get("chunks", [])
            
            # Simple correlation: map table indices to chunk indices
            # For now, use simple round-robin mapping
            # In future, could use semantic similarity or position-based mapping
            for table_idx, table in enumerate(tables):
                # Map each table to a chunk (round-robin)
                chunk_idx = table_idx % len(chunks) if chunks else None
                if chunk_idx is not None:
                    correlation_map["structured_to_unstructured"][f"table_{table_idx}"] = f"chunk_{chunk_idx}"
                    correlation_map["unstructured_to_structured"][f"chunk_{chunk_idx}"] = f"table_{table_idx}"
                    correlation_map["confidence_scores"][f"table_{table_idx}_to_chunk_{chunk_idx}"] = 0.5  # Default confidence
            
            # Map records to chunks
            for record_idx, record in enumerate(records):
                chunk_idx = (len(tables) + record_idx) % len(chunks) if chunks else None
                if chunk_idx is not None:
                    correlation_map["structured_to_unstructured"][f"record_{record_idx}"] = f"chunk_{chunk_idx}"
                    correlation_map["unstructured_to_structured"][f"chunk_{chunk_idx}"] = f"record_{record_idx}"
                    correlation_map["confidence_scores"][f"record_{record_idx}_to_chunk_{chunk_idx}"] = 0.5  # Default confidence
            
            # Metadata correlations
            structured_metadata = structured_result.get("metadata", {})
            unstructured_metadata = unstructured_result.get("metadata", {})
            
            correlation_map["metadata_correlations"] = {
                "page_count": {
                    "structured": structured_metadata.get("page_count", 0),
                    "unstructured": unstructured_metadata.get("page_count", 0)
                },
                "file_type": structured_result.get("file_type"),
                "parsing_timestamp": datetime.utcnow().isoformat()
            }
            
            return correlation_map
            
        except Exception as e:
            self.service.logger.warning(f"⚠️ Correlation map creation failed: {e}")
            # Return minimal correlation map
            return {
                "structured_to_unstructured": {},
                "unstructured_to_structured": {},
                "confidence_scores": {},
                "metadata_correlations": {},
                "error": str(e)
            }
