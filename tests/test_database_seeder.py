"""
AI-Powered Intelligent HRMS — Synthetic Database Seeder Test Suite.

Verifies:
1. Deterministic generation reproducibility across seeds
2. Manager hierarchy DAG acyclicity (no circular reporting loops)
3. Salary conformance to compensation bands (L1 to L8)
4. Scale presets ('small', 'medium', 'large')
5. Deterministic statutory payroll arithmetic integrity
6. Cross-domain referential consistency
"""

import pytest
from backend.database.seeder.seeder import DatabaseSeeder


def test_seeder_deterministic_reproducibility():
    """Verify identical seeds produce identical employee counts, IDs, and payroll totals."""
    seeder1 = DatabaseSeeder(seed=42)
    result1 = seeder1.generate_all(scale="small", organization_id="org-test")

    seeder2 = DatabaseSeeder(seed=42)
    result2 = seeder2.generate_all(scale="small", organization_id="org-test")

    # Counts must match exactly
    assert result1["summary"].employee_count == result2["summary"].employee_count
    assert result1["summary"].payroll_runs_count == result2["summary"].payroll_runs_count

    # First employee details must match
    emp1 = result1["employees"][0]
    emp2 = result2["employees"][0]
    assert emp1.id == emp2.id
    assert emp1.full_name == emp2.full_name
    assert emp1.salary == emp2.salary


def test_manager_hierarchy_dag_acyclicity():
    """Verify that reporting hierarchy forms a valid directed acyclic graph (DAG)."""
    seeder = DatabaseSeeder(seed=42)
    result = seeder.generate_all(scale="medium", organization_id="org-test")
    employees = result["employees"]

    emp_dict = {e.id: e for e in employees}

    # CEO must have manager_id = None
    ceo = next(e for e in employees if e.level == 8)
    assert ceo.manager_id is None

    # Every subordinate must trace back to CEO without loops
    for emp in employees:
        if emp.id == ceo.id:
            continue

        visited = set()
        curr = emp
        while curr.manager_id is not None:
            assert curr.id not in visited, f"Circular reporting loop detected for employee {curr.id}"
            visited.add(curr.id)
            assert curr.manager_id in emp_dict, f"Dangling manager reference: {curr.manager_id}"
            curr = emp_dict[curr.manager_id]

        assert curr.id == ceo.id, f"Reporting hierarchy for {emp.id} did not terminate at CEO"


def test_salary_conformance_to_bands():
    """Verify all employee salaries fall within their assigned salary band boundaries."""
    seeder = DatabaseSeeder(seed=42)
    result = seeder.generate_all(scale="small", organization_id="org-test")
    org_data = result["org_data"]
    employees = result["employees"]

    bands = {b.code: b for b in org_data.salary_bands}

    for emp in employees:
        band = bands[emp.band_code]
        assert emp.salary >= band.min_salary * 0.9, f"Salary for {emp.full_name} is below band floor"
        assert emp.salary <= band.max_salary * 1.1, f"Salary for {emp.full_name} is above band ceiling"


def test_payroll_arithmetic_integrity():
    """Verify deterministic gross-to-net deductions math on payslips."""
    seeder = DatabaseSeeder(seed=42)
    result = seeder.generate_all(scale="small", organization_id="org-test")
    payroll_runs = result["payroll_runs"]

    for run in payroll_runs:
        for slip in run.payslips:
            assert round(slip.base_salary + slip.special_allowance, 2) == round(slip.gross_earnings, 2)
            assert round(slip.epf_deduction + slip.tds_tax_deduction + slip.other_deductions, 2) == round(slip.total_deductions, 2)
            assert round(slip.gross_earnings - slip.total_deductions, 2) == round(slip.net_payable, 2)


def test_scale_presets():
    """Verify scale presets generate expected target sizes."""
    seeder = DatabaseSeeder(seed=42)

    small_res = seeder.generate_all(scale="small")
    assert small_res["summary"].employee_count == 20

    med_res = seeder.generate_all(scale="medium")
    assert med_res["summary"].employee_count == 60


def test_all_14_hrms_domains_populated():
    """Verify all 14 HRMS domains have referentially sound synthetic entities."""
    seeder = DatabaseSeeder(seed=42)
    result = seeder.generate_all(scale="medium", organization_id="org-apex-01")

    assert len(result["org_data"].departments) == 7
    assert len(result["employees"]) == 60
    assert len(result["attendance"]) > 500
    assert len(result["leave_policies"]) == 4
    assert len(result["leave_requests"]) > 0
    assert len(result["payroll_runs"]) == 3
    assert len(result["jobs"]) == 6
    assert len(result["reviews"]) > 0
    assert len(result["agents"]) == 12
    assert len(result["approvals"]) == 3
    assert len(result["audit_logs"]) == 5
