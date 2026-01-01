# Disk Space Cleanup Strategy

**Date:** 2025-01-29  
**Current Status:** 94% disk usage (68G / 73G used)  
**Goal:** Free up space to run tests (need < 90% for test safety checks)

---

## 📊 Current Disk Usage Analysis

### **Largest Directories:**
1. **symphainy_source**: 2.8G (active code - keep)
2. **symphainy-mvp-aaron-legacy**: 2.4G (legacy - can remove)
3. **archive**: 950M (archive - review)
4. **symphainy-legacy**: 795M (legacy - can remove)
5. **symphainy-mvp-backend-final-legacy**: 402M (legacy - can remove)

### **Other Space Consumers:**
- **Docker images**: 7.3GB (2.1GB reclaimable)
- **node_modules**: 626MB (can reinstall)
- **Python cache**: Small (safe to remove)
- **Test artifacts**: Small (safe to remove)

---

## 🎯 Cleanup Strategy (Safe → Aggressive)

### **Phase 1: Safe Cleanups (Always Safe)**
**Estimated Space Saved:** ~100-200MB

These are always safe to remove and can be regenerated:

```bash
# Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Pytest cache
find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Coverage files
find . -type d -name "htmlcov" -exec rm -rf {} +
find . -type f -name ".coverage*" -delete

# Python build artifacts
find . -type d -name "*.egg-info" -exec rm -rf {} +
find . -type d -name "dist" -exec rm -rf {} +

# Old log files (keep last 7 days)
find . -type f -name "*.log" -mtime +7 -delete
```

**Impact:** ✅ Safe, no risk  
**Time:** 1 minute

---

### **Phase 2: Docker Cleanup**
**Estimated Space Saved:** 2-3GB

```bash
# Remove unused Docker images and containers
docker system prune -f

# More aggressive (removes all unused images and volumes)
docker system prune -af --volumes
```

**Impact:** ✅ Safe, removes unused Docker resources  
**Time:** 2-3 minutes

---

### **Phase 3: Node Modules (Optional)**
**Estimated Space Saved:** 626MB

```bash
# Remove node_modules (you'll need to reinstall)
rm -rf symphainy_source/symphainy-frontend/node_modules

# Reinstall later:
cd symphainy_source/symphainy-frontend && npm install
```

**Impact:** ⚠️ Requires reinstall (5-10 minutes)  
**Time:** 1 minute to remove, 5-10 minutes to reinstall

---

### **Phase 4: Legacy Directories (Review Carefully)**
**Estimated Space Saved:** 4-5GB

These are legacy/archive directories. Review before removing:

```bash
# Legacy directories (review each one):
symphainy-mvp-aaron-legacy        # 2.4G - Legacy MVP
archive                            # 950M - Archive
symphainy-legacy                   # 795M - Legacy Symphainy
symphainy-mvp-backend-final-legacy # 402M - Legacy Backend
symphainy-platformMVP              # 19M - Legacy Platform
symphainy-mvp-clean                # 14M - Legacy Clean
symphainy-mvp-final                # 12M - Legacy Final
```

**Impact:** ⚠️ Permanent deletion - review first  
**Time:** 5-10 minutes

---

## 🚀 Quick Start: Automated Cleanup Script

I've created an automated cleanup script that handles all of this safely:

```bash
# Dry run first (see what would be removed)
cd /home/founders/demoversion/symphainy_source/tests/scripts
./cleanup_disk_space.sh --dry-run

# Run safe cleanups only (no confirmations needed)
./cleanup_disk_space.sh

# Aggressive mode (removes everything, skips confirmations)
./cleanup_disk_space.sh --aggressive
```

---

## 📋 Recommended Cleanup Order

### **Option A: Quick Win (5 minutes)**
1. Run Phase 1 (Safe cleanups) → ~200MB
2. Run Phase 2 (Docker cleanup) → ~2GB
3. **Total:** ~2.2GB freed, should get you below 90%

### **Option B: Maximum Cleanup (15 minutes)**
1. Run Phase 1 (Safe cleanups) → ~200MB
2. Run Phase 2 (Docker cleanup) → ~2GB
3. Run Phase 3 (node_modules) → ~626MB
4. Review and remove legacy directories → ~4-5GB
5. **Total:** ~7GB freed

---

## ⚠️ Safety Guidelines

### **Always Safe to Remove:**
- ✅ `__pycache__` directories
- ✅ `.pytest_cache` directories
- ✅ `.coverage` files
- ✅ `*.egg-info` directories
- ✅ Old log files (>7 days)
- ✅ Unused Docker images

### **Review Before Removing:**
- ⚠️ Legacy directories (check if you need them)
- ⚠️ Archive directories (check if you need them)
- ⚠️ `node_modules` (you'll need to reinstall)

### **Never Remove:**
- ❌ Active code directories (`symphainy_source`)
- ❌ `.git` directories
- ❌ Configuration files
- ❌ Recent log files (<7 days)

---

## 🎯 Target: Get Below 90% Disk Usage

**Current:** 94% (68G / 73G)  
**Target:** <90% (65.7G / 73G)  
**Need to Free:** ~2.3GB

**Quick Win Strategy:**
1. Safe cleanups: ~200MB
2. Docker cleanup: ~2GB
3. **Total:** ~2.2GB → Should get you to ~91%

**If Still Above 90%:**
4. Remove node_modules: +626MB → Should get you to ~90%
5. Remove one legacy directory: +400MB-2.4GB → Should get you well below 90%

---

## 📝 Post-Cleanup Checklist

After cleanup:
- [ ] Verify tests can run: `pytest tests/e2e/production/test_api_smoke.py::TestAPISmoke::test_health_endpoint -v`
- [ ] If removed node_modules, reinstall: `cd symphainy_source/symphainy-frontend && npm install`
- [ ] Verify Docker containers still work: `docker ps`
- [ ] Check disk space: `df -h`

---

## 💡 Maintenance Tips

To prevent this in the future:

1. **Regular Cleanup:**
   ```bash
   # Run weekly
   ./cleanup_disk_space.sh
   ```

2. **Monitor Disk Usage:**
   ```bash
   # Check disk usage
   df -h
   
   # Find large directories
   du -sh * | sort -hr | head -10
   ```

3. **Git Clean:**
   ```bash
   # Remove untracked files
   git clean -fd
   ```

4. **Docker Maintenance:**
   ```bash
   # Weekly Docker cleanup
   docker system prune -f
   ```

---

## 🚨 Emergency: If You Need More Space Fast

If you're still above 90% after all cleanups:

1. **Check for large files:**
   ```bash
   find . -type f -size +100M -exec ls -lh {} \;
   ```

2. **Check Docker volumes:**
   ```bash
   docker volume ls
   docker volume prune -f
   ```

3. **Check for duplicate files:**
   ```bash
   find . -type f -exec md5sum {} \; | sort | uniq -d -w 32
   ```

---

**Bottom Line:** Run the cleanup script with `--dry-run` first to see what would be removed, then run it for real. The safe cleanups + Docker cleanup should get you below 90% in about 5 minutes.





