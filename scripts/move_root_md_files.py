#!/usr/bin/env python3
"""
Script to move all .md files from symphainy_source root to docs/12-5-archive/
"""
import os
import shutil
from pathlib import Path

# Define paths
root_dir = Path("/home/founders/demoversion/symphainy_source")
docs_dir = root_dir / "docs"
archive_dir = docs_dir / "12-5-archive"

# Files to keep in root (like README.md)
keep_in_root = {"README.md"}

def move_md_files():
    """Move all .md files from root to archive directory."""
    # Create archive directory if it doesn't exist
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all .md files in root
    root_md_files = list(root_dir.glob("*.md"))
    
    moved_files = []
    skipped_files = []
    
    for md_file in root_md_files:
        # Skip files that should stay in root
        if md_file.name in keep_in_root:
            skipped_files.append(md_file.name)
            continue
        
        # Skip if file is actually in a subdirectory
        if md_file.parent != root_dir:
            continue
        
        # Destination path
        dest_path = archive_dir / md_file.name
        
        # Move file
        try:
            shutil.move(str(md_file), str(dest_path))
            moved_files.append(md_file.name)
            print(f"✓ Moved: {md_file.name}")
        except Exception as e:
            print(f"✗ Error moving {md_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Moved: {len(moved_files)} files")
    print(f"  Skipped: {len(skipped_files)} files (kept in root)")
    print(f"  Archive location: {archive_dir}")
    print(f"{'='*60}")
    
    if moved_files:
        print(f"\nMoved files:")
        for f in sorted(moved_files):
            print(f"  - {f}")
    
    if skipped_files:
        print(f"\nSkipped files (kept in root):")
        for f in sorted(skipped_files):
            print(f"  - {f}")

if __name__ == "__main__":
    move_md_files()



