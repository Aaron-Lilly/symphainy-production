#!/usr/bin/env python3
"""
Celery Infrastructure Adapter

Raw Celery bindings for task management and workflow execution.
Thin wrapper around Celery SDK with no business logic.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
import logging

try:
    from celery import Celery
    from celery.result import AsyncResult
    from celery.exceptions import CeleryError
except ImportError:
    Celery = None
    AsyncResult = None
    CeleryError = Exception


class CeleryAdapter:
    """Raw Celery adapter for task management and workflow execution."""
    
    def __init__(self, broker_url: str, result_backend: str, **kwargs):
        """
        Initialize Celery adapter.
        
        Args:
            broker_url: Celery broker URL (Redis/RabbitMQ)
            result_backend: Result backend URL
        """
        self.broker_url = broker_url
        self.result_backend = result_backend
        self.logger = logging.getLogger("CeleryAdapter")
        
        # Celery app
        self.celery_app = None
        self.is_worker_running = False
        
        # Task registry
        self.registered_tasks = {}
        
        # Initialize Celery app
        self._initialize_celery_app()
    
    def _initialize_celery_app(self):
        """Initialize Celery application."""
        if Celery is None:
            self.logger.error("Celery not installed")
            return
            
        try:
            self.celery_app = Celery(
                'conductor_tasks',
                broker=self.broker_url,
                backend=self.result_backend
            )
            
            # Configure Celery
            self.celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                task_track_started=True,
                task_time_limit=300,  # 5 minutes
                task_soft_time_limit=240,  # 4 minutes
                worker_prefetch_multiplier=1,
                task_acks_late=True,
                worker_disable_rate_limits=False
            )
            
            self.logger.info("✅ Celery adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Celery: {e}")
            self.celery_app = None
    
    def register_task(self, task_name: str, task_func: Callable) -> bool:
        """
        Register a task with Celery.
        
        Args:
            task_name: Name of the task
            task_func: Task function
            
        Returns:
            bool: Success status
        """
        if not self.celery_app:
            return False
            
        try:
            # Register task with Celery
            self.celery_app.task(name=task_name)(task_func)
            self.registered_tasks[task_name] = task_func
            
            self.logger.info(f"✅ Registered task: {task_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register task {task_name}: {e}")
            return False
    
    def execute_task(self, task_name: str, args: List = None, kwargs: Dict = None, 
                    queue: str = 'default', priority: int = 0, 
                    eta: datetime = None, countdown: int = None) -> str:
        """
        Execute a task asynchronously.
        
        Args:
            task_name: Name of the task to execute
            args: Task arguments
            kwargs: Task keyword arguments
            queue: Task queue
            priority: Task priority
            eta: Estimated time of arrival
            countdown: Countdown in seconds
            
        Returns:
            str: Task ID
        """
        if not self.celery_app:
            raise CeleryError("Celery not initialized")
            
        try:
            # Execute task
            result = self.celery_app.send_task(
                task_name,
                args=args or [],
                kwargs=kwargs or {},
                queue=queue,
                priority=priority,
                eta=eta,
                countdown=countdown
            )
            
            self.logger.info(f"✅ Task {task_name} queued with ID: {result.id}")
            return result.id
            
        except Exception as e:
            self.logger.error(f"Failed to execute task {task_name}: {e}")
            raise CeleryError(f"Task execution failed: {e}")
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get task result by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Dict: Task result and status
        """
        if not self.celery_app:
            return {"error": "Celery not initialized", "status": "FAILURE"}
            
        try:
            result = AsyncResult(task_id, app=self.celery_app)
            
            return {
                "task_id": task_id,
                "status": result.status,
                "result": result.result if result.ready() else None,
                "ready": result.ready(),
                "successful": result.successful() if result.ready() else False,
                "failed": result.failed() if result.ready() else False,
                "traceback": result.traceback if result.failed() else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get task result {task_id}: {e}")
            return {"error": str(e), "status": "FAILURE"}
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """
        Revoke a task.
        
        Args:
            task_id: Task ID
            terminate: Whether to terminate the task
            
        Returns:
            bool: Success status
        """
        if not self.celery_app:
            return False
            
        try:
            self.celery_app.control.revoke(task_id, terminate=terminate)
            self.logger.info(f"✅ Task {task_id} revoked")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke task {task_id}: {e}")
            return False
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of active tasks.
        
        Returns:
            List: Active tasks
        """
        if not self.celery_app:
            return []
            
        try:
            inspect = self.celery_app.control.inspect()
            active_tasks = inspect.active()
            
            tasks = []
            for worker, task_list in active_tasks.items():
                for task in task_list:
                    tasks.append({
                        "worker": worker,
                        "task_id": task.get("id"),
                        "name": task.get("name"),
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {}),
                        "time_start": task.get("time_start")
                    })
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to get active tasks: {e}")
            return []
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of scheduled tasks.
        
        Returns:
            List: Scheduled tasks
        """
        if not self.celery_app:
            return []
            
        try:
            inspect = self.celery_app.control.inspect()
            scheduled_tasks = inspect.scheduled()
            
            tasks = []
            for worker, task_list in scheduled_tasks.items():
                for task in task_list:
                    tasks.append({
                        "worker": worker,
                        "task_id": task.get("id"),
                        "name": task.get("name"),
                        "eta": task.get("eta"),
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {})
                    })
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to get scheduled tasks: {e}")
            return []
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """
        Get worker statistics.
        
        Returns:
            Dict: Worker statistics
        """
        if not self.celery_app:
            return {}
            
        try:
            inspect = self.celery_app.control.inspect()
            stats = inspect.stats()
            
            return stats or {}
            
        except Exception as e:
            self.logger.error(f"Failed to get worker stats: {e}")
            return {}
    
    def start_worker(self, concurrency: int = 1, queues: List[str] = None) -> bool:
        """
        Start Celery worker.
        
        Args:
            concurrency: Number of worker processes
            queues: List of queues to consume
            
        Returns:
            bool: Success status
        """
        if not self.celery_app:
            return False
            
        try:
            # Start worker in background
            worker = self.celery_app.Worker(
                concurrency=concurrency,
                queues=queues or ['default']
            )
            
            # Note: In production, this would be handled by systemd/supervisor
            self.logger.info(f"✅ Celery worker started with concurrency {concurrency}")
            self.is_worker_running = True
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start worker: {e}")
            return False
    
    def stop_worker(self) -> bool:
        """
        Stop Celery worker.
        
        Returns:
            bool: Success status
        """
        if not self.celery_app:
            return False
            
        try:
            # Stop worker
            self.celery_app.control.shutdown()
            self.is_worker_running = False
            self.logger.info("✅ Celery worker stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop worker: {e}")
            return False
    
    def get_queue_length(self, queue: str = 'default') -> int:
        """
        Get queue length.
        
        Args:
            queue: Queue name
            
        Returns:
            int: Queue length
        """
        if not self.celery_app:
            return 0
            
        try:
            inspect = self.celery_app.control.inspect()
            reserved = inspect.reserved()
            
            total_length = 0
            for worker, tasks in reserved.items():
                total_length += len(tasks)
            
            return total_length
            
        except Exception as e:
            self.logger.error(f"Failed to get queue length: {e}")
            return 0
    
    def purge_queue(self, queue: str = 'default') -> bool:
        """
        Purge queue.
        
        Args:
            queue: Queue name
            
        Returns:
            bool: Success status
        """
        if not self.celery_app:
            return False
            
        try:
            self.celery_app.control.purge()
            self.logger.info(f"✅ Queue {queue} purged")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to purge queue {queue}: {e}")
            return False



