"""
AI-Powered Intelligent HRMS — Cryptographic Hash-Chain Tamper-Evident Audit Trail.

Features:
- Immutable SHA-256 blockchain-style chaining:
    Hash_i = SHA-256(EventData_i || Hash_{i-1})
- Continuous tamper-verification algorithm
- Cryptographic proof generation
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ChainedAuditEvent:
    index: int
    event_id: str
    timestamp: str
    actor: str
    action: str
    target: str
    risk_level: str
    payload: dict[str, Any]
    prev_hash: str
    current_hash: str = ""

    def compute_hash(self) -> str:
        """Computes the deterministic SHA-256 hash of this block chained to prev_hash."""
        content = {
            "index": self.index,
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "target": self.target,
            "risk_level": self.risk_level,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
        }
        encoded = json.dumps(content, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


class CryptographicAuditLedger:
    """Append-only tamper-evident cryptographic audit ledger."""

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self) -> None:
        self._chain: list[ChainedAuditEvent] = []

    @property
    def chain(self) -> list[ChainedAuditEvent]:
        return list(self._chain)

    def append_event(
        self,
        event_id: str,
        actor: str,
        action: str,
        target: str,
        risk_level: str = "LOW",
        payload: dict[str, Any] | None = None,
    ) -> ChainedAuditEvent:
        """Appends a new event block, cryptographically chained to the latest block."""
        prev_hash = self._chain[-1].current_hash if self._chain else self.GENESIS_HASH
        index = len(self._chain)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

        event = ChainedAuditEvent(
            index=index,
            event_id=event_id,
            timestamp=timestamp,
            actor=actor,
            action=action,
            target=target,
            risk_level=risk_level,
            payload=payload or {},
            prev_hash=prev_hash,
        )
        event.current_hash = event.compute_hash()
        self._chain.append(event)
        return event

    def verify_integrity(self) -> tuple[bool, str]:
        """
        Verifies the cryptographic integrity of the entire chain.
        Returns (is_valid, detail_message).
        """
        if not self._chain:
            return True, "Empty chain is valid."

        for i, event in enumerate(self._chain):
            # 1. Verify block internal hash matches computed hash
            expected_hash = event.compute_hash()
            if event.current_hash != expected_hash:
                return False, f"Tamper detected at block {i} ({event.event_id}): hash mismatch."

            # 2. Verify backward link to previous block
            if i == 0:
                if event.prev_hash != self.GENESIS_HASH:
                    return False, f"Genesis block prev_hash is invalid."
            else:
                prev_event = self._chain[i - 1]
                if event.prev_hash != prev_event.current_hash:
                    return False, f"Broken chain link between block {i-1} and block {i}."

        return True, f"Chain integrity fully verified ({len(self._chain)} blocks intact)."
