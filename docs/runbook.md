# Runbook — chaos-slo-gameday
> Last updated: 2026-08-29

## Quick Start
```bash
# Bring up the cluster and deploy Chaos Mesh + target app
kind create cluster --name chaos-lab
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --create-namespace --set chaosDaemon.runtime=containerd --set chaosDaemon.socketPath=/run/containerd/containerd.sock
kubectl apply -f k8s/deployment.yaml
```

## Run Tests / Demos
```bash
kubectl apply -f chaos-experiments/network-delay.yaml
# Monitor metrics
```

## Failure Modes
| Symptom | Cause | Fix |
|---|---|---|
| Chaos experiment fails to apply | Chaos Daemon not running | Ensure `chaosDaemon.runtime` matches your local k8s provider |


---

## Release Runbook

### Release Trigger
Tag push matching `v*.*.*` (e.g., `v0.1.0`).

### Automated Pipeline Stages
1. **Quality & Validation Gate:** Validates policy syntax, manifest schemas, and configuration integrity.
2. **Distribution Packaging:** Bundles clean production manifests into `chaos-slo-gameday-<tag>.tar.gz` and calculates SHA256 checksums.
3. **Syft Source SBOM:** Generates `sbom.spdx.json` adhering to SPDX 2.3 standard.
4. **GitHub Release:** Publishes release assets and release notes.

### Verification
```bash
gh release view v0.1.0 --repo SumitDalavi/chaos-slo-gameday
gh release download v0.1.0 --repo SumitDalavi/chaos-slo-gameday --pattern "checksums.txt"
```

### Failure Modes & Remediation
- **Linter / Test Failure:** Inspect policy syntax, configurations, or module arguments locally before tagging.
- **Checksum Mismatch:** Ensure file was completely downloaded without network truncation.
