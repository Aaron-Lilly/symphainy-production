#!/usr/bin/env python3
"""
Test File Standardization Script
Standardizes test file naming to test_*.py pattern
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple
import re

def find_test_files() -> List[Tuple[str, str]]:
    """Find all test files with inconsistent naming."""
    test_files = []
    
    # Find files matching *_test.py pattern
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('_test.py'):
                old_path = os.path.join(root, file)
                new_name = file.replace('_test.py', '.py')
                new_name = f"test_{new_name}"
                new_path = os.path.join(root, new_name)
                test_files.append((old_path, new_path))
    
    # Find files matching *_tests.py pattern
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('_tests.py'):
                old_path = os.path.join(root, file)
                new_name = file.replace('_tests.py', '.py')
                new_name = f"test_{new_name}"
                new_path = os.path.join(root, new_name)
                test_files.append((old_path, new_path))
    
    return test_files

def update_import_references(old_path: str, new_path: str) -> None:
    """Update import references in Python files."""
    old_module = old_path.replace('/', '.').replace('.py', '').lstrip('.')
    new_module = new_path.replace('/', '.').replace('.py', '').lstrip('.')
    
    # Find all Python files that might import the old module
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Update import statements
                    updated_content = content.replace(f"from {old_module}", f"from {new_module}")
                    updated_content = updated_content.replace(f"import {old_module}", f"import {new_module}")
                    
                    if content != updated_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        print(f"  ✅ Updated imports in {file_path}")
                        
                except Exception as e:
                    print(f"  ⚠️ Could not update {file_path}: {e}")

def standardize_test_files():
    """Standardize test file naming."""
    print("🔧 STANDARDIZING TEST FILE NAMING")
    print("=================================")
    print("")
    
    test_files = find_test_files()
    
    if not test_files:
        print("✅ No test files need standardization")
        return
    
    print(f"📋 Found {len(test_files)} test files to standardize:")
    print("")
    
    for old_path, new_path in test_files:
        print(f"📝 {old_path} → {new_path}")
        
        # Check if target already exists
        if os.path.exists(new_path):
            print(f"  ⚠️ Target already exists, skipping")
            continue
        
        try:
            # Move the file
            shutil.move(old_path, new_path)
            print(f"  ✅ Renamed successfully")
            
            # Update import references
            update_import_references(old_path, new_path)
            
        except Exception as e:
            print(f"  ❌ Failed to rename: {e}")
    
    print("")
    print("✅ Test file standardization complete!")

if __name__ == "__main__":
    standardize_test_files()
