# Architecture: Chaos + SLO Game-Day
> Maturity: Lab / Reference Implementation

## System Diagram
The following Mermaid.js sequence diagram maps the core workflow and interactions:

```mermaid
sequenceDiagram
    CRD->>ChaosController: Apply NetworkDelay
ChaosController->>Daemon: Inject to Pod
Prometheus->>Grafana: Monitor SLO Burn
```


## SLO Framework
### SLIs (Service Level Indicators)
- **Availability SLI**: Ratio of successful HTTP responses (2xx) to total requests
- **Latency SLI**: P99 request duration

### SLOs (Service Level Objectives)
- **Availability**: 99.9% over a 30-day rolling window
- **Latency**: P99 < 500ms

### Error Budget
Error budget = `1 - ((1 - actual_availability) / (1 - target_availability))`.
When the error budget drops below 25%, an alert fires telling the team to stop feature work and focus on reliability.

## Chaos Experiments
Three experiment types cover the most common failure modes:
1. **Pod Kill**: Validates that the Deployment's replicas and readiness probes ensure zero-downtime recovery
2. **Network Delay**: Validates that the service degrades gracefully under latency (circuit breakers, timeouts)
3. **CPU Stress**: Validates resource limits and HPA (Horizontal Pod Autoscaler) behavior

## Game-Day Workflow
1. Deploy the target app and monitoring stack
2. Verify baseline SLO metrics on the Grafana dashboard
3. Apply a chaos experiment (e.g., `kubectl apply -f chaos-experiments/pod-kill.yaml`)
4. Observe the error budget on Grafana — does it burn?
5. Document findings and corrective actions

## Progressive Credential Loading & Production Architecture (v0.2.0)

This service implements the **Progressive Credential Loading (PCL)** pattern, decoupling development speed from external infrastructure provisioning:

```mermaid
graph LR
    Env[Environment Credentials] -->|Detect Keys & URLs| Detector[Credential Detector]
    Detector -->|No Credentials / Missing| Mock[Mock Mode Factory]
    Detector -->|Valid Credentials Present| Live[Live Provider Factory]
    Mock --> Runtime[Application Core & /health]
    Live --> Runtime
```

### Core Architecture Components
1. **Mode Detection Singleton:** Inspects environment configuration at boot time without hard crashes on missing secrets.
2. **Dual-Mode Factory Wrappers:**
   - **Storage / Cache:** In-process maps or SQLite `:memory:` transparently promote to managed Redis or PostgreSQL when connection strings are supplied.
   - **AI Providers:** Deterministic heuristic generators and local embeddings transparently promote to live OpenAI, Anthropic, or Gemini API clients.
3. **Hot-Reload & Dynamic TLS:** File watchers monitor mounted volume paths (Kubernetes ConfigMaps and Secrets) to update certificates and limit configs atomically without process restarts.
4. **Health & Observability:** The `/health` endpoint exposes real-time runtime mode metadata (`mock` vs `live`) across all backing adapters.

## Closed-Loop Canary Chaos Verification (v0.2.1)

```mermaid
sequenceDiagram
    participant Rollout as Argo Rollouts (25% Weight)
    participant Chaos as Chaos Mesh (NetworkChaos)
    participant Metrics as Prometheus Monitoring
    participant SelfHeal as Autonomous Rollback
    
    Rollout->>Chaos: Active Canary Pods
    Chaos->>Rollout: Inject 400ms Delay + 15% HTTP 500
    Metrics->>Rollout: Success Rate Drops to 84.9% (SLO < 99.5%)
    Rollout->>SelfHeal: FailureLimit (3) Tripped
    SelfHeal->>Rollout: Abort Rollout & Kill Canary Pods
    Rollout->>Rollout: Restore 100% Traffic to Stable ReplicaSet
```
