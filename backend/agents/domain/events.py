"""
Agent Domain Events — Lifecycle and Task Events.
"""

from __future__ import annotations

from backend.hrms.domain.events import DomainEvent


class AgentRegistered(DomainEvent):
    event_type: str = "AgentRegistered"


class AgentActivated(DomainEvent):
    event_type: str = "AgentActivated"


class AgentPaused(DomainEvent):
    event_type: str = "AgentPaused"


class AgentSuspended(DomainEvent):
    event_type: str = "AgentSuspended"


class AgentDisabled(DomainEvent):
    event_type: str = "AgentDisabled"


class AgentTerminated(DomainEvent):
    event_type: str = "AgentTerminated"


class AgentTaskCreated(DomainEvent):
    event_type: str = "AgentTaskCreated"


class AgentTaskStarted(DomainEvent):
    event_type: str = "AgentTaskStarted"


class AgentTaskCompleted(DomainEvent):
    event_type: str = "AgentTaskCompleted"


class AgentTaskFailed(DomainEvent):
    event_type: str = "AgentTaskFailed"


class AgentTaskDelegated(DomainEvent):
    event_type: str = "AgentTaskDelegated"


# Planning & Orchestration Events
class AgentPlanCreated(DomainEvent):
    event_type: str = "AgentPlanCreated"


class AgentPlanValidated(DomainEvent):
    event_type: str = "AgentPlanValidated"


class AgentPlanStarted(DomainEvent):
    event_type: str = "AgentPlanStarted"


class AgentPlanStepStarted(DomainEvent):
    event_type: str = "AgentPlanStepStarted"


class AgentPlanStepCompleted(DomainEvent):
    event_type: str = "AgentPlanStepCompleted"


class AgentPlanStepFailed(DomainEvent):
    event_type: str = "AgentPlanStepFailed"


class AgentPlanWaitingApproval(DomainEvent):
    event_type: str = "AgentPlanWaitingApproval"


class AgentPlanReplanned(DomainEvent):
    event_type: str = "AgentPlanReplanned"


class AgentReasoningIterationStarted(DomainEvent):
    event_type: str = "AgentReasoningIterationStarted"


class AgentReasoningIterationCompleted(DomainEvent):
    event_type: str = "AgentReasoningIterationCompleted"


class AgentExecutionPaused(DomainEvent):
    event_type: str = "AgentExecutionPaused"


class AgentExecutionResumed(DomainEvent):
    event_type: str = "AgentExecutionResumed"


class AgentExecutionCompleted(DomainEvent):
    event_type: str = "AgentExecutionCompleted"


class AgentExecutionFailed(DomainEvent):
    event_type: str = "AgentExecutionFailed"


class AgentExecutionLimitReached(DomainEvent):
    event_type: str = "AgentExecutionLimitReached"


# Multi-Agent Delegation Events
class AgentDelegationRequested(DomainEvent):
    event_type: str = "AgentDelegationRequested"


class AgentDelegationApproved(DomainEvent):
    event_type: str = "AgentDelegationApproved"


class AgentDelegationActivated(DomainEvent):
    event_type: str = "AgentDelegationActivated"


class AgentDelegationRejected(DomainEvent):
    event_type: str = "AgentDelegationRejected"


class AgentDelegationRevoked(DomainEvent):
    event_type: str = "AgentDelegationRevoked"


class AgentDelegationExpired(DomainEvent):
    event_type: str = "AgentDelegationExpired"


class AgentDelegatedTaskCreated(DomainEvent):
    event_type: str = "AgentDelegatedTaskCreated"


class AgentDelegatedTaskStarted(DomainEvent):
    event_type: str = "AgentDelegatedTaskStarted"


class AgentDelegatedTaskCompleted(DomainEvent):
    event_type: str = "AgentDelegatedTaskCompleted"


class AgentDelegatedTaskFailed(DomainEvent):
    event_type: str = "AgentDelegatedTaskFailed"


class AgentDelegatedTaskCancelled(DomainEvent):
    event_type: str = "AgentDelegatedTaskCancelled"


class AgentDelegationCompleted(DomainEvent):
    event_type: str = "AgentDelegationCompleted"


# ==========================================
# AGENT GOVERNANCE & OBSERVABILITY EVENTS
# ==========================================


class AgentGovernanceViolation(DomainEvent):
    event_type: str = "AgentGovernanceViolation"


class AgentBudgetExceeded(DomainEvent):
    event_type: str = "AgentBudgetExceeded"


class AgentExecutionRecorded(DomainEvent):
    event_type: str = "AgentExecutionRecorded"


class AgentEvaluationCompleted(DomainEvent):
    event_type: str = "AgentEvaluationCompleted"


class AgentQuarantined(DomainEvent):
    event_type: str = "AgentQuarantined"


class AgentRestricted(DomainEvent):
    event_type: str = "AgentRestricted"


class AgentGovernancePolicyChanged(DomainEvent):
    event_type: str = "AgentGovernancePolicyChanged"


class AgentGovernancePolicyCreated(DomainEvent):
    event_type: str = "AgentGovernancePolicyCreated"


class AgentPolicyViolationDetected(DomainEvent):
    event_type: str = "AgentPolicyViolationDetected"


class AgentEvaluationStarted(DomainEvent):
    event_type: str = "AgentEvaluationStarted"


class AgentAnomalyDetected(DomainEvent):
    event_type: str = "AgentAnomalyDetected"


class AgentContainmentTriggered(DomainEvent):
    event_type: str = "AgentContainmentTriggered"


class AgentAuditRecorded(DomainEvent):
    event_type: str = "AgentAuditRecorded"


class AgentMetricRecorded(DomainEvent):
    event_type: str = "AgentMetricRecorded"
