# Scripts Directory

This directory contains all utility scripts for the Symphainy Platform, organized into logical categories for easy navigation and maintenance.

## 📁 Directory Structure

### 🟢 **active/** - Production Ready Scripts
Scripts that are actively used in production and development environments.

#### **setup/** - Environment Setup Scripts
- `setup_dependencies.py` - Resolves MCP and FastAPI dependency conflicts
- `setup_environment.py` - Environment configuration setup
- `setup_dev.sh` - Development environment setup
- `setup_test_database.py` - Test database setup
- `setup_test_environment.sh` - Test environment setup
- `setup_testing_infrastructure.py` - Testing infrastructure setup

#### **service/** - Service Management Scripts
- `startup_gateway.sh` - MCP Gateway startup script
- `startup_orchestrated.sh` - Orchestrated startup script
- `startup_robust.sh` - Robust startup with health checks
- `startup-testing.sh` - Testing environment startup
- `service_orchestrator.py` - Service orchestration logic

#### **testing/** - Testing Scripts
- `run_enhanced_e2e_tests.py` - Comprehensive E2E testing
- `run_tests.py` - Main test runner
- `run_tests.sh` - Test runner shell script

#### **production/** - Production Readiness Scripts
- `check_production_readiness.py` - Production readiness validator
- `validate_api_contracts.py` - API contract validation
- `capability_inventory.py` - Capability analysis and inventory

### 🟡 **evaluate/** - Scripts to Evaluate
Scripts that may be useful but need evaluation for production use.

#### **development/** - Development Tools
- `analyze_frontend_apis.py` - Frontend API analysis
- `check_anti_patterns.py` - Anti-pattern detection
- `infrastructure_audit.py` - Infrastructure auditing
- `trace_infrastructure_pipeline.py` - Pipeline tracing

#### **testing/** - Test Scripts
- `test_direct_connection.py` - Direct connection testing
- `test_direct_rest_connection.py` - REST connection testing
- `test_e2e_connection.py` - E2E connection testing
- `test_e2e_solution.py` - E2E solution testing
- `test_simple_curator.py` - Simple curator testing
- `test_simple_tool_exposure.py` - Tool exposure testing
- `test_tool_exposure.py` - Tool exposure testing

### 🔴 **archive/** - Legacy/Obsolete Scripts
Scripts that are no longer used but kept for reference.

#### **legacy_development/** - Legacy Development Scripts
- `add_cross_dimensional_integration.py` - Legacy integration script
- `add_mcp_tools_remaining_pillars.py` - Legacy MCP tools script
- `add_utilities_to_mcp_servers.py` - Legacy utilities script
- `create_placeholder_modules.py` - Legacy placeholder creation
- `deploy_test.py` - Legacy deployment test

#### **legacy_validation/** - Legacy Validation Scripts
- `validate_smart_city_compliance.py` - Legacy Smart City validation
- `validate_smart_city_compliance_fixed.py` - Legacy Smart City validation (fixed)
- `validate_utilities_integration.py` - Legacy utilities validation
- `validate_utilities_integration_fixed.py` - Legacy utilities validation (fixed)

## 🚀 Usage

### Running Active Scripts
```bash
# Setup environment
./active/setup/setup_dev.sh

# Start services
./active/service/startup_robust.sh

# Run tests
./active/testing/run_tests.py

# Check production readiness
./active/production/check_production_readiness.py
```

### Evaluating Scripts
Scripts in the `evaluate/` directory should be tested and evaluated before moving to `active/`.

### Archived Scripts
Scripts in the `archive/` directory are kept for reference but should not be used in production.

## 📝 Maintenance

- **Active scripts** should be regularly maintained and updated
- **Evaluate scripts** should be reviewed periodically for promotion to active
- **Archive scripts** should be reviewed for potential deletion after 6 months

## 🔧 Adding New Scripts

1. **Development scripts** → `evaluate/development/`
2. **Test scripts** → `evaluate/testing/`
3. **Production scripts** → `active/` (appropriate subdirectory)
4. **Legacy scripts** → `archive/` (appropriate subdirectory)

## 📞 Support

For questions about scripts, refer to the individual script documentation or contact the development team.


