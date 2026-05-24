"""Unit tests for individual CephMind agents."""

import pytest

from cephmind.agents import (
    ComplianceAgent,
    ContradictionAgent,
    CostAgent,
    DomainExpertAgent,
    LogicAgent,
    RiskAgent,
)
from cephmind.core.models import Query, Stance


# ---------------------------------------------------------------------------
# LogicAgent
# ---------------------------------------------------------------------------

class TestLogicAgent:
    agent = LogicAgent()

    def test_structured_query_proceeds(self):
        q = Query("The project plan includes a phased migration strategy with clear milestones and objectives.")
        v = self.agent.analyze(q)
        assert v.stance == Stance.PROCEED
        assert v.confidence >= 0.60

    def test_vague_query_caution(self):
        q = Query("Maybe we might possibly do something, but we're not sure and it's unclear.")
        v = self.agent.analyze(q)
        assert v.stance in (Stance.CAUTION, Stance.DELAY)

    def test_contradictory_query_escalates(self):
        q = Query("We should proceed but however although this conflicts and contradicts our goals yet despite issues.")
        v = self.agent.analyze(q)
        assert v.stance in (Stance.CAUTION, Stance.DELAY)

    def test_confidence_in_range(self):
        q = Query("Proceed with deployment.")
        v = self.agent.analyze(q)
        assert 0.0 <= v.confidence <= 1.0


# ---------------------------------------------------------------------------
# RiskAgent
# ---------------------------------------------------------------------------

class TestRiskAgent:
    agent = RiskAgent()

    def test_high_risk_query_blocks_or_delays(self):
        q = Query(
            "We will migrate all critical production data without rollback, "
            "irreversible cutover, no backup, vendor lock-in, single point of failure."
        )
        v = self.agent.analyze(q)
        assert v.stance in (Stance.DELAY, Stance.BLOCK)
        assert v.confidence >= 0.70

    def test_mitigated_query_proceeds(self):
        q = Query(
            "We have a rollback plan, staging environment, tested backups, "
            "disaster recovery and monitoring in place."
        )
        v = self.agent.analyze(q)
        assert v.stance == Stance.PROCEED

    def test_blockers_populated_for_high_risk(self):
        q = Query("Critical production migration with data loss risk and no rollback.")
        v = self.agent.analyze(q)
        if v.stance in (Stance.DELAY, Stance.BLOCK):
            assert len(v.blockers) > 0


# ---------------------------------------------------------------------------
# DomainExpertAgent
# ---------------------------------------------------------------------------

class TestDomainExpertAgent:
    agent = DomainExpertAgent()

    def test_erp_domain_detected(self):
        q = Query("Should we proceed with the Oracle ERP UAT and go-live?")
        v = self.agent.analyze(q)
        assert v.metadata.get("detected_domain") == "erp"

    def test_cloud_domain_detected(self):
        q = Query("We plan to migrate workloads to AWS using Kubernetes and Terraform IaC.")
        v = self.agent.analyze(q)
        assert v.metadata.get("detected_domain") == "cloud"

    def test_concern_escalates_stance(self):
        q = Query("Go live on Oracle ERP without UAT — skip training and bypass tests.")
        v = self.agent.analyze(q)
        assert v.stance in (Stance.DELAY, Stance.BLOCK)


# ---------------------------------------------------------------------------
# ContradictionAgent
# ---------------------------------------------------------------------------

class TestContradictionAgent:
    agent = ContradictionAgent()

    def test_no_contradiction_proceeds(self):
        q = Query("We have a fully tested migration plan with staged rollout.")
        v = self.agent.analyze(q)
        assert v.stance == Stance.PROCEED
        assert v.confidence >= 0.70

    def test_downtime_contradiction_detected(self):
        q = Query("We need zero downtime but will perform a full migration of all data.")
        v = self.agent.analyze(q)
        assert v.stance != Stance.PROCEED

    def test_test_skip_contradiction(self):
        q = Query("We want to skip all tests and go directly to production.")
        v = self.agent.analyze(q)
        assert v.stance != Stance.PROCEED


# ---------------------------------------------------------------------------
# CostAgent
# ---------------------------------------------------------------------------

class TestCostAgent:
    agent = CostAgent()

    def test_overrun_signals_delay(self):
        q = Query("The project is over budget with undefined cost and no approved budget.")
        v = self.agent.analyze(q)
        assert v.stance in (Stance.DELAY, Stance.BLOCK)

    def test_good_financials_proceed(self):
        q = Query("We have an approved budget, ROI model, and TCO analysis in place.")
        v = self.agent.analyze(q)
        assert v.stance in (Stance.PROCEED, Stance.CAUTION)

    def test_large_spend_flagged(self):
        q = Query("This project requires a $50 million investment with no budget approved.")
        v = self.agent.analyze(q)
        assert v.stance in (Stance.DELAY, Stance.BLOCK, Stance.CAUTION)


# ---------------------------------------------------------------------------
# ComplianceAgent
# ---------------------------------------------------------------------------

class TestComplianceAgent:
    agent = ComplianceAgent()

    def test_no_compliance_signals_neutral(self):
        q = Query("Should we hire more engineers?")
        v = self.agent.analyze(q)
        assert v.stance == Stance.CAUTION  # cautious neutrality

    def test_satisfied_compliance_proceeds(self):
        q = Query("GDPR compliance reviewed, DPO approved, and controls in place.")
        v = self.agent.analyze(q)
        assert v.stance in (Stance.PROCEED, Stance.CAUTION)

    def test_gaps_escalate_to_delay_or_block(self):
        q = Query("No encryption, no access control, missing SOX audit trail, no SoD.")
        v = self.agent.analyze(q)
        assert v.stance in (Stance.DELAY, Stance.BLOCK)
        assert len(v.blockers) > 0
