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

## 👨‍💻 Author

*Built to demonstrate SRE practices: chaos engineering, SLO frameworks, and error-budget-driven development.*
