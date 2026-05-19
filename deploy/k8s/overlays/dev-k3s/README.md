# DevBoard dev k3s overlay

This overlay targets the single-node homelab k3s cluster managed by Ansible.

- Namespace: `devboard-dev`
- Ingress host: `dev.devboard.local`
- Storage class: `local-path`
- Database: in-cluster MySQL with its own PVC
- Secrets: placeholder Kubernetes Secrets for the first homelab pass

Replace the placeholder secrets when the k3s dev/prod secret-management decision
is implemented.

