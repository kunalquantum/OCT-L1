# CephMind

> An experimental AI architecture inspired by distributed cognition — where multiple reasoning agents collaborate, challenge, and validate before producing an answer.

---

## Architecture

```
User Query
    │
    ▼
CephMindOrchestrator
    │
    ├── Logic Agent          (internal consistency, structural feasibility)
    ├── Risk Agent           (operational, technical, strategic risks)
    ├── Domain Expert Agent  (domain best-practices: ERP / Cloud / Finance)
    ├── Contradiction Agent  (conflicting claims within the query)
    ├── Cost Agent           (budget exposure, financial governance)
    └── Compliance Agent     (regulatory obligations, control gaps)
    │
    ▼
Consensus + Confidence Engine
    │
    ▼
ReasoningResult
  • Stance per agent (PROCEED / CAUTION / DELAY / BLOCK)
  • Confidence score  (0 – 100%)
  • Reliability score (inter-agent agreement)
  • Recommendation
  • Blockers list
```

---

## Quickstart

```bash
pip install -e ".[dev]"
python -m cephmind.examples.erp_migration
python -m cephmind.examples.cloud_migration
```

### Example output — risky ERP migration

```
==============================================================
  CephMind Reasoning Report
  Query : Should this Oracle ERP migration proceed? The pro…
==============================================================
Agent                     Stance     Conf
---------------------------------------------
Compliance Agent          BLOCK       88%
Contradiction Agent       PROCEED     82%
Cost Agent                DELAY       74%
Domain Expert Agent       DELAY       35%
Logic Agent               CAUTION     60%
Risk Agent                BLOCK       85%
---------------------------------------------

  Consensus     : BLOCK
  Confidence    : 51%
  Reliability   : 40%

  Recommendation: Do not proceed — critical blockers must be resolved first.

  Blockers:
    • Critical compliance controls missing — regulatory exposure is high.
    • Unmitigated risks need remediation plan (3 net signals).
==============================================================
```

---

## Using the API

```python
from cephmind import CephMindOrchestrator, Query
from cephmind.agents import DEFAULT_AGENTS

orch = CephMindOrchestrator(DEFAULT_AGENTS)
result = orch.reason(Query(
    "Should we proceed with the Oracle ERP cutover next week?",
    domain="erp",
))
print(result.summary_table())
```

### Adding a custom agent

```python
from cephmind.core.base_agent import BaseAgent
from cephmind.core.models import AgentVerdict, Stance

class SecurityAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Security Agent"

    def analyze(self, query) -> AgentVerdict:
        # your logic here
        return AgentVerdict(
            agent_name=self.name,
            stance=Stance.CAUTION,
            confidence=0.70,
            summary="Security review pending.",
        )

orch = CephMindOrchestrator(DEFAULT_AGENTS + [SecurityAgent()])
```

---

## Running tests

```bash
pytest cephmind/tests/ -v
```

---

## Design notes

- **No LLM dependency** — agents use deterministic signal analysis so the architecture can be understood, tested, and audited without API keys. Swap in LLM-backed agents by implementing `BaseAgent.analyze()`.
- **Parallel execution** — agents run concurrently via `ThreadPoolExecutor`; agent failures degrade gracefully.
- **Transparent scoring** — confidence and reliability are computed from first principles (signal counts, inter-agent agreement, variance), not a black-box model score.
- **Extensible** — add domain profiles to `DomainExpertAgent`, conflict pairs to `ContradictionAgent`, or whole new agents without touching the orchestrator.
