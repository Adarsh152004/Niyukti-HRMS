"""Tests — Agent Performance Metrics."""

from datetime import UTC, datetime

from backend.agents.performance import AgentPerformanceMetrics, PerformanceThreshold


def _make_metrics(**kwargs) -> AgentPerformanceMetrics:
    base = {
        "agent_id": "agent-001",
        "agent_role": "RESUME_SCREENING_AGENT",
        "measurement_period_start": datetime(2024, 1, 1, tzinfo=UTC),
        "measurement_period_end": datetime(2024, 1, 31, tzinfo=UTC),
    }
    base.update(kwargs)
    return AgentPerformanceMetrics(**base)


def test_metrics_creation():
    m = _make_metrics()
    assert m.agent_id == "agent-001"
    assert m.task_success_rate == 0.0
    assert m.human_override_rate == 0.0


def test_metrics_all_fields_present():
    m = _make_metrics(
        total_tasks=100,
        successful_tasks=92,
        failed_tasks=8,
        task_success_rate=0.92,
        accuracy=0.89,
        precision=0.91,
        recall=0.87,
        f1_score=0.89,
        mean_confidence=0.85,
        avg_latency_seconds=2.3,
        total_cost=15.50,
        human_override_rate=0.05,
        escalation_rate=0.08,
        recommendation_acceptance_rate=0.88,
        error_rate=0.02,
        policy_violation_rate=0.0,
        false_positive_rate=0.04,
        false_negative_rate=0.06,
    )
    assert m.task_success_rate == 0.92
    assert m.accuracy == 0.89
    assert m.human_override_rate == 0.05
    assert m.policy_violation_rate == 0.0


def test_reliability_score():
    """Reliability score should be lower when error_rate and violation_rate are high."""
    good = _make_metrics(task_success_rate=0.95, error_rate=0.01, policy_violation_rate=0.0)
    bad = _make_metrics(task_success_rate=0.70, error_rate=0.15, policy_violation_rate=0.05)
    assert good.reliability_score > bad.reliability_score


def test_custom_metrics():
    """Agent-specific metrics must be supported."""
    m = _make_metrics(
        custom_metrics={
            "screening_accuracy": 0.91,
            "candidate_recall": 0.88,
            "false_rejection_rate": 0.04,
        }
    )
    assert m.custom_metrics["screening_accuracy"] == 0.91


def test_performance_threshold_creation():
    threshold = PerformanceThreshold(
        agent_role="RESUME_SCREENING_AGENT",
        metric_name="human_override_rate",
        max_value=0.2,
        alert_on_breach=True,
        reduce_autonomy_on_breach=True,
    )
    assert threshold.metric_name == "human_override_rate"
    assert threshold.max_value == 0.2
    assert threshold.reduce_autonomy_on_breach is True


def test_thresholds_are_configurable():
    """Performance thresholds must be configurable — not hardcoded."""
    t1 = PerformanceThreshold(agent_role="PAYROLL_AGENT", metric_name="accuracy", min_value=0.99)
    t2 = PerformanceThreshold(agent_role="SENTIMENT_ANALYSIS_AGENT", metric_name="accuracy", min_value=0.80)
    assert t1.min_value != t2.min_value
