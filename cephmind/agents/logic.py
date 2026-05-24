"""Logic Agent — checks internal consistency and structural feasibility."""

from __future__ import annotations

import re

from ..core.base_agent import BaseAgent
from ..core.models import AgentVerdict, Query, Stance

# Signal words that suggest logical structure is present
_POSITIVE_SIGNALS = re.compile(
    r"\b(plan|strategy|roadmap|process|phase|step|objective|goal|requirement"
    r"|architecture|design|schedule|milestone)\b",
    re.IGNORECASE,
)

# Words that suggest the request is underspecified
_VAGUE_SIGNALS = re.compile(
    r"\b(maybe|perhaps|might|possibly|unclear|unsure|not sure|don'?t know"
    r"|undefined|TBD|TBC|unknown)\b",
    re.IGNORECASE,
)

# Contradiction markers
_CONTRADICTION_SIGNALS = re.compile(
    r"\b(but|however|although|yet|despite|conflict|contradict|inconsistent)\b",
    re.IGNORECASE,
)


class LogicAgent(BaseAgent):
    """Evaluates whether the request is internally coherent and structurally sound."""

    @property
    def name(self) -> str:
        return "Logic Agent"

    def analyze(self, query: Query) -> AgentVerdict:
        text = query.text

        positive_hits = len(_POSITIVE_SIGNALS.findall(text))
        vague_hits = len(_VAGUE_SIGNALS.findall(text))
        contradiction_hits = len(_CONTRADICTION_SIGNALS.findall(text))

        findings: list[str] = []
        blockers: list[str] = []

        if positive_hits >= 2:
            findings.append(f"Structured intent detected ({positive_hits} planning signals).")
        if vague_hits > 0:
            findings.append(f"{vague_hits} vague/undefined term(s) found.")
        if contradiction_hits > 0:
            findings.append(f"{contradiction_hits} potential contradiction marker(s) detected.")

        # Scoring
        clarity_score = max(0, positive_hits * 0.15 - vague_hits * 0.20)
        contradiction_penalty = contradiction_hits * 0.10

        confidence = min(0.90, max(0.30, 0.60 + clarity_score - contradiction_penalty))

        if contradiction_hits >= 2:
            stance = Stance.DELAY
            blockers.append("Multiple contradictions weaken logical coherence.")
        elif vague_hits >= 3:
            stance = Stance.CAUTION
        elif confidence >= 0.65:
            stance = Stance.PROCEED
        else:
            stance = Stance.CAUTION

        summary = (
            "Logic is coherent and well-structured."
            if stance == Stance.PROCEED
            else "Logical gaps or contradictions require clarification."
        )

        return AgentVerdict(
            agent_name=self.name,
            stance=stance,
            confidence=round(confidence, 3),
            summary=summary,
            findings=findings,
            blockers=blockers,
        )
