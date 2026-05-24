"""Shared data models for CephMind agents and orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Confidence(float, Enum):
    """Canonical confidence bands used across the system."""
    VERY_LOW = 0.20
    LOW = 0.40
    MODERATE = 0.60
    HIGH = 0.75
    VERY_HIGH = 0.90


class Stance(str, Enum):
    PROCEED = "PROCEED"
    CAUTION = "CAUTION"
    DELAY = "DELAY"
    BLOCK = "BLOCK"


@dataclass
class Query:
    """Input submitted to CephMind for distributed reasoning."""
    text: str
    domain: str = "general"
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentVerdict:
    """A single agent's structured output."""
    agent_name: str
    stance: Stance
    confidence: float          # 0.0 – 1.0
    summary: str
    findings: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsensusResult:
    """Aggregated output from the Consensus Engine."""
    overall_stance: Stance
    confidence_score: float    # 0.0 – 1.0
    recommendation: str
    key_findings: list[str] = field(default_factory=list)
    major_blockers: list[str] = field(default_factory=list)
    dissenting_agents: list[str] = field(default_factory=list)


@dataclass
class ReasoningResult:
    """Full pipeline output returned to the caller."""
    query: Query
    verdicts: list[AgentVerdict]
    consensus: ConsensusResult
    reliability_score: float   # 0.0 – 1.0; agreement-weighted

    def summary_table(self) -> str:
        """Human-readable ASCII summary."""
        lines = [
            "=" * 62,
            f"  CephMind Reasoning Report",
            f"  Query : {self.query.text[:55]}{'…' if len(self.query.text) > 55 else ''}",
            "=" * 62,
        ]
        lines.append(f"{'Agent':<25} {'Stance':<10} {'Conf':>6}")
        lines.append("-" * 45)
        for v in self.verdicts:
            lines.append(f"{v.agent_name:<25} {v.stance.value:<10} {v.confidence:>5.0%}")
        lines.append("-" * 45)
        lines.append(
            f"\n  Consensus     : {self.consensus.overall_stance.value}"
        )
        lines.append(f"  Confidence    : {self.consensus.confidence_score:.0%}")
        lines.append(f"  Reliability   : {self.reliability_score:.0%}")
        lines.append(f"\n  Recommendation: {self.consensus.recommendation}")
        if self.consensus.major_blockers:
            lines.append("\n  Blockers:")
            for b in self.consensus.major_blockers:
                lines.append(f"    • {b}")
        lines.append("=" * 62)
        return "\n".join(lines)
