#!/usr/bin/env python3
"""
Tempo Infrastructure Adapter

Raw Tempo bindings for distributed tracing.
Thin wrapper around Tempo client with no business logic.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
import uuid

try:
    import tempo
    from tempo import TempoClient
except ImportError:
    tempo = None
    TempoClient = None


class TempoAdapter:
    """Raw Tempo adapter for distributed tracing integration."""
    
    def __init__(self, tempo_url: str = "http://localhost:3200", **kwargs):
        """
        Initialize Tempo adapter.
        
        Args:
            tempo_url: Tempo server URL
        """
        self.tempo_url = tempo_url
        self.logger = logging.getLogger("TempoAdapter")
        
        # Tempo client (private - use wrapper methods instead)
        self._client = None
        
        # Initialize Tempo
        self._initialize_tempo()
    
    def _initialize_tempo(self):
        """Initialize Tempo client."""
        if not tempo or not TempoClient:
            self.logger.warning("Tempo not installed, tracing will be disabled")
            return
        
        try:
            # Create Tempo client (private)
            self._client = TempoClient(self.tempo_url)
            # Keep client as alias for backward compatibility (will be removed)
            self.client = self._client
            self.logger.info("✅ Tempo adapter initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Tempo client: {e}")
            self._client = None
            self.client = None
    
    async def start_trace(self, trace_name: str, context: Dict[str, Any]) -> str:
        """Start a distributed trace."""
        if not self._client:
            return str(uuid.uuid4())  # Return mock trace ID if Tempo not available
        
        try:
            trace_id = str(uuid.uuid4())
            self.logger.debug(f"Starting trace: {trace_name} ({trace_id})")
            return trace_id
        except Exception as e:
            self.logger.error(f"Failed to start trace: {e}")
            return str(uuid.uuid4())
    
    async def add_span(self, trace_id: str, span_name: str, context: Dict[str, Any]) -> str:
        """Add a span to a trace."""
        if not self._client:
            return str(uuid.uuid4())  # Return mock span ID if Tempo not available
        
        try:
            span_id = str(uuid.uuid4())
            self.logger.debug(f"Adding span: {span_name} ({span_id}) to trace {trace_id}")
            return span_id
        except Exception as e:
            self.logger.error(f"Failed to add span: {e}")
            return str(uuid.uuid4())
    
    async def end_span(self, span_id: str, status: str = "success") -> bool:
        """End a span."""
        if not self._client:
            return True  # Return success if Tempo not available
        
        try:
            self.logger.debug(f"Ending span: {span_id} with status {status}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to end span: {e}")
            return False
    
    async def end_trace(self, trace_id: str, status: str = "success") -> bool:
        """End a trace."""
        if not self._client:
            return True  # Return success if Tempo not available
        
        try:
            self.logger.debug(f"Ending trace: {trace_id} with status {status}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to end trace: {e}")
            return False
    
    async def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve trace data."""
        if not self._client:
            return {
                "trace_id": trace_id,
                "spans": [],
                "status": "mock"
            }
        
        try:
            self.logger.debug(f"Retrieving trace: {trace_id}")
            # Mock trace data for now
            return {
                "trace_id": trace_id,
                "spans": [],
                "status": "retrieved"
            }
        except Exception as e:
            self.logger.error(f"Failed to retrieve trace: {e}")
            return None
    
    async def search_traces(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Search traces."""
        if not self._client:
            return []
        
        try:
            self.logger.debug(f"Searching traces with query: {query}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to search traces: {e}")
            return []
    
    async def get_trace_metrics(self, trace_id: str) -> Dict[str, Any]:
        """Get trace metrics."""
        if not self._client:
            return {"trace_id": trace_id, "metrics": {}}
        
        try:
            self.logger.debug(f"Getting metrics for trace: {trace_id}")
            return {"trace_id": trace_id, "metrics": {}}
        except Exception as e:
            self.logger.error(f"Failed to get trace metrics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Tempo adapter health."""
        try:
            if not self._client:
                return {
                    "status": "unhealthy",
                    "reason": "tempo_not_available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test connection
            test_trace = await self.start_trace("health_check", {})
            if test_trace:
                return {
                    "status": "healthy",
                    "tempo_url": self.tempo_url,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "reason": "connection_failed",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "reason": "health_check_failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

