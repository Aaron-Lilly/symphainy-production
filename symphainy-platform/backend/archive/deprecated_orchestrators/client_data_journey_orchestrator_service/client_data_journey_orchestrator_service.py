#!/usr/bin/env python3
"""
Client Data Journey Orchestrator Service

⚠️ DEPRECATED: This service is deprecated and no longer used.
DataSolutionOrchestratorService now calls ContentJourneyOrchestrator directly.

WHAT: Orchestrates client data journey: Ingest → Parse → Embed → Expose
HOW: Composes FrontendGatewayService → routes to ContentOrchestrator (Content realm)

This service was a redundant layer that just routed through FrontendGatewayService.
The architecture has been simplified:
- DataSolutionOrchestratorService (Solution realm) → ContentJourneyOrchestrator (Journey realm) → Content Services

Architecture:
- Extends OrchestratorBase (orchestrator pattern)
- Composes FrontendGatewayService (Experience realm)
- Routes to ContentOrchestrator (Content realm) ✅
- Proper architectural layering: Journey → Experience → Content → Smart City
- Registered with Curator for discovery

Status: DEPRECATED - Do not use. Use DataSolutionOrchestratorService instead.
"""

import os
import sys
import uuid
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class ClientDataJourneyOrchestratorService(OrchestratorBase):
    """
    Client Data Journey Orchestrator Service - Journey realm.
    
    Orchestrates the client data journey:
    1. Ingest: File upload → ContentOrchestrator
    2. Parse: File parsing → ContentOrchestrator
    3. Embed: Semantic embeddings → ContentOrchestrator
    4. Expose: Semantic layer exposure → ContentOrchestrator
    
    Key Principles:
    - Composes FrontendGatewayService (Experience realm)
    - Routes to ContentOrchestrator (Content realm) ✅
    - Proper architectural layering (no direct Smart City calls)
    - workflow_id propagation for end-to-end tracking
    - Registered with Curator for discovery
    """
    
    def __init__(
        self,
        service_name: str,
        realm_name: str,
        platform_gateway: Any,
        di_container: Any,
        delivery_manager: Any = None
    ):
        """
        Initialize Client Data Journey Orchestrator Service.
        
        Args:
            service_name: Service name (typically "ClientDataJourneyOrchestratorService")
            realm_name: Realm name (typically "journey")
            platform_gateway: Platform Gateway instance
            di_container: DI Container instance
            delivery_manager: Delivery Manager reference (optional, for orchestrator management)
        """
        super().__init__(
            service_name=service_name,
            realm_name=realm_name,
            platform_gateway=platform_gateway,
            di_container=di_container,
            delivery_manager=delivery_manager
        )
        
        # Content realm orchestrators (discovered via Curator)
        self.content_orchestrator = None
    
    async def initialize(self) -> bool:
        """
        Initialize Client Data Journey Orchestrator Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Phase 2 Curator registration
        
        Returns:
            True if initialization successful, False otherwise
        """
        # Start telemetry tracking (via _realm_service delegation)
        await self._realm_service.log_operation_with_telemetry(
            "client_data_journey_orchestrator_initialize_start",
            success=True
        )
        
        # Call parent initialize (sets up OrchestratorBase and _realm_service)
        init_result = await super().initialize()
        if not init_result:
            self.logger.warning("⚠️ Base orchestrator initialization failed, continuing anyway...")
        
        try:
            self.logger.info("🚀 Initializing Client Data Journey Orchestrator Service...")
            
            # FrontendGatewayService will be lazy-loaded when needed
            # (discovered via Curator in _discover_frontend_gateway())
            
            # Register with Curator for discovery
            await self._register_with_curator()
            
            self.logger.info("✅ Client Data Journey Orchestrator Service initialized successfully")
            
            # Complete telemetry tracking (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "client_data_journey_orchestrator_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Client Data Journey Orchestrator Service: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            
            # Record failure in telemetry (via _realm_service delegation)
            await self._realm_service.log_operation_with_telemetry(
                "client_data_journey_orchestrator_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            await self._realm_service.handle_error_with_audit(e, "initialize")
            return False
    
    async def _register_with_curator(self):
        """Register Client Data Journey Orchestrator Service with Curator for discovery."""
        try:
            # Get Curator via OrchestratorBase helper method
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                # Register service instance (required for get_service() discovery)
                service_metadata = {
                    "service_name": self.service_name,
                    "service_type": "client_data_journey_orchestration",
                    "realm_name": self.realm_name,
                    "capabilities": ["client_data_ingest", "client_data_parse", "client_data_embed", "client_data_expose"],
                    "description": "Orchestrates client data journey: Ingest → Parse → Embed → Expose"
                }
                await curator.register_service(self, service_metadata)
                self.logger.info("✅ Registered Client Data Journey Orchestrator Service instance with Curator")
                
                # Also register capability (for capability-based discovery)
                capability_definition = {
                    "service_name": self.service_name,
                    "realm_name": self.realm_name,
                    "capability_type": "client_data_journey_orchestration",
                    "description": "Orchestrates client data journey: Ingest → Parse → Embed → Expose",
                    "contracts": {
                        "orchestrate_client_data_ingest": {
                            "description": "Orchestrate client data ingestion",
                            "parameters": ["file_data", "file_name", "file_type", "user_context"],
                            "returns": ["success", "file_id", "workflow_id"]
                        },
                        "orchestrate_client_data_parse": {
                            "description": "Orchestrate client data parsing",
                            "parameters": ["file_id", "parse_options", "user_context", "workflow_id"],
                            "returns": ["success", "parse_result", "parsed_file_id", "content_metadata", "workflow_id"]
                        },
                        "orchestrate_client_data_embed": {
                            "description": "Orchestrate semantic embedding creation",
                            "parameters": ["file_id", "parsed_file_id", "content_metadata", "user_context", "workflow_id"],
                            "returns": ["success", "embeddings_count", "content_id", "workflow_id"]
                        },
                        "orchestrate_client_data_expose": {
                            "description": "Orchestrate client data exposure",
                            "parameters": ["file_id", "parsed_file_id", "user_context"],
                            "returns": ["success", "parsed_data", "content_metadata", "embeddings_available"]
                        }
                    }
                }
                await curator.register_capability(capability_definition)
                self.logger.info("✅ Registered Client Data Journey Orchestrator Service capability with Curator")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Curator: {e}")
    
    async def _discover_content_orchestrator(self):
        """Discover ContentOrchestrator from Content realm via Curator."""
        try:
            # Primary method: Curator discovery (Content realm)
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                # Try to discover by actual service name: ContentAnalysisOrchestratorService
                content_orchestrator = await curator.discover_service_by_name("ContentAnalysisOrchestratorService")
                if content_orchestrator:
                    # Verify it's from Content realm (not Business Enablement)
                    orchestrator_realm = getattr(content_orchestrator, 'realm_name', None)
                    if orchestrator_realm == "content":
                        self.logger.info("✅ Discovered ContentOrchestrator from Content realm via Curator")
                        return content_orchestrator
                    else:
                        self.logger.warning(f"⚠️ Found ContentOrchestrator but wrong realm: {orchestrator_realm} (expected 'content')")
                
                # Fallback: Try ContentManagerService (which may have content_orchestrator attribute)
                try:
                    content_manager = await curator.discover_service_by_name("ContentManagerService")
                    if content_manager and hasattr(content_manager, 'content_orchestrator'):
                        content_orchestrator = content_manager.content_orchestrator
                        if content_orchestrator:
                            orchestrator_realm = getattr(content_orchestrator, 'realm_name', None)
                            if orchestrator_realm == "content":
                                self.logger.info("✅ Got ContentOrchestrator from ContentManagerService")
                                return content_orchestrator
                except Exception as e:
                    self.logger.debug(f"⚠️ Could not get ContentOrchestrator from ContentManagerService: {e}")
            
            # Fallback: Try DI container service registry
            try:
                content_orchestrator = self.di_container.service_registry.get("ContentAnalysisOrchestratorService")
                if content_orchestrator:
                    # Verify realm
                    orchestrator_realm = getattr(content_orchestrator, 'realm_name', None)
                    if orchestrator_realm == "content":
                        self.logger.info("✅ Got ContentOrchestrator from DI container service registry (Content realm)")
                        return content_orchestrator
                    else:
                        self.logger.warning(f"⚠️ Found ContentOrchestrator in DI container but wrong realm: {orchestrator_realm}")
            except Exception as e:
                self.logger.debug(f"⚠️ Could not get ContentOrchestrator from DI container: {e}")
            
            # Last resort: Try direct import and initialization (Content realm)
            self.logger.warning("⚠️ ContentOrchestrator not found via Curator, attempting direct initialization from Content realm")
            try:
                from backend.content.orchestrators.content_orchestrator.content_analysis_orchestrator import ContentOrchestrator
                # Get ContentManagerService to pass to ContentOrchestrator
                content_manager = None
                if curator:
                    content_manager = await curator.discover_service_by_name("ContentManagerService")
                
                if not content_manager:
                    # Try DI container
                    try:
                        content_manager = self.di_container.service_registry.get("ContentManagerService")
                    except:
                        pass
                
                if content_manager:
                    content_orchestrator = ContentOrchestrator(
                        content_manager=content_manager
                    )
                    await content_orchestrator.initialize()
                    self.logger.info("✅ ContentOrchestrator lazy-initialized directly from Content realm")
                    return content_orchestrator
                else:
                    self.logger.warning("⚠️ ContentManagerService not available - cannot initialize ContentOrchestrator")
            except Exception as init_error:
                self.logger.warning(f"⚠️ Failed to lazy-initialize ContentOrchestrator from Content realm: {init_error}")
                import traceback
                self.logger.debug(f"Traceback: {traceback.format_exc()}")
            
            self.logger.warning("⚠️ ContentOrchestrator not found via any method")
            return None
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to discover ContentOrchestrator: {e}")
            import traceback
            self.logger.debug(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def orchestrate_client_data_ingest(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate client data ingestion.
        
        Flow:
        1. Route via FrontendGatewayService → ContentOrchestrator
        2. ContentOrchestrator handles upload → Content Steward
        3. Track lineage → Data Steward
        4. Record observability → Nurse
        
        Args:
            file_data: File data as bytes
            file_name: Name of the file
            file_type: MIME type or file extension
            user_context: Optional user context (includes workflow_id)
        
        Returns:
            Dict with success status, file_id, and workflow_id
        """
        try:
            # Get workflow_id from user_context (generated at gateway)
            workflow_id = (
                user_context.get("workflow_id") if user_context else None
            ) or str(uuid.uuid4())
            
            self.logger.info(f"📥 Orchestrating client data ingestion: {file_name} (workflow_id: {workflow_id})")
            
            # Compose ContentOrchestrator (Content realm) ✅
            if not self.content_orchestrator:
                self.content_orchestrator = await self._discover_content_orchestrator()
            
            if not self.content_orchestrator:
                raise ValueError("ContentOrchestrator not available - Content realm services must be initialized")
            
            # Call ContentOrchestrator directly (internal orchestration, not external API)
            # Extract user_id and session_id from user_context
            user_id = user_context.get("user_id") if user_context else "anonymous"
            session_id = user_context.get("session_id") if user_context else None
            
            result = await self.content_orchestrator.handle_content_upload(
                file_data=file_data,
                filename=file_name,
                file_type=file_type,
                user_id=user_id,
                session_id=session_id,
                user_context=user_context
            )
            
            # Ensure workflow_id is in result
            if result and not result.get("workflow_id"):
                result["workflow_id"] = workflow_id
            
            self.logger.info(f"✅ Client data ingestion complete: file_id={result.get('file_id')}, workflow_id={workflow_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Client data ingestion failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_client_data_ingest")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id if 'workflow_id' in locals() else None
            }
    
    async def orchestrate_client_data_parse(
        self,
        file_id: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate client data parsing.
        
        Flow:
        1. Route via FrontendGatewayService → ContentOrchestrator
        2. ContentOrchestrator handles parsing → FileParserService
        3. Store parsed file → Content Steward
        4. Extract metadata → ContentMetadataExtractionService
        5. Store metadata → Librarian
        6. Track lineage → Data Steward
        
        Args:
            file_id: File identifier from ingestion
            parse_options: Optional parsing options
            user_context: Optional user context (includes workflow_id)
            workflow_id: Optional workflow_id (if not in user_context)
        
        Returns:
            Dict with success status, parse_result, parsed_file_id, content_metadata, workflow_id
        """
        try:
            # Get workflow_id from user_context or parameter
            if not workflow_id:
                workflow_id = (
                    user_context.get("workflow_id") if user_context else None
                ) or str(uuid.uuid4())
            
            self.logger.info(f"📝 Orchestrating client data parsing: file_id={file_id} (workflow_id: {workflow_id})")
            
            # Compose ContentOrchestrator (Content realm) ✅
            if not self.content_orchestrator:
                self.content_orchestrator = await self._discover_content_orchestrator()
            
            if not self.content_orchestrator:
                raise ValueError("ContentOrchestrator not available - Content realm services must be initialized")
            
            # Call ContentOrchestrator directly (internal orchestration, not external API)
            user_id = user_context.get("user_id") if user_context else "anonymous"
            
            result = await self.content_orchestrator.process_file(
                file_id=file_id,
                user_id=user_id,
                copybook_file_id=None,
                processing_options=parse_options
            )
            
            # Ensure workflow_id is in result
            if result and not result.get("workflow_id"):
                result["workflow_id"] = workflow_id
            
            self.logger.info(f"✅ Client data parsing complete: parsed_file_id={result.get('parsed_file_id')}, workflow_id={workflow_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Client data parsing failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_client_data_parse")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id if 'workflow_id' in locals() else None
            }
    
    async def orchestrate_client_data_embed(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate client data embedding.
        
        Flow:
        1. Route via FrontendGatewayService → ContentOrchestrator
        2. ContentOrchestrator handles embedding → EmbeddingService
        3. Store embeddings → Librarian
        4. Track lineage → Data Steward
        
        Args:
            file_id: File identifier
            parsed_file_id: Parsed file identifier
            content_metadata: Content metadata from parsing
            user_context: Optional user context (includes workflow_id)
            workflow_id: Optional workflow_id (if not in user_context)
        
        Returns:
            Dict with success status, embeddings_count, content_id, workflow_id
        """
        try:
            # Get workflow_id from user_context or parameter
            if not workflow_id:
                workflow_id = (
                    user_context.get("workflow_id") if user_context else None
                ) or str(uuid.uuid4())
            
            self.logger.info(f"🧬 Orchestrating client data embedding: file_id={file_id}, parsed_file_id={parsed_file_id} (workflow_id: {workflow_id})")
            
            # Compose ContentOrchestrator (Content realm) ✅
            if not self.content_orchestrator:
                self.content_orchestrator = await self._discover_content_orchestrator()
            
            if not self.content_orchestrator:
                raise ValueError("ContentOrchestrator not available - Content realm services must be initialized")
            
            # Use ContentJourneyOrchestrator.create_embeddings() method
            user_id = user_context.get("user_id") if user_context else "anonymous"
            result = await self.content_orchestrator.create_embeddings(
                parsed_file_id=parsed_file_id,
                user_id=user_id,
                file_id=file_id,
                user_context=user_context
            )
            
            # Ensure workflow_id is in result
            if result and not result.get("workflow_id"):
                result["workflow_id"] = workflow_id
            
            self.logger.info(f"✅ Client data embedding complete: content_id={result.get('content_id')}, workflow_id={workflow_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Client data embedding failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_client_data_embed")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id if 'workflow_id' in locals() else None
            }
    
    async def orchestrate_client_data_expose(
        self,
        file_id: str,
        parsed_file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate client data exposure.
        
        Flow:
        1. Route via FrontendGatewayService → ContentOrchestrator
        2. ContentOrchestrator exposes data (semantic view)
        
        Args:
            file_id: File identifier
            parsed_file_id: Optional parsed file identifier (if not provided, gets first one)
            user_context: Optional user context
        
        Returns:
            Dict with success status, parsed_data, content_metadata, embeddings info
        """
        try:
            self.logger.info(f"📤 Orchestrating client data exposure: file_id={file_id}")
            
            # Compose ContentOrchestrator (Content realm) ✅
            if not self.content_orchestrator:
                self.content_orchestrator = await self._discover_content_orchestrator()
            
            if not self.content_orchestrator:
                raise ValueError("ContentOrchestrator not available - Content realm services must be initialized")
            
            # Use ContentJourneyOrchestrator.expose_data() method
            result = await self.content_orchestrator.expose_data(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                user_context=user_context
            )
            
            self.logger.info(f"✅ Client data exposure complete: file_id={file_id}, parsed_file_id={parsed_file_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Client data exposure failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_client_data_expose")
            return {
                "success": False,
                "error": str(e)
            }

