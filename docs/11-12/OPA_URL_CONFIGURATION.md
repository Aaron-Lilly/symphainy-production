# OPA URL Configuration

**Date**: November 13, 2025  
**Purpose**: Document where and how to configure OPA_URL for the platform

---

## Configuration Location

OPA_URL is configured in **environment-specific config files** located in:
```
symphainy-platform/config/
├── development.env
├── production.env
├── staging.env
└── testing.env
```

These files are loaded by the `ConfigAdapter` during platform startup based on the `ENVIRONMENT` environment variable.

---

## Configuration Values

### Development (`development.env`)
```bash
OPA_URL=http://localhost:8181
```
- **Purpose**: Local development with OPA running in Docker or locally
- **Usage**: Run OPA locally or via Docker for development

### Testing (`testing.env`)
```bash
OPA_URL=http://localhost:8181
```
- **Purpose**: Local testing with OPA
- **Usage**: Same as development, or use a mock OPA service for tests

### Staging (`staging.env`)
```bash
OPA_URL=https://your-staging-opa-service-url
```
- **Purpose**: Staging environment with managed OPA service
- **Usage**: Replace with your staging OPA service URL (Option C deployment)

### Production (`production.env`)
```bash
OPA_URL=https://your-managed-opa-service-url
```
- **Purpose**: Production environment with managed OPA service
- **Usage**: Replace with your production OPA service URL (Option C deployment)

---

## How It Works

1. **Startup Process**:
   - Platform reads `ENVIRONMENT` environment variable
   - Loads corresponding config file from `symphainy-platform/config/{environment}.env`
   - `ConfigAdapter` reads `OPA_URL` from the config file
   - `PublicWorksFoundationService` uses `config_adapter.get("OPA_URL", "http://localhost:8181")`

2. **Code Flow**:
   ```python
   # In PublicWorksFoundationService._create_all_adapters()
   opa_url = self.config_adapter.get("OPA_URL", "http://localhost:8181")
   policy_adapter = OPAPolicyAdapter(opa_url=opa_url)
   ```

3. **Default Fallback**:
   - If `OPA_URL` is not found in config, defaults to `http://localhost:8181`
   - This ensures local development works even if config is missing

---

## Docker Configuration

### Option 1: Local OPA (Development)

If you want to run OPA locally via Docker, you can add it to `docker-compose.infrastructure.yml`:

```yaml
  # OPA - Policy Engine
  opa:
    image: openpolicyagent/opa:latest
    container_name: symphainy-opa
    ports:
      - "8181:8181"
    command: run --server --log-level debug
    networks:
      - smart_city_net
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8181/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped
```

Then use `OPA_URL=http://opa:8181` in your config (for Docker networking) or `OPA_URL=http://localhost:8181` (for host access).

### Option 2: Managed OPA Service (Option C - Production)

For Option C deployment, use a managed OPA service:
- **Cloud Provider**: Use your cloud provider's managed OPA service
- **Self-Hosted**: Use your own OPA service URL
- **Example**: `https://opa.your-domain.com` or `https://your-opa-service.cloud-provider.com`

---

## Environment Variable Override

You can also override `OPA_URL` using environment variables (takes precedence over config files):

```bash
export OPA_URL=https://custom-opa-url.com
```

This is useful for:
- Docker containers
- CI/CD pipelines
- Kubernetes deployments
- Local overrides

---

## Verification

To verify OPA_URL is loaded correctly:

1. **Check logs** during startup:
   ```
   ✅ Policy adapter created (OPA: http://localhost:8181)
   ```

2. **Test policy evaluation**:
   - Platform should connect to OPA at the configured URL
   - Policy evaluations should work correctly

---

## Summary

| Environment | Config File | OPA_URL Value | Notes |
|-------------|-------------|---------------|-------|
| Development | `development.env` | `http://localhost:8181` | Local OPA |
| Testing | `testing.env` | `http://localhost:8181` | Local OPA or mock |
| Staging | `staging.env` | `https://your-staging-opa-service-url` | Managed service (update) |
| Production | `production.env` | `https://your-managed-opa-service-url` | Managed service (update) |

**Action Required**: Update staging and production URLs with your actual managed OPA service URLs when deploying.





