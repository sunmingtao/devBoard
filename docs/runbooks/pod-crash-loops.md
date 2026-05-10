# Pod Crash Loops Runbook

## Purpose

Use this when a DevBoard pod restarts repeatedly, enters `CrashLoopBackOff`, or
causes one of the service unavailable alerts.

## Alerts

- `DevBoardPodRestarting`: a DevBoard container restarted within the last 15
  minutes and remained alerting for 5 minutes.
- `DevBoardBackendUnavailable`
- `DevBoardEventServiceUnavailable`
- `DevBoardFrontendUnavailable`
- `DevBoardActuatorScrapeFailure`
- `DevBoardServiceUnavailable`

## Impact

Users may see failed requests, stale pages, or missing event updates depending
on which component is restarting.

## First Checks

```bash
export APP_NS=devboard

kubectl get pods -n "$APP_NS" -o wide
kubectl get events -n "$APP_NS" --sort-by=.lastTimestamp | tail -40
kubectl get deployments -n "$APP_NS"
```

Find the failing pod:

```bash
kubectl get pods -n "$APP_NS" | grep -E 'CrashLoopBackOff|Error|ImagePullBackOff|Evicted|Pending'
```

Inspect the pod:

```bash
kubectl describe pod -n "$APP_NS" <pod-name>
kubectl logs -n "$APP_NS" <pod-name> --previous --tail=160
kubectl logs -n "$APP_NS" <pod-name> --tail=160
```

## Diagnosis

Classify the failure:

| Symptom | Likely cause | Check |
| --- | --- | --- |
| `ImagePullBackOff` | bad image tag, registry issue, missing image | `kubectl describe pod` events and `deploy/k8s/overlays/eks/kustomization.yaml` |
| `CrashLoopBackOff` soon after start | bad config, missing secret, app startup error | previous logs and configmaps |
| `OOMKilled` | memory limit too low or memory leak | pod status, container limits, Grafana memory panel |
| `Pending` | no schedulable node capacity | node status and pod events |
| readiness failing | dependency issue or bad health endpoint | pod events, service logs, dependency runbooks |

Check recent rollout state:

```bash
kubectl rollout history deployment/<deployment-name> -n "$APP_NS"
kubectl rollout status deployment/<deployment-name> -n "$APP_NS"
kubectl describe deployment <deployment-name> -n "$APP_NS"
```

Check config:

```bash
kubectl get configmap -n "$APP_NS"
kubectl get secret -n "$APP_NS"
kubectl get configmap <configmap-name> -n "$APP_NS" -o yaml
```

## Recovery

If a transient dependency caused the crash, restart the deployment after the
dependency is healthy:

```bash
kubectl rollout restart deployment/<deployment-name> -n "$APP_NS"
kubectl rollout status deployment/<deployment-name> -n "$APP_NS"
```

If the latest image or manifest is bad, use [Rollback Procedure](rollback-procedure.md).

If the pod is `OOMKilled`, either roll back the change that increased memory
usage or raise the memory limit in Git and let Argo CD reconcile it.

If the pod is `Pending`, inspect capacity:

```bash
kubectl get nodes
kubectl describe pod -n "$APP_NS" <pod-name>
```

Scale non-critical demo workloads down only when you are intentionally
recovering a demo environment:

```bash
kubectl scale deployment/<non-critical-deployment> -n "$APP_NS" --replicas=0
```

## Validation

```bash
kubectl get pods -n "$APP_NS"
kubectl rollout status deployment/<deployment-name> -n "$APP_NS"
kubectl get endpoints -n "$APP_NS"
kubectl logs -n "$APP_NS" deployment/<deployment-name> --tail=80
```

If the backend is involved:

```bash
kubectl port-forward -n "$APP_NS" svc/devboard-backend 8080:8080
curl -fsS http://localhost:8080/api/health
```

Confirm the restart alert resolves:

```bash
kubectl port-forward -n monitoring svc/devboard-monitoring-kube-p-alertmanager 9093:9093
curl -fsS 'http://localhost:9093/api/v2/alerts' | grep DevBoardPodRestarting || true
```

## Follow-Up

- Capture the exact failed image tag or config change.
- Add a startup validation test if bad config caused the crash.
- Add resource tuning notes if the pod was killed for memory or CPU pressure.
- If the crash was caused by a deploy, add or improve post-deploy smoke tests.
