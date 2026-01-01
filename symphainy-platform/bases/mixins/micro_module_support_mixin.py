#!/usr/bin/env python3
"""
Micro Module Support Mixin

Focused mixin for micro-module support - extracts module loading and management
functionality from base classes into a reusable, testable component.

WHAT (Micro Module Support Role): I provide micro-module loading and management patterns
HOW (Micro Module Support Mixin): I centralize module discovery and instantiation
"""

from typing import Dict, Any, Optional
import os
import importlib
import importlib.util
from pathlib import Path


class MicroModuleSupportMixin:
    """
    Mixin for micro-module support patterns.
    
    Provides consistent module loading, discovery, and instantiation across
    all services with proper error handling and caching.
    """
    
    def _init_micro_module_support(self, service_name: str, di_container: Optional[Any] = None):
        """Initialize micro-module support patterns."""
        self.service_name = service_name
        
        # Get logger from DI Container if available
        if di_container:
            if not hasattr(di_container, 'get_logger'):
                raise RuntimeError(
                    f"DI Container does not have get_logger method. "
                    f"This indicates a platform initialization failure or incorrect DI Container instance."
                )
            
            try:
                logger_service = di_container.get_logger(f"{self.__class__.__name__}.micro_modules")
                if not logger_service:
                    raise RuntimeError(
                        f"DI Container.get_logger() returned None. "
                        f"Logging service should be available - this indicates a platform initialization failure."
                    )
                self.logger = logger_service
            except Exception as e:
                raise RuntimeError(
                    f"Failed to get logger from DI Container: {e}. "
                    f"DI Container must initialize logging utility before services can use it. "
                    f"This indicates a platform initialization failure."
                ) from e
        else:
            # If no DI Container, this is a bootstrap scenario - fail fast
            raise ValueError(
                "DI Container is required for MicroModuleSupportMixin initialization. "
                "Services must be created with a valid DI Container instance."
            )
        
        # Micro-module management
        self.modules = {}
        self._micro_module_path = None
        
        # Detect modules directory
        self._detect_modules_directory()
        
        self.logger.debug("Micro-module support mixin initialized")
    
    def _detect_modules_directory(self):
        """Detect if service has a modules/ directory."""
        try:
            # Strategy 1: Use service_name to construct path (convert ServiceName to service_name)
            # e.g., "SecurityGuardService" -> "security_guard"
            service_name_lower = self.service_name.lower()
            # Remove "Service" suffix if present
            if service_name_lower.endswith("service"):
                service_name_lower = service_name_lower[:-7]  # Remove "service"
            # Convert CamelCase to snake_case (simple heuristic)
            import re
            service_dir_name = re.sub(r'(?<!^)(?=[A-Z])', '_', service_name_lower).lower()
            
            # Try multiple path strategies
            project_root = None
            
            # Strategy 1a: Find project root from current working directory
            current = Path.cwd().resolve()
            if (current / "foundations").exists() and (current / "main.py").exists():
                project_root = current
            else:
                # Strategy 1b: Find project root from this file's location
                # This file is at: bases/mixins/micro_module_support_mixin.py
                # Project root is: symphainy-platform/
                mixin_file = Path(__file__).resolve()
                # Go up: bases/mixins -> bases -> symphainy-platform
                potential_root = mixin_file.parent.parent.parent
                if (potential_root / "foundations").exists() and (potential_root / "main.py").exists():
                    project_root = potential_root
            
            if not project_root:
                self.logger.warning(f"Could not determine project root for {self.service_name}")
                return
            
            # Construct modules directory path
            modules_dir = project_root / "backend" / "smart_city" / "services" / service_dir_name / "modules"
            
            if modules_dir.exists() and modules_dir.is_dir():
                self._micro_module_path = str(modules_dir)
                self.logger.info(f"Found micro-modules directory: {self._micro_module_path}")
            else:
                # Strategy 2: Try using the class's __module__ to find the service file
                if hasattr(self, '__class__') and hasattr(self.__class__, '__module__'):
                    try:
                        import sys
                        module = sys.modules.get(self.__class__.__module__)
                        if module and hasattr(module, '__file__'):
                            service_file = Path(module.__file__).resolve()
                            # Service file is at: backend/smart_city/services/security_guard/security_guard_service.py
                            # Modules dir is at: backend/smart_city/services/security_guard/modules/
                            service_dir = service_file.parent
                            modules_dir = service_dir / "modules"
                            if modules_dir.exists() and modules_dir.is_dir():
                                self._micro_module_path = str(modules_dir)
                                self.logger.info(f"Found micro-modules directory via __module__: {self._micro_module_path}")
                                return
                    except Exception as e2:
                        self.logger.debug(f"Failed to use __module__ strategy: {e2}")
                
                self.logger.debug(f"No micro-modules directory found for {self.service_name} at {modules_dir}")
                
        except Exception as e:
            self.logger.error(f"Failed to detect modules directory: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def load_micro_module(self, module_name: str) -> bool:
        """Load micro-module dynamically."""
        try:
            if not self._micro_module_path:
                self.logger.warning(f"No micro-modules directory available for {self.service_name}")
                return False
            
            module_path = Path(self._micro_module_path) / f"{module_name}.py"
            self.logger.info(f"Attempting to load module {module_name} from {module_path}")
            
            if not module_path.exists():
                self.logger.error(f"Micro-module {module_name} not found at {module_path}")
                return False
            
            # Load module dynamically
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if not spec or not spec.loader:
                self.logger.error(f"Failed to create spec for {module_name} at {module_path}")
                return False
            
            self.logger.info(f"Loading module {module_name}...")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.logger.info(f"Module {module_name} executed successfully")
            
            # Store module reference
            self.modules[module_name] = module
            
            self.logger.info(f"Loaded micro-module: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load micro-module {module_name}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """Get micro-module instance."""
        # Use print as fallback to ensure we see what's happening
        print(f"[DEBUG] get_module called for: {module_name}", flush=True)
        try:
            # Logger should be available (set during initialization)
            if not hasattr(self, 'logger') or not self.logger:
                raise RuntimeError(
                    f"Logger not available in MicroModuleSupportMixin. "
                    f"This indicates a platform initialization failure. "
                    f"DI Container must initialize logging utility before services can use it."
                )
            
            # Ensure modules dict is initialized
            if not hasattr(self, 'modules'):
                self.modules = {}
                print(f"[DEBUG] Initialized modules dict", flush=True)
            
            print(f"[DEBUG] About to log with logger: {self.logger}", flush=True)
            self.logger.info(f"get_module called for: {module_name}")
            self.logger.info(f"Current modules cache: {list(self.modules.keys())}")
            print(f"[DEBUG] Logged successfully", flush=True)
            
            if module_name not in self.modules:
                # Try to load the module if not already loaded
                self.logger.info(f"Module {module_name} not in cache, loading...")
                load_result = self.load_micro_module(module_name)
                self.logger.info(f"load_micro_module returned: {load_result}")
                if not load_result:
                    self.logger.error(f"Failed to load module {module_name}")
                    return None
            
            module = self.modules[module_name]
            self.logger.info(f"Module {module_name} loaded, looking for instantiation pattern...")
            
            # Look for a main class or function to instantiate
            # Pass self (service instance) to module constructor/factory
            if hasattr(module, 'main'):
                # main() function takes service_instance
                self.logger.info(f"Found main() function in {module_name}")
                return module.main(self)
            elif hasattr(module, module_name.title()):
                # Class matching module name (e.g., Initialization for initialization.py)
                self.logger.info(f"Found class {module_name.title()} in {module_name}")
                ModuleClass = getattr(module, module_name.title())
                self.logger.info(f"Instantiating {module_name.title()} class with service instance...")
                instance = ModuleClass(self)
                self.logger.info(f"Successfully instantiated {module_name.title()} class")
                return instance
            elif hasattr(module, module_name):
                # Class matching module name exactly
                self.logger.info(f"Found class {module_name} in {module_name}")
                ModuleClass = getattr(module, module_name)
                self.logger.info(f"Instantiating {module_name} class with service instance...")
                instance = ModuleClass(self)
                self.logger.info(f"Successfully instantiated {module_name} class")
                return instance
            else:
                # Try to find any class that looks like it could be the module class
                # Look for class names that match common patterns
                attrs = [attr for attr in dir(module) if not attr.startswith('_')]
                self.logger.info(f"Available attributes in {module_name}: {attrs}")
                
                # Try common class name patterns
                possible_class_names = [
                    module_name.replace('_', '').title(),  # soa_mcp -> SoaMcp
                    ''.join(word.capitalize() for word in module_name.split('_')),  # soa_mcp -> SoaMcp
                    module_name.title().replace('_', ''),  # soa_mcp -> SoaMcp
                ]
                
                for class_name in possible_class_names:
                    if hasattr(module, class_name):
                        try:
                            ModuleClass = getattr(module, class_name)
                            if isinstance(ModuleClass, type):  # It's a class
                                self.logger.info(f"Found class {class_name} via pattern matching, instantiating...")
                                instance = ModuleClass(self)
                                self.logger.info(f"Successfully instantiated {class_name} class")
                                return instance
                        except Exception as e:
                            self.logger.warning(f"Failed to instantiate {class_name}: {e}")
                            continue
                
                # Return the module itself if no specific instantiation pattern
                self.logger.warning(f"No instantiation pattern found, returning module {module_name} directly")
                return module
                
        except Exception as e:
            self.logger.error(f"Failed to get micro-module {module_name}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    def list_available_modules(self) -> list:
        """List all available micro-modules."""
        try:
            if not self._micro_module_path:
                return []
            
            modules_dir = Path(self._micro_module_path)
            if not modules_dir.exists():
                return []
            
            modules = []
            for file_path in modules_dir.glob("*.py"):
                if file_path.name != "__init__.py":
                    module_name = file_path.stem
                    modules.append(module_name)
            
            return modules
            
        except Exception as e:
            self.logger.error(f"Failed to list available modules: {e}")
            return []
    
    def is_module_loaded(self, module_name: str) -> bool:
        """Check if micro-module is loaded."""
        return module_name in self.modules
    
    def unload_module(self, module_name: str) -> bool:
        """Unload micro-module."""
        try:
            if module_name in self.modules:
                del self.modules[module_name]
                self.logger.info(f"Unloaded micro-module: {module_name}")
                return True
            else:
                self.logger.warning(f"Micro-module {module_name} not loaded")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unload micro-module {module_name}: {e}")
            return False
    
    def get_loaded_modules(self) -> list:
        """Get list of loaded micro-modules."""
        return list(self.modules.keys())
    
    def has_micro_modules(self) -> bool:
        """Check if service has micro-modules support."""
        return self._micro_module_path is not None

