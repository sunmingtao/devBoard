#!/usr/bin/env bash
set -euo pipefail

REGION="ap-southeast-2"
CLUSTER_NAME="devboard-dev-eks"
NAMESPACE="devboard"
INGRESS_NAME="devboard-ingress"
ARGOCD_NAMESPACE="argocd"
DEVBOARD_APP="devboard"
KAFKA_APP="devboard-kafka"

echo "Updating kubeconfig..."
aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME" || true

echo "Stopping Argo CD reconciliation if apps exist..."
kubectl patch application "$DEVBOARD_APP" -n "$ARGOCD_NAMESPACE" \
  --type=merge \
  -p '{"spec":{"syncPolicy":null}}' >/dev/null 2>&1 || true
kubectl patch application "$KAFKA_APP" -n "$ARGOCD_NAMESPACE" \
  --type=merge \
  -p '{"spec":{"syncPolicy":null}}' >/dev/null 2>&1 || true
kubectl delete application "$DEVBOARD_APP" -n "$ARGOCD_NAMESPACE" --ignore-not-found=true || true
kubectl delete application "$KAFKA_APP" -n "$ARGOCD_NAMESPACE" --ignore-not-found=true || true

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
if terraform state list | grep -q '^module\.ingress'; then
  terraform state list | grep '^module\.ingress' | xargs -r terraform state rm
else
  echo "No Terraform-managed ingress resources found in state."
fi

echo "Destroying Terraform infra..."
terraform destroy -auto-approve

echo "Done."
