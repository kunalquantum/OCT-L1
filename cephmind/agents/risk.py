"""Risk Agent — identifies operational, technical, and strategic risks."""

from __future__ import annotations

import re

from ..core.base_agent import BaseAgent
from ..core.models import AgentVerdict, Query, Stance

_HIGH_RISK_TERMS = re.compile(
    r"\b(migration|cutover|legacy|critical|production|downtime|deadline|deadline"
    r"|irreversible|data loss|outage|failure|breach|dependency|vendor lock"
    r"|single point|SPOF|rollback|untested|prototype)\b",
    re.IGNORECASE,
)

_MITIGATING_TERMS = re.compile(
    r"\b(backup|rollback plan|tested|staging|pilot|DR|disaster recovery"
    r"|redundan|failover|monitor|alert|review|audit|checkpoint)\b",
    re.IGNORECASE,
)


class RiskAgent(BaseAgent):
    """Scans for operational, technical, and strategic risk signals."""

    @property
    def name(self) -> str:
        return "Risk Agent"

    def analyze(self, query: Query) -> AgentVerdict:
        text = query.text

        risk_hits = _HIGH_RISK_TERMS.findall(text)
        mitigation_hits = _MITIGATING_TERMS.findall(text)

        risk_count = len(risk_hits)
        mitigation_count = len(mitigation_hits)
        net_risk = risk_count - mitigation_count

        findings: list[str] = []
        blockers: list[str] = []

        if risk_count > 0:
            findings.append(f"{risk_count} risk signal(s) detected: {', '.join(set(risk_hits[:4]))}.")
        if mitigation_count > 0:
            findings.append(f"{mitigation_count} mitigation signal(s) present.")

        if net_risk >= 4:
            stance = Stance.BLOCK
            confidence = 0.85
            blockers.append(f"High unmitigated risk count ({net_risk} net risk signals).")
            if "migration" in text.lower():
                blockers.append("Migration without documented rollback plan.")
        elif net_risk >= 2:
            stance = Stance.DELAY
            confidence = 0.75
            blockers.append(f"Unmitigated risks need remediation plan ({net_risk} net signals).")
        elif net_risk >= 1:
            stance = Stance.CAUTION
            confidence = 0.65
        else:
            stance = Stance.PROCEED
            confidence = 0.78

        summary = (
            f"Elevated risk profile — {net_risk} unmitigated risk(s)."
            if net_risk > 0
            else "Risk profile acceptable; adequate mitigations referenced."
        )

        return AgentVerdict(
            agent_name=self.name,
            stance=stance,
            confidence=round(confidence, 3),
            summary=summary,
            findings=findings,
            blockers=blockers,
        )
