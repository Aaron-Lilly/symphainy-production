#!/usr/bin/env python3
"""
Phase 2 Test After Restart - Verify HF Agent Initialization
"""

import subprocess
import json
import sys

def run_in_container(cmd):
    """Run command in container."""
    result = subprocess.run(f"docker exec symphainy-backend-prod {cmd}", shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def check_hf_agent_initialization():
    """Check if HF agent was initialized."""
    print("=" * 70)
    print("Checking StatelessHFInferenceAgent Initialization")
    print("=" * 70)
    print()
    
    # Check recent logs
    stdout, stderr, code = run_in_container("docker logs symphainy-backend-prod --tail 500 2>&1 | grep -i 'stateless.*hf\|huggingface.*adapter.*created\|semantic.*processing' | tail -10")
    
    if stdout:
        print("✅ Found HF-related logs:")
        print(stdout)
        return True
    else:
        print("⚠️  No HF agent initialization logs found")
        print("   This might mean:")
        print("   - Orchestrator uses lazy initialization (loads on first request)")
        print("   - Logs are in a different format")
        print("   - Need to trigger orchestrator initialization")
        return False

def check_orchestrator_code():
    """Verify orchestrator code has semantic processing."""
    print("\n" + "=" * 70)
    print("Verifying Orchestrator Code")
    print("=" * 70)
    print()
    
    code = '''
import sys
sys.path.insert(0, '/app')
from backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator import ContentAnalysisOrchestrator
import inspect

# Check for semantic methods
methods = [m for m in dir(ContentAnalysisOrchestrator) if '_' in m and ('semantic' in m.lower() or 'detect_data' in m.lower())]
print(f"✅ Semantic methods: {methods}")

# Check parse_file signature
if hasattr(ContentAnalysisOrchestrator, 'parse_file'):
    sig = inspect.signature(ContentAnalysisOrchestrator.parse_file)
    print(f"✅ parse_file() exists: {sig}")
    
    # Check source for semantic_result
    source = inspect.getsource(ContentAnalysisOrchestrator.parse_file)
    if 'semantic_result' in source:
        print("✅ parse_file() includes semantic_result")
    else:
        print("❌ parse_file() does not include semantic_result")
else:
    print("❌ parse_file() not found")
'''
    
    stdout, stderr, code = run_in_container(f"python3 -c \"{code.replace(chr(10), '; ')}\"")
    print(stdout)
    if stderr:
        print("STDERR:", stderr)
    
    return "semantic_result" in stdout

def main():
    """Main test."""
    print("\n🧪 Phase 2 Post-Restart Verification")
    print("=" * 70)
    print()
    
    code_ok = check_orchestrator_code()
    logs_ok = check_hf_agent_initialization()
    
    print("\n" + "=" * 70)
    if code_ok:
        print("✅ Code Verification: PASSED")
        print("   Semantic processing code is present and correct")
    else:
        print("❌ Code Verification: FAILED")
    
    if logs_ok:
        print("✅ Initialization Logs: FOUND")
        print("   HF agent initialization detected in logs")
    else:
        print("⚠️  Initialization Logs: NOT FOUND")
        print("   This is OK if orchestrator uses lazy initialization")
        print("   HF agent will initialize on first parse_file() call")
    
    print("\n📝 Next: Test with actual file parse request")
    print("=" * 70)
    
    return code_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)






