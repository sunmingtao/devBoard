#!/usr/bin/env bash
set -euo pipefail

REGION="ap-southeast-2"
CLUSTER_NAME="devboard-dev-eks"
NAMESPACE="devboard"
INGRESS_NAME="devboard-ingress"

echo "Updating kubeconfig..."
aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME" || true

echo "Deleting ingress if exists..."
kubectl delete ingress "$INGRESS_NAME" -n "$NAMESPACE" --ignore-not-found=true || true

echo "Waiting for ingress deletion..."
for i in {1..30}; do
  if ! kubectl get ingress "$INGRESS_NAME" -n "$NAMESPACE" >/dev/null 2>&1; then
    echo "Ingress deleted."
    break
  fi

  echo "Ingress still exists, waiting..."
  sleep 10

  if [ "$i" -eq 30 ]; then
    echo "Ingress stuck. Removing finalizers..."
    kubectl patch ingress "$INGRESS_NAME" -n "$NAMESPACE" \
      -p '{"metadata":{"finalizers":[]}}' \
      --type=merge || true
  fi
done

echo "Deleting app resources..."
kubectl delete -k ../../../../../deploy/k8s/overlays/eks --ignore-not-found=true || true

echo "Removing ingress from Terraform state if present..."
terraform state rm module.ingress.kubernetes_ingress_v1.this || true

echo "Destroying Terraform infra..."
terraform destroy -auto-approve

echo "Done."