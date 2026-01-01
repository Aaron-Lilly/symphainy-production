#!/usr/bin/env python3
"""
Loki Adapter - Raw Technology Client

Raw Loki client wrapper with no business logic.
This is Layer 0 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw Loki operations for log aggregation
HOW (Infrastructure Implementation): I use HTTP client (httpx) to interact with Loki REST API
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import logging

try:
    import httpx
except ImportError:
    httpx = None
    logging.warning("httpx not available - Loki adapter will not work")

logger = logging.getLogger(__name__)


class LokiAdapter:
    """
    Raw Loki client wrapper - no business logic.
    
    This adapter provides direct access to Loki operations without
    any business logic or abstraction. It's the raw technology layer.
    
    Uses Loki's REST API:
    - POST /loki/api/v1/push - Push logs
    - GET /loki/api/v1/query_range - Query logs
    - GET /ready - Health check
    """
    
    def __init__(self, endpoint: str, tenant_id: str = None):
        """
        Initialize Loki adapter.
        
        Args:
            endpoint: Loki endpoint URL (e.g., "http://loki:3100")
            tenant_id: Optional tenant ID for multi-tenancy
        """
        if not httpx:
            raise ImportError("httpx is required for LokiAdapter")
        
        self.endpoint = endpoint.rstrip('/')
        self.tenant_id = tenant_id
        
        # HTTP client (will be created on first use)
        self._client: Optional[httpx.AsyncClient] = None
        self._is_connected = False
        
        logger.info(f"✅ Loki adapter initialized for endpoint: {endpoint}")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            timeout = httpx.Timeout(30.0, connect=10.0)
            self._client = httpx.AsyncClient(timeout=timeout)
        return self._client
    
    async def connect(self) -> bool:
        """
        Connect to Loki (test connection).
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.endpoint}/ready")
            
            if response.status_code == 200:
                self._is_connected = True
                logger.info(f"✅ Loki connected successfully ({self.endpoint})")
                return True
            else:
                logger.warning(f"⚠️ Loki connection test returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Loki connection failed: {e}")
            self._is_connected = False
            return False
    
    async def test_connection(self) -> bool:
        """Test Loki connection (alias for connect)."""
        return await self.connect()
    
    async def push_logs(self, logs: List[Dict[str, Any]]) -> bool:
        """
        Push logs to Loki via /loki/api/v1/push.
        
        Args:
            logs: List of log entries, each with:
                - timestamp: Unix nanoseconds or ISO 8601 string
                - line: Log line content
                - labels: Dict of label key-value pairs (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            client = await self._get_client()
            
            # Format logs for Loki push API
            # Loki expects: {"streams": [{"stream": {"label": "value"}, "values": [["timestamp", "line"], ...]}]}
            streams = []
            
            for log_entry in logs:
                # Extract labels and values
                labels = log_entry.get("labels", {})
                timestamp = log_entry.get("timestamp")
                line = log_entry.get("line", "")
                
                # Convert timestamp to nanoseconds if needed
                if isinstance(timestamp, str):
                    # ISO 8601 string - convert to nanoseconds
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp_ns = int(dt.timestamp() * 1_000_000_000)
                elif isinstance(timestamp, (int, float)):
                    # Unix timestamp - convert to nanoseconds
                    if timestamp < 1e12:  # Seconds
                        timestamp_ns = int(timestamp * 1_000_000_000)
                    else:  # Already nanoseconds
                        timestamp_ns = int(timestamp)
                else:
                    # Use current time
                    timestamp_ns = int(datetime.utcnow().timestamp() * 1_000_000_000)
                
                # Find or create stream for these labels
                stream_key = json.dumps(labels, sort_keys=True)
                stream = next((s for s in streams if s["stream"] == labels), None)
                
                if stream is None:
                    stream = {"stream": labels, "values": []}
                    streams.append(stream)
                
                # Add log entry to stream
                stream["values"].append([str(timestamp_ns), str(line)])
            
            # Prepare request payload
            payload = {"streams": streams}
            
            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if self.tenant_id:
                headers["X-Scope-OrgID"] = self.tenant_id
            
            # Push to Loki
            response = await client.post(
                f"{self.endpoint}/loki/api/v1/push",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 204:  # Loki returns 204 No Content on success
                logger.debug(f"✅ Pushed {len(logs)} log entries to Loki")
                return True
            else:
                logger.error(f"❌ Failed to push logs to Loki: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error pushing logs to Loki: {e}", exc_info=True)
            return False
    
    async def query_logs(
        self,
        query: str,
        limit: int = 100,
        start: Optional[int] = None,
        end: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Query logs from Loki via /loki/api/v1/query_range.
        
        Args:
            query: LogQL query string (e.g., "{service_name=\"backend\"}")
            limit: Maximum number of log entries to return
            start: Start time (Unix timestamp in nanoseconds, optional)
            end: End time (Unix timestamp in nanoseconds, optional)
        
        Returns:
            Dict containing query results with structure:
            {
                "status": "success",
                "data": {
                    "resultType": "streams",
                    "result": [...]
                }
            }
        """
        try:
            client = await self._get_client()
            
            # Default time range: last hour
            if end is None:
                end = int(datetime.utcnow().timestamp() * 1_000_000_000)
            if start is None:
                start = end - (3600 * 1_000_000_000)  # 1 hour ago
            
            # Prepare query parameters
            params = {
                "query": query,
                "limit": limit,
                "start": start,
                "end": end
            }
            
            # Prepare headers
            headers = {}
            if self.tenant_id:
                headers["X-Scope-OrgID"] = self.tenant_id
            
            # Query Loki
            response = await client.get(
                f"{self.endpoint}/loki/api/v1/query_range",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"✅ Query successful: {len(result.get('data', {}).get('result', []))} streams")
                return {
                    "status": "success",
                    "data": result.get("data", {}),
                    "query": query
                }
            else:
                logger.error(f"❌ Failed to query Loki: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "query": query
                }
                
        except Exception as e:
            logger.error(f"❌ Error querying Loki: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    async def close(self):
        """Close HTTP client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._is_connected = False
            logger.info("✅ Loki adapter closed")

