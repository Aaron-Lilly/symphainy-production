"""
Test configuration for SymphAIny Platform tests.

Provides test-specific configuration values and environment setup.
"""

import os
from typing import Dict, Any
from pathlib import Path

# Load .env.secrets if available (for Supabase test project credentials)
# This ensures tests use the test Supabase project, not production
try:
    from dotenv import load_dotenv
    # Try multiple possible paths for .env.secrets
    possible_paths = [
        Path("/home/founders/demoversion/symphainy_source/symphainy-platform/.env.secrets"),
        Path(__file__).parent.parent.parent.parent / "symphainy-platform" / ".env.secrets",
        Path(__file__).parent.parent.parent / "symphainy-platform" / ".env.secrets",
    ]
    for env_secrets_path in possible_paths:
        if env_secrets_path.exists():
            load_dotenv(env_secrets_path, override=False)  # Don't override existing env vars
            break
except ImportError:
    pass  # dotenv not available, skip


class TestConfig:
    """Test configuration manager."""
    
    # Test environment
    ENVIRONMENT = os.getenv("TEST_ENVIRONMENT", "test")
    
    # Infrastructure URLs (default to localhost for test environment)
    ARANGO_URL = os.getenv("TEST_ARANGO_URL", "http://localhost:8529")
    ARANGO_DB = os.getenv("TEST_ARANGO_DB", "symphainy_test")
    ARANGO_USER = os.getenv("TEST_ARANGO_USER", "root")
    ARANGO_PASS = os.getenv("TEST_ARANGO_PASS", "")
    
    REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379")
    REDIS_HOST = os.getenv("TEST_REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("TEST_REDIS_PORT", "6379"))
    
    CONSUL_HOST = os.getenv("TEST_CONSUL_HOST", "localhost")
    CONSUL_PORT = int(os.getenv("TEST_CONSUL_PORT", "8500"))
    CONSUL_DATACENTER = os.getenv("TEST_CONSUL_DATACENTER", "dc1")
    
    MEILI_HOST = os.getenv("TEST_MEILI_HOST", "localhost")
    MEILI_PORT = int(os.getenv("TEST_MEILI_PORT", "7700"))
    MEILI_MASTER_KEY = os.getenv("TEST_MEILI_MASTER_KEY", "masterKey")
    
    # API URLs
    BACKEND_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
    
    # Test data paths
    TEST_DATA_DIR = Path(__file__).parent.parent.parent / "tests" / "data"
    TEST_TMP_DIR = Path(__file__).parent.parent.parent / "tests" / "tmp"
    
    # Test timeouts
    DEFAULT_TIMEOUT = float(os.getenv("TEST_DEFAULT_TIMEOUT", "30.0"))
    FAST_TEST_TIMEOUT = float(os.getenv("TEST_FAST_TIMEOUT", "5.0"))
    SLOW_TEST_TIMEOUT = float(os.getenv("TEST_SLOW_TIMEOUT", "300.0"))
    
    # Supabase Configuration (Test Project - with rate limiting prevention)
    # Priority: TEST_SUPABASE_* > SUPABASE_* (to use test project, not production)
    # Note: .env.secrets is loaded above, so these will pick up test project credentials
    # Supabase has renamed keys: "anon key" → "Publishable Key", "service key" → "Secret Key"
    SUPABASE_URL = os.getenv("TEST_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    # Publishable Key (new name) or fallback to old names for backward compatibility
    SUPABASE_ANON_KEY = (
        os.getenv("TEST_SUPABASE_ANON_KEY") or 
        os.getenv("TEST_SUPABASE_PUBLISHABLE_KEY") or
        os.getenv("SUPABASE_PUBLISHABLE_KEY") or  # New Supabase naming
        os.getenv("SUPABASE_KEY") or  # Old naming
        os.getenv("SUPABASE_ANON_KEY")  # Old naming
    )
    # Secret Key (new name) or fallback to old names for backward compatibility
    SUPABASE_SERVICE_KEY = (
        os.getenv("TEST_SUPABASE_SERVICE_KEY") or 
        os.getenv("TEST_SUPABASE_SECRET_KEY") or
        os.getenv("SUPABASE_SECRET_KEY") or  # New Supabase naming
        os.getenv("SUPABASE_SERVICE_KEY")  # Old naming
    )
    SUPABASE_JWKS_URL = os.getenv("TEST_SUPABASE_JWKS_URL") or os.getenv("SUPABASE_JWKS_URL")
    SUPABASE_JWT_ISSUER = os.getenv("TEST_SUPABASE_JWT_ISSUER") or os.getenv("SUPABASE_JWT_ISSUER")
    
    # Test User Credentials (for Supabase auth)
    TEST_USER_EMAIL = os.getenv("TEST_SUPABASE_EMAIL") or os.getenv("TEST_USER_EMAIL", "test@symphainy.com")
    TEST_USER_PASSWORD = os.getenv("TEST_SUPABASE_PASSWORD") or os.getenv("TEST_USER_PASSWORD", "test_password_123")
    
    # LLM Configuration (Real but cheaper models for testing)
    # Default to cheaper models to validate functionality while minimizing costs
    LLM_OPENAI_API_KEY = os.getenv("TEST_OPENAI_API_KEY") or os.getenv("LLM_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    LLM_OPENAI_MODEL = os.getenv("TEST_OPENAI_MODEL", "gpt-3.5-turbo")  # Cheaper model for testing
    LLM_ANTHROPIC_API_KEY = os.getenv("TEST_ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    LLM_ANTHROPIC_MODEL = os.getenv("TEST_ANTHROPIC_MODEL", "claude-3-haiku-20240307")  # Cheaper model for testing
    
    # HuggingFace Configuration (for embedding creation)
    HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL = os.getenv("TEST_HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL") or os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
    HUGGINGFACE_EMBEDDINGS_API_KEY = os.getenv("TEST_HUGGINGFACE_EMBEDDINGS_API_KEY") or os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
    
    # Test flags (DEFAULT TO REAL INFRASTRUCTURE)
    # Use real infrastructure by default to catch production issues early
    USE_REAL_INFRASTRUCTURE = os.getenv("TEST_USE_REAL_INFRASTRUCTURE", "true").lower() == "true"
    USE_REAL_LLM = os.getenv("TEST_USE_REAL_LLM", "true").lower() == "true"  # Default to real LLM (cheaper models)
    USE_MOCK_LLM = os.getenv("TEST_USE_MOCK_LLM", "false").lower() == "true"  # Override to use mocks
    SKIP_SLOW_TESTS = os.getenv("TEST_SKIP_SLOW_TESTS", "false").lower() == "true"
    SKIP_LLM_TESTS = os.getenv("TEST_SKIP_LLM_TESTS", "false").lower() == "true"  # Skip LLM tests if no API keys
    
    @classmethod
    def get_infrastructure_config(cls) -> Dict[str, Any]:
        """Get infrastructure configuration for tests."""
        return {
            "arango": {
                "url": cls.ARANGO_URL,
                "database": cls.ARANGO_DB,
                "username": cls.ARANGO_USER,
                "password": cls.ARANGO_PASS,
            },
            "redis": {
                "url": cls.REDIS_URL,
                "host": cls.REDIS_HOST,
                "port": cls.REDIS_PORT,
            },
            "consul": {
                "host": cls.CONSUL_HOST,
                "port": cls.CONSUL_PORT,
                "datacenter": cls.CONSUL_DATACENTER,
            },
            "meilisearch": {
                "host": cls.MEILI_HOST,
                "port": cls.MEILI_PORT,
                "master_key": cls.MEILI_MASTER_KEY,
            },
            "supabase": {
                "url": cls.SUPABASE_URL,
                "anon_key": cls.SUPABASE_ANON_KEY,
                "service_key": cls.SUPABASE_SERVICE_KEY,
                "jwks_url": cls.SUPABASE_JWKS_URL,
                "jwt_issuer": cls.SUPABASE_JWT_ISSUER,
            },
        }
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration for tests (using cheaper models)."""
        return {
            "openai": {
                "api_key": cls.LLM_OPENAI_API_KEY,
                "model": cls.LLM_OPENAI_MODEL,  # gpt-3.5-turbo (cheaper)
            },
            "anthropic": {
                "api_key": cls.LLM_ANTHROPIC_API_KEY,
                "model": cls.LLM_ANTHROPIC_MODEL,  # claude-3-haiku (cheaper)
            },
            "use_real_llm": cls.USE_REAL_LLM and not cls.USE_MOCK_LLM,
            "skip_llm_tests": cls.SKIP_LLM_TESTS,
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Get API configuration for tests."""
        return {
            "backend_url": cls.BACKEND_URL,
            "frontend_url": cls.FRONTEND_URL,
        }
    
    @classmethod
    def ensure_test_directories(cls):
        """Ensure test data and tmp directories exist."""
        cls.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEST_TMP_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_real_infrastructure(cls) -> Dict[str, bool]:
        """
        Validate that real infrastructure is configured.
        
        Returns:
            Dictionary with validation status for each service
        """
        validation = {
            "supabase": bool(cls.SUPABASE_URL and cls.SUPABASE_ANON_KEY),
            "openai": bool(cls.LLM_OPENAI_API_KEY),
            "anthropic": bool(cls.LLM_ANTHROPIC_API_KEY),
            "arango": bool(cls.ARANGO_URL),
            "redis": bool(cls.REDIS_URL),
            "consul": bool(cls.CONSUL_HOST),
            "huggingface": bool(cls.HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL and cls.HUGGINGFACE_EMBEDDINGS_API_KEY),
        }
        return validation
    
    @classmethod
    def get_missing_infrastructure(cls) -> list:
        """Get list of missing infrastructure configuration."""
        missing = []
        validation = cls.validate_real_infrastructure()
        
        if cls.USE_REAL_INFRASTRUCTURE:
            if not validation["supabase"]:
                missing.append("Supabase (TEST_SUPABASE_URL, TEST_SUPABASE_ANON_KEY)")
            if not validation["arango"]:
                missing.append("ArangoDB (TEST_ARANGO_URL)")
            if not validation["redis"]:
                missing.append("Redis (TEST_REDIS_URL)")
            if not validation["consul"]:
                missing.append("Consul (TEST_CONSUL_HOST)")
            if not validation["huggingface"]:
                missing.append("HuggingFace (TEST_HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL, TEST_HUGGINGFACE_EMBEDDINGS_API_KEY)")
        
        if cls.USE_REAL_LLM and not cls.USE_MOCK_LLM:
            if not validation["openai"] and not validation["anthropic"]:
                missing.append("LLM API Key (TEST_OPENAI_API_KEY or TEST_ANTHROPIC_API_KEY)")
        
        return missing

