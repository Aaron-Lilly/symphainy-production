#!/usr/bin/env python3
"""
Production Readiness Audit Script

Scans the codebase for production readiness issues:
- Mocks/placeholders in production code
- Empty implementations
- TODOs/FIXMEs
- Hardcoded values
- Fallback patterns
- Missing error handling
- Configuration issues
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = PROJECT_ROOT / "symphainy-platform"
FRONTEND_ROOT = PROJECT_ROOT / "symphainy-frontend"

# Patterns to search for
PATTERNS = {
    "mocks": [
        r"Mock\(|mock\(|MagicMock\(|AsyncMock\(|@patch|unittest\.mock",
        r"fake_|Fake|FAKE|placeholder|Placeholder|PLACEHOLDER",
        r"stub_|Stub|STUB"
    ],
    "empty_implementations": [
        r"return \{\}\s*$",
        r"return None\s*$",
        r"^\s*pass\s*$",
        r"raise NotImplementedError",
        r"NotImplemented\s*$"
    ],
    "todos": [
        r"TODO|FIXME|XXX|HACK|CHEAT|BUG"
    ],
    "hardcoded_values": [
        r"localhost|127\.0\.0\.1|0\.0\.0\.0",
        r"hardcoded|hard-coded|HARDCODED",
        r"test_|TEST_|dev_|DEV_",
        r"change-in-production|CHANGE_IN_PRODUCTION"
    ],
    "fallback_patterns": [
        r"fallback|Fallback|FALLBACK",
        r"default.*=.*None|default.*=.*\{\}",
        r"or \{\}|or None|or ''|or \"\""
    ],
    "error_handling": [
        r"except.*:\s*pass",
        r"except.*:\s*return None",
        r"except.*:\s*return \{\}",
        r"except.*:\s*continue",
        r"except.*:\s*break"
    ],
    "secrets": [
        r"API_KEY|SECRET|PASSWORD|TOKEN|CREDENTIAL",
        r"sk-|pk_|eyJ"
    ]
}

# Directories to exclude
EXCLUDE_DIRS = {
    "__pycache__", "__tests__", "tests", "test", "archive", "archived",
    "node_modules", ".git", ".next", "coverage", "htmlcov", "logs",
    "playwright-report", "test-results", ".pytest_cache"
}

# File extensions to scan
BACKEND_EXTENSIONS = {".py"}
FRONTEND_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

# Files to exclude
EXCLUDE_FILES = {
    "production_readiness_audit.py",  # This script
    "test_", "spec.ts", "spec.js", ".test.", ".spec."
}


def should_scan_file(file_path: Path) -> bool:
    """Check if file should be scanned."""
    # Check if in excluded directory
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False
    
    # Check if excluded file
    file_name = file_path.name
    for exclude in EXCLUDE_FILES:
        if exclude in file_name:
            return False
    
    return True


def scan_file(file_path: Path, patterns: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    """Scan a single file for issues."""
    issues = defaultdict(list)
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments in some cases (but keep TODOs)
            stripped = line.strip()
            if stripped.startswith('#') and 'TODO' not in stripped and 'FIXME' not in stripped:
                continue
            
            # Check each pattern category
            for category, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Additional context
                        context_lines = []
                        start = max(0, line_num - 2)
                        end = min(len(lines), line_num + 2)
                        for i in range(start, end):
                            context_lines.append({
                                "line": i + 1,
                                "content": lines[i].rstrip()
                            })
                        
                        issues[category].append({
                            "file": str(file_path.relative_to(PROJECT_ROOT)),
                            "line": line_num,
                            "content": line.rstrip(),
                            "pattern": pattern,
                            "context": context_lines
                        })
                        break  # Only report once per line per category
    
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
    
    return dict(issues)


def scan_directory(directory: Path, extensions: set, patterns: Dict[str, List[str]]) -> Dict[str, List[Dict[str, Any]]]:
    """Scan a directory recursively."""
    all_issues = defaultdict(list)
    
    if not directory.exists():
        return dict(all_issues)
    
    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue
        
        if file_path.suffix not in extensions:
            continue
        
        if not should_scan_file(file_path):
            continue
        
        file_issues = scan_file(file_path, patterns)
        for category, issue_list in file_issues.items():
            all_issues[category].extend(issue_list)
    
    return dict(all_issues)


def analyze_configuration() -> Dict[str, Any]:
    """Analyze configuration files for issues."""
    config_issues = {
        "missing_files": [],
        "hardcoded_values": [],
        "security_issues": []
    }
    
    # Check for .env.secrets (we know it exists but Cursor can't see it)
    env_secrets = BACKEND_ROOT / ".env.secrets"
    if not env_secrets.exists():
        config_issues["missing_files"].append({
            "file": ".env.secrets",
            "issue": "File may not exist or be accessible",
            "note": "env_secrets_for_cursor.md exists as reference"
        })
    
    # Check production.env for hardcoded localhost
    prod_env = BACKEND_ROOT / "config" / "production.env"
    if prod_env.exists():
        with open(prod_env, 'r') as f:
            content = f.read()
            if 'localhost' in content:
                config_issues["hardcoded_values"].append({
                    "file": "config/production.env",
                    "issue": "Contains localhost references",
                    "note": "Acceptable for EC2 demo, needs Option C migration path"
                })
    
    # Check next.config.js for hardcoded localhost
    next_config = FRONTEND_ROOT / "next.config.js"
    if next_config.exists():
        with open(next_config, 'r') as f:
            content = f.read()
            if 'localhost:8000' in content:
                config_issues["hardcoded_values"].append({
                    "file": "symphainy-frontend/next.config.js",
                    "issue": "Defaults to localhost:8000",
                    "note": "Requires NEXT_PUBLIC_BACKEND_URL environment variable"
                })
    
    return config_issues


def analyze_startup_sequence() -> Dict[str, Any]:
    """Analyze startup sequence for issues."""
    startup_issues = {
        "error_handling": [],
        "dependencies": [],
        "configuration": []
    }
    
    main_py = BACKEND_ROOT / "main.py"
    if main_py.exists():
        with open(main_py, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
            # Check for error handling in startup
            for i, line in enumerate(lines, 1):
                if 'register_api_routers' in line and 'except' in lines[i:i+5]:
                    # Check if error is properly handled
                    if 'logger.warning' in '\n'.join(lines[i:i+10]):
                        startup_issues["error_handling"].append({
                            "file": "main.py",
                            "line": i,
                            "issue": "API router registration failure only logs warning",
                            "severity": "high",
                            "note": "Platform continues with 'monitoring endpoints only'"
                        })
                
                if 'load_dotenv' in line and '.env.secrets' in line:
                    startup_issues["configuration"].append({
                        "file": "main.py",
                        "line": i,
                        "issue": "Loads .env.secrets (file exists but Cursor can't see it)",
                        "severity": "info",
                        "note": "This is expected - file exists per user confirmation"
                    })
    
    startup_sh = BACKEND_ROOT / "startup.sh"
    if startup_sh.exists():
        with open(startup_sh, 'r') as f:
            content = f.read()
            if 'minimal mode' in content.lower():
                startup_issues["dependencies"].append({
                    "file": "startup.sh",
                    "issue": "Falls back to minimal mode if Docker Compose fails",
                    "severity": "medium",
                    "note": "Platform may start but services won't work"
                })
    
    return startup_issues


def generate_report(all_issues: Dict[str, List], config_issues: Dict, startup_issues: Dict) -> Dict[str, Any]:
    """Generate comprehensive audit report."""
    
    # Categorize by severity
    critical = []
    high = []
    medium = []
    low = []
    
    # Mocks in production code - CRITICAL
    if all_issues.get("mocks"):
        for issue in all_issues["mocks"]:
            if "backend" in issue["file"] and "test" not in issue["file"].lower():
                critical.append({
                    "category": "Mocks in Production Code",
                    "file": issue["file"],
                    "line": issue["line"],
                    "content": issue["content"][:100],
                    "severity": "critical"
                })
    
    # Empty implementations - HIGH
    if all_issues.get("empty_implementations"):
        for issue in all_issues["empty_implementations"]:
            if "backend" in issue["file"] and "test" not in issue["file"].lower():
                high.append({
                    "category": "Empty Implementation",
                    "file": issue["file"],
                    "line": issue["line"],
                    "content": issue["content"][:100],
                    "severity": "high"
                })
    
    # TODOs in production - MEDIUM
    if all_issues.get("todos"):
        for issue in all_issues["todos"]:
            if "test" not in issue["file"].lower() and "archive" not in issue["file"].lower():
                medium.append({
                    "category": "TODO/FIXME",
                    "file": issue["file"],
                    "line": issue["line"],
                    "content": issue["content"][:100],
                    "severity": "medium"
                })
    
    # Hardcoded values - MEDIUM
    if all_issues.get("hardcoded_values"):
        for issue in all_issues["hardcoded_values"]:
            if "test" not in issue["file"].lower() and "config" not in issue["file"].lower():
                medium.append({
                    "category": "Hardcoded Value",
                    "file": issue["file"],
                    "line": issue["line"],
                    "content": issue["content"][:100],
                    "severity": "medium"
                })
    
    # Silent error handling - HIGH
    if all_issues.get("error_handling"):
        for issue in all_issues["error_handling"]:
            if "backend" in issue["file"] and "test" not in issue["file"].lower():
                high.append({
                    "category": "Silent Error Handling",
                    "file": issue["file"],
                    "line": issue["line"],
                    "content": issue["content"][:100],
                    "severity": "high"
                })
    
    # Configuration issues
    if config_issues.get("hardcoded_values"):
        for issue in config_issues["hardcoded_values"]:
            medium.append({
                "category": "Configuration Issue",
                "file": issue["file"],
                "issue": issue["issue"],
                "note": issue.get("note", ""),
                "severity": "medium"
            })
    
    # Startup issues
    if startup_issues.get("error_handling"):
        for issue in startup_issues["error_handling"]:
            high.append({
                "category": "Startup Error Handling",
                "file": issue["file"],
                "line": issue.get("line", 0),
                "issue": issue["issue"],
                "note": issue.get("note", ""),
                "severity": issue.get("severity", "high")
            })
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "critical": len(critical),
            "high": len(high),
            "medium": len(medium),
            "low": len(low),
            "total": len(critical) + len(high) + len(medium) + len(low)
        },
        "issues": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },
        "raw_counts": {
            category: len(issues) for category, issues in all_issues.items()
        },
        "configuration_issues": config_issues,
        "startup_issues": startup_issues
    }


def main():
    """Main audit function."""
    print("=" * 80)
    print("PRODUCTION READINESS AUDIT")
    print("=" * 80)
    print()
    
    print("Scanning backend...")
    backend_issues = scan_directory(BACKEND_ROOT, BACKEND_EXTENSIONS, PATTERNS)
    
    print("Scanning frontend...")
    frontend_issues = scan_directory(FRONTEND_ROOT, FRONTEND_EXTENSIONS, PATTERNS)
    
    # Merge issues
    all_issues = defaultdict(list)
    for category in PATTERNS.keys():
        all_issues[category] = backend_issues.get(category, []) + frontend_issues.get(category, [])
    
    print("Analyzing configuration...")
    config_issues = analyze_configuration()
    
    print("Analyzing startup sequence...")
    startup_issues = analyze_startup_sequence()
    
    print("Generating report...")
    report = generate_report(dict(all_issues), config_issues, startup_issues)
    
    # Save report
    report_file = PROJECT_ROOT / "docs" / "11-12" / "PRODUCTION_READINESS_AUDIT_REPORT.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print()
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Critical Issues: {report['summary']['critical']}")
    print(f"High Priority: {report['summary']['high']}")
    print(f"Medium Priority: {report['summary']['medium']}")
    print(f"Low Priority: {report['summary']['low']}")
    print(f"Total Issues: {report['summary']['total']}")
    print()
    print("Raw Pattern Matches:")
    for category, count in report['raw_counts'].items():
        print(f"  {category}: {count}")
    print()
    print(f"Report saved to: {report_file}")
    print()
    
    # Print top critical issues
    if report['issues']['critical']:
        print("TOP CRITICAL ISSUES:")
        for i, issue in enumerate(report['issues']['critical'][:10], 1):
            print(f"{i}. {issue['file']}:{issue['line']} - {issue['category']}")
            print(f"   {issue['content'][:80]}...")
        print()
    
    return report


if __name__ == "__main__":
    main()



