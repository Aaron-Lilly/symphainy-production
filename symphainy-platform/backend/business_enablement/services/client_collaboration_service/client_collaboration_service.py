#!/usr/bin/env python3
"""
Client Collaboration Service

WHAT: Manages client artifact sharing and review workflow
HOW: Bridges MVP artifacts with client review/approval processes

This service enables clients to review, comment on, and approve artifacts
created during MVP engagements. It manages the collaboration workflow
between platform team and clients.

Use this to: Share artifacts with clients, manage review workflows, handle approvals
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class ClientCollaborationService(RealmServiceBase):
    """
    Client Collaboration Service for Business Enablement realm.
    
    Manages client artifact sharing and review workflow.
    Bridges MVP artifacts with client review/approval.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Client Collaboration Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.solution_composer = None
        self.journey_orchestrator = None
        self.curator = None
        self.post_office = None
        
        # Service state
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize Client Collaboration Service.
        
        Uses full utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Curator registration
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "client_collaboration_initialize_start",
            success=True
        )
        
        await super().initialize()
        
        try:
            # 1. Get Smart City services
            self.post_office = await self.get_post_office_api()
            
            # 2. Get Curator Foundation Service
            self.curator = self.di_container.get_foundation_service("CuratorFoundationService") if self.di_container else None
            
            # 3. Discover Solution and Journey services via Curator
            await self._discover_artifact_services()
            
            # 4. Register with Curator
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "client_collaboration",
                        "protocol": "ClientCollaborationProtocol",
                        "description": "Manage client artifact sharing and review workflow",
                        "contracts": {
                            "soa_api": {
                                "api_name": "share_artifact_with_client",
                                "endpoint": "/api/v1/client-collaboration/share-artifact",
                                "method": "POST",
                                "handler": self.share_artifact_with_client
                            }
                        }
                    }
                ],
                soa_apis=[
                    "share_artifact_with_client",
                    "get_client_artifacts",
                    "add_client_comment",
                    "approve_artifact",
                    "reject_artifact"
                ],
                mcp_tools=[],
                additional_metadata={
                    "service_type": "collaboration",
                    "realm": "business_enablement"
                }
            )
            
            self.is_initialized = True
            
            # Record health metric
            await self.record_health_metric("client_collaboration_initialized", 1.0, {
                "service": "client_collaboration"
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "client_collaboration_initialize_complete",
                success=True
            )
            
            self.logger.info("✅ Client Collaboration Service initialized successfully")
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "client_collaboration_initialize")
            
            # Record health metric (failure)
            await self.record_health_metric("client_collaboration_initialize_failed", 1.0, {
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "client_collaboration_initialize_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Client Collaboration Service initialization failed: {e}")
            return False
    
    async def _discover_artifact_services(self):
        """Discover Solution and Journey orchestrator services via Curator."""
        try:
            if not self.curator:
                self.logger.warning("⚠️ Curator not available - artifact services will not be discovered")
                return
            
            # Discover Solution Composer Service
            try:
                self.solution_composer = await self.curator.discover_service_by_name("SolutionComposerService")
                if self.solution_composer:
                    self.logger.info("✅ Discovered SolutionComposerService")
                else:
                    self.logger.warning("⚠️ SolutionComposerService not yet available")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to discover SolutionComposerService: {e}")
            
            # Discover Structured Journey Orchestrator Service
            try:
                self.journey_orchestrator = await self.curator.discover_service_by_name("StructuredJourneyOrchestratorService")
                if self.journey_orchestrator:
                    self.logger.info("✅ Discovered StructuredJourneyOrchestratorService")
                else:
                    self.logger.warning("⚠️ StructuredJourneyOrchestratorService not yet available")
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to discover StructuredJourneyOrchestratorService: {e}")
            
        except Exception as e:
            self.logger.error(f"❌ Artifact service discovery failed: {e}")
    
    async def share_artifact_with_client(
        self,
        artifact_id: str,
        artifact_type: str,  # "solution" or "journey"
        client_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Share artifact with client for review.
        
        Updates artifact status: "draft" → "review"
        Notifies client (via Post Office or email).
        
        Args:
            artifact_id: Artifact ID to share
            artifact_type: Type of artifact ("solution" or "journey")
            client_id: Client ID
            user_context: User context for security and tenant validation
        
        Returns:
            Result with success status and artifact info
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "share_artifact_with_client_start",
            success=True,
            details={"artifact_id": artifact_id, "artifact_type": artifact_type, "client_id": client_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "share_artifact_with_client", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "share_artifact_with_client",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("share_artifact_with_client_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get artifact from Curator
            if not self.curator:
                return {
                    "success": False,
                    "error": "Curator service not available"
                }
            
            artifact = await self.curator.get_artifact(artifact_id, user_context)
            
            if not artifact:
                return {
                    "success": False,
                    "error": f"Artifact {artifact_id} not found"
                }
            
            # Validate client_id matches
            artifact_client_id = artifact.get("client_id")
            if artifact_client_id and artifact_client_id != client_id:
                return {
                    "success": False,
                    "error": f"Artifact client_id ({artifact_client_id}) does not match provided client_id ({client_id})"
                }
            
            # Validate artifact_type matches
            artifact_entry = self.curator.artifact_registry.get(artifact_id) if hasattr(self.curator, 'artifact_registry') else None
            if artifact_entry and artifact_entry.get("artifact_type") != artifact_type:
                return {
                    "success": False,
                    "error": f"Artifact type mismatch: expected {artifact_type}, got {artifact_entry.get('artifact_type')}"
                }
            
            # Update status to "review"
            if artifact_type == "solution":
                if not self.solution_composer:
                    return {
                        "success": False,
                        "error": "SolutionComposerService not available"
                    }
                update_result = await self.solution_composer.update_solution_artifact_status(
                    artifact_id, "review", user_context
                )
            else:  # journey
                if not self.journey_orchestrator:
                    return {
                        "success": False,
                        "error": "StructuredJourneyOrchestratorService not available"
                    }
                update_result = await self.journey_orchestrator.update_journey_artifact_status(
                    artifact_id, "review", user_context
                )
            
            if not update_result.get("success"):
                return update_result
            
            # Notify client (via Post Office)
            if self.post_office:
                try:
                    notification = {
                        "type": "artifact_shared",
                        "client_id": client_id,
                        "artifact_id": artifact_id,
                        "artifact_type": artifact_type,
                        "message": f"Artifact {artifact_id} has been shared for your review",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    # TODO: Implement Post Office notification
                    # await self.post_office.send_notification(notification)
                    self.logger.info(f"📧 Notification prepared for client {client_id} (Post Office integration pending)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to send notification: {e}")
            
            result = {
                "success": True,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id,
                "status": "review",
                "shared_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("share_artifact_with_client_success", 1.0, {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "share_artifact_with_client_complete",
                success=True,
                details={"artifact_id": artifact_id}
            )
            
            self.logger.info(f"✅ Artifact {artifact_id} shared with client {client_id} for review")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "share_artifact_with_client", details={
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("share_artifact_with_client_failed", 1.0, {
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "share_artifact_with_client_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Share artifact with client failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_client_artifacts(
        self,
        client_id: str,
        artifact_type: Optional[str] = None,  # "solution" or "journey"
        status: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all artifacts for client (filtered by type and status).
        
        Used by client UI to display artifacts for review.
        
        Args:
            client_id: Client ID
            artifact_type: Optional filter by artifact type ("solution" or "journey")
            status: Optional filter by status
            user_context: User context for security and tenant validation
        
        Returns:
            Dictionary of artifacts keyed by artifact_id
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "get_client_artifacts_start",
            success=True,
            details={"client_id": client_id, "artifact_type": artifact_type, "status": status}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "get_client_artifacts", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "get_client_artifacts",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("get_client_artifacts_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            if not self.curator:
                return {
                    "success": False,
                    "error": "Curator service not available"
                }
            
            # Get artifacts from Curator
            artifacts = await self.curator.list_client_artifacts(
                client_id, artifact_type, status, user_context
            )
            
            result = {
                "success": True,
                "client_id": client_id,
                "artifacts": artifacts,
                "count": len(artifacts),
                "filters": {
                    "artifact_type": artifact_type,
                    "status": status
                }
            }
            
            # Record health metric
            await self.record_health_metric("get_client_artifacts_success", 1.0, {
                "client_id": client_id,
                "count": len(artifacts)
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "get_client_artifacts_complete",
                success=True,
                details={"client_id": client_id, "count": len(artifacts)}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "get_client_artifacts", details={"client_id": client_id})
            
            # Record health metric (failure)
            await self.record_health_metric("get_client_artifacts_failed", 1.0, {
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "get_client_artifacts_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Get client artifacts failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_client_comment(
        self,
        artifact_id: str,
        artifact_type: str,
        comment: Dict[str, Any],  # {"comment": "...", "section": "...", "user": "..."}
        client_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add client comment to artifact.
        
        Comments are stored with artifact (via artifact update).
        
        Args:
            artifact_id: Artifact ID
            artifact_type: Type of artifact ("solution" or "journey")
            comment: Comment data (comment text, section, user, etc.)
            client_id: Client ID
            user_context: User context for security and tenant validation
        
        Returns:
            Updated artifact with comment added
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "add_client_comment_start",
            success=True,
            details={"artifact_id": artifact_id, "artifact_type": artifact_type, "client_id": client_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "add_client_comment", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "add_client_comment",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("add_client_comment_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get artifact
            if not self.curator:
                return {
                    "success": False,
                    "error": "Curator service not available"
                }
            
            artifact = await self.curator.get_artifact(artifact_id, user_context)
            
            if not artifact:
                return {
                    "success": False,
                    "error": f"Artifact {artifact_id} not found"
                }
            
            # Validate client_id
            artifact_client_id = artifact.get("client_id")
            if artifact_client_id and artifact_client_id != client_id:
                return {
                    "success": False,
                    "error": f"Artifact client_id ({artifact_client_id}) does not match provided client_id ({client_id})"
                }
            
            # Add comment to artifact
            if "comments" not in artifact:
                artifact["comments"] = []
            
            comment_entry = {
                **comment,
                "comment_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "client_id": client_id,
                "user_id": user_context.get("user_id") if user_context else None
            }
            
            artifact["comments"].append(comment_entry)
            artifact["updated_at"] = datetime.utcnow().isoformat()
            
            # Update artifact in Curator
            await self.curator.update_artifact(
                artifact_id=artifact_id,
                artifact_data=artifact,
                user_context=user_context
            )
            
            # Also update via Solution/Journey orchestrator to persist
            if artifact_type == "solution":
                if self.solution_composer:
                    # Get current artifact to preserve status
                    current_result = await self.solution_composer.get_solution_artifact(artifact_id, user_context)
                    if current_result.get("success"):
                        current_artifact = current_result["artifact"]
                        # Merge comments
                        current_artifact["comments"] = artifact["comments"]
                        # Store updated artifact
                        await self.solution_composer.store_document(
                            document_data=current_artifact,
                            metadata={
                                "type": "solution_artifact",
                                "artifact_id": artifact_id,
                                "has_comments": True
                            }
                        )
            else:  # journey
                if self.journey_orchestrator:
                    # Get current artifact to preserve status
                    current_result = await self.journey_orchestrator.get_journey_artifact(artifact_id, user_context)
                    if current_result.get("success"):
                        current_artifact = current_result["artifact"]
                        # Merge comments
                        current_artifact["comments"] = artifact["comments"]
                        # Store updated artifact
                        await self.journey_orchestrator.store_document(
                            document_data=current_artifact,
                            metadata={
                                "type": "journey_artifact",
                                "artifact_id": artifact_id,
                                "has_comments": True
                            }
                        )
            
            result = {
                "success": True,
                "artifact_id": artifact_id,
                "comment": comment_entry,
                "total_comments": len(artifact["comments"])
            }
            
            # Record health metric
            await self.record_health_metric("add_client_comment_success", 1.0, {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "add_client_comment_complete",
                success=True,
                details={"artifact_id": artifact_id, "comment_id": comment_entry["comment_id"]}
            )
            
            self.logger.info(f"✅ Comment added to artifact {artifact_id} by client {client_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "add_client_comment", details={
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("add_client_comment_failed", 1.0, {
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "add_client_comment_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Add client comment failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def approve_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        client_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Client approves artifact.
        
        Updates artifact status: "review" → "approved"
        
        Args:
            artifact_id: Artifact ID
            artifact_type: Type of artifact ("solution" or "journey")
            client_id: Client ID
            user_context: User context for security and tenant validation
        
        Returns:
            Approved artifact
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "approve_artifact_start",
            success=True,
            details={"artifact_id": artifact_id, "artifact_type": artifact_type, "client_id": client_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "approve_artifact", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "approve_artifact",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("approve_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get artifact
            if not self.curator:
                return {
                    "success": False,
                    "error": "Curator service not available"
                }
            
            artifact = await self.curator.get_artifact(artifact_id, user_context)
            
            if not artifact:
                return {
                    "success": False,
                    "error": f"Artifact {artifact_id} not found"
                }
            
            # Validate client_id
            artifact_client_id = artifact.get("client_id")
            if artifact_client_id and artifact_client_id != client_id:
                return {
                    "success": False,
                    "error": f"Artifact client_id ({artifact_client_id}) does not match provided client_id ({client_id})"
                }
            
            # Validate status is "review"
            current_status = artifact.get("status")
            if current_status != "review":
                return {
                    "success": False,
                    "error": f"Artifact must be in 'review' status to approve. Current status: {current_status}"
                }
            
            # Update status to "approved"
            if artifact_type == "solution":
                if not self.solution_composer:
                    return {
                        "success": False,
                        "error": "SolutionComposerService not available"
                    }
                update_result = await self.solution_composer.update_solution_artifact_status(
                    artifact_id, "approved", user_context
                )
            else:  # journey
                if not self.journey_orchestrator:
                    return {
                        "success": False,
                        "error": "StructuredJourneyOrchestratorService not available"
                    }
                update_result = await self.journey_orchestrator.update_journey_artifact_status(
                    artifact_id, "approved", user_context
                )
            
            if not update_result.get("success"):
                return update_result
            
            result = {
                "success": True,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id,
                "status": "approved",
                "approved_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("approve_artifact_success", 1.0, {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "approve_artifact_complete",
                success=True,
                details={"artifact_id": artifact_id}
            )
            
            self.logger.info(f"✅ Artifact {artifact_id} approved by client {client_id}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "approve_artifact", details={
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("approve_artifact_failed", 1.0, {
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "approve_artifact_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Approve artifact failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reject_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        rejection_reason: str,
        client_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Client rejects artifact.
        
        Updates artifact status: "review" → "draft"
        Adds rejection reason as comment.
        
        Args:
            artifact_id: Artifact ID
            artifact_type: Type of artifact ("solution" or "journey")
            rejection_reason: Reason for rejection
            client_id: Client ID
            user_context: User context for security and tenant validation
        
        Returns:
            Rejected artifact with rejection comment
        """
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "reject_artifact_start",
            success=True,
            details={"artifact_id": artifact_id, "artifact_type": artifact_type, "client_id": client_id}
        )
        
        # Security and Tenant Validation
        if user_context:
            security = self.get_security()
            if security and not await security.check_permissions(user_context, "reject_artifact", "execute"):
                await self.handle_error_with_audit(
                    ValueError("Permission denied"),
                    "reject_artifact",
                    details={"user_id": user_context.get("user_id")}
                )
                await self.log_operation_with_telemetry("reject_artifact_complete", success=False)
                return {
                    "success": False,
                    "error": "Permission denied"
                }
        
        try:
            # Get artifact
            if not self.curator:
                return {
                    "success": False,
                    "error": "Curator service not available"
                }
            
            artifact = await self.curator.get_artifact(artifact_id, user_context)
            
            if not artifact:
                return {
                    "success": False,
                    "error": f"Artifact {artifact_id} not found"
                }
            
            # Validate client_id
            artifact_client_id = artifact.get("client_id")
            if artifact_client_id and artifact_client_id != client_id:
                return {
                    "success": False,
                    "error": f"Artifact client_id ({artifact_client_id}) does not match provided client_id ({client_id})"
                }
            
            # Validate status is "review"
            current_status = artifact.get("status")
            if current_status != "review":
                return {
                    "success": False,
                    "error": f"Artifact must be in 'review' status to reject. Current status: {current_status}"
                }
            
            # Add rejection comment
            rejection_comment = {
                "comment": f"REJECTED: {rejection_reason}",
                "section": "artifact_rejection",
                "type": "rejection",
                "user": user_context.get("user_id") if user_context else "client",
                "timestamp": datetime.utcnow().isoformat(),
                "client_id": client_id
            }
            
            # Add comment first
            comment_result = await self.add_client_comment(
                artifact_id, artifact_type, rejection_comment, client_id, user_context
            )
            
            if not comment_result.get("success"):
                return comment_result
            
            # Update status to "draft"
            if artifact_type == "solution":
                if not self.solution_composer:
                    return {
                        "success": False,
                        "error": "SolutionComposerService not available"
                    }
                update_result = await self.solution_composer.update_solution_artifact_status(
                    artifact_id, "draft", user_context
                )
            else:  # journey
                if not self.journey_orchestrator:
                    return {
                        "success": False,
                        "error": "StructuredJourneyOrchestratorService not available"
                    }
                update_result = await self.journey_orchestrator.update_journey_artifact_status(
                    artifact_id, "draft", user_context
                )
            
            if not update_result.get("success"):
                return update_result
            
            result = {
                "success": True,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id,
                "status": "draft",
                "rejection_reason": rejection_reason,
                "rejected_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("reject_artifact_success", 1.0, {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "reject_artifact_complete",
                success=True,
                details={"artifact_id": artifact_id}
            )
            
            self.logger.info(f"✅ Artifact {artifact_id} rejected by client {client_id}: {rejection_reason}")
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "reject_artifact", details={
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "client_id": client_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("reject_artifact_failed", 1.0, {
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry(
                "reject_artifact_complete",
                success=False,
                details={"error": str(e)}
            )
            
            self.logger.error(f"❌ Reject artifact failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "solution_composer_available": self.solution_composer is not None,
            "journey_orchestrator_available": self.journey_orchestrator is not None,
            "curator_available": self.curator is not None
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "collaboration_service",
            "realm": "business_enablement",
            "layer": "client_collaboration",
            "capabilities": ["artifact_sharing", "client_review", "approval_workflow", "comment_management"],
            "soa_apis": [
                "share_artifact_with_client",
                "get_client_artifacts",
                "add_client_comment",
                "approve_artifact",
                "reject_artifact"
            ],
            "mcp_tools": [],
            "composes": "solution_services, journey_services"
        }









