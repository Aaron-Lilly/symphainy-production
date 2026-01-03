#!/usr/bin/env python3
"""
Code Quality Markers Audit Script

Audits and categorizes TODO/FIXME/XXX/HACK/PLACEHOLDER/STUB markers in the active codebase.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class Marker:
    """Represents a code quality marker."""
    file: str
    line: int
    marker_type: str
    content: str
    category: str = "UNKNOWN"
    priority: str = "MEDIUM"
    description: str = ""

class MarkerAuditor:
    """Audit code quality markers."""
    
    MARKER_PATTERNS = {
        "TODO": r"TODO[:\s]*(.+)",
        "FIXME": r"FIXME[:\s]*(.+)",
        "XXX": r"XXX[:\s]*(.+)",
        "HACK": r"HACK[:\s]*(.+)",
        "PLACEHOLDER": r"PLACEHOLDER[:\s]*(.+)",
        "STUB": r"STUB[:\s]*(.+)",
    }
    
    CRITICAL_KEYWORDS = [
        "security", "vulnerability", "bug", "crash", "error", "fail",
        "incomplete", "missing", "broken", "temporary", "temp", "hack",
        "fix", "critical", "urgent", "must", "required"
    ]
    
    ENHANCEMENT_KEYWORDS = [
        "enhancement", "improve", "optimize", "performance", "feature",
        "future", "later", "nice to have", "consider", "could"
    ]
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.markers: List[Marker] = []
        self.exclude_dirs = {"archive", "__pycache__", "business_enablement_old", ".git", "node_modules"}
    
    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from audit."""
        parts = file_path.parts
        return any(excluded in parts for excluded in self.exclude_dirs)
    
    def categorize_marker(self, marker: Marker) -> Tuple[str, str]:
        """Categorize a marker based on its content."""
        content_lower = marker.content.lower()
        
        # Check for critical keywords
        if any(keyword in content_lower for keyword in self.CRITICAL_KEYWORDS):
            return "CRITICAL", "HIGH"
        
        # Check for enhancement keywords
        if any(keyword in content_lower for keyword in self.ENHANCEMENT_KEYWORDS):
            return "ENHANCEMENT", "LOW"
        
        # Check for documentation markers
        if any(word in content_lower for word in ["document", "comment", "clarify", "explain"]):
            return "DOCUMENTATION", "LOW"
        
        # Default based on marker type
        if marker.marker_type in ["FIXME", "HACK", "XXX"]:
            return "CRITICAL", "HIGH"
        elif marker.marker_type == "STUB":
            return "CRITICAL", "HIGH"
        elif marker.marker_type == "PLACEHOLDER":
            return "ENHANCEMENT", "MEDIUM"
        else:  # TODO
            return "ENHANCEMENT", "MEDIUM"
    
    def audit_file(self, file_path: Path) -> List[Marker]:
        """Audit a single file for markers."""
        markers = []
        relative_path = file_path.relative_to(self.base_path)
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"⚠️  Could not read {relative_path}: {e}")
            return []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # Check for each marker type
            for marker_type, pattern in self.MARKER_PATTERNS.items():
                # Case-insensitive search
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    marker_content = match.group(1).strip() if match.groups() else ""
                    
                    marker = Marker(
                        file=str(relative_path),
                        line=line_num,
                        marker_type=marker_type,
                        content=marker_content
                    )
                    
                    # Categorize
                    category, priority = self.categorize_marker(marker)
                    marker.category = category
                    marker.priority = priority
                    marker.description = marker_content
                    
                    markers.append(marker)
        
        return markers
    
    def audit_directory(self, directory: Path, pattern: str = "*.py") -> List[Marker]:
        """Audit all files in a directory."""
        all_markers = []
        
        for file_path in directory.rglob(pattern):
            if self.should_exclude(file_path):
                continue
            
            markers = self.audit_file(file_path)
            all_markers.extend(markers)
        
        return all_markers
    
    def generate_report(self) -> str:
        """Generate audit report."""
        report = []
        report.append("=" * 80)
        report.append("CODE QUALITY MARKERS AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total = len(self.markers)
        by_category = defaultdict(int)
        by_type = defaultdict(int)
        by_priority = defaultdict(int)
        
        for marker in self.markers:
            by_category[marker.category] += 1
            by_type[marker.marker_type] += 1
            by_priority[marker.priority] += 1
        
        report.append("SUMMARY")
        report.append("-" * 80)
        report.append(f"Total Markers: {total}")
        report.append("")
        
        report.append("By Category:")
        for category, count in sorted(by_category.items()):
            report.append(f"  {category}: {count}")
        report.append("")
        
        report.append("By Type:")
        for marker_type, count in sorted(by_type.items()):
            report.append(f"  {marker_type}: {count}")
        report.append("")
        
        report.append("By Priority:")
        for priority, count in sorted(by_priority.items()):
            report.append(f"  {priority}: {count}")
        report.append("")
        
        # Critical Markers
        critical_markers = [m for m in self.markers if m.category == "CRITICAL"]
        if critical_markers:
            report.append("CRITICAL MARKERS (Must Address)")
            report.append("-" * 80)
            for marker in sorted(critical_markers, key=lambda x: (x.file, x.line))[:50]:  # Limit to first 50
                report.append(f"  {marker.file}:{marker.line}")
                report.append(f"    Type: {marker.marker_type}")
                report.append(f"    Priority: {marker.priority}")
                report.append(f"    Content: {marker.content[:100]}")
                report.append("")
        
        # Enhancement Markers (Sample)
        enhancement_markers = [m for m in self.markers if m.category == "ENHANCEMENT"]
        if enhancement_markers:
            report.append("ENHANCEMENT MARKERS (Sample - First 20)")
            report.append("-" * 80)
            for marker in sorted(enhancement_markers, key=lambda x: (x.file, x.line))[:20]:
                report.append(f"  {marker.file}:{marker.line} - {marker.content[:80]}")
            report.append("")
        
        # Documentation Markers (Sample)
        doc_markers = [m for m in self.markers if m.category == "DOCUMENTATION"]
        if doc_markers:
            report.append(f"DOCUMENTATION MARKERS ({len(doc_markers)} total)")
            report.append("-" * 80)
            report.append(f"  {len(doc_markers)} markers need documentation updates")
            report.append("")
        
        report.append("=" * 80)
        return "\n".join(report)
    
    def generate_markdown_report(self) -> str:
        """Generate markdown-formatted report."""
        report = []
        report.append("# Code Quality Markers Audit Report")
        report.append("")
        report.append(f"**Date:** {Path(__file__).stat().st_mtime}")
        report.append(f"**Total Markers Found:** {len(self.markers)}")
        report.append("")
        
        # Summary Statistics
        by_category = defaultdict(int)
        by_type = defaultdict(int)
        by_priority = defaultdict(int)
        
        for marker in self.markers:
            by_category[marker.category] += 1
            by_type[marker.marker_type] += 1
            by_priority[marker.priority] += 1
        
        report.append("## Summary Statistics")
        report.append("")
        report.append("| Category | Count |")
        report.append("|----------|-------|")
        for category, count in sorted(by_category.items()):
            report.append(f"| {category} | {count} |")
        report.append("")
        
        report.append("| Marker Type | Count |")
        report.append("|-------------|-------|")
        for marker_type, count in sorted(by_type.items()):
            report.append(f"| {marker_type} | {count} |")
        report.append("")
        
        report.append("| Priority | Count |")
        report.append("|----------|-------|")
        for priority, count in sorted(by_priority.items()):
            report.append(f"| {priority} | {count} |")
        report.append("")
        
        # Critical Markers
        critical_markers = [m for m in self.markers if m.category == "CRITICAL"]
        if critical_markers:
            report.append("## Critical Markers (Must Address)")
            report.append("")
            report.append(f"**Total:** {len(critical_markers)}")
            report.append("")
            report.append("| File | Line | Type | Priority | Description |")
            report.append("|------|------|------|----------|-------------|")
            for marker in sorted(critical_markers, key=lambda x: (x.file, x.line)):
                description = marker.content[:60].replace("|", "\\|") if marker.content else ""
                report.append(f"| `{marker.file}` | {marker.line} | {marker.marker_type} | {marker.priority} | {description} |")
            report.append("")
        
        # Enhancement Markers
        enhancement_markers = [m for m in self.markers if m.category == "ENHANCEMENT"]
        if enhancement_markers:
            report.append("## Enhancement Markers")
            report.append("")
            report.append(f"**Total:** {len(enhancement_markers)}")
            report.append("")
            report.append("| File | Line | Type | Description |")
            report.append("|------|------|------|-------------|")
            for marker in sorted(enhancement_markers, key=lambda x: (x.file, x.line))[:50]:  # Limit to first 50
                description = marker.content[:60].replace("|", "\\|") if marker.content else ""
                report.append(f"| `{marker.file}` | {marker.line} | {marker.marker_type} | {description} |")
            report.append("")
        
        # Documentation Markers
        doc_markers = [m for m in self.markers if m.category == "DOCUMENTATION"]
        if doc_markers:
            report.append("## Documentation Markers")
            report.append("")
            report.append(f"**Total:** {len(doc_markers)}")
            report.append("")
            report.append("These markers indicate areas where documentation or comments need clarification.")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main audit function."""
    base_path = Path(__file__).parent.parent.parent
    
    auditor = MarkerAuditor(base_path)
    
    print("Auditing code quality markers...")
    print("")
    
    # Audit key directories
    directories = [
        base_path / "symphainy-platform" / "backend",
        base_path / "symphainy-platform" / "foundations",
        base_path / "symphainy-platform" / "bases",
    ]
    
    for directory in directories:
        if directory.exists():
            print(f"Auditing {directory.relative_to(base_path)}...")
            markers = auditor.audit_directory(directory)
            auditor.markers.extend(markers)
            print(f"  Found {len(markers)} markers")
    
    print("")
    print(f"Total markers found: {len(auditor.markers)}")
    print("")
    
    # Generate reports
    print("Generating reports...")
    
    # Text report
    text_report = auditor.generate_report()
    print(text_report)
    
    # Markdown report
    md_report = auditor.generate_markdown_report()
    report_path = base_path / "docs" / "final_production_docs" / "CODE_QUALITY_MARKERS.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(md_report, encoding='utf-8')
    print(f"\nMarkdown report saved to: {report_path}")
    
    # Summary
    critical_count = len([m for m in auditor.markers if m.category == "CRITICAL"])
    enhancement_count = len([m for m in auditor.markers if m.category == "ENHANCEMENT"])
    doc_count = len([m for m in auditor.markers if m.category == "DOCUMENTATION"])
    
    print("")
    print("=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Total Markers: {len(auditor.markers)}")
    print(f"Critical: {critical_count}")
    print(f"Enhancement: {enhancement_count}")
    print(f"Documentation: {doc_count}")
    print("=" * 80)
    
    return 0 if critical_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

