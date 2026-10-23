"""
AI-Powered Intelligent HRMS — Database Seeder CLI Command.

Usage:
  python -m backend.database.seeder.cli --scale small|medium|large --seed 42 --tenant-id org-apex-01
"""

from __future__ import annotations

import argparse
import sys

from backend.database.seeder.seeder import DatabaseSeeder


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-Powered Intelligent HRMS — Synthetic Database Seeder"
    )
    parser.add_argument(
        "--scale",
        choices=["small", "medium", "large"],
        default="medium",
        help="Volume of enterprise synthetic data to generate (default: medium)",
    )
    parser.add_argument(
        "--tenant-id",
        default="org-apex-01",
        help="Primary tenant / organization identifier (default: org-apex-01)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic PRNG seed for reproducibility (default: 42)",
    )

    args = parser.parse_args()

    print(f"\n==================================================================")
    print(f"AI-Powered Intelligent HRMS — Synthetic Data Seeder")
    print(f"==================================================================")
    print(f"• Scale:       {args.scale.upper()}")
    print(f"• Tenant ID:   {args.tenant_id}")
    print(f"• PRNG Seed:   {args.seed}")
    print(f"• Generating synthetic organizational graph...")

    seeder = DatabaseSeeder(seed=args.seed)
    result = seeder.generate_all(scale=args.scale, organization_id=args.tenant_id)
    summary = result["summary"]

    print(f"\n[+] Seeding Successful in {summary.duration_seconds}s!")
    print(f"------------------------------------------------------------------")
    print(f"  • Organizations:         1 ({summary.organization_id})")
    print(f"  • Departments:           {summary.department_count}")
    print(f"  • Employees:             {summary.employee_count}")
    print(f"  • Attendance Logs:       {summary.attendance_records_count}")
    print(f"  • Leave Requests:        {summary.leave_requests_count}")
    print(f"  • Payroll Runs:          {summary.payroll_runs_count} ({summary.payslips_count} payslips)")
    print(f"  • Job Openings:          {summary.jobs_count} ({summary.candidates_count} candidates)")
    print(f"  • Performance Reviews:   {summary.reviews_count}")
    print(f"  • AI Agent Fleet:        {summary.agents_count} agents")
    print(f"  • HITL Approvals Queue:  {summary.approvals_count} items")
    print(f"  • Audit Trail Logs:      {summary.audit_logs_count} entries")
    print(f"==================================================================\n")


if __name__ == "__main__":
    main()
