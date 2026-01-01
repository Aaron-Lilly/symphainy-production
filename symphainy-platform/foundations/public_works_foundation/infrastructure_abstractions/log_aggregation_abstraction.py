#!/usr/bin/env python3
"""
Log Aggregation Abstraction - Infrastructure abstraction for log aggregation

Coordinates log aggregation adapters and handles infrastructure-level concerns like
error handling, retries, logging, and log enrichment for Loki integration.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from foundations.public_works_foundation.abstraction_contracts.log_aggregation_protocol import (
    LogAggregationProtocol, LogEntry, LogQuery
)


class LogAggregationAbstraction:
    """
    Log Aggregation Abstraction - Infrastructure abstraction for log aggregation
    
    Coordinates different log aggregation adapters and handles infrastructure-level concerns.
    This layer provides swappable log aggregation engines and infrastructure coordination.
    
    NOTE: This abstraction accepts a log aggregation adapter via dependency injection.
          All adapter creation happens in Public Works Foundation Service.
    """
    
    def __init__(self,
                 loki_adapter: Any,  # LokiAdapter instance
                 config_adapter=None,
                 service_name: str = "log_aggregation_abstraction",
                 di_container=None):
        """
        Initialize Log Aggregation Abstraction.
        
        Args:
            loki_adapter: Loki adapter instance (required)
            config_adapter: Configuration adapter (optional)
            service_name: Service name for logging (optional)
            di_container: DI Container for logging (required)
        """
        if not loki_adapter:
            raise ValueError("LogAggregationAbstraction requires loki_adapter via dependency injection")
        if not di_container:
            raise ValueError("DI Container is required for LogAggregationAbstraction initialization")
        
        self.service_name = service_name
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(service_name)
        self.config_adapter = config_adapter
        
        # Use injected adapter
        self.adapter = loki_adapter
        self.adapter_type = "loki"
        
        # Infrastructure-level configuration
        self.max_retries = 3
        self.retry_delay = 0.1
        self.timeout = 30
        
        self.logger.info(f"Initialized Log Aggregation Abstraction with {self.adapter_type} adapter")
    
    async def push_logs(self, logs: List[LogEntry]) -> bool:
        """
        Push logs with infrastructure-level coordination.
        
        Args:
            logs: List of log entries to push
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not logs:
                self.logger.warning("⚠️ push_logs called with empty log list")
                return False
            
            self.logger.debug(f"Pushing {len(logs)} log entries with {self.adapter_type}")
            
            # Enrich logs with metadata
            enriched_logs = [self._enrich_log_entry(log_entry) for log_entry in logs]
            
            # Convert to adapter format
            adapter_logs = []
            for log_entry in enriched_logs:
                adapter_log = {
                    "timestamp": log_entry.timestamp.isoformat(),
                    "line": log_entry.line,
                    "labels": log_entry.labels.copy()
                }
                
                # Add standard labels
                if log_entry.service_name:
                    adapter_log["labels"]["service_name"] = log_entry.service_name
                if log_entry.level:
                    adapter_log["labels"]["level"] = log_entry.level
                if log_entry.trace_id:
                    adapter_log["labels"]["trace_id"] = log_entry.trace_id
                if log_entry.request_id:
                    adapter_log["labels"]["request_id"] = log_entry.request_id
                
                adapter_logs.append(adapter_log)
            
            # Push logs with retry logic
            success = await self._execute_with_retry(
                self.adapter.push_logs,
                adapter_logs
            )
            
            if success:
                self.logger.debug(f"✅ Pushed {len(logs)} log entries")
            else:
                self.logger.warning(f"⚠️ Failed to push {len(logs)} log entries")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to push logs: {e}", exc_info=True)
            return False
    
    async def query_logs(self, query: LogQuery) -> List[LogEntry]:
        """
        Query logs with infrastructure-level coordination.
        
        Args:
            query: Log query parameters
            
        Returns:
            List of log entries matching the query
        """
        try:
            self.logger.debug(f"Querying logs with query: {query.query}")
            
            # Convert timestamps to nanoseconds
            start_ns = None
            end_ns = None
            
            if query.start:
                start_ns = int(query.start.timestamp() * 1_000_000_000)
            if query.end:
                end_ns = int(query.end.timestamp() * 1_000_000_000)
            
            # Query with retry logic
            result = await self._execute_with_retry(
                self.adapter.query_logs,
                query.query,
                query.limit,
                start_ns,
                end_ns
            )
            
            if result.get("status") != "success":
                self.logger.warning(f"⚠️ Log query failed: {result.get('error')}")
                return []
            
            # Convert adapter results to LogEntry objects
            log_entries = []
            data = result.get("data", {})
            streams = data.get("result", [])
            
            for stream in streams:
                labels = stream.get("stream", {})
                values = stream.get("values", [])
                
                for timestamp_ns, line in values:
                    # Convert nanoseconds to datetime
                    timestamp = datetime.utcfromtimestamp(int(timestamp_ns) / 1_000_000_000)
                    
                    log_entry = LogEntry(
                        line=line,
                        timestamp=timestamp,
                        labels=labels.copy(),
                        level=labels.get("level"),
                        service_name=labels.get("service_name"),
                        trace_id=labels.get("trace_id"),
                        request_id=labels.get("request_id")
                    )
                    log_entries.append(log_entry)
            
            self.logger.debug(f"✅ Query returned {len(log_entries)} log entries")
            return log_entries
            
        except Exception as e:
            self.logger.error(f"Failed to query logs: {e}", exc_info=True)
            return []
    
    async def search_logs(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search logs with filters.
        
        Args:
            search_params: Search parameters including:
                - service_name: Filter by service name
                - level: Filter by log level
                - time_range: Time range for search (hours or dict with start/end)
                - text: Text search in log lines
        
        Returns:
            Dict containing search results
        """
        try:
            self.logger.debug(f"Searching logs with params: {search_params}")
            
            # Build LogQL query
            query_parts = []
            
            # Service filter
            if search_params.get("service_name"):
                query_parts.append(f'service_name="{search_params["service_name"]}"')
            
            # Level filter
            if search_params.get("level"):
                query_parts.append(f'level="{search_params["level"]}"')
            
            # Text search
            if search_params.get("text"):
                query_parts.append(f'|= "{search_params["text"]}"')
            
            # Build query string - LogQL requires at least one non-empty matcher
            if query_parts:
                query = "{" + ", ".join(query_parts) + "}"
            else:
                # Default query with a matcher that matches all (non-empty)
                query = '{service_name=~".+"}'  # Matches any service_name that exists
            
            # Determine time range
            time_range = search_params.get("time_range", {})
            if isinstance(time_range, dict):
                start = time_range.get("start")
                end = time_range.get("end")
            elif isinstance(time_range, (int, float)):
                # Hours ago
                hours = float(time_range)
                end = datetime.utcnow()
                start = end - timedelta(hours=hours)
            else:
                # Default: last hour
                end = datetime.utcnow()
                start = end - timedelta(hours=1)
            
            # Create query
            log_query = LogQuery(
                query=query,
                limit=search_params.get("limit", 100),
                start=start,
                end=end
            )
            
            # Execute query
            log_entries = await self.query_logs(log_query)
            
            result = {
                "status": "success",
                "query": query,
                "count": len(log_entries),
                "logs": log_entries
            }
            if start and end:
                result["time_range"] = {
                    "start": start.isoformat(),
                    "end": end.isoformat()
                }
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to search logs: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_log_metrics(self, time_range: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get log volume and aggregation metrics.
        
        Args:
            time_range: Time range for metrics (start, end, or hours/days)
        
        Returns:
            Dict containing metrics
        """
        try:
            self.logger.debug("Getting log metrics")
            
            # Determine time range
            if isinstance(time_range, dict):
                start = time_range.get("start")
                end = time_range.get("end")
            elif isinstance(time_range, (int, float)):
                # Hours ago
                hours = float(time_range)
                end = datetime.utcnow()
                start = end - timedelta(hours=hours)
            else:
                # Default: last hour
                end = datetime.utcnow()
                start = end - timedelta(hours=1)
            
            # Query for total volume - LogQL requires at least one non-empty matcher
            # Note: Loki default max_entries_limit_per_query is 5000, so we use 5000
            volume_query = LogQuery(
                query='{service_name=~".+"}',  # Matches any service_name that exists
                limit=5000,  # Max limit (Loki default is 5000)
                start=start,
                end=end
            )
            
            log_entries = await self.query_logs(volume_query)
            
            # Calculate metrics
            by_service = {}
            by_level = {}
            
            for log_entry in log_entries:
                # Count by service
                service = log_entry.service_name or "unknown"
                by_service[service] = by_service.get(service, 0) + 1
                
                # Count by level
                level = log_entry.level or "unknown"
                by_level[level] = by_level.get(level, 0) + 1
            
            result = {
                "status": "success",
                "volume": len(log_entries),
                "by_service": by_service,
                "by_level": by_level
            }
            if start and end:
                result["time_range"] = {
                    "start": start.isoformat(),
                    "end": end.isoformat()
                }
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get log metrics: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _enrich_log_entry(self, log_entry: LogEntry) -> LogEntry:
        """Enrich log entry with default metadata."""
        # Add default namespace if not present
        if "namespace" not in log_entry.labels:
            log_entry.labels["namespace"] = "symphainy-platform"
        
        return log_entry
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.timeout
                )
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    self.logger.debug(f"Retry {attempt + 1}/{self.max_retries} for {func.__name__}")
                else:
                    self.logger.error(f"Failed after {self.max_retries} attempts: {e}")
        
        raise last_exception

