"""Automated GameDay report generator."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional
from slo.calculator import calculate_error_budget, SLOStatus


def generate_report(
    game_day_name: str,
    experiments_run: List[Dict],
    services: List[Dict],
    observations: List[str],
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a structured Markdown GameDay report.

    Args:
        experiments_run: List of {name, duration, type, outcome}
        services: List of {name, slo_target, total_requests, failed_requests}
        observations: Free-text observations from the team
    """
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Calculate SLO impact for each service
    slo_statuses = []
    for svc in services:
        status = calculate_error_budget(
            service=svc["name"],
            slo_target=svc["slo_target"],
            total_requests=svc["total_requests"],
            failed_requests=svc["failed_requests"],
        )
        slo_statuses.append(status)

    # Build experiment table
    exp_table = "| Experiment | Type | Duration | Outcome |
|------------|------|----------|---------|
"
    for exp in experiments_run:
        exp_table += f"| {exp['name']} | {exp['type']} | {exp['duration']} | {exp['outcome']} |
"

    # Build SLO impact table
    slo_table = "| Service | SLO Target | Availability | Budget Used | Status |
|---------|-----------|--------------|-------------|--------|
"
    for s in slo_statuses:
        slo_table += (
            f"| {s.service} | {s.slo_target*100:.1f}% | {s.current_availability*100:.3f}% "
            f"| {s.error_budget_used_pct:.1f}% | {s.status} |
"
        )

    obs_md = "
".join(f"- {o}" for o in observations)

    report = f'''# GameDay Report: {game_day_name}

**Date:** {date}
**Status:** Completed

---

## Experiments Run

{exp_table}

## SLO Impact Analysis

{slo_table}

## Team Observations

{obs_md}

## Action Items

> Review the SLO impact table and create tickets for any service with STATUS != HEALTHY.
> Re-run failing experiments after fixes to validate improvement.

---
*Generated automatically by chaos-slo-gameday reporting tool*
'''
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved: {output_path}")

    return report
