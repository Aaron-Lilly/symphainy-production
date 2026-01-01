#!/usr/bin/env python3
"""
Platform-Wide Patterns Audit Script

This script audits the entire platform for compliance with architectural patterns.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

@dataclass
class AuditFinding:
    pattern: str
    severity: str
    file_path: str
    line_number: int
    code_snippet: str
    message: str
    recommendation: str

class PlatformPatternAuditor:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.findings: List[AuditFinding] = []
        self.stats = defaultdict(int)
        
        self.source_dirs = [
            project_root / "symphainy-platform" / "backend",
            project_root / "symphainy-platform" / "foundations",
            project_root / "symphainy-platform" / "platform_infrastructure",
            project_root / "symphainy-platform" / "bases",
            project_root / "symphainy-platform" / "utilities",
        ]
        
        self.exclude_patterns = [
            "**/__pycache__/**",
            "**/tests/**",
            "**/test_*.py",
            "**/*_test.py",
        ]
    
    def find_python_files(self) -> List[Path]:
        python_files = []
        for source_dir in self.source_dirs:
            if not source_dir.exists():
                continue
            for py_file in source_dir.rglob("*.py"):
                if any(py_file.match(pattern) for pattern in self.exclude_patterns):
                    continue
                python_files.append(py_file)
        return python_files
    
    def read_file_safe(self, file_path: Path) -> str:
        try:
            return file_path.read_text(encoding='utf-8')
        except:
            return ""
    
    def add_finding(self, pattern: str, severity: str, file_path: str, 
                   line_number: int, code_snippet: str, message: str, 
                   recommendation: str):
        finding = AuditFinding(
            pattern=pattern, severity=severity, file_path=str(file_path),
            line_number=line_number, code_snippet=code_snippet,
            message=message, recommendation=recommendation
        )
        self.findings.append(finding)
        self.stats[f"{pattern}_{severity}"] += 1
        self.stats[severity] += 1
    
    def audit_all(self):
        print("🔍 Starting comprehensive platform audit...")
        print("=" * 80)
        
        python_files = self.find_python_files()
        print(f"📁 Found {len(python_files)} Python files to audit\n")
        
        # Pattern 1: RealmServiceBase Usage
        print("📋 Pattern 1: RealmServiceBase Usage")
        self.audit_realm_service_base_usage(python_files)
        
        # Pattern 2: Smart City Service Delegation
        print("\n📋 Pattern 2: Smart City Service Delegation")
        self.audit_smart_city_delegation(python_files)
        
        # Pattern 3: Public Works Abstraction Access
        print("\n📋 Pattern 3: Public Works Abstraction Access")
        self.audit_abstraction_access(python_files)
        
        # Pattern 4: Method Signature Alignment
        print("\n📋 Pattern 4: Method Signature Alignment")
        self.audit_method_signatures(python_files)
        
        # Pattern 6: Public Works Foundation Creation Pattern
        print("\n📋 Pattern 6: Public Works Foundation Creation Pattern")
        self.audit_public_works_patterns(python_files)
        
        # Pattern 8: Protocol Migration
        print("\n📋 Pattern 8: Protocol Migration")
        self.audit_protocol_migration()
        
        # Pattern 9: Adapter Encapsulation
        print("\n📋 Pattern 9: Adapter Encapsulation")
        self.audit_adapter_encapsulation(python_files)
        
        # Pattern 10: Service Discovery Registry
        print("\n📋 Pattern 10: Service Discovery Registry Pattern")
        self.audit_service_discovery_registry()
        
        return self.generate_report()
    
    def audit_realm_service_base_usage(self, python_files: List[Path]):
        for file_path in python_files:
            content = self.read_file_safe(file_path)
            if not content:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if re.search(r'self\.di_container\.get_abstraction\(', line):
                    self.add_finding(
                        "RealmServiceBase Usage", "error",
                        file_path.relative_to(self.project_root), i, line.strip(),
                        "Direct di_container.get_abstraction() call",
                        "Use self.get_abstraction() instead"
                    )
                if re.search(r'self\.communication_foundation\.', line):
                    self.add_finding(
                        "RealmServiceBase Usage", "error",
                        file_path.relative_to(self.project_root), i, line.strip(),
                        "Direct communication_foundation access",
                        "Use Smart City services instead"
                    )
        print(f"  ✅ Scanned {len(python_files)} files")
    
    def audit_smart_city_delegation(self, python_files: List[Path]):
        for file_path in python_files:
            content = self.read_file_safe(file_path)
            if not content:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if re.search(r'\bopen\(', line) and 'test' not in str(file_path).lower():
                    if 'with open' in line or 'as f' in line:
                        continue
                    self.add_finding(
                        "Smart City Service Delegation", "warning",
                        file_path.relative_to(self.project_root), i, line.strip(),
                        "Custom file I/O found",
                        "Use RealmServiceBase.store_document()"
                    )
        print(f"  ✅ Scanned {len(python_files)} files")
    
    def audit_abstraction_access(self, python_files: List[Path]):
        direct_imports = [
            r'^import redis\b', r'^import httpx\b', r'^import boto3\b',
            r'^import meilisearch\b', r'^from meilisearch import',
            r'^import consul\b',
        ]
        for file_path in python_files:
            content = self.read_file_safe(file_path)
            if not content:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern in direct_imports:
                    if re.search(pattern, line):
                        if 'adapter' in str(file_path).lower() and 'infrastructure_adapters' in str(file_path):
                            continue
                        self.add_finding(
                            "Public Works Abstraction Access", "error",
                            file_path.relative_to(self.project_root), i, line.strip(),
                            f"Direct library import: {line.strip()}",
                            "Use abstractions via Platform Gateway"
                        )
                if re.search(r'=.*Adapter\(', line) and 'self.' in line:
                    if 'public_works_foundation_service.py' in str(file_path) and '_create_all_adapters' in content:
                        continue
                    if 'test' in str(file_path).lower():
                        continue
                    self.add_finding(
                        "Public Works Abstraction Access", "error",
                        file_path.relative_to(self.project_root), i, line.strip(),
                        "Direct adapter instantiation",
                        "Get abstraction via Platform Gateway"
                    )
        print(f"  ✅ Scanned {len(python_files)} files")
    
    def audit_method_signatures(self, python_files: List[Path]):
        incorrect_calls = [
            (r'librarian\.store_document\(', 'content_steward.process_upload()'),
            (r'librarian\.search_documents\(', 'librarian.search_knowledge()'),
            (r'data_steward\.validate_data\(', 'data_steward.validate_schema()'),
        ]
        for file_path in python_files:
            content = self.read_file_safe(file_path)
            if not content:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern, correct in incorrect_calls:
                    if re.search(pattern, line):
                        self.add_finding(
                            "Method Signature Alignment", "error",
                            file_path.relative_to(self.project_root), i, line.strip(),
                            f"Incorrect method call: {pattern}",
                            f"Use {correct} instead"
                        )
        print(f"  ✅ Scanned {len(python_files)} files")
    
    def audit_public_works_patterns(self, python_files: List[Path]):
        for file_path in python_files:
            content = self.read_file_safe(file_path)
            if not content:
                continue
            if 'registry' in str(file_path).lower() and 'infrastructure_registry' in str(file_path):
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if re.search(r'def build_infrastructure|async def build_infrastructure', line):
                        self.add_finding(
                            "Public Works Foundation Creation Pattern", "error",
                            file_path.relative_to(self.project_root), i, line.strip(),
                            "Registry has build_infrastructure()",
                            "Remove - registries should only expose"
                        )
        print(f"  ✅ Scanned {len(python_files)} files")
    
    def audit_protocol_migration(self):
        protocol_dir = self.project_root / "symphainy-platform" / "foundations" / "public_works_foundation" / "abstraction_contracts"
        if not protocol_dir.exists():
            print(f"  ⚠️  Protocol directory not found")
            return
        for protocol_file in protocol_dir.glob("*_protocol.py"):
            content = self.read_file_safe(protocol_file)
            if 'from abc import ABC' in content or 'import abc' in content:
                for i, line in enumerate(content.split('\n'), 1):
                    if 'ABC' in line or 'abstractmethod' in line:
                        self.add_finding(
                            "Protocol Migration", "warning",
                            protocol_file.relative_to(self.project_root), i, line.strip(),
                            "Protocol file uses abc.ABC",
                            "Migrate to typing.Protocol"
                        )
                        break
        print(f"  ✅ Scanned protocol files")
    
    def audit_adapter_encapsulation(self, python_files: List[Path]):
        for file_path in python_files:
            if 'infrastructure_adapters' in str(file_path):
                continue
            content = self.read_file_safe(file_path)
            if not content:
                continue
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if re.search(r'\.client\.', line) and 'self._client' not in line:
                    self.add_finding(
                        "Adapter Encapsulation", "error",
                        file_path.relative_to(self.project_root), i, line.strip(),
                        "Direct .client access",
                        "Use adapter wrapper methods"
                    )
        print(f"  ✅ Scanned files")
    
    def audit_service_discovery_registry(self):
        registry_file = self.project_root / "symphainy-platform" / "foundations" / "public_works_foundation" / "infrastructure_registry" / "service_discovery_registry.py"
        if not registry_file.exists():
            return
        content = self.read_file_safe(registry_file)
        if 'build_infrastructure' in content:
            for i, line in enumerate(content.split('\n'), 1):
                if 'build_infrastructure' in line:
                    self.add_finding(
                        "Service Discovery Registry Pattern", "error",
                        registry_file.relative_to(self.project_root), i, line.strip(),
                        "ServiceDiscoveryRegistry has build_infrastructure()",
                        "Remove - should be exposure-only"
                    )
                    break
        print(f"  ✅ Audited ServiceDiscoveryRegistry")
    
    def generate_report(self):
        by_pattern = defaultdict(list)
        by_severity = defaultdict(list)
        by_file = defaultdict(list)
        for finding in self.findings:
            by_pattern[finding.pattern].append(finding)
            by_severity[finding.severity].append(finding)
            by_file[finding.file_path].append(finding)
        return {
            'total_findings': len(self.findings),
            'by_pattern': {k: len(v) for k, v in by_pattern.items()},
            'by_severity': {k: len(v) for k, v in by_severity.items()},
            'by_file': {k: len(v) for k, v in by_file.items()},
            'findings': [asdict(f) for f in self.findings],
            'stats': dict(self.stats)
        }

if __name__ == '__main__':
    auditor = PlatformPatternAuditor(PROJECT_ROOT)
    report = auditor.audit_all()
    
    print("\n" + "=" * 80)
    print("📊 AUDIT SUMMARY")
    print("=" * 80)
    print(f"\nTotal Findings: {report['total_findings']}")
    print(f"\nBy Severity:")
    for severity, count in report['by_severity'].items():
        print(f"  {severity.upper()}: {count}")
    print(f"\nBy Pattern:")
    for pattern, count in report['by_pattern'].items():
        print(f"  {pattern}: {count}")
    
    output_path = PROJECT_ROOT / "docs" / "11-12" / "AUDIT_REPORT.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2))
    print(f"\n✅ Report saved to {output_path}")
    
    if report['by_severity'].get('error', 0) > 0:
        sys.exit(1)
