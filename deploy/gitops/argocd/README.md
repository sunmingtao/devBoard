# Argo CD GitOps Setup for DevBoard

This directory contains the Argo CD installation and configuration for DevBoard GitOps deployment.

## Quick Start

### 1. Install Argo CD

```bash
# Apply all manifests using Kustomize (recommended)
kubectl apply --server-side --force-conflicts -k deploy/gitops/argocd/
```

> **Note:** The `kustomization.yaml` file references the official Argo CD install manifest and local namespace configuration. Server-side apply avoids oversized client-side apply annotations on Argo CD CRDs.

### 2. Create the controller and DevBoard Argo CD applications

For the Ansible-managed homelab k3s cluster, prefer the Ansible playbook:

```bash
cd infra/ansible
ansible-playbook playbooks/argocd.yml
```

The playbook installs Argo CD and waits for the Argo CD CRDs and pods. It does
not apply the k3s `Application` manifests by default because they read from
GitHub `main`; enable them after the k3s manifests are on that branch:

```bash
cd infra/ansible
ansible-playbook playbooks/argocd.yml -e argocd_bootstrap_k3s_apps=true
```

The k3s app set is:

```bash
kubectl apply -f deploy/gitops/apps/argo-rollouts-k3s.yaml
kubectl apply -f deploy/gitops/apps/external-secrets-k3s.yaml
kubectl apply -f deploy/gitops/apps/ingress-nginx-k3s.yaml
kubectl wait --for condition=Established crd/rollouts.argoproj.io --timeout=180s
kubectl wait --for condition=Established crd/externalsecrets.external-secrets.io --timeout=180s
kubectl apply -f deploy/gitops/apps/devboard-kafka-dev-k3s.yaml
kubectl apply -f deploy/gitops/apps/devboard-kafka-prod-k3s.yaml
kubectl apply -f deploy/gitops/apps/devboard-dev-k3s.yaml
kubectl apply -f deploy/gitops/apps/devboard-prod-k3s.yaml
```

For EKS:

```bash
kubectl apply -f deploy/gitops/apps/argo-rollouts-eks.yaml
kubectl apply -f deploy/gitops/apps/external-secrets-eks.yaml
kubectl wait --for condition=Established crd/rollouts.argoproj.io --timeout=180s
kubectl wait --for condition=Established crd/externalsecrets.external-secrets.io --timeout=180s
kubectl apply -f deploy/gitops/apps/devboard-eks.yaml
```

This creates the Argo Rollouts and External Secrets controller applications,
then creates the DevBoard Argo CD `Application` named `devboard`. DevBoard
watches this repository on the `main` branch, reads Kubernetes manifests from
`deploy/k8s/overlays/eks`, and deploys them into the `devboard` namespace.

Automated sync is enabled with pruning and self-healing:

- `prune`: remove Kubernetes resources that were deleted from Git
- `selfHeal`: restore live cluster resources if they drift away from Git

### 3. Access Argo CD UI

```bash
# Start port-forward to Argo CD server
kubectl -n argocd port-forward svc/argocd-server 8080:443

# Argo CD UI will be available at: https://localhost:8080
```

`kubectl port-forward` binds to localhost on the machine where it runs. If the
command is running on the homelab server and you are browsing from your laptop,
use an SSH tunnel:

```bash
ssh -t -L 8080:127.0.0.1:8080 mike@192.168.0.46 \
  'kubectl -n argocd port-forward svc/argocd-server 8080:443'
```

Then open `https://localhost:8080` on the laptop.

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
├── argo-rollouts-eks.yaml # EKS Argo Rollouts controller Application
├── argo-rollouts-k3s.yaml # Homelab k3s Argo Rollouts controller Application
├── argo-rollouts-local.yaml # Local Argo Rollouts controller Application
├── devboard-dev-k3s.yaml # Homelab k3s DevBoard dev Application
├── external-secrets-eks.yaml # EKS External Secrets Application
├── external-secrets-k3s.yaml # Homelab k3s External Secrets Application
├── external-secrets-local.yaml # Local External Secrets Application
├── ingress-nginx-k3s.yaml # Homelab k3s ingress-nginx Application
├── devboard-prod-k3s.yaml # Homelab k3s DevBoard prod Application
├── devboard-eks.yaml      # EKS DevBoard Application
└── devboard-local.yaml    # Local DevBoard Application
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
