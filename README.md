
# Chaos Engineering + SLO Game-Day Project 💥📈

[![CI Pipeline](https://github.com/SumitDalavi/chaos-slo-gameday/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/SumitDalavi/chaos-slo-gameday/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/SumitDalavi/chaos-slo-gameday?color=0969da&label=release&logo=github)](https://github.com/SumitDalavi/chaos-slo-gameday/releases)
[![Release Workflow](https://github.com/SumitDalavi/chaos-slo-gameday/actions/workflows/release.yml/badge.svg)](https://github.com/SumitDalavi/chaos-slo-gameday/actions/workflows/release.yml)
[![SBOM](https://img.shields.io/badge/SBOM-SPDX%202.3-blueviolet?logo=spdx)](https://github.com/SumitDalavi/chaos-slo-gameday/releases/tag/v0.2.0)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Maturity:** Lab / Reference Implementation
> _Fault injection with Chaos Mesh against a Prometheus-backed SLO/error-budget dashboard — turning your "~99.95% uptime" resume claim into something an interviewer can actually inspect._

## The Problem

Every SRE resume claims "maintained 99.9%+ uptime." But without evidence of *how* you test resilience, it's just a number. Chaos engineering systematically injects failures to validate that SLOs hold under stress — and an error-budget dashboard makes the impact visible and measurable.

## The Solution

This project combines:
1. **A target application** (Node.js service with health and latency endpoints)
2. **Chaos experiments** (Chaos Mesh YAML manifests: pod kill, network delay, CPU stress)
3. **SLO/Error-Budget dashboard** (Prometheus recording rules + Grafana dashboard)
4. **Automated Remediation** (A webhook that catches Grafana alerts and automatically initiates a deployment freeze when error budgets are exhausted).

```
┌──────────────┐    Chaos Mesh     ┌──────────────┐
│ Chaos Mesh   │───injects fault──►│ Target App   │
│ Controller   │                   │ (Node.js)    │
└──────────────┘                   └──────┬───────┘
                                          │ /metrics
                                   ┌──────▼───────┐
                                   │  Prometheus   │
                                   │  (SLI/SLO     │
                                   │   recording)  │
                                   └──────┬───────┘
                                          │
                                   ┌──────▼───────┐
                                   │   Grafana     │
                                   │  Error Budget │
                                   │  Dashboard    │
                                   └──────────────┘
```

## Why This Over the Obvious Alternative

Running `kubectl delete pod` is not chaos engineering. This project uses **Chaos Mesh** (CNCF project) with declarative experiment manifests, and pairs it with a **quantitative SLO framework** (not just uptime monitoring). The Grafana dashboard shows remaining error budget in real time — the exact workflow Google SRE teams use.

## 📁 Project Structure

```
├── app/                          # Target application
│   ├── index.js
│   ├── package.json
│   └── Dockerfile
├── chaos-experiments/            # Chaos Mesh experiment manifests
│   ├── pod-kill.yaml
│   ├── network-delay.yaml
│   └── cpu-stress.yaml
├── monitoring/
│   ├── prometheus-rules.yaml     # SLI/SLO recording and alerting rules
│   └── grafana-dashboard.json    # Error budget dashboard
├── webhook/
│   └── server.js                 # Webhook for automated deployment freezes
├── k8s/                          # Kubernetes deployment manifests
│   └── deployment.yaml
├── docs/ARCHITECTURE.md
└── README.md
```

## 🛠️ Tech Stack

- **Chaos**: Chaos Mesh (CNCF)
- **Monitoring**: Prometheus, Grafana
- **Target**: Node.js + Express
- **Orchestration**: Kubernetes

## Decision Log

| Decision | Rationale |
|----------|-----------|
| Chaos Mesh over LitmusChaos | Chaos Mesh is more Kubernetes-native with CRD-based experiment definitions |
| Error budget over uptime % | Error budgets quantify *remaining tolerance for failure* — the modern SRE approach |
| Three experiment types | Covers the three most common failure modes: process crash, network degradation, resource exhaustion |

## 📋 Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | >= 1.28 | Kubernetes CLI |
| [kind](https://kind.sigs.k8s.io/) or [minikube](https://minikube.sigs.k8s.io/) | Latest | Local K8s cluster |
| [Helm](https://helm.sh/) | >= 3.x | Package manager for K8s |
| [Docker](https://www.docker.com/) | >= 24.x | Container runtime |

## 🚀 Step-by-Step Setup

### Option A: Local Cluster (kind)

```bash
# 1. Clone the repository
git clone https://github.com/SumitDalavi/chaos-slo-gameday.git
cd chaos-slo-gameday

# 2. Create a local Kubernetes cluster
kind create cluster --name chaos-lab

# 3. Install Chaos Mesh
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh --namespace chaos-mesh --create-namespace --set chaosDaemon.runtime=containerd --set chaosDaemon.socketPath=/run/containerd/containerd.sock

# 4. Deploy the target application
kubectl apply -f k8s/deployment.yaml

# 5. Install Prometheus for SLO monitoring
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace

# 6. Apply Prometheus alerting rules
kubectl apply -f monitoring/prometheus-rules.yaml -n monitoring
```

### Option B: Existing Cloud Cluster (EKS/AKS/GKE)

```bash
# Ensure kubectl is configured to your cluster
kubectl cluster-info

# Follow steps 3-6 from Option A
```

## 🧪 Usage & Demo â€” Running a GameDay

### Step 1: Verify the target app is healthy
```bash
kubectl get pods -l app=target-app
kubectl port-forward svc/target-app 8080:80 &
curl http://localhost:8080/health
```

### Step 2: Run a Pod Kill experiment
```bash
kubectl apply -f chaos-experiments/pod-kill.yaml
# Watch pods recover
kubectl get pods -w
```

### Step 3: Run a CPU Stress experiment
```bash
kubectl apply -f chaos-experiments/cpu-stress.yaml
# Monitor resource usage
kubectl top pods
```

### Step 4: Run a Network Delay experiment
```bash
kubectl apply -f chaos-experiments/network-delay.yaml
# Observe increased latency
curl -w "Total time: %{time_total}s\n" http://localhost:8080/health
```

### Step 5: Monitor SLO impact
```bash
# Port-forward Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &
# Open http://localhost:9090 and check alerting rules
```

## ✅ Verification

| Check | Command | Expected |
|-------|---------|----------|
| Cluster ready | `kubectl get nodes` | Node(s) in Ready state |
| App running | `kubectl get pods -l app=target-app` | Pod(s) Running |
| Chaos engine | `kubectl get podchaos,stresschaos,networkchaos -n default` | Experiments listed |
| Prometheus | Port-forward to 9090 | Metrics and alerts visible |

```bash
# Cleanup
kind delete cluster --name chaos-lab
```

## 👨‍💻 Author

**Sumit Dalavi** — Senior DevSecOps / Platform Engineer
[GitHub](https://github.com/SumitDalavi) | [LinkedIn](https://in.linkedin.com/in/sumit-dalavi-762838129)

## 🚀 Progressive Credential Loading & Execution Tiers

This project implements **Progressive Credential Loading (PCL)**, allowing it to run immediately out-of-the-box without external dependencies while seamlessly upgrading as credentials are provided.

### Tier 1: Zero-Config Mock Mode (Default)
Ideal for CI, testing, and rapid local evaluation.
- **Execution:** Run with default configuration (`cp .env.example .env`). Zero API keys, databases, or cloud credentials required.
- **Fallback Behavior:** In-memory caches, deterministic offline heuristics, mock vector embeddings, and local mock storage are automatically used.
- **Health Verification:** Endpoints report `{"mode": "mock"}` for unconfigured dependencies.

### Tier 2: Local Development with Live Services
Connect specific external services while keeping others mocked.
- **Execution:** Provide credentials in `.env` for the services you want active (e.g., `PROMETHEUS_URL, SLO_TARGET`).
- **Progressive Upgrade:** The runtime inspects environment variables on boot and dynamically promotes only configured modules to live mode.
- **Safe Fallback:** Any missing credentials automatically remain on mock fallbacks with no crashes or missing service errors.

### Tier 3: Production Hardened
Enterprise deployment with production-grade backends, security scans, and container distributions.
- **Release Distribution:** Download standalone release bundle and verified checksums:
  ```bash
  gh release download v0.2.0 --repo SumitDalavi/chaos-slo-gameday
  ```
- **Integrity & Security:** Checksums and SPDX SBOM (`sbom.spdx.json`) available on [GitHub Releases](https://github.com/SumitDalavi/chaos-slo-gameday/releases).

## 📚 Documentation

- [Game Day Report (2026-08-29)](docs/gameday-report-2026-08-29.md) — Real execution of failover testing.
- [Architecture](docs/ARCHITECTURE.md) — System diagram and component details
- [Runbook](docs/runbook.md) — Setup, commands, and expected outputs
- [Decisions](docs/decisions.md) — ADRs for Chaos Engineering approach
- [Changelog](docs/changelog.md) — Change history
- [GameDay Report](docs/gameday_report.md) — Results of SLO breach simulation

## Mock Boundaries (Honest Scope)

| What | Status | Details |
|---|---|---|
| Target Application | **Real** | A real Express.js app container instrumented for Prometheus. |
| Fault Injection | **Real** | Chaos Mesh actually kills pods and injects tc-based network delays via DaemonSets. |
| Alert Routing | **Mocked** | Webhook triggers a local script rather than actually paging PagerDuty or executing Argo rollbacks. |

## 🔗 Related Projects

- [`gitops-progressive-delivery`](../gitops-progressive-delivery/) — Uses the metrics proven here for automated rollbacks.

---

## Release & Security Verification

This repository is published as an immutable release catalog under the portfolio release standard:

- **Release Artifacts:** Authenticated distribution bundle (`chaos-slo-gameday-v0.2.0.tar.gz`) containing production policies, modules, and manifests.
- **Cryptographic Integrity:** SHA-256 integrity hash provided in `checksums.txt`.
- **Software Bill of Materials (SBOM):** Fully compliant SPDX JSON SBOM (`sbom.spdx.json`) generated by Anchore Syft.

### Verification Commands
```bash
# 1. View Release Metadata
gh release view v0.2.0 --repo SumitDalavi/chaos-slo-gameday

# 2. Download Release Assets & Verify SHA256 Checksum
gh release download v0.2.0 --repo SumitDalavi/chaos-slo-gameday --pattern "*.tar.gz" --pattern "checksums.txt"
sha256sum -c checksums.txt

# 3. Inspect SPDX SBOM
gh release download v0.2.0 --repo SumitDalavi/chaos-slo-gameday --pattern "sbom.spdx.json"
cat sbom.spdx.json | jq .spdxVersion
```
