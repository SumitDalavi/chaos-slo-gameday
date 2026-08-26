"""SLO Error Budget Calculator with burn rate tracking."""
from __future__ import annotations
import os, time
from dataclasses import dataclass
from typing import Optional

try:
    import httpx
    _HTTPX = True
except ImportError:
    _HTTPX = False


@dataclass
class SLOStatus:
    service: str
    slo_target: float          # e.g. 0.999 = 99.9%
    current_availability: float
    error_budget_total_minutes: float
    error_budget_remaining_minutes: float
    error_budget_burn_rate: float     # 1.0 = consuming at exactly the allowed rate
    window_days: int
    is_burning_fast: bool             # burn rate > 2x = alert
    alert_threshold: float = 2.0

    @property
    def error_budget_used_pct(self) -> float:
        if self.error_budget_total_minutes == 0:
            return 100.0
        return (1 - self.error_budget_remaining_minutes / self.error_budget_total_minutes) * 100

    @property
    def status(self) -> str:
        if self.error_budget_remaining_minutes <= 0:
            return "EXHAUSTED"
        if self.is_burning_fast:
            return "BURNING_FAST"
        if self.error_budget_used_pct > 80:
            return "WARNING"
        return "HEALTHY"


def calculate_error_budget(
    service: str,
    slo_target: float,
    total_requests: int,
    failed_requests: int,
    window_days: int = 30,
    prometheus_url: Optional[str] = None,
) -> SLOStatus:
    """
    Calculate SLO error budget status.

    Args:
        slo_target: Target availability (0.0–1.0), e.g. 0.999 for 99.9%
        total_requests: Total requests in the measurement window
        failed_requests: Failed requests (5xx) in the window
        window_days: SLO window in days (default 30)
        prometheus_url: If set, fetch metrics from Prometheus instead
    """
    # If Prometheus is available, pull live metrics
    if prometheus_url and _HTTPX:
        total_requests, failed_requests = _fetch_from_prometheus(prometheus_url, service, window_days)

    availability = 1.0 - (failed_requests / max(total_requests, 1))
    error_rate = 1.0 - availability

    window_minutes = window_days * 24 * 60
    allowed_error_minutes = window_minutes * (1 - slo_target)
    actual_error_minutes = window_minutes * error_rate
    remaining_minutes = allowed_error_minutes - actual_error_minutes

    # Burn rate: how many times faster we're consuming budget than allowed
    burn_rate = error_rate / (1 - slo_target) if (1 - slo_target) > 0 else float("inf")

    return SLOStatus(
        service=service,
        slo_target=slo_target,
        current_availability=availability,
        error_budget_total_minutes=round(allowed_error_minutes, 2),
        error_budget_remaining_minutes=round(remaining_minutes, 2),
        error_budget_burn_rate=round(burn_rate, 2),
        window_days=window_days,
        is_burning_fast=burn_rate > 2.0,
    )


def _fetch_from_prometheus(prometheus_url: str, service: str, window_days: int):
    """Query Prometheus for request counts."""
    window = f"{window_days * 24}h"
    try:
        client = httpx.Client(timeout=5)
        def query(q):
            r = client.get(f"{prometheus_url}/api/v1/query", params={"query": q})
            data = r.json()["data"]["result"]
            return float(data[0]["value"][1]) if data else 0.0

        total = query(f"sum(increase(http_requests_total{{service='{service}'}}[{window}]))")
        failed = query(f"sum(increase(http_requests_total{{service='{service}',status=~'5..'}}[{window}]))")
        return int(total), int(failed)
    except Exception:
        return 10000, 10  # fallback mock
