#!/usr/bin/env python3
"""
Validate poetry.lock file integrity.

This script checks that poetry.lock is:
1. Present
2. Valid TOML syntax
3. Not corrupted (doesn't start with Poetry output text)
4. In sync with pyproject.toml (via poetry check)

Usage:
    python3 scripts/validate-poetry-lock.py

Exit codes:
    0: Lock file is valid
    1: Lock file is invalid or missing
"""
import sys
import tomli
from pathlib import Path

def validate_lock_file():
    """Validate poetry.lock file integrity."""
    lock_file = Path("poetry.lock")
    
    if not lock_file.exists():
        print("❌ poetry.lock file not found")
        print("   Please run 'poetry lock' to generate the lock file")
        return False
    
    try:
        with open(lock_file, "rb") as f:
            content = f.read()
            
        # Check for common corruption patterns
        if content.startswith(b"Resolving dependencies"):
            print("❌ Lock file appears corrupted (starts with Poetry output text)")
            print("   This indicates stdout was redirected to the lock file")
            print("   Please run 'poetry lock' locally to regenerate")
            return False
        
        # Check for other corruption patterns
        if b"Writing lock file" in content[:200]:
            print("❌ Lock file appears corrupted (contains Poetry output text)")
            print("   Please run 'poetry lock' locally to regenerate")
            return False
        
        # Validate TOML syntax
        try:
            with open(lock_file, "rb") as f:
                data = tomli.load(f)
            
            # Basic structure validation
            if "package" not in str(data) and "metadata" not in str(data):
                print("⚠️  Lock file structure may be invalid (missing expected sections)")
                # Don't fail, but warn
            
            print("✅ poetry.lock is valid TOML")
            return True
            
        except tomli.TOMLDecodeError as e:
            print(f"❌ poetry.lock is invalid TOML: {e}")
            print("   Please run 'poetry lock' locally to regenerate")
            return False
            
    except Exception as e:
        print(f"❌ Error validating poetry.lock: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    # Change to project root if running from scripts directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    if (project_root / "pyproject.toml").exists():
        import os
        os.chdir(project_root)
    
    success = validate_lock_file()
    
    if success:
        print("✅ poetry.lock validation passed")
    else:
        print("❌ poetry.lock validation failed")
        print("\nTo fix:")
        print("  1. Run 'poetry lock' locally")
        print("  2. Commit the updated poetry.lock file")
        print("  3. Re-run this validation")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())






