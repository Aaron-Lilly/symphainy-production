"""
Test All Infrastructure Adapters - Layer 1

Validates that ALL adapters created in _create_all_adapters() can be initialized.
This catches missing dependencies, configuration issues, and initialization problems at Layer 1.

This is critical for bottom-up testing - we must validate Layer 1 before proceeding to Layer 2.
"""

import pytest
import os

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

@pytest.mark.integration
@pytest.mark.infrastructure

class TestAllAdaptersInitialization:
    """Test all adapters can be initialized."""
    
    @pytest.fixture
    def config_adapter(self):
        """Create ConfigAdapter for adapter initialization."""
        from foundations.public_works_foundation.infrastructure_adapters.config_adapter import ConfigAdapter
        adapter = ConfigAdapter()
        adapter.set_env_from_file(".env")
        # Also load secrets if available
        secrets_path = os.path.join(os.path.dirname(__file__), "../../../symphainy-platform/.env.secrets")
        if os.path.exists(secrets_path):
            adapter.set_env_from_file(secrets_path)
        return adapter
    
    def test_supabase_adapter_initialization(self, config_adapter):
        """Test SupabaseAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.supabase_adapter import SupabaseAdapter
        
        url = config_adapter.get_supabase_url()
        anon_key = config_adapter.get_supabase_anon_key()
        service_key = config_adapter.get_supabase_service_key()
        
        if not url or not anon_key:
            pytest.skip("Supabase configuration not available")
        
        adapter = SupabaseAdapter(url=url, anon_key=anon_key, service_key=service_key)
        assert adapter is not None, "Adapter should be initialized"
    
    def test_jwt_adapter_initialization(self, config_adapter):
        """Test JWTAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.jwt_adapter import JWTAdapter
        
        jwt_config = config_adapter.get_jwt_config()
        if not jwt_config.get("secret_key"):
            pytest.skip("JWT secret key not configured")
        
        adapter = JWTAdapter(
            secret_key=jwt_config["secret_key"],
            algorithm=jwt_config.get("algorithm", "HS256")
        )
        assert adapter is not None, "Adapter should be initialized"
    
    def test_gcs_adapter_initialization(self, config_adapter):
        """Test GCSFileAdapter can be initialized (REQUIRED)."""
        from foundations.public_works_foundation.infrastructure_adapters.gcs_file_adapter import GCSFileAdapter
        import os
        
        gcs_config = config_adapter.get_gcs_config()
        
        if not gcs_config.get("bucket_name") or not gcs_config.get("project_id"):
            pytest.fail(
                "GCS configuration missing (REQUIRED). "
                "Set GCS_BUCKET_NAME and GCS_PROJECT_ID environment variables."
            )
        
        # Handle bucket credentials (ONLY from GCS_CREDENTIALS_PATH - never from GOOGLE_APPLICATION_CREDENTIALS)
        # CRITICAL: GOOGLE_APPLICATION_CREDENTIALS is for SSH/VM access, not bucket access
        credentials_path = gcs_config.get("credentials_path")  # This is GCS_CREDENTIALS_PATH
        
        if credentials_path and not os.path.exists(credentials_path):
            credentials_path = None  # Use Application Default Credentials
        
        try:
            adapter = GCSFileAdapter(
                project_id=gcs_config.get("project_id"),
                bucket_name=gcs_config["bucket_name"],
                credentials_path=credentials_path
            )
            assert adapter is not None, "Adapter should be initialized"
        except Exception as e:
            pytest.fail(f"GCSFileAdapter failed to initialize (REQUIRED): {e}")
    
    def test_supabase_file_management_adapter_initialization(self, config_adapter):
        """Test SupabaseFileManagementAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
        from foundations.public_works_foundation.infrastructure_adapters.supabase_adapter import SupabaseAdapter
        
        url = config_adapter.get_supabase_url()
        anon_key = config_adapter.get_supabase_anon_key()
        service_key = config_adapter.get_supabase_service_key()
        
        if not url or not anon_key:
            pytest.skip("Supabase configuration not available")
        
        # Create SupabaseAdapter first
        supabase_adapter = SupabaseAdapter(url=url, anon_key=anon_key, service_key=service_key)
        
        adapter = SupabaseFileManagementAdapter(
            url=supabase_adapter.url,
            service_key=supabase_adapter.service_key or supabase_adapter.anon_key
        )
        assert adapter is not None, "Adapter should be initialized"
    
    def test_opentelemetry_health_adapter_initialization(self):
        """Test OpenTelemetryHealthAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.opentelemetry_health_adapter import OpenTelemetryHealthAdapter
        
        adapter = OpenTelemetryHealthAdapter(
            service_name="test_health",
            endpoint="http://localhost:4317",
            timeout=30
        )
        assert adapter is not None, "Adapter should be initialized"
    
    def test_telemetry_adapter_initialization(self):
        """Test TelemetryAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.telemetry_adapter import TelemetryAdapter
        
        adapter = TelemetryAdapter(
            service_name="test_telemetry",
            service_version="1.0.0"
        )
        assert adapter is not None, "Adapter should be initialized"
    
    def test_redis_alerting_adapter_initialization(self):
        """Test RedisAlertingAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.redis_alerting_adapter import RedisAlertingAdapter
        
        adapter = RedisAlertingAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_standard_visualization_adapter_initialization(self):
        """Test StandardVisualizationAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.standard_visualization_adapter import StandardVisualizationAdapter
        
        adapter = StandardVisualizationAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_standard_business_metrics_adapter_initialization(self):
        """Test StandardBusinessMetricsAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.standard_business_metrics_adapter import StandardBusinessMetricsAdapter
        
        adapter = StandardBusinessMetricsAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_huggingface_business_metrics_adapter_initialization(self):
        """Test HuggingFaceBusinessMetricsAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.huggingface_business_metrics_adapter import HuggingFaceBusinessMetricsAdapter
        
        adapter = HuggingFaceBusinessMetricsAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_celery_adapter_initialization(self, config_adapter):
        """Test CeleryAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.celery_adapter import CeleryAdapter
        
        redis_config = config_adapter.get_redis_config()
        adapter = CeleryAdapter(
            broker_url=f"redis://{redis_config['host']}:{redis_config['port']}/0",
            result_backend=f"redis://{redis_config['host']}:{redis_config['port']}/0"
        )
        assert adapter is not None, "Adapter should be initialized"
    
    def test_redis_graph_adapter_initialization(self, config_adapter):
        """Test RedisGraphAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.redis_graph_adapter import RedisGraphAdapter
        
        redis_config = config_adapter.get_redis_config()
        adapter = RedisGraphAdapter(
            host=redis_config["host"],
            port=redis_config["port"],
            db=1
        )
        assert adapter is not None, "Adapter should be initialized"
    
    def test_resource_adapter_initialization(self):
        """Test ResourceAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.resource_adapter import ResourceAdapter
        
        adapter = ResourceAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_redis_graph_knowledge_adapter_initialization(self, config_adapter):
        """Test RedisGraphKnowledgeAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.redis_graph_knowledge_adapter import RedisGraphKnowledgeAdapter
        
        redis_config = config_adapter.get_redis_config()
        adapter = RedisGraphKnowledgeAdapter(
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
            db=1
        )
        assert adapter is not None, "Adapter should be initialized"
    
    def test_bpmn_processing_adapter_initialization(self):
        """Test BPMNProcessingAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.bpmn_processing_adapter import BPMNProcessingAdapter
        
        adapter = BPMNProcessingAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_sop_parsing_adapter_initialization(self):
        """Test SOPParsingAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.sop_parsing_adapter import SOPParsingAdapter
        
        adapter = SOPParsingAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_sop_enhancement_adapter_initialization(self):
        """Test SOPEnhancementAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.sop_enhancement_adapter import SOPEnhancementAdapter
        
        adapter = SOPEnhancementAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_standard_strategic_planning_adapter_initialization(self):
        """Test StandardStrategicPlanningAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.standard_strategic_planning_adapter import StandardStrategicPlanningAdapter
        
        adapter = StandardStrategicPlanningAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    def test_standard_financial_adapter_initialization(self):
        """Test StandardFinancialAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.standard_financial_adapter import StandardFinancialAdapter
        
        adapter = StandardFinancialAdapter()
        assert adapter is not None, "Adapter should be initialized"
    
    @pytest.mark.asyncio
    async def test_consul_service_discovery_adapter_initialization(self, config_adapter):
        """Test ConsulServiceDiscoveryAdapter can be initialized."""
        from foundations.public_works_foundation.infrastructure_adapters.consul_service_discovery_adapter import ConsulServiceDiscoveryAdapter
        import consul
        
        consul_host = config_adapter.get("CONSUL_HOST", "localhost")
        consul_port = int(config_adapter.get("CONSUL_PORT", "8500"))
        consul_token = config_adapter.get("CONSUL_TOKEN", None)
        consul_datacenter = config_adapter.get("CONSUL_DATACENTER", None)
        
        consul_client_config = {"host": consul_host, "port": consul_port}
        if consul_token:
            consul_client_config["token"] = consul_token
        if consul_datacenter:
            consul_client_config["dc"] = consul_datacenter
        
        consul_client = consul.Consul(**consul_client_config)
        adapter = ConsulServiceDiscoveryAdapter(
            consul_client=consul_client,
            service_name="test_service"
        )
        assert adapter is not None, "Adapter should be initialized"
        
        # Test connection (may fail if Consul not running, but adapter should still be created)
        try:
            await adapter.connect()
        except Exception:
            pass  # Consul may not be running, but adapter should still be initialized
