# k3s SOPS + age Secrets

DevBoard k3s dev/prod secrets are stored in Git as SOPS-encrypted Kubernetes
Secret manifests and decrypted by Argo CD through KSOPS.

## Files

- `.sops.yaml` stores the public age recipient used for k3s secret files.
- `deploy/k8s/overlays/dev-k3s/*-secret.sops.yaml` contains encrypted dev
  Kubernetes Secrets.
- `deploy/k8s/overlays/prod-k3s/*-secret.sops.yaml` contains encrypted prod
  Kubernetes Secrets.
- `deploy/k8s/overlays/*-k3s/secrets-generator.yaml` tells KSOPS which SOPS
  files to decrypt during Kustomize rendering.
- `deploy/gitops/argocd/ksops-cmp-plugin.yaml` registers the Argo CD config
  management plugin.

## Local Key

The age private key lives outside Git:

```bash
~/.config/sops/age/keys.txt
```

Create one if it does not exist:

```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
chmod 600 ~/.config/sops/age/keys.txt
grep "public key:" ~/.config/sops/age/keys.txt
```

Put the public `age1...` recipient in `.sops.yaml`. Never commit
`keys.txt`.

## Argo CD Key Secret

The Ansible Argo CD role reads `~/.config/sops/age/keys.txt` from the control
node and applies it to the cluster as:

```text
argocd/sops-age
```

Manual equivalent:

```bash
kubectl -n argocd create secret generic sops-age \
  --from-file=keys.txt="$HOME/.config/sops/age/keys.txt" \
  --dry-run=client -o yaml |
kubectl apply -f -
```

The Argo CD repo-server KSOPS sidecar mounts that secret and uses
`SOPS_AGE_KEY_FILE=/home/argocd/.config/sops/age/keys.txt` when rendering the
k3s DevBoard applications.

## Edit Secrets

Edit encrypted files directly with SOPS:

```bash
SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt" \
  sops deploy/k8s/overlays/dev-k3s/backend-secret.sops.yaml
```

Encrypt a new plaintext secret file:

```bash
SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt" \
  sops --encrypt \
  --filename-override deploy/k8s/overlays/prod-k3s/backend-secret.sops.yaml \
  --input-type yaml \
  --output-type yaml \
  --output deploy/k8s/overlays/prod-k3s/backend-secret.sops.yaml \
  /tmp/backend-secret.yaml
```

Check decrypted output without writing a plaintext file:

```bash
SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt" \
  sops --decrypt deploy/k8s/overlays/prod-k3s/backend-secret.sops.yaml
```

## Deploy

After the encrypted secret files and `.sops.yaml` are committed to the branch
Argo CD watches, bootstrap or refresh Argo CD:

```bash
cd infra/ansible
ansible-playbook playbooks/argocd.yml -e argocd_bootstrap_k3s_apps=true
```

The k3s DevBoard Argo CD applications use the `ksops-v1.0` plugin. Argo CD
decrypts secrets during manifest generation and applies normal Kubernetes
Secret objects to the target namespace.
