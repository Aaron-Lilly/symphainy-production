#!/usr/bin/env python3
"""
Surgical Script: Replace content_steward with data_steward

ONLY replaces variable/attribute references:
- content_steward = → data_steward =
- self.content_steward → self.data_steward
- content_steward. → data_steward.
- await content_steward → await data_steward

DOES NOT replace:
- Class names (ContentStewardService)
- Method names (get_content_steward_api)
- Comments (preserved as-is)
- String literals
- Import statements

Usage:
    python3 scripts/update_content_steward_to_data_steward.py --dry-run  # Preview changes
    python3 scripts/update_content_steward_to_data_steward.py --execute  # Apply changes
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict

# Directories to process
TARGET_DIRS = [
    "backend/journey",
    "backend/content",
    "backend/insights",
    "backend/solution",
    "backend/smart_city/services/city_manager",
]

# Files to exclude (already updated or special cases)
EXCLUDE_PATTERNS = [
    "*.archived.*",
    "*.old",
    "__pycache__",
    ".pyc",
]

# Patterns to replace (surgical - only variable/attribute references)
REPLACEMENT_PATTERNS = [
    # Variable assignments: content_steward = → data_steward =
    (r'\bcontent_steward\s*=', r'data_steward ='),
    
    # Attribute access: self.content_steward → self.data_steward
    (r'\bself\.content_steward\b', r'self.data_steward'),
    
    # Direct variable access: content_steward. → data_steward.
    # But NOT in method names or class names
    (r'\bcontent_steward\.', r'data_steward.'),
    
    # In await statements: await content_steward → await data_steward
    (r'\bawait\s+content_steward\b', r'await data_steward'),
    
    # In if/elif conditions: if content_steward → if data_steward
    (r'\bif\s+content_steward\b', r'if data_steward'),
    (r'\belif\s+content_steward\b', r'elif data_steward'),
    
    # In not conditions: not content_steward → not data_steward
    (r'\bnot\s+content_steward\b', r'not data_steward'),
]

# Patterns to preserve (DO NOT replace)
PRESERVE_PATTERNS = [
    r'ContentSteward',  # Class names
    r'get_content_steward_api',  # Method names
    r'content_steward_service',  # Service names
    r'content_steward/',  # Directory paths
    r'"content_steward"',  # String literals
    r"'content_steward'",  # String literals
    r'#.*content_steward',  # Comments (we'll handle separately)
]


def should_exclude_file(file_path: Path) -> bool:
    """Check if file should be excluded."""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in str(file_path):
            return True
    return False


def is_preserved_context(line: str, match_start: int, match_end: int) -> bool:
    """Check if match is in a preserved context (string, comment, etc.)."""
    # Check if in string literal
    before = line[:match_start]
    after = line[match_end:]
    
    # Count quotes before match
    single_quotes_before = before.count("'") - before.count("\\'")
    double_quotes_before = before.count('"') - before.count('\\"')
    
    # Check if we're inside a string
    in_single_string = (single_quotes_before % 2) == 1
    in_double_string = (double_quotes_before % 2) == 1
    
    if in_single_string or in_double_string:
        return True
    
    # Check if in comment
    comment_pos = line.find('#')
    if comment_pos != -1 and match_start > comment_pos:
        return True
    
    # Check if matches preserve patterns
    for pattern in PRESERVE_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    
    return False


def replace_in_line(line: str) -> Tuple[str, List[str]]:
    """
    Replace content_steward with data_steward in a line.
    
    Returns:
        (new_line, changes_made)
    """
    original_line = line
    changes = []
    
    # Apply each replacement pattern
    for pattern, replacement in REPLACEMENT_PATTERNS:
        # Find all matches
        matches = list(re.finditer(pattern, line))
        
        # Process matches in reverse order (to preserve positions)
        for match in reversed(matches):
            start, end = match.span()
            
            # Check if this match should be preserved
            if is_preserved_context(line, start, end):
                continue
            
            # Check if it's part of a preserved pattern
            preserve_match = False
            for preserve_pattern in PRESERVE_PATTERNS:
                if re.search(preserve_pattern, line[max(0, start-20):end+20], re.IGNORECASE):
                    preserve_match = True
                    break
            
            if preserve_match:
                continue
            
            # Apply replacement
            line = line[:start] + replacement + line[end:]
            changes.append(f"  Line {match.start()}-{match.end()}: '{match.group()}' → '{replacement}'")
    
    return line, changes


def process_file(file_path: Path, dry_run: bool = True) -> Dict[str, any]:
    """Process a single file."""
    result = {
        "file": str(file_path),
        "changed": False,
        "changes": [],
        "error": None
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        file_changes = []
        
        for line_num, line in enumerate(lines, 1):
            new_line, changes = replace_in_line(line)
            
            if new_line != line:
                result["changed"] = True
                file_changes.append(f"Line {line_num}:")
                file_changes.extend(changes)
            
            new_lines.append(new_line)
        
        if result["changed"]:
            result["changes"] = file_changes
            
            if not dry_run:
                # Write changes
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                result["status"] = "UPDATED"
            else:
                result["status"] = "WOULD_UPDATE"
        else:
            result["status"] = "NO_CHANGES"
    
    except Exception as e:
        result["error"] = str(e)
        result["status"] = "ERROR"
    
    return result


def find_python_files(base_dir: Path) -> List[Path]:
    """Find all Python files in target directories."""
    python_files = []
    
    for target_dir in TARGET_DIRS:
        full_path = base_dir / target_dir
        if not full_path.exists():
            continue
        
        for py_file in full_path.rglob("*.py"):
            if not should_exclude_file(py_file):
                python_files.append(py_file)
    
    return sorted(python_files)


def main():
    parser = argparse.ArgumentParser(
        description="Surgically replace content_steward with data_steward"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply changes (requires explicit flag)"
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default="symphainy-platform",
        help="Base directory (default: symphainy-platform)"
    )
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Error: Must specify --dry-run or --execute")
        sys.exit(1)
    
    if args.dry_run and args.execute:
        print("❌ Error: Cannot specify both --dry-run and --execute")
        sys.exit(1)
    
    # Get script directory and find base
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent
    
    # Find base directory
    base_dir = workspace_root / args.base_dir
    if not base_dir.exists():
        print(f"❌ Error: Base directory not found: {base_dir}")
        sys.exit(1)
    
    print(f"🔍 Searching for Python files in: {base_dir}")
    print(f"📁 Target directories: {', '.join(TARGET_DIRS)}")
    print(f"🔧 Mode: {'DRY RUN (preview only)' if args.dry_run else 'EXECUTE (applying changes)'}")
    print()
    
    # Find files
    python_files = find_python_files(base_dir)
    print(f"📄 Found {len(python_files)} Python files to check")
    print()
    
    # Process files
    results = []
    for py_file in python_files:
        result = process_file(py_file, dry_run=args.dry_run)
        results.append(result)
    
    # Summary
    changed_files = [r for r in results if r["changed"]]
    error_files = [r for r in results if r.get("error")]
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files checked: {len(results)}")
    print(f"Files with changes: {len(changed_files)}")
    print(f"Files with errors: {len(error_files)}")
    print()
    
    if changed_files:
        print("FILES WITH CHANGES:")
        print("-" * 80)
        for result in changed_files:
            print(f"✅ {result['file']}")
            if result["changes"]:
                for change in result["changes"][:3]:  # Show first 3 changes
                    print(change)
                if len(result["changes"]) > 3:
                    print(f"  ... and {len(result['changes']) - 3} more changes")
            print()
    
    if error_files:
        print("FILES WITH ERRORS:")
        print("-" * 80)
        for result in error_files:
            print(f"❌ {result['file']}: {result['error']}")
        print()
    
    if args.dry_run and changed_files:
        print("=" * 80)
        print("💡 To apply these changes, run with --execute flag")
        print("=" * 80)
    elif args.execute and changed_files:
        print("=" * 80)
        print(f"✅ Successfully updated {len(changed_files)} files")
        print("=" * 80)
        print()
        print("⚠️  NOTE: Some code comments may still contain references to 'content_steward'")
        print("    These are preserved for historical context and can be updated manually if needed.")
        print()


if __name__ == "__main__":
    main()


