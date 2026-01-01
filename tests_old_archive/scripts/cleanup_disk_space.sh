#!/bin/bash
#
# Disk Space Cleanup Script for SymphAIny Platform
#
# This script safely cleans up disk space by removing:
# - Python cache files (__pycache__, *.pyc)
# - Test artifacts (.pytest_cache, coverage files)
# - Docker unused images and build cache
# - Node modules (if you want to reinstall)
# - Log files
# - Legacy/archive directories (with confirmation)
#
# Usage: ./cleanup_disk_space.sh [--aggressive] [--dry-run]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
AGGRESSIVE=false
DRY_RUN=false
PROJECT_ROOT="/home/founders/demoversion"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --aggressive)
            AGGRESSIVE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--aggressive] [--dry-run]"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🧹 Disk Space Cleanup Script${NC}"
echo "=================================="
echo ""

# Function to calculate space saved
calculate_space() {
    local path="$1"
    if [ -d "$path" ] || [ -f "$path" ]; then
        du -sh "$path" 2>/dev/null | cut -f1
    else
        echo "0"
    fi
}

# Function to remove with confirmation
safe_remove() {
    local path="$1"
    local description="$2"
    
    if [ ! -e "$path" ]; then
        echo -e "${YELLOW}⚠️  $description not found: $path${NC}"
        return
    fi
    
    local size=$(calculate_space "$path")
    echo -e "${BLUE}📦 $description: $size${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN] Would remove: $path${NC}"
    else
        rm -rf "$path"
        echo -e "${GREEN}✅ Removed: $path${NC}"
    fi
}

# Function to remove with user confirmation
confirm_remove() {
    local path="$1"
    local description="$2"
    
    if [ ! -e "$path" ]; then
        return
    fi
    
    local size=$(calculate_space "$path")
    echo -e "${YELLOW}⚠️  $description: $size${NC}"
    echo -e "${YELLOW}   Path: $path${NC}"
    
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN] Would ask to remove: $path${NC}"
        return
    fi
    
    if [ "$AGGRESSIVE" = true ]; then
        echo -e "${GREEN}   [AGGRESSIVE MODE] Removing...${NC}"
        rm -rf "$path"
        echo -e "${GREEN}✅ Removed: $path${NC}"
    else
        read -p "   Remove? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$path"
            echo -e "${GREEN}✅ Removed: $path${NC}"
        else
            echo -e "${YELLOW}⏭️  Skipped${NC}"
        fi
    fi
}

cd "$PROJECT_ROOT"

echo -e "${BLUE}📊 Current Disk Usage:${NC}"
df -h . | tail -1
echo ""

# ============================================================================
# PHASE 1: SAFE CLEANUPS (Always Safe)
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PHASE 1: Safe Cleanups (Always Safe to Remove)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Python cache files
echo -e "${BLUE}1. Python Cache Files (__pycache__, *.pyc)${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Python cache files removed${NC}"
echo ""

# Pytest cache
echo -e "${BLUE}2. Pytest Cache${NC}"
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✅ Pytest cache removed${NC}"
echo ""

# Coverage files
echo -e "${BLUE}3. Coverage Files${NC}"
find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name ".coverage" -delete 2>/dev/null || true
find . -type f -name ".coverage.*" -delete 2>/dev/null || true
find . -type d -name ".nyc_output" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✅ Coverage files removed${NC}"
echo ""

# Python egg-info and dist
echo -e "${BLUE}4. Python Build Artifacts${NC}"
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✅ Python build artifacts removed${NC}"
echo ""

# Log files (keep recent ones)
echo -e "${BLUE}5. Old Log Files${NC}"
find . -type f -name "*.log" -mtime +7 -delete 2>/dev/null || true
find . -type f -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
echo -e "${GREEN}✅ Old log files removed${NC}"
echo ""

# ============================================================================
# PHASE 2: DOCKER CLEANUP
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PHASE 2: Docker Cleanup${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if command -v docker &> /dev/null; then
    echo -e "${BLUE}Docker Space Usage:${NC}"
    docker system df
    echo ""
    
    if [ "$DRY_RUN" = false ]; then
        if [ "$AGGRESSIVE" = true ]; then
            echo -e "${GREEN}[AGGRESSIVE MODE] Cleaning Docker...${NC}"
            docker system prune -af --volumes 2>/dev/null || true
        else
            echo -e "${BLUE}Cleaning unused Docker images and containers...${NC}"
            docker system prune -f 2>/dev/null || true
            echo -e "${YELLOW}Note: Use --aggressive to also remove volumes and all unused images${NC}"
        fi
        echo -e "${GREEN}✅ Docker cleanup complete${NC}"
    else
        echo -e "${YELLOW}[DRY RUN] Would run: docker system prune -f${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Docker not available${NC}"
fi
echo ""

# ============================================================================
# PHASE 3: NODE MODULES (Optional - Requires Reinstall)
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PHASE 3: Node Modules (Optional - You'll Need to Reinstall)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

NODE_MODULES_SIZE=$(du -sh "$PROJECT_ROOT/symphainy_source/symphainy-frontend/node_modules" 2>/dev/null | cut -f1 || echo "0")
echo -e "${YELLOW}⚠️  node_modules: $NODE_MODULES_SIZE${NC}"
echo -e "${YELLOW}   Path: $PROJECT_ROOT/symphainy_source/symphainy-frontend/node_modules${NC}"
echo -e "${YELLOW}   Note: You'll need to run 'npm install' after removing this${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN] Would ask to remove node_modules${NC}"
elif [ "$AGGRESSIVE" = true ]; then
    echo -e "${GREEN}[AGGRESSIVE MODE] Removing node_modules...${NC}"
    rm -rf "$PROJECT_ROOT/symphainy_source/symphainy-frontend/node_modules"
    echo -e "${GREEN}✅ Removed node_modules${NC}"
else
    read -p "   Remove node_modules? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_ROOT/symphainy_source/symphainy-frontend/node_modules"
        echo -e "${GREEN}✅ Removed node_modules${NC}"
    else
        echo -e "${YELLOW}⏭️  Skipped node_modules${NC}"
    fi
fi
echo ""

# ============================================================================
# PHASE 4: LEGACY/ARCHIVE DIRECTORIES (Requires Confirmation)
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PHASE 4: Legacy/Archive Directories (Review Carefully)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Legacy directories (safe to remove if you're sure)
LEGACY_DIRS=(
    "$PROJECT_ROOT/symphainy-mvp-aaron-legacy:2.4G:Legacy MVP (Aaron)"
    "$PROJECT_ROOT/archive:950M:Archive directory"
    "$PROJECT_ROOT/symphainy-legacy:795M:Legacy Symphainy"
    "$PROJECT_ROOT/symphainy-mvp-backend-final-legacy:402M:Legacy MVP Backend"
    "$PROJECT_ROOT/symphainy-platformMVP:19M:Legacy Platform MVP"
    "$PROJECT_ROOT/symphainy-mvp-clean:14M:Legacy MVP Clean"
    "$PROJECT_ROOT/symphainy-mvp-final:12M:Legacy MVP Final"
)

for dir_info in "${LEGACY_DIRS[@]}"; do
    IFS=':' read -r path size description <<< "$dir_info"
    if [ -d "$path" ]; then
        confirm_remove "$path" "$description ($size)"
    fi
done
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📊 Final Disk Usage:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
df -h . | tail -1
echo ""

AVAILABLE=$(df -h . | tail -1 | awk '{print $4}')
echo -e "${GREEN}✅ Cleanup complete! Available space: $AVAILABLE${NC}"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo -e "   - Run with --dry-run first to see what would be removed"
echo -e "   - Run with --aggressive to skip confirmations"
echo -e "   - Legacy directories are safe to remove if you're sure you don't need them"
echo ""





