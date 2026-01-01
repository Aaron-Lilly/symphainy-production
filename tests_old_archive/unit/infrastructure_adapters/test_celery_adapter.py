#!/usr/bin/env python3
"""
CeleryAdapter Tests

Tests for CeleryAdapter in isolation.
Verifies adapter works correctly before anything uses it.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = [pytest.mark.unit, pytest.mark.fast, pytest.mark.infrastructure]

class TestCeleryAdapter:
    """Test CeleryAdapter functionality."""
    
    @pytest.fixture
    def mock_celery_app(self):
        """Mock Celery app."""
        mock_app = MagicMock()
        mock_app.conf = MagicMock()
        mock_app.conf.update = MagicMock()
        mock_app.task = MagicMock(return_value=MagicMock())
        return mock_app
    
    @pytest.fixture
    def adapter(self, mock_celery_app):
        """Create CeleryAdapter instance."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.celery_adapter.Celery', return_value=mock_celery_app):
            from foundations.public_works_foundation.infrastructure_adapters.celery_adapter import CeleryAdapter
            adapter = CeleryAdapter(
                broker_url="redis://localhost:6379/0",
                result_backend="redis://localhost:6379/0"
            )
            adapter.celery_app = mock_celery_app
            return adapter
    
    @pytest.mark.asyncio
    async def test_adapter_initializes(self, mock_celery_app):
        """Test adapter initializes correctly."""
        with patch('foundations.public_works_foundation.infrastructure_adapters.celery_adapter.Celery', return_value=mock_celery_app):
            from foundations.public_works_foundation.infrastructure_adapters.celery_adapter import CeleryAdapter
            adapter = CeleryAdapter(
                broker_url="redis://localhost:6379/0",
                result_backend="redis://localhost:6379/0"
            )
            assert adapter.broker_url == "redis://localhost:6379/0"
            assert adapter.result_backend == "redis://localhost:6379/0"
            assert adapter.celery_app is not None
    
    @pytest.mark.asyncio
    async def test_register_task(self, adapter, mock_celery_app):
        """Test adapter can register a task."""
        def test_task():
            return "result"
        
        result = adapter.register_task("test_task", test_task)
        assert result is True
        assert "test_task" in adapter.registered_tasks
    
    @pytest.mark.asyncio
    async def test_execute_task(self, adapter, mock_celery_app):
        """Test adapter can execute a task."""
        mock_result = MagicMock()
        mock_result.id = "task_123"
        mock_result.get = MagicMock(return_value="result")
        mock_celery_app.send_task = MagicMock(return_value=mock_result)
        
        result = await adapter.execute_task("test_task", {"arg": "value"})
        assert result is not None
        mock_celery_app.send_task.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_task_result(self, adapter, mock_celery_app):
        """Test adapter can get task status."""
        mock_result = MagicMock()
        mock_result.state = "SUCCESS"
        mock_result.ready = MagicMock(return_value=True)
        with patch('foundations.public_works_foundation.infrastructure_adapters.celery_adapter.AsyncResult', return_value=mock_result):
            result = await adapter.get_task_result("task_123")
            assert result is not None
            assert result["state"] == "SUCCESS"

