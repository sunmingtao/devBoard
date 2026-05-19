# Argo CD app layout

Local Minikube, homelab k3s, and EKS apps are intentionally separated by
directory:

- `local/`: local Minikube apps.
- `k3s/`: Ansible-managed homelab k3s apps.
- `eks/`: AWS EKS apps.

The homelab k3s cluster can run dev and prod side by side, so k3s app names are
unique inside the same Argo CD namespace:

- `k3s/devboard-dev.yaml` deploys `deploy/k8s/overlays/dev-k3s` into
  `devboard-dev`.
- `k3s/devboard-prod.yaml` deploys `deploy/k8s/overlays/prod-k3s` into
  `devboard-prod`.
- Kafka is installed once per environment namespace so both overlays can use the
  in-namespace `devboard-kafka:9092` bootstrap address.
- `k3s/devboard-kafka-exporter-dev.yaml` and
  `k3s/devboard-kafka-exporter-prod.yaml` scrape the dev and prod k3s Kafka
  clusters separately from the shared `monitoring` namespace.

Apply only the app manifests for the cluster you are bootstrapping.
