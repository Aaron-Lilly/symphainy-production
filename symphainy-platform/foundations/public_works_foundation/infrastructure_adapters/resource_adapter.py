#!/usr/bin/env python3
"""
Resource Infrastructure Adapter

Raw resource allocation bindings for infrastructure management.
Thin wrapper around resource management SDK with no business logic.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import logging
import uuid
import psutil
import os


class ResourceAdapter:
    """Raw resource adapter for infrastructure management."""
    
    def __init__(self, **kwargs):
        """
        Initialize resource adapter.
        
        Args:
            **kwargs: Additional configuration
        """
        self.logger = logging.getLogger("ResourceAdapter")
        
        # Resource limits
        self.cpu_limit = kwargs.get("cpu_limit", 80.0)  # CPU percentage
        self.memory_limit = kwargs.get("memory_limit", 80.0)  # Memory percentage
        self.disk_limit = kwargs.get("disk_limit", 80.0)  # Disk percentage
        
        # Initialize resource monitoring
        self._initialize_resource_monitoring()
    
    def _initialize_resource_monitoring(self):
        """Initialize resource monitoring."""
        try:
            self.logger.info("✅ Resource adapter initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize resource monitoring: {e}")
    
    def get_system_resources(self) -> Dict[str, Any]:
        """
        Get current system resource usage.
        
        Returns:
            Dict: System resource information
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total = memory.total
            memory_available = memory.available
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_total = disk.total
            disk_available = disk.free
            
            # Network usage
            network = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "limit": self.cpu_limit,
                    "status": "healthy" if cpu_percent < self.cpu_limit else "warning"
                },
                "memory": {
                    "percent": memory_percent,
                    "total": memory_total,
                    "available": memory_available,
                    "limit": self.memory_limit,
                    "status": "healthy" if memory_percent < self.memory_limit else "warning"
                },
                "disk": {
                    "percent": disk_percent,
                    "total": disk_total,
                    "available": disk_available,
                    "limit": self.disk_limit,
                    "status": "healthy" if disk_percent < self.disk_limit else "warning"
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system resources: {e}")
            return {"error": str(e), "success": False}
    
    def get_process_resources(self, pid: int = None) -> Dict[str, Any]:
        """
        Get process resource usage.
        
        Args:
            pid: Process ID (None for current process)
            
        Returns:
            Dict: Process resource information
        """
        try:
            if pid is None:
                process = psutil.Process()
            else:
                process = psutil.Process(pid)
            
            # Process info
            process_info = {
                "pid": process.pid,
                "name": process.name(),
                "status": process.status(),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            }
            
            # CPU usage
            cpu_percent = process.cpu_percent()
            cpu_times = process.cpu_times()
            
            # Memory usage
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # File descriptors
            try:
                num_fds = process.num_fds()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                num_fds = 0
            
            # Threads
            try:
                num_threads = process.num_threads()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                num_threads = 0
            
            return {
                "process": process_info,
                "cpu": {
                    "percent": cpu_percent,
                    "user_time": cpu_times.user,
                    "system_time": cpu_times.system
                },
                "memory": {
                    "rss": memory_info.rss,
                    "vms": memory_info.vms,
                    "percent": memory_percent
                },
                "resources": {
                    "file_descriptors": num_fds,
                    "threads": num_threads
                },
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get process resources: {e}")
            return {"error": str(e), "success": False}
    
    def allocate_resources(self, resource_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allocate resources for a task.
        
        Args:
            resource_request: Resource allocation request
            
        Returns:
            Dict: Resource allocation result
        """
        try:
            # Check available resources
            system_resources = self.get_system_resources()
            
            # Validate resource request
            cpu_request = resource_request.get("cpu", 0)
            memory_request = resource_request.get("memory", 0)
            disk_request = resource_request.get("disk", 0)
            
            # Check if resources are available
            cpu_available = 100 - system_resources["cpu"]["percent"]
            memory_available = 100 - system_resources["memory"]["percent"]
            disk_available = 100 - system_resources["disk"]["percent"]
            
            if (cpu_request > cpu_available or 
                memory_request > memory_available or 
                disk_request > disk_available):
                return {
                    "allocated": False,
                    "reason": "Insufficient resources",
                    "available": {
                        "cpu": cpu_available,
                        "memory": memory_available,
                        "disk": disk_available
                    },
                    "requested": resource_request
                }
            
            # Allocate resources
            allocation_id = str(uuid.uuid4())
            
            return {
                "allocated": True,
                "allocation_id": allocation_id,
                "resources": {
                    "cpu": cpu_request,
                    "memory": memory_request,
                    "disk": disk_request
                },
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to allocate resources: {e}")
            return {"error": str(e), "allocated": False}
    
    def deallocate_resources(self, allocation_id: str) -> bool:
        """
        Deallocate resources.
        
        Args:
            allocation_id: Resource allocation ID
            
        Returns:
            bool: Success status
        """
        try:
            # In a real implementation, this would track and release resources
            self.logger.info(f"✅ Resources deallocated for {allocation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deallocate resources {allocation_id}: {e}")
            return False
    
    def get_resource_limits(self) -> Dict[str, Any]:
        """
        Get current resource limits.
        
        Returns:
            Dict: Resource limits
        """
        try:
            return {
                "cpu_limit": self.cpu_limit,
                "memory_limit": self.memory_limit,
                "disk_limit": self.disk_limit,
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get resource limits: {e}")
            return {"error": str(e)}
    
    def set_resource_limits(self, limits: Dict[str, Any]) -> bool:
        """
        Set resource limits.
        
        Args:
            limits: New resource limits
            
        Returns:
            bool: Success status
        """
        try:
            if "cpu_limit" in limits:
                self.cpu_limit = limits["cpu_limit"]
            
            if "memory_limit" in limits:
                self.memory_limit = limits["memory_limit"]
            
            if "disk_limit" in limits:
                self.disk_limit = limits["disk_limit"]
            
            self.logger.info("✅ Resource limits updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set resource limits: {e}")
            return False
    
    def monitor_resources(self, duration: int = 60, interval: int = 5) -> List[Dict[str, Any]]:
        """
        Monitor resources over time.
        
        Args:
            duration: Monitoring duration in seconds
            interval: Sampling interval in seconds
            
        Returns:
            List: Resource monitoring data
        """
        try:
            import time
            
            monitoring_data = []
            end_time = time.time() + duration
            
            while time.time() < end_time:
                # Get current resources
                resources = self.get_system_resources()
                resources["timestamp"] = datetime.now().isoformat()
                
                monitoring_data.append(resources)
                
                # Wait for next sample
                time.sleep(interval)
            
            return monitoring_data
            
        except Exception as e:
            self.logger.error(f"Failed to monitor resources: {e}")
            return []
    
    def get_resource_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get resource usage history.
        
        Args:
            hours: Number of hours to retrieve
            
        Returns:
            List: Resource history
        """
        try:
            # In a real implementation, this would retrieve from a time-series database
            # For now, return empty list
            return []
            
        except Exception as e:
            self.logger.error(f"Failed to get resource history: {e}")
            return []
    
    def optimize_resources(self) -> Dict[str, Any]:
        """
        Optimize resource allocation.
        
        Returns:
            Dict: Optimization recommendations
        """
        try:
            # Get current resources
            resources = self.get_system_resources()
            
            recommendations = []
            
            # CPU optimization
            if resources["cpu"]["percent"] > 80:
                recommendations.append({
                    "type": "cpu",
                    "action": "reduce_cpu_load",
                    "priority": "high"
                })
            
            # Memory optimization
            if resources["memory"]["percent"] > 80:
                recommendations.append({
                    "type": "memory",
                    "action": "free_memory",
                    "priority": "high"
                })
            
            # Disk optimization
            if resources["disk"]["percent"] > 80:
                recommendations.append({
                    "type": "disk",
                    "action": "cleanup_disk",
                    "priority": "high"
                })
            
            return {
                "recommendations": recommendations,
                "current_resources": resources,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to optimize resources: {e}")
            return {"error": str(e)}



