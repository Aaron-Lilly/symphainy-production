#!/usr/bin/env python3
"""
Data Mapping Workflow

WHAT: Orchestrates end-to-end data mapping from source to target
HOW: Coordinates Insights realm services and agents to map data between schemas

This workflow implements the unified data mapping system supporting:
1. Unstructured → Structured (License PDF → Excel)
2. Structured → Structured (Legacy Policy Records → New Data Model)

Flow:
1. Detect mapping type (unstructured→structured or structured→structured)
2. Extract schemas from source and target
3. Get embeddings for semantic matching
4. Generate mapping rules
5. Extract/Transform data based on mapping type
6. Validate data quality (for structured→structured)
7. Transform data to target format
8. Generate output file
9. Generate cleanup actions (if quality issues found)
10. Track lineage
"""

import os
import sys
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../../'))

from bases.realm_service_base import RealmServiceBase


class DataMappingWorkflow:
    """
    Data Mapping Workflow - Orchestrates end-to-end data mapping process.
    
    Located in Journey Realm, composes Insights Realm Services and Agents.
    """
    
    def __init__(self, orchestrator):
        """
        Initialize Data Mapping Workflow.
        
        Args:
            orchestrator: InsightsJourneyOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = orchestrator.logger if hasattr(orchestrator, 'logger') else None
        if not self.logger:
            import logging
            self.logger = logging.getLogger(__name__)
    
    async def execute(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute data mapping workflow with solution context support.
        
        Stores user_context as instance variable for use in helper methods.
        """
        # Store user_context for use in helper methods
        self.user_context = user_context
        """
        Execute data mapping workflow with solution context support.
        
        Handles both:
        1. Unstructured → Structured (PDF → Excel)
        2. Structured → Structured (JSONL → Excel)
        
        Args:
            source_file_id: Source file identifier
            target_file_id: Target file identifier
            mapping_options: Optional mapping configuration
            user_context: Optional user context (includes workflow_id, session_id, solution_context)
        
        Returns:
        {
            "success": bool,
            "mapping_id": str,
            "mapping_type": "unstructured_to_structured" | "structured_to_structured",
            "mapping_rules": [...],
            "mapped_data": {...},
            "data_quality": {...},
            "cleanup_actions": [...],
            "output_file_id": str,
            "citations": [...],
            "confidence_scores": {...},
            "metadata": {...}
        }
        """
        # Store user_context for use in helper methods
        self.user_context = user_context
        
        try:
            mapping_id = f"mapping_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            self.logger.info(f"🚀 Starting data mapping workflow: {mapping_id}")
            
            # Step 1: Detect mapping type
            mapping_type = await self._detect_mapping_type(source_file_id, target_file_id)
            self.logger.info(f"📋 Mapping type detected: {mapping_type}")
            
            # Step 2: Extract schemas
            source_schema = await self._extract_source_schema(source_file_id, mapping_type)
            target_schema = await self._extract_target_schema(target_file_id)
            
            # Step 3: Get embeddings for semantic matching
            source_embeddings = await self._get_source_embeddings(source_file_id)
            target_embeddings = await self._get_target_embeddings(target_file_id)
            
            # Step 4: Generate mapping rules
            mapping_rules = await self._generate_mapping_rules(
                source_schema, target_schema,
                source_embeddings, target_embeddings
            )
            
            # Step 5: Extract/Transform data based on mapping type
            if mapping_type == "unstructured_to_structured":
                # Extract fields from unstructured source
                extracted_data = await self._extract_fields_from_unstructured(
                    source_file_id, mapping_rules
                )
            else:
                # Transform structured source data
                extracted_data = await self._get_structured_source_data(source_file_id)
            
            # Step 6: Validate data quality (for structured→structured)
            quality_results = None
            if mapping_type == "structured_to_structured":
                quality_results = await self._validate_data_quality(
                    extracted_data, target_schema, mapping_rules
                )
            
            # Step 7: Transform data to target format
            transformed_data = await self._transform_data(
                extracted_data, mapping_rules, target_schema, quality_results
            )
            
            # Step 8: Generate output file (already done in transformation service)
            output_file_id = transformed_data.get("output_file_id") if transformed_data.get("success") else None
            
            # Step 9: Generate cleanup actions (if quality issues found)
            cleanup_actions = None
            if quality_results and quality_results.get("has_issues"):
                cleanup_actions = await self._generate_cleanup_actions(quality_results, source_file_id)
            
            # Step 10: Track lineage
            await self._track_mapping_lineage(
                source_file_id, target_file_id, mapping_id, quality_results, user_context
            )
            
            self.logger.info(f"✅ Data mapping workflow complete: {mapping_id}")
            
            return {
                "success": True,
                "mapping_id": mapping_id,
                "mapping_type": mapping_type,
                "mapping_rules": mapping_rules,
                "mapped_data": transformed_data,
                "data_quality": quality_results,
                "cleanup_actions": cleanup_actions,
                "output_file_id": output_file_id,
                "citations": extracted_data.get("citations", []) if mapping_type == "unstructured_to_structured" else [],
                "confidence_scores": extracted_data.get("confidence_scores", {}) if mapping_type == "unstructured_to_structured" else {},
                "metadata": {
                    "source_file_id": source_file_id,
                    "target_file_id": target_file_id,
                    "mapping_timestamp": datetime.utcnow().isoformat(),
                    "workflow_id": user_context.get("workflow_id") if user_context else None
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data mapping workflow failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "mapping_id": mapping_id if 'mapping_id' in locals() else "unknown"
            }
    
    # ========================================================================
    # WORKFLOW STEPS
    # ========================================================================
    
    async def _detect_mapping_type(
        self,
        source_file_id: str,
        target_file_id: str
    ) -> str:
        """
        Detect mapping type based on source and target file types.
        
        Returns:
            "unstructured_to_structured" or "structured_to_structured"
        """
        try:
            # Get Content Steward to retrieve file metadata
            data_steward = await self.orchestrator.get_data_steward_api()
            if not data_steward:
                # Fallback: assume structured if can't determine
                self.logger.warning("⚠️ Content Steward not available, defaulting to structured→structured")
                return "structured_to_structured"
            
            # Get source file metadata
            source_file = await data_steward.get_file(source_file_id)
            source_file_type = source_file.get("file_type", "").lower() if source_file else ""
            
            # Get target file metadata
            target_file = await data_steward.get_file(target_file_id)
            target_file_type = target_file.get("file_type", "").lower() if target_file else ""
            
            # Determine mapping type
            unstructured_types = ["pdf", "docx", "doc", "txt", "rtf"]
            structured_types = ["xlsx", "xls", "csv", "json", "jsonl"]
            
            if source_file_type in unstructured_types:
                return "unstructured_to_structured"
            elif source_file_type in structured_types:
                return "structured_to_structured"
            else:
                # Default to structured→structured if unknown
                self.logger.warning(f"⚠️ Unknown source file type: {source_file_type}, defaulting to structured→structured")
                return "structured_to_structured"
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to detect mapping type: {e}, defaulting to structured→structured")
            return "structured_to_structured"
    
    async def _extract_source_schema(
        self,
        source_file_id: str,
        mapping_type: str
    ) -> Dict[str, Any]:
        """
        Extract schema from source file.
        
        For unstructured files: Use LLM to infer field schema
        For structured files: Extract column schema directly
        """
        try:
            self.logger.info(f"📋 Extracting source schema (mapping_type: {mapping_type})")
            
            # Get Data Mapping Agent
            from backend.insights.agents.data_mapping_agent import DataMappingAgent
            agent = DataMappingAgent(self.orchestrator)
            
            # Extract schema using agent
            schema = await agent.extract_source_schema(source_file_id, mapping_type)
            return schema
            
        except Exception as e:
            self.logger.error(f"❌ Source schema extraction failed: {e}")
            return {
                "schema_type": mapping_type,
                "fields": [],
                "error": str(e)
            }
    
    async def _extract_target_schema(
        self,
        target_file_id: str
    ) -> Dict[str, Any]:
        """Extract schema from target file."""
        try:
            self.logger.info(f"📋 Extracting target schema")
            
            # Get Data Mapping Agent
            from backend.insights.agents.data_mapping_agent import DataMappingAgent
            agent = DataMappingAgent(self.orchestrator)
            
            # Extract schema using agent
            schema = await agent.extract_target_schema(target_file_id)
            return schema
            
        except Exception as e:
            self.logger.error(f"❌ Target schema extraction failed: {e}")
            return {
                "schema_type": "structured",
                "fields": [],
                "error": str(e)
            }
    
    async def _get_source_embeddings(
        self,
        source_file_id: str
    ) -> List[Dict[str, Any]]:
        """Get embeddings for source file (for semantic matching)."""
        try:
            # Get Content Steward to find content metadata
            data_steward = await self.orchestrator.get_data_steward_api()
            if not data_steward:
                return []
            
            # Get parsed file to find content_metadata_id
            parsed_file = await data_steward.get_parsed_file(source_file_id)
            if not parsed_file:
                return []
            
            content_metadata_id = parsed_file.get("content_metadata_id")
            if not content_metadata_id:
                return []
            
            # Get embeddings from semantic data abstraction
            semantic_data = await self.orchestrator.get_infrastructure_abstraction("semantic_data")
            if semantic_data:
                embeddings = await semantic_data.get_embeddings(content_metadata_id)
                return embeddings if embeddings else []
            
            return []
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get source embeddings: {e}")
            return []
    
    async def _get_target_embeddings(
        self,
        target_file_id: str
    ) -> List[Dict[str, Any]]:
        """Get embeddings for target file (for semantic matching)."""
        try:
            # Get Content Steward to find content metadata
            data_steward = await self.orchestrator.get_data_steward_api()
            if not data_steward:
                return []
            
            # Get parsed file to find content_metadata_id
            parsed_file = await data_steward.get_parsed_file(target_file_id)
            if not parsed_file:
                return []
            
            content_metadata_id = parsed_file.get("content_metadata_id")
            if not content_metadata_id:
                return []
            
            # Get embeddings from semantic data abstraction
            semantic_data = await self.orchestrator.get_infrastructure_abstraction("semantic_data")
            if semantic_data:
                embeddings = await semantic_data.get_embeddings(content_metadata_id)
                return embeddings if embeddings else []
            
            return []
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to get target embeddings: {e}")
            return []
    
    async def _generate_mapping_rules(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_embeddings: List[Dict[str, Any]],
        target_embeddings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate mapping rules using semantic matching."""
        try:
            # Get Data Mapping Agent
            from backend.insights.agents.data_mapping_agent import DataMappingAgent
            agent = DataMappingAgent(self.orchestrator)
            
            # Generate mapping rules using agent
            mapping_rules = await agent.generate_mapping_rules(
                source_schema, target_schema, source_embeddings, target_embeddings
            )
            return mapping_rules
            
        except Exception as e:
            self.logger.error(f"❌ Mapping rule generation failed: {e}")
            return []
    
    async def _extract_fields_from_unstructured(
        self,
        source_file_id: str,
        mapping_rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract fields from unstructured source using Field Extraction Service."""
        try:
            field_extraction_service = await self.orchestrator._get_field_extraction_service()
            if not field_extraction_service:
                return {
                    "success": False,
                    "error": "Field Extraction Service not available"
                }
            
            # Build extraction schema from mapping rules
            extraction_schema = {
                "fields": [
                    {
                        "field_name": rule.get("source_field"),
                        "field_type": "string",  # Default, could be enhanced
                        "description": f"Extract {rule.get('source_field')}",
                        "patterns": [],  # Could be enhanced with patterns
                        "required": False
                    }
                    for rule in mapping_rules
                ]
            }
            
            # Extract fields
            result = await field_extraction_service.extract_fields(
                file_id=source_file_id,
                extraction_schema=extraction_schema
            )
            
            if result.get("success"):
                extracted_fields = result.get("extracted_fields", {})
                # Build citations and confidence scores
                citations = {}
                confidence_scores = {}
                for field_name, field_data in extracted_fields.items():
                    citations[field_name] = field_data.get("citation", "")
                    confidence_scores[field_name] = field_data.get("confidence", 0.0)
                
                return {
                    "success": True,
                    "extracted_fields": extracted_fields,
                    "citations": citations,
                    "confidence_scores": confidence_scores
                }
            else:
                return result
            
        except Exception as e:
            self.logger.error(f"❌ Field extraction failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_structured_source_data(
        self,
        source_file_id: str
    ) -> Dict[str, Any]:
        """Get structured source data."""
        try:
            # Get Content Steward to retrieve parsed file
            data_steward = await self.orchestrator.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "Content Steward not available"
                }
            
            # Get parsed file data
            parsed_file = await data_steward.get_parsed_file(source_file_id)
            if not parsed_file:
                return {
                    "success": False,
                    "error": f"Parsed file not found: {source_file_id}"
                }
            
            # Extract structured data from parsed file
            parsed_data = parsed_file.get("parsed_data") or parsed_file.get("data", {})
            
            # Handle different data formats
            records = []
            if isinstance(parsed_data, list):
                records = parsed_data
            elif isinstance(parsed_data, dict):
                if "rows" in parsed_data and "columns" in parsed_data:
                    # Table format: convert to records
                    columns = parsed_data["columns"]
                    rows = parsed_data["rows"]
                    for row in rows:
                        if isinstance(row, list):
                            record = {columns[i]: row[i] for i in range(min(len(columns), len(row)))}
                        elif isinstance(row, dict):
                            record = row
                        else:
                            continue
                        # Add record_id if not present
                        if "record_id" not in record:
                            record["record_id"] = f"record_{len(records)}"
                        records.append(record)
                elif "records" in parsed_data:
                    records = parsed_data["records"]
                else:
                    # Single record
                    records = [parsed_data]
            
            return {
                "success": True,
                "records": records,
                "schema": parsed_file.get("schema", {})
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get structured source data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _validate_data_quality(
        self,
        extracted_data: Dict[str, Any],
        target_schema: Dict[str, Any],
        mapping_rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate data quality using Data Quality Validation Service."""
        try:
            data_quality_service = await self.orchestrator._get_data_quality_validation_service()
            if not data_quality_service:
                return {
                    "success": False,
                    "error": "Data Quality Validation Service not available"
                }
            
            # Get records from extracted data
            records = extracted_data.get("records", [])
            if not records:
                return {
                    "success": True,
                    "overall_quality_score": 1.0,
                    "records_valid": 0,
                    "records_invalid": 0,
                    "has_issues": False,
                    "validation_results": [],
                    "summary": {
                        "total_records": 0,
                        "valid_records": 0,
                        "invalid_records": 0,
                        "overall_quality_score": 1.0,
                        "pass_rate": 1.0,
                        "common_issues": []
                    }
                }
            
            # Validate records
            quality_results = await data_quality_service.validate_records(
                records=records,
                target_schema=target_schema,
                mapping_rules=mapping_rules
            )
            
            return quality_results
            
        except Exception as e:
            self.logger.error(f"❌ Data quality validation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _transform_data(
        self,
        extracted_data: Dict[str, Any],
        mapping_rules: List[Dict[str, Any]],
        target_schema: Dict[str, Any],
        quality_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform data to target format using Data Transformation Service."""
        try:
            data_transformation_service = await self.orchestrator._get_data_transformation_service()
            if not data_transformation_service:
                return {
                    "success": False,
                    "error": "Data Transformation Service not available"
                }
            
            # Determine output format from target schema
            output_format = "excel"  # Default
            target_file_type = target_schema.get("file_type", "").lower()
            if target_file_type in ["json", "jsonl"]:
                output_format = "json"
            elif target_file_type == "csv":
                output_format = "csv"
            
            # Transform data
            transformation_result = await data_transformation_service.transform_data(
                source_data=extracted_data,
                mapping_rules=mapping_rules,
                target_schema=target_schema,
                output_format=output_format,
                quality_results=quality_results
            )
            
            return transformation_result
            
        except Exception as e:
            self.logger.error(f"❌ Data transformation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Removed _generate_output_file - now handled by Data Transformation Service
    
    async def _generate_cleanup_actions(
        self,
        quality_results: Dict[str, Any],
        source_file_id: str
    ) -> List[Dict[str, Any]]:
        """Generate cleanup actions using Data Quality Validation Service and Agent."""
        try:
            data_quality_service = await self.orchestrator._get_data_quality_validation_service()
            if not data_quality_service:
                return []
            
            # Generate cleanup actions using service
            cleanup_result = await data_quality_service.generate_cleanup_actions(
                validation_results=quality_results,
                source_file_id=source_file_id
            )
            
            if not cleanup_result.get("success"):
                return []
            
            cleanup_actions = cleanup_result.get("cleanup_actions", [])
            
            # Enhance with Data Quality Agent insights
            try:
                from backend.insights.agents.data_quality_agent import DataQualityAgent
                agent = DataQualityAgent(self.orchestrator)
                
                # Analyze quality issues
                quality_analysis = await agent.analyze_quality_issues(quality_results, source_file_id)
                
                # Enhance cleanup actions
                cleanup_actions = await agent.enhance_cleanup_actions(cleanup_actions, quality_analysis)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to enhance cleanup actions with agent: {e}")
            
            return cleanup_actions
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup action generation failed: {e}")
            return []
    
    async def _track_mapping_lineage(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_id: str,
        quality_results: Optional[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]]
    ):
        """Track data lineage for this mapping."""
        try:
            # Get Data Steward for lineage tracking
            data_steward = await self.orchestrator.get_data_steward_api()
            if data_steward:
                await data_steward.track_data_lineage({
                    "source": source_file_id,
                    "destination": target_file_id,
                    "transformation": {
                        "type": "data_mapping",
                        "mapping_id": mapping_id,
                        "orchestrator": "InsightsJourneyOrchestrator",
                        "quality_score": quality_results.get("overall_quality_score") if quality_results else None
                    }
                })
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to track lineage: {e}")

