# DevBoard prod k3s overlay

This overlay targets the single-node homelab k3s cluster managed by Ansible.

- Namespace: `devboard-prod`
- Ingress host: `prod.devboard.local`
- Storage class: `local-path`
- Database: in-cluster MySQL with its own PVC
- Secrets: placeholder Kubernetes Secrets for the first homelab pass

Replace the placeholder secrets before using this as a real production
deployment. The durable secret-management design is tracked separately in the
roadmap.

