"""
Example: Cloud migration decision with strong governance.

Run with:
    python -m cephmind.examples.cloud_migration
"""

from cephmind import CephMindOrchestrator, Query
from cephmind.agents import DEFAULT_AGENTS

QUERY = Query(
    text=(
        "Should we proceed with the AWS cloud migration? "
        "All workloads are containerised using Kubernetes. "
        "Terraform IaC is in place, CI/CD pipeline tested, "
        "blue-green deployment strategy confirmed, "
        "DR and failover validated in staging, "
        "encryption at rest and in transit enforced, "
        "least-privilege IAM policies reviewed. "
        "Budget approved, TCO model signed off by CFO, "
        "and AWS Well-Architected Review passed."
    ),
    domain="cloud",
)


def main() -> None:
    orchestrator = CephMindOrchestrator(DEFAULT_AGENTS)
    result = orchestrator.reason(QUERY)
    print(result.summary_table())


if __name__ == "__main__":
    main()
