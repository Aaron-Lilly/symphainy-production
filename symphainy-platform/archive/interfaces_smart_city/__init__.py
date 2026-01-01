#!/usr/bin/env python3
"""
Smart City Interfaces Package

Contains all the interface definitions for Smart City roles.
These interfaces define the contracts that Smart City roles must implement.

WHAT (Smart City Role): I need to define clear contracts for platform capabilities
HOW (Interface Package): I provide abstract base classes and data structures

Role-Based Interface Structure:
- Each interface matches a specific Smart City service
- All interfaces follow consistent patterns and naming conventions
- Clear separation of concerns with no duplicates
"""

# Security Guard Interface
from .security_guard_interface import (
    ISecurityGuard,
    AuthStatus,
    AuthLevel,
    SessionStatus,
    AuthenticateUserRequest,
    AuthenticateUserResponse,
    AuthorizeActionRequest,
    AuthorizeActionResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    ValidateSessionRequest,
    ValidateSessionResponse,
    RevokeSessionRequest,
    RevokeSessionResponse
)

# Traffic Cop Interface
from .traffic_cop_interface import (
    ITrafficCop,
    SessionPriority,
    StatePriority,
    SessionStatus as TrafficSessionStatus,
    StateStatus,
    SessionRequest,
    SessionResponse,
    RoutingRequest,
    RoutingResponse,
    StateRequest,
    StateResponse,
    SyncRequest,
    SyncResponse,
    AnalyticsRequest,
    AnalyticsResponse,
    HealthCheckRequest,
    HealthCheckResponse
)

# Conductor Interface
from .conductor_interface import (
    IConductor,
    WorkflowStatus,
    WorkflowPriority,
    TaskStatus,
    CreateWorkflowRequest,
    CreateWorkflowResponse,
    ExecuteWorkflowRequest,
    ExecuteWorkflowResponse,
    GetWorkflowStatusRequest,
    GetWorkflowStatusResponse,
    PauseWorkflowRequest,
    PauseWorkflowResponse,
    ResumeWorkflowRequest,
    ResumeWorkflowResponse
)

# Nurse Interface
from .nurse_interface import (
    INurse,
    HealthStatus,
    AlertSeverity,
    MetricType,
    CollectTelemetryRequest,
    CollectTelemetryResponse,
    GetHealthMetricsRequest,
    GetHealthMetricsResponse,
    SetAlertThresholdRequest,
    SetAlertThresholdResponse,
    RunDiagnosticsRequest,
    RunDiagnosticsResponse,
    GetSystemStatusRequest,
    GetSystemStatusResponse
)

# Librarian Interface
from .librarian_interface import (
    ILibrarian,
    KnowledgeType,
    SearchMode,
    MetadataStatus,
    StoreKnowledgeRequest,
    StoreKnowledgeResponse,
    SearchKnowledgeRequest,
    SearchKnowledgeResponse,
    GetMetadataRequest,
    GetMetadataResponse,
    UpdateMetadataRequest,
    UpdateMetadataResponse,
    GetSemanticRelationshipsRequest,
    GetSemanticRelationshipsResponse
)

# Data Steward Interface
from .data_steward_interface import (
    IDataSteward,
    DataStatus,
    DataPolicyType,
    DataLineageType,
    RegisterDatasetRequest,
    RegisterDatasetResponse,
    GetDataLineageRequest,
    GetDataLineageResponse,
    ApplyDataPolicyRequest,
    ApplyDataPolicyResponse,
    GetStorageMetricsRequest,
    GetStorageMetricsResponse,
    ArchiveDatasetRequest,
    ArchiveDatasetResponse
)

# Post Office Interface
from .post_office_interface import (
    IPostOffice,
    MessageStatus,
    EventType,
    MessagePriority,
    AgentStatus,
    SendMessageRequest,
    SendMessageResponse,
    RouteEventRequest,
    RouteEventResponse,
    RegisterAgentRequest,
    RegisterAgentResponse,
    GetMessagesRequest,
    GetMessagesResponse,
    GetMessageStatusRequest,
    GetMessageStatusResponse
)

# City Manager Interface
from .city_manager_interface import (
    ICityManager,
    PlatformStatus,
    GovernanceAction,
    OrchestrationScope,
    ServiceType,
    GetCityStatusRequest,
    GetCityStatusResponse,
    CoordinateServicesRequest,
    CoordinateServicesResponse,
    PlanDevelopmentRequest,
    PlanDevelopmentResponse,
    MonitorCityRequest,
    MonitorCityResponse,
    EnforceGovernanceRequest,
    EnforceGovernanceResponse
)

__all__ = [
    # Security Guard Interface
    "ISecurityGuard",
    "AuthStatus",
    "AuthLevel",
    "SessionStatus",
    "AuthenticateUserRequest",
    "AuthenticateUserResponse",
    "AuthorizeActionRequest",
    "AuthorizeActionResponse",
    "CreateSessionRequest",
    "CreateSessionResponse",
    "ValidateSessionRequest",
    "ValidateSessionResponse",
    "RevokeSessionRequest",
    "RevokeSessionResponse",
    
    # Traffic Cop Interface
    "ITrafficCop",
    "SessionPriority",
    "StatePriority",
    "TrafficSessionStatus",
    "StateStatus",
    "SessionRequest",
    "SessionResponse",
    "RoutingRequest",
    "RoutingResponse",
    "StateRequest",
    "StateResponse",
    "SyncRequest",
    "SyncResponse",
    "AnalyticsRequest",
    "AnalyticsResponse",
    "HealthCheckRequest",
    "HealthCheckResponse",
    
    # Conductor Interface
    "IConductor",
    "WorkflowStatus",
    "WorkflowPriority",
    "TaskStatus",
    "CreateWorkflowRequest",
    "CreateWorkflowResponse",
    "ExecuteWorkflowRequest",
    "ExecuteWorkflowResponse",
    "GetWorkflowStatusRequest",
    "GetWorkflowStatusResponse",
    "PauseWorkflowRequest",
    "PauseWorkflowResponse",
    "ResumeWorkflowRequest",
    "ResumeWorkflowResponse",
    
    # Nurse Interface
    "INurse",
    "HealthStatus",
    "AlertSeverity",
    "MetricType",
    "CollectTelemetryRequest",
    "CollectTelemetryResponse",
    "GetHealthMetricsRequest",
    "GetHealthMetricsResponse",
    "SetAlertThresholdRequest",
    "SetAlertThresholdResponse",
    "RunDiagnosticsRequest",
    "RunDiagnosticsResponse",
    "GetSystemStatusRequest",
    "GetSystemStatusResponse",
    
    # Librarian Interface
    "ILibrarian",
    "KnowledgeType",
    "SearchMode",
    "MetadataStatus",
    "StoreKnowledgeRequest",
    "StoreKnowledgeResponse",
    "SearchKnowledgeRequest",
    "SearchKnowledgeResponse",
    "GetMetadataRequest",
    "GetMetadataResponse",
    "UpdateMetadataRequest",
    "UpdateMetadataResponse",
    "GetSemanticRelationshipsRequest",
    "GetSemanticRelationshipsResponse",
    
    # Data Steward Interface
    "IDataSteward",
    "DataStatus",
    "DataPolicyType",
    "DataLineageType",
    "RegisterDatasetRequest",
    "RegisterDatasetResponse",
    "GetDataLineageRequest",
    "GetDataLineageResponse",
    "ApplyDataPolicyRequest",
    "ApplyDataPolicyResponse",
    "GetStorageMetricsRequest",
    "GetStorageMetricsResponse",
    "ArchiveDatasetRequest",
    "ArchiveDatasetResponse",
    
    # Post Office Interface
    "IPostOffice",
    "MessageStatus",
    "EventType",
    "MessagePriority",
    "AgentStatus",
    "SendMessageRequest",
    "SendMessageResponse",
    "RouteEventRequest",
    "RouteEventResponse",
    "RegisterAgentRequest",
    "RegisterAgentResponse",
    "GetMessagesRequest",
    "GetMessagesResponse",
    "GetMessageStatusRequest",
    "GetMessageStatusResponse",
    
    # City Manager Interface
    "ICityManager",
    "PlatformStatus",
    "GovernanceAction",
    "OrchestrationScope",
    "ServiceType",
    "GetCityStatusRequest",
    "GetCityStatusResponse",
    "CoordinateServicesRequest",
    "CoordinateServicesResponse",
    "PlanDevelopmentRequest",
    "PlanDevelopmentResponse",
    "MonitorCityRequest",
    "MonitorCityResponse",
    "EnforceGovernanceRequest",
    "EnforceGovernanceResponse"
]