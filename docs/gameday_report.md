# GameDay Report: Target App Resilience

**Date:** 2026-08-29  
**Target:** `target-app` (Node.js/Express)  
**SLO Objective:** 99.9% availability (max 43m downtime / month)

## Incident Simulation

**Experiment:** Pod Kill (Chaos Mesh)
- **Time Injected:** 10:00:00 UTC
- **Fault Description:** Chaos Daemon randomly killed 1 pod in the `target-app` replica set every 60 seconds.
- **Initial State:** 3/3 pods running, 100% availability.

## Observations

1. **10:01:00 UTC**: Pod 1 terminated. Traffic routed to Pods 2 & 3.
2. **10:01:05 UTC**: Node.js app failed to gracefully handle in-flight requests on Pod 1 before SIGKILL.
3. **SLI Impact**: Prometheus recorded a spike in HTTP 502s (Bad Gateway) from the ingress controller as connections were abruptly severed.
4. **SLO Breach**: The rolling 5-minute error rate spiked to 0.5%, breaching the 99.9% objective.

## Error Budget Impact
- **Budget Consumed:** 4 minutes of error budget was consumed during the 15-minute experiment window.
- **Remaining Budget:** ~39 minutes for the 30-day window.

## Remediation Applied

To fix the observed failure mode (dropped in-flight requests), the following remediations were applied:

1. **PreStop Hook**: Added a `preStop` hook to the Kubernetes deployment to delay pod termination by 5 seconds, giving the ingress time to remove the pod from its load balancing pool.
2. **Graceful Shutdown**: Added `SIGTERM` handlers in the Node.js app to complete in-flight requests before exiting.

**Verification:**
After deploying the fixes, a second GameDay was run. The Pod Kill experiment produced 0 HTTP 502s, maintaining 100% SLO compliance during chaotic node/pod turnover.
