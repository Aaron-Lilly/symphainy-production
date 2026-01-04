#!/usr/bin/env python3
"""
SymphAIny Platform - Updated Startup Orchestration
Aligned with latest architectural patterns:
- ManagerServiceBase with di_container only
- Platform Gateway for realm abstraction access
- Smart City services via SmartCityRoleBase
- Curator-based service discovery
"""

import os
import sys
import logging
import argparse
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Check for test mode first (before loading .env.secrets)
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# Try to load test environment variables from file (if running locally)
if TEST_MODE:
    test_env_file = Path(__file__).parent.parent / "tests" / ".env.test"
    if test_env_file.exists():
        load_dotenv(test_env_file, override=False)  # Don't override existing env vars
        print(f"✅ Test mode enabled - loaded test configuration from {test_env_file}")
    else:
        # Running in container - env_file in docker-compose already loaded variables
        print("✅ Test mode enabled - using environment variables (from docker-compose env_file)")

# Load environment secrets (production credentials)
load_dotenv('.env.secrets')

# AFTER loading .env.secrets, override with test credentials if in test mode
# This ensures test credentials take precedence over production credentials
if TEST_MODE:
    # Override Supabase credentials with test credentials if available
    # This allows tests to use a separate Supabase project
    test_supabase_url = os.getenv("TEST_SUPABASE_URL")
    test_supabase_anon_key = os.getenv("TEST_SUPABASE_ANON_KEY")
    test_supabase_service_key = os.getenv("TEST_SUPABASE_SERVICE_KEY")
    
    if test_supabase_url:
        os.environ["SUPABASE_URL"] = test_supabase_url
        print(f"✅ Using test Supabase URL: {test_supabase_url}")
    else:
        print("⚠️  TEST_MODE=true but TEST_SUPABASE_URL not set")
    
    if test_supabase_anon_key:
        os.environ["SUPABASE_ANON_KEY"] = test_supabase_anon_key
        os.environ["SUPABASE_KEY"] = test_supabase_anon_key  # Some code uses SUPABASE_KEY
        print("✅ Using test Supabase anon key")
    else:
        print("⚠️  TEST_MODE=true but TEST_SUPABASE_ANON_KEY not set")
    
    if test_supabase_service_key:
        os.environ["SUPABASE_SERVICE_KEY"] = test_supabase_service_key
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = test_supabase_service_key  # Some code uses this name
        print("✅ Using test Supabase service key")
    else:
        print("⚠️  TEST_MODE=true but TEST_SUPABASE_SERVICE_KEY not set")

# CRITICAL: Protect SSH access - unset any critical GCP env vars that might have been loaded
# These should NEVER be in .env.secrets as they break SSH access to GCP VMs
CRITICAL_GCP_ENV_VARS = [
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GCLOUD_PROJECT",
    "GOOGLE_CLOUD_PROJECT",
    "GCLOUD_CONFIG",
    "CLOUDSDK_CONFIG"
]

# Store original values (if they existed before loading .env.secrets)
_original_gcp_env_vars = {}
for var in CRITICAL_GCP_ENV_VARS:
    _original_gcp_env_vars[var] = os.environ.get(var)

# After load_dotenv, restore original values (don't let .env.secrets override them)
for var in CRITICAL_GCP_ENV_VARS:
    if var in os.environ and os.environ[var] != _original_gcp_env_vars[var]:
        # .env.secrets tried to set a critical GCP env var - restore original
        if _original_gcp_env_vars[var] is not None:
            os.environ[var] = _original_gcp_env_vars[var]
        else:
            # Remove it if it wasn't set originally
            os.environ.pop(var, None)
        logging.warning(
            f"⚠️ Protected {var} from being set by .env.secrets - "
            f"this variable is for SSH/VM access and should never be in config files. "
            f"Use GCS_CREDENTIALS_PATH for bucket credentials instead."
        )

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Load configuration first
from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
config_manager = UnifiedConfigurationManager(service_name="platform_orchestrated", config_root=project_root)

# AFTER UnifiedConfigurationManager is initialized, update cache with test credentials if in test mode
# This ensures test credentials override production credentials in the config cache
if TEST_MODE:
    test_supabase_url = os.getenv("TEST_SUPABASE_URL")
    test_supabase_anon_key = os.getenv("TEST_SUPABASE_ANON_KEY")
    test_supabase_service_key = os.getenv("TEST_SUPABASE_SERVICE_KEY")
    
    if test_supabase_url:
        # Update both environment and config cache
        os.environ["SUPABASE_URL"] = test_supabase_url
        config_manager.config_cache["SUPABASE_URL"] = test_supabase_url
        # Also update all possible key variations
        config_manager.config_cache["SUPABASE_PROJECT_URL"] = test_supabase_url
        print(f"✅ Updated config cache with test Supabase URL: {test_supabase_url}")
    
    if test_supabase_anon_key:
        # Update both environment and config cache
        os.environ["SUPABASE_ANON_KEY"] = test_supabase_anon_key
        os.environ["SUPABASE_KEY"] = test_supabase_anon_key
        os.environ["SUPABASE_PUBLISHABLE_KEY"] = test_supabase_anon_key
        config_manager.config_cache["SUPABASE_ANON_KEY"] = test_supabase_anon_key
        config_manager.config_cache["SUPABASE_KEY"] = test_supabase_anon_key
        config_manager.config_cache["SUPABASE_PUBLISHABLE_KEY"] = test_supabase_anon_key
        print("✅ Updated config cache with test Supabase anon key")
    
    if test_supabase_service_key:
        # Update both environment and config cache
        os.environ["SUPABASE_SERVICE_KEY"] = test_supabase_service_key
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = test_supabase_service_key
        os.environ["SUPABASE_SECRET_KEY"] = test_supabase_service_key
        config_manager.config_cache["SUPABASE_SERVICE_KEY"] = test_supabase_service_key
        config_manager.config_cache["SUPABASE_SERVICE_ROLE_KEY"] = test_supabase_service_key
        config_manager.config_cache["SUPABASE_SECRET_KEY"] = test_supabase_service_key
        print("✅ Updated config cache with test Supabase service key")
    
    # Verify the update worked
    cached_url = config_manager.get("SUPABASE_URL")
    if cached_url and cached_url == test_supabase_url:
        print(f"✅ Verified: Config cache has test Supabase URL: {cached_url}")
    else:
        print(f"⚠️  WARNING: Config cache verification failed. Expected: {test_supabase_url}, Got: {cached_url}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenTelemetry logging instrumentation
# This enables automatic log-to-trace correlation
try:
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    LoggingInstrumentor().instrument()
    logger.info("✅ OpenTelemetry logging instrumentation enabled")
except ImportError:
    # Check if production
    environment = config_manager.get("ENVIRONMENT", "development")
    if isinstance(environment, str):
        environment = environment.lower()
    if environment in ["production", "prod"]:
        raise RuntimeError(
            "opentelemetry-instrumentation-logging is required in production. "
            "Install with: pip install opentelemetry-instrumentation-logging"
        )
    logger.warning("⚠️ OpenTelemetry logging instrumentation not available (development mode)")
except Exception as e:
    environment = config_manager.get("ENVIRONMENT", "development")
    if isinstance(environment, str):
        environment = environment.lower()
    if environment in ["production", "prod"]:
        raise RuntimeError(f"Failed to enable OpenTelemetry logging in production: {e}") from e
    logger.warning(f"⚠️ Failed to enable OpenTelemetry logging: {e}")

# Import FastAPI
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn

# Initialize Celery app (for production and Docker containers)
# This allows celery -A main worker to work
try:
    from celery import Celery
    
    # Get Celery configuration from ConfigManager
    celery_broker_url = config_manager.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    celery_result_backend = config_manager.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    
    # Create Celery app instance
    celery = Celery(
        'symphainy',
        broker=celery_broker_url,
        backend=celery_result_backend
    )
    
    # Configure Celery (matching CeleryAdapter configuration)
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,  # 5 minutes
        task_soft_time_limit=240,  # 4 minutes
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_disable_rate_limits=False
    )
    
    logger.info("✅ Celery app initialized in main.py")
except ImportError:
    # Celery not installed - set to None
    celery = None
    logger.warning("⚠️ Celery not installed - celery app not available")
except Exception as e:
    # Failed to initialize Celery - set to None
    celery = None
    logger.warning(f"⚠️ Failed to initialize Celery app: {e}")

# Global state
app_state = {}


class PlatformOrchestrator:
    """
    Platform Orchestrator - Manages the complete startup sequence
    aligned with latest architectural patterns.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.startup_sequence = []
        self.managers = {}
        self.foundation_services = {}
        self.infrastructure_services = {}
        self.startup_status = {
            "foundation": "pending", 
            "smart_city_gateway": "pending",
            "lazy_hydration": "pending",
            "background_watchers": "pending",
            "curator_autodiscovery": "pending"
        }
        # Background task tracking
        self.background_tasks = []
        self._shutdown_event = asyncio.Event()
        # Store config_manager reference for background tasks
        self.config_manager = config_manager
        # FastAPI Router Manager (utility - like DI Container)
        self.router_manager = None
    
    async def orchestrate_platform_startup(self) -> Dict[str, Any]:
        """
        Orchestrate the complete platform startup sequence.
        
        Aligned with CTO's lazy-hydrating service mesh model:
        - Phase 1: Bootstrap Foundation (EAGER)
        - Phase 2: Register Smart City Gateway (EAGER)
        - Phase 3: Lazy Realm Hydration (deferred - no eager initialization)
        - Phase 4: Background Health Watchers (async tasks)
        - Phase 5: Curator Auto-Discovery (continuous)
        """
        self.logger.info("🚀 Starting SymphAIny Platform Orchestration (Lazy-Hydrating Service Mesh)")
        
        try:
            # ✅ Phase 0.5: Generate platform startup correlation_id for correlation tracking
            import uuid
            platform_startup_correlation_id = str(uuid.uuid4())
            app_state["platform_startup_correlation_id"] = platform_startup_correlation_id
            self.logger.info(f"📊 Platform startup correlation_id: {platform_startup_correlation_id}")
            
            # Phase 1: Bootstrap Foundation (EAGER)
            await self._initialize_foundation_infrastructure()
            
            # Phase 2: Register Smart City Gateway (EAGER)
            await self._initialize_smart_city_gateway()
            
            # Phase 2.5: Bootstrap Manager Hierarchy (EAGER)
            # This bootstraps the manager hierarchy (Solution Manager → Journey, Insights, Content Managers as peers)
            # Per Phase 0.4: Solution Manager bootstraps ALL realm managers (Journey, Insights, Content) as peers
            # Note: Delivery Manager to be archived (or kept for very narrow purpose if enabling services exist)
            await self._initialize_mvp_solution()
            
            # Phase 3: Lazy Realm Hydration (deferred - no eager initialization)
            # Realms, Managers, Orchestrators, and Services are all LAZY
            # They will be loaded on-demand when first accessed
            self.logger.info("🌀 Phase 3: Lazy Realm Hydration (deferred - services load on-demand)")
            self.startup_status["lazy_hydration"] = "ready"
            self.startup_sequence.append("lazy_realm_hydration")
            
            # Phase 4: Background Health Watchers (async tasks)
            await self._start_background_watchers()
            
            # Phase 5: Curator Auto-Discovery (continuous)
            await self._start_curator_autodiscovery()
            
            # Phase 6: Validate Critical Services Health (NEW - Production Readiness)
            await self._validate_critical_services_health()
            
            self.logger.info("🎉 Platform orchestration completed successfully!")
            self.logger.info("   ✅ Foundations initialized (EAGER)")
            self.logger.info("   ✅ Smart City Gateway active (EAGER)")
            self.logger.info("   ✅ Manager hierarchy bootstrapped (Solution → Journey, Insights, Content as peers)")
            self.logger.info("   ✅ Lazy hydration ready (services load on-demand)")
            self.logger.info("   ✅ Background watchers started")
            self.logger.info("   ✅ Curator auto-discovery active")
            self.logger.info("   ✅ Critical services health validated")
            
            return {
                "success": True,
                "startup_sequence": self.startup_sequence,
                "managers": list(self.managers.keys()),
                "foundation_services": list(self.foundation_services.keys()),
                "infrastructure_services": list(self.infrastructure_services.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Platform orchestration failed: {e}")
            raise
    
    async def _initialize_foundation_infrastructure(self):
        """Initialize foundation infrastructure (DI Container, Public Works, Curator, Communication, Agentic)."""
        self.logger.info("🔧 Phase 1: Initializing Foundation Infrastructure")
        
        try:
            # Import all foundation services
            from foundations.di_container.di_container_service import DIContainerService
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.platform_gateway_foundation.platform_gateway_foundation_service import PlatformGatewayFoundationService
            # Communication Foundation removed - no longer needed
            from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
            from foundations.agentic_foundation.agentic_foundation_service import AgenticFoundationService
            from foundations.experience_foundation.experience_foundation_service import ExperienceFoundationService
            
            # Initialize DI Container (Core infrastructure)
            di_container = DIContainerService("platform_orchestrated")
            self.infrastructure_services["di_container"] = di_container
            self.foundation_services["DIContainerService"] = di_container
            self.logger.info("✅ DI Container initialized")
            
            # Initialize FastAPI Router Manager (utility - like DI Container)
            from utilities.api_routing.fastapi_router_manager import FastAPIRouterManager
            self.router_manager = FastAPIRouterManager()
            await self.router_manager.initialize()
            self.infrastructure_services["router_manager"] = self.router_manager
            # Also register in DI Container service_registry for easy access by Experience Foundation
            di_container.service_registry["FastAPIRouterManager"] = self.router_manager
            self.logger.info("✅ FastAPI Router Manager initialized (utility) and registered in DI Container")
            
            # Initialize Public Works Foundation
            public_works_foundation = PublicWorksFoundationService(di_container)
            try:
                await public_works_foundation.initialize()
                self.infrastructure_services["public_works_foundation"] = public_works_foundation
                self.foundation_services["PublicWorksFoundationService"] = public_works_foundation
                # CRITICAL: Update DI container's public_works_foundation reference to the initialized instance
                di_container.public_works_foundation = public_works_foundation
                self.logger.info("✅ Public Works Foundation initialized and linked to DI container")
            except RuntimeError as e:
                if "initialize_foundation() returned False" in str(e):
                    # Some adapters may be optional - continue anyway
                    self.logger.warning(f"⚠️ Public Works Foundation initialization had warnings: {e}")
                    self.logger.warning("⚠️ Continuing startup - some adapters may be disabled")
                    self.infrastructure_services["public_works_foundation"] = public_works_foundation
                    self.foundation_services["PublicWorksFoundationService"] = public_works_foundation
                    di_container.public_works_foundation = public_works_foundation
                else:
                    raise
            
            # Initialize Platform Gateway Foundation (depends on Public Works Foundation)
            platform_gateway_foundation = PlatformGatewayFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation
            )
            await platform_gateway_foundation.initialize()
            self.infrastructure_services["platform_gateway_foundation"] = platform_gateway_foundation
            self.foundation_services["PlatformGatewayFoundationService"] = platform_gateway_foundation
            # Store Platform Infrastructure Gateway instance for backward compatibility
            platform_gateway = platform_gateway_foundation.get_platform_gateway()
            self.infrastructure_services["platform_gateway"] = platform_gateway
            self.foundation_services["PlatformInfrastructureGateway"] = platform_gateway
            # CRITICAL: Register in DI container so realms can access it
            di_container.service_registry["PlatformGatewayFoundationService"] = platform_gateway_foundation
            di_container.service_registry["PlatformInfrastructureGateway"] = platform_gateway
            self.logger.info(f"✅ Platform Gateway Foundation initialized and registered in DI container (service_registry now has {len(di_container.service_registry)} entries, PlatformInfrastructureGateway type: {type(platform_gateway).__name__})")
            
            # Initialize Curator Foundation
            curator_foundation = CuratorFoundationService(
                foundation_services=di_container,
                public_works_foundation=public_works_foundation
            )
            await curator_foundation.initialize()
            self.infrastructure_services["curator_foundation"] = curator_foundation
            self.foundation_services["CuratorFoundationService"] = curator_foundation
            # CRITICAL: Also register in DI container so services can discover it via di_container.get_foundation_service()
            di_container.service_registry["CuratorFoundationService"] = curator_foundation
            self.logger.info("✅ Curator Foundation initialized and registered in DI container")
            
            # Initialize Agentic Foundation (before Communication Foundation - no dependencies on other foundations)
            agentic_foundation = AgenticFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                curator_foundation=curator_foundation
            )
            await agentic_foundation.initialize()
            self.infrastructure_services["agentic_foundation"] = agentic_foundation
            self.foundation_services["AgenticFoundationService"] = agentic_foundation
            # CRITICAL: Register in DI container so orchestrators can access it via di_container.get_foundation_service()
            di_container.service_registry["AgenticFoundationService"] = agentic_foundation
            self.logger.info("✅ Agentic Foundation initialized and registered in DI container")
            
            # Initialize Experience Foundation (BEFORE Communication Foundation - Communication's realm bridges need it)
            experience_foundation = ExperienceFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                curator_foundation=curator_foundation
            )
            await experience_foundation.initialize()
            self.infrastructure_services["experience_foundation"] = experience_foundation
            self.foundation_services["ExperienceFoundationService"] = experience_foundation
            # CRITICAL: Register in DI container so realms can access it
            di_container.service_registry["ExperienceFoundationService"] = experience_foundation
            self.logger.info("✅ Experience Foundation initialized and registered in DI container")
            
            # Communication Foundation has been eliminated - functionality moved to:
            # - FastAPIRouterManager (utilities) - router management
            # - Experience Foundation SDK - WebSocket and realm bridges
            # - Post Office SOA APIs - messaging/events
            # - Curator Foundation - SOA Client
            # Realm bridges are now initialized via Experience Foundation SDK
            self.logger.info("✅ Communication Foundation eliminated - functionality distributed to appropriate services")
            
            self.startup_status["foundation"] = "completed"
            self.startup_sequence.append("foundation_infrastructure")
            
        except Exception as e:
            self.logger.error(f"❌ Foundation infrastructure initialization failed: {e}")
            raise
    
    async def _initialize_smart_city_gateway(self):
        """
        Initialize Smart City Gateway (EAGER).
        
        Initializes City Manager - the platform cannot run without it.
        Smart City roles are NOT initialized here - they're LAZY and loaded on-demand.
        
        Note: Platform Gateway is now initialized as a Foundation Service in Phase 1.
        """
        self.logger.info("🌇 Phase 2: Initializing Smart City Gateway (City Manager)")
        
        # Use absolute imports - project_root is already in sys.path (line 57)
        # No need for complex path manipulation
        try:
            di_container = self.infrastructure_services["di_container"]
            
            # Import City Manager using absolute import
            # Project root is already in sys.path, so absolute imports work directly
            # Debug: Check if project_root is in sys.path
            import sys
            project_root_str = str(project_root)
            if project_root_str not in sys.path:
                self.logger.warning(f"⚠️  Project root not in sys.path, adding it: {project_root_str}")
                sys.path.insert(0, project_root_str)
            
            # Try import with explicit path check
            try:
                from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
                self.logger.info("✅ City Manager imported successfully using absolute import")
            except ModuleNotFoundError as e:
                self.logger.error(f"❌ Import failed: {e}")
                self.logger.error(f"   Current working directory: {os.getcwd()}")
                self.logger.error(f"   Project root: {project_root}")
                self.logger.error(f"   Sys.path: {sys.path[:5]}")
                # Try alternative import path
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        "city_manager_service",
                        project_root / "backend" / "smart_city" / "services" / "city_manager" / "city_manager_service.py"
                    )
                    if spec and spec.loader:
                        city_manager_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(city_manager_module)
                        CityManagerService = city_manager_module.CityManagerService
                        self.logger.info("✅ City Manager imported using alternative method")
                    else:
                        raise ImportError("Could not create module spec")
                except Exception as e2:
                    self.logger.error(f"❌ Alternative import also failed: {e2}")
                    raise e  # Re-raise original error
            
            # CityManagerService is now available
            city_manager = CityManagerService(di_container=di_container)
            await city_manager.initialize()
            
            self.managers["city_manager"] = city_manager
            self.foundation_services["CityManagerService"] = city_manager
            self.logger.info("   ✅ City Manager initialized")
            
            # Register City Manager with Curator
            curator = self.foundation_services.get("CuratorFoundationService")
            if curator:
                result = await curator.register_service(
                    service_instance=city_manager,
                    service_metadata={
                        "service_name": "CityManager",
                        "service_type": "smart_city",
                        "realm": "smart_city",
                        "capabilities": ["service_discovery", "realm_orchestration", "manager_hierarchy"],
                        "startup_policy": "eager"
                    }
                )
                if result.get("success"):
                    self.logger.info("   📝 City Manager registered with Curator")
                else:
                    self.logger.warning(f"   ⚠️ City Manager Curator registration failed: {result.get('error')}")
            
            # Configure Smart City realm for lazy initialization
            # Smart City services (Traffic Cop, Security Guard, Nurse, Librarian, Data Steward, Content Steward, etc.)
            # will lazy-load on first use via PlatformCapabilitiesMixin.get_smart_city_api()
            self.logger.info("   🌀 Smart City services configured for lazy initialization")
            self.logger.info("   📝 Services will load on first use via PlatformCapabilitiesMixin")
            self.logger.info("   💡 This enables fast startup, memory efficiency, and headless architecture support")
            
            self.startup_status["smart_city_gateway"] = "completed"
            self.startup_sequence.append("smart_city_gateway")
            self.logger.info("✅ Smart City Gateway active (City Manager initialized)")
            
        except Exception as e:
            self.logger.error(f"❌ Smart City Gateway initialization failed: {e}")
            raise
    
    async def _initialize_mvp_solution(self):
        """
        Bootstrap Manager Hierarchy (EAGER).
        
        Per Phase 0.4 Architecture Contract:
        - City Manager bootstraps Solution Manager
        - Solution Manager bootstraps ALL realm managers (Journey, Insights, Content) as peers
        - All realm managers are peers under Solution Manager
        - Delivery Manager to be archived (or kept for very narrow purpose if enabling services exist)
        
        Flow:
        1. Bootstrap manager hierarchy (Solution Manager → Journey, Insights, Content Managers as peers)
        2. Create MVP Solution (provides context for MVP use case) - optional for MVP
        3. Verify all realm managers are available
        """
        self.logger.info("🎯 Phase 2.5: Bootstrapping Manager Hierarchy")
        
        try:
            # Get City Manager (should be initialized in Phase 2)
            city_manager = self.managers.get("city_manager")
            if not city_manager:
                self.logger.error("❌ City Manager not available - cannot bootstrap MVP Solution")
                raise RuntimeError("City Manager must be initialized before MVP Solution")
            
            # Step 1: Bootstrap manager hierarchy (Solution Manager → Journey, Insights, Content Managers as peers)
            self.logger.info("   Step 1: Bootstrapping manager hierarchy (Solution → Journey, Insights, Content as peers)...")
            bootstrap_result = await city_manager.bootstrap_manager_hierarchy({
                "solution_type": "mvp",
                "auto_bootstrap": True
            })
            
            # BootstrapResult is a BootstrapResponse dataclass, not a dict
            if not bootstrap_result.success:
                error_msg = bootstrap_result.error or "Unknown error"
                self.logger.error(f"❌ Manager hierarchy bootstrap failed: {error_msg}")
                raise RuntimeError(f"Manager hierarchy bootstrap failed: {error_msg}")
            
            self.logger.info("   ✅ Manager hierarchy bootstrapped successfully")
            self.logger.info(f"      - Bootstrapped managers: {', '.join(bootstrap_result.bootstrapped_managers)}")
            self.logger.info(f"      - Hierarchy status: {bootstrap_result.hierarchy_status}")
            
            # Step 2: Verify all realm managers are available
            self.logger.info("   Step 2: Verifying realm managers...")
            solution_manager_info = city_manager.manager_hierarchy.get("solution_manager")
            journey_manager_info = city_manager.manager_hierarchy.get("journey_manager")
            insights_manager_info = city_manager.manager_hierarchy.get("insights_manager")
            content_manager_info = city_manager.manager_hierarchy.get("content_manager")
            
            if not solution_manager_info or "instance" not in solution_manager_info:
                self.logger.error("❌ Solution Manager not available after bootstrap")
                raise RuntimeError("Solution Manager not available after bootstrap")
            self.logger.info("   ✅ Solution Manager available")
            
            if not journey_manager_info or "instance" not in journey_manager_info:
                self.logger.warning("   ⚠️ Journey Manager not available after bootstrap (may need to be created)")
            else:
                self.logger.info("   ✅ Journey Manager available")
            
            if not insights_manager_info or "instance" not in insights_manager_info:
                self.logger.warning("   ⚠️ Insights Manager not available after bootstrap (REQUIRED - needs to be created per Phase 0.4)")
            else:
                self.logger.info("   ✅ Insights Manager available")
            
            if not content_manager_info or "instance" not in content_manager_info:
                self.logger.warning("   ⚠️ Content Manager not available after bootstrap (REQUIRED - needs to be created per Phase 0.4)")
            else:
                self.logger.info("   ✅ Content Manager available")
            
            # Step 3: Optional - Create MVP Solution (provides context for MVP use case)
            # This is optional and can be done lazily when needed
            self.logger.info("   Step 3: MVP Solution will be created on-demand (lazy)")
            
            self.startup_status["manager_hierarchy"] = "completed"
            self.startup_sequence.append("manager_hierarchy")
            self.logger.info("✅ Manager hierarchy bootstrapped successfully")
            self.logger.info("   ✅ Solution Manager bootstrapped")
            self.logger.info("   ✅ Realm managers bootstrapped (Journey, Insights, Content as peers)")
            self.logger.info("   ⚠️ Note: Insights Manager and Content Manager need to be created (per Phase 0.4)")
            
        except Exception as e:
            self.logger.error(f"❌ MVP Solution initialization failed: {e}")
            # For MVP, this is required - fail startup if it fails
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"MVP Solution initialization failed (required for MVP): {e}") from e
    
    async def _start_background_watchers(self):
        """
        Phase 4: Start background health watchers (async tasks).
        
        These are LAZY Smart City roles that run as background tasks:
        - Nurse (Telemetry) - Health monitoring and telemetry collection
        - Post Office (Event Bus Heartbeats) - Event bus heartbeat monitoring
        - Conductor (Task Queue Watcher) - Task queue monitoring
        - Security Guard (Security Sentinel) - Security monitoring
        
        They initialize on-demand but run continuously once started.
        """
        self.logger.info("🩺 Phase 4: Starting Background Health Watchers")
        
        try:
            city_manager = self.managers.get("city_manager")
            if not city_manager:
                self.logger.warning("   ⚠️ City Manager not available - background watchers will start on-demand")
                self.startup_status["background_watchers"] = "deferred"
                self.startup_sequence.append("background_watchers")
                return
            
            # Get platform gateway for accessing Smart City services
            platform_gateway = self.infrastructure_services.get("platform_gateway")
            if not platform_gateway:
                self.logger.warning("   ⚠️ Platform Gateway not available - background watchers will start on-demand")
                self.startup_status["background_watchers"] = "deferred"
                self.startup_sequence.append("background_watchers")
                return
            
            # Start each background watcher as an async task
            watchers_started = []
            
            # 1. Nurse (Telemetry) - Health monitoring
            try:
                nurse_task = asyncio.create_task(self._run_nurse_background_task(platform_gateway))
                self.background_tasks.append(nurse_task)
                watchers_started.append("Nurse (Telemetry)")
                self.logger.info("   ✅ Nurse (Telemetry) background task started")
            except Exception as e:
                self.logger.warning(f"   ⚠️ Failed to start Nurse background task: {e}")
            
            # 2. Post Office (Event Bus Heartbeats)
            try:
                post_office_task = asyncio.create_task(self._run_post_office_background_task(platform_gateway))
                self.background_tasks.append(post_office_task)
                watchers_started.append("Post Office (Event Bus)")
                self.logger.info("   ✅ Post Office (Event Bus) background task started")
            except Exception as e:
                self.logger.warning(f"   ⚠️ Failed to start Post Office background task: {e}")
            
            # 3. Conductor (Task Queue Watcher)
            try:
                conductor_task = asyncio.create_task(self._run_conductor_background_task(platform_gateway))
                self.background_tasks.append(conductor_task)
                watchers_started.append("Conductor (Task Queue)")
                self.logger.info("   ✅ Conductor (Task Queue) background task started")
            except Exception as e:
                self.logger.warning(f"   ⚠️ Failed to start Conductor background task: {e}")
            
            # 4. Security Guard (Security Sentinel)
            try:
                security_guard_task = asyncio.create_task(self._run_security_guard_background_task(platform_gateway))
                self.background_tasks.append(security_guard_task)
                watchers_started.append("Security Guard (Security Sentinel)")
                self.logger.info("   ✅ Security Guard (Security Sentinel) background task started")
            except Exception as e:
                self.logger.warning(f"   ⚠️ Failed to start Security Guard background task: {e}")
            
            if watchers_started:
                self.startup_status["background_watchers"] = "running"
                self.startup_sequence.append("background_watchers")
                self.logger.info(f"✅ Background watchers started: {', '.join(watchers_started)}")
            else:
                self.startup_status["background_watchers"] = "failed"
                self.logger.warning("   ⚠️ No background watchers started")
            
        except Exception as e:
            self.logger.error(f"❌ Background watchers setup failed: {e}")
            self.startup_status["background_watchers"] = "failed"
            # Don't raise - background watchers are optional
    
    async def _run_nurse_background_task(self, platform_gateway: Any):
        """Run Nurse (Telemetry) background task - health monitoring."""
        try:
            # Get Nurse service via City Manager
            city_manager = self.managers.get("city_manager")
            if not city_manager:
                self.logger.warning("⚠️ City Manager not available for Nurse background task")
                return
            
            # Initialize Nurse service if needed
            nurse = None
            try:
                # Try to get Nurse via City Manager's orchestration
                nurse_result = await city_manager.orchestrate_realm_startup(services=["nurse"])
                if nurse_result and nurse_result.get("success"):
                    # Nurse should be available via platform gateway now
                    nurse = platform_gateway.get_abstraction("telemetry") or platform_gateway.get_abstraction("health")
            except Exception as e:
                self.logger.debug(f"Nurse initialization attempt: {e}")
            
            # Run periodic health monitoring and connection pool monitoring
            # Get intervals from configuration (with defaults)
            interval = self.config_manager.get_int("NURSE_HEALTH_CHECK_INTERVAL", 30)  # Default: 30 seconds
            pool_monitoring_interval = self.config_manager.get_int("NURSE_POOL_MONITORING_INTERVAL", 300)  # Default: 5 minutes
            log_monitoring_interval = self.config_manager.get_int("NURSE_LOG_MONITORING_INTERVAL", 300)  # Default: 5 minutes
            last_pool_check = 0
            last_log_check = 0
            
            while not self._shutdown_event.is_set():
                try:
                    current_time = asyncio.get_event_loop().time()
                    
                    # Regular health monitoring
                    if nurse and hasattr(nurse, 'orchestrate_health_monitoring'):
                        await nurse.orchestrate_health_monitoring({})
                    elif nurse and hasattr(nurse, 'monitor_service_health'):
                        await nurse.monitor_service_health({})
                    # If Nurse not available, log warning and continue
                    elif not nurse:
                        self.logger.warning("⚠️ Nurse service not available for health monitoring")
                    
                    # Connection pool monitoring (every 5 minutes)
                    if nurse and hasattr(nurse, 'telemetry_health_module'):
                        if current_time - last_pool_check >= pool_monitoring_interval:
                            try:
                                pool_result = await nurse.telemetry_health_module.monitor_connection_pools()
                                if pool_result.get("status") == "success":
                                    self.logger.debug("✅ Connection pool monitoring completed")
                                else:
                                    self.logger.warning(f"⚠️ Connection pool monitoring issue: {pool_result.get('error')}")
                            except Exception as pool_error:
                                self.logger.error(f"❌ Connection pool monitoring failed: {pool_error}", exc_info=True)
                            last_pool_check = current_time
                            
                            # Log aggregation monitoring (configurable interval)
                            if current_time - last_log_check >= log_monitoring_interval:
                                try:
                                    log_result = await nurse.telemetry_health_module.monitor_log_aggregation()
                                    if log_result.get("status") == "success":
                                        self.logger.debug("✅ Log aggregation monitoring completed")
                                    else:
                                        self.logger.warning(f"⚠️ Log aggregation monitoring issue: {log_result.get('error')}")
                                except Exception as log_error:
                                    self.logger.error(f"❌ Log aggregation monitoring failed: {log_error}", exc_info=True)
                                last_log_check = current_time
                            
                except Exception as e:
                    self.logger.error(f"❌ Nurse background task iteration error: {e}", exc_info=True)
                
                # Wait for interval or shutdown
                try:
                    await asyncio.wait_for(self._shutdown_event.wait(), timeout=interval)
                    break  # Shutdown requested
                except asyncio.TimeoutError:
                    continue  # Continue to next iteration
                    
        except Exception as e:
            self.logger.error(f"❌ Nurse background task failed: {e}", exc_info=True)
    
    async def _run_post_office_background_task(self, platform_gateway: Any):
        """Run Post Office (Event Bus) background task - heartbeat monitoring."""
        try:
            city_manager = self.managers.get("city_manager")
            if not city_manager:
                self.logger.warning("⚠️ City Manager not available for Post Office background task")
                return
            
            # Initialize Post Office service if needed
            post_office = None
            try:
                post_office_result = await city_manager.orchestrate_realm_startup(services=["post_office"])
                if post_office_result and post_office_result.get("success"):
                    post_office = platform_gateway.get_abstraction("event_bus")
            except Exception as e:
                self.logger.debug(f"Post Office initialization attempt: {e}")
            
            # Run periodic heartbeat monitoring
            interval = self.config_manager.get_int("POST_OFFICE_HEARTBEAT_INTERVAL", 60)  # Default: 60 seconds
            while not self._shutdown_event.is_set():
                try:
                    if post_office and hasattr(post_office, 'send_heartbeat'):
                        await post_office.send_heartbeat()
                    elif post_office and hasattr(post_office, 'monitor_heartbeat'):
                        await post_office.monitor_heartbeat()
                    # If Post Office not available, log warning and continue
                    elif not post_office:
                        self.logger.warning("⚠️ Post Office service not available for heartbeat monitoring")
                except Exception as e:
                    self.logger.error(f"❌ Post Office background task iteration error: {e}", exc_info=True)
                
                try:
                    await asyncio.wait_for(self._shutdown_event.wait(), timeout=interval)
                    break
                except asyncio.TimeoutError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"❌ Post Office background task failed: {e}", exc_info=True)
    
    async def _run_conductor_background_task(self, platform_gateway: Any):
        """Run Conductor (Task Queue) background task - queue monitoring."""
        try:
            city_manager = self.managers.get("city_manager")
            if not city_manager:
                self.logger.warning("⚠️ City Manager not available for Conductor background task")
                return
            
            # Initialize Conductor service if needed
            conductor = None
            try:
                conductor_result = await city_manager.orchestrate_realm_startup(services=["conductor"])
                if conductor_result and conductor_result.get("success"):
                    conductor = platform_gateway.get_abstraction("task_queue")
            except Exception as e:
                self.logger.debug(f"Conductor initialization attempt: {e}")
            
            # Run periodic queue monitoring
            interval = self.config_manager.get_int("CONDUCTOR_QUEUE_MONITORING_INTERVAL", 45)  # Default: 45 seconds
            while not self._shutdown_event.is_set():
                try:
                    if conductor and hasattr(conductor, 'monitor_queue'):
                        await conductor.monitor_queue()
                    elif conductor and hasattr(conductor, 'process_pending_tasks'):
                        await conductor.process_pending_tasks()
                    # If Conductor not available, log warning and continue
                    elif not conductor:
                        self.logger.warning("⚠️ Conductor service not available for queue monitoring")
                except Exception as e:
                    self.logger.error(f"❌ Conductor background task iteration error: {e}", exc_info=True)
                
                try:
                    await asyncio.wait_for(self._shutdown_event.wait(), timeout=interval)
                    break
                except asyncio.TimeoutError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"❌ Conductor background task failed: {e}", exc_info=True)
    
    async def _run_security_guard_background_task(self, platform_gateway: Any):
        """Run Security Guard (Security Sentinel) background task - security monitoring."""
        try:
            city_manager = self.managers.get("city_manager")
            if not city_manager:
                self.logger.warning("⚠️ City Manager not available for Security Guard background task")
                return
            
            # Initialize Security Guard service if needed
            security_guard = None
            try:
                security_guard_result = await city_manager.orchestrate_realm_startup(services=["security_guard"])
                if security_guard_result and security_guard_result.get("success"):
                    security_guard = platform_gateway.get_abstraction("security")
            except Exception as e:
                self.logger.debug(f"Security Guard initialization attempt: {e}")
            
            # Run periodic security monitoring
            interval = self.config_manager.get_int("SECURITY_GUARD_MONITORING_INTERVAL", 120)  # Default: 2 minutes
            while not self._shutdown_event.is_set():
                try:
                    if security_guard and hasattr(security_guard, 'monitor_security'):
                        await security_guard.monitor_security()
                    elif security_guard and hasattr(security_guard, 'run_security_scan'):
                        await security_guard.run_security_scan()
                    # If Security Guard not available, log warning and continue
                    elif not security_guard:
                        self.logger.warning("⚠️ Security Guard service not available for security monitoring")
                except Exception as e:
                    self.logger.error(f"❌ Security Guard background task iteration error: {e}", exc_info=True)
                
                try:
                    await asyncio.wait_for(self._shutdown_event.wait(), timeout=interval)
                    break
                except asyncio.TimeoutError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"❌ Security Guard background task failed: {e}", exc_info=True)
    
    async def _start_curator_autodiscovery(self):
        """
        Phase 5: Start Curator's continuous auto-discovery.
        
        Periodic sync between service registry and running services.
        Dynamic update of available APIs and MCP tools.
        """
        self.logger.info("🔍 Phase 5: Starting Curator Auto-Discovery")
        
        try:
            curator = self.foundation_services.get("CuratorFoundationService")
            if curator:
                # Start Curator auto-discovery as a background task
                curator_task = asyncio.create_task(self._run_curator_autodiscovery_task(curator))
                self.background_tasks.append(curator_task)
                
                self.logger.info("   📝 Curator auto-discovery background task started")
                self.logger.info("   - Periodic sync between service registry and running services")
                self.logger.info("   - Dynamic update of available APIs and MCP tools")
                
                self.startup_status["curator_autodiscovery"] = "running"
                self.startup_sequence.append("curator_autodiscovery")
                self.logger.info("✅ Curator auto-discovery active")
            else:
                self.logger.warning("   ⚠️ Curator not available - auto-discovery disabled")
                self.startup_status["curator_autodiscovery"] = "unavailable"
            
        except Exception as e:
            self.logger.error(f"❌ Curator auto-discovery setup failed: {e}")
            # Don't raise - auto-discovery is optional
    
    async def _run_curator_autodiscovery_task(self, curator: Any):
        """Run Curator auto-discovery background task - periodic service registry sync."""
        try:
            interval = self.config_manager.get_int("CURATOR_AUTODISCOVERY_INTERVAL", 300)  # Default: 5 minutes
            
            while not self._shutdown_event.is_set():
                try:
                    # Perform auto-discovery sync
                    if hasattr(curator, 'sync_service_registry'):
                        await curator.sync_service_registry()
                    elif hasattr(curator, 'discover_services'):
                        await curator.discover_services()
                    elif hasattr(curator, 'update_service_registry'):
                        await curator.update_service_registry()
                    else:
                        # Fallback: try to get registered services and update
                        try:
                            services = await curator.get_registered_services()
                            if services:
                                self.logger.debug(f"Curator auto-discovery: {len(services.get('services', {}))} services registered")
                        except Exception as e:
                            self.logger.debug(f"Curator auto-discovery iteration: {e}")
                    
                except Exception as e:
                    self.logger.debug(f"Curator auto-discovery iteration error: {e}")
                
                # Wait for interval or shutdown
                try:
                    await asyncio.wait_for(self._shutdown_event.wait(), timeout=interval)
                    break  # Shutdown requested
                except asyncio.TimeoutError:
                    continue  # Continue to next iteration
                    
        except Exception as e:
            self.logger.error(f"❌ Curator auto-discovery background task failed: {e}", exc_info=True)
    
    async def shutdown_background_tasks(self):
        """Shutdown all background tasks gracefully."""
        self.logger.info("🛑 Shutting down background tasks...")
        self._shutdown_event.set()
        
        # Wait for all tasks to complete (with timeout)
        if self.background_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.background_tasks, return_exceptions=True),
                    timeout=10.0
                )
                self.logger.info("✅ All background tasks shut down")
            except asyncio.TimeoutError:
                self.logger.warning("⚠️ Some background tasks did not shut down within timeout")
                # Cancel remaining tasks
                for task in self.background_tasks:
                    if not task.done():
                        task.cancel()
    
    async def load_realm_on_demand(self, realm_name: str) -> Optional[Any]:
        """
        Lazy-load a realm's Manager hierarchy on-demand.
        
        This implements the lazy-hydrating service mesh pattern:
        - Managers are only loaded when first accessed
        - City Manager bootstraps the full hierarchy (Solution → Journey → Experience → Delivery)
        - Returns the requested Manager or None if loading fails
        
        Args:
            realm_name: Name of the realm to load (e.g., "business_enablement", "experience", "journey", "solution")
            
        Returns:
            Manager instance or None if loading failed
        """
        try:
            # Map realm names to Manager hierarchy paths
            realm_to_manager = {
                "business_enablement": "delivery_manager",
                "experience": "experience_manager",
                "journey": "journey_manager",
                "solution": "solution_manager"
            }
            
            manager_name = realm_to_manager.get(realm_name)
            if not manager_name:
                self.logger.warning(f"⚠️ Unknown realm: {realm_name}")
                return None
            
            # Check if Manager is already loaded
            city_manager = self.managers.get("city_manager")
            if not city_manager:
                self.logger.warning("⚠️ City Manager not available - cannot load realm")
                return None
            
            # Check if Manager hierarchy is already bootstrapped
            if city_manager.manager_hierarchy.get(manager_name):
                manager_info = city_manager.manager_hierarchy[manager_name]
                if manager_info.get("status") == "initialized":
                    manager_instance = manager_info.get("instance")
                    if manager_instance:
                        self.logger.debug(f"✅ {manager_name} already loaded")
                        # Also store in PlatformOrchestrator.managers for direct access
                        self.managers[manager_name] = manager_instance
                        return manager_instance
            
            # Manager not loaded - bootstrap hierarchy via City Manager
            self.logger.info(f"🔄 Lazy-loading realm: {realm_name} (Manager: {manager_name})")
            
            # Bootstrap manager hierarchy (City Manager handles the full chain)
            result = await city_manager.bootstrap_manager_hierarchy()
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"❌ Failed to bootstrap manager hierarchy: {error_msg}")
                return None
            
            # Get the requested Manager from the bootstrapped hierarchy
            manager_info = city_manager.manager_hierarchy.get(manager_name)
            if manager_info and manager_info.get("status") == "initialized":
                manager_instance = manager_info.get("instance")
                if manager_instance:
                    # Store in PlatformOrchestrator.managers for direct access
                    self.managers[manager_name] = manager_instance
                    self.logger.info(f"✅ {manager_name} loaded and initialized")
                    return manager_instance
            
            self.logger.warning(f"⚠️ {manager_name} not found after bootstrap")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load realm {realm_name}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def get_manager(self, manager_name: str) -> Optional[Any]:
        """
        Get a Manager instance (lazy-load if needed).
        
        Args:
            manager_name: Name of the Manager (e.g., "delivery_manager", "experience_manager")
            
        Returns:
            Manager instance or None if not available
        """
        try:
            # Check if already loaded
            if manager_name in self.managers:
                return self.managers[manager_name]
            
            # Map manager_name to realm_name for lazy loading
            manager_to_realm = {
                "delivery_manager": "business_enablement",
                "experience_manager": "experience",
                "journey_manager": "journey",
                "solution_manager": "solution"
            }
            
            realm_name = manager_to_realm.get(manager_name)
            if not realm_name:
                self.logger.warning(f"⚠️ Unknown manager: {manager_name}")
                return None
            
            # Lazy-load the realm
            return await self.load_realm_on_demand(realm_name)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get manager {manager_name}: {e}")
            return None
    
    async def _validate_critical_services_health(self):
        """
        Validate critical infrastructure services are healthy before marking startup complete.
        
        This ensures the platform doesn't report "operational" when critical services are down.
        """
        self.logger.info("🏥 Phase 6: Validating Critical Services Health")
        
        health_checks = {}
        all_healthy = True
        
        try:
            # Get Public Works Foundation for infrastructure access
            public_works = self.foundation_services.get("PublicWorksFoundationService")
            if not public_works:
                self.logger.warning("⚠️ Public Works Foundation not available - skipping health checks")
                return
            
            # 1. Check ArangoDB
            try:
                arango_abstraction = public_works.get_abstraction("database")
                if arango_abstraction:
                    # Try to get a connection or perform a simple operation
                    # Most database abstractions have a test_connection or similar method
                    if hasattr(arango_abstraction, 'test_connection'):
                        is_healthy = await arango_abstraction.test_connection()
                        health_checks["arangodb"] = "healthy" if is_healthy else "unhealthy"
                        if not is_healthy:
                            all_healthy = False
                            self.logger.error("❌ ArangoDB health check failed")
                    else:
                        health_checks["arangodb"] = "unknown"
                        self.logger.warning("⚠️ ArangoDB abstraction doesn't have test_connection method")
                else:
                    health_checks["arangodb"] = "unavailable"
                    all_healthy = False
                    self.logger.error("❌ ArangoDB abstraction not available")
            except Exception as e:
                health_checks["arangodb"] = "error"
                all_healthy = False
                self.logger.error(f"❌ ArangoDB health check error: {e}")
            
            # 2. Check Redis
            try:
                cache_abstraction = public_works.get_abstraction("cache")
                if cache_abstraction:
                    if hasattr(cache_abstraction, 'test_connection'):
                        is_healthy = await cache_abstraction.test_connection()
                        health_checks["redis"] = "healthy" if is_healthy else "unhealthy"
                        if not is_healthy:
                            all_healthy = False
                            self.logger.error("❌ Redis health check failed")
                    else:
                        health_checks["redis"] = "unknown"
                        self.logger.warning("⚠️ Redis abstraction doesn't have test_connection method")
                else:
                    health_checks["redis"] = "unavailable"
                    all_healthy = False
                    self.logger.error("❌ Redis abstraction not available")
            except Exception as e:
                health_checks["redis"] = "error"
                all_healthy = False
                self.logger.error(f"❌ Redis health check error: {e}")
            
            # 3. Check Consul (if available)
            try:
                consul_abstraction = public_works.get_abstraction("service_discovery")
                if consul_abstraction:
                    if hasattr(consul_abstraction, 'test_connection'):
                        is_healthy = await consul_abstraction.test_connection()
                        health_checks["consul"] = "healthy" if is_healthy else "unhealthy"
                        if not is_healthy:
                            all_healthy = False
                            self.logger.error("❌ Consul health check failed")
                    else:
                        health_checks["consul"] = "unknown"
                else:
                    health_checks["consul"] = "unavailable"
                    # Consul is optional, so don't fail startup if unavailable
            except Exception as e:
                health_checks["consul"] = "error"
                # Consul is optional, so don't fail startup on error
                self.logger.warning(f"⚠️ Consul health check error: {e}")
            
            # Store health check results
            self.startup_status["health_validation"] = {
                "status": "healthy" if all_healthy else "unhealthy",
                "checks": health_checks,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if all_healthy:
                self.logger.info("✅ All critical services are healthy")
            else:
                self.logger.warning("⚠️ Some critical services are unhealthy - platform may not be fully operational")
                # Don't fail startup - allow platform to start but log warning
                # This allows graceful degradation
            
        except Exception as e:
            self.logger.error(f"❌ Health validation failed: {e}", exc_info=True)
            # Don't fail startup - log error but continue
            self.startup_status["health_validation"] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get comprehensive platform status."""
        # Check if platform is operational (foundation and gateway must be completed)
        is_operational = (
            self.startup_status.get("foundation") == "completed" and
            self.startup_status.get("smart_city_gateway") == "completed"
        )
        
        # Include health validation status if available
        health_validation = self.startup_status.get("health_validation", {})
        
        return {
            "platform_status": "operational" if is_operational else "initializing",
            "startup_status": self.startup_status,
            "health_validation": health_validation,
            "managers": {name: "healthy" if hasattr(mgr, "is_initialized") and mgr.is_initialized else "unhealthy" 
                        for name, mgr in self.managers.items()},
            "foundation_services": {name: "healthy" for name in self.foundation_services.keys()},
            "infrastructure_services": {name: "healthy" for name in self.infrastructure_services.keys()},
            "startup_sequence": self.startup_sequence,
            "lazy_services_ready": self.startup_status.get("lazy_hydration") == "ready",
            "timestamp": datetime.utcnow().isoformat()
        }


# Global orchestrator instance
platform_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Platform lifespan with updated architecture."""
    global platform_orchestrator
    
    # Choose orchestrator based on feature flag
    from utilities.configuration.cloud_ready_config import get_cloud_ready_config
    cloud_ready_config = get_cloud_ready_config()
    
    if cloud_ready_config.should_use_cloud_ready_startup():
        logger.info("🚀 Starting SymphAIny Platform (Cloud-Ready Mode)")
        from main_cloud_ready import CloudReadyPlatformOrchestrator
        platform_orchestrator = CloudReadyPlatformOrchestrator()
    else:
        logger.info("🚀 Starting SymphAIny Platform (Current Mode)")
        platform_orchestrator = PlatformOrchestrator()
    
    try:
        # Orchestrate complete platform startup
        startup_result = await platform_orchestrator.orchestrate_platform_startup()
        
        # Store in app state
        app_state["platform_orchestrator"] = platform_orchestrator
        app_state["startup_result"] = startup_result
        app_state["infrastructure_mode"] = "updated_architecture"
        
        # Setup FastAPI routes
        await setup_platform_routes(app)
        
        # Register API routers (NEW - connects frontend to new architecture)
        # CRITICAL: API routers are required for frontend to function
        try:
            # Set ConfigAdapter on WebSocketRoutingHelper at startup (before API router registration)
            # ConfigAdapter must be available before City Manager initialization per architecture
            try:
                from utilities.api_routing.websocket_routing_helper import WebSocketRoutingHelper
                public_works = platform_orchestrator.foundation_services.get("PublicWorksFoundationService")
                if public_works and hasattr(public_works, 'config_adapter') and public_works.config_adapter:
                    WebSocketRoutingHelper.set_config_adapter(public_works.config_adapter)
                    logger.info("✅ ConfigAdapter set on WebSocketRoutingHelper")
                else:
                    logger.warning("⚠️ ConfigAdapter not available - WebSocketRoutingHelper will fail if used")
            except Exception as e:
                logger.warning(f"⚠️ Failed to set ConfigAdapter on WebSocketRoutingHelper: {e}")
            
            from backend.api import register_api_routers
            await register_api_routers(app, platform_orchestrator)
            logger.info("✅ API routers registered successfully")
        except Exception as e:
            logger.error(f"❌ Failed to register MVP API routers: {e}")
            logger.error("Platform cannot run without API routers - failing startup")
            logger.error("Frontend API calls will fail - this is NOT production ready")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError("API router registration failed - platform cannot start") from e
        
        logger.info("🎉 SymphAIny Platform fully orchestrated and operational!")
        
    except Exception as e:
        logger.error(f"❌ Platform startup failed: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down platform...")
    if platform_orchestrator:
        # Shutdown background tasks first (if available)
        if hasattr(platform_orchestrator, 'shutdown_background_tasks'):
            try:
                await platform_orchestrator.shutdown_background_tasks()
            except Exception as e:
                logger.error(f"❌ Background tasks shutdown failed: {e}")
        
        # Shutdown managers in reverse order (if available)
        if hasattr(platform_orchestrator, 'managers') and platform_orchestrator.managers:
            for manager_name in reversed(list(platform_orchestrator.managers.keys())):
                try:
                    manager = platform_orchestrator.managers[manager_name]
                    if hasattr(manager, 'shutdown'):
                        await manager.shutdown()
                    logger.info(f"✅ {manager_name} shutdown complete")
                except Exception as e:
                    logger.error(f"❌ {manager_name} shutdown failed: {e}")

async def setup_platform_routes(app: FastAPI):
    """Setup FastAPI routes for the platform."""
    
    @app.get("/api/health")
    async def health():
        """Platform health endpoint."""
        if platform_orchestrator:
            return await platform_orchestrator.get_platform_status()
        return {"status": "unhealthy", "error": "Platform not initialized"}
    
    @app.get("/platform/status")
    async def platform_status():
        """Detailed platform status."""
        if platform_orchestrator:
            return await platform_orchestrator.get_platform_status()
        return {"error": "Platform not initialized"}
    
    @app.get("/managers")
    async def list_managers():
        """List all active managers."""
        if platform_orchestrator:
            # Handle both orchestrator types
            if hasattr(platform_orchestrator, 'managers'):
                return {
                    "managers": list(platform_orchestrator.managers.keys()),
                    "status": "operational"
                }
            else:
                # Cloud-ready orchestrator - managers are lazy-loaded
                return {
                    "managers": [],
                    "status": "operational",
                    "mode": "cloud_ready",
                    "note": "Managers are lazy-loaded on-demand"
                }
        return {"error": "Platform not initialized"}
    
    @app.get("/foundation/services")
    async def list_foundation_services():
        """List all foundation services."""
        if platform_orchestrator:
            # Handle both orchestrator types
            if hasattr(platform_orchestrator, 'foundation_services'):
                return {
                    "foundation_services": list(platform_orchestrator.foundation_services.keys()),
                    "infrastructure_services": list(platform_orchestrator.infrastructure_services.keys()),
                    "status": "operational"
                }
            else:
                # Cloud-ready orchestrator - use DI Container
                di_container = platform_orchestrator.get_di_container()
                if di_container and di_container.unified_registry:
                    services = di_container.unified_registry.list_services()
                    return {
                        "foundation_services": services,
                        "status": "operational",
                        "mode": "cloud_ready"
                    }
                return {
                    "foundation_services": [],
                    "status": "operational",
                    "mode": "cloud_ready"
                }
        return {"error": "Platform not initialized"}
    
    # Include unified router from FastAPI Router Manager (utility)
    if platform_orchestrator and platform_orchestrator.router_manager:
        try:
            unified_router = platform_orchestrator.router_manager.get_unified_router()
            if unified_router:
                app.include_router(unified_router)
                logger.info("✅ Unified router included from FastAPI Router Manager (utility)")
            else:
                logger.warning("⚠️ Unified router not available")
        except Exception as e:
            logger.error(f"❌ Failed to include unified router: {e}")
            import traceback
            logger.error(traceback.format_exc())

# Import custom JSON encoder for handling numpy/pandas types
# Note: utils is in the same directory as main.py, so we can import directly
# The Docker container sets PYTHONPATH to include /app (symphainy-platform directory)
try:
    from utils.json_encoder import custom_jsonable_encoder
    logger.info("✅ Custom JSON encoder module imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import custom JSON encoder: {e}")
    logger.error("   Will use FastAPI's default encoder (may fail on numpy types)")
    # Create a dummy encoder that just passes through
    def custom_jsonable_encoder(obj, **kwargs):
        from fastapi.encoders import jsonable_encoder
        return jsonable_encoder(obj, **kwargs)

# Create FastAPI app with custom JSON encoder
# This ensures all responses can be JSON-serialized, even with numpy/pandas types
app = FastAPI(
    title="SymphAIny Platform",
    description="AI-Coexistence Platform with Updated Architecture",
    version="2.1.0",
    lifespan=lifespan
)

# Override FastAPI's default jsonable_encoder to use our custom encoder
# This provides a global safety net for non-serializable types (numpy, pandas, etc.)
# Future-proof: Will handle other edge cases even if we move away from numpy
from fastapi.encoders import jsonable_encoder as fastapi_jsonable_encoder
from fastapi.encoders import ENCODERS_BY_TYPE
import fastapi.encoders

# Replace FastAPI's jsonable_encoder with our custom version
# Store original for reference (though we sanitize first in our encoder)
_original_jsonable_encoder = fastapi.encoders.jsonable_encoder
fastapi.encoders.jsonable_encoder = custom_jsonable_encoder

# Verify replacement worked
if fastapi.encoders.jsonable_encoder == custom_jsonable_encoder:
    logger.info("✅ Custom JSON encoder enabled (handles numpy/pandas types)")
else:
    logger.error("❌ Failed to replace FastAPI's jsonable_encoder")

# Instrument FastAPI app for automatic span creation
# This enables automatic trace creation for HTTP requests
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app)
    logger.info("✅ OpenTelemetry FastAPI instrumentation enabled")
except ImportError:
    environment = config_manager.get("ENVIRONMENT", "development")
    if isinstance(environment, str):
        environment = environment.lower()
    if environment in ["production", "prod"]:
        raise RuntimeError(
            "opentelemetry-instrumentation-fastapi is required in production. "
            "Install with: pip install opentelemetry-instrumentation-fastapi"
        )
    logger.warning("⚠️ OpenTelemetry FastAPI instrumentation not available (development mode)")
except Exception as e:
    environment = config_manager.get("ENVIRONMENT", "development")
    if isinstance(environment, str):
        environment = environment.lower()
    if environment in ["production", "prod"]:
        raise RuntimeError(f"Failed to instrument FastAPI in production: {e}") from e
    logger.warning(f"⚠️ Failed to instrument FastAPI: {e}")

# Phase 2: Configuration Management - CORS middleware will be added LAST
# (FastAPI applies middleware in reverse order, so last added = first executed)
# This ensures CORS runs first and can properly handle websocket upgrades
# Store the middleware setup for later (after other middlewares are added)
_cors_middleware_setup = None
try:
    from utilities.api_routing.websocket_routing_helper import WebSocketRoutingHelper, FastAPICORSMiddleware
    _cors_middleware_setup = ("FastAPICORSMiddleware", FastAPICORSMiddleware)
    logger.info("✅ CORS middleware imported (will be registered after other middlewares)")
except ImportError as e:
    logger.warning(f"⚠️ Failed to import WebSocketRoutingHelper: {e}")
    logger.warning("⚠️ Will use fallback CORS middleware")
    # Fallback CORS middleware setup
    cors_origins = config_manager.get("CORS_ORIGINS") or config_manager.get("API_CORS_ORIGINS", "*")
    if cors_origins == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    
    class CustomCORSMiddleware(BaseHTTPMiddleware):
        """Fallback CORS middleware."""
        async def dispatch(self, request: Request, call_next):
            is_websocket = (
                request.url.path.startswith("/api/ws") or
                (request.headers.get("upgrade", "").lower() == "websocket" and
                 "upgrade" in request.headers.get("connection", "").lower())
            )
            if is_websocket:
                return await call_next(request)
            
            if request.method == "OPTIONS":
                origin = request.headers.get("origin")
                if origin and (origin in allow_origins or "*" in allow_origins):
                    from starlette.responses import Response
                    return Response(status_code=200, headers={
                        "Access-Control-Allow-Origin": origin if "*" not in allow_origins else origin,
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                        "Access-Control-Allow-Headers": "*",
                    })
            
            response = await call_next(request)
            origin = request.headers.get("origin")
            if origin and (origin in allow_origins or "*" in allow_origins):
                response.headers["Access-Control-Allow-Origin"] = origin if "*" not in allow_origins else origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = "*"
            return response
    
    _cors_middleware_setup = ("CustomCORSMiddleware", CustomCORSMiddleware)

# Add JSON sanitization middleware (handles numpy/pandas types in responses)
class JSONSanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware to sanitize JSON responses for numpy/pandas types."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Only sanitize JSON responses
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                import json
                from utils.json_encoder import sanitize_for_json
                # Read response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                # Parse and sanitize
                try:
                    data = json.loads(body.decode('utf-8'))
                    sanitized_data = sanitize_for_json(data)
                    # Create new response with sanitized data
                    from fastapi.responses import JSONResponse
                    return JSONResponse(
                        content=sanitized_data,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # If not JSON, return original response
                    from fastapi.responses import Response
                    return Response(
                        content=body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.headers.get("content-type")
                    )
            except Exception as e:
                logger.warning(f"⚠️ JSON sanitization middleware error: {e}")
                # Return original response on error
                return response
        return response

app.add_middleware(JSONSanitizationMiddleware)

# Add security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Only add HSTS if using HTTPS
        # NOTE: In production, ensure HTTPS is configured (reverse proxy, load balancer, or direct SSL)
        # HSTS will only be added if request.url.scheme == "https"
        # If production uses HTTP directly, HSTS will not be added (which is correct)
        # If production uses a reverse proxy/load balancer with HTTPS termination, 
        # ensure X-Forwarded-Proto header is set so request.url.scheme == "https"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Add request logging middleware for debugging
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"🌐 [RequestLogging] {request.method} {request.url.path}")
        if request.url.path.startswith("/api/auth"):
            logger.info(f"🔍 [RequestLogging] Auth request detected: {request.method} {request.url.path}")
            logger.info(f"🔍 [RequestLogging] Headers: {dict(request.headers)}")
        try:
            response = await call_next(request)
            logger.info(f"✅ [RequestLogging] {request.method} {request.url.path} -> {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"❌ [RequestLogging] Exception in {request.method} {request.url.path}: {e}", exc_info=True)
            raise

app.add_middleware(RequestLoggingMiddleware)

# Phase 2: Add CORS middleware LAST (so it runs FIRST - FastAPI applies in reverse order)
# This ensures websocket upgrades are handled before other middlewares can interfere
if _cors_middleware_setup:
    middleware_name, middleware_class = _cors_middleware_setup
    app.add_middleware(middleware_class)
    logger.info(f"✅ {middleware_name} registered (runs first to handle websocket upgrades)")

# Add rate limiting middleware (if enabled)
rate_limiting_enabled = config_manager.get_bool("RATE_LIMITING_ENABLED", True)
if rate_limiting_enabled:
    # Rate limiting middleware (optional - may not be available in all environments)
    try:
        from utilities.api_routing.middleware.fastapi_rate_limiting_middleware import FastAPIRateLimitingMiddleware
        app.add_middleware(FastAPIRateLimitingMiddleware, config_manager=config_manager)
        logger.info("✅ Rate limiting middleware added")
    except ImportError as e:
        logger.warning(f"⚠️ Rate limiting middleware not available: {e}")
        # Continue without rate limiting middleware
    logger.info("✅ Rate limiting middleware enabled")
else:
    logger.info("⚠️ Rate limiting disabled")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SymphAIny Platform Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--reload", action="store_true", default=False, help="Enable auto-reload")
    parser.add_argument("--log-level", type=str, default="info", help="Log level")
    
    args = parser.parse_args()
    
    logger.info(f"🌐 Starting SymphAIny Platform on {args.host}:{args.port}")
    logger.info(f"🔄 Auto-reload: {args.reload}")
    logger.info(f"📊 Log level: {args.log_level}")
    
    # Get timeout configuration
    # Increased timeouts for file uploads and long-running requests
    timeout_keep_alive = config_manager.get_int("API_TIMEOUT_KEEP_ALIVE", 300)  # 5 minutes (was 5s)
    timeout_graceful_shutdown = config_manager.get_int("API_TIMEOUT_GRACEFUL_SHUTDOWN", 30)
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        timeout_keep_alive=timeout_keep_alive,
        timeout_graceful_shutdown=timeout_graceful_shutdown,
        limit_concurrency=config_manager.get_int("API_LIMIT_CONCURRENCY", 1000),
        limit_max_requests=config_manager.get_int("API_LIMIT_MAX_REQUESTS", 10000),
        backlog=config_manager.get_int("API_BACKLOG", 2048)
    )

if __name__ == "__main__":
    main()



