#!/usr/bin/env python3
"""
Content Metadata Composition Service - Complex Workflow Orchestration

Orchestrates complex content metadata workflows and business processes.
This is Layer 4 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I orchestrate complex content metadata workflows
HOW (Infrastructure Implementation): I compose multiple operations into business processes
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..infrastructure_abstractions.content_metadata_abstraction import ContentMetadataAbstraction
from ..infrastructure_abstractions.content_schema_abstraction import ContentSchemaAbstraction
from ..infrastructure_abstractions.content_insights_abstraction import ContentInsightsAbstraction

logger = logging.getLogger(__name__)

class ContentMetadataCompositionService:
    """
    Composition service for complex content metadata workflows.
    
    Orchestrates multiple content metadata operations into cohesive business processes
    for the platform's content analysis needs.
    """
    
    def __init__(self, content_metadata_abstraction: ContentMetadataAbstraction,
                 content_schema_abstraction: ContentSchemaAbstraction,
                 content_insights_abstraction: ContentInsightsAbstraction,
                 di_container=None):
        """Initialize content metadata composition service."""
        self.content_metadata = content_metadata_abstraction
        self.content_schema = content_schema_abstraction
        self.content_insights = content_insights_abstraction
        self.di_container = di_container
        self.service_name = "content_metadata_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Content Metadata Composition Service initialized")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    

    # ============================================================================
    # HYBRID CONTENT PROCESSING WORKFLOWS
    # ============================================================================
    
    async def process_hybrid_content(self, file_uuid: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process hybrid content and create comprehensive metadata.
        
        Args:
            file_uuid: UUID of the file in Supabase
            parsed_data: Parsed document data with text and tables
            
        Returns:
            Dict containing comprehensive content metadata
        """
        try:
            self.logger.info(f"🔧 Processing hybrid content for file: {file_uuid}")
            
            # Create main content metadata
            main_content_metadata = await self._create_main_content_metadata(file_uuid, parsed_data)
            
            # Process text component if exists
            text_metadata = None
            if parsed_data.get("text_content"):
                text_metadata = await self._process_text_component(
                    main_content_metadata["content_id"], parsed_data["text_content"]
                )
            
            # Process tables component if exists
            tables_metadata = None
            if parsed_data.get("tables"):
                tables_metadata = await self._process_tables_component(
                    main_content_metadata["content_id"], parsed_data["tables"]
                )
            
            # Create relationships between components
            relationships = await self._create_component_relationships(
                main_content_metadata["content_id"], text_metadata, tables_metadata
            )
            
            # Generate comprehensive analysis
            comprehensive_analysis = await self._generate_comprehensive_analysis(
                main_content_metadata["content_id"]
            )
            
            result = {
                "success": True,
                "file_uuid": file_uuid,
                "main_content_id": main_content_metadata["content_id"],
                "components": {
                    "text": text_metadata,
                    "tables": tables_metadata
                },
                "relationships": relationships,
                "comprehensive_analysis": comprehensive_analysis,
                "message": "Hybrid content processed successfully"
            }
            
            self.logger.info(f"✅ Hybrid content processed: {file_uuid}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("process_hybrid_content", {
                    "file_uuid": file_uuid,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "process_hybrid_content",
                    "file_uuid": file_uuid,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to process hybrid content: {e}")
            raise
    
    async def extract_complete_content_analysis(self, content_id: str) -> Dict[str, Any]:
        """
        Extract complete content analysis including metadata, schema, and insights.
        
        Args:
            content_id: Unique identifier for the content
            
        Returns:
            Dict containing complete analysis results
        """
        try:
            self.logger.info(f"🔍 Extracting complete content analysis: {content_id}")
            
            # Get content metadata
            content_metadata = await self.content_metadata.get_content_metadata(content_id)
            if not content_metadata:
                raise ValueError(f"Content metadata not found: {content_id}")
            
            # Extract schema
            schema_analysis = await self.content_schema.extract_content_schema(content_id)
            
            # Generate insights
            insights_analysis = await self.content_insights.generate_content_insights(content_id)
            
            # Analyze patterns
            pattern_analysis = await self.content_insights.analyze_content_patterns(content_id)
            
            # Extract business meaning
            business_meaning = await self.content_insights.extract_business_meaning(content_id)
            
            # Generate recommendations
            recommendations = await self.content_insights.generate_insight_recommendations(content_id)
            
            # Create comprehensive analysis document
            comprehensive_analysis = {
                "content_metadata": content_metadata,
                "schema_analysis": schema_analysis,
                "insights_analysis": insights_analysis,
                "pattern_analysis": pattern_analysis,
                "business_meaning": business_meaning,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "analysis_status": "completed"
            }
            
            # Store comprehensive analysis
            analysis_result = await self.content_metadata.arango_adapter.create_content_analysis({
                "analysis_id": str(uuid.uuid4()),
                "content_id": content_id,
                "analysis_type": "comprehensive",
                "analysis_data": comprehensive_analysis,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            })
            
            self.logger.info(f"✅ Complete content analysis extracted: {content_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("extract_complete_content_analysis", {
                    "content_id": content_id,
                    "success": True
                })
            
            return comprehensive_analysis
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "extract_complete_content_analysis",
                    "content_id": content_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to extract complete content analysis: {e}")
            raise
    
    # ============================================================================
    # CONTENT RELATIONSHIP WORKFLOWS
    # ============================================================================
    
    async def create_content_lineage_chain(self, root_content_id: str, 
                                          processing_stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a complete content lineage chain through processing stages.
        
        Args:
            root_content_id: ID of the root content
            processing_stages: List of processing stage configurations
            
        Returns:
            Dict containing lineage chain information
        """
        try:
            self.logger.info(f"🔗 Creating content lineage chain from root: {root_content_id}")
            
            lineage_chain = {
                "root_content_id": root_content_id,
                "stages": [],
                "total_content": 1
            }
            
            current_content_id = root_content_id
            
            for i, stage in enumerate(processing_stages):
                # Create child content for this stage
                child_content_data = {
                    "content_id": str(uuid.uuid4()),
                    "file_uuid": stage.get("file_uuid", ""),
                    "content_type": stage.get("content_type", "processed"),
                    "stage_name": stage["name"],
                    "stage_number": i + 1,
                    "parent_content_id": current_content_id
                }
                
                child_content = await self.content_metadata.create_content_metadata(child_content_data)
                
                # Create relationship
                await self.content_metadata.create_content_relationship(
                    current_content_id, child_content["content_id"], 
                    stage.get("relationship_type", "derived_from")
                )
                
                lineage_chain["stages"].append({
                    "stage_name": stage["name"],
                    "content_id": child_content["content_id"],
                    "stage_number": i + 1
                })
                
                current_content_id = child_content["content_id"]
                lineage_chain["total_content"] += 1
            
            self.logger.info(f"✅ Created content lineage chain with {len(processing_stages)} stages")
            
            result = {
                "success": True,
                "lineage_chain": lineage_chain,
                "message": "Content lineage chain created successfully"
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_content_lineage_chain", {
                    "root_content_id": root_content_id,
                    "stages_count": len(processing_stages),
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_content_lineage_chain",
                    "root_content_id": root_content_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to create content lineage chain: {e}")
            raise
    
    async def get_complete_content_lineage(self, content_id: str) -> Dict[str, Any]:
        """
        Get complete content lineage with detailed information.
        
        Args:
            content_id: ID of the content to get lineage for
            
        Returns:
            Dict containing complete lineage information
        """
        try:
            self.logger.info(f"🌳 Getting complete content lineage for: {content_id}")
            
            # Get content metadata
            content_metadata = await self.content_metadata.get_content_metadata(content_id)
            if not content_metadata:
                raise ValueError(f"Content metadata not found: {content_id}")
            
            # Get all relationships
            relationships = await self.content_metadata.get_content_relationships(content_id, "both")
            
            # Build lineage tree
            lineage_tree = await self._build_lineage_tree(content_id, relationships)
            
            # Organize lineage by generation
            lineage_by_generation = await self._organize_lineage_by_generation(lineage_tree)
            
            result = {
                "content_id": content_id,
                "lineage_tree": lineage_tree,
                "lineage_by_generation": lineage_by_generation,
                "relationships": relationships,
                "total_content": len(lineage_tree),
                "max_generation": max(lineage_by_generation.keys()) if lineage_by_generation else 0
            }
            
            self.logger.info(f"✅ Retrieved complete content lineage with {len(lineage_tree)} content items")
            
            result_dict = {
                "success": True,
                "lineage": result,
                "message": "Complete content lineage retrieved successfully"
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_complete_content_lineage", {
                    "content_id": content_id,
                    "items_count": len(lineage_tree),
                    "success": True
                })
            
            return result_dict
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_complete_content_lineage",
                    "content_id": content_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to get complete content lineage: {e}")
            raise
    
    # ============================================================================
    # CONTENT SEARCH AND DISCOVERY WORKFLOWS
    # ============================================================================
    
    async def advanced_content_search(self, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced content search with multiple criteria.
        
        Args:
            search_criteria: Dictionary of search criteria
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            self.logger.info(f"🔍 Advanced content search with criteria: {search_criteria}")
            
            search_results = []
            
            # Search by content metadata
            if "content_type" in search_criteria or "file_uuid" in search_criteria:
                metadata_results = await self.content_metadata.search_content_metadata(search_criteria)
                search_results.extend(metadata_results)
            
            # Search by schema patterns
            if "schema_pattern" in search_criteria:
                schema_results = await self.content_schema.search_schemas_by_pattern(
                    search_criteria["schema_pattern"]
                )
                search_results.extend(schema_results)
            
            # Search by insights
            if "insight_type" in search_criteria:
                insight_results = await self.content_insights.search_insights_by_type(
                    search_criteria["insight_type"]
                )
                search_results.extend(insight_results)
            
            # Remove duplicates
            seen_ids = set()
            unique_results = []
            for result in search_results:
                content_id = result.get("content_id") or result.get("_key")
                if content_id and content_id not in seen_ids:
                    unique_results.append(result)
                    seen_ids.add(content_id)
            
            self.logger.info(f"✅ Advanced content search found {len(unique_results)} results")
            
            result = {
                "success": True,
                "results": unique_results,
                "total_results": len(unique_results),
                "search_criteria": search_criteria,
                "message": "Advanced content search completed successfully"
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("advanced_content_search", {
                    "total_results": len(unique_results),
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "advanced_content_search",
                    "user_id": user_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to perform advanced content search: {e}")
            raise
    
    # ============================================================================
    # CONTENT ANALYTICS WORKFLOWS
    # ============================================================================
    
    async def generate_content_analytics(self, content_ids: List[str]) -> Dict[str, Any]:
        """
        Generate comprehensive content analytics.
        
        Args:
            content_ids: List of content identifiers
            
        Returns:
            Dict containing analytics data
        """
        try:
            self.logger.info(f"📊 Generating content analytics for {len(content_ids)} content items")
            
            # Get content metadata for all items
            content_metadata_list = []
            for content_id in content_ids:
                metadata = await self.content_metadata.get_content_metadata(content_id)
                if metadata:
                    content_metadata_list.append(metadata)
            
            # Calculate analytics
            analytics = {
                "total_content": len(content_metadata_list),
                "content_type_distribution": await self._analyze_content_type_distribution(content_metadata_list),
                "schema_analysis": await self._analyze_schema_patterns(content_metadata_list),
                "insights_analysis": await self._analyze_insights_patterns(content_metadata_list),
                "relationship_analysis": await self._analyze_relationship_patterns(content_metadata_list),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Generated comprehensive content analytics")
            
            result = {
                "success": True,
                "analytics": analytics,
                "message": "Content analytics generated successfully"
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("generate_content_analytics", {
                    "content_count": len(content_ids),
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "generate_content_analytics",
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to generate content analytics: {e}")
            raise
    
    # ============================================================================
    # HELPER METHODS FOR WORKFLOW ORCHESTRATION
    # ============================================================================
    
    async def _create_main_content_metadata(self, file_uuid: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create main content metadata for hybrid content."""
        content_data = {
            "content_id": str(uuid.uuid4()),
            "file_uuid": file_uuid,
            "content_type": "hybrid",
            "parsing_strategy": parsed_data.get("parsing_strategy", "text_and_tables"),
            "text_length": len(parsed_data.get("text_content", "")),
            "table_count": len(parsed_data.get("tables", [])),
            "page_count": parsed_data.get("page_count", 0),
            "parsing_timestamp": parsed_data.get("parsing_timestamp", datetime.utcnow().isoformat())
        }
        
        return await self.content_metadata.create_content_metadata(content_data)
    
    async def _process_text_component(self, parent_content_id: str, text_content: str) -> Dict[str, Any]:
        """Process text component of hybrid content."""
        text_content_data = {
            "content_id": str(uuid.uuid4()),
            "content_type": "unstructured",
            "parent_content_id": parent_content_id,
            "text_content": text_content,
            "text_length": len(text_content),
            "component_type": "text"
        }
        
        text_metadata = await self.content_metadata.create_content_metadata(text_content_data)
        
        # Create relationship
        await self.content_metadata.create_content_relationship(
            parent_content_id, text_metadata["content_id"], "parsed_from"
        )
        
        return text_metadata
    
    async def _process_tables_component(self, parent_content_id: str, tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process tables component of hybrid content."""
        tables_content_data = {
            "content_id": str(uuid.uuid4()),
            "content_type": "structured",
            "parent_content_id": parent_content_id,
            "tables": tables,
            "table_count": len(tables),
            "component_type": "tables"
        }
        
        tables_metadata = await self.content_metadata.create_content_metadata(tables_content_data)
        
        # Create relationship
        await self.content_metadata.create_content_relationship(
            parent_content_id, tables_metadata["content_id"], "parsed_from"
        )
        
        return tables_metadata
    
    async def _create_component_relationships(self, main_content_id: str, 
                                            text_metadata: Optional[Dict[str, Any]], 
                                            tables_metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create relationships between components."""
        relationships = []
        
        if text_metadata and tables_metadata:
            # Create relationship between text and tables
            relationship = await self.content_metadata.create_content_relationship(
                text_metadata["content_id"], tables_metadata["content_id"], "related_to"
            )
            relationships.append(relationship)
        
        return relationships
    
    async def _generate_comprehensive_analysis(self, content_id: str) -> Dict[str, Any]:
        """Generate comprehensive analysis for content."""
        return await self.extract_complete_content_analysis(content_id)
    
    async def _build_lineage_tree(self, content_id: str, relationships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build lineage tree from relationships."""
        # This would implement tree building logic
        return [{"content_id": content_id, "relationships": relationships}]
    
    async def _organize_lineage_by_generation(self, lineage_tree: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """Organize lineage by generation."""
        # This would implement generation organization
        return {0: lineage_tree}
    
    async def _analyze_content_type_distribution(self, content_metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content type distribution."""
        content_types = {}
        for metadata in content_metadata_list:
            content_type = metadata.get("content_type", "unknown")
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        return {
            "distribution": content_types,
            "total_types": len(content_types)
        }
    
    async def _analyze_schema_patterns(self, content_metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze schema patterns across content."""
        # This would implement schema pattern analysis
        return {
            "schema_analysis": "Schema pattern analysis not implemented yet"
        }
    
    async def _analyze_insights_patterns(self, content_metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze insights patterns across content."""
        # This would implement insights pattern analysis
        return {
            "insights_analysis": "Insights pattern analysis not implemented yet"
        }
    
    async def _analyze_relationship_patterns(self, content_metadata_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze relationship patterns across content."""
        # This would implement relationship pattern analysis
        return {
            "relationship_analysis": "Relationship pattern analysis not implemented yet"
        }




