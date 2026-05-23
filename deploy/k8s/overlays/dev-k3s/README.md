# DevBoard dev k3s overlay

This overlay targets the single-node homelab k3s cluster managed by Ansible.

- Namespace: `devboard-dev`
- Ingress host: `dev.devboard.local`
- Storage class: `local-path`
- Database: in-cluster MySQL with its own PVC
- Secrets: SOPS-encrypted Kubernetes Secrets decrypted by Argo CD/KSOPS

See `docs/k3s-sops-age-secrets.md` for key handling, editing, and Argo CD
bootstrap steps.
