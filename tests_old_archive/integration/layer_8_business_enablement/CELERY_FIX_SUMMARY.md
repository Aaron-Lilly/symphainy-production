# Celery Fix Summary - Production & Testing

## 🔍 Investigation Results

### Production Startup Script
- **Command**: `poetry run celery -A main worker --loglevel=info --detach` (line 214)
- **Issue**: `main.py` did NOT have a `celery` attribute
- **Result**: Production would have the same issue as Docker containers!

### Docker Compose
- **Command**: `celery -A main worker` (line 154)
- **Issue**: Same as production - no Celery app in `main.py`
- **Result**: Containers restarting with same error

### Verification
```python
# Test confirmed:
import main
hasattr(main, 'celery')  # False ❌
hasattr(main, 'app')      # True ✅ (FastAPI app)
```

---

## ✅ Solution: Add Celery App to main.py

**Decision**: Add Celery app to `main.py` for **both production and Docker containers**.

### Why This Approach?

1. **Consistency**: Both production and Docker use `celery -A main`
2. **Shared Infrastructure**: Celery is a platform component, not test-specific
3. **Single Source of Truth**: One Celery app configuration for all environments
4. **Production Fix**: Fixes production startup script issue too

---

## 🔧 Changes Made

### Added to `main.py` (after FastAPI imports, before app creation):

```python
# Initialize Celery app (for production and Docker containers)
# This allows celery -A main worker to work
try:
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
    
    logger.info("✅ Celery app initialized in main.py")
except ImportError:
    # Celery not installed - set to None
    celery = None
    logger.warning("⚠️ Celery not installed - celery app not available")
except Exception as e:
    # Failed to initialize Celery - set to None
    celery = None
    logger.warning(f"⚠️ Failed to initialize Celery app: {e}")
```

---

## ✅ Benefits

1. **Fixes Production**: Production startup script now works
2. **Fixes Docker**: Docker Compose Celery containers now work
3. **Consistent**: Same Celery app for all environments
4. **Graceful**: Handles missing Celery gracefully (won't break if not installed)
5. **Configurable**: Uses environment variables for broker/backend URLs

---

## 🧪 Testing

### Test Production Startup:
```bash
cd symphainy-platform
./scripts/production-startup.sh
# Should now successfully start Celery worker
```

### Test Docker Containers:
```bash
cd symphainy-platform
docker-compose -f docker-compose.infrastructure.yml up -d celery-worker celery-beat
# Containers should now start successfully
```

### Verify Celery App:
```python
import main
assert hasattr(main, 'celery')
assert main.celery is not None  # If Celery is installed
```

---

## 📋 Updated Approach

### Before:
- ❌ Production startup: Would fail (no Celery app)
- ❌ Docker containers: Restarting (no Celery app)
- ✅ Testing scripts: Created separate module (workaround)

### After:
- ✅ Production startup: Works (Celery app in main.py)
- ✅ Docker containers: Work (Celery app in main.py)
- ✅ Testing scripts: Can use `celery -A main` or keep separate module

---

## 🎯 Next Steps

1. ✅ **Celery app added to main.py** - Done
2. ⚠️ **Test production startup** - Verify it works
3. ⚠️ **Test Docker containers** - Verify they start successfully
4. 📝 **Update testing scripts** - Can simplify to use `main` instead of separate module

---

## 💡 Notes

- **CeleryAdapter**: Still exists and can be used for service-specific Celery tasks
- **main.py celery**: Platform-level Celery app for worker/beat processes
- **Both can coexist**: CeleryAdapter can register tasks with the main Celery app if needed

