"""Consensus + Confidence Engine — aggregates agent verdicts into one result."""

from __future__ import annotations

from collections import Counter
from statistics import mean, stdev

from .models import AgentVerdict, ConsensusResult, Stance


# Weight applied when ≥50% agents flag a blocker
_BLOCKER_CONFIDENCE_PENALTY = 0.10

# Minimum agreement fraction to call consensus HIGH
_HIGH_AGREEMENT_THRESHOLD = 0.70


def build_consensus(verdicts: list[AgentVerdict]) -> tuple[ConsensusResult, float]:
    """
    Return (ConsensusResult, reliability_score).

    reliability_score reflects inter-agent agreement; low agreement → low score
    even if individual confidence values are high.
    """
    if not verdicts:
        raise ValueError("Cannot build consensus from an empty verdict list.")

    stance_votes = [v.stance for v in verdicts]
    vote_counts: Counter[Stance] = Counter(stance_votes)
    dominant_stance, dominant_count = vote_counts.most_common(1)[0]
    agreement_ratio = dominant_count / len(verdicts)

    all_confidences = [v.confidence for v in verdicts]
    mean_confidence = mean(all_confidences)

    # Agreement penalty: low agreement → lower effective confidence
    adjusted_confidence = mean_confidence * (0.50 + 0.50 * agreement_ratio)

    # Collect blockers only from agents taking a hard stance
    hard_stances = {Stance.DELAY, Stance.BLOCK}
    blockers: list[str] = []
    for v in verdicts:
        if v.stance in hard_stances:
            blockers.extend(v.blockers)

    # Penalise confidence when many blockers exist
    blocker_penalty = _BLOCKER_CONFIDENCE_PENALTY if len(blockers) >= 2 else 0.0
    adjusted_confidence = max(0.0, adjusted_confidence - blocker_penalty)

    # Escalate stance if any agent found a BLOCK condition
    if vote_counts.get(Stance.BLOCK, 0) >= 1:
        final_stance = Stance.BLOCK if dominant_stance == Stance.BLOCK else Stance.DELAY
    else:
        final_stance = dominant_stance

    # Dissent: agents whose stance differs from the dominant
    dissenters = [
        v.agent_name for v in verdicts if v.stance != dominant_stance
    ]

    # Key findings from all agents
    key_findings = [v.summary for v in verdicts]

    recommendation = _build_recommendation(
        final_stance, adjusted_confidence, blockers
    )

    # Reliability: penalise high variance in confidence scores
    conf_spread = stdev(all_confidences) if len(all_confidences) > 1 else 0.0
    reliability = max(0.0, agreement_ratio - conf_spread * 0.5)

    consensus = ConsensusResult(
        overall_stance=final_stance,
        confidence_score=round(adjusted_confidence, 4),
        recommendation=recommendation,
        key_findings=key_findings,
        major_blockers=list(dict.fromkeys(blockers)),  # deduplicated, ordered
        dissenting_agents=dissenters,
    )
    return consensus, round(reliability, 4)


def _build_recommendation(
    stance: Stance, confidence: float, blockers: list[str]
) -> str:
    if stance == Stance.PROCEED and confidence >= 0.70:
        return "Proceed — agents are aligned and confidence is sufficient."
    if stance == Stance.PROCEED:
        return "Proceed with caution — moderate confidence, monitor closely."
    if stance == Stance.CAUTION:
        return "Proceed with caution — address flagged concerns before full rollout."
    if stance == Stance.DELAY:
        blocker_hint = f" Resolve: {blockers[0]}." if blockers else ""
        return f"Delay recommended — significant risks identified.{blocker_hint}"
    # BLOCK
    return "Do not proceed — critical blockers must be resolved first."
