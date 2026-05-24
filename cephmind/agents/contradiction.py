"""Contradiction Agent — detects conflicting claims within the query."""

from __future__ import annotations

import re

from ..core.base_agent import BaseAgent
from ..core.models import AgentVerdict, Query, Stance

# Pairs that are logically inconsistent when both appear in the same query
_CONFLICT_PAIRS: list[tuple[re.Pattern[str], re.Pattern[str], str]] = [
    (
        re.compile(r"\b(no downtime|zero downtime|live cutover)\b", re.IGNORECASE),
        re.compile(r"\b(full migration|complete migration|all data)\b", re.IGNORECASE),
        "Claims zero downtime while performing a full migration.",
    ),
    (
        re.compile(r"\b(no.*tests?|skip.*tests?|bypass.*tests?)\b", re.IGNORECASE),
        re.compile(r"\b(production|go-live|live)\b", re.IGNORECASE),
        "Proposes skipping tests before a live deployment.",
    ),
    (
        re.compile(r"\b(no.*budget|undefined.*cost|unknown.*cost)\b", re.IGNORECASE),
        re.compile(r"\b(approve|proceed|sign.?off|go ahead)\b", re.IGNORECASE),
        "Seeks approval without a defined budget.",
    ),
    (
        re.compile(r"\b(urgent|immediate|asap|rush)\b", re.IGNORECASE),
        re.compile(r"\b(thorough|comprehensive|complete|exhaustive)\b", re.IGNORECASE),
        "Urgency conflicts with the claimed thoroughness of the approach.",
    ),
    (
        re.compile(r"\b(manual|ad.hoc|spreadsheet)\b", re.IGNORECASE),
        re.compile(r"\b(scale|enterprise|1000|millions|large.scale)\b", re.IGNORECASE),
        "Manual/ad-hoc approach proposed for an enterprise-scale problem.",
    ),
]


class ContradictionAgent(BaseAgent):
    """Detects logical conflicts between claims made in the same query."""

    @property
    def name(self) -> str:
        return "Contradiction Agent"

    def analyze(self, query: Query) -> AgentVerdict:
        text = query.text
        conflicts: list[str] = []

        for pattern_a, pattern_b, description in _CONFLICT_PAIRS:
            if pattern_a.search(text) and pattern_b.search(text):
                conflicts.append(description)

        findings: list[str] = []
        blockers: list[str] = []

        if conflicts:
            findings = [f"Conflict {i + 1}: {c}" for i, c in enumerate(conflicts)]
        else:
            findings = ["No direct logical contradictions detected."]

        n = len(conflicts)

        if n == 0:
            stance = Stance.PROCEED
            confidence = 0.82
            summary = "No contradictions detected; internal consistency is good."
        elif n == 1:
            stance = Stance.CAUTION
            confidence = 0.68
            summary = "One contradiction detected — review before proceeding."
        elif n == 2:
            stance = Stance.DELAY
            confidence = 0.78
            blockers = conflicts
            summary = f"{n} contradictions undermine decision integrity."
        else:
            stance = Stance.BLOCK
            confidence = 0.85
            blockers = conflicts
            summary = f"{n} contradictions make the proposal internally inconsistent."

        return AgentVerdict(
            agent_name=self.name,
            stance=stance,
            confidence=round(confidence, 3),
            summary=summary,
            findings=findings,
            blockers=blockers,
        )
