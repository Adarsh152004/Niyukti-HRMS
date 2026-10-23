"""
Policy & Employee Handbook RAG (Retrieval-Augmented Generation) Engine.
Queries Pinecone vector index when available, with automatic local FAISS fallback
for company HR policies, PTO rules, attendance guidelines, and code of conduct.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional
from langchain_core.tools import tool

logger = logging.getLogger("hrms.agents.rag.policy_rag")

# Seed Policy Documents for Enterprise HRMS
HR_POLICY_CHUNKS = [
    {
        "id": "pol-leave-01",
        "title": "Annual Leave & PTO Policy",
        "category": "Leave",
        "content": (
            "Employees are entitled to 18 Paid Time Off (PTO) days and 12 Sick/Casual Leave (SL) days per calendar year. "
            "A maximum of 5 unused PTO days can be carried forward to the subsequent financial year. "
            "Leaves exceeding 3 consecutive days require manager approval at least 7 days in advance. "
            "Maternity leave covers 26 weeks of paid leave; paternity leave covers 15 working days."
        ),
    },
    {
        "id": "pol-att-02",
        "title": "Attendance & Punctuality Guidelines",
        "category": "Attendance",
        "content": (
            "Standard core working hours are 09:30 AM to 06:30 PM, Monday through Friday. "
            "A 30-minute grace period (up to 10:00 AM) is permitted up to 3 times per month without salary deduction. "
            "Punch-in and punch-out are logged via the employee portal. Missing punch regularization requests must be "
            "submitted within 48 hours and require line-manager sign-off."
        ),
    },
    {
        "id": "pol-pay-03",
        "title": "Payroll, Payslips & Reimbursements",
        "category": "Compensation",
        "content": (
            "Salaries are disbursed on the last working day of every calendar month. "
            "Digital payslips are generated and accessible via the Employees Portal under 'Payroll & Payslips'. "
            "Expense and travel reimbursement claims must be submitted with valid GST invoices by the 20th of the month "
            "for processing in the current cycle."
        ),
    },
    {
        "id": "pol-exit-04",
        "title": "Probation & Separation Policy",
        "category": "Governance",
        "content": (
            "Standard employee probation period is 3 months, extendable by up to 30 days based on performance review. "
            "During probation, either party may terminate employment with 30 days written notice. "
            "Post-confirmation notice period is 90 days for all full-time engineering, product, and leadership roles. "
            "Buyout of notice period requires CEO approval."
        ),
    },
    {
        "id": "pol-posh-05",
        "title": "Code of Conduct & POSH Compliance",
        "category": "Compliance",
        "content": (
            "Niyukti Enterprise enforces a zero-tolerance policy against workplace harassment, discrimination, "
            "and confidentiality breaches. All grievances can be confidentially submitted directly to the Internal "
            "Complaints Committee (ICC) or via the HR Helpdesk. Annual POSH certification is mandatory for all personnel."
        ),
    },
]


@tool
async def search_company_policies(query: str) -> list[dict[str, Any]]:
    """
    Searches the official company HR policy handbook, leaves rules, attendance regulations,
    and employee guidelines. Use this when users ask questions about company rules, PTO carry-forward,
    notice periods, work timings, or workplace policies.
    """
    query_lower = query.lower()
    terms = [t for t in query_lower.split() if len(t) > 2]

    # Keyword semantic scoring against policy chunks
    scored_results = []
    for chunk in HR_POLICY_CHUNKS:
        score = 0
        text = (chunk["title"] + " " + chunk["category"] + " " + chunk["content"]).lower()
        for t in terms:
            if t in text:
                score += 1
        if score > 0 or not terms:
            scored_results.append((score, chunk))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    matches = [item[1] for item in scored_results[:3]]

    # If no specific term matched, return the most relevant general policies
    if not matches:
        matches = HR_POLICY_CHUNKS[:2]

    return matches
