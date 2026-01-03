================================================================================
ERROR HANDLING VERIFICATION REPORT
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Services Checked: 231
Services Compliant: 208
Services Non-Compliant: 20

PATTERN USAGE
--------------------------------------------------------------------------------
  handle_error_with_audit: 89 files
  log_operation_with_telemetry: 91 files
  record_health_metric: 79 files
  error_type: 14 files
  error_code: 5 files

NON-COMPLIANT SERVICES
--------------------------------------------------------------------------------
  - symphainy-platform/backend/solution/services/operational_intelligence_dashboard_service/operational_intelligence_dashboard_service.py
  - symphainy-platform/backend/solution/services/solution_manager/mcp_server/solution_manager_mcp_server.py
  - symphainy-platform/backend/solution/services/solution_analytics_service/solution_analytics_service.py
  - symphainy-platform/backend/solution/services/saga_execution_dashboard_service/saga_execution_dashboard_service.py
  - symphainy-platform/backend/solution/services/solution_composer_service/solution_composer_service.py
  - symphainy-platform/backend/solution/services/wal_operations_dashboard_service/wal_operations_dashboard_service.py
  - symphainy-platform/backend/journey/orchestrators/business_outcomes_journey_orchestrator/agents/business_outcomes_specialist_agent.py
  - symphainy-platform/backend/journey/orchestrators/content_journey_orchestrator/content_analysis_orchestrator.py
  - symphainy-platform/backend/journey/orchestrators/content_journey_orchestrator/mcp_server/content_analysis_mcp_server.py
  - symphainy-platform/backend/journey/orchestrators/insights_journey_orchestrator/workflows/unstructured_analysis_workflow.py
  - symphainy-platform/backend/smart_city/services/content_steward/modules/content_validation.py
  - symphainy-platform/backend/smart_city/services/content_steward/modules/content_processing.py
  - symphainy-platform/backend/smart_city/services/content_steward/modules/file_processing.py
  - symphainy-platform/backend/smart_city/services/traffic_cop/modules/initialization.py
  - symphainy-platform/backend/smart_city/services/nurse/modules/telemetry_health.py
  - symphainy-platform/backend/content/services/semantic_enrichment_gateway/modules/enrichment.py
  - symphainy-platform/backend/content/services/embedding_service/modules/embedding_creation.py
  - symphainy-platform/backend/insights/services/field_extraction_service/field_extraction_service.py
  - symphainy-platform/backend/insights/services/data_transformation_service/data_transformation_service.py
  - symphainy-platform/backend/insights/services/data_analyzer_service/modules/eda_analysis.py

ISSUES FOUND
--------------------------------------------------------------------------------
  symphainy-platform/backend/solution/services/operational_intelligence_dashboard_service/operational_intelligence_dashboard_service.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
  symphainy-platform/backend/solution/services/solution_manager/mcp_server/solution_manager_mcp_server.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()
  symphainy-platform/backend/solution/services/solution_analytics_service/solution_analytics_service.py:
    - Exception handler missing handle_error_with_audit()
  symphainy-platform/backend/solution/services/saga_execution_dashboard_service/saga_execution_dashboard_service.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()
  symphainy-platform/backend/solution/services/solution_composer_service/solution_composer_service.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
  symphainy-platform/backend/solution/services/wal_operations_dashboard_service/wal_operations_dashboard_service.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()
  symphainy-platform/backend/journey/orchestrators/business_outcomes_journey_orchestrator/agents/business_outcomes_specialist_agent.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()
  symphainy-platform/backend/journey/orchestrators/content_journey_orchestrator/content_analysis_orchestrator.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()
  symphainy-platform/backend/journey/orchestrators/content_journey_orchestrator/mcp_server/content_analysis_mcp_server.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
  symphainy-platform/backend/journey/orchestrators/insights_journey_orchestrator/workflows/unstructured_analysis_workflow.py:
    - Exception handler missing handle_error_with_audit()
    - Exception handler missing log_operation_with_telemetry()
    - Exception handler missing record_health_metric()

SAMPLE DETAILED RESULTS
--------------------------------------------------------------------------------
File: symphainy-platform/backend/solution/services/operational_intelligence_dashboard_service/operational_intelligence_dashboard_service.py
  Compliant: False
  Exception Handlers: 3
  Compliant Handlers: 0
  Issues: 7

File: symphainy-platform/backend/solution/services/solution_manager/mcp_server/solution_manager_mcp_server.py
  Compliant: False
  Exception Handlers: 1
  Compliant Handlers: 0
  Issues: 3

File: symphainy-platform/backend/solution/services/solution_analytics_service/solution_analytics_service.py
  Compliant: False
  Exception Handlers: 1
  Compliant Handlers: 0
  Issues: 1

File: symphainy-platform/backend/solution/services/saga_execution_dashboard_service/saga_execution_dashboard_service.py
  Compliant: False
  Exception Handlers: 1
  Compliant Handlers: 0
  Issues: 3

File: symphainy-platform/backend/solution/services/solution_composer_service/solution_composer_service.py
  Compliant: False
  Exception Handlers: 4
  Compliant Handlers: 0
  Issues: 12

================================================================================