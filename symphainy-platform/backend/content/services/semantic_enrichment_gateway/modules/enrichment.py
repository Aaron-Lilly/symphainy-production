#!/usr/bin/env python3
"""Enrichment module for Semantic Enrichment Gateway."""

from typing import Dict, Any, List, Optional


class Enrichment:
    """Enrichment module for Semantic Enrichment Gateway."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
        self.logger = service_instance.logger
    
    def validate_enrichment_request(self, enrichment_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate enrichment request.
        
        Args:
            enrichment_request: Dict describing what semantic info is needed
            
        Returns:
            Dict with validation result:
            {
                "valid": bool,
                "error": str (if invalid)
            }
        """
        if not enrichment_request:
            return {
                "valid": False,
                "error": "Enrichment request is required"
            }
        
        enrichment_type = enrichment_request.get("type")
        if not enrichment_type:
            return {
                "valid": False,
                "error": "Enrichment type is required"
            }
        
        # Validate enrichment type
        valid_types = ["column_values", "statistics", "correlations", "distributions", "missing_values"]
        if enrichment_type not in valid_types:
            return {
                "valid": False,
                "error": f"Invalid enrichment type: {enrichment_type}. Valid types: {', '.join(valid_types)}"
            }
        
        return {"valid": True}
    
    async def get_enrichment_service(self):
        """
        Get enrichment service (runs in secure boundary).
        
        This service can access parsed data.
        It's a separate service that runs in secure boundary.
        
        Returns:
            SemanticEnrichmentService instance or None if not available
        """
        try:
            # Try to get enrichment service from DI Container or Curator
            # For now, we'll create it lazily if needed
            if self.service.enrichment_service is None:
                # Try to discover via Curator
                try:
                    from backend.business_enablement.enabling_services.semantic_enrichment_service.semantic_enrichment_service import SemanticEnrichmentService
                    
                    # Create enrichment service instance
                    # This service runs in secure boundary and can access parsed data
                    self.service.enrichment_service = SemanticEnrichmentService(
                        service_name="SemanticEnrichmentService",
                        realm_name="business_enablement",
                        platform_gateway=self.service.platform_gateway,
                        di_container=self.service.di_container
                    )
                    
                    # Initialize enrichment service
                    init_result = await self.service.enrichment_service.initialize()
                    if not init_result:
                        self.logger.warning("⚠️ Failed to initialize SemanticEnrichmentService")
                        self.service.enrichment_service = None
                        return None
                    
                    self.logger.info("✅ SemanticEnrichmentService initialized (secure boundary)")
                    
                except ImportError:
                    self.logger.warning("⚠️ SemanticEnrichmentService not available - enrichment cannot be performed")
                    self.service.enrichment_service = None
                    return None
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to create SemanticEnrichmentService: {e}")
                    self.service.enrichment_service = None
                    return None
            
            return self.service.enrichment_service
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get enrichment service: {e}")
            return None
    
    async def store_enriched_embeddings(
        self,
        content_id: str,
        embeddings: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store enriched embeddings in semantic layer.
        
        Args:
            content_id: Content metadata ID
            embeddings: List of new embeddings to store
            user_context: Optional user context
            
        Returns:
            Dict with storage result:
            {
                "success": bool,
                "error": str (if failed)
            }
        """
        try:
            if not self.service.librarian:
                return {
                    "success": False,
                    "error": "Librarian API not available"
                }
            
            if not self.service.semantic_data:
                return {
                    "success": False,
                    "error": "SemanticDataAbstraction not available"
                }
            
            # Get content metadata to find file_id
            content_metadata = await self.service.librarian.get_content_metadata(
                content_id,
                user_context
            )
            
            if not content_metadata:
                return {
                    "success": False,
                    "error": f"Content metadata not found for content_id: {content_id}"
                }
            
            file_id = content_metadata.get("file_id")
            if not file_id:
                return {
                    "success": False,
                    "error": f"file_id not found in content metadata for content_id: {content_id}"
                }
            
            # Store embeddings via semantic data abstraction
            # This maintains the security boundary - we're storing semantic data, not raw parsed data
            store_result = await self.service.semantic_data.store_semantic_embeddings(
                content_id=content_id,
                file_id=file_id,
                embeddings=embeddings,
                user_context=user_context
            )
            
            if not store_result or not store_result.get("success"):
                return {
                    "success": False,
                    "error": store_result.get("error", "Failed to store embeddings") if store_result else "Unknown error"
                }
            
            self.logger.info(f"✅ Stored {len(embeddings)} enriched embeddings for content_id: {content_id}")
            
            return {
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store enriched embeddings: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }

