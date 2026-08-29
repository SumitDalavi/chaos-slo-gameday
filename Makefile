.PHONY: gameday report slo-check help

## gameday: Run a full chaos game day against distributed-job-scheduler
gameday:
	@echo "🎯 Starting Chaos Game Day..."
	@echo "Target: distributed-job-scheduler"
	@bash scripts/run_gameday.sh 2>&1 | tee docs/run-history/$(shell date +%Y-%m-%d-%H).md

## report: Generate the latest game day report summary
report:
	@echo "📊 Latest Game Day Report:"
	@cat docs/gameday-report-2026-08-29.md

## slo-check: Verify SLO compliance from last game day
slo-check:
	@echo "🔍 Checking SLO Compliance..."
	@python3 scripts/check_slo.py

## help: Show this help
help:
	@grep -E '^## ' Makefile | sed 's/## /  /'
