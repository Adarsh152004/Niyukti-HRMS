"""
Tool Execution Gateway — Executes LLM Tool Proposals strictly via AgentCommandGateway -> CommandBus.
"""

from __future__ import annotations

from backend.agents.application.command_gateway import AgentCommandGateway
from backend.agents.domain.exceptions import AgentCapabilityError, AgentSecurityError
from backend.agents.domain.models import Agent, AgentExecutionContext
from backend.agents.tools.application.tool_registry import ToolRegistry
from backend.agents.tools.domain.exceptions import ToolAccessDeniedError
from backend.agents.tools.domain.models import ToolExecutionResult, ToolProposal
from backend.commands.domain.enums import CommandStatus
from backend.hrms.domain.actor import Actor


class ToolExecutionGateway:
    """
    Gateway converting ToolProposals into CommandBus dispatches via AgentCommandGateway.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        command_gateway: AgentCommandGateway | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry.get_instance()
        self.command_gateway = command_gateway or AgentCommandGateway()

    async def execute_proposal(
        self,
        agent: Agent,
        context: AgentExecutionContext,
        proposal: ToolProposal,
        actor: Actor | None = None,
    ) -> ToolExecutionResult:
        """
        Validate ToolProposal against ToolRegistry and Agent capabilities,
        then dispatch via AgentCommandGateway -> CommandBus pipeline.
        """
        # 1. Fetch ToolDefinition
        tool = self.registry.get_tool(proposal.tool_id)

        # 2. Verify Capability Match
        if not agent.has_capability(tool.resource, tool.action):
            raise ToolAccessDeniedError(
                f"Agent '{agent.name}' lacks capability for tool '{tool.tool_id}' ({tool.resource}:{tool.action})."
            )

        try:
            # 3. Request Action via AgentCommandGateway -> CommandBus
            cmd_result = await self.command_gateway.request_action(
                agent=agent,
                context=context,
                resource=tool.resource,
                action=tool.action,
                command_type=tool.command_type,
                payload=proposal.arguments,
                actor=actor,
            )

            status_str = cmd_result.status.value
            return ToolExecutionResult(
                proposal_id=proposal.proposal_id,
                tool_id=proposal.tool_id,
                status=status_str,
                data=cmd_result.result_data,
                error=cmd_result.error_message,
            )
        except (AgentSecurityError, AgentCapabilityError) as e:
            return ToolExecutionResult(
                proposal_id=proposal.proposal_id,
                tool_id=proposal.tool_id,
                status=CommandStatus.FAILED.value,
                data={},
                error=str(e),
            )
