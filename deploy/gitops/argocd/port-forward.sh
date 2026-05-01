#!/bin/bash
# Argo CD Port-Forward Script
# Usage: ./port-forward.sh [argocd-server|argocd-repo-server]
#
# Default: argocd-server (UI)

COMPONENT="${1:-argocd-server}"
NAMESPACE="argocd"

echo "Starting port-forward for ${COMPONENT} in namespace ${NAMESPACE}..."
echo "Press Ctrl+C to stop"

# Map different ports based on component
case "$COMPONENT" in
  argocd-server)
    echo "Argo CD UI will be available at: http://localhost:8080"
    kubectl port-forward -n "$NAMESPACE" svc/argocd-server 8080:443
    ;;
  argocd-repo-server)
    echo "Argo CD Repo Server will be available at: localhost:8081"
    kubectl port-forward -n "$NAMESPACE" svc/argocd-repo-server 8081:8081
    ;;
  *)
    echo "Unknown component: $COMPONENT"
    echo "Available: argocd-server, argocd-repo-server"
    exit 1
    ;;
esac
