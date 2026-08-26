"""Error budget policy and alerting rules."""
from __future__ import annotations
from typing import List, Dict
from slo.calculator import SLOStatus


def check_policy_violations(statuses: List[SLOStatus]) -> List[Dict]:
    """
    Evaluate error budget burn rate policies (Google SRE burn rate alerts):
    - Fast burn (14.4x over 1h): page immediately
    - Medium burn (6x over 6h): page within 1h  
    - Slow burn (3x over 3d): ticket
    """
    violations = []
    for s in statuses:
        if s.error_budget_remaining_minutes <= 0:
            violations.append({
                "service": s.service, "severity": "CRITICAL",
                "message": f"Error budget EXHAUSTED for {s.service} (SLO: {s.slo_target*100}%)",
                "action": "Incident response required immediately",
            })
        elif s.error_budget_burn_rate >= 14.4:
            violations.append({
                "service": s.service, "severity": "PAGE",
                "message": f"Fast burn rate {s.error_budget_burn_rate:.1f}x — budget will exhaust in ~1h",
                "action": "Page on-call engineer",
            })
        elif s.error_budget_burn_rate >= 6.0:
            violations.append({
                "service": s.service, "severity": "WARNING",
                "message": f"Medium burn rate {s.error_budget_burn_rate:.1f}x — budget at risk",
                "action": "Investigate within 1 hour",
            })
        elif s.error_budget_burn_rate >= 3.0:
            violations.append({
                "service": s.service, "severity": "INFO",
                "message": f"Elevated burn rate {s.error_budget_burn_rate:.1f}x — monitor closely",
                "action": "Create ticket and investigate",
            })
    return violations
