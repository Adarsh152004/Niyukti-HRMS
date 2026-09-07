"""
Workflow Template Catalog — Registers and builds all 20 comprehensive enterprise HR workflow DAG templates.
"""

from __future__ import annotations

from collections.abc import Callable

from backend.workflows.domain.definitions import validate_workflow_definition
from backend.workflows.domain.enums import Priority
from backend.workflows.domain.models import WorkflowDefinition, WorkflowStepDefinition


class WorkflowTemplateCatalog:
    """
    Central repository of standard enterprise HR workflow DAG definitions.
    """

    _instance: WorkflowTemplateCatalog | None = None

    def __init__(self) -> None:
        self._templates: dict[str, Callable[[str], WorkflowDefinition]] = {
            "onboarding": self.build_onboarding_workflow,
            "offboarding": self.build_offboarding_workflow,
            "recruitment_to_hire": self.build_recruitment_workflow,
            "payroll_processing": self.build_payroll_workflow,
            "performance_review_cycle": self.build_performance_review_workflow,
            "leave_approval": self.build_leave_approval_workflow,
            "promotion": self.build_promotion_workflow,
            "disciplinary": self.build_disciplinary_workflow,
            "probation_confirmation": self.build_probation_confirmation_workflow,
            "training_plan": self.build_training_plan_workflow,
            "internal_transfer": self.build_internal_transfer_workflow,
            "salary_revision": self.build_salary_revision_workflow,
            "document_verification": self.build_document_verification_workflow,
            "attendance_regularization": self.build_attendance_regularization_workflow,
            "bonus_distribution": self.build_bonus_distribution_workflow,
            "health_and_safety": self.build_health_and_safety_workflow,
            "contract_renewal": self.build_contract_renewal_workflow,
            "certification_tracking": self.build_certification_tracking_workflow,
            "employee_survey": self.build_employee_survey_workflow,
            "exit_interview": self.build_exit_interview_workflow,
        }

    @classmethod
    def get_instance(cls) -> WorkflowTemplateCatalog:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def list_template_names(self) -> list[str]:
        return list(self._templates.keys())

    def get_workflow(self, template_name: str, organization_id: str = "default-org") -> WorkflowDefinition:
        builder = self._templates.get(template_name)
        if not builder:
            raise ValueError(f"Unknown workflow template: '{template_name}'")
        wf = builder(organization_id)
        validate_workflow_definition(wf)
        return wf

    # 1. Onboarding
    def build_onboarding_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-onboarding"
        steps = [
            WorkflowStepDefinition(
                step_id="step_create_profile", workflow_id=wf_id, name="Create Employee Profile", command_type="employee.create"
            ),
            WorkflowStepDefinition(
                step_id="step_verify_docs",
                workflow_id=wf_id,
                name="Verify Identity Documents",
                command_type="document.verify",
                dependencies=["step_create_profile"],
            ),
            WorkflowStepDefinition(
                step_id="step_provision_it",
                workflow_id=wf_id,
                name="Provision Email & IT Accounts",
                command_type="it.provision_account",
                dependencies=["step_verify_docs"],
            ),
            WorkflowStepDefinition(
                step_id="step_order_hardware",
                workflow_id=wf_id,
                name="Order Laptop & Hardware",
                command_type="asset.assign_laptop",
                dependencies=["step_verify_docs"],
            ),
            WorkflowStepDefinition(
                step_id="step_assign_mentor",
                workflow_id=wf_id,
                name="Assign Onboarding Mentor",
                command_type="employee.assign_mentor",
                dependencies=["step_provision_it"],
            ),
            WorkflowStepDefinition(
                step_id="step_welcome_orientation",
                workflow_id=wf_id,
                name="Schedule Welcome Orientation",
                command_type="calendar.schedule_event",
                dependencies=["step_assign_mentor", "step_order_hardware"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Employee Onboarding",
            description="7-step automated onboarding pipeline",
            steps=steps,
            priority=Priority.HIGH,
        )

    # 2. Offboarding
    def build_offboarding_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-offboarding"
        steps = [
            WorkflowStepDefinition(
                step_id="step_resignation_notice",
                workflow_id=wf_id,
                name="Record Resignation Notice",
                command_type="employee.resign",
            ),
            WorkflowStepDefinition(
                step_id="step_exit_interview",
                workflow_id=wf_id,
                name="Conduct Exit Interview",
                command_type="feedback.exit_interview",
                dependencies=["step_resignation_notice"],
            ),
            WorkflowStepDefinition(
                step_id="step_collect_assets",
                workflow_id=wf_id,
                name="Collect Hardware Assets",
                command_type="asset.unassign_laptop",
                dependencies=["step_resignation_notice"],
            ),
            WorkflowStepDefinition(
                step_id="step_revoke_it_access",
                workflow_id=wf_id,
                name="Revoke IT & SSO Access",
                command_type="it.revoke_account",
                dependencies=["step_collect_assets"],
            ),
            WorkflowStepDefinition(
                step_id="step_settle_payroll",
                workflow_id=wf_id,
                name="Calculate Final Settlement",
                command_type="payroll.final_settlement",
                dependencies=["step_revoke_it_access"],
            ),
            WorkflowStepDefinition(
                step_id="step_clearance_certificate",
                workflow_id=wf_id,
                name="Issue Relieving Certificate",
                command_type="document.issue_certificate",
                dependencies=["step_settle_payroll", "step_exit_interview"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Employee Offboarding",
            description="6-step governed offboarding and asset recovery",
            steps=steps,
            priority=Priority.HIGH,
        )

    # 3. Recruitment To Hire
    def build_recruitment_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-recruitment"
        steps = [
            WorkflowStepDefinition(
                step_id="step_post_job", workflow_id=wf_id, name="Publish Job Posting", command_type="recruitment.post_job"
            ),
            WorkflowStepDefinition(
                step_id="step_screen_resumes",
                workflow_id=wf_id,
                name="Screen Incoming Resumes",
                command_type="recruitment.screen_candidates",
                dependencies=["step_post_job"],
            ),
            WorkflowStepDefinition(
                step_id="step_schedule_interviews",
                workflow_id=wf_id,
                name="Schedule Technical Interviews",
                command_type="recruitment.schedule_interview",
                dependencies=["step_screen_resumes"],
            ),
            WorkflowStepDefinition(
                step_id="step_generate_offer",
                workflow_id=wf_id,
                name="Generate Offer Letter",
                command_type="recruitment.generate_offer",
                dependencies=["step_schedule_interviews"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_offer_accepted",
                workflow_id=wf_id,
                name="Candidate Offer Acceptance",
                command_type="recruitment.accept_offer",
                dependencies=["step_generate_offer"],
            ),
            WorkflowStepDefinition(
                step_id="step_trigger_onboarding",
                workflow_id=wf_id,
                name="Trigger Automated Onboarding",
                command_type="workflow.trigger_onboarding",
                dependencies=["step_offer_accepted"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Recruitment to Hire",
            description="End-to-end recruitment lifecycle",
            steps=steps,
        )

    # 4. Payroll Processing
    def build_payroll_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-payroll"
        steps = [
            WorkflowStepDefinition(
                step_id="step_lock_timesheets",
                workflow_id=wf_id,
                name="Lock Monthly Timesheets",
                command_type="attendance.lock_timesheets",
            ),
            WorkflowStepDefinition(
                step_id="step_reconcile_leaves",
                workflow_id=wf_id,
                name="Reconcile Unpaid Leaves",
                command_type="leave.reconcile",
                dependencies=["step_lock_timesheets"],
            ),
            WorkflowStepDefinition(
                step_id="step_compute_gross_to_net",
                workflow_id=wf_id,
                name="Calculate Gross-to-Net Payroll",
                command_type="payroll.calculate_cycle",
                dependencies=["step_reconcile_leaves"],
            ),
            WorkflowStepDefinition(
                step_id="step_finance_quorum_approval",
                workflow_id=wf_id,
                name="Executive Quorum Approval",
                command_type="payroll.approve_run",
                dependencies=["step_compute_gross_to_net"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_execute_disbursement",
                workflow_id=wf_id,
                name="Execute Bank Wire Disbursement",
                command_type="payroll.disburse",
                dependencies=["step_finance_quorum_approval"],
            ),
            WorkflowStepDefinition(
                step_id="step_dispatch_payslips",
                workflow_id=wf_id,
                name="Dispatch Encrypted Payslips",
                command_type="payroll.dispatch_payslips",
                dependencies=["step_execute_disbursement"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Payroll Processing Cycle",
            description="Deterministic monthly payroll run",
            steps=steps,
            priority=Priority.CRITICAL,
        )

    # 5. Performance Review Cycle
    def build_performance_review_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-performance"
        steps = [
            WorkflowStepDefinition(
                step_id="step_launch_cycle",
                workflow_id=wf_id,
                name="Launch Review Cycle",
                command_type="performance.launch_cycle",
            ),
            WorkflowStepDefinition(
                step_id="step_self_evaluation",
                workflow_id=wf_id,
                name="Submit Self Evaluation",
                command_type="performance.submit_self",
                dependencies=["step_launch_cycle"],
            ),
            WorkflowStepDefinition(
                step_id="step_manager_evaluation",
                workflow_id=wf_id,
                name="Submit Manager Review",
                command_type="performance.submit_manager",
                dependencies=["step_self_evaluation"],
            ),
            WorkflowStepDefinition(
                step_id="step_360_peer_feedback",
                workflow_id=wf_id,
                name="Collect 360 Peer Feedback",
                command_type="performance.collect_360",
                dependencies=["step_launch_cycle"],
            ),
            WorkflowStepDefinition(
                step_id="step_score_calibration",
                workflow_id=wf_id,
                name="Calibrate Final Ratings",
                command_type="performance.calibrate",
                dependencies=["step_manager_evaluation", "step_360_peer_feedback"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Performance Appraisal Cycle",
            description="Annual 360 performance evaluation",
            steps=steps,
        )

    # 6. Leave Approval
    def build_leave_approval_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-leave"
        steps = [
            WorkflowStepDefinition(
                step_id="step_validate_balance",
                workflow_id=wf_id,
                name="Validate Leave Balance",
                command_type="leave.validate_balance",
            ),
            WorkflowStepDefinition(
                step_id="step_manager_approval",
                workflow_id=wf_id,
                name="Manager Approval Gate",
                command_type="leave.manager_approval",
                dependencies=["step_validate_balance"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_deduct_balance",
                workflow_id=wf_id,
                name="Deduct Leave Accrual",
                command_type="leave.deduct_balance",
                dependencies=["step_manager_approval"],
            ),
            WorkflowStepDefinition(
                step_id="step_update_calendar",
                workflow_id=wf_id,
                name="Update Department Roster",
                command_type="calendar.update_roster",
                dependencies=["step_deduct_balance"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Leave Request Approval",
            description="Standard leave application and deduction",
            steps=steps,
        )

    # 7. Promotion
    def build_promotion_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-promotion"
        steps = [
            WorkflowStepDefinition(
                step_id="step_manager_nomination",
                workflow_id=wf_id,
                name="Submit Promotion Nomination",
                command_type="promotion.nominate",
            ),
            WorkflowStepDefinition(
                step_id="step_check_eligibility",
                workflow_id=wf_id,
                name="Verify Rating Eligibility",
                command_type="performance.verify_eligibility",
                dependencies=["step_manager_nomination"],
            ),
            WorkflowStepDefinition(
                step_id="step_compensation_revision",
                workflow_id=wf_id,
                name="Draft Revised Compensation",
                command_type="salary.revise",
                dependencies=["step_check_eligibility"],
            ),
            WorkflowStepDefinition(
                step_id="step_executive_signoff",
                workflow_id=wf_id,
                name="Executive Signoff",
                command_type="promotion.signoff",
                dependencies=["step_compensation_revision"],
                requires_approval=True,
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Employee Promotion",
            description="Career advancement and compensation revision",
            steps=steps,
        )

    # 8. Disciplinary
    def build_disciplinary_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-disciplinary"
        steps = [
            WorkflowStepDefinition(
                step_id="step_log_incident",
                workflow_id=wf_id,
                name="Log Policy Incident",
                command_type="disciplinary.log_incident",
            ),
            WorkflowStepDefinition(
                step_id="step_policy_audit",
                workflow_id=wf_id,
                name="Audit Violated Policy Rules",
                command_type="policy.audit",
                dependencies=["step_log_incident"],
            ),
            WorkflowStepDefinition(
                step_id="step_ethics_committee_review",
                workflow_id=wf_id,
                name="Ethics Committee Review",
                command_type="disciplinary.review",
                dependencies=["step_policy_audit"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_issue_action_plan",
                workflow_id=wf_id,
                name="Issue Corrective Action Plan",
                command_type="disciplinary.issue_pip",
                dependencies=["step_ethics_committee_review"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Disciplinary & PIP",
            description="Workplace ethics investigation and action plan",
            steps=steps,
        )

    # 9. Probation Confirmation
    def build_probation_confirmation_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-probation"
        steps = [
            WorkflowStepDefinition(
                step_id="step_probation_alert", workflow_id=wf_id, name="Probation 90-Day Notice", command_type="probation.alert"
            ),
            WorkflowStepDefinition(
                step_id="step_manager_evaluation",
                workflow_id=wf_id,
                name="Manager Assessment",
                command_type="probation.evaluate",
                dependencies=["step_probation_alert"],
            ),
            WorkflowStepDefinition(
                step_id="step_hr_review",
                workflow_id=wf_id,
                name="HR Operations Confirmation",
                command_type="probation.confirm",
                dependencies=["step_manager_evaluation"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_issue_confirmation_letter",
                workflow_id=wf_id,
                name="Issue Official Confirmation",
                command_type="document.issue_confirmation",
                dependencies=["step_hr_review"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Probation Confirmation",
            description="90-day new hire probation review",
            steps=steps,
        )

    # 10. Training Plan
    def build_training_plan_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-training"
        steps = [
            WorkflowStepDefinition(
                step_id="step_identify_skill_gaps",
                workflow_id=wf_id,
                name="Identify Skill Gaps",
                command_type="skills.identify_gaps",
            ),
            WorkflowStepDefinition(
                step_id="step_assign_courses",
                workflow_id=wf_id,
                name="Assign Recommended Courses",
                command_type="course.enroll",
                dependencies=["step_identify_skill_gaps"],
            ),
            WorkflowStepDefinition(
                step_id="step_track_completion",
                workflow_id=wf_id,
                name="Track Course Completion",
                command_type="course.track_progress",
                dependencies=["step_assign_courses"],
            ),
            WorkflowStepDefinition(
                step_id="step_update_skill_matrix",
                workflow_id=wf_id,
                name="Update Org Skill Matrix",
                command_type="skills.update_matrix",
                dependencies=["step_track_completion"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Employee Training Plan",
            description="Targeted learning and capability building",
            steps=steps,
        )

    # 11. Internal Transfer
    def build_internal_transfer_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-transfer"
        steps = [
            WorkflowStepDefinition(
                step_id="step_submit_transfer", workflow_id=wf_id, name="Submit Transfer Request", command_type="transfer.submit"
            ),
            WorkflowStepDefinition(
                step_id="step_origin_dept_release",
                workflow_id=wf_id,
                name="Origin Department Release",
                command_type="transfer.release",
                dependencies=["step_submit_transfer"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_target_dept_accept",
                workflow_id=wf_id,
                name="Target Department Acceptance",
                command_type="transfer.accept",
                dependencies=["step_origin_dept_release"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_update_org_structure",
                workflow_id=wf_id,
                name="Update Department Records",
                command_type="employee.transfer",
                dependencies=["step_target_dept_accept"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Internal Department Transfer",
            description="Inter-departmental mobility workflow",
            steps=steps,
        )

    # 12. Salary Revision
    def build_salary_revision_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-salary-revision"
        steps = [
            WorkflowStepDefinition(
                step_id="step_propose_revision",
                workflow_id=wf_id,
                name="Propose Salary Increment",
                command_type="salary.propose_revision",
            ),
            WorkflowStepDefinition(
                step_id="step_benchmark_validation",
                workflow_id=wf_id,
                name="Benchmark Against Pay Band",
                command_type="salary.benchmark",
                dependencies=["step_propose_revision"],
            ),
            WorkflowStepDefinition(
                step_id="step_cfo_approval",
                workflow_id=wf_id,
                name="CFO Budget Approval",
                command_type="salary.cfo_approve",
                dependencies=["step_benchmark_validation"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_apply_revision",
                workflow_id=wf_id,
                name="Apply Salary Revision",
                command_type="salary.revise",
                dependencies=["step_cfo_approval"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Salary Revision & Adjustment",
            description="Governed compensation increment workflow",
            steps=steps,
            priority=Priority.HIGH,
        )

    # 13. Document Verification
    def build_document_verification_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-doc-verify"
        steps = [
            WorkflowStepDefinition(
                step_id="step_upload_document", workflow_id=wf_id, name="Upload Document File", command_type="document.upload"
            ),
            WorkflowStepDefinition(
                step_id="step_extract_ocr",
                workflow_id=wf_id,
                name="Extract OCR Metadata",
                command_type="document.extract_ocr",
                dependencies=["step_upload_document"],
            ),
            WorkflowStepDefinition(
                step_id="step_compliance_tag",
                workflow_id=wf_id,
                name="Verify and Tag Compliant",
                command_type="document.verify",
                dependencies=["step_extract_ocr"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Document Verification",
            description="Automated document ingestion and OCR validation",
            steps=steps,
        )

    # 14. Attendance Regularization
    def build_attendance_regularization_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-regularization"
        steps = [
            WorkflowStepDefinition(
                step_id="step_request_regularization",
                workflow_id=wf_id,
                name="Submit Missed Punch Request",
                command_type="attendance.request_regularization",
            ),
            WorkflowStepDefinition(
                step_id="step_supervisor_approval",
                workflow_id=wf_id,
                name="Supervisor Approval",
                command_type="attendance.approve_regularization",
                dependencies=["step_request_regularization"],
                requires_approval=True,
            ),
            WorkflowStepDefinition(
                step_id="step_apply_correction",
                workflow_id=wf_id,
                name="Update Attendance Record",
                command_type="attendance.update_record",
                dependencies=["step_supervisor_approval"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Attendance Regularization",
            description="Missed punch correction workflow",
            steps=steps,
        )

    # 15. Bonus Distribution
    def build_bonus_distribution_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-bonus"
        steps = [
            WorkflowStepDefinition(
                step_id="step_allocate_pool",
                workflow_id=wf_id,
                name="Allocate Annual Bonus Pool",
                command_type="bonus.allocate_pool",
            ),
            WorkflowStepDefinition(
                step_id="step_eligibility_filter",
                workflow_id=wf_id,
                name="Filter Eligible Employees",
                command_type="bonus.filter_eligible",
                dependencies=["step_allocate_pool"],
            ),
            WorkflowStepDefinition(
                step_id="step_calculate_payouts",
                workflow_id=wf_id,
                name="Calculate Individual Bonuses",
                command_type="bonus.calculate_payout",
                dependencies=["step_eligibility_filter"],
            ),
            WorkflowStepDefinition(
                step_id="step_stage_to_payroll",
                workflow_id=wf_id,
                name="Stage Payouts to Payroll",
                command_type="bonus.stage_payroll",
                dependencies=["step_calculate_payouts"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Bonus Distribution",
            description="Performance-based bonus allocation",
            steps=steps,
        )

    # 16. Health and Safety
    def build_health_and_safety_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-safety"
        steps = [
            WorkflowStepDefinition(
                step_id="step_report_hazard", workflow_id=wf_id, name="Log Safety Hazard", command_type="safety.log_hazard"
            ),
            WorkflowStepDefinition(
                step_id="step_dispatch_inspection",
                workflow_id=wf_id,
                name="Dispatch Safety Officer",
                command_type="safety.inspect",
                dependencies=["step_report_hazard"],
            ),
            WorkflowStepDefinition(
                step_id="step_close_remediation",
                workflow_id=wf_id,
                name="Verify Hazard Remediation",
                command_type="safety.close_hazard",
                dependencies=["step_dispatch_inspection"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Health & Safety Incident",
            description="Workplace hazard resolution workflow",
            steps=steps,
        )

    # 17. Contract Renewal
    def build_contract_renewal_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-contract-renewal"
        steps = [
            WorkflowStepDefinition(
                step_id="step_contract_expiry_alert",
                workflow_id=wf_id,
                name="60-Day Expiry Notice",
                command_type="contract.alert_expiry",
            ),
            WorkflowStepDefinition(
                step_id="step_evaluate_contractor",
                workflow_id=wf_id,
                name="Evaluate Performance",
                command_type="contract.evaluate",
                dependencies=["step_contract_expiry_alert"],
            ),
            WorkflowStepDefinition(
                step_id="step_draft_terms",
                workflow_id=wf_id,
                name="Draft Renewal Terms",
                command_type="contract.draft_terms",
                dependencies=["step_evaluate_contractor"],
            ),
            WorkflowStepDefinition(
                step_id="step_sign_contract",
                workflow_id=wf_id,
                name="Execute Contract Renewal",
                command_type="contract.sign",
                dependencies=["step_draft_terms"],
                requires_approval=True,
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Contract Renewal",
            description="Contractor extension and term renewal",
            steps=steps,
        )

    # 18. Certification Tracking
    def build_certification_tracking_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-cert-track"
        steps = [
            WorkflowStepDefinition(
                step_id="step_cert_expiry_alert", workflow_id=wf_id, name="Cert Expiry Notice", command_type="cert.alert_expiry"
            ),
            WorkflowStepDefinition(
                step_id="step_enroll_recert",
                workflow_id=wf_id,
                name="Enroll Recertification Course",
                command_type="course.enroll",
                dependencies=["step_cert_expiry_alert"],
            ),
            WorkflowStepDefinition(
                step_id="step_validate_credential",
                workflow_id=wf_id,
                name="Validate New Credential",
                command_type="cert.validate",
                dependencies=["step_enroll_recert"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Certification Tracking",
            description="Mandatory certification recertification",
            steps=steps,
        )

    # 19. Employee Survey
    def build_employee_survey_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-survey"
        steps = [
            WorkflowStepDefinition(
                step_id="step_create_survey", workflow_id=wf_id, name="Author Employee Survey", command_type="survey.create"
            ),
            WorkflowStepDefinition(
                step_id="step_dispatch_survey",
                workflow_id=wf_id,
                name="Distribute Anonymous Survey",
                command_type="survey.distribute",
                dependencies=["step_create_survey"],
            ),
            WorkflowStepDefinition(
                step_id="step_aggregate_responses",
                workflow_id=wf_id,
                name="Aggregate Survey Responses",
                command_type="survey.aggregate",
                dependencies=["step_dispatch_survey"],
            ),
            WorkflowStepDefinition(
                step_id="step_sentiment_report",
                workflow_id=wf_id,
                name="Generate Sentiment Report",
                command_type="survey.analyze_sentiment",
                dependencies=["step_aggregate_responses"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Employee Engagement Survey",
            description="Pulse and satisfaction survey execution",
            steps=steps,
        )

    # 20. Exit Interview
    def build_exit_interview_workflow(self, org_id: str) -> WorkflowDefinition:
        wf_id = "wf-tpl-exit-interview"
        steps = [
            WorkflowStepDefinition(
                step_id="step_dispatch_exit_form", workflow_id=wf_id, name="Dispatch Exit Form", command_type="exit.dispatch_form"
            ),
            WorkflowStepDefinition(
                step_id="step_collect_reasons",
                workflow_id=wf_id,
                name="Collect Separation Reasons",
                command_type="exit.collect_feedback",
                dependencies=["step_dispatch_exit_form"],
            ),
            WorkflowStepDefinition(
                step_id="step_feed_retention_analytics",
                workflow_id=wf_id,
                name="Update Attrition Risk Models",
                command_type="ml.update_attrition_features",
                dependencies=["step_collect_reasons"],
            ),
        ]
        return WorkflowDefinition(
            workflow_id=wf_id,
            organization_id=org_id,
            name="Exit Interview & Analytics",
            description="Separation feedback analysis and ML feature updates",
            steps=steps,
        )
