"""
Autonomous Recruitment Team — Coordinates job posting, candidate sourcing, resume screening, ranking, and interview intelligence.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.agents.operations.teams.base_team import MultiAgentTeam
from backend.agents.specialized.domain.enums import SpecializedAgentRole

logger = logging.getLogger(__name__)


class AutonomousRecruitmentTeam(MultiAgentTeam):
    """
    Recruitment Team composed of:
    - Supervisor: RECRUITMENT_AGENT
    - Workers: RESUME_SCREENING_AGENT, CANDIDATE_RANKING_AGENT, INTERVIEW_INTELLIGENCE_AGENT, ONBOARDING_AGENT
    """

    def __init__(self, organization_id: str) -> None:
        super().__init__(
            organization_id=organization_id,
            supervisor_role=SpecializedAgentRole.RECRUITMENT_AGENT,
            worker_roles=[
                SpecializedAgentRole.RESUME_SCREENING_AGENT,
                SpecializedAgentRole.CANDIDATE_RANKING_AGENT,
                SpecializedAgentRole.INTERVIEW_INTELLIGENCE_AGENT,
                SpecializedAgentRole.ONBOARDING_AGENT,
            ],
        )

    async def execute_team_operation(self, operation_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Coordinate multi-agent candidate screening & ranking pipeline."""
        if operation_name == "screen_and_rank_candidates":
            job_id = parameters.get("job_id", "job-default")
            candidates = parameters.get("candidates", [])

            # 1. Supervisor delegates screening
            screen_msg = await self.delegate_task_to_worker(
                worker_role=SpecializedAgentRole.RESUME_SCREENING_AGENT,
                task_name="screen_resumes",
                payload={"job_id": job_id, "count": len(candidates)},
            )

            # 2. Supervisor delegates ranking
            rank_msg = await self.delegate_task_to_worker(
                worker_role=SpecializedAgentRole.CANDIDATE_RANKING_AGENT,
                task_name="rank_candidates",
                payload={"job_id": job_id, "candidates": candidates},
            )

            return {
                "operation": operation_name,
                "job_id": job_id,
                "status": "COMPLETED",
                "screening_message_id": screen_msg.message_id,
                "ranking_message_id": rank_msg.message_id,
                "top_candidates": candidates[:3],
            }

        return {"operation": operation_name, "status": "UNKNOWN_OPERATION"}
