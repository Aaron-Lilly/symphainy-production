#!/usr/bin/env python3
"""
Data Mash CLI Tool for Insurance Use Case

WHAT: Client onboarding CLI tool for insurance data migration
HOW: Provides commands for ingestion, profiling, mapping, validation, and planning

This CLI tool enables client onboarding for the Insurance Use Case by providing
easy-to-use commands that interact with the platform APIs.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Add symphainy-platform to path for imports
sys.path.insert(0, str(project_root / "symphainy-platform"))

# Import platform components
PLATFORM_IMPORTS_AVAILABLE = False
try:
    from foundations.di_container.di_container_service import DIContainerService
    from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
    from foundations.client_config_foundation.client_config_foundation_service import ClientConfigFoundationService
    # PlatformGatewayService and DeliveryManagerService are optional for CLI
    # CLI can work with just Client Config Foundation
    PLATFORM_IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import platform components: {e}")
    print("   CLI will use API calls instead of direct service access")


class DataMashCLI:
    """Data Mash CLI Tool for Insurance Use Case."""
    
    def __init__(self):
        """Initialize CLI tool."""
        self.platform_initialized = False
        self.delivery_manager = None
        self.client_config_foundation = None
        self.config_loader = None
        self.config_validator = None
        self.config_storage = None
        self.config_versioner = None
        self.tenant_id = None
        self.tenant_configs = {}
        # Use Traefik route instead of direct service URL
        self.api_base_url = os.getenv("SYMPHAINY_API_URL", "http://localhost/api")
    
    async def _initialize_platform(self):
        """Initialize platform services (lazy initialization)."""
        if self.platform_initialized:
            return True
        
        if not PLATFORM_IMPORTS_AVAILABLE:
            return False
            
        try:
            # Try to initialize platform services
            di_container = DIContainerService("cli_realm")
            
            # Initialize Public Works Foundation (required for Client Config Foundation)
            public_works_foundation = None
            try:
                public_works_foundation = PublicWorksFoundationService(di_container)
                await public_works_foundation.initialize()
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Public Works Foundation: {e}")
            
            # Initialize Client Config Foundation
            if public_works_foundation:
                try:
                    self.client_config_foundation = ClientConfigFoundationService(
                        di_container=di_container,
                        public_works_foundation=public_works_foundation,
                        curator_foundation=None  # Optional for CLI
                    )
                    await self.client_config_foundation.initialize()
                except Exception as e:
                    print(f"⚠️  Warning: Could not initialize Client Config Foundation: {e}")
            
            # Delivery Manager is optional for CLI (only needed for some commands)
            # We'll initialize it lazily if needed
            self.di_container = di_container
            self.platform_initialized = True
            return True
            
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize platform services: {e}")
            print(f"   Falling back to API calls to {self.api_base_url}")
            return False
    
    async def _load_tenant_configs(self, tenant_id: str) -> Dict[str, Any]:
        """
        Load tenant-specific configurations.
        
        Args:
            tenant_id: Tenant ID
        
        Returns:
            Dictionary of tenant configurations
        """
        if not self.client_config_foundation:
            await self._initialize_platform()
        
        if not self.client_config_foundation:
            print(f"⚠️  Client Config Foundation not available, skipping tenant config loading")
            return {}
        
        try:
            # Create or get ConfigLoader for this tenant
            if not self.config_loader or self.tenant_id != tenant_id:
                config_loader_builder = await self.client_config_foundation.create_config_loader(
                    tenant_id=tenant_id
                )
                # Get the instance from the builder (method name: get_loader)
                self.config_loader = config_loader_builder.get_loader()
                self.tenant_id = tenant_id
            
            # Load tenant configs (load_config requires tenant_id and config_type)
            self.tenant_configs = {
                "domain_models": await self.config_loader.load_config(tenant_id, "domain_models"),
                "workflows": await self.config_loader.load_config(tenant_id, "workflows"),
                "ingestion_endpoints": await self.config_loader.load_config(tenant_id, "ingestion_endpoints"),
            }
            
            print(f"✅ Loaded tenant configs for: {tenant_id}")
            return self.tenant_configs
            
        except Exception as e:
            print(f"⚠️  Warning: Could not load tenant configs: {e}")
            return {}
    
    async def ingest(self, file_path: str, format: str = "auto", tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest legacy insurance data.
        
        Args:
            file_path: Path to data file
            format: File format (csv, json, xml, auto)
            tenant: Tenant ID for multi-tenant support
        
        Returns:
            Ingestion result with file_id
        """
        print(f"📥 Ingesting legacy data from: {file_path}")
        
        # Load tenant configs if tenant is provided
        if tenant:
            await self._load_tenant_configs(tenant)
            # Apply tenant-specific ingestion endpoint if configured
            ingestion_config = self.tenant_configs.get("ingestion_endpoints", {})
            if ingestion_config.get("custom_endpoint"):
                self.api_base_url = ingestion_config["custom_endpoint"]
                print(f"   Using tenant-specific endpoint: {self.api_base_url}")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Try platform services first
        if await self._initialize_platform():
            try:
                insurance_orchestrator = None
                orchestrators = self.delivery_manager.get_orchestrators()
                for orchestrator in orchestrators:
                    if hasattr(orchestrator, 'orchestrator_name') and orchestrator.orchestrator_name == "InsuranceMigrationOrchestrator":
                        insurance_orchestrator = orchestrator
                        break
                
                if insurance_orchestrator:
                    # Read file data
                    with open(file_path_obj, 'rb') as f:
                        file_data = f.read()
                    
                    user_context = {
                        "user_id": "cli_user",
                        "tenant_id": tenant or "default"
                    }
                    
                    result = await insurance_orchestrator.ingest_legacy_data(
                        file_data=file_data,
                        filename=file_path_obj.name,
                        user_context=user_context
                    )
                    
                    if result.get("success"):
                        print(f"✅ Ingestion successful")
                        print(f"   File ID: {result.get('file_id')}")
                        return result
                    else:
                        print(f"❌ Ingestion failed: {result.get('error')}")
                        return result
                        
            except Exception as e:
                print(f"⚠️  Platform service call failed: {e}")
        
        # Fallback to API call
        try:
            import requests
            
            with open(file_path_obj, 'rb') as f:
                files = {'file': (file_path_obj.name, f, f'application/{format}')}
                data = {
                    'format': format,
                    'tenant': tenant or 'default'
                }
                
                response = requests.post(
                    f"{self.api_base_url}/v1/insurance-migration/ingest-legacy-data",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Ingestion successful")
                    print(f"   File ID: {result.get('file_id')}")
                    return result
                else:
                    error_msg = response.json().get('error', 'Unknown error')
                    print(f"❌ Ingestion failed: {error_msg}")
                    return {"success": False, "error": error_msg}
                    
        except ImportError:
            print("❌ Error: 'requests' library not available for API calls")
            return {"success": False, "error": "API client not available"}
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def profile(self, file_id: str, output: Optional[str] = None) -> Dict[str, Any]:
        """
        Profile ingested data.
        
        Args:
            file_id: File ID from ingestion
            output: Output file path for profile report (optional)
        
        Returns:
            Profile result with data quality metrics
        """
        print(f"📊 Profiling data for file: {file_id}")
        
        # Try platform services first
        if await self._initialize_platform():
            try:
                # Get Content Analysis Composition Service
                content_analysis = await self.delivery_manager.get_enabling_service("ContentAnalysisCompositionService")
                if content_analysis:
                    user_context = {"user_id": "cli_user"}
                    result = await content_analysis.analyze_content(
                        file_id=file_id,
                        user_context=user_context
                    )
                    
                    if result.get("success"):
                        print(f"✅ Profiling successful")
                        profile_data = result.get("profile", {})
                        print(f"   Quality Score: {profile_data.get('quality_score', 'N/A')}")
                        print(f"   Total Records: {profile_data.get('total_records', 'N/A')}")
                        
                        # Save to file if requested
                        if output:
                            with open(output, 'w') as f:
                                json.dump(profile_data, f, indent=2)
                            print(f"   Profile saved to: {output}")
                        
                        return result
                    else:
                        print(f"❌ Profiling failed: {result.get('error')}")
                        return result
                        
            except Exception as e:
                print(f"⚠️  Platform service call failed: {e}")
        
        # Fallback to API call
        try:
            import requests
            
            response = requests.get(
                f"{self.api_base_url}/v1/insurance-migration/profile/{file_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                profile_data = result.get("profile", {})
                print(f"✅ Profiling successful")
                print(f"   Quality Score: {profile_data.get('quality_score', 'N/A')}")
                
                if output:
                    with open(output, 'w') as f:
                        json.dump(profile_data, f, indent=2)
                    print(f"   Profile saved to: {output}")
                
                return result
            else:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"❌ Profiling failed: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except ImportError:
            print("❌ Error: 'requests' library not available for API calls")
            return {"success": False, "error": "API client not available"}
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def map_to_canonical(self, source_schema: str, canonical: str = "policy_v1", tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Map source schema to canonical model.
        
        Args:
            source_schema: Source schema ID or path to schema file
            canonical: Canonical model name (default: policy_v1)
            tenant: Tenant ID for multi-tenant support
        
        Returns:
            Mapping result with field mappings and confidence score
        """
        print(f"🗺️  Mapping source schema to canonical model: {canonical}")
        
        # Load tenant configs if tenant is provided
        if tenant:
            await self._load_tenant_configs(tenant)
            # Use tenant-specific domain models if configured
            domain_models = self.tenant_configs.get("domain_models", {})
            if domain_models.get("canonical_model"):
                canonical = domain_models["canonical_model"]
                print(f"   Using tenant-specific canonical model: {canonical}")
        
        # Try platform services first
        if await self._initialize_platform():
            try:
                schema_mapper = await self.delivery_manager.get_enabling_service("SchemaMapperService")
                if schema_mapper:
                    # Load source schema if it's a file path
                    source_schema_data = None
                    if Path(source_schema).exists():
                        with open(source_schema, 'r') as f:
                            source_schema_data = json.load(f)
                    else:
                        # Assume it's a schema ID
                        source_schema_data = source_schema
                    
                    user_context = {"user_id": "cli_user"}
                    result = await schema_mapper.map_to_canonical(
                        source_schema=source_schema_data,
                        canonical_model_name=canonical,
                        user_context=user_context
                    )
                    
                    if result.get("success"):
                        print(f"✅ Mapping successful")
                        print(f"   Mapping ID: {result.get('mapping_id')}")
                        print(f"   Confidence: {result.get('confidence_score', 0.0):.2%}")
                        print(f"   Fields Mapped: {result.get('total_fields_mapped', 0)}")
                        return result
                    else:
                        print(f"❌ Mapping failed: {result.get('error')}")
                        return result
                        
            except Exception as e:
                print(f"⚠️  Platform service call failed: {e}")
        
        # Fallback to API call
        try:
            import requests
            
            # Load source schema if it's a file path
            source_schema_data = None
            if Path(source_schema).exists():
                with open(source_schema, 'r') as f:
                    source_schema_data = json.load(f)
            else:
                source_schema_data = {"schema_id": source_schema}
            
            response = requests.post(
                f"{self.api_base_url}/v1/insurance-migration/map-to-canonical",
                json={
                    "source_schema": source_schema_data,
                    "canonical_model": canonical
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Mapping successful")
                print(f"   Mapping ID: {result.get('mapping_id')}")
                print(f"   Confidence: {result.get('confidence_score', 0.0):.2%}")
                return result
            else:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"❌ Mapping failed: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except ImportError:
            print("❌ Error: 'requests' library not available for API calls")
            return {"success": False, "error": "API client not available"}
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_mapping(self, mapping_id: str) -> Dict[str, Any]:
        """
        Validate mapping rules.
        
        Args:
            mapping_id: Mapping ID from map-to-canonical
        
        Returns:
            Validation result with errors if any
        """
        print(f"✅ Validating mapping: {mapping_id}")
        
        # Try platform services first
        if await self._initialize_platform():
            try:
                schema_mapper = await self.delivery_manager.get_enabling_service("SchemaMapperService")
                if schema_mapper:
                    # For now, just retrieve and display mapping
                    # Full validation would require test data
                    librarian = await self.delivery_manager.get_librarian_api()
                    if librarian:
                        mapping_doc = await librarian.retrieve_document(mapping_id)
                        if mapping_doc:
                            print(f"✅ Mapping found")
                            print(f"   Confidence: {mapping_doc.get('confidence_score', 0.0):.2%}")
                            print(f"   Fields: {mapping_doc.get('total_fields_mapped', 0)}")
                            return {"success": True, "mapping": mapping_doc}
                        else:
                            return {"success": False, "error": "Mapping not found"}
                        
            except Exception as e:
                print(f"⚠️  Platform service call failed: {e}")
        
        # Fallback to API call
        try:
            import requests
            
            response = requests.get(
                f"{self.api_base_url}/v1/insurance-migration/validate-mapping/{mapping_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Validation successful")
                return result
            else:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"❌ Validation failed: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except ImportError:
            print("❌ Error: 'requests' library not available for API calls")
            return {"success": False, "error": "API client not available"}
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_plan(self, source: str, target: str, canonical: str = "policy_v1", tenant: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate migration plan.
        
        Args:
            source: Source system ID
            target: Target system ID
            canonical: Canonical model name (default: policy_v1)
            tenant: Tenant ID for multi-tenant support
        
        Returns:
            Migration plan with phases and steps
        """
        print(f"📋 Generating migration plan")
        print(f"   Source: {source}")
        print(f"   Target: {target}")
        print(f"   Canonical: {canonical}")
        
        # Load tenant configs if tenant is provided
        if tenant:
            await self._load_tenant_configs(tenant)
            # Use tenant-specific workflows if configured
            workflows = self.tenant_configs.get("workflows", {})
            if workflows.get("migration_workflow"):
                print(f"   Using tenant-specific migration workflow")
        
        # Try platform services first
        if await self._initialize_platform():
            try:
                solution_composer = await self.delivery_manager.get_solution_composer_api()
                if solution_composer:
                    user_context = {"user_id": "cli_user"}
                    result = await solution_composer.design_solution(
                        solution_type="insurance_migration",
                        requirements={
                            "source_system": source,
                            "target_system": target,
                            "canonical_model": canonical
                        },
                        user_context=user_context
                    )
                    
                    if result.get("success"):
                        print(f"✅ Migration plan generated")
                        solution = result.get("solution", {})
                        phases = solution.get("phases", [])
                        print(f"   Phases: {len(phases)}")
                        for i, phase in enumerate(phases, 1):
                            print(f"   Phase {i}: {phase.get('name', 'Unknown')}")
                        return result
                    else:
                        print(f"❌ Plan generation failed: {result.get('error')}")
                        return result
                        
            except Exception as e:
                print(f"⚠️  Platform service call failed: {e}")
        
        # Fallback to API call
        try:
            import requests
            
            response = requests.post(
                f"{self.api_base_url}/v1/wave-orchestration/create-wave",
                json={
                    "source": source,
                    "target": target,
                    "canonical": canonical
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Migration plan generated")
                return result
            else:
                error_msg = response.json().get('error', 'Unknown error')
                print(f"❌ Plan generation failed: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except ImportError:
            print("❌ Error: 'requests' library not available for API calls")
            return {"success": False, "error": "API client not available"}
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # Config Management Commands (Client Config SDK Integration)
    # ============================================================================
    
    async def config_load(self, tenant_id: str, config_type: str) -> Dict[str, Any]:
        """
        Load tenant-specific configuration.
        
        Args:
            tenant_id: Tenant ID
            config_type: Configuration type (domain_models, workflows, ingestion_endpoints, etc.)
        
        Returns:
            Configuration dictionary
        """
        print(f"📚 Loading {config_type} config for tenant: {tenant_id}")
        
        await self._initialize_platform()
        
        if not self.client_config_foundation:
            return {"success": False, "error": "Client Config Foundation not available"}
        
        try:
            configs = await self._load_tenant_configs(tenant_id)
            config = configs.get(config_type, {})
            
            if config:
                print(f"✅ Config loaded successfully")
                print(f"   Type: {config_type}")
                print(f"   Keys: {list(config.keys())}")
                return {"success": True, "config": config, "config_type": config_type}
            else:
                print(f"⚠️  No config found for type: {config_type}")
                return {"success": False, "error": f"No config found for type: {config_type}"}
                
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return {"success": False, "error": str(e)}
    
    async def config_validate(self, tenant_id: str, config_type: str, config_file: str) -> Dict[str, Any]:
        """
        Validate tenant-specific configuration.
        
        Args:
            tenant_id: Tenant ID
            config_type: Configuration type
            config_file: Path to configuration file (JSON)
        
        Returns:
            Validation result
        """
        print(f"🔍 Validating {config_type} config for tenant: {tenant_id}")
        
        await self._initialize_platform()
        
        if not self.client_config_foundation:
            return {"success": False, "error": "Client Config Foundation not available"}
        
        try:
            # Load config from file
            config_path = Path(config_file)
            if not config_path.exists():
                return {"success": False, "error": f"Config file not found: {config_file}"}
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Create ConfigValidator if needed
            if not self.config_validator or self.tenant_id != tenant_id:
                config_validator_builder = await self.client_config_foundation.create_config_validator(
                    tenant_id=tenant_id
                )
                # Get the instance from the builder (method name: get_validator)
                self.config_validator = config_validator_builder.get_validator()
                self.tenant_id = tenant_id
            
            # Validate config
            is_valid = await self.config_validator.validate_config(config_type, config)
            
            if is_valid:
                print(f"✅ Config validation passed")
                return {"success": True, "valid": True, "config_type": config_type}
            else:
                print(f"❌ Config validation failed")
                return {"success": False, "valid": False, "error": "Config validation failed"}
                
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def config_store(self, tenant_id: str, config_type: str, config_file: str) -> Dict[str, Any]:
        """
        Store tenant-specific configuration.
        
        Args:
            tenant_id: Tenant ID
            config_type: Configuration type
            config_file: Path to configuration file (JSON)
        
        Returns:
            Storage result with config_id
        """
        print(f"💾 Storing {config_type} config for tenant: {tenant_id}")
        
        await self._initialize_platform()
        
        if not self.client_config_foundation:
            return {"success": False, "error": "Client Config Foundation not available"}
        
        try:
            # Load config from file
            config_path = Path(config_file)
            if not config_path.exists():
                return {"success": False, "error": f"Config file not found: {config_file}"}
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Create ConfigStorage if needed
            if not self.config_storage or self.tenant_id != tenant_id:
                config_storage_builder = await self.client_config_foundation.create_config_storage(
                    tenant_id=tenant_id
                )
                # Get the instance from the builder (method name: get_storage)
                self.config_storage = config_storage_builder.get_storage()
                self.tenant_id = tenant_id
            
            # Store config
            config_id = await self.config_storage.store_config(config_type, config)
            
            print(f"✅ Config stored successfully")
            print(f"   Config ID: {config_id}")
            return {"success": True, "config_id": config_id, "config_type": config_type}
                
        except Exception as e:
            print(f"❌ Storage error: {e}")
            return {"success": False, "error": str(e)}
    
    async def config_version(self, tenant_id: str, config_type: str) -> Dict[str, Any]:
        """
        Get versions of tenant-specific configuration.
        
        Args:
            tenant_id: Tenant ID
            config_type: Configuration type
        
        Returns:
            List of versions
        """
        print(f"📋 Getting versions for {config_type} config (tenant: {tenant_id})")
        
        await self._initialize_platform()
        
        if not self.client_config_foundation:
            return {"success": False, "error": "Client Config Foundation not available"}
        
        try:
            # Create ConfigVersioner if needed
            if not self.config_versioner or self.tenant_id != tenant_id:
                config_versioner_builder = await self.client_config_foundation.create_config_versioner(
                    tenant_id=tenant_id
                )
                # Get the instance from the builder (method name: get_versioner)
                self.config_versioner = config_versioner_builder.get_versioner()
                self.tenant_id = tenant_id
            
            # Get versions
            versions = await self.config_versioner.get_versions(config_type)
            
            if versions:
                print(f"✅ Found {len(versions)} version(s)")
                for i, version in enumerate(versions, 1):
                    print(f"   Version {i}: {version}")
            else:
                print(f"⚠️  No versions found")
            
            return {"success": True, "versions": versions, "config_type": config_type}
                
        except Exception as e:
            print(f"❌ Version retrieval error: {e}")
            return {"success": False, "error": str(e)}


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Data Mash CLI Tool for Insurance Use Case',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest legacy data
  data-mash ingest ./client_drop/policy_dump_0425.dat --format=csv --tenant=client_abc

  # Profile ingested data
  data-mash profile --file-id=file_123 --output=profile_report.json

  # Map to canonical
  data-mash map-to-canonical --source-schema=schema_456 --canonical=policy_v1

  # Validate mapping
  data-mash validate-mapping --mapping-id=mapping_789

  # Generate migration plan
  data-mash generate-plan --source=legacy_system --target=new_platform --canonical=policy_v1
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest legacy insurance data')
    ingest_parser.add_argument('file', help='Path to data file')
    ingest_parser.add_argument('--format', default='auto', choices=['csv', 'json', 'xml', 'auto'],
                              help='File format (default: auto)')
    ingest_parser.add_argument('--tenant', help='Tenant ID for multi-tenant support')
    
    # Profile command
    profile_parser = subparsers.add_parser('profile', help='Profile ingested data')
    profile_parser.add_argument('--file-id', required=True, help='File ID from ingestion')
    profile_parser.add_argument('--output', help='Output file path for profile report')
    
    # Map-to-canonical command
    map_parser = subparsers.add_parser('map-to-canonical', help='Map source schema to canonical model')
    map_parser.add_argument('--source-schema', required=True, help='Source schema ID or path to schema file')
    map_parser.add_argument('--canonical', default='policy_v1', help='Canonical model name (default: policy_v1)')
    map_parser.add_argument('--tenant', help='Tenant ID for multi-tenant support')
    
    # Validate-mapping command
    validate_parser = subparsers.add_parser('validate-mapping', help='Validate mapping rules')
    validate_parser.add_argument('--mapping-id', required=True, help='Mapping ID from map-to-canonical')
    
    # Generate-plan command
    plan_parser = subparsers.add_parser('generate-plan', help='Generate migration plan')
    plan_parser.add_argument('--source', required=True, help='Source system ID')
    plan_parser.add_argument('--target', required=True, help='Target system ID')
    plan_parser.add_argument('--canonical', default='policy_v1', help='Canonical model name (default: policy_v1)')
    plan_parser.add_argument('--tenant', help='Tenant ID for multi-tenant support')
    
    # Config management commands
    config_parser = subparsers.add_parser('config', help='Manage tenant configurations')
    config_subparsers = config_parser.add_subparsers(dest='config_command', help='Config management commands')
    
    # Config load command
    config_load_parser = config_subparsers.add_parser('load', help='Load tenant configuration')
    config_load_parser.add_argument('tenant_id', help='Tenant ID')
    config_load_parser.add_argument('config_type', help='Configuration type (domain_models, workflows, ingestion_endpoints, etc.)')
    
    # Config validate command
    config_validate_parser = config_subparsers.add_parser('validate', help='Validate tenant configuration')
    config_validate_parser.add_argument('tenant_id', help='Tenant ID')
    config_validate_parser.add_argument('config_type', help='Configuration type')
    config_validate_parser.add_argument('config_file', help='Path to configuration file (JSON)')
    
    # Config store command
    config_store_parser = config_subparsers.add_parser('store', help='Store tenant configuration')
    config_store_parser.add_argument('tenant_id', help='Tenant ID')
    config_store_parser.add_argument('config_type', help='Configuration type')
    config_store_parser.add_argument('config_file', help='Path to configuration file (JSON)')
    
    # Config version command
    config_version_parser = config_subparsers.add_parser('version', help='Get versions of tenant configuration')
    config_version_parser.add_argument('tenant_id', help='Tenant ID')
    config_version_parser.add_argument('config_type', help='Configuration type')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize CLI
    cli = DataMashCLI()
    
    # Execute command
    try:
        if args.command == 'ingest':
            result = await cli.ingest(args.file, args.format, args.tenant)
        elif args.command == 'profile':
            result = await cli.profile(args.file_id, args.output)
        elif args.command == 'map-to-canonical':
            result = await cli.map_to_canonical(args.source_schema, args.canonical, args.tenant)
        elif args.command == 'validate-mapping':
            result = await cli.validate_mapping(args.mapping_id)
        elif args.command == 'generate-plan':
            result = await cli.generate_plan(args.source, args.target, args.canonical, args.tenant)
        elif args.command == 'config':
            # Config management commands
            if args.config_command == 'load':
                result = await cli.config_load(args.tenant_id, args.config_type)
            elif args.config_command == 'validate':
                result = await cli.config_validate(args.tenant_id, args.config_type, args.config_file)
            elif args.config_command == 'store':
                result = await cli.config_store(args.tenant_id, args.config_type, args.config_file)
            elif args.config_command == 'version':
                result = await cli.config_version(args.tenant_id, args.config_type)
            else:
                config_parser.print_help()
                sys.exit(1)
        else:
            parser.print_help()
            sys.exit(1)
        
        # Exit with error code if command failed
        if not result.get("success"):
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Command interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())


