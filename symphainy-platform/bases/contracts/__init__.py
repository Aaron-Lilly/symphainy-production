"""
Abstraction Contract Data Structures

Shared data structures (dataclasses, enums) used across the platform for abstraction contracts.
These are data structures, not implementations - they define the shape of data passed to/from abstractions.

Moved from foundations/public_works_foundation/abstraction_contracts/ to make them accessible
to all realms without architectural violations.
"""

from .document_intelligence import (
    DocumentProcessingRequest,
    DocumentProcessingResult,
    DocumentChunk,
    DocumentEntity,
    DocumentSimilarity
)

from .workflow_orchestration import (
    WorkflowStatus,
    NodeType,
    GatewayType,
    WorkflowNode,
    WorkflowEdge,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionRequest
)

__all__ = [
    # Document Intelligence
    "DocumentProcessingRequest",
    "DocumentProcessingResult",
    "DocumentChunk",
    "DocumentEntity",
    "DocumentSimilarity",
    # Workflow Orchestration
    "WorkflowStatus",
    "NodeType",
    "GatewayType",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowDefinition",
    "WorkflowExecution",
    "WorkflowExecutionRequest",
]

