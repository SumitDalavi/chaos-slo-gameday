# Decisions

## ADR-001: Chaos Mesh over LitmusChaos
**Date:** 2026-08-29  
**Status:** Accepted

**Context:**  
We need a fault injection framework to validate our Prometheus SLO definitions.

**Decision:**  
We selected Chaos Mesh because it leverages Kubernetes CRDs natively and does not require complex runner pods for basic experiments.

**Consequences:**  
- ✅ Declarative fault injection.
- ✅ Easy to automate with `kubectl apply`.
- ⚠️ Requires privileged DaemonSet (Chaos Daemon) to manipulate network namespaces and cgroups on the worker nodes.

## ADR-002: Progressive Credential Loading (PCL) Architecture
- **Context:** Production hardening required live backends (PostgreSQL, Redis, OpenAI, Anthropic), but removing mocks would break CI pipelines and create high developer onboarding friction.
- **Decision:** Implement Progressive Credential Loading. Keep in-memory and local mock heuristics as the default safe baseline, while wrapping external integrations in auto-promoting factory adapters triggered by environment variables.
- **Consequences:** 
  - *Pros:* 100% CI pass rate without requiring external secrets; zero setup friction for new contributors; progressive upgrade to production clusters.
  - *Cons:* Adds lightweight factory abstraction layers and runtime credential detection logic.

## ADR-003: Closed-Loop Canary Chaos Fault Injection and Automated Rollout Abort
- **Date:** 2026-10-27
- **Status:** Accepted
- **Context:** Validating resilience against canary degradation requires active fault injection directly targeted at canary pods to prove that automated progressive delivery controllers detect anomalies and abort without affecting stable baseline traffic.
- **Decision:** Introduce Chaos Mesh `NetworkChaos` targeting pods labeled with `rollouts-pod-template-hash` (canary pods) with 400ms latency and 15% packet corruption. Implement `scripts/verify-canary-chaos-abort.py` to simulate telemetry degradation and confirm autonomous canary termination and traffic restoration with zero downtime.
- **Consequences:**
  - *Pros:* Proves end-to-end self-healing loop under controlled chaos conditions; validates SLO protection mechanisms.
  - *Cons:* Requires Chaos Mesh CRDs installed in the target testbed cluster.
