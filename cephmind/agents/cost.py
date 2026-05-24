"""Cost Agent — evaluates budget exposure and financial risk signals."""

from __future__ import annotations

import re

from ..core.base_agent import BaseAgent
from ..core.models import AgentVerdict, Query, Stance

_OVERRUN_SIGNALS = re.compile(
    r"\b(over budget|budget.*exceed|cost.*overrun|unplanned.*cost|cost.*unknown"
    r"|no.*budget|undefined.*budget|cost.*unclear|hidden.*cost|scope creep)\b",
    re.IGNORECASE,
)

_POSITIVE_FINANCIAL_SIGNALS = re.compile(
    r"\b(ROI|business case|cost.benefit|NPV|fixed.*price"
    r"|TCO|financial model|cost model|contingency"
    r"|budget approved|approved budget)\b",
    re.IGNORECASE,
)

# Negation guard: exclude "no/not approved budget" from counting as positive
_NEGATED_APPROVAL = re.compile(r"\bno\s+approved\s+budget\b", re.IGNORECASE)

_LARGE_SPEND_SIGNALS = re.compile(
    r"\$[\d,]+[kKmMbB]?|\b\d+\s*(million|billion|thousand)\b|\blarge.*investment\b",
    re.IGNORECASE,
)


class CostAgent(BaseAgent):
    """Assesses financial risk, budget alignment, and return-on-investment clarity."""

    @property
    def name(self) -> str:
        return "Cost Agent"

    def analyze(self, query: Query) -> AgentVerdict:
        text = query.text

        overrun_hits = len(_OVERRUN_SIGNALS.findall(text))
        raw_positive = len(_POSITIVE_FINANCIAL_SIGNALS.findall(text))
        negation_hits = len(_NEGATED_APPROVAL.findall(text))
        positive_hits = max(0, raw_positive - negation_hits)
        large_spend = bool(_LARGE_SPEND_SIGNALS.search(text))

        findings: list[str] = []
        blockers: list[str] = []

        if overrun_hits:
            findings.append(f"{overrun_hits} budget-risk signal(s) detected.")
        if positive_hits:
            findings.append(f"{positive_hits} positive financial governance signal(s).")
        if large_spend:
            findings.append("Significant spend referenced — heightened financial scrutiny warranted.")

        net_financial_risk = overrun_hits - positive_hits + (1 if large_spend else 0)

        if net_financial_risk >= 3:
            stance = Stance.BLOCK
            confidence = 0.82
            blockers.append("Severe budget exposure with no financial governance evidence.")
        elif net_financial_risk >= 2:
            stance = Stance.DELAY
            confidence = 0.74
            blockers.append("Budget overrun risk requires financial review before proceeding.")
        elif net_financial_risk >= 1:
            stance = Stance.CAUTION
            confidence = 0.64
        else:
            stance = Stance.PROCEED
            confidence = 0.76

        summary = (
            f"Financial risk elevated — {net_financial_risk} net risk indicator(s)."
            if net_financial_risk > 0
            else "Financial signals appear adequate; no budget overrun risk detected."
        )

        return AgentVerdict(
            agent_name=self.name,
            stance=stance,
            confidence=round(confidence, 3),
            summary=summary,
            findings=findings,
            blockers=blockers,
        )
