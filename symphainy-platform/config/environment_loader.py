#!/usr/bin/env python3
"""
Environment Configuration Loader

Loads environment-specific configurations and integrates with foundation services.
Provides a clean interface for accessing configuration values across the application.

WHAT (Module Role): I load and provide environment-specific configurations
HOW (Module Implementation): I integrate with foundation services and provide clean access
"""

import os
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Using absolute imports from project root

from config import ConfigManager, Environment


class EnvironmentLoader:
    """
    Environment Configuration Loader
    
    Loads and manages environment-specific configurations with integration
    to foundation services and application components.
    """
    
    def __init__(self, environment: Optional[Environment] = None):
        """Initialize environment loader."""
        self.config_manager = ConfigManager(environment)
        self.environment = self.config_manager.get_environment()
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration for current environment."""
        required_keys = self._get_required_keys()
        missing_keys = []
        
        for key in required_keys:
            if not self.config_manager.get(key):
                missing_keys.append(key)
        
        if missing_keys:
            print(f"⚠️ Missing required configuration keys: {', '.join(missing_keys)}")
            if self.environment == Environment.PRODUCTION:
                raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
    
    def _get_required_keys(self) -> list:
        """
        Get required configuration keys for current environment.
        
        BREAKING: Removed JWT_SECRET from required keys.
        Supabase handles all user authentication tokens, so JWT_SECRET is not needed.
        """
        base_keys = [
            "ARANGO_URL",
            "REDIS_URL"
            # "SECRET_KEY"  # ❌ REMOVED - No actual usage found (may be legacy)
            # "JWT_SECRET"  # ❌ REMOVED - Supabase handles JWT tokens
        ]
        
        if self.environment == Environment.PRODUCTION:
            base_keys.extend([
                "SUPABASE_URL",
                "SUPABASE_KEY"
            ])
        
        return base_keys
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "url": self.config_manager.get("ARANGO_URL"),
            "pool_size": self.config_manager.get_int("DATABASE_POOL_SIZE", 10),
            "max_overflow": self.config_manager.get_int("DATABASE_MAX_OVERFLOW", 20),
            "echo": self.config_manager.get_bool("API_DEBUG", False)
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration."""
        return {
            "url": self.config_manager.get("REDIS_URL"),
            "password": self.config_manager.get("REDIS_PASSWORD"),
            "decode_responses": True
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API server configuration."""
        return {
            "host": self.config_manager.get("API_HOST", "0.0.0.0"),
            "port": self.config_manager.get_int("API_PORT", 8000),
            "debug": self.config_manager.get_bool("API_DEBUG", False),
            "reload": self.config_manager.get_bool("API_RELOAD", False)
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """
        Get security configuration.
        
        BREAKING: Removed jwt_secret from security config.
        Supabase handles all user authentication tokens.
        """
        return {
            # "secret_key": self.config_manager.get("SECRET_KEY"),  # ❌ REMOVED - No actual usage found (may be legacy)
            # "jwt_secret": self.config_manager.get("JWT_SECRET"),  # ❌ REMOVED - Supabase handles JWT
            "jwt_algorithm": self.config_manager.get("JWT_ALGORITHM", "HS256"),  # Kept for backward compatibility but not used
            "jwt_expiration": self.config_manager.get_int("JWT_EXPIRATION", 3600)  # Kept for backward compatibility but not used
        }
    
    def get_external_services_config(self) -> Dict[str, Any]:
        """Get external services configuration."""
        return {
            "supabase": {
                "url": self.config_manager.get("SUPABASE_URL"),
                "key": self.config_manager.get("SUPABASE_KEY")
            },
            "openai": {
                "api_key": self.config_manager.get("OPENAI_API_KEY")
            },
            "anthropic": {
                "api_key": self.config_manager.get("ANTHROPIC_API_KEY")
            }
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            "enable_metrics": self.config_manager.get_bool("ENABLE_METRICS", True),
            "metrics_port": self.config_manager.get_int("METRICS_PORT", 9090),
            "enable_tracing": self.config_manager.get_bool("ENABLE_TRACING", True),
            "tracing_sample_rate": float(self.config_manager.get("TRACING_SAMPLE_RATE", "1.0"))
        }
    
    def get_health_monitoring_config(self) -> Dict[str, Any]:
        """Get health monitoring configuration."""
        return {
            "enabled": self.config_manager.get_bool("HEALTH_MONITORING_ENABLED", True),
            "check_interval_seconds": self.config_manager.get_int("HEALTH_CHECK_INTERVAL_SECONDS", 30),
            "timeout_seconds": self.config_manager.get_int("HEALTH_CHECK_TIMEOUT_SECONDS", 10),
            "thresholds": {
                "cpu_percent": self.config_manager.get_float("HEALTH_THRESHOLD_CPU_PERCENT", 80.0),
                "memory_percent": self.config_manager.get_float("HEALTH_THRESHOLD_MEMORY_PERCENT", 85.0),
                "disk_percent": self.config_manager.get_float("HEALTH_THRESHOLD_DISK_PERCENT", 90.0),
                "response_time_ms": self.config_manager.get_int("HEALTH_THRESHOLD_RESPONSE_TIME_MS", 5000),
                "error_rate_percent": self.config_manager.get_float("HEALTH_THRESHOLD_ERROR_RATE_PERCENT", 5.0)
            },
            "slo_targets": {
                "availability_percent": self.config_manager.get_float("SLO_AVAILABILITY_PERCENT", 99.9),
                "response_time_p95_ms": self.config_manager.get_int("SLO_RESPONSE_TIME_P95_MS", 2000),
                "error_rate_percent": self.config_manager.get_float("SLO_ERROR_RATE_PERCENT", 0.1)
            },
            "retention_days": self.config_manager.get_int("HEALTH_DATA_RETENTION_DAYS", 30)
        }
    
    def get_alerting_config(self) -> Dict[str, Any]:
        """Get alert management configuration."""
        return {
            "enabled": self.config_manager.get_bool("ALERT_MANAGEMENT_ENABLED", True),
            "severity_levels": self.config_manager.get_list("ALERT_SEVERITY_LEVELS", ["critical", "warning", "info"]),
            "notification_channels": self.config_manager.get_list("ALERT_NOTIFICATION_CHANNELS", ["email", "slack", "webhook"]),
            "retention_days": self.config_manager.get_int("ALERT_RETENTION_DAYS", 30),
            "escalation": {
                "enabled": self.config_manager.get_bool("ALERT_ESCALATION_ENABLED", True),
                "escalation_delay_minutes": self.config_manager.get_int("ALERT_ESCALATION_DELAY_MINUTES", 15),
                "max_escalation_levels": self.config_manager.get_int("ALERT_MAX_ESCALATION_LEVELS", 3)
            },
            "suppression": {
                "enabled": self.config_manager.get_bool("ALERT_SUPPRESSION_ENABLED", True),
                "suppression_window_minutes": self.config_manager.get_int("ALERT_SUPPRESSION_WINDOW_MINUTES", 60)
            },
            "webhook_url": self.config_manager.get("ALERT_WEBHOOK_URL"),
            "email_config": {
                "smtp_host": self.config_manager.get("ALERT_SMTP_HOST"),
                "smtp_port": self.config_manager.get_int("ALERT_SMTP_PORT", 587),
                "smtp_username": self.config_manager.get("ALERT_SMTP_USERNAME"),
                "smtp_password": self.config_manager.get("ALERT_SMTP_PASSWORD"),
                "from_email": self.config_manager.get("ALERT_FROM_EMAIL"),
                "to_emails": self.config_manager.get_list("ALERT_TO_EMAILS", [])
            }
        }
    
    def get_failure_classification_config(self) -> Dict[str, Any]:
        """Get failure classification configuration."""
        return {
            "enabled": self.config_manager.get_bool("FAILURE_CLASSIFICATION_ENABLED", True),
            "pattern_detection": self.config_manager.get_bool("FAILURE_PATTERN_DETECTION", True),
            "recovery_automation": self.config_manager.get_bool("FAILURE_RECOVERY_AUTOMATION", True),
            "classification_rules": {
                "timeout_threshold_ms": self.config_manager.get_int("FAILURE_TIMEOUT_THRESHOLD_MS", 30000),
                "error_rate_threshold_percent": self.config_manager.get_float("FAILURE_ERROR_RATE_THRESHOLD_PERCENT", 10.0),
                "consecutive_failures_threshold": self.config_manager.get_int("FAILURE_CONSECUTIVE_FAILURES_THRESHOLD", 3),
                "memory_leak_threshold_mb": self.config_manager.get_int("FAILURE_MEMORY_LEAK_THRESHOLD_MB", 1000)
            },
            "recovery_strategies": {
                "restart_service": self.config_manager.get_bool("FAILURE_RECOVERY_RESTART_SERVICE", True),
                "scale_out": self.config_manager.get_bool("FAILURE_RECOVERY_SCALE_OUT", True),
                "circuit_breaker": self.config_manager.get_bool("FAILURE_RECOVERY_CIRCUIT_BREAKER", True),
                "rollback": self.config_manager.get_bool("FAILURE_RECOVERY_ROLLBACK", True)
            },
            "retention_days": self.config_manager.get_int("FAILURE_DATA_RETENTION_DAYS", 90)
        }
    
    def get_telemetry_config(self) -> Dict[str, Any]:
        """Get telemetry collection configuration."""
        return {
            "enabled": self.config_manager.get_bool("TELEMETRY_COLLECTION_ENABLED", True),
            "collection_interval": self.config_manager.get_int("TELEMETRY_COLLECTION_INTERVAL_SECONDS", 10),
            "batch_size": self.config_manager.get_int("TELEMETRY_COLLECTION_BATCH_SIZE", 100),
            "flush_interval": self.config_manager.get_int("TELEMETRY_COLLECTION_FLUSH_INTERVAL_SECONDS", 30),
            "metrics_enabled": self.config_manager.get_bool("TELEMETRY_METRICS_ENABLED", True),
            "events_enabled": self.config_manager.get_bool("TELEMETRY_EVENTS_ENABLED", True),
            "traces_enabled": self.config_manager.get_bool("TELEMETRY_TRACES_ENABLED", True),
            "logs_enabled": self.config_manager.get_bool("TELEMETRY_LOGS_ENABLED", True),
            "sampling_rate": self.config_manager.get_float("TELEMETRY_SAMPLING_RATE", 1.0),
            "metrics_sampling_rate": self.config_manager.get_float("TELEMETRY_METRICS_SAMPLING_RATE", 1.0),
            "traces_sampling_rate": self.config_manager.get_float("TELEMETRY_TRACES_SAMPLING_RATE", 0.1),
            "logs_sampling_rate": self.config_manager.get_float("TELEMETRY_LOGS_SAMPLING_RATE", 0.5),
            "storage_type": self.config_manager.get("TELEMETRY_STORAGE_TYPE", "arangodb"),
            "retention_days": self.config_manager.get_int("TELEMETRY_STORAGE_RETENTION_DAYS", 30),
            "compression": self.config_manager.get_bool("TELEMETRY_STORAGE_COMPRESSION", True),
            "indexing": self.config_manager.get_bool("TELEMETRY_STORAGE_INDEXING", True),
            "otel": {
                "enabled": self.config_manager.get_bool("OTEL_ENABLED", True),
                "exporter_endpoint": self.config_manager.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
                "traces_endpoint": self.config_manager.get("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT", "http://localhost:4317"),
                "metrics_endpoint": self.config_manager.get("OTEL_EXPORTER_OTLP_METRICS_ENDPOINT", "http://localhost:4317"),
                "logs_endpoint": self.config_manager.get("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT", "http://localhost:4317"),
                "service_name": self.config_manager.get("OTEL_SERVICE_NAME", "smart-city-platform"),
                "service_version": self.config_manager.get("OTEL_SERVICE_VERSION", "1.0.0"),
                "environment": self.config_manager.get("OTEL_ENVIRONMENT", "development"),
                "resource_attributes": self.config_manager.get("OTEL_RESOURCE_ATTRIBUTES", "service.name=smart-city-platform,service.version=1.0.0,deployment.environment=development"),
                "traces_sampler": self.config_manager.get("OTEL_TRACES_SAMPLER", "always_on"),
                "traces_sampler_arg": self.config_manager.get_float("OTEL_TRACES_SAMPLER_ARG", 1.0),
                "metrics_exporter": self.config_manager.get("OTEL_METRICS_EXPORTER", "otlp"),
                "logs_exporter": self.config_manager.get("OTEL_LOGS_EXPORTER", "otlp"),
                "bsp_schedule_delay": self.config_manager.get_int("OTEL_BSP_SCHEDULE_DELAY", 5000),
                "bsp_export_timeout": self.config_manager.get_int("OTEL_BSP_EXPORT_TIMEOUT", 30000),
                "bsp_max_queue_size": self.config_manager.get_int("OTEL_BSP_MAX_QUEUE_SIZE", 2048),
                "bsp_max_export_batch_size": self.config_manager.get_int("OTEL_BSP_MAX_EXPORT_BATCH_SIZE", 512)
            },
            "tempo": {
                "enabled": self.config_manager.get_bool("TEMPO_ENABLED", True),
                "container_name": self.config_manager.get("TEMPO_CONTAINER_NAME", "symphainy-tempo"),
                "ui_port": self.config_manager.get_int("TEMPO_CONTAINER_PORT_UI", 3200),
                "otlp_grpc_port": self.config_manager.get_int("TEMPO_CONTAINER_PORT_OTLP_GRPC", 4317),
                "otlp_http_port": self.config_manager.get_int("TEMPO_CONTAINER_PORT_OTLP_HTTP", 4318),
                "version": self.config_manager.get("TEMPO_CONTAINER_VERSION", "latest"),
                "retention_days": self.config_manager.get_int("TEMPO_RETENTION_DAYS", 7),
                "compression_enabled": self.config_manager.get_bool("TEMPO_COMPRESSION_ENABLED", True),
                "query_timeout": self.config_manager.get("TEMPO_QUERY_TIMEOUT", "30s"),
                "query_max_concurrent": self.config_manager.get_int("TEMPO_QUERY_MAX_CONCURRENT", 20)
            },
            "arango_telemetry": {
                "enabled": self.config_manager.get_bool("ARANGO_TELEMETRY_ENABLED", True),
                "host": self.config_manager.get("ARANGO_TELEMETRY_HOST", "localhost"),
                "port": self.config_manager.get_int("ARANGO_TELEMETRY_PORT", 8529),
                "database": self.config_manager.get("ARANGO_TELEMETRY_DATABASE", "telemetry"),
                "username": self.config_manager.get("ARANGO_TELEMETRY_USERNAME", "root"),
                "password": self.config_manager.get("ARANGO_TELEMETRY_PASSWORD", "admin"),
                "collection_prefix": self.config_manager.get("ARANGO_TELEMETRY_COLLECTION_PREFIX", "telemetry_"),
                "retention_days": self.config_manager.get_int("ARANGO_TELEMETRY_RETENTION_DAYS", 30),
                "batch_size": self.config_manager.get_int("ARANGO_TELEMETRY_BATCH_SIZE", 1000),
                "flush_interval": self.config_manager.get_int("ARANGO_TELEMETRY_FLUSH_INTERVAL", 30),
                "indexing": self.config_manager.get_bool("ARANGO_TELEMETRY_INDEXING", True),
                "compression": self.config_manager.get_bool("ARANGO_TELEMETRY_COMPRESSION", True)
            }
        }
    
    def get_metrics_storage_config(self) -> Dict[str, Any]:
        """Get metrics storage configuration."""
        return {
            "enabled": self.config_manager.get_bool("METRICS_STORAGE_ENABLED", True),
            "storage_type": self.config_manager.get("METRICS_STORAGE_TYPE", "arangodb"),
            "arangodb": {
                "url": self.config_manager.get("ARANGO_URL", "http://localhost:8529"),
                "database": self.config_manager.get("ARANGO_DB", "symphainy_metadata"),
                "collection": self.config_manager.get("METRICS_COLLECTION_NAME", "metrics_data"),
                "username": self.config_manager.get("ARANGO_USER", "root"),
                "password": self.config_manager.get("ARANGO_PASS", "")
            },
            "redis": {
                "host": self.config_manager.get("REDIS_HOST", "localhost"),
                "port": self.config_manager.get_int("REDIS_PORT", 6379),
                "db": self.config_manager.get_int("METRICS_REDIS_DB", 2),
                "password": self.config_manager.get("REDIS_PASSWORD", "")
            },
            "retention_days": self.config_manager.get_int("METRICS_RETENTION_DAYS", 30),
            "aggregation_intervals": {
                "minute": self.config_manager.get_bool("METRICS_AGGREGATION_MINUTE", True),
                "hour": self.config_manager.get_bool("METRICS_AGGREGATION_HOUR", True),
                "day": self.config_manager.get_bool("METRICS_AGGREGATION_DAY", True)
            }
        }
    
    def get_celery_config(self) -> Dict[str, Any]:
        """Get Celery configuration."""
        return {
            "enabled": self.config_manager.get_bool("CELERY_ENABLED", True),
            "broker_url": self.config_manager.get("CELERY_BROKER_URL", "redis://localhost:6379/1"),
            "result_backend": self.config_manager.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
            "broker_transport": self.config_manager.get("CELERY_BROKER_TRANSPORT", "redis"),
            "worker_concurrency": self.config_manager.get_int("CELERY_WORKER_CONCURRENCY", 4),
            "task_serializer": self.config_manager.get("CELERY_TASK_SERIALIZER", "json"),
            "result_serializer": self.config_manager.get("CELERY_RESULT_SERIALIZER", "json"),
            "accept_content": [self.config_manager.get("CELERY_ACCEPT_CONTENT", "json")],
            "timezone": self.config_manager.get("CELERY_TIMEZONE", "UTC"),
            "enable_utc": self.config_manager.get_bool("CELERY_ENABLE_UTC", True),
            "enable_monitoring": self.config_manager.get_bool("CELERY_ENABLE_MONITORING", True),
            "monitoring_interval": self.config_manager.get_int("CELERY_MONITORING_INTERVAL", 60),
            "task_routes": self.config_manager.get("CELERY_TASK_ROUTES", "").split(",") if self.config_manager.get("CELERY_TASK_ROUTES") else [],
            "task_always_eager": self.config_manager.get_bool("CELERY_TASK_ALWAYS_EAGER", False),
            "task_eager_propagates": self.config_manager.get_bool("CELERY_TASK_EAGER_PROPAGATES", True),
            "task_ignore_result": self.config_manager.get_bool("CELERY_TASK_IGNORE_RESULT", False),
            "worker_prefetch_multiplier": self.config_manager.get_int("CELERY_WORKER_PREFETCH_MULTIPLIER", 1),
            "task_acks_late": self.config_manager.get_bool("CELERY_TASK_ACKS_LATE", True),
            "result_expires": self.config_manager.get_int("CELERY_RESULT_EXPIRES", 3600),
            "result_persistent": self.config_manager.get_bool("CELERY_RESULT_PERSISTENT", True),
            "task_default_retry_delay": self.config_manager.get_int("CELERY_TASK_DEFAULT_RETRY_DELAY", 60),
            "task_max_retries": self.config_manager.get_int("CELERY_TASK_MAX_RETRIES", 3)
        }
    
    def get_redis_graph_config(self) -> Dict[str, Any]:
        """Get Redis Graph configuration."""
        return {
            "enabled": self.config_manager.get_bool("REDIS_GRAPH_ENABLED", True),
            "host": self.config_manager.get("REDIS_GRAPH_HOST", "localhost"),
            "port": self.config_manager.get_int("REDIS_GRAPH_PORT", 6379),
            "db": self.config_manager.get_int("REDIS_GRAPH_DB", 3),
            "password": self.config_manager.get("REDIS_GRAPH_PASSWORD", ""),
            "timeout": self.config_manager.get_int("REDIS_GRAPH_TIMEOUT", 30),
            "max_connections": self.config_manager.get_int("REDIS_GRAPH_MAX_CONNECTIONS", 10),
            "index_prefix": self.config_manager.get("REDIS_GRAPH_INDEX_PREFIX", "conductor_"),
            "default_graph": self.config_manager.get("REDIS_GRAPH_DEFAULT_GRAPH", "workflow_orchestration"),
            "query_timeout": self.config_manager.get_int("REDIS_GRAPH_QUERY_TIMEOUT", 60),
            "batch_size": self.config_manager.get_int("REDIS_GRAPH_BATCH_SIZE", 100)
        }
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get file storage configuration."""
        return {
            "type": self.config_manager.get("STORAGE_TYPE", "local"),
            "path": self.config_manager.get("STORAGE_PATH", "./storage"),
            "bucket": self.config_manager.get("STORAGE_BUCKET"),
            "region": self.config_manager.get("STORAGE_REGION"),
            "aws_access_key_id": self.config_manager.get("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": self.config_manager.get("AWS_SECRET_ACCESS_KEY"),
            "max_file_size": self.config_manager.get_int("MAX_FILE_SIZE", 10485760)
        }
    
    def get_search_config(self) -> Dict[str, Any]:
        """Get search services configuration."""
        return {
            "meilisearch": {
                "enabled": self.config_manager.get_bool("MEILISEARCH_ENABLED", True),
                "url": self.config_manager.get("MEILISEARCH_URL", "http://localhost:7700"),
                "key": self.config_manager.get("MEILISEARCH_KEY", ""),
                "timeout": self.config_manager.get_int("MEILISEARCH_TIMEOUT", 30),
                "max_connections": self.config_manager.get_int("MEILISEARCH_MAX_CONNECTIONS", 10),
                "index_prefix": self.config_manager.get("MEILISEARCH_INDEX_PREFIX", "symphainy_"),
                "default_index": self.config_manager.get("MEILISEARCH_DEFAULT_INDEX", "knowledge_assets"),
                "search_limit": self.config_manager.get_int("MEILISEARCH_SEARCH_LIMIT", 20),
                "max_search_limit": self.config_manager.get_int("MEILISEARCH_MAX_SEARCH_LIMIT", 100)
            },
            "elasticsearch": {
                "enabled": self.config_manager.get_bool("ELASTICSEARCH_ENABLED", False),
                "url": self.config_manager.get("ELASTICSEARCH_URL", "http://localhost:9200")
            }
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            "level": self.config_manager.get("LOG_LEVEL", "INFO"),
            "format": self.config_manager.get("LOG_FORMAT", "json"),
            "file": self.config_manager.get("LOG_FILE")
        }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags configuration."""
        return {
            "experimental_features": self.config_manager.get_bool("ENABLE_EXPERIMENTAL_FEATURES", False),
            "debug_endpoints": self.config_manager.get_bool("ENABLE_DEBUG_ENDPOINTS", False),
            "swagger_ui": self.config_manager.get_bool("ENABLE_SWAGGER_UI", True)
        }
    
    def get_environment(self) -> Environment:
        """Get current environment."""
        return self.environment
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information."""
        return {
            "environment": self.environment.value,
            "is_development": self.config_manager.is_development(),
            "is_testing": self.config_manager.is_testing(),
            "is_production": self.config_manager.is_production(),
            "is_staging": self.config_manager.is_staging()
        }
    
    def get_city_manager_config(self) -> Dict[str, Any]:
        """Get City Manager configuration."""
        return {
            "policy_management_enabled": self.config_manager.get_bool("POLICY_MANAGEMENT_ENABLED", True),
            "policy_storage_type": self.config_manager.get("POLICY_STORAGE_TYPE", "arangodb"),
            "policy_storage_collection": self.config_manager.get("POLICY_STORAGE_COLLECTION", "city_policies"),
            "policy_validation_enabled": self.config_manager.get_bool("POLICY_VALIDATION_ENABLED", True),
            "policy_enforcement_enabled": self.config_manager.get_bool("POLICY_ENFORCEMENT_ENABLED", True),
            "policy_cache_ttl_seconds": self.config_manager.get_int("POLICY_CACHE_TTL_SECONDS", 3600),
            
            # ArangoDB configuration for policy storage
            "arango": self.get_arango_config(),
            
            "resource_allocation_enabled": self.config_manager.get_bool("RESOURCE_ALLOCATION_ENABLED", True),
            "resource_budget_total": self.config_manager.get_int("RESOURCE_BUDGET_TOTAL", 1000000),
            "resource_allocation_timeout_seconds": self.config_manager.get_int("RESOURCE_ALLOCATION_TIMEOUT_SECONDS", 300),
            "resource_constraint_validation": self.config_manager.get_bool("RESOURCE_CONSTRAINT_VALIDATION", True),
            "resource_optimization_enabled": self.config_manager.get_bool("RESOURCE_OPTIMIZATION_ENABLED", True),
            
            "governance_enforcement_enabled": self.config_manager.get_bool("GOVERNANCE_ENFORCEMENT_ENABLED", True),
            "governance_layers": self.config_manager.get("GOVERNANCE_LAYERS", "authorization,infrastructure,data,patterns,knowledge,events,session,orchestration,telemetry,communication").split(","),
            "governance_compliance_threshold": self.config_manager.get_float("GOVERNANCE_COMPLIANCE_THRESHOLD", 0.8),
            "governance_audit_interval_minutes": self.config_manager.get_int("GOVERNANCE_AUDIT_INTERVAL_MINUTES", 60),
            "governance_violation_alert_enabled": self.config_manager.get_bool("GOVERNANCE_VIOLATION_ALERT_ENABLED", True),
            
            "strategic_coordination_enabled": self.config_manager.get_bool("STRATEGIC_COORDINATION_ENABLED", True),
            "coordination_timeout_seconds": self.config_manager.get_int("COORDINATION_TIMEOUT_SECONDS", 1800),
            "max_concurrent_coordinations": self.config_manager.get_int("MAX_CONCURRENT_COORDINATIONS", 50),
            "coordination_plan_retention_days": self.config_manager.get_int("COORDINATION_PLAN_RETENTION_DAYS", 30),
            "cross_role_communication_enabled": self.config_manager.get_bool("CROSS_ROLE_COMMUNICATION_ENABLED", True),
            
            "city_health_monitoring_enabled": self.config_manager.get_bool("CITY_HEALTH_MONITORING_ENABLED", True),
            "city_health_check_interval_seconds": self.config_manager.get_int("CITY_HEALTH_CHECK_INTERVAL_SECONDS", 60),
            "city_health_threshold_overall": self.config_manager.get_float("CITY_HEALTH_THRESHOLD_OVERALL", 0.8),
            "city_health_threshold_services": self.config_manager.get_float("CITY_HEALTH_THRESHOLD_SERVICES", 0.9),
            "city_health_threshold_compliance": self.config_manager.get_float("CITY_HEALTH_THRESHOLD_COMPLIANCE", 0.8),
            
            "emergency_coordination_enabled": self.config_manager.get_bool("EMERGENCY_COORDINATION_ENABLED", True),
            "emergency_escalation_timeout_seconds": self.config_manager.get_int("EMERGENCY_ESCALATION_TIMEOUT_SECONDS", 300),
            "emergency_notification_channels": self.config_manager.get("EMERGENCY_NOTIFICATION_CHANNELS", "email,slack,webhook").split(","),
            "emergency_auto_response_enabled": self.config_manager.get_bool("EMERGENCY_AUTO_RESPONSE_ENABLED", True),
            
            "inter_dimensional_communication_enabled": self.config_manager.get_bool("INTER_DIMENSIONAL_COMMUNICATION_ENABLED", True),
            "dimension_sync_interval_seconds": self.config_manager.get_int("DIMENSION_SYNC_INTERVAL_SECONDS", 300),
            "dimension_conflict_resolution": self.config_manager.get("DIMENSION_CONFLICT_RESOLUTION", "city_manager"),
            "dimension_protocol_version": self.config_manager.get("DIMENSION_PROTOCOL_VERSION", "1.0"),
            
            "city_manager_service_url": self.config_manager.get("CITY_MANAGER_SERVICE_URL", "http://localhost:8020"),
            "city_manager_mcp_url": self.config_manager.get("CITY_MANAGER_MCP_URL", "http://localhost:8021"),
            "city_manager_max_workflows": self.config_manager.get_int("CITY_MANAGER_MAX_WORKFLOWS", 100),
            "city_manager_workflow_timeout_minutes": self.config_manager.get_int("CITY_MANAGER_WORKFLOW_TIMEOUT_MINUTES", 60),
            "city_manager_enable_monitoring": self.config_manager.get_bool("CITY_MANAGER_ENABLE_MONITORING", True)
        }
    
    def get_llm_abstraction_config(self) -> Dict[str, Any]:
        """Get LLM Abstraction configuration."""
        return {
            # Provider Settings
            "provider_default": self.config_manager.get("LLM_PROVIDER_DEFAULT", "openai"),
            "provider_fallback": self.config_manager.get("LLM_PROVIDER_FALLBACK", "openai"),
            "provider_timeout_seconds": self.config_manager.get_int("LLM_PROVIDER_TIMEOUT_SECONDS", 30),
            "provider_retry_attempts": self.config_manager.get_int("LLM_PROVIDER_RETRY_ATTEMPTS", 3),
            "provider_retry_delay_seconds": self.config_manager.get_int("LLM_PROVIDER_RETRY_DELAY_SECONDS", 1),
            
            # Model Configuration
            "model_default": self.config_manager.get("LLM_MODEL_DEFAULT", "gpt-4o-mini"),
            "model_temperature": self.config_manager.get_float("LLM_MODEL_TEMPERATURE", 0.7),
            "model_max_tokens": self.config_manager.get_int("LLM_MODEL_MAX_TOKENS", 4000),
            "model_top_p": self.config_manager.get_float("LLM_MODEL_TOP_P", 1.0),
            "model_frequency_penalty": self.config_manager.get_float("LLM_MODEL_FREQUENCY_PENALTY", 0.0),
            "model_presence_penalty": self.config_manager.get_float("LLM_MODEL_PRESENCE_PENALTY", 0.0),
            
            # Caching Configuration
            "cache_enabled": self.config_manager.get_bool("LLM_CACHE_ENABLED", True),
            "cache_ttl_seconds": self.config_manager.get_int("LLM_CACHE_TTL_SECONDS", 3600),
            "cache_max_size": self.config_manager.get_int("LLM_CACHE_MAX_SIZE", 1000),
            "cache_storage_type": self.config_manager.get("LLM_CACHE_STORAGE_TYPE", "redis"),
            "cache_redis_url": self.config_manager.get("LLM_CACHE_REDIS_URL", "redis://localhost:6379/1"),
            
            # Rate Limiting
            "rate_limit_enabled": self.config_manager.get_bool("LLM_RATE_LIMIT_ENABLED", True),
            "rate_limit_requests_per_minute": self.config_manager.get_int("LLM_RATE_LIMIT_REQUESTS_PER_MINUTE", 60),
            "rate_limit_requests_per_hour": self.config_manager.get_int("LLM_RATE_LIMIT_REQUESTS_PER_HOUR", 1000),
            "rate_limit_tokens_per_minute": self.config_manager.get_int("LLM_RATE_LIMIT_TOKENS_PER_MINUTE", 100000),
            "rate_limit_tokens_per_hour": self.config_manager.get_int("LLM_RATE_LIMIT_TOKENS_PER_HOUR", 1000000),
            
            # Security Configuration
            "security_enabled": self.config_manager.get_bool("LLM_SECURITY_ENABLED", True),
            "content_filtering_enabled": self.config_manager.get_bool("LLM_CONTENT_FILTERING_ENABLED", True),
            "pii_detection_enabled": self.config_manager.get_bool("LLM_PII_DETECTION_ENABLED", True),
            "audit_logging_enabled": self.config_manager.get_bool("LLM_AUDIT_LOGGING_ENABLED", True),
            "response_validation_enabled": self.config_manager.get_bool("LLM_RESPONSE_VALIDATION_ENABLED", True),
            
            # Cost Management
            "cost_tracking_enabled": self.config_manager.get_bool("LLM_COST_TRACKING_ENABLED", True),
            "cost_alert_threshold_usd": self.config_manager.get_float("LLM_COST_ALERT_THRESHOLD_USD", 100.0),
            "cost_alert_email": self.config_manager.get("LLM_COST_ALERT_EMAIL", "admin@symphainy.com"),
            "budget_monthly_usd": self.config_manager.get_float("LLM_BUDGET_MONTHLY_USD", 1000.0),
            "budget_alert_percentage": self.config_manager.get_int("LLM_BUDGET_ALERT_PERCENTAGE", 80),
            
            # Performance Monitoring
            "monitoring_enabled": self.config_manager.get_bool("LLM_MONITORING_ENABLED", True),
            "metrics_collection_enabled": self.config_manager.get_bool("LLM_METRICS_COLLECTION_ENABLED", True),
            "response_time_threshold_ms": self.config_manager.get_int("LLM_RESPONSE_TIME_THRESHOLD_MS", 2000),
            "error_rate_threshold_percent": self.config_manager.get_float("LLM_ERROR_RATE_THRESHOLD_PERCENT", 5.0),
            "availability_threshold_percent": self.config_manager.get_float("LLM_AVAILABILITY_THRESHOLD_PERCENT", 99.0),
            
            # Agent Integration
            "agent_integration_enabled": self.config_manager.get_bool("LLM_AGENT_INTEGRATION_ENABLED", True),
            "agent_expertise_enabled": self.config_manager.get_bool("LLM_AGENT_EXPERTISE_ENABLED", True),
            "agent_context_management_enabled": self.config_manager.get_bool("LLM_AGENT_CONTEXT_MANAGEMENT_ENABLED", True),
            "agent_conversation_memory_enabled": self.config_manager.get_bool("LLM_AGENT_CONVERSATION_MEMORY_ENABLED", True),
            "agent_session_timeout_minutes": self.config_manager.get_int("LLM_AGENT_SESSION_TIMEOUT_MINUTES", 30),
            
            # Output Formatting
            "output_format_default": self.config_manager.get("LLM_OUTPUT_FORMAT_DEFAULT", "agui"),
            "output_format_supported": self.config_manager.get("LLM_OUTPUT_FORMAT_SUPPORTED", "agui,json,text,markdown").split(","),
            "output_validation_enabled": self.config_manager.get_bool("LLM_OUTPUT_VALIDATION_ENABLED", True),
            "output_schema_validation_enabled": self.config_manager.get_bool("LLM_OUTPUT_SCHEMA_VALIDATION_ENABLED", True),
            
            # Prompt Engineering
            "prompt_templates_enabled": self.config_manager.get_bool("LLM_PROMPT_TEMPLATES_ENABLED", True),
            "prompt_templates_path": self.config_manager.get("LLM_PROMPT_TEMPLATES_PATH", "prompts/templates"),
            "prompt_optimization_enabled": self.config_manager.get_bool("LLM_PROMPT_OPTIMIZATION_ENABLED", True),
            "prompt_analytics_enabled": self.config_manager.get_bool("LLM_PROMPT_ANALYTICS_ENABLED", True),
            
            # Multi-Provider Support
            "multi_provider_enabled": self.config_manager.get_bool("LLM_MULTI_PROVIDER_ENABLED", True),
            "provider_load_balancing_enabled": self.config_manager.get_bool("LLM_PROVIDER_LOAD_BALANCING_ENABLED", True),
            "provider_failover_enabled": self.config_manager.get_bool("LLM_PROVIDER_FAILOVER_ENABLED", True),
            "provider_health_check_interval_seconds": self.config_manager.get_int("LLM_PROVIDER_HEALTH_CHECK_INTERVAL_SECONDS", 60),
            
            # Development & Testing
            "dev_mode_enabled": self.config_manager.get_bool("LLM_DEV_MODE_ENABLED", False),
            "mock_responses_enabled": self.config_manager.get_bool("LLM_MOCK_RESPONSES_ENABLED", False),
            "debug_logging_enabled": self.config_manager.get_bool("LLM_DEBUG_LOGGING_ENABLED", False),
            "test_mode_enabled": self.config_manager.get_bool("LLM_TEST_MODE_ENABLED", False)
        }
    
    def get_content_pillar_config(self) -> Dict[str, Any]:
        """Get Content Pillar configuration."""
        return {
            # File Upload Settings
            "file_upload_enabled": self.config_manager.get_bool("FILE_UPLOAD_ENABLED", True),
            "file_upload_max_size_mb": self.config_manager.get_int("FILE_UPLOAD_MAX_SIZE_MB", 100),
            "file_upload_allowed_extensions": self.config_manager.get("FILE_UPLOAD_ALLOWED_EXTENSIONS", ".pdf,.docx,.xlsx,.csv,.txt,.cobol,.copybook").split(","),
            "file_upload_storage_type": self.config_manager.get("FILE_UPLOAD_STORAGE_TYPE", "local"),
            "file_upload_storage_path": self.config_manager.get("FILE_UPLOAD_STORAGE_PATH", "/tmp/uploads"),
            "file_upload_cleanup_interval_hours": self.config_manager.get_int("FILE_UPLOAD_CLEANUP_INTERVAL_HOURS", 24),
            
            # Document Parsing Settings
            "document_parsing_enabled": self.config_manager.get_bool("DOCUMENT_PARSING_ENABLED", True),
            "pdf_parsing_engine": self.config_manager.get("PDF_PARSING_ENGINE", "pdfplumber"),
            "word_parsing_enabled": self.config_manager.get_bool("WORD_PARSING_ENABLED", True),
            "excel_parsing_enabled": self.config_manager.get_bool("EXCEL_PARSING_ENABLED", True),
            "html_parsing_enabled": self.config_manager.get_bool("HTML_PARSING_ENABLED", True),
            "text_extraction_enabled": self.config_manager.get_bool("TEXT_EXTRACTION_ENABLED", True),
            
            # COBOL Processing Settings
            "cobol_processing_enabled": self.config_manager.get_bool("COBOL_PROCESSING_ENABLED", True),
            "cobol_copybook_parsing_enabled": self.config_manager.get_bool("COBOL_COPYBOOK_PARSING_ENABLED", True),
            "cobol_binary_conversion_enabled": self.config_manager.get_bool("COBOL_BINARY_CONVERSION_ENABLED", True),
            "cobol_output_format": self.config_manager.get("COBOL_OUTPUT_FORMAT", "parquet"),
            "cobol_charset_detection": self.config_manager.get_bool("COBOL_CHARSET_DETECTION", True),
            "cobol_debug_mode": self.config_manager.get_bool("COBOL_DEBUG_MODE", False),
            
            # Format Conversion Settings
            "format_conversion_enabled": self.config_manager.get_bool("FORMAT_CONVERSION_ENABLED", True),
            "conversion_output_formats": self.config_manager.get("CONVERSION_OUTPUT_FORMATS", "parquet,json,csv").split(","),
            "conversion_compression_enabled": self.config_manager.get_bool("CONVERSION_COMPRESSION_ENABLED", True),
            "conversion_batch_size": self.config_manager.get_int("CONVERSION_BATCH_SIZE", 1000),
            "conversion_timeout_seconds": self.config_manager.get_int("CONVERSION_TIMEOUT_SECONDS", 300),
            
            # Image Processing Settings
            "image_processing_enabled": self.config_manager.get_bool("IMAGE_PROCESSING_ENABLED", True),
            "ocr_enabled": self.config_manager.get_bool("OCR_ENABLED", True),
            "ocr_engine": self.config_manager.get("OCR_ENGINE", "tesseract"),
            "image_preprocessing_enabled": self.config_manager.get_bool("IMAGE_PREPROCESSING_ENABLED", True),
            "image_quality_threshold": self.config_manager.get_float("IMAGE_QUALITY_THRESHOLD", 0.8),
            
            # Content Analytics Settings
            "content_analytics_enabled": self.config_manager.get_bool("CONTENT_ANALYTICS_ENABLED", True),
            "metadata_extraction_enabled": self.config_manager.get_bool("METADATA_EXTRACTION_ENABLED", True),
            "content_validation_enabled": self.config_manager.get_bool("CONTENT_VALIDATION_ENABLED", True),
            "quality_scoring_enabled": self.config_manager.get_bool("QUALITY_SCORING_ENABLED", True),
            "analytics_cache_ttl_seconds": self.config_manager.get_int("ANALYTICS_CACHE_TTL_SECONDS", 3600),
            
            # Content Pillar Service Configuration
            "content_pillar_service_url": self.config_manager.get("CONTENT_PILLAR_SERVICE_URL", "http://localhost:8030"),
            "content_pillar_mcp_url": self.config_manager.get("CONTENT_PILLAR_MCP_URL", "http://localhost:8031"),
            "content_pillar_max_concurrent_uploads": self.config_manager.get_int("CONTENT_PILLAR_MAX_CONCURRENT_UPLOADS", 10),
            "content_pillar_upload_timeout_minutes": self.config_manager.get_int("CONTENT_PILLAR_UPLOAD_TIMEOUT_MINUTES", 30),
            "content_pillar_enable_monitoring": self.config_manager.get_bool("CONTENT_PILLAR_ENABLE_MONITORING", True)
        }
    
    def get_insights_pillar_config(self) -> Dict[str, Any]:
        """Get Insights Pillar configuration."""
        return {
            # Data Analysis Settings
            "data_analysis_enabled": self.config_manager.get_bool("DATA_ANALYSIS_ENABLED", True),
            "statistical_analysis_enabled": self.config_manager.get_bool("STATISTICAL_ANALYSIS_ENABLED", True),
            "correlation_analysis_enabled": self.config_manager.get_bool("CORRELATION_ANALYSIS_ENABLED", True),
            "clustering_analysis_enabled": self.config_manager.get_bool("CLUSTERING_ANALYSIS_ENABLED", True),
            "anomaly_detection_enabled": self.config_manager.get_bool("ANOMALY_DETECTION_ENABLED", True),
            "trend_analysis_enabled": self.config_manager.get_bool("TREND_ANALYSIS_ENABLED", True),
            
            # Visualization Settings
            "visualization_enabled": self.config_manager.get_bool("VISUALIZATION_ENABLED", True),
            "chart_generation_enabled": self.config_manager.get_bool("CHART_GENERATION_ENABLED", True),
            "dashboard_creation_enabled": self.config_manager.get_bool("DASHBOARD_CREATION_ENABLED", True),
            "interactive_plots_enabled": self.config_manager.get_bool("INTERACTIVE_PLOTS_ENABLED", True),
            "export_formats": self.config_manager.get("VISUALIZATION_EXPORT_FORMATS", "png,jpg,svg,pdf").split(","),
            
            # Machine Learning Settings
            "ml_analysis_enabled": self.config_manager.get_bool("ML_ANALYSIS_ENABLED", True),
            "model_training_enabled": self.config_manager.get_bool("MODEL_TRAINING_ENABLED", True),
            "prediction_enabled": self.config_manager.get_bool("PREDICTION_ENABLED", True),
            "classification_enabled": self.config_manager.get_bool("CLASSIFICATION_ENABLED", True),
            "regression_enabled": self.config_manager.get_bool("REGRESSION_ENABLED", True),
            
            # Performance Settings
            "max_data_size_mb": self.config_manager.get_int("INSIGHTS_MAX_DATA_SIZE_MB", 100),
            "analysis_timeout_seconds": self.config_manager.get_int("INSIGHTS_ANALYSIS_TIMEOUT_SECONDS", 300),
            "cache_results": self.config_manager.get_bool("INSIGHTS_CACHE_RESULTS", True),
            "cache_ttl_hours": self.config_manager.get_int("INSIGHTS_CACHE_TTL_HOURS", 24),
            "parallel_processing": self.config_manager.get_bool("INSIGHTS_PARALLEL_PROCESSING", True),
            "max_workers": self.config_manager.get_int("INSIGHTS_MAX_WORKERS", 4),
            
            # Service Configuration
            "insights_pillar_service_url": self.config_manager.get("INSIGHTS_PILLAR_SERVICE_URL", "http://localhost:8040"),
            "insights_pillar_mcp_url": self.config_manager.get("INSIGHTS_PILLAR_MCP_URL", "http://localhost:8041"),
            "enable_monitoring": self.config_manager.get_bool("INSIGHTS_ENABLE_MONITORING", True),
            "log_level": self.config_manager.get("INSIGHTS_LOG_LEVEL", "INFO"),
            
            # Data Quality Settings
            "data_quality_checks": self.config_manager.get_bool("INSIGHTS_DATA_QUALITY_CHECKS", True),
            "missing_data_threshold": self.config_manager.get_float("INSIGHTS_MISSING_DATA_THRESHOLD", 0.1),
            "outlier_detection_method": self.config_manager.get("INSIGHTS_OUTLIER_DETECTION_METHOD", "iqr"),
            "correlation_threshold": self.config_manager.get_float("INSIGHTS_CORRELATION_THRESHOLD", 0.7),
            
            # Advanced Analytics
            "time_series_analysis": self.config_manager.get_bool("INSIGHTS_TIME_SERIES_ANALYSIS", True),
            "seasonality_detection": self.config_manager.get_bool("INSIGHTS_SEASONALITY_DETECTION", True),
            "forecasting_enabled": self.config_manager.get_bool("INSIGHTS_FORECASTING_ENABLED", True),
            "forecast_horizon_days": self.config_manager.get_int("INSIGHTS_FORECAST_HORIZON_DAYS", 30),
            
            # Export & Reporting
            "export_enabled": self.config_manager.get_bool("INSIGHTS_EXPORT_ENABLED", True),
            "report_generation": self.config_manager.get_bool("INSIGHTS_REPORT_GENERATION", True),
            "automated_insights": self.config_manager.get_bool("INSIGHTS_AUTOMATED_INSIGHTS", True),
            "insight_summarization": self.config_manager.get_bool("INSIGHTS_INSIGHT_SUMMARIZATION", True)
        }
    
    def get_enhanced_file_management_config(self) -> Dict[str, Any]:
        """Get Enhanced File Management configuration."""
        return {
            # Supabase Configuration
            "supabase_enabled": self.config_manager.get_bool("SUPABASE_ENABLED", True),
            "supabase_url": self.config_manager.get("SUPABASE_URL", ""),
            "supabase_key": self.config_manager.get("SUPABASE_KEY", ""),
            "supabase_service_role_key": self.config_manager.get("SUPABASE_SERVICE_ROLE_KEY", ""),
            "supabase_bucket": self.config_manager.get("SUPABASE_BUCKET", "symphainy-files"),
            
            # Google Cloud Storage Configuration
            "gcs_enabled": self.config_manager.get_bool("GCS_ENABLED", True),
            "gcs_project_id": self.config_manager.get("GCS_PROJECT_ID", ""),
            "gcs_bucket_name": self.config_manager.get("GCS_BUCKET_NAME", "symphainy-platform-files"),
            "gcs_credentials_path": self.config_manager.get("GCS_CREDENTIALS_PATH", ""),
            "gcs_public_url_base": self.config_manager.get("GCS_PUBLIC_URL_BASE", ""),
            
            # ArangoDB Configuration (for metadata insights)
            "arangodb_enabled": self.config_manager.get_bool("ARANGODB_ENABLED", True),
            "arangodb_url": self.config_manager.get("ARANGODB_URL", "http://localhost:8529"),
            "arangodb_username": self.config_manager.get("ARANGODB_USERNAME", "root"),
            "arangodb_password": self.config_manager.get("ARANGODB_PASSWORD", ""),
            "arangodb_database": self.config_manager.get("ARANGODB_DATABASE", "symphainy_metadata"),
            
            # File Processing Configuration
            "max_file_size_mb": self.config_manager.get_int("MAX_FILE_SIZE_MB", 100),
            "allowed_file_types": self.config_manager.get("ALLOWED_FILE_TYPES", "csv,json,xlsx,pdf,docx,txt").split(","),
            "file_processing_timeout": self.config_manager.get_int("FILE_PROCESSING_TIMEOUT", 300),
            "concurrent_uploads": self.config_manager.get_int("CONCURRENT_UPLOADS", 5),
            
            # Metadata Extraction Configuration
            "metadata_extraction_enabled": self.config_manager.get_bool("METADATA_EXTRACTION_ENABLED", True),
            "google_ai_api_key": self.config_manager.get("GOOGLE_AI_API_KEY", ""),
            "metadata_extraction_timeout": self.config_manager.get_int("METADATA_EXTRACTION_TIMEOUT", 60),
            "metadata_quality_threshold": self.config_manager.get_float("METADATA_QUALITY_THRESHOLD", 0.7),
            "auto_extract_metadata": self.config_manager.get_bool("AUTO_EXTRACT_METADATA", True),
            
            # File Lineage Configuration
            "file_lineage_enabled": self.config_manager.get_bool("FILE_LINEAGE_ENABLED", True),
            "lineage_retention_days": self.config_manager.get_int("LINEAGE_RETENTION_DAYS", 365),
            "auto_track_lineage": self.config_manager.get_bool("AUTO_TRACK_LINEAGE", True),
            "lineage_chain_depth": self.config_manager.get_int("LINEAGE_CHAIN_DEPTH", 10),
            
            # File Linking Configuration
            "file_linking_enabled": self.config_manager.get_bool("FILE_LINKING_ENABLED", True),
            "max_linked_files": self.config_manager.get_int("MAX_LINKED_FILES", 50),
            "link_validation_enabled": self.config_manager.get_bool("LINK_VALIDATION_ENABLED", True),
            
            # Data Quality Configuration
            "data_quality_checks": self.config_manager.get_bool("DATA_QUALITY_CHECKS", True),
            "missing_data_threshold": self.config_manager.get_float("MISSING_DATA_THRESHOLD", 0.1),
            "outlier_detection_enabled": self.config_manager.get_bool("OUTLIER_DETECTION_ENABLED", True),
            "data_validation_rules": self.config_manager.get_bool("DATA_VALIDATION_RULES", True),
            
            # Security Configuration
            "file_encryption_enabled": self.config_manager.get_bool("FILE_ENCRYPTION_ENABLED", True),
            "virus_scanning_enabled": self.config_manager.get_bool("VIRUS_SCANNING_ENABLED", False),
            "access_control_enabled": self.config_manager.get_bool("ACCESS_CONTROL_ENABLED", True),
            "audit_logging_enabled": self.config_manager.get_bool("AUDIT_LOGGING_ENABLED", True),
            
            # Performance Configuration
            "file_cache_enabled": self.config_manager.get_bool("FILE_CACHE_ENABLED", True),
            "cache_ttl_hours": self.config_manager.get_int("FILE_CACHE_TTL_HOURS", 24),
            "compression_enabled": self.config_manager.get_bool("FILE_COMPRESSION_ENABLED", True),
            "thumbnail_generation": self.config_manager.get_bool("THUMBNAIL_GENERATION", True),
            
            # CEO Demo Configuration
            "ceo_demo_enabled": self.config_manager.get_bool("CEO_DEMO_ENABLED", True),
            "demo_metadata_extraction": self.config_manager.get_bool("DEMO_METADATA_EXTRACTION", True),
            "demo_file_lineage": self.config_manager.get_bool("DEMO_FILE_LINEAGE", True),
            "demo_data_quality": self.config_manager.get_bool("DEMO_DATA_QUALITY", True),
            "demo_insights_generation": self.config_manager.get_bool("DEMO_INSIGHTS_GENERATION", True)
        }
    
    def get_supabase_config(self) -> Dict[str, Any]:
        """Get Supabase-specific configuration."""
        return {
            "enabled": self.config_manager.get_bool("SUPABASE_ENABLED", True),
            "url": self.config_manager.get("SUPABASE_URL", ""),
            "key": self.config_manager.get("SUPABASE_KEY", ""),
            "service_role_key": self.config_manager.get("SUPABASE_SERVICE_ROLE_KEY", ""),
            "bucket": self.config_manager.get("SUPABASE_BUCKET", "symphainy-files"),
            "project_id": self.config_manager.get("SUPABASE_PROJECT_ID", ""),
            "region": self.config_manager.get("SUPABASE_REGION", "us-east-1"),
            "timeout": self.config_manager.get_int("SUPABASE_TIMEOUT", 30),
            "retry_attempts": self.config_manager.get_int("SUPABASE_RETRY_ATTEMPTS", 3)
        }
    
    def get_gcs_config(self) -> Dict[str, Any]:
        """Get Google Cloud Storage configuration."""
        return {
            "enabled": self.config_manager.get_bool("GCS_ENABLED", True),
            "project_id": self.config_manager.get("GCS_PROJECT_ID", ""),
            "bucket_name": self.config_manager.get("GCS_BUCKET_NAME", "symphainy-platform-files"),
            "credentials_path": self.config_manager.get("GCS_CREDENTIALS_PATH", ""),
            "public_url_base": self.config_manager.get("GCS_PUBLIC_URL_BASE", ""),
            "region": self.config_manager.get("GCS_REGION", "us-central1"),
            "storage_class": self.config_manager.get("GCS_STORAGE_CLASS", "STANDARD"),
            "timeout": self.config_manager.get_int("GCS_TIMEOUT", 60),
            "retry_attempts": self.config_manager.get_int("GCS_RETRY_ATTEMPTS", 3)
        }
    
    def get_arangodb_config(self) -> Dict[str, Any]:
        """Get ArangoDB configuration for metadata storage."""
        return {
            "enabled": self.config_manager.get_bool("ARANGODB_ENABLED", True),
            "url": self.config_manager.get("ARANGODB_URL", "http://localhost:8529"),
            "username": self.config_manager.get("ARANGODB_USERNAME", "root"),
            "password": self.config_manager.get("ARANGODB_PASSWORD", ""),
            "database": self.config_manager.get("ARANGODB_DATABASE", "symphainy_metadata"),
            "timeout": self.config_manager.get_int("ARANGODB_TIMEOUT", 30),
            "retry_attempts": self.config_manager.get_int("ARANGODB_RETRY_ATTEMPTS", 3),
            "max_connections": self.config_manager.get_int("ARANGODB_MAX_CONNECTIONS", 10)
        }
    
    def get_arango_config(self) -> Dict[str, Any]:
        """Get ArangoDB configuration (generic)."""
        return {
            "enabled": self.config_manager.get_bool("ARANGO_ENABLED", True),
            "host": self.config_manager.get("ARANGO_HOST", "localhost"),
            "port": self.config_manager.get_int("ARANGO_PORT", 8529),
            "database": self.config_manager.get("ARANGO_DATABASE", "symphainy"),
            "username": self.config_manager.get("ARANGO_USERNAME", "root"),
            "password": self.config_manager.get("ARANGO_PASSWORD", "admin"),
            "timeout": self.config_manager.get_int("ARANGO_TIMEOUT", 30),
            "max_connections": self.config_manager.get_int("ARANGO_MAX_CONNECTIONS", 10),
            "retry_attempts": self.config_manager.get_int("ARANGO_RETRY_ATTEMPTS", 3),
            "retry_delay": self.config_manager.get_int("ARANGO_RETRY_DELAY", 1)
        }
    
    def get_metadata_extraction_config(self) -> Dict[str, Any]:
        """Get metadata extraction configuration."""
        return {
            "enabled": self.config_manager.get_bool("METADATA_EXTRACTION_ENABLED", True),
            "google_ai_api_key": self.config_manager.get("GOOGLE_AI_API_KEY", ""),
            "timeout": self.config_manager.get_int("METADATA_EXTRACTION_TIMEOUT", 60),
            "quality_threshold": self.config_manager.get_float("METADATA_QUALITY_THRESHOLD", 0.7),
            "auto_extract": self.config_manager.get_bool("AUTO_EXTRACT_METADATA", True),
            "max_file_size_mb": self.config_manager.get_int("METADATA_MAX_FILE_SIZE_MB", 50),
            "supported_formats": self.config_manager.get("METADATA_SUPPORTED_FORMATS", "csv,json,xlsx,pdf,docx").split(","),
            "extraction_models": {
                "content_analysis": self.config_manager.get_bool("METADATA_CONTENT_ANALYSIS", True),
                "data_quality": self.config_manager.get_bool("METADATA_DATA_QUALITY", True),
                "business_insights": self.config_manager.get_bool("METADATA_BUSINESS_INSIGHTS", True),
                "statistical_summary": self.config_manager.get_bool("METADATA_STATISTICAL_SUMMARY", True),
                "topic_extraction": self.config_manager.get_bool("METADATA_TOPIC_EXTRACTION", True)
            }
        }
    
    def get_multi_tenant_config(self) -> Dict[str, Any]:
        """Get multi-tenant configuration."""
        return {
            "enabled": self.config_manager.get_bool("MULTI_TENANT_ENABLED", False),
            "default_tenant_type": self.config_manager.get("DEFAULT_TENANT_TYPE", "individual"),
            "max_tenants_per_user": self.config_manager.get_int("MAX_TENANTS_PER_USER", 1),
            "tenant_limits": {
                "individual": self.config_manager.get_int("INDIVIDUAL_MAX_USERS", 1),
                "organization": self.config_manager.get_int("ORGANIZATION_MAX_USERS", 50),
                "enterprise": self.config_manager.get_int("ENTERPRISE_MAX_USERS", 1000)
            },
            "tenant_features": {
                "individual": self.config_manager.get("INDIVIDUAL_FEATURES", "basic_analytics,file_upload").split(","),
                "organization": self.config_manager.get("ORGANIZATION_FEATURES", "basic_analytics,file_upload,team_collaboration,advanced_insights").split(","),
                "enterprise": self.config_manager.get("ENTERPRISE_FEATURES", "basic_analytics,file_upload,team_collaboration,advanced_insights,custom_integrations,audit_logs").split(",")
            },
            "security_guard": {
                "mcp_server_url": self.config_manager.get("SECURITY_GUARD_MCP_SERVER_URL", "http://localhost:8001"),
                "timeout": self.config_manager.get_int("SECURITY_GUARD_TIMEOUT", 30),
                "retry_attempts": self.config_manager.get_int("SECURITY_GUARD_RETRY_ATTEMPTS", 3)
            },
            "caching": {
                "tenant_cache_ttl": self.config_manager.get_int("TENANT_CACHE_TTL", 3600),
                "user_context_cache_ttl": self.config_manager.get_int("USER_CONTEXT_CACHE_TTL", 1800),
                "audit_log_retention_days": self.config_manager.get_int("AUDIT_LOG_RETENTION_DAYS", 90)
            },
            "rls": {
                "enabled": self.config_manager.get_bool("ENABLE_RLS_POLICIES", True),
                "strict_isolation": self.config_manager.get_bool("TENANT_ISOLATION_STRICT", True)
            }
        }
    
    def get_tenant_config(self, tenant_type: str) -> Dict[str, Any]:
        """Get configuration for specific tenant type."""
        multi_tenant_config = self.get_multi_tenant_config()
        return {
            "max_users": multi_tenant_config["tenant_limits"].get(tenant_type, 1),
            "features": multi_tenant_config["tenant_features"].get(tenant_type, []),
            "type": tenant_type
        }
    
    def is_multi_tenant_enabled(self) -> bool:
        """Check if multi-tenancy is enabled."""
        return self.config_manager.get_bool("MULTI_TENANT_ENABLED", False)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration as a dictionary."""
        return {
            "environment": self.get_environment_info(),
            "database": self.get_database_config(),
            "redis": self.get_redis_config(),
            "api": self.get_api_config(),
            "security": self.get_security_config(),
            "external_services": self.get_external_services_config(),
            "monitoring": self.get_monitoring_config(),
            "celery": self.get_celery_config(),
            "storage": self.get_storage_config(),
            "search": self.get_search_config(),
            "logging": self.get_logging_config(),
            "feature_flags": self.get_feature_flags(),
            "city_manager": self.get_city_manager_config(),
            "llm_abstraction": self.get_llm_abstraction_config(),
            "content_pillar": self.get_content_pillar_config(),
            "insights_pillar": self.get_insights_pillar_config(),
            "enhanced_file_management": self.get_enhanced_file_management_config(),
            "supabase": self.get_supabase_config(),
            "gcs": self.get_gcs_config(),
            "arangodb": self.get_arangodb_config(),
            "metadata_extraction": self.get_metadata_extraction_config(),
            "multi_tenant": self.get_multi_tenant_config()
        }
    
    def print_config_summary(self):
        """Print a summary of current configuration."""
        env_info = self.get_environment_info()
        print(f"\n🔧 Environment Configuration Summary")
        print(f"Environment: {env_info['environment']}")
        print(f"Database: {self.get_database_config()['url']}")
        print(f"Redis: {self.get_redis_config()['url']}")
        print(f"API: {self.get_api_config()['host']}:{self.get_api_config()['port']}")
        print(f"Debug Mode: {self.get_api_config()['debug']}")
        print(f"Logging Level: {self.get_logging_config()['level']}")
        
        feature_flags = self.get_feature_flags()
        print(f"Feature Flags:")
        for flag, enabled in feature_flags.items():
            print(f"  - {flag}: {enabled}")


# Global environment loader instance
env_loader = EnvironmentLoader()
