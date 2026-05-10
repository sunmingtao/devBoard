# DevBoard Runbooks

These runbooks turn DevBoard's alerts and GitOps workflow into repeatable
incident-response steps. They are written for demo and interview use, but the
shape is intentionally close to production operations:

1. Confirm the alert and impact.
2. Gather facts from Kubernetes, Prometheus, Grafana, and Argo CD.
3. Pick the safest recovery path.
4. Validate that users and alerts recover.
5. Record the cause and follow-up work.

## Quick Access

| Incident | Primary alert | Runbook |
| --- | --- | --- |
| Kafka consumer lag or stalled consumption | `DevBoardKafkaConsumerLagHigh`, `DevBoardKafkaNoMessagesConsumed`, `DevBoardKafkaListenerErrors` | [Kafka Consumer Lag](kafka-consumer-lag.md) |
| Pod crash loop or repeated restart | `DevBoardPodRestarting`, service unavailable alerts | [Pod Crash Loops](pod-crash-loops.md) |
| Failed Kubernetes rollout | Argo CD degraded/out-of-sync, unavailable deployment alerts | [Failed Kubernetes Rollout](failed-kubernetes-rollout.md) |
| Backend 5xx or high latency | `DevBoardBackendHighErrorRate`, `DevBoardBackendHighLatency`, `DevBoardServiceUnavailable` | [Backend High Error Rate](backend-high-error-rate.md) |
| Database connectivity issue | backend/event-service errors, failed health checks | [Database Connectivity](database-connectivity.md) |
| Roll back a bad release | deployment failure, regression, failed smoke test | [Rollback Procedure](rollback-procedure.md) |

## Common Commands

Set these shell variables before running commands:

```bash
export APP_NS=devboard
export MONITORING_NS=monitoring
export ARGO_NS=argocd
```

Check the main platform surfaces:

```bash
kubectl get pods -n "$APP_NS"
kubectl get application devboard -n "$ARGO_NS"
kubectl rollout status deployment/devboard-backend -n "$APP_NS"
kubectl rollout status deployment/devboard-event-service -n "$APP_NS"
```

Open monitoring locally:

```bash
kubectl port-forward -n "$MONITORING_NS" svc/devboard-monitoring-kube-p-prometheus 9090:9090
kubectl port-forward -n "$MONITORING_NS" svc/devboard-monitoring-kube-p-alertmanager 9093:9093
kubectl port-forward -n "$MONITORING_NS" svc/devboard-monitoring-grafana 3001:80
```

Query active alerts:

```bash
curl -fsS 'http://localhost:9090/api/v1/alerts'
curl -fsS 'http://localhost:9093/api/v2/alerts'
```

Open Argo CD:

```bash
deploy/gitops/argocd/port-forward.sh argocd-server
argocd app get devboard
```

## Severity Guide

| Severity | Examples | Target response |
| --- | --- | --- |
| Critical | backend unavailable, event-service unavailable, failed health endpoints | Start triage immediately and choose rollback if a recent deployment is suspected. |
| Warning | Kafka lag, listener errors, high latency, pod restart | Confirm impact, inspect recent changes, recover before backlog or latency becomes user-visible. |
| Demo | intentionally induced failure | Capture screenshots/output, recover using the runbook, then show alert resolution. |

## Demo Story

For interviews, the cleanest story is:

1. Show Argo CD healthy and synced.
2. Introduce a controlled failure, such as scaling `devboard-event-service` to
   zero or deploying a known-bad image in a temporary branch.
3. Show Alertmanager firing and Grafana confirming the signal.
4. Follow the relevant runbook.
5. Restore the workload through GitOps or rollback.
6. Show the alert resolving and the application healthy again.
