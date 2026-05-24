"""Abstract base class every CephMind agent must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import AgentVerdict, Query


class BaseAgent(ABC):
    """Contract all reasoning agents must satisfy."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique, human-readable agent identifier."""

    @abstractmethod
    def analyze(self, query: Query) -> AgentVerdict:
        """
        Analyse the query and return a structured verdict.

        Implementations must:
        - Be deterministic for identical inputs (no random state).
        - Set confidence proportional to evidence strength.
        - Populate blockers only when stance is DELAY or BLOCK.
        """
