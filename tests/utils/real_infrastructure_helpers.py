"""
Real infrastructure helpers for testing.

Provides utilities for working with real infrastructure services in tests.
"""

import os
import asyncio
from typing import Dict, Any, Optional
from config.test_config import TestConfig


def setup_real_infrastructure_environment():
    """
    Set up environment variables for real infrastructure testing.
    
    This ensures tests use real services (Supabase, LLMs) instead of mocks.
    """
    if not TestConfig.USE_REAL_INFRASTRUCTURE:
        return
    
    # Set TEST_MODE to enable test Supabase credentials
    os.environ["TEST_MODE"] = "true"
    
    # Override Supabase credentials with test project
    if TestConfig.SUPABASE_URL:
        os.environ["SUPABASE_URL"] = TestConfig.SUPABASE_URL
    if TestConfig.SUPABASE_ANON_KEY:
        os.environ["SUPABASE_ANON_KEY"] = TestConfig.SUPABASE_ANON_KEY
        os.environ["SUPABASE_KEY"] = TestConfig.SUPABASE_ANON_KEY
    if TestConfig.SUPABASE_SERVICE_KEY:
        os.environ["SUPABASE_SERVICE_KEY"] = TestConfig.SUPABASE_SERVICE_KEY
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = TestConfig.SUPABASE_SERVICE_KEY
    if TestConfig.SUPABASE_JWKS_URL:
        os.environ["SUPABASE_JWKS_URL"] = TestConfig.SUPABASE_JWKS_URL
    if TestConfig.SUPABASE_JWT_ISSUER:
        os.environ["SUPABASE_JWT_ISSUER"] = TestConfig.SUPABASE_JWT_ISSUER
    
    # Configure LLM for real but cheaper models
    if TestConfig.USE_REAL_LLM and not TestConfig.USE_MOCK_LLM:
        llm_config = TestConfig.get_llm_config()
        
        if llm_config["openai"]["api_key"]:
            os.environ["LLM_OPENAI_API_KEY"] = llm_config["openai"]["api_key"]
            os.environ["OPENAI_API_KEY"] = llm_config["openai"]["api_key"]
            # Use cheaper model for testing
            if llm_config["openai"]["model"]:
                os.environ["LLM_MODEL"] = llm_config["openai"]["model"]
                os.environ["OPENAI_MODEL"] = llm_config["openai"]["model"]
        
        if llm_config["anthropic"]["api_key"]:
            os.environ["ANTHROPIC_API_KEY"] = llm_config["anthropic"]["api_key"]
            # Use cheaper model for testing
            if llm_config["anthropic"]["model"]:
                os.environ["LLM_MODEL"] = llm_config["anthropic"]["model"]
                os.environ["ANTHROPIC_MODEL"] = llm_config["anthropic"]["model"]


def cleanup_real_infrastructure_environment():
    """Clean up environment variables after tests."""
    # Remove TEST_MODE
    if "TEST_MODE" in os.environ:
        del os.environ["TEST_MODE"]


def get_test_supabase_token() -> Optional[str]:
    """
    Get a test token from Supabase test project.
    
    Creates test user if needed using admin API (service key), then signs in.
    This ensures the test user exists and is email-confirmed.
    
    Returns:
        JWT token if successful, None otherwise
    """
    if not TestConfig.SUPABASE_URL or not TestConfig.SUPABASE_ANON_KEY:
        return None
    
    try:
        import httpx
        
        # First, try to sign in (user might already exist)
        sign_in_url = f"{TestConfig.SUPABASE_URL}/auth/v1/token?grant_type=password"
        response = httpx.post(
            sign_in_url,
            json={
                "email": TestConfig.TEST_USER_EMAIL,
                "password": TestConfig.TEST_USER_PASSWORD,
            },
            headers={"apikey": TestConfig.SUPABASE_ANON_KEY},
            timeout=10.0,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        
        # If sign in fails, create user using admin API (if service key available)
        # This ensures user is created and email-confirmed without requiring email verification
        if response.status_code in [400, 401] and TestConfig.SUPABASE_SERVICE_KEY:
            admin_url = f"{TestConfig.SUPABASE_URL}/auth/v1/admin/users"
            create_response = httpx.post(
                admin_url,
                json={
                    "email": TestConfig.TEST_USER_EMAIL,
                    "password": TestConfig.TEST_USER_PASSWORD,
                    "email_confirm": True,  # Auto-confirm email (no verification needed)
                    "user_metadata": {"test_user": True, "source": "test_suite"}
                },
                headers={
                    "apikey": TestConfig.SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {TestConfig.SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=10.0,
            )
            
            # If admin creation succeeds, try sign in
            if create_response.status_code == 200:
                sign_in_response = httpx.post(
                    sign_in_url,
                    json={
                        "email": TestConfig.TEST_USER_EMAIL,
                        "password": TestConfig.TEST_USER_PASSWORD,
                    },
                    headers={"apikey": TestConfig.SUPABASE_ANON_KEY},
                    timeout=10.0,
                )
                if sign_in_response.status_code == 200:
                    data = sign_in_response.json()
                    return data.get("access_token")
        
        # Fallback: Try regular signup (if admin API not available or failed)
        if response.status_code in [400, 401]:
            sign_up_url = f"{TestConfig.SUPABASE_URL}/auth/v1/signup"
            sign_up_response = httpx.post(
                sign_up_url,
                json={
                    "email": TestConfig.TEST_USER_EMAIL,
                    "password": TestConfig.TEST_USER_PASSWORD,
                },
                headers={"apikey": TestConfig.SUPABASE_ANON_KEY},
                timeout=10.0,
            )
            
            # If signup succeeds, try sign in again
            if sign_up_response.status_code in [200, 201]:
                sign_in_response = httpx.post(
                    sign_in_url,
                    json={
                        "email": TestConfig.TEST_USER_EMAIL,
                        "password": TestConfig.TEST_USER_PASSWORD,
                    },
                    headers={"apikey": TestConfig.SUPABASE_ANON_KEY},
                    timeout=10.0,
                )
                if sign_in_response.status_code == 200:
                    data = sign_in_response.json()
                    return data.get("access_token")
        
        return None
    except Exception as e:
        print(f"⚠️  Failed to get test Supabase token: {e}")
        return None


def validate_real_infrastructure_available() -> Dict[str, bool]:
    """
    Validate that real infrastructure is available and configured.
    
    Returns:
        Dictionary with availability status for each service
    """
    validation = TestConfig.validate_real_infrastructure()
    
    # Additional checks for actual connectivity
    availability = {
        "supabase": validation["supabase"],
        "openai": validation["openai"],
        "anthropic": validation["anthropic"],
        "arango": validation["arango"],
        "redis": validation["redis"],
        "consul": validation["consul"],
        "huggingface": validation["huggingface"],
    }
    
    return availability


def skip_if_missing_real_infrastructure(services: list):
    """
    Pytest marker helper to skip tests if real infrastructure is missing.
    
    Args:
        services: List of service names to check (e.g., ["supabase", "openai"])
    """
    import pytest
    
    availability = validate_real_infrastructure_available()
    missing = [s for s in services if not availability.get(s, False)]
    
    if missing:
        pytest.skip(
            f"Real infrastructure not available: {', '.join(missing)}. "
            f"Set TEST_USE_REAL_INFRASTRUCTURE=false to use mocks, "
            f"or configure missing services."
        )



