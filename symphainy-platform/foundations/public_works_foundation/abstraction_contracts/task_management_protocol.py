#!/usr/bin/env python3
"""
Task Management Protocol

Abstraction contract for task lifecycle management.
Defines interfaces for task creation, execution, and monitoring.
"""

from typing import Protocol, Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskRequest:
    """Task creation request."""
    task_name: str
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    queue: str = "default"
    priority: TaskPriority = TaskPriority.NORMAL
    eta: Optional[datetime] = None
    countdown: Optional[int] = None
    retries: int = 3
    timeout: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Task execution result."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskInfo:
    """Task information."""
    task_id: str
    task_name: str
    status: TaskStatus
    queue: str
    priority: TaskPriority
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskManagementProtocol(Protocol):
    """Protocol for task management operations."""
    
    async def create_task(self, request: TaskRequest) -> str:
        """
        Create a new task.
        
        Args:
            request: Task creation request
            
        Returns:
            str: Task ID
        """
        ...
    
    async def execute_task(self, task_id: str) -> TaskResult:
        """
        Execute a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskResult: Task execution result
        """
        ...
    
    async def get_task_status(self, task_id: str) -> TaskStatus:
        """
        Get task status.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskStatus: Current task status
        """
        ...
    
    async def get_task_result(self, task_id: str) -> TaskResult:
        """
        Get task result.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskResult: Task result
        """
        ...
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: Success status
        """
        ...
    
    async def retry_task(self, task_id: str) -> bool:
        """
        Retry a failed task.
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_active_tasks(self) -> List[TaskInfo]:
        """
        Get list of active tasks.
        
        Returns:
            List[TaskInfo]: Active tasks
        """
        ...
    
    async def get_task_history(self, limit: int = 100) -> List[TaskInfo]:
        """
        Get task history.
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List[TaskInfo]: Task history
        """
        ...
    
    async def register_task_handler(self, task_name: str, handler: Callable) -> bool:
        """
        Register a task handler.
        
        Args:
            task_name: Name of the task
            handler: Task handler function
            
        Returns:
            bool: Success status
        """
        ...
    
    async def get_queue_status(self, queue: str = "default") -> Dict[str, Any]:
        """
        Get queue status.
        
        Args:
            queue: Queue name
            
        Returns:
            Dict: Queue status information
        """
        ...
    
    async def purge_queue(self, queue: str = "default") -> bool:
        """
        Purge a queue.
        
        Args:
            queue: Queue name
            
        Returns:
            bool: Success status
        """
        ...



