"""
Specialized Agents CLI Commands — Typer command-line interface for inspecting and bootstrapping the 24 AI HR agents.
"""

from __future__ import annotations

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from backend.agents.specialized.application.specialization_service import SpecializedAgentService
from backend.agents.specialized.registry.catalog import SpecializedAgentCatalog

app = typer.Typer(name="agents", help="Manage and inspect the 24 Specialized AI HR Agents.")
console = Console()


@app.command("catalog")
def list_catalog() -> None:
    """List all 24 standard specialized AI HR agents in the catalog."""
    catalog = SpecializedAgentCatalog.get_instance()
    definitions = catalog.list_definitions()

    table = Table(title="Specialized AI HR Agents Catalog (24 Standard Roles)")
    table.add_column("No.", style="cyan", width=4)
    table.add_column("Role", style="bold green")
    table.add_column("Display Name", style="white")
    table.add_column("Supervisor", style="yellow")
    table.add_column("Autonomy Mode", style="magenta")
    table.add_column("Tier", style="blue")

    for idx, defn in enumerate(definitions, start=1):
        sup_str = defn.supervisor_role.value if defn.supervisor_role else "[dim]SYSTEM/GOVERNANCE[/dim]"
        table.add_row(
            str(idx),
            defn.role.value,
            defn.display_name,
            sup_str,
            defn.autonomy_mode.value,
            defn.model_policy.routing_tier.value,
        )

    console.print(table)


@app.command("bootstrap")
def bootstrap_org(
    organization_id: str = typer.Argument(..., help="Tenant Organization ID to bootstrap"),
) -> None:
    """Bootstrap all 24 standard specialized agents for an organization."""
    svc = SpecializedAgentService.get_instance()
    res = svc.bootstrap_tenant(organization_id)

    rprint(f"[bold green]Successfully bootstrapped organization [{organization_id}]:[/bold green]")
    rprint(f"  • Created: [cyan]{res.created_count}[/cyan]")
    rprint(f"  • Updated: [yellow]{res.updated_count}[/yellow]")
    rprint(f"  • Skipped: [dim]{res.skipped_count}[/dim]")
    rprint(f"  • Total Active Instances: [bold]{len(res.instances)}[/bold]")


@app.command("specialization")
def inspect_specialization(
    role: str = typer.Argument(..., help="Specialized Agent Role e.g. RESUME_SCREENING_AGENT"),
) -> None:
    """Detailed view of an agent's purpose, responsibilities, SLA, and budget."""
    catalog = SpecializedAgentCatalog.get_instance()
    defn = catalog.get_definition(role)

    rprint(f"[bold green]Agent Blueprint: {defn.display_name} ({defn.role.value})[/bold green]")
    rprint(f"[bold]Purpose:[/bold] {defn.purpose}")
    rprint(f"[bold]Supervisor:[/bold] {defn.supervisor_role.value if defn.supervisor_role else 'SYSTEM/GOVERNANCE'}")
    rprint(f"[bold]Autonomy Mode:[/bold] [magenta]{defn.autonomy_mode.value}[/magenta]")
    rprint(f"[bold]Daily Budget:[/bold] ${defn.daily_budget_usd:.2f} USD")
    rprint(f"[bold]Max Execution SLA:[/bold] {defn.max_execution_time_seconds}s")
    rprint("[bold]Responsibilities:[/bold]")
    for r in defn.responsibilities:
        rprint(f"  • {r}")


@app.command("capabilities")
def inspect_capabilities(
    role: str = typer.Argument(..., help="Specialized Agent Role e.g. PAYROLL_ASSISTANT_AGENT"),
) -> None:
    """List granted and prohibited capabilities for an agent."""
    svc = SpecializedAgentService.get_instance()
    caps = svc.get_capabilities(role)

    rprint(f"[bold]Capabilities for [{role}]:[/bold]")
    rprint("[green]Granted Capabilities:[/green]")
    for c in caps.capabilities:
        rprint(f"  [green]+[/green] {c}")

    rprint("[red]Prohibited Capabilities:[/red]")
    for p in caps.prohibited_capabilities:
        rprint(f"  [red]-[/red] {p}")


@app.command("tools")
def inspect_tools(
    role: str = typer.Argument(..., help="Specialized Agent Role e.g. RECRUITMENT_AGENT"),
) -> None:
    """List tool access policy matrix for an agent."""
    svc = SpecializedAgentService.get_instance()
    tool_pol = svc.get_tool_policy(role)

    table = Table(title=f"Tool Policy for [{role}]")
    table.add_column("Tool ID", style="cyan")
    table.add_column("Access Level", style="bold")

    for tool_id, access in sorted(tool_pol.tool_access.items()):
        color = "green" if access.value == "ALLOW" else ("yellow" if access.value == "REQUIRES_APPROVAL" else "red")
        table.add_row(tool_id, f"[{color}]{access.value}[/{color}]")

    console.print(table)


@app.command("knowledge")
def inspect_knowledge(
    role: str = typer.Argument(..., help="Specialized Agent Role e.g. EMPLOYEE_ASSISTANT_AGENT"),
) -> None:
    """List knowledge scope and confidentiality policies for an agent."""
    svc = SpecializedAgentService.get_instance()
    k_pol = svc.get_knowledge_policy(role)

    rprint(f"[bold]Knowledge Policy for [{role}]:[/bold]")
    rprint(f"  • Max Confidentiality: [yellow]{k_pol.max_classification.value}[/yellow]")
    rprint(f"  • Allowed Scopes: [cyan]{[s.value for s in k_pol.allowed_scopes]}[/cyan]")
    rprint(f"  • Prohibited Scopes: [red]{[p.value for p in k_pol.prohibited_scopes]}[/red]")


@app.command("evaluation")
def inspect_evaluation(
    role: str = typer.Argument(..., help="Specialized Agent Role e.g. ATTRITION_AGENT"),
) -> None:
    """List evaluation contract criteria for an agent."""
    svc = SpecializedAgentService.get_instance()
    eval_c = svc.get_evaluation_contract(role)

    rprint(f"[bold]Evaluation Contract for [{role}]:[/bold]")
    rprint(f"  • Metric: [cyan]{eval_c.accuracy_metric}[/cyan] (Min: {eval_c.min_accuracy_score})")
    rprint(f"  • Max Hallucination Rate: [yellow]{eval_c.max_hallucination_rate * 100}%[/yellow]")
    rprint(f"  • Unauthorized Retrievals Allowed: [red]{eval_c.unauthorized_retrieval_limit}[/red]")
    rprint(f"  • Target SLA: [green]{eval_c.target_sla_seconds}s[/green]")
    rprint("  • Criteria:")
    for crit in eval_c.evaluation_criteria:
        rprint(f"    - {crit}")
