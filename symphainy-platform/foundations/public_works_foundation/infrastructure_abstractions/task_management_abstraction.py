#!/usr/bin/env python3
"""
Task Management Abstraction

Infrastructure abstraction for task lifecycle management using Celery.
Implements TaskManagementProtocol using CeleryAdapter.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import asyncio
import logging

from ..abstraction_contracts.task_management_protocol import (
    TaskManagementProtocol, TaskRequest, TaskResult, TaskInfo, 
    TaskStatus, TaskPriority
)
from ..infrastructure_adapters.celery_adapter import CeleryAdapter

class TaskManagementAbstraction(TaskManagementProtocol):
    """Task management abstraction using Celery."""
    
    def __init__(self, celery_adapter: CeleryAdapter, di_container=None, **kwargs):
        """
        Initialize task management abstraction.
        
        Args:
            celery_adapter: Celery adapter instance
            di_container: DI Container for utilities
        """
        self.celery_adapter = celery_adapter
        self.di_container = di_container
        self.service_name = "task_management_abstraction"
        
        # Get logger from DI container if available, otherwise use module logger
        if self.di_container and hasattr(self.di_container, 'get_logger'):
            self.logger = self.di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("TaskManagementAbstraction")
        
        # Task registry
        self.task_handlers = {}
        self.task_history = []
        
        # Initialize task handlers
        self._initialize_task_handlers()
    
    def _initialize_task_handlers(self):
        """Initialize default task handlers."""
        try:
            # Register default task handlers
            self._register_default_handlers()
            self.logger.info("✅ Task management abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize task handlers: {e}")
            raise  # Re-raise for service layer to handle
    
    def _register_default_handlers(self):
        """Register default task handlers."""
        # Default handlers can be registered here if needed
        # For now, this is a placeholder
        pass
        # This would register common task handlers
        pass
    
    async def create_task(self, request: TaskRequest) -> str:
        """
        Create a new task.
        
        Args:
            request: Task creation request
            
        Returns:
            str: Task ID
        """
        try:
            # Register task handler if not already registered
            if request.task_name not in self.task_handlers:
                self.logger.warning(f"Task handler not found for {request.task_name}")
                raise ValueError(f"Task handler not found for {request.task_name}")
            
            # Execute task using Celery adapter
            task_id = self.celery_adapter.execute_task(
                task_name=request.task_name,
                args=request.args or [],
                kwargs=request.kwargs or {},
                queue=request.queue,
                priority=request.priority.value,
                eta=request.eta,
                countdown=request.countdown
            )
            
            # Create task info - build kwargs, only include metadata if provided
            kwargs = {
                "task_id": task_id,
                "task_name": request.task_name,
                "status": TaskStatus.PENDING,
                "queue": request.queue,
                "priority": request.priority
            }
            if request.metadata:
                kwargs["metadata"] = request.metadata
            task_info = TaskInfo(**kwargs)
            
            # Add to history
            self.task_history.append(task_info)
            
            self.logger.info(f"✅ Task {request.task_name} created with ID: {task_id}")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create task {request.task_name}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Execute a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskResult: Task execution result
        """
        try:
            # Get task result from Celery
            result_data = self.celery_adapter.get_task_result(task_id)
            
            # Convert to TaskResult
            status = self._convert_celery_status(result_data.get("status", "PENDING"))
            
            # Build kwargs - only include optional fields if they have values
            kwargs = {
                "task_id": task_id,
                "status": status,
                "result": result_data.get("result"),
                "error": result_data.get("traceback"),
                "started_at": datetime.now(),  # Would get from Celery in real implementation
                "completed_at": datetime.now() if status in [TaskStatus.COMPLETED, TaskStatus.FAILED] else None,
                "retry_count": 0  # Would get from Celery in real implementation
            }
            # metadata has default factory, so don't pass empty dict
            task_result = TaskResult(**kwargs)
            
            
            return task_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute task {task_id}: {e}")
            raise  # Re-raise for service layer to handle

        """Convert Celery status to TaskStatus."""
        status_mapping = {
            "PENDING": TaskStatus.PENDING,
            "STARTED": TaskStatus.RUNNING,
            "SUCCESS": TaskStatus.COMPLETED,
            "FAILURE": TaskStatus.FAILED,
            "RETRY": TaskStatus.RETRYING,
            "REVOKED": TaskStatus.CANCELLED
        }
        return status_mapping.get(celery_status, TaskStatus.PENDING)
    
    async def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Get task status.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskStatus: Current task status
        """
        try:
            result_data = self.celery_adapter.get_task_result(task_id)
            status = self._convert_celery_status(result_data.get("status", "PENDING"))
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get task status {task_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get task result.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskResult: Task result
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        try:
            result_data = self.celery_adapter.get_task_result(task_id)
            status = self._convert_celery_status(result_data.get("status", "PENDING"))
            
            # Build kwargs - metadata has default factory, so don't pass empty dict
            kwargs = {
                "task_id": task_id,
                "status": status,
                "result": result_data.get("result"),
                "error": result_data.get("traceback"),
                "started_at": datetime.now(),
                "completed_at": datetime.now() if status in [TaskStatus.COMPLETED, TaskStatus.FAILED] else None,
                "retry_count": 0
            }
            task_result = TaskResult(**kwargs)
            
            
            return task_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get task result {task_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Cancel a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: Success status
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        try:
            success = self.celery_adapter.revoke_task(task_id, terminate=True)
            
            if success:
                self.logger.info(f"✅ Task {task_id} cancelled")
            else:
                self.logger.warning(f"Failed to cancel task {task_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Retry a failed task.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: Success status
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        try:
            # Get task info from history
            task_info = next((t for t in self.task_history if t.task_id == task_id), None)
            if not task_info:
                self.logger.error(f"Task {task_id} not found in history")
                return False
            
            # Create new task with same parameters
            request = TaskRequest(
                task_name=task_info.task_name,
                queue=task_info.queue,
                priority=task_info.priority,
                args=[],
                kwargs={}
            )
            
            new_task_id = await self.create_task(request)
            success = new_task_id is not None
            
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to retry task {task_id}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get list of active tasks.
        
        Returns:
            List[TaskInfo]: Active tasks
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        try:
            # Get active tasks from Celery
            active_tasks = self.celery_adapter.get_active_tasks()
            
            task_infos = []
            for task_data in active_tasks:
                # Build kwargs - only include metadata if provided (default factory handles None)
                kwargs = {
                    "task_id": task_data.get("task_id", ""),
                    "task_name": task_data.get("name", ""),
                    "status": TaskStatus.RUNNING,
                    "queue": "default",
                    "priority": TaskPriority.NORMAL,
                    "started_at": datetime.now()
                }
                # created_at and metadata have default factories, so don't pass them
                task_info = TaskInfo(**kwargs)
                task_infos.append(task_info)
            
            
            return task_infos
            
        except Exception as e:
            self.logger.error(f"Failed to get active tasks: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get task history.
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List[TaskInfo]: Task history
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        try:
            # Return recent tasks from history
            recent_tasks = self.task_history[-limit:] if len(self.task_history) > limit else self.task_history
            
            
            return recent_tasks
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get task history: {e}")
            raise  # Re-raise for service layer to handle

        """
        Register a task handler.
        
        Args:
            task_name: Name of the task
            handler: Task handler function
            
        Returns:
            bool: Success status
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        try:
            # Register with Celery adapter
            success = self.celery_adapter.register_task(task_name, handler)
            
            if success:
                self.task_handlers[task_name] = handler
                self.logger.info(f"✅ Task handler registered for {task_name}")
            else:
                self.logger.error(f"Failed to register task handler for {task_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to register task handler {task_name}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Get queue status.
        
        Args:
            queue: Queue name
            
        Returns:
            Dict: Queue status information
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        try:
            # Get queue length
            queue_length = self.celery_adapter.get_queue_length(queue)
            
            # Get worker stats
            worker_stats = self.celery_adapter.get_worker_stats()
            
            status = {
                "queue": queue,
                "length": queue_length,
                "workers": len(worker_stats),
                "worker_stats": worker_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get queue status for {queue}: {e}")
            raise  # Re-raise for service layer to handle

        """
        Purge a queue.
        
        Args:
            queue: Queue name
            
        Returns:
            bool: Success status
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        try:
            success = self.celery_adapter.purge_queue(queue)
            
            if success:
                self.logger.info(f"✅ Queue {queue} purged")
            else:
                self.logger.warning(f"Failed to purge queue {queue}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to purge queue {queue}: {e}")
            raise  # Re-raise for service layer to handle
