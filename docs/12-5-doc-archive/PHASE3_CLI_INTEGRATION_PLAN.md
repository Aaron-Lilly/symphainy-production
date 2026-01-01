# Phase 3: CLI Integration with Client Config Foundation

**Date:** December 2024  
**Status:** 📋 **PLANNING**  
**Goal:** Enhance CLI to use Client Config SDK and expose CLI as a configurable experience

---

## 🎯 Strategic Vision

### **The Relationship: CLI ↔ Client Config Foundation**

**Both directions are true:**

1. **CLI USES Client Config SDK** (CLI as consumer)
   - CLI loads tenant-specific configurations via `ConfigLoader`
   - CLI validates configurations via `ConfigValidator`
   - CLI stores configuration updates via `ConfigStorage`
   - CLI manages configuration versions via `ConfigVersioner`

2. **CLI IS an Experience enabled by Client Config** (CLI as experience)
   - CLI is one of the "heads" that Experience Foundation enables
   - Client Config Foundation provides tenant-specific configs
   - CLI renders/configures based on those configs
   - Different tenants get different CLI capabilities based on their configs

### **Architecture Flow:**

```
┌─────────────────────────────────────────────────────────────┐
│         Client Config Foundation (Config Plane)              │
│  - Domain models (schemas, mapping rules)                    │
│  - Workflows (per-client workflows)                         │
│  - Dashboards & views (personalized)                        │
│  - Ingestion endpoints (per-client)                          │
│  - User management (RBAC hierarchy)                         │
│  - AI/agent personas (action patterns)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓ (provides configs)
┌─────────────────────────────────────────────────────────────┐
│              CLI Tool (Enhanced)                             │
│  Uses Client Config SDK:                                     │
│  - ConfigLoader → Load tenant-specific configs              │
│  - ConfigValidator → Validate configs before use           │
│  - ConfigStorage → Store config updates                    │
│  - ConfigVersioner → Manage config versions                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ (uses configs)
┌─────────────────────────────────────────────────────────────┐
│         Platform APIs (via Traefik)                          │
│  - Insurance Migration Orchestrator                         │
│  - Wave Orchestrator                                        │
│  - Policy Tracker Orchestrator                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Phase 3 Objectives

### **1. Enhance CLI to Use Client Config SDK**

**What:** Make CLI tenant-aware and config-driven

**How:**
- Initialize `ClientConfigFoundationService` in CLI
- Use `ConfigLoader` to load tenant-specific configurations
- Apply tenant configs to CLI commands (domain models, workflows, endpoints)
- Use `ConfigValidator` to validate configs before use
- Use `ConfigStorage` to store config updates
- Use `ConfigVersioner` to manage config versions

### **2. Make CLI Tenant-Aware**

**What:** CLI should be aware of tenant context and load appropriate configs

**How:**
- Add `--tenant` flag to CLI commands
- Load tenant-specific configs on CLI startup
- Apply tenant configs to command behavior
- Validate tenant access before operations

### **3. Expose CLI as Configurable Experience**

**What:** CLI capabilities should be driven by tenant configs

**How:**
- Different tenants can have different CLI command sets
- Tenant configs define available workflows, endpoints, mappings
- CLI dynamically adapts based on tenant configs

---

## 🔧 Implementation Tasks

### **Task 1: Integrate Client Config SDK into CLI**

**File:** `scripts/insurance_use_case/data_mash_cli.py`

**Changes:**
1. Add `ClientConfigFoundationService` initialization
2. Add `ConfigLoader` to load tenant configs
3. Add `ConfigValidator` to validate configs
4. Add `ConfigStorage` to store config updates
5. Add `ConfigVersioner` to manage versions

**Implementation:**
```python
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
        self.api_base_url = os.getenv("SYMPHAINY_API_URL", "http://localhost/api")
    
    async def _initialize_platform(self):
        """Initialize platform services (lazy initialization)."""
        if self.platform_initialized:
            return True
        
        try:
            # Initialize DI container and foundations
            di_container = DIContainer()
            platform_gateway = PlatformGatewayService(...)
            public_works_foundation = PublicWorksFoundationService(...)
            curator_foundation = CuratorFoundationService(...)
            
            # Initialize Client Config Foundation
            self.client_config_foundation = ClientConfigFoundationService(
                di_container=di_container,
                public_works_foundation=public_works_foundation,
                curator_foundation=curator_foundation
            )
            await self.client_config_foundation.initialize()
            
            # Initialize other services...
            self.platform_initialized = True
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize platform services: {e}")
            return False
    
    async def _load_tenant_configs(self, tenant_id: str):
        """Load tenant-specific configurations."""
        if not self.client_config_foundation:
            await self._initialize_platform()
        
        if not self.config_loader:
            self.config_loader = await self.client_config_foundation.create_config_loader(
                tenant_id=tenant_id
            )
        
        # Load tenant configs
        self.tenant_configs = {
            "domain_models": await self.config_loader.load_config("domain_models"),
            "workflows": await self.config_loader.load_config("workflows"),
            "ingestion_endpoints": await self.config_loader.load_config("ingestion_endpoints"),
        }
        
        return self.tenant_configs
```

### **Task 2: Add Tenant-Aware Commands**

**File:** `scripts/insurance_use_case/data_mash_cli.py`

**Changes:**
1. Add `--tenant` flag to all commands
2. Load tenant configs before executing commands
3. Apply tenant configs to command behavior
4. Validate tenant access

**Implementation:**
```python
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
    # Load tenant configs
    if tenant:
        await self._load_tenant_configs(tenant)
        self.tenant_id = tenant
        
        # Apply tenant-specific ingestion endpoint if configured
        ingestion_config = self.tenant_configs.get("ingestion_endpoints", {})
        if ingestion_config.get("custom_endpoint"):
            self.api_base_url = ingestion_config["custom_endpoint"]
    
    # Use tenant configs for domain models, workflows, etc.
    domain_models = self.tenant_configs.get("domain_models", {})
    
    # Rest of ingestion logic...
```

### **Task 3: Add Config Management Commands**

**File:** `scripts/insurance_use_case/data_mash_cli.py`

**Changes:**
1. Add `config load` command to load tenant configs
2. Add `config validate` command to validate configs
3. Add `config store` command to store config updates
4. Add `config version` command to manage versions

**Implementation:**
```python
async def config_load(self, tenant_id: str, config_type: str) -> Dict[str, Any]:
    """Load tenant-specific configuration."""
    await self._initialize_platform()
    configs = await self._load_tenant_configs(tenant_id)
    return configs.get(config_type, {})

async def config_validate(self, tenant_id: str, config_type: str, config: Dict[str, Any]) -> bool:
    """Validate tenant-specific configuration."""
    await self._initialize_platform()
    
    if not self.config_validator:
        self.config_validator = await self.client_config_foundation.create_config_validator(
            tenant_id=tenant_id
        )
    
    return await self.config_validator.validate_config(config_type, config)

async def config_store(self, tenant_id: str, config_type: str, config: Dict[str, Any]) -> str:
    """Store tenant-specific configuration."""
    await self._initialize_platform()
    
    if not self.config_storage:
        self.config_storage = await self.client_config_foundation.create_config_storage(
            tenant_id=tenant_id
        )
    
    config_id = await self.config_storage.store_config(config_type, config)
    return config_id

async def config_version(self, tenant_id: str, config_type: str) -> List[str]:
    """Get versions of tenant-specific configuration."""
    await self._initialize_platform()
    
    if not self.config_versioner:
        self.config_versioner = await self.client_config_foundation.create_config_versioner(
            tenant_id=tenant_id
        )
    
    return await self.config_versioner.get_versions(config_type)
```

### **Task 4: Update CLI Argument Parser**

**File:** `scripts/insurance_use_case/data_mash_cli.py`

**Changes:**
1. Add `--tenant` flag to all commands
2. Add `config` subcommand group
3. Add config management commands

**Implementation:**
```python
def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Data Mash CLI Tool for Insurance Use Case")
    parser.add_argument("--tenant", help="Tenant ID for multi-tenant operations")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Existing commands...
    ingest_parser = subparsers.add_parser("ingest", help="Ingest legacy insurance data")
    ingest_parser.add_argument("file_path", help="Path to data file")
    ingest_parser.add_argument("--format", default="auto", help="File format")
    ingest_parser.add_argument("--tenant", help="Tenant ID")
    
    # Config management commands
    config_parser = subparsers.add_parser("config", help="Manage tenant configurations")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    
    load_parser = config_subparsers.add_parser("load", help="Load tenant configuration")
    load_parser.add_argument("tenant_id", help="Tenant ID")
    load_parser.add_argument("config_type", help="Configuration type")
    
    validate_parser = config_subparsers.add_parser("validate", help="Validate tenant configuration")
    validate_parser.add_argument("tenant_id", help="Tenant ID")
    validate_parser.add_argument("config_type", help="Configuration type")
    validate_parser.add_argument("config_file", help="Path to configuration file")
    
    # ... more config commands
```

---

## 🧪 Testing

### **Test 1: CLI Loads Tenant Configs**

```bash
# Load tenant configs
python3 scripts/insurance_use_case/data_mash_cli.py config load tenant-123 domain_models
```

**Expected:** CLI loads and displays tenant-specific domain models

### **Test 2: CLI Uses Tenant Configs in Commands**

```bash
# Ingest with tenant configs
python3 scripts/insurance_use_case/data_mash_cli.py ingest data.csv --tenant tenant-123
```

**Expected:** CLI uses tenant-specific ingestion endpoint and domain models

### **Test 3: CLI Validates Configs**

```bash
# Validate tenant config
python3 scripts/insurance_use_case/data_mash_cli.py config validate tenant-123 workflows workflow.json
```

**Expected:** CLI validates configuration and reports success/failure

### **Test 4: CLI Stores Configs**

```bash
# Store tenant config
python3 scripts/insurance_use_case/data_mash_cli.py config store tenant-123 workflows workflow.json
```

**Expected:** CLI stores configuration and returns config ID

---

## 📊 Success Criteria

### **Phase 3 Complete When:**

1. ✅ CLI initializes `ClientConfigFoundationService`
2. ✅ CLI loads tenant-specific configs via `ConfigLoader`
3. ✅ CLI validates configs via `ConfigValidator`
4. ✅ CLI stores configs via `ConfigStorage`
5. ✅ CLI manages versions via `ConfigVersioner`
6. ✅ CLI commands are tenant-aware (accept `--tenant` flag)
7. ✅ CLI applies tenant configs to command behavior
8. ✅ All tests pass

---

## 🚀 Next Steps

1. **Implement Task 1:** Integrate Client Config SDK into CLI
2. **Implement Task 2:** Add tenant-aware commands
3. **Implement Task 3:** Add config management commands
4. **Implement Task 4:** Update CLI argument parser
5. **Test:** Run all tests
6. **Document:** Update CLI documentation

---

## 💡 Key Insights

### **CLI as Consumer of Client Config SDK:**
- CLI uses SDK to load, validate, store, and version tenant configs
- CLI behavior is driven by tenant configs
- CLI is tenant-aware

### **CLI as Experience Enabled by Client Config:**
- CLI is one of the "heads" that Experience Foundation enables
- Different tenants get different CLI capabilities
- CLI capabilities are configured via Client Config Foundation

### **Both Directions Work:**
- ✅ CLI uses Client Config SDK (CLI → SDK)
- ✅ CLI is an experience enabled by Client Config (Config → CLI)

---

**Last Updated:** December 2024  
**Status:** Ready for Implementation




