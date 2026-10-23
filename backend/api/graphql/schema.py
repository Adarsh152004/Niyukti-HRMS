"""
AI-Powered Intelligent HRMS — Unified GraphQL Gateway Schema.

Provides relational and graph querying for:
- Employee 360 graph (Department, Manager, Direct Reports, Skills)
- AI Agent Fleet hierarchy & telemetry
- Organizational metrics
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(tags=["GraphQL Gateway"])


class GraphQLRequest(BaseModel):
    query: str
    variables: dict[str, Any] | None = None
    operationName: str | None = None


# Synthetic graph data resolver for enterprise graph queries
DEMO_GRAPH_DATA = {
    "employees": [
        {
            "id": "emp-0001",
            "name": "Priya Sharma",
            "title": "Principal AI Architect",
            "department": {"id": "dept-01", "name": "AI & Data Engineering"},
            "skills": ["Distributed AI", "PyTorch", "System Architecture"],
            "manager": {"id": "emp-0007", "name": "Dr. Elena Rostova"},
            "directReports": [],
        },
        {
            "id": "emp-0002",
            "name": "Rahul Mehta",
            "title": "Staff Software Engineer",
            "department": {"id": "dept-02", "name": "Core Platform Engineering"},
            "skills": ["Go", "Kubernetes", "PostgreSQL", "Kafka"],
            "manager": {"id": "emp-0005", "name": "Amara Okafor"},
            "directReports": [],
        },
        {
            "id": "emp-0007",
            "name": "Dr. Elena Rostova",
            "title": "VP of AI Research",
            "department": {"id": "dept-01", "name": "AI & Data Engineering"},
            "skills": ["Leadership", "Executive Management", "Research Strategy"],
            "manager": None,
            "directReports": [{"id": "emp-0001", "name": "Priya Sharma"}],
        },
    ],
    "agents": [
        {"id": "ag-01", "name": "Executive Operations Agent", "status": "ACTIVE", "successRate": 0.994},
        {"id": "ag-02", "name": "Talent Acquisition Agent", "status": "ACTIVE", "successRate": 0.981},
        {"id": "ag-04", "name": "Payroll Assistant Agent", "status": "ACTIVE", "successRate": 1.000},
    ],
    "organization": {
        "name": "Apex Technologies Global",
        "totalHeadcount": 936,
        "activeAgents": 24,
        "activeWorkflows": 3,
    },
}


@router.post("/graphql", summary="GraphQL Gateway Endpoint")
async def handle_graphql(request: GraphQLRequest) -> JSONResponse:
    """
    Unified GraphQL endpoint resolving queries across employees, departments, and agent hierarchies.
    """
    query = request.query.strip()

    # Simple declarative resolver matching requested fields
    data: dict[str, Any] = {}

    if "employees" in query:
        data["employees"] = DEMO_GRAPH_DATA["employees"]
    if "agents" in query:
        data["agents"] = DEMO_GRAPH_DATA["agents"]
    if "organization" in query:
        data["organization"] = DEMO_GRAPH_DATA["organization"]

    # Fallback to entire graph if generic query
    if not data:
        data = DEMO_GRAPH_DATA

    return JSONResponse(content={"data": data})


@router.get("/graphql", summary="GraphQL Query Explorer")
async def get_graphql_schema() -> JSONResponse:
    """Returns the SDL schema definition."""
    schema_sdl = """
    type Department {
      id: ID!
      name: String!
    }

    type Employee {
      id: ID!
      name: String!
      title: String!
      department: Department
      skills: [String!]!
      manager: Employee
      directReports: [Employee!]!
    }

    type Agent {
      id: ID!
      name: String!
      status: String!
      successRate: Float!
    }

    type Query {
      employees: [Employee!]!
      agents: [Agent!]!
      organization: Organization!
    }
    """
    return JSONResponse(content={"schema": schema_sdl.strip()})
