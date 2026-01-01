#!/usr/bin/env python3
"""
Initialization Module - Conductor Service

Initializes infrastructure connections using mixin methods.
Proper abstractions: Task Management (Celery) and Workflow Orchestration (Redis Graph).
"""

from typing import Dict, Any


class Initialization:
    """Initialization module for Conductor Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def initialize_infrastructure(self):
        """Initialize infrastructure connections using mixin methods."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "initialize_infrastructure_start",
            success=True
        )
        
        try:
            # Use mixin methods - NOT direct foundation access!
            # Task Management Abstraction (Celery)
            self.service.task_management_abstraction = self.service.get_task_management_abstraction()
            if not self.service.task_management_abstraction:
                raise Exception("Task Management Abstraction (Celery) not available")
            
            # Workflow Orchestration Abstraction (Redis Graph)
            self.service.workflow_orchestration_abstraction = self.service.get_workflow_orchestration_abstraction()
            if not self.service.workflow_orchestration_abstraction:
                raise Exception("Workflow Orchestration Abstraction (Redis Graph) not available")
            
            self.service.is_infrastructure_connected = True
            
            # Record health metric
            await self.service.record_health_metric(
                "infrastructure_connected",
                1.0,
                {
                    "task_management": "connected",
                    "workflow_orchestration": "connected"
                }
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_complete",
                success=True,
                details={
                    "task_management": "connected",
                    "workflow_orchestration": "connected"
                }
            )
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "initialize_infrastructure")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "initialize_infrastructure_complete",
                success=False,
                details={"error": str(e)}
            )
            raise
