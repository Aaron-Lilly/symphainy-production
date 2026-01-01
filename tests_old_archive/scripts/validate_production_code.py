#!/usr/bin/env python3
"""
Production Code Validation Script

Scans production code for anti-patterns:
- Mocks in production code
- TODOs/FIXMEs
- Empty implementations
- Hardcoded test values
- HACK/CHEAT comments

Usage:
    python3 validate_production_code.py [--path PATH] [--fix]

Exit codes:
    0: No violations found
    1: Violations found
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class Violation:
    """Represents a code violation."""
    file_path: str
    line_number: int
    line_content: str
    violation_type: str
    message: str

class ProductionCodeValidator:
    """Validates production code for anti-patterns."""
    
    def __init__(self, base_path: Path):
        """Initialize validator."""
        self.base_path = base_path
        self.violations: List[Violation] = []
        
        # Patterns to check
        self.patterns = {
            "mock_in_production": [
                r'\bMock\(',
                r'\bMagicMock\(',
                r'\bAsyncMock\(',
                r'from unittest.mock import',
                r'import.*mock',
            ],
            "todo_comments": [
                r'#\s*TODO',
                r'#\s*FIXME',
                r'#\s*XXX',
                r'#\s*HACK',
                r'#\s*CHEAT',
                r'#\s*TEMP',
            ],
            "empty_implementation": [
                r'^\s+pass\s*$',  # Standalone pass statement
            ],
            "hardcoded_test_values": [
                r'["\']test_',
                r'["\']mock_',
                r'= "test',
                r'= \'test',
            ],
        }
        
        # Files/directories to exclude
        self.exclude_patterns = [
            '**/tests/**',
            '**/test_*.py',
            '**/__pycache__/**',
            '**/archive/**',
            '**/archived_*',
            '**/*_old.py',
            '**/*_backup.py',
            '**/*_original.py',
            '**/*_compact.py',
            '**/.pytest_cache/**',
            '**/htmlcov/**',
        ]
        
        # Patterns that are allowed (intentional pass statements)
        self.allowed_patterns = [
            r'^\s+pass\s*$.*#.*abstract',  # Abstract method
            r'^\s+pass\s*$.*#.*override',  # Override placeholder
            r'^\s+pass\s*$.*#.*ALLOWED',  # Explicitly allowed
        ]
    
    def should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned."""
        # Only scan Python files
        if not file_path.suffix == '.py':
            return False
        
        # Check exclude patterns
        file_str = str(file_path)
        for pattern in self.exclude_patterns:
            if Path(pattern).match(file_str) or file_path.match(pattern):
                return False
        
        # Only scan production code (symphainy-platform)
        if 'symphainy-platform' not in file_str:
            return False
        
        return True
    
    def scan_file(self, file_path: Path) -> List[Violation]:
        """Scan a file for violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                # Check each pattern type
                for violation_type, patterns in self.patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip if it's in a comment explaining why it's OK
                            if '# ALLOWED:' in line or '# VALID:' in line:
                                continue
                            
                            # Skip pass statements in abstract methods or base classes
                            if violation_type == "empty_implementation":
                                # Check if it's an abstract method (look for @abstractmethod or class is ABC)
                                if line_num > 1:
                                    # Check previous lines for abstract method decorator
                                    context_start = max(0, line_num - 5)
                                    context = '\n'.join(lines[context_start:line_num])
                                    if '@abstractmethod' in context or 'ABC' in context or 'abstract' in context.lower():
                                        continue
                            
                            violations.append(Violation(
                                file_path=str(file_path.relative_to(self.base_path)),
                                line_number=line_num,
                                line_content=line.rstrip(),
                                violation_type=violation_type,
                                message=self._get_violation_message(violation_type)
                            ))
                            break  # Only report once per line
        
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}", file=sys.stderr)
        
        return violations
    
    def _get_violation_message(self, violation_type: str) -> str:
        """Get human-readable violation message."""
        messages = {
            "mock_in_production": "Mock object found in production code (use dependency injection instead)",
            "todo_comments": "TODO/FIXME comment found (should be resolved before production)",
            "empty_implementation": "Empty implementation (pass statement) found",
            "hardcoded_test_values": "Hardcoded test value found (use configuration instead)",
        }
        return messages.get(violation_type, "Code quality violation")
    
    def scan_directory(self, directory: Path) -> List[Violation]:
        """Scan directory for violations."""
        violations = []
        
        for file_path in directory.rglob('*.py'):
            if self.should_scan_file(file_path):
                file_violations = self.scan_file(file_path)
                violations.extend(file_violations)
        
        return violations
    
    def validate(self) -> bool:
        """Validate production code. Returns True if no violations."""
        print("🔍 Scanning production code for anti-patterns...")
        print(f"   Base path: {self.base_path}")
        print()
        
        # Scan symphainy-platform directory
        platform_path = self.base_path / "symphainy-platform"
        if not platform_path.exists():
            print(f"❌ Platform directory not found: {platform_path}")
            return False
        
        self.violations = self.scan_directory(platform_path)
        
        # Group violations by type
        violations_by_type = {}
        for violation in self.violations:
            if violation.violation_type not in violations_by_type:
                violations_by_type[violation.violation_type] = []
            violations_by_type[violation.violation_type].append(violation)
        
        # Print results
        if not self.violations:
            print("✅ No violations found!")
            return True
        
        print(f"❌ Found {len(self.violations)} violation(s):\n")
        
        for violation_type, violations in violations_by_type.items():
            print(f"📋 {violation_type.upper().replace('_', ' ')} ({len(violations)} violation(s)):")
            for violation in violations:
                print(f"   {violation.file_path}:{violation.line_number}")
                print(f"      {violation.message}")
                print(f"      {violation.line_content[:80]}")
                print()
        
        return False
    
    def print_summary(self):
        """Print validation summary."""
        if not self.violations:
            return
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total violations: {len(self.violations)}")
        
        violations_by_type = {}
        for violation in self.violations:
            violations_by_type[violation.violation_type] = \
                violations_by_type.get(violation.violation_type, 0) + 1
        
        for violation_type, count in violations_by_type.items():
            print(f"  {violation_type}: {count}")
        
        print("\n💡 Tip: Review violations above and fix before committing")
        print("💡 Tip: Use '# ALLOWED: reason' to document intentional exceptions")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate production code for anti-patterns"
    )
    parser.add_argument(
        '--path',
        type=str,
        default=str(project_root),
        help='Base path to scan (default: project root)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix violations (not implemented yet)'
    )
    
    args = parser.parse_args()
    
    base_path = Path(args.path)
    if not base_path.exists():
        print(f"❌ Path does not exist: {base_path}")
        sys.exit(1)
    
    validator = ProductionCodeValidator(base_path)
    is_valid = validator.validate()
    validator.print_summary()
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()

