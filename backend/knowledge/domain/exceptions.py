"""
Knowledge Domain Exceptions.
"""

from __future__ import annotations


class KnowledgeDomainError(Exception):
    """Base exception for Knowledge Brain domain errors."""

    pass


class KnowledgeDocumentNotFoundError(KnowledgeDomainError):
    """Raised when requested document does not exist."""

    pass


class KnowledgeAccessDeniedError(KnowledgeDomainError):
    """Raised when actor/agent lacks authorization to retrieve or mutate document."""

    pass


class KnowledgeParserError(KnowledgeDomainError):
    """Raised when document content parsing fails."""

    pass


class KnowledgeIngestionError(KnowledgeDomainError):
    """Raised when document ingestion pipeline fails."""

    pass


class KnowledgeExpiredError(KnowledgeDomainError):
    """Raised when attempting to query or publish an expired document."""

    pass
