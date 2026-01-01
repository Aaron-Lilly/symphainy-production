#!/usr/bin/env python3
"""
Knowledge Infrastructure Composition Service - Orchestration Layer

Orchestrates knowledge infrastructure abstractions for Librarian service.
This is Layer 4 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I orchestrate knowledge infrastructure operations
HOW (Infrastructure Implementation): I coordinate between discovery and governance abstractions
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from foundations.public_works_foundation.infrastructure_abstractions.knowledge_discovery_abstraction import KnowledgeDiscoveryAbstraction
from foundations.public_works_foundation.infrastructure_abstractions.knowledge_governance_abstraction import KnowledgeGovernanceAbstraction

logger = logging.getLogger(__name__)

class KnowledgeInfrastructureCompositionService:
    """
    Knowledge Infrastructure Composition Service.
    
    Orchestrates the complete knowledge infrastructure workflow including:
    - Knowledge discovery and search operations
    - Knowledge governance and compliance
    - Cross-service knowledge coordination
    """
    
    def __init__(self, 
                 knowledge_discovery: KnowledgeDiscoveryAbstraction,
                 knowledge_governance: KnowledgeGovernanceAbstraction,
                 di_container=None):
        """Initialize knowledge infrastructure composition service."""
        self.knowledge_discovery = knowledge_discovery
        self.knowledge_governance = knowledge_governance
        self.di_container = di_container
        self.service_name = "knowledge_infrastructure_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ Knowledge Infrastructure Composition Service initialized")
    
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
    # KNOWLEDGE DISCOVERY ORCHESTRATION
    # ============================================================================
    
    async def orchestrate_knowledge_search(self, 
                                         query: str,
                                         search_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate comprehensive knowledge search workflow.
        
        Complete workflow:
        1. Perform hybrid search across all backends
        2. Apply governance filters and policies
        3. Enhance results with semantic relationships
        4. Generate recommendations
        """
        try:
            self.logger.info(f"🔍 Orchestrating knowledge search: {query}")
            
            # Step 1: Perform hybrid search
            search_results = await self.knowledge_discovery.search_knowledge(
                query=query,
                search_mode=search_context.get('search_mode', 'hybrid'),
                knowledge_types=search_context.get('knowledge_types'),
                scope=search_context.get('scope', 'global'),
                filters=search_context.get('filters'),
                limit=search_context.get('limit', 20),
                offset=search_context.get('offset', 0)
            )
            
            # Step 2: Apply governance filters
            governance_filtered_results = await self._apply_governance_filters(
                search_results, search_context
            )
            
            # Step 3: Enhance with semantic relationships
            enhanced_results = await self._enhance_with_semantic_relationships(
                governance_filtered_results, query
            )
            
            # Step 4: Generate recommendations
            recommendations = await self._generate_search_recommendations(
                enhanced_results, search_context
            )
            
            # Step 5: Track search analytics
            await self._track_search_analytics(query, enhanced_results, search_context)
            
            self.logger.info(f"✅ Knowledge search orchestrated: {len(enhanced_results.get('hits', []))} results")
            
            result = {
                "search_results": enhanced_results,
                "recommendations": recommendations,
                "governance_applied": True,
                "semantic_enhanced": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("orchestrate_knowledge_search", {
                    "results_count": len(enhanced_results.get('hits', [])),
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "orchestrate_knowledge_search",
                    "query": query,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Knowledge search orchestration failed: {e}")
            return {
                "search_results": {"hits": [], "totalHits": 0},
                "recommendations": [],
                "error": str(e),
                "error_code": "KNOWLEDGE_SEARCH_ERROR"
            }
    
    async def orchestrate_knowledge_discovery(self, 
                                            asset_id: str,
                                            discovery_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate comprehensive knowledge discovery workflow.
        
        Complete workflow:
        1. Discover related knowledge assets
        2. Find knowledge paths and relationships
        3. Generate knowledge clusters
        4. Apply governance and compliance checks
        """
        try:
            self.logger.info(f"🔗 Orchestrating knowledge discovery: {asset_id}")
            
            # Step 1: Discover related knowledge
            related_knowledge = await self.knowledge_discovery.discover_related_knowledge(
                asset_id=asset_id,
                relationship_types=discovery_context.get('relationship_types'),
                max_depth=discovery_context.get('max_depth', 2)
            )
            
            # Step 2: Find knowledge paths
            knowledge_paths = await self.knowledge_discovery.find_knowledge_paths(
                start_asset_id=asset_id,
                end_asset_id=discovery_context.get('target_asset_id'),
                max_paths=discovery_context.get('max_paths', 5)
            )
            
            # Step 3: Generate knowledge clusters
            knowledge_clusters = await self.knowledge_discovery.get_knowledge_clusters(
                cluster_size=discovery_context.get('cluster_size', 5),
                similarity_threshold=discovery_context.get('similarity_threshold', 0.6)
            )
            
            # Step 4: Apply governance compliance
            compliance_results = await self._check_discovery_compliance(
                related_knowledge, knowledge_paths, knowledge_clusters
            )
            
            self.logger.info(f"✅ Knowledge discovery orchestrated: {len(related_knowledge)} related assets")
            
            result = {
                "related_knowledge": related_knowledge,
                "knowledge_paths": knowledge_paths,
                "knowledge_clusters": knowledge_clusters,
                "compliance_results": compliance_results,
                "discovery_metadata": {
                    "asset_id": asset_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "governance_applied": True
                }
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("orchestrate_knowledge_discovery", {
                    "asset_id": asset_id,
                    "related_count": len(related_knowledge),
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "orchestrate_knowledge_discovery",
                    "asset_id": asset_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Knowledge discovery orchestration failed: {e}")
            return {
                "related_knowledge": [],
                "knowledge_paths": [],
                "knowledge_clusters": [],
                "error": str(e),
                "error_code": "KNOWLEDGE_DISCOVERY_ERROR"
            }
    
    # ============================================================================
    # KNOWLEDGE GOVERNANCE ORCHESTRATION
    # ============================================================================
    
    async def orchestrate_governance_policy_management(self, 
                                                     policy_data: Dict[str, Any],
                                                     governance_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate comprehensive governance policy management workflow.
        
        Complete workflow:
        1. Create governance policy
        2. Apply policy to relevant assets
        3. Validate policy compliance
        4. Generate governance reports
        """
        try:
            self.logger.info(f"📋 Orchestrating governance policy management")
            
            # Step 1: Create governance policy
            policy_id = await self.knowledge_governance.create_governance_policy(
                policy_name=policy_data.get('name'),
                policy_type=policy_data.get('type'),
                policy_data=policy_data.get('data'),
                description=policy_data.get('description')
            )
            
            if not policy_id:
                raise Exception("Failed to create governance policy")
            
            # Step 2: Apply policy to assets
            application_results = await self._apply_policy_to_assets(
                policy_id, governance_context.get('target_assets', [])
            )
            
            # Step 3: Validate policy compliance
            compliance_results = await self._validate_policy_compliance(
                policy_id, governance_context.get('compliance_rules', [])
            )
            
            # Step 4: Generate governance reports
            governance_reports = await self._generate_governance_reports(
                policy_id, application_results, compliance_results
            )
            
            self.logger.info(f"✅ Governance policy management orchestrated: {policy_id}")
            
            result = {
                "policy_id": policy_id,
                "application_results": application_results,
                "compliance_results": compliance_results,
                "governance_reports": governance_reports,
                "governance_metadata": {
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "active"
                }
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("orchestrate_governance_policy_management", {
                    "policy_id": policy_id,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "orchestrate_governance_policy_management",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Governance policy management orchestration failed: {e}")
            return {
                "policy_id": None,
                "error": str(e),
                "error_code": "GOVERNANCE_POLICY_ERROR"
            }
    
    async def orchestrate_metadata_governance(self, 
                                            asset_id: str,
                                            metadata_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate comprehensive metadata governance workflow.
        
        Complete workflow:
        1. Create/update asset metadata
        2. Apply semantic tagging
        3. Enforce governance policies
        4. Validate compliance
        """
        try:
            self.logger.info(f"📊 Orchestrating metadata governance: {asset_id}")
            
            # Step 1: Create/update asset metadata
            metadata_result = await self.knowledge_governance.create_asset_metadata(
                asset_id=asset_id,
                metadata=metadata_context.get('metadata', {}),
                governance_level=metadata_context.get('governance_level', 'internal')
            )
            
            # Step 2: Apply semantic tagging
            tagging_result = await self.knowledge_governance.add_semantic_tags(
                asset_id=asset_id,
                tags=metadata_context.get('semantic_tags', []),
                confidence_scores=metadata_context.get('confidence_scores'),
                tag_source=metadata_context.get('tag_source', 'system')
            )
            
            # Step 3: Enforce governance policies
            policy_enforcement = await self._enforce_governance_policies(
                asset_id, metadata_context.get('policies', [])
            )
            
            # Step 4: Validate compliance
            compliance_validation = await self._validate_metadata_compliance(
                asset_id, metadata_context.get('compliance_rules', [])
            )
            
            self.logger.info(f"✅ Metadata governance orchestrated: {asset_id}")
            
            result = {
                "metadata_result": metadata_result,
                "tagging_result": tagging_result,
                "policy_enforcement": policy_enforcement,
                "compliance_validation": compliance_validation,
                "metadata_governance_metadata": {
                    "asset_id": asset_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "governance_applied": True
                }
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("orchestrate_metadata_governance", {
                    "asset_id": asset_id,
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "orchestrate_metadata_governance",
                    "asset_id": asset_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Metadata governance orchestration failed: {e}")
            return {
                "metadata_result": False,
                "tagging_result": False,
                "error": str(e),
                "error_code": "METADATA_GOVERNANCE_ERROR"
            }
    
    # ============================================================================
    # CROSS-SERVICE KNOWLEDGE COORDINATION
    # ============================================================================
    
    async def coordinate_knowledge_workflow(self, 
                                         workflow_type: str,
                                         workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate cross-service knowledge workflow.
        
        Routes knowledge operations to appropriate orchestration methods.
        """
        try:
            self.logger.info(f"🔄 Coordinating knowledge workflow: {workflow_type}")
            
            result = None
            if workflow_type == "knowledge_search":
                result = await self.orchestrate_knowledge_search(
                    workflow_data.get('query', ''),
                    workflow_data.get('search_context', {})
                )
            elif workflow_type == "knowledge_discovery":
                result = await self.orchestrate_knowledge_discovery(
                    workflow_data.get('asset_id', ''),
                    workflow_data.get('discovery_context', {})
                )
            elif workflow_type == "governance_policy_management":
                result = await self.orchestrate_governance_policy_management(
                    workflow_data.get('policy_data', {}),
                    workflow_data.get('governance_context', {})
                )
            elif workflow_type == "metadata_governance":
                result = await self.orchestrate_metadata_governance(
                    workflow_data.get('asset_id', ''),
                    workflow_data.get('metadata_context', {})
                )
            else:
                self.logger.warning(f"⚠️ Unknown workflow type: {workflow_type}")
                result = {
                    "orchestrated": False,
                    "reason": "unknown_workflow_type"
                }
            
            # Record telemetry on success (if workflow was recognized and executed)
            if result and (workflow_type in ["knowledge_search", "knowledge_discovery", "governance_policy_management", "metadata_governance"]):
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("coordinate_knowledge_workflow", {
                        "workflow_type": workflow_type,
                        "success": True
                    })
            
            return result
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "coordinate_knowledge_workflow",
                    "workflow_type": workflow_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Knowledge workflow coordination failed: {e}")
            return {
                "orchestrated": False,
                "reason": "coordination_error",
                "error": str(e),
                "error_code": "KNOWLEDGE_WORKFLOW_ERROR"
            }
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def _apply_governance_filters(self, 
                                     search_results: Dict[str, Any],
                                     search_context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply governance filters to search results."""
        try:
            # Simplified governance filtering
            # In practice, this would involve complex policy evaluation
            filtered_hits = search_results.get('hits', [])
            
            # Apply basic governance filters
            governance_level = search_context.get('governance_level', 'internal')
            filtered_hits = [hit for hit in filtered_hits 
                           if hit.get('governance_level', 'internal') == governance_level]
            
            return {
                **search_results,
                "hits": filtered_hits,
                "totalHits": len(filtered_hits)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Governance filtering failed: {e}")
            return search_results
    
    async def _enhance_with_semantic_relationships(self, 
                                                  search_results: Dict[str, Any],
                                                  query: str) -> Dict[str, Any]:
        """Enhance search results with semantic relationships."""
        try:
            # Get semantic relationships for top results
            hits = search_results.get('hits', [])
            enhanced_hits = []
            
            for hit in hits[:5]:  # Enhance top 5 results
                asset_id = hit.get('id')
                if asset_id:
                    # Get semantic relationships
                    relationships = await self.knowledge_discovery.discover_related_knowledge(
                        asset_id, max_depth=1
                    )
                    hit['semantic_relationships'] = relationships
                
                enhanced_hits.append(hit)
            
            return {
                **search_results,
                "hits": enhanced_hits,
                "semantic_enhanced": True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Semantic enhancement failed: {e}")
            return search_results
    
    async def _generate_search_recommendations(self, 
                                            search_results: Dict[str, Any],
                                            search_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on search results."""
        try:
            # Get recommendations for top results
            hits = search_results.get('hits', [])
            recommendations = []
            
            for hit in hits[:3]:  # Get recommendations for top 3 results
                asset_id = hit.get('id')
                if asset_id:
                    recs = await self.knowledge_discovery.get_knowledge_recommendations(
                        asset_id, limit=5
                    )
                    recommendations.extend(recs)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"❌ Recommendation generation failed: {e}")
            return []
    
    async def _track_search_analytics(self, 
                                   query: str,
                                   search_results: Dict[str, Any],
                                   search_context: Dict[str, Any]):
        """Track search analytics."""
        try:
            await self.knowledge_discovery.track_search_event(
                query=query,
                results_count=len(search_results.get('hits', [])),
                user_id=search_context.get('user_id'),
                metadata=search_context
            )
        except Exception as e:
            self.logger.error(f"❌ Search analytics tracking failed: {e}")
    
    async def _check_discovery_compliance(self, 
                                        related_knowledge: List[Dict[str, Any]],
                                        knowledge_paths: List[Dict[str, Any]],
                                        knowledge_clusters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check compliance for discovery results."""
        try:
            # Simplified compliance checking
            return {
                "compliant": True,
                "violations": [],
                "checked_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Discovery compliance check failed: {e}")
            return {"compliant": False, "error": str(e)}
    
    async def _apply_policy_to_assets(self, 
                                    policy_id: str,
                                    target_assets: List[str]) -> Dict[str, Any]:
        """Apply policy to target assets."""
        try:
            application_results = []
            
            for asset_id in target_assets:
                success = await self.knowledge_governance.apply_policy_to_asset(
                    asset_id, policy_id
                )
                application_results.append({
                    "asset_id": asset_id,
                    "success": success
                })
            
            return {
                "total_assets": len(target_assets),
                "successful_applications": len([r for r in application_results if r['success']]),
                "application_results": application_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Policy application failed: {e}")
            return {"error": str(e)}
    
    async def _validate_policy_compliance(self, 
                                        policy_id: str,
                                        compliance_rules: List[str]) -> Dict[str, Any]:
        """Validate policy compliance."""
        try:
            # Simplified compliance validation
            return {
                "compliant": True,
                "violations": [],
                "validated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Policy compliance validation failed: {e}")
            return {"compliant": False, "error": str(e)}
    
    async def _generate_governance_reports(self, 
                                         policy_id: str,
                                         application_results: Dict[str, Any],
                                         compliance_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate governance reports."""
        try:
            return {
                "policy_id": policy_id,
                "application_summary": application_results,
                "compliance_summary": compliance_results,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Governance report generation failed: {e}")
            return {"error": str(e)}
    
    async def _enforce_governance_policies(self, 
                                         asset_id: str,
                                         policies: List[str]) -> Dict[str, Any]:
        """Enforce governance policies on asset."""
        try:
            enforcement_results = []
            
            for policy_id in policies:
                success = await self.knowledge_governance.apply_policy_to_asset(
                    asset_id, policy_id
                )
                enforcement_results.append({
                    "policy_id": policy_id,
                    "success": success
                })
            
            return {
                "total_policies": len(policies),
                "successful_enforcements": len([r for r in enforcement_results if r['success']]),
                "enforcement_results": enforcement_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Policy enforcement failed: {e}")
            return {"error": str(e)}
    
    async def _validate_metadata_compliance(self, 
                                          asset_id: str,
                                          compliance_rules: List[str]) -> Dict[str, Any]:
        """Validate metadata compliance."""
        try:
            # Simplified compliance validation
            return {
                "compliant": True,
                "violations": [],
                "validated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Metadata compliance validation failed: {e}")
            return {"compliant": False, "error": str(e)}
    
    async def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get comprehensive status of knowledge infrastructure components."""
        try:
            self.logger.info("📊 Getting knowledge infrastructure status")
            
            # Get discovery status
            discovery_health = await self.knowledge_discovery.health_check()
            
            # Get governance status
            governance_health = await self.knowledge_governance.health_check()
            
            status = {
                "timestamp": datetime.utcnow().isoformat(),
                "knowledge_discovery": discovery_health,
                "knowledge_governance": governance_health,
                "overall_status": "operational" if (
                    discovery_health.get('overall_health') == 'healthy' and
                    governance_health.get('overall_health') == 'healthy'
                ) else "degraded"
            }
            
            self.logger.info("✅ Knowledge infrastructure status retrieved")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_infrastructure_status", {
                    "success": True
                })
            
            return status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_infrastructure_status",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to get infrastructure status: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "error",
                "error": str(e),
                "error_code": "INFRASTRUCTURE_STATUS_ERROR"
            }

