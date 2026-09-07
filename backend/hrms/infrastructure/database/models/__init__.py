"""
Database Models Package - SQLAlchemy 2.x persistence models across all business domains.
"""

from __future__ import annotations

from backend.hrms.infrastructure.database.models.organization import OrganizationModel
from backend.hrms.infrastructure.database.models.department import DepartmentModel
from backend.hrms.infrastructure.database.models.designation import DesignationModel
from backend.hrms.infrastructure.database.models.role import RoleModel
from backend.hrms.infrastructure.database.models.employee import EmployeeModel
from backend.hrms.infrastructure.database.models.skills import SkillModel, EmployeeSkillModel
from backend.hrms.infrastructure.database.models.documents import EmployeeDocumentModel
from backend.hrms.infrastructure.database.models.outbox import OutboxEventModel

# New Business Domains
from backend.hrms.infrastructure.database.models.permission import PermissionModel, RolePermissionModel, EmployeeRoleModel
from backend.hrms.infrastructure.database.models.team import TeamModel, TeamMemberModel, EmploymentHistoryModel
from backend.hrms.infrastructure.database.models.attendance import WorkScheduleModel, ShiftModel, EmployeeWorkScheduleModel, AttendanceRecordModel, HolidayModel
from backend.hrms.infrastructure.database.models.leave import LeaveTypeModel, LeaveRequestModel
from backend.hrms.infrastructure.database.models.timesheet import TimesheetModel, TimesheetEntryModel
from backend.hrms.infrastructure.database.models.payroll import (
    SalaryComponentModel, SalaryStructureModel, SalaryStructureComponentModel,
    EmployeeSalaryRecordModel, EmployeeSalaryComponentModel, PayrollPeriodModel,
    PayrollRunModel, PayslipModel, PayslipItemModel
)
from backend.hrms.infrastructure.database.models.recruitment import (
    JobOpeningModel, CandidateModel, CandidateApplicationModel,
    InterviewModel, InterviewFeedbackModel, OfferModel
)
from backend.hrms.infrastructure.database.models.client import (
    ClientModel, ClientContactModel, ClientAddressModel,
    LeadModel, ClientCommunicationModel
)
from backend.hrms.infrastructure.database.models.project import ProjectModel, ProjectMemberModel, MilestoneModel
from backend.hrms.infrastructure.database.models.task import TaskModel, TaskAssignmentModel
from backend.hrms.infrastructure.database.models.project_activity import ChangeRequestModel, ReleaseModel
from backend.hrms.infrastructure.database.models.sales import (
    ClientRequirementModel, ProposalModel, QuotationModel,
    QuotationItemModel, ContractModel
)
from backend.hrms.infrastructure.database.models.finance import InvoiceModel, InvoiceItemModel, PaymentModel, ExpenseModel
from backend.hrms.infrastructure.database.models.support import (
    SupportContractModel, SupportTicketModel, TicketCommentModel, TicketAssignmentModel
)
from backend.hrms.infrastructure.database.models.document import DocumentModel
from backend.hrms.infrastructure.database.models.audit import AuditLogModel, LoginHistoryModel
from backend.security.infrastructure.models import UserModel, UserRoleModel, AgentIdentityModel, APIKeyModel

__all__ = [
    "OrganizationModel",
    "DepartmentModel",
    "DesignationModel",
    "RoleModel",
    "EmployeeModel",
    "SkillModel",
    "EmployeeSkillModel",
    "EmployeeDocumentModel",
    "OutboxEventModel",

    # Permissions & Teams
    "PermissionModel",
    "RolePermissionModel",
    "EmployeeRoleModel",
    "TeamModel",
    "TeamMemberModel",
    "EmploymentHistoryModel",

    # Attendance & Leave
    "WorkScheduleModel",
    "ShiftModel",
    "EmployeeWorkScheduleModel",
    "AttendanceRecordModel",
    "HolidayModel",
    "LeaveTypeModel",
    "LeaveRequestModel",
    "TimesheetModel",
    "TimesheetEntryModel",

    # Payroll
    "SalaryComponentModel",
    "SalaryStructureModel",
    "SalaryStructureComponentModel",
    "EmployeeSalaryRecordModel",
    "EmployeeSalaryComponentModel",
    "PayrollPeriodModel",
    "PayrollRunModel",
    "PayslipModel",
    "PayslipItemModel",

    # Recruitment
    "JobOpeningModel",
    "CandidateModel",
    "CandidateApplicationModel",
    "InterviewModel",
    "InterviewFeedbackModel",
    "OfferModel",

    # Client & CRM
    "ClientModel",
    "ClientContactModel",
    "ClientAddressModel",
    "LeadModel",
    "ClientCommunicationModel",

    # Projects & Dev
    "ProjectModel",
    "ProjectMemberModel",
    "MilestoneModel",
    "TaskModel",
    "TaskAssignmentModel",
    "ChangeRequestModel",
    "ReleaseModel",

    # Sales & Pipeline
    "ClientRequirementModel",
    "ProposalModel",
    "QuotationModel",
    "QuotationItemModel",
    "ContractModel",

    # Finance & Support
    "InvoiceModel",
    "InvoiceItemModel",
    "PaymentModel",
    "ExpenseModel",
    "SupportContractModel",
    "SupportTicketModel",
    "TicketCommentModel",
    "TicketAssignmentModel",

    # Documents & Audit
    "DocumentModel",
    "AuditLogModel",
    "LoginHistoryModel",

    # Security & Auth
    "UserModel",
    "UserRoleModel",
    "AgentIdentityModel",
    "APIKeyModel",
]
