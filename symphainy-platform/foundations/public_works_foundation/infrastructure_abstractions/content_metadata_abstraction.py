#!/usr/bin/env python3
"""
Content Metadata Abstraction - Business Logic Implementation

Implements content metadata operations with business logic.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I manage content metadata operations with business logic
HOW (Infrastructure Implementation): I implement business rules for content metadata
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..abstraction_contracts.content_metadata_protocol import ContentMetadataProtocol

logger = logging.getLogger(__name__)

class ContentMetadataAbstraction(ContentMetadataProtocol):
    """
    Content metadata abstraction with business logic.
    
    Implements content metadata operations with business rules,
    validation, and enhanced functionality for the platform.
    """
    
    def __init__(self, arango_adapter, config_adapter, di_container=None):
        """Initialize content metadata abstraction."""
        self.arango_adapter = arango_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "content_metadata_abstraction"
        
        # Collection names for ArangoDB
        self.content_metadata_collection = "content_metadata"
        self.content_relationships_collection = "content_relationships"
        self.content_schemas_collection = "content_schemas"
        self.content_insights_collection = "content_insights"
        self.analysis_collection = "content_analysis"
        # Note: Semantic data collections (embeddings, semantic graphs) moved to SemanticDataAbstraction
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Content Metadata Abstraction initialized")
    
    # ============================================================================
    # CORE CONTENT METADATA OPERATIONS WITH BUSINESS LOGIC
    # ============================================================================
    
    async def create_content_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create content metadata with business logic validation."""
        try:
            # Validate required fields
            required_fields = ["file_uuid", "content_type"]
            for field in required_fields:
                if field not in content_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate content ID if not provided
            content_id = content_data.get("content_id", str(uuid.uuid4()))
            
            # Add business logic metadata
            enhanced_content_data = {
                **content_data,
                "content_id": content_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": content_data.get("status", "active"),
                "version": content_data.get("version", 1),
                "analysis_status": content_data.get("analysis_status", "pending")
            }
            
            # Create content metadata using generic adapter method
            # Use content_id as the document key
            document = {**enhanced_content_data, "_key": content_id}
            result = await self.arango_adapter.create_document(
                self.content_metadata_collection,
                document
            )
            
            self.logger.info(f"✅ Content metadata created: {content_id} for file {content_data.get('file_uuid')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create content metadata: {e}")
            raise
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content metadata with business logic validation."""
        try:
            result = await self.arango_adapter.get_document(
                self.content_metadata_collection,
                content_id
            )
            
            if result:
                self.logger.debug(f"✅ Content metadata retrieved: {content_id}")
                
                # Record platform operation event
            else:
                self.logger.warning(f"⚠️ Content metadata not found: {content_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get content metadata {content_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_content_metadata(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update content metadata with business logic validation."""
        try:
            # Validate content exists
            existing_metadata = await self.get_content_metadata(content_id)
            if not existing_metadata:
                raise ValueError(f"Content metadata not found: {content_id}")
            
            # Add business logic to updates
            enhanced_updates = {
                **updates,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update content metadata using generic adapter method
            result = await self.arango_adapter.update_document(
                self.content_metadata_collection,
                content_id,
                enhanced_updates
            )
            
            self.logger.info(f"✅ Content metadata updated: {content_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update content metadata {content_id}: {e}")
            raise
    
    async def delete_content_metadata(self, content_id: str) -> bool:
        """Delete content metadata with business logic validation."""
        try:
            # Validate content exists
            existing_metadata = await self.get_content_metadata(content_id)
            if not existing_metadata:
                self.logger.warning(f"⚠️ Content metadata not found for deletion: {content_id}")
            
            # Check for relationships (business rule)
            relationships = await self.get_content_relationships(content_id, "both")
            if relationships:
                self.logger.warning(f"⚠️ Cannot delete content metadata with relationships: {content_id}")
                return False
            
            result = await self.arango_adapter.delete_document(
                self.content_metadata_collection,
                content_id
            )
            
            if result:
                self.logger.info(f"✅ Content metadata deleted: {content_id}")
                
                # Record platform operation event
            else:
                self.logger.error(f"❌ Failed to delete content metadata: {content_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete content metadata {content_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def search_content_metadata(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search content metadata with business logic filtering."""
        try:
            # Apply business logic filters
            enhanced_query = query.copy()
            
            # Add default filters
            if "status" not in enhanced_query:
                enhanced_query["status"] = "active"
            
            # Search content metadata using find_documents
            result = await self.arango_adapter.find_documents(
                self.content_metadata_collection,
                filter_conditions=enhanced_query
            )
            
            self.logger.debug(f"✅ Content metadata search returned {len(result)} results")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to search content metadata: {e}")
            raise  # Re-raise for service layer to handle
    
    async def analyze_content_structure(self, content_id: str) -> Dict[str, Any]:
        """Analyze content structure with business logic."""
        try:
            # Get content metadata
            content_metadata = await self.get_content_metadata(content_id)
            if not content_metadata:
                raise ValueError(f"Content metadata not found: {content_id}")
            
            # Analyze based on content type
            content_type = content_metadata.get("content_type", "unstructured")
            
            if content_type == "structured":
                analysis = await self._analyze_structured_content(content_metadata)
            elif content_type == "unstructured":
                analysis = await self._analyze_unstructured_content(content_metadata)
            elif content_type == "hybrid":
                analysis = await self._analyze_hybrid_content(content_metadata)
            else:
                analysis = {"error": f"Unknown content type: {content_type}"}
            
            # Update content metadata with analysis
            await self.update_content_metadata(content_id, {
                "structure_analysis": analysis,
                "analysis_status": "completed",
                "analysis_timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"✅ Content structure analyzed: {content_id}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze content structure {content_id}: {e}")
            raise
    
    async def extract_content_schema(self, content_id: str) -> Dict[str, Any]:
        """Extract content schema with business logic."""
        try:
            # Get content metadata
            content_metadata = await self.get_content_metadata(content_id)
            if not content_metadata:
                raise ValueError(f"Content metadata not found: {content_id}")
            
            # Extract schema based on content type
            content_type = content_metadata.get("content_type", "unstructured")
            
            if content_type in ["structured", "hybrid"]:
                schema = await self._extract_structured_schema(content_metadata)
            else:
                schema = await self._extract_unstructured_schema(content_metadata)
            
            # Store schema in ArangoDB using generic adapter method
            schema_id = str(uuid.uuid4())
            schema_document = {
                "_key": schema_id,
                "schema_id": schema_id,
                "content_id": content_id,
                "schema_type": content_type,
                "schema_data": schema,
                "extraction_timestamp": datetime.utcnow().isoformat()
            }
            schema_result = await self.arango_adapter.create_document(
                self.content_schemas_collection,
                schema_document
            )
            
            # Update content metadata with schema reference
            await self.update_content_metadata(content_id, {
                "schema_id": schema_result["_key"],
                "schema_extracted": True
            })
            
            self.logger.info(f"✅ Content schema extracted: {content_id}")
            
            return schema
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract content schema {content_id}: {e}")
            raise
    
    async def generate_content_insights(self, content_id: str) -> Dict[str, Any]:
        """Generate content insights with business logic."""
        try:
            # Get content metadata
            content_metadata = await self.get_content_metadata(content_id)
            if not content_metadata:
                raise ValueError(f"Content metadata not found: {content_id}")
            
            # Generate insights based on content type and structure
            insights = await self._generate_content_insights(content_metadata)
            
            # Store insights in ArangoDB using generic adapter method
            insight_id = str(uuid.uuid4())
            insight_document = {
                "_key": insight_id,
                "insight_id": insight_id,
                "content_id": content_id,
                "insight_type": "comprehensive_analysis",
                "insight_data": insights,
                "confidence_score": insights.get("confidence_score", 0.8),
                "generation_timestamp": datetime.utcnow().isoformat()
            }
            insight_result = await self.arango_adapter.create_document(
                self.content_insights_collection,
                insight_document
            )
            
            # Update content metadata with insights reference
            await self.update_content_metadata(content_id, {
                "insights_id": insight_result["_key"],
                "insights_generated": True
            })
            
            self.logger.info(f"✅ Content insights generated: {content_id}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate content insights {content_id}: {e}")
            raise
    
    # ============================================================================
    # CONTENT RELATIONSHIP OPERATIONS WITH BUSINESS LOGIC
    # ============================================================================
    
    async def create_content_relationship(self, parent_id: str, child_id: str, 
                                       relationship_type: str) -> Dict[str, Any]:
        """Create content relationship with business logic validation."""
        try:
            # Validate parent content exists
            parent_metadata = await self.get_content_metadata(parent_id)
            if not parent_metadata:
                raise ValueError(f"Parent content metadata not found: {parent_id}")
            
            # Validate child content exists
            child_metadata = await self.get_content_metadata(child_id)
            if not child_metadata:
                raise ValueError(f"Child content metadata not found: {child_id}")
            
            # Validate relationship type
            valid_relationship_types = [
                "derived_from", "parsed_from", "metadata_from", 
                "insights_from", "variant_of", "related_to"
            ]
            if relationship_type not in valid_relationship_types:
                raise ValueError(f"Invalid relationship type: {relationship_type}")
            
            # Create relationship using generic adapter method (as edge in graph)
            relationship_id = f"{parent_id}_{child_id}_{relationship_type}"
            relationship_document = {
                "_key": relationship_id,
                "_from": f"{self.content_metadata_collection}/{parent_id}",
                "_to": f"{self.content_metadata_collection}/{child_id}",
                "relationship_type": relationship_type,
                "created_at": datetime.utcnow().isoformat()
            }
            result = await self.arango_adapter.create_document(
                self.content_relationships_collection,
                relationship_document
            )
            
            self.logger.info(f"✅ Content relationship created: {parent_id} -> {child_id} ({relationship_type})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create content relationship: {e}")
            raise
    
    async def get_content_relationships(self, content_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        """Get content relationships with business logic validation."""
        try:
            # Validate content exists
            content_metadata = await self.get_content_metadata(content_id)
            if not content_metadata:
                self.logger.warning(f"⚠️ Content metadata not found for relationships: {content_id}")
            
            # Get relationships using AQL query
            if direction == "both":
                query = """
                    FOR edge IN @@collection
                        FILTER edge._from == @content_id OR edge._to == @content_id
                        RETURN edge
                """
            elif direction == "out":
                query = """
                    FOR edge IN @@collection
                        FILTER edge._from == @content_id
                        RETURN edge
                """
            else:  # direction == "in"
                query = """
                    FOR edge IN @@collection
                        FILTER edge._to == @content_id
                        RETURN edge
                """
            
            result = await self.arango_adapter.execute_aql(
                query,
                bind_vars={
                    "@collection": self.content_relationships_collection,
                    "content_id": f"{self.content_metadata_collection}/{content_id}"
                }
            )
            
            self.logger.debug(f"✅ Retrieved {len(result)} content relationships for {content_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get content relationships for {content_id}: {e}")
            raise
    
    async def perform_content_analysis(self, content_id: str) -> Dict[str, Any]:
        """Perform comprehensive content analysis with business logic."""
        try:
            # Get content metadata
            content_metadata = await self.get_content_metadata(content_id)
            if not content_metadata:
                raise ValueError(f"Content metadata not found: {content_id}")
            
            # Perform analysis steps
            analysis_steps = [
                ("structure_analysis", self.analyze_content_structure),
                ("schema_extraction", self.extract_content_schema),
                ("insights_generation", self.generate_content_insights)
            ]
            
            analysis_results = {}
            for step_name, step_function in analysis_steps:
                try:
                    result = await step_function(content_id)
                    analysis_results[step_name] = result
                except Exception as e:
                    self.logger.error(f"❌ Error: {e}")
                    self.logger.warning(f"⚠️ Analysis step {step_name} failed: {e}")
                    analysis_results[step_name] = {"error": str(e)}
            
            # Store comprehensive analysis
            analysis_result = await self.arango_adapter.create_document(
                self.analysis_collection,
                {
                    "analysis_id": str(uuid.uuid4()),
                    "content_id": content_id,
                    "analysis_results": analysis_results,
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "status": "completed"
                }
            )
            
            # Update content metadata with analysis reference
            await self.update_content_metadata(content_id, {
                "analysis_id": analysis_result["_key"],
                "analysis_completed": True
            })
            
            self.logger.info(f"✅ Content analysis completed: {content_id}")
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"❌ Failed to perform content analysis {content_id}: {e}")
            raise
    
    async def search_content_by_pattern(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search content by pattern with business logic."""
        try:
            # Apply business logic to pattern search
            enhanced_pattern = pattern.copy()
            
            # Add default filters
            if "status" not in enhanced_pattern:
                enhanced_pattern["status"] = "active"
            
            # Search content metadata using find_documents
            result = await self.arango_adapter.find_documents(
                self.content_metadata_collection,
                filter_conditions=enhanced_pattern
            )
            
            self.logger.debug(f"✅ Content pattern search returned {len(result)} results")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to search content by pattern: {e}")
            raise
    
    async def _analyze_structured_content(self, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze structured content (tables, CSV, etc.)."""
        # This would implement structured content analysis
        return {
            "content_type": "structured",
            "analysis": "Structured content analysis not implemented yet",
            "confidence_score": 0.8
        }
    
    async def _analyze_unstructured_content(self, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze unstructured content (text, documents, etc.)."""
        # This would implement unstructured content analysis
        return {
            "content_type": "unstructured",
            "analysis": "Unstructured content analysis not implemented yet",
            "confidence_score": 0.7
        }
    
    async def _analyze_hybrid_content(self, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hybrid content (PDFs with tables, etc.)."""
        # This would implement hybrid content analysis
        return {
            "content_type": "hybrid",
            "analysis": "Hybrid content analysis not implemented yet",
            "confidence_score": 0.75
        }
    
    async def _extract_structured_schema(self, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract schema from structured content."""
        # This would implement structured schema extraction
        return {
            "schema_type": "structured",
            "columns": [],
            "data_types": {},
            "constraints": []
        }
    
    async def _extract_unstructured_schema(self, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract schema from unstructured content."""
        # This would implement unstructured schema extraction
        return {
            "schema_type": "unstructured",
            "sections": [],
            "headers": [],
            "paragraphs": []
        }
    
    async def _generate_content_insights(self, content_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights from content metadata."""
        # This would implement insight generation
        return {
            "insight_type": "comprehensive_analysis",
            "business_meaning": "Content analysis not implemented yet",
            "data_quality": "unknown",
            "recommendations": []
        }
    
    # ============================================================================
    # NOTE: SEMANTIC DATA OPERATIONS MOVED TO SemanticDataAbstraction
    # ============================================================================
    # Semantic data operations (embeddings, semantic graphs) have been moved to
    # SemanticDataAbstraction to maintain clear separation of concerns:
    # - ContentMetadataAbstraction → Structural/parsing metadata only
    # - SemanticDataAbstraction → Embeddings and semantic graphs
    # ============================================================================
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health with business logic validation."""
        try:
            result = await self.arango_adapter.health_check()
            
            # Add business logic health checks
            if result.get("status") == "healthy":
                # Test content metadata operations
                test_search = await self.search_content_metadata({"status": "active"})
                result["business_logic"] = "operational"
                result["test_results"] = {"search_test": len(test_search)}
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            raise
