# Chaos Engineering + SLO Game-Day Project 💥📈

> Fault injection with Chaos Mesh against a Prometheus-backed SLO/error-budget dashboard — turning your "~99.95% uptime" resume claim into something an interviewer can actually inspect.

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


## ðŸ“‹ Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | >= 1.28 | Kubernetes CLI |
| [kind](https://kind.sigs.k8s.io/) or [minikube](https://minikube.sigs.k8s.io/) | Latest | Local K8s cluster |
| [Helm](https://helm.sh/) | >= 3.x | Package manager for K8s |
| [Docker](https://www.docker.com/) | >= 24.x | Container runtime |

## ðŸš€ Step-by-Step Setup

### Option A: Local Cluster (kind)

```bash
# 1. Clone the repository
git clone https://github.com/SumitDalavi/chaos-slo-gameday.git
cd chaos-slo-gameday

# 2. Create a local Kubernetes cluster
kind create cluster --name chaos-lab

# 3. Install LitmusChaos
kubectl apply -f https://litmuschaos.github.io/litmus/litmus-operator-v3.0.0.yaml

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

## ðŸ§ª Usage & Demo â€” Running a GameDay

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

## âœ… Verification

| Check | Command | Expected |
|-------|---------|----------|
| Cluster ready | `kubectl get nodes` | Node(s) in Ready state |
| App running | `kubectl get pods -l app=target-app` | Pod(s) Running |
| Chaos engine | `kubectl get chaosengines` | Experiments listed |
| Prometheus | Port-forward to 9090 | Metrics and alerts visible |

```bash
# Cleanup
kind delete cluster --name chaos-lab
```

## 👨‍💻 Author

*Built to demonstrate SRE practices: chaos engineering, SLO frameworks, and error-budget-driven development.*
