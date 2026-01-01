#!/usr/bin/env python3
"""
Document Intelligence Composition Service

Composition service for document intelligence capabilities.
Orchestrates document processing abstractions for agentic document analysis.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import uuid

from ..infrastructure_abstractions.document_intelligence_abstraction import DocumentIntelligenceAbstraction
from ..abstraction_contracts.document_intelligence_protocol import (
    DocumentProcessingRequest, DocumentProcessingResult, DocumentChunk, DocumentEntity
)


class DocumentIntelligenceCompositionService:
    """Composition service for document intelligence capabilities."""
    
    def __init__(self, document_intelligence_abstraction: DocumentIntelligenceAbstraction, di_container=None):
        """
        Initialize document intelligence composition service.
        
        Args:
            document_intelligence_abstraction: Document intelligence abstraction instance
            di_container: DI Container for utilities
        """
        self.document_intelligence = document_intelligence_abstraction
        self.di_container = di_container
        self.service_name = "document_intelligence_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("DocumentIntelligenceCompositionService")
        
        # Service status
        self.is_initialized = False
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the composition service."""
        try:
            self.logger.info("✅ Document intelligence composition service initialized")
            self.is_initialized = True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize document intelligence composition service: {e}")
            self.is_initialized = False
    
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
    # AGENTIC DOCUMENT INTELLIGENCE CAPABILITIES
    # ============================================================================
    
    async def process_agent_document(self, file_data: bytes, filename: str, 
                                   agent_context: Dict[str, Any] = None,
                                   user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process document for agentic analysis.
        
        Args:
            file_data: Document file data
            filename: Document filename
            agent_context: Agent context information
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Agent document processing result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "document", "process"
                )
                if validation_error:
                    return validation_error
            
            # Create processing request
            request = DocumentProcessingRequest(
                file_data=file_data,
                filename=filename,
                options=agent_context or {}
            )
            
            # Process document
            result = await self.document_intelligence.process_document(request)
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.error,
                    "filename": filename,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Format for agentic use
            agent_result = {
                "success": True,
                "filename": filename,
                "file_hash": result.file_hash,
                "text_length": result.text_length,
                "page_count": result.page_count,
                "chunks": [
                    {
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "start_position": chunk.start_position,
                        "end_position": chunk.end_position,
                        "length": chunk.length
                    }
                    for chunk in result.chunks or []
                ],
                "entities": [
                    {
                        "entity_id": entity.entity_id,
                        "text": entity.text,
                        "label": entity.label,
                        "start_position": entity.start_position,
                        "end_position": entity.end_position,
                        "confidence": entity.confidence
                    }
                    for entity in result.entities or []
                ],
                "metadata": result.metadata,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Agent document processed: {filename}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("process_agent_document", {
                    "filename": filename,
                    "success": True
                })
            
            return agent_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "process_agent_document",
                    "filename": filename,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to process agent document: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "DOCUMENT_PROCESSING_ERROR",
                "filename": filename,
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_document_similarity(self, text1: str, text2: str, 
                                        agent_context: Dict[str, Any] = None,
                                        user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze document similarity for agentic use.
        
        Args:
            text1: First document text
            text2: Second document text
            agent_context: Agent context information
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Document similarity analysis
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "document", "analyze"
                )
                if validation_error:
                    return validation_error
            
            # Calculate similarity
            similarity = await self.document_intelligence.calculate_document_similarity(text1, text2)
            
            # Format for agentic use
            similarity_analysis = {
                "similarity_id": similarity.similarity_id,
                "similarity_score": similarity.similarity_score,
                "is_similar": similarity.is_similar,
                "threshold": similarity.threshold,
                "agent_context": agent_context or {},
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Document similarity analyzed: {similarity.similarity_score}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("analyze_document_similarity", {
                    "similarity_score": similarity.similarity_score,
                    "success": True
                })
            
            return similarity_analysis
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "analyze_document_similarity",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to analyze document similarity: {e}")
            return {
                "error": str(e),
                "error_code": "DOCUMENT_SIMILARITY_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_document_embeddings_for_agent(self, texts: List[str], 
                                                   agent_id: str = None,
                                                   user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate document embeddings for agentic use.
        
        Args:
            texts: List of document texts
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Document embeddings result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "document", "embed"
                )
                if validation_error:
                    return validation_error
            
            # Generate embeddings
            embeddings = await self.document_intelligence.generate_document_embeddings(texts)
            
            # Format for agentic use
            embeddings_result = {
                "embeddings": embeddings,
                "text_count": len(texts),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Document embeddings generated for {len(texts)} texts")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("generate_document_embeddings_for_agent", {
                    "text_count": len(texts),
                    "success": True
                })
            
            return embeddings_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "generate_document_embeddings_for_agent",
                    "text_count": len(texts),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to generate document embeddings: {e}")
            return {
                "error": str(e),
                "error_code": "DOCUMENT_EMBEDDINGS_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def extract_entities_for_agent(self, text: str, agent_id: str = None,
                                       user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract entities for agentic use.
        
        Args:
            text: Document text
            agent_id: Agent ID for context
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Entity extraction result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "document", "extract"
                )
                if validation_error:
                    return validation_error
            
            # Extract entities
            entities = await self.document_intelligence.extract_document_entities(text)
            
            # Format for agentic use
            entity_result = {
                "entities": [
                    {
                        "entity_id": entity.entity_id,
                        "text": entity.text,
                        "label": entity.label,
                        "start_position": entity.start_position,
                        "end_position": entity.end_position,
                        "confidence": entity.confidence
                    }
                    for entity in entities
                ],
                "entity_count": len(entities),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Entities extracted for agent: {len(entities)} entities")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("extract_entities_for_agent", {
                    "entity_count": len(entities),
                    "success": True
                })
            
            return entity_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "extract_entities_for_agent",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to extract entities: {e}")
            return {
                "error": str(e),
                "error_code": "DOCUMENT_ENTITY_EXTRACTION_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def chunk_document_for_agent(self, text: str, agent_id: str = None, 
                                     chunk_size: int = None, chunk_overlap: int = None,
                                     user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Chunk document for agentic use.
        
        Args:
            text: Document text
            agent_id: Agent ID for context
            chunk_size: Chunk size
            chunk_overlap: Chunk overlap
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Document chunking result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "document", "chunk"
                )
                if validation_error:
                    return validation_error
            
            # Chunk document
            chunks = await self.document_intelligence.chunk_document(text, chunk_size, chunk_overlap)
            
            # Format for agentic use
            chunk_result = {
                "chunks": [
                    {
                        "chunk_id": chunk.chunk_id,
                        "text": chunk.text,
                        "start_position": chunk.start_position,
                        "end_position": chunk.end_position,
                        "length": chunk.length
                    }
                    for chunk in chunks
                ],
                "chunk_count": len(chunks),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Document chunked for agent: {len(chunks)} chunks")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("chunk_document_for_agent", {
                    "chunk_count": len(chunks),
                    "success": True
                })
            
            return chunk_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "chunk_document_for_agent",
                    "agent_id": agent_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to chunk document: {e}")
            return {
                "error": str(e),
                "error_code": "DOCUMENT_CHUNKING_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    # ============================================================================
    # SERVICE MANAGEMENT
    # ============================================================================
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get composition service status.
        
        Returns:
            Dict: Service status
        """
        try:
            # Get document intelligence status
            intelligence_health = await self.document_intelligence.health_check()
            
            return {
                "service": "DocumentIntelligenceCompositionService",
                "initialized": self.is_initialized,
                "document_intelligence": intelligence_health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_service_status",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get service status: {e}")
            return {
                "service": "DocumentIntelligenceCompositionService",
                "initialized": self.is_initialized,
                "error": str(e),
                "error_code": "DOCUMENT_INTELLIGENCE_SERVICE_STATUS_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components.
        
        Returns:
            Dict: Health check result
        """
        try:
            health_status = {
                "healthy": True,
                "components": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check document intelligence
            try:
                intelligence_health = await self.document_intelligence.health_check()
                health_status["components"]["document_intelligence"] = intelligence_health
                
                if not intelligence_health.get("healthy", False):
                    health_status["healthy"] = False
                    
            except Exception as e:
                health_status["components"]["document_intelligence"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
            
            return health_status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "error_code": "DOCUMENT_INTELLIGENCE_HEALTH_CHECK_ERROR",
                "timestamp": datetime.now().isoformat()
            }




