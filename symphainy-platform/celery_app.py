#!/usr/bin/env python3
"""
Celery App Module for SymphAIny Platform
Separate module to avoid conflicts with FastAPI app in main.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from celery import Celery

# Get Celery configuration from environment
celery_broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
celery_result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# Create Celery app instance
celery = Celery(
    'symphainy',
    broker=celery_broker_url,
    backend=celery_result_backend
)

# Configure Celery (matching CeleryAdapter configuration)
celery.conf.update(
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

# Import tasks from CeleryAdapter if available
try:
    from foundations.public_works_foundation.infrastructure_adapters.celery_adapter import CeleryAdapter
    # Tasks will be registered via CeleryAdapter
except ImportError:
    pass

if __name__ == '__main__':
    celery.start()

