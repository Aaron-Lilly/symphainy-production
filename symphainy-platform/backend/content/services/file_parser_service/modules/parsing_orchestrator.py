#!/usr/bin/env python3
"""
Parsing Orchestrator Module - File Parser Service

Routes parsing requests to appropriate parsing module based on parsing type.
"""

from typing import Dict, Any, Optional


class ParsingOrchestrator:
    """Routes parsing requests to appropriate parsing module."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        
        # Lazy initialization of parsing modules
        self._structured_parsing = None
        self._unstructured_parsing = None
        self._hybrid_parsing = None
        self._workflow_parsing = None
        self._sop_parsing = None
    
    async def _get_structured_parsing(self):
        """Lazy initialization of structured parsing module."""
        if self._structured_parsing is None:
            from .structured_parsing import StructuredParsing
            self._structured_parsing = StructuredParsing(self.service)
        return self._structured_parsing
    
    async def _get_unstructured_parsing(self):
        """Lazy initialization of unstructured parsing module."""
        if self._unstructured_parsing is None:
            from .unstructured_parsing import UnstructuredParsing
            self._unstructured_parsing = UnstructuredParsing(self.service)
        return self._unstructured_parsing
    
    async def _get_hybrid_parsing(self):
        """Lazy initialization of hybrid parsing module."""
        if self._hybrid_parsing is None:
            from .hybrid_parsing import HybridParsing
            self._hybrid_parsing = HybridParsing(self.service)
        return self._hybrid_parsing
    
    async def _get_workflow_parsing(self):
        """Lazy initialization of workflow parsing module."""
        if self._workflow_parsing is None:
            from .workflow_parsing import WorkflowParsing
            self._workflow_parsing = WorkflowParsing(self.service)
        return self._workflow_parsing
    
    async def _get_sop_parsing(self):
        """Lazy initialization of SOP parsing module."""
        if self._sop_parsing is None:
            from .sop_parsing import SOPParsing
            self._sop_parsing = SOPParsing(self.service)
        return self._sop_parsing
    
    async def parse_by_type(
        self,
        parsing_type: str,
        file_data: bytes,
        file_type: str,
        filename: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route to appropriate parsing module based on parsing type.
        
        Args:
            parsing_type: Parsing type ("structured", "unstructured", "hybrid", "workflow", "sop")
            file_data: File data as bytes
            file_type: File extension (e.g., "xlsx", "pdf")
            filename: Original filename
            parse_options: Optional parsing options
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Parsed result dictionary
        """
        try:
            if parsing_type == "structured":
                structured_parsing = await self._get_structured_parsing()
                return await structured_parsing.parse(
                    file_data=file_data,
                    file_type=file_type,
                    filename=filename,
                    parse_options=parse_options,
                    user_context=user_context
                )
            elif parsing_type == "unstructured":
                unstructured_parsing = await self._get_unstructured_parsing()
                return await unstructured_parsing.parse(
                    file_data=file_data,
                    file_type=file_type,
                    filename=filename,
                    parse_options=parse_options,
                    user_context=user_context
                )
            elif parsing_type == "hybrid":
                hybrid_parsing = await self._get_hybrid_parsing()
                return await hybrid_parsing.parse(
                    file_data=file_data,
                    file_type=file_type,
                    filename=filename,
                    parse_options=parse_options,
                    user_context=user_context
                )
            elif parsing_type == "workflow":
                workflow_parsing = await self._get_workflow_parsing()
                return await workflow_parsing.parse(
                    file_data=file_data,
                    file_type=file_type,
                    filename=filename,
                    parse_options=parse_options,
                    user_context=user_context
                )
            elif parsing_type == "sop":
                sop_parsing = await self._get_sop_parsing()
                return await sop_parsing.parse(
                    file_data=file_data,
                    file_type=file_type,
                    filename=filename,
                    parse_options=parse_options,
                    user_context=user_context
                )
            else:
                error_msg = f"Unknown parsing type: {parsing_type}"
                self.service.logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "parsing_type": parsing_type
                }
                
        except Exception as e:
            self.service.logger.error(f"❌ Parsing orchestrator failed: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "parsing_type": parsing_type
            }



