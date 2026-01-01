#!/usr/bin/env python3
"""
Production Test Client

Provides a test client for production testing with:
1. Rate limiting mitigation
2. Authentication caching
3. Test data isolation
4. Request throttling
"""

import asyncio
import httpx
import time
import os
import pytest
from typing import Optional, Dict, Any
from pathlib import Path


class RateLimitMonitor:
    """Monitor and enforce rate limits with safeguards."""
    
    def __init__(self, max_requests_per_minute: int = 50, test_mode: bool = False):
        """
        Initialize rate limit monitor.
        
        Args:
            max_requests_per_minute: Maximum requests per minute
                - Production: 50 (stays under 60 limit with buffer)
                - Test: 55 (still under 60, but more permissive)
            test_mode: Whether running in test mode (separate Supabase project)
        """
        # Adjust limits based on mode
        if test_mode:
            # Test mode: slightly more permissive but still safe
            self.max_requests = max_requests_per_minute if max_requests_per_minute != 50 else 55
        else:
            # Production mode: conservative limits
            self.max_requests = max_requests_per_minute
        
        self.test_mode = test_mode
        self.requests = []
        self.lock = asyncio.Lock()
        self.rate_limit_hits = 0
        self.last_rate_limit_warning = 0
    
    async def wait_if_needed(self):
        """Wait if we're approaching rate limit."""
        # Skip rate limiting entirely in test mode (test Supabase has no limits)
        if self.test_mode:
            return  # No throttling needed
        
        async with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.requests = [r for r in self.requests if now - r < 60]
            
            # Check if we're approaching limit (80% threshold for warning)
            threshold = int(self.max_requests * 0.8)
            if len(self.requests) >= threshold and now - self.last_rate_limit_warning > 10:
                print(f"⚠️  Rate limit warning (PRODUCTION): {len(self.requests)}/{self.max_requests} requests in last minute")
                self.last_rate_limit_warning = now
            
            if len(self.requests) >= self.max_requests:
                # Wait until we can make another request
                oldest_request = min(self.requests) if self.requests else now
                wait_time = 60 - (now - oldest_request) + 0.1  # Add 100ms buffer
                if wait_time > 0:
                    print(f"⏸️  Rate limit throttling (PRODUCTION): waiting {wait_time:.1f}s before next request")
                    await asyncio.sleep(wait_time)
                    # Remove the oldest request
                    self.requests.pop(0)
            
            self.requests.append(time.time())
    
    def record_rate_limit_hit(self):
        """Record that we hit a rate limit (429 error)."""
        self.rate_limit_hits += 1
        if self.test_mode:
            print(f"⚠️  Unexpected rate limit hit in test mode (test Supabase should have no limits)")
        else:
            print(f"🚨 Rate limit hit (PRODUCTION): {self.rate_limit_hits} total hits")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limit statistics."""
        return {
            "max_requests_per_minute": self.max_requests,
            "test_mode": self.test_mode,
            "current_requests_last_minute": len(self.requests),
            "rate_limit_hits": self.rate_limit_hits
        }


class ProductionTestClient:
    """
    Production test client with rate limiting mitigation.
    
    Features:
    - Rate limit monitoring and throttling
    - Authentication token caching
    - Request throttling (delay between requests)
    - Test data isolation
    """
    
    def __init__(
        self,
        base_url: str,
        test_user_email: Optional[str] = None,
        test_user_password: Optional[str] = None,
        request_delay: Optional[float] = None,
        max_requests_per_minute: Optional[int] = None
    ):
        """
        Initialize production test client with rate limiting safeguards.
        
        Args:
            base_url: Base URL for API (e.g., "http://localhost:8000")
            test_user_email: Test user email (default: from env or "test_user@symphainy.com")
            test_user_password: Test user password (default: from env or "test_password_123")
            request_delay: Delay between requests in seconds
                - Production: 0.5s (default)
                - Test: 0.2s (configurable via TEST_REQUEST_DELAY)
            max_requests_per_minute: Max requests per minute
                - Production: 50 (default)
                - Test: 55 (configurable via TEST_MAX_REQUESTS_PER_MINUTE)
        """
        self.base_url = base_url.rstrip('/')
        # Resolve test user credentials (priority: param > TEST_USER_* > TEST_SUPABASE_* > default)
        self.test_user_email = (
            test_user_email or 
            os.getenv("TEST_USER_EMAIL") or 
            os.getenv("TEST_SUPABASE_EMAIL") or 
            "test_user@symphainy.com"
        )
        self.test_user_password = (
            test_user_password or 
            os.getenv("TEST_USER_PASSWORD") or 
            os.getenv("TEST_SUPABASE_PASSWORD") or 
            "test_password_123"
        )
        
        # Auto-detect test mode: TEST_MODE=true OR test Supabase is configured
        test_supabase_configured = (
            os.getenv("TEST_SUPABASE_URL") and 
            os.getenv("TEST_SUPABASE_ANON_KEY")
        )
        self.test_mode = (
            os.getenv("TEST_MODE", "false").lower() == "true" or 
            test_supabase_configured
        )
        
        # Configure rate limiting based on mode
        # Test Supabase has no rate limits, so disable throttling entirely
        if request_delay is None:
            if self.test_mode:
                # Test mode: No rate limits, no delays needed
                self.request_delay = float(os.getenv("TEST_REQUEST_DELAY", "0.0"))
            else:
                # Production mode: conservative limits
                self.request_delay = float(os.getenv("PROD_REQUEST_DELAY", "0.5"))
        else:
            self.request_delay = request_delay
        
        if max_requests_per_minute is None:
            if self.test_mode:
                # Test mode: Effectively unlimited (test Supabase has no rate limits)
                self.max_requests_per_minute = int(os.getenv("TEST_MAX_REQUESTS_PER_MINUTE", "999999"))
            else:
                # Production mode: conservative limits
                self.max_requests_per_minute = int(os.getenv("PROD_MAX_REQUESTS_PER_MINUTE", "50"))
        else:
            self.max_requests_per_minute = max_requests_per_minute
        
        # Log mode detection for debugging (only if verbose logging is enabled)
        # Use logging instead of print to avoid interfering with pytest output
        import logging
        logger = logging.getLogger(__name__)
        if self.test_mode:
            mode_source = "TEST_MODE env var" if os.getenv("TEST_MODE", "false").lower() == "true" else "test Supabase config"
            logger.info(f"✅ ProductionTestClient: Test mode enabled (detected from {mode_source})")
            logger.info(f"   Rate limiting: DISABLED (test Supabase has no limits)")
            logger.info(f"   Request delay: {self.request_delay}s")
        else:
            logger.info(f"⚠️  ProductionTestClient: Production mode (rate limiting enabled)")
            logger.info(f"   Max requests/min: {self.max_requests_per_minute}")
            logger.info(f"   Request delay: {self.request_delay}s")
        
        self.rate_limit_monitor = RateLimitMonitor(
            max_requests_per_minute=self.max_requests_per_minute,
            test_mode=self.test_mode
        )
        
        # Retry configuration for 429 errors
        self.max_retries = int(os.getenv("TEST_MAX_RETRIES", "3"))
        self.retry_delay_base = float(os.getenv("TEST_RETRY_DELAY_BASE", "2.0"))
        
        # Cached authentication token
        self.cached_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None
        
        # HTTP client with appropriate timeout and connection settings
        # Use longer timeout for production tests (may go through Traefik)
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(30.0, connect=10.0),  # 10s connect, 30s total
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            follow_redirects=True
        )
    
    async def authenticate(self, force_refresh: bool = False) -> str:
        """
        Authenticate and get token (cached).
        
        Args:
            force_refresh: Force token refresh even if cached
        
        Returns:
            Authentication token
        """
        # Check if token is still valid
        if not force_refresh and self.cached_token and self.token_expires_at:
            if time.time() < self.token_expires_at:
                return self.cached_token
        
        # Wait for rate limit
        await self.rate_limit_monitor.wait_if_needed()
        
        # Add delay
        await asyncio.sleep(self.request_delay)
        
        # Authenticate
        try:
            response = await self.client.post(
                "/api/auth/login",
                json={
                    "email": self.test_user_email,
                    "password": self.test_user_password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.cached_token = data.get("token") or data.get("access_token")
                # Assume token expires in 1 hour (adjust if needed)
                self.token_expires_at = time.time() + 3600
                return self.cached_token
            else:
                raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
        
        except Exception as e:
            # If authentication fails, try to continue without token
            # (some endpoints may work without auth)
            print(f"⚠️ Authentication failed: {e}")
            return None
    
    async def make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with rate limiting, authentication, and 429 error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL path (relative to base_url)
            **kwargs: Additional arguments for httpx request
        
        Returns:
            HTTP response
        """
        # Retry loop for 429 errors
        for attempt in range(1, self.max_retries + 1):
            # Wait for rate limit (skipped in test mode)
            await self.rate_limit_monitor.wait_if_needed()
            
            # Add delay between requests (0.0 in test mode, 0.5s in production)
            if self.request_delay > 0:
                await asyncio.sleep(self.request_delay)
            
            # Get authentication token
            token = await self.authenticate()
            
            # Add authentication header if token available
            # CRITICAL: Ensure headers dict exists and is properly merged (httpx may not merge when files are present)
            if token:
                if "headers" not in kwargs:
                    kwargs["headers"] = {}
                elif kwargs["headers"] is None:
                    kwargs["headers"] = {}
                # Merge headers (don't overwrite existing headers)
                if isinstance(kwargs["headers"], dict):
                    kwargs["headers"]["Authorization"] = f"Bearer {token}"
                else:
                    # If headers is not a dict, convert it
                    headers_dict = dict(kwargs["headers"]) if hasattr(kwargs["headers"], "__iter__") else {}
                    headers_dict["Authorization"] = f"Bearer {token}"
                    kwargs["headers"] = headers_dict
            
            # Make request
            try:
                response = await self.client.request(method, url, **kwargs)
                
                # Handle 429 (Too Many Requests) errors
                if response.status_code == 429:
                    self.rate_limit_monitor.record_rate_limit_hit()
                    
                    # Handle 429 errors
                    # In test mode, 429 should be rare (test Supabase has no limits)
                    # But if it happens, fail fast rather than retrying
                    if self.test_mode:
                        print(f"⚠️  Unexpected 429 in test mode (test Supabase should have no limits)")
                        print(f"   This may indicate a configuration issue")
                        return response  # Fail fast in test mode
                    
                    # Production mode: retry with backoff
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait_time = int(retry_after)
                    else:
                        # Exponential backoff
                        wait_time = self.retry_delay_base * (2 ** (attempt - 1))
                    
                    if attempt < self.max_retries:
                        print(f"⏸️  Rate limit 429 (PRODUCTION): Waiting {wait_time}s before retry {attempt}/{self.max_retries}")
                        await asyncio.sleep(wait_time)
                        continue  # Retry
                    else:
                        # Max retries exceeded
                        print(f"❌ Rate limit 429 (PRODUCTION): Max retries exceeded")
                        return response  # Return the 429 response
                
                # Success or other error - return response
                return response
                
            except httpx.RequestError as e:
                # Network error - retry if we have attempts left
                if attempt < self.max_retries:
                    wait_time = self.retry_delay_base * (2 ** (attempt - 1))
                    print(f"⚠️  Request error: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise  # Re-raise if max retries exceeded
        
        # Should never reach here, but just in case
        raise RuntimeError("Max retries exceeded for request")
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Make GET request."""
        return await self.make_request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Make POST request."""
        return await self.make_request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        """Make PUT request."""
        return await self.make_request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Make DELETE request."""
        return await self.make_request("DELETE", url, **kwargs)
    
    async def upload_file(
        self,
        file_path: str,
        endpoint: str = "/api/v1/content-pillar/upload-file",
        copybook_path: Optional[str] = None
    ) -> httpx.Response:
        """
        Upload file with rate limiting.
        
        Args:
            file_path: Path to file to upload
            endpoint: Upload endpoint
            copybook_path: Optional path to copybook file
        
        Returns:
            HTTP response
        """
        # Wait for rate limit
        await self.rate_limit_monitor.wait_if_needed()
        
        # Add delay
        await asyncio.sleep(self.request_delay)
        
        # Read file
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path_obj, "rb") as f:
            file_content = f.read()
        
        # Prepare files
        files = {
            "file": (file_path_obj.name, file_content, "application/octet-stream")
        }
        
        if copybook_path:
            copybook_path_obj = Path(copybook_path)
            if copybook_path_obj.exists():
                with open(copybook_path_obj, "rb") as f:
                    copybook_content = f.read()
                files["copybook"] = (copybook_path_obj.name, copybook_content, "text/plain")
        
        # Get authentication token
        token = await self.authenticate()
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Upload file
        return await self.client.post(
            endpoint,
            files=files,
            headers=headers
        )
    
    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        return self.rate_limit_monitor.get_stats()
    
    async def close(self):
        """Close HTTP client and print rate limit statistics."""
        stats = self.get_rate_limit_stats()
        # Only print stats if there were rate limit hits (production mode) or unexpected issues (test mode)
        if stats["rate_limit_hits"] > 0:
            if self.test_mode:
                print(f"\n⚠️  Rate Limit Stats (TEST MODE - unexpected):")
                print(f"   Rate limit hits (429): {stats['rate_limit_hits']}")
                print(f"   This suggests test Supabase may not be configured correctly")
            else:
                print(f"\n📊 Rate Limit Stats (PRODUCTION):")
                print(f"   Max requests/min: {stats['max_requests_per_minute']}")
                print(f"   Requests in last minute: {stats['current_requests_last_minute']}")
                print(f"   Rate limit hits (429): {stats['rate_limit_hits']}")
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Pytest fixture for production test client
@pytest.fixture
async def production_client():
    """Create production test client."""
    base_url = os.getenv("PRODUCTION_BASE_URL", "http://localhost:8000")
    client = ProductionTestClient(base_url=base_url)
    yield client
    await client.close()

