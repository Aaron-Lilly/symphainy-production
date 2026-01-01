#!/usr/bin/env python3
"""
TaskManagementAbstraction Tests

Tests for TaskManagementAbstraction in isolation.
Verifies abstraction works correctly and realms can access it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestTaskManagementAbstraction:
    """Test TaskManagementAbstraction functionality."""
    
    @pytest.fixture
    def mock_celery_adapter(self):
        """Mock Celery adapter."""
        adapter = MagicMock()
        adapter.execute_task = AsyncMock(return_value="task_123")
        adapter.get_task_status = AsyncMock(return_value={"state": "SUCCESS"})
        adapter.get_task_result = AsyncMock(return_value={"state": "SUCCESS", "result": "completed"})
        adapter.register_task = MagicMock(return_value=True)
        return adapter
    
    @pytest.fixture
    def abstraction(self, mock_celery_adapter):
        """Create TaskManagementAbstraction instance."""
        from foundations.public_works_foundation.infrastructure_abstractions.task_management_abstraction import TaskManagementAbstraction
        from foundations.public_works_foundation.abstraction_contracts.task_management_protocol import TaskStatus
        
        abstraction = TaskManagementAbstraction(
            celery_adapter=mock_celery_adapter
        )
        return abstraction
    
    @pytest.mark.asyncio
    async def test_abstraction_initializes(self, mock_celery_adapter):
        """Test abstraction initializes correctly."""
        from foundations.public_works_foundation.infrastructure_abstractions.task_management_abstraction import TaskManagementAbstraction
        from foundations.public_works_foundation.abstraction_contracts.task_management_protocol import TaskStatus
        
        abstraction = TaskManagementAbstraction(
            celery_adapter=mock_celery_adapter
        )
        assert abstraction.celery_adapter == mock_celery_adapter
    
    @pytest.mark.asyncio
    async def test_create_task(self, abstraction, mock_celery_adapter):
        """Test abstraction can create a task."""
        from foundations.public_works_foundation.abstraction_contracts.task_management_protocol import TaskRequest, TaskPriority
        
        # Register a task handler first
        abstraction.task_handlers["test_task"] = lambda: "result"
        
        request = TaskRequest(
            task_name="test_task",
            args=[],
            kwargs={},
            queue="default",
            priority=TaskPriority.NORMAL
        )
        
        task_id = await abstraction.create_task(request)
        assert task_id is not None
        mock_celery_adapter.execute_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, abstraction, mock_celery_adapter):
        """Test abstraction can get task status."""
        result = await abstraction.get_task_status("task_123")
        assert result is not None
        assert result.value if hasattr(result, "value") else (result.get("state") if isinstance(result, dict) else str(result)) == "SUCCESS"
        mock_celery_adapter.get_task_result.assert_called_once_with("task_123")

