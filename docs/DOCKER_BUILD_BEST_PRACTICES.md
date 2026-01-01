# Docker Build Best Practices & Troubleshooting

**Date:** December 22, 2025  
**Purpose:** Document common Docker build issues and solutions for SymphAIny Platform

---

## ✅ Current Status: RESOLVED

**Issue:** Files not appearing in container  
**Root Cause:** Container was running old image  
**Solution:** Restart container to pick up new image  
**Status:** ✅ **FIXED** - Files are now in container

---

## 🔍 Common Docker Build Issues

### **Issue 1: Container Running Old Image**

**Symptoms:**
- Files exist in source but not in running container
- Changes don't appear after rebuild
- Import errors for new modules

**Root Cause:**
- Container is using cached/old image
- `docker-compose up` doesn't rebuild by default
- Image was built before files existed

**Solution:**
```bash
# Option 1: Rebuild and restart
docker-compose build --no-cache backend
docker-compose up -d backend

# Option 2: Force recreate
docker-compose up -d --force-recreate --build backend

# Option 3: Complete reset
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d backend
```

**Prevention:**
- Always use `--build` flag when starting: `docker-compose up -d --build`
- Use `--no-cache` for critical builds
- Check image timestamps: `docker images symphainy_source-backend`

---

### **Issue 2: Build Cache Not Invalidating**

**Symptoms:**
- Changes to code don't appear after rebuild
- `COPY . .` layer is cached
- Files modified but build uses old version

**Root Cause:**
- Docker caches layers based on file checksums
- `COPY . .` layer cached from previous build
- Build context snapshot taken at build start

**Solution:**
```bash
# Force rebuild without cache
docker-compose build --no-cache backend

# Or remove old image first
docker rmi symphainy_source-backend
docker-compose build backend
```

**Prevention:**
- Use `--no-cache` for development builds
- Consider explicit COPY for critical directories
- Use BuildKit for better caching: `DOCKER_BUILDKIT=1 docker-compose build`

---

### **Issue 3: .dockerignore Excluding Files**

**Symptoms:**
- Files exist in source but not in image
- Specific directories missing
- Build succeeds but files absent

**Root Cause:**
- `.dockerignore` pattern matching files
- Overly broad exclusion patterns
- Hidden files excluded

**Solution:**
```bash
# Check .dockerignore
cat symphainy-platform/.dockerignore

# Test what's excluded
docker build --no-cache -f Dockerfile . 2>&1 | grep -i "excluding\|ignoring"

# Temporarily rename .dockerignore
mv .dockerignore .dockerignore.bak
docker-compose build backend
mv .dockerignore.bak .dockerignore
```

**Prevention:**
- Review `.dockerignore` regularly
- Use specific patterns, not broad wildcards
- Test builds after updating `.dockerignore`

---

### **Issue 4: Build Context Wrong**

**Symptoms:**
- Files in wrong location in container
- Path errors in container
- Files missing despite being in source

**Root Cause:**
- Build context doesn't match Dockerfile location
- `COPY` paths relative to wrong directory
- Context excludes needed directories

**Solution:**
```bash
# Verify build context in docker-compose.yml
grep -A 5 "backend:" docker-compose.yml | grep context

# Should be: context: ./symphainy-platform
# Dockerfile should be in that directory

# Test build context
cd symphainy-platform
docker build -f Dockerfile . --progress=plain
```

**Prevention:**
- Keep build context and Dockerfile in sync
- Document build context in README
- Use absolute paths in docker-compose.yml

---

### **Issue 5: File Permissions/Ownership**

**Symptoms:**
- Files exist but can't be read
- Permission denied errors
- Files owned by wrong user

**Root Cause:**
- Files copied as root, container runs as non-root
- `chown` in Dockerfile not working
- Volume mounts with wrong permissions

**Solution:**
```bash
# Check file ownership in container
docker-compose exec backend ls -la /app/backend/journey/orchestrators/

# Fix in Dockerfile (already done):
RUN useradd -m -u 1000 symphainy && \
    chown -R symphainy:symphainy /app
USER symphainy
```

**Prevention:**
- Always set correct ownership in Dockerfile
- Use consistent UID/GID
- Test with non-root user

---

## 📋 Build Workflow Best Practices

### **Development Workflow:**

```bash
# 1. Make code changes
# ... edit files ...

# 2. Rebuild (with cache for speed)
docker-compose build backend

# 3. Restart to pick up changes
docker-compose restart backend

# OR: Rebuild and restart in one command
docker-compose up -d --build backend
```

### **Production Build Workflow:**

```bash
# 1. Clean old images
docker-compose down
docker rmi symphainy_source-backend

# 2. Rebuild without cache
docker-compose build --no-cache backend

# 3. Verify files in image
docker run --rm --entrypoint /bin/sh symphainy_source-backend \
  -c "ls -la /app/backend/journey/orchestrators/"

# 4. Start fresh
docker-compose up -d backend
```

### **Debugging Build Issues:**

```bash
# 1. Check what Docker sees in build context
cd symphainy-platform
docker build --no-cache -f Dockerfile . --progress=plain 2>&1 | grep COPY

# 2. Verify files in built image
docker run --rm --entrypoint /bin/sh symphainy_source-backend \
  -c "find /app -name 'content_journey_orchestrator*'"

# 3. Compare source vs image
# Source:
ls -la backend/journey/orchestrators/

# Image:
docker run --rm --entrypoint /bin/sh symphainy_source-backend \
  -c "ls -la /app/backend/journey/orchestrators/"
```

---

## 🔧 Quick Reference Commands

### **Rebuild Commands:**
```bash
# Quick rebuild (uses cache)
docker-compose build backend

# Full rebuild (no cache)
docker-compose build --no-cache backend

# Rebuild and restart
docker-compose up -d --build backend

# Force recreate
docker-compose up -d --force-recreate --build backend
```

### **Verification Commands:**
```bash
# Check image timestamp
docker images symphainy_source-backend

# Check container image
docker ps --filter "name=backend" --format "{{.Image}}"

# Verify files in container
docker-compose exec backend ls -la /app/backend/journey/orchestrators/

# Test import
docker-compose exec backend python3 -c "from backend.journey.orchestrators.content_journey_orchestrator.content_analysis_orchestrator import ContentJourneyOrchestrator; print('✅ OK')"
```

### **Cleanup Commands:**
```bash
# Remove old images
docker rmi symphainy_source-backend

# Clean build cache
docker builder prune

# Full cleanup (careful!)
docker system prune -a --volumes
```

---

## 📊 Troubleshooting Checklist

When files don't appear in container:

- [ ] **Check source files exist:** `ls -la symphainy-platform/backend/journey/orchestrators/`
- [ ] **Check .dockerignore:** `cat symphainy-platform/.dockerignore | grep -i journey`
- [ ] **Check build context:** `grep context docker-compose.yml`
- [ ] **Check image timestamp:** `docker images symphainy_source-backend`
- [ ] **Check container image:** `docker ps --filter "name=backend"`
- [ ] **Rebuild without cache:** `docker-compose build --no-cache backend`
- [ ] **Restart container:** `docker-compose restart backend`
- [ ] **Verify in container:** `docker-compose exec backend ls -la /app/backend/journey/orchestrators/`

---

## 🎯 Key Takeaways

1. **Always rebuild after code changes:** `docker-compose build backend`
2. **Use `--no-cache` for critical builds:** Ensures fresh build
3. **Restart container after rebuild:** `docker-compose restart backend`
4. **Check image timestamps:** Verify you're using the latest image
5. **Test imports in container:** Verify files are accessible

---

## 📝 Current Configuration

**Build Context:** `./symphainy-platform`  
**Dockerfile:** `Dockerfile` in `symphainy-platform/`  
**COPY Command:** `COPY . .` (copies everything)  
**.dockerignore:** No exclusions for `backend/journey/orchestrators/`  
**User:** `symphainy` (UID 1000)  
**Status:** ✅ **WORKING CORRECTLY**

---

**Last Updated:** December 22, 2025  
**Status:** ✅ **RESOLVED** - Files are in container, build is working correctly



