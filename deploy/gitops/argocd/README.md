# Argo CD GitOps Setup for DevBoard

This directory contains the Argo CD installation and configuration for DevBoard GitOps deployment.

## Quick Start

### 1. Install Argo CD

```bash
# Apply all manifests using Kustomize (recommended)
kubectl apply -k deploy/gitops/argocd/
```

> **Note:** The `kustomization.yaml` file references the official Argo CD install manifest and local namespace configuration.

### 2. Create the DevBoard Argo CD application

```bash
kubectl apply -f deploy/gitops/apps/devboard.yaml
```

This creates an Argo CD `Application` named `devboard`. It watches this repository on the `main` branch, reads Kubernetes manifests from `deploy/k8s/overlays/eks`, and deploys them into the `devboard` namespace.

Automated sync is enabled with pruning and self-healing:

- `prune`: remove Kubernetes resources that were deleted from Git
- `selfHeal`: restore live cluster resources if they drift away from Git

### 3. Access Argo CD UI

```bash
# Start port-forward to Argo CD server
deploy/gitops/argocd/port-forward.sh argocd-server

# Argo CD UI will be available at: http://localhost:8080
```

### 4. Login to Argo CD

```bash
# Get the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Username: admin
# Password: <output from above command>
```

### 5. Change the admin password (recommended)

```bash
# After logging in, change the password via UI or CLI
argocd login localhost:8080 --username admin --password <current-password>
argocd account update-password --current-password <current-password> --new-password <new-password>
```

## Directory Structure

```
deploy/gitops/argocd/
├── 00-namespace.yaml      # Creates argocd namespace
├── kustomization.yaml     # Kustomize entrypoint for kubectl apply -k
├── port-forward.sh        # Script to access Argo CD UI
└── README.md              # This file

deploy/gitops/apps/
└── devboard.yaml          # DevBoard Argo CD Application
```

## Common Commands

### Check Argo CD Status

```bash
# Check all Argo CD pods are running
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd

# Check Argo CD services
kubectl get svc -n argocd
```

### Check DevBoard Application Status

```bash
kubectl get application devboard -n argocd
argocd app get devboard
```

### Manual Sync for Safer Demos

Automated sync is enabled in Git, but for a slower interview demo you can temporarily switch the live Argo CD application to manual sync:

```bash
argocd app set devboard --sync-policy none
```

Then make or show a Git change, wait for Argo CD to mark the app `OutOfSync`, and trigger the deployment yourself:

```bash
argocd app diff devboard
argocd app sync devboard
argocd app wait devboard --health --sync
```

When the demo is finished, turn automated sync back on:

```bash
argocd app set devboard --sync-policy automated --auto-prune --self-heal
```

### Access Different Components

```bash
# Argo CD UI
deploy/gitops/argocd/port-forward.sh argocd-server

# Repo Server (for debugging sync issues)
deploy/gitops/argocd/port-forward.sh argocd-repo-server
```

### Uninstall Argo CD

```bash
# Remove Argo CD (keep namespace)
kubectl delete -k deploy/gitops/argocd/

# Or remove everything including namespace
kubectl delete -f deploy/gitops/argocd/00-namespace.yaml
```

## Next Steps

After Argo CD is installed, proceed to:
- [Configure GitOps workflow documentation](../README.md)

## Troubleshooting

### Pods not starting

```bash
# Check pod logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server

# Check for resource issues
kubectl describe pods -n argocd
```

### Cannot access UI

```bash
# Verify service is running
kubectl get svc -n argocd argocd-server

# Check port-forward is running
ps aux | grep port-forward
```

### Login issues

```bash
# Reset admin password
kubectl -n argocd delete secret argocd-initial-admin-secret
# Argo CD will generate a new secret on next sync
```

## Resources

- [Argo CD Documentation](https://argo-cd.readthedocs.io/)
- [Argo CD GitHub](https://github.com/argoproj/argo-cd)
