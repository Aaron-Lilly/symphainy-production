"""
POC Document Tool
Smart City Native + Micro-Modular Architecture
"""

from backend.bases.smart_city.base_mcp import BaseMCP
from backend.smart_city_library.infrastructure.infrastructure_services.infrastructure_service_factory import get_infrastructure_service_factory
from backend.smart_city_library.architectural_components import traffic_cop, conductor, post_office
from .micro_modules.document_generator import POCDocumentGenerator
from .micro_modules.content_formatter import POCContentFormatter
from .micro_modules.export_handler import POCExportHandler
from .micro_modules.template_manager import POCTemplateManager
from typing import Dict, Any, Optional
from datetime import datetime


class POCDocumentTool(BaseMCP):
    """
    POC Document Tool for Business Outcome pillar.
    Generates DOCX/PDF documents from POC proposals using micro-module architecture.
    """
    
    def __init__(self):
        super().__init__()
        self.tool_name = "poc_document_tool"
        self.pillar = "business_outcome"
        
        # Smart City infrastructure services
        factory = get_infrastructure_service_factory()
        self._logger = factory.get_logging_service("POCDocumentTool")
        self._config = factory.get_configuration_service()
        self._data_processing = factory.get_data_processing_service()
        self._response_formatter = factory.get_response_formatting_service()
        
        # Initialize micro-modules
        self._initialize_micro_modules()
        
        # Smart City components
        self.traffic_cop = traffic_cop
        self.conductor = conductor
        self.post_office = post_office
        
        self._logger.info("POCDocumentTool initialized with Smart City patterns")
    
    def _initialize_micro_modules(self):
        """Initialize micro-modules following Smart City patterns."""
        try:
            self.document_generator = POCDocumentGenerator(self._logger, self._config)
            self.content_formatter = POCContentFormatter(self._logger, self._config)
            self.export_handler = POCExportHandler(self._logger, self._config)
            self.template_manager = POCTemplateManager(self._logger, self._config)
            
            self._logger.info("POCDocumentTool micro-modules initialized successfully")
            
        except Exception as e:
            self._logger.error(f"Error initializing POCDocumentTool micro-modules: {e}")
            raise e
    
    async def generate_document(
        self, 
        poc_proposal: Dict[str, Any], 
        format_type: str = "docx",
        session_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate POC document using micro-module architecture.
        
        Args:
            poc_proposal: POC proposal data
            format_type: Document format (docx, pdf)
            session_token: Session token for Smart City integration
            
        Returns:
            Document generation result
        """
        try:
            # Validate session if provided
            if session_token:
                session_valid = self.traffic_cop.validate_session(session_token)
                if not session_valid:
                    return {
                        "error": "Invalid session token",
                        "success": False
                    }
            
            format_type = format_type.lower()
            
            # Step 1: Validate input data using template manager
            is_valid, warnings, validated_data = await self.template_manager.validate_poc_proposal(poc_proposal)
            
            if not is_valid:
                return {
                    "error": f"Validation failed: {', '.join(warnings)}",
                    "success": False,
                    "note": "Check that POC proposal data contains required fields: title, executive_summary, business_case, poc_scope, timeline, budget, success_metrics, risk_assessment, next_steps"
                }
            
            # Step 2: Generate document structure using document generator
            doc = await self.document_generator.create_document_structure(validated_data)
            
            # Step 3: Apply professional styling using content formatter
            await self.content_formatter.apply_document_styling(doc)
            await self.content_formatter.add_visual_separators(doc)
            await self.content_formatter.ensure_document_completeness(doc)
            
            # Step 4: Export document using export handler
            if format_type == "docx":
                result = await self.export_handler.save_docx_document(doc, validated_data)
            elif format_type == "pdf":
                # Generate DOCX first, then convert to PDF
                docx_result = await self.export_handler.save_docx_document(doc, validated_data)
                result = await self.export_handler.generate_pdf_from_docx(docx_result)
            else:
                return {
                    "error": f"Unsupported format: {format_type}",
                    "success": False,
                    "supported_formats": ["docx", "pdf"]
                }
            
            # Step 5: Validate export result
            if not await self.export_handler.validate_export_result(result):
                return {
                    "error": "Export validation failed",
                    "success": False,
                    "details": result
                }
            
            # Step 6: Add quality assessment
            quality_score = await self.template_manager.get_quality_score(validated_data)
            
            # Step 7: Create comprehensive result
            final_result = {
                "success": True,
                "format": format_type,
                "file_path": result.get("file_path", ""),
                "file_size": result.get("file_size", 0),
                "filename": result.get("filename", ""),
                "quality_score": quality_score,
                "warnings": warnings,
                "note": "Generated using micro-module architecture",
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Add PDF-specific note if applicable
            if format_type == "pdf" and "note" in result:
                final_result["pdf_note"] = result["note"]
            
            self._logger.info(f"Document generation completed successfully: {format_type}")
            return final_result
            
        except Exception as e:
            self._logger.error(f"Document generation failed: {str(e)}")
            return {
                "error": f"Document generation failed: {str(e)}",
                "success": False,
                "note": "Check logs for detailed error information"
            }
    
    async def get_quality_metrics(self, poc_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Get quality metrics for a POC proposal without generating a document."""
        try:
            return await self.template_manager.get_quality_score(poc_proposal)
        except Exception as e:
            self._logger.error(f"Error getting quality metrics: {e}")
            return {"error": str(e)}
    
    async def create_document_outline(self, poc_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document outline without generating the full document."""
        try:
            outline = await self.template_manager.create_document_outline(poc_proposal)
            return {
                "outline": outline,
                "total_sections": len(outline),
                "proposal_title": poc_proposal.get("title", "Untitled")
            }
        except Exception as e:
            self._logger.error(f"Error creating document outline: {e}")
            return {"error": str(e)}
    
    async def get_tool_capabilities(self) -> Dict[str, Any]:
        """Get information about tool capabilities and supported formats."""
        return {
            "supported_formats": ["docx", "pdf"],
            "required_fields": await self.template_manager.get_required_fields(),
            "optional_fields": await self.template_manager.get_optional_fields(),
            "architecture": "micro-module",
            "modules": [
                "document_generator",
                "content_formatter",
                "export_handler",
                "template_manager"
            ]
        }

