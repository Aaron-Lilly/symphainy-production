# Security Testing Guide

**Last Updated:** December 1, 2025  
**Version:** 2.0 (Post-Phase 1-4 Improvements)

---

## Overview

This guide explains security testing practices for the SymphAIny platform. Security tests ensure the platform is protected against common vulnerabilities and security threats.

---

## Security Testing Types

### 1. Vulnerability Scanning

**Automated scanning for known vulnerabilities:**

```bash
# Python dependencies
cd symphainy-platform
safety check
pip-audit --desc

# Frontend dependencies
cd symphainy-frontend
npm audit --audit-level=moderate
```

**CI/CD Integration:**
- ✅ Runs automatically in quality gates
- ✅ Blocks deployment if vulnerabilities found
- ✅ Reports uploaded as artifacts

---

### 2. Code Security Scanning

**Bandit - Python security linter:**

```bash
# Run Bandit scan
cd symphainy-platform
bandit -r . -ll

# Generate JSON report
bandit -r . -f json -o bandit-report.json
```

**Common Issues Found:**
- Hardcoded passwords
- SQL injection risks
- Insecure random number generation
- Use of insecure functions

**CI/CD Integration:**
- ✅ Runs automatically in quality gates
- ✅ Non-blocking (warnings)
- ✅ Reports uploaded as artifacts

---

### 3. Authentication & Authorization Tests

**Test authentication flows:**

```python
# tests/security/test_authentication.py
import pytest
import httpx

@pytest.mark.security
async def test_authentication_required():
    """Test that protected endpoints require authentication."""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/v1/protected")
        assert response.status_code == 401  # Unauthorized

@pytest.mark.security
async def test_authentication_with_token():
    """Test authentication with valid token."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {valid_token}"}
        response = await client.get(
            "http://localhost:8000/api/v1/protected",
            headers=headers
        )
        assert response.status_code == 200

@pytest.mark.security
async def test_authentication_invalid_token():
    """Test authentication with invalid token."""
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get(
            "http://localhost:8000/api/v1/protected",
            headers=headers
        )
        assert response.status_code == 401
```

---

### 4. Input Validation Tests

**Test input sanitization:**

```python
@pytest.mark.security
async def test_sql_injection_protection():
    """Test protection against SQL injection."""
    async with httpx.AsyncClient() as client:
        # SQL injection attempt
        malicious_input = "'; DROP TABLE users; --"
        response = await client.post(
            "http://localhost:8000/api/v1/query",
            json={"query": malicious_input}
        )
        # Should handle safely (not execute SQL)
        assert response.status_code in [400, 422]  # Bad request

@pytest.mark.security
async def test_xss_protection():
    """Test protection against XSS attacks."""
    async with httpx.AsyncClient() as client:
        # XSS attempt
        malicious_input = "<script>alert('XSS')</script>"
        response = await client.post(
            "http://localhost:8000/api/v1/content",
            json={"content": malicious_input}
        )
        # Should sanitize input
        assert "<script>" not in response.text
```

---

### 5. Secret Management Tests

**Test that secrets are not exposed:**

```python
@pytest.mark.security
def test_no_secrets_in_code():
    """Test that no secrets are hardcoded."""
    import os
    import re
    
    # Common secret patterns
    secret_patterns = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
    ]
    
    code_dir = "symphainy-platform"
    for root, dirs, files in os.walk(code_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        assert len(matches) == 0, f"Potential secret found in {filepath}"
```

---

## Security Test Structure

### Directory Structure

```
tests/
└── security/
    ├── test_authentication.py      # Auth tests
    ├── test_authorization.py       # Authorization tests
    ├── test_input_validation.py   # Input validation tests
    ├── test_secrets.py             # Secret management tests
    └── conftest.py                 # Security test fixtures
```

### Test Markers

```python
@pytest.mark.security              # All security tests
@pytest.mark.auth                  # Authentication tests
@pytest.mark.authorization         # Authorization tests
@pytest.mark.input_validation      # Input validation tests
```

---

## Security Requirements

### Authentication

- ✅ All protected endpoints require authentication
- ✅ Tokens expire after reasonable time
- ✅ Invalid tokens rejected
- ✅ Password requirements enforced

### Authorization

- ✅ Users can only access authorized resources
- ✅ Role-based access control enforced
- ✅ Admin endpoints protected

### Input Validation

- ✅ SQL injection prevented
- ✅ XSS attacks prevented
- ✅ Command injection prevented
- ✅ Input sanitized before processing

### Secret Management

- ✅ No secrets in code
- ✅ Secrets in environment variables
- ✅ Secrets encrypted at rest
- ✅ Secrets rotated regularly

---

## Running Security Tests

### Locally

```bash
# Run all security tests
pytest tests/security/ -v -m security

# Run authentication tests
pytest tests/security/ -v -m auth

# Run vulnerability scans
cd symphainy-platform
safety check
pip-audit --desc
bandit -r . -ll

cd ../symphainy-frontend
npm audit --audit-level=moderate
```

### In CI/CD

Security tests run automatically in quality gates:

```yaml
- name: Run security scan
  run: |
    bandit -r . -ll
    safety check
    pip-audit --desc
    npm audit --audit-level=moderate
```

**Status:** Blocking (deployment blocked if vulnerabilities found)

---

## Security Best Practices

### 1. Never Commit Secrets

**Use environment variables:**
```python
# ❌ BAD
API_KEY = "sk-1234567890"

# ✅ GOOD
API_KEY = os.getenv("API_KEY")
```

### 2. Validate All Input

**Sanitize user input:**
```python
# ❌ BAD
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# ✅ GOOD
query = "SELECT * FROM users WHERE name = ?"
db.execute(query, [user_input])
```

### 3. Use Parameterized Queries

**Prevent SQL injection:**
```python
# ✅ GOOD
db.execute("SELECT * FROM users WHERE id = ?", [user_id])
```

### 4. Encrypt Sensitive Data

**Encrypt at rest:**
```python
from cryptography.fernet import Fernet

key = os.getenv("ENCRYPTION_KEY")
cipher = Fernet(key)
encrypted = cipher.encrypt(sensitive_data.encode())
```

### 5. Use HTTPS

**Always use HTTPS in production:**
```python
# ✅ GOOD
API_URL = "https://api.example.com"
```

---

## Security Test Examples

### Authentication Test

```python
@pytest.mark.security
@pytest.mark.auth
async def test_token_expiration():
    """Test that expired tokens are rejected."""
    async with httpx.AsyncClient() as client:
        expired_token = generate_expired_token()
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await client.get(
            "http://localhost:8000/api/v1/protected",
            headers=headers
        )
        assert response.status_code == 401
```

### Authorization Test

```python
@pytest.mark.security
@pytest.mark.authorization
async def test_user_cannot_access_admin():
    """Test that regular users cannot access admin endpoints."""
    async with httpx.AsyncClient() as client:
        user_token = generate_user_token()
        headers = {"Authorization": f"Bearer {user_token}"}
        response = await client.get(
            "http://localhost:8000/api/v1/admin/users",
            headers=headers
        )
        assert response.status_code == 403  # Forbidden
```

### Input Validation Test

```python
@pytest.mark.security
@pytest.mark.input_validation
async def test_command_injection_protection():
    """Test protection against command injection."""
    async with httpx.AsyncClient() as client:
        malicious_input = "; rm -rf /"
        response = await client.post(
            "http://localhost:8000/api/v1/execute",
            json={"command": malicious_input}
        )
        # Should not execute command
        assert response.status_code in [400, 422]
```

---

## CI/CD Integration

### Security Scanning

**Automatic scanning:**
- ✅ Bandit (code security)
- ✅ Safety (dependency vulnerabilities)
- ✅ pip-audit (package vulnerabilities)
- ✅ npm audit (frontend vulnerabilities)

**Status:** Blocking (deployment blocked if vulnerabilities found)

### Security Reports

**Reports generated:**
- `bandit-report.json` - Code security issues
- `safety-report.json` - Dependency vulnerabilities
- `audit-report.json` - Package vulnerabilities
- `npm-audit-report.json` - Frontend vulnerabilities

**Artifacts:** Uploaded to GitHub Actions

---

## Security Checklist

### Before Deployment

- ✅ No hardcoded secrets
- ✅ All dependencies up to date
- ✅ No known vulnerabilities
- ✅ Authentication required
- ✅ Authorization enforced
- ✅ Input validated
- ✅ HTTPS enabled
- ✅ Secrets encrypted

### Regular Security Tasks

- ✅ Weekly dependency updates
- ✅ Monthly security audits
- ✅ Quarterly penetration testing
- ✅ Annual security review

---

## Troubleshooting

### Vulnerabilities Found

**Fix:**
```bash
# Update vulnerable packages
pip install --upgrade <vulnerable-package>
npm update <vulnerable-package>

# Update lock files
cd symphainy-platform
poetry lock

cd ../symphainy-frontend
npm install
```

### Security Tests Failing

**Check:**
- Authentication configuration
- Authorization rules
- Input validation logic
- Secret management

---

## Summary

**Security Testing:**
- ✅ Vulnerability scanning (automatic)
- ✅ Code security scanning (Bandit)
- ✅ Authentication/authorization tests
- ✅ Input validation tests
- ✅ Secret management tests

**Requirements:**
- ✅ No known vulnerabilities
- ✅ Authentication required
- ✅ Authorization enforced
- ✅ Input validated
- ✅ Secrets secure

**CI/CD:**
- ✅ Automatic scanning
- ✅ Blocking (deployment blocked if vulnerabilities)
- ✅ Reports generated

---

**Questions?** Contact the security team.


