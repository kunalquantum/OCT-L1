"""Compliance Agent — checks for regulatory and governance requirement signals."""

from __future__ import annotations

import re

from ..core.base_agent import BaseAgent
from ..core.models import AgentVerdict, Query, Stance

_COMPLIANCE_REQUIREMENTS = re.compile(
    r"\b(GDPR|HIPAA|SOX|PCI.?DSS|ISO 27001|NIST|CCPA|FedRAMP|SOC 2|DORA"
    r"|data.*privacy|data.*protection|regulatory|audit.*trail|access.*control"
    r"|segregation.*duties|SoD|encryption.*rest|encryption.*transit)\b",
    re.IGNORECASE,
)

_COMPLIANCE_SATISFIED = re.compile(
    r"\b(compliant|compliance.*reviewed|DPO.*approved|legal.*cleared|audit.*passed"
    r"|controls.*in place|approved.*by.*compliance|privacy.*review|certified)\b",
    re.IGNORECASE,
)

_COMPLIANCE_GAPS = re.compile(
    r"\b(non.compliant|compliance.*gap|missing.*control|no.*audit|bypass.*control"
    r"|no.*encryption|no.*access.*control|no.*SoD|no.*logging|no.*MFA"
    r"|compliance.*waiver|exception.*requested)\b",
    re.IGNORECASE,
)


class ComplianceAgent(BaseAgent):
    """Identifies regulatory obligations and checks whether controls are addressed."""

    @property
    def name(self) -> str:
        return "Compliance Agent"

    def analyze(self, query: Query) -> AgentVerdict:
        text = query.text

        requirement_hits = len(_COMPLIANCE_REQUIREMENTS.findall(text))
        satisfied_hits = len(_COMPLIANCE_SATISFIED.findall(text))
        gap_hits = len(_COMPLIANCE_GAPS.findall(text))

        findings: list[str] = []
        blockers: list[str] = []

        if requirement_hits:
            findings.append(f"{requirement_hits} compliance obligation(s) referenced.")
        if satisfied_hits:
            findings.append(f"{satisfied_hits} compliance satisfaction signal(s) present.")
        if gap_hits:
            findings.append(f"{gap_hits} compliance gap signal(s) detected.")

        # If no compliance signals at all — neutral CAUTION (we can't verify)
        if requirement_hits == 0 and gap_hits == 0:
            return AgentVerdict(
                agent_name=self.name,
                stance=Stance.CAUTION,
                confidence=0.55,
                summary="No compliance requirements referenced; manual review recommended.",
                findings=["No regulatory signals found in query."],
            )

        net_gap = gap_hits + max(0, requirement_hits - satisfied_hits)

        if net_gap >= 3:
            stance = Stance.BLOCK
            confidence = 0.88
            blockers.append("Critical compliance controls missing — regulatory exposure is high.")
        elif net_gap >= 2:
            stance = Stance.DELAY
            confidence = 0.78
            blockers.append("Compliance gaps require remediation before proceeding.")
        elif net_gap == 1:
            stance = Stance.CAUTION
            confidence = 0.66
        else:
            stance = Stance.PROCEED
            confidence = 0.80

        summary = (
            "Compliance requirements appear addressed."
            if stance == Stance.PROCEED
            else f"Compliance gaps detected — {net_gap} unresolved obligation(s)."
        )

        return AgentVerdict(
            agent_name=self.name,
            stance=stance,
            confidence=round(confidence, 3),
            summary=summary,
            findings=findings,
            blockers=blockers,
        )
