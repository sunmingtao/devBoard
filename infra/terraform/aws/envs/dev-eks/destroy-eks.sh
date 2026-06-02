#!/usr/bin/env bash
set -euo pipefail

REGION="ap-southeast-2"
CLUSTER_NAME="devboard-dev-eks"
NAMESPACE="devboard"
MONITORING_NAMESPACE="monitoring"
INGRESS_NAME="devboard-ingress"
ARGOCD_NAMESPACE="argocd"
ARGOCD_APPS=(
  observability-eks
  devboard-kafka-exporter
  devboard-monitoring
  devboard
  devboard-kafka
  ingress-nginx
)
MAIL_TO="sunmingtao@gmail.com"
STARTED_AT="$(date -Is)"

notify_result() {
  local exit_code=$?
  local status="SUCCESS"

  if [ "$exit_code" -ne 0 ]; then
    status="FAILURE"
  fi

  if command -v mail >/dev/null 2>&1; then
    {
      echo "devBoard EKS destroy finished with status: $status"
      echo "Exit code: $exit_code"
      echo "Cluster: $CLUSTER_NAME"
      echo "Region: $REGION"
      echo "Started: $STARTED_AT"
      echo "Finished: $(date -Is)"
    } | mail -s "devBoard EKS destroy $status" "$MAIL_TO" || true
  else
    echo "mail command not found; could not send destroy result to $MAIL_TO" >&2
  fi

  exit "$exit_code"
}

trap notify_result EXIT

echo "Updating kubeconfig..."
aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME" || true

echo "Stopping Argo CD reconciliation if apps exist..."
for app in "${ARGOCD_APPS[@]}"; do
  kubectl patch application "$app" -n "$ARGOCD_NAMESPACE" \
    --type=merge \
    -p '{"spec":{"syncPolicy":null}}' >/dev/null 2>&1 || true
done

echo "Deleting Argo CD Applications if they exist..."
for app in "${ARGOCD_APPS[@]}"; do
  kubectl delete application "$app" -n "$ARGOCD_NAMESPACE" --ignore-not-found=true || true
done

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

echo "Deleting DevBoard app resources..."
kubectl delete -k ../../../../../deploy/k8s/overlays/eks --ignore-not-found=true || true

echo "Deleting observability resources..."
kubectl delete -k ../../../../../deploy/observability/eks --ignore-not-found=true || true

echo "Deleting Argo-managed Kafka resources..."
kubectl delete statefulset,svc,cm,secret,sa,role,rolebinding,pdb \
  -n "$NAMESPACE" \
  -l app.kubernetes.io/instance=devboard-kafka \
  --ignore-not-found=true || true

echo "Deleting monitoring and devboard namespaces if they still exist..."
kubectl delete namespace "$MONITORING_NAMESPACE" --ignore-not-found=true --wait=false || true
kubectl delete namespace "$NAMESPACE" --ignore-not-found=true --wait=false || true

echo "Deleting cluster-scoped monitoring resources..."
kubectl delete \
  clusterrole,clusterrolebinding,customresourcedefinition,mutatingwebhookconfiguration,validatingwebhookconfiguration \
  -l app.kubernetes.io/instance=devboard-monitoring \
  --ignore-not-found=true || true

echo "Removing ingress from Terraform state if present..."
if terraform state list | grep -q '^module\.ingress'; then
  terraform state list | grep '^module\.ingress' | xargs -r terraform state rm
else
  echo "No Terraform-managed ingress resources found in state."
fi

echo "Destroying Terraform infra..."
terraform destroy -auto-approve

echo "Waiting for EKS cluster deletion..."
aws eks wait cluster-deleted --region "$REGION" --name "$CLUSTER_NAME"

echo "Done."
