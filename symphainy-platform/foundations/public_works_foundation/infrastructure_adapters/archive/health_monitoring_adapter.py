#!/usr/bin/env python3
"""
Health Monitoring Infrastructure Adapter

Raw system monitoring bindings for health monitoring and diagnostics.
Thin wrapper around psutil with no business logic.
"""

import logging
import psutil
from typing import Dict, Any, Optional


class HealthMonitoringAdapter:
    """Raw health monitoring adapter - thin wrapper around psutil."""
    
    def __init__(self, **kwargs):
        """
        Initialize health monitoring adapter.
        
        Args:
            **kwargs: Additional configuration
        """
        self.logger = logging.getLogger("HealthMonitoringAdapter")
        self.logger.info("✅ Health monitoring adapter initialized")
    
    def get_cpu_percent(self) -> float:
        """Get CPU usage percentage."""
        return psutil.cpu_percent()
    
    def get_cpu_count(self) -> int:
        """Get CPU count."""
        return psutil.cpu_count()
    
    def get_cpu_freq(self) -> Optional[float]:
        """Get CPU frequency."""
        freq = psutil.cpu_freq()
        return freq.current if freq else None
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information."""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used
        }
    
    def get_swap_info(self) -> Dict[str, Any]:
        """Get swap information."""
        swap = psutil.swap_memory()
        return {
            "total": swap.total,
            "used": swap.used,
            "percent": swap.percent
        }
    
    def get_disk_usage(self, path: str = '/') -> Dict[str, Any]:
        """Get disk usage for path."""
        disk = psutil.disk_usage(path)
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free
        }
    
    def get_network_io(self) -> Dict[str, Any]:
        """Get network I/O counters."""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    
    def get_process_count(self) -> int:
        """Get process count."""
        return len(psutil.pids())
    
    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get process information by PID."""
        try:
            process = psutil.Process(pid)
            return {
                "pid": process.pid,
                "name": process.name(),
                "status": process.status(),
                "cpu_percent": process.cpu_percent(),
                "memory_info": process.memory_info()._asdict(),
                "create_time": process.create_time()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None