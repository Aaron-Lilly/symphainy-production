#!/usr/bin/env python3
"""Phase 3 Configuration Test Script"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
frontend_root = project_root / "symphainy-frontend"
backend_root = project_root / "symphainy-platform"
ec2_ip = "35.215.64.103"

passed = []
failed = []
warnings = []

def log_pass(test_name, details=""):
    passed.append((test_name, details))
    print(f"✅ PASS: {test_name}")
    if details: print(f"   {details}")

def log_fail(test_name, details=""):
    failed.append((test_name, details))
    print(f"❌ FAIL: {test_name}")
    if details: print(f"   {details}")

def log_warn(test_name, details=""):
    warnings.append((test_name, details))
    print(f"⚠️  WARN: {test_name}")
    if details: print(f"   {details}")

print("=" * 70)
print("PHASE 3 CONFIGURATION TEST SUITE")
print("=" * 70)
print()

# Test 1: Frontend next.config.js
print("Testing Frontend Configuration...")
print("-" * 70)
config_path = frontend_root / "next.config.js"
if config_path.exists():
    content = config_path.read_text()
    if f"http://{ec2_ip}:8000" in content:
        log_pass("next.config.js EC2 default", f"Found {ec2_ip}:8000")
    else:
        log_fail("next.config.js EC2 default", "EC2 IP not found")
else:
    log_fail("next.config.js", "File not found")

# Test 2: Frontend package.json
package_path = frontend_root / "package.json"
if package_path.exists():
    content = package_path.read_text()
    if "HOSTNAME=0.0.0.0" in content:
        log_pass("package.json start script", "Binds to 0.0.0.0:3000")
    else:
        log_fail("package.json start script", "Does not bind to 0.0.0.0")
else:
    log_fail("package.json", "File not found")

# Test 3: Frontend service files
service_dir = frontend_root / "shared" / "services"
if service_dir.exists():
    service_files = list(service_dir.rglob("*.ts"))
    ec2_count = sum(1 for f in service_files if f"http://{ec2_ip}:8000" in f.read_text())
    if ec2_count > 0:
        log_pass("Service files EC2 defaults", f"{ec2_count} files use EC2 IP")
    else:
        log_fail("Service files EC2 defaults", "No files found with EC2 IP")
else:
    log_warn("Service files", "Directory not found")

print()

# Test 4: Backend production.env
print("Testing Backend Configuration...")
print("-" * 70)
env_path = backend_root / "config" / "production.env"
if env_path.exists():
    content = env_path.read_text()
    checks = {
        "EC2 pattern": "EC2 DEPLOYMENT" in content or "EC2 deployment" in content,
        "Option C migration": "OPTION C" in content or "Option C" in content,
        "Env var pattern": "${DATABASE_HOST:-localhost}" in content,
        "API_HOST 0.0.0.0": "API_HOST=${API_HOST:-0.0.0.0}" in content or "API_HOST=0.0.0.0" in content,
    }
    if all(checks.values()):
        log_pass("production.env EC2 pattern", "All checks passed")
    else:
        missing = [k for k, v in checks.items() if not v]
        log_fail("production.env EC2 pattern", f"Missing: {', '.join(missing)}")
else:
    log_fail("production.env", "File not found")

# Test 5: Backend main.py fail-fast
main_path = backend_root / "main.py"
if main_path.exists():
    content = main_path.read_text()
    if "RuntimeError" in content and "API router registration failed" in content:
        log_pass("main.py API router fail-fast", "Fails fast on registration error")
    else:
        log_warn("main.py API router", "Could not verify fail-fast pattern")
else:
    log_fail("main.py", "File not found")

# Test 6: Backend host binding
if main_path.exists():
    content = main_path.read_text()
    if 'default="0.0.0.0"' in content:
        log_pass("main.py host binding", "Defaults to 0.0.0.0")
    else:
        log_warn("main.py host binding", "Could not verify 0.0.0.0 default")

print()

# Test 7: Infrastructure health checks
print("Testing Infrastructure Health Checks...")
print("-" * 70)
script_path = backend_root / "scripts" / "start-infrastructure.sh"
if script_path.exists():
    content = script_path.read_text()
    if "OPA" in content and "8181/health" in content:
        log_pass("start-infrastructure.sh OPA check", "OPA health check found")
    else:
        log_warn("start-infrastructure.sh OPA check", "OPA check not found")
else:
    log_warn("start-infrastructure.sh", "File not found")

print()
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"✅ Passed: {len(passed)}")
print(f"❌ Failed: {len(failed)}")
print(f"⚠️  Warnings: {len(warnings)}")
print()

if failed:
    print("FAILED TESTS:")
    for test, details in failed:
        print(f"  - {test}: {details}")
    print()

if warnings:
    print("WARNINGS:")
    for test, details in warnings:
        print(f"  - {test}: {details}")
    print()

sys.exit(0 if len(failed) == 0 else 1)
