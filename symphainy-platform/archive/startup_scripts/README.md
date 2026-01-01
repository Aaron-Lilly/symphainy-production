# Startup Scripts Archive

This directory contains archived startup scripts that have been consolidated into the canonical `startup.sh` at the project root.

## Consolidation Date
2025-01-XX

## Rationale

After analysis, we determined that having multiple startup scripts caused:
- Confusion about which script to use
- Maintenance overhead
- Inconsistent behavior
- Missing best practices in some versions

## Consolidated Script

**Canonical Script:** `../startup.sh`

This script combines the best features from all versions:
- ✅ Poetry dependency management
- ✅ Infrastructure orchestration (Docker)
- ✅ Proper startup sequence (infrastructure → FastAPI LAST)
- ✅ Port binding wait (handles FastAPI startup lag)
- ✅ Health checks
- ✅ Background/foreground modes
- ✅ Comprehensive validation

## Archived Scripts

### `start_backend.sh`
- **Date:** Created 2025-01-XX
- **Purpose:** Simple backend startup with PYTHONPATH
- **Why Archived:** Missing Poetry, no infrastructure, no validation
- **Replaced By:** `startup.sh` (foreground mode)

### `start_backend_proper.sh`
- **Date:** Created 2025-01-XX
- **Purpose:** Proper backend startup with Poetry and infrastructure
- **Why Archived:** Consolidated into canonical `startup.sh`
- **Replaced By:** `startup.sh` (background mode)

### Scripts in `scripts/` directory
- `production-startup.sh` - Production-focused version
- `proper-startup.sh` - Infrastructure-focused version
- `working-startup.sh` - Working version
- `enhanced-startup.sh` - Enhanced version

**Why Archived:** Multiple experimental versions, consolidated into one canonical script

## Usage

### Development (Foreground)
```bash
./startup.sh
```

### Production (Background)
```bash
./startup.sh --background
```

### Minimal Mode (Infrastructure Already Running)
```bash
./startup.sh --minimal
```

## Migration Notes

If you were using any of the archived scripts:

1. **`start_backend.sh`** → Use `./startup.sh` (foreground mode)
2. **`start_backend_proper.sh`** → Use `./startup.sh --background`
3. **Scripts in `scripts/`** → Use `./startup.sh` with appropriate flags

## Key Improvements in Consolidated Script

1. **Poetry Integration:** Always uses `poetry run` for proper dependency management
2. **Startup Sequence:** Infrastructure → FastAPI LAST (from archives)
3. **Port Binding Wait:** Handles FastAPI startup lag (5-30 seconds)
4. **Health Checks:** Verifies infrastructure and backend readiness
5. **Flexible Modes:** Foreground (dev) and background (prod) options
6. **Comprehensive Validation:** Checks Poetry, Python, directory structure




