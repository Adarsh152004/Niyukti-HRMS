"""
AI-Powered Intelligent HRMS — Employee Synthetic Data Generator.

Generates:
- Realistic multicultural names (Indian, North American, European, East Asian)
- Strict acyclic manager hierarchy (CEO -> VP -> Director -> Manager -> Individual Contributor)
- Skills, work emails, salary aligned with bands, and hire dates
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

from backend.database.seeder.generators.org_generator import SyntheticOrgData


@dataclass
class SyntheticEmployee:
    id: str
    employee_number: str
    organization_id: str
    department_id: str
    department_name: str
    full_name: str
    email: str
    designation: str
    band_code: str
    level: int
    manager_id: str | None
    manager_name: str | None
    salary: float
    location: str
    hire_date: str
    skills: list[str]
    status: str = "active"


FIRST_NAMES = [
    "Priya", "Rahul", "Sara", "Marcus", "Aisha", "Vikram", "Elena", "Tom",
    "Ananya", "David", "Neha", "Michael", "Fatima", "Arjun", "Kavita", "James",
    "Siddharth", "Zoe", "Rohan", "Hannah", "Aditya", "Chloe", "Karan", "Daniel",
    "Meera", "Lucas", "Sunita", "Alex", "Deepak", "Sophia", "Rajesh", "Maya",
]

LAST_NAMES = [
    "Sharma", "Mehta", "Kim", "Chen", "Hassan", "Patel", "Rostova", "Bergson",
    "Deshmukh", "Park", "Verma", "Adeyemi", "Al-Rashid", "Nair", "Iyer", "Thornton",
    "Kapoor", "Lin", "Gupta", "Miller", "Fernandez", "Osei", "Okafor", "Liu",
]

LOCATIONS = [
    "Bangalore (Hybrid)", "Hyderabad (Hybrid)", "Mumbai (Office)", "San Francisco (Office)",
    "New York (Hybrid)", "London (Hybrid)", "Singapore (Office)", "Seoul (Remote)",
    "Chicago (Remote)", "Berlin (Remote)",
]

DEPARTMENT_SKILLS: dict[str, list[str]] = {
    "AI & Data Engineering": ["PyTorch", "Distributed Training", "MLOps", "Vector DBs", "FastAPI", "Python", "Ray", "CUDA"],
    "Core Platform Engineering": ["Go", "Kubernetes", "PostgreSQL", "Kafka", "mTLS", "Distributed Systems", "Redis", "Rust"],
    "Product Experience & Design": ["Design Systems", "Figma", "React", "TypeScript", "Tailwind CSS", "User Research", "WCAG"],
    "Finance & Treasury": ["Financial Modeling", "Payroll Audit", "Treasury Operations", "GAAP", "Tax Compliance", "ERP"],
    "Legal, Risk & Compliance": ["AI Ethics", "GDPR", "SOC 2", "ISO 27001", "Employment Law", "Contract Negotiation"],
    "Talent Acquisition & People Ops": ["Technical Sourcing", "Talent Pipeline", "Compensation Banding", "Interview Calibration", "HRIS"],
    "Enterprise Sales & GTM": ["Enterprise SaaS", "Strategic Accounts", "Contract Structuring", "Solution Selling", "CRM"],
}


def generate_employees(
    org_data: SyntheticOrgData,
    count: int = 50,
    seed: int = 42,
) -> list[SyntheticEmployee]:
    """
    Generates a deterministic cohort of employees with valid reporting hierarchies.
    """
    rng = random.Random(seed)
    employees: list[SyntheticEmployee] = []

    # 1. Create Executive CEO (Top of DAG)
    ceo_id = f"{org_data.organization_id}-emp-0001"
    ceo = SyntheticEmployee(
        id=ceo_id,
        employee_number="EMP-0001",
        organization_id=org_data.organization_id,
        department_id=org_data.departments[0].id,
        department_name=org_data.departments[0].name,
        full_name="Alex Rivera",
        email="alex.rivera@enterprise.demo",
        designation="Chief Executive Officer",
        band_code="L8",
        level=8,
        manager_id=None,
        manager_name=None,
        salary=12000000.0,
        location="San Francisco (Office)",
        hire_date="2020-01-15",
        skills=["Executive Leadership", "Board Governance", "Strategic Planning"],
    )
    employees.append(ceo)

    # 2. Create Department Heads (VPs / Directors reporting to CEO)
    dept_heads: dict[str, SyntheticEmployee] = {}
    for idx, dept in enumerate(org_data.departments):
        emp_id = f"{org_data.organization_id}-emp-{len(employees)+1:04d}"
        first = FIRST_NAMES[(idx * 3 + 1) % len(FIRST_NAMES)]
        last = LAST_NAMES[(idx * 2 + 1) % len(LAST_NAMES)]
        full_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@enterprise.demo"

        skills = rng.sample(DEPARTMENT_SKILLS.get(dept.name, ["Leadership", "Strategy"]), k=4)
        head = SyntheticEmployee(
            id=emp_id,
            employee_number=f"EMP-{len(employees)+1:04d}",
            organization_id=org_data.organization_id,
            department_id=dept.id,
            department_name=dept.name,
            full_name=full_name,
            email=email,
            designation=f"VP of {dept.name.split('&')[0].strip()}",
            band_code="L7",
            level=7,
            manager_id=ceo.id,
            manager_name=ceo.full_name,
            salary=7500000.0 + rng.uniform(-500000, 500000),
            location=LOCATIONS[idx % len(LOCATIONS)],
            hire_date="2020-06-01",
            skills=skills,
        )
        employees.append(head)
        dept_heads[dept.id] = head

    # 3. Populate remaining workforce distributed across departments
    remaining_count = max(0, count - len(employees))
    base_hire_date = date(2021, 1, 1)

    for i in range(remaining_count):
        emp_num = len(employees) + 1
        emp_id = f"{org_data.organization_id}-emp-{emp_num:04d}"

        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        full_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{emp_num}@enterprise.demo"

        # Select department based on target percentage
        dept = rng.choices(
            org_data.departments,
            weights=[d.target_headcount_pct for d in org_data.departments],
            k=1,
        )[0]

        # Select level (L1 - L6)
        level_num = rng.choices([1, 2, 3, 4, 5, 6], weights=[15, 25, 30, 18, 9, 3], k=1)[0]
        band = next(b for b in org_data.salary_bands if b.level == level_num)
        salary = rng.uniform(band.min_salary, band.max_salary)

        # Hierarchy: Find potential manager in the same department with higher level
        potential_managers = [
            e for e in employees
            if e.department_id == dept.id and e.level > level_num
        ]
        if not potential_managers:
            manager = dept_heads.get(dept.id, ceo)
        else:
            manager = rng.choice(potential_managers)

        hire_days_offset = rng.randint(0, 1800)
        emp_hire_date = (base_hire_date + timedelta(days=hire_days_offset)).isoformat()

        available_skills = DEPARTMENT_SKILLS.get(dept.name, ["Python", "SQL"])
        emp_skills = rng.sample(available_skills, k=min(len(available_skills), rng.randint(3, 5)))

        designation_title = f"{band.title_prefix} - {dept.name.split('&')[0].strip()}"

        emp = SyntheticEmployee(
            id=emp_id,
            employee_number=f"EMP-{emp_num:04d}",
            organization_id=org_data.organization_id,
            department_id=dept.id,
            department_name=dept.name,
            full_name=full_name,
            email=email,
            designation=designation_title,
            band_code=band.code,
            level=band.level,
            manager_id=manager.id,
            manager_name=manager.full_name,
            salary=round(salary, -3),
            location=rng.choice(LOCATIONS),
            hire_date=emp_hire_date,
            skills=emp_skills,
            status="active" if rng.random() > 0.05 else "inactive",
        )
        employees.append(emp)

    return employees
