#!/usr/bin/env python3
"""
LLM Response Cache for Tests

Caches LLM responses to avoid repeated API calls.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional

class LLMResponseCache:
    """Cache LLM responses to avoid repeated API calls."""
    
    def __init__(self, cache_dir: str = "tests/.llm_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache: Dict[str, str] = {}
        self._load_cache()
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response."""
        key = self._get_cache_key(prompt, model)
        return self.cache.get(key)
    
    def set(self, prompt: str, model: str, response: str):
        """Cache response."""
        key = self._get_cache_key(prompt, model)
        self.cache[key] = response
        self._save_cache()
    
    def _load_cache(self):
        """Load cache from disk."""
        cache_file = self.cache_dir / "responses.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}
    
    def _save_cache(self):
        """Save cache to disk."""
        cache_file = self.cache_dir / "responses.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass  # Non-critical if cache save fails
    
    def clear(self):
        """Clear cache."""
        self.cache = {}
        cache_file = self.cache_dir / "responses.json"
        if cache_file.exists():
            cache_file.unlink()







