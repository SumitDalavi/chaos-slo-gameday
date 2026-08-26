"""Tests for SLO error budget calculator."""
import pytest
from slo.calculator import calculate_error_budget
from slo.error_budget import check_policy_violations


def test_healthy_service():
    status = calculate_error_budget("api", 0.999, total_requests=100000, failed_requests=50)
    assert status.status == "HEALTHY"
    assert status.error_budget_remaining_minutes > 0
    assert status.current_availability > 0.999


def test_exhausted_budget():
    # 5% failure rate on a 99.9% SLO = budget instantly exhausted
    status = calculate_error_budget("api", 0.999, total_requests=10000, failed_requests=500)
    assert status.status in ("EXHAUSTED", "BURNING_FAST")
    assert status.error_budget_burn_rate > 2.0


def test_burn_rate_calculation():
    # exactly at SLO — burn rate should be 1.0
    status = calculate_error_budget("api", 0.99, total_requests=10000, failed_requests=100)
    assert abs(status.error_budget_burn_rate - 1.0) < 0.05


def test_policy_violations_critical():
    status = calculate_error_budget("svc", 0.999, total_requests=1000, failed_requests=999)
    violations = check_policy_violations([status])
    assert any(v["severity"] in ("CRITICAL", "PAGE") for v in violations)


def test_policy_no_violation_for_healthy():
    status = calculate_error_budget("svc", 0.99, total_requests=100000, failed_requests=10)
    violations = check_policy_violations([status])
    assert len(violations) == 0


def test_zero_requests_does_not_crash():
    status = calculate_error_budget("svc", 0.999, total_requests=0, failed_requests=0)
    assert status is not None
    assert status.current_availability == 1.0
