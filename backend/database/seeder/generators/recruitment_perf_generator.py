"""
AI-Powered Intelligent HRMS — Recruitment & Performance Synthetic Data Generator.

Generates:
- Job Openings & Candidate Pipeline with AI screening fit scores
- Performance Review Cycles, OKR goals, and calibrated ratings
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from backend.database.seeder.generators.employee_generator import (
    FIRST_NAMES,
    LAST_NAMES,
    SyntheticEmployee,
)
from backend.database.seeder.generators.org_generator import SyntheticOrgData


@dataclass
class SyntheticCandidate:
    id: str
    job_id: str
    full_name: str
    email: str
    stage: str  # APPLIED, SCREENING, INTERVIEW, OFFER, HIRED, REJECTED
    ai_score: int
    ai_summary: str
    confidence: int
    applied_date: str


@dataclass
class SyntheticJobOpening:
    id: str
    organization_id: str
    department_id: str
    title: str
    band_code: str
    headcount_target: int
    status: str  # OPEN, CLOSED, DRAFT
    candidates: list[SyntheticCandidate]


@dataclass
class SyntheticPerformanceReview:
    id: str
    employee_id: str
    employee_name: str
    cycle: str  # Q3-2026
    rating: str  # EXCEEDS_EXPECTATIONS, MEETS_EXPECTATIONS, NEEDS_IMPROVEMENT
    okr_progress_pct: int
    calibrated: bool


def generate_recruitment_and_performance(
    org_data: SyntheticOrgData,
    employees: list[SyntheticEmployee],
    seed: int = 42,
) -> tuple[list[SyntheticJobOpening], list[SyntheticPerformanceReview]]:
    """Generates synthetic job requisitions, candidate pipelines, and review cycles."""
    rng = random.Random(seed)
    jobs: list[SyntheticJobOpening] = []
    reviews: list[SyntheticPerformanceReview] = []

    org_id = org_data.organization_id

    # 1. Job Openings
    job_templates = [
        ("Principal AI Architect", "AI & Data Engineering", "L6"),
        ("Staff Software Engineer (Platform)", "Core Platform Engineering", "L5"),
        ("Lead Product Designer", "Product Experience & Design", "L4"),
        ("Senior Financial Analyst", "Finance & Treasury", "L3"),
        ("Lead Regulatory Counsel", "Legal, Risk & Compliance", "L5"),
        ("Enterprise Account Executive", "Enterprise Sales & GTM", "L4"),
    ]

    stages = ["APPLIED", "SCREENING", "INTERVIEW", "OFFER", "HIRED", "REJECTED"]
    stage_weights = [30, 25, 20, 10, 5, 10]

    for j_idx, (title, dept_name, band) in enumerate(job_templates):
        dept = next((d for d in org_data.departments if d.name == dept_name), org_data.departments[0])
        job_id = f"job-{org_id}-{j_idx+1:02d}"

        candidates: list[SyntheticCandidate] = []
        num_candidates = rng.randint(4, 8)

        for c_idx in range(num_candidates):
            first = rng.choice(FIRST_NAMES)
            last = rng.choice(LAST_NAMES)
            score = rng.randint(60, 98)
            conf = rng.randint(80, 99)

            summary = (
                f"Candidate matches {score}% of technical requirements. Strong domain experience verified."
                if score >= 85
                else f"Baseline competency met ({score}%). Minor gap in specialized tooling."
            )

            cand = SyntheticCandidate(
                id=f"cand-{job_id}-{c_idx+1:02d}",
                job_id=job_id,
                full_name=f"{first} {last}",
                email=f"{first.lower()}.{last.lower()}@applicant.demo",
                stage=rng.choices(stages, weights=stage_weights, k=1)[0],
                ai_score=score,
                ai_summary=summary,
                confidence=conf,
                applied_date="2026-08-15",
            )
            candidates.append(cand)

        jobs.append(
            SyntheticJobOpening(
                id=job_id,
                organization_id=org_id,
                department_id=dept.id,
                title=title,
                band_code=band,
                headcount_target=rng.randint(1, 3),
                status="OPEN",
                candidates=candidates,
            )
        )

    # 2. Performance Review Cycle
    ratings = ["EXCEEDS_EXPECTATIONS", "MEETS_EXPECTATIONS", "NEEDS_IMPROVEMENT"]
    rating_weights = [20, 75, 5]  # Standard bell curve

    for emp in employees:
        if emp.status != "active":
            continue

        rating = rng.choices(ratings, weights=rating_weights, k=1)[0]
        okr_pct = rng.randint(70, 100) if rating != "NEEDS_IMPROVEMENT" else rng.randint(40, 65)

        reviews.append(
            SyntheticPerformanceReview(
                id=f"rev-q3-2026-{emp.id}",
                employee_id=emp.id,
                employee_name=emp.full_name,
                cycle="Q3-2026",
                rating=rating,
                okr_progress_pct=okr_pct,
                calibrated=True,
            )
        )

    return jobs, reviews
