# Rollback Procedure

## Purpose

Use this when a release causes failed rollouts, user-visible errors, crash
loops, bad Kafka behavior, or failed smoke tests.

DevBoard deploys to EKS through GitOps:

1. Jenkins builds and scans images.
2. Jenkins updates image tags in `deploy/k8s/overlays/eks/kustomization.yaml`.
3. Argo CD reconciles the `devboard` application from the `main` branch.

The safest rollback is therefore a Git revert or a new Git commit that restores
the last known good image tags.

## Decide Whether to Roll Back

Roll back when one of these is true:

- A recent deployment correlates with critical alerts.
- A deployment is stuck and user traffic is affected.
- Smoke tests fail after Argo CD sync.
- A dependency or schema change is unsafe to fix in place.

Prefer a forward fix when the failure is isolated, understood, and can be
corrected faster than reverting.

## Find the Last Known Good Version

Check Argo CD history:

```bash
argocd app history devboard
argocd app get devboard
```

Check Kubernetes rollout history:

```bash
kubectl rollout history deployment/devboard-backend -n devboard
kubectl rollout history deployment/devboard-frontend -n devboard
kubectl rollout history deployment/devboard-event-service -n devboard
kubectl rollout history deployment/devboard-event-frontend -n devboard
```

Check Git history for image tag changes:

```bash
git log --oneline -- deploy/k8s/overlays/eks/kustomization.yaml
git show <known-good-commit>:deploy/k8s/overlays/eks/kustomization.yaml
```

## Preferred Recovery: Revert the GitOps Commit

If the bad release came from one commit, revert it:

```bash
git revert <bad-commit-sha>
git push origin main
```

Then watch Argo CD reconcile:

```bash
argocd app sync devboard
argocd app wait devboard --health --sync --timeout 600
kubectl get pods -n devboard
```

If automated sync is enabled and the revert is already pushed, Argo CD may sync
without a manual `argocd app sync`.

## Alternative Recovery: Restore Known Good Image Tags

If a normal revert is not clean, edit `deploy/k8s/overlays/eks/kustomization.yaml`
and restore the known good tags for the affected images:

```yaml
value: sunmingtao/devboard-backend:<known-good-tag>
value: sunmingtao/devboard-frontend:<known-good-tag>
value: sunmingtao/devboard-event-service:<known-good-tag>
value: sunmingtao/devboard-event-frontend:<known-good-tag>
```

Commit and push:

```bash
git add deploy/k8s/overlays/eks/kustomization.yaml
git commit -m "Rollback DevBoard EKS images to <known-good-tag>"
git push origin main
```

Then sync and wait:

```bash
argocd app sync devboard
argocd app wait devboard --health --sync --timeout 600
```

## Emergency Recovery: Kubernetes Rollout Undo

Use this only to restore service quickly while preparing the Git rollback.
Because Argo CD self-heal is enabled, live-only changes can be overwritten by
the desired state in Git.

```bash
kubectl rollout undo deployment/devboard-backend -n devboard
kubectl rollout status deployment/devboard-backend -n devboard
```

If needed, temporarily pause Argo CD automated sync for a controlled demo:

```bash
argocd app set devboard --sync-policy none
```

After the Git rollback is committed and synced, restore automated sync:

```bash
argocd app set devboard --sync-policy automated --auto-prune --self-heal
```

## Validation

Confirm GitOps health:

```bash
argocd app get devboard
argocd app wait devboard --health --sync --timeout 600
```

Confirm rollout health:

```bash
kubectl rollout status deployment/devboard-backend -n devboard
kubectl rollout status deployment/devboard-frontend -n devboard
kubectl rollout status deployment/devboard-event-service -n devboard
kubectl rollout status deployment/devboard-event-frontend -n devboard
```

Run smoke checks:

```bash
kubectl port-forward -n devboard svc/devboard-backend 8080:8080
curl -fsS http://localhost:8080/api/health
curl -fsS http://localhost:8080/api/hello
```

Check alerts:

```bash
kubectl port-forward -n monitoring svc/devboard-monitoring-kube-p-alertmanager 9093:9093
curl -fsS 'http://localhost:9093/api/v2/alerts' | grep DevBoard || true
```

## Interview Talking Points

- Git is the source of truth, so rollback is auditable.
- Argo CD reconciles the cluster instead of relying on manual kubectl changes.
- Emergency `kubectl rollout undo` is allowed for service restoration, but the
  desired state must be fixed in Git afterward.
- Validation includes both Kubernetes health and user-facing smoke checks.

## Follow-Up

- Open a post-incident note with bad commit, fixed commit, impact, and recovery
  time.
- Add a test or CI gate for the missed failure.
- If rollback took too long, automate known-good image redeploy in Jenkins or
  Argo CD.
