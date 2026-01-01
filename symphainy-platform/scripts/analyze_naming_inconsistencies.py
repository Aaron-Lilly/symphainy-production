#!/usr/bin/env python3
"""
SymphAIny Platform - Naming Inconsistencies Analysis Script

This script analyzes the platform for naming inconsistencies where we have multiple
versions of the same concept (e.g., main.py vs enhanced_main.py, test_*.py vs *_test.py).
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import sys

def analyze_naming_patterns():
    """Analyze naming patterns across the platform to identify inconsistencies."""
    print("🔍 SYMPHAINY PLATFORM - NAMING INCONSISTENCIES ANALYSIS")
    print("=" * 70)
    
    # Patterns to look for
    naming_patterns = {
        "main_variants": [
            r"main\.py$",
            r"enhanced_main\.py$", 
            r"modern_main\.py$",
            r"hybrid_main\.py$",
            r"minimal_main\.py$",
            r"startup\.py$",
            r"orchestrate_services\.py$"
        ],
        "test_variants": [
            r"test_.*\.py$",
            r".*_test\.py$",
            r".*_tests\.py$",
            r"test_.*_test\.py$"
        ],
        "service_variants": [
            r".*_service\.py$",
            r".*_services\.py$",
            r"service_.*\.py$",
            r"services_.*\.py$"
        ],
        "manager_variants": [
            r".*_manager\.py$",
            r".*_managers\.py$",
            r"manager_.*\.py$",
            r"managers_.*\.py$"
        ],
        "foundation_variants": [
            r".*_foundation\.py$",
            r".*_foundations\.py$",
            r"foundation_.*\.py$",
            r"foundations_.*\.py$"
        ],
        "config_variants": [
            r"config\.py$",
            r"configuration\.py$",
            r"settings\.py$",
            r"env\.py$",
            r"environment\.py$"
        ],
        "base_variants": [
            r"base\.py$",
            r"bases\.py$",
            r".*_base\.py$",
            r".*_bases\.py$"
        ],
        "init_variants": [
            r"__init__\.py$",
            r"init\.py$",
            r"initialize\.py$",
            r"initialization\.py$"
        ],
        "util_variants": [
            r"util\.py$",
            r"utils\.py$",
            r"utility\.py$",
            r"utilities\.py$"
        ],
        "helper_variants": [
            r"helper\.py$",
            r"helpers\.py$",
            r"assistant\.py$",
            r"assistants\.py$"
        ]
    }
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    print(f"\n📊 PLATFORM ANALYSIS:")
    print(f"  📁 Total Python files: {len(python_files)}")
    
    # Analyze each pattern
    inconsistencies = {}
    
    for pattern_name, patterns in naming_patterns.items():
        print(f"\n🔍 Analyzing {pattern_name.replace('_', ' ').title()}...")
        
        matches = defaultdict(list)
        
        for file_path in python_files:
            filename = os.path.basename(file_path)
            
            for pattern in patterns:
                if re.match(pattern, filename):
                    matches[pattern].append(file_path)
        
        # Find inconsistencies
        pattern_inconsistencies = []
        for pattern, files in matches.items():
            if len(files) > 1:
                pattern_inconsistencies.append({
                    "pattern": pattern,
                    "files": files,
                    "count": len(files)
                })
        
        if pattern_inconsistencies:
            inconsistencies[pattern_name] = pattern_inconsistencies
            print(f"  ❌ Found {len(pattern_inconsistencies)} inconsistencies")
            for inconsistency in pattern_inconsistencies:
                print(f"    Pattern: {inconsistency['pattern']}")
                print(f"    Files ({inconsistency['count']}):")
                for file in inconsistency['files']:
                    print(f"      - {file}")
        else:
            print(f"  ✅ No inconsistencies found")
    
    return inconsistencies, python_files

def analyze_specific_duplicates():
    """Analyze specific duplicate patterns."""
    print(f"\n🔍 ANALYZING SPECIFIC DUPLICATE PATTERNS:")
    
    # Look for files with similar names
    duplicate_groups = defaultdict(list)
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                # Extract base name without extension
                base_name = os.path.splitext(file)[0]
                
                # Remove common prefixes/suffixes to find similar files
                clean_name = re.sub(r'^(test_|_test|_tests)$', '', base_name)
                clean_name = re.sub(r'_(service|services|manager|managers|foundation|foundations|base|bases|util|utils|helper|helpers)$', '', clean_name)
                clean_name = re.sub(r'^(service|services|manager|managers|foundation|foundations|base|bases|util|utils|helper|helpers)_', '', clean_name)
                
                if clean_name:
                    duplicate_groups[clean_name].append(os.path.join(root, file))
    
    # Find groups with multiple files
    duplicates = {}
    for base_name, files in duplicate_groups.items():
        if len(files) > 1:
            duplicates[base_name] = files
    
    print(f"  📊 Found {len(duplicates)} potential duplicate groups")
    
    # Show top 20 most problematic
    sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n🔍 TOP DUPLICATE GROUPS:")
    for i, (base_name, files) in enumerate(sorted_duplicates[:20]):
        print(f"  {i+1:2d}. {base_name} ({len(files)} files):")
        for file in files:
            print(f"      - {file}")
    
    return duplicates

def analyze_import_inconsistencies():
    """Analyze import inconsistencies."""
    print(f"\n🔍 ANALYZING IMPORT INCONSISTENCIES:")
    
    import_patterns = defaultdict(set)
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Find import statements
                        import_matches = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+(\S+)', content, re.MULTILINE)
                        
                        for from_module, import_name in import_matches:
                            if from_module:
                                import_patterns[f"from {from_module} import {import_name}"].add(file_path)
                            else:
                                import_patterns[f"import {import_name}"].add(file_path)
                                
                except Exception as e:
                    continue
    
    # Find imports that appear in multiple files (potential inconsistencies)
    common_imports = {}
    for import_stmt, files in import_patterns.items():
        if len(files) > 1:
            common_imports[import_stmt] = list(files)
    
    print(f"  📊 Found {len(common_imports)} common imports across multiple files")
    
    # Show top 10 most common imports
    sorted_imports = sorted(common_imports.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n🔍 TOP COMMON IMPORTS:")
    for i, (import_stmt, files) in enumerate(sorted_imports[:10]):
        print(f"  {i+1:2d}. {import_stmt} ({len(files)} files):")
        for file in files[:5]:  # Show first 5 files
            print(f"      - {file}")
        if len(files) > 5:
            print(f"      ... and {len(files) - 5} more files")
    
    return common_imports

def generate_cleanup_recommendations(inconsistencies, duplicates, common_imports):
    """Generate cleanup recommendations."""
    print(f"\n🎯 CLEANUP RECOMMENDATIONS:")
    
    total_issues = 0
    
    # Count issues
    for pattern_name, pattern_inconsistencies in inconsistencies.items():
        for inconsistency in pattern_inconsistencies:
            total_issues += len(inconsistency['files']) - 1  # -1 because we keep one
    
    total_issues += sum(len(files) - 1 for files in duplicates.values())
    
    print(f"  📊 Total estimated cleanup items: {total_issues}")
    
    print(f"\n📋 CLEANUP STRATEGY:")
    print(f"  1. 🎯 Prioritize by impact:")
    print(f"     - Main entry points (main.py variants)")
    print(f"     - Test files (test_*.py vs *_test.py)")
    print(f"     - Service files (*_service.py vs *_services.py)")
    print(f"     - Manager files (*_manager.py vs *_managers.py)")
    
    print(f"\n  2. 🔄 Standardize naming conventions:")
    print(f"     - Use singular forms (service.py not services.py)")
    print(f"     - Use consistent prefixes (test_*.py not *_test.py)")
    print(f"     - Use descriptive names (main.py not enhanced_main.py)")
    
    print(f"\n  3. 🗑️ Archive legacy versions:")
    print(f"     - Move old versions to archive/legacy_naming/")
    print(f"     - Keep only the most current/architecturally consistent version")
    print(f"     - Update all references and imports")
    
    print(f"\n  4. 🔍 Update references:")
    print(f"     - Search and replace import statements")
    print(f"     - Update documentation references")
    print(f"     - Update test references")
    print(f"     - Update configuration files")
    
    return total_issues

def main():
    """Main analysis function."""
    try:
        print("🔍 Starting comprehensive naming inconsistencies analysis...")
        
        # Analyze naming patterns
        inconsistencies, python_files = analyze_naming_patterns()
        
        # Analyze specific duplicates
        duplicates = analyze_specific_duplicates()
        
        # Analyze import inconsistencies
        common_imports = analyze_import_inconsistencies()
        
        # Generate recommendations
        total_issues = generate_cleanup_recommendations(inconsistencies, duplicates, common_imports)
        
        print(f"\n🎯 SUMMARY:")
        print(f"  📊 Total Python files analyzed: {len(python_files)}")
        print(f"  ❌ Naming pattern inconsistencies: {len(inconsistencies)}")
        print(f"  ❌ Duplicate file groups: {len(duplicates)}")
        print(f"  ❌ Common import patterns: {len(common_imports)}")
        print(f"  🧹 Estimated cleanup items: {total_issues}")
        
        print(f"\n⚠️  CLEANUP IMPACT:")
        print(f"  • This is a MASSIVE cleanup task")
        print(f"  • Will require systematic approach")
        print(f"  • Will require updating hundreds of references")
        print(f"  • Will require comprehensive testing")
        
        return {
            "inconsistencies": inconsistencies,
            "duplicates": duplicates,
            "common_imports": common_imports,
            "total_issues": total_issues,
            "python_files": python_files
        }
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return None

if __name__ == "__main__":
    main()








