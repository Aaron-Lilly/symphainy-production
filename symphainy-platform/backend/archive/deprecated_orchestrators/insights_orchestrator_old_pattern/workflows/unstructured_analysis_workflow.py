#!/usr/bin/env python3
"""
Unstructured Data Analysis Workflow

WHAT: Orchestrates unstructured data analysis for insights (APG/AAR processing)
HOW: Delegates to enabling services (APGProcessor, InsightsGenerator, VisualizationEngine)

This workflow implements the unstructured data insights flow:
1. Get text content from DataSteward (file or content_metadata)
2. Process text using APGProcessorService
3. Extract themes/patterns using InsightsGeneratorService
4. Generate narrative summary
5. If AAR: extract lessons learned, risks, recommendations, timeline
6. Format as 3-way summary + optional AAR section
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


logger = logging.getLogger(__name__)


class UnstructuredAnalysisWorkflow:
    """
    Workflow for unstructured data analysis (text, documents, AARs).
    
    Produces 3-way summary + optional AAR section:
    - Textual: Business narrative (always present)
    - Tabular: Extracted data (when applicable)
    - Visualizations: Semantic visualizations (when applicable)
    - AAR Analysis: Lessons learned, risks, recommendations, timeline (optional)
    """
    
    def __init__(self, orchestrator):
        """
        Initialize workflow with orchestrator context.
        
        Args:
            orchestrator: InsightsOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = logger
    
    async def execute(
        self,
        source_type: str,
        file_id: Optional[str] = None,
        content_metadata_id: Optional[str] = None,
        text_content: Optional[str] = None,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute unstructured data analysis workflow.
        
        Args:
            source_type: 'file' or 'content_metadata'
            file_id: File identifier (if source_type='file')
            content_metadata_id: Content metadata ID from ArangoDB (if source_type='content_metadata')
            text_content: Direct text content (optional)
            analysis_options: Optional analysis configuration
                - aar_specific_analysis: bool (default: False)
                - include_visualizations: bool (default: True)
                - include_tabular_summary: bool (default: True)
        
        Returns:
            Dict[str, Any]: Analysis result with 3-way summary + optional AAR section
        """
        try:
            self.logger.info(f"📄 Starting unstructured data analysis workflow: source_type={source_type}")
            
            # Generate analysis ID
            analysis_id = f"analysis_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            # Default options
            options = analysis_options or {}
            aar_specific = options.get("aar_specific_analysis", False)
            include_visualizations = options.get("include_visualizations", True)
            include_tabular_summary = options.get("include_tabular_summary", True)
            
            # Step 1: Get text content
            text_result = await self._get_text_content(source_type, file_id, content_metadata_id, text_content)
            if not text_result.get("success"):
                return self._error_response(analysis_id, "Failed to retrieve text content", text_result.get("error"))
            
            text_data = text_result.get("text")
            source_info = text_result.get("source_info", {})
            
            # Step 2: Process text (APG/general)
            processing_result = await self._process_text(text_data, aar_specific, options)
            if not processing_result.get("success"):
                return self._error_response(analysis_id, "Text processing failed", processing_result.get("error"))
            
            # Step 3: Extract themes and patterns
            themes_result = await self._extract_themes(text_data, processing_result, options)
            
            # Step 4: Generate insights summary
            insights_result = await self._generate_insights(
                text_data,
                processing_result,
                themes_result,
                aar_specific,
                options
            )
            
            # Step 5: Generate visualizations (if requested)
            visualizations_result = None
            if include_visualizations:
                visualizations_result = await self._generate_visualizations(
                    text_data,
                    processing_result,
                    themes_result,
                    options
                )
            
            # Step 6: AAR-specific analysis (if requested)
            aar_analysis_result = None
            if aar_specific:
                aar_analysis_result = await self._perform_aar_analysis(
                    text_data,
                    processing_result,
                    options
                )
            
            # Step 7: Format as 3-way summary
            summary = self._format_three_way_summary(
                processing_result,
                themes_result,
                insights_result,
                visualizations_result,
                include_tabular_summary,
                include_visualizations
            )
            
            # Step 8: Extract insights list
            insights_list = self._extract_insights_list(insights_result, themes_result)
            
            # Step 9: Track lineage
            await self._track_workflow_lineage(source_type, file_id or content_metadata_id, analysis_id)
            
            # Step 10: Store results
            storage_result = await self._store_analysis_results(
                analysis_id,
                summary,
                insights_list,
                aar_analysis_result,
                source_info
            )
            
            self.logger.info(f"✅ Unstructured data analysis workflow complete: {analysis_id}")
            
            # Return formatted response (aligns with API contract)
            response = {
                "success": True,
                "analysis_id": analysis_id,
                "summary": summary,
                "insights": insights_list,
                "metadata": {
                    "content_type": "unstructured",
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "processing_time_ms": 0,  # TODO: Track actual processing time
                    "source_info": {
                        "type": source_type,
                        "id": file_id or content_metadata_id,
                        "name": source_info.get("name"),
                        "tenant_id": source_info.get("tenant_id")
                    }
                }
            }
            
            # Add AAR analysis if performed
            if aar_analysis_result and aar_analysis_result.get("success"):
                response["aar_analysis"] = aar_analysis_result.get("aar_data")
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Unstructured analysis workflow failed: {e}")
            return self._error_response(
                analysis_id if 'analysis_id' in locals() else "unknown",
                "Workflow execution failed",
                str(e)
            )
    
    # ========================================================================
    # WORKFLOW STEPS
    # ========================================================================
    
    async def _get_text_content(
        self,
        source_type: str,
        file_id: Optional[str],
        content_metadata_id: Optional[str],
        text_content: Optional[str]
    ) -> Dict[str, Any]:
        """Get text content from file, metadata, or direct input."""
        try:
            # If text_content provided directly, use it
            if text_content:
                return {
                    "success": True,
                    "text": text_content,
                    "source_info": {"type": "direct", "name": "direct_text"}
                }
            
            if source_type == "file":
                # Get file via Content Steward SOA API (lazy load if needed)
                content_steward = self.orchestrator.content_steward
                if not content_steward:
                    # Try lazy loading Content Steward
                    content_steward = await self.orchestrator.get_content_steward_api()
                    if content_steward:
                        # Cache it for future use
                        self.orchestrator.content_steward = content_steward
                if not content_steward:
                    return {"success": False, "error": "Content Steward service not available"}
                
                # Use Content Steward SOA API to get file
                file_record = await content_steward.get_file(file_id)
                if not file_record:
                    return {"success": False, "error": f"File {file_id} not found"}
                
                # Extract text content from file
                file_content = file_record.get("file_content", b"")
                if isinstance(file_content, bytes):
                    try:
                        text = file_content.decode('utf-8')
                    except UnicodeDecodeError:
                        # If binary, return error - unstructured analysis needs text
                        return {"success": False, "error": f"File {file_id} is binary and cannot be analyzed as unstructured text"}
                else:
                    text = str(file_content)
                
                return {
                    "success": True,
                    "text": text,
                    "source_info": {
                        "type": "file",
                        "id": file_id,
                        "name": file_record.get("filename", f"file_{file_id}"),
                        "content_type": file_record.get("file_type", "unknown")
                    }
                }
                
            elif source_type == "content_metadata":
                # Get content metadata via Content Steward SOA API (lazy load if needed)
                content_steward = self.orchestrator.content_steward
                if not content_steward:
                    # Try lazy loading Content Steward
                    content_steward = await self.orchestrator.get_content_steward_api()
                    if content_steward:
                        # Cache it for future use
                        self.orchestrator.content_steward = content_steward
                if not content_steward:
                    return {"success": False, "error": "Content Steward service not available"}
                
                # Use Content Steward SOA API to get asset metadata (includes content metadata from ArangoDB)
                asset_metadata = await content_steward.get_asset_metadata(content_metadata_id)
                if not asset_metadata or asset_metadata.get("status") != "success":
                    return {"success": False, "error": f"Content metadata {content_metadata_id} not found"}
                
                # Extract text from metadata
                metadata_dict = asset_metadata.get("metadata", {})
                processing_result = metadata_dict.get("processing_result", {})
                
                # Try to get text from parsed content or metadata
                text = None
                if processing_result.get("parsed_content"):
                    text = processing_result.get("parsed_content")
                elif metadata_dict.get("text_content"):
                    text = metadata_dict.get("text_content")
                elif metadata_dict.get("summary"):
                    text = metadata_dict.get("summary")
                
                if not text:
                    return {"success": False, "error": f"Content metadata {content_metadata_id} does not contain extractable text"}
                
                return {
                    "success": True,
                    "text": text,
                    "source_info": {
                        "type": "content_metadata",
                        "id": content_metadata_id,
                        "name": f"metadata_{content_metadata_id}",
                        "content_type": asset_metadata.get("content_type", "unknown")
                    }
                }
            
            else:
                return {"success": False, "error": f"Unknown source_type: {source_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_text(
        self,
        text_data: str,
        aar_specific: bool,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process text using APGProcessorService."""
        try:
            # Access APGProcessorService from orchestrator
            apg_processor = await self.orchestrator._get_apg_processor_service()
            if not apg_processor:
                # Fallback to basic processing if service not available
                self.logger.warning("⚠️ APG Processor Service not available, using basic processing")
                return {
                    "success": True,
                    "processed_text": text_data,
                    "entities_extracted": [],
                    "sentiment": "neutral",
                    "key_phrases": []
                }
            
            # Use APGProcessorService (extracted pattern from InsightsOrchestrationService)
            from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGMode
            apg_mode = APGMode.AUTO if not aar_specific else APGMode.ENABLED
            
            result = await apg_processor.process_apg_mode(
                data={"text": text_data},
                user_context=options.get("user_context"),
                session_id=options.get("session_id"),
                apg_mode=apg_mode
            )
            
            # Extract processing results
            if result.get("success"):
                return {
                    "success": True,
                    "processed_text": text_data,
                    "entities_extracted": result.get("entities", []),
                    "sentiment": result.get("sentiment", "neutral"),
                    "key_phrases": result.get("key_phrases", []),
                    "patterns": result.get("patterns", [])
                }
            else:
                # APG processing failed, return basic processing
                return {
                    "success": True,
                    "processed_text": text_data,
                    "entities_extracted": [],
                    "sentiment": "neutral",
                    "key_phrases": []
                }
            
        except Exception as e:
            self.logger.warning(f"⚠️ APG processing failed: {e}, using basic processing")
            return {
                "success": True,
                "processed_text": text_data,
                "entities_extracted": [],
                "sentiment": "neutral",
                "key_phrases": []
            }
    
    async def _extract_themes(
        self,
        text_data: str,
        processing_result: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract themes and patterns using InsightsGeneratorService."""
        try:
            # Access InsightsGeneratorService from orchestrator
            insights_generator = await self.orchestrator._get_insights_generator_service()
            if not insights_generator:
                # Fallback to basic themes if service not available
                self.logger.warning("⚠️ Insights Generator Service not available, using basic themes")
                return {
                    "success": True,
                    "themes": [],
                    "patterns": []
                }
            
            # Use InsightsGeneratorService.prepare_insights_data() to prepare structured data
            # Note: InsightsGeneratorService provides data/capabilities, not direct insights generation
            analysis_results = {
                "text": text_data,
                "processing_result": processing_result,
                "entities": processing_result.get("entities_extracted", []),
                "key_phrases": processing_result.get("key_phrases", [])
            }
            
            result = await insights_generator.prepare_insights_data(
                analysis_results=analysis_results,
                user_context=options.get("user_context"),
                session_id=options.get("session_id")
            )
            
            # Extract themes and patterns from prepared data
            if result.get("success"):
                insights_context = result.get("insights_context", {})
                return {
                    "success": True,
                    "themes": insights_context.get("themes", []),
                    "patterns": insights_context.get("patterns", []),
                    "insights": insights_context.get("insights", [])
                }
            else:
                # Data preparation failed, return empty themes
                return {
                    "success": True,
                    "themes": [],
                    "patterns": []
                }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Theme extraction failed: {e}, using basic themes")
            return {
                "success": True,
                "themes": [],
                "patterns": []
            }
    
    async def _generate_insights(
        self,
        text_data: str,
        processing_result: Dict[str, Any],
        themes_result: Dict[str, Any],
        aar_specific: bool,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights summary using InsightsGeneratorService."""
        try:
            # Access InsightsGeneratorService from orchestrator
            insights_generator = await self.orchestrator._get_insights_generator_service()
            if not insights_generator:
                # Fallback to basic summary if service not available
                self.logger.warning("⚠️ Insights Generator Service not available, using basic summary")
                text_length = len(text_data)
                word_count = len(text_data.split())
                key_phrases = processing_result.get("key_phrases", [])
                
                textual_summary = f"This document contains {word_count} words and {text_length} characters. "
                if key_phrases:
                    textual_summary += f"Key topics identified: {', '.join(key_phrases[:3])}. "
                textual_summary += "The document has been analyzed for themes, patterns, and insights."
                
                return {
                    "success": True,
                    "textual_summary": textual_summary,
                    "key_findings": processing_result.get("key_phrases", [])[:3],
                    "recommendations": ["Review key themes", "Consider further analysis"] if themes_result.get("themes") else []
                }
            
            # Use InsightsGeneratorService.prepare_insights_data() to prepare structured data
            # Note: InsightsGeneratorService provides data/capabilities, not direct insights generation
            # Combine processing and themes results for comprehensive insights
            analysis_results = {
                "text": text_data,
                "processing_result": processing_result,
                "themes_result": themes_result,
                "entities": processing_result.get("entities_extracted", []),
                "key_phrases": processing_result.get("key_phrases", []),
                "themes": themes_result.get("themes", []),
                "patterns": themes_result.get("patterns", [])
            }
            
            result = await insights_generator.prepare_insights_data(
                analysis_results=analysis_results,
                user_context=options.get("user_context"),
                session_id=options.get("session_id")
            )
            
            # Extract insights summary from prepared data
            if result.get("success"):
                insights_context = result.get("insights_context", {})
                business_rules = result.get("business_rules", [])
                
                # Generate textual summary from insights context
                textual_summary = insights_context.get("summary", "Analysis complete.")
                if not textual_summary or textual_summary == "Analysis complete.":
                    # Fallback to generating summary from data
                    text_length = len(text_data)
                    word_count = len(text_data.split())
                    key_phrases = processing_result.get("key_phrases", [])
                    themes = themes_result.get("themes", [])
                    
                    textual_summary = f"This document contains {word_count} words. "
                    if key_phrases:
                        textual_summary += f"Key topics: {', '.join(key_phrases[:3])}. "
                    if themes:
                        textual_summary += f"Identified {len(themes)} themes. "
                    textual_summary += "The document has been analyzed for insights."
                
                return {
                    "success": True,
                    "textual_summary": textual_summary,
                    "key_findings": insights_context.get("insights", processing_result.get("key_phrases", []))[:5],
                    "recommendations": business_rules[:3] if business_rules else []
                }
            else:
                # Data preparation failed, return basic summary
                text_length = len(text_data)
                word_count = len(text_data.split())
                key_phrases = processing_result.get("key_phrases", [])
                
                textual_summary = f"This document contains {word_count} words and {text_length} characters. "
                if key_phrases:
                    textual_summary += f"Key topics identified: {', '.join(key_phrases[:3])}. "
                textual_summary += "The document has been analyzed for themes, patterns, and insights."
                
                return {
                    "success": True,
                    "textual_summary": textual_summary,
                    "key_findings": processing_result.get("key_phrases", [])[:3],
                    "recommendations": []
                }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Insights generation failed: {e}, using basic summary")
            text_length = len(text_data)
            word_count = len(text_data.split())
            key_phrases = processing_result.get("key_phrases", [])
            
            textual_summary = f"This document contains {word_count} words and {text_length} characters. "
            if key_phrases:
                textual_summary += f"Key topics identified: {', '.join(key_phrases[:3])}. "
            textual_summary += "The document has been analyzed for themes, patterns, and insights."
            
            return {
                "success": True,
                "textual_summary": textual_summary,
                "key_findings": processing_result.get("key_phrases", [])[:3],
                "recommendations": []
            }
    
    async def _generate_visualizations(
        self,
        text_data: str,
        processing_result: Dict[str, Any],
        themes_result: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate semantic visualizations (word clouds, topic graphs, etc.)."""
        try:
            visualization_engine = await self.orchestrator._get_visualization_engine_service()
            if not visualization_engine:
                return {"success": False, "error": "VisualizationEngine service not available"}
            
            # TODO: Implement semantic visualization generation
            # Note: Unstructured data typically doesn't have tabular visualizations
            # Could add entity relationship diagrams or sentiment timelines in future
            return {
                "success": True,
                "visualizations": []  # No standard charts for unstructured text analysis
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _perform_aar_analysis(
        self,
        text_data: str,
        processing_result: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform Navy AAR-specific analysis using APGProcessorService with AAR mode."""
        try:
            # Access APGProcessorService from orchestrator
            apg_processor = await self.orchestrator._get_apg_processor_service()
            if not apg_processor:
                # Fallback to placeholder if service not available
                self.logger.warning("⚠️ APG Processor Service not available, using placeholder AAR analysis")
                return {
                    "success": True,
                    "aar_data": {
                        "lessons_learned": [],
                        "risks": [],
                        "recommendations": [],
                        "timeline": []
                    }
                }
            
            # Use APGProcessorService with AAR mode (extracted pattern from InsightsOrchestrationService)
            from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGMode
            result = await apg_processor.process_apg_mode(
                data={"text": text_data, "processing_result": processing_result},
                user_context=options.get("user_context"),
                session_id=options.get("session_id"),
                apg_mode=APGMode.MANUAL  # AAR-specific mode
            )
            
            # Extract AAR-specific data from result
            if result.get("success"):
                # Try to extract AAR data from result
                aar_data = result.get("aar_data") or result.get("aar_analysis") or {}
                
                return {
                    "success": True,
                    "aar_data": {
                        "lessons_learned": aar_data.get("lessons_learned", result.get("lessons_learned", [])),
                        "risks": aar_data.get("risks", result.get("risks", [])),
                        "recommendations": aar_data.get("recommendations", result.get("recommendations", [])),
                        "timeline": aar_data.get("timeline", result.get("timeline", []))
                    }
                }
            else:
                # APG processing failed, return empty AAR data
                return {
                    "success": True,
                    "aar_data": {
                        "lessons_learned": [],
                        "risks": [],
                        "recommendations": [],
                        "timeline": []
                    }
                }
            
        except Exception as e:
            self.logger.warning(f"⚠️ AAR analysis failed: {e}, using empty AAR data")
            return {
                "success": True,
                "aar_data": {
                    "lessons_learned": [],
                    "risks": [],
                    "recommendations": [],
                    "timeline": []
                }
            }
    
    # ========================================================================
    # FORMATTING & STORAGE
    # ========================================================================
    
    def _format_three_way_summary(
        self,
        processing_result: Dict[str, Any],
        themes_result: Dict[str, Any],
        insights_result: Dict[str, Any],
        visualizations_result: Optional[Dict[str, Any]],
        include_tabular: bool,
        include_visualizations: bool
    ) -> Dict[str, Any]:
        """Format results as 3-way summary (text/table/charts)."""
        summary = {
            "textual": insights_result.get("textual_summary", "Analysis complete.")
        }
        
        # Add tabular summary (if requested and themes available)
        if include_tabular and themes_result.get("success"):
            summary["tabular"] = {
                "columns": ["Theme", "Confidence", "Occurrences"],
                "rows": [
                    [theme["theme"], theme["confidence"], theme["occurrences"]]
                    for theme in themes_result.get("themes", [])
                ],
                "summary_stats": {
                    "total_rows": len(themes_result.get("themes", [])),
                    "total_columns": 3
                }
            }
        
        # Add visualizations (if requested and available)
        if include_visualizations and visualizations_result and visualizations_result.get("success"):
            summary["visualizations"] = visualizations_result.get("visualizations", [])
        
        return summary
    
    def _extract_insights_list(
        self,
        insights_result: Dict[str, Any],
        themes_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract insights as list format for API response."""
        insights_list = []
        
        # Add key findings as insights
        for finding in insights_result.get("key_findings", []):
            insights_list.append({
                "insight_id": f"insight_{uuid.uuid4().hex[:8]}",
                "type": "trend",
                "description": finding,
                "confidence": 0.80,
                "recommendations": insights_result.get("recommendations", []),
                "supporting_data": {}
            })
        
        return insights_list
    
    async def _track_workflow_lineage(
        self,
        source_type: str,
        source_id: str,
        analysis_id: str
    ) -> None:
        """Track data lineage for this workflow."""
        try:
            await self.orchestrator.track_data_lineage(
                {
                    "source": source_id,
                    "destination": analysis_id,
                    "transformation": {
                        "type": "unstructured_analysis_workflow",
                        "orchestrator": self.orchestrator.orchestrator_name,
                        "source_type": source_type
                    }
                }
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to track lineage: {e}")
    
    async def _store_analysis_results(
        self,
        analysis_id: str,
        summary: Dict[str, Any],
        insights: List[Dict[str, Any]],
        aar_analysis: Optional[Dict[str, Any]],
        source_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store analysis results via Librarian."""
        try:
            document_data = {
                "analysis_id": analysis_id,
                "summary": summary,
                "insights": insights,
                "source_info": source_info
            }
            
            if aar_analysis:
                document_data["aar_analysis"] = aar_analysis
            
            storage_result = await self.orchestrator.store_document(
                document_data=document_data,
                metadata={
                    "analysis_id": analysis_id,
                    "workflow": "unstructured_analysis",
                    "orchestrator": self.orchestrator.orchestrator_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            return storage_result
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to store results: {e}")
            return {}
    
    def _error_response(
        self,
        analysis_id: str,
        message: str,
        error: str
    ) -> Dict[str, Any]:
        """Format error response."""
        return {
            "success": False,
            "analysis_id": analysis_id,
            "error": message,
            "error_details": error,
            "timestamp": datetime.utcnow().isoformat()
        }

