# Remaining Agents - Quick Migration Template

**Status:** Creating remaining 6 agents using established patterns

## Pattern Assignment

- **Iterative Specialist** (complex generation): SOPGenerationSpecialist, WorkflowGenerationSpecialist, CoexistenceBlueprintSpecialist, RoadmapProposalSpecialist
- **Stateless Specialist** (simple analysis): CoexistenceStrategySpecialist, SagaWALManagementSpecialist

## Quick Template

For **Iterative Specialist**:
- `stateful: false`
- `iterative_execution: true`
- `max_iterations: 5`

For **Stateless Specialist**:
- `stateful: false`
- `iterative_execution: false`

All agents:
- Use absolute imports
- Inherit from DeclarativeAgentBase
- Preserve Priority 2 metadata
- Config path: `Path(__file__).parent / "configs" / "{agent_name}.yaml"`







