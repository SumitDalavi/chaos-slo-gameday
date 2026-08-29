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
