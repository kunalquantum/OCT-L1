"""All CephMind reasoning agents."""

from .compliance import ComplianceAgent
from .contradiction import ContradictionAgent
from .cost import CostAgent
from .domain_expert import DomainExpertAgent
from .logic import LogicAgent
from .risk import RiskAgent

DEFAULT_AGENTS = [
    LogicAgent(),
    RiskAgent(),
    DomainExpertAgent(),
    ContradictionAgent(),
    CostAgent(),
    ComplianceAgent(),
]

__all__ = [
    "LogicAgent",
    "RiskAgent",
    "DomainExpertAgent",
    "ContradictionAgent",
    "CostAgent",
    "ComplianceAgent",
    "DEFAULT_AGENTS",
]
