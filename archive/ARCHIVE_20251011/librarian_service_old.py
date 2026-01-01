#!/usr/bin/env python3
"""
Librarian Service - Multi-Tenant Architecture

Refactored to adhere to the new architectural principles with multi-tenant awareness:
- Inherits from SOAServiceBase
- Uses simple micro-modules for business logic
- Implements interfaces (duck typing) without importing them directly
- Leverages environment configuration for dynamic behavior
- Provides tenant-aware knowledge management

WHAT (Smart City Role): I manage all knowledge discovery, metadata, and semantic search with tenant awareness
HOW (Service Implementation): I use foundation services and micro-modules for knowledge management with tenant isolation
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.soa_service_base import SOAServiceBase
from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol, SOAEndpoint, SOAServiceInfo
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment

# Import micro-modules
from .micro_modules.knowledge_management import KnowledgeManagementModule
from .micro_modules.search_engine import SearchEngineModule
from .micro_modules.metadata_extraction import MetadataExtractionModule
from .micro_modules.knowledge_analytics import KnowledgeAnalyticsModule
from .micro_modules.knowledge_recommendations import KnowledgeRecommendationsModule


class LibrarianService(SOAServiceBase):
    """
    Librarian Service - Multi-Tenant Smart City Service
    
    Manages knowledge discovery, metadata, and semantic search using:
    - Foundation services for infrastructure access
    - Micro-modules for focused business logic
    - Environment configuration for dynamic behavior
    - Duck typing for interface compliance
    - Multi-tenant awareness and tenant isolation
    
    WHAT (Smart City Role): I manage all knowledge discovery, metadata, and semantic search with tenant awareness
    HOW (Service Implementation): I use foundation services and micro-modules for knowledge management with tenant isolation
    """
    
    def __init__(self, utility_foundation: UtilityFoundationService, curator_foundation: CuratorFoundationService = None, 
                 public_works_foundation: PublicWorksFoundationService = None, environment: Optional[Environment] = None):
        """Initialize Librarian Service with multi-tenant architecture."""
        super().__init__("LibrarianService", utility_foundation, curator_foundation)
        
        self.public_works_foundation = public_works_foundation
        self.env_loader = EnvironmentLoader(environment)
        
        # Multi-tenant coordination service
        self.multi_tenant_coordinator = None
        if self.public_works_foundation:
            self.multi_tenant_coordinator = self.public_works_foundation.multi_tenant_coordination_service
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}
        
        # Initialize SOA protocol with Public Works integration
        self.soa_protocol = LibrarianSOAProtocol("LibrarianService", self, curator_foundation, public_works_foundation)
        
        # Environment-specific configuration
        self.config = self.env_loader.get_all_config()
        self.api_config = self.env_loader.get_api_config()
        self.feature_flags = self.env_loader.get_feature_flags()
        
        # Initialize micro-modules (corrected architecture)
        self.knowledge_management = KnowledgeManagementModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        self.search_engine = SearchEngineModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        self.metadata_extraction = MetadataExtractionModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        self.knowledge_analytics = KnowledgeAnalyticsModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        self.knowledge_recommendations = KnowledgeRecommendationsModule(
            logger=self.logger,
            env_loader=self.env_loader
        )
        
        # Service capabilities
        self.capabilities = [
            "knowledge_management",
            "search_engine",
            "metadata_extraction",
            "knowledge_analytics",
            "knowledge_recommendations",
            "multi_tenant_knowledge_management"
        ]
        
        self.logger.info("📚 Librarian Service initialized - Multi-Tenant Knowledge Management Hub")
    
    async def initialize(self):
        """Initialize the Librarian Service with multi-tenant capabilities."""
        try:
            await super().initialize()
            
            self.logger.info("🚀 Initializing Librarian Service with multi-tenant capabilities...")

            # Initialize SOA protocol
            await self.soa_protocol.initialize()
            self.logger.info("✅ SOA Protocol initialized")

            # Initialize multi-tenant coordination
            if self.multi_tenant_coordinator:
                await self.multi_tenant_coordinator.initialize()
                self.logger.info("✅ Multi-tenant coordination initialized")
            
            # Load smart city abstractions through protocol
            await self.soa_protocol.load_smart_city_abstractions()
            self.smart_city_abstractions = self.soa_protocol.get_all_abstractions()
            self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions through protocol")
            
            # Initialize micro-modules
            await self.knowledge_management.initialize()
            await self.search_engine.initialize()
            await self.metadata_extraction.initialize()
            await self.knowledge_analytics.initialize()
            await self.knowledge_recommendations.initialize()
            
            # Apply environment-specific settings
            await self._apply_environment_settings()
            
            self.logger.info("✅ Librarian Service initialized successfully")
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_service_initialization")
            self.service_health = "unhealthy"
            raise
    
    async def _apply_environment_settings(self):
        """Apply environment-specific settings."""
        try:
            current_env = self.env_loader.get_environment().value
            self.logger.info(f"🔧 Applied {current_env} settings")
            
            # Example: Adjust logging level based on environment
            if self.api_config.get("debug"):
                self.logger.setLevel("DEBUG")
            else:
                self.logger.setLevel("INFO")
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_environment_settings")
    
    # NEW: Abstraction Access Methods using Protocol
    async def get_abstraction(self, abstraction_name: str) -> Any:
        """Get a business abstraction through the protocol."""
        return self.soa_protocol.get_abstraction(abstraction_name)
    
    async def has_abstraction(self, abstraction_name: str) -> bool:
        """Check if a business abstraction is available through the protocol."""
        return self.soa_protocol.has_abstraction(abstraction_name)
    
    async def get_abstraction_for_role(self, role: str) -> Dict[str, Any]:
        """Get business abstractions for a specific role through the protocol."""
        return self.soa_protocol.get_abstraction_for_role(role)
    
    async def create_abstraction_context(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Create abstraction context for cross-role operations."""
        abstraction_context = {}
        
        # Get available abstractions through protocol
        available_abstractions = self.soa_protocol.get_abstraction_names()
        
        for abstraction_name in available_abstractions:
            abstraction = self.soa_protocol.get_abstraction(abstraction_name)
            if abstraction:
                abstraction_context[abstraction_name] = abstraction
        
        self.logger.info(f"✅ Created abstraction context with {len(abstraction_context)} abstractions")
        return abstraction_context
    
    # IKnowledgeManagement Interface Implementation (duck typing)
    # The methods match the interface, but no explicit inheritance or import of IKnowledgeManagement
    
    async def search_knowledge(self, request: "KnowledgeSearchRequest", user_context: Optional[UserContext] = None) -> "KnowledgeSearchResponse":
        """Search knowledge assets with advanced capabilities using business abstractions."""
        try:
            # Create abstraction context for cross-role operations
            abstraction_context = await self.create_abstraction_context(user_context)
            
            # Validate user context and permissions using security abstraction
            if user_context:
                security_abstraction = self.soa_protocol.get_abstraction("security_management")
                if security_abstraction:
                    has_permission = await security_abstraction.check_permissions(
                        user_context.user_id, "knowledge_search", "read", user_context, abstraction_context
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "results": [],
                            "total_count": 0,
                            "error": "Insufficient permissions for knowledge search"
                        }
            
            # Delegate to search engine module
            search_result = await self.search_engine.search(
                query=request.query,
                search_mode=request.search_mode.value if hasattr(request.search_mode, 'value') else str(request.search_mode),
                filters={
                    "knowledge_type": request.knowledge_type.value if hasattr(request.knowledge_type, 'value') else str(request.knowledge_type) if request.knowledge_type else None,
                    "tags": request.tags,
                    "date_from": request.date_from,
                    "date_to": request.date_to
                },
                user_context=user_context.to_dict() if user_context else None
            )
            
            # Track search for analytics
            await self.knowledge_analytics.track_search(
                query=request.query,
                user_id=user_context.user_id if user_context else "anonymous",
                result_count=search_result.get("total_count", 0),
                search_duration=search_result.get("duration", 0),
                search_mode=request.search_mode.value if hasattr(request.search_mode, 'value') else str(request.search_mode)
            )
            
            # Record telemetry for knowledge search using health monitoring abstraction
            health_abstraction = self.soa_protocol.get_abstraction("health_monitoring")
            if health_abstraction:
                await health_abstraction.record_metric(
                    metric_name="knowledge_search_count", 
                    value=1,
                    metadata={"search_mode": request.search_mode.value if hasattr(request.search_mode, 'value') else str(request.search_mode), 
                             "query_length": len(request.query), "result_count": search_result.get("total_count", 0)},
                    user_context=user_context,
                    abstraction_context=abstraction_context
                )
            
            # Audit user action using security abstraction
            if user_context:
                security_abstraction = self.soa_protocol.get_abstraction("security_management")
                if security_abstraction:
                    await security_abstraction.audit_user_action(
                        user_context, "knowledge_search", "librarian_service",
                        {"query": request.query, "result_count": search_result.get("total_count", 0)},
                        abstraction_context
                    )
            
            return {
                "success": search_result["success"],
                "results": search_result.get("results", []),
                "total_count": search_result.get("total_count", 0),
                "search_mode": search_result.get("search_mode", "semantic"),
                "query": search_result.get("query", request.query)
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_knowledge_search")
            return {
                "success": False,
                "results": [],
                "total_count": 0,
                "error": str(e)
            }
    
    async def index_knowledge(self, request: "KnowledgeIndexRequest", user_context: Optional[UserContext] = None) -> "KnowledgeIndexResponse":
        """Index a knowledge asset using business abstractions."""
        try:
            # Create abstraction context for cross-role operations
            abstraction_context = await self.create_abstraction_context(user_context)
            
            # Validate user context and permissions using security abstraction
            if user_context:
                security_abstraction = self.soa_protocol.get_abstraction("security_management")
                if security_abstraction:
                    has_permission = await security_abstraction.check_permissions(
                        user_context.user_id, "knowledge_index", "write", user_context, abstraction_context
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "asset_id": None,
                            "error": "Insufficient permissions for knowledge indexing"
                        }
            # Extract metadata first
            metadata_result = await self.metadata_extraction.extract_metadata(
                content=request.content,
                content_type=request.content_type,
                file_name=request.title,
                user_context=user_context.to_dict() if user_context else None
            )
            
            # Create knowledge asset
            asset_data = {
                "title": request.title,
                "content": request.content,
                "knowledge_type": request.knowledge_type.value if hasattr(request.knowledge_type, 'value') else str(request.knowledge_type),
                "tags": request.tags,
                "metadata": metadata_result.get("metadata", {}) if metadata_result.get("success") else {}
            }
            
            create_result = await self.knowledge_management.create_knowledge_asset(
                asset_data=asset_data,
                user_context=user_context.to_dict() if user_context else None
            )
            
            # Record telemetry for knowledge indexing using standard utility foundation
            if create_result.get("success"):
                await self.telemetry_service.record_metric(
                    "knowledge_index_count", 1,
                    {"knowledge_type": request.knowledge_type.value if hasattr(request.knowledge_type, 'value') else str(request.knowledge_type),
                     "content_length": len(request.content), "tag_count": len(request.tags)}
                )
            
            if create_result["success"]:
                # Update search index
                await self.search_engine.update_search_index(create_result["asset"])
                
                # Track asset creation for analytics
                await self.knowledge_analytics.track_asset_creation(
                    asset_id=create_result["asset_id"],
                    asset_type=request.knowledge_type.value if hasattr(request.knowledge_type, 'value') else str(request.knowledge_type),
                    user_id=user_context.user_id if user_context else "system",
                    metadata={"content_length": len(request.content)}
                )
                
                return {
                    "success": True,
                    "asset_id": create_result["asset_id"],
                    "indexed_at": create_result["asset"]["created_at"],
                    "metadata": metadata_result.get("metadata", {}) if metadata_result.get("success") else {}
                }
            else:
                return {
                    "success": False,
                    "asset_id": None,
                    "error": create_result.get("error", "Failed to create knowledge asset")
                }
                
        except Exception as e:
            # Use error handling abstraction if available
            error_abstraction = self.soa_protocol.get_abstraction("error_handling")
            if error_abstraction:
                await error_abstraction.handle_error(e, context="librarian_knowledge_indexing", user_context=user_context)
            else:
                # Fallback to direct error handling
                self.logger.error(f"Error in knowledge indexing: {e}")
            
            return {
                "success": False,
                "asset_id": None,
                "error": str(e)
            }
    
    async def get_knowledge_asset(self, asset_id: str, user_context: Optional[UserContext] = None) -> Optional["KnowledgeAsset"]:
        """Get a knowledge asset by ID."""
        try:
            result = await self.knowledge_management.get_knowledge_asset(
                asset_id=asset_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                # Track asset access for analytics
                await self.knowledge_analytics.track_asset_access(
                    asset_id=asset_id,
                    user_id=user_context.user_id if user_context else "anonymous",
                    access_type="view"
                )
                
                return result["asset"]
            else:
                return None
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_get_knowledge_asset")
            return None
    
    async def update_knowledge_asset(self, asset_id: str, updates: Dict[str, Any], user_context: Optional[UserContext] = None) -> bool:
        """Update a knowledge asset."""
        try:
            result = await self.knowledge_management.update_knowledge_asset(
                asset_id=asset_id,
                updates=updates,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if result["success"]:
                # Update search index
                await self.search_engine.update_search_index(result["asset"])
                
                return True
            else:
                return False
                
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_update_knowledge_asset")
            return False
    
    async def delete_knowledge_asset(self, asset_id: str, user_context: Optional[UserContext] = None) -> bool:
        """Delete a knowledge asset."""
        try:
            success = await self.knowledge_management.delete_knowledge_asset(
                asset_id=asset_id,
                user_context=user_context.to_dict() if user_context else None
            )
            
            if success:
                # Remove from search index
                await self.search_engine.remove_from_search_index(asset_id)
                
            return success
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_delete_knowledge_asset")
            return False
    
    async def get_recommendations(self, request: "KnowledgeRecommendationRequest", user_context: Optional[UserContext] = None) -> "KnowledgeRecommendationResponse":
        """Get knowledge recommendations."""
        try:
            if request.recommendation_type == "content_based":
                result = await self.knowledge_recommendations.get_content_recommendations(
                    user_id=user_context.user_id if user_context else "anonymous",
                    asset_id=request.asset_id,
                    limit=request.limit,
                    user_context=user_context.to_dict() if user_context else None
                )
            else:
                result = await self.knowledge_recommendations.get_user_recommendations(
                    user_id=user_context.user_id if user_context else "anonymous",
                    limit=request.limit,
                    user_context=user_context.to_dict() if user_context else None
                )
            
            return {
                "success": result["success"],
                "recommendations": result.get("recommendations", []),
                "total_count": result.get("total_count", 0),
                "recommendation_type": request.recommendation_type
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_get_recommendations")
            return {
                "success": False,
                "recommendations": [],
                "total_count": 0,
                "error": str(e)
            }
    
    async def extract_metadata(self, request: "MetadataExtractionRequest", user_context: Optional[UserContext] = None) -> "MetadataExtractionResponse":
        """Extract metadata from content."""
        try:
            result = await self.metadata_extraction.extract_metadata(
                content=request.content,
                content_type=request.content_type,
                file_name=request.file_name,
                user_context=user_context.to_dict() if user_context else None
            )
            
            return {
                "success": result["success"],
                "metadata": result.get("metadata", {}),
                "error": result.get("error")
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_metadata_extraction")
            return {
                "success": False,
                "metadata": {},
                "error": str(e)
            }
    
    async def assess_quality(self, request: "KnowledgeQualityAssessmentRequest", user_context: Optional[UserContext] = None) -> "KnowledgeQualityAssessmentResponse":
        """Assess the quality of knowledge content."""
        try:
            # Simple quality assessment based on content length, structure, etc.
            content = request.content
            quality_score = 0.0
            quality_factors = []
            
            # Length factor
            if len(content) > 100:
                quality_score += 0.2
                quality_factors.append("adequate_length")
            else:
                quality_factors.append("short_content")
            
            # Structure factor (has paragraphs, sentences)
            if '\n\n' in content or '. ' in content:
                quality_score += 0.3
                quality_factors.append("well_structured")
            else:
                quality_factors.append("poor_structure")
            
            # Completeness factor (has title, content)
            if request.title and len(request.title) > 5:
                quality_score += 0.2
                quality_factors.append("has_title")
            
            # Metadata factor
            if request.metadata and len(request.metadata) > 0:
                quality_score += 0.3
                quality_factors.append("has_metadata")
            
            # Determine quality level
            if quality_score >= 0.8:
                quality_level = "high"
            elif quality_score >= 0.6:
                quality_level = "medium"
            else:
                quality_level = "low"
            
            return {
                "success": True,
                "quality_score": quality_score,
                "quality_level": quality_level,
                "quality_factors": quality_factors,
                "recommendations": self._get_quality_recommendations(quality_factors)
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="librarian_quality_assessment")
            return {
                "success": False,
                "quality_score": 0.0,
                "quality_level": "unknown",
                "error": str(e)
            }
    
    def _get_quality_recommendations(self, quality_factors: List[str]) -> List[str]:
        """Get recommendations for improving content quality."""
        recommendations = []
        
        if "short_content" in quality_factors:
            recommendations.append("Consider adding more detailed content")
        if "poor_structure" in quality_factors:
            recommendations.append("Improve content structure with paragraphs and clear sentences")
        if "has_title" not in quality_factors:
            recommendations.append("Add a descriptive title")
        if "has_metadata" not in quality_factors:
            recommendations.append("Add relevant metadata and tags")
        
        return recommendations
    
    # Note: Using standard FoundationServiceBase health check pattern
    # Custom health logic should be implemented in micro-modules, not in service health check
    
    # ============================================================================
    # MULTI-TENANT SPECIFIC METHODS
    # ============================================================================
    
    async def get_tenant_knowledge_base(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get knowledge base for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's knowledge base"}
            
            # Get tenant-specific knowledge items
            search_filters = {"tenant_id": tenant_id}
            knowledge_items = await self.search_knowledge(search_filters, user_context)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_knowledge_base", "librarian",
                    {"tenant_id": tenant_id, "knowledge_count": len(knowledge_items.get("results", []))}
                )
            
            return {"success": True, "knowledge_items": knowledge_items.get("results", []), "count": len(knowledge_items.get("results", []))}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_knowledge_base")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_knowledge_metrics(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get knowledge metrics for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's knowledge metrics"}
            
            # Get tenant knowledge base
            tenant_knowledge = await self.get_tenant_knowledge_base(tenant_id, user_context)
            if not tenant_knowledge.get("success"):
                return tenant_knowledge
            
            knowledge_items = tenant_knowledge.get("knowledge_items", [])
            
            # Calculate knowledge metrics
            knowledge_metrics = {
                "tenant_id": tenant_id,
                "total_knowledge_items": len(knowledge_items),
                "knowledge_by_type": self._calculate_knowledge_by_type(knowledge_items),
                "knowledge_by_quality": self._calculate_knowledge_by_quality(knowledge_items),
                "average_quality_score": self._calculate_average_quality_score(knowledge_items),
                "search_popularity": self._calculate_search_popularity(knowledge_items)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_knowledge_metrics", "librarian",
                    {"tenant_id": tenant_id, "total_items": knowledge_metrics["total_knowledge_items"]}
                )
            
            return {"success": True, "knowledge_metrics": knowledge_metrics}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_knowledge_metrics")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_search_analytics(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get search analytics for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's search analytics"}
            
            # Get tenant knowledge base for analytics
            tenant_knowledge = await self.get_tenant_knowledge_base(tenant_id, user_context)
            if not tenant_knowledge.get("success"):
                return tenant_knowledge
            
            knowledge_items = tenant_knowledge.get("knowledge_items", [])
            
            # Calculate search analytics
            search_analytics = {
                "tenant_id": tenant_id,
                "total_searches": self._calculate_total_searches(knowledge_items),
                "popular_search_terms": self._calculate_popular_search_terms(knowledge_items),
                "search_success_rate": self._calculate_search_success_rate(knowledge_items),
                "average_search_time": self._calculate_average_search_time(knowledge_items),
                "search_trends": self._calculate_search_trends(knowledge_items)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_search_analytics", "librarian",
                    {"tenant_id": tenant_id, "total_searches": search_analytics["total_searches"]}
                )
            
            return {"success": True, "search_analytics": search_analytics}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_search_analytics")
            return {"success": False, "error": str(e)}
    
    def _calculate_knowledge_by_type(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of knowledge by type."""
        type_counts = {}
        for item in knowledge_items:
            item_type = item.get("type", "unknown")
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        return type_counts
    
    def _calculate_knowledge_by_quality(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate distribution of knowledge by quality level."""
        quality_counts = {"high": 0, "medium": 0, "low": 0}
        for item in knowledge_items:
            quality_score = item.get("quality_score", 0)
            if quality_score >= 0.8:
                quality_counts["high"] += 1
            elif quality_score >= 0.6:
                quality_counts["medium"] += 1
            else:
                quality_counts["low"] += 1
        return quality_counts
    
    def _calculate_average_quality_score(self, knowledge_items: List[Dict[str, Any]]) -> float:
        """Calculate average quality score for knowledge items."""
        if not knowledge_items:
            return 0.0
        
        quality_scores = [item.get("quality_score", 0) for item in knowledge_items]
        return round(sum(quality_scores) / len(quality_scores), 3)
    
    def _calculate_search_popularity(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate search popularity for knowledge items."""
        popularity = {}
        for item in knowledge_items:
            item_id = item.get("id", "unknown")
            search_count = item.get("search_count", 0)
            popularity[item_id] = search_count
        return popularity
    
    def _calculate_total_searches(self, knowledge_items: List[Dict[str, Any]]) -> int:
        """Calculate total number of searches."""
        return sum(item.get("search_count", 0) for item in knowledge_items)
    
    def _calculate_popular_search_terms(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate popular search terms."""
        search_terms = {}
        for item in knowledge_items:
            if "search_terms" in item:
                for term in item["search_terms"]:
                    search_terms[term] = search_terms.get(term, 0) + 1
        return dict(sorted(search_terms.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _calculate_search_success_rate(self, knowledge_items: List[Dict[str, Any]]) -> float:
        """Calculate search success rate."""
        if not knowledge_items:
            return 100.0
        
        successful_searches = len([item for item in knowledge_items if item.get("search_count", 0) > 0])
        return round((successful_searches / len(knowledge_items)) * 100, 2)
    
    def _calculate_average_search_time(self, knowledge_items: List[Dict[str, Any]]) -> float:
        """Calculate average search time in milliseconds."""
        if not knowledge_items:
            return 0.0
        
        search_times = [item.get("search_time", 0) for item in knowledge_items if item.get("search_time")]
        return round(sum(search_times) / len(search_times), 2) if search_times else 0.0
    
    def _calculate_search_trends(self, knowledge_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate search trends over time."""
        # Simplified trend calculation - in a real implementation, you'd group by time periods
        return {
            "last_hour": len([item for item in knowledge_items if self._is_recent_search(item, 1)]),
            "last_24_hours": len([item for item in knowledge_items if self._is_recent_search(item, 24)]),
            "last_week": len([item for item in knowledge_items if self._is_recent_search(item, 168)])
        }
    
    def _is_recent_search(self, item: Dict[str, Any], hours: int) -> bool:
        """Check if an item was searched recently."""
        if not item.get("last_searched"):
            return False
        
        try:
            from datetime import datetime, timedelta
            last_searched = datetime.fromisoformat(item["last_searched"].replace('Z', '+00:00'))
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return last_searched >= cutoff_time
        except:
            return False


class LibrarianSOAProtocol(SOAServiceProtocol):
    """SOA Protocol implementation for Librarian Service."""
    
    def __init__(self, service_name: str, service_instance, curator_foundation=None, public_works_foundation=None):
        """Initialize Librarian SOA Protocol with Public Works integration."""
        super().__init__(service_name, None, curator_foundation, public_works_foundation)
        self.service_instance = service_instance
        self.service_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the SOA service."""
        # Create service info with multi-tenant metadata
        self.service_info = SOAServiceInfo(
            service_name="LibrarianService",
            version="1.0.0",
            description="Librarian Service - Multi-tenant knowledge management and search",
            interface_name="ILibrarian",
            endpoints=self._create_all_endpoints(),
            tags=["knowledge-management", "search", "multi-tenant", "content-discovery"],
            contact={"email": "librarian@smartcity.com"},
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_service_info(self) -> SOAServiceInfo:
        """Get service information for OpenAPI generation."""
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI 3.0 specification for this service."""
        if not self.service_info:
            return {"error": "Service not initialized"}
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description,
                "contact": self.service_info.contact
            },
            "servers": [
                {"url": "https://api.smartcity.com/librarian", "description": "Librarian Service"}
            ],
            "paths": self._create_openapi_paths(),
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    
    def get_docs(self) -> Dict[str, Any]:
        """Get service documentation."""
        return {
            "service": self.service_info.service_name,
            "description": self.service_info.description,
            "version": self.service_info.version,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
            "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
            "tenant_isolation_level": self.service_info.tenant_isolation_level
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this service with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],  # MCP tools handled separately
                "description": self.service_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
                "tenant_isolation_level": self.service_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.service_name, 
                capability, 
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_endpoints(self) -> List[SOAEndpoint]:
        """Create all endpoints for Librarian Service."""
        endpoints = []
        
        # Standard endpoints
        endpoints.extend(self._create_standard_endpoints())
        endpoints.extend(self._create_health_endpoints())
        endpoints.extend(self._create_tenant_aware_endpoints())
        
        # Librarian specific endpoints
        endpoints.extend([
            SOAEndpoint(
                path="/knowledge",
                method="POST",
                summary="Create Knowledge Item",
                description="Create a new knowledge item with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "type": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "metadata": {"type": "object"}
                    },
                    "required": ["title", "content", "type"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "knowledge_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Knowledge", "Management"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/knowledge/{knowledge_id}",
                method="GET",
                summary="Get Knowledge Item",
                description="Get a specific knowledge item",
                parameters=[
                    {
                        "name": "knowledge_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Knowledge Item ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "knowledge_id": {"type": "string"},
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "type": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    }
                }),
                tags=["Knowledge", "Retrieval"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/search",
                method="POST",
                summary="Search Knowledge",
                description="Search knowledge items with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "filters": {"type": "object"},
                        "limit": {"type": "integer"},
                        "offset": {"type": "integer"}
                    },
                    "required": ["query"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "results": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"},
                        "search_time_ms": {"type": "number"}
                    }
                }),
                tags=["Search", "Knowledge"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/knowledge",
                method="GET",
                summary="List Knowledge Items",
                description="List knowledge items for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "knowledge_items": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"}
                    }
                }),
                tags=["Knowledge", "Management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/knowledge/{knowledge_id}",
                method="PUT",
                summary="Update Knowledge Item",
                description="Update a knowledge item",
                parameters=[
                    {
                        "name": "knowledge_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Knowledge Item ID"
                    }
                ],
                request_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "metadata": {"type": "object"}
                    }
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "knowledge_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Knowledge", "Management"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/knowledge-summary",
                method="GET",
                summary="Get Tenant Knowledge Summary",
                description="Get knowledge summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_knowledge_items": {"type": "integer"},
                        "knowledge_by_type": {"type": "object"},
                        "average_quality_score": {"type": "number"}
                    }
                }),
                tags=["Tenant", "Knowledge"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/search-analytics",
                method="GET",
                summary="Get Tenant Search Analytics",
                description="Get search analytics for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_searches": {"type": "integer"},
                        "popular_search_terms": {"type": "object"},
                        "search_success_rate": {"type": "number"}
                    }
                }),
                tags=["Tenant", "Analytics"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return endpoints
    
    def _create_openapi_paths(self) -> Dict[str, Any]:
        """Create OpenAPI paths for all endpoints."""
        paths = {}
        
        for endpoint in self.service_info.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "security": [{"BearerAuth": []}] if endpoint.requires_tenant else []
                }
            }
            
            if endpoint.parameters:
                path_item[endpoint.method.lower()]["parameters"] = endpoint.parameters
            
            if endpoint.request_schema:
                path_item[endpoint.method.lower()]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
            
            if endpoint.response_schema:
                path_item[endpoint.method.lower()]["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": self._create_error_response_schema()
                            }
                        }
                    }
                }
            
            paths[endpoint.path] = path_item
        
        return paths
