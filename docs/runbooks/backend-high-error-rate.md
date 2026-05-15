# Backend High Error Rate Runbook

## Purpose

Use this when the backend returns elevated 5xx responses, health endpoints fail,
or request latency is high.

## Alerts

- `DevBoardBackendHighErrorRate`: more than 5% backend HTTP requests are 5xx for
  5 minutes.
- `DevBoardBackendHighLatency`: average backend request duration is above 750 ms
  for 5 minutes.
- `DevBoardServiceUnavailable`: `/api/health` or `/actuator/health` returned 5xx.
- `DevBoardActuatorScrapeFailure`: Prometheus cannot scrape backend actuator
  metrics.
- `DevBoardBackendUnavailable`: backend Rollout has no ready backend pod.

## Impact

Users may not be able to load tasks, create tasks, log in, or save comments.
Kafka events may stop being produced if task writes fail before event publish.

## First Checks

```bash
export APP_NS=devboard
export MONITORING_NS=monitoring

kubectl get pods -n "$APP_NS" -l app=devboard-backend
kubectl logs -n "$APP_NS" -l app=devboard-backend --tail=160
kubectl describe rollout devboard-backend -n "$APP_NS"
kubectl get events -n "$APP_NS" --sort-by=.lastTimestamp | tail -40
```

Check health directly:

```bash
kubectl port-forward -n "$APP_NS" svc/devboard-backend 8080:8080
curl -fsS http://localhost:8080/api/health
curl -fsS http://localhost:8080/actuator/health
```

Check error and latency metrics:

```bash
kubectl port-forward -n "$MONITORING_NS" svc/devboard-monitoring-kube-p-prometheus 9090:9090

curl -fsS 'http://localhost:9090/api/v1/query?query=sum(rate(http_server_requests_seconds_count%7Bjob%3D%22devboard-backend%22%2Curi!%3D%22%2Factuator%2Fprometheus%22%2Cstatus%3D~%225..%22%7D%5B5m%5D))'
curl -fsS 'http://localhost:9090/api/v1/query?query=sum(rate(http_server_requests_seconds_sum%7Bjob%3D%22devboard-backend%22%2Curi!%3D%22%2Factuator%2Fprometheus%22%7D%5B5m%5D))%20%2F%20sum(rate(http_server_requests_seconds_count%7Bjob%3D%22devboard-backend%22%2Curi!%3D%22%2Factuator%2Fprometheus%22%7D%5B5m%5D))'
```

## Diagnosis

Look for the main class of failure:

| Symptom | Likely cause | Next runbook |
| --- | --- | --- |
| SQL, connection pool, timeout errors | RDS or credentials issue | [Database Connectivity](database-connectivity.md) |
| producer/bootstrap errors | Kafka connectivity issue | [Kafka Consumer Lag](kafka-consumer-lag.md) |
| `OutOfMemoryError`, `OOMKilled` | memory pressure | [Pod Crash Loops](pod-crash-loops.md) |
| starts after latest deploy | bad release | [Rollback Procedure](rollback-procedure.md) |
| high latency with healthy dependencies | load or inefficient endpoint | inspect request volume and resource usage |

Check runtime config:

```bash
kubectl get configmap devboard-backend-config -n "$APP_NS" -o yaml
BACKEND_POD="$(kubectl get pod -n "$APP_NS" -l app=devboard-backend -o jsonpath='{.items[0].metadata.name}')"
kubectl exec -n "$APP_NS" "$BACKEND_POD" -- printenv | grep -E 'SPRING|DATABASE|KAFKA|CORS'
```

Check resource pressure:

```bash
kubectl top pods -n "$APP_NS"
kubectl top nodes
```

Check recent deployment history:

```bash
kubectl get rollout devboard-backend -n "$APP_NS"
argocd app history devboard
```

## Recovery

If the backend is wedged but config and dependencies are healthy:

```bash
kubectl rollout restart rollout.argoproj.io/devboard-backend -n "$APP_NS"
kubectl wait --for=condition=Available rollout.argoproj.io/devboard-backend -n "$APP_NS" --timeout=300s
```

If the latest deployment introduced the error, roll back with
[Rollback Procedure](rollback-procedure.md).

If the database is failing, recover database connectivity before restarting the
backend. Restarting repeatedly can increase pressure on the database.

If latency is caused by resource pressure, scale the backend temporarily during
the incident and make the replica change permanent in Git if it is still needed:

```bash
kubectl scale rollout.argoproj.io/devboard-backend -n "$APP_NS" --replicas=2
```

Because Argo CD self-heal is enabled, manual scaling may be reverted unless the
desired state is also changed in Git or sync is temporarily paused for the demo.

## Validation

```bash
curl -fsS http://localhost:8080/api/health
curl -fsS http://localhost:8080/api/hello
kubectl wait --for=condition=Available rollout.argoproj.io/devboard-backend -n "$APP_NS" --timeout=300s
```

Confirm alerts clear:

```bash
curl -fsS 'http://localhost:9093/api/v2/alerts' | grep DevBoardBackend || true
curl -fsS 'http://localhost:9093/api/v2/alerts' | grep DevBoardServiceUnavailable || true
```

## Follow-Up

- Add a smoke test for the endpoint or dependency that failed.
- Add structured log context around the failing path.
- Review whether the alert should route as critical if users were blocked.
- Document the exact recovery time for interview discussion.
