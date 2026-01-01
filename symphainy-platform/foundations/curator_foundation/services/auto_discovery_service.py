#!/usr/bin/env python3
"""
Auto-Discovery Service - Cloud-Ready Service Discovery

Automatically discovers and registers services without manual registration.

WHAT (Curator Micro-Service): I automatically discover and register services
HOW (Service Implementation): I scan service directories and register discovered services
"""

import os
import sys
import importlib
import inspect
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from utilities.configuration.cloud_ready_config import get_cloud_ready_config
from bases.foundation_service_base import FoundationServiceBase

logger = logging.getLogger(__name__)


class AutoDiscoveryService(FoundationServiceBase):
    """
    Auto-Discovery Service - Cloud-Ready Service Discovery
    
    Automatically discovers and registers services without manual registration.
    Scans service directories and registers discovered services with DI Container
    and Curator Foundation.
    
    WHAT (Curator Micro-Service): I automatically discover and register services
    HOW (Service Implementation): I scan service directories and register discovered services
    """
    """
    Auto-Discovery Service - Cloud-Ready Service Discovery
    
    Automatically discovers and registers services without manual registration.
    Scans service directories and registers discovered services with DI Container
    and Curator Foundation.
    """
    
    def __init__(self, di_container, curator_foundation):
        """Initialize Auto-Discovery Service."""
        super().__init__(
            service_name="auto_discovery_service",
            di_container=di_container,
            security_provider=None,
            authorization_guard=None
        )
        self.curator_foundation = curator_foundation
        self.logger = logging.getLogger("AutoDiscoveryService")
        
        # Service discovery patterns
        self.discovery_patterns = [
            {
                "path": "backend/smart_city/services",
                "pattern": "*_service.py",
                "base_class": "SmartCityRoleBase",
                "realm": "smart_city"
            },
            {
                "path": "backend/business_enablement",
                "pattern": "*_service.py",
                "base_class": "RealmServiceBase",
                "realm": "business_enablement"
            },
            {
                "path": "backend/journey",
                "pattern": "*_service.py",
                "base_class": "RealmServiceBase",
                "realm": "journey"
            },
            {
                "path": "backend/solution",
                "pattern": "*_service.py",
                "base_class": "RealmServiceBase",
                "realm": "solution"
            },
            {
                "path": "foundations",
                "pattern": "*_foundation_service.py",
                "base_class": "FoundationServiceBase",
                "realm": "foundation"
            }
        ]
        
        # Discovered services cache
        self.discovered_services: Dict[str, Any] = {}
        
        self.logger.info("🏗️ Auto-Discovery Service initialized")
    
    async def initialize(self):
        """Initialize Auto-Discovery Service."""
        await self.log_operation_with_telemetry("auto_discovery_initialize_start", success=True)
        try:
            await super().initialize()
            self.logger.info("🚀 Auto-Discovery Service initialized")
            self.is_initialized = True
            await self.log_operation_with_telemetry("auto_discovery_initialize_complete", success=True)
        except Exception as e:
            await self.handle_error_with_audit(e, "auto_discovery_initialize")
            self.logger.error(f"❌ Failed to initialize Auto-Discovery Service: {e}")
            raise
    
    async def discover_all_services(self) -> Dict[str, Any]:
        """
        Discover all services automatically.
        
        Returns:
            Dictionary of discovered services
        """
        cloud_ready_config = get_cloud_ready_config()
        if not cloud_ready_config.should_use_auto_discovery():
            self.logger.info("Auto-discovery disabled, skipping...")
            return {}
        
        self.logger.info("🔍 Starting auto-discovery...")
        
        discovered = {}
        
        # Discover foundation services
        foundation_services = await self._discover_foundation_services()
        discovered.update(foundation_services)
        
        # Discover realm services
        realm_services = await self._discover_realm_services()
        discovered.update(realm_services)
        
        # Discover Smart City services
        smart_city_services = await self._discover_smart_city_services()
        discovered.update(smart_city_services)
        
        self.logger.info(f"✅ Auto-discovered {len(discovered)} services")
        return discovered
    
    async def _discover_foundation_services(self) -> Dict[str, Any]:
        """Discover foundation services."""
        self.logger.info("🔍 Discovering foundation services...")
        discovered = {}
        
        try:
            # Foundation services are already initialized in main.py
            # We just need to register them with unified registry if enabled
            foundation_services = [
                "PublicWorksFoundationService",
                "CuratorFoundationService",
                "AgenticFoundationService",
                "ExperienceFoundationService"
            ]
            
            for service_name in foundation_services:
                service = self.di_container.get_foundation_service(service_name)
                if service:
                    discovered[service_name] = {
                        "service": service,
                        "type": "foundation",
                        "realm": "foundation"
                    }
                    self.logger.info(f"✅ Found foundation service: {service_name}")
        
        except Exception as e:
            self.logger.error(f"❌ Error discovering foundation services: {e}")
        
        return discovered
    
    async def _discover_realm_services(self) -> Dict[str, Any]:
        """Discover realm services."""
        self.logger.info("🔍 Discovering realm services...")
        discovered = {}
        
        try:
            # Scan realm service directories
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            backend_path = project_root / "backend"
            
            realms = ["business_enablement", "journey", "solution"]
            
            for realm in realms:
                realm_path = backend_path / realm
                if not realm_path.exists():
                    continue
                
                # Look for service files
                service_files = list(realm_path.rglob("*_service.py"))
                
                for service_file in service_files:
                    try:
                        # Import the module
                        module_path = service_file.relative_to(project_root).with_suffix("")
                        module_name = str(module_path).replace("/", ".")
                        
                        # Skip if already imported or if it's a test file
                        if "test" in module_name or "__pycache__" in module_name:
                            continue
                        
                        # Try to import and find service classes
                        try:
                            module = importlib.import_module(module_name)
                            for name, obj in inspect.getmembers(module, inspect.isclass):
                                # Check if it's a service class
                                if (name.endswith("Service") and 
                                    hasattr(obj, "__init__") and
                                    not name.startswith("_")):
                                    # Check if it inherits from RealmServiceBase
                                    bases = inspect.getmro(obj)
                                    if any("RealmServiceBase" in str(base) for base in bases):
                                        service_name = name
                                        discovered[service_name] = {
                                            "module": module_name,
                                            "class": obj,
                                            "type": "realm",
                                            "realm": realm,
                                            "file": str(service_file)
                                        }
                                        self.logger.info(f"✅ Found realm service: {service_name} in {realm}")
                        except ImportError as e:
                            self.logger.debug(f"⚠️ Could not import {module_name}: {e}")
                            continue
                    
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error processing {service_file}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"❌ Error discovering realm services: {e}")
        
        return discovered
    
    async def _discover_smart_city_services(self) -> Dict[str, Any]:
        """Discover Smart City services."""
        self.logger.info("🔍 Discovering Smart City services...")
        discovered = {}
        
        try:
            # Scan Smart City service directory
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            smart_city_path = project_root / "backend" / "smart_city" / "services"
            
            if not smart_city_path.exists():
                return discovered
            
            # Look for service files
            service_files = list(smart_city_path.rglob("*_service.py"))
            
            for service_file in service_files:
                try:
                    # Import the module
                    module_path = service_file.relative_to(project_root).with_suffix("")
                    module_name = str(module_path).replace("/", ".")
                    
                    # Skip if already imported or if it's a test file
                    if "test" in module_name or "__pycache__" in module_name:
                        continue
                    
                    # Try to import and find service classes
                    try:
                        module = importlib.import_module(module_name)
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            # Check if it's a service class
                            if (name.endswith("Service") and 
                                hasattr(obj, "__init__") and
                                not name.startswith("_")):
                                # Check if it inherits from SmartCityRoleBase
                                bases = inspect.getmro(obj)
                                if any("SmartCityRoleBase" in str(base) for base in bases):
                                    service_name = name
                                    discovered[service_name] = {
                                        "module": module_name,
                                        "class": obj,
                                        "type": "smart_city",
                                        "realm": "smart_city",
                                        "file": str(service_file)
                                    }
                                    self.logger.info(f"✅ Found Smart City service: {service_name}")
                    except ImportError as e:
                        self.logger.debug(f"⚠️ Could not import {module_name}: {e}")
                        continue
                
                except Exception as e:
                    self.logger.warning(f"⚠️ Error processing {service_file}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"❌ Error discovering Smart City services: {e}")
        
        return discovered
    
    async def register_discovered_services(self, discovered_services: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register discovered services with DI Container and Curator Foundation.
        
        Args:
            discovered_services: Dictionary of discovered services
        
        Returns:
            Dictionary with registration results
        """
        results = {
            "registered": [],
            "failed": [],
            "skipped": []
        }
        
        for service_name, service_info in discovered_services.items():
            try:
                # Check if service is already registered
                existing = self.di_container.get_foundation_service(service_name)
                if existing:
                    self.logger.debug(f"⚠️ Service {service_name} already registered, skipping...")
                    results["skipped"].append(service_name)
                    continue
                
                # For now, we just log discovered services
                # Actual instantiation and registration happens during service initialization
                # This is a discovery phase, not an instantiation phase
                self.logger.info(f"📝 Discovered service: {service_name} ({service_info.get('type')})")
                results["registered"].append(service_name)
                
                # Store in cache
                self.discovered_services[service_name] = service_info
                
            except Exception as e:
                self.logger.error(f"❌ Failed to register discovered service {service_name}: {e}")
                results["failed"].append({"service": service_name, "error": str(e)})
        
        return results

