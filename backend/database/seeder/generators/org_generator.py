"""
AI-Powered Intelligent HRMS — Organization & Department Synthetic Data Generator.

Generates:
- Enterprise legal entities (Parent Corp, Regional Operating Entities)
- Department hierarchy (AI Research, Platform Eng, Product, Finance, Legal, HR, Sales)
- Salary Bands & Grades (L1 to L8 / Exec)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SyntheticDepartment:
    id: str
    name: str
    code: str
    organization_id: str
    head_name: str
    target_headcount_pct: float
    budget: float


@dataclass
class SyntheticSalaryBand:
    code: str
    level: int
    title_prefix: str
    min_salary: float
    mid_salary: float
    max_salary: float


@dataclass
class SyntheticOrgData:
    organization_id: str
    legal_name: str
    departments: list[SyntheticDepartment]
    salary_bands: list[SyntheticSalaryBand]


def generate_organization_structure(
    organization_id: str = "org-apex-01",
    legal_name: str = "Apex Technologies Global Inc.",
    seed: int = 42,
) -> SyntheticOrgData:
    """Generates deterministic enterprise organizational hierarchy and salary bands."""
    rng = random.Random(seed)

    departments = [
        SyntheticDepartment(
            id=f"{organization_id}-dept-ai",
            name="AI & Data Engineering",
            code="AI-DATA",
            organization_id=organization_id,
            head_name="Dr. Elena Rostova",
            target_headcount_pct=0.20,
            budget=14800000.0,
        ),
        SyntheticDepartment(
            id=f"{organization_id}-dept-eng",
            name="Core Platform Engineering",
            code="PLAT-ENG",
            organization_id=organization_id,
            head_name="Amara Okafor",
            target_headcount_pct=0.35,
            budget=24500000.0,
        ),
        SyntheticDepartment(
            id=f"{organization_id}-dept-prod",
            name="Product Experience & Design",
            code="PROD-DES",
            organization_id=organization_id,
            head_name="James Thornton",
            target_headcount_pct=0.10,
            budget=7200000.0,
        ),
        SyntheticDepartment(
            id=f"{organization_id}-dept-fin",
            name="Finance & Treasury",
            code="FIN-OPS",
            organization_id=organization_id,
            head_name="Lucia Fernandez",
            target_headcount_pct=0.08,
            budget=4800000.0,
        ),
        SyntheticDepartment(
            id=f"{organization_id}-dept-leg",
            name="Legal, Risk & Compliance",
            code="LEGAL-GOV",
            organization_id=organization_id,
            head_name="Dr. Michael Adeyemi",
            target_headcount_pct=0.05,
            budget=3600000.0,
        ),
        SyntheticDepartment(
            id=f"{organization_id}-dept-hr",
            name="Talent Acquisition & People Ops",
            code="PEOPLE-OPS",
            organization_id=organization_id,
            head_name="Ananya Deshmukh",
            target_headcount_pct=0.06,
            budget=4100000.0,
        ),
        SyntheticDepartment(
            id=f"{organization_id}-dept-gtm",
            name="Enterprise Sales & GTM",
            code="GTM-SALES",
            organization_id=organization_id,
            head_name="Sandra Liu",
            target_headcount_pct=0.16,
            budget=16900000.0,
        ),
    ]

    salary_bands = [
        SyntheticSalaryBand("L1", 1, "Associate / Analyst", 450000, 600000, 750000),
        SyntheticSalaryBand("L2", 2, "Senior Analyst / Engineer I", 700000, 950000, 1200000),
        SyntheticSalaryBand("L3", 3, "Engineer II / Lead Specialist", 1100000, 1450000, 1800000),
        SyntheticSalaryBand("L4", 4, "Senior Engineer / Manager", 1600000, 2100000, 2600000),
        SyntheticSalaryBand("L5", 5, "Staff Engineer / Senior Manager", 2400000, 3100000, 3800000),
        SyntheticSalaryBand("L6", 6, "Principal / Director", 3500000, 4500000, 5600000),
        SyntheticSalaryBand("L7", 7, "Senior Director / Head of Dept", 5200000, 6800000, 8400000),
        SyntheticSalaryBand("L8", 8, "Vice President / C-Suite", 8000000, 11000000, 15000000),
    ]

    return SyntheticOrgData(
        organization_id=organization_id,
        legal_name=legal_name,
        departments=departments,
        salary_bands=salary_bands,
    )
