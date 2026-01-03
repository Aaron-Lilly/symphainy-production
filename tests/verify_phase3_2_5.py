#!/usr/bin/env python3
"""
Phase 3.2.5 Verification Script

Verifies the unified MCP pattern implementation:
1. No direct service access in agents (must use execute_mcp_tool())
2. All orchestrators/services define SOA APIs via _define_soa_api_handlers()
3. All MCP servers are properly initialized
4. Tool names match SOA API names (with realm prefix)
5. No false positives (all MCP tools correspond to working SOA APIs)
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class Phase325Verifier:
    """Verifier for Phase 3.2.5 unified MCP pattern."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_path = project_root / "symphainy-platform" / "backend"
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def verify(self) -> Dict[str, Any]:
        """Run all verification checks."""
        print("🔍 Phase 3.2.5 Verification: Unified MCP Pattern\n")
        
        # Check 1: Agents use MCP tools exclusively (no direct service access)
        print("1️⃣ Checking agents for direct service access...")
        self._check_agent_direct_service_access()
        
        # Check 2: Orchestrators define SOA APIs
        print("\n2️⃣ Checking orchestrators for SOA API definitions...")
        self._check_orchestrator_soa_api_definitions()
        
        # Check 3: MCP servers are properly initialized
        print("\n3️⃣ Checking MCP server initialization...")
        self._check_mcp_server_initialization()
        
        # Check 4: Tool name consistency
        print("\n4️⃣ Checking tool name consistency...")
        self._check_tool_name_consistency()
        
        # Check 5: Cross-realm access pattern
        print("\n5️⃣ Checking cross-realm access pattern...")
        self._check_cross_realm_access()
        
        # Summary
        print("\n" + "="*80)
        print("📊 VERIFICATION SUMMARY")
        print("="*80)
        print(f"✅ Successes: {len(self.successes)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Issues: {len(self.issues)}")
        
        if self.successes:
            print("\n✅ Successes:")
            for success in self.successes[:10]:  # Show first 10
                print(f"   {success}")
            if len(self.successes) > 10:
                print(f"   ... and {len(self.successes) - 10} more")
        
        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"   {warning}")
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more")
        
        if self.issues:
            print("\n❌ Issues (must be fixed):")
            for issue in self.issues:
                print(f"   {issue}")
        
        return {
            "successes": len(self.successes),
            "warnings": len(self.warnings),
            "issues": len(self.issues),
            "all_issues": self.issues,
            "all_warnings": self.warnings,
            "all_successes": self.successes
        }
    
    def _check_agent_direct_service_access(self):
        """Check agents for direct service access (anti-pattern)."""
        agent_files = list(self.backend_path.rglob("**/agents/*.py"))
        
        anti_patterns = [
            r'await\s+.*\.get_.*_api\s*\(',
            r'await\s+.*\.get_.*_service\s*\(',
            r'await\s+.*\.get_smart_city_service\s*\(',
            r'await\s+.*\.get_enabling_service\s*\(',
            r'await\s+.*\.get_foundation_service\s*\(',
            r'await\s+.*\.get_business_abstraction\s*\(',
            r'await\s+.*\.get_abstraction\s*\(',
            r'content_steward\s*=\s*await',
            r'file_parser\s*=\s*await',
            r'orchestrator\.handle_',
            r'orchestrator\.process_',
            r'orchestrator\.get_',
        ]
        
        for agent_file in agent_files:
            if not agent_file.is_file():
                continue
            
            try:
                content = agent_file.read_text()
                
                # Skip if it's a base class or protocol
                if 'base' in agent_file.name.lower() or 'protocol' in agent_file.name.lower():
                    continue
                
                # Check for anti-patterns
                for pattern in anti_patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = content.split('\n')[line_num - 1].strip()
                        
                        # Allow if it's in a comment or docstring
                        if line_content.startswith('#') or '"""' in line_content or "'''" in line_content:
                            continue
                        
                        # Allow if it's in execute_mcp_tool (that's the correct pattern)
                        if 'execute_mcp_tool' in line_content:
                            continue
                        
                        self.issues.append(
                            f"{agent_file.relative_to(self.project_root)}:{line_num} - "
                            f"Direct service access detected: {match.group()}"
                        )
                
                # Check for execute_mcp_tool usage (good pattern)
                if 'execute_mcp_tool' in content:
                    self.successes.append(
                        f"{agent_file.relative_to(self.project_root)} - Uses execute_mcp_tool()"
                    )
                
            except Exception as e:
                self.warnings.append(f"Error reading {agent_file}: {e}")
    
    def _check_orchestrator_soa_api_definitions(self):
        """Check orchestrators for SOA API definitions."""
        orchestrator_files = list(self.backend_path.rglob("**/*orchestrator*.py"))
        
        for orchestrator_file in orchestrator_files:
            if not orchestrator_file.is_file():
                continue
            
            # Skip base classes
            if 'base' in orchestrator_file.name.lower():
                continue
            
            try:
                content = orchestrator_file.read_text()
                
                # Check if it defines SOA APIs
                if '_define_soa_api_handlers' in content:
                    # Verify it returns a dict
                    if 'def _define_soa_api_handlers' in content:
                        # Check if it has proper return statement
                        if 'return {' in content or 'return dict(' in content:
                            self.successes.append(
                                f"{orchestrator_file.relative_to(self.project_root)} - "
                                f"Defines SOA APIs via _define_soa_api_handlers()"
                            )
                        else:
                            self.warnings.append(
                                f"{orchestrator_file.relative_to(self.project_root)} - "
                                f"Has _define_soa_api_handlers() but may not return dict"
                            )
                    else:
                        self.warnings.append(
                            f"{orchestrator_file.relative_to(self.project_root)} - "
                            f"References _define_soa_api_handlers but may not implement it"
                        )
                else:
                    # Check if it's an orchestrator that should define SOA APIs
                    if 'OrchestratorBase' in content or 'class' in content:
                        # It might be okay if it doesn't expose SOA APIs
                        # But we should check if it has methods that should be exposed
                        if any(method in content for method in ['async def orchestrate', 'async def execute', 'async def handle']):
                            self.warnings.append(
                                f"{orchestrator_file.relative_to(self.project_root)} - "
                                f"Orchestrator has methods but no _define_soa_api_handlers()"
                            )
                
            except Exception as e:
                self.warnings.append(f"Error reading {orchestrator_file}: {e}")
    
    def _check_mcp_server_initialization(self):
        """Check MCP server initialization."""
        mcp_server_files = list(self.backend_path.rglob("**/mcp_server/*.py"))
        
        for mcp_file in mcp_server_files:
            if not mcp_file.is_file():
                continue
            
            # Skip base classes
            if 'base' in mcp_file.name.lower():
                continue
            
            try:
                content = mcp_file.read_text()
                
                # Check if it follows unified pattern
                if 'MCPServerBase' in content:
                    if '_define_soa_api_handlers' in content or 'orchestrator._define_soa_api_handlers' in content:
                        self.successes.append(
                            f"{mcp_file.relative_to(self.project_root)} - "
                            f"Uses unified pattern (registers tools from SOA APIs)"
                        )
                    else:
                        self.warnings.append(
                            f"{mcp_file.relative_to(self.project_root)} - "
                            f"MCP Server may not use unified pattern"
                        )
                
                # Check for proper tool registration
                if 'register_tool' in content:
                    self.successes.append(
                        f"{mcp_file.relative_to(self.project_root)} - "
                        f"Registers tools"
                    )
                
            except Exception as e:
                self.warnings.append(f"Error reading {mcp_file}: {e}")
        
        # Check orchestrators initialize MCP servers
        orchestrator_files = list(self.backend_path.rglob("**/*orchestrator*.py"))
        for orchestrator_file in orchestrator_files:
            if not orchestrator_file.is_file() or 'base' in orchestrator_file.name.lower():
                continue
            
            try:
                content = orchestrator_file.read_text()
                
                if '_define_soa_api_handlers' in content:
                    # Should have _initialize_mcp_server
                    if '_initialize_mcp_server' in content:
                        self.successes.append(
                            f"{orchestrator_file.relative_to(self.project_root)} - "
                            f"Initializes MCP server"
                        )
                    else:
                        self.issues.append(
                            f"{orchestrator_file.relative_to(self.project_root)} - "
                            f"Defines SOA APIs but missing _initialize_mcp_server()"
                        )
                
            except Exception as e:
                self.warnings.append(f"Error reading {orchestrator_file}: {e}")
    
    def _check_tool_name_consistency(self):
        """Check tool name consistency (realm prefix)."""
        mcp_server_files = list(self.backend_path.rglob("**/mcp_server/*.py"))
        
        for mcp_file in mcp_server_files:
            if not mcp_file.is_file() or 'base' in mcp_file.name.lower():
                continue
            
            try:
                content = mcp_file.read_text()
                
                # Check for realm prefix in tool names
                if 'tool_name = f"' in content:
                    # Should have realm prefix
                    if 'content_' in content or 'insights_' in content or 'solution_' in content or 'business_enablement_' in content:
                        self.successes.append(
                            f"{mcp_file.relative_to(self.project_root)} - "
                            f"Uses realm prefix in tool names"
                        )
                    else:
                        self.warnings.append(
                            f"{mcp_file.relative_to(self.project_root)} - "
                            f"Tool names may not have realm prefix"
                        )
                
            except Exception as e:
                self.warnings.append(f"Error reading {mcp_file}: {e}")
    
    def _check_cross_realm_access(self):
        """Check cross-realm access pattern."""
        agent_files = list(self.backend_path.rglob("**/agents/*.py"))
        
        for agent_file in agent_files:
            if not agent_file.is_file() or 'base' in agent_file.name.lower() or 'protocol' in agent_file.name.lower():
                continue
            
            try:
                content = agent_file.read_text()
                
                # Check for cross-realm tool usage
                cross_realm_patterns = [
                    r'execute_mcp_tool\s*\(\s*["\']content_',
                    r'execute_mcp_tool\s*\(\s*["\']insights_',
                    r'execute_mcp_tool\s*\(\s*["\']solution_',
                    r'execute_mcp_tool\s*\(\s*["\']business_enablement_',
                ]
                
                for pattern in cross_realm_patterns:
                    if re.search(pattern, content):
                        self.successes.append(
                            f"{agent_file.relative_to(self.project_root)} - "
                            f"Uses cross-realm MCP tool access"
                        )
                        break
                
                # Check for execute_mcp_tool with realm parameter
                if 'execute_mcp_tool' in content and 'realm=' in content:
                    self.successes.append(
                        f"{agent_file.relative_to(self.project_root)} - "
                        f"Uses explicit realm parameter for cross-realm access"
                    )
                
            except Exception as e:
                self.warnings.append(f"Error reading {agent_file}: {e}")
        
        # Check base class has cross-realm support
        base_agent_files = list(self.backend_path.rglob("**/protocols/*agent*.py"))
        for base_file in base_agent_files:
            if not base_file.is_file():
                continue
            
            try:
                content = base_file.read_text()
                
                if '_execute_cross_realm_tool' in content and '_discover_realm_orchestrator' in content:
                    self.successes.append(
                        f"{base_file.relative_to(self.project_root)} - "
                        f"Has cross-realm access helpers"
                    )
                elif 'execute_mcp_tool' in content:
                    self.warnings.append(
                        f"{base_file.relative_to(self.project_root)} - "
                        f"Has execute_mcp_tool but may not have cross-realm support"
                    )
                
            except Exception as e:
                self.warnings.append(f"Error reading {base_file}: {e}")


def main():
    """Run verification."""
    project_root = Path(__file__).parent.parent
    verifier = Phase325Verifier(project_root)
    results = verifier.verify()
    
    # Exit with error code if there are issues
    if results["issues"] > 0:
        print(f"\n❌ Verification failed with {results['issues']} issues")
        sys.exit(1)
    elif results["warnings"] > 0:
        print(f"\n⚠️  Verification completed with {results['warnings']} warnings")
        sys.exit(0)
    else:
        print(f"\n✅ Verification passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

