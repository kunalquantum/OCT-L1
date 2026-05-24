"""Tests for the consensus engine and orchestrator."""

import pytest

from cephmind.agents import DEFAULT_AGENTS
from cephmind.core.consensus import build_consensus
from cephmind.core.models import AgentVerdict, Query, Stance
from cephmind.core.orchestrator import CephMindOrchestrator


def _verdict(name: str, stance: Stance, confidence: float, blockers=None) -> AgentVerdict:
    return AgentVerdict(
        agent_name=name,
        stance=stance,
        confidence=confidence,
        summary=f"{name} says {stance.value}",
        blockers=blockers or [],
    )


class TestBuildConsensus:
    def test_unanimous_proceed(self):
        verdicts = [
            _verdict("A", Stance.PROCEED, 0.80),
            _verdict("B", Stance.PROCEED, 0.85),
            _verdict("C", Stance.PROCEED, 0.75),
        ]
        result, reliability = build_consensus(verdicts)
        assert result.overall_stance == Stance.PROCEED
        assert reliability > 0.50

    def test_single_block_escalates(self):
        verdicts = [
            _verdict("A", Stance.PROCEED, 0.80),
            _verdict("B", Stance.PROCEED, 0.75),
            _verdict("C", Stance.BLOCK, 0.85, ["Critical issue"]),
        ]
        result, _ = build_consensus(verdicts)
        assert result.overall_stance in (Stance.DELAY, Stance.BLOCK)

    def test_many_blockers_penalise_confidence(self):
        verdicts = [
            _verdict("A", Stance.DELAY, 0.80, ["blocker 1"]),
            _verdict("B", Stance.DELAY, 0.78, ["blocker 2"]),
            _verdict("C", Stance.PROCEED, 0.70),
        ]
        result, _ = build_consensus(verdicts)
        assert result.confidence_score < 0.80

    def test_blockers_deduplicated(self):
        verdicts = [
            _verdict("A", Stance.DELAY, 0.80, ["same blocker"]),
            _verdict("B", Stance.DELAY, 0.78, ["same blocker"]),
        ]
        result, _ = build_consensus(verdicts)
        assert result.major_blockers.count("same blocker") == 1

    def test_empty_verdicts_raises(self):
        with pytest.raises(ValueError):
            build_consensus([])

    def test_reliability_bounded(self):
        verdicts = [
            _verdict("A", Stance.PROCEED, 0.90),
            _verdict("B", Stance.BLOCK, 0.90),
        ]
        _, reliability = build_consensus(verdicts)
        assert 0.0 <= reliability <= 1.0


class TestOrchestrator:
    def test_full_pipeline_returns_result(self):
        orch = CephMindOrchestrator(DEFAULT_AGENTS)
        q = Query(
            "Should this Oracle ERP migration proceed? "
            "We have UAT complete, rollback plan in place, budget approved, and GDPR compliant."
        )
        result = orch.reason(q)
        assert result.query is q
        assert len(result.verdicts) == len(DEFAULT_AGENTS)
        assert result.consensus is not None
        assert 0.0 <= result.reliability_score <= 1.0

    def test_verdicts_sorted_by_name(self):
        orch = CephMindOrchestrator(DEFAULT_AGENTS)
        q = Query("Simple test query.")
        result = orch.reason(q)
        names = [v.agent_name for v in result.verdicts]
        assert names == sorted(names)

    def test_summary_table_contains_all_agents(self):
        orch = CephMindOrchestrator(DEFAULT_AGENTS)
        q = Query("Test.")
        result = orch.reason(q)
        table = result.summary_table()
        for v in result.verdicts:
            assert v.agent_name in table

    def test_failed_agent_degrades_gracefully(self):
        from cephmind.core.base_agent import BaseAgent

        class BrokenAgent(BaseAgent):
            @property
            def name(self):
                return "Broken Agent"

            def analyze(self, query):
                raise RuntimeError("Simulated failure")

        orch = CephMindOrchestrator([BrokenAgent()])
        result = orch.reason(Query("test"))
        assert len(result.verdicts) == 1
        assert result.verdicts[0].confidence == 0.10

    def test_requires_at_least_one_agent(self):
        with pytest.raises(ValueError):
            CephMindOrchestrator([])
