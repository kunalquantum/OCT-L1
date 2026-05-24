"""
Example: Oracle ERP migration decision — the flagship CephMind demo.

Run with:
    python -m cephmind.examples.erp_migration
"""

from cephmind import CephMindOrchestrator, Query
from cephmind.agents import DEFAULT_AGENTS

QUERY = Query(
    text=(
        "Should this Oracle ERP migration proceed? "
        "The project has a fixed go-live date in 6 weeks. "
        "UAT is still incomplete, there is no rollback plan, "
        "the budget is over budget by 20%, "
        "data migration scripts are untested in production, "
        "and we have a dependency on a single legacy interface. "
        "GDPR controls are not yet reviewed by the DPO."
    ),
    domain="erp",
)


def main() -> None:
    orchestrator = CephMindOrchestrator(DEFAULT_AGENTS)
    result = orchestrator.reason(QUERY)
    print(result.summary_table())

    print("\nDetailed Agent Verdicts:")
    print("-" * 62)
    for v in result.verdicts:
        print(f"\n[{v.agent_name}]")
        print(f"  Stance     : {v.stance.value}")
        print(f"  Confidence : {v.confidence:.0%}")
        print(f"  Summary    : {v.summary}")
        for f in v.findings:
            print(f"  • {f}")
        for b in v.blockers:
            print(f"  ✖ BLOCKER: {b}")


if __name__ == "__main__":
    main()
