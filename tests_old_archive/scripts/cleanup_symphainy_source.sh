#!/bin/bash
#
# Symphainy Source Cleanup Script
# 
# Focused cleanup for symphainy_source directory only.
# Safe to run - only removes old logs and optimizes git.
#

set -e

PROJECT_ROOT="/home/founders/demoversion/symphainy_source"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🧹 Symphainy Source Cleanup${NC}"
echo "=============================="
echo ""

cd "$PROJECT_ROOT"

# Show current state
echo -e "${BLUE}📊 Current Size:${NC}"
du -sh . 2>/dev/null
echo ""

# ============================================================================
# PHASE 1: Clean Old Log Files
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PHASE 1: Clean Old Log Files${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -d "logs" ]; then
    # Count old logs
    OLD_LOGS=$(find logs -type f -name "*.log*" -mtime +7 | wc -l)
    OLD_LOGS_SIZE=$(find logs -type f -name "*.log*" -mtime +7 -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1 || echo "0")
    
    echo -e "${BLUE}Found $OLD_LOGS log files older than 7 days ($OLD_LOGS_SIZE)${NC}"
    
    if [ "$OLD_LOGS" -gt 0 ]; then
        echo -e "${YELLOW}Removing old log files...${NC}"
        find logs -type f -name "*.log*" -mtime +7 -delete
        echo -e "${GREEN}✅ Removed old log files${NC}"
    else
        echo -e "${GREEN}✅ No old log files to remove${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No logs directory found${NC}"
fi
echo ""

# ============================================================================
# PHASE 2: Optimize Git Repository
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PHASE 2: Optimize Git Repository${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -d ".git" ]; then
    echo -e "${BLUE}Current .git size:${NC}"
    du -sh .git 2>/dev/null
    echo ""
    
    echo -e "${YELLOW}Running git garbage collection...${NC}"
    echo -e "${YELLOW}(This may take a few minutes)${NC}"
    
    # Run git gc (non-aggressive first)
    git gc --auto --prune=now 2>&1 | head -5 || echo "Git gc completed"
    
    echo -e "${GREEN}✅ Git optimization complete${NC}"
    echo ""
    
    echo -e "${BLUE}New .git size:${NC}"
    du -sh .git 2>/dev/null
else
    echo -e "${YELLOW}⚠️  No .git directory found${NC}"
fi
echo ""

# ============================================================================
# PHASE 3: Clean Python Cache
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PHASE 3: Clean Python Cache${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BLUE}Removing Python cache files...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Python cache cleaned${NC}"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📊 Final Size:${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
du -sh . 2>/dev/null
echo ""

echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo -e "${BLUE}💡 Note:${NC}"
echo -e "   - Log files older than 7 days have been removed"
echo -e "   - Git repository has been optimized"
echo -e "   - Python cache files have been cleaned"
echo ""





