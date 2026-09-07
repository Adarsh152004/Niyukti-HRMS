"""
Payroll MCP Server — Read-only payslip component breakdowns and anomaly inquiry tools.
"""

from __future__ import annotations

from typing import Any

from backend.mcp.domain.models import MCPToolCallRequest, MCPToolContract
from backend.mcp.servers.base import MCPServer


class PayrollMCPServer(MCPServer):
    """Internal MCP server exposing read-only payslip breakdowns without mutating payroll records."""

    def __init__(self) -> None:
        super().__init__(
            server_id="payroll-server",
            name="Payroll Read-Only MCP Server",
            description="Explains payslip itemizations, gross-to-net calculations, and statistical variances.",
        )

    def _register_server_tools(self) -> None:
        self.register_tool(
            MCPToolContract(
                tool_id="payroll.explain_payslip_breakdown",
                server_id=self.server_id,
                name="Explain Payslip Breakdown",
                description="Retrieve itemized earnings, deductions, and tax withholdings for an employee payslip cycle.",
                input_schema={
                    "type": "object",
                    "properties": {"employee_id": {"type": "string"}, "cycle_month": {"type": "string"}},
                    "required": ["employee_id"],
                },
                required_capabilities=["payroll:read"],
                is_read_only=True,
            ),
            self._handle_explain_payslip,
        )

    async def _handle_explain_payslip(self, req: MCPToolCallRequest) -> dict[str, Any]:
        emp_id = req.arguments.get("employee_id", "emp-default")
        return {
            "employee_id": emp_id,
            "period": req.arguments.get("cycle_month", "2026-08"),
            "base_salary": 8500.0,
            "housing_allowance": 1200.0,
            "gross_pay": 9700.0,
            "tax_withholding": 1940.0,
            "health_insurance": 250.0,
            "net_pay": 7510.0,
            "currency": "USD",
        }
