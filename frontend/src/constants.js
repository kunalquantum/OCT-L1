export const STANCE_COLOR = {
  PROCEED: '#10b981',
  CAUTION: '#f59e0b',
  DELAY:   '#f97316',
  BLOCK:   '#ef4444',
}

export const EXAMPLES = {
  erp: {
    domain: 'erp',
    label: 'ERP migration (risky)',
    text: 'Should this Oracle ERP migration proceed? The project has a fixed go-live date in 6 weeks. UAT is still incomplete, there is no rollback plan, the budget is over budget by 20%, data migration scripts are untested in production, and we have a dependency on a single legacy interface. GDPR controls are not yet reviewed by the DPO.',
  },
  cloud: {
    domain: 'cloud',
    label: 'Cloud migration (clean)',
    text: 'Should we proceed with the AWS cloud migration? All workloads are containerised using Kubernetes. Terraform IaC is in place, CI/CD pipeline tested, blue-green deployment confirmed, DR and failover validated in staging, encryption at rest and in transit enforced, least-privilege IAM policies reviewed. Budget approved and TCO signed off by CFO.',
  },
  finance: {
    domain: 'finance',
    label: 'Budget approval',
    text: 'Should we approve the $2 million capex for the new data platform? No business case has been prepared, costs are unknown, there is no approved budget, no CFO sign-off, and no ROI model.',
  },
  contradiction: {
    domain: 'general',
    label: 'Contradictory proposal',
    text: 'We need zero downtime but will perform a complete live migration of all production data. We also need to skip all tests and go directly to production to meet the urgent deadline. The approach must be thorough and comprehensive yet completed by end of day.',
  },
}
