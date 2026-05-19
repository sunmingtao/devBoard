# Argo CD app layout

Local Minikube, homelab k3s, and EKS apps are intentionally separate.

- `*-local.yaml`: local Minikube apps.
- `*-k3s.yaml`: Ansible-managed homelab k3s apps.
- `*-eks.yaml` and existing cloud-oriented app files: AWS EKS apps.

The homelab k3s cluster can run dev and prod side by side, so k3s app names are
unique inside the same Argo CD namespace:

- `devboard-dev-k3s` deploys `deploy/k8s/overlays/dev-k3s` into `devboard-dev`.
- `devboard-prod-k3s` deploys `deploy/k8s/overlays/prod-k3s` into
  `devboard-prod`.
- Kafka is installed once per environment namespace so both overlays can use the
  in-namespace `devboard-kafka:9092` bootstrap address.

Apply only the app manifests for the cluster you are bootstrapping.

