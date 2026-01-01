#!/usr/bin/env python3
"""
Librarian Service - Search Module

Micro-module for knowledge search operations.
"""

from typing import Any, Dict, Optional


class Search:
    """Search module for Librarian service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def search_knowledge(self, query: str, filters: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Search knowledge base using Knowledge Discovery Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "search_knowledge_start",
            success=True,
            details={"query": query[:50] if query else "empty"}  # Truncate for telemetry
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "read"):
                        await self.service.record_health_metric("search_knowledge_access_denied", 1.0, {"query": query[:50] if query else "empty"})
                        await self.service.log_operation_with_telemetry("search_knowledge_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to search knowledge")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("search_knowledge_tenant_denied", 1.0, {"query": query[:50] if query else "empty", "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("search_knowledge_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Search using Knowledge Discovery Abstraction
            from foundations.public_works_foundation.abstraction_contracts.knowledge_discovery_protocol import SearchMode
            
            search_results = await self.service.knowledge_discovery_abstraction.search_knowledge(
                query=query,
                search_mode=SearchMode.HYBRID,
                filters=filters,
                limit=20,
                offset=0
            )
            
            result_count = len(search_results.get("hits", [])) if search_results else 0
            
            # Record health metric
            await self.service.record_health_metric(
                "knowledge_search_completed",
                1.0,
                {"query": query[:50] if query else "empty", "result_count": result_count}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "search_knowledge_complete",
                success=True,
                details={"query": query[:50] if query else "empty", "result_count": result_count}
            )
            
            if search_results:
                return {
                    "query": query,
                    "filters": filters,
                    "results": search_results.get("hits", []),
                    "total_results": search_results.get("totalHits", 0),
                    "status": "success"
                }
            else:
                return {
                    "query": query,
                    "filters": filters,
                    "results": [],
                    "total_results": 0,
                    "status": "success"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "search_knowledge")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "search_knowledge_complete",
                success=False,
                details={"query": query[:50] if query else "empty", "error": str(e)}
            )
            return {
                "query": query,
                "filters": filters,
                "results": [],
                "total_results": 0,
                "error": str(e),
                "status": "error"
            }
    
    async def semantic_search(self, concept: str, context: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform semantic search using Knowledge Discovery Abstraction."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "semantic_search_start",
            success=True,
            details={"concept": concept[:50] if concept else "empty"}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "read"):
                        await self.service.record_health_metric("semantic_search_access_denied", 1.0, {"concept": concept[:50] if concept else "empty"})
                        await self.service.log_operation_with_telemetry("semantic_search_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to perform semantic search")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("semantic_search_tenant_denied", 1.0, {"concept": concept[:50] if concept else "empty", "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("semantic_search_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Semantic search using Knowledge Discovery Abstraction
            similarity_threshold = context.get("similarity_threshold", 0.7) if context else 0.7
            max_results = context.get("max_results", 10) if context else 10
            
            semantic_results = await self.service.knowledge_discovery_abstraction.semantic_search(
                query=concept,
                similarity_threshold=similarity_threshold,
                max_results=max_results
            )
            
            result_count = len(semantic_results) if semantic_results else 0
            
            # Record health metric
            await self.service.record_health_metric(
                "semantic_search_completed",
                1.0,
                {"concept": concept[:50] if concept else "empty", "result_count": result_count}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "semantic_search_complete",
                success=True,
                details={"concept": concept[:50] if concept else "empty", "result_count": result_count}
            )
            
            if semantic_results:
                return {
                    "concept": concept,
                    "context": context,
                    "results": semantic_results,
                    "status": "success"
                }
            else:
                return {
                    "concept": concept,
                    "context": context,
                    "results": [],
                    "status": "success"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "semantic_search")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "semantic_search_complete",
                success=False,
                details={"concept": concept[:50] if concept else "empty", "error": str(e)}
            )
            return {
                "concept": concept,
                "context": context,
                "results": [],
                "error": str(e),
                "status": "error"
            }
    
    async def get_semantic_relationships(self, concept: str) -> Dict[str, Any]:
        """Get semantic relationships using Knowledge Discovery Abstraction."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get relationships using Knowledge Discovery Abstraction
            relationships = await self.service.knowledge_discovery_abstraction.discover_related_knowledge(
                asset_id=concept,
                relationship_types=None,
                max_depth=2
            )
            
            if relationships:
                if self.service.logger:
                    self.service.logger.info(f"✅ Semantic relationships retrieved: {len(relationships)} relationships")
                return {
                    "concept": concept,
                    "relationships": relationships,
                    "status": "success"
                }
            else:
                return {
                    "concept": concept,
                    "relationships": [],
                    "status": "success"
                }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error getting semantic relationships: {str(e)}")
            return {
                "concept": concept,
                "relationships": [],
                "error": str(e),
                "status": "error"
            }







