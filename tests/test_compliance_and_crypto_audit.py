"""
AI-Powered Intelligent HRMS — Security, Compliance & Cryptographic Audit Test Suite.

Verifies:
1. Cryptographic SHA-256 hash-chain integrity & tamper detection
2. GDPR Article 15 DSAR JSON export completeness
3. GDPR Article 17 Right to Erasure / Pseudonymization
4. SOC 2 Type II and ISO 27001 automated compliance rules
5. AI Decision Lineage provenance DAG resolution
"""

import pytest
from backend.governance.compliance.evaluator import ComplianceEvaluator
from backend.governance.lineage.tracker import DecisionLineageTracker
from backend.privacy.gdpr.pipeline import GDPRPrivacyEngine
from backend.security.audit.crypto_chain import CryptographicAuditLedger


def test_crypto_audit_chain_validity():
    """Verify hash chain integrity across sequentially appended audit blocks."""
    ledger = CryptographicAuditLedger()

    # Append sequential events
    evt1 = ledger.append_event("evt-01", "actor-user", "LOGIN", "SYSTEM")
    evt2 = ledger.append_event("evt-02", "actor-agent", "EXECUTE_TOOL", "tool-calc")
    evt3 = ledger.append_event("evt-03", "actor-admin", "APPROVE_PAYROLL", "run-2026-08")

    assert len(ledger.chain) == 3
    assert evt1.prev_hash == ledger.GENESIS_HASH
    assert evt2.prev_hash == evt1.current_hash
    assert evt3.prev_hash == evt2.current_hash

    is_valid, msg = ledger.verify_integrity()
    assert is_valid is True
    assert "3 blocks intact" in msg


def test_crypto_audit_chain_tamper_detection():
    """Verify tamper detection triggers if an audit event block is illegally altered."""
    ledger = CryptographicAuditLedger()

    ledger.append_event("evt-01", "actor-user", "LOGIN", "SYSTEM")
    ledger.append_event("evt-02", "actor-agent", "EXECUTE_TOOL", "tool-calc")
    ledger.append_event("evt-03", "actor-admin", "APPROVE_PAYROLL", "run-2026-08")

    # Manually mutate block 1 payload without re-signing subsequent chain
    ledger._chain[1].payload = {"tampered": True}

    is_valid, msg = ledger.verify_integrity()
    assert is_valid is False
    assert "Tamper detected at block 1" in msg


def test_gdpr_dsar_export():
    """Verify GDPR Article 15 DSAR export aggregates all required categories."""
    privacy = GDPRPrivacyEngine()
    result = privacy.export_dsar("emp-01", tenant_id="tenant-apex")

    assert result.employee_id == "emp-01"
    assert result.tenant_id == "tenant-apex"
    assert "personal_profile" in result.data_payload
    assert "compensation_history" in result.data_payload
    assert "performance_reviews" in result.data_payload
    assert len(result.archive_hash) == 64  # SHA-256


def test_gdpr_right_to_erasure():
    """Verify GDPR Article 17 erasure pseudonymizes identity and purges memory."""
    privacy = GDPRPrivacyEngine()
    result = privacy.execute_erasure("emp-01", tenant_id="tenant-apex")

    assert result.status == "COMPLETED"
    assert result.pseudonym_id.startswith("tok_")
    assert result.records_pseudonymized > 0
    assert result.vector_embeddings_purged > 0
    assert result.agent_memories_cleared > 0


def test_soc2_and_iso27001_compliance_evaluator():
    """Verify compliance evaluator certifies controls."""
    evaluator = ComplianceEvaluator()
    report = evaluator.evaluate_controls()

    assert report.overall_status == "CERTIFIED_COMPLIANT"
    assert report.soc2_compliance_rate == 1.0
    assert report.iso27001_compliance_rate == 1.0
    assert len(report.controls) >= 6


def test_decision_lineage_tracker():
    """Verify AI decision lineage records end-to-end provenance DAG."""
    tracker = DecisionLineageTracker()
    correlation_id = "corr-req-8891"

    # 1. User query
    tracker.start_trace(correlation_id, "Approve salary increase for emp-01", "usr-manager")

    # 2. Agent reasoning
    step1 = tracker.record_step(
        correlation_id=correlation_id,
        node_type="AGENT_PLAN",
        label="Evaluate salary band compliance",
        actor="ag-compensation",
    )

    # 3. Tool call
    step2 = tracker.record_step(
        correlation_id=correlation_id,
        node_type="TOOL_CALL",
        label="get_salary_band(emp-01)",
        actor="ag-compensation",
        parent_id=step1.node_id,
    )

    # 4. Human Approval
    step3 = tracker.record_step(
        correlation_id=correlation_id,
        node_type="HITL_APPROVAL",
        label="Approve by VP HR",
        actor="usr-vp-hr",
        parent_id=step2.node_id,
    )

    lineage = tracker.get_lineage(correlation_id)
    assert lineage is not None
    assert len(lineage.nodes) == 4
    assert lineage.nodes[0].node_type == "PROMPT"
    assert lineage.nodes[3].node_type == "HITL_APPROVAL"
    assert lineage.nodes[3].parent_node_ids == [step2.node_id]
