#!/usr/bin/env python3
"""
SymphAIny Platform - Comprehensive Naming Cleanup Script

This script performs systematic cleanup of naming inconsistencies across the platform.
It follows a surgical approach to preserve functionality while standardizing naming.
"""

import os
import shutil
import re
from pathlib import Path
from collections import defaultdict
import sys
from datetime import datetime

class NamingCleanupOrchestrator:
    """Orchestrates comprehensive naming cleanup across the platform."""
    
    def __init__(self):
        self.platform_root = Path(".")
        self.archive_dir = self.platform_root / "archive" / "legacy_naming_backup"
        self.cleanup_log = []
        self.renamed_files = {}
        self.updated_references = {}
        
    def create_archive_directory(self):
        """Create archive directory for backup."""
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created archive directory: {self.archive_dir}")
        
    def analyze_main_entry_points(self):
        """Analyze and standardize main entry points."""
        print("\n🔍 ANALYZING MAIN ENTRY POINTS:")
        
        main_variants = [
            "main.py",
            "enhanced_main.py", 
            "modern_main.py",
            "hybrid_main.py",
            "minimal_main.py",
            "startup.py",
            "orchestrate_services.py"
        ]
        
        existing_files = []
        for variant in main_variants:
            if (self.platform_root / variant).exists():
                existing_files.append(variant)
        
        print(f"  📊 Found {len(existing_files)} main entry point variants:")
        for file in existing_files:
            print(f"    - {file}")
        
        if len(existing_files) > 1:
            # Determine the most current version
            current_version = self._determine_current_main_version(existing_files)
            print(f"  🎯 Current version: {current_version}")
            
            # Archive other versions
            for file in existing_files:
                if file != current_version:
                    self._archive_file(file, f"main_entry_point_{file}")
                    print(f"    ✅ Archived: {file}")
            
            # Rename current version to main.py if needed
            if current_version != "main.py":
                self._rename_file(current_version, "main.py")
                print(f"    ✅ Renamed: {current_version} -> main.py")
        
        return existing_files
    
    def _determine_current_main_version(self, files):
        """Determine the most current main version based on content analysis."""
        # Priority order: enhanced_main.py > main.py > others
        priority_order = [
            "enhanced_main.py",
            "main.py", 
            "modern_main.py",
            "hybrid_main.py",
            "minimal_main.py",
            "startup.py",
            "orchestrate_services.py"
        ]
        
        for priority_file in priority_order:
            if priority_file in files:
                return priority_file
        
        return files[0]  # Fallback to first found
    
    def analyze_test_files(self):
        """Analyze and standardize test file naming."""
        print("\n🔍 ANALYZING TEST FILES:")
        
        test_patterns = [
            r"test_.*\.py$",
            r".*_test\.py$", 
            r".*_tests\.py$",
            r"test_.*_test\.py$"
        ]
        
        test_files = defaultdict(list)
        
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".py"):
                    for pattern in test_patterns:
                        if re.match(pattern, file):
                            test_files[pattern].append(os.path.join(root, file))
        
        print(f"  📊 Found test file inconsistencies:")
        for pattern, files in test_files.items():
            if len(files) > 1:
                print(f"    Pattern: {pattern} ({len(files)} files)")
                for file in files[:5]:  # Show first 5
                    print(f"      - {file}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
        
        # Standardize to test_*.py format
        self._standardize_test_files(test_files)
        
        return test_files
    
    def _standardize_test_files(self, test_files):
        """Standardize test files to test_*.py format."""
        print("  🔄 Standardizing test files to test_*.py format...")
        
        for pattern, files in test_files.items():
            if pattern != r"test_.*\.py$" and len(files) > 0:
                for file_path in files:
                    old_name = os.path.basename(file_path)
                    new_name = self._convert_to_test_format(old_name)
                    
                    if new_name != old_name:
                        new_path = os.path.join(os.path.dirname(file_path), new_name)
                        self._rename_file(file_path, new_path)
                        print(f"    ✅ Renamed: {old_name} -> {new_name}")
    
    def _convert_to_test_format(self, filename):
        """Convert filename to test_*.py format."""
        # Remove .py extension
        base_name = os.path.splitext(filename)[0]
        
        # Remove existing test prefixes/suffixes
        base_name = re.sub(r'^test_', '', base_name)
        base_name = re.sub(r'_test$', '', base_name)
        base_name = re.sub(r'_tests$', '', base_name)
        
        # Add test_ prefix
        return f"test_{base_name}.py"
    
    def analyze_service_files(self):
        """Analyze and standardize service file naming."""
        print("\n🔍 ANALYZING SERVICE FILES:")
        
        service_patterns = [
            r".*_service\.py$",
            r".*_services\.py$",
            r"service_.*\.py$",
            r"services_.*\.py$"
        ]
        
        service_files = defaultdict(list)
        
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".py"):
                    for pattern in service_patterns:
                        if re.match(pattern, file):
                            service_files[pattern].append(os.path.join(root, file))
        
        print(f"  📊 Found service file inconsistencies:")
        for pattern, files in service_files.items():
            if len(files) > 1:
                print(f"    Pattern: {pattern} ({len(files)} files)")
                for file in files[:5]:  # Show first 5
                    print(f"      - {file}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
        
        # Standardize to *_service.py format
        self._standardize_service_files(service_files)
        
        return service_files
    
    def _standardize_service_files(self, service_files):
        """Standardize service files to *_service.py format."""
        print("  🔄 Standardizing service files to *_service.py format...")
        
        for pattern, files in service_files.items():
            if pattern != r".*_service\.py$" and len(files) > 0:
                for file_path in files:
                    old_name = os.path.basename(file_path)
                    new_name = self._convert_to_service_format(old_name)
                    
                    if new_name != old_name:
                        new_path = os.path.join(os.path.dirname(file_path), new_name)
                        self._rename_file(file_path, new_path)
                        print(f"    ✅ Renamed: {old_name} -> {new_name}")
    
    def _convert_to_service_format(self, filename):
        """Convert filename to *_service.py format."""
        # Remove .py extension
        base_name = os.path.splitext(filename)[0]
        
        # Remove existing service prefixes/suffixes
        base_name = re.sub(r'^service_', '', base_name)
        base_name = re.sub(r'^services_', '', base_name)
        base_name = re.sub(r'_service$', '', base_name)
        base_name = re.sub(r'_services$', '', base_name)
        
        # Add _service suffix
        return f"{base_name}_service.py"
    
    def analyze_manager_files(self):
        """Analyze and standardize manager file naming."""
        print("\n🔍 ANALYZING MANAGER FILES:")
        
        manager_patterns = [
            r".*_manager\.py$",
            r".*_managers\.py$",
            r"manager_.*\.py$",
            r"managers_.*\.py$"
        ]
        
        manager_files = defaultdict(list)
        
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".py"):
                    for pattern in manager_patterns:
                        if re.match(pattern, file):
                            manager_files[pattern].append(os.path.join(root, file))
        
        print(f"  📊 Found manager file inconsistencies:")
        for pattern, files in manager_files.items():
            if len(files) > 1:
                print(f"    Pattern: {pattern} ({len(files)} files)")
                for file in files[:5]:  # Show first 5
                    print(f"      - {file}")
                if len(files) > 5:
                    print(f"      ... and {len(files) - 5} more")
        
        # Standardize to *_manager.py format
        self._standardize_manager_files(manager_files)
        
        return manager_files
    
    def _standardize_manager_files(self, manager_files):
        """Standardize manager files to *_manager.py format."""
        print("  🔄 Standardizing manager files to *_manager.py format...")
        
        for pattern, files in manager_files.items():
            if pattern != r".*_manager\.py$" and len(files) > 0:
                for file_path in files:
                    old_name = os.path.basename(file_path)
                    new_name = self._convert_to_manager_format(old_name)
                    
                    if new_name != old_name:
                        new_path = os.path.join(os.path.dirname(file_path), new_name)
                        self._rename_file(file_path, new_path)
                        print(f"    ✅ Renamed: {old_name} -> {new_name}")
    
    def _convert_to_manager_format(self, filename):
        """Convert filename to *_manager.py format."""
        # Remove .py extension
        base_name = os.path.splitext(filename)[0]
        
        # Remove existing manager prefixes/suffixes
        base_name = re.sub(r'^manager_', '', base_name)
        base_name = re.sub(r'^managers_', '', base_name)
        base_name = re.sub(r'_manager$', '', base_name)
        base_name = re.sub(r'_managers$', '', base_name)
        
        # Add _manager suffix
        return f"{base_name}_manager.py"
    
    def update_import_references(self):
        """Update import references to reflect renamed files."""
        print("\n🔍 UPDATING IMPORT REFERENCES:")
        
        # Find all Python files
        python_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        
        print(f"  📊 Analyzing {len(python_files)} Python files for import updates...")
        
        updated_count = 0
        for file_path in python_files:
            if self._update_imports_in_file(file_path):
                updated_count += 1
        
        print(f"  ✅ Updated imports in {updated_count} files")
        
        return updated_count
    
    def _update_imports_in_file(self, file_path):
        """Update imports in a specific file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Update imports based on renamed files
            for old_name, new_name in self.renamed_files.items():
                # Update import statements
                content = re.sub(
                    rf'from\s+(\S+)\s+import\s+{re.escape(old_name)}',
                    rf'from \1 import {new_name}',
                    content
                )
                content = re.sub(
                    rf'import\s+{re.escape(old_name)}',
                    f'import {new_name}',
                    content
                )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            print(f"    ⚠️ Error updating {file_path}: {e}")
            return False
    
    def _archive_file(self, file_path, archive_name):
        """Archive a file to the backup directory."""
        try:
            source_path = self.platform_root / file_path
            if source_path.exists():
                archive_path = self.archive_dir / archive_name
                shutil.move(str(source_path), str(archive_path))
                self.cleanup_log.append(f"Archived: {file_path} -> {archive_path}")
                return True
        except Exception as e:
            print(f"    ❌ Error archiving {file_path}: {e}")
            return False
    
    def _rename_file(self, old_path, new_path):
        """Rename a file and track the change."""
        try:
            old_path_obj = Path(old_path)
            new_path_obj = Path(new_path)
            
            if old_path_obj.exists():
                old_path_obj.rename(new_path_obj)
                self.renamed_files[old_path_obj.name] = new_path_obj.name
                self.cleanup_log.append(f"Renamed: {old_path} -> {new_path}")
                return True
        except Exception as e:
            print(f"    ❌ Error renaming {old_path}: {e}")
            return False
    
    def generate_cleanup_report(self):
        """Generate a comprehensive cleanup report."""
        report_path = self.archive_dir / "cleanup_report.md"
        
        with open(report_path, 'w') as f:
            f.write("# SymphAIny Platform - Naming Cleanup Report\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Summary\n")
            f.write(f"- **Files renamed:** {len(self.renamed_files)}\n")
            f.write(f"- **Files archived:** {len(self.cleanup_log)}\n")
            f.write(f"- **Import references updated:** {len(self.updated_references)}\n\n")
            
            f.write("## Renamed Files\n")
            for old_name, new_name in self.renamed_files.items():
                f.write(f"- `{old_name}` -> `{new_name}`\n")
            
            f.write("\n## Archived Files\n")
            for log_entry in self.cleanup_log:
                f.write(f"- {log_entry}\n")
        
        print(f"📄 Cleanup report generated: {report_path}")
    
    def run_comprehensive_cleanup(self):
        """Run the comprehensive naming cleanup process."""
        print("🚀 SYMPHAINY PLATFORM - COMPREHENSIVE NAMING CLEANUP")
        print("=" * 70)
        
        try:
            # Create archive directory
            self.create_archive_directory()
            
            # Analyze and clean up main entry points
            main_files = self.analyze_main_entry_points()
            
            # Analyze and clean up test files
            test_files = self.analyze_test_files()
            
            # Analyze and clean up service files
            service_files = self.analyze_service_files()
            
            # Analyze and clean up manager files
            manager_files = self.analyze_manager_files()
            
            # Update import references
            updated_imports = self.update_import_references()
            
            # Generate cleanup report
            self.generate_cleanup_report()
            
            print(f"\n🎉 CLEANUP COMPLETE!")
            print(f"  📊 Files renamed: {len(self.renamed_files)}")
            print(f"  📁 Files archived: {len(self.cleanup_log)}")
            print(f"  🔄 Import references updated: {updated_imports}")
            print(f"  📄 Report generated: {self.archive_dir / 'cleanup_report.md'}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Cleanup failed: {e}")
            return False

def main():
    """Main cleanup function."""
    orchestrator = NamingCleanupOrchestrator()
    success = orchestrator.run_comprehensive_cleanup()
    
    if success:
        print("\n✅ Comprehensive naming cleanup completed successfully!")
        print("⚠️  IMPORTANT: Please test the platform to ensure all functionality is preserved.")
    else:
        print("\n❌ Cleanup failed. Please review the errors and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()








