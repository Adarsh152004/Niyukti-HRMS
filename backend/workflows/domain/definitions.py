"""
Workflow Definitions & DAG Validation Engine.

Provides topological sorting, dependency resolution, and validation
for Workflow DAGs (detecting circular dependencies, missing dependencies, duplicate steps).
"""

from __future__ import annotations

from collections import defaultdict, deque

from backend.workflows.domain.exceptions import WorkflowValidationError
from backend.workflows.domain.models import WorkflowDefinition, WorkflowStepDefinition


def validate_workflow_definition(workflow_def: WorkflowDefinition) -> None:
    """
    Validate a WorkflowDefinition DAG for structural correctness.
    Checks:
    - Step list not empty
    - Unique step IDs
    - All dependencies reference existing step IDs
    - No circular dependencies
    """
    if not workflow_def.steps:
        raise WorkflowValidationError(f"Workflow '{workflow_def.name}' must contain at least one step.")

    step_ids = set()
    for step in workflow_def.steps:
        if step.step_id in step_ids:
            raise WorkflowValidationError(f"Duplicate step ID '{step.step_id}' found in workflow '{workflow_def.name}'.")
        step_ids.add(step.step_id)

    # Verify dependencies exist
    for step in workflow_def.steps:
        for dep in step.dependencies:
            if dep not in step_ids:
                raise WorkflowValidationError(f"Step '{step.step_id}' references unknown dependency '{dep}'.")

    # Cycle Detection using Kahn's Algorithm
    in_degree: dict[str, int] = {s.step_id: 0 for s in workflow_def.steps}
    graph: dict[str, list[str]] = defaultdict(list)

    for step in workflow_def.steps:
        for dep in step.dependencies:
            graph[dep].append(step.step_id)
            in_degree[step.step_id] += 1

    queue = deque([sid for sid, deg in in_degree.items() if deg == 0])
    visited_count = 0

    while queue:
        node = queue.popleft()
        visited_count += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited_count != len(step_ids):
        raise WorkflowValidationError(f"Circular dependency cycle detected in workflow '{workflow_def.name}'.")


def get_execution_order(workflow_def: WorkflowDefinition) -> list[list[WorkflowStepDefinition]]:
    """
    Compute topological execution order levels for ready steps.
    Steps in the same level can execute concurrently.
    """
    validate_workflow_definition(workflow_def)

    step_map = {s.step_id: s for s in workflow_def.steps}
    in_degree: dict[str, int] = {s.step_id: len(s.dependencies) for s in workflow_def.steps}
    graph: dict[str, list[str]] = defaultdict(list)

    for step in workflow_def.steps:
        for dep in step.dependencies:
            graph[dep].append(step.step_id)

    levels: list[list[WorkflowStepDefinition]] = []
    current_level = [sid for sid, deg in in_degree.items() if deg == 0]

    while current_level:
        levels.append([step_map[sid] for sid in current_level])
        next_level = []
        for sid in current_level:
            for neighbor in graph[sid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_level.append(neighbor)
        current_level = next_level

    return levels
