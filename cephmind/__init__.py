"""
CephMind — Distributed AI Reasoning Inspired by Cephalopod Cognition

Multiple specialized reasoning agents collaborate, challenge, and validate
before producing a final decision with an explicit reliability score.
"""

from .core.orchestrator import CephMindOrchestrator
from .core.models import Query, ReasoningResult

__all__ = ["CephMindOrchestrator", "Query", "ReasoningResult"]
__version__ = "0.1.0"
