# Symphainy Source Optimization Analysis

**Date:** 2025-01-29  
**Current Size:** 2.5GB  
**Goal:** Identify optimization opportunities within symphainy_source

---

## 📊 Current Space Breakdown

### **Total: 2.5GB**

| Component | Size | % of Total | Optimization Potential |
|-----------|------|------------|------------------------|
| `.git` | 1.3GB | 52% | ⚠️ Medium (git gc) |
| `logs/` | 640MB | 26% | ✅ High (clean old logs) |
| `symphainy-frontend/node_modules` | 405MB | 16% | ⚠️ Low (can reinstall) |
| `symphainy-platform` | 147MB | 6% | ❌ None (active code) |
| `tests/` | 15MB | <1% | ❌ None (active code) |
| Other | ~10MB | <1% | ❌ None |

---

## 🎯 Optimization Opportunities

### **1. Log Files (640MB) - HIGH PRIORITY** ✅

**Location:** `symphainy_source/logs/`

**Current State:**
- Many log files are 8-11MB each
- Multiple rotated log files (`.log.1`, `.log.2`, etc.)
- Old logs accumulating over time

**Optimization:**
```bash
# Remove logs older than 7 days
find symphainy_source/logs -type f -name "*.log*" -mtime +7 -delete

# Or keep only last 5 rotated logs per service
find symphainy_source/logs -type f -name "*.log.[6-9]" -delete
find symphainy_source/logs -type f -name "*.log.[1-9][0-9]" -delete
```

**Potential Savings:** ~400-500MB (keeping last week of logs)

**Risk:** ✅ Low - logs can be regenerated

---

### **2. Git Repository (1.3GB) - MEDIUM PRIORITY** ⚠️

**Location:** `symphainy_source/.git/`

**Current State:**
- Large pack file: `pack-9497f0c5a7f6257d16d1f9416c1c6604d0b5c1ac.pack` (1.3GB)
- This is normal for active repositories with history
- Contains all commit history and objects

**Optimization:**
```bash
cd symphainy_source

# Aggressive garbage collection (removes unreachable objects)
git gc --aggressive --prune=now

# Remove old reflog entries (if you don't need them)
git reflog expire --expire=now --all
git gc --prune=now
```

**Potential Savings:** ~200-400MB (depends on repo state)

**Risk:** ⚠️ Medium - aggressive gc can take time, but safe

**Note:** This is normal for active repos. The 1.3GB pack file contains your entire git history, which is valuable.

---

### **3. Node Modules (405MB) - LOW PRIORITY** ⚠️

**Location:** `symphainy_source/symphainy-frontend/node_modules/`

**Current State:**
- Standard Next.js/React dependencies
- Can be regenerated with `npm install`

**Optimization:**
```bash
# Remove and reinstall (only if you need the space)
cd symphainy_source/symphainy-frontend
rm -rf node_modules
npm install
```

**Potential Savings:** 0MB (you'd need to reinstall)

**Risk:** ✅ Low - but requires reinstall time

**Note:** Not recommended unless you're desperate for space. The 405MB is normal for a modern frontend project.

---

## 🚀 Recommended Cleanup Strategy

### **Quick Win (5 minutes):**
```bash
cd /home/founders/demoversion/symphainy_source

# Clean old log files (keep last 7 days)
find logs -type f -name "*.log*" -mtime +7 -delete

# Expected savings: ~400-500MB
```

### **Medium Effort (10 minutes):**
```bash
cd /home/founders/demoversion/symphainy_source

# Clean old logs
find logs -type f -name "*.log*" -mtime +7 -delete

# Optimize git repository
git gc --aggressive --prune=now

# Expected savings: ~600-900MB total
```

---

## 📋 Detailed Log File Analysis

### **Largest Log Files:**
- `TrafficCopService.log.*` - 11MB each (5 files = 55MB)
- `ServiceDiscoveryAbstraction*.log.*` - 11MB each (multiple files)
- `ConsulServiceDiscoveryAdapter*.log` - 9.2MB
- `NurseService.log` - 8.6MB
- `PostOfficeService.log` - 8.5MB
- Many others in 7-8MB range

### **Log Rotation Pattern:**
Most services have rotated logs:
- `.log` (current)
- `.log.1` (previous)
- `.log.2` (older)
- `.log.3` (even older)
- etc.

**Recommendation:** Keep only `.log`, `.log.1`, `.log.2` (last 3 rotations)

---

## 💡 Long-Term Optimization Strategies

### **1. Implement Log Rotation Policy**
```python
# In logging configuration
LOG_ROTATION_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_ROTATION_BACKUP_COUNT = 3  # Keep only 3 backups
```

### **2. Use Log Aggregation**
- Send logs to external service (e.g., Loki, which you already have)
- Keep only recent logs locally
- Archive old logs to cold storage

### **3. Git LFS for Large Files**
If you have large binary files in git history:
```bash
git lfs migrate import --include="*.pdf,*.zip,*.tar.gz" --everything
```

### **4. Regular Maintenance Script**
Create a weekly cleanup script:
```bash
#!/bin/bash
# Clean logs older than 7 days
find logs -type f -name "*.log*" -mtime +7 -delete

# Git maintenance
git gc --auto

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
```

---

## 🎯 Summary

### **Within symphainy_source (2.5GB total):**

**Quick Wins:**
- ✅ Log files: ~400-500MB (clean old logs)
- ⚠️ Git optimization: ~200-400MB (git gc)

**Total Potential Savings:** ~600-900MB (24-36% reduction)

**Not Recommended:**
- ❌ Removing node_modules (requires reinstall, no net savings)
- ❌ Removing active code (symphainy-platform, tests)

### **The Real Space Issue:**

The 70GB is **not** in symphainy_source (only 2.5GB). It's in:
- Legacy directories: 4.5GB (you said not ready to remove)
- Docker: 7.3GB (can't free while containers running)
- Other directories: ~56GB (need to investigate)

**Next Step:** We should investigate what's using the other ~56GB in the parent directory.

---

## 🔍 Action Items

1. ✅ **Clean old log files** (quick win - 400-500MB)
2. ⚠️ **Run git gc** (medium effort - 200-400MB)
3. 🔍 **Investigate parent directory** (find the other 56GB)

---

**Bottom Line:** Within symphainy_source, we can free ~600-900MB by cleaning logs and optimizing git. The real space issue is elsewhere in the filesystem.





