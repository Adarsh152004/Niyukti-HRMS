"""
AI-Powered Intelligent HRMS — Decision Provenance & Lineage Graph Tracker.

Tracks complete operational lineage:
User Prompt -> Agent Execution -> Tool Invocations -> ML Predictions -> HITL Gates -> Result Action
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LineageNode:
    node_id: str
    node_type: str  # PROMPT, AGENT_PLAN, TOOL_CALL, ML_INFERENCE, HITL_APPROVAL, ACTION_EXECUTED
    label: str
    actor: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_node_ids: list[str] = field(default_factory=list)


@dataclass
class DecisionLineageGraph:
    correlation_id: str
    root_prompt: str
    nodes: list[LineageNode]
    finished: bool = True


class DecisionLineageTracker:
    """Records and resolves end-to-end lineage graphs for auditing AI decisions."""

    def __init__(self) -> None:
        self._graphs: dict[str, DecisionLineageGraph] = {}

    def start_trace(self, correlation_id: str, prompt: str, user_id: str) -> DecisionLineageGraph:
        """Initializes a new decision lineage graph from an initial user request."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        root_node = LineageNode(
            node_id=f"{correlation_id}-root",
            node_type="PROMPT",
            label="User Operational Query",
            actor=user_id,
            timestamp=timestamp,
            metadata={"raw_prompt": prompt},
        )
        graph = DecisionLineageGraph(
            correlation_id=correlation_id,
            root_prompt=prompt,
            nodes=[root_node],
        )
        self._graphs[correlation_id] = graph
        return graph

    def record_step(
        self,
        correlation_id: str,
        node_type: str,
        label: str,
        actor: str,
        metadata: dict[str, Any] | None = None,
        parent_id: str | None = None,
    ) -> LineageNode:
        """Appends a causal node to the decision lineage graph."""
        graph = self._graphs.get(correlation_id)
        if not graph:
            graph = self.start_trace(correlation_id, label, actor)

        node_id = f"{correlation_id}-step-{len(graph.nodes)+1}"
        parents = [parent_id] if parent_id else [graph.nodes[-1].node_id]

        node = LineageNode(
            node_id=node_id,
            node_type=node_type,
            label=label,
            actor=actor,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            metadata=metadata or {},
            parent_node_ids=parents,
        )
        graph.nodes.append(node)
        return node

    def get_lineage(self, correlation_id: str) -> DecisionLineageGraph | None:
        """Retrieves complete lineage graph by correlation ID."""
        return self._graphs.get(correlation_id)


# Global singleton tracker
lineage_tracker = DecisionLineageTracker()
