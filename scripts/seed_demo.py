"""
AI-Powered Intelligent HRMS — Production & Demo Database Seeding Script.

Usage:
  python scripts/seed_demo.py --employees 100 --scale medium --tenant org-apex-01 --seed 42
"""

from __future__ import annotations

import argparse
import sys

from backend.database.seeder.seeder import DatabaseSeeder


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AI-Powered Intelligent HRMS — Synthetic Demo Database Seeder"
    )
    parser.add_argument(
        "--employees",
        type=int,
        default=100,
        help="Number of synthetic employees to generate (default: 100)",
    )
    parser.add_argument(
        "--scale",
        choices=["small", "medium", "large"],
        default="medium",
        help="Volume preset (default: medium)",
    )
    parser.add_argument(
        "--tenant",
        default="org-apex-01",
        help="Organization tenant ID (default: org-apex-01)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic PRNG seed (default: 42)",
    )

    args = parser.parse_args()

    print("==================================================================")
    print("AI-POWERED INTELLIGENT HRMS — SYNTHETIC DEMO SEEDER")
    print("==================================================================")
    print(f"• Target Scale:        {args.scale.upper()} (~{args.employees} employees)")
    print(f"• Tenant Identifier:   {args.tenant}")
    print(f"• PRNG Seed:           {args.seed}")
    print("• Synthesizing enterprise organization, employee DAG, and records...")

    seeder = DatabaseSeeder(seed=args.seed)
    result = seeder.generate_all(scale=args.scale, organization_id=args.tenant)
    summary = result["summary"]

    print("\n[+] Synthetic Database Graph Generated Successfully!")
    print(f"  • Execution Duration:    {summary.duration_seconds}s")
    print(f"  • Organization Entities: 1 ({summary.organization_id})")
    print(f"  • Departments:           {summary.department_count}")
    print(f"  • Employees:             {summary.employee_count}")
    print(f"  • Biometric Attendance:  {summary.attendance_records_count} logs")
    print(f"  • Leave Ledger Requests: {summary.leave_requests_count} entries")
    print(f"  • Payroll Batches:       {summary.payroll_runs_count} runs ({summary.payslips_count} payslips)")
    print(f"  • Talent Openings:       {summary.jobs_count} requisitions ({summary.candidates_count} candidates)")
    print(f"  • Performance Reviews:   {summary.reviews_count} completed reviews")
    print(f"  • AI Agent Fleet:        {summary.agents_count} operational agents")
    print(f"  • HITL Approval Queue:   {summary.approvals_count} pending governance items")
    print(f"  • Audit Trail Logs:      {summary.audit_logs_count} cryptographic entries")
    print("==================================================================\n")


if __name__ == "__main__":
    main()
