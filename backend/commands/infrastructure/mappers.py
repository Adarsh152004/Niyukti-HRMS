"""
Command Domain ↕ Database Mappers.
"""

from __future__ import annotations

from datetime import UTC, datetime

from backend.commands.domain.enums import CommandChannel, CommandStatus
from backend.commands.domain.models import Command
from backend.commands.infrastructure.models import CommandModel


class CommandMapper:
    @staticmethod
    def to_domain(model: CommandModel) -> Command:
        now = datetime.now(tz=UTC)
        return Command(
            command_id=model.id,
            command_type=model.command_type,
            actor_id=model.actor_id,
            organization_id=model.organization_id,
            channel=CommandChannel(model.channel),
            request_id=model.request_id,
            correlation_id=model.correlation_id,
            created_at=model.created_at or now,
            payload=model.payload_json or {},
            status=CommandStatus(model.status),
            idempotency_key=model.idempotency_key,
            payload_hash=model.payload_hash,
        )

    @staticmethod
    def to_model(domain: Command) -> CommandModel:
        return CommandModel(
            id=domain.command_id,
            organization_id=domain.organization_id,
            command_type=domain.command_type,
            actor_id=domain.actor_id,
            channel=domain.channel.value,
            payload_json=domain.payload,
            payload_hash=domain.payload_hash,
            status=domain.status.value,
            idempotency_key=domain.idempotency_key,
            request_id=domain.request_id,
            correlation_id=domain.correlation_id,
        )
