#!/usr/bin/env python3
"""
Supabase JWKS Adapter - JWKS Fetcher and Cache

Fetches and caches Supabase's JWKS (JSON Web Key Set) for local JWT verification.
This is Layer 1 of the 5-layer security architecture.

WHAT (Infrastructure Role): I provide JWKS fetching and caching
HOW (Infrastructure Implementation): I fetch from Supabase's JWKS endpoint and cache public keys
"""

import os
import logging
import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SupabaseJWKSAdapter:
    """
    JWKS adapter for Supabase - fetches and caches public keys.
    
    Supabase provides JWKS at: https://<project>.supabase.co/auth/v1/.well-known/jwks.json
    This allows local JWT verification without network calls to Supabase API.
    """
    
    def __init__(self, supabase_url: str = None, jwks_url: str = None, cache_ttl: int = 600, config_adapter = None):
        """
        Initialize JWKS adapter.
        
        Args:
            supabase_url: Supabase project URL (used to construct JWKS URL if jwks_url not provided)
            jwks_url: Direct JWKS URL (takes precedence)
            cache_ttl: Cache TTL in seconds (default 10 minutes, Supabase caches for 10 min)
            config_adapter: Optional ConfigAdapter for reading configuration (preferred over os.getenv)
        """
        self.config_adapter = config_adapter
        
        # Use SUPABASE_JWKS_URL if provided (recommended), otherwise construct from supabase_url
        if jwks_url:
            # Normalize JWKS URL - ensure it has .well-known (not well-known)
            self.jwks_url = jwks_url.replace("/well-known/", "/.well-known/")
        elif supabase_url:
            # Normalize URL - remove trailing slashes
            self.supabase_url = supabase_url.rstrip('/') if supabase_url else supabase_url
            self.jwks_url = f"{self.supabase_url}/auth/v1/.well-known/jwks.json"
        else:
            # Try to get from ConfigAdapter (required, no fallback to os.getenv)
            if config_adapter:
                jwks_url_env = config_adapter.get("SUPABASE_JWKS_URL")
                if jwks_url_env:
                    # Normalize JWKS URL - ensure it has .well-known (not well-known)
                    self.jwks_url = jwks_url_env.replace("/well-known/", "/.well-known/")
                else:
                    raise ValueError(
                        "SUPABASE_JWKS_URL not found in configuration. "
                        "Either provide jwks_url or supabase_url parameter, or ensure config contains SUPABASE_JWKS_URL."
                    )
            else:
                raise ValueError(
                    "ConfigAdapter is required. "
                    "Pass config_adapter from Public Works Foundation. "
                    "Example: SupabaseJWKSAdapter(config_adapter=config_adapter, supabase_url=url)"
                )
        
        self.cache_ttl = cache_ttl
        
        # Cache for JWKS
        self._jwks_cache: Optional[Dict[str, Any]] = None
        self._jwks_cache_time: Optional[datetime] = None
        self._jwks_lock = asyncio.Lock()
        
        logger.info(f"✅ Supabase JWKS adapter initialized for: {self.jwks_url}")
    
    async def get_jwks(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get JWKS (cached or fresh).
        
        Args:
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            JWKS dictionary with keys
        """
        async with self._jwks_lock:
            # Check if cache is valid
            if not force_refresh and self._jwks_cache and self._jwks_cache_time:
                age = (datetime.utcnow() - self._jwks_cache_time).total_seconds()
                if age < self.cache_ttl:
                    logger.debug(f"Using cached JWKS (age: {age:.1f}s)")
                    return self._jwks_cache
            
            # Fetch fresh JWKS
            try:
                logger.info(f"Fetching JWKS from: {self.jwks_url}")
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(self.jwks_url)
                    response.raise_for_status()
                    
                    jwks = response.json()
                    
                    # Validate JWKS structure
                    if not isinstance(jwks, dict) or "keys" not in jwks:
                        raise ValueError("Invalid JWKS structure: missing 'keys'")
                    
                    # Cache JWKS
                    self._jwks_cache = jwks
                    self._jwks_cache_time = datetime.utcnow()
                    
                    logger.info(f"✅ JWKS fetched and cached ({len(jwks.get('keys', []))} keys)")
                    return jwks
                    
            except httpx.TimeoutException:
                logger.error(f"❌ JWKS fetch timeout: {self.jwks_url}")
                # Return cached JWKS if available (even if expired)
                if self._jwks_cache:
                    logger.warning("⚠️ Using expired JWKS cache due to timeout")
                    return self._jwks_cache
                raise
            except Exception as e:
                logger.error(f"❌ Failed to fetch JWKS: {e}")
                # Return cached JWKS if available (even if expired)
                if self._jwks_cache:
                    logger.warning("⚠️ Using expired JWKS cache due to error")
                    return self._jwks_cache
                raise
    
    def get_key_by_kid(self, kid: str, jwks: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get public key by key ID (kid) from JWKS.
        
        Args:
            kid: Key ID from JWT header
            jwks: JWKS dictionary (if None, uses cached JWKS)
            
        Returns:
            Public key dictionary or None if not found
        """
        if jwks is None:
            jwks = self._jwks_cache
        
        if not jwks or "keys" not in jwks:
            return None
        
        # Find key with matching kid
        for key in jwks["keys"]:
            if key.get("kid") == kid:
                return key
        
        return None
    
    async def refresh_jwks(self) -> Dict[str, Any]:
        """Force refresh JWKS cache."""
        return await self.get_jwks(force_refresh=True)

