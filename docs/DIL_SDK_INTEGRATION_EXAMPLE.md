# DIL SDK Integration Example: Complete Data Lifecycle

**Date:** December 11, 2025  
**Purpose:** Demonstrate how Business Enablement orchestrators use DIL SDK to interact with all Smart City services throughout the complete data lifecycle.

---

## Overview

This document shows how a Business Enablement orchestrator (e.g., `ContentAnalysisOrchestrator`) uses the DIL SDK to orchestrate the complete data lifecycle, ensuring every data path lands in Smart City's canonical data plane.

---

## Complete Data Lifecycle Flow

```
User Upload → Security Guard (auth) → Content Steward (raw data) 
  → Business Enablement (parse) → Content Steward (parsed data)
  → Business Enablement (extract metadata) → Librarian (content metadata)
  → Business Enablement (create embeddings) → Librarian (semantic data)
  → Data Steward (governance + lineage) → Conductor (workflow) 
  → Post Office (events) → Traffic Cop (sessions) → Nurse (telemetry)
  → City Manager (orchestration + governance)
```

---

## Integration Example: ContentAnalysisOrchestrator with DIL SDK

```python
#!/usr/bin/env python3
"""
Content Analysis Orchestrator - DIL SDK Integration Example

Demonstrates complete data lifecycle using DIL SDK to interact with all Smart City services.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from bases.orchestrator_base import OrchestratorBase
from backend.smart_city.sdk.dil_sdk import DILSDK


class ContentAnalysisOrchestrator(OrchestratorBase):
    """
    Content Analysis Orchestrator using DIL SDK.
    
    Orchestrates the complete data lifecycle:
    1. Security Guard → Authentication & Authorization
    2. Content Steward → Raw & Parsed Data Storage
    3. Librarian → Semantic Data & Content Metadata
    4. Data Steward → Governance & Lineage
    5. Conductor → Workflow Orchestration
    6. Post Office → Event Publishing
    7. Traffic Cop → Session Management
    8. Nurse → Observability & Telemetry
    9. City Manager → Platform Orchestration
    """
    
    def __init__(self, di_container: Any):
        """Initialize orchestrator with DIL SDK."""
        super().__init__(di_container=di_container)
        
        # Initialize DIL SDK
        self.dil_sdk = None  # Will be initialized in initialize()
        
        # Smart City service references (for direct access when needed)
        self.security_guard = None
        self.conductor = None
        self.post_office = None
        self.traffic_cop = None
        self.city_manager = None
    
    async def initialize(self) -> bool:
        """Initialize orchestrator and DIL SDK."""
        try:
            # Get Smart City services for DIL SDK
            content_steward = await self.get_content_steward_api()
            librarian = await self.get_librarian_api()
            data_steward = await self.get_data_steward_api()
            nurse = await self.get_nurse_api()
            
            # Initialize DIL SDK
            smart_city_services = {
                "content_steward": content_steward,
                "librarian": librarian,
                "data_steward": data_steward,
                "nurse": nurse
            }
            self.dil_sdk = DILSDK(smart_city_services, logger=self.logger)
            
            # Get other Smart City services for direct access
            self.security_guard = await self.get_security_guard_api()
            self.conductor = await self.get_conductor_api()
            self.post_office = await self.get_post_office_api()
            self.traffic_cop = await self.get_traffic_cop_api()
            self.city_manager = await self.get_city_manager_api()
            
            self.logger.info("✅ ContentAnalysisOrchestrator initialized with DIL SDK")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize orchestrator: {e}")
            return False
    
    async def process_file_upload_complete_lifecycle(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        user_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process file upload through complete data lifecycle.
        
        This method demonstrates the full integration with all Smart City services.
        """
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"
        
        try:
            # ========================================================================
            # STEP 1: Security Guard → Authentication & Authorization
            # ========================================================================
            self.logger.info("🔐 Step 1: Security Guard - Authentication & Authorization")
            
            if not self.security_guard:
                raise ValueError("Security Guard not available")
            
            # Authenticate user
            auth_result = await self.security_guard.authenticate_user(
                user_context=user_context
            )
            if not auth_result.get("authenticated"):
                raise PermissionError("User authentication failed")
            
            # Authorize file upload
            authz_result = await self.security_guard.authorize_action(
                action="file_upload",
                resource="content_pillar",
                user_context=user_context
            )
            if not authz_result.get("authorized"):
                raise PermissionError("User not authorized to upload files")
            
            # Record security event via Nurse (via DIL SDK)
            await self.dil_sdk.record_platform_event(
                event_type="log",
                event_data={
                    "level": "info",
                    "message": f"User authenticated and authorized for file upload: {file_name}",
                    "service_name": "ContentAnalysisOrchestrator",
                    "metadata": {
                        "user_id": user_context.get("user_id"),
                        "action": "file_upload"
                    }
                },
                trace_id=trace_id,
                user_context=user_context
            )
            
            # ========================================================================
            # STEP 2: Traffic Cop → Session Management
            # ========================================================================
            self.logger.info("🚦 Step 2: Traffic Cop - Session Management")
            
            if self.traffic_cop and session_id:
                # Get or create session
                session = await self.traffic_cop.get_session(session_id)
                if not session:
                    session = await self.traffic_cop.create_session(
                        session_id=session_id,
                        user_context=user_context
                    )
                
                # Update session with workflow context
                await self.traffic_cop.update_session(
                    session_id=session_id,
                    updates={
                        "current_workflow": workflow_id,
                        "workflow_type": "file_upload",
                        "status": "processing"
                    }
                )
            
            # ========================================================================
            # STEP 3: Content Steward → Raw Data Storage (via DIL SDK)
            # ========================================================================
            self.logger.info("📦 Step 3: Content Steward - Raw Data Storage")
            
            # Upload file via DIL SDK
            upload_result = await self.dil_sdk.upload_file(
                file_data=file_data,
                file_name=file_name,
                file_type=file_type,
                metadata={
                    "description": f"Uploaded via ContentAnalysisOrchestrator",
                    "workflow_id": workflow_id,
                    "trace_id": trace_id
                },
                user_context=user_context
            )
            
            file_id = upload_result["file_id"]
            self.logger.info(f"✅ File uploaded: {file_id}")
            
            # Record platform event
            await self.dil_sdk.record_platform_event(
                event_type="log",
                event_data={
                    "level": "info",
                    "message": f"File uploaded: {file_name}",
                    "service_name": "ContentAnalysisOrchestrator",
                    "metadata": {"file_id": file_id, "file_size": len(file_data)}
                },
                trace_id=trace_id,
                user_context=user_context
            )
            
            # ========================================================================
            # STEP 4: Conductor → Workflow Orchestration
            # ========================================================================
            self.logger.info("🎼 Step 4: Conductor - Workflow Orchestration")
            
            if self.conductor:
                # Start workflow
                workflow = await self.conductor.start_workflow(
                    workflow_id=workflow_id,
                    workflow_type="file_processing",
                    initial_state={
                        "file_id": file_id,
                        "file_name": file_name,
                        "status": "parsing"
                    },
                    user_context=user_context
                )
                
                # Record workflow start event
                await self.dil_sdk.record_platform_event(
                    event_type="log",
                    event_data={
                        "level": "info",
                        "message": f"Workflow started: {workflow_id}",
                        "service_name": "ContentAnalysisOrchestrator",
                        "metadata": {"workflow_id": workflow_id, "workflow_type": "file_processing"}
                    },
                    trace_id=trace_id,
                    user_context=user_context
                )
            
            # ========================================================================
            # STEP 5: Business Enablement → Parse File
            # ========================================================================
            self.logger.info("🔧 Step 5: Business Enablement - Parse File")
            
            # Get File Parser Service (Business Enablement enabling service)
            file_parser = await self.get_enabling_service("FileParserService")
            if not file_parser:
                raise ValueError("FileParserService not available")
            
            # Parse file
            parse_result = await file_parser.parse_file(
                file_id=file_id,
                file_data=file_data,
                file_type=file_type,
                user_context=user_context
            )
            
            parsed_file_id = parse_result.get("parsed_file_id")
            parsed_file_data = parse_result.get("parsed_file_data")
            format_type = parse_result.get("format_type", "parquet")
            content_type = parse_result.get("content_type", "structured")
            
            # ========================================================================
            # STEP 6: Content Steward → Store Parsed Data (via DIL SDK)
            # ========================================================================
            self.logger.info("📦 Step 6: Content Steward - Store Parsed Data")
            
            parsed_storage_result = await self.dil_sdk.store_parsed_file(
                file_id=file_id,
                parsed_file_data=parsed_file_data,
                format_type=format_type,
                content_type=content_type,
                parse_result=parse_result,
                user_context=user_context
            )
            
            parsed_file_id = parsed_storage_result.get("parsed_file_id", parsed_file_id)
            self.logger.info(f"✅ Parsed file stored: {parsed_file_id}")
            
            # ========================================================================
            # STEP 7: Data Steward → Track Lineage (via DIL SDK)
            # ========================================================================
            self.logger.info("📋 Step 7: Data Steward - Track Lineage")
            
            lineage_result = await self.dil_sdk.track_lineage(
                lineage_data={
                    "source_id": file_id,
                    "target_id": parsed_file_id,
                    "operation": "parse",
                    "operation_type": "file_parsing",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {
                        "format_type": format_type,
                        "content_type": content_type,
                        "workflow_id": workflow_id
                    }
                },
                user_context=user_context
            )
            
            lineage_id = lineage_result.get("lineage_id")
            self.logger.info(f"✅ Lineage tracked: {lineage_id}")
            
            # ========================================================================
            # STEP 8: Business Enablement → Extract Content Metadata
            # ========================================================================
            self.logger.info("🔍 Step 8: Business Enablement - Extract Content Metadata")
            
            # Extract metadata from parsed file
            # (In future, this will be a dedicated ContentMetadataExtractionService)
            content_metadata = {
                "content_type": content_type,
                "format_type": format_type,
                "schema": parse_result.get("schema", {}),
                "row_count": parse_result.get("row_count", 0),
                "column_count": parse_result.get("column_count", 0),
                "column_names": parse_result.get("column_names", []),
                "data_types": parse_result.get("data_types", {})
            }
            
            # ========================================================================
            # STEP 9: Librarian → Store Content Metadata (via DIL SDK)
            # ========================================================================
            self.logger.info("📚 Step 9: Librarian - Store Content Metadata")
            
            metadata_result = await self.dil_sdk.store_content_metadata(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                content_metadata=content_metadata,
                user_context=user_context
            )
            
            content_id = metadata_result.get("content_id")
            self.logger.info(f"✅ Content metadata stored: {content_id}")
            
            # ========================================================================
            # STEP 10: Business Enablement → Create Embeddings
            # ========================================================================
            self.logger.info("🧠 Step 10: Business Enablement - Create Embeddings")
            
            # Create embeddings from parsed data
            # (In future, this will be a dedicated EmbeddingService)
            # For now, using existing StatelessHFInferenceAgent or similar
            embeddings = []  # Placeholder - would call embedding service here
            
            # ========================================================================
            # STEP 11: Librarian → Store Semantic Embeddings (via DIL SDK)
            # ========================================================================
            self.logger.info("📚 Step 11: Librarian - Store Semantic Embeddings")
            
            if embeddings:
                embeddings_result = await self.dil_sdk.store_semantic_embeddings(
                    content_id=content_id,
                    file_id=file_id,
                    embeddings=embeddings,
                    user_context=user_context
                )
                self.logger.info(f"✅ Embeddings stored: {len(embeddings)} embeddings")
            
            # ========================================================================
            # STEP 12: Data Steward → Track Additional Lineage
            # ========================================================================
            self.logger.info("📋 Step 12: Data Steward - Track Additional Lineage")
            
            await self.dil_sdk.track_lineage(
                lineage_data={
                    "source_id": parsed_file_id,
                    "target_id": content_id,
                    "operation": "metadata_extraction",
                    "operation_type": "content_metadata_extraction",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"workflow_id": workflow_id}
                },
                user_context=user_context
            )
            
            if embeddings:
                await self.dil_sdk.track_lineage(
                    lineage_data={
                        "source_id": content_id,
                        "target_id": f"embeddings_{content_id}",
                        "operation": "embedding_creation",
                        "operation_type": "semantic_embedding",
                        "timestamp": datetime.utcnow().isoformat(),
                        "metadata": {"workflow_id": workflow_id}
                    },
                    user_context=user_context
                )
            
            # ========================================================================
            # STEP 13: Post Office → Publish Events
            # ========================================================================
            self.logger.info("📮 Step 13: Post Office - Publish Events")
            
            if self.post_office:
                # Publish file processed event
                await self.post_office.publish_event(
                    event_type="file_processed",
                    event_data={
                        "file_id": file_id,
                        "parsed_file_id": parsed_file_id,
                        "content_id": content_id,
                        "workflow_id": workflow_id,
                        "status": "completed"
                    },
                    user_context=user_context
                )
                
                # Publish semantic data ready event
                if embeddings:
                    await self.post_office.publish_event(
                        event_type="semantic_data_ready",
                        event_data={
                            "content_id": content_id,
                            "file_id": file_id,
                            "embedding_count": len(embeddings)
                        },
                        user_context=user_context
                    )
            
            # ========================================================================
            # STEP 14: Conductor → Update Workflow Status
            # ========================================================================
            self.logger.info("🎼 Step 14: Conductor - Update Workflow Status")
            
            if self.conductor:
                await self.conductor.update_workflow_state(
                    workflow_id=workflow_id,
                    state_updates={
                        "status": "completed",
                        "file_id": file_id,
                        "parsed_file_id": parsed_file_id,
                        "content_id": content_id,
                        "completed_at": datetime.utcnow().isoformat()
                    },
                    user_context=user_context
                )
            
            # ========================================================================
            # STEP 15: Nurse → Record Complete Telemetry (via DIL SDK)
            # ========================================================================
            self.logger.info("🏥 Step 15: Nurse - Record Complete Telemetry")
            
            # Record trace
            await self.dil_sdk.record_platform_event(
                event_type="trace",
                event_data={
                    "span_name": "file_upload_complete_lifecycle",
                    "service_name": "ContentAnalysisOrchestrator",
                    "start_time": datetime.utcnow(),  # Would be actual start time
                    "duration_ms": 0.0,  # Would be actual duration
                    "status": "ok",
                    "metadata": {
                        "file_id": file_id,
                        "workflow_id": workflow_id,
                        "steps_completed": 15
                    }
                },
                trace_id=trace_id,
                user_context=user_context
            )
            
            # Record metric
            await self.dil_sdk.record_platform_event(
                event_type="metric",
                event_data={
                    "metric_name": "file_processing_complete",
                    "value": 1.0,
                    "service_name": "ContentAnalysisOrchestrator",
                    "metadata": {
                        "file_type": file_type,
                        "content_type": content_type
                    }
                },
                trace_id=trace_id,
                user_context=user_context
            )
            
            # ========================================================================
            # STEP 16: City Manager → Platform Orchestration & Governance
            # ========================================================================
            self.logger.info("🏛️ Step 16: City Manager - Platform Orchestration & Governance")
            
            if self.city_manager:
                # Report workflow completion to City Manager
                await self.city_manager.report_workflow_completion(
                    workflow_id=workflow_id,
                    workflow_type="file_processing",
                    result={
                        "file_id": file_id,
                        "parsed_file_id": parsed_file_id,
                        "content_id": content_id,
                        "status": "completed"
                    },
                    user_context=user_context
                )
                
                # City Manager ensures governance compliance
                governance_check = await self.city_manager.validate_governance_compliance(
                    resource_id=file_id,
                    resource_type="file",
                    user_context=user_context
                )
                
                if not governance_check.get("compliant"):
                    self.logger.warning(f"⚠️ Governance compliance issues: {governance_check.get('issues')}")
            
            # ========================================================================
            # RETURN RESULT
            # ========================================================================
            return {
                "success": True,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "content_id": content_id,
                "workflow_id": workflow_id,
                "trace_id": trace_id,
                "lineage_id": lineage_id,
                "status": "completed",
                "metadata": {
                    "format_type": format_type,
                    "content_type": content_type,
                    "has_embeddings": len(embeddings) > 0 if embeddings else False
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ File processing failed: {e}")
            
            # Record error via Nurse
            await self.dil_sdk.record_platform_event(
                event_type="log",
                event_data={
                    "level": "error",
                    "message": f"File processing failed: {str(e)}",
                    "service_name": "ContentAnalysisOrchestrator",
                    "metadata": {"file_name": file_name, "error": str(e)}
                },
                trace_id=trace_id,
                user_context=user_context
            )
            
            # Update workflow status
            if self.conductor and workflow_id:
                await self.conductor.update_workflow_state(
                    workflow_id=workflow_id,
                    state_updates={"status": "failed", "error": str(e)},
                    user_context=user_context
                )
            
            raise
```

---

## City Manager Role in Data Lifecycle

### Current Role

City Manager currently:
1. **Bootstraps Manager Hierarchy** - Ensures managers are initialized
2. **Orchestrates Realm Startup** - Ensures Smart City services start in correct order
3. **Platform Governance** - Validates governance compliance

### Recommended Enhanced Role

City Manager should also:

1. **Data Path Validation**
   - Ensure every data operation goes through Smart City services
   - Validate that DIL SDK is used (not direct service access)
   - Enforce canonical data plane pattern

2. **Data Lifecycle Orchestration**
   - Coordinate multi-step data operations across services
   - Ensure proper sequencing (e.g., upload → parse → metadata → embeddings)
   - Handle rollback/compensation if any step fails

3. **Governance Enforcement**
   - Validate data classification (client vs platform)
   - Ensure lineage tracking for all data operations
   - Enforce data policies and contracts

4. **Observability Aggregation**
   - Aggregate observability data from all services
   - Provide platform-wide data health dashboard
   - Track data quality metrics

### Manager Bootstrap Pattern for Data Paths

Similar to how City Manager bootstraps the manager hierarchy, we should implement a **Data Path Bootstrap Pattern**:

```python
class CityManagerService:
    async def bootstrap_data_paths(self):
        """
        Bootstrap data paths to ensure all data operations land in Smart City.
        
        This ensures:
        1. All Business Enablement orchestrators use DIL SDK
        2. All data operations go through Smart City services
        3. All data paths are tracked and observable
        """
        # Validate DIL SDK is initialized in all orchestrators
        orchestrators = await self.get_all_orchestrators()
        for orchestrator in orchestrators:
            if not hasattr(orchestrator, 'dil_sdk') or not orchestrator.dil_sdk:
                self.logger.warning(f"⚠️ Orchestrator {orchestrator.service_name} missing DIL SDK")
                # Initialize DIL SDK for orchestrator
                await self._initialize_dil_sdk_for_orchestrator(orchestrator)
        
        # Register data path validators
        await self._register_data_path_validators()
        
        # Ensure all Smart City services are ready for data operations
        await self._validate_smart_city_data_services()
```

---

## Key Benefits

1. **Unified Interface**: DIL SDK provides single interface for all data operations
2. **Complete Lifecycle**: Every step of data lifecycle is tracked and observable
3. **Governance**: All data operations go through governance (Data Steward)
4. **Observability**: All operations are observable (Nurse)
5. **Workflow Tracking**: All operations are tracked in workflows (Conductor)
6. **Event-Driven**: All operations publish events (Post Office)
7. **Session Management**: All operations are tied to sessions (Traffic Cop)
8. **Security**: All operations are authenticated/authorized (Security Guard)
9. **Platform Orchestration**: City Manager ensures everything is coordinated

---

## Next Steps

1. **Implement DIL SDK initialization** in all Business Enablement orchestrators
2. **Add City Manager data path bootstrap** to ensure all orchestrators use DIL SDK
3. **Add data path validators** to ensure all data operations go through Smart City
4. **Create governance policies** for data operations
5. **Add observability dashboards** for data lifecycle tracking


