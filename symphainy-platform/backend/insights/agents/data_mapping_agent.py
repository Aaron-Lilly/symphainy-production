#!/usr/bin/env python3
"""
Data Mapping Agent - Insights Realm

WHAT: Extracts schemas and generates mapping rules using semantic matching
HOW: Uses embeddings for semantic similarity and LLM for intelligent matching

This agent provides:
- Schema extraction (both unstructured and structured sources)
- Semantic matching using embeddings
- Mapping rule generation with confidence scores
"""

import os
import sys
import re
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../'))


class DataMappingAgent:
    """
    Data Mapping Agent - Extracts schemas and generates mapping rules.
    
    This is a simplified agent class that can be instantiated directly
    by the orchestrator (not via Agentic Foundation factory).
    """
    
    def __init__(self, orchestrator):
        """
        Initialize Data Mapping Agent.
        
        Args:
            orchestrator: InsightsJourneyOrchestrator instance (provides services)
        """
        self.orchestrator = orchestrator
        self.logger = orchestrator.logger if hasattr(orchestrator, 'logger') else None
        if not self.logger:
            import logging
            self.logger = logging.getLogger(__name__)
        
        # Services (lazy initialization)
        self._embedding_service = None
        self._data_steward = None
        self._llm_composition = None
    
    async def _get_embedding_service(self):
        """Get Embedding Service for semantic matching."""
        if self._embedding_service is None:
            try:
                from backend.content.services.embedding_service.embedding_service import EmbeddingService
                self._embedding_service = EmbeddingService(
                    service_name="EmbeddingService",
                    realm_name="content",
                    platform_gateway=self.orchestrator.platform_gateway,
                    di_container=self.orchestrator.di_container
                )
                await self._embedding_service.initialize()
            except Exception as e:
                self.logger.warning(f"⚠️ Embedding Service not available: {e}")
                return None
        return self._embedding_service
    
    # ❌ REMOVED: _get_content_steward() - Anti-pattern (direct service access)
    # Use execute_mcp_tool("content_get_parsed_file", ...) instead (unified pattern)
    
    async def _get_llm_composition(self):
        """Get LLM Composition Service."""
        if self._llm_composition is None:
            self._llm_composition = await self.orchestrator.get_business_abstraction("llm_composition")
        return self._llm_composition
    
    async def extract_source_schema(
        self,
        source_file_id: str,
        mapping_type: str
    ) -> Dict[str, Any]:
        """
        Extract schema from source file.
        
        For unstructured files: Use LLM to infer field schema
        For structured files: Extract column schema directly
        
        Args:
            source_file_id: Source file identifier
            mapping_type: "unstructured_to_structured" or "structured_to_structured"
        
        Returns:
        {
            "schema_type": str,
            "fields": [
                {
                    "field_name": str,
                    "field_type": str,
                    "description": str,
                    "required": bool
                },
                ...
            ]
        }
        """
        try:
            self.logger.info(f"📋 Extracting source schema (mapping_type: {mapping_type})")
            
            # Use cross-realm MCP tool access (unified pattern)
            # DataMappingAgent is in Insights realm but needs Content realm capabilities
            parsed_file_result = await self.execute_mcp_tool(
                "content_get_parsed_file",  # Cross-realm: Content realm MCP tool
                {"parsed_file_id": source_file_id}
            )
            
            if not parsed_file_result.get("success"):
                return {
                    "schema_type": mapping_type,
                    "fields": [],
                    "error": parsed_file_result.get("error", "Failed to get parsed file")
                }
            
            parsed_file = parsed_file_result
            
            if mapping_type == "unstructured_to_structured":
                # Use LLM to infer field schema from unstructured content
                text_content = parsed_file.get("parsed_content") or parsed_file.get("text_content", "")
                return await self._infer_schema_from_text(text_content)
            else:
                # Extract schema from structured data
                parsed_data = parsed_file.get("parsed_data") or parsed_file.get("data", {})
                return await self._extract_schema_from_structured(parsed_data)
            
        except Exception as e:
            self.logger.error(f"❌ Source schema extraction failed: {e}")
            return {
                "schema_type": mapping_type,
                "fields": [],
                "error": str(e)
            }
    
    async def _infer_schema_from_text(self, text_content: str) -> Dict[str, Any]:
        """Infer field schema from unstructured text using LLM."""
        try:
            llm_composition = await self._get_llm_composition()
            if not llm_composition:
                return {
                    "schema_type": "unstructured",
                    "fields": [],
                    "error": "LLM service not available"
                }
            
            prompt = f"""Analyze the following document and identify the key fields that should be extracted.

Document Text:
{text_content[:3000]}  # Limit for LLM

Please identify the key fields in this document and return a JSON schema:
{{
    "fields": [
        {{
            "field_name": "field_name",
            "field_type": "string|number|date|boolean",
            "description": "Description of the field",
            "required": true|false
        }}
    ]
}}

Focus on fields that would be useful for data mapping (dates, names, numbers, identifiers, etc.).
"""
            
            llm_response = await llm_composition.generate_text(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse LLM response
            import json
            response_text = llm_response.get("text", "") if isinstance(llm_response, dict) else str(llm_response)
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                schema = json.loads(json_match.group())
                return {
                    "schema_type": "unstructured",
                    "fields": schema.get("fields", []),
                    "extraction_method": "llm_inference"
                }
            else:
                # Fallback: return empty schema
                return {
                    "schema_type": "unstructured",
                    "fields": [],
                    "extraction_method": "fallback"
                }
            
        except Exception as e:
            self.logger.warning(f"⚠️ LLM schema inference failed: {e}")
            return {
                "schema_type": "unstructured",
                "fields": [],
                "error": str(e)
            }
    
    async def _extract_schema_from_structured(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract schema from structured data."""
        try:
            fields = []
            
            # Handle different structured data formats
            if "columns" in parsed_data:
                # Table-like structure
                columns = parsed_data["columns"]
                rows = parsed_data.get("rows", [])
                
                for col in columns:
                    # Infer type from sample data
                    field_type = "string"  # Default
                    if rows:
                        sample_value = rows[0].get(col) if isinstance(rows[0], dict) else rows[0][columns.index(col)] if isinstance(rows[0], list) else None
                        if sample_value is not None:
                            if isinstance(sample_value, (int, float)):
                                field_type = "number"
                            elif isinstance(sample_value, bool):
                                field_type = "boolean"
                            elif isinstance(sample_value, str):
                                # Check if it looks like a date
                                import re
                                if re.match(r'\d{4}-\d{2}-\d{2}', sample_value):
                                    field_type = "date"
                    
                    fields.append({
                        "field_name": col,
                        "field_type": field_type,
                        "description": f"Column: {col}",
                        "required": False  # Could be determined from data
                    })
            
            elif isinstance(parsed_data, list) and len(parsed_data) > 0:
                # List of records
                first_record = parsed_data[0]
                if isinstance(first_record, dict):
                    for key, value in first_record.items():
                        field_type = "string"
                        if isinstance(value, (int, float)):
                            field_type = "number"
                        elif isinstance(value, bool):
                            field_type = "boolean"
                        
                        fields.append({
                            "field_name": key,
                            "field_type": field_type,
                            "description": f"Field: {key}",
                            "required": False
                        })
            
            return {
                "schema_type": "structured",
                "fields": fields,
                "extraction_method": "direct_extraction"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Structured schema extraction failed: {e}")
            return {
                "schema_type": "structured",
                "fields": [],
                "error": str(e)
            }
    
    async def extract_target_schema(
        self,
        target_file_id: str
    ) -> Dict[str, Any]:
        """Extract schema from target file."""
        try:
            self.logger.info(f"📋 Extracting target schema")
            
            # Use cross-realm MCP tool access (unified pattern)
            # DataMappingAgent is in Insights realm but needs Content realm capabilities
            parsed_file_result = await self.execute_mcp_tool(
                "content_get_parsed_file",  # Cross-realm: Content realm MCP tool
                {"parsed_file_id": target_file_id}
            )
            
            if not parsed_file_result.get("success"):
                return {
                    "schema_type": "structured",
                    "fields": [],
                    "error": parsed_file_result.get("error", "Failed to get parsed file")
                }
            
            parsed_file = parsed_file_result
            
            # Extract schema from structured target
            parsed_data = parsed_file.get("parsed_data") or parsed_file.get("data", {})
            return await self._extract_schema_from_structured(parsed_data)
            
        except Exception as e:
            self.logger.error(f"❌ Target schema extraction failed: {e}")
            return {
                "schema_type": "structured",
                "fields": [],
                "error": str(e)
            }
    
    async def generate_mapping_rules(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_embeddings: List[Dict[str, Any]],
        target_embeddings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate mapping rules using semantic matching.
        
        Uses embeddings for semantic similarity matching.
        Falls back to LLM if embeddings not available.
        
        Returns:
        [
            {
                "source_field": "license_expiration_date",
                "target_field": "Expiration Date",
                "confidence": 0.95,
                "matching_method": "semantic_embedding",
                "transformation": "date_format"
            },
            ...
        ]
        """
        try:
            self.logger.info("🔗 Generating mapping rules")
            
            source_fields = source_schema.get("fields", [])
            target_fields = target_schema.get("fields", [])
            
            mapping_rules = []
            
            # Try semantic matching first (if embeddings available)
            if source_embeddings and target_embeddings:
                for source_field in source_fields:
                    source_field_name = source_field.get("field_name")
                    best_match = None
                    best_similarity = 0.0
                    
                    # Find source field embedding
                    source_embedding = None
                    for emb in source_embeddings:
                        if emb.get("column_name") == source_field_name or emb.get("field_name") == source_field_name:
                            source_embedding = emb.get("meaning_embedding")
                            break
                    
                    if source_embedding:
                        # Compare with target embeddings
                        for target_field in target_fields:
                            target_field_name = target_field.get("field_name")
                            
                            # Find target field embedding
                            target_embedding = None
                            for emb in target_embeddings:
                                if emb.get("column_name") == target_field_name or emb.get("field_name") == target_field_name:
                                    target_embedding = emb.get("meaning_embedding")
                                    break
                            
                            if target_embedding:
                                # Calculate cosine similarity
                                similarity = self._cosine_similarity(source_embedding, target_embedding)
                                if similarity > best_similarity:
                                    best_similarity = similarity
                                    best_match = target_field_name
                    
                    if best_match and best_similarity > 0.7:  # Threshold for good match
                        mapping_rules.append({
                            "source_field": source_field_name,
                            "target_field": best_match,
                            "confidence": best_similarity,
                            "matching_method": "semantic_embedding",
                            "transformation": self._determine_transformation(
                                source_field.get("field_type"),
                                next((f for f in target_fields if f.get("field_name") == best_match), {}).get("field_type")
                            )
                        })
            
            # Fallback: Use LLM for matching if embeddings not available or low confidence
            if not mapping_rules or len(mapping_rules) < len(source_fields) * 0.5:
                llm_rules = await self._generate_mapping_rules_with_llm(source_schema, target_schema)
                # Merge with existing rules (don't duplicate)
                existing_targets = {r["target_field"] for r in mapping_rules}
                for rule in llm_rules:
                    if rule["target_field"] not in existing_targets:
                        mapping_rules.append(rule)
            
            self.logger.info(f"✅ Generated {len(mapping_rules)} mapping rules")
            return mapping_rules
            
        except Exception as e:
            self.logger.error(f"❌ Mapping rule generation failed: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import numpy as np
            
            if not isinstance(vec1, list) or not isinstance(vec2, list):
                return 0.0
            
            if len(vec1) != len(vec2):
                return 0.0
            
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except ImportError:
            # Fallback: manual calculation if numpy not available
            try:
                if not isinstance(vec1, list) or not isinstance(vec2, list):
                    return 0.0
                if len(vec1) != len(vec2):
                    return 0.0
                
                dot_product = sum(a * b for a, b in zip(vec1, vec2))
                norm1 = sum(a * a for a in vec1) ** 0.5
                norm2 = sum(b * b for b in vec2) ** 0.5
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                return float(dot_product / (norm1 * norm2))
            except Exception as e:
                self.logger.warning(f"⚠️ Cosine similarity calculation failed: {e}")
                return 0.0
        except Exception as e:
            self.logger.warning(f"⚠️ Cosine similarity calculation failed: {e}")
            return 0.0
    
    def _determine_transformation(self, source_type: str, target_type: str) -> Optional[str]:
        """Determine transformation needed between source and target types."""
        if source_type == target_type:
            return None
        
        if source_type == "date" and target_type == "date":
            return "date_format"  # May need format conversion
        
        if source_type in ["string", "text"] and target_type in ["number", "integer", "float"]:
            return "to_number"
        
        if target_type == "string":
            return "to_string"
        
        return None
    
    async def _generate_mapping_rules_with_llm(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate mapping rules using LLM."""
        try:
            llm_composition = await self._get_llm_composition()
            if not llm_composition:
                return []
            
            source_fields = source_schema.get("fields", [])
            target_fields = target_schema.get("fields", [])
            
            prompt = f"""Match source fields to target fields based on their names and descriptions.

Source Fields:
{json.dumps(source_fields, indent=2)}

Target Fields:
{json.dumps(target_fields, indent=2)}

For each source field, find the best matching target field and return JSON:
{{
    "mappings": [
        {{
            "source_field": "source_field_name",
            "target_field": "target_field_name",
            "confidence": 0.0-1.0,
            "matching_method": "llm_semantic",
            "transformation": "transformation_type_if_needed"
        }}
    ]
}}
"""
            
            llm_response = await llm_composition.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1
            )
            
            # Parse LLM response
            import json
            response_text = llm_response.get("text", "") if isinstance(llm_response, dict) else str(llm_response)
            
            # Try to find JSON object (may be nested)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result.get("mappings", [])
                except json.JSONDecodeError:
                    pass
            
            return []
            
        except Exception as e:
            self.logger.warning(f"⚠️ LLM mapping rule generation failed: {e}")
            return []

