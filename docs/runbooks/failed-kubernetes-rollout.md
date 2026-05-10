# Failed Kubernetes Rollout Runbook

## Purpose

Use this when Argo CD applies a change but a deployment does not become healthy,
or when `kubectl rollout status` does not complete.

## Signals

- Argo CD app `devboard` is `Degraded`, `Progressing`, or stuck `OutOfSync`.
- `kubectl rollout status deployment/<name> -n devboard` times out.
- `DevBoardBackendUnavailable`, `DevBoardEventServiceUnavailable`, or
  `DevBoardFrontendUnavailable` fires.
- Pods show `ImagePullBackOff`, `CrashLoopBackOff`, readiness failures, or
  unschedulable status.

## First Checks

```bash
export APP_NS=devboard
export ARGO_NS=argocd

kubectl get application devboard -n "$ARGO_NS"
argocd app get devboard
argocd app diff devboard
kubectl get deployments -n "$APP_NS"
kubectl get pods -n "$APP_NS" -o wide
kubectl get events -n "$APP_NS" --sort-by=.lastTimestamp | tail -50
```

Check the deployment that failed:

```bash
kubectl rollout status deployment/<deployment-name> -n "$APP_NS"
kubectl describe deployment <deployment-name> -n "$APP_NS"
kubectl describe pod -n "$APP_NS" -l app=<deployment-name>
```

## Diagnosis

Check what Argo CD tried to apply:

```bash
argocd app manifests devboard | grep -A5 -B5 '<deployment-name>'
argocd app history devboard
```

Check the GitOps image tags:

```bash
grep -n 'sunmingtao/devboard' deploy/k8s/overlays/eks/kustomization.yaml
```

Common failure paths:

| Failure | Evidence | Action |
| --- | --- | --- |
| Bad image tag | `ImagePullBackOff`, image not found | roll back image tag in Git |
| Bad application config | app logs show startup/config errors | revert config change or restore secret |
| Readiness failure | pod running but not ready | inspect health endpoint and dependency logs |
| Resource pressure | pods pending or OOMKilled | add capacity, tune requests/limits, or roll back |
| Invalid manifest | Argo CD sync error | fix manifest and resync |

## Recovery

If the issue is an invalid or risky release, use [Rollback Procedure](rollback-procedure.md).

If the manifest is fixed in Git, let Argo CD reconcile:

```bash
git status --short
argocd app sync devboard
argocd app wait devboard --health --sync --timeout 600
```

If automated sync is temporarily disabled for a demo, re-enable it after the
safe manifest is committed:

```bash
argocd app set devboard --sync-policy automated --auto-prune --self-heal
```

If Argo CD is stuck because the live cluster drifted during manual debugging,
compare live state to Git before forcing any changes:

```bash
argocd app diff devboard
kubectl get deployment <deployment-name> -n "$APP_NS" -o yaml
```

## Validation

```bash
argocd app get devboard
argocd app wait devboard --health --sync --timeout 600
kubectl get pods -n "$APP_NS"
kubectl rollout status deployment/devboard-backend -n "$APP_NS"
kubectl rollout status deployment/devboard-frontend -n "$APP_NS"
kubectl rollout status deployment/devboard-event-service -n "$APP_NS"
kubectl rollout status deployment/devboard-event-frontend -n "$APP_NS"
```

Run a backend smoke check:

```bash
kubectl port-forward -n "$APP_NS" svc/devboard-backend 8080:8080
curl -fsS http://localhost:8080/api/health
```

## Follow-Up

- Add the failure mode to the Jenkins or post-deploy smoke checks.
- Record the bad commit SHA and fixed commit SHA.
- If the issue was a missing dependency, document it in the deployment docs.
- If the issue was capacity, update the EKS node group sizing notes.
