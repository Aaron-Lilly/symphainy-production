#!/usr/bin/env python3
"""
Content Solution Orchestrator Service

WHAT: Orchestrates content solution flow: Solution → Journey → Content Realm
HOW: Lightweight shell that delegates to ContentJourneyOrchestrator and orchestrates platform correlation

This service ensures Content realm follows the proper pattern:
Solution → Journey → Content Realm (not bypassing Solution realm)

Architecture:
- Extends OrchestratorBase (orchestrator pattern)
- Routes to ContentJourneyOrchestrator (Journey realm)
- Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
- Ensures all platform correlation data follows content operations through journey
- Registered with Curator for discovery
"""

import os
import sys
import uuid
import json
from typing import Dict, Any, Optional, List, Callable

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class ContentSolutionOrchestratorService(OrchestratorBase):
    """
    Content Solution Orchestrator Service - Lightweight shell with platform correlation.
    
    "One Stop Shopping" for:
    1. Content Operations (via ContentJourneyOrchestrator - Journey realm)
    2. Platform Correlation Data (auth, session, workflow, events, telemetry)
    
    Orchestrates the complete content solution flow:
    1. Upload: File upload → ContentJourneyOrchestrator (Journey realm)
    2. Parse: File parsing → ContentJourneyOrchestrator (Journey realm)
    3. Embed: Semantic embeddings → ContentJourneyOrchestrator (Journey realm)
    4. Expose: Semantic layer exposure → ContentJourneyOrchestrator (Journey realm)
    
    Key Principles:
    - Routes to ContentJourneyOrchestrator (Journey realm) - follows Solution → Journey → Realm pattern
    - Orchestrates platform correlation (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)
    - Ensures all platform correlation data follows content operations through journey
    - correlation_id propagation for end-to-end tracking
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
        Initialize Content Solution Orchestrator Service.
        
        Args:
            service_name: Service name (typically "ContentSolutionOrchestratorService")
            realm_name: Realm name (typically "solution")
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
        
        # Journey orchestrators (discovered via Curator)
        self.content_journey_orchestrator = None  # Content operations orchestration
        
        # Platform correlation services (discovered via Curator)
        self.security_guard = None
        self.traffic_cop = None
        self.conductor = None
        self.post_office = None
        self.nurse = None
    
    # ============================================================================
    # UNIFIED SOA API → MCP TOOL PATTERN (Phase 3.2.5)
    # ============================================================================
    
    def _define_soa_api_handlers(self) -> Dict[str, Any]:
        """
        Define Content Solution Orchestrator SOA APIs.
        
        UNIFIED PATTERN: MCP Server automatically registers these as MCP Tools.
        
        Returns:
            Dict of SOA API definitions with handlers, input schemas, and descriptions
        """
        return {
            "orchestrate_content_upload": {
                "handler": self.orchestrate_content_upload,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_data": {
                            "type": "string",
                            "format": "binary",
                            "description": "File data as bytes"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "Name of the file"
                        },
                        "file_type": {
                            "type": "string",
                            "description": "MIME type or file extension"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context (includes correlation_id)"
                        }
                    },
                    "required": ["file_data", "file_name", "file_type"]
                },
                "description": "Orchestrate content upload with platform correlation"
            },
            "orchestrate_content_parse": {
                "handler": self.orchestrate_content_parse,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "File identifier from upload"
                        },
                        "parse_options": {
                            "type": "object",
                            "description": "Optional parsing options",
                            "default": None
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": ["file_id"]
                },
                "description": "Orchestrate content parsing with platform correlation"
            },
            "orchestrate_content_embed": {
                "handler": self.orchestrate_content_embed,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "File identifier from upload"
                        },
                        "embedding_options": {
                            "type": "object",
                            "description": "Optional embedding options",
                            "default": None
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": ["file_id"]
                },
                "description": "Orchestrate content embedding with platform correlation"
            },
            "orchestrate_content_expose": {
                "handler": self.orchestrate_content_expose,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_id": {
                            "type": "string",
                            "description": "File identifier from upload"
                        },
                        "parsed_file_id": {
                            "type": "string",
                            "description": "Optional parsed file identifier (if not provided, gets first one)"
                        },
                        "user_context": {
                            "type": "object",
                            "description": "Optional user context"
                        }
                    },
                    "required": ["file_id"]
                },
                "description": "Orchestrate content exposure with platform correlation"
            }
        }
    
    async def _initialize_mcp_server(self):
        """
        Initialize Solution Realm MCP Server (unified pattern).
        
        MCP Server automatically registers SOA APIs as MCP Tools.
        """
        try:
            from foundations.agentic_foundation.mcp_server.mcp_server_base import MCPServerBase
            
            # Create MCP Server instance
            self.mcp_server = MCPServerBase(
                service_name=self.service_name,
                soa_apis=self._define_soa_api_handlers(),
                di_container=self.di_container
            )
            
            # MCP Server automatically registers SOA APIs as MCP Tools
            if self.logger:
                self.logger.info(f"✅ {self.service_name} MCP Server initialized")
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️ Failed to initialize MCP Server: {e}")
    
    # ============================================================================
    # PLATFORM CORRELATION (Phase 0.4 - Data as First-Class Citizen)
    # ============================================================================
    
    async def _orchestrate_platform_correlation(
        self,
        operation: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate platform correlation data to follow content operations through journey.
        
        "One Stop Shopping" for all platform correlation:
        - Security Guard: Validate auth & tenant
        - Traffic Cop: Manage session/state
        - Conductor: Track workflow
        - Post Office: Publish events & messaging
        - Nurse: Record telemetry & observability
        
        Args:
            operation: Operation name (e.g., "content_upload", "content_parse")
            user_context: Optional user context
        
        Returns:
            Enhanced user_context with all platform correlation data
        """
        # Generate correlation_id if not present
        correlation_id = user_context.get("correlation_id") if user_context else str(uuid.uuid4())
        workflow_id = user_context.get("workflow_id") if user_context else None
        
        # Discover platform correlation services (lazy-load)
        if not self.security_guard:
            self.security_guard = await self.get_security_guard_api()
        if not self.traffic_cop:
            self.traffic_cop = await self.get_traffic_cop_api()
        if not self.conductor:
            self.conductor = await self.get_conductor_api()
        if not self.post_office:
            self.post_office = await self.get_post_office_api()
        if not self.nurse:
            self.nurse = await self.get_nurse_api()
        
        # Build enhanced correlation context
        correlation_context = {
            "correlation_id": correlation_id,
            "workflow_id": workflow_id,
            "operation": operation,
            "timestamp": json.dumps({"timestamp": str(uuid.uuid4())})  # Placeholder
        }
        
        # Merge with user_context
        if user_context:
            correlation_context.update(user_context)
        
        return correlation_context
    
    async def _discover_content_journey_orchestrator(self):
        """Discover Content Journey Orchestrator via Curator."""
        try:
            curator = await self.get_foundation_service("CuratorFoundationService")
            if curator:
                content_journey_orchestrator = await curator.discover_service_by_name("ContentJourneyOrchestratorService")
                if content_journey_orchestrator:
                    self.logger.info("✅ Discovered ContentJourneyOrchestratorService")
                    return content_journey_orchestrator
        except Exception as e:
            self.logger.warning(f"⚠️ ContentJourneyOrchestratorService not available: {e}")
        return None
    
    # ============================================================================
    # CONTENT OPERATIONS (Solution → Journey → Content Realm Pattern)
    # ============================================================================
    
    async def orchestrate_content_upload(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate content upload with platform correlation.
        
        Flow:
        1. Orchestrate platform correlation (auth, session, workflow, events, telemetry)
        2. Delegate to ContentJourneyOrchestrator (Journey realm)
        3. Record completion in platform correlation
        
        Args:
            file_data: File data as bytes
            file_name: Name of the file
            file_type: MIME type or file extension
            user_context: Optional user context (includes correlation_id)
        
        Returns:
            Dict with success status, file_id, correlation_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="content_upload",
                user_context=user_context
            )
            
            # Step 2: Route to Content Journey Orchestrator (Journey realm)
            if not self.content_journey_orchestrator:
                self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
            
            if not self.content_journey_orchestrator:
                raise ValueError("ContentJourneyOrchestratorService not available - Journey services must be initialized")
            
            # Step 3: Execute content operation with correlation context
            user_id = correlation_context.get("user_id") if correlation_context else "anonymous"
            session_id = correlation_context.get("session_id") if correlation_context else None
            
            result = await self.content_journey_orchestrator.handle_content_upload(
                file_data=file_data,
                filename=file_name,
                file_type=file_type,
                user_id=user_id,
                session_id=session_id,
                user_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Content upload failed: {e}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_content_upload")
            correlation_id = user_context.get("correlation_id") if user_context else None
            return {
                "success": False,
                "error": str(e),
                "correlation_id": correlation_id
            }
    
    async def orchestrate_content_parse(
        self,
        file_id: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate content parsing with platform correlation.
        
        Flow:
        1. Orchestrate platform correlation
        2. Delegate to ContentJourneyOrchestrator (Journey realm)
        3. Record completion in platform correlation
        
        Args:
            file_id: File identifier from upload
            parse_options: Optional parsing options
            user_context: Optional user context
        
        Returns:
            Dict with success status, parse_result, parsed_file_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="content_parse",
                user_context=user_context
            )
            
            # Step 2: Route to Content Journey Orchestrator
            if not self.content_journey_orchestrator:
                self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
            
            if not self.content_journey_orchestrator:
                raise ValueError("ContentJourneyOrchestratorService not available")
            
            # Step 3: Execute content operation
            result = await self.content_journey_orchestrator.handle_content_parse(
                file_id=file_id,
                parse_options=parse_options,
                user_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Content parsing failed: {e}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_content_parse")
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id
            }
    
    async def orchestrate_content_embed(
        self,
        file_id: str,
        embedding_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate content embedding with platform correlation.
        
        Flow:
        1. Orchestrate platform correlation
        2. Delegate to ContentJourneyOrchestrator (Journey realm)
        3. Record completion in platform correlation
        
        Args:
            file_id: File identifier from upload
            embedding_options: Optional embedding options
            user_context: Optional user context
        
        Returns:
            Dict with success status, embeddings_count, content_id
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="content_embed",
                user_context=user_context
            )
            
            # Step 2: Route to Content Journey Orchestrator
            if not self.content_journey_orchestrator:
                self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
            
            if not self.content_journey_orchestrator:
                raise ValueError("ContentJourneyOrchestratorService not available")
            
            # Step 3: Execute content operation
            result = await self.content_journey_orchestrator.handle_content_embed(
                file_id=file_id,
                embedding_options=embedding_options,
                user_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Content embedding failed: {e}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_content_embed")
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id
            }
    
    async def orchestrate_content_expose(
        self,
        file_id: str,
        parsed_file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate content exposure with platform correlation.
        
        Flow:
        1. Orchestrate platform correlation
        2. Delegate to ContentJourneyOrchestrator (Journey realm)
        3. Record completion in platform correlation
        
        Args:
            file_id: File identifier from upload
            parsed_file_id: Optional parsed file identifier
            user_context: Optional user context
        
        Returns:
            Dict with exposed content data
        """
        try:
            # Step 1: Orchestrate platform correlation
            correlation_context = await self._orchestrate_platform_correlation(
                operation="content_expose",
                user_context=user_context
            )
            
            # Step 2: Route to Content Journey Orchestrator
            if not self.content_journey_orchestrator:
                self.content_journey_orchestrator = await self._discover_content_journey_orchestrator()
            
            if not self.content_journey_orchestrator:
                raise ValueError("ContentJourneyOrchestratorService not available")
            
            # Step 3: Execute content operation
            result = await self.content_journey_orchestrator.handle_content_expose(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                user_context=correlation_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Content exposure failed: {e}")
            await self._realm_service.handle_error_with_audit(e, "orchestrate_content_expose")
            return {
                "success": False,
                "error": str(e),
                "file_id": file_id
            }


