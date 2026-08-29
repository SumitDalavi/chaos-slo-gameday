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
