"""
CephMindOrchestrator — coordinates all reasoning agents and returns a
unified ReasoningResult with confidence and reliability scores.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Sequence

from .base_agent import BaseAgent
from .consensus import build_consensus
from .models import AgentVerdict, Query, ReasoningResult


class CephMindOrchestrator:
    """
    Entry point for CephMind distributed reasoning.

    Usage::

        from cephmind import CephMindOrchestrator, Query
        from cephmind.agents import DEFAULT_AGENTS

        orchestrator = CephMindOrchestrator(DEFAULT_AGENTS)
        result = orchestrator.reason(Query("Should we migrate to cloud ERP?"))
        print(result.summary_table())
    """

    def __init__(
        self,
        agents: Sequence[BaseAgent],
        *,
        max_workers: int = 6,
    ) -> None:
        if not agents:
            raise ValueError("At least one agent is required.")
        self._agents = list(agents)
        self._max_workers = max_workers

    def reason(self, query: Query) -> ReasoningResult:
        """Run all agents in parallel and return the aggregated result."""
        verdicts = self._gather_verdicts(query)
        consensus, reliability = build_consensus(verdicts)
        return ReasoningResult(
            query=query,
            verdicts=verdicts,
            consensus=consensus,
            reliability_score=reliability,
        )

    def _gather_verdicts(self, query: Query) -> list[AgentVerdict]:
        verdicts: list[AgentVerdict] = []
        with ThreadPoolExecutor(max_workers=self._max_workers) as pool:
            futures = {pool.submit(agent.analyze, query): agent for agent in self._agents}
            for future in as_completed(futures):
                agent = futures[future]
                try:
                    verdicts.append(future.result())
                except Exception as exc:  # noqa: BLE001
                    # Degraded-mode: record a low-confidence CAUTION rather than crash
                    from .models import AgentVerdict, Stance
                    verdicts.append(AgentVerdict(
                        agent_name=agent.name,
                        stance=Stance.CAUTION,
                        confidence=0.10,
                        summary=f"Agent failed to analyse query: {exc}",
                    ))
        # Stable ordering by agent name for reproducible output
        verdicts.sort(key=lambda v: v.agent_name)
        return verdicts
