"""Domain Expert Agent — validates domain-specific terminology and best practices."""

from __future__ import annotations

import re
from typing import NamedTuple

from ..core.base_agent import BaseAgent
from ..core.models import AgentVerdict, Query, Stance


class _DomainProfile(NamedTuple):
    keywords: re.Pattern[str]
    best_practice_signals: re.Pattern[str]
    concern_signals: re.Pattern[str]


_DOMAIN_PROFILES: dict[str, _DomainProfile] = {
    "erp": _DomainProfile(
        keywords=re.compile(
            r"\b(ERP|Oracle|SAP|Dynamics|Workday|cutover|UAT|go-live|data migration"
            r"|chart of accounts|GL|AP|AR|procurement|FICO|HCM)\b",
            re.IGNORECASE,
        ),
        best_practice_signals=re.compile(
            r"\b(UAT|user acceptance|parallel run|data cleansing|change management"
            r"|training|cutover plan|sign-off|hypercare|SIT)\b",
            re.IGNORECASE,
        ),
        concern_signals=re.compile(
            r"\b(skip.*test|no.*UAT|rush|compress.*timeline|skip.*training"
            r"|manual.*data|no.*backup|live.*without.*test)\b",
            re.IGNORECASE,
        ),
    ),
    "cloud": _DomainProfile(
        keywords=re.compile(
            r"\b(cloud|AWS|Azure|GCP|kubernetes|container|microservice|serverless"
            r"|IaaS|PaaS|SaaS|VPC|subnet|IAM|S3|blob|lift.and.shift)\b",
            re.IGNORECASE,
        ),
        best_practice_signals=re.compile(
            r"\b(IaC|terraform|ansible|CI/CD|blue.green|canary|WAF|least privilege"
            r"|encryption|backup|DR|monitoring|alerting)\b",
            re.IGNORECASE,
        ),
        concern_signals=re.compile(
            r"\b(no.*encryption|public.*bucket|root.*account|no.*MFA|hardcoded"
            r"|no.*monitoring|shadow IT)\b",
            re.IGNORECASE,
        ),
    ),
    "finance": _DomainProfile(
        keywords=re.compile(
            r"\b(budget|capex|opex|ROI|TCO|NPV|IRR|cost.*benefit|audit|GAAP|IFRS"
            r"|revenue|P&L|cash flow|fiscal)\b",
            re.IGNORECASE,
        ),
        best_practice_signals=re.compile(
            r"\b(business case|cost model|sensitivity analysis|approval|sign-off"
            r"|budget.*approved|financial.*review|controller|CFO)\b",
            re.IGNORECASE,
        ),
        concern_signals=re.compile(
            r"\b(no.*budget|over.*budget|undefined.*cost|no.*approval|unapproved"
            r"|cost.*unknown|spend.*uncontrolled)\b",
            re.IGNORECASE,
        ),
    ),
    "general": _DomainProfile(
        keywords=re.compile(r".+", re.IGNORECASE),
        best_practice_signals=re.compile(
            r"\b(plan|document|review|test|validate|approve|monitor|measure)\b",
            re.IGNORECASE,
        ),
        concern_signals=re.compile(
            r"\b(skip|rush|ignore|bypass|no plan|undocumented|ad.hoc)\b",
            re.IGNORECASE,
        ),
    ),
}


def _detect_domain(text: str, hint: str) -> str:
    """Infer the most relevant domain from hint or query text."""
    hint_lower = hint.lower()
    for domain in ("erp", "cloud", "finance"):
        if domain in hint_lower:
            return domain
        profile = _DOMAIN_PROFILES[domain]
        if profile.keywords.search(text):
            return domain
    return "general"


class DomainExpertAgent(BaseAgent):
    """Assesses alignment with domain-specific terminology and best practices."""

    @property
    def name(self) -> str:
        return "Domain Expert Agent"

    def analyze(self, query: Query) -> AgentVerdict:
        domain = _detect_domain(query.text, query.domain)
        profile = _DOMAIN_PROFILES[domain]

        kw_hits = len(profile.keywords.findall(query.text))
        bp_hits = len(profile.best_practice_signals.findall(query.text))
        concern_hits = len(profile.concern_signals.findall(query.text))

        findings: list[str] = [f"Domain inferred: {domain.upper()}."]
        blockers: list[str] = []

        if kw_hits > 0:
            findings.append(f"{kw_hits} domain keyword(s) recognised.")
        if bp_hits > 0:
            findings.append(f"{bp_hits} best-practice signal(s) present.")
        if concern_hits > 0:
            findings.append(f"{concern_hits} domain-concern signal(s) detected.")

        # Score
        base = 0.50 + bp_hits * 0.08 - concern_hits * 0.15
        confidence = min(0.92, max(0.25, base))

        if concern_hits >= 2:
            stance = Stance.BLOCK
            blockers.append(f"Domain best-practice violations detected ({concern_hits}).")
        elif concern_hits == 1:
            stance = Stance.DELAY
            blockers.append("At least one domain best-practice concern requires resolution.")
        elif bp_hits >= 2:
            stance = Stance.PROCEED
        else:
            stance = Stance.CAUTION

        summary = (
            f"Domain ({domain.upper()}) requirements appear satisfied."
            if stance in (Stance.PROCEED, Stance.CAUTION)
            else f"Domain ({domain.upper()}) best-practice gaps identified."
        )

        return AgentVerdict(
            agent_name=self.name,
            stance=stance,
            confidence=round(confidence, 3),
            summary=summary,
            findings=findings,
            blockers=blockers,
            metadata={"detected_domain": domain},
        )
